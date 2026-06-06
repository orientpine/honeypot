#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportExplicitAny=false, reportAny=false
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from html import unescape
from pathlib import Path
from typing import Any, cast

import pytest


pytestmark = pytest.mark.integration

SECTION_XML = "Contents/section0.xml"
KNOWN_EMPTY_SLOT_IDS = {"1000000004", "1000000006", "1000000008", "1000000009"}
SLOT_A = "1000000004"
SLOT_B = "1000000006"


def _load_form_fill_modules(scripts_dir: Path) -> tuple[Any, Any, Any, Any]:
    sys.path.insert(0, str(scripts_dir))
    import form_mapper
    from slot_filler import fill_slots_by_paragraph_id
    from zip_surgery import validate_surgery, HwpxSurgeon

    return form_mapper, fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon


def _section_bytes(hwpx_path: Path) -> bytes:
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return zf.read(SECTION_XML)


def _save_section(source_path: Path, section_bytes: bytes, output_path: Path, HwpxSurgeon: Any) -> Path:
    surgeon = HwpxSurgeon(source_path)
    surgeon.replace_text({surgeon.section_bytes.decode("utf-8"): section_bytes.decode("utf-8")})
    return surgeon.save(output_path)


def _paragraph_xml(section_text: str, paragraph_id: str) -> str:
    match = re.search(rf'<hp:p id="{re.escape(paragraph_id)}"(?=[ >]).*?</hp:p>', section_text)
    assert match is not None, f"paragraph {paragraph_id} not found"
    return match.group(0)


def _paragraph_text(section_text: str, paragraph_id: str) -> str:
    paragraph_xml = _paragraph_xml(section_text, paragraph_id)
    return "".join(unescape(text) for text in re.findall(r"<hp:t>(.*?)</hp:t>", paragraph_xml))


def _final_static_form_map(partial_form_map: dict[str, object]) -> dict[str, object]:
    final_form_map = json.loads(json.dumps(partial_form_map, ensure_ascii=False))
    slots = cast(list[dict[str, object]], final_form_map["slots"])
    for slot in slots:
        slot["slot_type"] = "empty_input"
        slot["zone"] = "detail"
        slot["confidence"] = "high"
    final_form_map["confidence"] = "high"
    return cast(dict[str, object], final_form_map)


def _paragraph_id_slots(form_map: dict[str, object]) -> list[dict[str, object]]:
    slots = cast(list[dict[str, object]], form_map["slots"])
    return [
        slot
        for slot in slots
        if cast(dict[str, object], slot["addressing"])["method"] == "paragraph_id"
    ]


def _fills_from_form_map(
    final_form_map: dict[str, object], content_by_paragraph_id: dict[str, str]
) -> dict[str, list[tuple[str, str]]]:
    fills: dict[str, list[tuple[str, str]]] = {}
    for slot in cast(list[dict[str, object]], final_form_map["slots"]):
        addressing = cast(dict[str, object], slot["addressing"])
        paragraph_id = addressing.get("paragraph_id")
        if (
            addressing.get("method") == "paragraph_id"
            and slot.get("confidence") == "high"
            and isinstance(paragraph_id, str)
            and paragraph_id in content_by_paragraph_id
        ):
            fills[paragraph_id] = [("0", content_by_paragraph_id[paragraph_id])]
    return fills


