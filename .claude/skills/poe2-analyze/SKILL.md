---
name: poe2-analyze
description: Pull a Path of Exile 2 character from the account, expand it, analyze the build, and record findings to the notes vault. Use when asked to import/analyze/review a PoE2 character (e.g. "analyze my PoE2 character X", "pull toteBotato", "review my Warrior").
---

# PoE2: pull → expand → analyze → record

End-to-end workflow for a Path of Exile 2 character. All commands run from the
repo root `/Users/a/code/games/poe`. Always use `uv run python`.

## 1. Pull the character (OAuth)

```bash
uv run python poe2_import.py "<CharacterName>"
```
- Downloads via GGG's OAuth API into `PathOfBuilding-PoE2/tools/<Name>_<ts>.json`
  (normalized) plus `<Name>_<ts>_raw.json` (raw response).
- **Auth is automatic.** A refresh token is cached in
  `PathOfBuilding-PoE2/tools/.poe2_token.json`; normal runs need no browser. Only
  if the refresh token itself has expired does the script call `webbrowser.open`
  to open the user's browser for a one-time login (localhost callback on ports
  49082-49084, 30s window). Running this via Bash executes on the user's Mac, so
  the browser opens for them — tell them to log in when it does.
- To discover names first: `uv run python poe2_import.py` (no arg) lists the
  account's PoE2 characters. `--logout` forgets the token.

## 2. Expand (offline)

```bash
uv run python build_expander_poe2.py PathOfBuilding-PoE2/tools/<Name>_<ts>.json \
  -o build_snapshots_poe2/<Name>_<ts>_expanded.json
```
Reads the passive tree from `PathOfBuilding-PoE2/src/TreeData/<latest>/tree.json`.
If the summary reports non-zero `unresolved` passives, pass `--tree-version` to
match the character's league (update PathOfBuilding-PoE2 if needed).

Or run steps 1+2 together: `make snapshot2 CHARACTER=<Name>`.

## 3. Analyze

Read the expanded JSON and analyze from what the data actually shows:
- **Class / ascendancy** (ascendancy is derived from allocated nodes), **level, league**.
- **Skill links** (`skills.groups`): main skill + supports per group — identify the
  main damage skill vs utility/aura/movement.
- **Passives**: keystone(s), notable themes, `skill_overrides` (attribute nodes).
- **Defence**: life/ES/armour/evasion from gear mods, resistances, block; note gaps.
- **Items**: uniques, jewels, runes (PoE2 item sockets hold runes/soul-cores, not
  gems), charms.

**Critical constraint:** there is no game-data MCP in this project for PoE2 (no
poemcp, no wiki lookup). Do **not** assert PoE2 mechanics, gem numbers, or
interactions from memory — PoE2 (0.x) changes fast and training data is stale.
Ground every claim in the character's own data; explicitly flag anything about
mechanics as unverified. See [[conventions]] and [[status]].

## 4. Record to the notes vault

Persist the analysis so it outlives the session (this is the "notes mcp" step):
- Write a build note `projects/poe/build-<name>.md` (`type: note`) with sections:
  Overview · Skills · Passives & Ascendancy · Defence · Items · Findings / TODO.
  Use the vault tools (`write_note`/`edit_section`), never a filesystem edit.
- Update `projects/poe/status.md` to point at the latest snapshot + note.
- `recall` first to update an existing build note rather than duplicating.

Keep the chat reply to the gist; put the depth in the note and cite its title/path.
```
