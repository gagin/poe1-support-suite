"""Head-to-head: which jewel best fills a single fixed slot?

The greedy `socket_optimizer.py` is deliberately myopic (marginal-step) and can
assign slots badly (e.g. putting a low-flat pc jewel in the belt x2.21). This
script is the reliable alternative for "swap X for Y" decisions: you fix the
belt + tree structure and the non-jewel bases, then it ranks one-slot candidates
by their marginal contribution to total cursed bossing DPS.

Candidates are added one at a time to the *same* fixed frame, so rankings are
directly comparable. Pair it with derive_bases.py for the bases.

Usage:
    # use a snapshot for the belt/tree structure + non-jewel bases
    uv run python jewel_slot_compare.py --snapshot build_snapshots/<Char>_..._expanded.json wg-8-dot mg-14-lres-dot fp-9-life

    # or specify the structure and bases explicitly
    uv run python jewel_slot_compare.py --belt ei-19-pc,hs-20-pc-life \
        --tree ho-23-es-pc,ap-8,wg-17-life-es-pc,el-31-clres,fg-25-lres \
        --flat 230.5 --inc 289 --cast 96 --amanamu 1.30 wg-8-dot mg-14-lres-dot
"""
from __future__ import annotations

import argparse

import socket_optimizer as so
import derive_bases


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("candidates", nargs="+", help="jewel ids to rank for the slot")
    p.add_argument("--db", default="jewels.db")
    p.add_argument("--snapshot", help="derive structure + bases from a snapshot")
    p.add_argument("--belt", help="comma-separated fixed belt jewel ids")
    p.add_argument("--tree", help="comma-separated fixed tree jewel ids")
    p.add_argument("--remove", action="append", default=[],
                   help="jewel id to drop from the base structure before filling the "
                        "slot (repeatable) -- use for a swap test against the snapshot")
    p.add_argument("--flat", type=float)
    p.add_argument("--inc", type=float)
    p.add_argument("--cast", type=float)
    p.add_argument("--belt-mult", type=float, default=2.21)
    p.add_argument("--amanamu", type=float, default=1.0,
                   help="amanamu DoT pool (1.0 rare amulet, 1.30 Amanamu's Gaze)")
    p.add_argument("--base-life", type=float, default=None)
    p.add_argument("--base-es", type=float, default=None)
    p.add_argument("--checks", action="store_true",
                   help="also print frame checks (res/pc/life/es) for each candidate")
    args = p.parse_args(argv)

    jewels = so.load_jewels(args.db)

    if args.snapshot:
        b = derive_bases.derive(args.snapshot, db_path=args.db,
                                belt_mult=args.belt_mult)
        belt_ids, tree_ids = b["belt_ids"], b["tree_ids"]
        flat, inc, cast = b["flat"], b["inc"], b["cast"]
        base_life, base_es = b["base_life"], b["base_es"]
    else:
        if not (args.belt and args.tree):
            raise SystemExit("either --snapshot or both --belt and --tree are required")
        belt_ids = [x for x in args.belt.split(",") if x]
        tree_ids = [x for x in args.tree.split(",") if x]
        if args.flat is None or args.inc is None or args.cast is None:
            raise SystemExit("--flat/--inc/--cast required when not using --snapshot")
        flat, inc, cast = args.flat, args.inc, args.cast
        base_life = args.base_life
        base_es = args.base_es

    for c in args.candidates:
        if c not in jewels:
            raise SystemExit(f"unknown jewel id: {c}")

    # drop contested-slot jewels so the candidate fills exactly one free slot
    for r in args.remove:
        if r not in jewels:
            raise SystemExit(f"unknown --remove jewel id: {r}")
        if r in belt_ids:
            belt_ids.remove(r)
        elif r in tree_ids:
            tree_ids.remove(r)
        else:
            print(f"[note] --remove {r} not present in the structure")

    bl = [jewels[i] for i in belt_ids]
    tl = [jewels[i] for i in tree_ids]
    base = so._engine(so.make_frame({"baseline": flat}, inc, cast, bl, tl,
                                    args.belt_mult, amanamu_pool=args.amanamu)).total_cursed

    rows = []
    for c in args.candidates:
        if c in belt_ids or c in tree_ids:
            print(f"[skip] {c} occupies another fixed slot")
            continue
        t2 = tl + [jewels[c]]
        total = so._engine(so.make_frame({"baseline": flat}, inc, cast, bl, t2,
                                         args.belt_mult, amanamu_pool=args.amanamu)).total_cursed
        rows.append((total, c))
    rows.sort(reverse=True)

    print(f"base (slot empty): {base:,.0f}")
    print(f"belt: {', '.join(belt_ids)}")
    print(f"tree: {', '.join(tree_ids)}")
    print(f"bases: flat {flat}  inc {inc}  cast {cast}  amanamu {args.amanamu}")
    print()
    for total, c in rows:
        print(f"{c:<16} {total:,.0f}  (+{total - base:+,.0f})")

    if args.checks and rows:
        from soulwrest_dps import check_frame
        best = rows[0][1]
        f = so.make_frame({"baseline": flat}, inc, cast,
                          bl, tl + [jewels[best]], args.belt_mult,
                          amanamu_pool=args.amanamu)
        print(f"\nchecks for best ({best}):")
        print("  " + str(check_frame(f)))


if __name__ == "__main__":
    main()