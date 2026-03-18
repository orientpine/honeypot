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
        "image_placeholder": {"paraPrIDRef": "0", "charPrIDRef": "0"},
        "bullet_auto": [41, 43, 90, 91, 113, 114, 115],
    }


def test_bullet_auto_strips_leading_bullet_prefix(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "segments": [{"type": "plain", "text": "◦ 항목 텍스트"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, sample_styles())

    assert "<hp:t>◦ 항목 텍스트</hp:t>" not in xml
    assert "<hp:t>항목 텍스트</hp:t>" in xml


def test_bullet_prefix_not_stripped_when_style_not_auto_bullet(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    styles = sample_styles()
    styles["bullet_auto"] = []
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "segments": [{"type": "plain", "text": "◦ 항목 텍스트"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, styles)

    assert "<hp:t>◦ 항목 텍스트</hp:t>" in xml
