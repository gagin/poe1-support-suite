# Path of Exile 2 — Harness Reference

PoE2 character import + expansion harness, mirroring the PoE1 two-step flow but
adapted for PoE2's realities on macOS.

**Note:** Always use `uv run python` to run Python scripts in this project.

---

## Why PoE2 differs from PoE1

The PoE1 harness downloads characters from the legacy cookie endpoint
(`character-window/get-characters?realm=sony`). **That endpoint only serves PoE1.**
Verified: `realm=sony` returns the PoE1 characters, and every PoE2 realm variant
(`poe2`, `poe2-sony`, …) returns an empty list even on a public account.

GGG exposes PoE2 characters **only** through the new OAuth API
(`api.pathofexile.com/character/poe2/...`), which is what PathOfBuilding-PoE2 uses
(`src/Classes/PoEAPI.lua` + `src/LaunchServer.lua`). PoB-PoE2 doesn't run natively
on macOS, so `poe2_import.py` ports that OAuth flow to run standalone here:

| PoB-PoE2 (Windows) | `poe2_import.py` (macOS) |
|---|---|
| `OpenURL(...)` | `webbrowser.open` (→ `open`) |
| lua `socket` subscript (`LaunchServer.lua`) | Python `http.server` on localhost |
| endpoints, client_id=pob, scopes, PKCE S256, ports 49082-49084, refresh | ported verbatim |

**OAuth ≠ cookie.** You log in through the browser **once**; a refresh token is
saved to `PathOfBuilding-PoE2/tools/.poe2_token.json` (chmod 600, gitignored) and
future runs refresh silently.

---

## Standard Workflow — Importing a PoE2 Character

### Step 1: Download (OAuth)
```bash
uv run python poe2_import.py                 # first run: opens browser, then lists your PoE2 characters
uv run python poe2_import.py <CharacterName>  # download one character
```
First run opens pathofexile.com to log in (once). Output:
- `PathOfBuilding-PoE2/tools/<CharacterName>_YYYYMMDDHHMM.json` (normalized)
- `..._raw.json` alongside it (raw OAuth response, for debugging)

`uv run python poe2_import.py --logout` forgets the saved token.

### Step 2: Expand (python, offline)
```bash
uv run python build_expander_poe2.py PathOfBuilding-PoE2/tools/<CharacterName>_*.json
```
Reads the passive tree from `PathOfBuilding-PoE2/src/TreeData/<latest>/tree.json`
(no POEMCP, no network). Output: `<CharacterName>_YYYYMMDDHHMM_expanded.json`.
Options: `--tree-version 0_5`, `-o <path>`.

### Step 2b (optional): Compact markdown (agent/manual reading)
```bash
uv run python build_expander_md_poe2.py PathOfBuilding-PoE2/tools/<CharacterName>_*.json
```
The expanded JSON is verbose. This collapses each item / node / skill group onto
a single line under headings, and strips GGG's `[Tag|Text]` bracket noise, so an
agent or a human can skim the build cheaply. Output: `<CharacterName>_YYYYMMDDHHMM_expanded.md`.
Options: `--tree-version 0_5`, `-o <path>`.

### Or via Makefile (from repo root)
```bash
make listchars2                       # list characters
make snapshot2 CHARACTER=<name>       # download + expand (JSON + MD) -> build_snapshots_poe2/
make expand2 CHARACTER=<name>         # expand latest download to JSON
make expandmd2 CHARACTER=<name>       # render latest download to compact markdown
make logout2                          # forget token
```

---

## Files

| File | Role |
|---|---|
| `poe2_import.py` | OAuth downloader (Mac port of PoB-PoE2's PoEAPI + LaunchServer) |
| `build_expander_poe2.py` | Offline expander (reads PoB-PoE2 `tree.json`) |
| `build_expander_md_poe2.py` | Compact markdown renderer (single-line items/nodes/skills; strips bracket tags) |
| `PathOfBuilding-PoE2/tools/.poe2_token.json` | Saved OAuth refresh token (gitignored, chmod 600) |

---

## Expanded output shape

```
character         # name/class/ascendancy/level/league
passive_tree      # keystones, notables, ascendancy, masteries, small_passives,
                  #   cluster_notables, unresolved (hashes not in this tree version)
items             # equipment, jewels (via inventoryId PassiveJewels*), flasks, charms
skills            # active_skills, support_gems, all_gems (name/level/quality/socket)
metadata          # game=poe2, tree_version, source_file, generated
```

If `passive_tree.unresolved` is non-empty, the character's tree version differs
from the one bundled in PoB-PoE2 — pass `--tree-version` or update PoB-PoE2.

---

## Reading item data (two gotchas)

Two easy ways to misread the expanded item JSON:

1. **Hybrid mods are flattened into separate stat lines.** The GGG OAuth response
   and `build_expander_poe2.py` report each stat of a **hybrid** mod as its own
   entry in `explicitMods`, so one mod shows up as multiple lines. Example: a
   single desecrated hybrid like "42% increased Energy Shield **and** +42 to
   maximum Life" appears as two separate `explicitMods` entries. Do not assume two
   lines are two independent mods — when it matters, count mods by their shared
   source (e.g. a crafted / desecrated flag) rather than by line count.

2. **The item's base `Energy Shield` / `Armour` / `Evasion` value already includes
   that item's own mods.** The number in `properties` is the result *after* the
   piece's local flat + local-% mods, and **quality is a separate multiplier**:
   `displayed = base × (1 + quality%) × (1 + local increased%)` (e.g. a Kamasan
   Tiara: 103 base × 1.20 quality × 1.29 inc ES ≈ 159 — the "97" would be a
   runeforged value, not the true base). Item mods are **local**: "X% increased
   ES" on a piece affects only that piece. So to recover a piece's true base,
   reverse out its own local mods and quality first. A claimed sheet delta ("this
   piece added +300 ES") is the **total after all global sources of increased ES**
   (tree, jewels, etc.) outside that item — not the local change.

---

## Known gaps / TODO

- **Console vs PC realm**: the OAuth path uses realm `poe2`; the authenticated
  account decides which characters come back. Your PlayStation characters should
  appear once you log in with the linked GGG account (Ladimir_Lepin#9831). If the
  list is empty, the account may have no PoE2 characters yet.
- **OAuth response shape is normalized defensively** (`poe2_import.normalize`).
  The raw response is always saved as `*_raw.json`; if a field is missing from the
  expanded build, check the raw file and adjust the mapping.
- **Gem / item DB enrichment** not wired in (`src/Data/Gems.lua` available locally
  if wanted). Mods and gem names pass through verbatim.
