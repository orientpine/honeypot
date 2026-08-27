# pyright: reportAny=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

# Contract declared by SKILL.md, agents/hwpx-builder.md, commands/hwpx-generate.md;
# block markers (#, -, >) are consumed by the line matchers, so only inline ones remain.
MARKER_PATTERNS = {
    "code span": re.compile(r"`"),
    "strikethrough": re.compile(r"~~"),
    "link syntax": re.compile(r"\[[^\]]*\]\([^)]*\)"),
    "bold": re.compile(r"\*\*"),
}


def load_md_parser_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("md_parser", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _markers_in(text: str) -> list[str]:
    return [name for name, pattern in MARKER_PATTERNS.items() if pattern.search(text)]


def _every_text(block: dict[str, Any]) -> list[str]:
    texts = [str(block.get("text", ""))]
    for segment in block.get("segments") or []:
        texts.append(str(segment.get("text", "")))
    for row in [block.get("headers") or []] + list(block.get("rows") or []):
        texts.extend(str(cell) for cell in row)
    return [text for text in texts if text]


def test_segment_path_leaves_no_inline_marker_in_paragraph_text(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown(
        "본문에 **굵게**와 `인라인코드`, ~~취소선~~, [보고서](https://example.test/r) 가 있다.",
        "inline",
    )

    leaked = {
        text: _markers_in(text)
        for block in parsed["blocks"]
        for text in _every_text(block)
        if _markers_in(text)
    }
    assert not leaked, f"markdown syntax reached the paragraph text: {leaked}"


def test_bullet_and_blockquote_text_carry_no_inline_marker(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown(
        "- 불릿 `코드` 와 ~~지운말~~\n\n> 인용에 [문서](https://example.test/d) 가 있다\n",
        "inline",
    )

    leaked = {
        text: _markers_in(text)
        for block in parsed["blocks"]
        for text in _every_text(block)
        if _markers_in(text)
    }
    assert not leaked, f"markdown syntax reached a bullet or blockquote: {leaked}"


def test_table_cells_carry_no_inline_marker(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown(
        "| 항목 | 설명 |\n| --- | --- |\n"
        "| **굵은셀** | `코드` 와 ~~취소~~ 와 [출처](https://example.test/s) |\n",
        "inline",
    )

    table = next(b for b in parsed["blocks"] if b["type"] == "table")
    leaked = {text: _markers_in(text) for text in _every_text(table) if _markers_in(text)}
    assert not leaked, f"markdown syntax reached a table cell: {leaked}"


def test_stripping_keeps_the_words_and_the_link_target(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown(
        "출처는 `bench.py` 와 ~~구버전~~ 신버전, [보고서](https://example.test/r) 다.",
        "inline",
    )
    text = parsed["blocks"][0]["text"]

    for word in ("bench.py", "구버전", "신버전", "보고서", "https://example.test/r"):
        assert word in text, f"stripping ate content: {word!r} missing from {text!r}"


def test_emphasis_still_becomes_its_own_segment(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown("앞 **굵게** 와 *기울임* 뒤", "inline")
    segments = parsed["blocks"][0]["segments"]

    kinds = {segment["type"]: segment["text"] for segment in segments}
    assert kinds.get("bold") == "굵게", f"bold segment lost: {segments}"
    assert kinds.get("italic") == "기울임", f"italic segment lost: {segments}"


def test_inline_image_is_not_mistaken_for_a_link(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")

    parsed = parser.parse_markdown("앞말 ![도해](img/fig1.png) 뒷말", "inline")
    text = parsed["blocks"][0]["text"]

    assert "!도해" not in text, f"image syntax was half-stripped into prose: {text!r}"
