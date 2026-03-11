# PoE 1 Support Suite

Claude Code tools and knowledge base for Path of Exile 1 build analysis, character import, and timeless jewel calculation. Designed for use with Claude Code (CLI) on PlayStation/Sony realm, but the scripts work on any realm.

## What's included

- **`build_expander.py`** — imports a character JSON and enriches it with full passive tree details, item mods, gem info, and prices
- **`timeless_jewel_analysis.py`** — calculates exact Lethal Pride (and other timeless jewel) effects at a specific passive tree socket position for a given seed
- **`pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua`** — modified PoB import script (adds YYYYMMDDHHMM timestamp to output filenames)
- **`pob/unpack_pob.py`** — decodes a Path of Building export string to XML
- **`pob/pob_config_is_in_inline_var.py`** — PoB config utility
- **`CLAUDE.md`** — Claude Code project instructions (workflow, mechanics knowledge, build analysis rules)
- **`skill.md`** — PoE mechanics reference and build audit procedure
- **`economy.md`** — Lab gem economy guide (Facetor's Lens, transfigured gem conversion)
- **`builds/`** — build-specific knowledge files (Chieftain, Shield Crush + Impale, Melee + Warcry)

---

## External Dependencies

### 1. POEMCP — Game Data MCP Server

Provides gem, item, passive, price, and wiki lookup tools via MCP.

```bash
git clone https://github.com/shalayiding/POEMCP.git POEMCP
cd POEMCP
pip install -e .
```

Place the cloned directory at `POEMCP/` relative to this repo root.

### 2. PathOfBuilding — Character Import Backend

Required for `import_character_cli.lua` (Lua runtime) and `mcp_server.py`.

Download release **2.59.2** from:
https://github.com/PathOfBuildingCommunity/PathOfBuilding/releases/tag/v2.59.2

Extract so the directory structure is:
```
pob/PathOfBuilding-2.59.2/
```

Then copy our modified import script over the default one:
```bash
cp pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua
# (already in place if you cloned this repo first — the file is tracked here)
```

Requires Lua (bundled with PathOfBuilding's runtime on Windows; on macOS/Linux install via `brew install lua` or system package manager).

### 3. timeless-jewels — Timeless Jewel Calculator

Required for `timeless_jewel_analysis.py`.

```bash
git clone https://github.com/Vilsol/timeless-jewels.git pob/timeless-jewels
cd pob/timeless-jewels
go build -o cli/timeless-jewel-cli ./cli/...
```

Requires Go (`brew install go` or https://go.dev/dl/).

The data files (`pob/timeless-jewels/data/SkillTree.json.gz`, `passive_skills.json.gz`, etc.) are included in the cloned repo.

---

## Setup

### MCP Configuration

Copy `.mcp.json.example` to `.mcp.json` and update the paths:

```bash
cp .mcp.json.example .mcp.json
# Edit .mcp.json — replace /path/to/poe1-support-suite with your actual repo path
```

### Claude Code

The `CLAUDE.md` file is automatically loaded by Claude Code. It contains:
- Standard import/expand workflow
- Build analysis rules
- PoE mechanics reference

---

## Workflow

### 1. Import character

```bash
cd pob/PathOfBuilding-2.59.2/tools
lua import_character_cli.lua SONY <AccountName>#<ID> <CharacterName>
# Output: pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json
```

### 2. Expand with full details

```bash
# From repo root
python build_expander.py pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json --league <League> --realm sony
# Output: <CharacterName>_YYYYMMDDHHMM_expanded.json
```

### 3. Analyze timeless jewel

```bash
python timeless_jewel_analysis.py <character_json> <jewel_slot_index> <GeneralName> <seed>
# Example:
python timeless_jewel_analysis.py pob/PathOfBuilding-2.59.2/tools/MiragMaraBatato_202603111443.json 0 Kaom 12566
```

`jewel_slot_index` is the `x` value from the jewel item in `passive_tree.items`. General names: `Kaom`, `Rakiata`, `Akoya`, `Dominus`, `Maxarius`, `Avarius`, `Xibaqua`, `Doryani`, `Ahuana`, `Balbala`, `Nasima`, `Asenath`, `Caspiro`, `Cadiro`, `Victario`.

---

## Example Build Files

The `builds/` directory contains knowledge files for specific build archetypes:

- **`builds/chieftain.md`** — Chieftain ascendancy mechanics (Tasalio/Valako fire res stacking, Ngamahu Str bonus, Sione warcries, Lethal Pride interactions)
- **`builds/shield_crush_impale.md`** — Shield Crush scaling, Precise Technique, Impale setup, Dawnbreaker/Prismatic Eclipse interactions
- **`builds/melee_warcry.md`** — Multistrike + warcry exert interactions, warcry types

**`skill.md`** covers general mechanics used across builds:
- Damage scaling (increased vs more vs flat)
- Resistance overcapping for altars
- Ailment handling layers
- Eater/Exarch implicits
- Timeless jewel build audit procedure (3 layers: general, Lethal Pride, Ngamahu)
- Leveling to 95 priorities

---

## Notes

- Default account in CLAUDE.md: `Ladimir_Lepin#9831` (Sony/PlayStation realm)
- Current league: Mirage
- No public price data exists for PlayStation — do not use price_check tools for PS builds
