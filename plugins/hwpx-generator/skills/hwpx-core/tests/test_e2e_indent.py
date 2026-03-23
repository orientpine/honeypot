from __future__ import annotations

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportAny=false, reportExplicitAny=false, reportUnusedCallResult=false

import importlib.util
import re
import zipfile
from pathlib import Path
from typing import Any, cast

import pytest


pytestmark = pytest.mark.integration


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_left_margins(xml_str: str) -> list[int]:
    return [int(v) for v in re.findall(r'leftMargin="(\d+)"', xml_str)]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_style_map_from_hwpx(
    analyze_template_mod: Any, hwpx_path: Path, tmp_path: Path
) -> dict[str, object]:
    extract_dir = tmp_path / "analyze_extract"
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        zf.extract("Contents/header.xml", path=extract_dir)
        zf.extract("Contents/section0.xml", path=extract_dir)

    header_path = extract_dir / "Contents" / "header.xml"
    section_path = extract_dir / "Contents" / "section0.xml"
    header_root = analyze_template_mod.etree.parse(str(header_path)).getroot()
    section_root = analyze_template_mod.etree.parse(str(section_path)).getroot()
    return analyze_template_mod.extract_style_map(header_root, section_root)


def test_md_parser_produces_indent_level_on_5jang(scripts_dir, project_root):
    md_parser = load_module("md_parser", scripts_dir / "md_parser.py")
    md_path = project_root / "dev" / "hwpx_indent" / "5장.md"

    parsed = md_parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    blocks = parsed.get("blocks", [])
    bullets = [b for b in blocks if isinstance(b, dict) and b.get("type") == "bullet"]

    assert bullets, "Expected bullet blocks in 5장.md"
    assert all("indent_level" in b for b in bullets), (
        "All bullets must include indent_level"
    )

    levels = {
        int(b["indent_level"]) for b in bullets if b.get("indent_level") is not None
    }
    assert len(levels) >= 2, (
        f"Expected >=2 distinct indent levels, got {sorted(levels)}"
    )


def test_xml_writer_indent_levels_produce_different_margins(scripts_dir):
    xml_writer = load_module("xml_writer", scripts_dir / "xml_writer.py")

    parsed = {
        "blocks": [
            {"type": "bullet", "text": "level0", "indent_level": 0, "marker": "-"},
            {"type": "bullet", "text": "level1", "indent_level": 1, "marker": "-"},
        ]
    }
    style_config = {
        "heading_1": {"paraPrIDRef": "1", "charPrIDRef": "1"},
        "heading_2": {"paraPrIDRef": "1", "charPrIDRef": "1"},
        "heading_3": {"paraPrIDRef": "1", "charPrIDRef": "1"},
        "heading_4": {"paraPrIDRef": "1", "charPrIDRef": "1"},
        "body": {"paraPrIDRef": "1", "charPrIDRef": "1"},
        "bullet": {
            "paraPrIDRef": "2",
            "charPrIDRef": "1",
            "left_margin": 1200,
            "indent": -300,
        },
        "bullet_level_0": {
            "paraPrIDRef": "2",
            "charPrIDRef": "1",
            "left_margin": 1200,
            "indent": -300,
        },
        "bullet_level_1": {
            "paraPrIDRef": "3",
            "charPrIDRef": "1",
            "left_margin": 2000,
            "indent": -300,
        },
        "bold": {"charPrIDRef": "1"},
        "table_header": {
            "charPrIDRef": "1",
            "paraPrIDRef": "1",
            "borderFillIDRef": "1",
        },
        "table_cell": {"charPrIDRef": "1", "paraPrIDRef": "1", "borderFillIDRef": "1"},
        "table_width": 40000,
        "image_placeholder": {"paraPrIDRef": "1", "charPrIDRef": "1"},
    }

    xml_str = xml_writer.build_fragment(parsed, style_config)
    margins = _extract_left_margins(xml_str)

    assert margins, "Expected leftMargin attributes in xml output"
    assert len(set(margins)) >= 2, (
        f"Expected >=2 distinct leftMargin values, got {sorted(set(margins))}"
    )


def test_analyze_template_extracts_bullet_levels_from_real_hwpx(
    scripts_dir, project_root, tmp_path
):
    analyze_template = load_module(
        "analyze_template", scripts_dir / "analyze_template.py"
    )
    hwpx_path = project_root / "dev" / "hwpx_indent" / "제안서_최종_포맷완료_v6.hwpx"

    style_map = _extract_style_map_from_hwpx(analyze_template, hwpx_path, tmp_path)
    assert "bullet_level_0" in style_map
    assert "bullet_level_1" in style_map

    level0 = cast(dict[str, object], style_map["bullet_level_0"])
    level1 = cast(dict[str, object], style_map["bullet_level_1"])
    lm0 = _safe_int(level0.get("left_margin", 0))
    lm1 = _safe_int(level1.get("left_margin", 0))
    assert lm0 <= lm1, f"Expected monotone increasing left_margin, got {lm0} > {lm1}"


def test_md_merger_produces_separator_between_files(scripts_dir, tmp_path):
    md_merger = load_module("md_merger", scripts_dir / "md_merger.py")

    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("# A\n\n- item\n", encoding="utf-8")
    f2.write_text("# B\n\n- item\n", encoding="utf-8")

    merged = md_merger.merge_markdown_files([str(f1), str(f2)], target_level=2)
    blocks = merged.get("blocks", [])

    assert any(isinstance(b, dict) and b.get("type") == "separator" for b in blocks)
    heading_levels = [
        int(level)
        for b in blocks
        if isinstance(b, dict)
        and b.get("type") == "heading"
        and isinstance((level := b.get("level")), int)
    ]
    assert heading_levels, "Expected heading blocks in merged output"
    assert min(heading_levels) == 2, (
        f"Expected heading offset to target_level=2, got {heading_levels}"
    )


def test_full_pipeline_indent_preserved(scripts_dir, project_root, tmp_path):
    analyze_template = load_module(
        "analyze_template", scripts_dir / "analyze_template.py"
    )
    md_parser = load_module("md_parser", scripts_dir / "md_parser.py")
    xml_writer = load_module("xml_writer", scripts_dir / "xml_writer.py")

    hwpx_path = project_root / "dev" / "hwpx_indent" / "제안서_최종_포맷완료_v6.hwpx"
    md_path = project_root / "dev" / "hwpx_indent" / "5장.md"

    style_map = _extract_style_map_from_hwpx(analyze_template, hwpx_path, tmp_path)
    parsed = md_parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    xml_str = xml_writer.build_fragment(parsed, style_map)

    margins = _extract_left_margins(xml_str)
    assert margins, "Expected leftMargin attributes in full-pipeline xml output"
    assert len(set(margins)) >= 2, (
        "Expected different leftMargin values for different indent levels"
    )
    assert "lxml" not in xml_str
    assert "xml.etree.ElementTree" not in xml_str
