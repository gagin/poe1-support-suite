#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp[cli]",
#   "httpx",
#   "beautifulsoup4",
# ]
# ///
"""
Build Expander - Import PoE character data and expand with full details.

Usage:
    python build_expander.py <character_json_file> [--league <league>] [--realm <realm>]
    
Or for interactive import from PoE:
    python build_expander.py --import [--character <name>] [--league <league>] [--realm <realm>]
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, "/Users/a/code/games/poe/POEMCP")

from scrapers.player.passives import _load_tree
from scrapers.player.items import _get_all_items, get_item_detail as fetch_item_detail
from scrapers.player.gems import _get_all_gems, get_gem_detail as fetch_gem_detail
from scrapers.economy.pricing import price_check as fetch_price_check, _resolve_league


REALM_MAP = {
    "pc": "pc",
    "xbox": "xbox",
    "sony": "sony",
    "PC": "pc",
    "XBOX": "xbox",
    "SONY": "sony",
}


def load_character_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def expand_passive_tree(character_data: dict) -> dict:
    """Expand passive tree nodes with full details."""
    print("Loading passive tree data...")
    tree = _load_tree()
    nodes_by_id = tree["by_id"]
    
    result = {
        "total_points": 0,
        "keystones": [],
        "notables": [],
        "masteries": [],
        "small_passives": [],
        "ascendancy": [],
        "other": [],
    }
    
    passive_data = character_data.get("passive_tree", {})
    hashes = passive_data.get("hashes", [])
    # mastery_effects: {nodeId_str: effectId_int} — which effect was chosen per mastery node
    mastery_effects = passive_data.get("mastery_effects", {})

    # Build lookup: nodeId_str -> {effect_id, stats} for the selected effect
    mastery_effect_lookup = {}
    for node_id_str, effect_id in mastery_effects.items():
        node = nodes_by_id.get(node_id_str)
        if node:
            for effect in node.get("masteryEffects", []):
                if effect["effect"] == effect_id:
                    mastery_effect_lookup[node_id_str] = {
                        "effect_id": effect_id,
                        "stats": effect.get("stats", []),
                    }
                    break

    # hashes is a flat list of node IDs
    for node_id in hashes:
        node_key = str(node_id)
        node = nodes_by_id.get(node_key)
        if node:
            result["total_points"] += 1
            node_type = node.get("_type", "unknown")
            node_info = {
                "id": node_id,
                "name": node.get("name", ""),
                "stats": node.get("stats", []),
                "type": node_type,
            }

            if node.get("isKeystone"):
                result["keystones"].append(node_info)
            elif node.get("isNotable"):
                result["notables"].append(node_info)
            elif node.get("isMastery"):
                # Enrich with the selected mastery effect
                effect_info = mastery_effect_lookup.get(node_key)
                if effect_info:
                    node_info["effect_id"] = effect_info["effect_id"]
                    node_info["stats"] = effect_info["stats"]
                result["masteries"].append(node_info)
            elif node.get("ascendancyName"):
                node_info["ascendancy"] = node.get("ascendancyName", "")
                result["ascendancy"].append(node_info)
            else:
                result["small_passives"].append(node_info)

    # Cluster jewel nodes live in jewel_data subgraphs, not in the main tree.
    # hashes_ex contains the allocated node IDs within those subgraphs.
    hashes_ex = set(str(h) for h in passive_data.get("hashes_ex", []))
    cluster_notables = []
    for slot_id, jewel_entry in passive_data.get("jewel_data", {}).items():
        subgraph_nodes = jewel_entry.get("subgraph", {}).get("nodes", {})
        for node_id_str, node in subgraph_nodes.items():
            if node_id_str not in hashes_ex:
                continue
            if node.get("isJewelSocket") or not node.get("stats"):
                continue
            node_info = {
                "id": int(node_id_str),
                "name": node.get("name", ""),
                "stats": node.get("stats", []),
                "cluster_slot": int(slot_id),
            }
            if node.get("isNotable"):
                cluster_notables.append(node_info)
            else:
                result["small_passives"].append(node_info)
    result["cluster_notables"] = cluster_notables

    return result


def find_unique_item(name: str, items_list: list[dict]) -> dict | None:
    """Find a unique item by name from the items list."""
    name_lower = name.lower()
    for item in items_list:
        if item["name"].lower() == name_lower:
            return item
    return None


def expand_items(character_data: dict, realm: str = "pc", league: str = "", include_swap: bool = False, skip_poedb: bool = False) -> tuple[dict, set]:
    """Expand character items with full details.
    
    Args:
        character_data: The character data dict
        realm: Realm for price checks
        league: League for price checks
        include_swap: If True, include weapon swap items and gems
        skip_poedb: If True, skip poedb.tw item lookup (use when site is down)
    """
    if skip_poedb:
        print("Skipping poedb.tw item lookup...")
        items_db = []
    else:
        print("Loading item database...")
        items_db = _get_all_items()
    
    items_data = character_data.get("items", {})
    inventory = items_data.get("items", [])  # Not "inventory"

    # Jewels socketed in the passive tree are in passive_tree.items, not items.items
    tree_items = character_data.get("passive_tree", {}).get("items", [])
    inventory = inventory + [i for i in tree_items if i]

    # Filter out weapon swap items unless include_swap is True
    if not include_swap:
        inventory = [i for i in inventory if i and i.get("inventoryId") not in ("Weapon2", "Offhand2")]
    
    result = {
        "equipment": [],
        "flasks": [],
        "jewels": [],
        "unknown": [],
        "prices": {},
    }

    unique_names = set()

    for idx, item in enumerate(inventory):
        if not item:
            continue
            
        # Skip weapon swap items if not included
        if not include_swap and item.get("inventoryId") in ("Weapon2", "Offhand2"):
            continue
            
        item_id = item.get("id", f"slot_{idx}")
        name = item.get("name", "")
        type_line = item.get("typeLine", "")
        base_type = item.get("baseType", "")
        
        item_entry = {
            "slot": idx,
            "id": item_id,
            "name": name,
            "typeLine": type_line,
            "baseType": base_type,
            "explicitMods": item.get("explicitMods", []),
            "implicitMods": item.get("implicitMods", []),
            "enchantMods": item.get("enchantMods", []),
            "fracturedMods": item.get("fracturedMods", []),
            "synthesizedMods": item.get("synthesizedMods", []),
            "craftedMods": item.get("craftedMods", []),
            "veiledMods": item.get("veiledMods", []),
            "corrupted": item.get("corrupted", False),
            "shaper": item.get("shaper", False),
            "elder": item.get("elder", False),
            "influences": item.get("influences", {}),
            "properties": item.get("properties", []),
            "requirements": item.get("requirements", []),
            "socketedGems": item.get("socketedItems", []),  # Note: socketedItems
        }
        
        # Determine category from frameType: 1=normal, 2=magic, 3=rare, 4=unique, 5=gem, 6=currency, 7=divination card, 8=quest item, 9=prophecy, 10=relic
        frame_type = item.get("frameType", 0)
        is_unique = frame_type == 4
        
        # Check for flask by base type
        if base_type and ("Flask" in base_type or "Quicksilver" in base_type or "Silver" in base_type or "Basilisk" in base_type or "Divine" in base_type or "Life" in base_type or "Mana" in base_type):
            result["flasks"].append(item_entry)
        # Check for jewels
        elif base_type and "Jewel" in base_type:
            if is_unique and name:
                unique_names.add(name)
                db_item = find_unique_item(name, items_db)
                if db_item:
                    item_entry["db_url"] = db_item.get("url", "")
            result["jewels"].append(item_entry)
        # Unique items
        elif is_unique and name:
            unique_names.add(name)
            db_item = find_unique_item(name, items_db)
            if db_item:
                item_entry["db_url"] = db_item.get("url", "")
                item_entry["db_implicits"] = db_item.get("implicits", [])
                item_entry["db_explicits"] = db_item.get("explicits", "")
            result["equipment"].append(item_entry)
        # Regular equipment
        elif base_type:
            result["equipment"].append(item_entry)
        else:
            result["unknown"].append(item_entry)
    
    return result, unique_names


def expand_skills(character_data: dict, include_swap: bool = False, skip_poedb: bool = False) -> dict:
    """Expand skill gems with full details.
    
    Args:
        character_data: The character data dict
        include_swap: If True, include gems from weapon swap
        skip_poedb: If True, skip poedb.tw gem lookup (use when site is down)
    """
    if skip_poedb:
        print("Skipping poedb.tw gem lookup...")
        gems_db = []
    else:
        print("Loading gem database...")
        gems_db = _get_all_gems()
    
    items_data = character_data.get("items", {})
    inventory = items_data.get("items", [])
    
    # Filter out weapon swap items unless include_swap is True
    if not include_swap:
        inventory = [i for i in inventory if i and i.get("inventoryId") not in ("Weapon2", "Offhand2")]
    
    result = {
        "active_skills": [],
        "support_gems": [],
        "all_gems": [],
    }
    
    all_gems = []
    
    for item in inventory:
        if not item:
            continue
        
        # Get socketed gems from this item
        socketed_gems = item.get("socketedItems", [])
        for gem in socketed_gems:
            # Gems use baseType or name field
            gem_name = gem.get("baseType", gem.get("name", ""))
            if gem_name:
                all_gems.append({
                    "name": gem_name,
                    "level": gem.get("level", 1),
                    "quality": gem.get("quality", 0),
                    "isEnabled": gem.get("enabled", True),
                })
                
                if gem.get("support"):
                    result["support_gems"].append(gem_name)
                else:
                    result["active_skills"].append(gem_name)
    
    result["all_gems"] = all_gems
    return result


async def get_prices(unique_names: set, realm: str, league: str) -> dict:
    """Get prices for unique items."""
    if not unique_names:
        return {}
    
    print(f"Fetching prices for {len(unique_names)} unique items...")
    prices = {}
    
    for name in unique_names:
        try:
            result = await fetch_price_check(name, league=league, realm=realm)
            prices[name] = result
        except Exception as e:
            prices[name] = f"Error: {e}"
    
    return prices


async def main():
    parser = argparse.ArgumentParser(description="Expand PoE character build with full details")
    parser.add_argument("character_file", help="Path to character JSON file (from lua import script)")
    parser.add_argument("--league", default="Mirage", help="League name (default: Mirage)")
    parser.add_argument("--realm", default="sony", help="Realm: pc, xbox, sony (default: sony)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--include-swap", action="store_true", help="Include weapon swap items and gems")
    parser.add_argument("--skip-poedb", action="store_true", help="Skip poedb.tw item lookup (use when site is down)")
    
    args = parser.parse_args()
    
    realm = REALM_MAP.get(args.realm, "sony")
    league = args.league
    
    # Load character from JSON file
    print(f"Loading character from {args.character_file}...")
    character_data = load_character_json(args.character_file)
    league = character_data.get("character", {}).get("league", args.league)
    
    if not character_data:
        print("No character data loaded")
        sys.exit(1)
    
    char_name = character_data.get("character", {}).get("name", "Unknown")
    print(f"\n=== Expanding build for: {char_name} ===\n")
    
    print("1. Expanding passive tree...")
    passives = expand_passive_tree(character_data)
    
    print("2. Expanding items...")
    try:
        items, unique_names = expand_items(character_data, realm=realm, league=league, include_swap=args.include_swap, skip_poedb=args.skip_poedb)
    except Exception as e:
        if "503" in str(e) or "poedb" in str(e).lower():
            print(f"poedb.tw unavailable ({e}), retrying with --skip-poedb...")
            items, unique_names = expand_items(character_data, realm=realm, league=league, include_swap=args.include_swap, skip_poedb=True)
        else:
            raise
    
    print("3. Expanding skill gems...")
    try:
        skills = expand_skills(character_data, include_swap=args.include_swap, skip_poedb=args.skip_poedb)
    except Exception as e:
        if "503" in str(e) or "poedb" in str(e).lower():
            print(f"poedb.tw unavailable ({e}), retrying with --skip-poedb...")
            skills = expand_skills(character_data, include_swap=args.include_swap, skip_poedb=True)
        else:
            raise
    
    print("4. Fetching prices...")
    prices = await get_prices(unique_names, realm=realm, league=league)
    
    expanded = {
        "character": character_data.get("character", {}),
        "passive_tree": passives,
        "items": items,
        "skills": skills,
        "prices": prices,
        "metadata": {
            "realm": args.realm,
            "league": league,
        },
    }
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_path = args.output or f"{char_name}_{timestamp}_expanded.json"
    with open(output_path, "w") as f:
        json.dump(expanded, f, indent=2)
    
    print(f"\n=== Build expanded and saved to: {output_path} ===")
    
    print(f"\n=== Summary ===")
    print(f"Character: {char_name}")
    print(f"Class: {character_data.get('character', {}).get('class', 'Unknown')}")
    print(f"Level: {character_data.get('character', {}).get('level', 'Unknown')}")
    print(f"Passive Points: {passives['total_points']}")
    print(f"Keystones: {len(passives['keystones'])}")
    print(f"Notables: {len(passives['notables'])}")
    print(f"Masteries: {len(passives['masteries'])}")
    print(f"Equipment slots: {len(items['equipment'])}")
    print(f"Flasks: {len(items['flasks'])}")
    print(f"Jewels: {len(items['jewels'])}")
    print(f"Active skills: {len(skills['active_skills'])}")
    print(f"Support gems: {len(skills['support_gems'])}")


if __name__ == "__main__":
    asyncio.run(main())
