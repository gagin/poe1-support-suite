# Chieftain Ascendancy — Passive Reference

**Class:** Marauder → Chieftain
**Theme:** Karui ancestors, fire, strike/slam skills, warcries
**Verified:** [verified 2026-03] via poewiki.net

You may take **4 notables** from the 7 available. The tree has prerequisite chains (see below).

---

## Notable Passives (all 7)

### Ngamahu, Flame's Advance
- Non-Unique Jewels cause Increases and Reductions to other Damage Types in a Large Radius to be Transformed to apply to Fire Damage
- Non-Unique Jewels cause Small and Notable Passive Skills in a Large Radius to also grant **+4 to Strength**
- *Preceding minor node: Life Regeneration, Fire Damage*
- *Last changed: 3.27.0 (+4 Str, was +3)*
- *PoB measured [2026-03, MiragMaraBatato]: +4.4% DPS with vs without (1.247 → 1.194). Fire damage line blocked by Brutality — gain is purely from Str.*

### Hinekora, Death's Fury
- Enemies you or your Totems Kill have **10% chance to Explode**, dealing **250% of their maximum Life as Fire Damage**
- *No prerequisite notable required*
- *Preceding minor node: Life Regeneration, Fire Damage*
- *Last changed: 3.28.0 (was 5% chance / 500% max life — same expected damage, double the proc rate)*

### Ramako, Sun's Light
- Nearby Enemy Monsters' Fire Resistance against Damage over Time is **-20%** while you are Stationary
- *No prerequisite notable required*
- *Preceding minor node: Life Regeneration, Fire Damage*
- *Note: only useful for stationary fire DoT builds (e.g. Righteous Fire). Irrelevant for attack builds or moving builds.*

### Tasalio, Cleansing Water
- Modifiers to Fire Resistance also apply to Cold and Lightning Resistances at **50% of their Value**
- Unaffected by Ignite
- *No prerequisite notable required*
- *Preceding minor node: Life Regeneration, Fire Resistance*

### Valako, Storm's Embrace
- Modifiers to Maximum Fire Resistance also apply to Maximum Cold and Lightning Resistances
- *Requires: Tasalio, Cleansing Water*
- *Preceding minor node: Life Regeneration, Fire Resistance*

