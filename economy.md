# PoE Lab Economy — Gem Conversion Guide

## Overview

The Labyrinth's **Divine Font** (in the Aspirant's Plaza, after the final boss) offers several gem-related enchantments. Two are relevant for economy:

1. **Facetor's Lens farming** — sacrifice high-level trash gems for lenses
2. **Transfigured gem conversion** — deterministic if the base gem has only one transfigured variant

---

## 1. Facetor's Lens — Converting Trash Level 21 Gems

### Divine Font options (random each run)

Each Font use presents **4 random options** from this pool — you pick one, the rest are lost:

| Option | Value | Notes |
|--------|-------|-------|
| Add quality to gem | ★★★★ | Up to 20% in one roll; ~2.5c per % |
| Sacrifice gem → Facetor's Lenses | ★★★★ | Scales with gem level; level 21 → ~63m lens |
| Transfigure a specific gem | ★★★★ | **Rare** to appear; deterministic if one variant (see section 2) |
| Change gem to random transfigured | ★★☆☆ | Random from same-color pool; high variance |
| Add XP to a gem | ★★☆☆ | 50m XP is ~60c if applied to a gem you're leveling, but competes with better options |
| Sacrifice gem for treasure keys | ★☆☆☆ | Trash; keys have minimal value vs other options |

**Font uses per difficulty:**
- Merciless lab: **1 use** (occasionally 2 — rare and unusual, not reliable)
- Eternal lab: **2 uses** — each use gets its own fresh 4-option draw

If the option you want doesn't appear on a use, it's gone — you can't reroll. The run still gives helmet enchants and atlas completion regardless.

### What the Facetor's Lens option does
Sacrifices a gem and returns Facetor's Lenses scaled to the gem's level. The conversion rate shown (e.g. "20%") is the fraction of the gem's total experience converted into lens quality-experience.

- Level 21 gems return significantly more lenses than lower levels
- Any gem type works — identity doesn't matter, only level
- The gem is consumed regardless of outcome

### Sony market reference (Mirage league, day 5)

> **Context:** Mirage is a slower-moving league with redesigned progression — economy moves slower than a typical popular league. These prices reflect early availability, not peak market.

| Lens quantity | Price |
|--------------|-------|
| 10 million   | ~20c  |
| 50 million   | ~60c  |
| 200 million  | ~90c  |
| 500 million  | ~90c (outlier/premium listing) |

**Lens use tiers:**
- Regular gems (most skills): need ~300 million quality experience to fully level → a 200m lens covers most of the way; 50m lens gets you partway
- Awakened or Exceptional gems: need much more experience → 500m+ lenses are worth saving for these; don't use them on regular gems

**Example run A — merciless lab (free):**
- Level 21 trash gem cost: ~3c
- Run time: ~6 min (Shield Charge Chieftain)
- Options offered included Facetor's Lens conversion → took it
- Lens yield: ~63 million quality experience
- Market value: ~60c
- **Net: ~57c for 6 minutes**

**Example run B — eternal lab (paid, 2 Font uses):**
- Lab pass cost: ~4c, run time: ~7 min (same build)
- **Use 1 — options:** random transfigure / 50m XP / 20% quality / sacrifice for treasure keys
  - Took 20% quality → ~90c at ask side of spread
- **Use 2 — options:** random transfigure / specific gem transfigure / 50m XP / 8% quality
  - Took specific transfigure on Shock Nova → Shock Nova of Repetition, lowest ask ~60c
- **Gross: ~150c. Net: ~145c for 7 minutes** (minus ~4c pass + ~1c base Shock Nova)

**Key observations from run B:**
- The valuable "specific transfigure" option appeared only on the second use — not guaranteed on either
- 50m XP appeared on both uses (consistent filler option)
- Treasure keys appeared on use 1 — correctly skipped (trash)
- Taking 20% quality on use 1 over the random transfigure was correct — certainty beats variance when the certain option is already high value

### Decision criteria

**Worth converting if:**
- You have level 21 gems that are common and low demand in base form
- The gem has no valuable transfigured version to convert to instead (check section 2 first)
- Merciless lab is available free

