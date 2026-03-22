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


def test_bullet_multiline_continuation(scripts_dir):
    """Bullet text spanning multiple lines should be joined into one bullet."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "◦ LiDAR, 카메라, GPS 센서 등의\n멀티모달 센서 데이터를 수집"
    parsed = parser.parse_markdown(md, "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "bullet"
    assert block["marker"] == "◦"
    assert "카메라" in block["text"]
    assert "수집" in block["text"]
    # Continuation line joined with space
    assert "등의 멀티모달" in block["text"]


def test_bullet_multiline_stops_at_next_bullet(scripts_dir):
    """Continuation stops when a new bullet starts."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "◦ 첫 번째 항목\n계속되는 내용\n◦ 두 번째 항목"
    parsed = parser.parse_markdown(md, "inline")

    blocks = parsed["blocks"]
    assert len(blocks) == 2
    assert blocks[0]["type"] == "bullet"
    assert "계속되는 내용" in blocks[0]["text"]
    assert blocks[1]["type"] == "bullet"
    assert blocks[1]["text"] == "두 번째 항목"


def test_bullet_multiline_stops_at_blank(scripts_dir):
    """Continuation stops at a blank line."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "◦ 첫 번째 항목\n계속\n\n다음 문단"
    parsed = parser.parse_markdown(md, "inline")

    blocks = parsed["blocks"]
    assert len(blocks) == 2
    assert blocks[0]["type"] == "bullet"
    assert "계속" in blocks[0]["text"]
    assert blocks[1]["type"] == "paragraph"
    assert blocks[1]["text"] == "다음 문단"


def test_blockquote_multiline_continuation(scripts_dir):
    """Blockquote text spanning multiple lines should be joined."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "> 연구 결과를 종합하면\n전체적인 성능이 향상되었다"
    parsed = parser.parse_markdown(md, "inline")

    assert len(parsed["blocks"]) == 1
    block = parsed["blocks"][0]
    assert block["type"] == "blockquote"
    assert "종합하면 전체적인" in block["text"]


def test_blockquote_multiline_stops_at_heading(scripts_dir):
    """Blockquote continuation stops at a heading."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "> 인용문 내용\n계속 이어지는 인용\n## 다음 섹션"
    parsed = parser.parse_markdown(md, "inline")

    blocks = parsed["blocks"]
    assert len(blocks) == 2
    assert blocks[0]["type"] == "blockquote"
    assert "계속 이어지는 인용" in blocks[0]["text"]
    assert blocks[1]["type"] == "heading"


def test_bullet_korean_text_not_truncated(scripts_dir):
    """Regression: Korean text like 카메라 must not be truncated to 카메."""
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md = "◦ LiDAR, 카메라, GPS 센서를 활용한 멀티모달 인지 기술"
    parsed = parser.parse_markdown(md, "inline")

    block = parsed["blocks"][0]
    assert block["type"] == "bullet"
    assert "카메라" in block["text"]
    assert block["text"].endswith("인지 기술")
