#!/usr/bin/env python3
"""Pack a directory back into an HWPX (ZIP) file.

The mimetype file is stored as the first entry with ZIP_STORED (no compression),
per OPC packaging conventions.

Usage:
    python pack.py input_dir/ output.hwpx
"""

import argparse
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


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
