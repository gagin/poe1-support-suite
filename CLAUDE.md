# Path of Exile Build Assistant - Claude Instructions

## MCP Servers (pre-configured in .mcp.json)

- **poemcp** - Game data: gems, items, passives, price checks, wiki, mods
- **pob-importer** - DISABLED / unreliable: returns HTTP 403 when listing characters. Do not use it for importing.

Only poemcp is reliably usable.

## Standard Workflow

**Always use the two-step lua + python process. Do NOT use the pob-importer MCP for character imports.**

### Step 1: Import character via lua script
```bash
cd pob/PathOfBuilding-2.59.2/tools
lua import_character_cli.lua SONY Ladimir_Lepin#9831 <CharacterName>
```
Output: `pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json`

### Step 2: Expand the JSON (run from repo root)
```bash
python build_expander.py pob/PathOfBuilding-2.59.2/tools/<CharacterName>_YYYYMMDDHHMM.json --league <League> --realm sony
```
Output: `<CharacterName>_YYYYMMDDHHMM_expanded.json`

Note: The `--import` combined flag exists but the two-step approach is preferred for reliability.

## Build Analysis Rules

### Information Validity — Always Verify
**PoE changes mechanics every league (~3 months). Assume any recalled knowledge may be outdated.**

- Before stating a mechanic as fact, verify it via MCP tools (search_passive, get_gem_detail, fetch_wiki_page) or note explicitly that it is unverified.
- Training data and previous memory entries can describe mechanics that no longer exist. Example: alternate quality gems (Anomalous/Divergent/Phantasmal) were removed in patch 3.23.0 and no longer exist.
- When a fact is verified in a session, it can be noted with a date in memory files: `[verified YYYY-MM]`. Undated entries should be reverified before being cited confidently.

### Weapon Swaps
**Ignore weapon swap slots entirely.** Only analyze the main hand and offhand that are active for the build. Weapon swap sets are typically for utility (flasks, movement) and not part of the core build.

---

## PoE Mechanics — Core Knowledge for Build Advising

### Skill Links and the 6-Link

