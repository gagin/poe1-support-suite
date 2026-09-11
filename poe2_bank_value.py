"""Live bank valuation for PoE2 (Forbidden Rites) via GGG's public trade API.

PoE2 trade is a single cross-platform pool, so anonymous queries reflect the
same market on console and PC.

Architecture (pull decoupled from assessment)
  - Pull layer fetches market prices and stores them timestamped in sqlite
    (market_cache.db, table `prices`). One row per item/ratio.
  - Assessment reads the bank from HOLDINGS, values it from sqlite, and only
    hits the API for rows that are missing or staler than --max-age hours
    (default 1). Fully-cached runs are instant and offline.

Usage
  uv run python poe2_bank_value.py                  # assess; refresh stale>1h
  uv run python poe2_bank_value.py --refresh        # force full re-pull
  uv run python poe2_bank_value.py --no-refresh     # offline, cache only
  uv run python poe2_bank_value.py --max-age 0.25   # 15-min staleness
  uv run python poe2_bank_value.py --probe NAME     # debug one query shape

Rate limits: GGG throttles aggressively (429s observed). API calls are spaced
~4s apart with Retry-After/backoff handling; each stored row is committed
immediately so Ctrl-C never loses fetched data. Personal use only.

Edit HOLDINGS to match your current bank. Each entry:
  (label, qty, query_type | None, override_chaos | None)
If a query yields <3 priced listings, the override is used (and flagged).
"""
from __future__ import annotations

import argparse
import datetime
import json
import sqlite3
import statistics
import sys
import time
import urllib.error
import urllib.request

LEAGUE = "Forbidden Rites"
LEAGUE_SLUG = "Forbidden%20Rites"
DB_PATH = "market_cache.db"
UA = {
    "User-Agent": "poe-bank-valuer personal-use",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://www.pathofexile.com",
    "Referer": "https://www.pathofexile.com/trade2/",
}
SLEEP_S = 4.0
FETCH_N = 10

# (label, qty, trade type search | None, manual override in chaos | None)
# State as of 2026-09-11 pre-sleep tally. Chance omen spent on challenge.
HOLDINGS = [
    ("Orb of Annulment", 6, "Orb of Annulment", 5.8),
    ("Divine Orb", 40, None, None),  # the numeraire leg, valued at div rate
    ("Fracturing Orb", 2, "Fracturing Orb", 89.3),  # 7.44d @12
    ("Greater Exalted Orb", 1, "Greater Exalted Orb", 18.5),
    ("Greater Chaos Orb", 12, "Greater Chaos Orb", 30.6),  # 2.55d @12
    ("flat Chaos Orb", 312, None, 1.0),  # 209 + 103 overnight sales
    ("Exalted Orb", 1408, "Exalted Orb", None),
    ("Perfect Jeweller's Orb", 2, "Perfect Jeweller's Orb", None),
    ("Cryptic Key", 6, "Cryptic Key", 26.0),  # 26c carried, AMBIGUOUS
    ("Orb of Chance", 16, "Orb of Chance", None),
    ("Omen of Sinistral Annulment", 1, "Omen of Sinistral Annulment", 80.0),
    ("Omen of Dextral Annulment", 2, "Omen of Dextral Annulment", 31.0),
    ("Omen of Dextral Erasure", 2, "Omen of Dextral Erasure", 48.0),
    ("Omen of Whittling", 1, "Omen of Whittling", 42.0),  # 3.5d @12
    ("Omen of Dextral Crystallisation", 4,
     "Omen of Dextral Crystallisation", 2.4),
    ("Omen of Abyssal Echoes", 18, "Omen of Abyssal Echoes", 3.6),
    ("Omen of Light", 2, "Omen of Light", 30.5),
    ("Omen of the Blessed", 1, "Omen of the Blessed", None),
    ("Chaotic rarity tablet", 7, None, 2.9),
    ("Chaotic quantity tablet", 3, None, 5.4),
    ("Chaotic monsters tablet", 6, None, 1.1),
    ("Chaotic effectiveness tablet", 2, None, None),
    ("Preserved Cranium", 17, "Preserved Cranium", 69.6),  # 5.8d @12
    ("Ancient Collarbone", 1, "Ancient Collarbone", 43.2),  # 3.6d @12
    ("Liquid Melancholy", 1, "Liquid Melancholy", 4.0),
    ("Expedition Logbook", 7, "Expedition Logbook", 2.3),
    ("Masterwork Rune", 5, "Masterwork Rune", 7.0),
    ("Simulacrum", 1, "Simulacrum", 22.0),
]

