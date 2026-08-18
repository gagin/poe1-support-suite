"""Analytical balance optimizer for the Soulwrest jewel set.

Model
-----
A stylised "average jewel" holds the mean of each damage stat over the jewel
pool (flat / inc / cast / pc / dot). Because the build sockets 9 jewels -- 7
tree (x1.0) + 2 belt (x2.21) -- the total pool for any stat is ~11.4x the
per-jewel average. By choosing specialised jewels you can skew each stat's pool
by a multiplier m_k in [0.5, 1.5] from its baseline (all-average-jewels) value.

Zero-sum budget (the simplification the user asked for): boosting one stat by
+d costs the same -d somewhere else, i.e. sum(m_k) == #stats is conserved. We
solve for the m_k that maximise total cursed bossing DPS, then fit an actual
jewel set whose aggregate profile matches that ideal balance as closely as
possible.

Assumptions (all tunable)
-------------------------
* pool multiplier ~11.4 (7 tree + 2 belt x2.21); use --pool to override.
* bounds [0.5, 1.5] per multiplier; --lo / --hi to override.
* hit-only engine params (Anger, Sniper's Mark, CD+Returned, Cull, no Amanamu,
  poison_dur 2.0). --poison keeps the full poison build instead.
"""
from __future__ import annotations
import argparse

from soulwrest_dps import Frame, compute_boss_dps as _engine
from socket_optimizer import load_jewels, ANGER_FLAT, CULL_MORE, _hit_more

STATS = ("flat", "inc", "cast", "pc", "dot")


def pool_means(jewels) -> dict[str, float]:
    n = len(jewels)
    return {k: sum(getattr(j, k) for j in jewels.values()) / n for k in STATS}


def max_pool(jewels, k: str, belt_mult: float, slots: int) -> float:
    """Real achievable ceiling: top `slots` jewels by stat k, top two belt-boosted."""
    top = sorted(jewels.values(), key=lambda j: -getattr(j, k))[:slots]
    return sum(getattr(j, k) * belt_mult for j in top[:2]) \
        + sum(getattr(j, k) for j in top[2:])


def dps_of(v: list[float], amanamu_pool: float = 1.0, poison_dur: float = 2.0,
           malevolence_more: float = 1.0, cd: bool = True) -> float:
    """Engine total_cursed for absolute jewel pools v = [flat,inc,cast,pc,dot]."""
    f = Frame(
        name="balance",
        flatsum={"base": 230.5, "anger": ANGER_FLAT, "jewel_pool": v[0]},
        inc=379.0 + v[1],
        cast=122.0 + v[2],
        poison_chance=min(1.0, v[3] / 100.0),
        amanamu_dot_pool=amanamu_pool + v[4] / 100.0,
        poison_dur=poison_dur,
        malevolence_more=malevolence_more,
        crit_chance=0.0 if cd else 0.05,
    )
    f.curse = "sniper"
    f.more = ([1.40, 1.35, 1.39, CULL_MORE] if cd
              else [1.40, 1.35, CULL_MORE])
    return _engine(f).total_cursed


def optimize(maxes: list[float], budget: float, start: list[float],
             start_step: float = 2.0, amanamu_pool: float = 1.0,
             poison_dur: float = 2.0, malevolence_more: float = 1.0,
             cd: bool = True):
    """Coordinate ascent on the conserved budget: v in [0,max], sum(v)==budget.

    Each pass tries all pair-wise transfers (a +d, b -d within caps) and keeps
    the best; step halves when a full pass yields no improvement.
    """
    def obj(v): return dps_of(v, amanamu_pool, poison_dur, malevolence_more, cd)
    cur = list(start)
    curv = obj(cur)
    step = start_step
    while step >= 0.1:
        best, bestv = cur, curv
        for a in range(len(STATS)):
            for b in range(len(STATS)):
                if a == b:
                    continue
                for d in (step, -step):
                    if not (0.0 <= cur[a] + d <= maxes[a]
                            and 0.0 <= cur[b] - d <= maxes[b]):
                        continue
                    trial = list(cur)
                    trial[a] += d
                    trial[b] -= d
                    tv = obj(trial)
                    if tv > bestv:
                        best, bestv = trial, tv
        if bestv <= curv + 1e-9:
            step /= 2
        cur, curv = best, bestv
    return cur, curv


def aggregate_frame(agg: dict[str, float], amanamu_pool: float,
                    poison_dur: float, malevolence_more: float, cd: bool) -> Frame:
    f = Frame(
        name="fit",
        flatsum={"base": 230.5, "anger": ANGER_FLAT, "jewel_pool": agg["flat"]},
        inc=379.0 + agg["inc"],
        cast=122.0 + agg["cast"],
        poison_chance=min(1.0, agg["pc"] / 100.0),
        amanamu_dot_pool=amanamu_pool + agg["dot"] / 100.0,
        poison_dur=poison_dur,
        malevolence_more=malevolence_more,
        crit_chance=0.0 if cd else 0.05,
    )
    f.curse = "sniper"
    f.more = ([1.40, 1.35, 1.39, CULL_MORE] if cd else [1.40, 1.35, CULL_MORE])
    return f


