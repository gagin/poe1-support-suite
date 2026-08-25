"""Greedy jewel socket optimizer for the Soulwrest Phantasm Necromancer.

Feeds a starting DPS frame (flat, inc, cast from tree + equipment + auras +
gems, plus the single Amanamu's Gaze baseline jewel) and a list of jewels. It
recomputes marginal DPS deltas -- flat, inc, cast, dot, pc -- from the real
bossing DPS engine *on every selection step* against the currently-socketed
set, then picks the best jewel for the current priority slot. There is no
flat-normalization: a jewel's score is its actual contribution to total cursed
bossing DPS, in "DPS-point" units where 1 point = 0.01% of the total.

Baselines: the non-jewel flat/inc/cast pools are derived LIVE from the newest
expanded snapshot via phantasm_model (engine frame minus socketed-jewel
contribution). ``--snapshot`` pins a specific snapshot; ``--weapon-set 1|2``
chooses which weapon swap's staff/gems count (set 2 may have no minion-flat
weapon at all). Explicit ``--flat/--inc/--cast`` override derivation; if no
snapshot exists, the frozen BASELINE_* fallbacks in phantasm_model are used
with a printed notice. Model constants (support more-multipliers, curses,
auras) come from phantasm_model too — nothing numeric is defined in this file.

Selection priority (belt = x2.21 on every stat, tree = x1.0):
    1,2    two non-pc DPS jewels            (highest DPSL, tree)
    3,4    two belt pc jewels               (highest belt-DPSL)
    5,6,7  three non-belt pc jewels         (highest DPSL)
    8      last non-pc DPS jewel            (highest DPSL)

pc and dot are valued dynamically against the current set: a pc jewel earns its
+poison (poison is linear in chance) and a dot jewel only earns its amanamu-pool
effect to the extent poison is already socketed. So an early pc jewel is valued
for its flat/cast plus its pc; later pc jewels' marginal pc value is unchanged
(up to cap). DPSL = DPS points + life/ES points, where +1 life and +1 es are each
valued by their effective-HP contribution (x inc_life / inc_es) as a % of total
EHP, in the SAME 0.01%-of-total units as the DPS points (see DPSWeights.
pt_life/pt_es).

Usage:
    uv run python socket_optimizer.py                     # baselines from newest snapshot, weapon set 1
    uv run python socket_optimizer.py --weapon-set 2      # second swap (different staff/gems)
    uv run python socket_optimizer.py --db jewels.db --belt-mult 2.21
    uv run python socket_optimizer.py --flat 236.5 --inc 289 --cast 96    # pin manually
    uv run python socket_optimizer.py --hit-only          # glass-cannon variant
"""
from __future__ import annotations
from dataclasses import dataclass, field
import argparse
import sqlite3

from soulwrest_dps import Frame, avg_flat, compute_boss_dps as _engine
import phantasm_model as M
from phantasm_model import (BASELINE_FLAT as DEFAULT_FLAT,
                            BASELINE_INC as DEFAULT_INC,
                            BASELINE_CAST as DEFAULT_CAST)

# ---- HIT-ONLY variant (drops Amanamu/Unbound poison scaling) -------------- #
# Different auras, support gems and curses than the poison build. Poison chance
# from jewels is still honored (reduced layer); it is the *scaling* that's gone.
# Different auras, support gems and curses than the poison build:
#   AURA:  Malevolence(+Generosity)  -> Anger. Anger's fire flat converts to chaos
#          via Mind Claw (fire->chaos), scaled by the phantasm's 1.5 add-eff.
#   SUPP:  Unbound Ailments (poison) dropped; add Controlled Destruction (39% more
#          spell dmg) + Returned Projectiles (projectile hits out-and-back).
#   CURSE: Despair + Temporal Chains -> Despair + Sniper's Mark (2 curses via
#          Whispers of Doom); Sniper's Mark only boosts hit, which is all that's left.
ANGER_FLAT = M.ANGER_FLAT_GENEROSITY   # Anger x aura-effect stack (Gen+Sov+chest), fire->chaos
HIT_ONLY_CURSE = "sniper"          # engine curse key: hit x1.30 (Despair) x1.34 (Sniper)
# Amanamu's Gaze is NOT optional in the poison build: the +30% DoT-mult pool
# base (phantasm_model.AMANAMU_POOL_BASE) IS this jewel. It always occupies one
# tree socket, so the optimizer auto-seeds it and never offers it as a pick.
# (In hit-only mode the jewel is dropped and the pool base with it.)
AMANAMU_GAZE_ID = "ag-0-attr"
# Returned Projectiles realized multiplier is uncertain (see analysis): ~1.5
# conservative, ~2.0 optimistic. Tune via --returned.
CULL_MORE = M.CULL_MORE      # Culling Strike on the Cyclone trigger (always channelled): +11.1% more
def _hit_more(returned: float, predator: bool = True,
              no_returned: bool = False) -> list[float]:
    # Hit-only supports. CD (1.39) is the DPS-add; Returned Projectiles is a
    # question-mark (realized double-hit uncertain) and Predator is optional
    # (user drops it for ubers/mapping).
    more = [M.MD_MORE, M.VM_MORE, M.CD_MORE]  # MD, VM, CD
    if predator:
        more += [M.PREDATOR_MORE, M.PREY_MORE]   # Predator, Prey mark
    if not no_returned:
        more.append(returned)
    return more


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
    d_dot: float            # absolute DPS gained by +1% dot (amanamu pool)
    d_pc: float             # absolute DPS gained by +1% poison chance
    base_life: float        # non-jewel base life (before inc_life)
    base_es: float          # non-jewel base es (before inc_es)
    inc_life: float         # % increased life
    inc_es: float           # % increased es
    base_es_regen: float    # total ES regen / s (pool for 0.01% scaling)
    base_life_regen: float  # total life regen / s (pool for 0.01% scaling)
    regen_scale: float = 0.5  # ES is recharge (conditional on no recent dmg) and
                              # life regen only kicks in once ES is spent, so
                              # regen is worth roughly half of a flat pool.
    life_weight: float = 1.0  # multiplier on +life point value (survivability boost)
    survival: float = 1.0     # 0 disables ALL survival point value (life/es/regen) —
                              # the hit-only glass-cannon mode values damage only.

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
    def pt_pc(self) -> float: return self.scale(self.d_pc)

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
        return (1 + self.inc_life / 100) / (self.total_ehp * 0.0001) * self.life_weight * self.survival

    @property
    def pt_es(self) -> float:
        """DPS-points worth of +1 es (same 0.01% units as +1 life and DPS)."""
        if self.total_ehp <= 0:
            return 0.0
        return (1 + self.inc_es / 100) / (self.total_ehp * 0.0001) * self.survival

    @property
    def pt_es_regen(self) -> float:
        """DPS-points worth of +1 ES regen / s (0.01% of total ES regen)."""
        if self.base_es_regen <= 0:
            return 0.0
        return 1.0 / (self.base_es_regen * 0.0001) * self.survival

    @property
    def pt_life_regen(self) -> float:
        """DPS-points worth of +1 life regen / s (0.01% of total life regen)."""
        if self.base_life_regen <= 0:
            return 0.0
        return 1.0 / (self.base_life_regen * 0.0001) * self.survival


