#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
PoE2 Build Expander - expand a downloaded PoE2 character into a readable build.

Unlike the PoE1 expander (build_expander.py), this has NO POEMCP dependency.
All passive-tree data is read directly from the tree.json shipped inside
PathOfBuilding-PoE2 (src/TreeData/<version>/tree.json), so it works offline.

Two-step harness (mirrors PoE1):
  1) uv run python poe2_import.py <CharName>
     -> writes PathOfBuilding-PoE2/tools/<CharName>_YYYYMMDDHHMM.json
  2) uv run python build_expander_poe2.py PathOfBuilding-PoE2/tools/<CharName>_*.json
     -> writes <CharName>_YYYYMMDDHHMM_expanded.json

Usage:
    uv run python build_expander_poe2.py <character_json> [--tree-version 0_5] [-o out.json]
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

POB2_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PathOfBuilding-PoE2")
TREE_DATA_DIR = os.path.join(POB2_ROOT, "src", "TreeData")


def _latest_tree_version() -> str:
    """Pick the highest numeric tree version dir (e.g. 0_5) under src/TreeData."""
    versions = []
    for name in os.listdir(TREE_DATA_DIR):
        if re.fullmatch(r"\d+_\d+", name) and os.path.isfile(
            os.path.join(TREE_DATA_DIR, name, "tree.json")
        ):
            versions.append(name)
    if not versions:
        raise SystemExit(f"No tree.json found under {TREE_DATA_DIR}")
    versions.sort(key=lambda v: tuple(int(p) for p in v.split("_")))
    return versions[-1]


def load_tree(version: str | None) -> dict:
    version = version or _latest_tree_version()
    path = os.path.join(TREE_DATA_DIR, version, "tree.json")
    print(f"Loading passive tree {version} from {path}...")
    with open(path) as f:
        tree = json.load(f)
    # Index nodes by string id. tree["nodes"] is keyed by id already.
    by_id = {}
    for nid, node in tree["nodes"].items():
        if isinstance(node, dict):
            by_id[str(nid)] = node
    return {"raw": tree, "by_id": by_id, "version": version}


def load_character_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def expand_passive_tree(character_data: dict, tree: dict) -> dict:
    nodes_by_id = tree["by_id"]
    result = {
        "total_points": 0,
        "keystones": [],
        "notables": [],
        "masteries": [],
        "ascendancy": [],
        "small_passives": [],
        "unresolved": [],
    }

    passive_data = character_data.get("passive_tree", {}) or {}
    hashes = passive_data.get("hashes", []) or []
    mastery_effects = passive_data.get("mastery_effects", {}) or {}
    # PoE2 replaces some allocated nodes (e.g. attribute nodes) via skill_overrides,
    # keyed by node id -> {name, stats, ...}. Apply these over the base tree data.
    skill_overrides = passive_data.get("skill_overrides", {}) or {}

    # Selected mastery effect per node -> its stats
    mastery_effect_lookup = {}
    for node_id_str, effect_id in mastery_effects.items():
        node = nodes_by_id.get(str(node_id_str))
        if node:
            for effect in node.get("masteryEffects", []) or []:
                if effect.get("effect") == effect_id:
                    mastery_effect_lookup[str(node_id_str)] = {
                        "effect_id": effect_id,
                        "stats": effect.get("stats", []),
                    }
                    break

    for node_id in hashes:
        key = str(node_id)
        node = nodes_by_id.get(key)
        if not node:
            result["unresolved"].append(node_id)
            continue
        result["total_points"] += 1
        override = skill_overrides.get(key)
        info = {
            "id": node_id,
            "name": (override or node).get("name", ""),
            "stats": (override or node).get("stats", node.get("stats", [])),
        }
        if override:
            info["overridden"] = True
            # An overridden node keeps its tree category unless it's clearly a
            # generic attribute swap; keep it simple and classify by base node.
        if node.get("isKeystone"):
            result["keystones"].append(info)
        elif node.get("isMastery"):
            eff = mastery_effect_lookup.get(key)
            if eff:
                info["effect_id"] = eff["effect_id"]
                info["stats"] = eff["stats"]
            result["masteries"].append(info)
        elif node.get("ascendancyName"):
            info["ascendancy"] = node.get("ascendancyName", "")
            result["ascendancy"].append(info)
        elif node.get("isNotable"):
            result["notables"].append(info)
        else:
            result["small_passives"].append(info)

    # Jewel-socket subgraph nodes (cluster/expansion jewels), if present.
    hashes_ex = set(str(h) for h in passive_data.get("hashes_ex", []) or [])
    cluster_notables = []
    for slot_id, jewel_entry in (passive_data.get("jewel_data", {}) or {}).items():
        subgraph_nodes = (jewel_entry.get("subgraph", {}) or {}).get("nodes", {}) or {}
        for node_id_str, node in subgraph_nodes.items():
            if node_id_str not in hashes_ex:
                continue
            if node.get("isJewelSocket") or not node.get("stats"):
                continue
            entry = {
                "id": int(node_id_str) if str(node_id_str).isdigit() else node_id_str,
                "name": node.get("name", ""),
                "stats": node.get("stats", []),
                "cluster_slot": slot_id,
            }
            if node.get("isNotable"):
                cluster_notables.append(entry)
            else:
                result["small_passives"].append(entry)
    result["cluster_notables"] = cluster_notables
    return result


