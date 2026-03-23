#!/usr/bin/env python3
"""Safe ZIP-level surgery for HWPX files.

This is the ONLY safe method for editing existing HWPX documents while
preserving byte-level fidelity.  It uses raw string operations instead
of ElementTree to avoid XML declaration, namespace, and whitespace corruption.

Preserves:
  - ZIP entry order and compression types
  - XML declaration (including standalone='no' and quote style)
  - All namespace declarations on root <hs:sec> tag
  - Single-line XML body (no added newlines)
  - Byte-identical non-modified entries

Safety rules:
  - NEVER use ET.tostring() or tree.write() on section XML
  - NEVER insert newlines between child elements
  - NEVER run cell_writer.py on surgery output (Hangul recalculates layout)
  - ALWAYS validate with validate_surgery() after editing

Usage:
    # Library
    from zip_surgery import HwpxSurgeon
    surgeon = HwpxSurgeon('document.hwpx')
    children = surgeon.extract_children()
    children.append(surgeon.make_paragraph('9999', 'New text'))
    surgeon.replace_children(children)
    surgeon.save('output.hwpx')

    # CLI
    python zip_surgery.py extract document.hwpx -o section0.xml
    python zip_surgery.py replace document.hwpx -s new_section0.xml -o result.hwpx
    python zip_surgery.py validate original.hwpx result.hwpx
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ZipEntry:
    """One entry in a ZIP archive with preserved metadata."""

    filename: str
    data: bytes
    compress_type: int
    date_time: tuple[int, int, int, int, int, int] = field(
        default_factory=lambda: (1980, 1, 1, 0, 0, 0)
    )
    external_attr: int = 0
    create_system: int = 0
    create_version: int = 20
    extract_version: int = 20
    flag_bits: int = 0
    comment: bytes = field(default_factory=bytes)
    extra: bytes = field(default_factory=bytes)
    internal_attr: int = 0
    volume: int = 0


@dataclass
class SectionParts:
    """Parsed section0.xml components (string-level, no ET)."""

    xml_header: str  # XML declaration + root open tag (with all xmlns)
    body: str  # Everything between root open and close tags
    root_close_tag: str  # "</hs:sec>"


# ---------------------------------------------------------------------------
# ZIP operations — preserve order and compression types
# ---------------------------------------------------------------------------


def read_zip(hwpx_path: str | Path) -> tuple[list[ZipEntry], list[str]]:
    """Read all ZIP entries preserving order and compression types.

    Returns (entries, entry_order).
    """
    entries: list[ZipEntry] = []
    order: list[str] = []

    with zipfile.ZipFile(str(hwpx_path), "r") as zin:
        for info in zin.infolist():
            entries.append(
                ZipEntry(
                    filename=info.filename,
                    data=zin.read(info.filename),
                    compress_type=info.compress_type,
                    date_time=info.date_time,
                    external_attr=info.external_attr,
                    create_system=info.create_system,
                    create_version=info.create_version,
                    extract_version=info.extract_version,
                    flag_bits=info.flag_bits,
                    comment=info.comment,
                    extra=info.extra,
                    internal_attr=info.internal_attr,
                    volume=info.volume,
                )
            )
            order.append(info.filename)

    return entries, order


def write_zip(
    output_path: str | Path,
    entries: list[ZipEntry],
    order: list[str],
    modified: dict[str, bytes] | None = None,
) -> None:
    """Write ZIP archive preserving entry order and compression types.

    Only entries listed in ``modified`` are replaced; everything else is
    copied byte-identical with the original compression type.
    """
    modified = modified or {}
    entry_map = {e.filename: e for e in entries}

    with zipfile.ZipFile(str(output_path), "w") as zout:
        for name in order:
            entry = entry_map[name]
            info = zipfile.ZipInfo(name)
            info.compress_type = entry.compress_type
            info.date_time = entry.date_time
            info.external_attr = entry.external_attr
            info.create_system = entry.create_system
            info.create_version = entry.create_version
            info.extract_version = entry.extract_version
            info.flag_bits = entry.flag_bits
            info.comment = entry.comment
            info.extra = entry.extra
            info.internal_attr = entry.internal_attr
            data = modified.get(name, entry.data)
            zout.writestr(info, data)


# ---------------------------------------------------------------------------
# Section XML parsing — string-level only, NEVER ElementTree
# ---------------------------------------------------------------------------


def parse_section(xml_bytes: bytes) -> SectionParts:
    """Parse section XML into components using string operations only.

    Preserves XML declaration (including standalone='no' and quote style)
    and all namespace declarations on the root tag exactly as-is.
    """
    text = xml_bytes.decode("utf-8")

    # Locate root tag
    root_start = text.find("<hs:sec")
    if root_start == -1:
        raise ValueError("No <hs:sec> root tag found in section XML")

    root_open_end = text.find(">", root_start) + 1
    if root_open_end == 0:
        raise ValueError("Malformed <hs:sec> root tag — no closing >")

    # Everything up to and including root open tag (XML decl + root tag)
    xml_header = text[:root_open_end]

    # Closing tag
    closing_tag = "</hs:sec>"
    closing_pos = text.rfind(closing_tag)
    if closing_pos == -1:
        raise ValueError("No closing </hs:sec> tag found")

    body = text[root_open_end:closing_pos]

    return SectionParts(
        xml_header=xml_header,
        body=body,
        root_close_tag=closing_tag,
    )


def extract_children(body_text: str, tag: str = "hp:p") -> list[str]:
    """Extract top-level child elements from body text via string slicing.

    Uses depth counting to handle nested elements (e.g. <hp:p> inside
    table cells).  Each returned string is byte-identical to the original.
    """
    OPEN = f"<{tag}"
    CLOSE = f"</{tag}>"

    slices: list[str] = []
    pos = 0

    while pos < len(body_text):
        start = body_text.find(OPEN, pos)
        if start == -1:
            break

        depth = 0
        scan = start
        found = False

        while True:
            next_o = body_text.find(OPEN, scan + 1)
            next_c = body_text.find(CLOSE, scan + 1)

            if next_c == -1:
                break

            if next_o != -1 and next_o < next_c:
                ch = body_text[next_o + len(OPEN)]
                if ch in (" ", ">", "/"):
                    depth += 1
                scan = next_o
            else:
                if depth == 0:
                    end = next_c + len(CLOSE)
                    slices.append(body_text[start:end])
                    pos = end
                    found = True
                    break
                depth -= 1
                scan = next_c

        if not found:
            break

    return slices


def assemble_section(parts: SectionParts, children: list[str]) -> bytes:
    """Assemble section XML from header, children, and close tag.

    Rules:
      - XML declaration preserved exactly (from xml_header)
      - No newlines between child elements
      - Only 1 newline in entire file: the one after XML declaration
        (already embedded in xml_header)
    """
    result = parts.xml_header + "".join(children) + parts.root_close_tag
    return result.encode("utf-8")


# ---------------------------------------------------------------------------
# Element creation — string-based, no ElementTree
# ---------------------------------------------------------------------------


def _xml_escape(text: str) -> str:
    """Escape special XML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def make_paragraph(
    pid: str,
    text: str,
    paraPrIDRef: str = "0",
    charPrIDRef: str = "0",
    styleIDRef: str = "0",
) -> str:
    """Create a <hp:p> element as a string.

    Uses namespace prefixes only (xmlns declarations live on root tag).
    """
    if not text:
        t_elem = "<hp:t/>"
    else:
        t_elem = f"<hp:t>{_xml_escape(text)}</hp:t>"

    return (
        f'<hp:p id="{pid}" paraPrIDRef="{paraPrIDRef}" '
        f'styleIDRef="{styleIDRef}" pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="{charPrIDRef}">{t_elem}</hp:run>'
        f"</hp:p>"
    )


