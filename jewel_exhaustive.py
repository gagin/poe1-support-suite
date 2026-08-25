"""Exhaustive constrained jewel-set search for Phantomastress (Soulwrest phantasm poison).

Unlike socket_optimizer.py (greedy, marginal-step — can miss the global optimum
under the poison-chance constraint), this enumerates EVERY valid combination of
socketed ghastly-eye jewels against the full jewels.db pool and ranks them by
exact boss DPS (same math as soulwrest_dps.compute_boss_dps, inlined for speed).

Constraint structure (Phantomastress convention):
  belt  : 2 slots, both poison-chance jewels (pc >= --belt-min-pc, default 14)
  tree  : 3 poison-chance jewels (pc >= 12, or flat >= 40), then remaining
          sockets are pure-DPS jewels (pc == 0)
  fixed : Amanamu's Gaze (ag-0-attr) occupies the last tree socket
  global: total poison chance >= 100 (belt jewels count x2.21)

Speed: per-jewel stat vectors are precomputed in ONE db pass and the DPS formula
is inlined, so millions of combinations evaluate in seconds. Results were
cross-validated against soulwrest_dps.jewel_frame + compute_boss_dps.

NOTE on baselines: non-jewel gear contributions are derived from the (fixed)
build_frame_from_snapshot by SUBTRACTING load_jewels_from_db(equipped ids),
which reproduces the engine's math exactly for any candidate set. Safe since
the 2026-08-21 builder fixes (belt resolution, PassiveJewels double-count,
dot pool).

Usage:
  uv run python jewel_exhaustive.py [snapshot_path]
  (default snapshot: newest Phantomastress_*_expanded.json)
"""

import itertools
import json
import sqlite3
import sys
import time
from math import prod
from pathlib import Path

import phantasm_model as M
import soulwrest_dps as sw

DB = "jewels.db"
BELT_MULT = 2.21
COUNT = M.DEFAULT_COUNT           # Dark Monarch doubled, NO Congregation (bossing)
MORE = prod(M.POISON_MORE)        # MD/VM/CD/Predator/Prey (lvl-21 verified)
HIT_CRIT = M.HIT_CRIT_MULT
DUR = M.POISON_DUR_UNBOUND * M.TEMP_CHAINS_DUR_MULT   # Unbound (+65%) x Temp Chains (x1.40)
CURSE_HIT, CURSE_POISON = M.CURSE_MULTS["despair_tc"]   # Despair: -30% chaos res, +35% DoT taken
MALEV = M.MALEV                   # 20% more DoT x aura effect (Gen40+Sov10+chest12)
UNBOUND = M.UNBOUND_AILMENT_MORE  # "20% more Damage with Ailments" — poison only
TOP_N = 8

# vec/G field order
FLAT, INC, CAST, DOT, PC, LIFE, ES, COLD, FIRE, LTG, CHAOS = range(11)

EQ_BELT = ["ei-19-pc", "ho-23-es-pc"]
EQ_TREE = ["wg-17-life-es-pc", "ms-15-pc-strdx", "ap-8",
           "fg-25-lres", "el-31-clres", "wg-8-dot", "ag-0-attr"]
EXCLUDE = {"qu-0"}      # unique Quickening Covenant — not part of the search pool

# Non-jewel gear contributions are DERIVED from the snapshot frame by
# subtracting load_jewels_from_db(equipped ids). This is safe only since the
# 2026-08-21 fixes to build_frame_from_snapshot (hardcoded belt_order removed;
# PassiveJewels no longer double-counted in the gear-mod scan). If equips
# change, just re-run — derivation follows the snapshot.


def latest_snapshot() -> str:
    snaps = sorted(Path("build_snapshots").glob("Phantomastress_*_expanded.json"))
    if not snaps:
        raise SystemExit("no build_snapshots/Phantomastress_*_expanded.json found")
    return str(snaps[-1])


def avg(r, k):
    return ((r[f"{k}_l"] or 0) + (r[f"{k}_h"] or 0)) / 2


def vec(rows, jid, belt=False):
    r = rows[jid]
    m = BELT_MULT if belt else 1.0
    return (
        (avg(r, "phys") + avg(r, "chaos") + avg(r, "fire")) * m,
        (r["inc"] or 0) * m,
        (r["minion_cast_speed"] or 0) * m,
        (r["dot"] or 0) * m,
        (r["pc"] or 0) * m,
        (r["life"] or 0) * m,
        (r["es"] or 0) * m,
        (r["cold_res"] or 0) * m, (r["fire_res"] or 0) * m,
        (r["ltg_res"] or 0) * m, (r["chaos_res"] or 0) * m,
    )


def dps_of(v):
    """Inline compute_boss_dps (curse=despair_tc) over aggregated vector v."""
    flat, inc, cast, dot, pc = v[FLAT], v[INC], v[CAST], v[DOT], v[PC]
    per = (M.INTRINSIC + M.ADD_EFF * flat) * (1 + inc / 100)
    tr = M.BASE_APS * (1 + cast / 100) * COUNT
    hit = per * tr * MORE * HIT_CRIT * CURSE_HIT
    pool = M.amanamu_pool(dot)
    cpm = 1.0 + M.MINION_CRIT_CHANCE * M.CRIT_POISON_BONUS / pool
    ch = pc / 100.0 if pc < 100.0 else 1.0
    poi = (per * tr * M.POISON_BASE * DUR * ch * MORE * UNBOUND * pool * MALEV
           * cpm * CURSE_POISON)
    return hit + poi


