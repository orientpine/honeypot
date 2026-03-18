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


def extract_image_refs(blocks):
    return [block for block in blocks if block.get("type") == "image_ref"]


def test_parse_images_in_chapter3_markdown(project_root, scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md_path = project_root / "dev" / "3장.md"
    parsed = parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    image_blocks = extract_image_refs(parsed["blocks"])

    assert len(image_blocks) == 3
    assert [block["caption_id"] for block in image_blocks] == ["3-1", "3-2", "3-3"]

    for block in image_blocks:
        assert block["type"] == "image_ref"
        assert block["id"] is None
        assert isinstance(block["path"], str) and block["path"].startswith("./images/")
        assert isinstance(block["alt"], str)
        assert isinstance(block["caption"], str) and block["caption"]
        assert isinstance(block["caption_id"], str)
        assert block["filename"] == Path(block["path"]).name


def test_parse_images_in_chapter4_markdown(project_root, scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    md_path = project_root / "dev" / "4장.md"
    parsed = parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    image_blocks = extract_image_refs(parsed["blocks"])

    assert len(image_blocks) == 12
    assert [block["caption_id"] for block in image_blocks] == [
        f"4-{i}" for i in range(1, 13)
    ]

    for block in image_blocks:
        assert block["type"] == "image_ref"
        assert block["id"] is None
        assert isinstance(block["path"], str) and block["path"].startswith("./images/")
        assert isinstance(block["alt"], str)
        assert isinstance(block["caption"], str) and block["caption"]
        assert isinstance(block["caption_id"], str)
        assert block["filename"] == Path(block["path"]).name


def test_legacy_image_ref_format_is_still_supported(scripts_dir):
    parser = load_md_parser_module(scripts_dir / "md_parser.py")
    parsed = parser.parse_markdown("<그림 9-1: 기존 포맷 캡션>", "inline")
    image_blocks = extract_image_refs(parsed["blocks"])

    assert len(image_blocks) == 1
    assert image_blocks[0] == {
        "type": "image_ref",
        "id": "9-1",
        "caption": "기존 포맷 캡션",
    }
