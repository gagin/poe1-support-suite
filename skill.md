# PoE Build Advisor — Mechanics & Tools

## Damage Scaling Principles

### Increased Damage — Additive, Diminishing Returns
All "increased damage", "increased physical damage", "increased fire damage", etc. pool together additively:
```
total_multiplier = 1 + sum(all_increased%)
```
If you already have 400% increased damage total, adding 20% more increased is only a 20/500 = 4% actual damage gain. **Heavily diminishing.** When a build is already stacked with increased, prioritize other scaling vectors.

### Attack Speed — Additive with Each Other, Multiplicative with Damage
"Increased attack speed" mods pool additively with each other — just like increased damage. If you already have 70% increased attack speed, adding 8% more is only 8/170 ≈ 4.7% more hits. **This has the same diminishing returns problem as increased damage when the pool is already large.**

What makes attack speed valuable is that hits-per-second multiplies with your full damage-per-hit stack — so attack speed is multiplicative *with damage*, but individual attack speed sources are still additive *with each other*. Evaluate new attack speed sources the same way as increased damage: check the current pool size first.

### More Multipliers — Always Multiplicative
Support gems and some ascendancy nodes grant "more" damage — each is its own multiplier:
```
DPS = BaseDamage × (1 + Σincreased%) × more_1 × more_2 × more_3 × APS
```
A new "more" source is almost always the strongest damage upgrade. Adding a 40% more support when you have two 40% more supports already is: 1.4 × 1.4 × 1.4 = 2.74× base, vs 1.4 × 1.4 = 1.96× — still a genuine 40% more.

### Priority Order for Damage Upgrades
1. New "more" multipliers (supports, ascendancy, uniques granting more)
2. Attack/cast speed (multiplicative with damage per hit)
3. Flat damage added to attacks (if effectiveness of added damage is high)
4. Increased damage (only valuable if current total is low, e.g. <200%)

---

## Build Analysis Rules
- **Always verify passive names/stats with `search_passive` MCP** before stating what they do. Never guess.
- Mid-league jewels commonly have dead mods — do not flag this as an issue.
- Early/mid-league underleveled gems are expected. Only flag gem levels if clearly wrong (e.g. a critical support sitting at level 1 when it should be leveled).
- Ignore weapon swap slots entirely. Only analyze the active weapon set.
- **Lab enchants do not exist in current PoE.** Do not suggest or reference helmet/boot/glove enchants from the Divine Font. This is a legacy mechanic from older versions.

## Resistance Overcapping — Blue Altars and Map Mods

Resistances above the cap (75%) are called overcap. They don't increase your effective resistance normally, but they protect against mods that temporarily lower your resistances:

- **Blue altars (Eater of Worlds)** can have mods that reduce your resistances by 20–30% for the encounter
- **Map mods** ("players have -X% to all resistances") work the same way
- Without overcap, these mods drop you below 75% and you take significantly more elemental damage

**How much overcap to target:** Enough to stay at 75% cap after the worst altar/map mod combination you intend to run. 30%+ overcap on all elements is a common endgame target for atlas farming. Chaos resistance should also be overcapped — chaos altar mods exist.

**Practical note:** Fire/cold/lightning res on gear often comes in pairs or triples. Getting one element overcapped usually means others follow. Chaos res is harder and competes for suffix slots.

---

## Ailment Handling — Layers and Interactions

### Ailment Categories
- **Damaging ailments:** Ignite, Bleed, Poison, Corrupted Blood — deal damage over time
- **Non-damaging ailments:** Chill, Freeze, Shock, Scorch, Brittle, Sap — debuffs without direct DoT

### Defense Layers
- **Specific immunities** (most reliable): Ignite immunity from Tasalio (Chieftain ascendancy) or flasks; Corrupted Blood immunity from jewel implicit (e.g. "Corrupted Blood cannot be inflicted on you")
- **Protection Mastery** ("damaging ailments cannot be inflicted on you while you have one; same for non-damaging"): prevents ailment stacking/compounding. If bleeding, cannot be poisoned. If chilled, cannot be shocked or frozen. Poisons cannot stack. Strong layer that doesn't require immunities.
- **Extinguish (Searing Exarch glove implicit):** Debuff applied to enemies on hit — prevents the afflicted enemy from applying elemental ailments for 4 seconds. At high hit rates (Multistrike etc.), stays up permanently on the target. Covers all elemental ailments: chill, freeze, shock, scorch, brittle, sap, ignite. Does NOT cover non-elemental ailments (bleed, poison).
- **Pantheon:** Brine King (chill/freeze reduction), Abberath (ignite immunity while moving), others — situational coverage
- **Flasks:** Ruby/Sapphire/Topaz with ailment immunity suffix cover gaps for mapping