def add(*vecs):
    return tuple(map(sum, zip(*vecs)))


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("snapshot", nargs="?", default=latest_snapshot())
    p.add_argument("--timeout", type=float, default=300.0,
                   help="abort the search after N seconds (partial results, default 300)")
    p.add_argument("--top", type=int, default=TOP_N, help="rows to print")
    args = p.parse_args()
    snap = args.snapshot
    print(f"snapshot: {snap}")

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = {r["id"]: dict(r) for r in db.execute("SELECT * FROM jewels")}

    # --- non-jewel gear contributions: derive from the (fixed) snapshot frame ---
    f_snap = sw.build_frame_from_snapshot(snap, db_path=DB, name="snap")
    jl_eq = sw.load_jewels_from_db(DB, EQ_BELT, EQ_TREE)
    G = (sum(v for k, v in f_snap.flatsum.items() if not k.startswith("jewel")),
         f_snap.inc - jl_eq.inc,
         f_snap.cast - jl_eq.cast,
         0.0, 0.0,
         f_snap.life - jl_eq.life,
         f_snap.es - jl_eq.es,
         f_snap.ele_res["cold"] - jl_eq.ele_res["cold"],
         f_snap.ele_res["fire"] - jl_eq.ele_res["fire"],
         f_snap.ele_res["lightning"] - jl_eq.ele_res["lightning"],
         f_snap.chaos_res - jl_eq.chaos_res)

    eq_tot = add(G, *[vec(rows, j, j in EQ_BELT) for j in EQ_BELT + EQ_TREE])
    eq_dps = dps_of(eq_tot)
    print(f"equipped: {eq_dps:,.0f}  (pc={eq_tot[PC]:.1f}, chaos={eq_tot[CHAOS]:.1f})")

    # --- candidate pools ---
    belt_pool = [j for j, r in rows.items() if j not in EXCLUDE and (r["pc"] or 0) >= 14]
    tpc_pool = [j for j, r in rows.items() if j not in EXCLUDE
                and ((r["pc"] or 0) >= 12 or (r["flat"] or 0) >= 40)]

    def score(j):
        r = rows[j]
        return ((r["flat"] or 0) + 4.0 * (r["minion_cast_speed"] or 0)
                + 3.0 * (r["inc"] or 0) + 5.3 * (r["dot"] or 0))

    tdps_pool = sorted([j for j, r in rows.items()
                        if j not in EXCLUDE and not (r["pc"] or 0)],
                       key=lambda j: -score(j))[:14]

    belt_combos = [(a, b, add(vec(rows, a, True), vec(rows, b, True)))
                   for a, b in itertools.combinations(belt_pool, 2)]
    tpc_combos = [(t, add(vec(rows, t[0]), vec(rows, t[1]), vec(rows, t[2])))
                  for t in itertools.combinations(tpc_pool, 3)]
    tdps_combos = [(t, add(vec(rows, t[0]), vec(rows, t[1]), vec(rows, t[2])))
                   for t in itertools.combinations(tdps_pool, 3)]
    print(f"searching {len(belt_combos)}x{len(tpc_combos)}x{len(tdps_combos)} "
          f"(belt_pc>=14, tree_pc>=12/flat>=40, dps top-{len(tdps_pool)})")

    t0, n, best = time.time(), 0, []
    deadline = t0 + args.timeout
    timed_out = False
    pairs_total = len(belt_combos) * len(tpc_combos)
    pairs_done, next_mark = 0, 0.1
    for ba, bb, vb in belt_combos:
        if time.time() > deadline and n:
            timed_out = True
            break
        for tp, vt in tpc_combos:
            if len({ba, bb, *tp}) != 5:
                continue
            base = add(vb, vt)
            if base[PC] + G[PC] < 100:
                continue
            for td, vd in tdps_combos:
                if len({ba, bb, *tp, *td}) != 8:
                    continue
                n += 1
                best.append((dps_of(add(base, vd, G)), ba, bb, tp, td))
        pairs_done += len(tpc_combos)
        frac = pairs_done / pairs_total
        if frac >= next_mark:
            print(f"  {min(frac, 1.0):>5.0%} done ({n:,} combos, "
                  f"{time.time() - t0:.0f}s)", flush=True)
            next_mark += 0.1
    best.sort(key=lambda x: -x[0])
    status = "PARTIAL — timeout hit" if timed_out else "complete"
    print(f"evaluated {n:,} combos in {time.time() - t0:.1f}s ({status})\n")

    for d, ba, bb, tp, td in best[:args.top]:
        mark = ("  <= equipped"
                if {ba, bb, *tp, *td} == {*EQ_BELT, *EQ_TREE} else "")
        print(f"{d:,.0f} ({d / eq_dps - 1:+.2%})  belt[{ba}+{bb}] "
              f"pc[{','.join(tp)}] dps[{','.join(td)}]{mark}")


if __name__ == "__main__":
    main()
