# Static Strike Life-Stacker — Chieftain (Mirage League)

**Character:** MiragMaraBatato | **Level:** 98 | **Realm:** Sony (PlayStation)

***

# 1. Core Concept

This is a life-stacking Chieftain built around Static Strike, where **life is not just your HP pool — it simultaneously scales your flat damage output and your percentage damage multipliers**. Every point of maximum life makes you both tankier and hits harder, across two independent multiplicative damage layers at once. This double-scaling relationship is the entire reason the build works.

## Why Chieftain

Chieftain provides four things no other class matches simultaneously:

- **Tasalio + Valako**: Fire resistance modifiers apply to cold and lightning at 50% value, and maximum fire res modifiers propagate to all elements. Cap fire res once and all three elements cap together.
- **Sione**: Warcries have infinite power. Enduring Cry always grants full endurance charges and maximum regen — no power stacks to manage.
- **Tukohama**: Body armour strike skills are supported by a free Level 30 Ancestral Call, effectively giving the main skill a 7th link that also provides 10% more damage unconditionally.
- **Ignite immunity** (from Tasalio): A free defensive layer at no cost.

## The Life-Scaling Engine

Life feeds damage in two distinct ways that multiply against each other:

**Layer 1 — Flat damage (direct life scaling):**
*The Grey Wind* axe adds flat fire damage equal to **12% of maximum life** to every attack. At ~11,000 life this is roughly 1,320 flat fire added to each hit — completely dwarfing the weapon's physical base damage. More life = more flat damage, immediately and directly.

**Layer 2 — Increased damage (life + Str → spell damage → attack damage):**
- *Iron Will* keystone converts Strength's damage bonus to Spell Damage
- *Crown of Eyes* helmet makes all increased/reduced Spell Damage apply to Attacks at **150% of its value**
- *Rathpith Globe* shield grants **5% increased Spell Damage per 100 maximum life**
- Strength comes from the passive tree, Split Personalities, and gear — and Strength itself scales with life through Split Personality jewels

The result: life feeds Strength, Strength feeds Spell Damage via Iron Will, and Spell Damage feeds Attack Damage at 1.5× via Crown of Eyes. Life also feeds Rathpith's bonus directly. Both paths converge on the same Crown of Eyes multiplier.

**Why this matters:** these two layers are multiplicative with each other. A 10% life increase doesn't give you 10% more damage — it increases flat damage *and* increases percentage modifiers *simultaneously*, compounding across both layers. This is what "life-stacking" actually means in this build.

## Mandatory Uniques

| Item | Slot | Key Stat |
|------|------|----------|
| **The Grey Wind** | Weapon (Spectral Axe) | Added fire = 12% max life; +5 max Rage; Fire Exposure at max Rage |
| **Crown of Eyes** | Helmet (Hubris Circlet) | Spell Damage → Attack Damage at 150%; −30 fire res penalty |
| **Rathpith Globe** | Shield (Titanium Spirit Shield) | 5% increased Spell Damage per 100 max life |
| **Xoph's Blood (Foulborn)** | Amulet (Amber) | Mutated: Elemental Overload + 6% Phys taken as Fire; Penetrates 10% Fire Res |

## The Amulet — Foulborn Xoph's Blood

The amulet has **mutated modifiers** — a Keepers league mechanic that stayed core. Our version grants **Elemental Overload** (40% more elemental damage when you crit recently) and **6% of Physical Damage from Hits taken as Fire Damage**. It also removes Avatar of Fire, so we are no longer restricted to dealing only fire damage, which allows non-fire added damage sources (cold from rings, etc.) to function, and more importantly allows the Foulborn Red Dream jewel's **8% of Fire Damage as Extra Chaos Damage** to actually deal damage instead of being deleted by the engine.

# 2. Platform & Market Conditions

This build was developed on the **PlayStation / Sony realm** in Mirage league. The PS market is fundamentally thinner than PC — items that are cheap or plentiful on PC can have literally zero supply on PS. Several decisions that look suboptimal compared to the PC meta are direct consequences of this constraint.

## Ruled Out by PS Market Availability

**Elegant Hubris (correct seed):** The original Peuget2 template this build is based on revolves around *Enmity's Embrace* — stacking massive fire resistance on every gear slot, then converting that overcapped fire res into fire penetration. The mechanism requires a specific *Elegant Hubris* seed that converts nearby passive nodes into 50% fire resistance each, providing ~20% more damage through the penetration loop alone. That specific jewel seed **does not exist on the PlayStation market**. Not expensive — simply unavailable.

**Awakened support gems:** Awakened Elemental Focus and Awakened Elemental Damage with Attacks have zero supply on PS. Again, not a budget issue — they don't exist in the market.

**Mirror-tier corrupted life implicits on uniques:** The Peuget2 template requires corrupted life implicits on uniques to push HP high enough that sheer pool size + Defiance of Destiny compensates for running *Apostate* chest with no traditional defences. Achieving that life total without corrupted implicits is not realistic on PS.

## What We Gain by Skipping Enmity's Embrace

Skipping the Enmity's Embrace loop entirely is not purely a loss. The original build must run **Purity of Elements** (35% reservation) to cap non-fire resistances, since every suffix on every piece of gear must go to fire res for the loop to function. By abandoning the loop we free those aura slots entirely:

- **Skitterbots** — permanent Shock (increased damage taken) and permanent Chill on nearby enemies, enabling Hypothermia for bossing
- **Arctic Armour** — 21% less physical and fire damage taken while stationary
- **Precision** — accuracy for hit chance + critical strike for Elemental Overload uptime

Three utility auras replace one damage ring plus one defensive aura. Gearing becomes simpler — suffixes can carry mixed resistances, chaos res, and attributes instead of being entirely devoted to fire res.

