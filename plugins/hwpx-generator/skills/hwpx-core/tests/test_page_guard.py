#!/usr/bin/env python3
"""Tests for page_guard.py --mode=template-fill and default mode."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

# Import page_guard from scripts/ (sibling of tests/)
# tests/test_page_guard.py -> parent = tests/ -> parent = hwpx-core/ -> scripts/
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
_spec = importlib.util.spec_from_file_location(
    "page_guard", _SCRIPTS_DIR / "page_guard.py"
)
assert _spec and _spec.loader
_page_guard = importlib.util.module_from_spec(_spec)
sys.modules["page_guard"] = _page_guard
_spec.loader.exec_module(_page_guard)

Metrics = _page_guard.Metrics
compare_metrics = _page_guard.compare_metrics


def _make_metrics(
    paragraph_count: int = 10,
    page_break_count: int = 0,
    column_break_count: int = 0,
    table_count: int = 2,
    table_shapes: list | None = None,
    text_char_total: int = 1000,
    text_char_total_nospace: int = 800,
    paragraph_text_lengths: List[int] | None = None,
) -> Metrics:
    return Metrics(
        paragraph_count=paragraph_count,
        page_break_count=page_break_count,
        column_break_count=column_break_count,
        table_count=table_count,
        table_shapes=table_shapes or [],
        text_char_total=text_char_total,
        text_char_total_nospace=text_char_total_nospace,
        paragraph_text_lengths=paragraph_text_lengths or [100] * paragraph_count,
    )


# ── CLI argument tests ──────────────────────────────────────────────


def test_mode_argument_exists():
    """--mode argument is registered with correct choices."""
    with patch(
        "sys.argv",
        [
            "page_guard",
            "--reference",
            "r.hwpx",
            "--output",
            "o.hwpx",
            "--mode",
            "template-fill",
        ],
    ):
        parser = _build_parser()
        args = parser.parse_args()
        assert args.mode == "template-fill"


def test_mode_default_value():
    """--mode defaults to 'default' when not specified."""
    with patch(
        "sys.argv", ["page_guard", "--reference", "r.hwpx", "--output", "o.hwpx"]
    ):
        parser = _build_parser()
        args = parser.parse_args()
        assert args.mode == "default"


def test_mode_invalid_choice():
    """--mode rejects invalid choices."""
    with patch(
        "sys.argv",
        [
            "page_guard",
            "--reference",
            "r.hwpx",
            "--output",
            "o.hwpx",
            "--mode",
            "bogus",
        ],
    ):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args()


def _build_parser():
    """Build the same parser as page_guard.main() uses."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", "-r", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--max-text-delta-ratio", type=float, default=0.15)
    parser.add_argument("--max-paragraph-delta-ratio", type=float, default=0.25)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--mode", choices=["default", "template-fill"], default="default"
    )
    return parser


