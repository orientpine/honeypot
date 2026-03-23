from __future__ import annotations
# pyright: basic

import importlib.util
import re
from pathlib import Path


def load_xml_writer_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("xml_writer", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def style_config_with_indent_levels() -> dict:
    return {
        "heading_1": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "heading_2": {"charPrIDRef": "49", "paraPrIDRef": "39"},
        "heading_3": {"charPrIDRef": "49", "paraPrIDRef": "39"},
        "heading_4": {"charPrIDRef": "49", "paraPrIDRef": "39"},
        "body": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "bullet": {
            "charPrIDRef": "36",
            "paraPrIDRef": "91",
            "left_margin": 0,
            "indent": -1584,
        },
        "bullet_level_0": {"paraPrIDRef": "5", "charPrIDRef": "2", "left_margin": 800},
        "bullet_level_1": {"paraPrIDRef": "6", "charPrIDRef": "2", "left_margin": 1600},
        "bullet_level_2": {"paraPrIDRef": "7", "charPrIDRef": "2", "left_margin": 2400},
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


def _left_margins(xml: str) -> list[int]:
    return [int(v) for v in re.findall(r'leftMargin="(\d+)"', xml)]


def test_indent_level_0_uses_bullet_level_0_parapr_idref(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 0,
                "segments": [{"type": "plain", "text": "레벨 0 항목"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert 'paraPrIDRef="5"' in xml


def test_indent_level_1_left_margin_is_larger_than_level_0(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 0,
                "segments": [{"type": "plain", "text": "레벨 0"}],
            },
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 1,
                "segments": [{"type": "plain", "text": "레벨 1"}],
            },
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())
    margins = _left_margins(xml)

    assert len(margins) >= 2
    assert margins[1] > margins[0]


def test_indent_level_2_left_margin_is_larger_than_level_1(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 0,
                "segments": [{"type": "plain", "text": "레벨 0"}],
            },
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 1,
                "segments": [{"type": "plain", "text": "레벨 1"}],
            },
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 2,
                "segments": [{"type": "plain", "text": "레벨 2"}],
            },
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())
    margins = _left_margins(xml)

    assert len(margins) >= 3
    assert margins[2] > margins[1]


def test_indent_level_3_fallback_uses_level_2_plus_hwpunit_per_level(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 3,
                "segments": [{"type": "plain", "text": "레벨 3"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert 'leftMargin="3200"' in xml


def test_numbered_item_uses_build_numbered_and_emits_number_marker(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "numbered_item",
                "segments": [{"type": "plain", "text": "번호 목록 항목"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert re.search(r"<hp:t>\s*1[\.|\)]\s*</hp:t>", xml) is not None


def test_backward_compat_bullet_without_indent_level_behaves_like_level_0(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "segments": [{"type": "plain", "text": "기본 불릿"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert 'paraPrIDRef="5"' in xml


def test_backward_compat_existing_bullet_dict_without_indent_level_no_crash(
    scripts_dir,
):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "-",
                "text": "foo",
                "segments": [{"type": "plain", "text": "foo"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert "<hp:p" in xml
    assert 'paraPrIDRef="5"' in xml


def test_bullet_level_0_style_config_values_are_reflected_in_xml(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "bullet",
                "marker": "◦",
                "indent_level": 0,
                "segments": [{"type": "plain", "text": "스타일 매핑 확인"}],
            }
        ]
    }

    xml = writer.build_fragment(parsed, style_config_with_indent_levels())

    assert 'paraPrIDRef="5"' in xml
    assert 'leftMargin="800"' in xml
    assert 'charPrIDRef="2"' in xml