def fit_set(jewels, ideal: list[float], amanamu_pool: float, poison_dur: float,
            malevolence_more: float, cd: bool):
    """Greedily socket 9 jewels (2 belt x2.21 + 7 tree) to match the ideal pools.

    Each slot picks the unused jewel that minimises the weighted squared
    distance of the resulting aggregate to the target pool, weighting each stat
    by its current marginal point value (pt from dps_weights).
    """
    from socket_optimizer import dps_weights
    target = {k: mm for k, mm in zip(STATS, ideal)}
    belt: list = []
    tree: list = []
    used: set = set()
    agg = {k: 0.0 for k in STATS}
    slots = [("belt", 2.21), ("belt", 2.21)] + [("tree", 1.0)] * 7
    for _slot, mult in slots:
        w = dps_weights(aggregate_frame(agg, amanamu_pool, poison_dur,
                                        malevolence_more, cd),
                        hit_only=True, survival=0.0)
        pt = {"flat": w.pt_flat, "inc": w.pt_inc, "cast": w.pt_cast,
              "pc": w.pt_pc, "dot": w.pt_dot}
        best, bestscore = None, float("inf")
        for j in jewels.values():
            if j.id in used:
                continue
            score = sum(pt[k] * (agg[k] + getattr(j, k) * mult - target[k]) ** 2
                        for k in STATS)
            if score < bestscore:
                best, bestscore = j, score
        if best is None:
            break
        used.add(best.id)
        for k in STATS:
            agg[k] += getattr(best, k) * mult
        (belt if _slot == "belt" else tree).append(best)
    f = aggregate_frame(agg, amanamu_pool, poison_dur, malevolence_more, cd)
    val = _engine(f).total_cursed
    return belt, tree, agg, val


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--belt-mult", type=float, default=2.21)
    ap.add_argument("--slots", type=int, default=9,
                    help="total jewel slots (7 tree + 2 belt)")
    ap.add_argument("--amanamu-pool", type=float, default=1.30,
                    help="amanamu_dot_pool (1.0 rare .. 1.30 Amanamu)")
    ap.add_argument("--poison-dur", type=float, default=2.0,
                    help="poison_dur (2.0 no Unbound .. 3.3 Unbound)")
    ap.add_argument("--malevolence-more", type=float, default=1.28,
                    help="malevolence_more (1.0 Anger .. 1.28 Malevolence)")
    ap.add_argument("--no-cd", action="store_true",
                    help="drop Controlled Destruction (keep crits) for Unbound")
    ap.add_argument("--db", default="jewels.db")
    args = ap.parse_args()
    cd = not args.no_cd

    jewels = load_jewels(args.db)
    avg = pool_means(jewels)
    tree_slots = args.slots - 2
    pool = tree_slots + 2 * args.belt_mult            # 7 + 2x2.21 = ~11.42
    avg_pool = {k: pool * avg[k] for k in STATS}      # all-average baseline
    budget = sum(avg_pool.values())
    maxes = [max_pool(jewels, k, args.belt_mult, args.slots) for k in STATS]

    cfg = (args.amanamu_pool, args.poison_dur, args.malevolence_more, cd)
    v, val = optimize(maxes, budget, [avg_pool[k] for k in STATS],
                      amanamu_pool=args.amanamu_pool, poison_dur=args.poison_dur,
                      malevolence_more=args.malevolence_more, cd=cd)
    base = dps_of([avg_pool[k] for k in STATS], args.amanamu_pool,
                  args.poison_dur, args.malevolence_more, cd)

    print(f"{args.slots} slots (2 belt x{args.belt_mult}) -> pool ~{pool:.2f}x; "
          f"budget = {budget:.0f} (all-average); per-stat caps "
          f"{' '.join(f'{k}={m:.0f}' for k, m in zip(STATS, maxes))}")
    print(f"config: amanamu_pool={args.amanamu_pool} poison_dur={args.poison_dur} "
          f"malevolence_more={args.malevolence_more} cd={'on' if cd else 'off'}")
    print(f"average jewel: " + "  ".join(f"{k}={avg[k]:.2f}" for k in STATS))
    print(f"\nbaseline (all-average): {base:,.0f}")
    print(f"optimal allocation:      {val:,.0f}  (+{(val/base-1)*100:+.1f}%)")
    print(f"\n{'stat':<5} {'avg':>7} {'cap':>7} {'v*':>7} {'%cap':>6}")
    for k, vv, mx in zip(STATS, v, maxes):
        print(f"{k:<5} {avg_pool[k]:>7.1f} {mx:>7.1f} {vv:>7.1f} "
              f"{(vv/mx*100 if mx else 0):>5.0f}%")

    belt, tree, agg, fitval = fit_set(jewels, v, args.amanamu_pool,
                                      args.poison_dur, args.malevolence_more, cd)
    print(f"\n== fitted set (greedy to ideal balance) ==")
    print("  belt:", ", ".join(j.id for j in belt))
    print("  tree:", ", ".join(j.id for j in tree))
    print(f"  fitted total: {fitval:,.0f}   (target-optimal {val:,.0f})")
    print("  achieved pools vs target (effective units):")
    for k in STATS:
        print(f"    {k:<5} achieved={agg[k]:>7.1f}  target={v[STATS.index(k)]:>7.1f}  "
              f"diff={agg[k]-v[STATS.index(k)]:+7.1f}")


if __name__ == "__main__":
    main()
