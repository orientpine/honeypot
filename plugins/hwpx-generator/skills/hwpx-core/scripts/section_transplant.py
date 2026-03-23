#!/usr/bin/env python3
"""HWPX Section Transplant — chapter-level content migration tool.

Transplants chapters from a source HWPX into a target HWPX,
with automatic style ID remapping based on header.xml analysis.

Guardrails (NEVER violate):
  - No lxml, xml.etree, or BeautifulSoup imports
  - No bare string replace for style IDs
  - Never modify source or target originals
  - Never insert newlines between child elements
"""

from __future__ import annotations

import re
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path

_ = (sys, warnings, field, Path)


@dataclass
class HeadingInfo:
    index: int
    text: str
    char_pr_id: str
    chapter_num: int


def _top_level_view(paragraph_xml: str) -> str:
    nested_start = paragraph_xml.find("<hp:p", 1)
    if nested_start == -1:
        return paragraph_xml
    return paragraph_xml[:nested_start]


def _parse_font_sizes(header_xml: bytes) -> dict[str, int]:
    text = header_xml.decode("utf-8", errors="replace")
    result: dict[str, int] = {}

    charpr_pattern = re.compile(
        r'<hh:charPr\s+id="(\d+)"[^>]*>(.*?)</hh:charPr>', re.DOTALL
    )
    fontsize_pattern = re.compile(r'<hh:fontSize[^>]*\ssize="(\d+)"')

    for match in charpr_pattern.finditer(text):
        cid = match.group(1)
        block = match.group(2)
        fs_match = fontsize_pattern.search(block)
        if fs_match:
            result[cid] = int(fs_match.group(1))
    return result


def _extract_text(paragraph_xml: str) -> str:
    visible_xml = _top_level_view(paragraph_xml)
    return "".join(re.findall(r"<hp:t>(.*?)</hp:t>", visible_xml, re.DOTALL)).strip()


def _get_char_pr_id(paragraph_xml: str) -> str | None:
    visible_xml = _top_level_view(paragraph_xml)
    match = re.search(r'charPrIDRef="(\d+)"', visible_xml)
    return match.group(1) if match else None


def detect_headings(children: list[str], header_xml: bytes) -> list[HeadingInfo]:
    font_sizes = _parse_font_sizes(header_xml)
    if not font_sizes:
        return []

    max_size = max(font_sizes.values())
    h1_ids = {cid for cid, size in font_sizes.items() if size == max_size}

    headings: list[HeadingInfo] = []
    for idx, paragraph_xml in enumerate(children):
        char_pr_id = _get_char_pr_id(paragraph_xml)
        if not char_pr_id or char_pr_id not in h1_ids:
            continue

        text = _extract_text(paragraph_xml)
        chapter_match = re.match(r"^(\d+)\.", text)
        chapter_num = int(chapter_match.group(1)) if chapter_match else 0

        headings.append(
            HeadingInfo(
                index=idx,
                text=text,
                char_pr_id=char_pr_id,
                chapter_num=chapter_num,
            )
        )

    return headings


def extract_chapter_ranges(
    children: list[str],
    headings: list[HeadingInfo],
) -> dict[int, tuple[int, int]]:
    ranges: dict[int, tuple[int, int]] = {}
    total = len(children)

    for i, heading in enumerate(headings):
        start = heading.index
        if i + 1 < len(headings):
            end = headings[i + 1].index - 1
        else:
            end = total - 1

        chapter_num = heading.chapter_num if heading.chapter_num > 0 else (i + 1)
        ranges[chapter_num] = (start, end)

    return ranges
