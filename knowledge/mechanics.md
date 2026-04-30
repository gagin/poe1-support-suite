# PoE Core Mechanics Reference

Generic game mechanics for build advising. Verify via MCP/wiki before citing — PoE changes every league (~3 months).

---

## Skill Links and the 6-Link

The **body armour** is the default 6-link slot for the main skill. Exceptions:
- **Helmet with support implicits** (e.g. Elder helmet with "supported by Burning Damage"): helmet becomes the main skill slot; body armour holds an aura or secondary skill. Righteous Fire builds commonly do this.
- **Bow builds**: the bow itself is 6-linked; quiver is offhand. Body armour holds a secondary skill or auras.
- **Two-handed weapon builds**: weapon is 6-linked; body armour holds secondary skill or auras.
- **Squire shield**: provides 4 additional supports to a skill in the main hand — effectively a 6-link from a 2-link weapon. Body armour is free for another 6-link.
- Any build with a 6-linked weapon uses body armour for a second major skill or aura setup.

**Always identify which slot is the actual main skill slot before advising on links.**

---

## Damage Formula

```
DPS = Base × (1 + Σincreased%) × more_1 × more_2 × ... × APS
```

### Increased — Additive Pool
All "increased damage", "increased fire damage", "increased physical damage", etc. sum together:
- Adding 50% increased when you already have 300% is a 50/400 = 12.5% actual gain, not 50%.
- The larger the existing pool, the weaker each new source.

### More — Each Its Own Multiplier
Support gems and some ascendancy nodes grant "more" — each multiplies the total independently:
- Adding a 40% more source on top of two existing 40% more sources: `1.4 × 1.4 × 1.4 = 2.74×` vs `1.4 × 1.4 = 1.96×` without it — a genuine 40% gain regardless of existing pool.
- A new "more" source is almost always the strongest damage upgrade available.

### Flat (Added) Damage
"Adds X to Y damage" mods contribute to base damage before all multipliers. Effectiveness depends on the skill:
- Attacks typically have **100% effectiveness of added damage** — flat damage from rings, gloves, abyss jewels applies fully.
- Spells list their own **effectiveness of added damage** in the skill description (e.g. 70%, 30%). Low-effectiveness spells gain little from flat damage sources — don't stack it for them.
- Totems, traps, mines can have their own effectiveness modifiers.

### Attack Speed
"Increased attack speed" sources pool additively with each other (same diminishing returns as increased damage). But hits-per-second multiplies with full damage-per-hit — so attack speed is multiplicative *with damage*, while individual AS sources are additive *with each other*. Check the current AS pool size before valuing a new source.

### Priority Order for Damage Upgrades
1. New "more" multipliers (supports, ascendancy, uniques granting more)
2. Attack/cast speed (multiplicative with damage per hit)
3. Flat damage to attacks (only if effectiveness of added damage is high)
4. Increased damage (only valuable if current total is low, e.g. <200%)

---

## Damage Multipliers Beyond "More"

These are often overlooked but act as powerful additional multipliers:

### Shock (Lightning Ailment)
- Enemies take "increased damage" — a separate layer on the enemy side, not the player.
- Base shock: 15% increased damage taken. Scalable up to 50% with "effect of shock".
- Because it's on the enemy's side, it multiplies with all of the player's own damage scaling.
- Effective for any damage type, not just lightning.

### Exposure
- Lowers enemy resistance by 10% (more with scaling). Each element has exposure sources (Combustion support, Frost Bomb, Ball Lightning of Static, etc.)
- Stacks with penetration differently — exposure lowers the resistance value, penetration ignores a portion of it.

### Curses
- Vulnerability: increased physical damage taken + chance to bleed.
- Flammability/Frostbite/Conductivity: lower elemental resistances (similar to exposure but larger effect).
- Elemental Weakness: lowers all elemental resistances.
- Work on the enemy side — benefit the whole party.

### Charges
- **Power charges**: +40% critical strike chance per charge (base), up to 3 (or more with passives).
- **Frenzy charges**: 4% more attack/cast speed + 4% more damage per charge (up to 3+).
- **Endurance charges**: +4% physical damage reduction + 4% to all elemental resistances per charge.
- Frenzy = offensive; power = crit; endurance = defensive.

### Elemental Overload
Doubles crit effectiveness but removes crit multiplier — only worthwhile on low-crit builds that still crit occasionally.

---

## Physical vs Elemental vs Chaos

### Physical Damage
Mitigated by **armour** (effective mainly vs small hits; much weaker vs large hits) and **physical damage reduction** (flat %, reliable across all hit sizes). Fortify provides 20% PDR.

