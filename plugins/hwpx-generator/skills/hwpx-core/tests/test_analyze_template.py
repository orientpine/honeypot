from __future__ import annotations

import importlib.util
from pathlib import Path

import lxml.etree as etree


def load_analyzer_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("analyze_template", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_style_map_detects_image_caption_and_bullet_auto(scripts_dir):
    analyzer = load_analyzer_module(scripts_dir / "analyze_template.py")

    header_xml = """
    <hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
      <hh:refList>
        <hh:charPr id="36" height="1000" />
        <hh:charPr id="48" height="1500"><hh:bold/></hh:charPr>
        <hh:charPr id="49" height="1300" />
        <hh:charPr id="121" height="1000" />
        <hh:paraPr id="4" />
        <hh:paraPr id="38" />
        <hh:paraPr id="39" />
        <hh:paraPr id="41"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="43"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="90"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="91"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="113"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="114"><hh:heading type="BULLET"/></hh:paraPr>
        <hh:paraPr id="115"><hh:heading type="BULLET"/></hh:paraPr>
      </hh:refList>
      <hh:style id="1" name="본문" engName="Body" type="PARA" paraPrIDRef="38" charPrIDRef="48"/>
      <hh:style id="2" name="개요 1" engName="Outline 1" type="PARA" paraPrIDRef="38" charPrIDRef="48"/>
      <hh:style id="3" name="개요 2" engName="Outline 2" type="PARA" paraPrIDRef="39" charPrIDRef="49"/>
    </hh:head>
    """.strip()

    section_xml = """
    <hs:section xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
      <hs:sec>
        <hp:p paraPrIDRef="4">
          <hp:run charPrIDRef="48"><hp:pic id="1"/></hp:run>
        </hp:p>
        <hp:p paraPrIDRef="118">
          <hp:run charPrIDRef="121"><hp:t>그림 3-1 캡션</hp:t></hp:run>
        </hp:p>
        <hp:p paraPrIDRef="38">
          <hp:run charPrIDRef="48"><hp:t>제목</hp:t></hp:run>
        </hp:p>
        <hp:p paraPrIDRef="39">
          <hp:run charPrIDRef="49"><hp:t>소제목</hp:t></hp:run>
        </hp:p>
        <hp:p paraPrIDRef="91">
          <hp:run charPrIDRef="36"><hp:t>▪ 항목</hp:t></hp:run>
        </hp:p>
      </hs:sec>
    </hs:section>
    """.strip()

    style_map = analyzer.extract_style_map(
        etree.fromstring(header_xml.encode("utf-8")),
        etree.fromstring(section_xml.encode("utf-8")),
    )

    assert style_map["image_caption"] == {
        "paraPrIDRef": "118",
        "charPrIDRef": "121",
        "confidence": "confirmed",
    }
    assert style_map["bullet_auto"] == [41, 43, 90, 91, 113, 114, 115]
    assert style_map["heading_1"]["confidence"] == "confirmed"
    assert style_map["heading_2"]["confidence"] == "confirmed"
    assert style_map["body"]["confidence"] == "confirmed"
    assert style_map["confidence"] == "confirmed"


def test_extract_style_map_uses_name_based_fallback(scripts_dir):
    analyzer = load_analyzer_module(scripts_dir / "analyze_template.py")

    header_xml = """
    <hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
      <hh:refList>
        <hh:charPr id="6" height="1000" />
        <hh:charPr id="7" height="1400" />
        <hh:charPr id="8" height="1200" />
        <hh:charPr id="9" height="1000" />
        <hh:paraPr id="8" />
        <hh:paraPr id="10" />
        <hh:paraPr id="11" />
        <hh:paraPr id="77"><hh:heading type="BULLET"/></hh:paraPr>
      </hh:refList>
      <hh:style id="1" name="바탕글" engName="Normal" type="PARA" paraPrIDRef="8" charPrIDRef="6"/>
      <hh:style id="2" name="개요 1" engName="Outline 1" type="PARA" paraPrIDRef="10" charPrIDRef="7"/>
      <hh:style id="3" name="개요 2" engName="Outline 2" type="PARA" paraPrIDRef="11" charPrIDRef="8"/>
      <hh:style id="4" name="캡션" engName="Caption" type="PARA" paraPrIDRef="11" charPrIDRef="9"/>
      <hh:style id="5" name="인용문" engName="Blockquote" type="PARA" paraPrIDRef="10" charPrIDRef="6"/>
    </hh:head>
    """.strip()

    section_xml = """
    <hs:section xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
      <hs:sec>
        <hp:p paraPrIDRef="4">
          <hp:run charPrIDRef="6"><hp:pic id="1"/></hp:run>
        </hp:p>
      </hs:sec>
    </hs:section>
    """.strip()

    style_map = analyzer.extract_style_map(
        etree.fromstring(header_xml.encode("utf-8")),
        etree.fromstring(section_xml.encode("utf-8")),
    )

    assert style_map["heading_1"]["confidence"] == "estimated"
    assert style_map["heading_2"]["confidence"] == "estimated"
    assert style_map["body"]["confidence"] == "estimated"
    assert style_map["image_caption"]["confidence"] == "estimated"
    assert style_map["bullet"]["confidence"] == "estimated"
    assert style_map["bullet_auto"] == [77]
    assert style_map["blockquote"]["confidence"] == "estimated"
