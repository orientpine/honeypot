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


def test_build_fragment_caption_markdown_format(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "image_ref",
                "path": "./images/01.png",
                "caption": "비전 개념도",
                "caption_id": "3-1",
                "filename": "01.png",
            }
        ]
    }
    xml = writer.build_fragment(parsed, sample_styles())
    assert "그림 3-1: 비전 개념도" in xml
    assert "<hp:p " in xml  # paragraph_from_segments가 생성하는 태그
    assert "<!--IMAGE:image1-->" in xml  # 플레이스홀더도 반드시 존재


def test_build_fragment_caption_legacy_format(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "image_ref",
                "id": "3-1",
                "caption": "비전 개념도",
                # caption_id 키 없음 — Legacy 형식
            }
        ]
    }
    xml = writer.build_fragment(parsed, sample_styles())
    assert "그림 3-1: 비전 개념도" in xml


def test_build_fragment_caption_empty_skip(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "image_ref",
                "path": "./images/01.png",
                "caption": "",
                "caption_id": None,
                "id": None,
            }
        ]
    }
    xml = writer.build_fragment(parsed, sample_styles())
    assert "<!--IMAGE:image1-->" in xml  # 플레이스홀더는 존재
    assert "그림" not in xml  # 캡션 문단 없음


def test_build_fragment_caption_xml_escape(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "image_ref",
                "path": "./images/01.png",
                "caption": "A & B <=> C",
                "caption_id": "3-1",
                "filename": "01.png",
            }
        ]
    }
    xml = writer.build_fragment(parsed, sample_styles())
    assert "&amp;" in xml
    assert "&lt;" in xml
    assert "&gt;" in xml
    assert "A & B" not in xml  # 이스케이프 안 된 원본 없음