@dataclass
class Jewel:
    id: str          # user-facing code (e.g. "el-31-clres"), the stable display key
    uid: int         # numeric primary key (stable reference for eql/jewel_selections)
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
                      + self.dot * w.pt_dot
                      + self.pc * w.pt_pc)
        if not incl_life_es:
            return dmg
        life_regen = self.life_regen_pct / 100.0 * w.base_life  # flat life / s
        surv = mult * (self.life * w.pt_life + self.es * w.pt_es
                       + w.regen_scale * (self.es_regen * w.pt_es_regen
                                          + life_regen * w.pt_life_regen))
        return dmg + surv


def load_jewels(db_path: str) -> dict[str, Jewel]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    out = {}
    for r in con.execute("SELECT * FROM jewels"):
        out[r["id"]] = Jewel(
            id=r["id"], uid=r["uid"], name=r["name"],
            flat=avg_flat(r),
            inc=float(r["inc"] or 0.0),
            cast=float(r["minion_cast_speed"] or 0.0),
            dot=float(r["dot"] or 0.0),
            pc=float(r["pc"] or 0.0),
            life=float(r["life"] or 0.0) + (r["str"] or 0.0) / 2.0,
            es=float(r["es"] or 0.0),
            es_regen=float(r["es_regen"] or 0.0),
            life_regen_pct=float(r["life_regen_pct"] or 0.0),
        )
    con.close()
    return out


def make_frame(flat_chunks: dict[str, float], inc: float, cast: float,
               belt_jewels: list[Jewel], tree_jewels: list[Jewel],
               belt_mult: float, hit_only: bool = False,
               returned: float = 2.0, predator: bool = True,
               no_returned: bool = False,
               amanamu_pool: float = 1.0, poison_dur: float = 2.0,
               malevolence_more: float = 1.0, cd: bool = True,
               chaos_pen_bonus: float = 0.0,
               crit_chance: float = 0.05, crit_multi: float = 1.50,
               no_cull: bool = False, count: float | None = None) -> Frame:
    """Build a Frame for the given socketed set (amanamu baseline presumed).

    ``hit_only`` selects the dropped-poison-scaling support set (Sniper's Mark,
    Controlled Destruction + Returned Projectiles) but socketed pc still yields
    a reduced poison layer. Its poison params are parameterisable for the
    aspect sweep (amanamu vs rare, unbound vs CD, anger vs malevolence):

    * ``amanamu_pool``  -- 1.0 (rare amulet) .. 1.30 (Amanamu's Gaze)
    * ``poison_dur``    -- 2.0 (no Unbound) .. 3.3 (Unbound Ailments)
    * ``malevolence_more`` -- 1.0 (Anger) .. Malevolence value (model MALEV)
    * ``cd``            -- include Controlled Destruction's more (universal)
    * ``no_cull``       -- drop the Culling-Strike-on-Cyclone multiplier
    * ``count``         -- override phantasm count (e.g. 58 with Congregation)
    """
    flatsum = dict(flat_chunks)
    jinc = 0.0
    jcast = 0.0
    jpc = 0.0
    jdot = 0.0
    for j in belt_jewels:
        flatsum[f"jewel {j.id}"] = j.flat * belt_mult
        jinc += j.inc * belt_mult
        jcast += j.cast * belt_mult
        jpc += j.pc * belt_mult
        jdot += j.dot * belt_mult
    for j in tree_jewels:
        flatsum[f"jewel {j.id}"] = j.flat
        jinc += j.inc
        jcast += j.cast
        jpc += j.pc
        jdot += j.dot
    if hit_only:
        more = [M.MD_MORE, M.VM_MORE]  # MD, VM
        if predator:
            more += [M.PREDATOR_MORE, M.PREY_MORE]
        if cd:
            more.append(M.CD_MORE)   # Controlled Destruction (universal)
        if not no_returned:
            more.append(returned)
        if not no_cull:
            more += [CULL_MORE]
        f = Frame(
            name="opt-hit",
            flatsum=flatsum,
            inc=inc + jinc,
            cast=cast + jcast,
            # poison chance is preserved (pc jewels still yield poison) but with
            # the dropped-scaling params: no Amanamu pool (1.0) and no Unbound
            # duration (2.0). pc feeds a reduced poison layer; a 0-pc set stays
            # hit-only.
            poison_chance=min(1.0, jpc / 100.0),
            amanamu_dot_pool=amanamu_pool,
            poison_dur=poison_dur,
            malevolence_more=malevolence_more,
            # CD is "100% less crit" -> it kills the +50% DoT-mult-on-crit bonus
            # for poison; non-CD (e.g. Unbound) keeps the phantasm's base crit.
            crit_chance=0.0 if cd else crit_chance,
            crit_multi=crit_multi,
            chaos_pen_bonus=chaos_pen_bonus,
        )
        f.curse = HIT_ONLY_CURSE
        f.more = more
        if count is not None:
            f.count = count
        return f
    f = Frame(
        name="opt",
        flatsum=flatsum,
        inc=inc + jinc,
        cast=cast + jcast,
        poison_chance=min(1.0, jpc / 100.0),
        amanamu_dot_pool=M.amanamu_pool(jdot),
        chaos_pen_bonus=chaos_pen_bonus,
        # honor the caller's poison-duration config instead of silently assuming
        # Unbound Ailments (Frame default poison_dur=3.4, unbound more=1.20).
        poison_dur=poison_dur,
        unbound_ailment_more=(M.UNBOUND_AILMENT_MORE if poison_dur > 2.0 else 1.0),
    )
    f.more = list(M.POISON_MORE)   # MD/VM/CD -- verified bossing set
    if count is not None:
        f.count = count
    return f


