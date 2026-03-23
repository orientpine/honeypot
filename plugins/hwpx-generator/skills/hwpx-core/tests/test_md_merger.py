from __future__ import annotations

# pyright: reportMissingImports=false, reportOptionalMemberAccess=false

import importlib.util
from pathlib import Path

import pytest


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_md_merger_or_fail(scripts_dir):
    script_path = scripts_dir / "md_merger.py"
    try:
        return load_module("md_merger", script_path)
    except FileNotFoundError as exc:
        pytest.fail(f"md_merger.py not found (expected RED): {exc}")
    except ImportError as exc:
        pytest.fail(f"md_merger import failed (expected RED): {exc}")


@pytest.fixture
def md_parser_module(scripts_dir):
    return load_module("md_parser", scripts_dir / "md_parser.py")


def write_md(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_single_file_output_unchanged(scripts_dir, md_parser_module, tmp_path):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    md = "# 제목\n\n본문 문단\n\n## 하위 제목\n\n- 항목 A"
    file1 = write_md(tmp_path, "single.md", md)

    expected = md_parser_module.parse_markdown(md, str(file1))
    result = md_merger_module.merge_markdown_files([str(file1)], target_level=1)

    assert result == expected


def test_two_files_h1_to_target_level2_offsets_first_file_headings(
    scripts_dir, tmp_path
):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    file1 = write_md(tmp_path, "first.md", "# 첫 파일\n\n## 첫 파일 하위")
    file2 = write_md(tmp_path, "second.md", "# 두 번째 파일\n\n본문")

    merged = md_merger_module.merge_markdown_files(
        [str(file1), str(file2)], target_level=2
    )
    headings = [b for b in merged["blocks"] if b.get("type") == "heading"]

    assert headings[0]["text"] == "첫 파일"
    assert headings[0]["level"] == 2
    assert headings[1]["text"] == "첫 파일 하위"
    assert headings[1]["level"] == 3


def test_two_files_have_separator_block_between_results(scripts_dir, tmp_path):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    file1 = write_md(tmp_path, "a.md", "# A")
    file2 = write_md(tmp_path, "b.md", "# B")

    merged = md_merger_module.merge_markdown_files(
        [str(file1), str(file2)], target_level=1
    )

    assert {"type": "separator"} in merged["blocks"]


def test_empty_file_is_skipped_without_error(scripts_dir, tmp_path):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    empty_file = write_md(tmp_path, "empty.md", "\n\n")
    file2 = write_md(tmp_path, "nonempty.md", "# 유효 제목\n\n본문")

    merged = md_merger_module.merge_markdown_files(
        [str(empty_file), str(file2)], target_level=1
    )
    blocks = merged["blocks"]

    assert any(
        b.get("type") == "heading" and b.get("text") == "유효 제목" for b in blocks
    )
    assert all(b.get("type") != "separator" for b in blocks)


def test_body_only_markdown_merges_as_paragraph_blocks(scripts_dir, tmp_path):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    file1 = write_md(tmp_path, "body1.md", "첫 번째 문단만 있음")
    file2 = write_md(tmp_path, "body2.md", "둘째 파일도 본문만 있음")

    merged = md_merger_module.merge_markdown_files(
        [str(file1), str(file2)], target_level=1
    )
    paragraphs = [b for b in merged["blocks"] if b.get("type") == "paragraph"]

    assert len(paragraphs) >= 2
    assert any("첫 번째" in p.get("text", "") for p in paragraphs)
    assert any("둘째 파일" in p.get("text", "") for p in paragraphs)


def test_list_indent_level_not_changed_during_merge(
    scripts_dir, md_parser_module, tmp_path
):
    md_merger_module = load_md_merger_or_fail(scripts_dir)
    content = "- 상위 항목\n  - 하위 항목\n1. 번호 항목\n   1. 번호 하위 항목"
    file1 = write_md(tmp_path, "list.md", content)

    parsed = md_parser_module.parse_markdown(content, str(file1))
    merged = md_merger_module.merge_markdown_files([str(file1)], target_level=1)

    parsed_lists = [
        b
        for b in parsed["blocks"]
        if b.get("type") in {"bullet", "numbered", "numbered_list"}
    ]
    merged_lists = [
        b
        for b in merged["blocks"]
        if b.get("type") in {"bullet", "numbered", "numbered_list"}
    ]

    assert len(parsed_lists) == len(merged_lists)
    for before, after in zip(parsed_lists, merged_lists):
        assert before.get("marker") == after.get("marker")
        assert before.get("text") == after.get("text")
        assert before.get("segments") == after.get("segments")
        assert before.get("indent_level") == after.get("indent_level")
