"""Single source of truth for the Soulwrest Phantasm bossing model.

Three layers live in this module:

1. MODEL CONSTANTS — gem/aura/curse scalars consumed by ``soulwrest_dps.py``,
   ``jewel_exhaustive.py``, ``socket_optimizer.py``, ``aspect_sweep.py`` and
   ``jewel_balance.py``. Every value carries provenance and was verified
   against level-21 gem text (2026-08-21 snapshot) unless noted otherwise.
   When gems change — levels, quality, socket-colour quality grants,
   Runegrafts (e.g. Runegraft of Gemcraft: +1 to all non-exceptional support
   gems) — re-derive the affected values and update THIS FILE ONLY. No
   consumer may redefine these numbers locally.

2. BUILD BASELINES (offline fallbacks) — ``BASELINE_FLAT/INC/CAST``: non-jewel
   gear pools frozen as scalars, valid only for the gear state they were
   derived from. Consumers use them ONLY when live snapshot derivation is
   impossible (no snapshot found / unreadable), with a printed notice.

3. SNAPSHOT-DERIVED BASELINES (preferred) — ``baseline_flat()/baseline_inc()/
   baseline_cast()`` re-derive each pool LIVE from an expanded character
   snapshot: they build a Frame with the current engine, subtract the resolved
   jewels' contribution, and return what remains (tree + gear + auras/
   supports). Gear changes therefore propagate by taking a new snapshot —
   no edits to this file.
     * ``weapon_set`` selects which weapon swap contributes flat/gems
       (1 = Weapon/Offhand slots, 2 = Weapon2/Offhand2). Staff flat varies per
       swap; the switch keeps both sets comparable.
     * Envy's flat (+106 chaos, from the aura, not an item mod) is included
       only while ``ENVY_SOURCE_AMULET`` is the equipped amulet.
     * ``latest_snapshot()`` picks the newest matching file automatically;
       pass ``snapshot_path`` to pin a specific one.

Derivation needs ``soulwrest_dps`` + ``jewels.db`` and imports them lazily
inside the functions, so importing this module alone has no heavy
dependencies. Not-yet-dynamic constants that still require manual refresh:
support-gem more multipliers, Unbound/duration values, Vaal Haste, and the
aura-effect stacks themselves (Gen 40 / Sov 10 / chest 12) -- snapshot text
does not carry support-gem values; deriving those needs PoB gem data parsed
by level/quality.
"""

from __future__ import annotations
from dataclasses import dataclass
from math import prod

# --------------------------------------------------------------------------- #
# Base damage                                                                  #
# --------------------------------------------------------------------------- #
INTRINSIC = 684.1          # lvl-21 Summon Phantasm phys base damage (avg)
ADD_EFF = 1.5              # phantasm added-damage effectiveness
BASE_APS = 0.855           # actions/sec per phantasm at 0% cast speed

# --------------------------------------------------------------------------- #
# Aura effect stack (shared by Malevolence DoT more and Anger's added flat)    #
# --------------------------------------------------------------------------- #
AURA_EFFECT_MULT = 1.0 + 0.40 + 0.10 + 0.12   # Generosity 40 + Sovereignty 10 + chest eldritch 12

# --------------------------------------------------------------------------- #
# Flat damage from auras                                                       #
# --------------------------------------------------------------------------- #
ENVY_FLAT = (91 + 121) / 2     # 106: Envy lvl 15 "Adds 91 to 121 Chaos Damage with Spells"
ENVY_SOURCE_AMULET = "Aul's Uprising"   # Envy comes from this amulet; no Aul, no envy
# Envy IS an aura (Aura tag), so increased aura effect scales its flat -- but it
# is a GRANTED skill, so Generosity cannot link to it; only Sovereignty + chest apply.
ENVY_AURA_EFFECT_MULT = 1.0 + 0.10 + 0.12   # Sovereignty 10 + chest eldritch 12
ENVY_FLAT_EFFECTIVE = ENVY_FLAT * ENVY_AURA_EFFECT_MULT   # 129.32
ANGER_FLAT = (84 + 125) / 2    # 20/20 Anger added fire at BASE aura effect
ANGER_FLAT_GENEROSITY = ANGER_FLAT * AURA_EFFECT_MULT   # x1.62 (Gen+Sov+chest):
                               # hit-based variant runs Anger linked to Generosity,
                               # so its flat scales with the aura-effect stack

