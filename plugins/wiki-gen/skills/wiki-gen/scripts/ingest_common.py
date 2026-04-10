#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SKIP_DIR_NAMES = {
    # Version control
    '.git',
    '.svn',
    '.hg',
    # Obsidian meta
    '.obsidian',
    '.trash',
    # AI/IDE settings
    '.claude',
    '.cursor',
    '.vscode',
    '.opencode',
    '.idea',
    # Python/Node caches
    '.ruff_cache',
    '.mypy_cache',
    '.pytest_cache',
    '__pycache__',
    '.venv',
    'venv',
    'env',
    # JS dependencies
    'node_modules',
    # OS noise
    '.DS_Store',
    'Thumbs.db',
}

# Date regexes
DATE_YYYYMMDD = re.compile(r'(?<!\d)(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})(?!\d)')
ISO_DATETIME = re.compile(
    r'^\s*(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})(?:[T ](?P<H>\d{2}):(?P<M>\d{2})(?::(?P<S>\d{2}))?)?'
)

@dataclass
class Entry:
    """A normalized wiki-gen entry."""

    id: str
    date: str
    time: str
    title: str
    source_type: str
    source_path: str
    source_relative: str
    source_top: str
    source_category: str
    source_subcategory: str
    tags: list[str] = field(default_factory=list)
    author: str | None = None
    word_count: int = 0
    char_count: int = 0
    line_count: int = 0
    aliases: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
    body: str = ''

    def to_markdown(self) -> str:
        fm: dict[str, Any] = {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'title': self.title,
            'source_type': self.source_type,
            'source_category': self.source_category,
            'source_subcategory': self.source_subcategory,
            'source_top': self.source_top,
            'source_relative': self.source_relative,
            'tags': self.tags,
            'author': self.author or '',
            'aliases': self.aliases,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'line_count': self.line_count,
        }
        if self.extra:
            fm['extra'] = self.extra
        yaml_text = yaml.safe_dump(
            fm,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=10000,
        )
        return f"---\n{yaml_text}---\n\n{self.body}\n"


def log(msg: str) -> None:
    print(msg, flush=True)


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    items = {item.strip() for item in value.split(',') if item.strip()}
    return items or None


def slugify(text: str, max_length: int = 60) -> str:
    """Return a filesystem-safe slug preserving Korean characters.

    Removes unsafe path chars. Collapses whitespace and underscores.
    Trims to max_length characters.
    """
    text = text.strip()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[\/:*?"<>|\n	]+', '_', text)
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_.')
    if len(text) > max_length:
        text = text[:max_length].rstrip('_.')
    return text or 'entry'


def parse_yaml_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Extract YAML frontmatter if present. Returns (fm_dict, remaining_body)."""
    if not text.startswith('---'):
        return None, text
    end = text.find('\n---', 3)
    if end == -1:
        return None, text
    fm_text = text[3:end].strip('\n')
    remaining = text[end + 4 :]
    if remaining.startswith('\n'):
        remaining = remaining[1:]
    if remaining.startswith('\n'):
        remaining = remaining[1:]
    try:
        data = yaml.safe_load(fm_text) or {}
        if not isinstance(data, dict):
            return None, text
        return data, remaining
    except yaml.YAMLError:
        return None, text

def extract_heading_title(text: str) -> tuple[str | None, str]:
    """If first non-blank line is '# title', extract and return (title, remaining_text)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() == '':
        i += 1
    if i >= len(lines):
        return None, text
    m = re.match(r'^\s*#\s+(.+?)\s*$', lines[i])
    if not m:
        return None, text
    title = m.group(1).strip()
    remaining = '\n'.join(lines[i + 1 :]).lstrip('\n')
    return title, remaining


def extract_tags(text: str) -> list[str]:
    """Find #tag style tags in content."""
    raw = re.findall(r'(?<!\w)#([A-Za-z0-9가-힣_\-/]+)', text)
    return sorted({t for t in raw if not t.isdigit()})


def _valid_date(y: int, m: int, d: int) -> bool:
    """Validate a Gregorian-ish date: year 1990-2030, month 1-12, day 1-31."""
    if not (1990 <= y <= 2030):
        return False
    if not (1 <= m <= 12):
        return False
    if not (1 <= d <= 31):
        return False
    return True


def _extract_path_year(rel_path: str) -> str | None:
    """Find a 4-digit year 1990-2030 in the source path (e.g. Archive/2024/..)."""
    for m in re.finditer(r'(?<!\d)(19\d{2}|20[0-2]\d)(?!\d)', rel_path):
        y = int(m.group(1))
        if 1990 <= y <= 2030:
            return m.group(1)
    return None


def parse_date_fields(
    fm: dict[str, Any],
    callout: dict[str, str],
    filename_stem: str,
    file_stat: os.stat_result,
    source_relative: str,
) -> tuple[str, str, str]:
    """Determine the best (date, time, source) for this entry.

    Priority:
    1. YAML frontmatter 'created'
    2. YAML frontmatter 'date'
    3. YAML frontmatter 'modified'
    4. Callout 'created'
    5. Date pattern in filename stem
    6. Date pattern in source path
    7. Year hint from source path + January 1
    8. File mtime
    """
    for key in ('created', 'date', 'modified'):
        val = fm.get(key)
        if not val:
            continue
        s = str(val)
        m = ISO_DATETIME.match(s)
        if m:
            y, mo, d = int(m.group('y')), int(m.group('m')), int(m.group('d'))
            if _valid_date(y, mo, d):
                time_s = (
                    f"{m.group('H')}:{m.group('M')}:{m.group('S') or '00'}"
                    if m.group('H')
                    else '00:00:00'
                )
                return f'{y:04d}-{mo:02d}-{d:02d}', time_s, f'fm.{key}'

    created_value = callout.get('created', '')
    if created_value and '`=' not in created_value:
        m = ISO_DATETIME.match(created_value)
        if m:
            y, mo, d = int(m.group('y')), int(m.group('m')), int(m.group('d'))
            if _valid_date(y, mo, d):
                return f'{y:04d}-{mo:02d}-{d:02d}', '00:00:00', 'callout.created'

    for m in DATE_YYYYMMDD.finditer(filename_stem):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}', '00:00:00', 'filename'

    for m in DATE_YYYYMMDD.finditer(source_relative):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}', '00:00:00', 'source_path'

    path_year = _extract_path_year(source_relative)
    if path_year:
        return f'{path_year}-01-01', '00:00:00', 'source_year'

    dt = datetime.fromtimestamp(file_stat.st_mtime)
    return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S'), 'mtime'

def coerce_tag_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip().lstrip('#') for x in value if str(x).strip()]
    if isinstance(value, str):
        parts = re.split(r'[,\s]+', value.strip())
        return [p.lstrip('#') for p in parts if p]
    return [str(value)]


def coerce_alias_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(value)]


def count_markdown_files(tree_root: Path) -> int:
    count = 0
    for p in tree_root.rglob('*.md'):
        if p.is_file():
            count += 1
    return count

def format_breakdown(counter: Counter) -> str:
    if not counter:
        return 'none'
    return ', '.join(f'{key}={value}' for key, value in sorted(counter.items()))
