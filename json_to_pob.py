#!/usr/bin/env python3
"""
Convert character JSON to PoB import string.

Usage:
    python json_to_pob.py <character.json> [--include-swap]
"""

import argparse
import base64
import json
import zlib
import sys
import os

def escape_xml(s):
    """Escape special XML characters."""
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def convert_items_to_pob(items_list, include_swap=False):
    """Convert items to PoB XML format."""
    lines = []
    
    for idx, item in enumerate(items_list):
        if not item:
            continue
        
        # Skip weapon swap unless included
        if not include_swap and item.get("inventoryId") in ("Weapon2", "Offhand2"):
            continue
            
        inv_id = item.get("inventoryId", "")
        
        # Determine slot name
        slot_map = {
            "Weapon": "Weapon1",
            "Offhand": "Weapon1Offhand",
            "Weapon2": "Weapon2",
            "Offhand2": "Weapon2Offhand",
            "Helm": "Head",
            "BodyArmour": "Body",
            "Gloves": "Hands",
            "Boots": "Feet",
            "Amulet": "Amulet",
            "Ring": "Ring",
            "Ring2": "Ring2",
            "Belt": "Belt",
        }
        slot = slot_map.get(inv_id, inv_id)
        
        # Get item data
        base_type = item.get("baseType", "")
        name = item.get("name", "")
        type_line = item.get("typeLine", "")
        
        # Build the PoB item line
        # Format: slot:id:variant:category:league:exarchEater:
        # Then baseType:Name:typeLine:variant:level:quality:...

        # Start with slot and unique identifier
        item_id = item.get("id", f"import_{idx}")
        
        # Check if it's a unique
        frame_type = item.get("frameType", 0)
        is_unique = frame_type == 4
        
        # Build the item string
        parts = [slot, item_id, "", "", "", ""]
        line = ":".join(parts)
        
        # Second part: baseType:Name:typeLine
        name_str = name if name else ""
        type_str = type_line if type_line else base_type
        second = f"{base_type}:{name_str}:{type_str}"
        
        # Third part: variant:level:quality
        variant = ""
        level = ""
        quality = ""
        third = f"{variant}:{level}:{quality}"
        
        # Fourth part: serial:...
        serial = ""
        
        full_line = f"{line}\0{second}\0{third}\0{serial}"
        
        lines.append(full_line)
    
    return lines

def convert_skills_to_pob(items_list, include_swap=False):
    """Convert skills to PoB format."""
    lines = []
    
    skill_id = 1
    for idx, item in enumerate(items_list):
        if not item:
            continue
        
        # Skip weapon swap unless included
        if not include_swap and item.get("inventoryId") in ("Weapon2", "Offhand2"):
            continue
        
        socketed = item.get("socketedItems", [])
        if not socketed:
            continue
        
        for gem in socketed:
            gem_name = gem.get("baseType", gem.get("name", ""))
            if not gem_name:
                continue
            
            gem_level = gem.get("level", 1)
            gem_quality = gem.get("quality", 0)
            gem_enabled = gem.get("enabled", True)
            
            # Format: socketGroup:skill:skillId:level:quality:enable:virtuality:noSupports:source
            
            # Determine socket group (1 = main, else group number)
            is_main = (idx == 0)  # First equipped item is main
            
            # Build skill entry
            skill_line = f"1:{gem_name}:{skill_id}:{gem_level}:{gem_quality}:{1 if gem_enabled else 0}:0:0:{item.get('id', '')}"
            
            lines.append(skill_line)
            skill_id += 1
    
    return lines

def convert_passive_to_pob(character_data):
    """Convert passive tree to PoB XML format."""
    passive = character_data.get("passive_tree", {})
    hashes = passive.get("hashes", [])
    mastery_effects = passive.get("masteryEffects", {})
    
    # Convert hashes to space-separated string
    hash_str = " ".join(str(h) for h in hashes)
    
    # Get class info from character
    char_class = character_data.get("character", {}).get("class", "")
    
    # Map class names to IDs
    class_map = {
        "Scion": 0, "Marauder": 1, "Ranger": 2, " Witch": 3,
        "Duelist": 4, "Templar": 5, "Shadow": 6, "Ascendant": 7
    }
    class_id = class_map.get(char_class, 0)
    
    return {
        "hashes": hash_str,
        "classId": class_id,
        "ascendClassId": 0,  # Would need to determine from passive tree
    }

def generate_pob_xml(character_data, include_swap=False):
    """Generate PoB import XML."""
    character = character_data.get("character", {})
    items = character_data.get("items", {}).get("items", [])
    passive = character_data.get("passive_tree", {})
    
    # Convert items
    item_lines = convert_items_to_pob(items, include_swap)
    skill_lines = convert_skills_to_pob(items, include_swap)
    
    # Get passive tree info
    hashes = passive.get("hashes", [])
    mastery_effects = passive.get("masteryEffects", {})
    
    # Build XML
    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>']
    xml_lines.append('<PathOfBuilding>')
    
    # Build section
    xml_lines.append('  <Build>')
    xml_lines.append('    <Character')
    xml_lines.append(f'      name="{escape_xml(character.get("name", "Imported"))}"')
    xml_lines.append(f'      classId="{character.get("class", "Scion")}"')
    xml_lines.append(f'      ascendClassId="0"')
    xml_lines.append(f'      level="{character.get("level", 1)}"')
    xml_lines.append('      realm="PC"')
    xml_lines.append('    />')
    xml_lines.append('  </Build>')
    
    # Skills section
    xml_lines.append('  <Skills>')
    for skill in skill_lines:
        xml_lines.append(f'    <Skill>{escape_xml(skill)}</Skill>')
    xml_lines.append('  </Skills>')
    
    # Items section  
    xml_lines.append('  <Items>')
    for item in item_lines:
        xml_lines.append(f'    <Item>{escape_xml(item)}</Item>')
    xml_lines.append('  </Items>')
    
    # Tree section
    xml_lines.append('  <Tree>')
    xml_lines.append(f'    <Spec')
    xml_lines.append(f'      classId="{character.get("class", "Scion")}"')
    xml_lines.append(f'      ascendClassId="0"')
    xml_lines.append(f'      hashes="{" ".join(str(h) for h in hashes)}"')
    xml_lines.append(f'    />')
    xml_lines.append('  </Tree>')
    
    xml_lines.append('</PathOfBuilding>')
    
    return "\n".join(xml_lines)

def compress_and_encode(xml_string):
    """Compress with zlib (deflate) and base64 encode with URL-safe replacement."""
    compressed = zlib.compress(xml_string.encode('utf-8'), 9)
    encoded = base64.b64encode(compressed).decode('ascii')
    # URL-safe replacement
    encoded = encoded.replace('+', '-').replace('/', '_')
    return encoded

def main():
    parser = argparse.ArgumentParser(description="Convert character JSON to PoB import string")
    parser.add_argument("character_file", help="Path to character JSON file")
    parser.add_argument("--include-swap", action="store_true", help="Include weapon swap items and gems")
    parser.add_argument("--output", "-o", help="Output file for import string")
    
    args = parser.parse_args()
    
    # Load character data
    with open(args.character_file, 'r') as f:
        character_data = json.load(f)
    
    # Generate PoB XML
    xml = generate_pob_xml(character_data, args.include_swap)
    
    # Compress and encode
    import_string = compress_and_encode(xml)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(import_string)
        print(f"PoB import string saved to {args.output}")
    else:
        print(import_string)

if __name__ == "__main__":
    main()
