#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias, cast
import xml.etree.ElementTree as etree

sys.path.insert(0, str(Path(__file__).parent)); import analyze_template as at  # pyright: ignore[reportImplicitRelativeImport]


JsonObject: TypeAlias = dict[str, object]
NS: dict[str, str] = at.NS
GET_TEXT = cast(Callable[[etree.Element], str], at.get_text)


SCHEMA_VERSION = "1.0.0"
PLACEHOLDER_SYMBOLS = {"◦", "○", "•", "-", "※", "·", "□", "■"}
SECTION_XML = "Contents/section0.xml"
HEADER_XML = "Contents/header.xml"


@dataclass
class ParagraphInfo:
    element: etree.Element
    paragraph_id: str | None
    text: str
    para_order: int
    top_para_order: int
    table_index: int | None = None
    row: int | None = None
    col: int | None = None
    label_association: str | None = None

    @property
    def is_table_slot(self) -> bool:
        return self.table_index is not None


@dataclass
class CellInfo:
    table_index: int
    row: int
    col: int
    row_span: int
    col_span: int
    text: str
    paragraphs: list[ParagraphInfo] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return is_empty_input(self.text)

    @property
    def is_short_label_text(self) -> bool:
        stripped = self.text.strip()
        return bool(stripped) and not is_empty_input(stripped) and len(stripped) <= 30


@dataclass
class TableInfo:
    index: int
    cells: dict[tuple[int, int], CellInfo] = field(default_factory=dict)
    label_cells: set[tuple[int, int]] = field(default_factory=set)


class ScanState:
    def __init__(self) -> None:
        self.next_table_index: int = 0
        self.next_para_order: int = 0
        self.tables: dict[int, TableInfo] = {}
        self.empty_slots: list[ParagraphInfo] = []
        self.paragraph_ids: list[str] = []

    def para_order(self) -> int:
        value = self.next_para_order
        self.next_para_order += 1
        return value

    def table_index(self) -> int:
        value = self.next_table_index
        self.next_table_index += 1
        return value

    def record_paragraph(self, p: etree.Element) -> None:
        paragraph_id = p.get("id")
        if paragraph_id is not None:
            self.paragraph_ids.append(paragraph_id)


def is_empty_input(text: str) -> bool:
    if text == "":
        return True
    stripped = text.strip()
    if stripped == "":
        return True
    return stripped in PLACEHOLDER_SYMBOLS


def _safe_int(raw: str | None, default: int) -> int:
    try:
        return int(raw) if raw is not None else default
    except ValueError:
        return default


def _load_roots(hwpx_path: Path) -> tuple[etree.Element, etree.Element]:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            names = set(zf.namelist())
            missing = [name for name in (HEADER_XML, SECTION_XML) if name not in names]
            if missing:
                raise ValueError(f"Missing required HWPX XML: {', '.join(missing)}")
            header_path = Path(zf.extract(HEADER_XML, tmpdir))
            section_path = Path(zf.extract(SECTION_XML, tmpdir))

        header_root = etree.parse(header_path).getroot()
        section_root = etree.parse(section_path).getroot()
        return header_root, section_root


def _has_nonfillable_control(p: etree.Element) -> bool:
    return (
        p.find(".//hp:secPr", NS) is not None
        or p.find(".//hp:ctrl", NS) is not None
        or p.find(".//hp:pic", NS) is not None
    )


def _cell_address(tc: etree.Element, fallback_row: int, fallback_col: int) -> tuple[int, int]:
    addr = tc.find("hp:cellAddr", NS)
    if addr is None:
        return fallback_row, fallback_col
    row = _safe_int(addr.get("rowAddr"), fallback_row)
    col = _safe_int(addr.get("colAddr"), fallback_col)
    return row, col


def _cell_span(tc: etree.Element) -> tuple[int, int]:
    span = tc.find("hp:cellSpan", NS)
    if span is None:
        return 1, 1
    row_span = _safe_int(span.get("rowSpan"), 1)
    col_span = _safe_int(span.get("colSpan"), 1)
    return row_span, col_span