The **body armour** is the default 6-link slot for the main skill. Exceptions:
- **Helmet with support implicits** (e.g. Inpulsa's + Elder helmet with supported-by-Burning Damage implicit): the helmet becomes the main skill slot; body armour is used for an aura or secondary skill. Righteous Fire builds commonly do this.
- **Bow builds**: the bow itself is 6-linked; quiver is the offhand. Body armour holds a secondary skill or auras.
- **Two-handed weapon builds**: the weapon is 6-linked; body armour holds a secondary skill or auras.
- **Squire shield**: provides 4 additional supports to a skill in the main hand — effectively a 6-link from a 2-link weapon. Body armour is free for another 6-link.
- Any build with a 6-linked weapon uses the body armour for a second major skill or aura setup.

When advising on links, identify which slot is actually the main skill slot before recommending anything.

### More vs Increased — Damage Scaling

**Increased** modifiers are **additive** with each other:
- All sources of "increased damage", "increased fire damage", "increased spell damage" etc. pool into one sum: `(1 + total_increased%)`
- Adding 50% increased when you already have 300% increased is a small relative gain.

**More** modifiers are **multiplicative** — each is its own separate multiplier:
- Support gems typically grant "more" damage: e.g. Empower, Concentrated Effect, Elemental Focus.
- Each "more" multiplier stacks multiplicatively with the others.
- Adding a new "more" source is usually much stronger than adding more "increased".

**Formula (simplified):**
```
Damage = Base × (1 + Σincreased%) × more_1 × more_2 × more_3 × ...
```

Implication: when a build already has 400%+ increased damage, additional increased is weak. A new "more" multiplier is often the strongest upgrade.

### Flat (Added) Damage and Effectiveness of Added Damage

"Adds X to Y damage" mods add a flat amount to the skill's base damage **before** scaling.
- Attacks typically have **100% effectiveness of added damage** — flat damage from rings, gloves, abyss jewels, etc. applies fully.
- Spells have their own **effectiveness of added damage** listed in the skill description (e.g. Freezing Pulse has 100%, Arc has 70%, some skills have 30%). Low-effectiveness spells gain little from added flat damage — don't stack it for them.
- Totems, traps, and mines can have their own effectiveness modifiers.

### Damage Multipliers Beyond "More" — Shock, Charges, Exposure, Curses

These are often overlooked but act as strong multipliers:

**Shock** (Lightning ailment):
- Enemy takes "increased damage" — this is a separate "increased damage taken" layer on the enemy, not on the player.
- Base shock: 15% increased damage taken. Can be scaled up to 50% with "effect of shock".
- Because it's on the enemy's side, it multiplies with all the player's own damage scaling.
- Effective for any damage type, not just lightning.

**Exposure**:
- Lowers enemy resistance by 10% (more with scaling). Stacks with penetration differently — exposure lowers the resistance value, penetration ignores a portion of it.
- All three elemental types have exposure skills/ailments (Combustion support, Frost Bomb, Ball Lightning of Static, etc.)

**Curses**:
- Vulnerability: increased physical damage taken + chance to bleed.
- Flammability/Frostbite/Conductivity: lower elemental resistances (similar to exposure but larger).
- Elemental Weakness: lowers all elemental resistances.
- These work on the enemy side — powerful multipliers that benefit the whole party.

**Charges**:
- **Power charges**: +40% critical strike chance per charge (base), up to 3 (or more with passives).
- **Frenzy charges**: 4% more attack/cast speed + 4% more damage per charge (up to 3+).
- **Endurance charges**: +4% physical damage reduction + 4% to all elemental resistances per charge.
- Frenzy charges are the offensive charges; power charges are for crit builds; endurance is defensive.

**Elemental Overload**: doubles effectiveness if you crit, but removes crit multiplier — only worthwhile on low-crit builds.

### Physical vs Elemental (and Chaos)

**Physical damage**: mitigated by **armour** (effective mainly vs small hits) and **physical damage reduction** (flat %, much more reliable). Fortify provides 20% PDR.

**Elemental damage (fire/cold/lightning)**: mitigated by **resistances**. Default cap is **75%**. Characters can raise their cap via:
- Purity of Elements/Fire/Ice/Lightning (auras)
- The Consuming Dark (unique), Atziri's Splendour, etc.
- Passive nodes (rare)

**Chaos damage**: mitigated by **chaos resistance** — often negative on characters. Chaos res gear is frequently overlooked but critical for endgame.

**Penetration vs Exposure**:
- Penetration (e.g. "enemies have -X% fire resistance" from Flammability, or fire penetration support): ignores that amount of the enemy's resistance. More valuable when enemy resistances are high.
- Exposure: reduces the enemy's actual resistance value. Both stack independently.

**Conversion**:
- Physical → elemental conversion (e.g. 50% phys to fire via Pyre or passives): the converted portion benefits from both physical damage scaling *before* conversion and elemental scaling *after*. Non-converted portion remains physical.
- Full conversion (100%) means all physical scaling + all fire scaling apply — very powerful.
- Conversion is applied before any mitigation, so the damage type at the time of hit determines what resists it.

### Curse Limit

Default: **1 curse** on enemies at a time. Sources that grant additional curses:
- **Whispers of Doom** keystone (passive tree)
- **Doedre's Damning** ring (+1 curse)
- **Windscream / Windshriek** boots (+1 curse to non-unique enemies)
- **Impresence** amulet (free reservation for one specific curse + +1 effective for that curse type)
- **Malediction** (Occultist ascendancy): enemies can have +1 curse
- Some unique items and cluster notable passives

If a build needs 2 curses, explicitly verify one of these sources exists. Don't assume multi-curse without it.

### Critical Strikes

- **Crit chance** = base skill crit × (1 + increased crit chance%) × more crit chance
- **Crit multiplier** = 150% base + flat additions (e.g. "+50% to global crit multi"). Added together, then multiplied as a "more" during a crit hit.
- Crit is only valuable if the build actually reaches a meaningful hit rate (typically 60%+ for it to be a significant DPS source; 90%+ for pure crit builds).
- **Ailment builds** (ignite, bleed, poison): only the initial crit matters for ailment magnitude — crit multi does **not** scale DoT damage unless specifically stated (e.g. "ignite deals damage based on crit multi" from passive nodes).

### Damage Over Time vs Hit-Based

**Hit-based** skills: deal damage at the moment of hit. Trigger on-hit effects, leech, ailments, crit.

**DoT skills** (Ignite, Bleed, Poison, Caustic Arrow, Scorching Ray, etc.):
- Do **not** trigger on-hit effects, leech (unless specifically granted), or stacking crits.
- Scale with: "increased/more X damage over time", "increased/more burning/bleeding/poisoning damage".
- "Increased damage" without a qualifier applies to hits **and** DoTs.
- Ignite damage is based on the hit that caused it (or crit multi, if the build stacks it via nodes).
- Poison scales with the base physical + chaos damage of the hit. Bleed scales with physical.

### Defense Layers — Don't Recommend Single-Layer Defense

A well-rounded character needs multiple layers:
1. **Life / ES / Mana (Mana before Life / EB+MoM)** — primary buffer
2. **Armor** — reduces physical hit damage (especially effective vs small hits; less vs large)
3. **Evasion** — chance to avoid hits entirely (pairs with Acrobatics)
4. **Resistances** — elemental and chaos cap; always check all four are capped
5. **Block** — chance to block attacks/spells (Shield / block passives)
6. **Fortify** — 20% less hit damage taken while active
7. **Endurance charges** — physical reduction + all-res per charge
8. **Flasks** — Granite (armor), Jade (evasion), Topaz/Ruby/Sapphire (resistance), Basalt, Quartz
9. **Recovery** — life regen, life on hit, leech rate
10. **Ailment immunity** — freeze/shock/ignite immunity are often flask-based

Never recommend stacking only one layer. Check what the build lacks before suggesting offense upgrades.

### Aura Reservation

- Auras reserve mana (or ES with Arcane Surge/Watcher's Eye or ES reservation gear).
- Default reservation: Determination/Grace/Hatred/Haste = 50% mana; Purity = 35%; Herald = 25%; Aspect skills = 25%; Enlighten reduces reservation.
- Enlighten (level 3/4) on an aura setup is a significant investment — check if the build actually needs it.
- Mana reservation efficiency from tree/gear stacks additively to reduce cost.

### Corruption

Corrupting an item (Vaal Orb) applies one of several effects and makes the item **unmodifiable** afterward (no crafting bench, no orbs except Awakener's Orb on influenced items):
- **Implicit mod replaced or augmented**: the most common and valuable outcome. Items can gain a second implicit or have their existing implicit replaced with a corruption-specific one (e.g. +1 to level of socketed gems, +2 to socketed AoE/Projectile/etc. gems, culling strike, blind on hit, life gained on kill).
- **Sockets/links changed**: random resocket or relink.
- **Quality converted to experience**: item quality is removed, converted to gem experience (if applicable) or wasted.
- **Nothing**: no change.

**Key points for advising:**
- A corrupted item with a valuable implicit (e.g. "+1 to socketed gems" on a 6-link body armor) is often dramatically more valuable than the base item.
- When evaluating an item slot, always check if a corruption implicit would be a significant upgrade — sometimes a corrupted version of an item is the real bis.
- Gems can also be corrupted: can gain a level beyond 20 (level 21), quality beyond 20 (up to 23%), or a Vaal version implicit. 21/20 gems are the gold standard for key active skills.
- Corrupted gems with alternate quality (Anomalous/Divergent/Phantasmal) can also be corrupted for extra level/quality.
- Double-corrupt (Tempered by War/Suffering/Misery in the temple) applies two corruption outcomes — very high variance, can brick or greatly enhance an item.

### Item Affixes — Prefixes and Suffixes

Rare items can have up to **3 prefixes** and **3 suffixes** (6 explicit mods total). Magic items have 1 prefix + 1 suffix max.

**Prefixes** (generally): Life, Armour, Energy Shield, Evasion, Mana, flat added damage (to attacks or spells), resistances on some bases, physical damage on weapons, % increased physical damage on weapons.

**Suffixes** (generally): Accuracy Rating, Action/Attack/Cast Speed, Resistances (fire/cold/lightning/chaos), Attributes (Str/Dex/Int), % increased Damage (elemental or type), Critical Strike Chance/Multiplier, Flask modifiers, Mana regeneration, Movement Speed (boots).

**Practical notes:**
- When a build needs accuracy (e.g. Precise Technique), accuracy is a **suffix** — it competes with resistances and attributes for suffix slots.
- Life is a **prefix** — doesn't compete with resistances for slot space.
- Each item base type has its own mod pool with different available mods and weightings. Not every mod is available on every base.
- **Influenced items** (Shaper, Elder, Crusader, Redeemer, Hunter, Warlord) have additional exclusive mod pools — often the strongest possible mods for a slot, but only available on that influence type.
- When crafting, check which affixes are already allocated (prefix vs suffix) before choosing a bench craft, since the bench can only fill open slots of the correct type.
- A "full" item (3 prefixes + 3 suffixes) cannot be crafted further without using an Orb of Annulment to remove a mod first.

### Cluster Jewels — Sockets and Sizing

**Socket counts (non-unique clusters):**
- **Large** cluster jewels: always **2 jewel sockets** (for medium clusters)
- **Medium** cluster jewels: always **1 jewel socket** (for small clusters)
- **Small** cluster jewels: no jewel sockets

**Passive count and sizing preferences:**

*Large clusters:*
- **8 passives** — preferred when the small passives on the cluster are weak relative to what the passive tree offers nearby. Fewer smalls to path through, lower cost to reach both notables.
- **12 passives** — preferred when the cluster's small passives are stronger than what the tree would otherwise provide. More smalls allocated, but each small is high value (e.g. 10%+ attack damage per small).
- Avoid 10-passive larges — worst of both worlds.

*Medium clusters:*
- **4 or 5 passives** — standard. Minimises small passives pathed through while still reaching both notables.

*Small clusters:*
- **2 passives** — always preferred. One notable + one small; minimal passive investment, direct access to the notable.

**Evaluating a large cluster:**
1. Check both notables — are they best-in-slot for the build, or just filler?
2. Check the small passive enchant — "10% increased Attack Damage" per small is very strong; "2% increased Damage" is filler.
3. With strong smalls → prefer 12P. With weak smalls → prefer 8P.
4. The jewel enchant (e.g. "12% increased Physical Damage") is a fixed bonus regardless of passives — factor it in but it's not the primary evaluation criterion.

### Local vs Global Modifiers

A modifier is **local** if it meets any of these criteria:

1. **Modifies the item's own base stats** — e.g., `#% increased Physical Damage` or `Adds # to # Physical Damage` on a weapon changes the weapon's own Physical Damage and APS values shown in the tooltip (displayed in blue). That enhanced value then flows into the character's total. Local flat damage on a weapon scales with the weapon's local increased physical damage and quality. Local mods are visible as the blue numbers on the item.

2. **Hand-specific** — mods containing "with this Weapon", "Main Hand", or "Off Hand" are treated as local (technically global but scoped to one hand). These **cannot** be scaled by other local modifiers.

3. **Weapon hit effect** — stats that trigger on any attack hit with a generic weapon: `#% Chance to Poison on Hit`, `#% Chance to Maim`, `#% of Physical Attack Damage Leeched as Life`, flat Accuracy. Note: Ignite chance is always **global** because weapons have no base fire damage.

**Global** = everything else. All conditional mods (e.g., "while you have a buff", "against bleeding enemies") are global except the hand-specific ones above. Global mods apply to the character's stats, not the item's base stats.

**Critical practical difference:**
- `Adds 10–20 Physical Damage` on a **weapon** → local. It increases the weapon's base damage, which is then multiplied by the weapon's local `% increased Physical Damage` and quality. Very strong.
- `Adds 10–20 Physical Damage to Attacks` on a **ring** → global. It is added to the character's total attack damage pool *after* the weapon's local calculation, and is only scaled by global increased/more modifiers.

**Hybrid modifiers** (two lines on one mod, e.g., Incursion architect mods) treat each line independently — one line can be local and the other global.

---

### League-Specific Advice
- **League changes significantly affect meta, balance, and item availability.** Check the wiki or patch notes for current league changes before recommending items or builds.
- Current league: **Mirage** (Sony/PlayStation realm)
- **No price data exists for PlayStation** — do not reference prices from any tool or site.
- **Originator map petal skills removed in 3.28** — Prior to Mirage, Originator-influenced maps had 8 manually-activated memory petal skills (Memory of Desire, Memory of Panic, etc.) accessible via the skill bar (L2+R2 on controller). These were removed entirely in 3.28. Petals now passively increase the chance for dropped items to have Memory Strands. Active decision-making moved to Memory Altars at the end of each map boss in a Memory Thread — these apply modifiers automatically, some consuming petals automatically under conditions. If a player reports the L2+R2 memory skill option missing, this is intentional, not a bug.
- **Borrowed power mechanics** — each league introduces temporary mechanics that do not carry to Standard or future leagues. Mirage example: Coin of Power/Knowledge/Skill gem imbuement. When advising on whether to invest in a borrowed power mechanic, factor in that it disappears at league end. Also note that random-pool borrowed power mechanics (like gem imbuement) typically have poor hit rates for any specific build — selling the currency is always better EV than self-use.
- Items, gem levels, and passive tree may be buffed/nerfed each league - always verify current state via wiki before advising.

### League Stage Priorities

#### Early League / League Start (first 1-2 weeks)
Do NOT recommend:
- Forbidden Flame / Forbidden Flesh jewels (extremely rare, expensive early)
- Awakened support gems (not available early, cost dozens of divines)
- 21/20 gems (require 23 quality gems + corruption, very expensive)
- Mirror-tier or high-end crafted items
- Headhunter, Mageblood, or other chase uniques

DO recommend:
- Self-craft or cheap rares
- Normal 20/20 gems (or even 20/0)
- Budget unique alternatives
- Core build uniques that drop commonly
- Cluster jewels with basic notables
- Focus on survivability before damage optimization

#### Mid League (2-6 weeks)
- Awakened gems exist but are still costly — only recommend if player has surplus currency
- Forbidden jewels exist but are expensive — only recommend if budget allows
- 20/20 gems are standard; 21/20 may be achievable for key gems
- Divine orbs are the main currency benchmark (but no exact price data available for PS)

#### Late League / Endgame Pushing
- Full optimization: awakened gems, 21/20 on key gems, forbidden jewels
- Mirror crafts for bis slots
- Six-link +1 gems weapons, etc.

### General Advice
- **Do NOT use price_check or currency_overview MCP tools.** PlayStation (Sony) has no public price data sources — poe.ninja and similar sites do not index the PS market. Price estimates are meaningless and should not be presented.
- When discussing item costs, speak in relative terms only: "this is a chase item and will be expensive", "this drops commonly and should be cheap", "this requires a divine orb craft" — not specific chaos/divine values.
- When suggesting upgrades, order by: impact on build (damage, survivability, QoL) weighted by expected availability.
- For gem recommendations: check if corrupted implicit matters for the build
- Mastery choices: verify they work with the build mechanic before suggesting
- Always check if a unique's mods are still relevant after potential nerfs

## Files
- MCP config: `.mcp.json`
- POEMCP server: `POEMCP/server.py`
- POB importer: `pob/PathOfBuilding-2.59.2/tools/mcp_server.py`
- POB importer CLI: `pob/PathOfBuilding-2.59.2/tools/import_character_cli.lua`
- Build expander: `build_expander.py`
- Expanded builds: `<CharName>_YYYYMMDDHHMM_expanded.json`