# --------------------------------------------------------------------------- #
# Support-gem more multipliers (level/quality dependent)                       #
# --------------------------------------------------------------------------- #
MD_MORE = 1.40             # Minion Damage Support (lvl 21; NOT melee)
VM_MORE = 1.35             # Void Manipulation (chaos-only == generic on this build)
CD_MORE = 1.40             # Controlled Destruction, lvl 21 (same gem in every config)
PREDATOR_MORE = 1.13       # Predator Support generic more -- lvl 22 via
                           # Runegraft of Gemcraft (was 12% at lvl 21)
PREY_MORE = 1.25           # Prey mark
CULL_MORE = 1.111          # Culling Strike on the Cyclone trigger (+11.1% more)

POISON_MORE = (MD_MORE, VM_MORE, CD_MORE)   # Predator Support dropped (controller
                                            # targeting counterproductive vs packs)

# --------------------------------------------------------------------------- #
# Withered (applied by minions via Unholy Might -- tree notable                #
# "Unnatural Strength": Minions have Unholy Might; 25% chance on hit)          #
# Withered: 6% increased Chaos Damage Taken per stack, up to 15 stacks.        #
# Sustained bossing assumption: full stacks (58 phantasms cap them ~1s).       #
# --------------------------------------------------------------------------- #
WITHERED_PER_STACK = 6.0    # % increased Chaos Damage Taken per stack
WITHERED_MAX_STACKS = 15
# Abyssal bloodline node (>=3 ghastly eyes socketed): Unholy Might also applies
# 20% Increased Effect of Withered => 7.2%/stack => +108% at max stacks.
WITHERED_EFFECT_MULT = 1.20
# Same node: Unholy Might-granted damage Penetrates 10% Chaos Resistance.
# PENETRATION IS HIT-ONLY (DoT never penetrates) -- poison does not benefit.
BLOODLINE_CHAOS_PEN = 10.0
# Forbidden Flame + Forbidden Flesh pair (tree jewel sockets) permanently
# allocates Void Beacon: -20% enemy Chaos Res, always on, affects hits AND DoT
# (it is resistance REDUCTION, not penetration).
VOID_BEACON_CHAOS_RES_REDUCTION = 20.0


def withered_mult(stacks: float = WITHERED_MAX_STACKS) -> float:
    """Damage multiplier from Withered stacks (hits and DoT alike)."""
    return 1.0 + stacks * WITHERED_PER_STACK * WITHERED_EFFECT_MULT / 100.0

# --------------------------------------------------------------------------- #
# Crit (minion)                                                                #
# --------------------------------------------------------------------------- #
MINION_CRIT_CHANCE = 0.05
MINION_CRIT_MULTI = 1.50   # base crit multiplier
CRIT_POISON_BONUS = 0.50   # +50% DoT multiplier on a crit-poison, additive pool

HIT_CRIT_MULT = 1.0 + MINION_CRIT_CHANCE * (MINION_CRIT_MULTI - 1.0)

# --------------------------------------------------------------------------- #
# Ailments / DoT                                                               #
# --------------------------------------------------------------------------- #
UNBOUND_AILMENT_MORE = 1.20    # Unbound Ailments 21: 20% more Damage with Ailments (poison only)
BASE_POISON_DUR = 2.0          # unmodified poison duration, s
# Unbound Ailments duration: +55% at lvl 21 + 15% from 30% quality = +70%.
# (Quality is NOT captured by the expander, so this bakes the 30%-quality case in.)
UNBOUND_DUR_BONUS = 0.70
POISON_DUR_UNBOUND = BASE_POISON_DUR * (1 + UNBOUND_DUR_BONUS)   # 3.4 (pre-TC)

# Temp Chains lvl 21: "debuffs expire 25% slower" => duration x 1/(1-0.25) = x1.333
TEMP_CHAINS_SLOW = 0.25
TEMP_CHAINS_DUR_MULT = 1.0 / (1.0 - TEMP_CHAINS_SLOW)