def _mods(item: dict) -> dict:
    return {
        "explicitMods": item.get("explicitMods", []),
        "implicitMods": item.get("implicitMods", []),
        "enchantMods": item.get("enchantMods", []),
        "runeMods": item.get("runeMods", []),
        "desecratedMods": item.get("desecratedMods", []),  # PoE2 desecrated/well mods
        "fracturedMods": item.get("fracturedMods", []),
        "craftedMods": item.get("craftedMods", []),
        "corrupted": item.get("corrupted", False),
    }


SWAP_SLOTS = {"weapon2", "offhand2"}


def _gem_name(g: dict) -> str:
    return g.get("baseType") or g.get("name") or g.get("typeLine", "")


def expand_items(character_data: dict, include_swap: bool = False) -> dict:
    items_data = character_data.get("items", {}) or {}
    inventory = list(items_data.get("items", []) or [])
    # Tree-socketed jewels live under passive_tree.items in the GGG payload.
    tree_items = (character_data.get("passive_tree", {}) or {}).get("items", []) or []
    inventory += [i for i in tree_items if i]

    result = {"equipment": [], "flasks": [], "jewels": [], "charms": [],
              "runes": [], "granted_skills": [], "unknown": []}

    for idx, item in enumerate(inventory):
        if not item:
            continue
        inv = str(item.get("inventoryId", ""))
        if not include_swap and inv.lower() in SWAP_SLOTS:
            continue
        name = item.get("name", "")
        base_type = item.get("baseType", "")
        type_line = item.get("typeLine", "")
        frame_type = item.get("frameType", 0)

        # In PoE2 an item's socketedItems are runes/soul-cores (support == None)
        # or item-granted skills (support == False); they are NOT gem links.
        socketed = item.get("socketedItems", []) or []
        for sub in socketed:
            sname = _gem_name(sub)
            if not sname:
                continue
            if sub.get("support") is None:
                result["runes"].append({"name": sname, "socket": inv})
            else:
                result["granted_skills"].append({"name": sname, "socket": inv})

        entry = {
            "slot": idx,
            "inventoryId": inv,
            "name": name,
            "typeLine": type_line,
            "baseType": base_type,
            "frameType": frame_type,
            "isUnique": frame_type == 4,
            "properties": item.get("properties", []),
            "requirements": item.get("requirements", []),
            "runes": [_gem_name(s) for s in socketed if s.get("support") is None],
            **_mods(item),
        }
        hay = f"{base_type} {type_line}".lower()
        invl = inv.lower()
        if "charm" in hay or "charm" in invl:
            result["charms"].append(entry)
        elif "flask" in hay or invl.startswith("flask"):
            result["flasks"].append(entry)
        elif "jewel" in hay or "jewel" in invl:
            # PoE2 jewel bases (Time-Lost Diamond, etc.) lack "Jewel" in the name;
            # the socket's inventoryId (e.g. PassiveJewels1) is the reliable signal.
            result["jewels"].append(entry)
        elif base_type or name:
            result["equipment"].append(entry)
        else:
            result["unknown"].append(entry)
    return result


