#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAny=false
from __future__ import annotations

import re
import sys
import zipfile
from html import unescape
from pathlib import Path
from typing import Callable


SECTION_XML = "Contents/section0.xml"
SLOT_A = "1000000004"
SLOT_B = "1000000006"


def _load_required_modules(scripts_dir: Path):
    sys.path.insert(0, str(scripts_dir))
    from slot_filler import fill_slots_by_paragraph_id
    from zip_surgery import validate_surgery, HwpxSurgeon

    return fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon


def _extract_plain_with_optional_text_extract(hwpx_path: Path, section_text: str) -> str:
    try:
        from text_extract import extract_plain
    except ModuleNotFoundError:
        return "".join(
            unescape(text) for text in re.findall(r"<hp:t>(.*?)</hp:t>", section_text)
        )
    return extract_plain(str(hwpx_path), include_tables=True)


def _section_bytes(hwpx_path: Path) -> bytes:
    with zipfile.ZipFile(str(hwpx_path), "r") as zf:
        return zf.read(SECTION_XML)


def _save_filled_hwpx(
    source_path: Path,
    filled_section_bytes: bytes,
    output_path: Path,
    HwpxSurgeon,
) -> Path:
    surgeon = HwpxSurgeon(source_path)
    surgeon.replace_text(
        {surgeon.section_bytes.decode("utf-8"): filled_section_bytes.decode("utf-8")}
    )
    return surgeon.save(output_path)


def _fill_and_save(
    source_path: Path,
    fills: dict[str, list[tuple[str, str]]],
    output_path: Path,
    scripts_dir: Path,
) -> tuple[bytes, list[str], Path, Callable[[str | Path, str | Path], list[str]]]:
    fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon = _load_required_modules(
        scripts_dir
    )
    filled_section, unresolved = fill_slots_by_paragraph_id(
        _section_bytes(source_path), fills
    )
    result_path = _save_filled_hwpx(
        source_path, filled_section, output_path, HwpxSurgeon
    )
    return filled_section, unresolved, result_path, validate_surgery


def _paragraph_xml(section_text: str, paragraph_id: str) -> str:
    match = re.search(
        rf'<hp:p id="{re.escape(paragraph_id)}"(?=[ >]).*?</hp:p>',
        section_text,
    )
    assert match is not None, f"paragraph {paragraph_id} not found"
    return match.group(0)


def _paragraph_text(paragraph_xml: str) -> str:
    return "".join(unescape(text) for text in re.findall(r"<hp:t>(.*?)</hp:t>", paragraph_xml))


def _opening_tag(paragraph_xml: str) -> str:
    return paragraph_xml[: paragraph_xml.index(">") + 1]


def _normalized_empty_cell_shape(paragraph_xml: str) -> str:
    return re.sub(r'id="\d+"', 'id="PID"', paragraph_xml, count=1)


def test_fill_single_slot_validates(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    filled_section, unresolved, result_path, validate_surgery = _fill_and_save(
        form_simple_path,
        {SLOT_A: [("0", "단일 슬롯 채움")]},
        tmp_path / "form_simple.filled.hwpx",
        scripts_dir,
    )

    assert unresolved == []
    assert "단일 슬롯 채움" in filled_section.decode("utf-8")
    assert validate_surgery(form_simple_path, result_path) == []


def test_fill_only_target_cell(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    content = "target-cell-only"
    filled_section, unresolved, result_path, validate_surgery = _fill_and_save(
        form_simple_path,
        {SLOT_A: [("0", content)]},
        tmp_path / "form_simple.target-only.hwpx",
        scripts_dir,
    )
    section_text = filled_section.decode("utf-8")

    assert unresolved == []
    assert _paragraph_text(_paragraph_xml(section_text, SLOT_A)) == content
    for paragraph_id in (SLOT_B, "1000000008", "1000000009"):
        assert _paragraph_text(_paragraph_xml(section_text, paragraph_id)) == ""
    extracted_text = _extract_plain_with_optional_text_extract(result_path, section_text)
    assert extracted_text.count(content) == 1
    assert validate_surgery(form_simple_path, result_path) == []


def test_uniqueness_form_edge(form_edge_path: Path, scripts_dir: Path, tmp_path: Path):
    original_text = _section_bytes(form_edge_path).decode("utf-8")
    original_a = _paragraph_xml(original_text, SLOT_A)
    original_b = _paragraph_xml(original_text, SLOT_B)
    assert _normalized_empty_cell_shape(original_a) == _normalized_empty_cell_shape(
        original_b
    )

    content = "edge-slot-a-only"
    filled_section, unresolved, result_path, validate_surgery = _fill_and_save(
        form_edge_path,
        {SLOT_A: [("0", content)]},
        tmp_path / "form_edge.a-only.hwpx",
        scripts_dir,
    )
    section_text = filled_section.decode("utf-8")

    assert unresolved == []
    assert _paragraph_text(_paragraph_xml(section_text, SLOT_A)) == content
    assert _paragraph_xml(section_text, SLOT_B) == original_b
    assert _paragraph_text(_paragraph_xml(section_text, SLOT_B)) == ""
    assert validate_surgery(form_edge_path, result_path) == []


def test_unresolved_slot_reported(form_simple_path: Path, scripts_dir: Path):
    fill_slots_by_paragraph_id, _, _ = _load_required_modules(scripts_dir)

    filled_section, unresolved = fill_slots_by_paragraph_id(
        _section_bytes(form_simple_path),
        {"9999999999": [("0", "ignored because slot does not exist")]},
    )

    assert unresolved == ["9999999999"]
    assert "ignored because slot does not exist" not in filled_section.decode("utf-8")


def test_multirun_fill(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    original_text = _section_bytes(form_simple_path).decode("utf-8")
    original_opening = _opening_tag(_paragraph_xml(original_text, SLOT_A))

    filled_section, unresolved, result_path, validate_surgery = _fill_and_save(
        form_simple_path,
        {SLOT_A: [("0", "first "), ("0", "second")]},
        tmp_path / "form_simple.multirun.hwpx",
        scripts_dir,
    )
    filled_paragraph = _paragraph_xml(filled_section.decode("utf-8"), SLOT_A)

    assert unresolved == []
    assert _opening_tag(filled_paragraph) == original_opening
    assert filled_paragraph.count('<hp:run charPrIDRef="0">') == 2
    assert "<hp:t>first </hp:t>" in filled_paragraph
    assert "<hp:t>second</hp:t>" in filled_paragraph
    assert _paragraph_text(filled_paragraph) == "first second"
    assert validate_surgery(form_simple_path, result_path) == []


def test_invariants(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    filled_section, unresolved, result_path, validate_surgery = _fill_and_save(
        form_simple_path,
        {SLOT_A: [("0", "invariant check")]},
        tmp_path / "form_simple.invariants.hwpx",
        scripts_dir,
    )
    section_text = filled_section.decode("utf-8")
    root_end = section_text.find(">", section_text.find("<hs:sec")) + 1
    assert root_end > 0

    root_tag = section_text[:root_end]
    body = section_text[root_end:]

    assert unresolved == []
    assert section_text.count("\n") == 1
    assert root_tag.count("xmlns:") >= 10
    assert body.count("xmlns:") == 0
    assert validate_surgery(form_simple_path, result_path) == []