## The Apostate Decision

The original template uses an *Apostate* body armour. We have one in stash, six-linked and coloured — this is not a "can't afford it" situation. We chose not to use it.

Apostate's defensive value is zero on its own. The entire survival model in Peuget2's version is: push life high enough that raw HP + Defiance of Destiny absorbs what Apostate doesn't mitigate. On PC with corrupted life implicits on uniques and mirror-tier gear everywhere, you can reach the life threshold where this works. On PS without those implicits and with our actual budget, you cannot — the life total simply isn't achievable.

A rare **Royal Plate** solves this: high armour base, Fortify from chest implicit, and all three prefixes available for life and stats. Our current chest is exceptionally well-rolled (see Section 3b), but even a modest Royal Plate outperforms Apostate at any realistic PS budget by keeping you alive in the first place.

If you are building this on PC with mirror-tier life-corrupted uniques and the correct Elegant Hubris seed, the Apostate + Enmity's Embrace route is strictly better. That build is Peuget2's, not this one. One final note though: the 3.26 patch buffed Static Strike's base damage effectiveness, and Void Shockwave was introduced as a new support in the same patch. Both changes disproportionately benefit this build's architecture. It is entirely possible that our approach — life-stacking Chieftain with Static Strike + Void Shockwave — is simply the stronger path in the current patch regardless of platform, and that the Apostate + Enmity's Embrace route on PC would itself benefit from adopting this same tech on top of its higher life ceiling.

***

# 3. Damage Multipliers & Tricks

Beyond the core life-scaling engine, damage is layered through several independent multipliers that are multiplicative with each other and with the engine itself. Each layer added multiplies everything before it.

```
Flat damage  ×  Increased%  ×  More multipliers  ×  Enemy debuffs  ×  Enemy res reduction
```

## Elemental Overload

Xoph's Blood (Foulborn) grants **Elemental Overload**: 40% more elemental damage whenever you have critically struck in the past 8 seconds. Crit itself is irrelevant beyond triggering EO — there is no crit multiplier scaling, and Elemental Focus prevents ignite anyway. Precision aura provides enough accuracy and base crit to maintain EO uptime permanently. Think of it as a sustained 40% more multiplier that costs nothing beyond the aura reservation.

## Rage Engine — Bloodscent is Load-Bearing

Rage is not a nice-to-have. It is a large damage multiplier in its own right, and two additional mechanics activate only at maximum Rage:

- **Rage Mastery**: nearby enemies are Intimidated while you have Rage (10% more damage taken)
- **Grey Wind Fire Exposure**: at maximum Rage, the axe applies Fire Exposure to nearby enemies — though Wave of Conviction's −15% exposure supersedes this, so the real value is the Intimidation and the Rage damage bonus itself

Rage ramp is capped by the game engine at one gain event per 0.5 seconds per source. To reach maximum Rage quickly enough to matter in boss fights:

- **Bloodscent** (Large Axe/Sword Cluster notable): +2 Rage on Hit with Axes or Swords — this is mandatory
- **2× Rage on Melee Hit** small nodes from the passive tree

Combined: 4 Rage per hit event, capped at 0.5s intervals = 8 Rage per second. Maximum Rage (~50) reached in roughly 6 seconds of combat. Without Bloodscent the ramp is too slow for either mechanic to be reliable in boss fights.

*Fuel the Fight* on the same cluster (mana leech + attack speed + 20% increased damage while leeching) is a solid bonus but not the reason you take the cluster.

## Lethal Pride 10740 (Kaom)

Socketed at node 54127 (adjacent to Savagery). Converts small passive nodes in radius to +5 Strength each (more life and damage via the engine), and grants **5% chance to deal double damage** on both the *Golem's Blood* and *Master of the Arena* notables — approximately **10% more DPS** as a combined multiplier.

## Skitterbots + Hypothermia

Skitterbots permanently Shock and Chill nearby enemies. Shock increases damage taken. Chill enables **Hypothermia Support** (30% more damage against chilled enemies) for bossing — this applies to both the initial hit *and* the Static Strike beams. The *Blight Ornament* Viridian jewel's 6% increased effect of non-damaging ailments implicit makes both Shock and Chill stronger.

## Double Curse

- **Flammability on Hit** (fractured ring suffix): automatically applies Flammability on every hit, lowering enemy fire resistance
- **Poacher's Mark** (via Mark on Hit Support): needed to enable Frenzy on hit and cull via Mark wheel on the tree. See Section 9b for full mark analysis

Double curse currently enabled by *Whispers of Doom* anoint on the Cord Belt (+1 curse limit). If Cord belts go away after 3.28, it would have to be on the amulet instead of Tenacity.

## Wave of Conviction (CwDT)

Auto-triggers on damage taken, applying −15% Fire Exposure. This is stronger than the axe's exposure and supersedes it. Exposures and curses (Flammability) stack additively with each other — WoC handles exposure, Flammability handles the curse layer, they are independent. Keep **Frost Bomb** in inventory for high-regen content (Uber Lab, regen map mods) where the cold exposure and regen reduction matter.

## Extra Chaos Damage — Foulborn Red Dream

The Foulborn Red Dream jewel (socketed near Barbarism) provides passives in radius that convert fire resistance nodes to maximum life, and its Foulborn implicit grants **8% of Fire Damage as Extra Chaos Damage**. Because our Xoph's Blood mutation *removed* Avatar of Fire, we deal non-fire damage types — this chaos component is not deleted by the engine and functions as a true ~8% more damage multiplier. This interaction only works because of the mutated amulet.

## Tincture

