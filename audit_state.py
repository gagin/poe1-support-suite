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
        "label": "All reservation slots filled — no spare reservation unused",
        "depends": ["gems", "passive_tree", "equipment"],
        "tier": 1,
    },
    # Tier 2 — Mid-League
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
# Commands
# ---------------------------------------------------------------------------

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

    p_status = sub.add_parser('status', help='Show full audit status')
    p_status.add_argument('audit', help='Path to audit state JSON')

    p_todo = sub.add_parser('todo', help='Show only stale and unknown checks')
    p_todo.add_argument('audit', help='Path to audit state JSON')

    args = parser.parse_args()

    if args.command == 'init':
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