def make_empty_paragraph(pid: str, paraPrIDRef: str = "0") -> str:
    """Create an empty paragraph (blank line)."""
    return (
        f'<hp:p id="{pid}" paraPrIDRef="{paraPrIDRef}" '
        f'styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0"><hp:t/></hp:run>'
        f"</hp:p>"
    )


def make_multi_run_paragraph(
    pid: str,
    runs: list[tuple[str, str]],
    paraPrIDRef: str = "0",
    styleIDRef: str = "0",
) -> str:
    """Create a paragraph with multiple styled runs.

    Args:
        runs: List of (charPrIDRef, text) tuples.
    """
    run_parts: list[str] = []
    for char_id, text in runs:
        if not text:
            t_elem = "<hp:t/>"
        else:
            t_elem = f"<hp:t>{_xml_escape(text)}</hp:t>"
        run_parts.append(f'<hp:run charPrIDRef="{char_id}">{t_elem}</hp:run>')

    return (
        f'<hp:p id="{pid}" paraPrIDRef="{paraPrIDRef}" '
        f'styleIDRef="{styleIDRef}" pageBreak="0" columnBreak="0" merged="0">'
        f"{''.join(run_parts)}"
        f"</hp:p>"
    )


# ---------------------------------------------------------------------------
# Text replacement — safe in-place editing
# ---------------------------------------------------------------------------


