"""Greedy jewel socket optimizer for the Soulwrest Phantasm Necromancer.

Feeds a starting DPS frame (flat, inc, cast from tree + equipment + auras +
gems, plus the single Amanamu's Gaze baseline jewel) and a list of jewels. It
recomputes the four equal-equivalency (EQ) weights -- flat, inc, cast, dot --
*on every selection step* against the currently-socketed set, then picks the
best jewel for the current priority slot.

Selection priority (belt = x2.21 on every stat, tree = x1.0):
    1,2    two non-pc DPS jewels            (highest EQ, tree)
    3,4    two belt pc jewels               (highest belt-EQ)
    5,6,7  three non-belt pc jewels         (highest tree-EQ)
    8      last non-pc DPS jewel            (highest EQ, tree)

EQ weights are derived by numerically perturbing the full bossing DPS engine
(+1 flat / +1% inc / +1% cast / +1% dot), normalized so flat = 1.0. This makes
the weights drift correctly as the socketed pool grows (the dot weight depends
on the hit/poison split, which shifts each step).

Usage:
    uv run python socket_optimizer.py
    uv run python socket_optimizer.py --db jewels.db --belt-mult 2.21
"""
from __future__ import annotations
from dataclasses import dataclass, field
import argparse
import sqlite3

from soulwrest_dps import Frame, avg_flat, compute_boss_dps as _engine

# Baseline (non-jewel) frame inputs -- derived from
# Phantomastress_202608130159_expanded.json: tree + gear + auras + gems, with
# the single Amanamu's Gaze (ag-0-attr, 0 flat/inc/cast) already present.
DEFAULT_FLAT = 230.5        # envy 106 + staff Soulwrest 124.5 (non-jewel)
DEFAULT_INC = 325.0         # non-jewel minion inc pool
DEFAULT_CAST = 86.0         # non-jewel minion cast pool


@dataclass
class Jewel:
    id: str
    name: str
    flat: float
    inc: float
    cast: float
    dot: float
    pc: float
    life: float
    es: float

    @property
    def dps_mods(self) -> bool:
        return (self.flat > 0 or self.inc > 0 or self.cast > 0 or self.dot > 0)

    @property
    def is_pc(self) -> bool:
        return self.pc > 0

    def eq(self, w_flat: float, w_inc: float, w_cast: float, w_dot: float,
           mult: float) -> float:
        """Flat-equivalent score under current weights, at belt/tree scaling."""
        return mult * (self.flat * w_flat
                       + self.inc * w_inc
                       + self.cast * w_cast
                       + self.dot * w_dot)


def load_jewels(db_path: str) -> dict[str, Jewel]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    out = {}
    for r in con.execute("SELECT * FROM jewels"):
        out[r["id"]] = Jewel(
            id=r["id"], name=r["name"],
            flat=avg_flat(r),
            inc=float(r["inc"] or 0.0),
            cast=float(r["cast"] or 0.0),
            dot=float(r["dot"] or 0.0),
            pc=float(r["pc"] or 0.0),
            life=float(r["life"] or 0.0),
            es=float(r["es"] or 0.0),
        )
    con.close()
    return out


def make_frame(flat_chunks: dict[str, float], inc: float, cast: float,
               belt_jewels: list[Jewel], tree_jewels: list[Jewel],
               belt_mult: float) -> Frame:
    """Build a Frame for the given socketed set (amanamu baseline presumed)."""
    flatsum = dict(flat_chunks)
    jinc = 0.0
    jcast = 0.0
    jpc = 0.0
    for j in belt_jewels:
        flatsum[f"jewel {j.id}"] = j.flat * belt_mult
        jinc += j.inc * belt_mult
        jcast += j.cast * belt_mult
        jpc += j.pc * belt_mult
    for j in tree_jewels:
        flatsum[f"jewel {j.id}"] = j.flat
        jinc += j.inc
        jcast += j.cast
        jpc += j.pc
    return Frame(
        name="opt",
        flatsum=flatsum,
        inc=inc + jinc,
        cast=cast + jcast,
        poison_chance=min(1.0, jpc / 100.0),
    )


def weights(f: Frame) -> dict[str, float]:
    """EQ weights from numeric perturbation; flat = 1.0."""
    base = _engine(f).total_cursed

    def delta(apply) -> float:
        g = Frame(
            name="w", flatsum=dict(f.flatsum), inc=f.inc, cast=f.cast,
            poison_chance=f.poison_chance,
            amanamu_dot_pool=f.amanamu_dot_pool, curse=f.curse,
        )
        apply(g)
        return _engine(g).total_cursed - base

    def eins(g):  # +1 flat
        g.flatsum.setdefault("perturb", 0.0)
        g.flatsum["perturb"] += 1.0
    dflat = delta(eins)

    def einc(g): g.inc += 1.0
    dinc = delta(einc)

    def ecst(g): g.cast += 1.0
    dcast = delta(ecst)

    def edot(g): g.amanamu_dot_pool += 0.01
    ddot = delta(edot)

    return {
        "flat": 1.0,
        "inc": dinc / dflat,
        "cast": dcast / dflat,
        "dot": ddot / dflat,
    }


