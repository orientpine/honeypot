#!/usr/bin/env python3
"""Map raw entries to batches for parallel absorption agents."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--entries-dir', type=Path, required=True, help='Path to raw/entries directory')
    parser.add_argument('--ingest-log', type=Path, required=True, help='Path to raw/ingest_log.json')
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    entries_dir = args.entries_dir.resolve()
    log_path = args.ingest_log.resolve()

    if not entries_dir.exists():
        print(f'ERROR: entries dir not found: {entries_dir}')
        return 1
    if not log_path.exists():
        print(f'ERROR: ingest log not found: {log_path}')
        return 1

    log = json.loads(log_path.read_text(encoding='utf-8'))

    groups = defaultdict(list)
    all_entries = log['entries']

    for e in all_entries:
        top = e['source_top']
        cat = e['source_category']
        sub_parts = e['source_subcategory'].split('/') if e['source_subcategory'] else []
        sub = sub_parts[0] if sub_parts else ''
        key = (top, cat, sub)
        groups[key].append(e)

    print('=' * 80)
    print(f'Total entries: {len(all_entries)}')
    print('=' * 80)

    summary_rows = []
    for key in sorted(groups.keys()):
        top, cat, sub = key
        entries = groups[key]
        label = f'{top}/{cat}/{sub}' if sub else f'{top}/{cat}'
        summary_rows.append((label, len(entries), top, cat, sub))

    by_top = defaultdict(list)
    for label, n, top, cat, sub in summary_rows:
        by_top[top].append((label, n, cat, sub))

    for top in sorted(by_top.keys()):
        total = sum(n for _, n, _, _ in by_top[top])
        print(f'\n## {top} (total: {total})')
        for label, n, cat, sub in by_top[top]:
            print(f'  {n:5d}  {label}')

    print('\n' + '=' * 80)
    print('PROPOSED BATCHES (target ~80-150 entries each)')
    print('=' * 80)

    batch_plan = []
    for label, n, top, cat, sub in summary_rows:
        if n <= 150:
            batch_plan.append({'label': label, 'n': n, 'top': top, 'cat': cat, 'sub': sub, 'split': 1})
        else:
            key = (top, cat, sub)
            entries = groups[key]
            deeper = defaultdict(list)
            for e in entries:
                parts = e['source_subcategory'].split('/') if e['source_subcategory'] else []
                d = parts[1] if len(parts) > 1 else '(root)'
                deeper[d].append(e)
            print(f'\n[SPLIT] {label} ({n} entries):')
            for d, es in sorted(deeper.items(), key=lambda x: -len(x[1])):
                print(f'    {len(es):5d}  -> {d}')
                batch_plan.append(
                    {
                        'label': f'{label}/{d}',
                        'n': len(es),
                        'top': top,
                        'cat': cat,
                        'sub': sub,
                        'deep': d,
                        'split': len(deeper),
                    }
                )

    out_path = entries_dir.parent / 'batch_plan.json'
    out_path.write_text(json.dumps(batch_plan, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'\nTotal batches: {len(batch_plan)}')
    print(f'Saved to {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
