# pyright: reportAny=false
import importlib
import sys
import warnings
from pathlib import Path
from typing import Callable


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _section_transplant_module():
    return importlib.import_module("section_transplant")


def _require_symbol(name: str):
    module = _section_transplant_module()
    try:
        return getattr(module, name)
    except AttributeError as exc:
        raise ImportError(
            f"cannot import name '{name}' from 'section_transplant'"
        ) from exc


def test_parse_header_styles_extracts_char_styles(
    make_header_xml: Callable[..., bytes],
):
    parse_header_styles = _section_transplant_module().parse_header_styles

    header_bytes = make_header_xml(
        char_styles=[(1, 1500, True), (2, 1000, False)],
        para_styles=[(10, "JUSTIFY"), (20, "CENTER")],
    )
    style_map = parse_header_styles(header_bytes)

    assert "1" in style_map.char_styles
    assert style_map.char_styles["1"].font_size == 1500
    assert style_map.char_styles["1"].bold is True
    assert "2" in style_map.char_styles
    assert style_map.char_styles["2"].font_size == 1000
    assert style_map.char_styles["2"].bold is False


def test_parse_header_styles_extracts_para_styles(
    make_header_xml: Callable[..., bytes],
):
    parse_header_styles = _section_transplant_module().parse_header_styles

    header_bytes = make_header_xml(
        char_styles=[(1, 1500, True)],
        para_styles=[(10, "JUSTIFY"), (20, "CENTER")],
    )
    style_map = parse_header_styles(header_bytes)

    assert "10" in style_map.para_styles
    assert style_map.para_styles["10"].align == "JUSTIFY"
    assert "20" in style_map.para_styles
    assert style_map.para_styles["20"].align == "CENTER"


def test_build_mapping_matches_by_font_size_and_bold(
    make_header_xml: Callable[..., bytes],
):
    module = _section_transplant_module()
    build_style_mapping = module.build_style_mapping
    parse_header_styles = module.parse_header_styles

    source_header = make_header_xml(
        char_styles=[(45, 1500, True), (46, 1000, False)],
        para_styles=[(34, "JUSTIFY")],
    )
    target_header = make_header_xml(
        char_styles=[(48, 1500, True), (49, 1000, False)],
        para_styles=[(38, "JUSTIFY")],
    )

    source_styles = parse_header_styles(source_header)
    target_styles = parse_header_styles(target_header)
    mapping = build_style_mapping(source_styles, target_styles)

    assert mapping["charPrIDRef"]["45"] == "48"
    assert mapping["charPrIDRef"]["46"] == "49"
    assert mapping["paraPrIDRef"]["34"] == "38"


def test_id_zero_excluded_from_remapping(
    make_header_xml: Callable[..., bytes],
):
    module = _section_transplant_module()
    build_style_mapping = module.build_style_mapping
    parse_header_styles = module.parse_header_styles

    source_header = make_header_xml(
        char_styles=[(1, 1500, True)], para_styles=[(10, "JUSTIFY")]
    )
    target_header = make_header_xml(
        char_styles=[(5, 1500, True)], para_styles=[(15, "JUSTIFY")]
    )

    source_styles = parse_header_styles(source_header)
    target_styles = parse_header_styles(target_header)
    mapping = build_style_mapping(source_styles, target_styles)

    assert mapping["charPrIDRef"]["0"] == "0"
    assert mapping["paraPrIDRef"]["0"] == "0"
    assert mapping["borderFillIDRef"]["0"] == "0"
    assert mapping["styleIDRef"]["0"] == "0"


def test_unmatched_style_keeps_original_with_warning(
    make_header_xml: Callable[..., bytes],
):
    module = _section_transplant_module()
    build_style_mapping = module.build_style_mapping
    parse_header_styles = module.parse_header_styles

    source_header = make_header_xml(
        char_styles=[(99, 2000, True)],
        para_styles=[(88, "JUSTIFY")],
    )
    target_header = make_header_xml(
        char_styles=[(10, 1000, False)],
        para_styles=[(20, "JUSTIFY")],
    )

    source_styles = parse_header_styles(source_header)
    target_styles = parse_header_styles(target_header)

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        mapping = build_style_mapping(source_styles, target_styles)
        assert len(warning_list) >= 1

    assert mapping["charPrIDRef"]["99"] == "99"


def test_remap_style_ids_attribute_scoped():
    remap_style_ids = _require_symbol("remap_style_ids")

    xml = '<hp:p paraPrIDRef="34"><hp:run charPrIDRef="45"><hp:t>45명의 연구원</hp:t></hp:run></hp:p>'
    mapping = {
        "charPrIDRef": {"45": "48", "0": "0"},
        "paraPrIDRef": {"34": "38", "0": "0"},
        "borderFillIDRef": {"0": "0"},
        "styleIDRef": {"0": "0"},
    }

    result = remap_style_ids(xml, mapping)
    assert 'charPrIDRef="48"' in result
    assert 'paraPrIDRef="38"' in result
    assert "45명의 연구원" in result


def test_remap_id_zero_not_changed():
    remap_style_ids = _require_symbol("remap_style_ids")

    xml = '<hp:p paraPrIDRef="0"><hp:run charPrIDRef="0"><hp:t>text</hp:t></hp:run></hp:p>'
    mapping = {
        "charPrIDRef": {"0": "0"},
        "paraPrIDRef": {"0": "0"},
        "borderFillIDRef": {"0": "0"},
        "styleIDRef": {"0": "0"},
    }
    result = remap_style_ids(xml, mapping)
    assert 'charPrIDRef="0"' in result
    assert 'paraPrIDRef="0"' in result
