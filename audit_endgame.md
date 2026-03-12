# Endgame Build Audit Checklist

Ordered roughly by accessibility — earlier sections apply at all stages, later sections require significant investment. Check in order and stop where currency runs out.

---

## 1. Fundamentals (Always)

### Passive Tree
- [ ] All available passive points allocated (level 95 = 117 points; push to 95 before optimizing gear)
- [ ] Every mastery wheel has its mastery choice selected — unselected masteries are free stats being wasted
- [ ] Anoint on amulet: optimal notable for the build
- [ ] Anoint on Cord Belt (if equipped, Mirage league+): second optimal notable
- [ ] Timeless jewel analysis run — see Build Audit Procedure in skill.md

### Ascendancy and Labs
- [ ] All 4 ascendancy points allocated (all 4 lab difficulties completed)
- [ ] Bandits choice is optimal for the build (Kill All = 2 passive points; Alira = crit multi + res; Oak = life regen + phys reduction; Kraityn = attack speed + dodge)

### Resistances
- [ ] All elemental resistances capped (75%, or higher with Purity auras)
- [ ] Chaos resistance capped or close
- [ ] Resistances overcapped by 20–30%+ for blue altar mods and map mods that reduce resistances — fire overcap is especially valuable for Chieftain (Tasalio converts to cold/lightning)

### Gem Links
- [ ] Main skill is in a 6-link
- [ ] All supports have a green checkmark in PoB (actually applying to the skill)
- [ ] No support gem sitting at level 1 when it should be leveled (especially Impale Support, Empower, damage supports)
- [ ] CwDT setups: triggered gem level ≤ CwDT's supported gem level cap — if triggered gem is too high level, it never fires

### Aura Budget
- [ ] All aura/reservation slots are filled — no spare reservation going unused
- [ ] If any slot is borderline, check if a mana reservation efficiency anoint would open an additional slot

---

## 2. Mid-League Optimization

### Flasks
- [ ] All 5 flask slots filled with appropriate types for the build
- [ ] Each flask has **3 charges on hit** or equivalent sustain prefix (keeps flasks active during combat)
- [ ] Suffixes provide ailment immunity for gaps not covered elsewhere (freeze, shock, etc.) or high-value utility (increased effect, reduced charges used)
- [ ] Useful suffix rolls are high tier — check the roll range
- [ ] All flasks are at 20% quality
- [ ] Flask effects don't duplicate each other or conflict with build mechanics:
  - Builds with belts that modify flask behavior (e.g. Mageblood, Petrified Blood interactions) require different setup
  - Granite/Jade flasks are weaker if the build already has massive armour/evasion
  - Life/mana flasks may be redundant with strong leech or regen — replace with utility

### Items — Affixes
- [ ] Every rare item has 6 affixes (3 prefix + 3 suffix) — no empty slots unless intentionally held open for a specific bench craft during an ongoing crafting process
- [ ] No dead mods for the build (e.g. "damage with one-handed weapons" on Shield Crush, crit multi without crit)

### Eldritch Implicits (Eater/Exarch)
- [ ] All eligible items (non-unique, non-influenced, non-corrupted armour pieces) have both Eater and Exarch implicits
- [ ] Implicits are build-relevant — check the pool for each slot before rolling
- [ ] Rolls are not the minimum tier — re-roll low values if the mod matters

### Catalysts
- [ ] Rings, amulet, and belt are at 20% quality using the correct catalyst type for the build's key mods
- [ ] Apply catalyst BEFORE crafting to get higher mod values

### Gear Quality
- [ ] All items are at 20% quality (armour and weapons especially — quality on a weapon increases local physical damage)

### Socket Colors
- [ ] Socket colors are optimal for the support setup — off-colors are acceptable only if the DPS gain justifies the crafting cost
- [ ] Check if remaining off-colors can be fixed with Jeweller's Touch / Vorici bench without losing links