### Easiest Solution: Purity of Elements
**Purity of Elements** grants immunity to all elemental ailments (chill, freeze, shock, scorch, brittle, sap, ignite) in one aura. If a build can fit it in the reservation budget, it replaces all the above layers for elemental ailments completely. The cost is an aura slot (35% mana reservation) — builds that can afford it don't need to think about elemental ailment coverage at all.

When a build **cannot** fit Purity of Elements, achieving the same coverage becomes expensive: passive tree nodes, Exarch glove implicits (Extinguish), jewels like Grand Spectrum (ailment immunity), and flask suffixes all become opportunity costs competing for slots. The Extinguish + mastery approach above is one such alternative — effective but assembled from multiple pieces.

### Interaction Note
Extinguish + Protection Mastery together give comprehensive coverage: Extinguish blocks all elemental ailments from the target you're hitting; mastery prevents non-elemental ailments from stacking. The remaining gap is a single bleed or poison landing — mitigated by life/leech for most melee builds.

---

## Item Implicits — Eater/Exarch Currency

Non-unique, non-influenced, non-corrupted body armour, helmets, gloves, and boots can have **implicits added and rerolled** using Eldritch currency (Orbs of Conflict, Ichors, Embers from The Eater of Worlds / The Searing Exarch). Each item slot has its own implicit pool split between Eater and Exarch. Rerolling costs currency and randomises within the pool — check the pool for a slot before committing to rolls.

## Catalysts — Rings, Amulets, Belts

Catalysts add quality to rings, amulets, and belts, increasing the numeric value of specific mod categories on the item. Different catalyst types boost different mod types (e.g. Abrasive Catalyst boosts attack mods, Fertile Catalyst boosts life/mana mods). Quality caps at 20%. Apply before crafting to get higher mod values.

## Shield Crush — Wave Overlap and Positioning

Shield Crush fires 3 waves in a segmented cone: left, center, right. The center wave is the longest. Enemies can be hit by **up to 2 waves** where adjacent waves overlap — counting as 2 separate hits for impale, life-on-hit, and similar effects.

**Overlap zones:** The seams are between center+left and center+right, not at the dead center of the cone.

**Optimal positioning:** Stand adjacent to (touching) the boss. At point-blank melee range, the cone's seam zones land on or very near the target naturally. Alternatively, angle your attack so the boss is slightly off-center — at the boundary between center and a side wave. Both approaches work; touching the boss is the simpler and more consistent method.

**On controller:** Achievable. You don't control aim angle with mouse precision, but standing flush against the boss achieves the overlap naturally. The difference vs mouse is minor — overlap is a bonus, not a requirement.

### Shield Crush of the Chieftain differences
Same 3-wave/2-overlap geometry. Key changes:
- Converts entirely to **fire damage** — benefits from fire scaling, not physical
- Adds fire damage from the shield's **armour rating** (not evasion) — an armour-based shield provides both defense and skill damage
- Center wave has significantly **more AoE** than base version; gem quality further scales center wave AoE — the seam zone is easier to land naturally
- Lower mana cost; slower base attack speed than the base version

---

## Cord Belt — Second Anoint (Mirage League)

The **Cord Belt** base (added in Mirage league) can be anointed with oils like an amulet, granting an additional passive notable beyond the amulet anoint. This effectively gives two anoint slots: one on the amulet and one on the Cord Belt. Factor this into build planning — the belt anoint is a meaningful extra notable slot.

---

## Aura Slots — Mana Reservation Efficiency Anoint

Anointing a **mana reservation efficiency** notable is a strong general choice for almost any build (exception: Blood Magic builds). Reducing aura costs can unlock an additional aura slot that otherwise doesn't fit the budget. Evaluate this before committing to a damage or defensive anoint — the extra aura may outvalue the anoint's direct stats. Not applicable to builds that deliberately use Blood Magic for aura reservation.

---

## Leveling to 95 — Passive Points Over Everything

Each level up to 95 is a free passive point. Passive points are the strongest possible upgrade per unit of effort at this stage, so **leveling should be prioritized over atlas progression, side content, and quests** until 95. After 95 the XP curve becomes brutal and the calculus shifts.

### Best XP Method: Abyss
- Go full Abyss investment on the atlas tree
- Abyss adds extra XP from the monsters it spawns
- **Exception: skip Abyssal Depths.** The Stygian Spire boss can be deadly if chaos resistance is not maxed. Not worth the death risk.

### Map Rolling
- Roll maps **magic** (not rare — too rippy, slower clear)
- Target the **"more magic monsters"** explicit modifier using Alteration Orbs
- More magic monsters = more XP per map without adding deadly mechanics