MALEV_DOT_MORE = 0.20          # Malevolence lvl 21: 20% more Damage over Time
MALEV = 1.0 + MALEV_DOT_MORE * AURA_EFFECT_MULT                  # 1.324

AMANAMU_POOL_BASE = 1.30       # Amanamu's Gaze +30% DoT mult (additive pool)


def amanamu_pool(dot_pct: float) -> float:
    """Additive DoT-mult pool: base 1.30 plus jewel/belt +x% contributions."""
    return AMANAMU_POOL_BASE + dot_pct / 100.0


# --------------------------------------------------------------------------- #
# Auras (cast speed)                                                           #
# --------------------------------------------------------------------------- #
VAAL_HASTE_CAST = 24.0     # Vaal Haste: +24% minion attack/cast speed (cast part)

# --------------------------------------------------------------------------- #
# Poison                                                                       #
# --------------------------------------------------------------------------- #
POISON_BASE = 0.20         # poison deals 20% of combined phys+chaos hit per second

# --------------------------------------------------------------------------- #
# Curses -- engine curse key -> damage multipliers                             #
# Monster chaos RESISTANCE model: the boss has real chaos res, and debuff      #
# penetration lowers it; damage scales linearly with (1 - res/100), negative   #
# res amplifying (PoE rule).                                                   #
#   BOSS_CHAOS_RES 30% -> uncursed x0.70; Despair -30% -> x1.00;               #
#   Despair + extra pen P -> x(1 + P/100).                                     #
# Sniper's Mark: x1.34 hit only. +35% DoT-taken stays poison-only.             #
# --------------------------------------------------------------------------- #
BOSS_CHAOS_RES = 30.0      # % chaos resistance on the bossing target (2026-08-21)
DESPAIR_HIT_MULT = 1.30    # -30% chaos res (kept as the curse's pen magnitude)
DESPAIR_DOT_TAKEN = 1.35
SNIPER_HIT_MULT = 1.34


def curse_mults(curse_key: str | None, extra_chaos_pen: float = 0.0,
                boss_chaos_res: float = BOSS_CHAOS_RES,
                hit_chaos_pen: float = 0.0) -> tuple[float, float]:
    """(hit_mult, poison_mult) vs a boss holding ``boss_chaos_res`` % chaos res.

    Despair contributes -30 points of pen; ``extra_chaos_pen`` stacks more
    percentage points on top (res REDUCTION -- applies to hits AND DoT).
    ``hit_chaos_pen`` is true PENETRATION (e.g. the bloodline's 10%) and
    applies to the HIT side only: penetration changes what a hit deals, not
    the pre-mitigation damage poison is based on. Multiplier =
    1 - effective_res/100, so with the 30%-res boss: uncursed x0.70,
    Despair x1.00, Despair + 20 reduction x1.20 -- NOT the naive x1.30/x1.50
    of a res-less target.
    """
    pen = extra_chaos_pen
    cursed = curse_key in ("despair_tc", "sniper")
    if cursed:
        pen += (DESPAIR_HIT_MULT - 1.0) * 100.0   # Despair: -30 points
    eff = boss_chaos_res - pen
    hit = 1.0 - (eff - hit_chaos_pen) / 100.0     # penetration: hit side only
    if curse_key == "sniper":
        hit *= SNIPER_HIT_MULT
    # poison scales with res (and Despair's DoT-taken) but NOT with penetration
    # or Sniper's hit bonus
    poison = 1.0 - eff / 100.0
    poison = poison * DESPAIR_DOT_TAKEN if cursed else poison
    return hit, poison


# Zero-extra-pen multipliers at the default boss res (backward-compat table;
# jewel_exhaustive unpacks these). despair_tc -> x1.00 / x1.35, sniper ->
# x1.34 / x1.35, uncursed -> x0.70 both.
CURSE_MULTS: dict[str | None, tuple[float, float]] = {
    key: curse_mults(key) for key in ("despair_tc", "sniper", None)
}

