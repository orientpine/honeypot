#!/usr/bin/env python3
"""Finalize the wiki: run all verification scripts and produce a final report.

This orchestrates:
  1. rebuild_index.py    -> wiki/_index.md, wiki/_backlinks.json
  2. check_coverage.py   -> wiki/_absorb_log.json, wiki/_uncovered.md
  3. verify_content.py   -> wiki/_content_coverage.md, wiki/_content_uncovered.json
  4. consolidate_analyze.py -> wiki/_consolidation_report.md, wiki/_merge_candidates.json

Then writes wiki/_FINAL_REPORT.md summarizing:
  - Entry ingestion stats
  - Article creation stats
  - Coverage (citation + content)
  - Duplicates / merge candidates
  - Stubs / bloat
  - Orphans

Run from project root. Idempotent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS = [
    'rebuild_index.py',
    'check_coverage.py',
    'verify_content.py',
    'consolidate_analyze.py',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    return parser.parse_args()


def run(cmd: list[str], cwd: Path) -> int:
    print(f"\n>>> {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=False)
    if r.returncode != 0:
        print(f'  FAILED: {cmd[1]}')
    return r.returncode


def read_json(p: Path) -> dict | list:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / 'raw'
    entries_dir = raw_root / 'entries'
    ingest_log_path = raw_root / 'ingest_log.json'
    script_dir = Path(__file__).parent.resolve()

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1

    commands = [
        [sys.executable, str(script_dir / 'rebuild_index.py'), '--wiki-root', str(wiki_root)],
        [sys.executable, str(script_dir / 'check_coverage.py'), '--wiki-root', str(wiki_root), '--ingest-log', str(ingest_log_path)],
        [sys.executable, str(script_dir / 'verify_content.py'), '--wiki-root', str(wiki_root), '--entries-dir', str(entries_dir), '--ingest-log', str(ingest_log_path)],
        [sys.executable, str(script_dir / 'consolidate_analyze.py'), '--wiki-root', str(wiki_root)],
    ]

    for script_name, cmd in zip(SCRIPTS, commands):
        rc = run(cmd, script_dir)
        if rc != 0:
            print(f'Warning: {script_name} returned {rc}, continuing')

    ingest = read_json(ingest_log_path)
    absorb = read_json(wiki_root / '_absorb_log.json')
    merge_cand = read_json(wiki_root / '_merge_candidates.json')
    content_uncov = read_json(wiki_root / '_content_uncovered.json')

    total_entries = len(ingest.get('entries', [])) if isinstance(ingest, dict) else 0
    total_articles = absorb.get('total_articles', 0) if isinstance(absorb, dict) else 0
    citation_covered = absorb.get('covered_entries', 0) if isinstance(absorb, dict) else 0
    content_uncov_count = len(content_uncov) if isinstance(content_uncov, list) else 0
    content_covered = total_entries - content_uncov_count

    dir_counts: dict[str, int] = {}
    for p in sorted(wiki_root.rglob('*.md')):
        if p.name.startswith('_'):
            continue
        rel = p.relative_to(wiki_root).as_posix()
        d = rel.rsplit('/', 1)[0] if '/' in rel else '(root)'
        dir_counts[d] = dir_counts.get(d, 0) + 1

    exact_dups = merge_cand.get('exact_duplicates', []) if isinstance(merge_cand, dict) else []
    fuzzy_dups = merge_cand.get('fuzzy_duplicates', []) if isinstance(merge_cand, dict) else []
    source_root = ingest.get('source_root', '(unknown)') if isinstance(ingest, dict) else '(unknown)'
    total_files = ingest.get('total_files', 0) if isinstance(ingest, dict) else 0
    skipped = ingest.get('skipped', 0) if isinstance(ingest, dict) else 0
    skipped_breakdown = ingest.get('skipped_breakdown', {}) if isinstance(ingest, dict) else {}

    report_lines = [
        '# Wiki Final Report',
        '',
        f'Generated: {datetime.now().isoformat(timespec="seconds")}',
        f'Source: `{source_root}`',
        f'Wiki root: `{wiki_root}`',
        '',
        '## Ingestion',
        '',
        f'- Source files scanned: {total_files} markdown files',
        f'- Skipped: {skipped}',
    ]
    if skipped_breakdown:
        for key, value in sorted(skipped_breakdown.items()):
            report_lines.append(f'  - {key}: {value}')
    report_lines.extend(
        [
            f'- Ingested: {total_entries} personal knowledge entries',
            '',
            '## Articles Produced',
            '',
            f'- Total articles: {total_articles}',
            f'- Directories: {len(dir_counts)}',
            '',
            '### Articles per directory',
            '',
        ]
    )
    for d, n in sorted(dir_counts.items(), key=lambda x: -x[1]):
        report_lines.append(f'- `{d}`: {n}')

    report_lines.extend(
        [
            '',
            '## Coverage',
            '',
            '- **Citation coverage** (entry IDs cited in article body/frontmatter):',
            f'  {citation_covered} / {total_entries} ({citation_covered / max(1, total_entries) * 100:.1f}%)',
            '- **Content coverage** (citation OR title/source token match):',
            f'  {content_covered} / {total_entries} ({content_covered / max(1, total_entries) * 100:.1f}%)',
            '',
            '## Duplicate Candidates',
            '',
            f'- Exact title duplicates: {len(exact_dups)}',
            f'- Fuzzy title duplicates: {len(fuzzy_dups)}',
            '',
        ]
    )

    if exact_dups:
        report_lines.append('### Exact duplicate groups')
        report_lines.append('')
        for d in exact_dups[:20]:
            report_lines.append(f"- **{d.get('title', '?')}**")
            for p in d.get('paths', []):
                report_lines.append(f'  - `{p}`')

    report_lines.extend(
        [
            '',
            '## See Also',
            '',
            '- `wiki/_index.md` — full article index',
            '- `wiki/_backlinks.json` — reverse-link map',
            '- `wiki/_absorb_log.json` — citation map entry_id → articles',
            '- `wiki/_consolidation_report.md` — detailed duplicate and stub analysis',
            '- `wiki/_content_coverage.md` — content-based coverage report',
            '- `wiki/_uncovered.md` — entries not yet citation-covered',
            '- `wiki/_content_uncovered.json` — entries not content-covered',
            '',
        ]
    )

    out = wiki_root / '_FINAL_REPORT.md'
    out.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"\n{'=' * 60}")
    print(f'FINAL REPORT: {out}')
    print(f'  Articles: {total_articles}')
    print(f'  Entries: {total_entries}')
    print(f'  Citation coverage: {citation_covered / max(1, total_entries) * 100:.1f}%')
    print(f'  Content coverage: {content_covered / max(1, total_entries) * 100:.1f}%')
    print(f'  Exact dups: {len(exact_dups)}')
    print(f'  Fuzzy dups: {len(fuzzy_dups)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
