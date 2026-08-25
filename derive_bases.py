"""Derive non-jewel baseline pools (flat / inc / cast / base-life / base-ES) from a snapshot.

This is Step 2 of the jewel-optimization workflow: strip all swappable jewels
from a fresh expanded snapshot to get the fixed base that socket_optimizer.py
adds jewel stats on top of. Belt jewels are resolved by signature (not by the
hardcoded socket order), so the belt pair can change without editing anything.

Use it every time gear or the tree drifts -- the bases do NOT stay constant
(see the operating manual, "Re-derive; these drift with gear/tree"). Feed the
outputs into socket_optimizer.py / jewel_slot_compare.py.

Usage:
    uv run python derive_bases.py build_snapshots/<Char>_YYYYMMDDHHMM_expanded.json
    uv run python derive_bases.py build_snapshots/<Char>_YYYYMMDDHHMM_expanded.json --db jewels.db
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3

import soulwrest_dps as sw

VAAL_HASTE_CAST = 24.0  # Vaal Haste aura grants 24% minion cast speed


def _mod_strings(item) -> list[str]:
    """Collapse an item/gem's mod dicts into plain strings (gem socketedGems use dicts)."""
    out: list[str] = []
    for f in sw._MOD_SOURCES:
        for m in item.get(f) or []:
            out.append(m["description"] if isinstance(m, dict) else str(m))
    return out


def _resolve_belt(snap, db_path: str) -> list[str]:
    """Resolve belt-socketed gems to jewels.db ids by signature, in socket order.

    The belt's Abyssal-socketed ghastly jewels carry their mods in
    `socketedGems` (dicts), so they are signature-matched like tree jewels
    rather than taken from a positional name->id map.
    """
    items = sw._all_items(snap)
    belt = next((it for it in items if it.get("inventoryId") == "Belt"), {})
    sockets = [g for g in (belt.get("socketedGems") or [])
               if isinstance(g, dict) and g.get("name")]

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    ids: list[str] = []
    for g in sockets:
        sig = sw._jewel_signature(_mod_strings(g))
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM jewels WHERE name = ?", (g["name"],)).fetchall()]
        best, best_score = None, 1e9
        for r in rows:
            cand = {"flat": r["flat"] or 0.0, "inc": r["inc"] or 0.0,
                    "cast": r["minion_cast_speed"] or 0.0, "life": r["life"] or 0.0,
                    "es": r["es"] or 0.0, "pc": r["pc"] or 0.0,
                    "hinder": r["hinder"] or 0.0}
            for k in ("cold", "fire", "lightning"):
                cand[k] = (r.get(k + "_res") or 0.0) + (r["all_res"] or 0.0)
            score = sum(abs(cand[k] - v) for k, v in sig.items())
            if score < best_score:
                best, best_score = r["id"], score
        ids.append(best)
    con.close()
    return ids


def _resolve_tree(snap, db_path: str) -> list[str]:
    """Resolve passive-tree ghastly jewels to ids by signature (dedup)."""
    ids: list[str] = []
    for it in sw._all_items(snap):
        if it.get("inventoryId") != "PassiveJewels":
            continue
        n = it.get("name")
        if not n:
            continue
        ident = sw._resolve_jewel(n, sw._jewel_signature(sw._item_mods(it)),
                                  db_path, None)
        if ident and ident not in ids:
            ids.append(ident)
    return ids


def derive(snapshot: str, db_path: str = "jewels.db", belt_mult: float = 2.21) -> dict:
    """Return the non-jewel baseline pools derived from `snapshot`.

    Returns a dict with: belt_ids, tree_ids, flat, inc, cast, base_life, base_es,
    plus the component breakdown (tree_inc, gear_inc, tree_cast, gear_cast,
    vaal_haste) and the resolved jewel flat/inc/cast.
    """
    snap = json.load(open(snapshot))
    items = sw._all_items(snap)

    belt_ids = _resolve_belt(snap, db_path)
    tree_ids = _resolve_tree(snap, db_path)
    jl = sw.load_jewels_from_db(db_path, belt_ids=belt_ids, tree_ids=tree_ids,
                                belt_mult=belt_mult)

    # non-jewel inc/cast: tree parse + gear-only scan (exclude socketed jewels,
    # whose own mods come from jewels.db and are added back by the optimizer).
    tree = sw._parse_tree(snap)
    inc = tree["inc"]
    cast = tree["cast"]
    gear_inc = 0.0
    gear_cast = 0.0
    for it in items:
        if it.get("inventoryId") == "PassiveJewels":
            continue
        for m in sw._item_mods(it):
            if re.match(r"Minions deal (\d+)% increased Damage", m):
                v = sw._num(m); inc += v; gear_inc += v
            if re.match(r"Minions have (\d+)% increased Cast Speed", m):
                v = sw._num(m); cast += v; gear_cast += v
            if re.match(r"Minions have (\d+)% increased Attack and Cast Speed", m):
                v = sw._num(m); cast += v; gear_cast += v
    cast += VAAL_HASTE_CAST

    flat = sum(sw._parse_flat(snap).values())

    # base life/es = frame flat pools minus jewel contributions
    frame = sw.build_frame_from_snapshot(snapshot, db_path=db_path,
                                         belt_order=belt_ids)
    base_life = frame.life - jl.life
    base_es = frame.es - jl.es

    return {
        "snapshot": snapshot,
        "belt_ids": belt_ids,
        "tree_ids": tree_ids,
        "flat": flat,
        "inc": inc,
        "cast": cast,
        "tree_inc": tree["inc"],
        "gear_inc": gear_inc,
        "tree_cast": tree["cast"],
        "gear_cast": gear_cast,
        "vaal_haste": VAAL_HASTE_CAST,
        "base_life": base_life,
        "base_es": base_es,
        "jewel_flat": sum(jl.to_flatsum_dict().values()),
        "jewel_inc": jl.inc,
        "jewel_cast": jl.cast,
        "belt_mult": belt_mult,
    }


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("snapshot", help="expanded snapshot JSON path")
    p.add_argument("--db", default="jewels.db")
    p.add_argument("--belt-mult", type=float, default=2.21)
    args = p.parse_args(argv)

    b = derive(args.snapshot, db_path=args.db, belt_mult=args.belt_mult)

    print(f"snapshot : {b['snapshot']}")
    print(f"belt     : {', '.join(b['belt_ids'])}")
    print(f"tree     : {', '.join(b['tree_ids'])}")
    print()
    print(f"non-jewel flat base : {b['flat']:.1f}")
    print(f"non-jewel inc pool  : {b['inc']:.2f}   (tree {b['tree_inc']:.1f} + gear {b['gear_inc']:.1f})")
    print(f"non-jewel cast pool : {b['cast']:.2f}   (tree {b['tree_cast']:.1f} + gear {b['gear_cast']:.1f} + VaalHaste {b['vaal_haste']:.0f})")
    print(f"non-jewel base life : {b['base_life']:.1f}")
    print(f"non-jewel base es   : {b['base_es']:.1f}")
    print(f"jewel load          : flat {b['jewel_flat']:.1f}  inc {b['jewel_inc']:.2f}  cast {b['jewel_cast']:.2f}  (belt x{b['belt_mult']})")


if __name__ == "__main__":
    main()