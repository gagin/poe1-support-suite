Here is the revised build document with all your corrections applied.

***

# Static Strike Life-Stacker — Chieftain (Mirage League)

**Character:** MiragMaraBatato | **Level:** 98 | **Realm:** Sony (PlayStation)

***

## 1. Core Concept

**Chieftain** provides four things no other class matches simultaneously: fire resistance modifiers applying to all elements (Tasalio + Valako), warcries with infinite power (Sione), and a free 7th support gem on body armour strike skills (Tukohama). Together these handle defence, sustain, and a significant chunk of offence in the ascendancy alone. 

**Life-Stacking Engine**: Life serves triple duty here. It is your HP pool, your flat damage, and your percentage multiplier. 
1. *The Grey Wind* (Spectral Axe) adds flat fire damage equal to 12% of maximum life to every attack. At ~11k life, this is ~1,320 flat fire, dwarfing the weapon's physical base. 
2. *Rathpith Globe* grants 5% increased Spell Damage per 100 maximum life.
3. *Crown of Eyes* makes all increased/reduced Spell Damage apply to Attacks at 150% of its value. 
4. *Iron Will* (keystone) converts Strength bonuses to Spell Damage. 
The result: Life feeds flat damage directly. Life feeds Str, Str feeds Spell Damage, and Spell Damage feeds Attack Damage at 1.5×. 

**Mutated Xoph's Blood**: Our amulet has mutated modifiers granting **Elemental Overload** and **6% of Physical Damage from Hits taken as Fire Damage**, while *removing* Avatar of Fire. Elemental Overload grants 40% more elemental damage when we crit (sustained via Precision aura), and removing the Avatar of Fire restriction ("Deal no Non-Fire Damage") allows us to benefit from non-fire added damage sources.

### Mandatory Uniques

| Item | Slot | Key stat |
|------|------|---------|
| **The Grey Wind** | Weapon (Spectral Axe) | Added fire = 12% max life; +5 max Rage; Fire Exposure at max Rage |
| **Crown of Eyes** | Helmet (Hubris Circlet) | Spell Damage → Attack Damage at 150%; −30 fire res penalty |
| **Rathpith Globe** | Shield (Titanium Spirit Shield) | 5% increased Spell Damage per 100 max life |
| **Xoph's Blood (Foulborn)** | Amulet (Amber) | Mutated: Elemental Overload + Phys taken as Fire; Penetrates 10% Fire Res |

***

## 2. Conditions

This build was heavily shaped by the **PlayStation / Sony realm (Mirage league)** economy. The PS market is thin; items that are cheap on PC can have zero supply here. 

**Ruled out due to PS market:**
- *Elegant Hubris* (correct seed for fire res conversion is unavailable)
- *Awakened support gems* (Elemental Focus, Awakened Elemental Damage with Attacks — zero supply)
- Mirror-tier corrupted life implicits on uniques

**Ruled out by choice:**
- *Apostate* chest (We have the gear, but chose not to use it. See Section 8).

***

## 3. Tricks & Multipliers

**Bloodscent**: Large Axe/Sword Cluster Jewel notable (Mandatory). Grants 2 Rage on Hit with Axes/Swords. Combined with 2 Rage on Melee Hit from the tree, we gain 4 Rage per hit event. With beams hitting every 0.32s and the game engine capping Rage gain at 0.5s intervals, we reach maximum Rage in ~5 seconds of combat. *Fuel the Fight* on the same cluster is a nice mana leech/attack speed bonus but is not mandatory.

**Rage Synergy**: At maximum Rage, Grey Wind applies Fire Exposure to nearby enemies. Furthermore, the Rage Mastery makes nearby enemies **Intimidated** (10% more damage taken) while you have Rage. Both effects require maximum Rage uptime, making Bloodscent load-bearing.

**Lethal Pride 10740 (Kaom)**: Socketed near Savagery. Converts small nodes into +5 Strength, and grants a 5% chance to deal double damage on both the *Golem's Blood* and *Master of the Arena* notables, acting as a ~10% more DPS multiplier.

**Skitterbots**: Permanent Shock (increased damage taken) and permanent Chill on nearby enemies. Chill enables *Hypothermia Support* (30% more damage) for bossing. The *Blight Ornament* Viridian jewel's 6% non-damaging ailment implicit makes both effects stronger.

