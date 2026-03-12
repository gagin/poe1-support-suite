#!/usr/bin/env python3
"""
Manage per-character build audit state.

Each check tracks: status (unknown/verified/stale/na), last verified snapshot,
date, and notes. When a diff is applied, checks whose dependencies include
any changed component are marked stale.

Usage:
    python audit_state.py init   <expanded.json>            # create audit state
    python audit_state.py update <diff.json>                # apply diff, mark stale
    python audit_state.py verify <audit.json> <check_id>    # mark check verified
                                 [--notes "text"]
    python audit_state.py status <audit.json>               # show all checks
    python audit_state.py todo   <audit.json>               # show stale/unknown only

Audit state is saved as <CharName>_audit.json in the current directory.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Dependency map — which component categories affect each check
# Categories: equipment, passive_tree, jewels, gems, flasks
# ---------------------------------------------------------------------------
CHECKS = {
    # Tier 1 — Fundamentals
    "passive_points": {
        "label": "All passive points allocated (target: level 95)",
        "depends": ["passive_tree"],
        "tier": 1,
    },
    "masteries_complete": {
        "label": "Every mastery wheel has a choice selected",
        "depends": ["passive_tree"],
        "tier": 1,
    },
    "anoints": {
        "label": "Anoints on amulet and Cord Belt are optimal",
        "depends": ["equipment", "passive_tree"],
        "tier": 1,
    },
    "ascendancy": {
        "label": "All 4 ascendancy points allocated",
        "depends": ["passive_tree"],
        "tier": 1,
    },
    "bandits": {
        "label": "Bandit choice is optimal for the build",
        "depends": ["passive_tree"],
        "tier": 1,
    },
    "resistance_cap": {
        "label": "All elemental resistances capped (75% or higher with Purity auras)",
        "depends": ["equipment", "passive_tree", "jewels"],
        "tier": 1,
    },
    "chaos_resistance": {
        "label": "Chaos resistance capped or close",
        "depends": ["equipment", "passive_tree", "jewels"],
        "tier": 1,
    },
    "resistance_overcap": {
        "label": "Resistances overcapped 20-30%+ for blue altars and map mods",
        "depends": ["equipment", "passive_tree", "jewels"],
        "tier": 1,
    },
    "main_skill_6link": {
        "label": "Main skill is in a 6-link",
        "depends": ["equipment"],
        "tier": 1,
    },
    "supports_valid": {
        "label": "All supports apply to skill (green checkmark in PoB)",
        "depends": ["gems", "equipment"],
        "tier": 1,
    },
    "cwdt_ratios": {
        "label": "CwDT: triggered gem levels are within supported range",
        "depends": ["gems"],
        "tier": 1,
    },
    "aura_budget": {
        "label": "Main-hand set: all reservation slots filled — no spare reservation unused",
        "depends": ["gems", "passive_tree", "equipment"],
        "tier": 1,
    },
    # Tier 2 — Mid-League
    "swap_setup": {
        "label": "Weapon swap: active mechanic OR optimal gem-leveling setup (9-socket, item quality, no maxed/attribute-blocked gems)",
        "depends": ["equipment", "gems"],
        "tier": 2,
    },
    "flask_setup": {
        "label": "Flasks: 3 charges on hit, useful suffixes, 20% quality, no conflicts",
        "depends": ["flasks", "equipment"],
        "tier": 2,
    },
    "item_affixes_complete": {
        "label": "All rare items have 6 affixes — no wasted slots",
        "depends": ["equipment"],
        "tier": 2,
    },
    "eater_exarch_implicits": {
        "label": "All eligible items have both Eater and Exarch implicits at good tiers",
        "depends": ["equipment"],
        "tier": 2,
    },
    "catalyst_quality": {
        "label": "Rings, amulet, belt at 20% quality with correct catalyst type",
        "depends": ["equipment"],
        "tier": 2,
    },
    "gear_quality": {
        "label": "All items at 20% quality",
        "depends": ["equipment"],
        "tier": 2,
    },
    "socket_colors": {
        "label": "Socket colors are optimal for support setup",
        "depends": ["equipment"],
        "tier": 2,
    },
    "pantheon": {
        "label": "Pantheon: synergistic major/minor gods, all useful divine vessel upgrades unlocked",
        "depends": [],  # external — manual only
        "tier": 2,
    },
    # Tier 3 — Endgame
    "gem_levels_quality": {
        "label": "Key gems 20/20+; attempt corruption for 21/20 on main active skills",
        "depends": ["gems"],
        "tier": 3,
    },
    "vaal_gems": {
        "label": "Vaal versions of applicable skills present (Vaal Molten Shell etc.)",
        "depends": ["gems"],
        "tier": 3,
    },
    "transfigured_gems": {
        "label": "Transfigured variants checked for key skills — use if mechanic is better",
        "depends": ["gems"],
        "tier": 3,
    },
    "jewels_filled": {
        "label": "All jewel sockets on tree filled; all abyssal sockets on gear filled",
        "depends": ["jewels", "passive_tree"],
        "tier": 3,
    },
    "jewel_mods": {
        "label": "Jewel mods are relevant — no dead mods for the build",
        "depends": ["jewels"],
        "tier": 3,
    },
    "timeless_jewel": {
        "label": "Timeless jewel analysis run: keystone check, allocated bonuses, unallocated pathing",
        "depends": ["jewels", "passive_tree"],
        "tier": 3,
    },
    "cluster_jewels": {
        "label": "Cluster jewel enchants and notables are optimal",
        "depends": ["jewels"],
        "tier": 3,
    },
    # Tier 4 — Late Endgame
    "corrupted_items": {
        "label": "Key items have useful corruption implicits (chest: +1 gems, culling, etc.)",
        "depends": ["equipment"],
        "tier": 4,
    },
    "forbidden_jewels": {
        "label": "Forbidden Flesh/Flame considered — best ascendancy notable from another class",
        "depends": ["jewels"],
        "tier": 4,
    },
    "awakened_gems": {
        "label": "Awakened support gems for key supports in main link",
        "depends": ["gems"],
        "tier": 4,
    },
    # Tier 5 — Mirror Tier
    "gems_21_23": {
        "label": "Key active gems at 21/23; key supports 20/23 or awakened L5",
        "depends": ["gems"],
        "tier": 5,
    },
    "items_double_corrupted": {
        "label": "Key items double-corrupted with two useful implicits",
        "depends": ["equipment"],
        "tier": 5,
    },
    "influenced_items_optimal": {
        "label": "Mirror-tier crafted bases with optimal influence combinations per slot",
        "depends": ["equipment"],
        "tier": 5,
    },
}

TIER_LABELS = {1: "Fundamentals", 2: "Mid-League", 3: "Endgame", 4: "Late Endgame", 5: "Mirror Tier"}
STATUS_SYMBOLS = {"verified": "✓", "stale": "!", "unknown": "?", "na": "-"}


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def state_path(char_name):
    return Path(f"{char_name}_audit.json")


def load_state(path):
    with open(path) as f:
        return json.load(f)


def save_state(state, path):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)


def init_state(char_name, snapshot_path):
    checks = {}
    for check_id, meta in CHECKS.items():
        checks[check_id] = {
            "status": "unknown",
            "last_verified_snapshot": None,
            "last_verified_date": None,
            "notes": "",
        }
    return {
        "character": char_name,
        "current_snapshot": str(snapshot_path),
        "last_updated": datetime.now().isoformat(timespec='seconds'),
        "checks": checks,
    }


def apply_diff(state, diff):
    """Mark checks stale based on which components changed in the diff."""
    changed_components = set(diff.get('changes', {}).keys())

    stale_checks = []
    for check_id, meta in CHECKS.items():
        if state['checks'][check_id]['status'] == 'na':
            continue
        if any(dep in changed_components for dep in meta['depends']):
            if state['checks'][check_id]['status'] == 'verified':
                state['checks'][check_id]['status'] = 'stale'
                stale_checks.append(check_id)

    state['current_snapshot'] = diff['to']
    state['last_updated'] = datetime.now().isoformat(timespec='seconds')
    return stale_checks


# ---------------------------------------------------------------------------
# Weapon swap analysis
# ---------------------------------------------------------------------------

SWAP_SLOTS = {'Weapon2', 'Offhand2'}
MAIN_SLOTS = {'Weapon', 'Offhand'}

# Uniques known to provide active mechanics when swapped to (not gem leveling)
ACTIVE_SWAP_UNIQUES = {
    "Victario's Charity",       # frenzy/power charges on kill
    "Heartbound Loop",          # minion life triggers
    "Geofri's Sanctuary",       # ES recovery
    "The Surrender",            # reckoning proc
    "Echoforge",                # warcry enchant stacks
}


def load_raw_pob(path):
    with open(path) as f:
        d = json.load(f)
    # Support both top-level list of items and nested structure
    items = d.get('items', {})
    if isinstance(items, dict):
        return items.get('items', [])
    return items


def gem_level(socketed_item):
    for p in socketed_item.get('properties', []):
        if p['name'] == 'Level' and p.get('values'):
            val = p['values'][0][0]
            return int(val.split()[0]) if val else 1
    return 1


def gem_quality(socketed_item):
    for p in socketed_item.get('properties', []):
        if p['name'] == 'Quality' and p.get('values'):
            val = p['values'][0][0].strip('+%')
            try:
                return int(val)
            except ValueError:
                return 0
    return 0


def item_quality(item):
    for p in item.get('properties', []):
        if p['name'] == 'Quality' and p.get('values'):
            val = p['values'][0][0].strip('+%')
            try:
                return int(val)
            except ValueError:
                return 0
    return 0


def analyze_swap(raw_pob_path):
    """Return (swap_type, findings_list, recommended_note)."""
    items = load_raw_pob(raw_pob_path)
    swap_items = [i for i in items if isinstance(i, dict) and i.get('inventoryId') in SWAP_SLOTS]

    if not swap_items:
        return 'empty', ['No items in weapon swap.'], 'Swap is empty — no gem leveling or active mechanic setup.'

    findings = []

    # Detect active mechanic swap
    active_uniques = [i for i in swap_items if i.get('name', '') in ACTIVE_SWAP_UNIQUES]
    if active_uniques:
        for u in active_uniques:
            findings.append(f"Active mechanic unique in swap: {u['name']}")
        return 'active', findings, 'Active mechanic swap: ' + ', '.join(u['name'] for u in active_uniques) + ' — verify the mechanic is functional and intentional.'

    # Detect 9-socket setup: look for Maloney's Mechanism or any bow in offhand2
    has_maloneys = any(i.get('name') == "Maloney's Mechanism" for i in swap_items)
    total_sockets = sum(len(i.get('sockets', [])) for i in swap_items)

    # Gem inventory
    all_swap_gems = []
    for item in swap_items:
        inv_id = item.get('inventoryId', '?')
        item_q = item_quality(item)
        item_name = item.get('name') or item.get('typeLine', '?')
        sockets = len(item.get('sockets', []))
        findings.append(f"{inv_id}: {item_name} — {sockets} sockets, {item_q}% quality")
        if item_q < 20:
            findings.append(f"  ↳ Item at {item_q}% quality — gem XP penalty; bring to 20% for full gem leveling speed")
        for gem in item.get('socketedItems', []):
            lvl = gem_level(gem)
            qual = gem_quality(gem)
            name = gem.get('typeLine', '?')
            is_support = gem.get('support', False)
            all_swap_gems.append({'name': name, 'level': lvl, 'quality': qual, 'support': is_support})

    findings.append(f"Total swap sockets: {total_sockets}{' (9-socket setup via Maloney\'s)' if has_maloneys else ''}")

    if not all_swap_gems:
        findings.append("No gems socketed in swap items.")
        return 'leveling', findings, '\n'.join(findings)

    # Flag maxed gems (wasting XP)
    maxed = [g for g in all_swap_gems if g['level'] >= 20]
    if maxed:
        findings.append(f"Maxed gems wasting XP ({len(maxed)}): " + ', '.join(f"{g['name']} L{g['level']}" for g in maxed))
        findings.append("  ↳ Replace maxed gems with unleveled ones to use this XP efficiently")

    # Gems not yet maxed (being actively leveled)
    leveling = [g for g in all_swap_gems if g['level'] < 20]
    if leveling:
        findings.append("Gems being leveled: " + ', '.join(f"{g['name']} L{g['level']}" for g in leveling))
        findings.append("  ↳ Check in-game that none are stopped by attribute requirements")

    note = f"Gem leveling swap — {total_sockets} total sockets"
    if has_maloneys:
        note += " (9-socket via Maloney's)"
    if maxed:
        note += f"; {len(maxed)} maxed gems wasting XP"
    any_low_quality = any(item_quality(i) < 20 for i in swap_items)
    if any_low_quality:
        note += "; some items below 20% quality"

    return 'leveling', findings, note

def cmd_init(args):
    expanded = Path(args.expanded)
    if not expanded.exists():
        print(f"File not found: {expanded}")
        sys.exit(1)

    with open(expanded) as f:
        data = json.load(f)
    char_name = data.get('character', {}).get('name', expanded.stem.split('_')[0])

    path = state_path(char_name)
    if path.exists() and not args.force:
        print(f"Audit state already exists: {path}")
        print("Use --force to reinitialize.")
        sys.exit(1)

    state = init_state(char_name, expanded)
    save_state(state, path)
    print(f"Initialized audit state: {path}")
    print(f"  Character: {char_name}")
    print(f"  Snapshot:  {expanded.name}")
    print(f"  {len(CHECKS)} checks — all status: unknown")


def cmd_update(args):
    diff_file = Path(args.diff)
    if not diff_file.exists():
        print(f"Diff file not found: {diff_file}")
        sys.exit(1)

    with open(diff_file) as f:
        diff = json.load(f)

    char_name = diff['character']
    path = state_path(char_name)
    if not path.exists():
        print(f"No audit state found for {char_name}. Run 'init' first.")
        sys.exit(1)

    state = load_state(path)
    stale = apply_diff(state, diff)
    save_state(state, path)

    if not diff.get('changes'):
        print("No changes in diff — audit state unchanged.")
        return

    print(f"Applied diff for {char_name}")
    print(f"Changed components: {', '.join(diff['changes'].keys())}")
    if stale:
        print(f"\nMarked stale ({len(stale)}):")
        for check_id in stale:
            print(f"  ! {check_id}: {CHECKS[check_id]['label']}")
    else:
        print("No previously-verified checks affected.")


def cmd_analyze_swap(args):
    raw_path = Path(args.raw)
    if not raw_path.exists():
        print(f"Raw PoB JSON not found: {raw_path}")
        sys.exit(1)

    swap_type, findings, note = analyze_swap(raw_path)

    print(f"=== Weapon Swap Analysis ===")
    print(f"Type: {swap_type}\n")
    for line in findings:
        print(f"  {line}")
    print(f"\nRecommended note for swap_setup:\n  {note}")

    if args.audit:
        audit_path = Path(args.audit)
        if not audit_path.exists():
            print(f"\nAudit state not found: {audit_path} — skipping auto-note")
            return
        state = load_state(audit_path)
        if 'swap_setup' not in state['checks']:
            state['checks']['swap_setup'] = {"status": "unknown", "last_verified_snapshot": None, "last_verified_date": None, "notes": ""}
        state['checks']['swap_setup']['notes'] = note
        save_state(state, audit_path)
        print(f"\nNote saved to swap_setup in {audit_path}")


def cmd_verify(args):
    path = Path(args.audit)
    if not path.exists():
        print(f"Audit state not found: {path}")
        sys.exit(1)

    state = load_state(path)
    check_id = args.check_id

    if check_id not in CHECKS:
        print(f"Unknown check: {check_id}")
        print(f"Valid checks: {', '.join(CHECKS.keys())}")
        sys.exit(1)

    state['checks'][check_id].update({
        "status": "verified",
        "last_verified_snapshot": state['current_snapshot'],
        "last_verified_date": datetime.now().isoformat(timespec='seconds'),
        "notes": args.notes or state['checks'][check_id].get('notes', ''),
    })
    save_state(state, path)
    print(f"✓ {check_id}: {CHECKS[check_id]['label']}")
    if args.notes:
        print(f"  Notes: {args.notes}")


def cmd_na(args):
    path = Path(args.audit)
    if not path.exists():
        print(f"Audit state not found: {path}")
        sys.exit(1)

    state = load_state(path)
    check_id = args.check_id

    if check_id not in CHECKS:
        print(f"Unknown check: {check_id}")
        print(f"Valid checks: {', '.join(CHECKS.keys())}")
        sys.exit(1)

    state['checks'][check_id].update({
        "status": "na",
        "notes": args.notes or state['checks'][check_id].get('notes', ''),
    })
    save_state(state, path)
    print(f"- {check_id}: marked N/A")
    if args.notes:
        print(f"  Notes: {args.notes}")


def cmd_note(args):
    path = Path(args.audit)
    if not path.exists():
        print(f"Audit state not found: {path}")
        sys.exit(1)

    state = load_state(path)
    check_id = args.check_id

    if check_id not in CHECKS:
        print(f"Unknown check: {check_id}")
        print(f"Valid checks: {', '.join(CHECKS.keys())}")
        sys.exit(1)

    state['checks'][check_id]['notes'] = args.notes
    save_state(state, path)
    print(f"? {check_id}: note added")
    print(f"  {args.notes}")


def cmd_status(args, todo_only=False):
    path = Path(args.audit)
    if not path.exists():
        print(f"Audit state not found: {path}")
        sys.exit(1)

    state = load_state(path)
    print(f"Character: {state['character']}")
    print(f"Snapshot:  {Path(state['current_snapshot']).name}")
    print(f"Updated:   {state['last_updated']}\n")

    counts = {"verified": 0, "stale": 0, "unknown": 0, "na": 0}
    current_tier = None

    for check_id, meta in CHECKS.items():
        check = state['checks'].get(check_id, {"status": "unknown"})
        status = check['status']
        counts[status] = counts.get(status, 0) + 1

        if todo_only and status not in ('stale', 'unknown'):
            continue

        tier = meta['tier']
        if tier != current_tier:
            current_tier = tier
            print(f"── Tier {tier}: {TIER_LABELS[tier]} ──")

        sym = STATUS_SYMBOLS.get(status, '?')
        line = f"  [{sym}] {check_id}: {meta['label']}"
        if check.get('notes'):
            line += f"\n       {check['notes']}"
        if status == 'stale' and check.get('last_verified_snapshot'):
            line += f"\n       (last verified: {Path(check['last_verified_snapshot']).name})"
        print(line)

    if not todo_only:
        print(f"\nSummary: {counts.get('verified',0)} verified, "
              f"{counts.get('stale',0)} stale, "
              f"{counts.get('unknown',0)} unknown, "
              f"{counts.get('na',0)} n/a")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Build audit state manager")
    sub = parser.add_subparsers(dest='command')

    p_init = sub.add_parser('init', help='Initialize audit state from expanded JSON')
    p_init.add_argument('expanded', help='Path to expanded character JSON')
    p_init.add_argument('--force', action='store_true', help='Overwrite existing state')

    p_update = sub.add_parser('update', help='Apply a diff, marking dependent checks stale')
    p_update.add_argument('diff', help='Path to diff JSON (from build_differ.py)')

    p_verify = sub.add_parser('verify', help='Mark a check as verified')
    p_verify.add_argument('audit', help='Path to audit state JSON')
    p_verify.add_argument('check_id', help='Check ID to mark verified')
    p_verify.add_argument('--notes', help='Optional notes', default='')

    p_na = sub.add_parser('na', help='Mark a check as not applicable')
    p_na.add_argument('audit', help='Path to audit state JSON')
    p_na.add_argument('check_id', help='Check ID to mark N/A')
    p_na.add_argument('--notes', help='Optional notes', default='')

    p_note = sub.add_parser('note', help='Add notes to a check without changing its status')
    p_note.add_argument('audit', help='Path to audit state JSON')
    p_note.add_argument('check_id', help='Check ID')
    p_note.add_argument('notes', help='Notes text')

    p_swap = sub.add_parser('analyze-swap', help='Analyze weapon swap (gem leveling vs active mechanic)')
    p_swap.add_argument('raw', help='Path to raw PoB JSON (from lua import, not expanded)')
    p_swap.add_argument('--audit', help='Path to audit state JSON — if provided, auto-saves note to swap_setup check', default='')

    p_status = sub.add_parser('status', help='Show full audit status')
    p_status.add_argument('audit', help='Path to audit state JSON')

    p_todo = sub.add_parser('todo', help='Show only stale and unknown checks')
    p_todo.add_argument('audit', help='Path to audit state JSON')

    args = parser.parse_args()

    if args.command == 'analyze-swap':
        cmd_analyze_swap(args)
    elif args.command == 'na':
        cmd_na(args)
    elif args.command == 'note':
        cmd_note(args)
    elif args.command == 'init':
        cmd_init(args)
    elif args.command == 'update':
        cmd_update(args)
    elif args.command == 'verify':
        cmd_verify(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'todo':
        cmd_status(args, todo_only=True)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
