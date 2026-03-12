# Mirage League (3.28) — 40 Challenges

Reward milestones: **12** = Orb Regalia Boots, **20** = Gloves, **28** = Body Armour, **36** = Helmet.
Totem pole decoration pieces awarded throughout.

[verified 2026-03 via u4n/poedb/poewiki]

---

## Tier 1 — Early (Campaign)

1. **Beginner's Basics** — Use Orb of Transmutation, Alteration, Augmentation, and Alchemy at least once each.

2. **Mysterious Mirages** — Complete the Mirage mechanic: choose a wish, enter a Mirage portal, break an Astral Chain.

3. **Peddler's Produce I** — Obtain flasks and jewellery through vendor recipes.

4. **Act Adversaries I** — Defeat final bosses of Acts 1–5 (Merveil, Vaal Oversoul, Dominus, Malachai, Kitava).

5. **Beneficial Bounties** — Complete four specific quests across Acts 1–4.

6. **Desecrated Djinn** — Choose wishes 5 times, defeat 10 rare Mirage monsters, break 15 Astral Chains.

7. **Act Adversaries II** — Defeat final bosses of Acts 6–10.

8. **Helpful Hideaways** — Visit seven specific areas (including Aspirant's Plaza, Rogue Harbour).

9. **Added Accessories** — Complete 30 encounters each from any 3 of: Essences, Strongboxes, Shrines, Possessed monsters, Rogue Exiles, Beyond.

10. **Atlas Additions** — Complete 30 encounters each from any 5 of 10 league mechanics (Abysses, Expeditions, Harvest, Legion, Blights, etc.).

---

## Tier 2 — Mid Game (Atlas)

11. **Master Missives** — Complete 30 missions from any 2 Master encounter types in Tier 11+ maps.

12. **Sacred Sigils** — Choose wishes using each of the three Djinn sigils (Navira, Kelari, Ruzhan) 50 times each.

13. **Cartographer's Courage** — Complete a rare map of each tier from Tier 1 to Tier 16.

14. **Crafting Craze** — Use 15 different currency item types a specified number of times each.

15. **Maniacal Monsters** — Defeat 200 map bosses in rare maps with 80%+ Item Quantity.

16. **Deadly Deeds** — Complete any 5 of 10 endgame encounters in area level 81+ zones.

17. **Empowered Encounters** — Complete any 4 league mechanics inside Mirages the required number of times each.

18. **Achieve Ascension** — Use the Ascendancy Device in all four Labyrinths and gain a Bloodline class.

19. **Potent Premonitions** — Turn in divination cards granting currency, gems, unique items, and six-linked items.

20. **Peddler's Produce II** — Obtain unique items and influenced items through vendor recipes.

---

## Tier 3 — Endgame Encounters

21. **Lethal Leaders** — Defeat any 6 of 8 specific bosses at area level 80+ (Atziri, Abyssal Lich, Izaro, etc.).

22. **Coveted Currency** — Use any 7 of the Mirage-specific currency/crafting items the required number of times.

23. **Remarkable Realms** — Complete all 17 unique maps.

24. **Succinct Scarabs** — Complete rare Tier 14+ maps with any 8 different scarab types, 30 times each.

25. **Glorious Gemcraft** — Complete any 3 of 4 gem tasks:
    - Corrupt gems
    - Use Prism items
    - Achieve a quality total across gems *(see note below)*
    - Level exceptional gems (Empower/Enlighten/Enhance)

26. **Cross Contamination** — Complete any 4 combined league mechanic encounters (two mechanics simultaneously).

27. **Wishful Willing** — Select any 13 of the 20 available Mirage wishes.

28. **Seized Strength** — Defeat any 7 of 11 specific bosses (Trialmaster, Oshabi, Catarina, Simulacrum, etc.).

29. **Atlas Astrolabes** — Complete rare Tier 14+ maps in 4 Astrolabe regions, 30 times each.

30. **Tyrannical Tiers** — Accumulate 8,000 total map tiers completed.

---

## Tier 4 — Late Endgame

31. **Magnificent Memories** — Complete rare Originator-influenced maps totalling 2,500% Item Quantity.

32. **Sandswept Survivor** — Break 150 Astral Chains in rare Tier 14+ maps with 100%+ Item Quantity.

33. **Eldritch Evocation** — Defeat 100 Maven-witnessed map bosses OR activate 200 Eldritch Altars in Astrolabe maps.

34. **Vaulted Valuables** — Collect any 3 reward types from Memory Vaults 5 times each.

35. **Instigative Invitations** — Complete all 8 endgame invitations each with at least 4 modifiers.

36. **Nightmare Nemeses** — Complete any 4 Tier 17 (Nightmare) maps with 175%+ Item Quantity.

37. **Weeping Warlords Warfare** — Defeat Saresh (Mirage pinnacle boss) in three specific ways avoiding certain mechanics.

38. **Tremendous Tempests** — Slay map bosses in 75 rare Tier 16 Astrolabe maps with 150%+ Item Quantity.

39. **Uber Undertaking** — Defeat any 5 of 10 Uber pinnacle bosses (Uber Atziri, Uber Elder, Uber Maven, etc.) at area level 85.

40. **Gallant Grinding Goals** — Complete any 4 heavy grind tasks: reach level 100, accumulate Divine Font uses, complete 500 Tier 16 maps, etc.

---

## Notes for Build Planning

### Challenge 25 — Glorious Gemcraft: quality total sub-task
The "achieve a quality total" sub-task counts across all gems on the character. With 15+ gems at 20% quality, this is easily cleared without any special gems. A 20/23 gem contributes only +3% over a normal 20% gem — irrelevant for this challenge.

### Challenge 22 — Coveted Currency
Requires using Mirage-specific currencies. Relevant ones:
- **Coin of Restoration** — restores Afarud unique to Maraketh form
- **Coin of Desecration** — twists Maraketh unique to Afarud form, adding a corruption implicit
- **Coin of Power / Knowledge / Skill** — imbues a level 20 skill gem with a random support effect
- **Dextral / Sinistral Catalyst** — quality catalysts enhancing suffixes / prefixes

### Challenge 25 — exceptional gem leveling sub-task
Requires leveling Empower, Enlighten, or Enhance. Having them in a 9-socket gem leveling swap counts. See `audit_state.py analyze-swap` for swap setup evaluation.

---

## Mirage-Specific Item Pairs (Coin of Restoration)

| Afarud form (drops in Mirage) | Maraketh form (after Coin of Restoration) |
|---|---|
| Khatal's Weeping | Khatal's Geyser |
| Fleshrender | Skysunder |
| The Bane of Hope | The Flame of Hope |
| The Desecrated Chalice | The Sacred Chalice |
| Saresh's Darkness | Solerai's Radiance |

**Foulborn items**: Using Coin of Desecration on a Maraketh unique converts it to Afarud form with a corruption implicit. Using Coin of Restoration on *that* item restores it to Maraketh form while **preserving the corruption implicit**. Result: a Maraketh unique with a corruption implicit — the most valuable state.
