#!/usr/bin/env python3
"""Strip stale <hp:linesegarray> from HWPX section XML.

linesegarray is HWP's per-paragraph line-layout cache. Heuristic generation
cannot match HWP's real glyph metrics, so this utility only REMOVES the whole
element — Hancom recomputes layout on open. Heights are never mutated.

Modes:
- XML mode: strip one section XML.
- HWPX mode: unpack .hwpx, strip all section*.xml, repack.
"""

from __future__ import annotations

import argparse
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


def _remove_linesegarray(root: etree._Element) -> int:
    """Remove every hp:linesegarray under root. Returns count removed."""
    count = 0
    for node in root.xpath(".//hp:linesegarray", namespaces=NS):
        node.getparent().remove(node)
        count += 1
    return count


def process_section(
    section_root: etree._Element,
    header_root: etree._Element | None = None,
    body_width: int = 42520,
) -> int:
    """Strip all linesegarray from a section. Returns count removed."""
    return _remove_linesegarray(section_root)


def process_section_file(
    section_path: Path,
    header_path: Path | None = None,
    output_path: Path | None = None,
    body_width: int = 42520,
) -> int:
    """Parse, strip, write a section XML. Returns count removed.

    If output_path is None, overwrite input file.
    """
    section_tree = etree.parse(str(section_path))
    count = process_section(section_tree.getroot(), None, body_width=body_width)

    target = output_path or section_path
    section_tree.write(
        str(target),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )
    return count


def _pack_hwpx(work_dir: Path, hwpx_path: Path) -> None:
    """Repack extracted files into HWPX format (mimetype first, ZIP_STORED)."""
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
    """Strip HWPX in place: unpack -> strip -> repack. Returns total removed."""
    if not hwpx_path.is_file():
        raise SystemExit(f"HWPX file not found: {hwpx_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        with ZipFile(hwpx_path, "r") as zf:
            zf.extractall(tmp_root)

        contents = tmp_root / "Contents"
        total = 0
        for section in sorted(contents.glob("section*.xml")):
            total += process_section_file(section, None, section, body_width)

        _pack_hwpx(tmp_root, hwpx_path)
        return total


def main() -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Strip stale <hp:linesegarray> from HWPX section XML"
    )

    # Mode A: Unpacked XML files
    parser.add_argument("--section", type=Path, help="Path to section0.xml")
    parser.add_argument("--header", type=Path, help="Path to header.xml (ignored)")
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
        help="Strip HWPX file in-place (unpack -> strip -> repack)",
    )

    # Options
    parser.add_argument(
        "--body-width",
        type=int,
        default=42520,
        help="Accepted for backward compatibility (unused)",
    )

    args = parser.parse_args()

    if args.hwpx:
        count = process_hwpx_file(args.hwpx, body_width=args.body_width)
        print(f"Stripped {count} linesegarray in {args.hwpx}")
        return

    if not args.section:
        parser.error("XML mode requires --section")

    count = process_section_file(
        section_path=args.section,
        header_path=args.header,
        output_path=args.output,
        body_width=args.body_width,
    )
    target = args.output or args.section
    print(f"Stripped {count} linesegarray -> {target}")


if __name__ == "__main__":
    main()
