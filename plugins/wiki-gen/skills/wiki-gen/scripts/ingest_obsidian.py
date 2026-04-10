#!/usr/bin/env python3
"""
Ingest Obsidian vault into raw/entries/ for wiki-gen.

Walks the Obsidian vault at SOURCE_ROOT, reads every markdown file,
extracts metadata (date, tags, author, title) from YAML frontmatter or
Obsidian '[!info]' callouts, and writes normalized entries to
raw/entries/{YYYY-MM-DD}_{slug}.md.

Idempotent: running twice produces the same output (overwrites by ID).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from ingest_common import (
    DEFAULT_SKIP_DIR_NAMES,
    DATE_YYYYMMDD,
    ISO_DATETIME,
    Entry,
    log,
    parse_csv_set,
    slugify,
    parse_yaml_frontmatter,
    extract_heading_title,
    extract_tags,
    _valid_date,
    _extract_path_year,
    parse_date_fields,
    coerce_tag_list,
    coerce_alias_list,
    count_markdown_files,
    format_breakdown,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


# Obsidian info-callout line matchers (one-liners inside blockquotes).
CALLOUT_TITLE_RE = re.compile(r'^\s*>\s*\[!info\]\s*$', re.IGNORECASE)
CALLOUT_FIELD_RE = re.compile(r'^\s*>\s*\*\*(?P<key>[^*]+)\*\*\s*:\s*(?P<value>.*)$')
CALLOUT_LINE_RE = re.compile(r'^\s*>')

GITMODULE_PATH_RE = re.compile(r'^\s*path\s*=\s*(.+?)\s*$')



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0] if __doc__ else '')
    parser.add_argument('--source-root', type=Path, required=True, help='Path to the source Obsidian vault')
    parser.add_argument('--wiki-root', type=Path, required=True, help='Path to wiki/ directory')
    parser.add_argument(
        '--ingest-log',
        type=Path,
        default=None,
        help='Path to raw/ingest_log.json (default: <wiki-root>/../raw/ingest_log.json)',
    )
    parser.add_argument(
        '--include-top-dirs',
        default=None,
        help='Comma-separated top-level directories to include (default: include all top-level dirs)',
    )
    parser.add_argument(
        '--skip-dirs',
        default=None,
        help='Comma-separated directory names to skip anywhere in the tree (default: standard exclusion list)',
    )
    return parser.parse_args()




def parse_info_callout(text: str) -> tuple[dict[str, str], str]:
    """Extract an Obsidian '[!info]' callout block and return parsed fields + remaining body.

    Consumes contiguous leading blank lines and the entire '>' block.
    """
    lines = text.splitlines()
    idx = 0
    while idx < len(lines) and lines[idx].strip() == '':
        idx += 1
    if idx >= len(lines) or not CALLOUT_LINE_RE.match(lines[idx]):
        return {}, text
    block_start = idx
    while idx < len(lines) and CALLOUT_LINE_RE.match(lines[idx]):
        idx += 1
    block_lines = lines[block_start:idx]
    info_found = any(CALLOUT_TITLE_RE.match(bl) for bl in block_lines)
    if not info_found:
        return {}, text
    fields: dict[str, str] = {}
    for bl in block_lines:
        m = CALLOUT_FIELD_RE.match(bl)
        if m:
            key = m.group('key').strip().lower()
            value = m.group('value').strip()
            value = re.sub(r'`=[^`]*`', '', value).strip()
            if value:
                fields[key] = value
    while idx < len(lines) and lines[idx].strip() == '':
        idx += 1
    remaining = '\n'.join(lines[idx:])
    return fields, remaining




def classify_source(rel_parts: tuple[str, ...]) -> tuple[str, str, str]:
    """Return (source_top, source_category, source_subcategory)."""
    if not rel_parts:
        return 'Root', 'Root', ''
    top = rel_parts[0]
    source_top_map = {
        '000_PARA': 'Personal',
        '001_KIMM_PARA': 'KIMM',
        '002_Schedule': 'Schedule',
        '999_limbo': 'Limbo',
        'Excalidraw': 'Excalidraw',
    }
    source_top = source_top_map.get(top, top)
    category = rel_parts[1] if len(rel_parts) > 1 else ''
    subcategory = '/'.join(rel_parts[2:-1]) if len(rel_parts) > 2 else ''
    return source_top, category, subcategory



def load_submodule_paths(source_root: Path) -> list[Path]:
    gitmodules = source_root / '.gitmodules'
    if not gitmodules.exists():
        return []
    submodules: list[Path] = []
    try:
        text = gitmodules.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return []
    for line in text.splitlines():
        m = GITMODULE_PATH_RE.match(line)
        if m:
            submodules.append(Path(m.group(1).strip()))
    return submodules




def walk_markdown(
    source_root: Path,
    include_top_dirs: set[str] | None,
    skip_dir_names: set[str],
    submodule_paths: list[Path],
) -> tuple[list[Path], Counter]:
    """Return markdown files plus skip-count breakdown."""
    collected: list[Path] = []
    skip_counts: Counter = Counter()

    for p in sorted(source_root.glob('*.md')):
        if p.is_file():
            collected.append(p)

    if include_top_dirs is None:
        top_dirs = sorted(p.name for p in source_root.iterdir() if p.is_dir())
    else:
        top_dirs = sorted(include_top_dirs)

    submodule_map = {sub.as_posix(): sub for sub in submodule_paths}

    for top in top_dirs:
        top_path = source_root / top
        if not top_path.exists() or not top_path.is_dir():
            continue
        if top in skip_dir_names:
            skip_counts[top] += count_markdown_files(top_path)
            continue
        if top_path.relative_to(source_root).as_posix() in submodule_map:
            skip_counts[f'submodule:{top}'] += count_markdown_files(top_path)
            continue
        for root, dirs, files in os.walk(top_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(source_root)
            pruned: list[str] = []
            for d in list(dirs):
                child_rel = rel_root / d
                child_rel_posix = child_rel.as_posix()
                child_path = source_root / child_rel
                if d in skip_dir_names:
                    skip_counts[d] += count_markdown_files(child_path)
                    pruned.append(d)
                    continue
                if child_rel_posix in submodule_map:
                    skip_counts[f'submodule:{child_rel_posix}'] += count_markdown_files(child_path)
                    pruned.append(d)
            dirs[:] = [d for d in dirs if d not in pruned]
            for f in files:
                if f.lower().endswith('.md'):
                    collected.append(root_path / f)

    return collected, skip_counts


def ingest_file(path: Path, source_root: Path) -> tuple[Entry | None, str | None]:
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception as exc:
        log(f'SKIP (read error): {path} -- {exc}')
        return None, 'read_error'

    if not text.strip():
        log(f'SKIP (empty): {path}')
        return None, 'empty'

    file_stat = path.stat()

    fm, remaining = parse_yaml_frontmatter(text)
    fm = fm or {}
    if not remaining.strip():
        log(f'SKIP (empty after frontmatter): {path}')
        return None, 'empty_after_frontmatter'

    callout, remaining = parse_info_callout(remaining)
    heading_title, body = extract_heading_title(remaining)

    title = (
        (fm.get('title') if isinstance(fm.get('title'), str) else None)
        or heading_title
        or path.stem
    )

    tags = coerce_tag_list(fm.get('tags')) or []
    tag_field = callout.get('tag', '')
    if tag_field:
        tags += [t.lstrip('#') for t in re.split(r'[,\s]+', tag_field) if t]
    tags += extract_tags(body)
    tags = sorted(set(t for t in tags if t))

    aliases = coerce_alias_list(fm.get('aliases'))
    author = fm.get('author') or callout.get('author') or ''

    rel_path = path.relative_to(source_root)
    rel_str = rel_path.as_posix()
    source_top, source_category, source_subcategory = classify_source(rel_path.parts)

    date_str, time_str, date_source = parse_date_fields(
        fm,
        callout,
        path.stem,
        file_stat,
        rel_str,
    )

    entry_id = hashlib.sha1(rel_str.encode('utf-8')).hexdigest()[:12]

    body_clean = body.strip()
    word_count = len(re.findall(r'\S+', body_clean))
    char_count = len(body_clean)
    line_count = body_clean.count('\n') + (1 if body_clean else 0)

    known_fm_keys = {
        'title',
        'tags',
        'aliases',
        'created',
        'modified',
        'date',
        'author',
    }
    extra: dict[str, Any] = {'date_source': date_source}
    for k, v in fm.items():
        if k in known_fm_keys:
            continue
        try:
            json.dumps(v, ensure_ascii=False)
            extra[k] = v
        except TypeError:
            extra[k] = str(v)

    return (
        Entry(
            id=entry_id,
            date=date_str,
            time=time_str,
            title=title,
            source_type='obsidian',
            source_path=str(path),
            source_relative=rel_str,
            source_top=source_top,
            source_category=source_category,
            source_subcategory=source_subcategory,
            tags=tags,
            author=str(author) if author else None,
            aliases=aliases,
            word_count=word_count,
            char_count=char_count,
            line_count=line_count,
            extra=extra,
            body=body_clean,
        ),
        None,
    )




def main(args: argparse.Namespace) -> int:
    source_root = args.source_root.resolve()
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / 'raw'
    entries_dir = raw_root / 'entries'
    ingest_log = args.ingest_log.resolve() if args.ingest_log else (raw_root / 'ingest_log.json')
    include_top_dirs = parse_csv_set(args.include_top_dirs)
    skip_dir_names = parse_csv_set(args.skip_dirs) or set(DEFAULT_SKIP_DIR_NAMES)

    if not source_root.exists():
        log(f'ERROR: source not found: {source_root}')
        return 1
    if not wiki_root.exists():
        log(f'ERROR: wiki root not found: {wiki_root}')
        return 1

    entries_dir.mkdir(parents=True, exist_ok=True)

    submodule_paths = load_submodule_paths(source_root)

    log(f'Walking source: {source_root}')
    md_files, skip_breakdown = walk_markdown(source_root, include_top_dirs, skip_dir_names, submodule_paths)
    log(f'Found {len(md_files)} markdown files after directory filtering')

    produced: list[dict[str, Any]] = []
    seen_names: dict[str, int] = {}
    ingest_skip_counts: Counter = Counter()
    written = 0
    mtime_fallback_count = 0

    for idx, md in enumerate(md_files, start=1):
        entry, skip_reason = ingest_file(md, source_root)
        if entry is None:
            ingest_skip_counts[skip_reason or 'unknown'] += 1
            continue

        if entry.extra.get('date_source') == 'mtime':
            mtime_fallback_count += 1

        slug = slugify(entry.title)
        base_name = f'{entry.date}_{slug}_{entry.id}.md'
        if base_name in seen_names:
            seen_names[base_name] += 1
            base_name = f'{entry.date}_{slug}_{entry.id}_{seen_names[base_name]}.md'
        else:
            seen_names[base_name] = 0

        out_path = entries_dir / base_name
        try:
            out_path.write_text(entry.to_markdown(), encoding='utf-8', newline='\n')
            written += 1
        except Exception as exc:
            log(f'WRITE ERROR: {out_path} -- {exc}')
            ingest_skip_counts['write_error'] += 1
            continue

        produced.append(
            {
                'id': entry.id,
                'file': base_name,
                'date': entry.date,
                'title': entry.title,
                'source_top': entry.source_top,
                'source_category': entry.source_category,
                'source_subcategory': entry.source_subcategory,
                'source_relative': entry.source_relative,
                'word_count': entry.word_count,
                'tags': entry.tags,
            }
        )

        if idx % 200 == 0:
            log(f'  ... processed {idx}/{len(md_files)}')

    total_skipped = sum(skip_breakdown.values()) + sum(ingest_skip_counts.values())
    ingest_log.parent.mkdir(parents=True, exist_ok=True)
    ingest_log.write_text(
        json.dumps(
            {
                'source_root': str(source_root),
                'wiki_root': str(wiki_root),
                'entries_dir': str(entries_dir),
                'total_files': len(md_files),
                'written': written,
                'skipped': total_skipped,
                'skipped_breakdown': dict(skip_breakdown + ingest_skip_counts),
                'ingested_at': datetime.now().isoformat(timespec='seconds'),
                'include_top_dirs': sorted(include_top_dirs) if include_top_dirs else None,
                'skip_dir_names': sorted(skip_dir_names),
                'submodule_paths': [p.as_posix() for p in submodule_paths],
                'mtime_fallback_count': mtime_fallback_count,
                'mtime_fallback_ratio': (mtime_fallback_count / written) if written else 0.0,
                'entries': produced,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding='utf-8',
    )

    combined_breakdown = skip_breakdown + ingest_skip_counts
    log(f'Scanned: {len(md_files)} files. Skipped: {total_skipped} ({format_breakdown(combined_breakdown)}). Ingested: {written} entries.')
    if written and (mtime_fallback_count / written) > 0.2:
        ratio = mtime_fallback_count / written * 100
        log(
            f'WARNING: {mtime_fallback_count} of {written} entries ({ratio:.1f}%) have mtime-only dates. '
            'These may be clustered on the checkout date.'
        )
    log(f'Log: {ingest_log}')
    return 0


if __name__ == '__main__':
    sys.exit(main(parse_args()))
