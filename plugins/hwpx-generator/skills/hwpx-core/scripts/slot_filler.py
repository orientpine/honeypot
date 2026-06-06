#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent))
from zip_surgery import _xml_escape, HwpxSurgeon, validate_surgery  # pyright: ignore[reportImplicitRelativeImport, reportPrivateUsage]  # noqa: E402


SECTION_XML = "Contents/section0.xml"
OPEN_P = "<hp:p"
CLOSE_P = "</hp:p>"


def _find_next_paragraph_open(section_text: str, start: int) -> int:
    pos = section_text.find(OPEN_P, start)
    while pos != -1:
        marker_end = pos + len(OPEN_P)
        if marker_end < len(section_text) and section_text[marker_end] in (" ", ">", "/"):
            return pos
        pos = section_text.find(OPEN_P, marker_end)
    return -1


def _find_paragraph_span(section_text: str, p_start: int) -> tuple[int, int, int] | None:
    tag_end = section_text.find(">", p_start)
    if tag_end == -1:
        return None
    tag_end += 1

    depth = 0
    scan = tag_end
    while True:
        next_open = _find_next_paragraph_open(section_text, scan)
        next_close = section_text.find(CLOSE_P, scan)

        if next_close == -1:
            return None

        if next_open != -1 and next_open < next_close:
            nested_tag_end = section_text.find(">", next_open)
            if nested_tag_end == -1:
                return None
            if section_text[nested_tag_end - 1] != "/":
                depth += 1
            scan = nested_tag_end + 1
            continue

        if depth == 0:
            return tag_end, next_close, next_close + len(CLOSE_P)

        depth -= 1
        scan = next_close + len(CLOSE_P)


def _escape_text_content(text: str) -> str:
    return (
        _xml_escape(text)
        .replace("\r\n", "&#10;")
        .replace("\r", "&#13;")
        .replace("\n", "&#10;")
    )


def _normalize_section_text(section_text: str) -> str:
    if not section_text.startswith("<?xml"):
        return section_text.replace("\r\n", "").replace("\r", "").replace("\n", "")

    declaration_end = section_text.find("?>")
    if declaration_end == -1:
        return section_text.replace("\r\n", "").replace("\r", "").replace("\n", "")

    declaration = section_text[:declaration_end]
    body = section_text[declaration_end + 2 :].lstrip("\r\n")
    if "standalone=" not in declaration:
        declaration = f"{declaration} standalone='no'"

    body = body.replace("\r\n", "").replace("\r", "").replace("\n", "")
    return f"{declaration}?>\n{body}"


def _make_runs(runs_list: list[tuple[str, str]]) -> str:
    run_parts: list[str] = []
    for charPrIDRef, text in runs_list:
        escaped = _escape_text_content(text)
        if escaped:
            run_parts.append(
                f'<hp:run charPrIDRef="{charPrIDRef}"><hp:t>{escaped}</hp:t></hp:run>'
            )
        else:
            run_parts.append(f'<hp:run charPrIDRef="{charPrIDRef}"><hp:t/></hp:run>')
    return "".join(run_parts)


def fill_slots_by_paragraph_id(
    section_bytes: bytes,
    fills: dict[str, list[tuple[str, str]]],
) -> tuple[bytes, list[str]]:
    """
    Returns (modified_section_bytes, list_of_unresolved_paragraph_ids).
    Only fills slots where paragraph_id is found exactly once in section_bytes.
    """

    section_text = section_bytes.decode("utf-8")
    unresolved: list[str] = []

    for paragraph_id, runs_list in fills.items():
        needle = f'<hp:p id="{paragraph_id}"'
        p_start = section_text.find(needle)
        if p_start == -1 or section_text.find(needle, p_start + len(needle)) != -1:
            unresolved.append(paragraph_id)
            continue

        span = _find_paragraph_span(section_text, p_start)
        if span is None:
            unresolved.append(paragraph_id)
            continue

        opening_end, _closing_start, paragraph_end = span
        opening_tag = section_text[p_start:opening_end]
        replacement = f"{opening_tag}{_make_runs(runs_list)}{CLOSE_P}"
        section_text = section_text[:p_start] + replacement + section_text[paragraph_end:]

    section_text = _normalize_section_text(section_text)
    return section_text.encode("utf-8"), unresolved


def _parse_fills(raw_fills: str) -> dict[str, list[tuple[str, str]]]:
    try:
        payload = cast(object, json.loads(raw_fills))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid --fills JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("--fills must be a JSON object")

    fills: dict[str, list[tuple[str, str]]] = {}
    payload_dict = cast(dict[object, object], payload)
    for paragraph_id, runs_object in payload_dict.items():
        if not isinstance(runs_object, list):
            raise ValueError(f"Fill for {paragraph_id!r} must be a list of runs")

        runs = cast(list[object], runs_object)
        parsed_runs: list[tuple[str, str]] = []
        for index, run_object in enumerate(runs):
            if not isinstance(run_object, list):
                raise ValueError(
                    f"Run {index} for {paragraph_id!r} must be [charPrIDRef, text]"
                )
            run = cast(list[object], run_object)
            if len(run) != 2:
                raise ValueError(
                    f"Run {index} for {paragraph_id!r} must be [charPrIDRef, text]"
                )
            parsed_runs.append((str(run[0]), str(run[1])))
        fills[str(paragraph_id)] = parsed_runs

    return fills


def fill_hwpx(
    input_path: Path,
    fills: dict[str, list[tuple[str, str]]],
    output_path: Path,
) -> list[str]:
    surgeon = HwpxSurgeon(input_path)
    modified_section, unresolved = fill_slots_by_paragraph_id(surgeon.section_bytes, fills)
    original_section = surgeon.section_bytes.decode("utf-8")
    modified_text = modified_section.decode("utf-8")
    surgeon.replace_text({original_section: modified_text})
    _ = surgeon.save(output_path)
    return unresolved


class CliArgs(argparse.Namespace):
    hwpx: str = ""
    fills: str = ""
    output: str = ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill HWPX template slots by paragraph id",
    )
    _ = parser.add_argument("--hwpx", required=True, help="Input .hwpx template path")
    _ = parser.add_argument(
        "--fills",
        required=True,
        help='JSON: {"paragraph_id": [["charPrIDRef", "text"], ...]}',
    )
    _ = parser.add_argument("--output", "-o", required=True, help="Output .hwpx path")
    args = parser.parse_args(namespace=CliArgs())

    input_path = Path(args.hwpx)
    if not input_path.is_file():
        print(f"Error: File not found: {args.hwpx}", file=sys.stderr)
        sys.exit(1)

    try:
        fills = _parse_fills(args.fills)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    if output_path.parent != Path(""):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        unresolved = fill_hwpx(input_path, fills, output_path)
    except (KeyError, OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if unresolved:
        print("Unresolved slots: " + ", ".join(unresolved))

    errors = validate_surgery(input_path, output_path)
    if errors:
        print(f"FAIL: surgery validation ({len(errors)} issues)")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("PASS: surgery validation")
    print("  standalone, xmlns, newlines, byte-identical, compression — all OK")


if __name__ == "__main__":
    main()
