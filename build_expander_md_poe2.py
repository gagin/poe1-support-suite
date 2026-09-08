#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
PoE2 Markdown Build Expander - render a downloaded PoE2 character as compact,
human-readable markdown (the PoE2 counterpart to build_expander_md.py).

The expanded JSON is verbose; this collapses each aspect of the character onto
a single line per item / node / skill group, grouped under headings, so an agent
or a human can skim it quickly and cheaply.

Usage:
    uv run python build_expander_md_poe2.py <character_json> [--tree-version 0_5] [-o out.md]

The input is the normalized JSON from poe2_import.py (supports globs). It reuses
the tree expansion from build_expander_poe2.py (offline, no network).
"""

import argparse
import glob
import os
import re
from datetime import datetime

from build_expander_poe2 import (
    load_character_json,
    load_tree,
    expand_passive_tree,
    expand_items,
    expand_skills,
)

WEAPON_SLOTS = {"Weapon", "Weapon2", "Offhand", "Offhand2", "Sceptre", "Staff", "Wand", "Bow", "Quiver"}
ARMOUR_SLOTS = {"Helm", "Helmet", "BodyArmour", "Gloves", "Boots", "Shield"}
JEWELLERY_SLOTS = {"Amulet", "Ring", "Ring2", "Belt"}

GROUP_ORDER = [
    ("Weapons", WEAPON_SLOTS),
    ("Armour", ARMOUR_SLOTS),
    ("Accessories", JEWELLERY_SLOTS),
    ("Other", {"Other"}),
]


def group_for(inventory_id: str) -> str:
    for label, slots in GROUP_ORDER:
        if inventory_id in slots:
            return label
    return "Other"


def _clean(text: str) -> str:
    # Strip GGG's "[Tag|Display]" -> "Display" and bare "[Tag]" -> "Tag" noise.
    text = re.sub(r"\[([^\]|]+)\|([^\]]+)\]", r"\2", text)
    text = re.sub(r"\[([^\]|]+)\]", r"\1", text)
    return text


def _desc(m) -> str:
    if isinstance(m, dict):
        d = m.get("description") or m.get("name") or str(m)
    else:
        d = str(m)
    return _clean(d)


def item_display_name(item: dict) -> str:
    name = item.get("name", "")
    type_line = item.get("typeLine", "")
    if name and type_line and name != type_line:
        return name
    return type_line or name or item.get("baseType", "")


def prop_value(item: dict, target: str):
    for p in item.get("properties", []) or []:
        if p.get("name") == target and p.get("displayMode") == 0:
            for v in p.get("values", []) or []:
                return v[0]
    return None


def item_line(item: dict) -> str:
    display = item_display_name(item)
    base = item.get("baseType")
    type_line = item.get("typeLine", "")
    if base and base not in (display, type_line):
        display += f" ({base})"
    ilvl = item.get("ilvl")
    if ilvl:
        display += f" (ilvl {ilvl})"

    bits = []
    if item.get("corrupted"):
        bits.append("corrupted")
    for flag in ("craftedMods", "fracturedMods", "desecratedMods"):
        if item.get(flag):
            bits.append(flag.replace("Mods", ""))
    req = None
    for r in item.get("requirements", []) or []:
        if r.get("name") == "Level":
            req = r["values"][0][0]
    if req:
        bits.append(f"req lvl {req}")
    mods = []
    for f in ("implicitMods", "explicitMods", "enchantMods", "runeMods"):
        m = " | ".join(_desc(x) for x in (item.get(f) or []))
        if m:
            mods.append(m)
    if mods:
        bits.append(" | ".join(mods))
    return display + ((" — " + ", ".join(bits)) if bits else "")


def render_equipment(items: dict) -> str:
    lines = []
    for label in [g[0] for g in GROUP_ORDER]:
        entries = [i for i in items.get("equipment", []) if group_for(i["inventoryId"]) == label]
        if not entries:
            continue
        lines.append(f"## {label}")
        for it in entries:
            lines.append(f"- **{it['inventoryId']}**: {item_line(it)}")
    if items.get("flasks"):
        lines.append("## Flasks")
        for it in items["flasks"]:
            lines.append(f"- **{it['inventoryId']}**: {item_line(it)}")
    if items.get("charms"):
        lines.append("## Charms")
        for it in items["charms"]:
            lines.append(f"- **{it['inventoryId']}**: {item_line(it)}")
    return "\n".join(lines)


def render_jewels(items: dict) -> str:
    jewels = items.get("jewels", [])
    if not jewels:
        return ""
    rare = sum(1 for j in jewels if not j.get("isUnique"))
    unique = len(jewels) - rare
    lines = ["## Jewels"]
    for it in jewels:
        tag = "unique" if it.get("isUnique") else "rare"
        lines.append(f"- **{item_line(it)}** ({it.get('inventoryId')}, {tag})")
    return "\n".join(lines)


def render_runes(items: dict) -> str:
    runes = items.get("runes", [])
    if not runes:
        return ""
    by_socket = {}
    for r in runes:
        by_socket.setdefault(r.get("socket", "?"), []).append(r.get("name"))
    lines = ["## Runes"]
    for socket in sorted(by_socket):
        lines.append(f"- {socket}: {', '.join(by_socket[socket])}")
    return "\n".join(lines)


def render_skills(skills: dict) -> str:
    lines = []
    for g in skills.get("groups", []):
        name = g.get("skill", "?")
        lvl = g.get("level")
        head = f"**{name}**"
        if lvl not in (None, "", "?"):
            head += f" (L{lvl})"
        supp = g.get("supports", [])
        lines.append(f"- {head}" + (f": {', '.join(supp)}" if supp else ": —"))
    return "\n".join(lines)


def render_tree(tree: dict) -> str:
    lines = [f"**{tree['total_points']} passives allocated**"]
    if tree.get("keystones"):
        lines.append("## Keystones")
        for n in tree["keystones"]:
            label = n["name"]
            if n.get("stats"):
                label += " — " + " | ".join(n["stats"])
            lines.append(f"- **{label}**")
    if tree.get("ascendancy"):
        lines.append("## Ascendancy")
        for n in tree["ascendancy"]:
            label = f"{n.get('ascendancy', '')} — {n['name']}"
            if n.get("stats"):
                label += " · " + " | ".join(n["stats"])
            lines.append(f"- {label}")
    if tree.get("masteries"):
        lines.append(f"## Masteries ({len(tree['masteries'])})")
        for n in tree["masteries"]:
            lines.append(f"- {n['name']}: {' | '.join(n.get('stats', []))}")
    if tree.get("notables"):
        lines.append(f"## Notable Passives ({len(tree['notables'])})")
        for n in tree["notables"]:
            lines.append(f"- {n['name']}: {' | '.join(n.get('stats', []))}")
    cluster = tree.get("cluster_notables", [])
    if cluster:
        lines.append(f"## Cluster Notables ({len(cluster)})")
        for n in cluster:
            lines.append(f"- {n['name']}: {' | '.join(n.get('stats', []))}")
    small = tree.get("small_passives", [])
    if small:
        distinct = sorted(set(n["name"] for n in small if n.get("name")))
        lines.append(f"## Small Passives ({len(small)} allocated — {len(distinct)} kinds)")
        lines.append(f"- _({', '.join(distinct)})_")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render a PoE2 character snapshot as compact markdown")
    parser.add_argument("character_file", help="Normalized JSON from poe2_import.py (supports globs)")
    parser.add_argument("--tree-version", help="Tree version dir under src/TreeData (default: latest)")
    parser.add_argument("--output", "-o", help="Output .md file path (default: <char>_<ts>_expanded.md)")
    args = parser.parse_args()

    matches = sorted(glob.glob(args.character_file), key=os.path.getmtime)
    path = matches[-1] if matches else args.character_file
    print(f"Loading character from {path}...")
    character_data = load_character_json(path)

    char = character_data.get("character", {}) or {}
    char_name = char.get("name", "Unknown")

    tree = load_tree(args.tree_version)
    passives = expand_passive_tree(character_data, tree)
    items = expand_items(character_data)
    skills = expand_skills(character_data)

    asc_name = char.get("ascendancyClass") or char.get("ascendancy")
    if not asc_name and passives["ascendancy"]:
        asc_name = next((n.get("ascendancy") for n in passives["ascendancy"] if n.get("ascendancy")), None)

    parts = []
    parts.append(f"# {char_name} — {char.get('class')} (Level {char.get('level')}) — {char.get('league')}")
    if asc_name:
        parts.append(f"Ascendancy: {asc_name}")
    parts.append("")
    parts.append("# Equipment")
    parts.append(render_equipment(items))
    parts.append("")
    parts.append("# Passive Tree")
    parts.append(render_tree(passives))
    parts.append("")
    j = render_jewels(items)
    if j:
        parts.append(j); parts.append("")
    r = render_runes(items)
    if r:
        parts.append(r); parts.append("")
    parts.append("# Skills")
    parts.append(render_skills(skills))

    md = "\n".join(parts).rstrip() + "\n"

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    out = args.output or f"{char_name}_{timestamp}_expanded.md"
    with open(out, "w") as f:
        f.write(md)

    print(f"\n=== Markdown build rendered to: {out} ===")
    print(f"  Equipment: {len(items['equipment'])} | Jewels: {len(items['jewels'])} | "
          f"Flasks: {len(items['flasks'])} | Charms: {len(items['charms'])}")
    print(f"  Passives: {passives['total_points']} | Skill groups: {len(skills['groups'])}")


if __name__ == "__main__":
    main()