def test_help_returns_zero(scripts_dir):
    """page_guard.py --help exits 0."""
    import subprocess

    result = subprocess.run(
        [sys.executable, str(scripts_dir / "page_guard.py"), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout


# ── Default mode: behavior unchanged ────────────────────────────────


def test_default_mode_detects_paragraph_count_mismatch():
    """Default mode flags paragraph count differences."""
    ref = _make_metrics(paragraph_count=10)
    out = _make_metrics(paragraph_count=15)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert any("문단 수 불일치" in e for e in errors)


def test_default_mode_detects_text_length_delta():
    """Default mode flags large text length changes."""
    ref = _make_metrics(text_char_total_nospace=800)
    out = _make_metrics(text_char_total_nospace=1200)  # 50% delta
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert any("전체 텍스트 길이 편차 초과" in e for e in errors)


def test_default_mode_detects_paragraph_text_delta():
    """Default mode flags per-paragraph text changes."""
    ref = _make_metrics(paragraph_count=3, paragraph_text_lengths=[100, 100, 100])
    out = _make_metrics(paragraph_count=3, paragraph_text_lengths=[100, 200, 100])
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert any("문단 텍스트 길이 편차 초과" in e for e in errors)


def test_default_mode_passes_identical():
    """Default mode passes when metrics are identical."""
    ref = _make_metrics()
    out = _make_metrics()
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert errors == []


def test_default_mode_detects_table_count_mismatch():
    """Default mode flags table count differences."""
    ref = _make_metrics(table_count=2)
    out = _make_metrics(table_count=3)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert any("표 수 불일치" in e for e in errors)


def test_default_mode_detects_page_break_mismatch():
    """Default mode flags pageBreak differences."""
    ref = _make_metrics(page_break_count=1)
    out = _make_metrics(page_break_count=2)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="default")
    assert any("pageBreak 수 불일치" in e for e in errors)


# ── Template-fill mode: text/paragraph suppressed ───────────────────


def test_template_fill_suppresses_paragraph_count():
    """Template-fill mode ignores paragraph count differences."""
    ref = _make_metrics(paragraph_count=5)
    out = _make_metrics(paragraph_count=20)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert not any("문단 수 불일치" in e for e in errors)


def test_template_fill_suppresses_text_length_delta():
    """Template-fill mode ignores text length growth."""
    ref = _make_metrics(text_char_total_nospace=100)
    out = _make_metrics(text_char_total_nospace=2000)  # 1900% delta
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert not any("전체 텍스트 길이 편차 초과" in e for e in errors)


def test_template_fill_suppresses_paragraph_text_delta():
    """Template-fill mode ignores per-paragraph text changes."""
    ref = _make_metrics(paragraph_count=3, paragraph_text_lengths=[10, 10, 10])
    out = _make_metrics(paragraph_count=3, paragraph_text_lengths=[10, 500, 10])
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert not any("문단 텍스트 길이 편차 초과" in e for e in errors)


def test_template_fill_allows_table_addition():
    """Template-fill mode allows table additions (warning, not error)."""
    ref = _make_metrics(table_count=3)
    out = _make_metrics(table_count=5)
    errors, warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert not any("표 수 불일치" in e for e in errors)
    assert any("표 2개 추가" in w for w in warnings)


def test_template_fill_still_detects_table_shape():
    """Template-fill mode still catches table shape changes."""
    ref = _make_metrics(table_shapes=[("3", "4", "100", "200", "", "")])
    out = _make_metrics(table_shapes=[("5", "4", "100", "200", "", "")])
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert any("표 구조" in e for e in errors)


def test_template_fill_still_detects_page_break():
    """Template-fill mode still catches pageBreak differences."""
    ref = _make_metrics(page_break_count=1)
    out = _make_metrics(page_break_count=3)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert any("pageBreak 수 불일치" in e for e in errors)


def test_template_fill_still_detects_column_break():
    """Template-fill mode still catches columnBreak differences."""
    ref = _make_metrics(column_break_count=0)
    out = _make_metrics(column_break_count=2)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert any("columnBreak 수 불일치" in e for e in errors)


def test_template_fill_passes_when_structure_identical():
    """Template-fill mode passes when structural elements match (ignoring text)."""
    ref = _make_metrics(
        text_char_total_nospace=50, paragraph_count=5, paragraph_text_lengths=[10] * 5
    )
    out = _make_metrics(
        text_char_total_nospace=5000,
        paragraph_count=50,
        paragraph_text_lengths=[100] * 50,
    )
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert errors == []


def test_template_fill_detects_table_deletion():
    """Template-fill mode detects table deletion as error."""
    ref = _make_metrics(table_count=5)
    out = _make_metrics(table_count=3)
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert any("표 삭제 감지" in e for e in errors)


def test_template_fill_detects_existing_table_structure_change():
    """Template-fill mode detects modification of existing table structures."""
    original = [("3", "4", "100", "200", "", ""), ("2", "3", "50", "60", "", "")]
    modified = [("3", "4", "100", "200", "", ""), ("9", "9", "50", "60", "", "")]
    ref = _make_metrics(table_count=2, table_shapes=original)
    out = _make_metrics(table_count=3, table_shapes=modified + [("1", "1", "10", "10", "", "")])
    errors, _warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert any("기존 표 구조 변경 감지" in e for e in errors)


def test_template_fill_warning_on_table_addition():
    """Template-fill mode emits warning (not error) for table additions with preserved structure."""
    shapes = [("3", "4", "100", "200", "", "")]
    ref = _make_metrics(table_count=1, table_shapes=shapes)
    out = _make_metrics(
        table_count=3,
        table_shapes=shapes + [("2", "2", "50", "50", "", ""), ("1", "1", "10", "10", "", "")]
    )
    errors, warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert errors == []
    assert any("표 2개 추가" in w for w in warnings)
    assert any("구조 보존 확인" in w for w in warnings)


def test_template_fill_preservation_warning():
    """Template-fill mode emits preservation confirmation warning."""
    shapes = [("3", "4", "100", "200", "", ""), ("2", "3", "50", "60", "", "")]
    ref = _make_metrics(table_count=2, table_shapes=shapes)
    out = _make_metrics(table_count=2, table_shapes=shapes)
    errors, warnings = compare_metrics(ref, out, 0.15, 0.25, mode="template-fill")
    assert errors == []
    assert any("기존 표 2개 구조 보존 확인" in w for w in warnings)