def _walk_table(tbl: etree.Element, state: ScanState, top_para_order: int) -> None:
    table_index = state.table_index()
    table = TableInfo(index=table_index)
    state.tables[table_index] = table

    for fallback_row, tr in enumerate(tbl.findall("hp:tr", NS)):
        for fallback_col, tc in enumerate(tr.findall("hp:tc", NS)):
            row, col = _cell_address(tc, fallback_row, fallback_col)
            row_span, col_span = _cell_span(tc)
            sublist = tc.find("hp:subList", NS)
            cell_text = GET_TEXT(sublist) if sublist is not None else ""
            cell = CellInfo(
                table_index=table_index,
                row=row,
                col=col,
                row_span=row_span,
                col_span=col_span,
                text=cell_text,
            )
            table.cells[(row, col)] = cell

            if sublist is None:
                continue

            for p in sublist.findall("hp:p", NS):
                state.record_paragraph(p)
                para = ParagraphInfo(
                    element=p,
                    paragraph_id=p.get("id"),
                    text=GET_TEXT(p),
                    para_order=state.para_order(),
                    top_para_order=top_para_order,
                    table_index=table_index,
                    row=row,
                    col=col,
                )
                cell.paragraphs.append(para)

                nested_tables: list[etree.Element] = []
                for run in p.findall("hp:run", NS):
                    nested = run.find("hp:tbl", NS)
                    if nested is not None:
                        nested_tables.append(nested)

                if nested_tables:
                    for nested in nested_tables:
                        _walk_table(nested, state, top_para_order)
                    continue

                if is_empty_input(para.text):
                    state.empty_slots.append(para)


def _has_adjacent_empty_cell(table: TableInfo, cell: CellInfo) -> bool:
    right = table.cells.get((cell.row, cell.col + cell.col_span))
    below = table.cells.get((cell.row + cell.row_span, cell.col))
    return (right is not None and right.is_empty) or (below is not None and below.is_empty)


def _build_label_candidates(table: TableInfo) -> None:
    for key, cell in table.cells.items():
        if cell.is_short_label_text and _has_adjacent_empty_cell(table, cell):
            table.label_cells.add(key)


def _find_left_label(table: TableInfo, slot: ParagraphInfo) -> str | None:
    if slot.row is None or slot.col is None:
        return None

    candidates: list[CellInfo] = []
    for key in table.label_cells:
        cell = table.cells[key]
        if cell.row == slot.row and cell.col + cell.col_span == slot.col:
            candidates.append(cell)

    if not candidates:
        return None
    nearest = max(candidates, key=lambda cell: cell.col)
    return nearest.text.strip() or None


def _find_above_label(table: TableInfo, slot: ParagraphInfo) -> str | None:
    if slot.row is None or slot.col is None:
        return None

    candidates: list[CellInfo] = []
    for key in table.label_cells:
        cell = table.cells[key]
        same_column = cell.col <= slot.col < cell.col + cell.col_span
        directly_above = cell.row + cell.row_span == slot.row
        if same_column and directly_above:
            candidates.append(cell)

    if not candidates:
        return None
    nearest = max(candidates, key=lambda cell: cell.row)
    return nearest.text.strip() or None


def _find_same_cell_label(table: TableInfo, slot: ParagraphInfo) -> str | None:
    if slot.row is None or slot.col is None:
        return None
    cell = table.cells.get((slot.row, slot.col))
    if cell is None:
        return None

    labels = [
        p.text.strip()
        for p in cell.paragraphs
        if p.para_order < slot.para_order
        and p.text.strip()
        and not is_empty_input(p.text)
        and len(p.text.strip()) <= 30
    ]
    return labels[-1] if labels else None


def _assign_table_labels(state: ScanState) -> None:
    for table in state.tables.values():
        _build_label_candidates(table)

    for slot in state.empty_slots:
        if slot.table_index is None:
            continue
        table = state.tables[slot.table_index]
        slot.label_association = (
            _find_left_label(table, slot)
            or _find_same_cell_label(table, slot)
            or _find_above_label(table, slot)
        )