def _skill_level(skill: dict) -> str | int:
    for pr in skill.get("properties", []) or []:
        if pr.get("name") == "Level":
            for v in pr.get("values", []) or []:
                return v[0]
    return skill.get("level", "?")


def expand_skills(character_data: dict) -> dict:
    """PoE2 skill gems live in character.skills (carried through as skills_raw):
    each entry is a main active skill whose socketedItems are its support gems."""
    skills_raw = character_data.get("skills_raw", []) or []
    result = {"groups": [], "active_skills": [], "support_gems": []}
    for skill in skills_raw:
        main = _gem_name(skill)
        if not main:
            continue
        supports = []
        for sub in skill.get("socketedItems", []) or []:
            sn = _gem_name(sub)
            if sn:
                supports.append(sn)
        result["groups"].append({
            "skill": main,
            "level": _skill_level(skill),
            "supports": supports,
        })
        result["active_skills"].append(main)
        result["support_gems"].extend(supports)
    return result


def main():
    parser = argparse.ArgumentParser(description="Expand a PoE2 character build (offline).")
    parser.add_argument("character_file", help="JSON from poe2_import.py (supports globs)")
    parser.add_argument("--tree-version", help="Tree version dir under src/TreeData (default: latest)")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    # Support globs / newest match, mirroring the PoE1 Makefile convenience.
    matches = sorted(glob.glob(args.character_file), key=os.path.getmtime)
    path = matches[-1] if matches else args.character_file
    print(f"Loading character from {path}...")
    character_data = load_character_json(path)

    char = character_data.get("character", {}) or {}
    char_name = char.get("name", "Unknown")
    print(f"\n=== Expanding PoE2 build: {char_name} ===\n")

    tree = load_tree(args.tree_version)
    print("1. Expanding passive tree...")
    passives = expand_passive_tree(character_data, tree)
    print("2. Expanding items...")
    items = expand_items(character_data)
    print("3. Expanding skill gems...")
    skills = expand_skills(character_data)

    expanded = {
        "character": char,
        "passive_tree": passives,
        "items": items,
        "skills": skills,
        "metadata": {
            "game": "poe2",
            "tree_version": tree["version"],
            "source_file": os.path.basename(path),
            "generated": datetime.now().isoformat(timespec="seconds"),
        },
    }

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    out = args.output or f"{char_name}_{timestamp}_expanded.json"
    with open(out, "w") as f:
        json.dump(expanded, f, indent=2)
    print(f"\n=== Saved to: {out} ===")

    print("\n=== Summary ===")
    print(f"Character: {char_name}")
    asc_name = char.get("ascendancyClass") or char.get("ascendancy")
    if not asc_name and passives["ascendancy"]:
        asc_name = next((n.get("ascendancy") for n in passives["ascendancy"] if n.get("ascendancy")), None)
    print(f"Class: {char.get('class', 'Unknown')}  Ascendancy: {asc_name or '—'}")
    print(f"Level: {char.get('level', 'Unknown')}  League: {char.get('league', 'Unknown')}")
    print(f"Passive points: {passives['total_points']}")
    print(f"Keystones: {len(passives['keystones'])}  Notables: {len(passives['notables'])}  "
          f"Ascendancy: {len(passives['ascendancy'])}  Masteries: {len(passives['masteries'])}")
    if passives["unresolved"]:
        print(f"  ! {len(passives['unresolved'])} passive hashes not found in tree {tree['version']} "
              f"(tree version mismatch?)")
    print(f"Equipment: {len(items['equipment'])}  Jewels: {len(items['jewels'])}  "
          f"Flasks: {len(items['flasks'])}  Charms: {len(items['charms'])}  "
          f"Runes: {len(items['runes'])}")
    print(f"Skill groups: {len(skills['groups'])}  "
          f"(active {len(skills['active_skills'])}, supports {len(skills['support_gems'])})")
    for g in skills["groups"]:
        supp = ", ".join(g["supports"]) if g["supports"] else "—"
        print(f"  • {g['skill']} (L{g['level']}): {supp}")


if __name__ == "__main__":
    main()