VOICES_TARGET_D = 359.0


# ── sqlite cache ──────────────────────────────────────────────────────────
def db():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS prices ("
        " item TEXT PRIMARY KEY,"
        " unit_chaos REAL NOT NULL,"
        " n INTEGER NOT NULL DEFAULT 0,"
        " src TEXT NOT NULL DEFAULT '',"
        " fetched_at TEXT NOT NULL)")
    con.execute(
        "CREATE TABLE IF NOT EXISTS snapshots ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " taken_at TEXT NOT NULL,"
        " total_chaos REAL NOT NULL,"
        " total_div REAL,"
        " div_rate REAL,"
        " div_src TEXT NOT NULL DEFAULT '',"
        " voices_pct REAL)")
    con.execute(
        "CREATE TABLE IF NOT EXISTS snapshot_lines ("
        " snapshot_id INTEGER NOT NULL REFERENCES snapshots(id),"
        " label TEXT NOT NULL,"
        " qty REAL NOT NULL,"
        " unit_chaos REAL,"
        " value_chaos REAL,"
        " src TEXT NOT NULL DEFAULT '')")
    return con


def now_iso():
    return (datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"))


def cached(con, item):
    row = con.execute(
        "SELECT unit_chaos, n, src, fetched_at FROM prices WHERE item=?",
        (item,)).fetchone()
    if not row:
        return None
    unit, n, src, ts = row
    age_h = ((datetime.datetime.now(datetime.timezone.utc)
              - datetime.datetime.fromisoformat(ts)).total_seconds() / 3600)
    return {"unit": unit, "n": n, "src": src, "age_h": age_h}


def store(con, item, unit, n, src):
    con.execute(
        "INSERT INTO prices (item, unit_chaos, n, src, fetched_at)"
        " VALUES (?, ?, ?, ?, ?)"
        " ON CONFLICT (item) DO UPDATE SET"
        " unit_chaos=excluded.unit_chaos, n=excluded.n,"
        " src=excluded.src, fetched_at=excluded.fetched_at",
        (item, unit, n, src, now_iso()))
    con.commit()


# ── throttled API ─────────────────────────────────────────────────────────
def _req(method, path, body=None, tries=4):
    url = f"https://www.pathofexile.com{path}"
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        req = urllib.request.Request(url, data=data, headers=UA,
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            retry = e.headers.get("Retry-After")
            wait = float(retry) if retry else 8 * (attempt + 1)
            print(f"  HTTP {e.code}, backing off {wait:.0f}s...",
                  file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"API failed after {tries} tries: {path}")


def _paced():
    time.sleep(SLEEP_S)


def search_type(item_type, limit_ids=FETCH_N):
    body = {"query": {"status": {"option": "online"}, "type": item_type},
            "sort": {"price": "asc"}}
    s = _req("POST", f"/api/trade2/search/poe2/{LEAGUE_SLUG}", body)
    return s.get("id"), s.get("result", [])[:limit_ids], s.get("total", 0)


def fetch_listings(ids, query_id):
    out = []
    for i in range(0, len(ids), 10):
        chunk = ids[i:i + 10]
        f = _req("GET", "/api/trade2/fetch/" + ",".join(chunk)
                 + f"?query={query_id}")
        out.extend(f.get("result", []))
        _paced()
    return out


def listing_chaos(item, rates):
    listing = item.get("listing") or {}
    price = listing.get("price") or {}
    amount, cur = price.get("amount"), (price.get("currency") or "")
    if amount is None or not cur:
        return None
    # Listed price covers the whole stack; unit price divides by stackSize.
    stack = ((item.get("item") or {}).get("stackSize")) or 1
    try:
        per_unit = float(amount) / float(stack)
    except (TypeError, ValueError):
        return None
    cur = cur.lower()
    if cur == "chaos":
        return per_unit
    if cur in rates:
        return per_unit * rates[cur]
    return None


def pull_item_median(item_type, rates):
    """Returns (median_chaos | None, total_listings). Two API rounds."""
    qid, ids, total = search_type(item_type)
    _paced()
    if not ids:
        return None, total
    prices = []
    for r in fetch_listings(ids, qid):
        v = listing_chaos(r, rates)
        if v is not None:
            prices.append(v)
    prices.sort()
    use = prices[:max(3, min(len(prices), 10))]
    if len(use) < 3:
        return None, total
    return statistics.median(use), total


# ── assessment ────────────────────────────────────────────────────────────
def estimate_div_rate():
    """Tripwire only: median of high-stock exchange ratios.

    The exchange book is full of 1c price-fix bait, so this is NOT used as
    the numeraire — it only flags when the market moved away from the rate
    in use. Returns (estimate | None, n_listings).
    """
    body = {"exchange": {"status": {"option": "online"},
                         "have": ["divine"], "want": ["chaos"]}}
    ex = _req("POST", f"/api/trade2/exchange/poe2/{LEAGUE_SLUG}", body)
    res = ex.get("result") or {}
    ratios = []
    for listing in res.values():
        offers = ((listing.get("listing") or {}).get("offers")) or []
        for offer in offers:
            exch = offer.get("exchange") or {}
            item = offer.get("item") or {}
            have_amt, want_amt = exch.get("amount"), item.get("amount")
            stock = item.get("stock") or 0
            if have_amt and want_amt and stock >= 100:
                ratios.append(float(want_amt) / float(have_amt))
    if not ratios:
        return None, ex.get("total", 0)
    ratios.sort()
    return statistics.median(ratios), ex.get("total", 0)


def resolve_rate(con, key, fallback_rate, max_age_h, force, offline):
    """Numeraire resolution order: --div-rate > fresh cache > live tripwire.

    Never auto-adopts a pulled rate: fixer bait makes auto-rates dangerous.
    A pulled estimate is stored for reference and warns on big deviation.
    """
    if fallback_rate:
        return fallback_rate, "manual-override"
    hit = cached(con, key)
    if force or hit is None or hit["age_h"] > max_age_h:
        if offline:
            return (hit["unit"], "STALE-OFFLINE") if hit else (None, "NO-DATA")
        est, n = estimate_div_rate()
        _paced()
        if est is None:
            return (hit["unit"], "EST-FAILED") if hit else (None, "NO-DATA")
        store(con, key + ":estimate", est, n, "exchange-tripwire")
        if hit and hit["unit"]:
            dev = abs(est - hit["unit"]) / hit["unit"]
            flag = (f"MARKET-MOVED? est {est:.1f} vs used {hit['unit']:.1f}"
                    if dev > 0.15 else "in-line")
            print(f"  [tripwire] divine est {est:.1f}c (n={n}), "
                  f"cached {hit['unit']:.1f}c — {flag}", file=sys.stderr)
            return hit["unit"], f"cache {hit['age_h']:.1f}h"
        return None, f"no baseline; est {est:.1f}c — pass --div-rate"
    return hit["unit"], f"cache {hit['age_h']:.1f}h"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", help="debug a single type search, then exit")
    ap.add_argument("--refresh", action="store_true",
                    help="force full re-pull of every price")
    ap.add_argument("--no-refresh", action="store_true",
                    help="offline: cache/overrides only, no API calls")
    ap.add_argument("--max-age", type=float, default=1.0,
                    help="staleness threshold in hours (default 1)")
    ap.add_argument("--div-rate", type=float, default=None,
                    help="manual chaos-per-divine (your in-game observed "
                         "rate beats any estimator; also re-baselines cache)")
    ap.add_argument("--ex-rate", type=float, default=None,
                    help="manual chaos-per-exalted")
    ap.add_argument("--no-snapshot", action="store_true",
                    help="skip writing the portfolio snapshot row")
    args = ap.parse_args()

    if args.probe:
        qid, ids, total = search_type(args.probe)
        print(f"total={total} ids={len(ids)}")
        return

    con = db()
    print(f"League: {LEAGUE} (single cross-platform pool) | "
          f"cache: {DB_PATH} | max-age: {args.max_age}h"
          + (" | OFFLINE" if args.no_refresh else "")
          + (" | FORCE-REFRESH" if args.refresh else ""))

    if args.div_rate:
        store(con, "rate:divine_chaos", args.div_rate, -1, "manual-override")
        div_c, div_src = args.div_rate, "manual-override"
    else:
        div_c, div_src = resolve_rate(con, "rate:divine_chaos", None,
                                      args.max_age, args.refresh,
                                      args.no_refresh)
    if not args.no_refresh:
        _paced()
    if args.ex_rate:
        store(con, "rate:exalted_chaos", args.ex_rate, -1, "manual-override")
        ex_c, ex_src = args.ex_rate, "manual-override"
    else:
        ex_c, ex_src = resolve_rate(con, "rate:exalted_chaos", None,
                                    args.max_age, args.refresh,
                                    args.no_refresh)
    print(f"divine = {div_c:.2f}c [{div_src}]" if div_c
          else "divine rate UNAVAILABLE")
    print(f"exalted = {ex_c:.2f}c [{ex_src}]" if ex_c
          else "exalted UNAVAILABLE")
    rates = {}
    if div_c:
        rates["divine"] = div_c
    if ex_c:
        rates["exalted"] = ex_c

    print(f"\n{'holding':38s} {'qty':>4s} {'unit/c':>9s} "
          f"{'value/c':>10s}  src")
    total_c = 0.0
    lines = []
    completed = True
    try:
        for label, qty, query, override in HOLDINGS:
            if label == "Divine Orb":
                unit, src = div_c, "numeraire"
            elif label == "flat Chaos Orb":
                unit, src = 1.0, "face"
            elif query is not None:
                key = f"item:{query}"
                hit = cached(con, key)
                if (args.refresh or hit is None
                        or hit["age_h"] > args.max_age):
                    if args.no_refresh:
                        unit = override or (hit["unit"] if hit else None)
                        src = "manual/offline"
                    else:
                        unit, n_list = pull_item_median(query, rates)
                        _paced()
                        if unit is None:
                            unit = override
                            src = (f"OVERRIDE (only {n_list} listings)"
                                   if override else "NO-DATA")
                        else:
                            store(con, key, unit, n_list, "market")
                            src = f"live (n~{n_list})"
                else:
                    unit, src = (hit["unit"],
                                 f"cache {hit['age_h']:.1f}h")
            else:
                unit, src = override, "manual"
            if unit is None:
                print(f"{label:38s} {qty:>4d} {'NO-DATA':>9s}")
                lines.append((label, qty, None, None, "NO-DATA"))
                continue
            total_c += qty * unit
            print(f"{label:38s} {qty:>4d} {unit:>9.2f} "
                  f"{qty * unit:>10.2f}  {src}")
            lines.append((label, qty, unit, qty * unit, src))
    except KeyboardInterrupt:
        print("\ninterrupted — partial total, cache kept.", file=sys.stderr)
        completed = False

    total_d = total_c / div_c if div_c else None
    voices_pct = (total_d / VOICES_TARGET_D * 100
                  if total_d else None)
    print(f"\nTOTAL {total_c:.1f}c", end="")
    if total_d:
        print(f" = {total_d:.1f}d "
              f"({voices_pct:.0f}% of {VOICES_TARGET_D:.0f}d Voices)")
    else:
        print()

    if completed and not args.no_snapshot:
        cur = con.execute(
            "INSERT INTO snapshots (taken_at, total_chaos, total_div,"
            " div_rate, div_src, voices_pct)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (now_iso(), round(total_c, 1), total_d, div_c, div_src,
             voices_pct))
        sid = cur.lastrowid
        con.executemany(
            "INSERT INTO snapshot_lines"
            " (snapshot_id, label, qty, unit_chaos, value_chaos, src)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [(sid, lb, q, u, v, s) for lb, q, u, v, s in lines])
        con.commit()
        print(f"[snapshot #{sid} recorded]")


if __name__ == "__main__":
    main()