def _walk_section(section_root: etree.Element) -> tuple[list[ParagraphInfo], set[str]]:
    state = ScanState()
    sec = section_root.find(".//hs:sec", NS)
    if sec is None:
        sec = section_root

    for p in sec.findall("hp:p", NS):
        top_para_order = state.para_order()
        state.record_paragraph(p)
        tables: list[etree.Element] = []
        for run in p.findall("hp:run", NS):
            tbl = run.find("hp:tbl", NS)
            if tbl is not None:
                tables.append(tbl)

        if tables:
            for tbl in tables:
                _walk_table(tbl, state, top_para_order)
            continue

        text = GET_TEXT(p)
        if _has_nonfillable_control(p):
            continue
        if is_empty_input(text):
            state.empty_slots.append(
                ParagraphInfo(
                    element=p,
                    paragraph_id=p.get("id"),
                    text=text,
                    para_order=top_para_order,
                    top_para_order=top_para_order,
                )
            )

    _assign_table_labels(state)
    return sorted(state.empty_slots, key=_slot_sort_key), _duplicate_ids(state.paragraph_ids)


def _slot_sort_key(slot: ParagraphInfo) -> tuple[int, int, int, int, int]:
    table_index = slot.table_index if slot.table_index is not None else 1_000_000
    row = slot.row if slot.row is not None else 1_000_000
    col = slot.col if slot.col is not None else 1_000_000
    return (slot.top_para_order, table_index, row, col, slot.para_order)


def _addressing(slot: ParagraphInfo, duplicate_ids: set[str]) -> JsonObject:
    cell: JsonObject | None = None
    if slot.is_table_slot:
        cell = {
            "table_index": slot.table_index,
            "row": slot.row,
            "col": slot.col,
        }

    if slot.paragraph_id is None or slot.paragraph_id in duplicate_ids:
        return {
            "method": "sentinel",
            "paragraph_id": None,
            "cell": cell,
        }

    return {
        "method": "paragraph_id",
        "paragraph_id": slot.paragraph_id,
        "cell": cell,
    }


def _duplicate_ids(paragraph_ids: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for paragraph_id in paragraph_ids:
        if paragraph_id in seen:
            duplicates.add(paragraph_id)
        seen.add(paragraph_id)
    return duplicates


def build_form_map(hwpx_path: str | Path) -> tuple[JsonObject, list[str]]:
    path = Path(hwpx_path)
    _header_root, section_root = _load_roots(path)
    slots, duplicate_ids = _walk_section(section_root)

    warnings = [
        f"Duplicate paragraph_id {pid}; using sentinel addressing"
        for pid in sorted(duplicate_ids)
    ]

    mapped_slots: list[JsonObject] = []
    for index, slot in enumerate(slots, start=1):
        mapped_slots.append(
            {
                "slot_id": f"slot_{index:02d}",
                "slot_type": None,
                "addressing": _addressing(slot, duplicate_ids),
                "label_association": slot.label_association,
                "zone": None,
                "confidence": None,
                "expected_content_hint": None,
            }
        )

    return (
        {
            "schema_version": SCHEMA_VERSION,
            "source_template": path.name,
            "slots": mapped_slots,
            "unresolved": [],
            "confidence": None,
        },
        warnings,
    )


def _summary(form_map: JsonObject) -> str:
    slots = cast(list[JsonObject], form_map["slots"])
    table_count = sum(
        1
        for slot in slots
        if cast(JsonObject, slot["addressing"])["cell"] is not None
    )
    body_count = len(slots) - table_count
    return (
        f"Found {len(slots)} empty slots: "
        f"{table_count} table cells, {body_count} body placeholder"
        f"{'s' if body_count != 1 else ''}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract deterministic fillable slot addresses from an HWPX template"
    )
    _ = parser.add_argument("input", help="Path to .hwpx template")
    _ = parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output form_map.partial.json path",
    )
    args = parser.parse_args()

    input_arg = cast(str, args.input)
    output_arg = cast(str, args.output)
    input_path = Path(input_arg)
    if not input_path.is_file():
        print(f"Error: File not found: {input_arg}", file=sys.stderr)
        sys.exit(1)

    try:
        form_map, warnings = build_form_map(input_path)
    except (OSError, zipfile.BadZipFile, etree.ParseError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(output_arg)
    if output_path.parent != Path(""):
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_text = json.dumps(form_map, ensure_ascii=False, indent=2) + "\n"
    _ = output_path.write_text(output_text, encoding="utf-8")

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    print(_summary(form_map))


if __name__ == "__main__":
    main()
