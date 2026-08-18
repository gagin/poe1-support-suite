"""Build-aspect sweep for the Soulwrest Necromancer.

Runs the greedy jewel optimizer across the three poison-vs-universal aspects to
find whether a mid-point (partial poison scaling) beats either extreme:

  amulet : rare (dot pool 1.0)            vs Amanamu's Gaze (pool 1.30)
  aura   : Anger (flat +no DoT more)      vs Malevolence (DoT more 1.28)
  support: Controlled Destruction (x1.39 more, both sides) vs Unbound (dur 3.3, poison)

Universal scaling (CD more, Anger flat) multiplies BOTH the hit and poison base;
poison-only scaling (Amanamu pool, Malevolence DoT, Unbound duration) multiplies
only the poison side. pc (poison chance) is a continuous jewel-derived variable
the greedy allocates freely. Output = best jewel set + DPS per combination.

Amanamu's Gaze is a unique jewel that OCCUPIES one tree socket (it competes with
a rare jewel for that slot): amanamu combos fit 8 rare jewels (2 belt + 6 tree)
plus the Amanamu itself, rare combos fit 9 rare jewels (2 belt + 7 tree). The
pure-cast unique qu-0 (16 cast, nothing else) is excluded -- real rares cap at
cast 6, and qu-0 is not a realistic option.
"""
from __future__ import annotations
import argparse

from soulwrest_dps import compute_boss_dps as _engine
from socket_optimizer import (make_frame, dps_weights, load_jewels, ANGER_FLAT)

FLAT_BASE = 230.5
INC_BASE = 379.0
CAST_BASE = 122.0
BELT_MULT = 2.21
EXCLUDE = {"qu-0"}


def greedy(db: str, amanamu_pool: float, poison_dur: float,
           malevolence_more: float, cd: bool, anger: bool):
    jewels = load_jewels(db)
    flat_chunks = {"baseline": FLAT_BASE}
    if anger:
        flat_chunks["anger"] = ANGER_FLAT
    belt, tree, used = [], [], set(EXCLUDE)
    amanamu_socket = amanamu_pool != 1.0

    def frame():
        return make_frame(flat_chunks, INC_BASE, CAST_BASE, belt, tree, BELT_MULT,
                          hit_only=True, returned=2.0, predator=True,
                          no_returned=True, amanamu_pool=amanamu_pool,
                          poison_dur=poison_dur, malevolence_more=malevolence_more,
                          cd=cd)

    slots = [("belt", BELT_MULT), ("belt", BELT_MULT)] + [("tree", 1.0)] * 7
    if amanamu_socket:
        slots = slots[:-1]  # Amanamu takes the 9th tree socket
    for _slot, mult in slots:
        w = dps_weights(frame(), hit_only=True, survival=0.0)
        pt = {"flat": w.pt_flat, "inc": w.pt_inc, "cast": w.pt_cast,
              "dot": w.pt_dot, "pc": w.pt_pc}
        best, bestscore = None, -1.0
        for j in jewels.values():
            if j.id in used:
                continue
            score = mult * (j.flat * pt["flat"] + j.inc * pt["inc"]
                            + j.cast * pt["cast"] + j.dot * pt["dot"]
                            + j.pc * pt["pc"])
            if score > bestscore:
                best, bestscore = j, score
        if best is None:
            break
        used.add(best.id)
        (belt if _slot == "belt" else tree).append(best)

    r = _engine(frame())
    return belt, tree, r.hit_cursed, r.poison_cursed, r.total_cursed, \
        frame().poison_chance


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="jewels.db")
    args = ap.parse_args()

    combos = []
    for amulet_name, pool in (("rare", 1.0), ("amanamu", 1.30)):
        for aura_name, mm, anger in (("anger", 1.0, True),
                                     ("malev", 1.28, False)):
            for sup_name, cd, dur in (("cd", True, 2.0),
                                      ("unbound", False, 3.3)):
                combos.append((f"{amulet_name}+{aura_name}+{sup_name}",
                               pool, dur, mm, cd, anger))

    print(f"{'combo':<24} {'hit':>11} {'poison':>11} {'total':>11} "
          f"{'pc%':>6}  set")
    results = []
    for name, pool, dur, mm, cd, anger in combos:
        belt, tree, hit, poi, tot, pc = greedy(
            args.db, pool, dur, mm, cd, anger)
        results.append((tot, name))
        print(f"{name:<24} {hit:>11,.0f} {poi:>11,.0f} {tot:>11,.0f} "
              f"{pc*100:>5.0f}%  belt:{','.join(b.id for b in belt)} "
              f"tree:{','.join(t.id for t in tree)}")

    results.sort(reverse=True)
    print(f"\nbest: {results[0][1]} @ {results[0][0]:,.0f}")


if __name__ == "__main__":
    main()
