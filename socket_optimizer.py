"""Greedy jewel socket optimizer for the Soulwrest Phantasm Necromancer.

Feeds a starting DPS frame (flat, inc, cast from tree + equipment + auras +
gems, plus the single Amanamu's Gaze baseline jewel) and a list of jewels. It
recomputes four marginal DPS deltas -- flat, inc, cast, dot -- from the real
bossing DPS engine *on every selection step* against the currently-socketed
set, then picks the best jewel for the current priority slot. There is no
flat-normalization: a jewel's score is its actual contribution to total cursed
bossing DPS, in "DPS-point" units where 1 point = 0.01% of the total.

Selection priority (belt = x2.21 on every stat, tree = x1.0):
    1,2    two non-pc DPS jewels            (highest DPSL, tree)
    3,4    two belt pc jewels               (highest belt-DPSL)
    5,6,7  three non-belt pc jewels         (highest DPSL)
    8      last non-pc DPS jewel            (highest DPSL)

Poison chance is always assumed capped (pc = 100%) when computing deltas -- it
is a guaranteed-achievable constraint, so dot is valued from the first step.
DPSL = DPS points + life/ES points, where +1 life and +1 es are each valued by
their effective-HP contribution (x inc_life / inc_es) as a % of total EHP, in
the SAME 0.01%-of-total units as the DPS points (see DPSWeights.pt_life/pt_es).

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
class DPSWeights:
    """Absolute marginal DPS deltas (cursed bossing total) per unit of each mod.

    Everything is expressed in "DPS-point" units where 1 point = 0.01% of the
    total cursed bossing DPS (so the whole build == 10000 points). A jewel's
    DPS = flat·d_flat + inc·d_inc + cast·d_cast + dot·d_dot. There is NO flat
    normalization -- the score is the jewel's real impact on total DPS.
    """
    total: float            # total cursed bossing DPS (absolute)
    d_flat: float           # absolute DPS gained by +1 flat
    d_inc: float            # absolute DPS gained by +1% inc
    d_cast: float           # absolute DPS gained by +1% cast
    d_dot: float            # absolute DPS gained by +1% dot
    base_life: float        # non-jewel base life (before inc_life)
    base_es: float          # non-jewel base es (before inc_es)
    inc_life: float         # % increased life
    inc_es: float           # % increased es
    base_es_regen: float    # total ES regen / s (pool for 0.01% scaling)
    base_life_regen: float  # total life regen / s (pool for 0.01% scaling)

    def scale(self, val: float) -> float:
        """Convert an absolute-DPS delta into DPS-points (1 pt = 0.01% of total)."""
        if self.total <= 0:
            return 0.0
        return val / (self.total * 0.0001)

    @property
    def pt_flat(self) -> float: return self.scale(self.d_flat)
    @property
    def pt_inc(self) -> float: return self.scale(self.d_inc)
    @property
    def pt_cast(self) -> float: return self.scale(self.d_cast)
    @property
    def pt_dot(self) -> float: return self.scale(self.d_dot)

    @property
    def total_ehp(self) -> float:
        """Total effective life+es pool (base x inc multipliers)."""
        return (self.base_life * (1 + self.inc_life / 100)
                + self.base_es * (1 + self.inc_es / 100))

    @property
    def pt_life(self) -> float:
        """DPS-points worth of +1 life: its +EHP as a % of total EHP, same 0.01% units."""
        if self.total_ehp <= 0:
            return 0.0
        return (1 + self.inc_life / 100) / (self.total_ehp * 0.0001)

    @property
    def pt_es(self) -> float:
        """DPS-points worth of +1 es (same 0.01% units as +1 life and DPS)."""
        if self.total_ehp <= 0:
            return 0.0
        return (1 + self.inc_es / 100) / (self.total_ehp * 0.0001)

    @property
    def pt_es_regen(self) -> float:
        """DPS-points worth of +1 ES regen / s (0.01% of total ES regen)."""
        if self.base_es_regen <= 0:
            return 0.0
        return 1.0 / (self.base_es_regen * 0.0001)

    @property
    def pt_life_regen(self) -> float:
        """DPS-points worth of +1 life regen / s (0.01% of total life regen)."""
        if self.base_life_regen <= 0:
            return 0.0
        return 1.0 / (self.base_life_regen * 0.0001)


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
    es_regen: float = 0.0
    life_regen_pct: float = 0.0

    @property
    def dps_mods(self) -> bool:
        return (self.flat > 0 or self.inc > 0 or self.cast > 0 or self.dot > 0)

    @property
    def is_pc(self) -> bool:
        return self.pc > 0

    def dps(self, w: DPSWeights, mult: float, incl_life_es: bool = True) -> float:
        """DPS-points contributed by this jewel at belt/tree scaling.

        Damage portion scales by pt_flat/pt_inc/pt_cast/pt_dot. When
        incl_life_es, life, ES, and regen are valued at their effective-HP /
        regen point worth (pt_life/pt_es/pt_es_regen/pt_life_regen) -- the same
        0.01%-of-total units as the DPS points. % life regen converts to flat/s
        via the current base life (w.base_life).
        """
        dmg = mult * (self.flat * w.pt_flat
                      + self.inc * w.pt_inc
                      + self.cast * w.pt_cast
                      + self.dot * w.pt_dot)
        if not incl_life_es:
            return dmg
        life_regen = self.life_regen_pct / 100.0 * w.base_life  # flat life / s
        surv = mult * (self.life * w.pt_life + self.es * w.pt_es
                       + self.es_regen * w.pt_es_regen
                       + life_regen * w.pt_life_regen)
        return dmg + surv


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
            es_regen=float(r["es_regen"] or 0.0),
            life_regen_pct=float(r["life_regen_pct"] or 0.0),
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


def dps_weights(f: Frame, base_life: float = 1830.0, base_es: float = 735.0,
                inc_life: float = 151.6, inc_es: float = 112.7,
                base_es_regen: float = 686.3, base_life_regen: float = 136.6) -> DPSWeights:
    """Absolute marginal DPS deltas, measured against the total cursed bossing DPS.

    Poison chance is assumed capped (pc = 100%) for weighting -- it is a build
    constraint guaranteed by the end, so early selections must not discount
    dot merely because pc jewels are not socketed yet.
    """
    eff = Frame(
        name="w", flatsum=dict(f.flatsum), inc=f.inc, cast=f.cast,
        poison_chance=1.0,
        amanamu_dot_pool=f.amanamu_dot_pool, curse=f.curse,
    )
    base = _engine(eff).total_cursed

    def delta(apply) -> float:
        g = Frame(
            name="w", flatsum=dict(f.flatsum), inc=f.inc, cast=f.cast,
            poison_chance=1.0,
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

    return DPSWeights(total=base, d_flat=dflat, d_inc=dinc, d_cast=dcast, d_dot=ddot,
                      base_life=base_life, base_es=base_es,
                      inc_life=inc_life, inc_es=inc_es,
                      base_es_regen=base_es_regen, base_life_regen=base_life_regen)


def run(db_path: str, belt_mult: float, flat: float, inc: float, cast: float,
        base_life: float = 1830.0, base_es: float = 735.0,
        inc_life: float = 151.6, inc_es: float = 112.7,
        base_es_regen: float = 686.3, base_life_regen: float = 136.6,
        seed_tree: list[str] | None = None,
        verbose: bool = True) -> None:
    jewels = load_jewels(db_path)
    # baseline flat chunk (amanamu ag-0-attr adds 0)
    flat_chunks = {"baseline": flat}

    belt: list[Jewel] = []
    tree: list[Jewel] = []
    picked: set[str] = set()

    # Pre-socket fixed jewels (e.g. a chaos-res-cap jewel) on the tree. They
    # occupy non-pc tree slots, reducing the number of 'dps' picks below.
    for sid in (seed_tree or []):
        if sid not in jewels:
            raise ValueError(f"unknown seed jewel: {sid}")
        tree.append(jewels[sid])
        picked.add(sid)

    # Priority: (slot_type, belt_or_tree)
    #   'dps'      -> non-pc jewel, tree
    #   'belt_pc'  -> pc jewel, belt
    #   'nonbelt_pc'-> pc jewel, tree
    # 1 DPS-point = 0.01% of total cursed bossing DPS; life/ES use the same
    # 0.01%-of-total-EHP units (see DPSWeights.pt_life / pt_es).

    def cur_w() -> DPSWeights:
        return dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult),
                           base_life=base_life, base_es=base_es,
                           inc_life=inc_life, inc_es=inc_es,
                           base_es_regen=base_es_regen, base_life_regen=base_life_regen)

    def best_dps(avail) -> Jewel:
        w = cur_w()
        return max(avail, key=lambda j: j.dps(w, 1.0))

    def best_belt_pc(avail) -> Jewel:
        w = cur_w()
        return max(avail, key=lambda j: j.dps(w, belt_mult))

    def best_tree_pc(avail) -> Jewel:
        w = cur_w()
        return max(avail, key=lambda j: j.dps(w, 1.0))

    # 6 flexible tree slots (7 minus Amanamu) + 2 belt. 3 of the 6 tree slots
    # must be pc (to cap 100 alongside the 2 belt pc). Seeded non-pc tree jewels
    # fill some of the remaining non-pc slots, so fewer 'dps' picks are needed.
    tree_pc_slots = 3          # nonbelt_pc
    belt_pc_slots = 2          # belt_pc
    seed_nonpc = sum(1 for j in tree if not j.is_pc)
    tree_dps_slots = (6 - tree_pc_slots) - seed_nonpc  # remaining non-pc tree slots
    # Priority sequence (user's order): 1-2 non-pc DPS -> 3-4 belt pc -> 5-7
    # tree pc -> last non-pc DPS. Seeded non-pc jewels shrink the trailing dps
    # block; the pc blocks are fixed.
    dps_front = min(tree_dps_slots, 2)
    order = (["dps"] * dps_front
             + ["belt_pc"] * belt_pc_slots
             + ["nonbelt_pc"] * tree_pc_slots
             + ["dps"] * (tree_dps_slots - dps_front))

    if verbose:
        print(f"baseline flat={flat} inc={inc} cast={cast} belt_mult={belt_mult}"
              + (f" seeded_tree={tree}" if tree else ""))
        hdr = f"{'step':>4} {'slot':<10} {'jewel':<18} {'flat':>6} {'inc':>4} {'cast':>4} {'dot':>4} {'pc':>4} | "
        hdr += f"{'pt_flat':>7} {'pt_inc':>7} {'pt_cast':>8} {'pt_dot':>7} {'DPSL':>7}"
        print(hdr)
        print("-" * len(hdr))

    for step, slot in enumerate(order, 1):
        w = dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult),
                        base_life=base_life, base_es=base_es,
                        inc_life=inc_life, inc_es=inc_es,
                        base_es_regen=base_es_regen, base_life_regen=base_life_regen)
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
        w2 = dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult),
                         base_life=base_life, base_es=base_es,
                         inc_life=inc_life, inc_es=inc_es,
                         base_es_regen=base_es_regen, base_life_regen=base_life_regen)
        dl = chosen.dps(w2, mult)
        if verbose:
            print(
                f"{step:>4} {slot:<10} {chosen.id:<18} {chosen.flat:6.1f} "
                f"{chosen.inc:4.0f} {chosen.cast:4.0f} {chosen.dot:4.0f} {chosen.pc:4.0f} | "
                f"{w2.pt_flat:7.2f} {w2.pt_inc:7.2f} {w2.pt_cast:8.2f} {w2.pt_dot:7.2f} {dl:7.1f}"
            )

    if verbose:
        print("\nFinal socketed set (DPSL-ranked):")
        print("  belt:", ", ".join(j.id for j in belt))
        print("  tree:", ", ".join(j.id for j in tree))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", default="jewels.db")
    p.add_argument("--belt-mult", type=float, default=2.21)
    p.add_argument("--flat", type=float, default=DEFAULT_FLAT, help="non-jewel flat")
    p.add_argument("--inc", type=float, default=DEFAULT_INC, help="non-jewel inc pool %")
    p.add_argument("--cast", type=float, default=DEFAULT_CAST, help="non-jewel cast pool %")
    p.add_argument("--base-life", type=float, default=1830.0, help="non-jewel base life")
    p.add_argument("--base-es", type=float, default=735.0, help="non-jewel base es")
    p.add_argument("--inc-life", type=float, default=151.6, help="%% increased life")
    p.add_argument("--inc-es", type=float, default=112.7, help="%% increased es")
    p.add_argument("--base-es-regen", type=float, default=686.3, help="non-jewel ES regen/s")
    p.add_argument("--base-life-regen", type=float, default=136.6, help="non-jewel life regen/s")
    p.add_argument("--seed-tree", action="append", default=None,
                   help="jewel id to pre-socket on the tree (repeatable)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)
    run(args.db, args.belt_mult, args.flat, args.inc, args.cast,
        base_life=args.base_life, base_es=args.base_es,
        inc_life=args.inc_life, inc_es=args.inc_es,
        base_es_regen=args.base_es_regen, base_life_regen=args.base_life_regen,
        seed_tree=args.seed_tree, verbose=not args.quiet)


if __name__ == "__main__":
    main()