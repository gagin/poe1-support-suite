import base64
import json
import pytest
from better_trading.importer import (
    _extract_base_type,
    _guess_category,
    _extract_modifiers,
    get_bt_import_string,
    generate_trade_link,
)


def decode_bt_import(encoded: str) -> dict:
    """Decode a Better Trading import string."""
    if encoded.startswith("3:"):
        encoded = encoded[2:]
    return json.loads(base64.b64decode(encoded))


class TestExtractBaseType:
    def test_unique_item(self):
        text = '''"Soul Mantle"
Saint's Hauberk
--------
Armour: 688'''
        assert _extract_base_type(text) == "Soul Mantle"

    def test_rare_item(self):
        text = '''Rare Ring
--------
+10 to maximum Life
+10% to Cold Resistance'''
        assert _extract_base_type(text) == "Ring"

    def test_magic_item(self):
        text = '''Magic Boots
--------
+20% to Fire Resistance'''
        assert _extract_base_type(text) == "Boots"

    def test_base_type_only(self):
        text = '''Thief's Torment
--------
Ring
--------
+12 to maximum Life'''
        result = _extract_base_type(text)
        assert result in ["Thief's Torment", "Ring"]


class TestGuessCategory:
    def test_armour_types(self):
        assert _guess_category("Soul Mantle") == "armour"
        assert _guess_category("Gloves") == "armour"
        assert _guess_category("Boots") == "armour"
        assert _guess_category("Helmet") == "armour"
        assert _guess_category("Shield") == "armour"

    def test_jewelry_types(self):
        assert _guess_category("Ring") == "jewelry"
        assert _guess_category("Amulet") == "jewelry"
        assert _guess_category("Belt") == "jewelry"

    def test_weapon_types(self):
        assert _guess_category("Sword") == "weapon"
        assert _guess_category("Bow") == "weapon"
        assert _guess_category("Dagger") == "weapon"
        assert _guess_category("Staff") == "weapon"
        assert _guess_category("Claw") == "weapon"

    def test_other_categories(self):
        assert _guess_category("Flask") == "flask"
        assert _guess_category("Jewel") == "jewel"
        assert _guess_category("Map") == "map"
        assert _guess_category("Quiver") == "accessory"


class TestExtractModifiers:
    def test_extracts_mods(self):
        text = '''Rare Ring
--------
+10 to maximum Life
+10% to Cold Resistance
--------
Corrupted'''
        mods = _extract_modifiers(text)
        assert len(mods) >= 2

    def test_skips_headers(self):
        text = '''Rare Ring
--------
Requirements:
Level 1
--------
+10 to maximum Life
--------
Sockets: R-R'''
        mods = _extract_modifiers(text)
        assert "Requirements:" not in mods
        assert "+10 to maximum Life" in mods


class TestGetBTImport:
    def test_basic_import(self):
        result = get_bt_import_string("Headhunter", "jewelry")
        assert result.startswith("3:")
        decoded = decode_bt_import(result)
        assert decoded["trs"][0]["loc"] == "poe1:jewelry:Headhunter"

    def test_with_custom_title(self):
        result = get_bt_import_string("Headhunter", "jewelry", "HH search")
        decoded = decode_bt_import(result)
        assert decoded["tit"] == "HH search"

    def test_armour_category(self):
        result = get_bt_import_string("Soul Mantle", "armour")
        decoded = decode_bt_import(result)
        assert "armour" in decoded["trs"][0]["loc"]


class TestGenerateTradeLink:
    def test_generates_url(self):
        text = '"Soul Mantle"\nSaint\'s Hauberk\n--------\nArmour: 688'
        result = generate_trade_link(text)
        assert "pathofexile.com/trade/search" in result

    def test_generates_bt_import(self):
        text = '"Soul Mantle"\nSaint\'s Hauberk\n--------\nArmour: 688'
        result = generate_trade_link(text)
        assert "3:" in result
        assert "Better Trading Import" in result

    def test_error_on_empty(self):
        result = generate_trade_link("")
        assert "Error" in result

    def test_custom_league(self):
        text = '"Soul Mantle"\nSaint\'s Hauberk'
        result = generate_trade_link(text, league="Standard")
        assert "Standard" in result
