#!/usr/bin/env python3
"""Rebuild wiki/_index.md and wiki/_backlinks.json from current wiki state.

Walks every *.md article under wiki/ (except `_*.md`), extracts the title,
type, aliases, and wikilinks, and writes:
  - wiki/_index.md      human-readable index with aliases for entry matching
  - wiki/_backlinks.json reverse-link map (article_title -> [backlink_titles])

Idempotent. Run after every absorb batch.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

WIKILINK_RE = re.compile(r'\[\[([^\[\]|#]+?)(?:#[^\[\]|]+)?(?:\|([^\[\]]+))?\]\]')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    return parser.parse_args()


def load_wikiignore_patterns(root: Path) -> list[str]:
    ignore_path = root / '.wikiignore'
    if not ignore_path.exists():
        return []
    patterns: list[str] = []
    for line in ignore_path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        patterns.append(stripped)
    return patterns


def is_ignored(path: Path, root: Path, patterns: list[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    rel_path = Path(rel)
    for pattern in patterns:
        normalized = pattern.rstrip('/')
        if rel_path.match(normalized) or path.name == normalized or rel == normalized:
            return True
        if rel_path.match(f'{normalized}/**'):
            return True
    return False


def iter_articles(root: Path, patterns: list[str]):
    for p in sorted(root.rglob('*.md')):
        if p.name.startswith('_') or p.name.lower() == 'readme.md':
            continue
        if is_ignored(p, root, patterns):
            continue
        yield p


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


def extract_wikilinks(body: str) -> list[str]:
    targets: list[str] = []
    for m in WIKILINK_RE.finditer(body):
        target = m.group(1).strip()
        if target:
            targets.append(target)
    return targets


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    index_path = wiki_root / '_index.md'
    backlinks_path = wiki_root / '_backlinks.json'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1

    patterns = load_wikiignore_patterns(wiki_root)

    articles: list[dict] = []
    backlinks: dict[str, set[str]] = defaultdict(set)
    title_to_dir: dict[str, str] = {}

    for path in iter_articles(wiki_root, patterns):
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as exc:
            print(f'  read error: {path} -- {exc}')
            continue

        fm, body = parse_frontmatter(text)
        title = fm.get('title') or path.stem
        art_type = fm.get('type', '')
        aliases = fm.get('aliases', []) or []
        if isinstance(aliases, str):
            aliases = [aliases]

        rel = path.relative_to(wiki_root).as_posix()
        directory = str(Path(rel).parent) if Path(rel).parent != Path('.') else ''
        filename_stem = path.stem
        articles.append(
            {
                'title': title,
                'filename_stem': filename_stem,
                'type': art_type,
                'path': rel,
                'directory': directory,
                'aliases': aliases,
            }
        )
        title_to_dir[title] = directory

        links = extract_wikilinks(body)
        for target in links:
            backlinks[target].add(title)

    articles.sort(key=lambda a: (a['directory'], a['title'].lower()))
    index_lines = [
        '# Wiki Index',
        '',
        f'Total articles: {len(articles)}',
        '',
    ]
    by_dir: dict[str, list[dict]] = defaultdict(list)
    for a in articles:
        by_dir[a['directory'] or '(root)'].append(a)

    for directory in sorted(by_dir.keys()):
        index_lines.append(f'## {directory}')
        index_lines.append('')
        for a in by_dir[directory]:
            aliases_str = ''
            if a['aliases']:
                aliases_str = f" | also: {', '.join(str(x) for x in a['aliases'])}"
            type_str = f" ({a['type']})" if a['type'] else ''
            stem = a['filename_stem']
            title = a['title']
            if stem == title:
                link = f'[[{stem}]]'
            else:
                link = f'[[{stem}|{title}]]'
            index_lines.append(f'- {link}{type_str}{aliases_str}')
        index_lines.append('')

    index_path.write_text('\n'.join(index_lines), encoding='utf-8', newline='\n')

    backlinks_out = {k: sorted(v) for k, v in sorted(backlinks.items())}
    backlinks_path.write_text(
        json.dumps(backlinks_out, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'Wrote {index_path} with {len(articles)} articles')
    print(f'Wrote {backlinks_path} with {len(backlinks_out)} targets')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
