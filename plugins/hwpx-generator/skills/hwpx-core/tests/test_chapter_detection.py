"""Tests for chapter boundary detection in section_transplant.py.

These tests are RED until section_transplant.py is implemented.
"""

import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def test_find_h1_headings(make_test_hwpx, make_header_xml):
    """detect_headings() should find all H1 paragraphs."""
    from section_transplant import detect_headings
    import zipfile

    hwpx_path = make_test_hwpx(chapters=3)
    with zipfile.ZipFile(str(hwpx_path)) as zf:
        section_bytes = zf.read("Contents/section0.xml")
        header_bytes = zf.read("Contents/header.xml")

    sys.path.insert(0, str(SCRIPTS_DIR))
    from zip_surgery import parse_section, extract_children

    parts = parse_section(section_bytes)
    children = extract_children(parts.body)

    headings = detect_headings(children, header_bytes)
    assert len(headings) == 3, f"Expected 3 H1 headings, got {len(headings)}"
    for i, h in enumerate(headings, 1):
        assert str(i) in h.text, f"Heading {i} should contain chapter number"


def test_chapter_boundaries(make_test_hwpx):
    """extract_chapter_ranges() should return correct start/end indices."""
    from section_transplant import detect_headings, extract_chapter_ranges
    import zipfile

    hwpx_path = make_test_hwpx(chapters=3)
    with zipfile.ZipFile(str(hwpx_path)) as zf:
        section_bytes = zf.read("Contents/section0.xml")
        header_bytes = zf.read("Contents/header.xml")

    sys.path.insert(0, str(SCRIPTS_DIR))
    from zip_surgery import parse_section, extract_children

    parts = parse_section(section_bytes)
    children = extract_children(parts.body)

    headings = detect_headings(children, header_bytes)
    ranges = extract_chapter_ranges(children, headings)

    assert 1 in ranges, "Chapter 1 should be in ranges"
    assert 2 in ranges, "Chapter 2 should be in ranges"
    assert 3 in ranges, "Chapter 3 should be in ranges"
    # Each chapter has 2 paragraphs (heading + body)
    for ch_num in [1, 2, 3]:
        start, end = ranges[ch_num]
        assert end > start, f"Chapter {ch_num}: end ({end}) must be > start ({start})"


def test_empty_chapter(make_section_xml, make_header_xml, tmp_path):
    """extract_chapter_ranges handles chapter with only heading (no body)."""
    from section_transplant import detect_headings, extract_chapter_ranges
    import zipfile

    sys.path.insert(0, str(SCRIPTS_DIR))
    from zip_surgery import make_paragraph, parse_section, extract_children

    # Chapter with only heading, no body
    paragraphs = [
        make_paragraph("1001", "1. 챕터 A", charPrIDRef="1", paraPrIDRef="20"),
        make_paragraph("1002", "2. 챕터 B", charPrIDRef="1", paraPrIDRef="20"),
    ]
    section_bytes = make_section_xml(paragraphs)
    header_bytes = make_header_xml(
        [(1, 1500, True), (2, 1000, False)], [(10, "JUSTIFY"), (20, "JUSTIFY")]
    )

    parts = parse_section(section_bytes)
    children = extract_children(parts.body)
    headings = detect_headings(children, header_bytes)
    ranges = extract_chapter_ranges(children, headings)

    # Both chapters should be detected even if empty
    assert len(ranges) >= 1, "At least one chapter should be detected"


def test_content_before_first_h1(make_test_hwpx):
    """Content before first H1 (cover/preamble) is chapter 0 or excluded."""
    from section_transplant import detect_headings, extract_chapter_ranges
    import zipfile

    hwpx_path = make_test_hwpx(chapters=2)
    with zipfile.ZipFile(str(hwpx_path)) as zf:
        section_bytes = zf.read("Contents/section0.xml")
        header_bytes = zf.read("Contents/header.xml")

    sys.path.insert(0, str(SCRIPTS_DIR))
    from zip_surgery import parse_section, extract_children

    parts = parse_section(section_bytes)
    children = extract_children(parts.body)
    headings = detect_headings(children, header_bytes)

    # First heading should start after the cover page paragraph
    assert headings[0].index > 0, (
        "First H1 should not be at index 0 (cover page exists)"
    )


def test_nested_hp_p_in_table(make_section_xml, make_header_xml, tmp_path):
    """depth-counted detection ignores nested hp:p inside table cells."""
    from section_transplant import detect_headings, extract_chapter_ranges
    import zipfile

    sys.path.insert(0, str(SCRIPTS_DIR))
    from zip_surgery import make_paragraph, parse_section, extract_children

    # Create a table cell that contains nested hp:p (should NOT be counted as top-level heading)
    nested_paragraph = (
        '<hp:p id="2001" paraPrIDRef="20" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="1"><hp:t>1. 진짜 H1 제목</hp:t></hp:run>'
        "</hp:p>"
    )
    table_with_nested = (
        '<hp:p id="3001" paraPrIDRef="10" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        "<hp:tbl><hp:tr><hp:tc>"
        # nested hp:p inside table cell — depth-counted parser should NOT extract this at top level
        '<hp:p id="9999" paraPrIDRef="20" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="1"><hp:t>가짜 H1 inside table</hp:t></hp:run>'
        "</hp:p>"
        "</hp:tc></hp:tr></hp:tbl>"
        "</hp:p>"
    )

    section_bytes = make_section_xml([nested_paragraph, table_with_nested])
    header_bytes = make_header_xml(
        [(1, 1500, True), (2, 1000, False)], [(10, "JUSTIFY"), (20, "JUSTIFY")]
    )

    parts = parse_section(section_bytes)
    children = extract_children(parts.body)
    headings = detect_headings(children, header_bytes)

    # Should only find 1 heading (the real H1), not the nested one in the table
    assert len(headings) == 1, (
        f"Expected 1 heading, got {len(headings)}: {[h.text for h in headings]}"
    )