### Death Avoidance
- Death at high levels loses significant XP — a single death can cost 10+ minutes of grinding
- **Avoid rippy mechanics** (Delirium, high-tier Beyond, dangerous map mods) until you hit 95
- Best time to attempt dangerous content: immediately after leveling, when you have a full XP buffer before the next level matters

---

# PoE Build Analyzer Tools Guide

## Overview

This project provides MCP servers and scripts for analyzing Path of Exile builds, with full support for Sony (PlayStation) realm players.

## Quick Start

```bash
# 1. List your characters
# Use the pob-importer MCP tool: list_characters

# 2. Import and analyze a character
python build_expander.py --import --character "YourCharName" --league Mirage --realm sony
```

---

## MCP Servers

### 1. poemcp
**Purpose:** Path of Exile game data lookup

**Tools:**
- `search_gem` / `get_gem_detail` - Gem info
- `search_item` / `get_item_detail` - Unique item info  
- `search_passive` / `get_passive_detail` - Passive tree nodes
- `price_check` - Item prices from poe.ninja
- `currency_overview` - Currency exchange rates
- `search_mods` - Item modifier search
- `parse_pob` - Parse Path of Building export strings

**Realm Support:** Add `realm: "sony"` parameter for accurate PlayStation prices

**Example:**
```
price_check(query: "Headhunter", league: "Mirage", realm: "sony")
```

### 2. pob-importer
**Purpose:** Import character data from PoE API

**Tools:**
- `list_leagues` - List available leagues
- `list_characters` - List characters in a league
- `import_character` - Download full character data

**Defaults (pre-configured):**
- realm: SONY
- account: Ladimir_Lepin#9831

**Example:**
```
import_character(character_name: "YourCharName", league: "Mirage")
```

---

## Scripts

### build_expander.py

Comprehensive build analysis - imports character and enriches with full details.

```bash
python build_expander.py [options]

Options:
  character_file          Path to existing character JSON
  --import               Import character from PoE first
  --character <name>     Character name to import
  --league <name>        League name (default: Mirage)
  --realm <realm>        pc, xbox, sony (default: sony)
  --output, -o           Output file path
```

**Usage Examples:**

```bash
# Import and expand character directly
python build_expander.py --import --character "MyCharacter" --league Mirage --realm sony

# Expand from existing JSON
python build_expander.py MyCharacter.json --league Mirage

# Save to custom location
python build_expander.py --import --character "MyCharacter" -o build_analysis.json
```

**Output includes:**
- Passive tree: keystones, notables, masteries with full stats
- Equipment: all items with explicit/implicit/enchant mods
- Unique items: mod details from poedb.tw database
- Skill gems: levels, quality, support/link info
- Prices: current chaos/divine values from poe.ninja

---

## Typical Workflow

### 1. List Your Characters
```
Use MCP tool: list_characters
Parameters: realm="SONY", account="Ladimir_Lepin#9831", league="Mirage"
```

### 2. Import Character
```
Use MCP tool: import_character  
Parameters: character_name="CharName", league="Mirage"
```

Or use the script:
```bash
python build_expander.py --import --character "CharName"
```

### 3. Get Item/Gem Details
```
Use MCP tools:
- get_item_detail("Item Name")
- get_gem_detail("Gem Name") 
- get_passive_detail("Node Name")
```

### 4. Check Prices
```
Use MCP tool: price_check
Parameters: query="Item Name", league="Mirage", realm="sony"
```

---

## File Structure

```
/Users/a/code/games/poe/
├── .mcp.json                    # MCP configuration
├── .claude/
│   └── memory.md                # Project memory
├── POEMCP/                      # Poemcp server
│   └── server.py
├── pob/
│   └── PathOfBuilding-2.59.2/
│       └── tools/
│           └── mcp_server.py    # POB importer server
└── build_expander.py            # Build analysis script
```

---

## Troubleshooting

### "Account is private"
Your PoE account is set to private. To import characters:
1. Make account public on pathofexile.com, OR
2. Provide POESESSID cookie (for private profiles)

### Price mismatch
Ensure you're using `realm: "sony"` for PlayStation prices. PC and Sony have separate economies on poe.ninja.

### Import fails
- Check character name is exact (case-sensitive)
- Verify league name is correct
- Account must exist on the specified realm

---

## Notes

- Sony realm uses poe.ninja API with `realm=sony` parameter
- Default account: Ladimir_Lepin#9831
- Current league: Mirage
- All tools support async operation via MCP protocol

---

# Build Audit Procedure

A systematic checklist to run when reviewing a build. Do not skip sections — missed opportunities are often in areas assumed to be already optimised.

## 1. Passive Tree

