"""Root-cause regression tests for linesegarray strip policy.

linesegarray is HWP's per-paragraph precomputed LINE-LAYOUT CACHE. The
generation pipeline must NEVER emit heuristic linesegarray (wrong glyph
metrics cram text into one line) and must NEVER mutate table/cell heights.
Instead every production path STRIPS the whole <hp:linesegarray> element so
Hancom recomputes accurate layout when the document is opened.

S1: build() must not emit linesegarray (nor an empty <hp:linesegarray/>).
S2: build() must not emit linesegarray and must not mutate cell/table heights.
S3: pack() must strip stale linesegarray, keep mimetype-first/ZIP_STORED, stay valid.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path
from zipfile import ZIP_STORED

import pytest

# Make scripts/ and scripts/office/ importable (mirrors make_test_hwpx fixture).
_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
_OFFICE_DIR = _SCRIPTS_DIR / "office"
for _p in (_SCRIPTS_DIR, _OFFICE_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import build_hwpx  # noqa: E402
import pack as pack_mod  # noqa: E402  (scripts/office/pack.py)
import validate as validate_mod  # noqa: E402


# Full namespace root tag copied from templates/base so generated section XML
# parses with lxml (hp/hs/hh/hc declared).
_ROOT_OPEN = (
    '<hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app"'
    ' xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"'
    ' xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph"'
    ' xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"'
    ' xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"'
    ' xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"'
    ' xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history"'
    ' xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page"'
    ' xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf"'
    ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
    ' xmlns:opf="http://www.idpf.org/2007/opf/"'
    ' xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart"'
    ' xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar"'
    ' xmlns:epub="http://www.idpf.org/2007/ops"'
    ' xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0">'
)

# 60 Korean chars in a single <hp:t> (well over the 50-char minimum).
_LONG_KO = "가나다라마바사아자차카타파하" * 5  # 14 * 5 = 70 chars


def _section(inner: str) -> str:
    return f"<?xml version='1.0' encoding='UTF-8'?>\n{_ROOT_OPEN}{inner}</hs:sec>"


def _long_para() -> str:
    return (
        '<hp:p id="100" paraPrIDRef="0" styleIDRef="0" pageBreak="0"'
        ' columnBreak="0" merged="0"><hp:run charPrIDRef="0">'
        f"<hp:t>{_LONG_KO}</hp:t></hp:run></hp:p>"
    )


def _table_para(cell_h: str, tbl_h: str) -> str:
    """One 1x1 table with deliberately-small cell/table heights + long text."""
    return (
        '<hp:p id="200" paraPrIDRef="0" styleIDRef="0" pageBreak="0"'
        ' columnBreak="0" merged="0"><hp:run charPrIDRef="0">'
        '<hp:tbl id="1" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM"'
        ' textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL"'
        ' repeatHeader="1" rowCnt="1" colCnt="1" cellSpacing="0" borderFillIDRef="3"'
        ' noAdjust="0">'
        f'<hp:sz width="40000" widthRelTo="ABSOLUTE" height="{tbl_h}"'
        ' heightRelTo="ABSOLUTE" protect="0"/>'
        '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0"'
        ' holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP"'
        ' horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
        '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        '<hp:inMargin left="510" right="510" top="141" bottom="141"/>'
        '<hp:tr>'
        '<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0"'
        ' borderFillIDRef="3">'
        '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK"'
        ' vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0"'
        ' textHeight="0" hasTextRef="0" hasNumRef="0">'
        '<hp:p id="201" paraPrIDRef="0" styleIDRef="0" pageBreak="0"'
        ' columnBreak="0" merged="0"><hp:run charPrIDRef="0">'
        f"<hp:t>{_LONG_KO}</hp:t></hp:run></hp:p>"
        '</hp:subList>'
        '<hp:cellAddr colAddr="0" rowAddr="0"/>'
        '<hp:cellSpan colSpan="1" rowSpan="1"/>'
        f'<hp:cellSz width="40000" height="{cell_h}"/>'
        '<hp:cellMargin left="510" right="510" top="141" bottom="141"/>'
        '</hp:tc>'
        '</hp:tr>'
        '</hp:tbl>'
        '</hp:run></hp:p>'
    )


def _read_section(hwpx_path: Path) -> str:
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return zf.read("Contents/section0.xml").decode("utf-8")


# --------------------------------------------------------------------------- #
# S1: build() must not emit linesegarray for a long Korean paragraph.
# --------------------------------------------------------------------------- #
def test_s1_build_strips_linesegarray(tmp_path):
    section_file = tmp_path / "s1_section0.xml"
    section_file.write_text(_section(_long_para()), encoding="utf-8")
    out = tmp_path / "s1.hwpx"

    build_hwpx.build(
        template=None,
        header_override=None,
        section_override=section_file,
        title=None,
        creator=None,
        output=out,
    )

    section = _read_section(out)
    assert "<hp:linesegarray" not in section, (
        "build() emitted heuristic linesegarray; expected ZERO"
    )
    assert "linesegarray" not in section, "stray linesegarray substring present"
    assert "<hp:linesegarray/>" not in section, (
        "empty <hp:linesegarray/> left behind; whole element must be removed"
    )


# --------------------------------------------------------------------------- #
# S2: build() must not emit linesegarray and must not mutate heights.
# --------------------------------------------------------------------------- #
def test_s2_build_table_no_lineseg_no_height_mutation(tmp_path):
    cell_h = "100"
    tbl_h = "100"
    section_file = tmp_path / "s2_section0.xml"
    section_file.write_text(_section(_table_para(cell_h, tbl_h)), encoding="utf-8")
    out = tmp_path / "s2.hwpx"

    build_hwpx.build(
        template=None,
        header_override=None,
        section_override=section_file,
        title=None,
        creator=None,
        output=out,
    )

    section = _read_section(out)
    # (a) no linesegarray
    assert "linesegarray" not in section, (
        "build() emitted linesegarray inside table cell; expected ZERO"
    )
    # (b) heights unchanged (cell + table)
    assert f'<hp:cellSz width="40000" height="{cell_h}"/>' in section, (
        f"cellSz height mutated; expected unchanged height={cell_h}"
    )
    assert (
        f'<hp:sz width="40000" widthRelTo="ABSOLUTE" height="{tbl_h}"' in section
    ), f"table hp:sz height mutated; expected unchanged height={tbl_h}"


# --------------------------------------------------------------------------- #
# S3: pack() must strip stale linesegarray and keep packaging invariants.
# --------------------------------------------------------------------------- #
def test_s3_pack_strips_stale_linesegarray(tmp_path):
    # Build an unpacked dir from templates/base, inject a stale linesegarray.
    base = build_hwpx.BASE_DIR
    work = tmp_path / "unpacked"
    shutil.copytree(base, work)

    section_path = work / "Contents" / "section0.xml"
    text = section_path.read_text(encoding="utf-8")
    stale = (
        '<hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000"'
        ' textheight="1000" baseline="850" spacing="600" horzpos="0"'
        ' horzsize="42520" flags="393216"/></hp:linesegarray>'
    )
    # Inject as the last child of the first paragraph.
    text = text.replace("</hp:p>", stale + "</hp:p>", 1)
    section_path.write_text(text, encoding="utf-8")
    assert "<hp:linesegarray" in section_path.read_text(encoding="utf-8")

    out = tmp_path / "s3.hwpx"
    pack_mod.pack(str(work), str(out))

    section = _read_section(out)
    assert "linesegarray" not in section, (
        "pack() left stale linesegarray; expected ZERO"
    )

    # mimetype first + ZIP_STORED
    with zipfile.ZipFile(out, "r") as zf:
        names = zf.namelist()
        assert names[0] == "mimetype", "mimetype is not the first ZIP entry"
        assert zf.getinfo("mimetype").compress_type == ZIP_STORED, (
            "mimetype must be ZIP_STORED"
        )

    # validate.py reports no errors
    errors, _warnings = validate_mod.validate(str(out))
    assert errors == [], f"validate.py reported errors: {errors}"


# --------------------------------------------------------------------------- #
# S4: pack() must strip ALL linesegarray shapes — self-closing + attributes.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "stale",
    [
        pytest.param("<hp:linesegarray/>", id="self_closing"),
        pytest.param(
            '<hp:linesegarray foo="bar" baz="1">'
            '<hp:lineseg textpos="0"/></hp:linesegarray>',
            id="open_tag_with_attributes",
        ),
        pytest.param(
            "<hp:linesegarray >\n  <hp:lineseg textpos='0'/>\n</hp:linesegarray >",
            id="whitespace_in_tags",
        ),
    ],
)
def test_s4_pack_strips_all_linesegarray_shapes(tmp_path, stale):
    base = build_hwpx.BASE_DIR
    work = tmp_path / "unpacked"
    shutil.copytree(base, work)

    section_path = work / "Contents" / "section0.xml"
    text = section_path.read_text(encoding="utf-8")
    text = text.replace("</hp:p>", stale + "</hp:p>", 1)
    section_path.write_text(text, encoding="utf-8")
    assert "linesegarray" in section_path.read_text(encoding="utf-8")

    out = tmp_path / "s4.hwpx"
    pack_mod.pack(str(work), str(out))

    section = _read_section(out)
    assert "linesegarray" not in section, (
        f"pack() left stale linesegarray for shape: {stale!r}"
    )