def _run_text_extract(scripts_dir: Path, hwpx_path: Path) -> str:
    result = subprocess.run(
        [
            sys.executable,
            str(scripts_dir / "text_extract.py"),
            str(hwpx_path),
            "--include-tables",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout
    if "ModuleNotFoundError: No module named 'hwpx'" in result.stderr:
        section_text = _section_bytes(hwpx_path).decode("utf-8")
        return "".join(unescape(text) for text in re.findall(r"<hp:t>(.*?)</hp:t>", section_text))
    assert result.returncode == 0, result.stderr
    return result.stdout


def _build_base_hwpx(scripts_dir: Path, output_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "build_hwpx.py"), "--output", str(output_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output_path.is_file()


def test_e2e_pipeline_form_simple(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    form_mapper, fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon = _load_form_fill_modules(scripts_dir)
    partial_form_map, warnings = form_mapper.build_form_map(form_simple_path)
    final_form_map = _final_static_form_map(partial_form_map)
    fills = _fills_from_form_map(
        final_form_map,
        {SLOT_A: "연구책임자", SLOT_B: "2026년 6월"},
    )

    filled_section, unresolved = fill_slots_by_paragraph_id(_section_bytes(form_simple_path), fills)
    result_path = _save_section(form_simple_path, filled_section, tmp_path / "form_simple.e2e.hwpx", HwpxSurgeon)
    section_text = filled_section.decode("utf-8")
    extracted = _run_text_extract(scripts_dir, result_path)

    assert warnings == []
    assert {cast(dict[str, object], slot["addressing"])["paragraph_id"] for slot in _paragraph_id_slots(final_form_map)} == KNOWN_EMPTY_SLOT_IDS
    assert unresolved == []
    assert validate_surgery(form_simple_path, result_path) == []
    assert _paragraph_text(section_text, SLOT_A) == "연구책임자"
    assert _paragraph_text(section_text, SLOT_B) == "2026년 6월"
    for paragraph_id in KNOWN_EMPTY_SLOT_IDS - {SLOT_A, SLOT_B}:
        assert _paragraph_text(section_text, paragraph_id) == ""
    assert extracted.count("연구책임자") == 1
    assert extracted.count("2026년 6월") == 1


def test_e2e_content_in_declared_cell_only(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    _form_mapper, fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon = _load_form_fill_modules(scripts_dir)
    content = "테스트 내용"

    filled_section, unresolved = fill_slots_by_paragraph_id(
        _section_bytes(form_simple_path), {SLOT_A: [("0", content)]}
    )
    result_path = _save_section(form_simple_path, filled_section, tmp_path / "form_simple.ac4.hwpx", HwpxSurgeon)
    section_text = filled_section.decode("utf-8")

    assert unresolved == []
    assert section_text.count(content) == 1
    assert _paragraph_text(section_text, SLOT_A) == content
    assert _paragraph_text(section_text, SLOT_B) == ""
    assert content not in _paragraph_xml(section_text, SLOT_B)
    assert validate_surgery(form_simple_path, result_path) == []


def test_e2e_xml_first_regression_lock(scripts_dir: Path, tmp_path: Path):
    first = tmp_path / "xml_first_1.hwpx"
    second = tmp_path / "xml_first_2.hwpx"

    _build_base_hwpx(scripts_dir, first)
    _build_base_hwpx(scripts_dir, second)

    assert first.read_bytes() == second.read_bytes()


def test_e2e_unresolved_not_silently_filled(form_simple_path: Path, scripts_dir: Path):
    _form_mapper, fill_slots_by_paragraph_id, _validate_surgery, _HwpxSurgeon = _load_form_fill_modules(scripts_dir)
    form_map = {
        "schema_version": "1.0.0",
        "source_template": form_simple_path.name,
        "slots": [
            {
                "slot_id": "slot_unresolved",
                "slot_type": "empty_input",
                "addressing": {"method": "unresolved", "paragraph_id": None, "cell": None},
                "zone": "detail",
                "confidence": "high",
            }
        ],
    }
    slot_id = cast(str, cast(list[dict[str, object]], form_map["slots"])[0]["slot_id"])

    filled_section, unresolved = fill_slots_by_paragraph_id(
        _section_bytes(form_simple_path), {slot_id: [("0", "절대 채워지면 안 됨")]}
    )
    section_text = filled_section.decode("utf-8")

    assert slot_id in unresolved
    assert "절대 채워지면 안 됨" not in section_text
    assert _paragraph_text(section_text, SLOT_A) == ""


def test_e2e_validate_surgery_invariants(form_simple_path: Path, scripts_dir: Path, tmp_path: Path):
    _form_mapper, fill_slots_by_paragraph_id, validate_surgery, HwpxSurgeon = _load_form_fill_modules(scripts_dir)

    filled_section, unresolved = fill_slots_by_paragraph_id(
        _section_bytes(form_simple_path), {SLOT_A: [("0", "불변식 검증")]}
    )
    result_path = _save_section(form_simple_path, filled_section, tmp_path / "form_simple.invariants.hwpx", HwpxSurgeon)
    section_text = filled_section.decode("utf-8")
    root_end = section_text.find(">", section_text.find("<hs:sec")) + 1
    assert root_end > 0
    root_tag = section_text[:root_end]
    body = section_text[root_end:]

    assert unresolved == []
    assert "standalone='no'" in section_text[:200] or 'standalone="no"' in section_text[:200]
    assert root_tag.count("xmlns:") >= 10
    assert body.count("xmlns:") == 0
    assert section_text.count("\n") == 1
    assert validate_surgery(form_simple_path, result_path) == []