**Wave of Conviction (CwDT)**: Auto-triggers on damage taken to apply −15% Fire Exposure. This overwrites the axe's baseline −10%. Exposures do not stack (strongest applies), but it stacks additively with Flammability.

**Double Curse**: *Flammability on Hit* (ring suffix) lowers fire resistance, while *Poacher's Mark* is enabled by the *Whispers of Doom* anoint on our Cord Belt (+1 curse limit). 

**Frenzy & Culling**: Poacher's Mark grants frenzy charges on kill. For bossing, the Mark Mastery gives a 10% chance to gain a frenzy charge on hit against marked enemies. The *Marked for Death* notable grants Culling Strike against marked enemies.

**Extra Chaos Damage**: The Foulborn Red Dream jewel grants *8% of Fire Damage as Extra Chaos Damage*. Because our amulet lacks Avatar of Fire, this damage is not deleted by the game engine and functions as a true ~8% more damage multiplier. 

**Tincture (Prismatic)**: *Increased Elemental Damage with Melee Weapons* applies to both the initial hit and Static Strike beams. Suffix: roll **Penetration** for the Void Shockwave path (Shockwaves aren't melee weapons, so penetration scales the beams/hits better) or **Attack Speed** for the Multistrike path. Use Blessed Orbs to reroll the implicit value.

**Fortify**: The Royal Plate chest implicit grants *Melee Hits have a 7% chance to Fortify*, maintaining near-permanent 20% damage reduction.

**Onslaught**: A Flagellant's Silver Flask (auto-triggers at full charges) guarantees permanent 20% increased attack/movement speed in combat. 

**Blood Rage**: Grants 14% attack speed, life leech, and frenzy on kill. The 4% maximum life per second physical degen is mitigated by our endurance charges, life leech, and the amulet's physical-taken-as-fire modifier.

***

## 3a. Life Stacking

**Tier 1 Rare Gear**: Obviously, we aim for Tier 1 Life and high Strength on every single non-unique item we equip. 

**Split Personalities**: The passive tree takes a long, winding path to maximise the passives allocated between the start location and our jewel sockets. This rewards us with massive flat life, strength, and accuracy scaling. One socket holds **Life + Strength** (scales both damage loops). The other holds **Life + Accuracy** (mandatory to cap hit chance against endgame bosses). 

**Foulborn Red Dream**: Socketed near Barbarism. Its radius effect dictates that *passives granting Fire Resistance or All Elemental Resistances also grant Maximum Life at 50% of their value*. By replacing attribute nodes in its radius with Fire Resistance tattoos, we generate extra flat life. It provides a solid chunk of life (~500 max life, raising us from ~10.8k to ~11.3k), but it isn't strictly mandatory. Because we don't have spare passive points to fully saturate its radius, it arguably provides more DPS via the 8% extra chaos damage than it does via the life conversion.

**Hunter Belt**: The *Cord Belt* base with Hunter influence. When crafting, `% increased Attributes` is somewhat better for our situation than `% increased Life`. We already have a massive increased life pool, meaning diminishing returns apply heavily to life modifiers, whereas attributes scale Str (damage/life), Int (gem requirements), and Dex (accuracy) all at once.

**Life Masteries**: We allocate 6 Life Masteries solely to trigger the powerful *10% more Maximum Life* payoff. Most of these masteries (aside from the weak +30 flat life node) do practically nothing for us on their own, but the 10% more multiplier is worth the "wasted" passive points.

**Rings**: The core ring is an Amethyst Ring featuring a fractured *Flammability on Hit* mod, giving us a free chaos resistance implicit. The eventual long-term target is to also incorporate a Vermillion Ring (highest flat life implicit). Both rings must carry the crafted -7 non-channelling mana cost prefix.

***

## 3b. Defence

**Life Double-Duty**: Every point of life adds to the HP pool while simultaneously scaling flat damage (Grey Wind) and increased damage (Rathpith). Str adds to HP while scaling damage (Iron Will). 

**Armour Stack**: Royal Plate base + Juggernaut + Bravery + Granite Flask. This armour feeds **Vaal Molten Shell**, which absorbs hits equal to 10% of armour (max 5000) before life takes damage. The CwDT setup fires the base version; the Vaal version is an on-demand panic button.

**Arctic Armour**: 21% less physical and fire damage taken from hits while stationary. Grants Freeze immunity and chills enemies that hit you.

**Vaal Impurity of Fire**: The base aura grants +51 fire res and +4 maximum fire res. The Vaal version makes your hits ignore enemy fire resistance completely — a massive situational burst of offence and defence.

**Maximum Fire Resistance Sources**:
Because Valako's Embrace propagates max fire res to cold and lightning at a 50% ratio, capping fire caps everything.
- Barbarism notable (+1)
- Chest Exarch implicit (+2)
- Tree small node id 6043 (+1)
- Prismatic Skin notable (+2 all)
- Vaal Impurity of Fire (+4)
- Ruby Flask auto-trigger (+5)
*Result: 85% baseline max fire res, pushing to 90% when Impurity is active.*

**Endurance Charges**: 5 max charges (Endurance + Stamina notables). Maintained permanently by Enduring Cry, providing 20% physical damage reduction and 20% all elemental resistances. 

**Phys taken as Fire**: The mutated Xoph's Blood amulet converts 6% of incoming physical damage from hits to fire damage. Our massive fire max res and Arctic Armour mitigate this physical damage effortlessly.

***

## 4. Four Buttons (Controller Setup)

1. **Static Strike** (Main button): Strike once, reposition. The beams do the work while you focus on mechanics. 
   - *Modifier + Main:* **Vaal Impurity of Fire**.
2. **Shield Charge** (Movement): Combat Rush (from Close Combat support) gives 20% more movement speed to travel skills after a hit.
   - *Modifier + Movement:* **Flame Dash** to cross gaps.
3. **Enduring Cry** (Utility): Provides +670 life/sec consecrated ground and endurance charges.
   - *Modifier + Utility:* **Blood Rage**.
4. **Vaal Molten Shell** (Panic / "X" Button): Huge situational survivability buffer.

***

## 5. Main Skill Variants

### 5a. Static Strike + Void Shockwave (Main Build)
**Why it works:** Static Strike beams persist for 4 seconds. You maintain 100% DPS uptime while dodging. 
**Beam Mechanics:** Beams hit exactly every 0.32s. *Attack speed does not increase beam frequency or Void Shockwave cooldown.* Beams are melee attacks (they proc Fortify and Rage) but not melee strikes. 
**Links:** Static Strike *(Cruelty)* + Void Shockwave + Inspiration + Elemental Damage with Attacks + Close Combat + **[Swap]** + Ancestral Call *(Free)*
**Socket Colours & Swaps:** If your Royal Plate is struggling with off-colours (green/blue), use an **Omen of Blanching** to guarantee white sockets and ignore colour restrictions entirely. Swap *Close Combat* for *Greater Chain* depending on crowd density and spread (Chain for clear, Close Combat for single-target). 

### 5b. Multistrike Variant
**Why it works:** Replaces Void Shockwave with *Greater Multistrike*. Attack speed becomes a priority DPS stat, as you rely on rapidly executing the physical hit combo during boss vulnerability windows. 
**Skill Options:**
- *Smite of Divine Judgement:* Best for Blight (50+ mobs) or pure face-tanking. *Note: You must stand close enough to hit the boss with the melee strike to generate Rage; the AoE portion does not grant Rage.*
- *Infernal Blow:* Unmatched for Beyond density farming due to on-death clustering explosions.
- *Static Strike of Gathering Lightning:* **Broken.** Do not use. Greater Multistrike repeats do not count as individual hits for stacking.

***

## 6. Endgame Checks & Wrong Things to Try

- **Scaling Ignite:** Rathpith and Crown of Eyes specifically scale *Attack Damage*. Ignite strictly ignores Attack Damage multipliers. An ignite pivot is mechanically impossible without rebuilding the engine.
- **Rage Decay:** The Life Mastery (Skills cost Life) does *not* count as taking damage. It will not reset the 2-second Rage decay timer. You must hit enemies.
- **Overcapping Max Res:** Do not invest in +2 max fire res on rings if you are already sitting at 85% with your Ruby Flask active. 
- **Missing Easy Min-Maxes:** Apply Sacred Orbs to all armour pieces. Upgrade to Level 4 Exceptional gems (Void Shockwave). 

***

## 7. Levelling

- **Intimidating Cry:** Excellent for early mobility (knocks back and stuns).
- **Movement:** Shield Charge + Faster Attacks + Momentum. With the attack speed scaling of the Multistrike path, this is incredibly fast.
- **Tukohama Ascendancy:** If levelling with Shield Crush, note that Shield Crush is neither a strike nor a slam. Tukohama's free links will not activate. Use Ngamahu instead (+4 Str per jewel) until you transition to Static Strike.

***

## 8. History (Peuget2 Template)

This build originates from Peuget2's Apostate life-stacker. That template utilized an *Enmity's Embrace* loop (stacking massive fire res to convert to fire penetration via *Elegant Hubris*). 

We could not replicate that here due to the PlayStation market: the required *Elegant Hubris* seed doesn't exist. Even with an *Apostate* in stash, we chose a rare Royal Plate — flat armour and Fortify keep us alive on a realistic budget (the "budget" being the astronomical cost required to push life high enough to survive *without* physical defence layers). 

***

## 9. Appendixes

### 9a. Ascendancy Choices
- **vs Hinekora:** Hinekora offers explosions (250% life as fire). Clear is already fine. Losing Sione's infinite warcry power and 632 life/sec regen is too severe a trade-off.
- **vs Ngamahu:** Ngamahu grants ~3% more life overall, but Tukohama grants a free 7th link (10% more damage unconditionally). Tukohama wins.

### 9b. Marks
Marks exist to enable frenzy generation and culling, not as primary damage layers.
- **Poacher's Mark (Chosen):** Sustained life/mana on hit for bossing; frenzy on kill for mapping.
- **Assassin's Mark:** Life on kill is useless during bossing. Power charges are wasted since Elemental Overload doesn't use crit multi.
- **Warlord's Mark:** Endurance charges already capped via Enduring Cry.

### 9c. Main Skill Supports (Imbued Skills)
- **Cruelty Imbue > Ruthless Imbue:** Cruelty grants 15% more damage to hits. Ruthless cannot apply to triggered skills (Void Shockwave) and feels terrible on a hit-and-run playstyle. 
- **Mana Cost:** Level 1 Cruelty adds a 140% cost multiplier. This is why dual -7 non-channelling mana cost ring crafts are mandatory.

### 9d. Enduring Cry Supports
*Current:* Blessed Call (imbue) + More Duration + Urgent Orders + CDR Support. 
Blessed Call adds a CDR penalty, which CDR Support cancels out perfectly. Next league (when imbues are gone), simply run Urgent Orders + Blessed Call + More Duration. 

### 9e. CwDT Options
*Current:* Vaal Molten Shell + Wave of Conviction + CwDT L11.
Do not use Withering Step here. CwDT is reactive; Withering Step requires proactive casting and fails if you are already Elusive. Keep Frost Bomb in your inventory for high-regen map mods or Uber Lab.

### 9f. Axe Enchant Options
- **AoE (Chosen):** Increases beam chain reach and overlap radius. Also buffs Smite and Infernal Blow.
- **Attack Speed:** Only buffs the initial hit, not the beams.
- *(Note: We attempted Tempering Orbs for increased fire effect. 10 Divines later, we reverted to the Lifeforce AoE enchant. Not recommended).*

### 9g. Mirage League Borrowed Power
- **Cord Belt:** A Mirage league base that can be Anointed (giving us Whispers of Doom). 
- **Catalysts:** The crafted *Increased Elemental Damage with Attack Skills* on the belt can be further enhanced by Dextral (Attack) catalysts. 
- **Volatile Vaal Orbs:** Could theoretically push Grey Wind's 12% life implicit to a higher tier or add a second implicit. 

### 9h. Ring Crafting
Target an **Amethyst Ring** base (the chaos res implicit acts as a free affix slot). Fracture *Flammability on Hit* on a good base first, then use recombinators to hit high Life and Attributes. Finish with the mandatory -7 mana cost bench craft.
