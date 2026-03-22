#!/usr/bin/env python3
"""Validate the structural integrity of an HWPX file.

Checks (standard):
  - Valid ZIP archive
  - Required files present (mimetype, content.hpf, header.xml, section0.xml)
  - mimetype content is correct
  - mimetype is the first ZIP entry and stored without compression
  - All XML files are well-formed
  - Image embedding consistency (BinData/header.xml/content.hpf/section0.xml)

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
import os
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_STORED, BadZipFile, ZipFile

from lxml import etree  # pyright: ignore[reportMissingImports]

REQUIRED_FILES = [
    "mimetype",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
]

EXPECTED_MIMETYPE = "application/hwp+zip"


def validate(hwpx_path: str, *, strict: bool = False) -> tuple[list[str], list[str]]:
    """Validate HWPX file and return (errors, warnings) lists (empty = valid).

    Args:
        hwpx_path: Path to the HWPX file.
        strict: Enable strict checks for ZIP-level surgery compliance
                (standalone, xmlns, newlines, table attributes).
    """

    errors: list[str] = []
    warnings: list[str] = []
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

        # Image embedding consistency checks (always run when images exist)
        errors_img, warnings_img = _image_checks(zf, names)
        errors.extend(errors_img)
        warnings.extend(warnings_img)

        # Strict mode: ZIP-level surgery compliance checks
        if strict:
            errors.extend(_strict_checks(zf, names))

    return errors, warnings


def _image_checks(zf: ZipFile, names: list[str]) -> tuple[list[str], list[str]]:
    """Validate image embedding consistency across section0.xml, header.xml, and content.hpf.
    
    Returns (errors, warnings) tuples.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Run only when BinData files exist
    bin_files = [n for n in names if n.startswith("BinData/") and not n.endswith("/")]
    if not bin_files:
        return errors, warnings

    section_name = "Contents/section0.xml"
    header_name = "Contents/header.xml"
    hpf_name = "Contents/content.hpf"

    sec_text = zf.read(section_name).decode("utf-8") if section_name in names else ""
    header_text = zf.read(header_name).decode("utf-8") if header_name in names else ""
    hpf_text = zf.read(hpf_name).decode("utf-8") if hpf_name in names else ""

    # 1 & 2: hp:pic must include renderingInfo, instid, and be inside hp:run
    if sec_text:
        pic_pattern = re.compile(r"<hp:pic\b([^>]*)>(.*?)</hp:pic>", re.DOTALL)
        for match in pic_pattern.finditer(sec_text):
            pic_attrs = match.group(1)
            pic_content = match.group(2)
            pic_start = match.start()

            if "instid=" not in pic_attrs:
                errors.append(
                    "[image] hp:pic element missing required 'instid' attribute"
                )

            if "<hp:renderingInfo>" not in pic_content:
                errors.append(
                    "[image] hp:pic element missing required <hp:renderingInfo>"
                )

            # hp:pic must be inside <hp:run>, not a section-level sibling
            preceding = sec_text[max(0, pic_start - 200):pic_start]
            if "<hp:run" not in preceding or "</hp:run>" in preceding:
                # Check if the closest run tag before hp:pic is an opening tag
                last_run_open = preceding.rfind("<hp:run")
                last_run_close = preceding.rfind("</hp:run>")
                if last_run_open < 0 or last_run_close > last_run_open:
                    errors.append(
                        "[image] hp:pic is not inside <hp:run> — "
                        "한/글 ignores section-level hp:pic elements"
                    )

    # 3: header.xml binDataList is deprecated — warn if present, OK if absent
    if header_text:
        if "<hh:binDataList" in header_text:
            warnings.append(
                "[image][WARN] header.xml contains binDataList "
                "(deprecated; manual section 8 says remove it)"
            )
    # 4: binaryItemIDRef in section0.xml must exist as opf:item id in content.hpf
    if sec_text and hpf_text:
        hpf_ids = set(re.findall(r'<opf:item[^>]+\bid="([^"]+)"', hpf_text))
        for m in re.finditer(r'binaryItemIDRef="([^"]*)"', sec_text):
            ref_id = m.group(1)
            if ref_id not in hpf_ids:
                errors.append(
                    f'[image] binaryItemIDRef="{ref_id}" not found in '
                    f"content.hpf opf:item entries"
                )

    # 5: BinData magic bytes must match media-type in content.hpf
    if hpf_text:
        declared_media_by_href: dict[str, str] = {}
        for item_match in re.finditer(r"<opf:item\b[^>]*/?>" , hpf_text):
            tag = item_match.group(0)
            href_match = re.search(r"\bhref=\"([^\"]+)\"" , tag)
            media_match = re.search(r"\bmedia-type=\"([^\"]+)\"" , tag)
            if href_match and media_match:
                declared_media_by_href[href_match.group(1)] = media_match.group(1)

        for bin_file in bin_files:
            bin_data = zf.read(bin_file)
            basename = os.path.basename(bin_file)

            is_png = bin_data[:8] == b"\x89PNG\r\n\x1a\n"
            is_jpeg = bin_data[:3] == b"\xff\xd8\xff"

            declared_type = declared_media_by_href.get(bin_file)
            if declared_type is None:
                for href, media_type in declared_media_by_href.items():
                    if href.endswith(basename):
                        declared_type = media_type
                        break

            if declared_type == "image/png" and not is_png:
                actual = "JPEG" if is_jpeg else "unknown"
                errors.append(
                    f"[image] {bin_file}: declared as image/png but actual format "
                    f"is {actual} (magic bytes mismatch)"
                )
            elif declared_type == "image/jpeg" and not is_jpeg:
                actual = "PNG" if is_png else "unknown"
                errors.append(
                    f"[image] {bin_file}: declared as image/jpeg but actual format "
                    f"is {actual} (magic bytes mismatch)"
                )

    return errors, warnings


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

    # 4. Newline count (HWPX section0.xml must have 0 newlines)
    # 한/글 templates have 0 newlines. lxml's tostring() adds a newline
    # between <?xml ...?> and <hs:sec>, which crashes 한/글.
    newline_count = sec_text.count("\n")
    if newline_count > 0:
        errors.append(
            f"[strict] section0.xml contains {newline_count} newline(s) "
            f"(expected 0 — 한/글 crashes on any newline in section XML)"
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


def _run_proofread(hwpx_path: str) -> dict[str, object]:
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
            checks = [
                "double_bullets",
                "font_consistency",
                "empty_paragraphs",
                "orphaned_placeholders",
                "table_borders",
            ]
            all_pass = all(
                isinstance(data.get(c), dict) and data[c].get("pass", False)
                for c in checks
            )
            failed = [
                c
                for c in checks
                if isinstance(data.get(c), dict) and not data[c].get("pass", True)
            ]
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

def _caption_checks(section_xml: str, parsed_path: str | None, errors: list, warnings: list) -> None:
    """Validate image caption count matches parsed blocks."""
    if not parsed_path:
        return
    with open(parsed_path, encoding="utf-8") as f:
        parsed = json.load(f)
    md_caption_count = sum(
        1 for b in parsed.get("blocks", [])
        if b.get("type") == "image_ref"
        and (b.get("caption_id") or b.get("id"))
        and (b.get("caption", "").strip())
    )
    hwpx_caption_count = len(re.findall(r"그림\s*\d+-\d+", section_xml))
    if md_caption_count != hwpx_caption_count:
        errors.append(
            f"Caption count mismatch: MD has {md_caption_count} captions, "
            f"HWPX has {hwpx_caption_count} caption paragraphs"
        )


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
    parser.add_argument(
        "--parsed",
        help="Path to parsed JSON (from md_parser.py) for caption count validation. "
        "If omitted, caption validation is skipped.",
    )
    args = parser.parse_args()

    errors, warnings = validate(args.input, strict=args.strict)

    proofread_result = None
    if args.proofread:
        proofread_result = _run_proofread(args.input)
    if args.parsed:
        # Read section0.xml for caption check
        try:
            with ZipFile(args.input, "r") as zf:
                if "Contents/section0.xml" in zf.namelist():
                    section_xml = zf.read("Contents/section0.xml").decode("utf-8")
                    _caption_checks(section_xml, args.parsed, errors, [])
        except Exception as exc:
            errors.append(f"Caption check error: {exc}")

    if errors:
        print(f"INVALID: {args.input}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        if warnings:
            print(f"\nWarnings:", file=sys.stderr)
            for warn in warnings:
                print(f"  - {warn}", file=sys.stderr)
        if proofread_result is not None:
            print(f"\nProofread: {proofread_result['summary']}", file=sys.stderr)
        sys.exit(1)
    else:
        mode = "strict" if args.strict else "standard"
        suffix = "+proofread" if args.proofread else ""
        print(f"VALID: {args.input} ({mode}{suffix} mode)")
        print("  All checks passed.")
        if warnings:
            print(f"\nWarnings:", file=sys.stderr)
            for warn in warnings:
                print(f"  - {warn}", file=sys.stderr)
        if proofread_result is not None:
            print(f"  Proofread: {proofread_result['summary']}")
            if not proofread_result["pass"]:
                print("  WARNING: proofread found issues (see details below)")
                print(
                    json.dumps(
                        proofread_result["details"], ensure_ascii=False, indent=4
                    )
                )
                sys.exit(1)


if __name__ == "__main__":
    main()
