# Path of Exile 1 — Project Reference

All PoE1-specific instructions, workflow, and knowledge index for this project.

**Note:** Always use `uv run python` to run Python scripts in this project.

---

## MCP Servers (pre-configured in .mcp.json)

- **poemcp** — Game data: gems, items, passives, wiki, mods. Reliably usable.
- **pob-importer** — DISABLED / unreliable: returns HTTP 403. Do not use for imports.
- **better-trading** — Trade link generator: parses item text to create PoE trade URLs and Better Trading browser extension import strings.

---

## Standard Workflow — Importing Characters

**Always use the two-step lua + python process.**

### Step 1: Import character via lua script
```bash
cd pob/PathOfBuilding-2.59.2/tools
lua import_character_cli.lua SONY Ladimir_Lepin#9831 <CharacterName>
```
Output: `pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json`

### Step 2: Expand the JSON (run from repo root)
```bash
uv run python build_expander.py pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json --league <League> --realm sony
```
Output: `<CharacterName>_YYYYMMDDHHMM_expanded.json`

Or use the Makefile (downloads + expands automatically):
```bash
make snapshot CHARACTER=<CharacterName> LEAGUE=<League> REALM=sony
```
Output: `build_snapshots/<CharacterName>_YYYYMMDDHHMM_expanded.json`

---

## Information Validity — Always Verify

**PoE changes mechanics every league (~3 months). Assume any recalled knowledge may be outdated.**

- Before stating a mechanic as fact, verify via MCP tools (`search_passive`, `get_gem_detail`, `fetch_wiki_page`) or note explicitly that it is unverified.
- **MCP data can also be stale.** poemcp databases are not guaranteed to reflect the current patch. Cross-check important facts with `fetch_wiki_page` and flag with a verification date.
- When a fact is verified in a session, note it as `[verified YYYY-MM]`. Undated entries should be reverified before being cited confidently.

---

## Knowledge Files

| File | Contents |
|---|---|
| `mechanics.md` | Core PoE mechanics: damage formula, defense layers, item affixes, cluster jewels, local/global, weapon swaps, skill links |
| `skill.md` | Build analysis rules, damage scaling principles, Shield Crush specifics, ailment handling, resistance overcapping, build audit procedure |
| `knowledge/economy.md` | Lab economy, gem conversion, league stage priorities, PS pricing rules, upgrade advice |
| `knowledge/base_valuation_filterblade.md` | Base valuation and Filterblade economy adjustments |
| `mirage_challenges.md` | Mirage league challenges, Mirage-specific mechanics (memory altars, borrowed power coins) |
| `classes/chieftain.md` | All 7 Chieftain ascendancy notables, prerequisite tree, version history, build notes |
| `better_trading/README.md` | Trade link generator usage for Better Trading browser extension |

---

## Project Files

- MCP config: `.mcp.json`
- POEMCP server: `POEMCP/server.py`
- POB importer CLI: `pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua`
- Build expander: `build_expander.py`
- Expanded builds: `build_snapshots/<CharName>_YYYYMMDDHHMM_expanded.json`
- Better Trading importer: `better_trading/`
