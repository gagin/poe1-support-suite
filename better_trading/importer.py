"""
Better Trading Import Tool

Generates trade links and import strings for the Better Trading browser extension
from item descriptions pasted by the user.
"""

import re
import json
import base64
from urllib.parse import quote

ITEM_CATEGORY_MAP = {
    # Weapons
    "Claw": "weapon",
    "Dagger": "weapon",
    "Wand": "weapon",
    "One Hand Sword": "weapon",
    "One Hand Axe": "weapon",
    "One Hand Mace": "weapon",
    "Sceptre": "weapon",
    "Thrusting One Hand Sword": "weapon",
    "Bow": "weapon",
    "Staff": "weapon",
    "Two Hand Sword": "weapon",
    "Two Hand Axe": "weapon",
    "Two Hand Mace": "weapon",
    "Warstaff": "weapon",
    "Fishing Rod": "weapon",
    # Off-hand
    "Quiver": "accessory",
    "Shield": "armour",
    # Armour
    "Gloves": "armour",
    "Boots": "armour",
    "Body Armour": "armour",
    "Helmet": "armour",
    # Jewellery
    "Amulet": "jewelry",
    "Ring": "jewelry",
    "Belt": "jewelry",
    # Other
    "Jewel": "jewel",
    "Flask": "flask",
    "Map": "map",
    "Skill Gem": "skillgem",
    "Cluster Jewel": "jewel",
}

TRADE_BASE_URL = "https://www.pathofexile.com/trade"


def _normalize_mod(mod: str) -> str:
    """Normalize a modifier for trade search."""
    mod = mod.strip()
    mod = re.sub(r'\s+', ' ', mod)
    return mod


def _extract_base_type(item_text: str) -> str | None:
    """Extract the base type from item text.
    
    Looks for patterns like:
    - "Rare Bow" at start of line
    - "Saint's Hauberk" (unique name)
    - "Sorcerer Boots" (rare item base)
    """
    lines = item_text.strip().split('\n')
    
    # Check first non-empty line for item header
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Unique item pattern: "Item Name"
        if line.startswith('"') and line.endswith('"'):
            return line.strip('"')
        
        # Rare item pattern: "Rare Amulet" or "Rare Two-Toned Steel Ring"
        rare_match = re.match(r'^Rare\s+(.+)$', line, re.IGNORECASE)
        if rare_match:
            return rare_match.group(1).strip()
        
        # Magic item pattern: "Magic Gloves"
        magic_match = re.match(r'^Magic\s+(.+)$', line, re.IGNORECASE)
        if magic_match:
            return magic_match.group(1).strip()
        
        # Normal item (base type only)
        if line in ITEM_CATEGORY_MAP or any(
            line.endswith(cat) for cat in ["Boots", "Gloves", "Helmet", "Armour", 
                                           "Sword", "Axe", "Mace", "Bow", "Staff",
                                           "Dagger", "Wand", "Claw", "Sceptre",
                                           "Ring", "Amulet", "Belt", "Flask", "Jewel",
                                           "Quiver", "Shield"]
        ):
            return line
        
        # Default: return first significant line
        if len(line) > 3 and not line.startswith('--------'):
            return line
    
    return None


def _guess_category(base_type: str) -> str:
    """Guess the trade category from base type."""
    base_lower = base_type.lower()
    
    # Direct mappings
    for key, cat in ITEM_CATEGORY_MAP.items():
        if key.lower() in base_lower:
            return cat
    
    # Fallback - check keywords (check if base type ends with or contains)
    if any(w in base_lower for w in ["ring", "amulet", "belt"]):
        return "jewelry"
    if any(base_lower.endswith(w) for w in ["gloves", "boots", "helmet", "shield", "coat", "jack", "vest", "plate", "cuirass", "doublet", "mantle", "robe"]):
        return "armour"
    if "armour" in base_lower or "leather" in base_lower:
        return "armour"
    if any(base_lower.endswith(w) for w in ["bow", "wand", "dagger", "sword", "axe", "mace", "staff", "claw", "sceptre", "blade"]):
        return "weapon"
    if "flask" in base_lower:
        return "flask"
    if "jewel" in base_lower:
        return "jewel"
    if "map" in base_lower:
        return "map"
    if "quiver" in base_lower:
        return "accessory"
    
    return "weapon"  # Default


def _extract_modifiers(item_text: str) -> list[str]:
    """Extract modifiers from item text."""
    mods = []
    
    # Skip header lines
    skip_patterns = [
        r'^Item Class:',
        r'^Rarity:',
        r'^--------',
        r'^Requirements:',
        r'^Sockets:',
        r'^Linked',
        r'^Corrupted',
        r'^Synthesised',
        r'^Fractured',
    ]
    
    lines = item_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        
        # Skip empty and header lines
        if not line:
            continue
        if any(re.match(p, line, re.IGNORECASE) for p in skip_patterns):
            continue
        
        # Skip lines that are just numbers (ilvl, quality, etc.)
        if re.match(r'^(\d+|-\d+)$', line):
            continue
        
        # Skip socket info
        if re.match(r'^[RGBWA-]+$', line):
            continue
        
        # This looks like a modifier
        if '-->' in line or any(c in line for c in ['+', '%', '#']):
            mods.append(_normalize_mod(line))
    
    return mods


