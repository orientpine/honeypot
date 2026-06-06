# pyright: reportMissingImports=false, reportMissingParameterType=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportIndexIssue=false
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def load_form_mapper(scripts_dir: Path):
    sys.path.insert(0, str(scripts_dir))
    import form_mapper

    return form_mapper


def run_form_mapper_cli(scripts_dir: Path, hwpx_path: Path, out_path: Path) -> None:
    result = subprocess.run(
        [
            "python3",
            str(scripts_dir / "form_mapper.py"),
            str(hwpx_path),
            "--output",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def paragraph_id_slots(form_map: dict[str, object]) -> list[dict[str, object]]:
    slots = form_map["slots"]
    assert isinstance(slots, list)
    return [
        slot
        for slot in slots
        if isinstance(slot, dict)
        and isinstance(slot.get("addressing"), dict)
        and slot["addressing"].get("method") == "paragraph_id"
    ]


def paragraph_ids(form_map: dict[str, object]) -> set[int]:
    return {
        int(slot["addressing"]["paragraph_id"])
        for slot in paragraph_id_slots(form_map)
    }


def test_form_simple_slot_count(scripts_dir, form_simple_path):
    form_mapper = load_form_mapper(scripts_dir)

    form_map, warnings = form_mapper.build_form_map(form_simple_path)

    assert warnings == []
    assert len(paragraph_id_slots(form_map)) == 4


def test_form_simple_slot_ids(scripts_dir, form_simple_path):
    form_mapper = load_form_mapper(scripts_dir)

    form_map, warnings = form_mapper.build_form_map(form_simple_path)

    assert warnings == []
    assert paragraph_ids(form_map) == {1000000004, 1000000006, 1000000008, 1000000009}


def test_form_edge_uniqueness(scripts_dir, form_edge_path):
    form_mapper = load_form_mapper(scripts_dir)

    form_map, warnings = form_mapper.build_form_map(form_edge_path)
    ids = [
        slot["addressing"]["paragraph_id"]
        for slot in paragraph_id_slots(form_map)
    ]

    assert warnings == []
    assert len(ids) >= 2
    assert len(set(ids)) == len(ids)


def test_determinism(scripts_dir, form_simple_path, tmp_path):
    first = tmp_path / "first.form_map.json"
    second = tmp_path / "second.form_map.json"

    run_form_mapper_cli(scripts_dir, form_simple_path, first)
    run_form_mapper_cli(scripts_dir, form_simple_path, second)

    assert first.read_bytes() == second.read_bytes()


def test_imports_analyze_template(scripts_dir):
    source = (scripts_dir / "form_mapper.py").read_text(encoding="utf-8")

    assert "import analyze_template" in source or "as at" in source


def test_no_crash_instruction_only(scripts_dir, make_test_hwpx):
    form_mapper = load_form_mapper(scripts_dir)
    no_empty_input_path = make_test_hwpx(chapters=1)

    form_map, warnings = form_mapper.build_form_map(no_empty_input_path)

    assert warnings == []
    assert len(form_map["slots"]) == 0