### Sione, Sun's Roar
- Warcries have infinite Power
- 30% increased Warcry Buff Effect
- *No prerequisite notable required*
- *Preceding minor node: Life Regeneration, Warcry Duration*
- *Added in 3.25.0 (replaced Arohongui, Moon's Presence)*
- *Power reference: Normal = 1, Magic = 2, Rare = 10, Unique = 20, Player = 5*

### Tukohama, War's Herald
- Skills from Equipped Body Armour are Supported by **Level 30 Ancestral Call**
- Skills from Equipped Body Armour are Supported by **Level 20 Fist of War**
- *Requires: Hinekora, Death's Fury OR Sione, Sun's Roar*
- *Preceding minor node: Life Regeneration, Melee Damage*
- **⚠ Build note:** Ancestral Call requires a **Strike** skill. Fist of War requires a **Slam** skill. Shield Crush is neither — it is tagged AoE Attack Melee Physical. **Both supports are completely non-functional for Shield Crush builds.** Tukohama has zero value for this build.

---

## Prerequisite Tree

```
[Fire Dmg minor] → Ngamahu
[Fire Dmg minor] → Hinekora → [Melee Dmg minor] → Tukohama (if also Hinekora OR Sione)
[Fire Dmg minor] → Ramako
[Fire Res minor] → Tasalio → [Fire Res minor] → Valako
[Warcry Dur minor] → Sione → [Melee Dmg minor] → Tukohama (if also Hinekora OR Sione)
```

---

## Notable Combinations (pick 4)

| Combination | Notes |
|---|---|
| Ngamahu + Tasalio + Valako + Sione | **Current build.** Best all-around: Str bonus per jewel, fire→all res, max fire→max all res, infinite warcry power |
| Ngamahu + Tasalio + Valako + Hinekora | Swap Sione for explosions. Lose infinite warcry power — Enduring Cry now needs nearby enemies to generate endurance charges |
| Ngamahu + Tasalio + Valako + Ramako | Ramako is for stationary fire DoT builds only. Useless for attack builds. |
| Any combo including Tukohama | **Not viable for Shield Crush** — Tukohama's supports require Strike/Slam tags that Shield Crush does not have |

---

## Tukohama — Physical Shield Crush Build

**Not viable for Shield Crush.** Ancestral Call requires a Strike skill; Fist of War requires a Slam skill. Shield Crush is tagged AoE Attack Melee Physical — not a Strike, not a Slam. Both supports do nothing. Tukohama should not be considered for any Shield Crush variant.

---

## Minor Passive Nodes

| Name | Stats | Notes |
|---|---|---|
| Life Regeneration, Fire Damage | Regen 0.5%/s; 10% increased Fire Damage | Paths to Ngamahu, Hinekora, Ramako |
| Life Regeneration, Fire Resistance | Regen 0.5%/s; +10% or +15% Fire Resistance | Paths to Tasalio, Valako |
| Life Regeneration, Melee Damage | Regen 0.5%/s; 10% increased Melee Damage | Paths to Tukohama |
| Life Regeneration, Warcry Duration | Regen 0.5%/s; 15% increased Warcry Duration | Paths to Sione |

---

## Version History (relevant changes)

| Patch | Change |
|---|---|
| 3.28.0 | Hinekora: 5% → 10% chance to explode; 500% → 250% max life as fire (same EV, higher proc rate) |
| 3.27.0 | Ngamahu: +3 → +4 Str per non-unique jewel in large radius |
| 3.25.0 | Sione added (replaced Arohongui). Tukohama now gates on Sione OR Hinekora. Tawhoa removed. |
| 3.22.0 | Major rework: Valako now requires Tasalio. Tukohama prerequisite chain changed. Hinekora no longer has a prerequisite notable. |

---

## Forbidden Flame / Forbidden Flesh — Other Ascendancy Notables

Using Forbidden jewels to access notables from other ascendancies. Costs 2 jewel slots. Verified [verified 2026-03].

### Evaluated for Physical Shield Crush (Impale, Brutality, Multistrike, Precise Technique)

| Notable | Ascendancy | Value | Notes |
|---|---|---|---|
| **Rite of Ruin** | Berserker | ★★★★★ | 50% increased Rage Effect → 1.5% more damage per Rage. At 50 Rage cap = **75% more attack damage**. Life drain 5% life/sec at cap — easily covered by build's ~19% regen/sec. Best boss DPS available. |
| **Bane of Legends** | Slayer | ★★★☆☆ | 20% more vs Unique enemies (unconditional) + 10% more if killed recently. Solid boss damage, no downside. Far weaker than Rite of Ruin but cheaper to evaluate. |
| **War Bringer** | Berserker | ✗ | Warcries Exert twice as many Attacks. Exerted double damage does not apply to multi-hit skills — Multistrike makes Shield Crush multi-hit. Useless. |
| **Impact** | Slayer | ✗ | "Does not apply to Areas of Effect." Shield Crush is AoE. The 15% more based on proximity does nothing. |
| **Master of Metal** | Champion | ✗ | +1 impale stack (7 vs 6) + 6–12 flat phys per stack (~54 flat vs ~1960 base = <3% damage). Negligible. |
| **Brutal Fervour** | Slayer | ✗ | Defensive leech mechanics. Not boss damage. |
| **Headsman** | Slayer | ✗ | Culling at 20% life + increased ATS/move speed on kill. Mapping only, nothing for boss DPS. |

### Rite of Ruin — Rage Math

- Rage gain: Rage Support gives 3 Rage per hit. With Multistrike (3 hits/sequence) at ~2.7 APS = ~24 Rage/sec gained.
- Reach 50 Rage cap in ~2 seconds of attacking. Stays capped for any sustained boss fight.
- At 50 Rage with Rite of Ruin: 50 × 1.5% = **75% more attack damage** (true "more" multiplier, multiplies with all existing more sources)
- Life drain at cap: 50 × 0.1% = 5% life/sec. Build regen ~19%/sec → net ~14% life/sec positive before leech. Fully sustainable.
