#!/usr/bin/env python3
"""Diagnose wikilink resolution: which [[titles]] in _index.md don't map to any file.

Obsidian resolves [[Target]] by checking:
  1. File with name == Target.md (case-insensitive, anywhere in vault)
  2. File whose frontmatter `aliases:` contains Target
  3. File whose frontmatter `title:` equals Target (maybe, depends on version)

This script reports for each index wikilink:
  - UNRESOLVED: no matching filename AND no matching alias AND no matching title
  - RESOLVED_BY_FILENAME
  - RESOLVED_BY_ALIAS
  - RESOLVED_BY_TITLE_ONLY (risky: Obsidian may not do this)
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import yaml

FM_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
WIKILINK_RE = re.compile(r'\[\[([^\[\]|#]+?)(?:#[^\[\]|]+)?(?:\|[^\[\]]+)?\]\]')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    return parser.parse_args()


def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def normalize(s: str) -> str:
    return s.strip().lower()


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    index = wiki_root / '_index.md'

    if not wiki_root.exists():
        print(f'ERROR: wiki root not found: {wiki_root}')
        return 1
    if not index.exists():
        print(f'ERROR: index not found: {index}')
        return 1

    filename_index = {}
    alias_index = defaultdict(list)
    title_index = defaultdict(list)

    all_articles = []
    for p in sorted(wiki_root.rglob('*.md')):
        if p.name.startswith('_'):
            continue
        if p.name.lower() == 'readme.md':
            continue
        stem = p.stem
        filename_index[normalize(stem)] = p
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        fm = parse_frontmatter(text)
        title = str(fm.get('title') or stem).strip()
        title_index[normalize(title)].append(p)
        aliases = fm.get('aliases', []) or []
        if isinstance(aliases, str):
            aliases = [aliases]
        for a in aliases:
            if a:
                alias_index[normalize(str(a))].append(p)
        all_articles.append({'path': p, 'stem': stem, 'title': title, 'aliases': aliases})

    index_text = index.read_text(encoding='utf-8')
    index_links = []
    for m in WIKILINK_RE.finditer(index_text):
        target = m.group(1).strip()
        index_links.append(target)

    unresolved = []
    resolved_by_filename = []
    resolved_by_alias = []
    resolved_by_title_only = []

    for target in index_links:
        t = normalize(target)
        if t in filename_index:
            resolved_by_filename.append((target, filename_index[t]))
        elif t in alias_index:
            resolved_by_alias.append((target, alias_index[t][0]))
        elif t in title_index:
            resolved_by_title_only.append((target, title_index[t][0]))
        else:
            unresolved.append(target)

    print(f'Total index wikilinks: {len(index_links)}')
    print(f'  Resolved by filename (ideal):     {len(resolved_by_filename)}')
    print(f'  Resolved by alias (works in Obsidian): {len(resolved_by_alias)}')
    print(f'  Resolved by title only (risky):   {len(resolved_by_title_only)}')
    print(f'  UNRESOLVED (broken links):        {len(unresolved)}')

    if unresolved:
        print('\n=== UNRESOLVED LINKS ===')
        for t in unresolved[:30]:
            print(f'  [[{t}]]')

    if resolved_by_title_only:
        print('\n=== RESOLVED BY TITLE ONLY (may not work in Obsidian) ===')
        for target, path in resolved_by_title_only[:30]:
            print(f'  [[{target}]] -> {path.relative_to(wiki_root).as_posix()}')

    print('\n=== SAMPLE ARTICLES (filename vs title) ===')
    for art in all_articles[:10]:
        print(f"  File: {art['stem']}.md  |  Title: {art['title']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(parse_args()))