# --------------------------------------------------------------------------- #
# Build configuration                                                          #
# --------------------------------------------------------------------------- #
DEFAULT_COUNT = 58.0       # phantasms active: 11 base -> x2 Summon Phantasm Support
                           # -> x2 Dark Monarch -> Congregation lvl 3 (~58, mapping cap).
                           # Congregation is part of the CURRENT bossing link set and
                           # does not change between poison/hit variants.
COUNT_NO_CONGREGATION = 44.0  # legacy config without the Congregation link

DEFAULT_COUNT = 58.0       # phantasms active: 11 base -> x2 Summon Phantasm Support
                           # -> x2 Dark Monarch -> Congregation lvl 3 (~58, mapping cap).
                           # Congregation is part of the CURRENT bossing link set and
                           # does not change between poison/hit variants.
COUNT_NO_CONGREGATION = 44.0  # legacy config without the Congregation link

# --------------------------------------------------------------------------- #
# Support-gem scaling -- poedb 3.29 level tables (known points; values are     #
# the gem's relevant "% more/% increased" magnitude in percent points).        #
# Effective level = shown level + RUNEGRAFT_SUPPORT_BONUS for non-exceptional  #
# supports while the Runegraft of Gemcraft is installed.                       #
# --------------------------------------------------------------------------- #
RUNEGRAFT_SUPPORT_BONUS = 1

_GEM_LEVEL_TABLES = {
    "Minion Damage Support":          {19: 38, 20: 39, 21: 40, 22: 40, 23: 41},
    "Void Manipulation Support":      {19: 33, 20: 34, 21: 35, 22: 35, 23: 36},
    "Controlled Destruction Support": {19: 38, 20: 39, 21: 40, 22: 40, 23: 41},
    "Unbound Ailments Support":       {20: 19, 21: 20, 22: 20},   # more Damage with Ailments
}
_PREDATOR_GENERIC = {20: 12, 21: 12, 22: 13}   # Minions deal X% more Damage
_PREDATOR_PREY    = {20: 24, 21: 25, 22: 25}   # vs Prey, with Hits AND Ailments
_FLESH_OFFERING_CAST = {20: 30, 21: 30}        # +% minion Cast Speed while active
_CONGREGATION_COUNT = {2: 58, 3: 58}           # league-tuned mapping cap by link level


def _table_value(table: dict, level: float):
    """Exact hit, else linear interpolation between nearest known levels."""
    if not table:
        return None
    lv = sorted(table)
    if level <= lv[0]:
        return table[lv[0]]
    if level >= lv[-1]:
        return table[lv[-1]]
    for a, b in zip(lv, lv[1:]):
        if a <= level <= b:
            return table[a] + (table[b] - table[a]) * (level - a) / (b - a)
    return table[lv[-1]]


@dataclass
class GemConfig:
    more: list                 # damage-more multipliers contributed by socketed supports
    unbound_more: float        # 1.0 when Unbound Ailments is not socketed
    count: float               # phantasm count
    cast_bump: float           # Flesh Offering / Vaal Haste contributions to cast pool
    anger_flat: float          # ANGER_FLAT_GENEROSITY when Anger runs linked to Generosity
    malevolence: bool          # Malevolence socketed (aura-effect scaled separately)
    curse: str | None          # inferred from socketed curse gems
    warnings: list


