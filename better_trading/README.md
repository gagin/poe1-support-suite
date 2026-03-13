# Better Trading Import Tool

MCP tool for generating PoE trade links and Better Trading browser extension import strings from item descriptions.

## Installation

The MCP server is configured in `.mcp.json`. Make sure Claude Code is restarted to pick up the new MCP server.

## Usage

### Tool 1: `generate_trade_link`

Paste item text (copied from in-game with Ctrl+C) to generate:
- A trade search URL
- A Better Trading import string

```
generate_trade_link(item_text, league="Mirage")
```

Example input (paste this):
```
"Soul Mantle"
Saint's Hauberk
--------
Armour: 688 (augmented)
--------
Requirements:
Level 65, 107 Str, 67 Dex
--------
Sockets: R-R-R-R-R-R 
--------
Item Level: 86
--------
Socketed Support Gems are Triggered by Supported Skills
Socketed Support Gems Gain a 8% Mana Multiplier
Socketed Support Gems have 20% increased Support Effect
+19 to maximum Mana
Socketed Triggered Skills have -15 to Total Mana Cost
Triggered Attacks cannot be Evaded
-------- 
Corrupted
```

Output:
- Trade URL: `https://www.pathofexile.com/trade/search/Mirage/Soul%20Mantle`
- BT Import string (copy and import in Better Trading)

### Tool 2: `get_bt_import`

Generate a Better Trading import string directly without the trade URL.

```
get_bt_import(base_type, category, title=None)
```

Categories: `weapon`, `armour`, `jewelry`, `jewel`, `flask`, `map`, `accessory`, `skillgem`, `fragment`

Example:
```
get_bt_import("Headhunter", "jewelry", "HH search")
```

## Better Trading Import

To import the generated string into Better Trading:

1. Copy the import string (the base64 encoded part)
2. Open Better Trading in Chrome
3. Look for an import option (usually in bookmarks section)
4. Paste the string

The import creates a bookmark folder with a trade search link.
