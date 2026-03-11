# Ascendancy: Chieftain

## Fire Resistance Stacking Defense (Tasalio + Valako)

- **Tasalio:** Fire resistance also applies 50% to cold and lightning resistance. Also grants **ignite immunity** — no need for ignite immunity on flasks or gear.
- **Valako:** Maximum fire resistance also applies as cold and lightning maximum resistance

Combined: stacking fire res (via Purity of Fire) covers all three elemental resistances. Significant gear budget savings — you need much less cold/lightning res on items.

**Overcap fire res generously** — blue altars (Eater of Worlds) and map mods can reduce resistances by 20–30%. With Tasalio, fire overcap also protects cold and lightning. Target 30%+ overcap for comfortable atlas farming.

When Purity of Fire is swapped out, verify elemental resistances don't drop below cap.

---

## Ngamahu

- "Passives in radius of non-unique jewels also apply their damage bonuses as fire damage"
- **Primary practical use: +4 Strength per non-unique jewel socketed in regular passive tree jewel sockets within radius**
- **Ngamahu does NOT apply to jewels socketed inside cluster jewel sockets** — only regular tree sockets count
- Converts **any** non-fire damage bonuses (physical, cold, lightning, chaos) on passives in radius to also apply as fire — for fire builds this is a pure benefit; for non-fire builds (e.g. Brutality physical) the converted fire is wasted
- Place unique jewels (Lethal Pride etc.) in sockets where a non-unique jewel would waste the conversion — only relevant for non-fire builds

---

## Sione

- Warcries have infinite power — max stacks immediately on use, no enemies required
- 30% increased warcry buff effect

---

## Lethal Pride (Kaom) — Timeless Jewel

- Adds stats to nodes in radius (does NOT replace existing stats)
- Only keystones in radius are replaced — if no keystones in radius, the jewel is purely additive
- Use `timeless_jewel_analysis.py` to calculate exact effects for a given seed + socket:
  ```
  python timeless_jewel_analysis.py <char_json> <slot_index> Kaom <seed>
  ```
- The `"keystone"` field in the CLI output is what WOULD happen to a keystone if one existed in the radius — it is NOT granted to the character unconditionally. If no keystone node is in the radius, the keystone has no effect.
