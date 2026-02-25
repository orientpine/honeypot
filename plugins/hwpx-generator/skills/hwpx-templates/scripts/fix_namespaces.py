#!/usr/bin/env python3
"""
HWPX namespace post-processing utility.

Replace auto-generated XML namespace prefixes in HWPX files with
Hangul Office standard prefixes.

Without this step, some viewers (especially on macOS) may display
the document as blank pages after ZIP-level replacements.

Usage:
  CLI:    python fix_namespaces.py <file.hwpx>
"""

import os
import re
import sys
import zipfile


def fix_hwpx_namespaces(hwpx_path):
    """Normalize HWPX XML namespace prefixes using regex replacements."""
    ns_map = {
        "http://www.hancom.co.kr/hwpml/2011/head": "hh",
        "http://www.hancom.co.kr/hwpml/2011/core": "hc",
        "http://www.hancom.co.kr/hwpml/2011/paragraph": "hp",
        "http://www.hancom.co.kr/hwpml/2011/section": "hs",
    }

    tmp_path = hwpx_path + ".tmp"

    with zipfile.ZipFile(hwpx_path, "r") as zin:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename.startswith("Contents/") and item.filename.endswith(
                    ".xml"
                ):
                    text = data.decode("utf-8")

                    ns_aliases = {}
                    for match in re.finditer(r'xmlns:(ns\d+)="([^"]+)"', text):
                        alias, uri = match.group(1), match.group(2)
                        if uri in ns_map:
                            ns_aliases[alias] = ns_map[uri]

                    for old_prefix, new_prefix in ns_aliases.items():
                        text = text.replace(
                            f"xmlns:{old_prefix}=", f"xmlns:{new_prefix}="
                        )
                        text = text.replace(f"<{old_prefix}:", f"<{new_prefix}:")
                        text = text.replace(f"</{old_prefix}:", f"</{new_prefix}:")

                    data = text.encode("utf-8")

                zout.writestr(item, data)

    os.replace(tmp_path, hwpx_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_namespaces.py <file.hwpx>")
        print("  Fixes namespace prefixes for Hangul Viewer compatibility.")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    fix_hwpx_namespaces(path)
    print(f"Fixed namespaces: {path}")