The Prismatic Tincture's implicit provides **140% increased Elemental Damage with Melee Weapons** — this applies to both the initial hit *and* Static Strike beams, since beams count as melee weapon damage. Very noticeable damage boost in all content. Prefix gives 140% by boosting effect at a cost of extra mana burn (which is compensated by mana leech). For suffix choice, see Section 3a.

## Blood Rage

Grants 15% attack speed and 1.2% of attack damage leeched as life. The degen is mitigated by endurance charges and the amulet's 6% phys-taken-as-fire conversion.

## Fortify & Onslaught

- **Fortify**: Royal Plate chest implicit grants 7% chance on Melee Hits to Fortify, maintaining near-permanent 20% damage reduction
- **Onslaught**: Flagellant's Silver Flask (auto-triggers at full charges) guarantees permanent 20% increased attack and movement speed in combat


# 3a. Tincture Suffix — Penetration vs Attack Speed

Two viable suffix options, with meaningfully different performance depending on context.

**Attack Speed**: Increases hit rate directly. Irrelevant for Void Shockwave triggers, affects only hits part of the damage.

**Penetration**: Drives enemy fire resistance into negative territory — a boss sitting at 50% res gets pushed below zero by flask + penetration combined, meaning they take more than baseline damage. Penetration wins in most content by a wide margin.

Note: the tincture is not a normal flask — its implicit value (the 140% increased Elemental Damage with Melee Weapons, and the effect multiplier) can be rerolled with **Blessed Orbs**. Roll the implicit as high as possible before committing to a suffix.

## The Vaal Impurity Caveat

Vaal Impurity makes your hits ignore enemy fire resistance entirely, setting effective resistance to zero. Penetration's entire value is pushing resistance *below* zero for many enemies. For most enemies, Impurity does more harm than good, especially with this suffix on the tincture.

# 3b. Life Stacking

Every non-unique gear slot should have **Tier 1 Life and high Strength** as the baseline target. This is not optional polish — it feeds both damage layers simultaneously. Beyond raw gear, several systems specifically amplify how much life you can stack.

## Split Personalities

The passive tree takes a long, deliberately winding path from the starting location to the jewel sockets. Every passive allocated between start and socket increases the Split Personality jewel's effect. Two jewels are socketed:

- **Life + Strength**: scales both damage loops at once — more life for Grey Wind flat damage, more Str feeding Iron Will → Crown of Eyes
- **Life + Accuracy**: mandatory for hit chance against endgame bosses; capping accuracy is not achievable through gear alone at our budget

The winding path also passes through many small nodes inside the Lethal Pride radius, each converted to +5 Strength.

## Foulborn Red Dream

Socketed near Barbarism. Passives in its radius that grant Fire Resistance or All Elemental Resistances also grant Maximum Life at 50% of their value — replacing attribute nodes in radius with Fire Resistance tattoos generates meaningful flat life from nodes that would otherwise give nothing useful. Provides roughly 500 maximum life total (pushing from ~10,800 to ~11,300), and its Foulborn implicit delivers the 8% of Fire Damage as Extra Chaos Damage described in Section 3.

## Life Masteries

Six Life Masteries are allocated primarily to trigger the **10% more Maximum Life** payoff — a more multiplier on your entire life pool, which itself multiplies both damage layers. Of other five masteries:
- two don't do anything - low life and full life (unless you use support that relies on being at full life)
- one is weak, but useful - 30 flat life
- one can be useful, allowing to use chest without life modifiers, but we don't use it (see below)
- one is really useful - **Skills Cost Life instead of 15% of Mana Cost**, which contributes to the mana solution (see Section 6).

## The 15% Mastery — No-Life Chest Route

A Life Mastery grants **15% increased Maximum Life if there are no Life Modifiers on Equipped Body Armour**. This seems attractive as an alternative chest strategy — skip life on the chest, activate the mastery. We tested it, no-life rare chest results in much lower total life than what we have with 180 max flat life explicit.

This is partly because our Royal Plate is exceptionally well-rolled — four T1 mods (+45 Intelligence, +499 Armour, 106% increased Armour, +180 maximum Life), near-maximum intrinsic armour, and open creaftable suffix which we use for 6% icreased attributes. If your chest life is not T1, run the numbers in PoB before assuming the flat life chest wins.

## Hunter Belt — Attributes Over Life

The Cord Belt (Hunter influence base) has **9% Increased Attributes** as an implicit. When bench crafting the belt, **% increased Attributes is better than % increased Life** in our situation. We already have an enormous increased life pool — additional % increased life hits severe diminishing returns. Attributes scale Strength (damage and life), Dexterity (accuracy, gem levels), and Intelligence (gem requirements) all simultaneously, and benefit from the Hunter implicit's multiplicative attribute scaling on top. Again, check what you can craft, and what resulting life/dps it will produce.

## Rings

