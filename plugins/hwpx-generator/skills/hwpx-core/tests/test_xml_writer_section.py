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


def sample_parsed_blocks() -> dict:
    return {
        "blocks": [
            {"type": "heading", "level": 1, "text": "제목"},
            {"type": "paragraph", "text": "본문"},
        ]
    }


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
        "page_width": 59528,
        "page_height": 84188,
        "margin_left": 5669,
        "margin_right": 5669,
        "margin_top": 2834,
        "margin_bottom": 4251,
        "margin_header": 4251,
        "margin_footer": 2834,
    }


def test_wrap_section_outputs_hs_sec_root(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")

    xml = writer.build_fragment(
        sample_parsed_blocks(), sample_styles(), wrap_section=True
    )

    assert xml.startswith("<hs:sec ")
    assert "<hs:secPr>" in xml
    assert "</hs:sec>" in xml


def test_wrap_section_includes_page_size_and_margins(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")

    xml = writer.build_fragment(
        sample_parsed_blocks(), sample_styles(), wrap_section=True
    )

    assert '<hs:pageSize width="59528" height="84188" orientation="PORTRAIT"/>' in xml
    assert (
        '<hs:pageMargin left="5669" right="5669" top="2834" bottom="4251" '
        'header="4251" footer="2834" gutter="0"/>' in xml
    )


def test_wrap_section_root_has_all_required_namespaces(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")

    xml = writer.build_fragment(
        sample_parsed_blocks(), sample_styles(), wrap_section=True
    )

    assert 'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"' in xml
    assert 'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"' in xml
    assert 'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"' in xml
    assert 'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"' in xml


def test_without_wrap_section_keeps_hwpx_fragment_root(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")

    xml = writer.build_fragment(
        sample_parsed_blocks(), sample_styles(), wrap_section=False
    )

    assert xml.startswith("<hwpx-fragment ")
    assert "<hs:secPr>" not in xml
    assert "<hs:sec " not in xml
