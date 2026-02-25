#!/usr/bin/env python3
"""Extract text from an HWPX document.

Wraps python-hwpx's TextExtractor for convenient CLI use.

Usage:
    python text_extract.py document.hwpx
    python text_extract.py document.hwpx --format markdown
    python text_extract.py document.hwpx --include-tables
"""

import argparse
import sys
from pathlib import Path

from hwpx import TextExtractor


def extract_plain(hwpx_path: str, *, include_tables: bool = False) -> str:
    """Extract plain text from HWPX file."""

    object_behavior = "nested" if include_tables else "skip"
    with TextExtractor(hwpx_path) as ext:
        return ext.extract_text(
            include_nested=include_tables,
            object_behavior=object_behavior,
            skip_empty=True,
        )


def extract_markdown(hwpx_path: str) -> str:
    """Extract text as Markdown with section separators."""

    lines: list[str] = []

    with TextExtractor(hwpx_path) as ext:
        for section in ext.iter_sections():
            if lines:
                lines.append("")
                lines.append("---")
                lines.append("")

            for para in ext.iter_paragraphs(section, include_nested=True):
                text = para.text(object_behavior="nested")
                if text.strip():
                    if para.is_nested:
                        # Table cell or nested content - indent
                        lines.append(f"  {text}")
                    else:
                        lines.append(text)

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from an HWPX document")
    parser.add_argument("input", help="Path to .hwpx file")
    parser.add_argument(
        "--format",
        "-f",
        choices=["plain", "markdown"],
        default="plain",
        help="Output format (default: plain)",
    )
    parser.add_argument(
        "--include-tables",
        action="store_true",
        help="Include text from tables and nested objects (plain mode)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.format == "markdown":
        result = extract_markdown(args.input)
    else:
        result = extract_plain(args.input, include_tables=args.include_tables)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Extracted to: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