# Non-jewel baselines for the RESULTING-build log.
# >>> 2026-08-15 re-based from level-100 snapshot (NEW ring Brood Loop, boots
#      recrafted +19% cold&fire); see the AUTHORITATIVE blocks below. <<<
# [history] 2026-08-13 no-jewel state: life 4410, es 1639, es recharge 546.3,
# life regen 126.8 (pre-5-EC), res 88/93/93/92. 2026-08-14: boots -> 14% ES
# recharge so cold/ltg res base dropped 20 (->68/73). Values below supersede all.
# Life regen assumes 5 max Endurance Charges (3 base + Endurance +1 + notables[12]
# +1; maintained via "Gain 1 EC every second if Hit Recently"). Per-charge regen =
# 0.4%/charge (0.2% boots implicit "per Endurance Charge" + 0.2% tree small passive
# "Life Regeneration per Endurance Charge") = 2.0% at 5 charges. BASE_LIFE_REGEN:
# flat tree % (2.42%: 0.8+1.0+0.5+0.12) + 2.0% charges = 4.42% x1.19 (19% inc Life
# Regen rate, boots) x 4555 (no-jewel effective life) => 239.6.
# 2026-08-16 re-based from Phantomastress_202608161639 (HIT-ONLY build applied:
# Flesh and Stone -> Culling Strike on the Cyclone trigger, Malevolence -> Anger,
# Amanamu's Gaze dropped, +2 max ele res (Nomadic Teachings) + Spiritual Command +
# Cannibalistic Rite from dropped big-life & mana clusters, chest sacred-orb'd &
# 6-linked, top-flat jewels (Enthralling Lens + Foul Globe) in the belt). Jewels
# stripped from frame: current life/es/res/inc/cast (1827/801/108-92-157-84/492.2/163.3)
# minus current hit set. Life dropped (big life cluster out); ES up (chest).
BASE_LIFE = 1778.0
BASE_ES = 747.0
BASE_ES_RECHARGE = 546.3      # approx: boots lost the 14% ES-recharge craft; recharge a bit lower
BASE_LIFE_REGEN = 239.6
BASE_RES = {"cold": 86.0, "fire": 92.0, "ltg": 89.0, "chaos": 84.0}
INC_LIFE = 151.6
INC_ES = 112.7