### Elemental Damage (Fire / Cold / Lightning)
Mitigated by **resistances**. Default cap is **75%**. Raising the cap requires:
- Purity of Elements/Fire/Ice/Lightning (auras)
- Specific uniques (e.g. Atziri's Splendour, Kaom-series notables via Lethal Pride)
- Passive nodes (Barbarism, Prismatic Skin, Armour Mastery, etc.)

### Chaos Damage
Mitigated by **chaos resistance** — often negative on characters. Chaos res is frequently overlooked but critical for endgame. Amethyst Ring base (+23% chaos implicit) is the easiest source.

### Penetration vs Exposure
- **Penetration** (e.g. fire penetration support, Flammability): ignores that amount of the enemy's resistance. More valuable when enemy resistances are high.
- **Exposure**: reduces the enemy's actual resistance value. Stacks with penetration independently.

### Damage Conversion
- Physical → elemental (e.g. 50% phys to fire): converted portion benefits from physical scaling *before* conversion and elemental scaling *after*.
- Full conversion (100%) means all physical scaling + all elemental scaling apply — very powerful.
- Conversion is applied before mitigation — the damage type at time of hit determines what resists it.

---

## Curse Limit

Default: **1 curse** on enemies. Sources that grant additional curses:
- **Whispers of Doom** keystone (passive tree)
- **Doedre's Damning** ring (+1 curse)
- **Windscream / Windshriek** boots (+1 curse to non-unique enemies)
- **Impresence** amulet (free reservation for one curse + effectively +1 for that type)
- **Malediction** (Occultist ascendancy): +1 curse
- Some unique items and cluster notable passives

**Always verify a multi-curse source exists before assuming a build can apply 2+ curses.**

---

## Critical Strikes

- **Crit chance** = base skill crit × (1 + increased crit chance%) × more crit chance
- **Crit multiplier** = 150% base + flat additions. All additions are additive with each other, then applied as a "more" on a crit hit.
- Crit is only meaningful if the build reaches a significant hit rate (typically 60%+ to matter; 90%+ for pure crit builds).
- **Ailment builds** (ignite, bleed, poison): only the initial crit matters for ailment magnitude — crit multi does **not** scale DoT damage unless specifically stated (e.g. "ignite damage based on crit multi" from certain passive nodes).

---

## Damage Over Time vs Hit-Based

### Hit-Based Skills
Deal damage at the moment of impact. Trigger on-hit effects, leech, ailments, crit.

### DoT Skills (Ignite, Bleed, Poison, Caustic Arrow, Scorching Ray, etc.)
- Do **not** trigger on-hit effects, leech (unless specifically granted), or stacking crits.
- Scale with: "increased/more X damage over time", "increased/more burning/bleeding/poisoning damage".
- "Increased damage" without a qualifier applies to hits **and** DoTs.
- Ignite damage is based on the hit that caused it (or crit multi, if the build stacks it via nodes).
- Poison scales with the base physical + chaos damage of the hit. Bleed scales with physical.

---

## Defense Layers

A well-rounded character needs multiple layers. Never recommend stacking only one.

1. **Life / ES / Mana (Mana before Life / EB+MoM)** — primary buffer
2. **Armour** — reduces physical hit damage (effective vs small hits; less vs large)
3. **Evasion** — chance to avoid hits entirely (pairs with Acrobatics)
4. **Resistances** — elemental and chaos cap; always verify all four are capped
5. **Block** — chance to block attacks/spells (shield / block passives)
6. **Fortify** — 20% less hit damage taken while active
7. **Endurance charges** — physical reduction + all-res per charge
8. **Flasks** — Granite (armour), Jade (evasion), Topaz/Ruby/Sapphire (resistance), Basalt, Quartz
9. **Recovery** — life regen, life on hit, leech rate
10. **Ailment immunity** — freeze/shock/ignite immunity are often flask-based

Check what the build lacks before suggesting offense upgrades.

---

## Aura Reservation

- Auras reserve mana (or ES with specific gear/passives).
- Default reservation: Determination/Grace/Hatred/Haste = 50% mana; Purity auras = 35%; Heralds = 25%; Aspect skills = 25%.
- Enlighten (level 3/4) reduces reservation — significant investment, verify the build actually needs it.
- Mana reservation efficiency from tree/gear stacks additively to reduce costs.
- Anointing a mana reservation efficiency notable can unlock an additional aura slot — evaluate this before committing to a damage or defensive anoint.

---

## Corruption

Corrupting an item (Vaal Orb) makes it **unmodifiable** afterward (no crafting bench, no currency except Awakener's Orb on influenced items). One of four outcomes:
- **Implicit replaced or augmented** — most common and valuable. Can gain a second implicit or have existing implicit replaced (e.g. "+1 to level of socketed gems", culling strike, blind on hit).
- **Sockets/links changed** — random resocket or relink.
- **Quality converted** — quality removed, converted to gem XP or wasted.
- **Nothing** — no change.

**Key points:**
- A corrupted item with a valuable implicit (e.g. "+1 to socketed gems" on a 6-link) is often dramatically more valuable than the base.
- Gems can also be corrupted: gain a level beyond 20 (level 21), quality beyond 20 (up to 23%), or a Vaal implicit. 21/20 gems are the standard for key active skills.
- Double-corrupt (Tempered by War/Suffering/Misery in the temple) applies two outcomes — very high variance, can brick or greatly enhance an item.

---

## Item Affixes — Prefixes and Suffixes

Rare items: up to **3 prefixes + 3 suffixes** (6 explicit mods total). Magic items: 1 prefix + 1 suffix max.

**Prefixes** (generally): Life, Armour, Energy Shield, Evasion, Mana, flat added damage (to attacks or spells), physical damage on weapons, % increased physical damage on weapons.

**Suffixes** (generally): Accuracy Rating, Attack/Cast Speed, Resistances (fire/cold/lightning/chaos), Attributes (Str/Dex/Int), % increased Damage, Critical Strike Chance/Multiplier, Flask modifiers, Mana regeneration, Movement Speed (boots).

**Practical notes:**
- Accuracy is a **suffix** — competes with resistances and attributes.
- Life is a **prefix** — doesn't compete with resistances.
- **Influenced items** (Shaper, Elder, Crusader, Redeemer, Hunter, Warlord) have exclusive mod pools — often the strongest possible mods for a slot.
- A full item (3 prefixes + 3 suffixes) cannot be crafted further without Orb of Annulment first.
- When crafting, check which affixes are prefix vs suffix before choosing a bench craft.

---

## Cluster Jewels — Sockets and Sizing

### Socket Counts
- **Large** cluster jewels: always **2 jewel sockets**
- **Medium** cluster jewels: always **1 jewel socket**
- **Small** cluster jewels: no jewel sockets

### Sizing Preferences

*Large clusters:*
- **8 passives** — preferred when cluster small passives are weak (fewer smalls to path through).
- **12 passives** — preferred when cluster small passives are strong (e.g. 10%+ attack damage per small). More smalls allocated = more value per passive.
- Avoid 10-passive larges — worst of both worlds.

*Medium clusters:*
- **4 or 5 passives** — standard. Minimises small passives pathed while still reaching both notables.

*Small clusters:*
- **2 passives** — always preferred. One notable + one small; minimal passive investment.

**Evaluating a large cluster:**
1. Are both notables best-in-slot for the build?
2. Is the small passive enchant strong (10%+ attack damage) or filler (2% damage)?
3. Strong smalls → prefer 12P. Weak smalls → prefer 8P.
4. The jewel enchant (e.g. "12% increased Physical Damage") is fixed regardless of passives — factor it in but it's not the primary criterion.

---

## Local vs Global Modifiers

A modifier is **local** if it meets any of these criteria:

1. **Modifies the item's own base stats** — e.g., `#% increased Physical Damage` or `Adds # to # Physical Damage` on a weapon changes the weapon's own Physical Damage and APS values shown in the tooltip (displayed in blue). Local flat damage on a weapon scales with the weapon's local increased physical damage and quality.

2. **Hand-specific** — mods containing "with this Weapon", "Main Hand", or "Off Hand". Cannot be scaled by other local modifiers.

3. **Weapon hit effect** — `#% Chance to Poison on Hit`, `#% Chance to Maim`, `#% of Physical Attack Damage Leeched as Life`, flat Accuracy on a weapon. Note: Ignite chance is always **global** because weapons have no base fire damage.

**Global** = everything else. All conditional mods are global except hand-specific ones.

**Critical practical difference:**
- `Adds 10–20 Physical Damage` on a **weapon** → local. Multiplied by the weapon's local `% increased Physical Damage` and quality. Very strong.
- `Adds 10–20 Physical Damage to Attacks` on a **ring** → global. Added to the character's total pool *after* the weapon's local calculation. Only scaled by global modifiers.

**Hybrid modifiers** treat each line independently — one line can be local, the other global.

---

## Weapon Swaps

**Ignore weapon swap slots entirely.** Only analyze the main hand and offhand that are active for the build. Weapon swap sets are typically for utility (flasks, movement) and not part of the core build.
