"""Bank ledger CLI: inventory snapshots + price observations + SQL valuation.

The user reports holdings in free text ("26 d", "17 cranium"); this tool
normalizes names via the `aliases` table and stores counts. Valuation is
pure SQL (see bank_schema.sql): latest price per item, staleness warning,
snapshot totals in chaos and divines.

Usage
  uv run python bank.py init                      # create bank.db + seed items
  uv run python bank.py snapshot "note" \\
      "Divine Orb=40" "Preserved Cranium=17" ...  # exact ids, or ...
  uv run python bank.py snapshot-free "note" < lines.txt   # free text, alias-resolved
  uv run python bank.py price "Preserved Cranium" 60.3 --src manual
  uv run python bank.py value [--snapshot N] [--max-age H]
  uv run python bank.py prices                     # latest price table
"""
from __future__ import annotations

import argparse
import datetime
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "bank.db"
SCHEMA_PATH = HERE / "bank_schema.sql"

# Canonical registry: (item_id, display, kind, [aliases...]).
# Aliases cover every shorthand the user has used in chat so far.
ITEMS = [
    ("Chaos Orb", "Chaos Orb", "currency",
     ["c", "chaos", "flat chaos", "flat chaos orb"]),
    ("Divine Orb", "Divine Orb", "currency",
     ["d", "div", "divine", "divines"]),
    ("Exalted Orb", "Exalted Orb", "currency",
     ["e", "ex", "exalt", "exalted", "exalted orb"]),
    ("Greater Exalted Orb", "Greater Exalted Orb", "currency",
     ["exalted iii", "exaltiii", "ex3", "exiii", "greater exalted",
      "exalted 3", "ex iii"]),
    ("Greater Chaos Orb", "Greater Chaos Orb", "currency",
     ["chaos iii", "chaosiii", "c3", "chaos3", "greater chaos", "chaos 3",
      "c iii"]),
    ("Orb of Annulment", "Orb of Annulment", "currency",
     ["annul", "annuls", "annulment", "orb of annulment"]),
    ("Orb of Chance", "Orb of Chance", "currency",
     ["chance orb", "chance orbs", "orb of chance"]),
    ("Fracturing Orb", "Fracturing Orb", "currency",
     ["fracturing", "fracturing orb"]),
    ("Perfect Jeweller's Orb", "Perfect Jeweller's Orb", "currency",
     ["perfect jeweller", "perfect jeweler", "perfect jeweller orb",
      "perfect jeweler orb"]),
    ("Cryptic Key", "Cryptic Key", "currency",
     ["cryptic key", "cryptic keys", "key", "keys"]),
    ("Simulacrum", "Simulacrum", "misc",
     ["simulacrum", "simu"]),
    ("Expedition Logbook", "Expedition Logbook", "misc",
     ["logbook", "logbooks", "expedition logbook"]),
    ("Preserved Cranium", "Preserved Cranium", "bone",
     ["cranium", "preserved cranium"]),
    ("Ancient Collarbone", "Ancient Collarbone", "bone",
     ["collarbone", "ancient collarbone"]),
    ("Omen of Sinistral Annulment", "Omen of Sinistral Annulment", "omen",
     ["sin annul", "sinistral annul", "sinistral annulment",
      "omen of sinistral annulment", "sinistral annulment"]),
    ("Omen of Dextral Annulment", "Omen of Dextral Annulment", "omen",
     ["dextral annul", "dextral annulment", "omen of dextral annulment"]),
    ("Omen of Dextral Erasure", "Omen of Dextral Erasure", "omen",
     ["erasure", "dextral erasure", "omen of dextral erasure",
      "dextal erasure"]),
    ("Omen of Whittling", "Omen of Whittling", "omen",
     ["whittling", "omen of whittling"]),
    ("Omen of Dextral Crystallisation", "Omen of Dextral Crystallisation",
     "omen", ["dextral crystal", "dextral crystals", "dextral cryst",
              "dextral crystallization", "dextral crystallisation",
              "omen of dextral crystallisation"]),
    ("Omen of Sinistral Crystallisation", "Omen of Sinistral Crystallisation",
     "omen", ["sin crystal", "sinistral crystal", "sinistral cryst",
              "sinistral crystallization", "sinistral crystallisation",
              "sinitral crystal", "omen of sinistral crystallisation"]),
    ("Omen of Abyssal Echoes", "Omen of Abyssal Echoes", "omen",
     ["echoes", "abyssal echoes", "omen of abyssal echoes", "echo"]),
    ("Omen of Light", "Omen of Light", "omen",
     ["light", "omen of light"]),
    ("Omen of Chance", "Omen of Chance", "omen",
     ["chance omen", "omen of chance"]),
    ("Omen of the Blessed", "Omen of the Blessed", "omen",
     ["blessed", "omen of the blessed"]),
    ("Chaotic rarity tablet", "Chaotic rarity tablet", "tablet",
     ["rarity", "chaotic rarity", "rarity tablet"]),
    ("Chaotic quantity tablet", "Chaotic quantity tablet", "tablet",
     ["quantity", "chaotic quantity", "quantity tablet"]),
    ("Chaotic monsters tablet", "Chaotic monsters tablet", "tablet",
     ["monsters", "chaotic monsters", "monsters tablet"]),
    ("Chaotic effectiveness tablet", "Chaotic effectiveness tablet", "tablet",
     ["effectiveness", "chaotic effectiveness", "effectiveness tablet"]),
    ("Liquid Melancholy", "Liquid Melancholy", "misc",
     ["melancholy", "liquid melancholy", "ancient melancholy",
      "ancient potent liquid melancholy"]),
    ("Masterwork Rune", "Masterwork Rune", "misc",
     ["masterwork", "masterwork rune", "masterwork runes"]),
]


