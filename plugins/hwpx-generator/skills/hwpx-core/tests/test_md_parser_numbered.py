# pyright: reportAny=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false
from __future__ import annotations

import importlib.util
from pathlib import Path


def load_md_parser_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("md_parser", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_numbered_decimal_parses_as_numbered_item(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("1. 첫 번째 항목", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "1"
    assert block["indent_level"] == 0
    assert block["text"] == "첫 번째 항목"


def test_numbered_decimal_with_two_space_indent_is_level_one(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("  1. 들여쓴 번호 항목", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "1"
    assert block["indent_level"] == 1
    assert block["text"] == "들여쓴 번호 항목"


def test_numbered_alpha_marker_parses_as_numbered_item(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("a. 영문 번호 항목", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "a"
    assert block["indent_level"] == 0
    assert block["text"] == "영문 번호 항목"


def test_numbered_parenthesized_marker_parses_as_numbered_item(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("(1) 괄호 번호 항목", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "(1)"
    assert block["indent_level"] == 0
    assert block["text"] == "괄호 번호 항목"


def test_numbered_korean_circle_number_parses_as_numbered_item(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("① 원문자 번호 항목", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "①"
    assert block["indent_level"] == 0
    assert block["text"] == "원문자 번호 항목"


def test_mixed_numbered_and_bullet_blocks_parse_together(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "1. 번호 리스트\n- 불릿 리스트"
    parsed = parser.parse_markdown(md, "inline")

    assert len(parsed["blocks"]) == 2
    numbered = parsed["blocks"][0]
    bullet = parsed["blocks"][1]

    assert numbered["type"] == "numbered_item"
    assert numbered["number"] == "1"
    assert numbered["indent_level"] == 0
    assert numbered["text"] == "번호 리스트"

    assert bullet["type"] == "bullet"
    assert bullet["marker"] == "-"
    assert bullet["text"] == "불릿 리스트"


def test_numbered_item_strips_marker_and_keeps_remaining_text(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("2. [중요] 데이터 100건", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "numbered_item"
    assert block["number"] == "2"
    assert block["indent_level"] == 0
    assert block["text"] == "[중요] 데이터 100건"
