#!/usr/bin/env python3
"""Write hp:linesegarray for paragraphs and adjust table heights.

Modes:
- XML mode: process one section XML with one header XML.
- HWPX mode: unpack .hwpx, process all section*.xml, repack.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import lxml.etree as etree

HP_NS = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HS_NS = "http://www.hancom.co.kr/hwpml/2011/section"
HH_NS = "http://www.hancom.co.kr/hwpml/2011/head"
HC_NS = "http://www.hancom.co.kr/hwpml/2011/core"

NS = {
    "hp": HP_NS,
    "hs": HS_NS,
    "hh": HH_NS,
    "hc": HC_NS,
}

DEFAULT_BODY_WIDTH = 42520
DEFAULT_FONT_HEIGHT = 1000
DEFAULT_LS_TYPE = "PERCENT"
DEFAULT_LS_VALUE = 160
LINESEG_FLAGS = 393216


def _as_int(value: str | None, default: int = 0) -> int:
    """Return parsed int or default."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def estimate_char_width(char: str, font_height: int = 1000) -> int:
    """Estimate character width in hwpunit.

    Calibration (10pt 휴먼고딕 = font_height 1000):
    - Korean (가-힣): ~1000 -> 1.0 * font_height
    - Latin/digits: ~500 -> 0.5 * font_height
    - Punctuation/symbols: ~500 -> 0.5 * font_height
    - CJK fullwidth: ~1000 -> 1.0 * font_height
    - Space: ~250 -> 0.25 * font_height
    """
    if not char:
        return max(1, int(font_height * 0.5))

    code = ord(char)
    if char.isspace():
        ratio = 0.25
    elif 0xAC00 <= code <= 0xD7A3:
        ratio = 1.0
    elif 0x3000 <= code <= 0x303F:
        ratio = 1.0
    elif 0x3400 <= code <= 0x9FFF:
        ratio = 1.0
    elif 0xF900 <= code <= 0xFAFF:
        ratio = 1.0
    elif 0xFF01 <= code <= 0xFF60:
        ratio = 1.0
    elif 0xFFE0 <= code <= 0xFFE6:
        ratio = 1.0
    elif char.isascii() and char.isalnum():
        ratio = 0.5
    else:
        ratio = 0.5
    return max(1, int(font_height * ratio))


def calculate_spacing(font_height: int, ls_type: str, ls_value: int) -> int:
    """Calculate lineseg spacing from paraPr lineSpacing.

    - PERCENT: height * (value / 100) - height
    - FIXED: value - height (or 0)
    - BETWEEN: value
    default: PERCENT 160
    """
    kind = (ls_type or DEFAULT_LS_TYPE).upper()
    value = ls_value if ls_value > 0 else DEFAULT_LS_VALUE

    if kind == "PERCENT":
        spacing = int(font_height * (value / 100.0) - font_height)
    elif kind == "FIXED":
        spacing = max(0, value - font_height)
    elif kind == "BETWEEN":
        spacing = max(0, value)
    else:
        spacing = int(font_height * 0.6)
    return max(0, spacing)


def build_charpr_map(header_root: etree._Element) -> dict[str, int]:
    """Build map: charPr id -> height."""
    result: dict[str, int] = {}
    for node in header_root.xpath(".//hh:charPr", namespaces=NS):
        cid = node.get("id")
        if cid:
            result[cid] = _as_int(node.get("height"), DEFAULT_FONT_HEIGHT)
    return result


def build_parapr_map(header_root: etree._Element) -> dict[str, tuple[str, int]]:
    """Build map: paraPr id -> (lineSpacing type, value)."""
    result: dict[str, tuple[str, int]] = {}
    for node in header_root.xpath(".//hh:paraPr", namespaces=NS):
        pid = node.get("id")
        if not pid:
            continue

        ls_type = DEFAULT_LS_TYPE
        ls_value = DEFAULT_LS_VALUE
        ls_nodes = node.xpath(".//hh:lineSpacing", namespaces=NS)
        if ls_nodes:
            ls = ls_nodes[0]
            ls_type = ls.get("type", DEFAULT_LS_TYPE)
            ls_value = _as_int(ls.get("value"), DEFAULT_LS_VALUE)
        result[pid] = (ls_type, ls_value)
    return result


