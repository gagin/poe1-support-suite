# Path of Exile 1 — Project Reference

All PoE1-specific instructions, workflow, and knowledge index for this project.

**Note:** Always use `uv run python` to run Python scripts in this project.

---

## MCP Servers (pre-configured in .mcp.json)

- **poemcp** — Game data: gems, items, passives, wiki, mods. Reliably usable.
- **pob-importer** — DISABLED / unreliable: returns HTTP 403. Do not use for imports.
- **better-trading** — Legacy prototype only; it is not the screenshot-price-check
  implementation and should remain untouched.

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
uv run python build_expander.py pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json --league <League> --realm sony --include-swap
```
Output: `<CharacterName>_YYYYMMDDHHMM_expanded.json`

Or use the Makefile (downloads + expands automatically):
```bash
make snapshot CHARACTER=<CharacterName> LEAGUE=<League> REALM=SONY
```
Output: `build_snapshots/<CharacterName>_YYYYMMDDHHMM_expanded.json`

Realm input to the Lua importer is case-insensitive; `SONY` is the canonical
form used in documentation and Makefile examples.

Weapon-swap inclusion is required for character reviews. `build_expander.py`
omits `Weapon2` and `Offhand2` unless `--include-swap` is passed; the Makefile
passes it by default so separate clear/boss weapon sets are both captured.

### Path of Building repository boundaries

There are two deliberately separate PoB locations:

- `pob/PathOfBuilding-2.59.2/` is the ignored release installation used only as
  the Lua character-import runtime. The root repository tracks our customized
  `tools/import_character_cli.lua` inside it. It is not a PoB Git checkout; do
  not try to update it with `git pull` or overwrite it from another checkout.
- `pob-port/PathOfBuildingCommunityMac/` is a nested PoB Git checkout used as
  the current reference for PoB mechanics, data, and passive trees. Before
  relying on its source or data, update it from the official upstream with
  `git pull --ff-only upstream dev`. Its Git history is independent of the root
  support-suite repository; the root stores only its pinned submodule commit.
  After an intentional update, the root will show that pointer as modified
  until it is committed there.

Updating the reference checkout must not copy files over the import runtime or
touch `build_expander.py`, the root `Makefile`, or the customized importer. The
reference checkout also contains an untracked Mac-port `Makefile`; preserve it
when updating.

### Required post-import checks

Do not infer jewel-socket occupancy from the jewel list alone. For every
character review:

1. Count allocated passive-tree nodes marked as jewel sockets.
2. Count jewels in `passive_tree.items`.
3. Report any difference as an allocated but empty jewel socket.

The official character download contains both sets of information, but the raw
API does not present an explicit human-readable "empty socket" warning.

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
| `better_trading/README.md` | Legacy Better Trading import prototype (separate; do not extend for screenshot price checking) |
| `poe_screenshot_trade/README.md` | Sony screenshot properties → official authenticated trade-board search |

---

## Project Files

- MCP config: `.mcp.json`
- POEMCP server: `POEMCP/server.py`
- POB importer CLI: `pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua`
- Current POB source/data reference: `pob-port/PathOfBuildingCommunityMac/`
- Build expander: `build_expander.py`
- Expanded builds: `build_snapshots/<CharName>_YYYYMMDDHHMM_expanded.json`
- Legacy Better Trading importer: `better_trading/` (unrelated to screenshot price checking)
- Sony screenshot trade generator: `poe_screenshot_trade/`
