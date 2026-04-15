# Static Strike Life-Stacker — Chieftain (Mirage League)

**Character:** MiragMaraBatato | **Level:** 98 | **Realm:** Sony (PlayStation)

## Origin

Based on [Peuget2's Apostate life-stacker Smite Chieftain](https://mobalytics.gg/poe/builds/life-stacking-smite-chieftain). The original template requires extremely high life (corrupted life implicits on uniques, mirror-tier gear) so that sheer HP pool + Defiance of Destiny compensates for the lack of traditional defence layers. We don't have the budget for life-corrupted uniques, and several key items from the original don't exist on the PlayStation market.

## Divergences from Peuget2's Template

### Defence — Royal Plate instead of Apostate
- **Royal Plate body armour** instead of **Apostate** chest — Apostate requires life-corrupted uniques to push HP high enough to compensate for its lack of defences. Without that budget, a rare Royal Plate provides armour + Fortify from mastery
- No-life chest planned (see crafting.md) to activate **15% increased maximum Life mastery** — the life-stacking payoff without needing corrupted uniques

### No Enmity's Embrace — Different Damage Paradigm
The original build revolves around **Enmity's Embrace** ring: stacking fire resistance → fire penetration. Peuget2 claims ~40% more damage from this ring alone, with the entire gearing strategy warped around fire res on every suffix. He uses **Elegant Hubris** (8 chaos on PC) to convert two passive nodes to 50% fire res each, gaining ~20% more damage through the Enmity's Embrace penetration loop.

**Why we skip it:**
- Enmity's Embrace cuts 3/4 of your fire res — requires massive fire res overcapping on every gear slot to stay survivable
- Forces **Purity of Elements** aura (35% reservation) to cap other resistances, since all suffixes go to fire res
- **Elegant Hubris with the right seed doesn't exist on PlayStation market** — the specific timeless jewel that converts nodes to fire res is unavailable
- Awakened gems (Ele Focus, EDwA) also don't exist on PS — not expensive, literally zero supply

**What we gain by skipping Enmity's Embrace:**
- Free aura slots: **Skitterbots** (shock = increased damage taken), **Arctic Armour** (phys/fire damage reduction), **Precision** (accuracy + crit for EO uptime)
- Simpler gearing — suffixes can have mixed resistances, chaos res, attributes
- Three utility auras replace one damage ring + one defensive aura

### Curse Setup
- **Flammability on Hit** ring suffix + **Whispers of Doom** belt anoint for double curse (Flammability + Mark)
- **Flammability** — 15% fire exposure (meaningful upgrade over axe baseline 10%)

### Mark Analysis
Marks applied via Mark on Hit support. Mark mastery provides 10% chance to gain frenzy charge on hit against marked enemy (primary frenzy source during bossing).

| Mark | Assessment |
|------|-----------|
| **Assassin's Mark** | Current. Culling strike + life/mana on kill. Power charges and crit wasted (EO self-sustains, no crit scaling). On-kill useless for boss sustain. |
| **Warlord's Mark** | Life leech overcapped, endurance charges redundant (Enduring Cry), rage on stun unreliable. |
| **Poacher's Mark** | **Best overall.** Life + mana on hit procs continuously during boss fights at high hit rate (Greater Multistrike + Ancestral Call). Frenzy on kill backs up mastery 10% for reliable frenzy capping during clear. Flat phys converts to fire via AoF (minor). -20% phys reduction dead (fire build). |
| **Alchemist's Mark** | Dead. No ignite (Elemental Focus), no poison. |
| **Sniper's Mark** | Projectiles only, irrelevant. |

**Recommendation: Poacher's Mark.** Switch to Assassin's if culling strike threshold matters for specific boss.

### Pathing & Split Personalities
- Long winding passive tree path to maximise **two Split Personalities** (life+str and life+acc to catch up on hit chance)
- The winding path also passes through many small nodes in Lethal Pride radius, each gaining +5 Str

### Mana Solution
- 8-link (Ancestral Call from acendancy + 5 actual supports + imbue on gem) creates high mana cost
- **-7 to non-channelling mana cost** craft on ring prefix solves this (if not using multistrike to have several its for same mana cost, then on both rings)

## The Damage Engine

Damage layering is **multiplicative between layers**, not additive:

```
Flat/Added  ×  Increased  ×  More multipliers  ×  Overlaps  ×  Enemy res reduction  ×  More taken
```

### Layer 1 — Flat Damage (scales with life)
- **Grey Wind** sword: adds flat fire damage equal to **12% of maximum life**
- With 11k+ life, this is ~1,320 flat fire added to attacks
- Life scaling feeds this layer directly

### Layer 2 — Increased Damage (scales with life via Str)
- **Iron Will** (Strength → spell damage)
- **Crown of Eyes** helmet: spell damage applies to attacks at **150%** value
- **Rathpith Globe** shield: spell damage per 100 maximum life
- Life → Str (Split Personality, tree) → spell damage → attack damage at 1.5x
- Life → Rathpith flat bonus → spell damage → attack damage at 1.5x
- **Result:** life double-dips across two multiplicative layers (flat AND increased)

### Layer 3 — More Multipliers
- **Elemental Overload** (from Xoph's Blood amulet): 40% more elemental damage when crit recently, no crit multiplier
- **Crit is irrelevant** beyond activating EO — EO has no crit multiplier, and Assassin's Mark is for mark effects (frenzy on hit, culling strike) and EO uptime, not crit scaling
- **Elemental Focus** prevents ignite, so crit-based ignite damage is irrelevant regardless
- Support gems: Greater Multistrike, Elemental Focus, Inspiration, Elemental Damage with Attacks, Cruelty (imbued)
- **Lethal Pride 10740 Kaom** at node 54127: 2x 5% chance to deal double damage on allocated notables (Golem's Blood + Master of the Arena) — effectively ~10% more DPS

### Layer 4 — Enemy Debuffs
- **Flammability** curse (on hit from ring): 15% fire exposure — meaningful upgrade over the axe exposure (10%)
- **Assassin's Mark**: culling strike (10% more effective life damage)
- Frenzy charges from Mark mastery: 4% more damage per charge
- **Summon Skitterbots**: shock nearby enemies (increased damage taken)

## Main Skill: Static Strike (Cruelty Imbued)

### Why Static Strike on Controller
- **Beams persist for 4 seconds** while dodging/repositioning
- Other skills (Smite of DJ, Wild Strike) deal zero damage during movement
- Effective DPS ≈ paper DPS for Static Strike; alternatives lose 30-50% to dodge windows
- **Saresh target dummy confirmed:** Static Strike quarter-life 10s vs Smite DJ 15s despite lower paper DPS

### Beam Mechanics
- Fixed **0.32s frequency** — attack speed does NOT affect beam tick rate
- **6 max targets** per beam set
- Beams are **melee attacks** but NOT melee strikes
- **+1 chain** baseline on beams
- Ancestral Call (free from Tukohama ascendancy) — **unclear if phantom strikes generate independent beam sets.** Wiki says beam damage is "considered damage from the attack that granted static energy" but doesn't address whether each Ancestral Call strike grants its own energy/beams. Saresh testing suggests some contribution but unverified. [unverified 2026-03]

### Links (Body Armour, 7L + Tukohama)
Static Strike (Ruthless imbue) + Close Combat + Greater Multistrike + Inspiration + **[Greater Chain / Hypothermia]** + Elemental Damage with Attacks + Ancestral Call (free from Tukohama)

**Imbue:** Ruthless instead of Cruelty — Close Combat replaces Elemental Focus for melee-specific scaling.

### Build Milestones

**Simulacrum:** Current build state clears all waves with 3 portals remaining.
- Build file: `builds_arc/MiragMaraBatato_simulacrum_expanded.json`

**Green socket swap (same socket, two options):**
- **Mapping:** Greater Chain — beams chain 3x, packs clear while moving
- **Bossing:** Hypothermia — 30% more damage against chilled enemies (Skitterbots permanently chill the boss), applies to both hit AND beams. Faster Attacks only boosts hit speed and does nothing for beam frequency, so Hypothermia is strictly better for bossing.

**Greater Chain and Beyond:** Greater Chain's longer range is counterproductive for Beyond density farming. Beyond portals spawn when monsters die clustered near each other — longer chain range spreads kills across a wider area, reducing clustering and therefore fewer Beyond portals. For maximum Beyond density, use Faster Attacks (shorter-range beams, deaths stay clustered). Greater Chain makes Beyond manageable but actively reduces Beyond spawn rate.

### Support Gem Paths

Static Strike has two viable support gem paths that fundamentally change its scaling direction:

**Greater Multistrike path** — hit-heavy. Attack speed directly increases hit rate, beams trigger more frequently from faster attacks. Better for single-target focused builds with high attack speed.

**Void Shockwave path** — beam-heavy. Shockwave adds AoE wave damage that chains from hit enemies, and waves repeat from nearby enemies. Attack speed does NOT affect beam frequency or shockwave cooldown — convert attack speed sources to flat damage instead. Potential for ignite build-around (WIP — PoB shows small contribution, supposedly working without large hits and Grey Wind DoT mod).

Void Shockwave is comparable in DPS to Greater Multistrike on paper and against static bosses, but is more sluggish and beam-focused. It works best with Static Strike only.

### Skill Swap Framework

The engine (Grey Wind + Rathpith + Crown of Eyes + life stacking) is **skill-agnostic** — any strike skill benefits from the same links and scaling. Gem swap only, no regearing needed.

Path column: **MS** = Greater Multistrike path, **VS** = Void Shockwave path

| Content | Skill | Path | Why |
|---------|-------|------|-----|
| **Easy mapping** | Static Strike + Greater Chain | MS | Beams chain 3x, clears packs while moving. Note: longer range reduces Beyond spawn clustering. |
| **Hard bossing** | Static Strike + Hypothermia | MS | 30% more damage on chilled enemies (Skitterbots permanently chill the boss), applies to both hit AND beams. Faster Attacks only boosts hit speed and does nothing for beam frequency, so Hypothermia is strictly better for bossing. |
| **Easy mapping (Shockwave path)** | Static Strike + Shockwave | VS | Shockwave adds AoE clear, beams handle single-target. More beam-heavy than Multistrike. |
| **Beyond / density farming** | Infernal Blow | MS/VS | On-death explosions chain through packs and cluster kills for Beyond portal spawning. Best clear skill in the kit. |
| **Loaded Blights / 50+ simultaneous mobs** | Smite of Divine Judgement | MS/VS | Static beams cap at **24 simultaneous hits per 0.32s tick** (6 beams × 4 targets with 3 chains). Above this density Smite's unlimited area scales better. |
| **Mid-tier face-tank** | Smite of Divine Judgement | MS/VS | 6.37m PoB DPS (2.46m hit + 3.76m area + cull). Stand still, full DPS, no positioning required. |

**PoB numbers (corrected, Cruelty imbue disabled for fair comparison):** Smite 6.37m (2.46m hit + 3.76m area, with cull) vs Static Strike 4.76m (2.76m hit + 1.23m beams, with cull). Smite is 34% higher on paper.

**PoB vs reality:** Smite's 6.37m beats Static Strike's 4.76m on paper (34% gap), but Saresh target dummy tests tell a different story: measuring health bar progress over time, Static Strike dealt ~12% more effective DPS than Smite despite lower PoB numbers. Earlier test (2026-03-25): quarter-life 10s Static vs 15s Smite. Likely explained by Ancestral Call generating independent beam sets that PoB doesn't model.

### Other Skill Tests
- **Wild Strike** — tested on Saresh, inconsistent (13s vs 21s quarter-life). Zero imbued versions on PS market. Nobody plays it.
- **Static Strike of Gathering Lightning** — broken interaction with Greater Multistrike (repeats don't count as individual melee hits for stacking, stuck at 5-6 stacks instead of 12)

## League-New Mechanics Used

### Imbued Skills (Mirage League)
- Static Strike imbued with **Cruelty** — the imbue is a property on the gem itself, not a separate link
- Cruelty imbue provides a "more" damage multiplier (level 1 = ~15% more from PoB)
- Imbued gem shows as 20/20 even if you have a 21/20 base — imbued is more damage regardless
- Imbue is why mana cost is so high (level 1 Cruelty still adds 140% cost multiplier) → needs -7 mana cost craft

### Greater Multistrike (new)
- Superior to old Multistrike for this build
- **Caveat:** breaks Gathering Lightning stacking (repeats don't count as individual hits)

### Improved Static Strike (3.26 patch)
- Base damage effectiveness buffed this patch
- 21/20 base has 360.7% of base damage

## Ascendancy — Chieftain

### Tasalio, Cleansing Water
- Fire res modifiers also apply to cold/lightning at 50% of their value
- Unaffected by Ignite
- **Why:** Core Chieftain node. Fire res stacking from gear passively caps cold/lightning. Ignite immunity is a free defensive layer.

### Valako, Storm's Embrace
- Modifiers to maximum fire res also apply to maximum cold and lightning res
- **Why:** Pairs with Tasalio. Barbarism's +1% max fire res becomes +1% to all max res. Ruby flask's max fire bonus extends to all elements. Pushes effective max res across the board.

### Tukohama, War's Herald
- Body armour skills supported by level 30 Ancestral Call (strikes) or level 20 Fist of War (slams)
- Node serves whichever skill type is equipped — not half-wasted
- **Why:** Level 30 Ancestral Call grants **10% more damage** unconditionally, plus extra strike targets for clearing. The 10% more alone justifies the node.
- **Levelling note:** During the Shield Crush phase (see [shield_crush_impale.md](/Users/a/code/games/poe/builds/shield_crush_impale.md)), Shield Crush is neither a strike nor a slam, so Tukohama's supports don't activate. **Ngamahu** was used instead for +4 Str per non-unique jewel in radius. Swapped to Tukohama when transitioning to Static Strike.
- **vs Ngamahu:** Ngamahu gives +4 Str per non-unique jewel in radius (+161 Str total, 711→872), but Lethal Pride already occupies the high-density pathing socket and Red Dream takes another, leaving only 4 sockets with mostly pathing nodes. Net result: Ngamahu gives ~3% more life (11,286→11,630) but loses the 10% more damage. Tukohama wins on damage.
- **Ancestral Call beam interaction:** unclear if phantom strikes generate independent beam sets — wiki doesn't address it, Saresh testing was suggestive but not conclusive. [unverified 2026-03]

### Sione, Sun's Roar
- Warcries have infinite Power + 30% increased Warcry Buff Effect
- **Why:** Enduring Cry is the only warcry. Infinite power guarantees full endurance charges per cry + maximum life regen from the buff. 30% buff effect further boosts the regen. Net regen with Sione: ~1,975/sec; without: ~1,343/sec. The 632 life/sec difference is not tradeable.
- **vs Hinekora, Death's Fury:** Hinekora gives 10% chance for enemies to explode (250% max life as fire damage) — strong clear speed, but beams + Chain Support already clear well. Losing 632 life/sec regen is too costly for marginal clear improvement.

## Tincture

**Increased Elemental Damage with Melee Weapons** tincture — applies to both the initial hit AND beams (beams count as melee weapon damage). Very noticeable damage boost. Sustain the tincture duration through boss fights for maximum uptime. This is shared with the original Peuget2 build.

## Key Unique Items

| Item | Role |
|------|------|
| **Grey Wind** (axe) | Flat fire = 12% max life — the engine's core |
| **Crown of Eyes** (helmet) | Spell damage → attack damage at 150% |
| **Rathpith Globe** (shield) | Spell damage per 100 life |
| **Foulborn Xoph's Blood** (amulet) | Elemental Overload (double foulborn with phys as fire nice but not crucial) |

## Jewels

| Jewel | Socket | Purpose |
|-------|--------|---------|
| **Split Personality** (life+str) ×2 | End of long paths | Life + Str scaling, maximised by winding pathing |
| **Lethal Pride 10740 Kaom** | Node 54127 (next to Savagery) | 2x 5% double damage on Golem's Blood + Master of the Arena; +5 Str on small nodes in radius |
| **Red Dream (Foulborn)** | Near Barbarism | Max life for fire res + all-ele res in radius |
| Rare jewel (corrupted blood immunity) | — | 7% max life, 8 all attributes, 8% attack speed with axes |

**Note:** Dex on rare jewels is required to cap Dex for gem requirements. All attributes jewel solves Int requirement for Crown of Eyes + Rathpith after Split Personality swap from life+int to life+str.


## Other Gem Links

### Gloves — Enduring Cry
**Current: Enduring Cry (imbued Blessed Call L1) + More Duration + Urgent Orders + CDR Support**

- Enduring Cry creates consecrated ground on every use — **+670 life/sec regen** (boosted by Devotion: 25% increased effect of consecrated ground you create)
- Blessed Call adds 20% reduced Cooldown Recovery Rate, but CDR Support cancels this entirely
- Urgent Orders at level 20 + CDR Support = large safety overlap on uptime. Without CDR, uptime is exact (no buffer)
- More Duration extends consecrated ground duration beyond Blessed Call's base 4.1s

**Next league (no imbued mechanic): default 4-link**
- Urgent Orders + Blessed Call + More Duration (default trio)
- Upgrade More Duration → CDR Support if budget allows and you want 100% Enduring Cry uptime
- Note: Blessed Call value depends on playstyle — if you move around constantly (e.g. Static Strike mapping), consecrated ground uptime is low and Blessed Call is less useful

## CwDT Slot (Shield)

**Current: Vaal Molten Shell L? + WoC L14 + CwDT L11**

Withering Step is dead weight — CwDT triggers on damage taken, but Withering Step wants to be used proactively and can't be cast while already Elusive.

**Best: Wave of Conviction** — 15% fire exposure via CwDT is irreplacable. Axe only provides 10% baseline exposure. Frost Bomb kept in inventory for swap-in against regen enemies (Uber Lab, map mods).

## Grey Wind Enchant (2026-04-03)

Upgraded to uncorrupted Grey Wind with **12% life conversion + +5 rage** (from 8% + 0 rage base).

**Key weapon stat:** "Added Fire Damage equal to 12% of Player's Maximum Life" — this is ~600 flat fire at 5k life. The physical base (29-48) is negligible. The weapon's entire value is the life-as-fire scaling.

**Enchant options:**
- **AOE** — best option. Increases beam range (better reach before chaining), easier beam overlap while dodging, also applies to Smite and Infernal Blow swaps. No other AOE scaling in the build.
- **Attack speed** — PoB shows highest gain but only affects melee strike, not beams
- **Strike range** — PoB can't calculate this

**Decision: AOE enchant.** Improves beams, Smite, and Infernal Blow. Best all-around choice.

## Crafting Projects

### No-Life Royal Plate — Rejected
Originally planned to use a no-life chest to activate the **15% increased maximum Life** mastery. Tested and rejected: the 15% more max life (11,148 final) is less than the current flat life (11,489 final). The third prefix slot has no meaningful upgrade to compensate. Keep the current armour.

See [crafting.md](crafting.md) for other projects.

## Flexible Slots

### Hunter Belt
The Hunter base gives **+2% to all Attributes** as an implicit, strong value per slot. When bench-crafting:
- **% attributes > % increased life.** Life adds to an already large increased% pool (heavy diminishing returns). Attributes help all three stats (str for damage/life, int for gems, dex for accuracy) and benefit from the Hunter implicit's more-efficient attribute scaling.
- % attributes is rarer than % increased life (weight 1000 / 70,750 vs weight 1000 / 54,300) — harder to hit on bench but more valuable.

### Rings
Rings carry
- Int
- Chaos res
- Life
- Str
- Fire res
- Two -7 mana cost crafted prefixes
Middle endgame vermillion and amethyst - both fractured, one life, other flammability on hit (first, get flammability on good base, then try to fracture it)
Make sure +1 curse is coming from somewhere (Whispers of Doom anoint is simplest), so flammability and mark both would work

## Endgame Mistakes

### Build-specific

- **+2 max fire res on rings is wasted** if max fire res is 85 without them. Ruby flask carries the remaining 5 res via its "gains max fire res" mod — no need to overcap on gear.
- **Assassin's Mark vs Poacher's Mark:** Assassin's is life on kill (useless in boss fights), Poacher's is life on hit (procs continuously at high hit rate). Poacher is strictly better for sustained boss damage.
- **Having rage ramp too slow** - it's inherently limited to 1 rage per source in 0.5 seconds, so need more gain rage on hit - glove exarch implicit, lethal pride potentially, but best - Bloodscent node on axe/sword large cluster is the best, with 2  points from tree it brings to 4 total and 8 per second, whihc is good. Another alternative - rage on warcry on mastery instead of intimidation on max rage, can be considered if using indimidating cry instead, but cluster + indimidate on max is better because of easier uptime.

### General minmaxxing mistakes (from actual experience)
- **Not applying sacred orbs to armor** - check if all done
- **Not using lvl 4 exceptional gems** when have funds already