def replace_text_in_section(
    section_bytes: bytes,
    replacements: dict[str, str],
) -> bytes:
    """Replace text content within section XML without touching structure.

    Operates on the raw XML string — no parsing, no serialization.
    Preserves XML declaration, namespaces, and formatting exactly.
    """
    text = section_bytes.decode("utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Post-surgery validation
# ---------------------------------------------------------------------------


def validate_surgery(
    original_path: str | Path,
    result_path: str | Path,
) -> list[str]:
    """Validate that ZIP-level surgery preserved file integrity.

    Checks:
      1. standalone='no' preserved in section0.xml
      2. Sufficient xmlns declarations on root tag
      3. Only 1 newline in section0.xml (after XML declaration)
      4. No xmlns declarations in body (all on root tag)
      5. Non-section files byte-identical to original
      6. ZIP entry order preserved
      7. ZIP compression types preserved
    """
    errors: list[str] = []

    orig_entries, orig_order = read_zip(original_path)
    result_entries, result_order = read_zip(result_path)

    orig_map = {e.filename: e for e in orig_entries}
    result_map = {e.filename: e for e in result_entries}

    # 1. Entry order
    if orig_order != result_order:
        errors.append(
            f"ZIP entry order changed: "
            f"original={len(orig_order)} entries, result={len(result_order)}"
        )

    # 2. Compression types
    for name in orig_order:
        if name in result_map and name in orig_map:
            if orig_map[name].compress_type != result_map[name].compress_type:
                errors.append(
                    f"Compression type changed for {name}: "
                    f"{orig_map[name].compress_type} -> "
                    f"{result_map[name].compress_type}"
                )

    # 3. section0.xml specifics
    section_name = "Contents/section0.xml"
    if section_name in result_map:
        sec_text = result_map[section_name].data.decode("utf-8")

        # standalone='no'
        decl = sec_text[:200]
        if "standalone='no'" not in decl and 'standalone="no"' not in decl:
            errors.append("standalone='no' missing from section0.xml XML declaration")

        # xmlns count on root tag
        root_end = sec_text.find(">", sec_text.find("<hs:sec")) + 1
        if root_end > 0:
            root_tag = sec_text[:root_end]
            xmlns_count = len(re.findall(r"xmlns:", root_tag))
            if xmlns_count < 10:
                errors.append(
                    f"Only {xmlns_count} xmlns declarations on root tag "
                    f"(expected >=10, original HWPX typically has 15)"
                )

            # Body xmlns (should be 0)
            body_xmlns = len(re.findall(r"xmlns:", sec_text[root_end:]))
            if body_xmlns > 0:
                errors.append(
                    f"Found {body_xmlns} xmlns declarations in body "
                    f"(should be 0 — all must be on root tag)"
                )

        # Newline count
        newline_count = sec_text.count("\n")
        if newline_count != 1:
            errors.append(
                f"section0.xml has {newline_count} newlines (expected exactly 1)"
            )

    # 4. Non-section files byte-identical
    for name in orig_order:
        if name not in orig_map or name not in result_map:
            continue
        if "section" in name and name.endswith(".xml"):
            continue  # Section files may be modified
        if orig_map[name].data != result_map[name].data:
            errors.append(f"Non-section file modified: {name}")

    return errors


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------


class HwpxSurgeon:
    """High-level interface for safe HWPX editing.

    Usage:
        surgeon = HwpxSurgeon('document.hwpx')
        children = surgeon.extract_children()
        # ... modify / reorder / insert children ...
        surgeon.replace_children(children)
        surgeon.save('output.hwpx')
    """

    def __init__(self, hwpx_path: str | Path) -> None:
        self._path = Path(hwpx_path)
        self._entries, self._order = read_zip(hwpx_path)
        self._entry_map = {e.filename: e for e in self._entries}
        self._section_name = "Contents/section0.xml"
        self._modified: dict[str, bytes] = {}

    @property
    def section_bytes(self) -> bytes:
        """Raw bytes of section0.xml (modified if replace_* was called)."""
        if self._section_name in self._modified:
            return self._modified[self._section_name]
        return self._entry_map[self._section_name].data

    def extract_children(self, tag: str = "hp:p") -> list[str]:
        """Extract top-level child elements from section0.xml."""
        parts = parse_section(self.section_bytes)
        return extract_children(parts.body, tag)

    def replace_children(self, children: list[str]) -> None:
        """Replace all children in section0.xml, preserving header/xmlns."""
        parts = parse_section(self.section_bytes)
        self._modified[self._section_name] = assemble_section(parts, children)

    def replace_text(self, replacements: dict[str, str]) -> None:
        """Replace text content in section0.xml without touching structure."""
        self._modified[self._section_name] = replace_text_in_section(
            self.section_bytes,
            replacements,
        )

    def save(self, output_path: str | Path | None = None) -> Path:
        """Write the modified HWPX to disk."""
        out = Path(output_path) if output_path else self._path
        write_zip(out, self._entries, self._order, self._modified)
        return out

    def validate(self, output_path: str | Path | None = None) -> list[str]:
        """Validate surgery result against the original."""
        out = Path(output_path) if output_path else self._path
        return validate_surgery(self._path, out)

    def transplant_from(
        self,
        source_path: str | Path,
        chapters: list[int],
        style_map: dict[str, dict[str, str]] | None = None,
        dry_run: bool = False,
    ) -> dict[str, object]:
        """Transplant chapters from source HWPX into this document.

        Modifies self._modified in place (like replace_children).
        Use save() afterwards to write output.

        Returns the result dict from transplant_sections().
        """
        _my_dir = Path(__file__).parent
        if str(_my_dir) not in sys.path:
            sys.path.insert(0, str(_my_dir))

        from section_transplant import transplant_sections

        # Write current state to a temp file, then transplant
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".hwpx", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Save current state as temp target
            write_zip(tmp_path, self._entries, self._order, self._modified)

            if dry_run:
                return transplant_sections(
                    source_hwpx=source_path,
                    target_hwpx=tmp_path,
                    chapter_nums=chapters,
                    style_map=style_map,
                    dry_run=True,
                )

            with tempfile.NamedTemporaryFile(suffix=".hwpx", delete=False) as out_tmp:
                out_tmp_path = Path(out_tmp.name)

            try:
                result = transplant_sections(
                    source_hwpx=source_path,
                    target_hwpx=tmp_path,
                    chapter_nums=chapters,
                    output_path=out_tmp_path,
                    style_map=style_map,
                    dry_run=False,
                )
                # Load the result back into self._modified
                new_entries, _ = read_zip(out_tmp_path)
                new_map = {e.filename: e for e in new_entries}
                section_name = "Contents/section0.xml"
                if section_name in new_map:
                    self._modified[section_name] = new_map[section_name].data
                return result
            finally:
                out_tmp_path.unlink(missing_ok=True)
        finally:
            tmp_path.unlink(missing_ok=True)
    # --- Element factories (convenience wrappers) ---

    @staticmethod
    def make_paragraph(
        pid: str,
        text: str,
        paraPrIDRef: str = "0",
        charPrIDRef: str = "0",
    ) -> str:
        return make_paragraph(pid, text, paraPrIDRef, charPrIDRef)

    @staticmethod
    def make_empty_paragraph(pid: str, paraPrIDRef: str = "0") -> str:
        return make_empty_paragraph(pid, paraPrIDRef)

    @staticmethod
    def make_multi_run_paragraph(
        pid: str,
        runs: list[tuple[str, str]],
        paraPrIDRef: str = "0",
    ) -> str:
        return make_multi_run_paragraph(pid, runs, paraPrIDRef)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_extract(args: argparse.Namespace) -> None:
    section_name = args.section or "Contents/section0.xml"
    entries, _ = read_zip(args.input)
    entry_map = {e.filename: e for e in entries}

    if section_name not in entry_map:
        print(f"Error: {section_name} not found in {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.output or f"/tmp/{Path(args.input).stem}_section0.xml"
    Path(output).write_bytes(entry_map[section_name].data)
    print(f"Extracted: {section_name} -> {output}")


def _cmd_replace(args: argparse.Namespace) -> None:
    section_file = Path(args.section_file)
    if not section_file.is_file():
        print(f"Error: Section file not found: {args.section_file}", file=sys.stderr)
        sys.exit(1)

    entries, order = read_zip(args.input)
    new_section = section_file.read_bytes()
    output = args.output or args.input

    write_zip(output, entries, order, modified={"Contents/section0.xml": new_section})
    print(f"Replaced: Contents/section0.xml in {output}")


def _cmd_validate(args: argparse.Namespace) -> None:
    errors = validate_surgery(args.original, args.result)
    if errors:
        print(f"FAIL: surgery validation ({len(errors)} issues)")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: surgery validation")
        print("  standalone, xmlns, newlines, byte-identical, compression — all OK")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safe ZIP-level surgery for HWPX files",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_ext = sub.add_parser("extract", help="Extract section XML from HWPX")
    p_ext.add_argument("input", help="Input HWPX file")
    p_ext.add_argument("--section", help="Entry name (default: Contents/section0.xml)")
    p_ext.add_argument("--output", "-o", help="Output XML path")

    p_rep = sub.add_parser("replace", help="Replace section XML in HWPX")
    p_rep.add_argument("input", help="Input HWPX file")
    p_rep.add_argument("--section-file", "-s", required=True, help="New section0.xml")
    p_rep.add_argument("--output", "-o", help="Output HWPX (default: overwrite input)")

    p_val = sub.add_parser("validate", help="Validate surgery result")
    p_val.add_argument("original", help="Original HWPX file")
    p_val.add_argument("result", help="Surgery result HWPX file")

    args = parser.parse_args()

    if args.command == "extract":
        _cmd_extract(args)
    elif args.command == "replace":
        _cmd_replace(args)
    elif args.command == "validate":
        _cmd_validate(args)


if __name__ == "__main__":
    main()
