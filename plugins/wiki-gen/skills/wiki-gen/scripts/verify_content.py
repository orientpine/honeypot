#!/usr/bin/env python3
"""Verify content coverage beyond citation coverage.

Citation coverage (check_coverage.py) only counts entries whose 12-char IDs
appear in wiki articles. But an entry's CONTENT may be absorbed into an
article without its ID being cited. This script does a softer check:

For each entry, it extracts a signature (title tokens + top content tokens),
then searches wiki articles for matches. If any article shares significant
tokens, the entry is considered "content-absorbed".

Outputs:
  wiki/_content_coverage.md: Report with covered/uncovered counts
  wiki/_content_uncovered.json: Entries that are both citation-uncovered
    AND content-unmatched (require real remediation)
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
KOREAN_WORD_RE = re.compile(r'[가-힣]{2,}|[A-Za-z][A-Za-z0-9]{2,}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    parser.add_argument(
        '--entries-dir',
        type=Path,
        default=None,
        help='Path to raw/entries (default: <wiki-root>/../raw/entries)',
    )
    parser.add_argument(
        '--ingest-log',
        type=Path,
        default=None,
        help='Path to raw/ingest_log.json (default: <wiki-root>/../raw/ingest_log.json)',
    )
    return parser.parse_args()


def load_ingest_log(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_absorb_log(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return {'entry_to_articles': {}}


def tokenize(text: str) -> set[str]:
    tokens = set()
    for m in KOREAN_WORD_RE.finditer(text):
        t = m.group(0).lower()
        if len(t) >= 2:
            tokens.add(t)
    return tokens


def strip_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    if m:
        return text[m.end() :]
    return text


def build_entry_signature(entry_meta: dict, entry_file: Path) -> set[str]:
    """Extract salient tokens from an entry's title and top content."""
    title = entry_meta.get('title', '')
    title_tokens = tokenize(title)
    if entry_file.exists():
        try:
            text = entry_file.read_text(encoding='utf-8')
            body = strip_frontmatter(text)
            body_tokens = tokenize(body[:800])
        except Exception:
            body_tokens = set()
    else:
        body_tokens = set()
    return title_tokens | body_tokens


def build_wiki_token_map(wiki_root: Path) -> dict[str, set[str]]:
    """Map each article path to its token set."""
    out: dict[str, set[str]] = {}
    for p in sorted(wiki_root.rglob('*.md')):
        if p.name.startswith('_'):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        body = strip_frontmatter(text)
        rel = p.relative_to(wiki_root).as_posix()
        out[rel] = tokenize(body)
    return out


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / 'raw'
    entries_dir = args.entries_dir.resolve() if args.entries_dir else (raw_root / 'entries')
    ingest_log = args.ingest_log.resolve() if args.ingest_log else (raw_root / 'ingest_log.json')
    absorb_log = wiki_root / '_absorb_log.json'
    report = wiki_root / '_content_coverage.md'
    uncovered_out = wiki_root / '_content_uncovered.json'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1
    if not entries_dir.exists():
        print(f'ERROR: entries dir not found: {entries_dir}')
        return 1
    if not ingest_log.exists():
        print(f'ERROR: ingest log not found: {ingest_log}')
        return 1

    ingest = load_ingest_log(ingest_log)
    absorb = load_absorb_log(absorb_log)
    cited_ids = set(absorb.get('entry_to_articles', {}).keys())

    entries_meta = {e['id']: e for e in ingest['entries']}
    print(f'Loaded {len(entries_meta)} entries')

    wiki_tokens = build_wiki_token_map(wiki_root)
    print(f'Loaded {len(wiki_tokens)} wiki articles')

    content_covered_ids: set[str] = set(cited_ids)
    content_uncovered: list[dict] = []
    match_threshold_ratio = 0.35

    for eid, meta in entries_meta.items():
        if eid in content_covered_ids:
            continue
        title = meta.get('title', '')
        source_rel = meta.get('source_relative', '')
        sig_text = f"{title} {source_rel.replace('/', ' ').replace('_', ' ')}"
        sig_tokens = tokenize(sig_text)
        _ = build_entry_signature(meta, entries_dir / meta.get('file', ''))
        if not sig_tokens:
            content_uncovered.append(
                {
                    'id': eid,
                    'title': title,
                    'source_relative': source_rel,
                    'reason': 'no_signature_tokens',
                }
            )
            continue
        best_match = None
        best_ratio = 0.0
        for path, atoks in wiki_tokens.items():
            if not atoks:
                continue
            intersection = sig_tokens & atoks
            if not intersection:
                continue
            ratio = len(intersection) / len(sig_tokens)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = path
        if best_match and best_ratio >= match_threshold_ratio:
            content_covered_ids.add(eid)
        else:
            content_uncovered.append(
                {
                    'id': eid,
                    'title': title,
                    'source_relative': source_rel,
                    'best_match': best_match,
                    'best_ratio': round(best_ratio, 2),
                }
            )

    cite_cov = len(cited_ids)
    content_cov = len(content_covered_ids)
    total = len(entries_meta)

    lines = [
        '# Content Coverage Report',
        '',
        f'Total entries: {total}',
        f'Citation-covered (entry ID in article body/frontmatter): {cite_cov} ({cite_cov / total * 100:.1f}%)',
        f'Content-covered (citation OR title/source tokens match an article): {content_cov} ({content_cov / total * 100:.1f}%)',
        f'Truly uncovered: {len(content_uncovered)} ({len(content_uncovered) / total * 100:.1f}%)',
        '',
        '## Truly uncovered entries',
        '',
        "(These entries are not cited AND their salient tokens don't match any wiki article.)",
        '',
    ]

    by_top: dict[str, list[dict]] = defaultdict(list)
    for e in content_uncovered:
        meta = entries_meta.get(e['id'], {})
        top = meta.get('source_top', '?')
        by_top[top].append(e)

    for top in sorted(by_top.keys()):
        lines.append(f"### {top} ({len(by_top[top])})")
        lines.append('')
        for e in by_top[top][:30]:
            br = e.get('best_ratio', 0)
            bm = e.get('best_match', 'none')
            lines.append(f"- `{e['id']}` {e['title'][:50]} [best: {bm} @ {br}]")
        if len(by_top[top]) > 30:
            lines.append(f"  ... and {len(by_top[top]) - 30} more")
        lines.append('')

    report.write_text('\n'.join(lines), encoding='utf-8')
    uncovered_out.write_text(
        json.dumps(content_uncovered, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'Citation-covered: {cite_cov}/{total} ({cite_cov / total * 100:.1f}%)')
    print(f'Content-covered:  {content_cov}/{total} ({content_cov / total * 100:.1f}%)')
    print(f'Truly uncovered:  {len(content_uncovered)}')
    print(f'Wrote {report}')
    print(f'Wrote {uncovered_out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
