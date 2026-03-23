from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


def load_analyzer_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("analyze_template", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_style_map_from_hwpx(analyzer, hwpx_path: Path):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            zf.extractall(tmpdir)

        header_path = Path(tmpdir) / "Contents" / "header.xml"
        section_path = Path(tmpdir) / "Contents" / "section0.xml"

        header_root = ET.parse(header_path).getroot()
        section_root = ET.parse(section_path).getroot()
        return analyzer.extract_style_map(header_root, section_root)


def _load_style_map_for_proposal(scripts_dir, project_root):
    analyzer = load_analyzer_module(scripts_dir / "analyze_template.py")
    hwpx_path = project_root / "dev" / "hwpx_indent" / "제안서_최종_포맷완료_v6.hwpx"
    assert hwpx_path.exists(), f"Missing HWPX fixture: {hwpx_path}"
    return extract_style_map_from_hwpx(analyzer, hwpx_path)


def test_extract_style_map_has_bullet_level_0_key(scripts_dir, project_root):
    style_map = _load_style_map_for_proposal(scripts_dir, project_root)
    assert "bullet_level_0" in style_map


def test_extract_style_map_has_bullet_level_1_key(scripts_dir, project_root):
    style_map = _load_style_map_for_proposal(scripts_dir, project_root)
    assert "bullet_level_1" in style_map


def test_bullet_levels_have_left_margin_and_increase(scripts_dir, project_root):
    style_map = _load_style_map_for_proposal(scripts_dir, project_root)

    level_0 = style_map["bullet_level_0"]
    level_1 = style_map["bullet_level_1"]

    assert "left_margin" in level_0
    assert "left_margin" in level_1
    assert level_1["left_margin"] > level_0["left_margin"]


def test_bullet_levels_have_paraPrIDRef(scripts_dir, project_root):
    style_map = _load_style_map_for_proposal(scripts_dir, project_root)

    assert "paraPrIDRef" in style_map["bullet_level_0"]
    assert "paraPrIDRef" in style_map["bullet_level_1"]


def test_existing_keys_preserved_and_detects_at_least_two_bullet_levels(
    scripts_dir, project_root
):
    style_map = _load_style_map_for_proposal(scripts_dir, project_root)

    assert "bullet" in style_map
    assert "heading_1" in style_map
    assert "body" in style_map

    bullet_level_keys = [k for k in style_map if k.startswith("bullet_level_")]
    assert len(bullet_level_keys) >= 2