- **Every allocated notable:** verify its stats still apply to the build mechanics. Dead mods on tree notables (e.g. "damage with one-handed weapons" on a Shield Crush build) are points that should be reallocated.
- **Overcapped stats:** check block, resistances, accuracy. Overcap on block = wasted points or an opportunity for Versatile Combatant conversion. Overcap on resistances = potential to drop res nodes for damage.
- **Pathing efficiency:** each small node on the path to a notable costs a point. Check if the path could be rerouted through better small nodes (e.g. armour% instead of regen), or if a shorter path exists.

## 2. Timeless Jewels — Three Separate Checks

### Layer A: Timeless Jewels in General
Timeless jewels split into two fundamentally different categories:

**Additive only (Lethal Pride):**
- Adds bonus stats to nodes in radius without removing existing stats
- Exception: keystones in radius are replaced, not augmented
- Audit: what is being ADDED to your existing nodes, and is any keystone in radius being replaced

**Full conversion (Glorious Vanity, Militant Faith, Elegant Hubris, Brutal Restraint):**
- Replace or convert ALL notable passives in radius (and sometimes small nodes) to entirely different stats
- You are trading your existing allocated notables for new ones — the loss matters as much as the gain
- Audit: for every allocated notable in radius, compare what you had vs what it becomes. Also check unallocated notables in radius — they may become worth allocating, or previously valuable notables may no longer be worth pathing to
- Keystones in radius are also replaced, same as Lethal Pride

For any timeless jewel, run the analysis tool (`timeless_jewel_analysis.py`) for the specific seed + socket position. Effects are fully deterministic but seed+position dependent — never assume without calculating.

### Layer B: Lethal Pride Specifically
Lethal Pride is purely **additive** — it adds bonus stats to nodes without removing existing ones (except keystone replacement if applicable).

**Allocated nodes — read every bonus:**
- Each allocated node in radius gains extra stats. Read them all.
- The best possible Lethal Pride bonus is **5% chance to deal Double Damage** — a "more" multiplier, effectively ~5% more DPS. Highest priority if present anywhere in radius.
- Other strong bonuses: life%, armour%, strength, damage%.

**Unallocated notables in radius — pathing evaluation:**
- The script lists unallocated notables within radius and what Lethal Pride bonus they carry.
- For each: (1) is the notable's own stats good? (2) is the Lethal Pride bonus on it good? (3) how many points to reach it?
- **Critical step:** check whether a single repath of an existing small node puts you adjacent to a notable with a strong bonus. One point of rerouting can unlock 5% double damage or similar — this is easy to miss and must be checked explicitly.

### Layer C: Ngamahu Jewel Placement (Chieftain Ascendancy — non-fire builds only)
Ngamahu converts any non-fire damage bonuses on passives in radius of non-unique jewels to also apply as fire — this includes physical, cold, lightning, and chaos damage bonuses. For **fire builds** (the natural Chieftain path), this is a pure benefit. For **non-fire builds** (e.g. physical Shield Crush with Brutality, which zeroes out fire damage), the converted fire bonuses are wasted.

Ngamahu also grants +4 Strength per non-unique jewel in regular passive tree sockets within radius.

**The check (non-fire builds only):**
- For each regular tree jewel socket in Ngamahu's radius: if a non-unique jewel is placed there, would it cause Ngamahu to convert important damage bonuses on nearby passives to fire (wasted)?
- If yes: place a **unique jewel** there instead — loses the +4 Str bonus but preserves the damage nodes as their original type
- If no important damage nodes are in that sub-radius: a non-unique jewel is fine, capturing the +4 Str bonus

This check is irrelevant for fire Chieftain builds where the fire conversion is desirable.

## 3. Gear Implicits

- **Eldritch implicits (Eater/Exarch):** for each non-unique, non-influenced, non-corrupted armour piece — is there an implicit? Is it optimal for the build? Check the pool for the slot before deciding to reroll.
- **Corrupted implicits:** for corrupted items, note what implicit was gained. Check if a different corruption would be significantly stronger (relevant when upgrading the base item).

## 4. Gem Links

- Is the main skill in a 6-link? Is every support actually applying to the skill (check for "no green checkmark" in PoB)?
- Are support gems leveled appropriately? A support at level 1 when it should be 18-20 is a major loss (especially impale, empower, etc.).
- Are gems corrupted for +1 level where it matters (key active skill, empower)?

## 5. Aura / Reservation Budget

- List all active auras and their reservation cost. Is there room for one more? If not, would a mana reservation efficiency anoint open a slot?
- Check if any aura can be dropped (e.g. Precision if accuracy is already well above life for Precise Technique) and replaced with something more impactful.

## 6. Flask Setup

- Each flask should have a purpose: life recovery, armour/evasion buff, ailment immunity, utility.
- Check ailment coverage — which ailments are not covered by tree/gear? Flask suffixes fill the gap.
- Dying Sun, Bottled Faith, Taste of Hate: check if any are accessible and impactful for the build.