def propagate_paragraph_attrs(tc_element: etree._Element) -> None:
    """Copy core paragraph attrs in a cell from first p to others."""
    paragraphs = tc_element.xpath("./hp:subList/hp:p", namespaces=NS)
    if len(paragraphs) <= 1:
        return

    src = paragraphs[0]
    keys = ["paraPrIDRef", "styleIDRef", "pageBreak", "columnBreak", "merged"]
    attrs = {k: src.get(k) for k in keys if src.get(k) is not None}
    if not attrs:
        return

    for p_node in paragraphs[1:]:
        for key, value in attrs.items():
            p_node.set(key, value)


def _remove_linesegarray(p_element: etree._Element) -> None:
    """Remove all direct hp:linesegarray nodes."""
    for node in p_element.xpath("./hp:linesegarray", namespaces=NS):
        p_element.remove(node)


def _collect_text(p_element: etree._Element) -> str:
    """Collect text from hp:t and explicit hp:lineBreak."""
    parts: list[str] = []
    for node in p_element.xpath(".//hp:run/*", namespaces=NS):
        if not isinstance(node.tag, str):
            continue
        if node.tag == f"{{{HP_NS}}}t":
            parts.append(node.text or "")
        elif node.tag == f"{{{HP_NS}}}lineBreak":
            parts.append("\n")

    if parts:
        return "".join(parts)

    for t_node in p_element.xpath(".//hp:t", namespaces=NS):
        parts.append(t_node.text or "")
    return "".join(parts)


def _paragraph_font_height(p_element: etree._Element, cmap: dict[str, int]) -> int:
    """Get paragraph font height from first run's charPrIDRef."""
    run = p_element.find("./hp:run", NS)
    if run is None:
        return DEFAULT_FONT_HEIGHT
    cid = run.get("charPrIDRef")
    if not cid:
        return DEFAULT_FONT_HEIGHT
    return cmap.get(cid, DEFAULT_FONT_HEIGHT)


def _paragraph_line_spacing(
    p_element: etree._Element,
    pmap: dict[str, tuple[str, int]],
) -> tuple[str, int]:
    """Get paragraph line spacing info from paraPrIDRef."""
    pid = p_element.get("paraPrIDRef")
    if not pid:
        return (DEFAULT_LS_TYPE, DEFAULT_LS_VALUE)
    return pmap.get(pid, (DEFAULT_LS_TYPE, DEFAULT_LS_VALUE))


def _line_starts(text: str, width: int, font_height: int) -> list[int]:
    """Compute greedy wrapped line starts as character positions."""
    if not text:
        return [0]

    starts: list[int] = [0]
    limit = max(1, width)
    used = 0
    pos = 0

    for ch in text:
        if ch == "\n":
            pos += 1
            if pos < len(text):
                starts.append(pos)
            used = 0
            continue

        ch_w = estimate_char_width(ch, font_height)
        if used > 0 and used + ch_w > limit:
            starts.append(pos)
            used = 0
        used += ch_w
        pos += 1

    return starts or [0]


def _paragraph_width(p_element: etree._Element, body_width: int) -> int:
    """Get body width or table-cell width minus left/right margins."""
    tc_nodes = p_element.xpath("ancestor::hp:tc[1]", namespaces=NS)
    if not tc_nodes:
        return max(1, body_width)

    tc = tc_nodes[0]
    cell_sz = tc.find("./hp:cellSz", NS)
    if cell_sz is None:
        return max(1, body_width)

    margin = tc.find("./hp:cellMargin", NS)
    left = _as_int(margin.get("left") if margin is not None else None, 0)
    right = _as_int(margin.get("right") if margin is not None else None, 0)
    cell_width = _as_int(cell_sz.get("width"), body_width)
    return max(1, cell_width - left - right)


