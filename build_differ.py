#!/usr/bin/env python3
"""
Compare two expanded character JSONs and output a structured change report.

Usage:
    python build_differ.py <old_expanded.json> <new_expanded.json>

Output: human-readable diff + <charname>_diff.json for audit_state.py consumption.
"""

import json
import sys
from pathlib import Path


def item_fingerprint(item):
    quality = None
    for p in item.get('properties', []):
        if p['name'] == 'Quality' and p.get('values'):
            quality = p['values'][0][0]
            break
    return {
        'name': item.get('name', ''),
        'typeLine': item.get('typeLine', ''),
        'explicitMods': sorted(item.get('explicitMods', [])),
        'implicitMods': sorted(item.get('implicitMods', [])),
        'enchantMods': sorted(item.get('enchantMods', [])),
        'corrupted': item.get('corrupted', False),
        'quality': quality,
    }


def diff_item_collection(old_items, new_items):
    changes = {}
    old_by_slot = {i['slot']: i for i in old_items}
    new_by_slot = {i['slot']: i for i in new_items}

    for slot in sorted(set(old_by_slot) | set(new_by_slot)):
        old = old_by_slot.get(slot)
        new = new_by_slot.get(slot)
        label = (new or old).get('name') or (new or old).get('typeLine', f'slot {slot}')

        if old is None:
            changes[slot] = {'change': 'added', 'label': label}
        elif new is None:
            changes[slot] = {'change': 'removed', 'label': label}
        else:
            old_fp = item_fingerprint(old)
            new_fp = item_fingerprint(new)
            if old_fp != new_fp:
                diff = {k: {'old': old_fp[k], 'new': new_fp[k]}
                        for k in old_fp if old_fp[k] != new_fp[k]}
                changes[slot] = {'change': 'modified', 'label': label, 'diff': diff}

    return changes


def diff_passive_tree(old_tree, new_tree):
    changes = {}

    def names(key):
        return lambda tree: {n['name'] for n in tree.get(key, [])}

    for key, label in [('notables', 'notables'), ('keystones', 'keystones'), ('ascendancy', 'ascendancy')]:
        old_set = names(key)(old_tree)
        new_set = names(key)(new_tree)
        added, removed = new_set - old_set, old_set - new_set
        if added or removed:
            changes[label] = {'added': sorted(added), 'removed': sorted(removed)}

    # Masteries — identified by (name, effect_id) pair
    old_m = {(m['name'], m.get('effect_id')) for m in old_tree.get('masteries', [])}
    new_m = {(m['name'], m.get('effect_id')) for m in new_tree.get('masteries', [])}
    if old_m != new_m:
        changes['masteries'] = {
            'added': sorted([{'name': m[0], 'effect_id': m[1]} for m in new_m - old_m], key=lambda x: x['name']),
            'removed': sorted([{'name': m[0], 'effect_id': m[1]} for m in old_m - new_m], key=lambda x: x['name']),
        }

    old_pts = old_tree.get('total_points', 0)
    new_pts = new_tree.get('total_points', 0)
    if old_pts != new_pts:
        changes['total_points'] = {'old': old_pts, 'new': new_pts}

    return changes


def diff_gems(old_skills, new_skills):
    def gem_set(skills):
        return {(g['name'], g['level'], g['quality']) for g in skills.get('all_gems', [])}

    old_g = gem_set(old_skills)
    new_g = gem_set(new_skills)
    added = new_g - old_g
    removed = old_g - new_g
    if not added and not removed:
        return {}
    return {
        'added': sorted([{'name': g[0], 'level': g[1], 'quality': g[2]} for g in added], key=lambda x: x['name']),
        'removed': sorted([{'name': g[0], 'level': g[1], 'quality': g[2]} for g in removed], key=lambda x: x['name']),
    }


def diff_builds(old_path, new_path):
    with open(old_path) as f:
        old = json.load(f)
    with open(new_path) as f:
        new = json.load(f)

    result = {
        'from': str(old_path),
        'to': str(new_path),
        'character': new.get('character', {}).get('name', '?'),
        'changes': {},
    }

    for key, label in [('equipment', 'equipment'), ('flasks', 'flasks'), ('jewels', 'jewels')]:
        diff = diff_item_collection(old['items'][key], new['items'][key])
        if diff:
            result['changes'][label] = diff

    pt_diff = diff_passive_tree(old['passive_tree'], new['passive_tree'])
    if pt_diff:
        result['changes']['passive_tree'] = pt_diff

    gem_diff = diff_gems(old['skills'], new['skills'])
    if gem_diff:
        result['changes']['gems'] = gem_diff

    return result


def print_diff(result):
    changes = result['changes']
    if not changes:
        print(f"No changes detected.")
        return

    print(f"Character: {result['character']}")
    print(f"From: {Path(result['from']).name}")
    print(f"To:   {Path(result['to']).name}\n")

    for section, section_label in [
        ('equipment', 'Equipment'), ('flasks', 'Flasks'), ('jewels', 'Jewels')
    ]:
        if section not in changes:
            continue
        print(f"=== {section_label} ===")
        for slot, c in sorted(changes[section].items()):
            if c['change'] in ('added', 'removed'):
                print(f"  Slot {slot}: {c['change']} — {c['label']}")
            else:
                print(f"  Slot {slot} ({c['label']}):")
                for field, delta in c['diff'].items():
                    print(f"    {field}: {delta['old']}  →  {delta['new']}")

    if 'passive_tree' in changes:
        print("\n=== Passive Tree ===")
        pt = changes['passive_tree']
        if 'notables' in pt:
            if pt['notables']['added']:
                print(f"  + notables: {', '.join(pt['notables']['added'])}")
            if pt['notables']['removed']:
                print(f"  - notables: {', '.join(pt['notables']['removed'])}")
        if 'keystones' in pt:
            if pt['keystones']['added']:
                print(f"  + keystones: {', '.join(pt['keystones']['added'])}")
            if pt['keystones']['removed']:
                print(f"  - keystones: {', '.join(pt['keystones']['removed'])}")
        if 'masteries' in pt:
            if pt['masteries']['added']:
                print(f"  + masteries: {[m['name'] for m in pt['masteries']['added']]}")
            if pt['masteries']['removed']:
                print(f"  - masteries: {[m['name'] for m in pt['masteries']['removed']]}")
        if 'ascendancy' in pt:
            if pt['ascendancy']['added']:
                print(f"  + ascendancy: {', '.join(pt['ascendancy']['added'])}")
            if pt['ascendancy']['removed']:
                print(f"  - ascendancy: {', '.join(pt['ascendancy']['removed'])}")
        if 'total_points' in pt:
            print(f"  total_points: {pt['total_points']['old']} → {pt['total_points']['new']}")

    if 'gems' in changes:
        print("\n=== Gems ===")
        gc = changes['gems']
        for g in gc.get('added', []):
            print(f"  + {g['name']} L{g['level']} Q{g['quality']}")
        for g in gc.get('removed', []):
            print(f"  - {g['name']} L{g['level']} Q{g['quality']}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]
    result = diff_builds(old_path, new_path)
    print_diff(result)

    out_path = Path(new_path).stem.replace('_expanded', '') + '_diff.json'
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nDiff saved to: {out_path}")


if __name__ == '__main__':
    main()
