"""Soulwrest Phantasm bossing DPS calculator.

Encodes the model in ``phantomastress-eq-and-dps-method.md`` (Part 1 EQ ratios +
Part 2 full bossing DPS: hits + poison, robust to frame changes). The calculator is
*pure*: it takes an equipment/frame description and returns DPS numbers, with no
hidden state. Swapping a glove/ring is just feeding different parameters.

Usage (CLI):
    uv run python soulwrest_dps.py                     # current 17:29 frame (baseline)
    uv run python soulwrest_dps.py old                 # old glove+ring projection

Usage (library):
    from soulwrest_dps import compute_boss_dps, frames
    res = compute_boss_dps(frames["current"])
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Iterable

import phantasm_model as M

# --------------------------------------------------------------------------- #
# Frame model — everything that shapes DPS, fed as one dataclass.              #
# --------------------------------------------------------------------------- #

@dataclass
class Frame:
    name: str
    # -- base damage (constants: phantasm_model) ---------------------------- #
    intrinsic: float = M.INTRINSIC    # level-21 Summon Phantasm phys base
    add_eff: float = M.ADD_EFF        # phantasm added-damage effectiveness
    # flat chunks (all converted to chaos). key = label, value = avg flat.
    flatsum: dict[str, float] = field(default_factory=dict)
    # -- scaling pools ------------------------------------------------------ #
    inc: float = 0.0                  # total % increased minion damage
    cast: float = 0.0                 # total % minion cast speed (spellcaster)
    # -- attack -------------------------------------------                  #
    count: float = M.DEFAULT_COUNT    # phantasms active (Helm Doubled, NO Congregation — bossing config)
    base_aps: float = M.BASE_APS      # actions/sec per phantasm at 0 cast
    # -- more & DoT ---------------------------------------                  #
    more: list[float] = field(default_factory=lambda: list(M.POISON_MORE))
    # Unbound Ailments 21: "Supported Skills deal 20% more Damage with Ailments"
    # — poison-only (hits are not ailments). Set 1.0 for Unbound-less configs.
    unbound_ailment_more: float = M.UNBOUND_AILMENT_MORE
    amanamu_dot_pool: float = M.AMANAMU_POOL_BASE   # +30% DoT mult (additive pool)
    malevolence_more: float = M.MALEV   # Malevolence+Generosity DoT more
    # -- curses: exactly one of "despair_tc" or "sniper" -------------------  #
    curse: str = "despair_tc"
    # extra monster chaos-res penetration (% points) beyond the curse itself
    # (e.g. 20 => Despair's -30% becomes -50% total pen)
    # Void Beacon (allocated permanently via Forbidden Flame/Flesh jewels):
    # -20% enemy Chaos Res, always on, applies to hits AND DoT
    chaos_pen_bonus: float = M.VOID_BEACON_CHAOS_RES_REDUCTION
    # the bossing target's own chaos resistance (%); damage scales with
    # 1 - (boss_res - pen)/100, so Despair vs this boss is x1.00, not x1.30
    boss_chaos_res: float = M.BOSS_CHAOS_RES
    # Withered stacks on the target (minions apply via Unholy Might on hit;
    # sustained-bossing assumption: full stacks). 0 disables.
    withered_stacks: float = M.WITHERED_MAX_STACKS
    # Bloodline node: unholy-might damage Penetrates 10% chaos res -- HIT ONLY
    # (DoT never penetrates; poison base is pre-mitigation)
    minion_chaos_pen: float = M.BLOODLINE_CHAOS_PEN
    # -- poison ------------------------------------------------------------- #
    poison_base: float = M.POISON_BASE  # 20% of combined phys+chaos hit /s
    poison_dur: float = M.POISON_DUR_UNBOUND  # baseline bossing w/ Unbound (+65% dur)
    # poison chance 0..1 (>=1 == capped)
    poison_chance: float = 1.0
    # minion critical strike chance. A poison inflicted by a crit gains a +50%
    # damage-over-time multiplier, additive with other DoT-mult sources (the
    # model's amanamu_dot_pool). CD (100% less crit) zeroes this. 
    crit_chance: float = M.MINION_CRIT_CHANCE
    # minion critical strike multiplier (base 150%). A crit hit deals this x
    # damage; only affects the hit portion (the +20% from a crit wheel does not
    # touch poison, whose DoT-mult bonus is the flat +50% above).
    crit_multi: float = M.MINION_CRIT_MULTI

    # -- defensive stats (from jewels+belt, usually override per checked frame) #
    #  per-element resistance: cold/fire/lightning
    ele_res: dict[str, float] = field(default_factory=lambda: {"cold": 0.0, "fire": 0.0, "lightning": 0.0})
    chaos_res: float = 0.0              # chaos resistance
    life: float = 0.0                   # base life before inc_life
    es: float = 0.0                     # base ES before inc_es
    inc_life: float = 151.6             # % increased life (multiplies life)
    inc_es: float = 112.7               # % increased ES (multiplies es)

    # convenience ----------------------------------------------------------- #
    def base_flat(self) -> float:
        return self.intrinsic + self.add_eff * sum(self.flatsum.values())

    def more_prod(self) -> float:
        m = 1.0
        for x in self.more:
            m *= x
        return m




# --------------------------------------------------------------------------- #
# Jewels.db loader — build jewel-derived stats from socketed jewel ids.        #
# --------------------------------------------------------------------------- #

RES_KEYS = ("cold_res", "fire_res", "ltg_res", "chaos_res")


@dataclass
class JewelLoad:
    """Aggregated jewel-derived stats. Belt jewels already carry their ×belt_mult."""
    flatsum: dict[str, float]   # key = jewel id, val = flat (post belt mult)
    inc: float
    cast: float
    dot: float
    ele_res: dict[str, float]   # cold/fire/lightning (post belt mult)
    chaos_res: float
    life: float
    es: float
    pc: float
    belt_ids: set[str]
    tree_ids: set[str]

    def to_flatsum_dict(self) -> dict[str, float]:
        out = {f"jewel {k}": v for k, v in self.flatsum.items()}
        return out


def avg_flat(row) -> float:
    return (
        ((row["phys_l"] or 0.0) + (row["phys_h"] or 0.0)) / 2
        + ((row["chaos_l"] or 0.0) + (row["chaos_h"] or 0.0)) / 2
        + ((row["fire_l"] or 0.0) + (row["fire_h"] or 0.0)) / 2
    )


def load_jewels_from_db(db_path, belt_ids, tree_ids, belt_mult: float = 2.21) -> JewelLoad:
    """Read socketed jewels from jewels.db, aggregating flat/inc/cast/res/pc/life/es."""
    import sqlite3
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    jl = JewelLoad(
        flatsum={}, inc=0.0, cast=0.0, dot=0.0,
        ele_res={"cold": 0.0, "fire": 0.0, "lightning": 0.0},
        chaos_res=0.0, life=0.0, es=0.0, pc=0.0,
        belt_ids=set(belt_ids), tree_ids=set(tree_ids),
    )
    ids = tuple(list(belt_ids) + list(tree_ids))
    if not ids:
        con.close()
        return jl

    ph = ",".join("?" * len(ids))
    rows = con.execute(
        'SELECT id, phys_l, phys_h, chaos_l, chaos_h, fire_l, fire_h, inc, '
        'minion_cast_speed, life, es, pc, dot, str, '
        "cold_res, fire_res, ltg_res, chaos_res, all_res FROM jewels WHERE id IN (" + ph + ")",
        ids,
    ).fetchall()
    rowmap = {r["id"]: r for r in rows}
    con.close()

    for jid in ids:
        r = rowmap.get(jid)
        if r is None:
            raise KeyError(f"jewel {jid} not in jewels.db")
        mult = belt_mult if jid in jl.belt_ids else 1.0
        jl.flatsum[jid] = avg_flat(r) * mult
        jl.inc += (r["inc"] or 0.0) * mult
        jl.cast += (r["minion_cast_speed"] or 0.0) * mult
        jl.dot += (r["dot"] or 0.0) * mult
        jl.ele_res["cold"] += (r["cold_res"] or 0.0) * mult
        jl.ele_res["fire"] += (r["fire_res"] or 0.0) * mult
        jl.ele_res["lightning"] += (r["ltg_res"] or 0.0) * mult
        jl.chaos_res += (r["chaos_res"] or 0.0) * mult
        jl.life += ((r["life"] or 0.0) + (r["str"] or 0.0) / 2.0) * mult
        jl.es += (r["es"] or 0.0) * mult
        jl.pc += (r["pc"] or 0.0) * mult
        # all_res applies to cold/fire/lightning
        allres = (r["all_res"] or 0.0) * mult
        for k in ("cold", "fire", "lightning"):
            jl.ele_res[k] += allres

    return jl


def jewel_frame(name, db_path, belt_ids, tree_ids, gear_flat=None, gear_inc=0.0,
                gear_cast=0.0, gear_res=None, gear_chaos_res=0.0, gear_life=0.0,
                gear_es=0.0, curse="despair_tc", belt_mult: float = 2.21,
                flat_delta: Optional[dict[str, float]] = None,
                inc_delta: float = 0.0) -> Frame:
    """Build a Frame from a socketed jewel set + gear contribution fields.

    ``flat_delta`` subtracts flat from named jewels (e.g. to drop fire flat when
    fire->chaos is off) and ``inc_delta`` adjusts the total inc pool.
    """
    jl = load_jewels_from_db(db_path, belt_ids, tree_ids, belt_mult)
    flatsum = jl.to_flatsum_dict()
    if flat_delta:
        for jid, delta in flat_delta.items():
            key = f"jewel {jid}"
            if key in flatsum:
                flatsum[key] += delta
            else:
                raise KeyError(f"flat_delta jewel {jid} not in socketed set")
    if gear_flat:
        flatsum["gear"] = gear_flat
    er = {"cold": gear_res.get("cold", 0.0) if gear_res else 0.0,
          "fire": gear_res.get("fire", 0.0) if gear_res else 0.0,
          "lightning": gear_res.get("lightning", 0.0) if gear_res else 0.0}
    return Frame(
        name=name,
        flatsum=flatsum,
        inc=jl.inc + gear_inc + inc_delta,
        cast=jl.cast + gear_cast,
        ele_res={k: er[k] + jl.ele_res[k] for k in er},
        chaos_res=jl.chaos_res + gear_chaos_res,
        life=jl.life + gear_life,
        es=jl.es + gear_es,
        poison_chance=jl.pc / 100.0 if jl.pc < 100.0 else 1.0,
        amanamu_dot_pool=M.amanamu_pool(jl.dot),
        curse=curse,
    )


# --------------------------------------------------------------------------- #
# Stat checks — ele res cap/overcap, chaos cap, pc cap, life/es.               #
# --------------------------------------------------------------------------- #

RES_CAP = {"cold": 75, "fire": 75, "lightning": 75}
CHAOS_CAP = 75
PC_CAP = 100
ELE_RES_KEYS = ("cold", "fire", "lightning")


def check_frame(f: Frame) -> dict:
    """Validate res/pc/life/es breakpoints. Returns {metric: (status, value, detail)}."""
    report: dict = {}

    # elemental res: 75 = cap, value reported as overcap amount.
    for k in ELE_RES_KEYS:
        v = f.ele_res[k]
        cap = RES_CAP[k]
        if v >= cap:
            report[f"ele_{k}_overcap"] = ("OK", v - cap, f"total {v:+.0f} -> {v - cap:+.0f} over cap ({cap})")
        else:
            report[f"ele_{k}_overcap"] = ("FAIL", v, f"total {v:+.0f} -> {cap - v:+.0f} UNDER cap ({cap})")

    if f.chaos_res >= CHAOS_CAP:
        report["chaos_overcap"] = ("OK", f.chaos_res - CHAOS_CAP, f"total {f.chaos_res:+.0f} -> {f.chaos_res - CHAOS_CAP:+.0f} over cap ({CHAOS_CAP})")
    else:
        report["chaos_overcap"] = ("FAIL", f.chaos_res, f"total {f.chaos_res:+.0f} -> {CHAOS_CAP - f.chaos_res:+.0f} UNDER cap ({CHAOS_CAP})")

    pc = f.poison_chance * 100.0 if f.poison_chance <= 1.0 else 100.0
    if pc >= PC_CAP:
        report["pc_cap"] = ("OK", pc, f"{pc:+.1f}% (cap {PC_CAP}%)")
    else:
        report["pc_cap"] = ("FAIL", pc, f"{PC_CAP - pc:+.1f}% UNDER (need {PC_CAP}%)")

    report["life"] = ("info", f.life * (1 + f.inc_life / 100), f"{f.life:,.1f} base x +{f.inc_life:.1f}% = {f.life * (1 + f.inc_life/100):,.1f} total")
    report["es"] = ("info", f.es * (1 + f.inc_es / 100), f"{f.es:,.1f} base x +{f.inc_es:.1f}% = {f.es * (1 + f.inc_es/100):,.1f} total")
    return report


def print_checks(f: Frame) -> None:
    rep = check_frame(f)
    print(f"-- stat checks: {f.name}")
    for metric, (status, value, detail) in rep.items():
        mark = {"OK": "[OK] ", "FAIL": "[!!] ", "info": "......"}[status]
        print(f"  {mark}{metric:20} {detail}")



# --------------------------------------------------------------------------- #
# Snapshot-derived frame loader — builds a Frame from an expanded snapshot.    #
#                                                                              #
# Everything that shaped DPS is summed from the snapshot (tree+clusters,        #
# gear mods, supports, auras, socketed jewels) instead of being hardcoded.      #
# Only the model constants (intrinsic, add_eff, MORE, poison params, curse)     #
# stay fixed — they come from the documented method note, not from per-item      #
# snapshot text.                                                                #
# --------------------------------------------------------------------------- #

import json as _json
import re as _re

_MOD_SOURCES = ("implicitMods", "explicitMods", "enchantMods", "craftedMods", "fracturedMods")

# Class base attributes (start of the character sheet; Necromancer == Witch).
_CLASS_BASE_ATTR = {
    "Marauder": (32, 14, 14), "Ranger": (14, 32, 14), "Witch": (14, 14, 32),
    "Duelist": (23, 23, 14), "Templar": (23, 14, 23), "Shadow": (14, 23, 23),
    "Scion": (20, 20, 20),
}


def _class_base_attr(character) -> tuple[float, float, float]:
    cls = (character or {}).get("class") or ""
    base = _CLASS_BASE_ATTR.get(cls, (20, 20, 20))
    return float(base[0]), float(base[1]), float(base[2])


def _attributes(snap) -> tuple[float, float, float]:
    """Total Str/Dex/Int = class base + tree nodes + gear + jewels."""
    str_, dex, int_ = _class_base_attr(snap.get("character"))
    add_all = 0.0
    for sec in ("small_passives", "notables", "masteries", "keystones",
                "ascendancy", "cluster_notables"):
        for node in (snap.get("passive_tree") or {}).get(sec) or []:
            for st in node.get("stats") or []:
                m = _re.match(r"\+(\d+) to (Strength|Dexterity|Intelligence)", st)
                if m:
                    v = float(m.group(1))
                    {"Strength": (str_, "s"), "Dexterity": (dex, "d"),
                     "Intelligence": (int_, "i")}[m.group(2)]
                    if m.group(2) == "Strength": str_ += v
                    elif m.group(2) == "Dexterity": dex += v
                    else: int_ += v
                elif _re.match(r"\+(\d+) to all Attributes", st):
                    add_all += _num(st)
    for it in _all_items(snap):
        for m in _item_mods(it):
            mm = _re.match(r"\+(\d+) to (Strength|Dexterity|Intelligence)", m)
            if mm:
                v = float(mm.group(1))
                if mm.group(2) == "Strength": str_ += v
                elif mm.group(2) == "Dexterity": dex += v
                else: int_ += v
            elif _re.match(r"\+(\d+) to all Attributes", m):
                add_all += _num(m)
    str_ += add_all; dex += add_all; int_ += add_all
    return str_, dex, int_


def _item_mods(item) -> list[str]:
    out = []
    for f in _MOD_SOURCES:
        for m in item.get(f) or []:
            out.append(m.get("description") if isinstance(m, dict) else str(m))
    return out


def _all_items(snap) -> list[dict]:
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "inventoryId" in o and o.get("inventoryId"):
                out.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(snap.get("items"))
    return out


def _num(s: str) -> float:
    m = _re.search(r"([+-]?\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else 0.0


def _flat_avg(m: str) -> float:
    # "Minions deal X to Y additional <Phys/Chaos/Fire> Damage"
    mm = _re.match(r"Minions deal (\d+) to (\d+) additional (\w+) Damage", m)
    if not mm:
        return 0.0
    return (float(mm.group(1)) + float(mm.group(2))) / 2.0


def _jewel_signature(mods: list[str]) -> dict[str, float]:
    """Collapse a socketed jewel's mod strings into a {metric: value} signature.

    Used to disambiguate jewels that share a display name (e.g. two Whispering
    Globes / Grim Orbs) by matching against jewels.db parameters.
    """
    sig = {"flat": 0.0, "inc": 0.0, "cast": 0.0, "life": 0.0, "es": 0.0,
           "pc": 0.0, "cold": 0.0, "fire": 0.0, "lightning": 0.0, "hinder": 0.0}
    for m in mods:
        ml = m.lower()
        a = _flat_avg(m)
        if a:
            sig["flat"] += a
        mm = _re.search(r"minions deal (\d+)% increased damage if", ml)
        if mm:
            sig["inc"] += float(mm.group(1))
        mm = _re.match(r"minions have (\d+)% increased cast speed\b", ml)
        if mm:
            sig["cast"] += float(mm.group(1))
        mm = _re.search(r"(\d+)% increased attack and cast speed", ml)
        if mm:
            sig["cast"] += float(mm.group(1))
        mm = _re.match(r"\+(\d+) to maximum life\b", ml)
        if mm:
            sig["life"] += float(mm.group(1))
        mm = _re.match(r"\+(\d+) to maximum energy shield\b", ml)
        if mm:
            sig["es"] += float(mm.group(1))
        mm = _re.search(r"(\d+)% chance to poison enemies on hit", ml)
        if mm:
            sig["pc"] += float(mm.group(1))
        mm = _re.search(r"(\d+)% to (cold|fire|lightning) resistance", ml)
        if mm:
            sig[mm.group(2).lower()] += float(mm.group(1))
        mm = _re.search(r"(\d+)% chance to hinder enemies", ml)
        if mm:
            sig["hinder"] += float(mm.group(1))
    return sig


def _resolve_jewel(name: str, sig: dict[str, float], db_path: str,
                   belt_ids_override: dict[str, str] | None) -> str | None:
    """Map a socketed jewel's display name + signature to a jewels.db id.

    1. Explicit per-position override (resolves belt collisions: the two
       Whispering Globes differ by life/es/phy which mods often can't tell apart).
    2. Else: filter DB rows by display name, pick the one whose params best score
       against the socketed ''signature'' (flat/inc/cast/life/es/pc/res/hinder).
    3. Unmatched (unique jewels like Amanamu's Gaze / cluster jewels) -> None.
    """
    import sqlite3
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM jewels WHERE name = ?", (name,)).fetchall()]
    con.close()

    if belt_ids_override and name in belt_ids_override:
        oid = belt_ids_override[name]
        if any(r["id"] == oid for r in rows):
            return oid

    if not rows:
        return None

    best, best_score = None, 10 ** 9
    for r in rows:
        cand = {"flat": r["flat"] or 0.0, "inc": r["inc"] or 0.0,
                "cast": r["minion_cast_speed"] or 0.0, "life": r["life"] or 0.0,
                "es": r["es"] or 0.0, "pc": r["pc"] or 0.0,
                "hinder": r["hinder"] or 0.0}
        for k in ("cold", "fire", "lightning"):
            cand[k] = (r.get(k + "_res") or 0.0) + (r["all_res"] or 0.0)
        # lower score = better match. flat is the distinguishing DPS stat, so it
        # dominates; the rest break ties. A mod the DB has but the jewel lacks
        # (e.g. a fractured life the DB row didn't record) costs half.
        score = 0.0
        for k, v in sig.items():
            d = cand[k] - v
            if k == "flat":
                score += d * d * 4.0
            elif v or cand[k]:
                score += d * d if d > 0 else d * d * 0.5
        if score < best_score:
            best, best_score = r["id"], score
    return best


WEAPON_SET_SLOTS = {1: ("Weapon", "Offhand"), 2: ("Weapon2", "Offhand2")}


def _parse_flat(snap, weapon_set: int = 1) -> dict[str, float]:
    """flat from the chosen weapon set (staff) + Envy aura; phys+chaos+fire all
    as Chaos. Keyed by inventoryId so same-name staves (two Soulwrest rolls,
    one per swap) cannot collide and silently drop one."""
    slots = WEAPON_SET_SLOTS.get(weapon_set, WEAPON_SET_SLOTS[1])
    flat = {}
    for it in _all_items(snap):
        inv = it.get("inventoryId")
        mods = _item_mods(it)
        if inv in slots:
            # pick the bossing staff = the one with Minion phys flat
            for m in mods:
                a = _flat_avg(m)
                if a:
                    flat[f"staff {inv} " + it.get("name", inv)] = a
        elif inv == "Amulet":
            # Envy aura: "Adds 91 to 121 Chaos Damage to Spells" is granted by
            # Aul's Uprising (see phantasm_model.ENVY_SOURCE_AMULET), not by an
            # amulet mod — so include it only while that amulet is equipped.
            if (it.get("name") or "").lower() == M.ENVY_SOURCE_AMULET.lower():
                flat["envy"] = M.ENVY_FLAT_EFFECTIVE
    return flat


def _parse_tree(snap) -> dict:
    """Sum minion inc / cast / life / es / res from tree nodes + cluster notables."""
    pt = snap.get("passive_tree") or {}
    agg = {"inc": 0.0, "cast": 0.0, "life": 0.0, "es": 0.0,
           "res": {"cold": 0.0, "fire": 0.0, "lightning": 0.0, "chaos": 0.0}}

    def add_stats(stats):
        for s in stats or []:
            ls = s.lower()
            m = _re.match(r"minions deal (\d+)% increased damage", ls)
            if m:
                agg["inc"] += float(m.group(1))
            m = _re.match(r"minions have (\d+)% increased cast speed", ls)
            if m:
                agg["cast"] += float(m.group(1))
            m = _re.match(r"minions have (\d+)% increased attack and cast speed", ls)
            if m:
                agg["cast"] += float(m.group(1))
            # life / es on the character
            m = _re.match(r"\+(\d+) to maximum life\b", ls)
            if m:
                agg["life"] += float(m.group(1))
            m = _re.match(r"\+(\d+) to maximum energy shield\b", ls)
            if m:
                agg["es"] += float(m.group(1))
            m = _re.match(r"\+(\d+)% to (\w+) resistance", ls)
            if m:
                elem = m.group(2).lower()
                if elem == "all":
                    for k in ("cold", "fire", "lightning"):
                        agg["res"][k] += float(m.group(1))
                elif elem == "chaos":
                    agg["res"]["chaos"] += float(m.group(1))
                elif elem in agg["res"]:
                    agg["res"][elem] += float(m.group(1))
            m = _re.match(r"\+(\d+)% to all elemental resistances", ls)
            if m:
                for k in ("cold", "fire", "lightning"):
                    agg["res"][k] += float(m.group(1))

    for sec in ("small_passives", "notables", "masteries", "keystones", "ascendancy", "cluster_notables"):
        for node in pt.get(sec) or []:
            add_stats(node.get("stats"))
    return agg


def resolve_snapshot_jewels(snap, db_path: str = "jewels.db",
                            belt_order: Optional[list[str]] = None,
                            ) -> tuple[list[str], list[str], list[str]]:
    """Resolve socketed jewels (belt + tree + chest-abyssal) against jewels.db.

    Returns ``(belt_ids, tree_ids, chest_ids)``. Every jewel resolves by
    display name + mod signature; ``belt_order`` is an explicit positional
    override for the belt only. Same-name collisions (two Whispering Globe
    rolls) are separated by the parameter score. Chest abyssal sockets
    (Shroud of the Lightless-style) carry NO belt multiplier. Unmatched names
    are reported on stdout (normal for uniques like Amanamu's Gaze).
    """
    items = _all_items(snap)
    belt = next((it for it in items if it.get("inventoryId") == "Belt"), {})
    belt_sockets = [g for g in (belt.get("socketedGems") or []) if isinstance(g, dict) and g.get("name")]

    unresolved: list[str] = []
    belt_ids_resolved: list[str] = []
    for g in belt_sockets:
        ident = _resolve_jewel(g["name"], _jewel_signature(_item_mods(g)),
                               db_path, None)
        if ident:
            belt_ids_resolved.append(ident)
        else:
            unresolved.append("belt:" + g["name"])
    if belt_order:
        belt_ids_resolved = list(belt_order)[:len(belt_sockets)]

    jewel_ids: list[str] = []
    chest_ids: list[str] = []
    for it in items:
        inv = it.get("inventoryId")
        if inv == "PassiveJewels":
            n = it.get("name")
            if not n:
                continue
            sig = _jewel_signature(_item_mods(it))
            ident = _resolve_jewel(n, sig, db_path, None)
            if ident:
                if ident not in jewel_ids:
                    jewel_ids.append(ident)
            elif n != "Amanamu's Gaze":   # unique: legitimately absent from the db pool
                unresolved.append("tree:" + n)
        elif inv == "BodyArmour":
            for g in it.get("socketedGems") or []:
                if not isinstance(g, dict) or g.get("baseType") != "Ghastly Eye Jewel":
                    continue   # skill gems share these sockets
                n = g.get("name") or ""
                ident = _resolve_jewel(n, _jewel_signature(_item_mods(g)), db_path, None)
                if ident:
                    chest_ids.append(ident)
                else:
                    unresolved.append("chest:" + (n or "?"))
    if unresolved:
        print(f"[jewel-resolve] unmatched socketed jewels "
              f"(ok for uniques): {', '.join(unresolved)}")
    return belt_ids_resolved, jewel_ids, chest_ids


def read_socketed_gems(snap, weapon_set: int = 1) -> list[dict]:
    """Collect socketed gems from equipped items, for the ACTIVE weapon set only.

    The inactive weapon swap's gems are not in play, so its supports must not
    feed the model (the bow swap runs its own Predator/CD/Congregation setup).
    Returns dicts with {"name", "baseType", "level", "support"} where level is
    parsed from the gem's properties and support is True/False/None.
    """
    active_weapon_slots = {("Weapon", "Offhand")} if weapon_set == 1 \
        else {("Weapon2", "Offhand2")}
    active_weapon_slots = set(next(iter(active_weapon_slots)))
    gems: list[dict] = []
    for it in _all_items(snap):
        inv = it.get("inventoryId")
        if inv in ("Weapon", "Offhand", "Weapon2", "Offhand2") and inv not in active_weapon_slots:
            continue
        for g in it.get("socketedGems") or []:
            if not isinstance(g, dict) or not g.get("baseType"):
                continue
            props = {p.get("name"): p.get("values") for p in g.get("properties") or [] if p.get("values")}
            lvl_raw = str(props.get("Level", [["20"]])[0][0])
            m = _re.match(r"(\d+)", lvl_raw)
            gems.append({
                "name": g.get("name") or g.get("baseType"),
                "baseType": g.get("baseType"),
                "level": float(m.group(1)) if m else 20.0,
                "support": g.get("support"),
                "inventoryId": inv,
            })
    return gems


def build_frame_from_snapshot(snapshot_path: str, db_path: str = "jewels.db",
                              belt_mult: float = 2.21, name: str = "snapshot",
                              curse: str = "despair_tc",
                              belt_order: Optional[list[str]] = None,
                              weapon_set: int = 1) -> Frame:
    """Derive a Frame from an expanded snapshot JSON.

    Hybrid: tree/gear/supports/auras are read from the snapshot; socketed jewel
    stats come from jewels.db (belt jewels get ×belt_mult on every stat) because
    the snapshot omits some jewel mods (e.g. corrupted Hollow Oculus).
    ``weapon_set`` selects which weapon swap contributes flat/gems (1 = the
    Weapon/Offhand slots, 2 = Weapon2/Offhand2).
    """
    with open(snapshot_path) as f:
        snap = _json.load(f)

    # ---- jewels: belt = belt.socketedGems, tree = PassiveJewels ----------- #
    items = _all_items(snap)
    belt_ids_resolved, jewel_ids, chest_ids = resolve_snapshot_jewels(
        snap, db_path, belt_order)

    jl = load_jewels_from_db(db_path, belt_ids=belt_ids_resolved,
                             tree_ids=jewel_ids + chest_ids, belt_mult=belt_mult)

    # ---- flatsum: jewels + staff + envy ------------------------------------ #
    flatsum = jl.to_flatsum_dict()
    flatsum.update(_parse_flat(snap, weapon_set))

    # ---- inc / cast pools --------------------------------------------------- #
    tree = _parse_tree(snap)
    inc = jl.inc + tree["inc"]
    cast = jl.cast + tree["cast"]

    # ---- gem configuration: derive supports/auras/curses from socketed gems - #
    gems = read_socketed_gems(snap, weapon_set)
    cfg = M.derive_gem_config(gems)
    for w in cfg.warnings:
        print(f"[gem-config] {w}")

    # gear: gloves + ring2 minion inc/cast, auras, supports.
    # SKIP PassiveJewels: their "increased Damage / Cast Speed" lines are already
    # counted in jl.inc/jl.cast — scanning them here double-counted every jewel
    # carrying those mods (2026-08-21 bug: +55 inc / +18 cast phantom pool).
    for it in items:
        if it.get("inventoryId") in ("PassiveJewels", None):
            continue
        inv = it.get("inventoryId")
        for m in _item_mods(it):
            if _re.match(r"Minions deal (\d+)% increased Damage", m):
                inc += _num(m)
            if _re.match(r"Minions have (\d+)% increased Cast Speed", m):
                cast += _num(m)
            if _re.match(r"Minions have (\d+)% increased Attack and Cast Speed", m):
                cast += _num(m)
            if _re.match(r"Minions have (\d+)% increased Attack Speed", m):
                pass  # attack speed does nothing for the spellcasting phantasm
    # Flesh Offering / Vaal Haste cast contributions (phantasm_model, from gems)
    cast += cfg.cast_bump

    # ---- life / es / res from tree + gear + jewels -------------------------- #
    life = tree["life"] + jl.life
    es = tree["es"] + jl.es
    res = {"cold": tree["res"]["cold"] + jl.ele_res["cold"],
           "fire": tree["res"]["fire"] + jl.ele_res["fire"],
           "lightning": tree["res"]["lightning"] + jl.ele_res["lightning"]}
    chaos_res = tree["res"]["chaos"] + jl.chaos_res
    # elemental + chaos resistance penalty (acts 5 + 10)
    RES_PENALTY = -60.0
    for k in res: res[k] += RES_PENALTY
    chaos_res += RES_PENALTY
    for it in items:
        if it.get("inventoryId") in ("Helm", "BodyArmour", "Gloves", "Boots", "Belt", "Ring", "Ring2", "Amulet"):
            for m in _item_mods(it):
                # combined craft like "+19% to Fire and Cold Resistances" AND
                # singular "+27% to Lightning Resistance" / "+30% to Chaos Res"
                elems = set(); v = None
                com = _re.match(r"\+(\d+)% to ([\w ]+) Resist", m)
                if com:
                    v = float(com.group(1))
                    for part in com.group(2).split(" and "):
                        p = part.strip().lower()
                        if p in ("cold", "fire", "lightning", "chaos", "all"):
                            elems.add(p)
                if v is not None:
                    for elem in elems:
                        if elem == "all":
                            for k in ("cold", "fire", "lightning"):
                                res[k] += v
                        elif elem == "chaos":
                            chaos_res += v
                        else:
                            res[elem] += v
                ml = _re.match(r"\+(\d+) to maximum Life\b", m)
                if ml:
                    life += float(ml.group(1))

    # ---- base life/es: level base + attribute contributions ---------------- #
    # PoE base life = 38 + 12·level, then +1 life per 2 Str. Intelligence adds
    # 1% increased ES per 10 Int (a multiplier on the ES pool).
    # inherent Energy Shield on armour/helm (from item properties, not +ES mods)
    for it in items:
        if it.get("inventoryId") in ("Helm", "BodyArmour", "Gloves", "Boots", "Belt", "Weapon", "Weapon2", "Amulet", "Ring", "Ring2", "Trinket"):
            for p in it.get("properties") or []:
                if p.get("name") == "Energy Shield":
                    es += float(p["values"][0][0]) if p.get("values") else 0.0
    lvl = (snap.get("character") or {}).get("level") or 1
    str_, _dex, _int_ = _attributes(snap)
    life += 38 + 12 * lvl + str_ / 2.0
    # inc_es is a fixed model constant (112.7 ≈ the real 113% = 17 amulet + 30
    # staff + 21 Sanctum + 20 Purity + 25 int). Int's 1%/10 is already inside,
    # so we do NOT add int_/10 here.
    inc_es = Frame(name="").inc_es

    poison_chance = min(1.0, jl.pc / 100.0)
    if cfg.anger_flat:
        flatsum["anger"] = cfg.anger_flat

    return Frame(
        name=name,
        flatsum=flatsum,
        inc=inc,
        cast=cast,
        amanamu_dot_pool=M.amanamu_pool(jl.dot),
        ele_res=res,
        chaos_res=chaos_res,
        life=life,
        es=es,
        inc_es=inc_es,
        poison_chance=poison_chance,
        curse=cfg.curse or curse,
        # gem-derived configuration (phantasm_model.derive_gem_config)
        more=cfg.more,
        count=cfg.count,
        unbound_ailment_more=cfg.unbound_more,
        # poison duration tracks whether Unbound Ailments is actually socketed
        # (3.3s with Unbound, 2.0s base otherwise) -- never assume the pool.
        poison_dur=(M.POISON_DUR_UNBOUND if cfg.unbound_more > 1.0
                    else M.BASE_POISON_DUR),
        malevolence_more=M.MALEV if cfg.malevolence else 1.0,
    )


# --------------------------------------------------------------------------- #
# Current frame (snapshot-derived). Swapping gear = re-derive or patch inputs. #
# --------------------------------------------------------------------------- #

DEFAULT_SNAPSHOT = "build_snapshots/Phantomastress_202608151933_expanded.json"

frames: dict[str, Frame] = {
    "current": build_frame_from_snapshot(DEFAULT_SNAPSHOT, name="Current (snapshot-derived)"),
}

# --------------------------------------------------------------------------- #
# Engine                                                                       #
# --------------------------------------------------------------------------- #

@dataclass
class DpsResult:
    frame: str
    per_attack: float
    rate: float
    hit_pre: float
    poison_pre: float
    hit_cursed: float
    poison_cursed: float
    total_cursed: float

    def __str__(self) -> str:
        return (
            f"[{self.frame}]  pre-curse  hit {self.hit_pre:>12,.0f}  "
            f"poison {self.poison_pre:>12,.0f}  total {self.hit_pre+self.poison_pre:>13,.0f}\n"
            f"{'':21}   cursed   hit {self.hit_cursed:>12,.0f}  "
            f"poison {self.poison_cursed:>12,.0f}  total {self.total_cursed:>13,.0f}"
        )


def effective_poison_dur(f: Frame) -> float:
    dur = f.poison_dur
    if f.curse == "despair_tc":
        dur *= M.TEMP_CHAINS_DUR_MULT   # Temp Chains: debuffs expire 40% slower
    return dur


def compute_boss_dps(f: Frame) -> DpsResult:
    per_attack = f.base_flat() * (1 + f.inc / 100)
    rate = f.base_aps * (1 + f.cast / 100)
    total_rate = rate * f.count
    more = f.more_prod()
    chance = min(f.poison_chance or f.poison_chance, 1.0)
    dur = effective_poison_dur(f)

    hit_pre = per_attack * total_rate * more
    # crits raise the hit by (crit_multi-1) on crit_chance of hits; poison's
    # crit bonus is a separate flat +50% DoT mult (additive with the pool).
    hit_pre *= 1.0 + f.crit_chance * (f.crit_multi - 1.0)
    hit_pre *= M.withered_mult(f.withered_stacks)
    crit_poison_mult = 1.0 + f.crit_chance * M.CRIT_POISON_BONUS / max(f.amanamu_dot_pool, 1e-9)
    poison_pre = (
        per_attack * total_rate * f.poison_base * dur * chance
        * more * f.unbound_ailment_more * f.amanamu_dot_pool
        * f.malevolence_more * crit_poison_mult
    )
    poison_pre *= M.withered_mult(f.withered_stacks)

    # curses: Despair -30 chaos res vs the boss's own res (x1.00 at 30% boss res,
    # not x1.30), +35% DoT taken poison-only; Temp Chains' duration effect is
    # folded into `dur`; Sniper's Mark x1.34 hit only. chaos_pen_bonus stacks
    # extra -% monster chaos res (hits+DoT); minion_chaos_pen is true
    # penetration and boosts the HIT side only.
    hit_mult, poison_mult = M.curse_mults(f.curse, f.chaos_pen_bonus,
                                          f.boss_chaos_res, f.minion_chaos_pen)
    hit_cursed = hit_pre * hit_mult
    poison_cursed = poison_pre * poison_mult

    return DpsResult(
        frame=f.name,
        per_attack=per_attack,
        rate=rate,
        hit_pre=hit_pre,
        poison_pre=poison_pre,
        hit_cursed=hit_cursed,
        poison_cursed=poison_cursed,
        total_cursed=hit_cursed + poison_cursed,
    )


# --------------------------------------------------------------------------- #
# CLI / smoke                                                                   #
# --------------------------------------------------------------------------- #

def main(argv: Optional[list[str]] = None) -> None:
    from sys import argv as sys_argv
    argv = argv if argv is not None else sys_argv[1:]
    targets = argv if argv else ["current"]

    results = []
    for name in targets:
        if name not in frames:
            raise SystemExit(f"unknown frame {name!r}; available: {list(frames)}")
        results.append(compute_boss_dps(frames[name]))
        print(results[-1], "\n")
        print_checks(frames[name])
        print()

    if len(results) == 2:
        a, b = results
        print(
            f"delta vs {b.frame}: "
            f"{(b.total_cursed/a.total_cursed - 1) * 100:+.1f}% "
            f"(cursed total)"
        )


if __name__ == "__main__":
    main()