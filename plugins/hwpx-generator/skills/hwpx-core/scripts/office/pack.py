#!/usr/bin/env python3
"""Pack a directory back into an HWPX (ZIP) file.

The mimetype file is stored as the first entry with ZIP_STORED (no compression),
per OPC packaging conventions.  Section XMLs are post-processed with
cell_writer to generate correct <hp:linesegarray> elements.  Falls back to
regex-based stripping if cell_writer is unavailable.

Usage:
    python pack.py input_dir/ output.hwpx
"""

import argparse
import os
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

_LINESEG_RE = re.compile(
    r"\s*<[^>]*:linesegarray>.*?</[^>]*:linesegarray>",
    re.DOTALL,
)

def pack(input_dir: str, hwpx_path: str) -> None:
    """Create HWPX archive from a directory."""

    root = Path(input_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Directory not found: {input_dir}")

    mimetype_file = root / "mimetype"
    if not mimetype_file.is_file():
        raise FileNotFoundError(f"Missing required 'mimetype' file in {input_dir}")

    all_files = sorted(
        p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
    )

    with ZipFile(hwpx_path, "w", ZIP_DEFLATED) as zf:
        # mimetype MUST be the first entry, stored without compression
        zf.write(mimetype_file, "mimetype", compress_type=ZIP_STORED)

        for rel_path in all_files:
            if rel_path == "mimetype":
                continue  # Already written
            full_path = root / rel_path

            # Generate linesegarray for section XMLs (with regex-strip fallback).
            if (
                rel_path.startswith("Contents/")
                and rel_path.endswith(".xml")
                and "section" in rel_path
            ):
                header_path = root / "Contents" / "header.xml"
                generated = False
                if header_path.is_file():
                    try:
                        # cell_writer lives one level up from office/
                        import importlib.util
                        _cw_path = Path(__file__).resolve().parent.parent / "cell_writer.py"
                        if _cw_path.is_file():
                            spec = importlib.util.spec_from_file_location("cell_writer", _cw_path)
                            cw = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
                            spec.loader.exec_module(cw)  # type: ignore[union-attr]
                            from lxml import etree as _et
                            sec_tree = _et.parse(str(full_path))
                            hdr_tree = _et.parse(str(header_path))
                            cw.process_section(sec_tree.getroot(), hdr_tree.getroot())
                            sec_data = _et.tostring(
                                sec_tree, pretty_print=True,
                                xml_declaration=True, encoding="UTF-8",
                            )
                            zf.writestr(rel_path, sec_data)
                            generated = True
                    except Exception:
                        pass  # Fall through to regex fallback.

                if not generated:
                    # Regex fallback: strip stale linesegarray.
                    data = full_path.read_bytes()
                    text = data.decode("utf-8")
                    cleaned = _LINESEG_RE.sub("", text)
                    if cleaned != text:
                        zf.writestr(rel_path, cleaned.encode("utf-8"))
                        continue

            zf.write(full_path, rel_path, compress_type=ZIP_DEFLATED)

    count = len(all_files)
    print(f"Packed: {input_dir} -> {hwpx_path}")
    print(f"  Files: {count} entries (mimetype first, ZIP_STORED)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pack a directory into an HWPX (ZIP) file"
    )
    parser.add_argument("input", help="Input directory path")
    parser.add_argument("output", help="Output .hwpx file path")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"Error: Directory not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    pack(args.input, args.output)


if __name__ == "__main__":
    main()
