from mcp.server.fastmcp import FastMCP

from better_trading.importer import generate_trade_link as _generate_trade_link, get_bt_import_string as _get_bt_import_string

mcp = FastMCP("BetterTradingMCP")

@mcp.tool()
def generate_trade_link(item_text: str, league: str = "Mirage") -> str:
    """Generate a PoE trade link and Better Trading import string from item description.
    
    Paste the full item text (as copied from in-game) to generate:
    - A trade search URL
    - A Better Trading import string that can be imported into the browser extension
    
    Args:
        item_text: The full item description text (copy from in-game with Ctrl+C)
        league: The league to search in (default: Mirage)
    """
    return _generate_trade_link(item_text, league)


@mcp.tool()
def get_bt_import(base_type: str, category: str, title: str | None = None) -> str:
    """Generate a Better Trading import string for a specific item search.
    
    Creates a direct import string without generating a trade URL.
    Use this when you already know the base type and category.
    
    Args:
        base_type: The item base type (e.g., "Saint's Hauberk", "Titanium Spirit Shield")
        category: Trade category - one of: weapon, armour, jewelry, jewel, flask, map, accessory, skillgem, fragment
        title: Optional custom title for the bookmark
    
    Returns:
        The Better Trading import string (base64 encoded)
    """
    return _get_bt_import_string(base_type, category, title)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