def _build_linesegarray(
    p_element: etree._Element,
    width: int,
    cmap: dict[str, int],
    pmap: dict[str, tuple[str, int]],
) -> tuple[etree._Element, int, int, int]:
    """Create linesegarray for one paragraph.

    Returns: (linesegarray, line_count, vertsize, spacing)
    """
    font_height = _paragraph_font_height(p_element, cmap)
    ls_type, ls_value = _paragraph_line_spacing(p_element, pmap)
    spacing = calculate_spacing(font_height, ls_type, ls_value)
    starts = _line_starts(_collect_text(p_element), width, font_height)

    baseline = int(font_height * 0.85)
    step = font_height + spacing
    lsa = etree.Element(f"{{{HP_NS}}}linesegarray")

    for i, start in enumerate(starts):
        seg = etree.SubElement(lsa, f"{{{HP_NS}}}lineseg")
        seg.set("textpos", str(start))
        seg.set("vertpos", str(i * step))
        seg.set("vertsize", str(font_height))
        seg.set("textheight", str(font_height))
        seg.set("baseline", str(baseline))
        seg.set("spacing", str(spacing))
        seg.set("horzpos", "0")
        seg.set("horzsize", str(max(1, width)))
        seg.set("flags", str(LINESEG_FLAGS))

    return lsa, len(starts), font_height, spacing


def process_paragraph(
    p_element: etree._Element,
    available_width: int,
    charpr_map: dict[str, int],
    parapr_map: dict[str, tuple[str, int]],
) -> bool:
    """Process single paragraph. Returns True on success.

    On ANY exception: remove existing linesegarray from this paragraph,
    log warning, and continue to next paragraph.
    """
    try:
        _remove_linesegarray(p_element)
        lsa, _, _, _ = _build_linesegarray(
            p_element,
            available_width,
            charpr_map,
            parapr_map,
        )
        p_element.append(lsa)
        return True
    except Exception as exc:  # noqa: BLE001
        _remove_linesegarray(p_element)
        pid = p_element.get("id", "unknown")
        print(f"WARNING: paragraph id={pid} failed: {exc}", file=sys.stderr)
        return False


def adjust_cell_height(
    tc_element: etree._Element, line_count: int, vertsize: int, spacing: int
) -> bool:
    """Adjust cellSz height if text requires more space."""
    cell_sz = tc_element.find("./hp:cellSz", NS)
    if cell_sz is None:
        return False

    margin = tc_element.find("./hp:cellMargin", NS)
    top = _as_int(margin.get("top") if margin is not None else None, 0)
    bottom = _as_int(margin.get("bottom") if margin is not None else None, 0)

    count = max(1, line_count)
    required = (count * vertsize) + ((count - 1) * max(0, spacing)) + top + bottom
    current = _as_int(cell_sz.get("height"), 0)
    if required > current:
        cell_sz.set("height", str(required))
        return True
    return False


def adjust_table_height(tbl_element: etree._Element) -> None:
    """Recalculate table hp:sz height based on row max heights."""
    table_sz = tbl_element.find("./hp:sz", NS)
    if table_sz is None:
        return

    total = 0
    for row in tbl_element.xpath("./hp:tr", namespaces=NS):
        row_h = 0
        for tc in row.xpath("./hp:tc", namespaces=NS):
            cell_sz = tc.find("./hp:cellSz", NS)
            if cell_sz is not None:
                row_h = max(row_h, _as_int(cell_sz.get("height"), 0))
        total += row_h

    if total > 0:
        table_sz.set("height", str(total))


def _process_cell(
    tc_element: etree._Element,
    cmap: dict[str, int],
    pmap: dict[str, tuple[str, int]],
    body_width: int,
) -> int:
    """Process one tc. Return count of generated paragraph linesegarrays."""
    propagate_paragraph_attrs(tc_element)
    count = 0
    content_height = 0

    paragraphs = tc_element.xpath("./hp:subList/hp:p", namespaces=NS)
    for p_node in paragraphs:
        width = _paragraph_width(p_node, body_width)
        if not process_paragraph(p_node, width, cmap, pmap):
            continue
        count += 1

        lsa = p_node.find("./hp:linesegarray", NS)
        if lsa is None:
            continue
        lines = lsa.xpath("./hp:lineseg", namespaces=NS)
        if not lines:
            continue

        first = lines[0]
        line_count = len(lines)
        vertsize = _as_int(first.get("vertsize"), DEFAULT_FONT_HEIGHT)
        spacing = _as_int(first.get("spacing"), int(DEFAULT_FONT_HEIGHT * 0.6))
        content_height += line_count * vertsize
        content_height += (line_count - 1) * max(0, spacing)

    if content_height > 0:
        adjust_cell_height(tc_element, 1, content_height, 0)
    return count


