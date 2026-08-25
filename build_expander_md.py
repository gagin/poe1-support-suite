#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Markdown Build Expander - Render a PoE character snapshot as compact, human-readable markdown.

Instead of the large expanded JSON, this collapses each aspect of the character onto
a single line per item / node, grouped under headings, so it can be skimmed manually.

Usage:
    python build_expander_md.py <character_json_file> [-o output.md]

The input is the raw download JSON produced by import_character_cli.lua
(the same file the regular expander consumes). It reuses the tree-expansion logic
from build_expander.py but skips network lookups, so it is fast and offline.
"""

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_expander import (
    load_character_json,
    expand_passive_tree,
    expand_items,
    expand_skills,
)

ARMOUR_SLOTS = {"Helm", "Helmet", "BodyArmour", "Gloves", "Boots", "Shield"}
JEWELLERY_SLOTS = {"Amulet", "Ring", "Ring2", "Belt", "Trinket", "Quiver"}
WEAPON_SLOTS = {"Weapon", "Weapon2", "Offhand", "Offhand2", "Staff", "Bow", "Wand", "Dagger", "Sceptre", "Claw", "OneHand"}

# Ordered groups for display. Items not matching a known slot fall into the group
# of the first key that is a substring of their inventoryId, else "Other".
GROUP_ORDER = [
    ("Weapons", WEAPON_SLOTS),
    ("Armour",  ARMOUR_SLOTS),
    ("Accessories", JEWELLERY_SLOTS),
    ("Other",   {"Other"}),
]


def group_for(inventory_id: str) -> str:
    for label, slots in GROUP_ORDER:
        if inventory_id in slots:
            return label
    return "Other"


def mod_descs(item: dict, fields) -> list:
    out = []
    for f in fields:
        mods = item.get(f, [])
        if not mods:
            continue
        descs = []
        for m in mods:
            if isinstance(m, dict):
                d = m.get("description")
                descs.append(d if d else m.get("name", str(m)))
            elif isinstance(m, str):
                descs.append(m)
        if descs:
            out.append(f"{f}: {' | '.join(descs)}".replace("implicitMods:", "implicit")
                .replace("explicitMods:", "explicit").replace("enchantMods:", "enchant"))
    return out


def prop_value(item: dict, target: str):
    for p in item.get("properties", []) or []:
        if p.get("name") == target and p.get("displayMode") == 0:
            return p["values"][0][0]
    return None


def item_display_name(item: dict) -> str:
    name = item.get("name", "")
    type_line = item.get("typeLine", "")
    if name and type_line and name != type_line:
        return f"{name}"
    return type_line or name or item.get("baseType", "")


def item_mods_part(item: dict) -> str:
    parts = []
    if item.get("corrupted"):
        parts.append("corrupted")
    for f in ("fracturedMods", "synthesizedMods", "craftedMods", "veiledMods", "mutatedMods"):
        if item.get(f):
            parts.append(f.replace("Mods", ""))
    req_level = None
    for r in item.get("requirements", []) or []:
        if r.get("name") == "Level":
            req_level = r["values"][0][0]
    if req_level:
        parts.append(f"req lvl {req_level}")
    mods = mod_descs(item, ["implicitMods", "explicitMods", "enchantMods"])
    if mods:
        parts.append(" | ".join(mods))
    return " — ".join(parts)


def item_line(item: dict) -> str:
    display = item_display_name(item)
    ilvl = item.get("ilvl")
    if ilvl:
        display += f" (ilvl {ilvl})"
    mods = item_mods_part(item)
    return display + (f" — {mods}" if mods else "")


def render_equipment(item_entries: dict) -> str:
    lines = []
    for label in [g[0] for g in GROUP_ORDER]:
        entries = [i for i in item_entries.get("equipment", []) if group_for(i["inventoryId"]) == label]
        if not entries:
            continue
        lines.append(f"## {label}")
        for item in entries:
            lines.append(f"- **{item['inventoryId']}**: {item_line(item)}")
    flasks = item_entries.get("flasks", [])
    if flasks:
        lines.append("## Flasks")
        for item in flasks:
            lines.append(f"- **{item['inventoryId']}**: {item_line(item)}")
    return "\n".join(lines)


def gem_summary(gem: dict) -> str:
    parts = [gem.get("baseType") or gem.get("name") or "?"]
    lvl = prop_value(gem, "Level")
    if lvl:
        parts.append(f"lvl {lvl}")
    quality = prop_value(gem, "Quality")
    if quality:
        q = str(quality).replace("%", "").replace("+", "")
        if q and q != "0":
            parts.append(f"q{q}%")
    if gem.get("corrupted"):
        parts.append("corrupted")
    return " ".join(parts)


def render_skills(item_entries: dict) -> str:
    sources = []
    for item in item_entries.get("equipment", []) + item_entries.get("flasks", []):
        gems = item.get("socketedGems", [])
        if not gems:
            continue
        sources.append((item_display_name(item), gems))

    lines = []
    for src, gems in sources:
        gems = [g for g in gems if "Jewel" not in (g.get("baseType") or "")]
        if not gems:
            continue
        lines.append(f"## {src}")
        for g in gems:
            lines.append(f"- {gem_summary(g)}")
    return "\n".join(lines)


def render_tree(tree: dict) -> str:
    lines = []
    lines.append(f"**{tree['total_points']} passives allocated**")

    if tree.get("ascendancy"):
        lines.append("## Ascendancy")
        for n in tree["ascendancy"]:
            label = f"{n.get('ascendancy', '')} — {n['name']}"
            if n.get("stats"):
                label += " · " + " | ".join(n["stats"])
            lines.append(f"- {label}")

    if tree.get("keystones"):
        lines.append("## Keystones")
        for n in tree["keystones"]:
            label = n["name"]
            if n.get("stats"):
                label += " — " + " | ".join(n["stats"])
            lines.append(f"- **{label}**")

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
        lines.append(f"## Cluster Notable Passives ({len(cluster)})")
        for n in cluster:
            lines.append(f"- {n['name']}: {' | '.join(n.get('stats', []))}")

    small = tree.get("small_passives", [])
    if small:
        distinct = sorted(set(n["name"] for n in small if n.get("name")))
        lines.append(f"## Small Passives ({len(small)} allocated — {len(distinct)} kinds)")
        lines.append(f"- _({', '.join(distinct)})_")

    return "\n".join(lines)


def jewelry_scope(character_data: dict) -> dict:
    """Locate every jewel on the character for display with its socket location."""
    tree_items = []
    for it in character_data.get("passive_tree", {}).get("items", []):
        if it and "Jewel" in (it.get("baseType") or ""):
            tree_items.append(it)

    socketed = []
    for it in character_data.get("items", {}).get("items", []):
        if not it:
            continue
        jewels = [g for g in (it.get("socketedItems") or []) if g and "Jewel" in (g.get("baseType") or "")]
        if jewels:
            parent = it.get("inventoryId") or ""
            name = it.get("name") or it.get("typeLine")
            if name and name != parent:
                parent = f"{parent} ({name})"
            socketed.append((parent, jewels))

    return {"passive_tree_items": tree_items, "socketed_jewels": socketed}


def render_jewels(item_entries: dict) -> str:
    def rarity(item):
        ft = item.get("frameType")
        if ft == 3:
            return "unique"
        return "rare"

    clusters, socketed_tree, equipped = [], [], []
    for it in item_entries.get("passive_tree_items", []):
        entry = (it, f"tree socket {it.get('x')}", rarity(it))
        if "Cluster" in (it.get("baseType") or ""):
            clusters.append(entry)
        else:
            socketed_tree.append(entry)

    for parent, gems in item_entries.get("socketed_jewels", []):
        for g in gems:
            equipped.append((g, f"in {parent}", rarity(g)))

    def emit(title, entries):
        if not entries:
            return []
        counts = {}
        for _, _, r in entries:
            counts[r] = counts.get(r, 0) + 1
        breakdown = ", ".join(f"{n} {r}" for r, n in sorted(counts.items()))
        out = [f"## {title} ({len(entries)} — {breakdown})"]
        for item, loc, _ in entries:
            display = item_display_name(item)
            type_line = item.get("typeLine")
            if type_line and type_line != display:
                display += f" ({type_line})"
            mods = item_mods_part(item)
            out.append(f"- **{display}** · {loc}{(' — ' + mods) if mods else ''}")
        return out

    lines = ("# Jewels", *emit("Cluster Jewels", clusters), *emit("Tree Jewels", socketed_tree), *emit("Equipment Jewels", equipped))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render a PoE character snapshot as compact markdown")
    parser.add_argument("character_file", help="Path to the raw character JSON (download output)")
    parser.add_argument("--output", "-o", help="Output .md file path (default: <char>_<ts>_expanded.md)")
    parser.add_argument("--include-swap", action="store_true", help="Include weapon swap items and gems")
    args = parser.parse_args()

    character_data = load_character_json(args.character_file)
    if not character_data:
        sys.exit("No character data loaded")

    char = character_data.get("character", {})
    char_name = char.get("name", "Unknown")

    tree = expand_passive_tree(character_data)
    items, _ = expand_items(character_data, skip_poedb=True, include_swap=args.include_swap)
    skills = expand_skills(character_data, skip_poedb=True, include_swap=args.include_swap)

    lines = []
    lines.append(f"# {char_name} — {char.get('class')} (Level {char.get('level')}) — {char.get('league')}")
    lines.append("")

    lines.append("# Equipment")
    lines.append(render_equipment(items))
    lines.append("")

    lines.append("# Passive Tree")
    lines.append(render_tree(tree))
    lines.append("")

    lines.append(render_jewels(jewelry_scope(character_data)))
    lines.append("")

    lines.append("# Skills")
    lines.append(render_skills(items))
    lines.append("")

    md = "\n".join(lines).rstrip() + "\n"

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_path = args.output or f"{char_name}_{timestamp}_expanded.md"
    with open(output_path, "w") as f:
        f.write(md)

    print(f"=== Markdown build rendered to: {output_path} ===")
    print(f"  Equipment: {len(items['equipment'])} | Flasks: {len(items['flasks'])} | Jewels: {len(items['jewels'])}")
    print(f"  Passives: {tree['total_points']} | Gems: {len(skills['all_gems'])}")


if __name__ == "__main__":
    main()