def derive_gem_config(gems, runegraft_bonus: int = RUNEGRAFT_SUPPORT_BONUS,
                      ) -> GemConfig:
    """Derive the gem-dependent frame fields from socketed gem data.

    ``gems``: iterable of dicts with at least {"name", "level", "support"}.
    Unknown gems are ignored; core damage supports that are MISSING fall back
    to the verified model constants with a warning (snapshots taken mid-
    reconfigure can transiently drop gems).
    """
    more: list = []
    unbound = 1.0
    cast_bump = 0.0
    anger = malev = False
    has_despair = has_tc = has_sniper = False
    sp_present = cong_level = None
    warns: list = []

    for g in gems:
        name = g.get("name") or ""
        try:
            lvl = float(g.get("level") or 20)
        except (TypeError, ValueError):
            lvl = 20.0
        support = g.get("support")
        eff = lvl + (runegraft_bonus if support else 0)

        if name == "Minion Damage Support" and support:
            v = _table_value(_GEM_LEVEL_TABLES[name], eff)
            if v is None: warns.append(f"{name}: no scaling data")
            else: more.append(1.0 + v / 100.0)
        elif name == "Void Manipulation Support" and support:
            v = _table_value(_GEM_LEVEL_TABLES[name], eff)
            if v is None: warns.append(f"{name}: no scaling data")
            else: more.append(1.0 + v / 100.0)
        elif name == "Controlled Destruction Support" and support:
            v = _table_value(_GEM_LEVEL_TABLES[name], eff)
            if v is None: warns.append(f"{name}: no scaling data")
            else: more.append(1.0 + v / 100.0)
        elif name == "Predator Support" and support:
            pg = _table_value(_PREDATOR_GENERIC, eff)
            pp = _table_value(_PREDATOR_PREY, eff)
            if pg is None or pp is None: warns.append("Predator: no scaling data")
            else:
                more.append(1.0 + pg / 100.0)   # generic: hits + ailments alike
                more.append(1.0 + pp / 100.0)   # Prey: "with Hits and Ailments"
        elif name == "Unbound Ailments Support" and support:
            v = _table_value(_GEM_LEVEL_TABLES[name], eff)
            if v is None: warns.append("Unbound Ailments: no scaling data")
            else: unbound = 1.0 + v / 100.0
        elif name == "Summon Phantasm Support" and support:
            sp_present = True
        elif name == "Congregation Support" and support:
            cong_level = eff
        elif name == "Flesh Offering":
            v = _table_value(_FLESH_OFFERING_CAST, lvl)
            if v is not None: cast_bump += v
        elif name == "Vaal Haste":
            cast_bump += VAAL_HASTE_CAST
        elif name == "Malevolence":
            malev = True
        elif name == "Anger":
            anger = True   # counts only if Generosity is also present (checked below)
        elif name == "Generosity":
            pass           # presence checked alongside Anger below
        elif name == "Despair":
            has_despair = True
        elif name == "Temporal Chains":
            has_tc = True
        elif name == "Sniper's Mark":
            has_sniper = True

    # Anger only contributes its flat when linked to Generosity -- approximate
    # by co-presence of both gems anywhere in the config.
    anger_flat = ANGER_FLAT_GENEROSITY if (anger and any(
        g.get("name") == "Generosity" for g in gems)) else 0.0

    # count: Summon Phantasm doubles 11 -> 22, Dark Monarch doubles -> 44,
    # Congregation multiplies to ~58 (league-tuned cap).
    if sp_present and cong_level is not None:
        count = float(_CONGREGATION_COUNT.get(int(cong_level),
                                              max(_CONGREGATION_COUNT.values())))
    elif sp_present:
        count = COUNT_NO_CONGREGATION
    else:
        count = DEFAULT_COUNT
        warns.append("Summon Phantasm Support not found in snapshot")

    # core trio fallback so mid-reconfigure snapshots stay sane
    for core, const in (("Minion Damage Support", MD_MORE),
                        ("Void Manipulation Support", VM_MORE),
                        ("Controlled Destruction Support", CD_MORE)):
        if not any(m == const for m in more):
            warns.append(f"{core}: not found in snapshot -- falling back to "
                         f"{const:.2f}")
            more.insert(0, const)

    curse = None
    if has_sniper:
        curse = "sniper"
    elif has_despair and has_tc:
        curse = "despair_tc"
    elif has_despair:
        curse = "despair"
    else:
        warns.append("no Despair found in snapshot")

    return GemConfig(more=more, unbound_more=unbound, count=count,
                     cast_bump=cast_bump, anger_flat=anger_flat,
                     malevolence=malev, curse=curse, warnings=warns)