def _build_trade_query(base_type: str, category: str, modifiers: list[str]) -> dict:
    """Build the trade search query structure."""
    query = {
        "query": {
            "status": {"option": "online"},
            "type": base_type,
        },
        "sort": {"price": "asc"},
    }
    
    # Add filters based on category
    if category == "weapon":
        query["query"]["filters"] = {
            "weapon_filters": {"disabled": True},
            "armour_filters": {"disabled": True},
            "socket_filters": {"disabled": True},
        }
    elif category == "armour":
        query["query"]["filters"] = {
            "weapon_filters": {"disabled": True},
            "armour_filters": {"disabled": True},
        }
    
    return query


def _dict_to_query_string(d: dict, prefix: str = "") -> str:
    """Convert nested dict to query string format for PoE trade."""
    parts = []
    for key, value in d.items():
        if isinstance(value, dict):
            parts.append(_dict_to_query_string(value, f"{prefix}{key}."))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    parts.append(_dict_to_query_string(item, f"{prefix}{key}.{i}."))
                else:
                    parts.append(f"{prefix}{key}.{i}={quote(str(item))}")
        else:
            parts.append(f"{prefix}{key}={quote(str(value))}")
    return "&".join(parts)


def generate_trade_link(item_text: str, league: str = "Mirage") -> str:
    """Generate a PoE trade link from item description text.
    
    Args:
        item_text: The full item description text (as copied from game)
        league: The league to search in (default: Mirage)
    
    Returns:
        A formatted result with trade URL and Better Trading import string
    """
    if not item_text or not item_text.strip():
        return "Error: No item text provided. Please paste the item description."
    
    # Extract base type
    base_type = _extract_base_type(item_text)
    if not base_type:
        return "Error: Could not determine item base type from text."
    
    # Extract modifiers
    modifiers = _extract_modifiers(item_text)
    
    # Determine category
    category = _guess_category(base_type)
    
    # Build trade URL
    # PoE trade uses a hash-based URL system
    # We'll create a simple search by type
    
    # For now, generate a basic search URL
    # The full query system is complex - this is a simplified version
    query_hash = "dummy"  # PoE trade requires a server-side hash
    
    # Build the URL with basic parameters
    # Note: Full PoE trade search requires POST to their API
    # This generates a basic search that user can refine
    
    encoded_type = quote(base_type)
    trade_url = f"{TRADE_BASE_URL}/search/{league}/{encoded_type}"
    
    # Build Better Trading import string
    trade_location = {
        "version": "poe1",
        "type": category,
        "slug": encoded_type,  # The search query slug
    }
    
    import_data = {
        "icn": "chaos",  # Default icon
        "tit": f"Search: {base_type[:30]}",
        "ver": "poe1",
        "trs": [
            {
                "tit": f"Search: {base_type[:50]}",
                "loc": f"poe1:{category}:{encoded_type}",
            }
        ],
    }
    
    # Encode as base64 with version prefix
    json_str = json.dumps(import_data)
    b64 = base64.b64encode(json_str.encode()).decode()
    bt_import = f"3:{b64}"
    
    # Format output
    result = []
    result.append(f"## Item Detected")
    result.append(f"- **Base Type:** {base_type}")
    result.append(f"- **Category:** {category}")
    result.append(f"- **Modifiers found:** {len(modifiers)}")
    result.append("")
    result.append(f"## Trade Search")
    result.append(f"**URL:** {trade_url}")
    result.append("")
    result.append(f"## Better Trading Import")
    result.append(f"Copy the string below and import via Better Trading:")
    result.append(f"```")
    result.append(bt_import)
    result.append(f"```")
    result.append("")
    result.append(f"**Note:** This is a basic search by item type. For precise modifier")
    result.append(f"filtering, use the trade site directly.")
    
    return "\n".join(result)


def get_bt_import_string(base_type: str, category: str, title: str | None = None) -> str:
    """Generate a Better Trading import string for a specific item search.
    
    Args:
        base_type: The item base type to search for
        category: The trade category (weapon, armour, jewelry, etc.)
        title: Optional custom title for the bookmark
    
    Returns:
        The Better Trading import string
    """
    if title is None:
        title = f"Search: {base_type}"
    
    encoded_type = quote(base_type)
    
    import_data = {
        "icn": "chaos",
        "tit": title[:50],
        "ver": "poe1",
        "trs": [
            {
                "tit": title[:100],
                "loc": f"poe1:{category}:{encoded_type}",
            }
        ],
    }
    
    json_str = json.dumps(import_data)
    b64 = base64.b64encode(json_str.encode()).decode()
    return f"3:{b64}"