### Pantheon
- [ ] Major god choice is synergistic with the build's defenses (e.g. Lunaris for dodge builds, Brine King for stun immunity if needed)
- [ ] Minor god choice covers a weakness not handled elsewhere
- [ ] All useful **divine vessel upgrades** are unlocked — each god has expanded powers after completing the divine vessel for its map boss. Unlocking all options lets you swap situationally.

---

## 3. Endgame Optimization

### Gems — 20/20 and Beyond
- [ ] All active skill gems at level 20, 20% quality minimum
- [ ] All support gems at level 20, 20% quality minimum
- [ ] Key active skill gems: attempt corruption for level 21 (21/20 is standard endgame)
- [ ] **Alternate quality** (Anomalous/Divergent/Phantasmal): these are not upgrades — they change the gem's behavior entirely. Use only when the specific behavior is what the build wants. Check each key gem's alternate versions to see if any variant's mechanic is better suited than the normal version for the build. Do not default to alt quality; default to normal and swap only with reason.
- [ ] Vaal versions of active skills where relevant (Vaal Molten Shell, Vaal Ancestral Warchief, etc.)

### Jewels
- [ ] All jewel sockets on the passive tree are filled
- [ ] All abyssal sockets on gear are filled
- [ ] Jewel mods are all relevant — no dead mods (see Build Audit Procedure for timeless jewels)
- [ ] Timeless jewel in place with correct seed/position for the build (see timeless_jewel_analysis.py)

### Cluster Jewels
- [ ] Large cluster jewels: enchant and notables are best available for the build
- [ ] Medium cluster jewels: notables provide mods orthogonal to what tree already provides (not stacking into already-large additive pools)
- [ ] Small cluster jewels in medium cluster sockets: useful notables, not filler

### Item Implicits — Completion
- [ ] All eligible non-unique items have both Eater and Exarch implicits at good tiers
- [ ] Check pool for each slot — some slots have build-defining implicits (e.g. gloves: ignore enemy phys reduction; helmet: supported by X gem)

---

## 4. Late Endgame

### Corrupted Items
- [ ] Key items have useful corruption implicits — especially body armour (+1 to socketed gems, culling strike), weapon (+1 gems, %phys), helmet (+2 to socketed support gems, culling)
- [ ] Corrupted 6-link body armour with a good implicit is significantly stronger than uncorrupted equivalent
- [ ] Double-corrupt (Tempered by War/Suffering/Misery via temple) for high-variance bis outcomes on key pieces

### Forbidden Flesh / Forbidden Flame
- [ ] Pair of jewels granting an ascendancy notable from another class — check which ascendancy notables from other classes would most benefit the build
- [ ] Expensive and high-variance to acquire; plan which one to target before investing

### Awakened Support Gems
- [ ] Awakened versions of key supports: Awakened Brutality, Awakened Melee Physical Damage, Awakened Multistrike, Awakened Impale, etc.
- [ ] Each awakened gem is +1 level over the base and has an additional bonus effect at gem level 5
- [ ] Prioritize awakened versions of the supports that provide the most "more" multiplier in the main link

---

## 5. Mirror Tier

### Gems
- [ ] Key active gems: 21/23 (level 21 via corruption + 23% quality via corrupt or alternate quality base)
- [ ] Key supports: 20/23 or awakened at level 5
- [ ] Empower level 4 in appropriate links

### Items
- [ ] Every slot: mirror-tier crafted base with optimal influence combination and perfect rolls
- [ ] All items double-corrupted with two useful implicits
- [ ] Influenced item combinations (e.g. Shaper+Elder, Crusader+Warlord) for the strongest possible mod combinations per slot

---

## Notes

- Flask and aura behavior changes significantly with Mageblood (flasks are always active), Petrified Blood, and similar uniques — adjust checklist accordingly
- On PlayStation (Sony realm): no public price data — assess item value via in-game trade search, not poe.ninja
- Lab enchants no longer exist in current PoE — do not reference helmet/boot/glove enchants from the Divine Font
