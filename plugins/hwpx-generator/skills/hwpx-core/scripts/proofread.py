#!/usr/bin/env python3
"""HWPX quality proofreader (stdlib-only, regex/string scanning).

Checks:
- double_bullets
- font_consistency
- empty_paragraphs
- orphaned_placeholders
- table_borders
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile


DEFAULT_BULLET_AUTO_IDS = [41, 43, 45, 90, 91, 92, 93, 113, 114, 115, 117, 118, 119]
BULLET_PREFIX_RE = re.compile(r"^[\s\u00A0]*[○●□■◆◇•▶►→※◦–]")
DOUBLE_BULLET_RE = re.compile(
    r"^[\s\u00A0]*[○●□■◆◇•▶►→※◦–][\s\u00A0]*[○●□■◆◇•▶►→※◦–]"
)
SECTION_ENTRY = "Contents/section0.xml"


def _read_section_xml(hwpx_path: Path) -> str:
    if not hwpx_path.is_file():
        raise FileNotFoundError(f"File not found: {hwpx_path}")

    try:
        with ZipFile(hwpx_path, "r") as zf:
            if SECTION_ENTRY not in zf.namelist():
                raise ValueError(f"Missing {SECTION_ENTRY} in {hwpx_path}")
            return zf.read(SECTION_ENTRY).decode("utf-8", errors="replace")
    except BadZipFile as exc:
        raise ValueError(f"Invalid HWPX (ZIP) file: {hwpx_path}") from exc


def _load_bullet_ids(cli_ids: list[int] | None) -> list[int]:
    if cli_ids:
        return sorted(set(cli_ids))

    project_root = Path(__file__).resolve().parents[5]
    golden_path = project_root / "dev" / "golden" / "bullet_styles.json"
    if golden_path.is_file():
        try:
            data = json.loads(golden_path.read_text(encoding="utf-8"))
            ids = data.get("bullet_auto_paraPrIDRefs")
            if isinstance(ids, list):
                parsed = []
                for value in ids:
                    try:
                        parsed.append(int(value))
                    except (TypeError, ValueError):
                        continue
                if parsed:
                    return sorted(set(parsed))
        except (OSError, json.JSONDecodeError):
            pass

    return DEFAULT_BULLET_AUTO_IDS[:]


def _iter_paragraph_blocks(section_xml: str) -> list[str]:
    return re.findall(r"<hp:p\b[^>]*>.*?</hp:p>", section_xml, flags=re.DOTALL)


def _paragraph_text(paragraph_xml: str) -> str:
    parts = re.findall(r"<hp:t\b[^>]*>(.*?)</hp:t>", paragraph_xml, flags=re.DOTALL)
    if not parts:
        return ""
    text = "".join(parts)
    text = re.sub(r"<[^>]+>", "", text)
    return text


def check_double_bullets(section_xml: str, bullet_ids: list[int]) -> dict[str, object]:
    bullet_set = {str(v) for v in bullet_ids}
    violations: list[dict[str, object]] = []

    for idx, p_block in enumerate(_iter_paragraph_blocks(section_xml), start=1):
        open_tag_match = re.search(r"<hp:p\b[^>]*>", p_block)
        if not open_tag_match:
            continue
        open_tag = open_tag_match.group(0)
        para_id_match = re.search(r'paraPrIDRef="(\d+)"', open_tag)
        if not para_id_match:
            continue
        para_style = para_id_match.group(1)

        text = _paragraph_text(p_block)
        if not text.strip():
            continue

        # Check 1: For bullet_auto styles, any bullet prefix in text is a violation
        # (HWPX auto-generates the marker, so text content should be clean).
        if para_style in bullet_set and BULLET_PREFIX_RE.search(text):
            violations.append(
                {
                    "paragraph_index": idx,
                    "paraPrIDRef": int(para_style),
                    "text_preview": text.strip()[:80],
                    "reason": "bullet_auto_prefix",
                }
            )
            continue

        # Check 2: For ALL styles, double bullet markers are always a violation
        # (e.g., \"◦ ◦text\" from marker prepended + unstripped content).
        if DOUBLE_BULLET_RE.search(text):
            violations.append(
                {
                    "paragraph_index": idx,
                    "paraPrIDRef": int(para_style),
                    "text_preview": text.strip()[:80],
                    "reason": "double_bullet",
                }
            )

    return {
        "pass": len(violations) == 0,
        "count": len(violations),
        "details": violations,
    }


def check_font_consistency(section_xml: str) -> dict[str, object]:
    groups: dict[str, dict[str, int]] = {}

    for p_block in _iter_paragraph_blocks(section_xml):
        open_tag_match = re.search(r"<hp:p\b[^>]*>", p_block)
        if not open_tag_match:
            continue
        open_tag = open_tag_match.group(0)
        para_id_match = re.search(r'paraPrIDRef="(\d+)"', open_tag)
        if not para_id_match:
            continue
        para_style = para_id_match.group(1)

        char_ids = re.findall(r'charPrIDRef="(\d+)"', p_block)
        if not char_ids:
            continue

        style_counts = groups.setdefault(para_style, {})
        for char_id in char_ids:
            style_counts[char_id] = style_counts.get(char_id, 0) + 1

    group_details: list[dict[str, object]] = []
    total_share = 0.0
    total_groups = 0
    failed_groups = 0

    for para_style, counts in sorted(groups.items(), key=lambda x: int(x[0])):
        total = sum(counts.values())
        if total == 0:
            continue

        dominant_char, dominant_count = max(counts.items(), key=lambda item: item[1])
        share = dominant_count / total
        group_pass = share > 0.60

        total_share += share
        total_groups += 1
        if not group_pass:
            failed_groups += 1

        group_details.append(
            {
                "paraPrIDRef": int(para_style),
                "dominant_charPrIDRef": int(dominant_char),
                "dominant_share": round(share, 4),
                "unique_charPr_count": len(counts),
                "pass": group_pass,
            }
        )

    score = 1.0 if total_groups == 0 else round(total_share / total_groups, 4)
    return {
        "pass": failed_groups == 0,
        "score": score,
        "groups": group_details,
        "failed_groups": failed_groups,
        "total_groups": total_groups,
    }


def check_empty_paragraphs(section_xml: str) -> dict[str, object]:
    structural_markers = (
        "<hp:secPr",
        "<hp:ctrl",
        "<hp:tbl",
        "<hp:pic",
        "<hp:shape",
        "<hp:line",
        "<hp:rect",
        "<hp:container",
        "<hp:ole",
    )

    count = 0
    for p_block in _iter_paragraph_blocks(section_xml):
        if any(marker in p_block for marker in structural_markers):
            continue

        has_text_element = bool(re.search(r"<hp:t\b", p_block))
        if not has_text_element:
            count += 1
            continue

        text = _paragraph_text(p_block)
        if text.strip() == "":
            count += 1

    return {"pass": count == 0, "count": count}


def check_orphaned_placeholders(section_xml: str) -> dict[str, object]:
    text_chunks = re.findall(r"<hp:t\b[^>]*>(.*?)</hp:t>", section_xml, flags=re.DOTALL)
    text_only = "\n".join(re.sub(r"<[^>]+>", "", t) for t in text_chunks)

    patterns = [
        re.compile(r"\bIMAGE\b", re.IGNORECASE),
        re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
        re.compile(r"\[\s*작성\s*\]"),
        re.compile(r"\[\s*내용\s*\]"),
        re.compile(r"<\s*(?:IMAGE|PLACEHOLDER|작성|내용)\s*>", re.IGNORECASE),
    ]

    found: list[str] = []
    for pattern in patterns:
        for match in pattern.finditer(text_only):
            found.append(match.group(0))

    if "{{" in section_xml or "}}" in section_xml:
        found.append("{{ }}")

    unique_found = sorted(set(found))
    return {
        "pass": len(unique_found) == 0,
        "count": len(unique_found),
        "found": unique_found,
    }


def check_table_borders(section_xml: str) -> dict[str, object]:
    cell_tags = re.findall(r"<hp:tc\b[^>]*>", section_xml)
    missing = 0

    for tag in cell_tags:
        border_match = re.search(r'borderFillIDRef="(-?\d+)"', tag)
        if not border_match:
            missing += 1
            continue
        try:
            border_value = int(border_match.group(1))
        except ValueError:
            missing += 1
            continue
        if border_value <= 0:
            missing += 1

    return {
        "pass": missing == 0,
        "missing_count": missing,
        "table_cell_count": len(cell_tags),
    }


def run_proofread(
    input_hwpx: Path,
    bullet_ids: list[int],
    golden_hwpx: Path | None = None,
) -> tuple[dict[str, object], int]:
    section_xml = _read_section_xml(input_hwpx)
    result: dict[str, object] = {
        "input": str(input_hwpx),
        "double_bullets": check_double_bullets(section_xml, bullet_ids),
        "font_consistency": check_font_consistency(section_xml),
        "empty_paragraphs": check_empty_paragraphs(section_xml),
        "orphaned_placeholders": check_orphaned_placeholders(section_xml),
        "table_borders": check_table_borders(section_xml),
    }

    if golden_hwpx is not None:
        result["golden"] = str(golden_hwpx)

    all_pass = True
    for key in (
        "double_bullets",
        "font_consistency",
        "empty_paragraphs",
        "orphaned_placeholders",
        "table_borders",
    ):
        check_result = result.get(key)
        if not isinstance(check_result, dict) or not bool(
            check_result.get("pass", False)
        ):
            all_pass = False
            break
    return result, (0 if all_pass else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proofread HWPX quality with regex-based XML checks"
    )
    parser.add_argument("input", help="Input .hwpx path")
    parser.add_argument("--output", help="Optional output JSON path")
    parser.add_argument("--golden", help="Optional golden reference .hwpx path")
    parser.add_argument(
        "--bullet-auto-ids",
        nargs="+",
        type=int,
        help="Override bullet-auto paraPrIDRefs (e.g. --bullet-auto-ids 41 45 92)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    golden_path = Path(args.golden) if args.golden else None
    bullet_ids = _load_bullet_ids(args.bullet_auto_ids)

    try:
        result, exit_code = run_proofread(input_path, bullet_ids, golden_path)
    except Exception as exc:
        error_result = {
            "input": str(input_path),
            "error": str(exc),
            "double_bullets": {"pass": False, "count": 0, "details": []},
            "font_consistency": {"pass": False, "score": 0.0},
            "empty_paragraphs": {"pass": False, "count": 0},
            "orphaned_placeholders": {"pass": False, "count": 0, "found": []},
            "table_borders": {"pass": False, "missing_count": 0},
        }
        text = json.dumps(error_result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(text)
        sys.exit(1)

    json_text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(json_text + "\n", encoding="utf-8")
    print(json_text)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
