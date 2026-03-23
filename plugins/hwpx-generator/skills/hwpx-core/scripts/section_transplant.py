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
from typing import Callable

_ = (sys, warnings, field, Path)

StyleIdMapping = dict[str, dict[str, str]]


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


@dataclass
class CharStyle:
    """Parsed charPr attributes from header.xml."""

    id: str
    font_size: int
    bold: bool = False


@dataclass
class ParaStyle:
    """Parsed paraPr attributes from header.xml."""

    id: str
    align: str = "JUSTIFY"


@dataclass
class StyleMap:
    """Extracted style definitions from header.xml."""

    char_styles: dict[str, CharStyle]
    para_styles: dict[str, ParaStyle]


def parse_header_styles(header_bytes: bytes) -> StyleMap:
    """Extract charPr and paraPr definitions from header.xml bytes.

    Uses regex only — no XML parser.
    """
    text = header_bytes.decode("utf-8", errors="replace")

    char_styles: dict[str, CharStyle] = {}
    para_styles: dict[str, ParaStyle] = {}

    charpr_pattern = re.compile(
        r'<hh:charPr\s+id="(\d+)"[^>]*>(.*?)</hh:charPr>', re.DOTALL
    )
    fontsize_pattern = re.compile(r'<hh:fontSize[^>]*\ssize="(\d+)"')
    bold_pattern = re.compile(r'\bbold="1"')

    for match in charpr_pattern.finditer(text):
        cid = match.group(1)
        block = match.group(2)
        fs_match = fontsize_pattern.search(block)
        font_size = int(fs_match.group(1)) if fs_match else 0
        bold = bool(bold_pattern.search(block))
        char_styles[cid] = CharStyle(id=cid, font_size=font_size, bold=bold)

    parapr_pattern = re.compile(
        r'<hh:paraPr\s+id="(\d+)"[^>]*>(.*?)</hh:paraPr>', re.DOTALL
    )
    align_pattern = re.compile(r'<hh:alignment[^>]*\stype="([^"]+)"')

    for match in parapr_pattern.finditer(text):
        pid = match.group(1)
        block = match.group(2)
        align_match = align_pattern.search(block)
        align = align_match.group(1) if align_match else "JUSTIFY"
        para_styles[pid] = ParaStyle(id=pid, align=align)

    return StyleMap(char_styles=char_styles, para_styles=para_styles)


def build_style_mapping(
    source_styles: StyleMap,
    target_styles: StyleMap,
) -> dict[str, dict[str, str]]:
    """Build {attr_type: {source_id: target_id}} mapping.

    Matches charPr by (font_size, bold). ID "0" always maps to "0".
    Unmatched source IDs keep their original value (with warning).
    """
    mapping: dict[str, dict[str, str]] = {
        "charPrIDRef": {},
        "paraPrIDRef": {},
        "borderFillIDRef": {},
        "styleIDRef": {},
    }

    mapping["charPrIDRef"]["0"] = "0"
    mapping["paraPrIDRef"]["0"] = "0"
    mapping["borderFillIDRef"]["0"] = "0"
    mapping["styleIDRef"]["0"] = "0"

    target_char_by_attrs: dict[tuple[int, bool], str] = {}
    for tid, target_style in target_styles.char_styles.items():
        key = (target_style.font_size, target_style.bold)
        target_char_by_attrs[key] = tid

    for sid, source_style in source_styles.char_styles.items():
        if sid == "0":
            continue
        key = (source_style.font_size, source_style.bold)
        if key in target_char_by_attrs:
            mapping["charPrIDRef"][sid] = target_char_by_attrs[key]
        else:
            warnings.warn(
                f"charPr id={sid} (size={source_style.font_size}, bold={source_style.bold}) has no match in target — keeping original ID",
                stacklevel=2,
            )
            mapping["charPrIDRef"][sid] = sid

    target_para_by_align: dict[str, str] = {}
    for tid, target_style in target_styles.para_styles.items():
        if target_style.align not in target_para_by_align:
            target_para_by_align[target_style.align] = tid

    for sid, source_style in source_styles.para_styles.items():
        if sid == "0":
            continue
        if source_style.align in target_para_by_align:
            mapping["paraPrIDRef"][sid] = target_para_by_align[source_style.align]
        else:
            warnings.warn(
                f"paraPr id={sid} (align={source_style.align}) has no match in target — keeping original ID",
                stacklevel=2,
            )
            mapping["paraPrIDRef"][sid] = sid

    return mapping


_SECPR_TAG = "<hp:secPr"
_PIC_TAG = "<hp:pic"


def remap_style_ids(paragraph_xml: str, mapping: StyleIdMapping) -> str:
    result = paragraph_xml

    for attr in ("charPrIDRef", "paraPrIDRef", "borderFillIDRef", "styleIDRef"):
        attr_map = mapping.get(attr, {})
        if not attr_map:
            continue

        def _make_sub(m: dict[str, str]) -> Callable[[re.Match[str]], str]:
            def _sub(match: re.Match[str]) -> str:
                src_id = match.group(2)
                if src_id == "0":
                    return match.group(0)
                target_id = m.get(src_id, src_id)
                return f"{match.group(1)}{target_id}{match.group(3)}"

            return _sub

        pattern = re.compile(rf'({re.escape(attr)}=")(\d+)(")')
        result = pattern.sub(_make_sub(attr_map), result)

    return result


def remap_chapters(chapters_xml: list[str], mapping: StyleIdMapping) -> list[str]:
    result: list[str] = []
    for para in chapters_xml:
        if _SECPR_TAG in para:
            continue
        if _PIC_TAG in para:
            warnings.warn(
                "hp:pic found in transplanted chapter — image binary data is NOT transplanted; image reference may be broken.",
                stacklevel=2,
            )
        result.append(remap_style_ids(para, mapping))
    return result
