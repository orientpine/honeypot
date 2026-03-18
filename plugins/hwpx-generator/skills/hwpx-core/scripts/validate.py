#!/usr/bin/env python3
"""Validate the structural integrity of an HWPX file.

Checks (standard):
  - Valid ZIP archive
  - Required files present (mimetype, content.hpf, header.xml, section0.xml)
  - mimetype content is correct
  - mimetype is the first ZIP entry and stored without compression
  - All XML files are well-formed

Checks (--strict, for ZIP-level surgery output):
  - standalone='no' present in section0.xml XML declaration
  - Sufficient xmlns declarations on root <hs:sec> tag (>=10)
  - No xmlns declarations in section body (all on root tag)
  - Only 1 newline in section0.xml (after XML declaration)
  - Table auto-adjust attributes (noAdjust="0", pageBreak="CELL")

Usage:
    python validate.py document.hwpx
    python validate.py document.hwpx --strict
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_STORED, BadZipFile, ZipFile

from lxml import etree

REQUIRED_FILES = [
    "mimetype",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
]

EXPECTED_MIMETYPE = "application/hwp+zip"


def validate(hwpx_path: str, *, strict: bool = False) -> list[str]:
    """Validate HWPX file and return a list of error messages (empty = valid).

    Args:
        hwpx_path: Path to the HWPX file.
        strict: Enable strict checks for ZIP-level surgery compliance
                (standalone, xmlns, newlines, table attributes).
    """

    errors: list[str] = []
    path = Path(hwpx_path)

    if not path.is_file():
        return [f"File not found: {hwpx_path}"]

    # Check valid ZIP
    try:
        zf = ZipFile(hwpx_path, "r")
    except BadZipFile:
        return [f"Not a valid ZIP archive: {hwpx_path}"]

    with zf:
        names = zf.namelist()

        # Check required files
        for required in REQUIRED_FILES:
            if required not in names:
                errors.append(f"Missing required file: {required}")

        # Check mimetype content
        if "mimetype" in names:
            mimetype_content = zf.read("mimetype").decode("utf-8").strip()
            if mimetype_content != EXPECTED_MIMETYPE:
                errors.append(
                    f"Invalid mimetype: expected '{EXPECTED_MIMETYPE}', "
                    f"got '{mimetype_content}'"
                )

            # Check mimetype is first entry
            if names[0] != "mimetype":
                errors.append(
                    f"mimetype is not the first ZIP entry (found at index "
                    f"{names.index('mimetype')})"
                )

            # Check mimetype is stored without compression
            info = zf.getinfo("mimetype")
            if info.compress_type != ZIP_STORED:
                errors.append(
                    f"mimetype should use ZIP_STORED (0), "
                    f"got compress_type={info.compress_type}"
                )

        # Check XML well-formedness
        for name in names:
            if name.endswith(".xml") or name.endswith(".hpf"):
                try:
                    data = zf.read(name)
                    etree.fromstring(data)
                except etree.XMLSyntaxError as e:
                    errors.append(f"Malformed XML in {name}: {e}")

        # Strict mode: ZIP-level surgery compliance checks
        if strict:
            errors.extend(_strict_checks(zf, names))

    return errors


def _strict_checks(zf: ZipFile, names: list[str]) -> list[str]:
    """Additional checks for ZIP-level surgery compliance.

    See references/zip-surgery-guide.md for the full specification.
    """
    errors: list[str] = []
    section_name = "Contents/section0.xml"

    if section_name not in names:
        return errors

    sec_bytes = zf.read(section_name)
    sec_text = sec_bytes.decode("utf-8")

    # 1. standalone='no' in XML declaration
    decl = sec_text[:200]
    if "standalone='no'" not in decl and 'standalone="no"' not in decl:
        errors.append(
            "[strict] standalone='no' missing from section0.xml XML declaration"
        )

    # 2. xmlns declarations on root <hs:sec> tag
    hs_sec_pos = sec_text.find("<hs:sec")
    if hs_sec_pos != -1:
        root_end = sec_text.find(">", hs_sec_pos) + 1
        if root_end > 0:
            root_tag = sec_text[:root_end]
            xmlns_count = len(re.findall(r"xmlns:", root_tag))
            if xmlns_count < 10:
                errors.append(
                    f"[strict] Only {xmlns_count} xmlns declarations on root tag "
                    f"(expected >=10, typical HWPX has 15)"
                )

            # 3. No xmlns declarations in body
            body_xmlns = len(re.findall(r"xmlns:", sec_text[root_end:]))
            if body_xmlns > 0:
                errors.append(
                    f"[strict] Found {body_xmlns} xmlns declarations in body "
                    f"(should be 0 — all must be on root tag)"
                )
    else:
        errors.append("[strict] No <hs:sec> root tag found in section0.xml")

    # 4. Newline count (should be exactly 1: after XML declaration)
    newline_count = sec_text.count("\n")
    if newline_count != 1:
        errors.append(
            f"[strict] section0.xml has {newline_count} newlines "
            f"(expected exactly 1, after XML declaration)"
        )

    # 5. Table attributes: noAdjust and pageBreak
    tbl_pattern = re.compile(r"<hp:tbl\b[^>]*>")
    for match in tbl_pattern.finditer(sec_text):
        tbl_tag = match.group(0)

        no_adjust = re.search(r'noAdjust="(\d)"', tbl_tag)
        if no_adjust and no_adjust.group(1) != "0":
            errors.append(
                f'[strict] Table has noAdjust="{no_adjust.group(1)}" '
                f'(should be "0" for auto row height)'
            )

        page_break = re.search(r'pageBreak="([^"]*)"', tbl_tag)
        if page_break and page_break.group(1) == "NONE":
            errors.append(
                '[strict] Table has pageBreak="NONE" '
                '(should be "CELL" for cross-page tables)'
            )

    return errors

def _run_proofread(hwpx_path: str) -> dict:
    """Run proofread.py as a subprocess and return structured result."""
    proofread_script = Path(__file__).parent / "proofread.py"
    if not proofread_script.is_file():
        return {
            "pass": False,
            "summary": "proofread.py not found",
            "details": {"error": f"Script not found: {proofread_script}"},
        }

    try:
        proc = subprocess.run(
            [sys.executable, str(proofread_script), hwpx_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # proofread.py outputs JSON to stdout
        if proc.stdout.strip():
            data = json.loads(proc.stdout)
            # Determine overall pass from individual checks
            checks = ["double_bullets", "font_consistency", "empty_paragraphs",
                      "orphaned_placeholders", "table_borders"]
            all_pass = all(
                isinstance(data.get(c), dict) and data[c].get("pass", False)
                for c in checks
            )
            failed = [c for c in checks
                      if isinstance(data.get(c), dict) and not data[c].get("pass", True)]
            summary = "PASS" if all_pass else f"FAIL ({', '.join(failed)})"
            return {"pass": all_pass, "summary": summary, "details": data}
        else:
            return {
                "pass": False,
                "summary": f"proofread.py returned no output (exit={proc.returncode})",
                "details": {"stderr": proc.stderr.strip()},
            }
    except subprocess.TimeoutExpired:
        return {"pass": False, "summary": "proofread.py timed out", "details": {}}
    except json.JSONDecodeError as exc:
        return {
            "pass": False,
            "summary": f"proofread.py returned invalid JSON: {exc}",
            "details": {},
        }
    except Exception as exc:
        return {"pass": False, "summary": f"proofread.py error: {exc}", "details": {}}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the structural integrity of an HWPX file"
    )
    parser.add_argument("input", help="Path to .hwpx file")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict checks for ZIP-level surgery compliance "
        "(standalone, xmlns, newlines, table attributes)",
    )
    parser.add_argument(
        "--proofread",
        action="store_true",
        help="Run proofread.py after validation and include results",
    )
    args = parser.parse_args()

    errors = validate(args.input, strict=args.strict)

    proofread_result = None
    if args.proofread:
        proofread_result = _run_proofread(args.input)

    if errors:
        print(f"INVALID: {args.input}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        if proofread_result is not None:
            print(f"\nProofread: {proofread_result['summary']}", file=sys.stderr)
        sys.exit(1)
    else:
        mode = "strict" if args.strict else "standard"
        suffix = "+proofread" if args.proofread else ""
        print(f"VALID: {args.input} ({mode}{suffix} mode)")
        print("  All checks passed.")
        if proofread_result is not None:
            print(f"  Proofread: {proofread_result['summary']}")
            if not proofread_result["pass"]:
                print("  WARNING: proofread found issues (see details below)")
                print(json.dumps(proofread_result["details"], ensure_ascii=False, indent=4))
                sys.exit(1)

if __name__ == "__main__":
    main()
