from __future__ import annotations

import importlib.util
import re
from pathlib import Path


def load_md_parser_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("md_parser", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blockquote_preserves_inline_bold_segments(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("> **목표**: 하드웨어 독립 인지 모델", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "blockquote"
    assert block["text"] == "목표: 하드웨어 독립 인지 모델"
    assert block["segments"] == [
        {"type": "bold", "text": "목표"},
        {"type": "plain", "text": ": 하드웨어 독립 인지 모델"},
    ]


def test_heading_level4_keeps_circle_number_token(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("#### (1) 연구 목표", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "heading"
    assert block["level"] == 4
    assert block["text"] == "(1) 연구 목표"
    assert block["segments"] == [{"type": "plain", "text": "(1) 연구 목표"}]


def test_standalone_bold_bracket_line_becomes_bold_label(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("**[재난 분야]**", "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block == {
        "type": "bold_label",
        "text": "[재난 분야]",
        "segments": [{"type": "bold", "text": "[재난 분야]"}],
    }


def test_parse_chapter4_complex_patterns(project_root, scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md_path = project_root / "dev" / "4장.md"
    parsed = parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    blocks = parsed["blocks"]

    blockquotes = [b for b in blocks if b.get("type") == "blockquote"]
    bold_labels = [b for b in blocks if b.get("type") == "bold_label"]
    separators = [b for b in blocks if b.get("type") == "separator"]
    h4_headings = [
        b
        for b in blocks
        if b.get("type") == "heading"
        and b.get("level") == 4
        and isinstance(b.get("text"), str)
    ]
    circle_h4 = [
        b for b in h4_headings if re.match(r"^(?:\([0-9]+\)|[①-⑳])", b["text"].strip())
    ]

    assert len(blockquotes) >= 4
    assert len(bold_labels) >= 6
    assert len(circle_h4) >= 1
    assert len(separators) >= 4
