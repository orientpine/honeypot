#!/usr/bin/env python3
"""Analyze wiki/ state after all absorption batches complete.

Walks wiki/, collects all articles across batch directories, and reports:
  - Total articles per batch directory
  - Title overlaps (potential duplicates)
  - Cross-batch wikilink density
  - Orphan articles (no inbound links, no outbound links)
  - Article length distribution (stubs, bloated)
  - Type distribution (person, project, concept, etc.)

Writes a report to wiki/_consolidation_report.md and candidate merge list
to wiki/_merge_candidates.json.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml

WIKILINK_RE = re.compile(r'\[\[([^\[\]|#]+?)(?:#[^\[\]|]+)?(?:\|[^\[\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    return parser.parse_args()


def normalize_title(s: str) -> str:
    """Normalize a title for fuzzy comparison."""
    s = s.strip().lower()
    s = re.sub(r'[_\-\s]+', ' ', s)
    s = re.sub(r'[^\w\s가-힣]', '', s)
    return s.strip()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            return {}, text
        return fm, text[m.end() :]
    except yaml.YAMLError:
        return {}, text


def collect_articles(wiki_root: Path) -> list[dict[str, Any]]:
    articles = []
    for p in sorted(wiki_root.rglob('*.md')):
        if p.name.startswith('_'):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        fm, body = parse_frontmatter(text)
        title = str(fm.get('title') or p.stem).strip()
        art_type = str(fm.get('type', '')).strip()
        rel = p.relative_to(wiki_root).as_posix()
        directory = rel.rsplit('/', 1)[0] if '/' in rel else ''
        line_count = len(body.splitlines())
        wikilinks = [m.group(1).strip() for m in WIKILINK_RE.finditer(body)]
        sources = fm.get('sources', []) or []
        if isinstance(sources, str):
            sources = [sources]
        articles.append(
            {
                'title': title,
                'normalized_title': normalize_title(title),
                'type': art_type,
                'path': rel,
                'directory': directory,
                'line_count': line_count,
                'wikilinks': wikilinks,
                'sources': sources,
                'batch': fm.get('batch', ''),
            }
        )
    return articles


def find_duplicates(articles: list[dict]) -> dict[str, list[dict]]:
    """Find articles with identical or very similar titles across directories."""
    by_norm: dict[str, list[dict]] = defaultdict(list)
    for a in articles:
        by_norm[a['normalized_title']].append(a)

    exact_dups = [{'title': k, 'articles': v} for k, v in by_norm.items() if len(v) > 1]

    titles_list = list(by_norm.keys())
    fuzzy_dups = []
    seen = set()
    for i, t1 in enumerate(titles_list):
        if len(by_norm[t1]) > 1:
            continue
        for t2 in titles_list[i + 1 :]:
            if (t1, t2) in seen or t1 == t2:
                continue
            if abs(len(t1) - len(t2)) > 10:
                continue
            if SequenceMatcher(None, t1, t2).ratio() >= 0.85:
                fuzzy_dups.append(
                    {
                        'norm_a': t1,
                        'norm_b': t2,
                        'articles': by_norm[t1] + by_norm[t2],
                    }
                )
                seen.add((t1, t2))

    return {'exact': exact_dups, 'fuzzy': fuzzy_dups}


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    report_path = wiki_root / '_consolidation_report.md'
    merge_candidates_path = wiki_root / '_merge_candidates.json'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1

    articles = collect_articles(wiki_root)
    print(f'Collected {len(articles)} articles from wiki/')

    by_dir = Counter(a['directory'] for a in articles)
    by_type = Counter(a['type'] for a in articles)
    stubs = [a for a in articles if a['line_count'] < 15]
    bloat = [a for a in articles if a['line_count'] > 150]
    total_links = sum(len(a['wikilinks']) for a in articles)

    dup_info = find_duplicates(articles)

    titles_set = {a['title'] for a in articles}
    inbound: dict[str, int] = Counter()
    for a in articles:
        for link in a['wikilinks']:
            inbound[link] += 1

    orphans = [
        a
        for a in articles
        if len(a['wikilinks']) == 0 and inbound.get(a['title'], 0) == 0
    ]

    merge_candidates_path.write_text(
        json.dumps(
            {
                'exact_duplicates': [
                    {
                        'title': d['title'],
                        'paths': [x['path'] for x in d['articles']],
                        'titles': [x['title'] for x in d['articles']],
                    }
                    for d in dup_info['exact']
                ],
                'fuzzy_duplicates': [
                    {
                        'a': d['norm_a'],
                        'b': d['norm_b'],
                        'paths': [x['path'] for x in d['articles']],
                    }
                    for d in dup_info['fuzzy']
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding='utf-8',
    )

    lines = [
        '# Wiki Consolidation Report',
        '',
        f'Total articles: {len(articles)}',
        f'Total wikilinks: {total_links}',
        f'Avg links per article: {total_links / max(1, len(articles)):.1f}',
        '',
        '## Articles per Directory',
        '',
    ]
    for d, n in sorted(by_dir.items(), key=lambda x: -x[1]):
        lines.append(f"- `{d or '(root)'}`: {n}")

    lines.extend(['', '## Articles per Type', ''])
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        lines.append(f"- `{t or '(none)'}`: {n}")

    lines.extend(['', f'## Stubs ({len(stubs)} articles < 15 lines)', ''])
    for a in stubs[:20]:
        lines.append(f"- `{a['path']}` ({a['line_count']} lines)")

    lines.extend(['', f'## Bloated ({len(bloat)} articles > 150 lines)', ''])
    for a in bloat[:20]:
        lines.append(f"- `{a['path']}` ({a['line_count']} lines)")

    lines.extend(['', '## Duplicate Candidates', '', f"### Exact title matches ({len(dup_info['exact'])})", ''])
    for d in dup_info['exact'][:30]:
        lines.append(f"- **{d['articles'][0]['title']}**")
        for a in d['articles']:
            lines.append(f"  - `{a['path']}` ({a['line_count']} lines)")

    lines.extend(['', f"### Fuzzy matches ({len(dup_info['fuzzy'])})", ''])
    for d in dup_info['fuzzy'][:30]:
        paths = [a['path'] for a in d['articles']]
        lines.append(f"- `{d['norm_a']}` vs `{d['norm_b']}`: {paths}")

    lines.extend(['', f'## Orphans ({len(orphans)} articles with no inbound or outbound links)', ''])
    for a in orphans[:20]:
        lines.append(f"- `{a['path']}` ({a['line_count']} lines)")

    lines.extend(['', '## Most referenced (top 30 by inbound links)', ''])
    for title, count in inbound.most_common(30):
        status = 'HAS ARTICLE' if title in titles_set else 'MISSING'
        lines.append(f'- [{count}] {title} ({status})')

    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'Wrote {report_path}')
    print(f'Wrote {merge_candidates_path}')
    print('\nSummary:')
    print(f'  Total articles: {len(articles)}')
    print(f'  Stubs: {len(stubs)}')
    print(f'  Bloated: {len(bloat)}')
    print(f"  Exact dup groups: {len(dup_info['exact'])}")
    print(f"  Fuzzy dup pairs: {len(dup_info['fuzzy'])}")
    print(f'  Orphans: {len(orphans)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