def process_section(
    section_root: etree._Element,
    header_root: etree._Element,
    body_width: int = 42520,
) -> int:
    """Process all paragraphs in a section.

    Returns count of generated linesegarrays.
    """
    count = 0
    cmap = build_charpr_map(header_root)
    pmap = build_parapr_map(header_root)

    handled: set[int] = set()
    for tc in section_root.xpath(".//hp:tc", namespaces=NS):
        count += _process_cell(tc, cmap, pmap, body_width)
        for p_node in tc.xpath("./hp:subList/hp:p", namespaces=NS):
            handled.add(id(p_node))

    for p_node in section_root.xpath(".//hp:p", namespaces=NS):
        if id(p_node) in handled:
            continue
        width = _paragraph_width(p_node, body_width)
        if process_paragraph(p_node, width, cmap, pmap):
            count += 1

    for table in section_root.xpath(".//hp:tbl", namespaces=NS):
        adjust_table_height(table)

    return count


def process_section_file(
    section_path: Path,
    header_path: Path,
    output_path: Path | None = None,
    body_width: int = 42520,
) -> int:
    """Process section XML file. Returns generated linesegarray count.

    If output_path is None, overwrite input file.
    """
    section_tree = etree.parse(str(section_path))
    header_tree = etree.parse(str(header_path))

    count = process_section(
        section_tree.getroot(),
        header_tree.getroot(),
        body_width=body_width,
    )

    target = output_path or section_path
    section_tree.write(
        str(target),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )
    return count


def _pack_hwpx(work_dir: Path, hwpx_path: Path) -> None:
    """Repack extracted files into HWPX format."""
    files = sorted(
        p.relative_to(work_dir).as_posix() for p in work_dir.rglob("*") if p.is_file()
    )

    mimetype = work_dir / "mimetype"
    with ZipFile(hwpx_path, "w", ZIP_DEFLATED) as zf:
        if mimetype.is_file():
            zf.write(mimetype, "mimetype", compress_type=ZIP_STORED)
        for rel in files:
            if rel == "mimetype":
                continue
            zf.write(work_dir / rel, rel, compress_type=ZIP_DEFLATED)


def process_hwpx_file(hwpx_path: Path, body_width: int = 42520) -> int:
    """Process HWPX in place: unpack -> process -> repack."""
    if not hwpx_path.is_file():
        raise SystemExit(f"HWPX file not found: {hwpx_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        with ZipFile(hwpx_path, "r") as zf:
            zf.extractall(tmp_root)

        contents = tmp_root / "Contents"
        header = contents / "header.xml"
        if not header.is_file():
            raise SystemExit(f"Missing Contents/header.xml in {hwpx_path}")

        total = 0
        for section in sorted(contents.glob("section*.xml")):
            total += process_section_file(section, header, section, body_width)

        _pack_hwpx(tmp_root, hwpx_path)
        return total


def main() -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Generate linesegarray and adjust cell heights in HWPX section XML"
    )

    # Mode A: Unpacked XML files
    parser.add_argument("--section", type=Path, help="Path to section0.xml")
    parser.add_argument("--header", type=Path, help="Path to header.xml")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output section XML (default: overwrite input)",
    )

    # Mode B: Packed HWPX file
    parser.add_argument(
        "--hwpx",
        type=Path,
        help="Process HWPX file in-place (unpack -> process -> repack)",
    )

    # Options
    parser.add_argument(
        "--body-width",
        type=int,
        default=42520,
        help="Body text width in hwpunit (default: 42520 for A4)",
    )

    args = parser.parse_args()

    if args.hwpx:
        count = process_hwpx_file(args.hwpx, body_width=args.body_width)
        print(f"Processed {count} paragraphs in {args.hwpx}")
        return

    if not args.section or not args.header:
        parser.error("XML mode requires both --section and --header")

    count = process_section_file(
        section_path=args.section,
        header_path=args.header,
        output_path=args.output,
        body_width=args.body_width,
    )
    target = args.output or args.section
    print(f"Processed {count} paragraphs -> {target}")


if __name__ == "__main__":
    main()