**Not worth converting if:**
- The base gem has trade value on its own
- The gem is 20/20 quality — has its own value floor regardless of skill demand
- The gem could be a good base for corruption (level 21 → 21/20 attempt for a popular skill)
- You have a better use of 6 minutes (mapping, etc.)

### Workflow

1. Identify level 21 gems you consider trash
2. Use `search_gem` MCP — check if any transfigured version is worth converting to instead
3. If no transfigured opportunity and gem is cheap → run merciless lab and sacrifice it
4. **Save 500m+ lenses** — don't apply them to regular gems; hold for awakened/exceptional gems

### Quality enchant vs other options

Quality ranges observed: 8–20% per Font use. At ~2.5c per GCP equivalent:
- 20% quality → ~50c value
- 8% quality → ~20c value

Quality is worth taking over random transfigure (high variance), XP filler, and keys. Only skip it if the specific transfigure option is also available and the target gem has exactly one variant and is worth more than the quality value.

### Notes
- The Font option you need is not guaranteed — plan around getting it occasionally, not every run
- Eternal lab (2 Font uses) doubles your chances of hitting the option you want and doubles value if you do
- Buying an eternal lab pass (~4c) can be worth it if you have multiple gems to convert

---

## 2. Transfigured Gem Conversion — Deterministic vs Random

### Two different Font options — know the difference

**"Change gem to random transfigured (same color)"** — common option:
- Picks a random transfigured variant from the pool matching the gem's socket color
- NOT limited to variants of the specific gem you sacrifice — it's any transfig of the same color
- High variance; only good if you intentionally sacrifice a cheap gem to fish for expensive same-color transfigs

**"Transfigure a gem"** — rare option:
- Converts the specific gem you sacrifice into one of *its own* transfigured variants
- If the gem has only one transfigured version → **deterministic, guaranteed outcome**
- If the gem has multiple transfigured versions → random among them

**Critical rule for the rare option: only use a valuable target gem when the gem has exactly ONE transfigured version.**

### How to check how many transfigured variants exist

Use the MCP tools:
```
search_gem("Shock Nova")       → shows base gem + all variants
get_gem_detail("Shock Nova")   → confirms variant count and names
```

If the search returns only one transfigured name (e.g. "Shock Nova of Repetition" and nothing else), conversion is safe.

### Decision criteria

**Convert if (all three conditions):**
1. The gem has exactly **one** transfigured version
2. That transfigured version is **expensive** — meaningfully more valuable than the base gem
3. The base gem itself is **cheap** — you're not sacrificing something valuable to gamble