def run(db_path: str, belt_mult: float, flat: float, inc: float, cast: float,
        verbose: bool = True) -> None:
    jewels = load_jewels(db_path)
    # baseline flat chunk (amanamu ag-0-attr adds 0)
    flat_chunks = {"baseline": flat}

    belt: list[Jewel] = []
    tree: list[Jewel] = []
    picked: set[str] = set()

    # Priority: (slot_type, belt_or_tree)
    #   'dps'      -> non-pc jewel, tree
    #   'belt_pc'  -> pc jewel, belt
    #   'nonbelt_pc'-> pc jewel, tree
    def best_dps(avail) -> Jewel:
        w = weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult))
        return max(avail, key=lambda j: j.eq(w["flat"], w["inc"], w["cast"], w["dot"], 1.0))

    def best_belt_pc(avail) -> Jewel:
        w = weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult))
        return max(avail, key=lambda j: j.eq(w["flat"], w["inc"], w["cast"], w["dot"], belt_mult))

    def best_tree_pc(avail) -> Jewel:
        w = weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult))
        return max(avail, key=lambda j: j.eq(w["flat"], w["inc"], w["cast"], w["dot"], 1.0))

    order = ["dps", "dps", "belt_pc", "belt_pc", "nonbelt_pc",
             "nonbelt_pc", "nonbelt_pc", "dps"]

    if verbose:
        print(f"baseline flat={flat} inc={inc} cast={cast} belt_mult={belt_mult}")
        hdr = f"{'step':>4} {'slot':<10} {'jewel':<18} {'flat':>6} {'inc':>4} {'cast':>4} {'dot':>4} {'pc':>4} | "
        hdr += f"{'w_flat':>6} {'w_inc':>6} {'w_cast':>7} {'w_dot':>6} {'EQ':>7}"
        print(hdr)
        print("-" * len(hdr))

    for step, slot in enumerate(order, 1):
        w = weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult))
        used = set(x.id for x in belt) | set(x.id for x in tree) | picked
        avail = [j for j in jewels.values() if j.id not in used]
        # only socketable DPS jewels are eligible; pure-utility (attrib/leech)
        # and zero-value jewels never win a slot.
        candidate_pool = [j for j in avail if j.dps_mods]

        chosen = None
        if slot == "dps":
            avail_nonpc = [j for j in candidate_pool if not j.is_pc]
            chosen = best_dps(avail_nonpc)
        elif slot == "belt_pc":
            avail_pc = [j for j in candidate_pool if j.is_pc]
            chosen = best_belt_pc(avail_pc)
        else:  # nonbelt_pc
            avail_pc = [j for j in candidate_pool if j.is_pc]
            chosen = best_tree_pc(avail_pc)

        if chosen is None:
            print(f"step {step}: no eligible jewel for slot {slot}")
            break

        if slot == "belt_pc":
            belt.append(chosen)
            mult = belt_mult if slot == "belt_pc" else 1.0
        else:
            tree.append(chosen)
            mult = 1.0
        picked.add(chosen.id)

        # recompute weights AFTER adding (that is the point of the process)
        w2 = weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult))
        eq = chosen.eq(w2["flat"], w2["inc"], w2["cast"], w2["dot"], mult)
        if verbose:
            print(
                f"{step:>4} {slot:<10} {chosen.id:<18} {chosen.flat:6.1f} "
                f"{chosen.inc:4.0f} {chosen.cast:4.0f} {chosen.dot:4.0f} {chosen.pc:4.0f} | "
                f"{w2['flat']:6.2f} {w2['inc']:6.2f} {w2['cast']:7.2f} {w2['dot']:6.2f} {eq:7.1f}"
            )

    if verbose:
        print("\nFinal socketed set:")
        print("  belt:", ", ".join(j.id for j in belt))
        print("  tree:", ", ".join(j.id for j in tree))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", default="jewels.db")
    p.add_argument("--belt-mult", type=float, default=2.21)
    p.add_argument("--flat", type=float, default=DEFAULT_FLAT, help="non-jewel flat")
    p.add_argument("--inc", type=float, default=DEFAULT_INC, help="non-jewel inc pool %")
    p.add_argument("--cast", type=float, default=DEFAULT_CAST, help="non-jewel cast pool %")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)
    run(args.db, args.belt_mult, args.flat, args.inc, args.cast,
        verbose=not args.quiet)


if __name__ == "__main__":
    main()