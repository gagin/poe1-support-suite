#!/usr/bin/env python3
"""
Analyze a Timeless Jewel's effect on a character's passive tree.

Usage:
    python timeless_jewel_analysis.py <character_json> <jewel_slot_index> <general_name> <seed>

Example:
    python timeless_jewel_analysis.py pob/PathOfBuilding-2.59.2/tools/MiragMaraBatato.json 0 Kaom 12566

jewel_slot_index: the 'x' value from the jewel item in passive_tree.items (0-indexed into jewelSlots array)
general_name: Kaom, Rakiata, Akoya, Dominus, Maxarius, Avarius, Xibaqua, Doryani, Ahuana, Balbala, Nasima, Asenath, Caspiro, Cadiro, Victario
"""

import gzip
import json
import math
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
CLI = BASE / "pob/timeless-jewels/cli/timeless-jewel-cli"
SKILL_TREE_GZ = BASE / "pob/timeless-jewels/data/SkillTree.json.gz"
PASSIVE_SKILLS_GZ = BASE / "pob/timeless-jewels/data/passive_skills.json.gz"

ORBIT_RADII = [0, 82, 162, 335, 493, 662, 846]
ORBIT_COUNTS = [1, 6, 12, 12, 40, 72, 72]


def get_node_pos(node, groups):
    gid = str(node.get("group", ""))
    g = groups.get(gid, {})
    gx, gy = g.get("x", 0), g.get("y", 0)
    orbit = node.get("orbit", 0)
    orbit_index = node.get("orbitIndex", 0)
    radius = ORBIT_RADII[orbit] if orbit < len(ORBIT_RADII) else 0
    count = ORBIT_COUNTS[orbit] if orbit < len(ORBIT_COUNTS) else 12
    angle = 2 * math.pi * orbit_index / count - math.pi / 2
    return gx + radius * math.cos(angle), gy + radius * math.sin(angle)


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    char_file = sys.argv[1]
    slot_index = int(sys.argv[2])
    general_name = sys.argv[3]
    seed = sys.argv[4]

    # Load character
    with open(char_file) as f:
        char = json.load(f)
    allocated = set(char["passive_tree"].get("hashes", []))

    # Load skill tree
    with gzip.open(SKILL_TREE_GZ) as f:
        tree = json.load(f)
    nodes = tree["nodes"]
    groups = tree["groups"]
    jewel_slots = tree["jewelSlots"]

    # Load passive_skills key→graphid mapping
    with gzip.open(PASSIVE_SKILLS_GZ) as f:
        ps_list = json.load(f)
    key_to_graphid = {item["_key"]: item["PassiveSkillGraphId"] for item in ps_list}

    # Find socket node
    socket_node_id = str(jewel_slots[slot_index])
    socket_node = nodes.get(socket_node_id)
    if not socket_node:
        print(f"Socket node {socket_node_id} not found in tree")
        sys.exit(1)
    sx, sy = get_node_pos(socket_node, groups)

    # Get jewel data for this slot (radius)
    jewel_data = char["passive_tree"].get("jewel_data", {}).get(str(slot_index), {})
    radius_limit = jewel_data.get("radius", 1200)

    # Run calculator
    result = subprocess.run(
        [str(CLI), general_name, seed],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Calculator error: {result.stderr}")
        sys.exit(1)
    calc = json.loads(result.stdout)

    # Filter altered nodes to those within radius
    altered_in_radius = []
    for altered in calc.get("altered_nodes", []):
        graph_id = key_to_graphid.get(altered["node_id"])
        if graph_id is None:
            continue
        tree_node = nodes.get(str(graph_id))
        if tree_node is None:
            continue
        nx, ny = get_node_pos(tree_node, groups)
        dist = math.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
        if dist > radius_limit:
            continue
        stats = [s for s in altered["altered_stats"] if s]
        if not stats:
            continue
        altered_in_radius.append({
            "graph_id": graph_id,
            "name": tree_node.get("name", altered["node_name"]),
            "stats": stats,
            "is_notable": tree_node.get("isNotable", False),
            "is_keystone": tree_node.get("isKeystone", False),
            "dist": dist,
            "allocated": graph_id in allocated,
        })

    altered_in_radius.sort(key=lambda x: (not x["allocated"], x["dist"]))

    char_name = char.get("character", {}).get("name", "?")
    print(f"=== Timeless Jewel: {general_name} #{seed} ===")
    print(f"Character: {char_name}")
    print(f"Socket: jewelSlots[{slot_index}] = node {socket_node_id} at ({sx:.0f}, {sy:.0f})")
    print(f"Radius: {radius_limit}")
    print(f"Keystone granted/replaced: {calc.get('keystone', 'none')}")
    print()

    allocated_nodes = [n for n in altered_in_radius if n["allocated"]]
    unalloc_notables = [n for n in altered_in_radius if not n["allocated"] and n["is_notable"]]

    print(f"--- ALLOCATED nodes affected ({len(allocated_nodes)}) ---")
    for e in allocated_nodes:
        tag = "[KEYSTONE]" if e["is_keystone"] else ("[notable]" if e["is_notable"] else "[small]  ")
        action = "REPLACED" if e["is_keystone"] else "also gains"
        stat_str = " | ".join(e["stats"])
        print(f"  {tag} {e['name']}: {action}: {stat_str}")

    print()
    print(f"--- Unallocated NOTABLES in radius ({len(unalloc_notables)}) ---")
    for e in unalloc_notables:
        stat_str = " | ".join(e["stats"])
        print(f"  [notable] {e['name']} (dist={e['dist']:.0f}): would also grant: {stat_str}")


if __name__ == "__main__":
    main()