**Do not convert if:**
- The gem has multiple transfigured versions (random outcome — calculate expected value first)
- The base gem is already valuable (you're paying more than you think)
- The transfigured version's value is uncertain — wait until you can assess demand

### Example: Shock Nova of Repetition (Mirage league reference)
- Shock Nova has only one transfigured version: **Shock Nova of Repetition**
- Shock Nova of Repetition is sought after for specific shock-stacking builds
- Base Shock Nova is trivially cheap
- Result: this is a high-confidence deterministic conversion — always worth running if the Divine Font offers the transfiguration option

### Expected value calculation for multi-variant gems (if you want to try anyway)
```
EV = (value_variant_A + value_variant_B + value_variant_C) / number_of_variants
```
Only worth converting if EV > (cost of base gem + cost of lab run).

On PlayStation, you cannot get prices from poe.ninja. Use in-game trade search to manually check current ask prices for each variant before committing.

---

## 3. Lab Run Checklist for Gem Economy

Before running lab specifically for gem conversion:

- [ ] **Identify the gem(s) you want to convert** — have them in inventory
- [ ] **Check variant count** using `search_gem` MCP — confirm deterministic or calculate EV for random
- [ ] **Verify the gem is actually cheap** — don't sacrifice a gem with hidden value
- [ ] **Check the enchantment pool** — the option you need (Facetor's Lens or Transfiguration) must appear; it's not guaranteed every run
- [ ] **Have a lab key/offering ready** if required
- [ ] **Run Uber Lab** for best enchantment pool access

---

## 4. Other Divine Font Gem Options (for reference)

| Option | What it does | When useful |
|--------|-------------|-------------|
| Add quality to gem | Adds % quality (amount varies) | Early league when 20q gems are scarce |
| Corrupt a gem | Standard corruption — can add level, quality, Vaal version, or nothing | Pre-corrupting 20/20 gems for 21/20 attempts |
| Sacrifice for Vaal version | Destroys gem, gives Vaal variant | If you need a Vaal gem and it's cheaper to run lab than buy |
| Sacrifice for Facetor's Lenses | Destroys gem, gives lenses | Level 21 trash gem conversion (see Section 1) |
| Sacrifice for Transfigured | Destroys gem, gives transfigured variant | Deterministic if only one variant (see Section 2) |

---

## Using MCP Tools for These Decisions

```
# Check all variants of a gem before converting
search_gem("Gem Base Name")

# Verify what the transfigured version actually does (is it useful/sought after?)
get_gem_detail("Gem Name of Variant")

# Look up wiki for lab Font options if unsure what's in the pool
fetch_wiki_page("Divine Font")
```

**Reminder:** No price data exists for PlayStation on poe.ninja. All value assessments must be done via in-game trade search or community knowledge. When in doubt, ask in trade chat before converting.

---

## 5. Menagerie — Unique Map Crafting

Einhar's Menagerie beastcrafting includes a recipe to **create a unique map** from a normal map base using four specific beasts. This is reliable early/mid league income because:

- Unique maps are scarce early — players need them for challenge #23 (Remarkable Realms: complete all 17 unique maps) and for specific farming strategies
- The recipe is deterministic: you choose which unique map to craft based on the beast combination
- Normal map bases cost nothing; the value is entirely in the beasts captured

**How to use it:**
1. Check which unique maps are in demand (challenge #23 requires all 17 — any unique map has demand early league)
2. Capture the required beasts while mapping (Einhar missions or Einhar appearing naturally)
3. Craft in the Menagerie — pick the most valuable unique map the current beast stock allows
4. List immediately; early league scarcity means buyers are active

**Mapping strategy note:** Beasts and Essences do not benefit meaningfully from higher map tiers — their rewards don't scale significantly with map level. Run these mechanics freely on lower-tier progression maps without opportunity cost. Save high-tier map investment for mechanics that do scale: Delirium, Abyss depth, Breach (more splinters), Legion (more emblems), etc.

---

## 6. Selling Items — Trade Filter Visibility

When listing rare items for sale, the item needs to match what buyers' trade filters are searching for. A 5-mod item may be invisible to filters that require 6 mods or a specific combination.

### Benchcraft for discoverability
Add a cheap bench craft to fill the last affix slot before listing. This makes the item:
- Show as "6 affixes" (some filters specifically require 6-mod rares)
- Match more specific filter combinations if the craft adds a commonly-searched mod (e.g. fire resistance, life regeneration, flat armour)

The craft costs you nothing meaningful but can significantly increase the number of buyers who see the item. Pick a craft that:
1. Is cheap (1–2c bench cost or free)
2. Doesn't conflict with the item's purpose
3. Ideally adds something buyers might want alongside the item's main mods

**Important:** Catalyst quality interacts with benchcrafts — apply catalysts *before* crafting, as catalyst quality only boosts mods of the matching type. A suffix craft after a suffix-quality catalyst will benefit from the quality.

### Exalted orbs — current state (Mirage league)
Exalted orbs are cheap this league. Use them freely to fill out rare items:
- Fill 5 mods with exalts, **keep one slot open for a bench craft**
- The bench craft is reserved for the most useful or cheapest option you can add
- An item with 5 strong exalted mods + a bench craft is nearly always better than 4 exalted + 2 bench (or leaving slots empty)

---

## 7. Mirage League — Coin of Restoration Economy

### What it does
Coin of Restoration upgrades an Afarud unique (tainted Maraketh item that drops in Mirage encounters) to its Maraketh form — the restored, usually stronger version.

| Afarud (drops from Mirage) | → Maraketh (after Coin of Restoration) |
|---|---|
| Khatal's Weeping | Khatal's Geyser |
| Fleshrender | Skysunder |
| The Bane of Hope | The Flame of Hope |
| The Desecrated Chalice | The Sacred Chalice |
| Saresh's Darkness | Solerai's Radiance |

Maraketh forms are generally the endgame-ready versions. Coins of Restoration drop commonly and have no meaningful market value — they are effectively free. The conversion is therefore costless: buy a cheap Afarud unique, restore it for free, sell the Maraketh version. Profit is purely the price spread between Afarud and Maraketh forms, which depends on whether the Maraketh version has any demand.

### Foulborn items — the high-value interaction
**Coin of Desecration** (drops from Beyond bosses in Mirage areas) does the reverse: converts a Maraketh unique into its Afarud form and **adds a corruption implicit modifier** to it. The resulting item is corrupted.

**Key rule:** Using Coin of Restoration on a Coin-of-Desecration'd (foulborn) item restores it to Maraketh form **while preserving the corruption implicit**. This produces:

> Maraketh unique + corruption implicit = most valuable state

This is the high-value use case. Steps:
1. Obtain a Maraketh unique (or restore an Afarud one first)
2. Use Coin of Desecration → get Afarud form with a corruption implicit
3. Use Coin of Restoration → get Maraketh form, implicit preserved

The implicit is random, so this is a gamble — but if the result is good, the item is significantly more valuable than either base form alone. Check demand for the Maraketh item before investing Coins of Desecration. Coins of Restoration are worthless/free so the only real cost is the Desecration coin and the base Maraketh item.

### Mirage Gem Imbuement — Coins of Power/Knowledge/Skill
**Borrowed power mechanic** — league-temporary, will not exist after Mirage ends.

These coins corrupt a **level 20 skill gem**, adding the effects of a random Support gem of the matching colour (Str/Int/Dex) as an implicit. The gem becomes corrupted.

- Coin of Power → random Strength support effect
- Coin of Knowledge → random Intelligence support effect
- Coin of Skill → random Dexterity support effect

**In practice:** The support pool is large and most rolls are irrelevant to any specific build. Coin of Power in particular has very poor hit rate for melee/phys builds — the chance of landing a useful Str support (e.g. Brutality, Impale, Melee Physical Damage) is low. These coins have market value because other players want to gamble with them. **Always sell Power/Knowledge/Skill coins rather than using them yourself** — the EV of self-use is too low to justify, and the coins are worth more to gamblers than to you.

### Coin Price Data — Sony (PlayStation) vs PC

Recorded: Mirage league day 5 [2026-03-11]. PC data via poe.ninja; Sony data from in-game trade spreads.

**Sony spread notation: bid–ask** (e.g. 56–91c = buyers at 56c, sellers at 91c). n/a on the left = no buyers; n/a on the right = no sellers. A number with n/a on the other side means one-sided market — no real price.

| Currency | Sony (ask–bid) | PC (poe.ninja) | Notes |
|---|---|---|---|
| Coin of Knowledge | 56–91c | ~71c | Sony roughly on par |
| Coin of Power | 23–69c | ~97c | Sony much cheaper — less demand or more supply |
| Coin of Skill | 33–57c | ~41c | Sony roughly on par |
| Coin of Desecration | n/a–17c | ~0.53c (1.9/c) | Sony: sellers at 17c but no buyers — no demand, illiquid |
| Coin of Restoration | n/a–1/3c | ~0.036c (28/c) | Sony: sellers at 1/3c, no buyers — worthless; drops freely and has no meaningful use |
| Exalted Orb | 1/2–1c | ~2c | Sony cheaper; both realms near-zero vs divine |
| Divine Orb | 170–175c | ~172c | Essentially 1:1 |

**Foulborn Exalted Orb** (PC): ~350c — no Sony reference yet, but high value on PC implies significant value on Sony given div parity.

**Observations:**
- Sony and PC divine orb prices are nearly identical — both markets anchor to the same benchmark.
- **Coin of Power**: Sony (23–69c) vs PC (97c) — Sony significantly cheaper. Power has the worst hit rate for most builds; PC gamblers may be more active or have more currency to burn.
- **Coin of Desecration**: 0.53c on PC (liquid market). Sony has sellers at 17c but no buyers — no demand at that price. Effectively illiquid; the ask is meaningless without a bid.
- **Exalted Orb**: effectively vendor trash on both realms now (~2c PC, sub-1c Sony). Historic high of 60–80c in older leagues — the shift to Divine Orb as the primary currency sink is complete.
- Restoration worthless because it both drops freely AND has no meaningful use case (conversion is free by design).

---

## PlayStation (Sony) Realm — No Public Price Data

poe.ninja and similar sites do not index the PlayStation market. **Do NOT use price_check or currency_overview MCP tools for PS builds.** Price data returned will be PC prices, which are meaningless for PS economy.

When discussing item costs for PS players:
- Speak in relative terms only: "this is a chase item and will be expensive", "this drops commonly and should be cheap", "this requires a divine orb craft"
- Never cite specific chaos/divine values

---

## League Stage Priorities

### Early League / League Start (first 1–2 weeks)
Do NOT recommend:
- Forbidden Flame / Forbidden Flesh jewels (extremely rare, expensive early)
- Awakened support gems (not available early, cost dozens of divines)
- 21/20 gems (require 23% quality gems + corruption, very expensive)
- Mirror-tier or high-end crafted items
- Headhunter, Mageblood, or other chase uniques

DO recommend:
- Self-craft or cheap rares
- Normal 20/20 gems (or even 20/0)
- Budget unique alternatives
- Core build uniques that drop commonly
- Cluster jewels with basic notables
- Survivability before damage optimization

### Mid League (2–6 weeks)
- Awakened gems exist but are still costly — only recommend if player has surplus currency
- Forbidden jewels exist but are expensive — only recommend if budget allows
- 20/20 gems are standard; 21/20 may be achievable for key gems
- Divine orbs are the main currency benchmark (no exact price data for PS)

### Late League / Endgame Pushing
- Full optimization: awakened gems, 21/20 on key gems, forbidden jewels
- Mirror crafts for BIS slots
- Six-link +1 gems weapons, etc.

---

## 8. Astrolabe Prices — Sony (PlayStation)

Recorded: Mirage league [2026-03-25]. Sony data from in-game trade spreads (bid–ask in chaos).

| Astrolabe | Bid | Ask |
|---|---|---|
| Grasping Breaches | 191 | 300 |
| Nameless Ritual | 80 | 135 |
| Runic | 75 | 120 |
| Fruiting | 102 | 109 |
| Chaotic Ultimatum | 75 | 100 |
| Enshrouded Delirium | 50 | 100 |
| Lightless | 25 | 100 |
| Timeless Legion | n/a | 75 |
| Templar Shaper | 55 | 75 |
| Fungal | 36 | 50 |

**Observations:**
- Grasping Breaches is the premium astrolabe — wide spread suggests low liquidity at the top
- Fruiting has the tightest spread (102–109) — most liquid, active market
- Lightless has a huge spread (25–100) — buyers and sellers far apart, illiquid
- Timeless Legion has no buyers — sellers only at 75c

---

## 9. Dust Disenchanting — Vulconus

For converting chaos into dust (Mirage disenchanting currency), **Vulconus** is efficient:
- Costs 1c to buy
- Gives ~45k dust at ilvl 83 without quality
- **Watch item levels when buying** — dust value scales with item level. Lower ilvl = less dust.

---

## 10. Gold → Fusing Orb Conversion via Trash Six-Links

When fusing orbs are expensive (e.g. 2:1 chaos), you can convert excess gold into fusings by buying vendor-priced six-link items from other players and vendoring them.

**How it works:**
- Six-link items vendor for **20 Fusing Orbs** (guaranteed vendor recipe)
- Trash six-links (bad bases, bad mods) are listed for 1c or less because they have no use beyond the vendor recipe
- At 2:1 fusing-to-chaos ratio, 20 fusings = 10 chaos value
- Cost: 1c purchase + ~5k gold → **~9c profit per item**

**When to do this:**
- Fusing price is high (1.5:1 or better vs chaos)
- You have gold to burn and no better use for it
- Trash six-links are available at 1c or below

**When NOT to do this:**
- Fusing price drops below 2:1 — profit margin disappears
- Six-links are listed above 5c — other players are already pricing in the recipe value

---

## General Upgrade Advice

- When suggesting upgrades, order by: impact on build (damage, survivability, QoL) weighted by expected availability.
- For gem recommendations: check if corrupted implicit (+1 level) matters for the skill before recommending corruption.
- Always check if a unique's mods are still relevant after potential nerfs — verify via wiki.
- Mastery choices: verify they work with the build mechanic before suggesting.
