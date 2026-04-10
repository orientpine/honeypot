#!/usr/bin/env python3
"""Show uncovered entries grouped by absorption batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    parser.add_argument(
        '--batches-dir',
        type=Path,
        default=None,
        help='Path to raw/batches directory (default: <wiki-root>/../raw/batches)',
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / 'raw'
    absorb_log = wiki_root / '_absorb_log.json'
    batches_dir = args.batches_dir.resolve() if args.batches_dir else (raw_root / 'batches')
    out_path = raw_root / 'uncovered_by_batch.json'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1
    if not absorb_log.exists():
        print(f'ERROR: absorb log not found: {absorb_log}')
        return 1
    if not batches_dir.exists():
        print(f'ERROR: batches dir not found: {batches_dir}')
        return 1

    absorb = json.loads(absorb_log.read_text(encoding='utf-8'))
    covered_ids = set(absorb['entry_to_articles'].keys())

    batch_stats = []
    for manifest_path in sorted(batches_dir.glob('*.json')):
        m = json.loads(manifest_path.read_text(encoding='utf-8'))
        bid = m['batch_id']
        total = m['entry_count']
        batch_entries = [e['id'] for e in m['entries_meta']]
        uncovered = [eid for eid in batch_entries if eid not in covered_ids]
        covered = total - len(uncovered)
        pct = (covered / total * 100) if total else 0
        batch_stats.append(
            {
                'batch_id': bid,
                'wiki_target_dir': m['wiki_target_dir'],
                'total': total,
                'covered': covered,
                'uncovered': len(uncovered),
                'pct': pct,
                'uncovered_ids': uncovered,
            }
        )

    batch_stats.sort(key=lambda x: -x['uncovered'])

    print(f"{'BATCH':35s} {'TOTAL':>5s} {'COV':>4s} {'UNCOV':>5s} {'PCT':>6s}")
    print('-' * 65)
    for b in batch_stats:
        print(f"{b['batch_id']:35s} {b['total']:5d} {b['covered']:4d} {b['uncovered']:5d} {b['pct']:5.1f}%")

    total_t = sum(b['total'] for b in batch_stats)
    total_c = sum(b['covered'] for b in batch_stats)
    total_u = sum(b['uncovered'] for b in batch_stats)
    print('-' * 65)
    print(f"{'TOTAL':35s} {total_t:5d} {total_c:4d} {total_u:5d} {total_c / total_t * 100:5.1f}%")

    out = {}
    for b in batch_stats:
        if b['uncovered'] > 0:
            out[b['batch_id']] = {
                'wiki_target_dir': b['wiki_target_dir'],
                'uncovered_count': b['uncovered'],
                'uncovered_ids': b['uncovered_ids'],
            }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nSaved to {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