# --------------------------------------------------------------------------- #
# Build baseline -- non-jewel gear pools (Phantomastress, jewels stripped)     #
# Re-derived from the FIXED snapshot builder 2026-08-21; re-derive whenever    #
# non-jewel gear/tree changes. Consumers: socket_optimizer, aspect_sweep,      #
# jewel_balance.                                                               #
# --------------------------------------------------------------------------- #
STAFF_FLAT = 124.5         # Soulwrest Phantasm staff minion flat (avg)
BASELINE_FLAT = ENVY_FLAT_EFFECTIVE + STAFF_FLAT   # 253.8 (envy x aura effect + staff)
BASELINE_INC = 289.0       # tree + gloves + ring + aura/support inc pool
BASELINE_CAST = 56.0 + VAAL_HASTE_CAST + 16.0   # tree + Vaal Haste + ring Eagle Knuckle


# --------------------------------------------------------------------------- #
# Snapshot-derived baselines                                                   #
# The BASELINE_* scalars above are CACHED FALLBACKS. The functions below       #
# re-derive them live from an expanded snapshot, so gem/gear/tree changes      #
# propagate by re-snapshotting instead of hand-editing this file.              #
# --------------------------------------------------------------------------- #

SNAPSHOT_DIR = "build_snapshots"
SNAPSHOT_GLOB = "Phantomastress_*_expanded.json"


def latest_snapshot(directory: str = SNAPSHOT_DIR,
                    pattern: str = SNAPSHOT_GLOB) -> "str | None":
    """Newest matching expanded snapshot path, or None if none exist."""
    from pathlib import Path
    snaps = sorted(Path(directory).glob(pattern))
    return str(snaps[-1]) if snaps else None


def _snapshot_frame_and_jewels(snapshot_path: "str | None", db_path: str,
                               belt_mult: float, weapon_set: int = 1):
    """Shared loader: (Frame, JewelLoad) for a snapshot via the current engine.

    ``weapon_set`` selects the weapon swap whose flat/gems count (1 or 2).
    """
    import json as _json
    import soulwrest_dps as sw   # lazy: soulwrest_dps imports this module

    path = snapshot_path or latest_snapshot()
    if not path:
        raise FileNotFoundError(
            f"no snapshot matching {SNAPSHOT_GLOB!r} under {SNAPSHOT_DIR!r}; "
            "pass snapshot_path or use the BASELINE_* fallback")
    with open(path) as fh:
        snap = _json.load(fh)
    f = sw.build_frame_from_snapshot(path, db_path=db_path, belt_mult=belt_mult,
                                     name="baseline", weapon_set=weapon_set)
    belt_ids, tree_ids, chest_ids = sw.resolve_snapshot_jewels(snap, db_path)
    jl = sw.load_jewels_from_db(db_path, belt_ids=belt_ids,
                                tree_ids=tree_ids + chest_ids,
                                belt_mult=belt_mult)
    return f, jl


def baseline_flat(snapshot_path: "str | None" = None, db_path: str = "jewels.db",
                  belt_mult: float = 2.21, weapon_set: int = 1) -> float:
    """Non-jewel minion flat (chosen weapon set's staff + Envy aura), LIVE."""
    f, jl = _snapshot_frame_and_jewels(snapshot_path, db_path, belt_mult,
                                       weapon_set)
    return sum(v for k, v in f.flatsum.items() if not k.startswith("jewel"))


def baseline_inc(snapshot_path: "str | None" = None, db_path: str = "jewels.db",
                 belt_mult: float = 2.21, weapon_set: int = 1) -> float:
    """Non-jewel minion increased-damage pool, derived LIVE from a snapshot.

    Builds the frame from the snapshot with the current engine and subtracts
    the socketed jewels' inc contribution (belt jewels x belt_mult), leaving
    the non-jewel pool: tree + gear + auras/supports. Falls back to nothing --
    callers decide how to handle absence of snapshots.
    """
    f, jl = _snapshot_frame_and_jewels(snapshot_path, db_path, belt_mult,
                                       weapon_set)
    return f.inc - jl.inc


def baseline_cast(snapshot_path: "str | None" = None, db_path: str = "jewels.db",
                  belt_mult: float = 2.21, weapon_set: int = 1) -> float:
    """Non-jewel minion cast-speed pool (tree + gear + Vaal Haste), LIVE."""
    f, jl = _snapshot_frame_and_jewels(snapshot_path, db_path, belt_mult,
                                       weapon_set)
    return f.cast - jl.cast