def _init_selection_table(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS jewel_selections(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created TEXT NOT NULL,
          belt_ids TEXT NOT NULL,            -- comma-separated
          tree_ids TEXT NOT NULL,            -- comma-separated
          seed_tree_ids TEXT,                -- comma-separated (seeds included in tree_ids)
          belt_mult REAL, regen_scale REAL,
          flat_base REAL, inc_base REAL, cast_base REAL,
          total_dps REAL,                    -- engine total_cursed for final set
          pc REAL,
          life REAL, es REAL,                -- resulting effective life/es pools
          es_regen REAL, life_regen REAL,    -- resulting regen / s (raw, pre-discount)
          cold_res REAL, fire_res REAL, ltg_res REAL, chaos_res REAL,
          equipment TEXT)                    -- free-form note: rare equipment piece names
    """)
    con.commit()
    con.close()


def record_selection(db_path: str, belt: list[Jewel], tree: list[Jewel],
                     belt_mult: float, flat: float, inc: float, cast: float,
                     regen_scale: float, seed_tree: list[str] | None,
                     equipment: str | None = None,
                     hit_only: bool = False, returned: float = 2.0,
                     predator: bool = True, no_returned: bool = False,
                     amanamu_pool: float = 1.0, poison_dur: float = 2.0,
                     malevolence_more: float = 1.0, cd: bool = True,
                     chaos_pen_bonus: float = 0.0,
                     no_cull: bool = False, count: float | None = None) -> None:
    """Persist the resulting build stats for this selection as a timestamped row."""
    import datetime
    _init_selection_table(db_path)

    flat_chunks = {"baseline": flat}
    if hit_only:
        flat_chunks["anger"] = ANGER_FLAT
    frame = make_frame(flat_chunks, inc, cast, belt, tree, belt_mult,
                       hit_only=hit_only, returned=returned, predator=predator,
                       no_returned=no_returned, amanamu_pool=amanamu_pool,
                       poison_dur=poison_dur, malevolence_more=malevolence_more,
                       cd=cd, chaos_pen_bonus=chaos_pen_bonus,
                       no_cull=no_cull, count=count)
    total_dps = _engine(frame).total_cursed
    jpc = sum(j.pc * belt_mult for j in belt) + sum(j.pc for j in tree)

    # Effective in-game pools: (flat base + jewel flat) x (1 + inc/100).
    def jewel_sum(belt_j: list[Jewel], tree_j: list[Jewel], attr: str) -> float:
        return sum(getattr(j, attr) * (belt_mult if j in belt_j else 1.0) for j in belt_j) \
            + sum(getattr(j, attr) for j in tree_j)

    flat_life = BASE_LIFE + jewel_sum(belt, tree, "life")
    flat_es = BASE_ES + jewel_sum(belt, tree, "es")
    life = flat_life * (1 + INC_LIFE / 100)
    es = flat_es * (1 + INC_ES / 100)
    # regen/recharge are flat pools + jewel contributions (flat /s, no multiplier).
    # life regen from % mods converts via the current flat base life.
    es_regen = BASE_ES_RECHARGE + jewel_sum(belt, tree, "es_regen")
    life_regen = BASE_LIFE_REGEN \
        + sum((j.life_regen_pct / 100.0 * flat_life) * (belt_mult if j in belt else 1.0) for j in belt) \
        + sum(j.life_regen_pct / 100.0 * flat_life for j in tree)

    # res from jewels: read via sqlite (Jewel dataclass doesn't carry res)
    import sqlite3
    con = sqlite3.connect(db_path); con.row_factory = sqlite3.Row
    jewel_rows = {r["id"]: r for r in con.execute("SELECT * FROM jewels")}
    col = {"cold": "cold_res", "fire": "fire_res", "ltg": "ltg_res", "chaos": "chaos_res"}

    def res_total(key: str) -> float:
        c = col[key]
        v = BASE_RES[key]
        for j in belt:
            v += (jewel_rows[j.id][c] or 0.0) * belt_mult
        for j in tree:
            v += (jewel_rows[j.id][c] or 0.0)
        return v

    seed_ids = ",".join(str(jewel_rows[c]["uid"]) for c in (seed_tree or []))
    con.execute(
        "INSERT INTO jewel_selections(created,belt_ids,tree_ids,seed_tree_ids,belt_mult,"
        "regen_scale,flat_base,inc_base,cast_base,total_dps,pc,life,es,es_regen,life_regen,"
        "cold_res,fire_res,ltg_res,chaos_res,equipment) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (datetime.datetime.utcnow().isoformat(" "),
         ",".join(str(j.uid) for j in belt), ",".join(str(j.uid) for j in tree), seed_ids,
         belt_mult, regen_scale, flat, inc, cast, total_dps, jpc, life, es,
         es_regen, life_regen, res_total("cold"), res_total("fire"),
         res_total("ltg"), res_total("chaos"), equipment))
    con.commit()
    con.close()


def dps_weights(f: Frame, base_life: float = 1830.0, base_es: float = 735.0,
                inc_life: float = 151.6, inc_es: float = 112.7,
                base_es_regen: float = 686.3, base_life_regen: float = 136.6,
                regen_scale: float = 0.5, life_weight: float = 1.0,
                hit_only: bool = False, survival: float = 1.0,
                returned: float = 2.0) -> DPSWeights:
    """Absolute marginal DPS deltas, measured against the total cursed bossing DPS.

    Each delta is measured by perturbing a full copy of the *current* frame `f`
    (so it inherits the socketed set's actual `more`, `malevolence_more`,
    `poison_dur`, `poison_chance` and `amanamu_dot_pool`). pc and dot are valued
    dynamically against the current set: poison scales linearly in chance, so a
    pc jewel earns its +poison from whatever pc is already socketed (up to cap);
    dot (amanamu pool) only matters to the extent poison is already present.
    """
    import copy

    base = _engine(copy.deepcopy(f)).total_cursed

    def delta(perturb) -> float:
        g = copy.deepcopy(f)
        perturb(g)
        return _engine(g).total_cursed - base

    dflat = delta(lambda g: g.flatsum.__setitem__(
        "perturb", g.flatsum.get("perturb", 0.0) + 1.0))
    dinc = delta(lambda g: setattr(g, "inc", g.inc + 1.0))
    dcast = delta(lambda g: setattr(g, "cast", g.cast + 1.0))
    ddot = delta(lambda g: setattr(g, "amanamu_dot_pool",
                                   g.amanamu_dot_pool + 0.01))
    dpc = delta(lambda g: setattr(g, "poison_chance",
                                  min(1.0, g.poison_chance + 0.01)))

    return DPSWeights(total=base, d_flat=dflat, d_inc=dinc, d_cast=dcast,
                      d_dot=ddot, d_pc=dpc,
                      base_life=base_life, base_es=base_es,
                      inc_life=inc_life, inc_es=inc_es,
                      base_es_regen=base_es_regen, base_life_regen=base_life_regen,
                      regen_scale=regen_scale, life_weight=life_weight,
                      survival=survival)


def run(db_path: str, belt_mult: float, flat: float, inc: float, cast: float,
        base_life: float = 1830.0, base_es: float = 735.0,
        inc_life: float = 151.6, inc_es: float = 112.7,
        base_es_regen: float = 686.3, base_life_regen: float = 136.6,
        regen_scale: float = 0.5, life_weight: float = 1.0,
        seed_tree: list[str] | None = None,
        seed_belt: list[str] | None = None,
        equipment: str | None = None,
        hit_only: bool = False,
        returned: float = 2.0,
        predator: bool = True,
        no_returned: bool = False,
        amanamu_pool: float = 1.0, poison_dur: float = 2.0,
        malevolence_more: float = 1.0, cd: bool = True,
        weapon_set: int = 1, equipped_snapshot: str | None = None,
        belt_min_pc: float = 14.0,
        tree_sockets: int = 7, reserve_tree: int = 0,
        chaos_pen_bonus: float = M.VOID_BEACON_CHAOS_RES_REDUCTION,
        no_cull: bool = False, count: float | None = None,
        verbose: bool = True) -> None:
    jewels = load_jewels(db_path)
    # baseline flat chunk (amanamu ag-0-attr adds 0). In hit-only, Malevolence is
    # swapped for Anger, whose fire flat is folded into the baseline (->chaos).
    flat_chunks = {"baseline": flat}
    if hit_only:
        flat_chunks["anger"] = ANGER_FLAT
        life_weight = 0.0   # glass cannon: value damage only, ignore life/es/regen

    belt: list[Jewel] = []
    tree: list[Jewel] = []
    picked: set[str] = set()

    # Poison build: Amanamu's Gaze is a FIXED tree socket (the +30% DoT pool
    # base IS the jewel), auto-seeded and excluded from the pick pool. Hit-only
    # drops the jewel, so its slot is freed there.
    if not hit_only:
        if AMANAMU_GAZE_ID not in jewels:
            raise ValueError(f"{AMANAMU_GAZE_ID} (Amanamu's Gaze) missing from "
                             "the catalog -- it is a fixed socket in the poison build")
        tree.append(jewels[AMANAMU_GAZE_ID])
        picked.add(AMANAMU_GAZE_ID)

    # Pre-socket fixed jewels on the belt (e.g. the survivability belt pair).
    # They occupy belt pc slots; a seeded non-pc belt jewel would also fill a slot.
    seed_belt_pcs = 0
    for sid in (seed_belt or []):
        if sid not in jewels:
            raise ValueError(f"unknown seed belt jewel: {sid}")
        belt.append(jewels[sid])
        picked.add(sid)
        if jewels[sid].is_pc:
            seed_belt_pcs += 1

    # Pre-socket fixed jewels (e.g. a chaos-res-cap jewel) on the tree. They
    # occupy non-pc tree slots, reducing the number of 'dps' picks below.
    for sid in (seed_tree or []):
        if sid not in jewels:
            raise ValueError(f"unknown seed jewel: {sid}")
        if sid == AMANAMU_GAZE_ID:
            continue   # auto-seeded above in poison mode; never a manual pick
        tree.append(jewels[sid])
        picked.add(sid)

    # Priority: (slot_type, belt_or_tree)
    #   'dps'      -> non-pc jewel, tree
    #   'belt_pc'  -> pc jewel, belt
    #   'nonbelt_pc'-> pc jewel, tree
    # 1 DPS-point = 0.01% of total cursed bossing DPS; life/ES use the same
    # 0.01%-of-total-EHP units (see DPSWeights.pt_life / pt_es).

    def cur_w() -> DPSWeights:
        return dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult,
                                      hit_only=hit_only, returned=returned,
                                      predator=predator, no_returned=no_returned,
                                      amanamu_pool=amanamu_pool, poison_dur=poison_dur,
                                      malevolence_more=malevolence_more, cd=cd,
                                      chaos_pen_bonus=chaos_pen_bonus,
                                      no_cull=no_cull, count=count),
                           base_life=base_life, base_es=base_es,
                           inc_life=inc_life, inc_es=inc_es,
                           base_es_regen=base_es_regen, base_life_regen=base_life_regen,
                           regen_scale=regen_scale, life_weight=life_weight,
                           hit_only=hit_only, survival=0.0 if hit_only else 1.0)

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
    # must be pc (to cap 100 alongside the 2 belt pc). Seeded jewels occupy
    # their slot type: a seeded pc jewel reduces the pc picks still needed, a
    # seeded non-pc jewel fills a non-pc slot (fewer 'dps' picks needed).
    # ``reserve_tree`` folds fixed non-modeled uniques (Forbidden Flame/Flesh,
    # Honour Sliver, etc.) into the tree geometry -- they occupy sockets without
    # contributing to the model, so they shrink the flexible pool. The glass-
    # cannon chest (Shroud of Lightless, 3 abyss sockets) is simply a bigger
    # tree via --tree-sockets 10.
    # In hit-only mode there are NO pc slots -- all flexible slots are pure DPS
    # (pc/dot ignored), so the belt's x2.21 is the only slot distinction.
    if hit_only:
        tree_pc_slots = 0
        belt_pc_slots = 2 - seed_belt_pcs
        pc_picks = 0
        # tree sockets minus reserved uniques (Amanamu's Gaze is dropped in
        # hit-only, so its slot is freed too -- all remaining are flexible DPS).
        tree_dps_slots = max(0, tree_sockets - reserve_tree
                             - sum(1 for j in tree if not j.is_pc))
        order = (["belt_pc"] * belt_pc_slots + ["dps"] * tree_dps_slots)
    else:
        # flexible tree sockets = total minus the fixed Amanamu's Gaze, minus
        # reserved non-modeled uniques, minus whatever seeds already occupy slots
        flexible = (tree_sockets - 1 - reserve_tree) \
            - sum(1 for j in tree if j is not jewels[AMANAMU_GAZE_ID])
        belt_pc_slots = 2 - seed_belt_pcs          # belt_pc, minus already-seeded belt pc
        tree_pc_slots = min(3, max(0, flexible))   # pc tree picks (cap-100 convention)
        pc_picks = tree_pc_slots
        tree_dps_slots = max(0, flexible - tree_pc_slots)
        # Priority sequence (user's order): 1-2 non-pc DPS -> 3-4 belt pc -> 5-7
        # tree pc -> last non-pc DPS. Seeded non-pc jewels shrink the trailing dps
        # block; the pc blocks are fixed.
        dps_front = min(tree_dps_slots, 2)
        order = (["dps"] * dps_front
                 + ["belt_pc"] * belt_pc_slots
                 + ["nonbelt_pc"] * pc_picks
                 + ["dps"] * (tree_dps_slots - dps_front))

    if verbose:
        print(f"baseline flat={flat} inc={inc} cast={cast} belt_mult={belt_mult}"
              + (f" seeded_tree={tree}" if tree else ""))
        hdr = f"{'step':>4} {'slot':<10} {'jewel':<18} {'flat':>6} {'inc':>4} {'cast':>4} {'dot':>4} {'pc':>4} | "
        hdr += f"{'pt_flat':>7} {'pt_inc':>7} {'pt_cast':>8} {'pt_dot':>7} {'pt_pc':>7} {'DPSL':>7}"
        print(hdr)
        print("-" * len(hdr))

    for step, slot in enumerate(order, 1):
        w = dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult,
                                   hit_only=hit_only, returned=returned,
                                   predator=predator, no_returned=no_returned,
                                   amanamu_pool=amanamu_pool, poison_dur=poison_dur,
                                   malevolence_more=malevolence_more, cd=cd,
                                   chaos_pen_bonus=chaos_pen_bonus,
                                   no_cull=no_cull, count=count),
                        base_life=base_life, base_es=base_es,
                        inc_life=inc_life, inc_es=inc_es,
                        base_es_regen=base_es_regen, base_life_regen=base_life_regen,
                         regen_scale=regen_scale, life_weight=life_weight,
                         hit_only=hit_only, survival=0.0 if hit_only else 1.0)
        used = set(x.id for x in belt) | set(x.id for x in tree) | picked
        avail = [j for j in jewels.values() if j.id not in used]
        # only socketable DPS jewels are eligible; pure-utility (attrib/leech)
        # and zero-value jewels never win a slot.
        candidate_pool = [j for j in avail if j.dps_mods]

        chosen = None
        if slot == "dps":
            pool = candidate_pool if hit_only else [j for j in candidate_pool if not j.is_pc]
            chosen = best_dps(pool)
        elif slot == "belt_pc":
            pool = candidate_pool if hit_only \
                else [j for j in candidate_pool
                      if j.is_pc and j.pc >= belt_min_pc]
            chosen = best_belt_pc(pool)
        else:  # nonbelt_pc
            pool = [j for j in candidate_pool if j.is_pc]
            chosen = best_tree_pc(pool)

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
        w2 = dps_weights(make_frame(flat_chunks, inc, cast, belt, tree, belt_mult,
                                    hit_only=hit_only, returned=returned,
                                    predator=predator, no_returned=no_returned,
                                    amanamu_pool=amanamu_pool, poison_dur=poison_dur,
                                    malevolence_more=malevolence_more, cd=cd,
                                    chaos_pen_bonus=chaos_pen_bonus,
                                    no_cull=no_cull, count=count),
                         base_life=base_life, base_es=base_es,
                         inc_life=inc_life, inc_es=inc_es,
                         base_es_regen=base_es_regen, base_life_regen=base_life_regen,
                         regen_scale=regen_scale, life_weight=life_weight,
                         hit_only=hit_only, survival=0.0 if hit_only else 1.0)
        dl = chosen.dps(w2, mult)
        if verbose:
            print(
                f"{step:>4} {slot:<10} {chosen.id:<18} {chosen.flat:6.1f} "
                f"{chosen.inc:4.0f} {chosen.cast:4.0f} {chosen.dot:4.0f} {chosen.pc:4.0f} | "
                f"{w2.pt_flat:7.2f} {w2.pt_inc:7.2f} {w2.pt_cast:8.2f} {w2.pt_dot:7.2f} {w2.pt_pc:7.2f} {dl:7.1f}"
            )

    # ---- local swap refinement --------------------------------------------- #
    # Greedy picks are marginal and myopic (slot placement, joint poison value).
    # Steepest-ascent over single swaps (a picked jewel <-> an unused one),
    # each scored by the REAL engine, removes single-swap-dominated picks.
    # Role-preserving: belt stays pc (poison mode), tree pc stays pc, tree dps
    # stays non-pc, so slot constraints and the pc cap survive every swap.
    def total_of(b: list[Jewel], t: list[Jewel]) -> float:
        return _engine(make_frame(
            flat_chunks, inc, cast, b, t, belt_mult,
            hit_only=hit_only, returned=returned, predator=predator,
            no_returned=no_returned, amanamu_pool=amanamu_pool,
            poison_dur=poison_dur, malevolence_more=malevolence_more,
            cd=cd, chaos_pen_bonus=chaos_pen_bonus,
            no_cull=no_cull, count=count)).total_cursed

    if verbose:
        print("\nswap refinement (engine-verified single swaps):")
    while True:
        start = total_of(belt, tree)
        # each move: (gain, label, kind, i, j, jewel)
        #   kind "belt"/"tree": replace lst[i] with jewel
        #   kind "x": exchange belt[i] <-> tree[j] (both pc)
        moves: list[tuple[float, str, str, int, int, Jewel | None]] = []
        used_ids = {j.id for j in belt} | {j.id for j in tree}
        avail = [j for j in jewels.values()
                 if j.id not in used_ids and j.dps_mods]
        for loc in ("belt", "tree"):
            lst = belt if loc == "belt" else tree
            for i, cur in enumerate(lst):
                if cur.id == AMANAMU_GAZE_ID:
                    continue   # fixed socket
                for cand in avail:
                    if hit_only:
                        ok = True
                    elif loc == "belt":
                        ok = (cur.is_pc and cand.is_pc
                              and cand.pc >= belt_min_pc)
                    elif cur.is_pc:
                        ok = cand.is_pc
                    else:
                        ok = not cand.is_pc
                    if not ok:
                        continue
                    trial = list(lst)
                    trial[i] = cand
                    tot = (total_of(trial, tree) if loc == "belt"
                           else total_of(belt, trial))
                    if tot > start + 1e-9:
                        moves.append((tot - start,
                                      f"{loc}[{cur.id}] -> {cand.id}",
                                      loc, i, -1, cand))
        if not hit_only:
            for bi, bj in enumerate(belt):
                for ti, tj in enumerate(tree):
                    if tj.id == AMANAMU_GAZE_ID or not (bj.is_pc and tj.is_pc):
                        continue
                    if tj.pc < belt_min_pc:
                        continue   # would move a sub-floor jewel into the belt
                    tb, tt = list(belt), list(tree)
                    tb[bi], tt[ti] = tj, bj
                    tot = total_of(tb, tt)
                    if tot > start + 1e-9:
                        moves.append((tot - start,
                                      f"exchange belt[{bj.id}] <-> tree[{tj.id}]",
                                      "x", bi, ti, None))
        if not moves:
            break
        gain, label, kind, i, jdx, cand = max(moves, key=lambda m: m[0])
        if kind == "x":
            belt[i], tree[jdx] = tree[jdx], belt[i]
        else:
            (belt if kind == "belt" else tree)[i] = cand
        if verbose:
            print(f"  {label}  (+{gain:,.0f} cursed DPS)")

    # ---- comparison against what is actually equipped ----------------------- #
    if equipped_snapshot:
        try:
            import json as _json
            import soulwrest_dps as _sw
            eq_frame = _sw.build_frame_from_snapshot(
                equipped_snapshot, db_path=db_path, weapon_set=weapon_set,
                name="equipped")
            eq_total = _engine(eq_frame).total_cursed
            opt_total = total_of(belt, tree)
            d = (opt_total / eq_total - 1) * 100 if eq_total else 0.0
            if verbose:
                print(f"\nvs equipped ({eq_frame.name}):")
                print(f"  equipped     {eq_total:>13,.0f}")
                print(f"  recommended  {opt_total:>13,.0f}  ({d:+.2f}%)")
                if d < 0:
                    print("  !! recommendation is BELOW your current set -- "
                          "keep your jewels (greedy/refinement found nothing "
                          "better than what you already run)")
        except (OSError, ValueError, KeyError) as e:
            print(f"[compare] skipped: {e}")

    if verbose:
        print("\nFinal socketed set (DPSL-ranked):")
        print("  belt:", ", ".join(j.id for j in belt))
        print("  tree:", ", ".join(j.id for j in tree))

    record_selection(db_path, belt, tree, belt_mult, flat, inc, cast,
                     regen_scale, seed_tree, equipment,
                     hit_only=hit_only, returned=returned, predator=predator,
                     no_returned=no_returned,
                     amanamu_pool=amanamu_pool, poison_dur=poison_dur,
                     malevolence_more=malevolence_more, cd=cd,
                     chaos_pen_bonus=chaos_pen_bonus,
                     no_cull=no_cull, count=count)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", default="jewels.db")
    p.add_argument("--belt-mult", type=float, default=2.21)
    p.add_argument("--snapshot", default=None,
                   help="expanded snapshot for dynamic baseline derivation "
                        "(default: newest under build_snapshots/)")
    p.add_argument("--weapon-set", type=int, choices=(1, 2), default=1,
                   help="weapon swap whose flat/gems count (default 1 = "
                        "Weapon/Offhand; 2 = Weapon2/Offhand2)")
    p.add_argument("--belt-min-pc", type=float, default=14.0,
                   help="poison mode: belt jewels need at least this much pc "
                        "to be socketed or exchanged into the belt "
                        "(Phantomastress convention; 0 lifts the floor)")
    p.add_argument("--tree-sockets", type=int, default=7,
                   help="total tree jewel sockets incl. the fixed Amanamu's "
                        "Gaze (default 7; e.g. 5 = two sockets less)")
    p.add_argument("--reserve-tree", type=int, default=0,
                   help="tree sockets occupied by fixed non-modeled uniques "
                        "(Forbidden Flame/Flesh, Honour Sliver, etc.) that "
                        "shrink the flexible pick pool (default 0; e.g. 2 = "
                        "the two Forbidden gems)")
    p.add_argument("--chaos-pen", type=float,
                   default=M.VOID_BEACON_CHAOS_RES_REDUCTION,
                   help="extra -%% monster chaos res on top of Despair "
                        "(default 20 = Void Beacon via the Forbidden FF/F pair; "
                        "e.g. 0 = no FF/F)")
    p.add_argument("--flat", type=float, default=None,
                   help="non-jewel flat (default: derived LIVE from the "
                        f"snapshot weapon set; offline fallback {DEFAULT_FLAT:g})")
    p.add_argument("--inc", type=float, default=None,
                   help="non-jewel inc pool %% (default: derived LIVE from the "
                        f"snapshot; offline fallback {DEFAULT_INC:g})")
    p.add_argument("--cast", type=float, default=None,
                   help="non-jewel cast pool %% (default: derived LIVE from the "
                        f"snapshot; offline fallback {DEFAULT_CAST:g})")
    p.add_argument("--base-life", type=float, default=1830.0, help="non-jewel base life")
    p.add_argument("--base-es", type=float, default=735.0, help="non-jewel base es")
    p.add_argument("--inc-life", type=float, default=151.6, help="%% increased life")
    p.add_argument("--inc-es", type=float, default=112.7, help="%% increased es")
    p.add_argument("--base-es-regen", type=float, default=686.3, help="non-jewel ES regen/s")
    p.add_argument("--base-life-regen", type=float, default=136.6, help="non-jewel life regen/s")
    p.add_argument("--regen-scale", type=float, default=0.5,
                   help="discount factor for conditional regen (ES=recharge, life gated behind ES)")
    p.add_argument("--seed-tree", action="append", default=None,
                   help="jewel id to pre-socket on the tree (repeatable)")
    p.add_argument("--seed-belt", action="append", default=None,
                   help="jewel id to pre-socket on the belt (repeatable)")
    p.add_argument("--equipment", default=None,
                   help="free-form note of rare equipment piece names, so a later "
                        "gear change is identifiable in the selection log")
    p.add_argument("--hit-only", action="store_true",
                   help="glass-cannon HIT-ONLY variant: drops the poison/DoT layer "
                        "(Anger aura, Controlled Destruction + Returned Projectiles "
                        "supports, Sniper's Mark curse). No pc/dot slots, no "
                        "survivability weighting. Flat base auto-adds ANGER_FLAT.")
    p.add_argument("--returned", type=float, default=2.0,
                   help="Returned Projectiles realized multiplier (default 2.0; "
                        "~1.5 conservative, ~2.0 optimistic). Hit-only only.")
    p.add_argument("--no-predator", action="store_true",
                   help="hit-only: omit Predator Support + its Prey mark from the "
                        "more list (you dropped Predator for ubers/mapping).")
    p.add_argument("--no-returned", action="store_true",
                   help="hit-only: omit Returned Projectiles from the more list "
                        "(testing showed it doesn't double-hit; drop it).")
    p.add_argument("--no-cull", action="store_true",
                   help="hit-only: drop the Culling-Strike-on-Cyclone x1.111 more")
    p.add_argument("--count", type=float, default=None,
                   help="override phantasm count (e.g. 58 = Summon Phantasm + "
                        "Dark Monarch + Congregation)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)
    for name, derive, fallback in (
            ("flat", M.baseline_flat, DEFAULT_FLAT),
            ("inc", M.baseline_inc, DEFAULT_INC),
            ("cast", M.baseline_cast, DEFAULT_CAST)):
        if getattr(args, name) is not None:
            continue
        try:
            setattr(args, name, derive(args.snapshot, db_path=args.db,
                                       belt_mult=args.belt_mult,
                                       weapon_set=args.weapon_set))
            if not args.quiet:
                print(f"[baseline] non-jewel {name} derived from snapshot: "
                      f"{getattr(args, name):g}")
        except (FileNotFoundError, OSError) as e:
            setattr(args, name, fallback)
            if not args.quiet:
                print(f"[baseline] snapshot derivation failed, {name} fallback "
                      f"{fallback:g}: {e}")
    run(args.db, args.belt_mult, args.flat, args.inc, args.cast,
        base_life=args.base_life, base_es=args.base_es,
        inc_life=args.inc_life, inc_es=args.inc_es,
        base_es_regen=args.base_es_regen, base_life_regen=args.base_life_regen,
        regen_scale=args.regen_scale,
        seed_tree=args.seed_tree, seed_belt=args.seed_belt, equipment=args.equipment,
        hit_only=args.hit_only, returned=args.returned,
        predator=not args.no_predator, no_returned=args.no_returned,
        weapon_set=args.weapon_set,
        equipped_snapshot=args.snapshot or M.latest_snapshot(),
        belt_min_pc=args.belt_min_pc,
        tree_sockets=args.tree_sockets, chaos_pen_bonus=args.chaos_pen,
        reserve_tree=args.reserve_tree,
        no_cull=args.no_cull, count=args.count,
        verbose=not args.quiet)


if __name__ == "__main__":
    main()