def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def now_iso():
    return (datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"))


def cmd_init(_args):
    con = connect()
    con.executescript(SCHEMA_PATH.read_text())
    for item_id, display, kind, aliases in ITEMS:
        con.execute(
            "INSERT INTO items(item_id, display, kind) VALUES (?,?,?)"
            " ON CONFLICT(item_id) DO UPDATE SET display=excluded.display,"
            " kind=excluded.kind", (item_id, display, kind))
        for a in aliases:
            con.execute(
                "INSERT INTO aliases(alias, item_id) VALUES (?,?)"
                " ON CONFLICT(alias) DO UPDATE SET item_id=excluded.item_id",
                (a.strip().lower(), item_id))
    con.commit()
    n_items = con.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    n_alias = con.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
    print(f"bank.db ready: {n_items} items, {n_alias} aliases")
    con.close()


def resolve(con, raw):
    """Free text -> canonical item_id, or raise with candidates."""
    key = raw.strip().lower()
    row = con.execute("SELECT item_id FROM aliases WHERE alias=?",
                      (key,)).fetchone()
    if row:
        return row[0]
    row = con.execute("SELECT item_id FROM items WHERE item_id=?", (raw,)).fetchone()
    if row:
        return row[0]
    cands = con.execute(
        "SELECT alias FROM aliases WHERE alias LIKE ? LIMIT 8",
        (f"%{key}%",)).fetchall()
    hint = (", ".join(c[0] for c in cands) or "no close aliases")
    raise KeyError(f"unknown item {raw!r} (similar: {hint})")


PAIR_RE = re.compile(r"^\s*(.+?)\s*=\s*(\d+(?:\.\d+)?)\s*$")


def cmd_snapshot(args):
    con = connect()
    lines = []
    for pair in args.lines:
        m = PAIR_RE.match(pair)
        if not m:
            raise SystemExit(f"bad line (want Name=qty): {pair!r}")
        item_id = resolve(con, m.group(1))
        lines.append((item_id, float(m.group(2))))
    cur = con.execute(
        "INSERT INTO inventory_snapshots(taken_at, note) VALUES (?, ?)",
        (now_iso(), args.note))
    sid = cur.lastrowid
    con.executemany(
        "INSERT INTO inventory_lines(snapshot_id, item_id, qty)"
        " VALUES (?,?,?)", [(sid, i, q) for i, q in lines])
    con.commit()
    print(f"inventory snapshot #{sid}: {len(lines)} lines")
    con.close()


def cmd_price(args):
    con = connect()
    item_id = resolve(con, args.item)
    con.execute(
        "INSERT INTO prices(item_id, unit_chaos, n, src, fetched_at)"
        " VALUES (?,?,?,?,?)",
        (item_id, args.unit, args.n, args.src, now_iso()))
    con.commit()
    print(f"price: {item_id} = {args.unit}c [{args.src}]")
    con.close()


def cmd_value(args):
    con = connect()
    if args.max_age is not None:
        con.execute("UPDATE config SET value=? WHERE key='price_max_age_h'",
                    (str(args.max_age),))
    sid = args.snapshot
    if sid is None:
        row = con.execute("SELECT MAX(id) FROM inventory_snapshots").fetchone()
        sid = row[0]
        if sid is None:
            raise SystemExit("no inventory snapshots yet")
    max_age = con.execute(
        "SELECT value FROM config WHERE key='price_max_age_h'").fetchone()[0]
    print(f"snapshot #{sid} (max-age {max_age}h)")
    print(f"{'item':36s} {'qty':>6s} {'unit/c':>9s} "
          f"{'value/c':>10s}  flags")
    for r in con.execute(
            "SELECT item_id, qty, unit_chaos, value_chaos, price_age_h,"
            " price_src, is_missing, is_stale FROM snapshot_value"
            " WHERE snapshot_id=? ORDER BY value_chaos DESC", (sid,)):
        item_id, qty, unit, val, age, src, missing, stale = r
        flags = []
        if missing:
            flags.append("NO-PRICE")
        elif stale:
            flags.append(f"STALE {age:.1f}h")
        print(f"{item_id:36s} {qty:>6g} "
              f"{(f'{unit:.2f}' if unit is not None else '-'):>9s} "
              f"{(f'{val:.1f}' if val is not None else '-'):>10s}  "
              f"{' '.join(flags)}")
    t = con.execute(
        "SELECT total_chaos, total_div, voices_pct, n_missing, n_stale"
        " FROM snapshot_totals WHERE snapshot_id=?", (sid,)).fetchone()
    print(f"\nTOTAL {t[0]:.1f}c", end="")
    if t[1]:
        print(f" = {t[1]:.1f}d ({t[2]:.0f}% of Voices)", end="")
    print(f"  [missing={t[3]} stale={t[4]}]")
    con.close()


def cmd_prices(_args):
    con = connect()
    for r in con.execute(
            "SELECT item_id, unit_chaos, n, src, fetched_at, age_h, is_stale"
            " FROM latest_prices ORDER BY item_id"):
        flag = "STALE" if r[6] else ""
        print(f"{r[0]:36s} {r[1]:>9.2f}c  n={r[2]:<4} {r[3]:20s} {flag}")
    con.close()


def cmd_buy(args):
    con = connect()
    item_id = resolve(con, args.item)
    con.execute(
        "INSERT INTO lots (item_id, qty_bought, qty_remaining,"
        " unit_cost_chaos, acquired_at, note)"
        " VALUES (?,?,?,?,?,?)",
        (item_id, args.qty, args.qty, args.at, now_iso(), args.note))
    con.commit()
    print(f"lot: {args.qty:g} x {item_id} @ "
          f"{args.at if args.at is not None else 'UNKNOWN'}c"
          + (f" ({args.note})" if args.note else ""))
    con.close()


def cmd_sell(args):
    """FIFO disposal; captures realized P&L against lot costs."""
    con = connect()
    item_id = resolve(con, args.item)
    need = args.qty
    cost_sum, matched = 0.0, 0.0
    lots = con.execute(
        "SELECT id, qty_remaining, unit_cost_chaos FROM lots"
        " WHERE item_id=? AND qty_remaining > 0 ORDER BY id",
        (item_id,)).fetchall()
    for lid, rem, cost in lots:
        if need <= 0:
            break
        take = min(rem, need)
        con.execute("UPDATE lots SET qty_remaining=? WHERE id=?",
                    (rem - take, lid))
        if cost is not None:
            cost_sum += take * cost
            matched += take
        need -= take
    if need > 0:
        # selling more than based lots: record the excess unbased
        con.execute(
            "INSERT INTO lots (item_id, qty_bought, qty_remaining,"
            " unit_cost_chaos, acquired_at, note)"
            " VALUES (?,?,0,NULL,?,'auto: oversell')",
            (item_id, need, now_iso()))
    avg = cost_sum / matched if matched else None
    pnl = (args.at - avg) * (args.qty - need) if avg is not None else None
    con.execute(
        "INSERT INTO realized (item_id, qty, unit_price_chaos,"
        " unit_cost_chaos, pnl_chaos, sold_at, note)"
        " VALUES (?,?,?,?,?,?,?)",
        (item_id, args.qty - need, args.at, avg, pnl, now_iso(), args.note))
    con.commit()
    print(f"sold {args.qty - need:g} x {item_id} @ {args.at}c"
          + (f", avg cost {avg:.2f}c, realized {pnl:+.1f}c"
             if pnl is not None else ", UNBASED part")
          + (f" ({args.note})" if args.note else ""))
    con.close()


def cmd_pnl(_args):
    con = connect()
    print(f"{'item':36s} {'based':>6s} {'avg cost':>9s} "
          f"{'latest':>9s} {'unrealized':>11s}")
    total = 0.0
    for r in con.execute(
            "SELECT item_id, based_qty, avg_cost, latest,"
            " unrealized_chaos, unrealized_pct FROM position_pnl"
            " ORDER BY unrealized_chaos DESC"):
        total += r[4] or 0.0
        pct = f" ({r[5]:+.0f}%)" if r[5] is not None else ""
        print(f"{r[0]:36s} {r[1]:>6g} {r[2]:>9.2f} {r[3]:>9.2f} "
              f"{r[4]:>+11.1f}{pct}")
    print(f"\nUNREALIZED TOTAL {total:+.1f}c")
    rt = con.execute(
        "SELECT COALESCE(SUM(pnl_chaos),0), COUNT(*) FROM realized"
        " WHERE pnl_chaos IS NOT NULL").fetchone()
    print(f"REALIZED TOTAL {rt[0]:+.1f}c over {rt[1]} sales")
    con.close()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("snapshot")
    p.add_argument("note")
    p.add_argument("lines", nargs="+", help="Item=qty ...")
    p = sub.add_parser("price")
    p.add_argument("item")
    p.add_argument("unit", type=float)
    p.add_argument("--src", default="manual")
    p.add_argument("--n", type=int, default=-1)
    p = sub.add_parser("value")
    p.add_argument("--snapshot", type=int, default=None)
    p.add_argument("--max-age", type=float, default=None)
    p = sub.add_parser("buy")
    p.add_argument("item")
    p.add_argument("qty", type=float)
    p.add_argument("--at", type=float, default=None,
                   help="unit cost in chaos (omit = unknown basis)")
    p.add_argument("--note", default="")
    p = sub.add_parser("sell")
    p.add_argument("item")
    p.add_argument("qty", type=float)
    p.add_argument("--at", type=float, required=True,
                   help="unit sale price in chaos")
    p.add_argument("--note", default="")
    sub.add_parser("pnl")
    sub.add_parser("prices")
    args = ap.parse_args()
    try:
        {"init": cmd_init, "snapshot": cmd_snapshot, "price": cmd_price,
         "value": cmd_value, "prices": cmd_prices, "buy": cmd_buy,
         "sell": cmd_sell, "pnl": cmd_pnl}[args.cmd](args)
    except KeyError as e:
        print(f"normalization needed: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
