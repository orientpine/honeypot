from __future__ import annotations

import importlib.util
from pathlib import Path


def load_xml_writer_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("xml_writer", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_styles() -> dict:
    return {
        "heading_1": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "heading_2": {"charPrIDRef": "49", "paraPrIDRef": "39"},
        "body": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "bullet": {
            "charPrIDRef": "36",
            "paraPrIDRef": "91",
            "left_margin": 0,
            "indent": -1584,
        },
        "bold": {"charPrIDRef": "48"},
        "table_header": {
            "charPrIDRef": "95",
            "paraPrIDRef": "71",
            "borderFillIDRef": "45",
        },
        "table_cell": {
            "charPrIDRef": "136",
            "paraPrIDRef": "98",
            "borderFillIDRef": "42",
        },
        "table_width": 42520,
        "image_placeholder": {"paraPrIDRef": "4", "charPrIDRef": "0"},
        "image_caption": {"paraPrIDRef": "118", "charPrIDRef": "121"},
        "page_width": 59528,
        "margin_left": 5669,
        "margin_right": 5669,
    }


def sample_image_block() -> dict:
    return {
        "type": "image_ref",
        "path": "./images/01_비전_개념도.png",
        "alt": "alt",
        "caption": "caption text",
        "caption_id": "3-1",
        "filename": "01_비전_개념도.png",
        "placeholder": True,
    }


def test_build_image_with_caption_contains_hp_pic(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    xml = writer.build_image_with_caption(
        sample_image_block(), sample_styles(), image_idx=1
    )
    assert "<hp:pic" in xml
    assert 'embeddingFile="image1"' in xml


def test_build_image_with_caption_contains_caption_prefix(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    xml = writer.build_image_with_caption(
        sample_image_block(), sample_styles(), image_idx=1
    )
    assert "그림 3-1: caption text" in xml


def test_build_image_with_caption_uses_image_caption_style_ids(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    xml = writer.build_image_with_caption(
        sample_image_block(), sample_styles(), image_idx=1
    )
    assert '<hp:para paraPrIDRef="118" hp:align="CENTER">' in xml
    assert '<hp:run charPrIDRef="121">' in xml