Both rings carry the near-mandatory crafted **−7 Non-Channelling Skills Mana Cost** prefix. Core targets for the remaining affixes: Life, Strength, Intelligence, Chaos Resistance, and Fire Resistance as needed. One of rings needs *Flammability on Hit* suffix. I bought cheap flammability rings and rolled amethysts for high life rolls and used non-destroying recombinator mode until got flammability on the Amethyst ring, and then fractured it which helped with further crafting. Other option is Vermillion ring (7% increased life implicit) (and/or Enthalpic with its +2% max fire res implicit, if your max fire res is below 85 or Ruby flask isn't always on).

## Chest Suffix — Current Decision

The chest previously used `+15% Fire and Chaos Resistances` as a utility fill when the cluster jewel needed chaos res coverage. The Bloodscent cluster (with its fractured +7 Intelligence and +4% Chaos Res on small nodes) now covers that gap, freeing the suffix. Useful suffixes for rare armour chest:

- **+30 Strength** — feeds both damage loops directly, no conditions
- **13 all Attributes** — less Str than the above but covers Dex and Int simultaneously
- **6% increased Attributes** — ~2.7% more damage, scales all three attributes proportionally
- **3% Physical Damage Reduction** — pure survivability, meaningful in Simulacrum wave 20+ and Uber content



# 3c. Defence

The build stacks multiple independent defensive layers. No single layer is a silver bullet — the safety comes from their overlap.

## Life Pool

~11,500 maximum life is itself the first and largest defensive layer. At this pool size, hits that would one-shot a 5,000 life character are survivable. Every defensive calculation below scales with this number — Vaal Molten Shell absorption, life regeneration rates, leech caps, all of it.

## Armour + Vaal Molten Shell

Royal Plate base + Juggernaut + Bravery notables + Granite Flask produce a large armour total. This directly feeds **Vaal Molten Shell**, which absorbs damage equal to 10% of your armour (capped at 5,000) before your life takes a hit. The CwDT setup fires the base Molten Shell reactively on damage taken. The Vaal version is an on-demand panic button for telegraphed large hits — use it proactively on boss slams, not reactively after you're already low.

## Maximum Resistance — Fire Caps Everything

Tasalio + Valako mean that capping fire resistance caps all three elements. Maximum fire resistance sources stack to 85% baseline:

- Barbarism notable: +1%
- Chest Exarch implicit: +2%
- Tree small node: +1%
- Prismatic Skin notable: +2% all elements
- Purity of Fire: +4%

 Ruby Flask (auto-trigger) pushes maximum fire res to **90%** while active — and via Valako, cold and lightning maximum res follow at the same value.

**Crown of Eyes imposes a −30% fire resistance penalty.** This is non-negotiable — it is baked into every resistance calculation. Your gear must account for it.

## Arctic Armour

21% less physical and fire damage taken from hits while stationary - useful to stand and facetank bosses.

## Endurance Charges

5 maximum charges (Endurance + Stamina notables). Maintained permanently by Enduring Cry (Sione's infinite warcry power guarantees full charges on every use). Each charge provides 4% physical damage reduction and 4% elemental resistances — 5 charges is 20% physical reduction and 20% all elemental resistances permanently.

## Phys Taken as Fire

The mutated Xoph's Blood converts **6% of incoming physical damage from hits to fire damage**. Our maximum fire resistance and Arctic Armour mitigate that converted fire damage trivially. Net effect: a portion of physical hits is reduced by ~85%+ instead of being reduced only by armour.

## Protection Mastery

**Damaging Ailments cannot be inflicted while you already have one. Non-Damaging Ailments cannot be inflicted while you already have one.** In practice this means once a bleed, ignite, or poison lands, a second one cannot stack on top. Combined with Tasalio's ignite immunity, it means only one stack of bleed or poison can affect, which is almost as good as immunity. Also, it's either chill or shock - and shock is the biggest danger, needs to be mitigated via flask suffixes.

## Enduring Cry imbued with Blessed Call Support lvl1 — Consecrated Ground

Every Enduring Cry use creates consecrated ground for 4 seconds via it's imbued Blessed Call Support. Consecrated ground gives 5% max life as regen, boosted by Devotion's 25% increased effect of consecrated ground you create. Again, useful to stand and facetank.

## Life Regeneration Stack

Passive regeneration from multiple sources compounds continuously:

- Golem's Blood: 1.6% life/sec
- Warrior's Blood: 1.8% life/sec  
- Master of the Arena: 1% life/sec
- Ascendancy minor nodes: 4× 0.5% life/sec
- Endurance charge mastery: 0.2% per charge × 5 charges = 1% life/sec
- Consecrated ground (Enduring Cry): ~670 flat/sec

Total passive regen outside consecrated ground is substantial enough to recover from chip damage between encounters without flask use. PoB shows 2400 life/second recovery.
Then there's leech, about 2200 per second.

## Mana & Life Cost

The 8-link setup (Static Strike + 5 supports + Inspiration + free Ancestral Call from Tukohama) is expensive to run. The cost solution layers three systems:

- **2× −7 Non-Channelling Mana Cost** crafted on both rings: −14 mana flat
- **Skills Cost Life instead of 15% of Mana Cost** (Life Mastery): offloads 15% of remaining cost to life
- **Mana Leech** (Fuel the Fight cluster): recovers mana continuously in combat

Net result: **22 mana + 11 life per cast** after all reductions. The 11 life drain is imperceptible at 11,500 life. Mana leech in sustained combat keeps mana effectively topped up — Inspiration support further reduces cost as charges accumulate.

# 4. Main Skill — Static Strike & Void Shockwave

## Why Static Strike on Controller

On keyboard, skills like Smite of Divine Judgement or Wild Strike can be aimed and repositioned freely. On a controller, one can only choose direction, so no shotgunning of overlapping aoe is possible.

Static Strike sidesteps this entirely. You hit the boss once to generate static energy, then the **auto-targeting beams do the work for the next 4 seconds** while you reposition. Effective DPS ≈ paper DPS. Other skills lose 30–50% of their theoretical output to movement. That is applicable to keyboard/mouse as well. And it's nice not to have to target anyway.

## Beam Mechanics

Understanding beams is necessary to understand every gem choice in the main link.

- Beams fire every **0.32 seconds** — this is fixed and cannot be changed
- **Attack speed does not affect beam frequency**
- Beams are **melee attacks** but not melee strikes — they proc Fortify and generate Rage, but do not count as strike hits for mechanics that require a melee strike specifically
- Maximum **6 beam targets** simultaneously
- Beams have **+1 chain** baseline
- Beam duration is **4 seconds** — the window in which you can reposition freely

## Void Shockwave — How It Works

Void Shockwave is a support gem that triggers a shockwave on melee hit. The shockwave fires on a **0.50 second cooldown**. Beams tick every 0.32 seconds — fast enough that a beam tick catches the shockwave immediately as it comes off cooldown, giving approximately **2 shockwave triggers per second** in sustained combat. This cadence was verified by counting shockwave explosion sound as heartbeats.

The shockwave itself deals area damage in a 2.1 metre radius and **repeats from up to 5 enemies hit**, with repeats dealing 50% less damage. This secondary explosion chain is what makes Void Shockwave better than Greater Multistrike for clear when there are more enemies than beams, even with Greater Chain support.

**This mechanism only works with Static Strike.** Other skills cannot guarantee a continuous stream of hits at 0.32 second intervals to keep firing the shockwave off cooldown. On Smite, Infernal Blow, or any skill with a slower hit cadence, the shockwave fires inconsistently and the DPS advantage evaporates.

## Void Shockwave vs Greater Multistrike

Both paths produce comparable DPS against stationary bosses on paper. The real differences are practical:

| | Void Shockwave | Greater Multistrike |
|--|----------------|---------------------|
| **Clear** | Better — shockwave chains cover packs, no target cap | Worse — beam cap limits coverage |
| **Boss DPS uptime** | Better — beams maintain DPS during dodges, less reliant on landing hits | Worse — relies more on hit frequency during vulnerability windows |
| **Attack speed value** | None for shockwave cooldown or beam frequency | Directly increases hit rate and beam trigger rate |
| **Feel** | More passive, beams do the work | More active, player-controlled hit cadence |
| **Skill compatibility** | Static Strike only | Works with Smite, Infernal Blow, Wild Strike swaps |

The Void Shockwave path shifts the damage split toward beams and away from hits. You are less dependent on landing strikes during boss mechanics. The trade-off is that the build feels slightly more passive and less directly controlled than the Multistrike path.

Greater Multistrike feels better though. Despite it's locking the toon in the animation for 4 strikes, with more attack speed from the gem, it feels more dynamic. And you control where and when to direct damage, and Tincture with attack speed boost feels stronger too.

## Imbue — Ruthless vs Cruelty

The main skill gem is imbued — a Mirage league mechanic where a support gem's effect is baked directly into the skill gem as a property, freeing a link slot. Depends on what you can get, and what that gem will do at level 1 (while having the same mana cost multiplier as level 21 would).

I couldn't roll or buy Hypothermia imbue (20% more against chilled at lvl1 vs 30% at lvl 21, 130% cost miltiplier), so I use Cruelty - Grants a flat 15% more damage multiplier on hits at lvl 1 (vs 25% at level 21, so same loss of "more", but has 140% cost multiplier). It's damage over time effects are irrelevant here.

I have also Ruthless imbue, but not sure if it works with triggered effects - beams and shockwave explosions. Likely interpretation: with Ruthless support, every third attack causes a Ruthless Blow — the blow is the melee strike itself dealing more damage. Beams are not the blow, they are a secondary effect of the attack. So Ruthless only amplifies the strike hit every third swing, not beams or shockwave. Cruelty imbue: flat 15% more damage with hits from the supported skill. Applies consistently to every strike hit and likely beams (as damage from the originating attack). Shockwave excluded as a triggered skill.

## Gem Links (Body Armour — 8L with Tukohama and imbue)

**Static Strike *(Ruthless imbue)* + Void Shockwave + Inspiration + Close Combat / Greater Chain + Elemental Damage with Attacks + Hypothermia  + Ancestral Call *(free from Tukohama)* + Cruelty imbue**

Arguably ELemental Focus can be better than Close Combat as it's more universal. We lose ignite/chill/shock, but ignite is small, and chill/shock provided by Skitterbots. But at facetank distance, Close Combat is stronger (40% vs 35% more at lvl 21). Plus ignite gives few percents of dps too.

**The swappable socket:**
- **Bossing**: Close Combat.
- **Mapping**: Greater Chain — beams chain 3 additional times, clearing packs across a wider area while moving. Note: Greater Chain's longer range spreads kills over a wider area, which *reduces* Beyond portal spawn clustering. For Beyond density farming specifically, this is a drawback.

**Socket colours:** We mostly need red, which is easy with armour base, so it's not hard to use **Omen of Blanching** to get enough white sockets for flexibility.


## Ignite

Ignite contributes approximately 255k out of 12 million total DPS (with tincture on, full rage and so on). It is present but not a meaningful part of the damage profile and should not be scaled. Rathpith Globe and Crown of Eyes specifically scale Attack Damage — ignite strictly ignores Attack Damage multipliers, making an ignite pivot mechanically impossible without dismantling the entire engine.

# 5. Skill Swap Framework

The core engine — Grey Wind, Rathpith Globe, Crown of Eyes, life stacking — is **skill-agnostic**. Any strike or slam skill benefits from the same scaling. Swapping content is a gem swap only, no regearing needed. Tukohama's ascendancy node serves whichever skill type is socketed: strikes get Level 30 Ancestral Call, slams get Level 20 Fist of War.

## Skill Selection by Content

If you use Greater Multistrike, there are more choices of the main skill.

- Infernal Blow nice for clear in high density with its on-death explosions cluster kills.
- Smite of Divine Judgement covers area and feels nice too. Note: Smite's AoE portion does not generate Rage — you must land the melee strike on the boss to maintain Rage and Intimidation.
- Wild Strike is fun in mapping, but inconsistent on bosses.

Rejected:

- Static Strike of Gathering Lightning: Broken interaction with Greater Multistrike — repeats do not count as individual melee hits for lightning stack accumulation, capping at 5–6 stacks instead of the intended 12. Do not use with Multistrike.

# 6. Controller Setup & Playstyle

## Four Buttons

| Button | Primary | Modified (R2) |
|--------|---------|---------|
| **Square** | Static Strike | n/a |
| **Triangle** | Shield Charge | Flame Dash |
| **Circle** | Enduring Cry | Blood Rage |
| **Cross** | Vaal Molten Shell | n/a |

Plus one button for Tincture. Everything else is automated.

## Movement

**Shield Charge** is the primary movement skill. While levelling, Quicksilver flask, move speed suffixes on flasks, attack speed for Multistrike setup, Indimidating Cry made this build very zoomy.  **Flame Dash** handles gaps and ledges that Shield Charge cannot cross.


## Rage Ramp

At the start of every boss fight, Rage starts at zero. Allow ~6 seconds of hitting before expecting full Intimidation and maximum Rage benefits.


## Vaal Impurity of Fire

Can be kept if you are sure that boss has fire res so high that all our measures dont make it negative, otherwise it's counter-productive. I can't be bothered to think about it, so I removed it from the build when I changed Tincture suffix to resistance decrease.When penetration was low, I used it during boss damage windows. The ignore-resistance burst is significant but short.

## Enduring Cry Timing

Enduring Cry has a short delay before the buff applies. Press it between attack sequences, not during. With CDR Support + Urgent Orders, uptime has a comfortable buffer — you do not need to press it the instant it comes off cooldown. The consecrated ground lasts long enough that as long as you cry roughly every 4–5 seconds, regeneration is continuous.

## Flask Management

All flasks are automated where possible with Flagellant (gain 3 charges when being hit), and active most of the time in combat:

- **Granite Flask**: keep it rolling for armour and Vaal Molten Shell absorption. See if Granite or Bismuth is better depending on your armour values.
- **Ruby Flask**: maintains the +5 maximum fire res that caps all elements via Valako
- **Silver Flask** Onslaught
- **Tincture**: manual — activate at the start of a pack or boss fight, sustain through mana leech. Mana leech from Fuel the Fight keeps the tincture running through sustained combat
- At some point I lost some chaos res, went below cap, so I replaced life/hybrid flask with Amethyst Flask

**Frost Bomb**: kept in inventory, not on the flask bar. Swap in for high-regen content (Uber Lab, map mods with regeneration). The cold exposure and regen reduction matter specifically against enemies that outpace your damage with recovery.

# 7. Ascendancy — Chieftain

## Tasalio, Cleansing Water
Fire resistance modifiers also apply to cold and lightning resistances at **50% of their value**. Unaffected by Ignite.

This is the build's elemental defence foundation. Every piece of fire resistance on gear passively caps cold and lightning at the same time.

## Valako, Storm's Embrace
Modifiers to maximum fire resistance also apply to maximum cold and lightning resistances.

Pairs directly with Tasalio. See max fire res sources above.

## Tukohama, War's Herald
Skills from equipped body armour are supported by **Level 30 Ancestral Call** (strikes) or **Level 20 Fist of War** (slams).

Level 30 Ancestral Call provides **10% more damage** unconditionally, plus additional strike targets for clearing. The free 7th link alone justifies this node. The node is not wasted on skill swaps — whatever strike or slam is socketed benefits automatically.

**vs Ngamahu**: Ngamahu grants +4 Strength per non-unique jewel in radius. With Lethal Pride occupying the high-density pathing socket and Red Dream taking another, few sockets remain with mostly pathing nodes — netting roughly +3% more life but losing the 10% more damage from Tukohama's free Ancestral Call. Tukohama wins on damage by a clear margin.

**Levelling note**: If one levels with Shield Crush / Impale, note that Shield Crush is neither a strike nor a slam — Tukohama's supports do not activate. Use Ngamahu instead (+4 Str per non-unique jewel) until transitioning to Static Strike, then swap to Tukohama.

## Sione, Sun's Roar
Warcries have infinite power. 30% increased Warcry Buff Effect.

Infinite power guarantees full endurance charges on every Enduring Cry use and maximises the life regen buff. The 30% buff effect increases consecrated ground potency — net regen with Sione is ~1,975/sec versus ~1,343/sec without. The 632 life/sec difference is the margin between comfortable sustain and struggling against sustained damage.

**vs Hinekora, Death's Fury**: Hinekora offers 10% chance for enemies to explode (250% maximum life as fire damage) — strong clear speed in theory. Beams and Greater Chain already clear well. Losing 632 life/sec regen is too severe a trade for marginal clear improvement that the build does not need.


# 8. Gem Links — Full Reference

## Body Armour (effective 8L)

**Static Strike *(Cruelty imbue)* + Void Shockwave + Inspiration + Close Combat / Greater Chain + Elemental Damage with Attacks + Hypothermia  + Ancestral Call *(free)***

- **Void Shockwave** (4/23 Exceptional): core of the shockwave path, triggers on beam ticks at ~2/sec
- **Inspiration**: 40% less mana cost + more elemental damage per charge. Despite being a "free" support in terms of mana, it is a genuine damage gem.
- **Close Combat**: up to 40% more melee damage (at lvl21) based on proximity. Swap to **Greater Chain** for relaxed mapping situations.
- **Elemental Damage with Attacks**: flat more multiplier on all elemental damage - 35% more at level 21.
- **Hypothermia** 30% more damage on chilled enemies at lvl 21 (Skitterbots chill them)
- **Ancestral Call** (free, Level 30): 10% more damage + extra strike targets. Whether phantom strikes generate independent beam sets is unverified but Saresh testing suggests they may

## Helmet (4L)

**Purity of Fire + Arctic Armour + Summon Skitterbots + Enlighten**

- **Enlighten** keeps reservation manageable across three auras simultaneously
- **Purity of Fire**: aura grants +52 fire res and +4 maximum fire res.
- **Arctic Armour**: 21% less physical and fire damage taken while stationary. Freeze immunity. Chills enemies that hit you
- **Summon Skitterbots**: permanent Shock and Chill. Enables Hypothermia. A corruption on rare jewel (6% non-damaging ailment effect) makes both stronger

## Gloves (4L)

**Enduring Cry *(Blessed Call imbue)* + More Duration + Urgent Orders + Cooldown Recovery Support**

- **Blessed Call imbue**: makes consecrated ground, increases speed, but adds a CDR penalty to Enduring Cry — CDR Support cancels this exactly, restoring full uptime
- **Urgent Orders**: instant warcry, level 20 provides large CDR overlap buffer so uptime is comfortable rather than frame-perfect
- **More Duration**: extends consecrated ground duration beyond Blessed Call's base 4.1 seconds

**Next league (no imbue mechanic)**: Urgent Orders + Blessed Call + More Duration as default trio. Upgrade More Duration to CDR Support if budget allows.

## Shield (3L)

**Vaal Molten Shell + Wave of Conviction + Cast when Damage Taken**

- **CwDT** (Level 11): auto-triggers both gems on damage taken
- **Wave of Conviction**: auto-applies −15% Fire Exposure on hit — strongest exposure source in the build, supersedes the axe's max Rage exposure
- **Vaal Molten Shell**: base version fires automatically via CwDT. Vaal version is manual panic button — use proactively on telegraphed large hits


## Boots (4L)

**Precision; Faster Attacks - Shield Charge, FLame Dash

- **Precision**: accuracy for hit chance cap + base crit for Elemental Overload uptime
- **Faster Attacks**: supports Shield Charge movement speed

## Weapon (3L)

**Blood Rage** — self-cast, Level 11/20 or whatever dex allows. 15% attack speed and 1.2% attack damage leeched as life. Degen is covered by leech and endurance charges. 25% chance to gain a Frenzy Charge on Kill (but we have it on hit anyway, as we need it for bossing).
- **Poacher's Mark + Mark on Hit**: marks used to enable cull and frenzy charge generation on hit. Marks' own effects are mostly irrelevant. Poacher's Life and mana on hit procs continuously during boss fights at our hit rate. Frenzy on kill helps charge generation during mapping (but then same does Blood Rage).

# 9. Jewels & Gear Reference

## Jewels

| Jewel | Socket | Purpose |
|-------|--------|---------|
| **Split Personality** (Life + Str) | End of long winding path | Life + Str scaling, both damage loops |
| **Split Personality** (Life + Acc) | End of long winding path | Life + accuracy for hit chance cap |
| **Lethal Pride 10740 Kaom** | Node 54127 (adjacent to Savagery) | +5 Str on small nodes in radius; 5% double damage on Golem's Blood + Master of the Arena (~10% more DPS) |
| **Foulborn Red Dream** | Near Barbarism | Fire res nodes → max life in radius; 8% fire damage as extra chaos damage |
| **Blight Ornament** (Viridian) | — | 7% incr Life, attibutes, corruption for 6% increased effect of non-damaging ailments — strengthens Shock and Chill from Skitterbots |
| **Bramble Curio** (Crimson) | — | 7% max life, 12% chaos res, 4% attack speed with shield, Str+Dex |
| **Kraken Spark** (Large Cluster) | Large socket | Bloodscent (2 Rage on hit with axes/swords) + Fuel the Fight (mana leech, attack speed, 20% damage while leeching); small passives grant +4% chaos res, +7 Int, 12% axe/sword damage |
Corrupted blood immunity jewel has 7% incr life and flat str.

**Dexterity note**: Dex on rare jewels is required to meet gem requirements. The Blight Ornament and Bramble Curio both contribute here.

## Equipment Reference

### Weapon — The Grey Wind (Spectral Axe)
The entire value is the implicit: **Added Fire Damage equal to 12% of maximum life**. At 11k+ life this is ~1,320 flat fire per hit. The physical base (29–48) is negligible. Current version: 12% life conversion + **+5 max Rage** enchant (upgraded from 8% + 0 Rage base on 2026-04-03).

**Axe enchant options:**
- **AoE** (chosen): increases beam chain reach and overlap radius. Also buffs Smite and Infernal Blow swaps. No other AoE scaling exists in the build — this is the only source
- **Attack Speed**: only affects the melee strike, not beams. PoB shows higher number but real-world beam uptime gain is zero
- **Strike Range**: PoB cannot calculate this accurately

*Note: Tempering Orbs were attempted for increased fire effect. 10 Divines later, reverted to Lifeforce AoE enchant. Not recommended.*

### Helmet — Crown of Eyes (Hubris Circlet)
Spell Damage applies to Attacks at 150% of its value. The −30% fire resistance penalty is permanent and must be accounted for in all resistance calculations. Useful corruption for Purity of Fire level.

### Shield — Rathpith Globe (Titanium Spirit Shield)
5% increased Spell Damage per 100 maximum life. At 11k life this is 55% increased spell damage, which Crown of Eyes converts to 82.5% increased attack damage. Scales directly and continuously with life. Try to het good spell block roll. Crit for spells is wasted.

### Body Armour — Royal Plate ("Spirit Pelt")
Current chest is exceptionally well-rolled: four T1 mods (+45 Intelligence, +499 Armour, 106% increased Armour, +180 maximum Life), +46% Fire Resistance, near-maximum intrinsic armour, +2% maximum Fire Resistance Exarch implicit, 7% Fortify chance implicit. Crafted suffix currently under evaluation (see Section 3b).

**The no-life chest route**: a 15% increased maximum Life mastery activates with no life modifiers on body armour. Tested and rejected on this chest — with that equipment the mastery produced 11,148 final life versus this chest's 11,489. On a less exceptional chest this calculation may differ. Run the numbers in PoB before assuming flat life wins.

### Amulet — Xoph's Blood (Foulborn Amber)
Mutated modifiers: Elemental Overload + 6% phys taken as fire. Removes Avatar of Fire restriction. Penetrates 10% fire resistance. The mutation removing Avatar of Fire is what enables the Red Dream chaos damage interaction.

### Belt — Cord Belt (Hunter influence)
Hunter influence to get % incr life prefix and/or % incr attributes suffix. Whispers of Doom anoint: +1 curse limit (enables double curse — Flammability + Poacher's Mark simultaneously). Craft % increased Attributes over % increased Life — diminishing returns on the already large increased life pool make attributes the more efficient bench craft.

### Rings
- **Amethyst Ring** ("Doom Grasp"): fractured Flammability on Hit, +419 accuracy, +112 life, +40% chaos res, +27% chaos res implicit, crafted −7 mana cost
- **Vermillion Ring** ("Dusk Turn"): fractured +112 life, +61 Str, +42 Int, +47% fire res, 7% max life implicit, crafted −7 mana cost

Both rings carry the mandatory −7 Non-Channelling Mana Cost craft. Combined with the life mastery cost offset and Fuel the Fight mana leech: 22 mana + 11 life per cast in sustained combat.

### Gloves
Rare gloves. Priority stats: life, strength, intelligence, resistances as needed to cap. Possible exarch implicit: Gain Rage on Hit — contributes to rage ramp alongside Bloodscent and tree nodes. Open prefix for 40% incr damage while leeching benchcraft.

### Boots
Rare boots. Priority stats: life, movement speed, resistances. Dexterity if needed for gem requirements.

# 10. Appendices

## 10a. Mark Analysis

Marks are applied automatically via Mark on Hit Support. The Mark Mastery provides 10% chance to gain a frenzy charge on hit against the marked enemy — the primary frenzy source during bossing. Marks exist to enable frenzy generation and culling, not as primary damage layers.

| Mark | Assessment |
|------|-----------|
| **Poacher's Mark** ✓ | Life and mana on hit — procs continuously at our hit rate during boss fights. Frenzy on kill handles charge generation during mapping. Best overall |
| **Assassin's Mark** | Culling strike is useful for specific bosses. Power charges and crit multi are wasted — Elemental Overload has no crit multiplier. Life on kill is useless during boss fights. Switch to this if culling strike threshold matters for a specific encounter |
| **Warlord's Mark** | Endurance charges already permanently capped via Enduring Cry. Life leech overcapped. Rage on stun unreliable at boss level. Nothing useful |
| **Alchemist's Mark** | Requires ignite or poison. We have neither. Dead |
| **Sniper's Mark** | Projectiles only. Irrelevant |

## 10b. Enduring Cry — Next League Note

Current setup uses the Mirage league imbue mechanic: Blessed Call imbued into Enduring Cry, with CDR Support cancelling Blessed Call's cooldown penalty exactly.

Without the imbue mechanic (next league): run **Urgent Orders + Blessed Call + More Duration** as the default trio. Upgrade More Duration to CDR Support if budget allows and you want the comfortable uptime buffer rather than exact uptime. Note that Blessed Call's value scales with how stationary your playstyle is — during mapping with constant movement, consecrated ground uptime is inherently low regardless of support gems.

## 10c. Levelling Notes

- **Early game**: Intimidating Cry is excellent for mobility (knockback + stun). Shield Charge + Faster Attacks + Momentum for movement — with the build's attack speed scaling this is very fast travel
- This league I levelled with Shield Crush, focusing on phys damage and impale. Easy to max damage by upgrading shields, Dawbreaker shield with huge armour values is cheap. Next league I'll try levelling with Static Strike from the start (requires level 12), regular Shockwave support (requires level 18). Uniques for life stacking won't be available at the start, we'll see if Static Strike will carry still, and how to get damage for it without lifestacking engine.

## 10d. Pay attention

### General Min-Maxing
- **Sacred Orbs**: apply to all armour pieces — check that all are done
- **Blessed Orbs on tincture**: the tincture implicit value is rollable — maximise it before committing to a suffix craft

## 10e. Origin — Peuget2 Template

This build originates from Peuget2's Apostate life-stacker Smite Chieftain. The original template uses *Enmity's Embrace* (stacking massive fire res on every gear slot, converting overcapped fire res to fire penetration via a specific *Elegant Hubris* seed) for ~40% more damage from the ring alone. The entire gearing strategy in that build is warped around fire res on every suffix, with Purity of Elements consuming 35% reservation to cap other resistances.

We cannot replicate that on PlayStation — the required Elegant Hubris seed does not exist on the PS market, awakened support gems have zero supply, and mirror-tier life-corrupted uniques are not achievable. We have an Apostate in stash, six-linked and coloured — this is not a budget constraint. We chose not to use it because without the life-corrupted uniques to push HP high enough, Apostate's zero-defence model leaves you dead at any realistic PS budget. A rare Royal Plate with flat armour, Fortify, and T1 life mods keeps you alive where Apostate cannot.

What we gain by skipping Enmity's Embrace: free aura slots (Skitterbots, Arctic Armour, Precision), simpler gearing, and suffixes available for chaos res and attributes instead of being entirely devoted to fire res.

One final note: the 3.26 patch buffed Static Strike's base damage effectiveness and introduced Void Shockwave as a new support. Both changes disproportionately benefit this build's architecture. The life-stacking Chieftain with Static Strike + Void Shockwave may simply be the stronger path in the current patch regardless of platform — and the Apostate + Enmity's Embrace route on PC would itself benefit from adopting this same tech on top of its higher life ceiling.
