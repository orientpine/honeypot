#!/usr/bin/env python3
"""Strip stale <hp:linesegarray> from HWPX section XML.

linesegarray is HWP's per-paragraph line-layout cache. Heuristic generation
cannot match HWP's real glyph metrics, so this utility only REMOVES the whole
element — Hancom recomputes layout on open. Heights are never mutated.

Modes:
- XML mode: strip one section XML (unpacked build path; lxml is fine here).
- HWPX mode: repair an already-built .hwpx through zip_surgery.write_zip(),
  so the XML declaration, namespaces, newline count, non-section bytes and
  per-entry compression stay byte-identical (surgery-safe).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import lxml.etree as etree

sys.path.insert(0, str(Path(__file__).parent))
from zip_surgery import read_zip, write_zip  # noqa: E402

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


_LSA_OPEN = re.compile(r"<[A-Za-z_][\w.-]*:linesegarray\b")


def _is_section_entry(name: str) -> bool:
    return name.startswith("Contents/") and "section" in name and name.endswith(".xml")


def process_hwpx_file(hwpx_path: Path, body_width: int = 42520) -> int:
    """Strip HWPX in place via zip_surgery.write_zip(). Returns total removed."""
    if not hwpx_path.is_file():
        raise SystemExit(f"HWPX file not found: {hwpx_path}")

    entries, order = read_zip(hwpx_path)
    total = sum(
        len(_LSA_OPEN.findall(entry.data.decode("utf-8", "replace")))
        for entry in entries
        if _is_section_entry(entry.filename)
    )
    write_zip(hwpx_path, entries, order)
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
