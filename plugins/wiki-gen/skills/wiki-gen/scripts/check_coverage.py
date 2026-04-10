#!/usr/bin/env python3
"""Verify entry coverage across all wiki articles.

Walks wiki/ collecting sources fields from frontmatter, compares against
raw/ingest_log.json to report which entries are absorbed and which are not.

Writes:
  - wiki/_absorb_log.json: authoritative mapping of entry_id -> articles that cite it
  - wiki/_uncovered.md: list of entries not cited by any article (if any)
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    parser.add_argument(
        '--ingest-log',
        type=Path,
        default=None,
        help='Path to raw/ingest_log.json (default: <wiki-root>/../raw/ingest_log.json)',
    )
    return parser.parse_args()


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        data = yaml.safe_load(m.group(1)) or {}
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError:
        return {}


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / 'raw'
    ingest_log = args.ingest_log.resolve() if args.ingest_log else (raw_root / 'ingest_log.json')
    absorb_log = wiki_root / '_absorb_log.json'
    uncovered_report = wiki_root / '_uncovered.md'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1
    if not ingest_log.exists():
        print(f'ERROR: ingest log not found: {ingest_log}')
        return 1

    log = json.loads(ingest_log.read_text(encoding='utf-8'))
    entries_by_id = {e['id']: e for e in log['entries']}
    print(f'Loaded {len(entries_by_id)} entries from ingest log')
    hex_id_re = re.compile(r'(?<![0-9a-fA-F])([0-9a-f]{12})(?![0-9a-fA-F])')

    entry_to_articles: dict[str, list[str]] = defaultdict(list)
    total_articles = 0
    for p in sorted(wiki_root.rglob('*.md')):
        if p.name.startswith('_'):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        total_articles += 1
        fm = parse_frontmatter(text)
        sources = fm.get('sources', []) or []
        if isinstance(sources, str):
            sources = [sources]
        rel = p.relative_to(wiki_root).as_posix()
        cited_ids: set[str] = set()
        for s in sources:
            s = str(s).strip()
            if s:
                cited_ids.add(s)
        for m in hex_id_re.finditer(text):
            if m.group(1) in entries_by_id:
                cited_ids.add(m.group(1))
        for eid in cited_ids:
            entry_to_articles[eid].append(rel)

    print(f'Walked {total_articles} articles')

    covered = {eid for eid in entry_to_articles if eid in entries_by_id}
    uncovered = [eid for eid in entries_by_id if eid not in covered]
    print(f'Covered entries: {len(covered)} / {len(entries_by_id)}')
    print(f'Uncovered: {len(uncovered)}')

    absorb_data = {
        'total_entries': len(entries_by_id),
        'covered_entries': len(covered),
        'uncovered_entries': len(uncovered),
        'total_articles': total_articles,
        'entry_to_articles': dict(entry_to_articles),
    }
    absorb_log.write_text(
        json.dumps(absorb_data, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    if uncovered:
        by_group: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
        for eid in uncovered:
            e = entries_by_id[eid]
            key = (
                e['source_top'],
                e['source_category'],
                e['source_subcategory'].split('/')[0] if e['source_subcategory'] else '',
            )
            by_group[key].append(e)
        lines = [
            '# Uncovered Entries',
            '',
            f'Total: {len(uncovered)}',
            '',
        ]
        for key in sorted(by_group.keys()):
            entries = by_group[key]
            lines.append(f"## {'/'.join(filter(None, key))} ({len(entries)})")
            lines.append('')
            for e in entries[:30]:
                lines.append(
                    f"- [{e['date']}] {e['title']} — `{e['source_relative']}` (id: {e['id']})"
                )
            if len(entries) > 30:
                lines.append(f'  ... and {len(entries) - 30} more')
            lines.append('')
        uncovered_report.write_text('\n'.join(lines), encoding='utf-8')
    elif uncovered_report.exists():
        uncovered_report.unlink()

    print(f'Wrote {absorb_log}')
    if uncovered:
        print(f'Wrote {uncovered_report}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
