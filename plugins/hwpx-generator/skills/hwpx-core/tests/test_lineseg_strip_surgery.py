"""Root-cause regression tests: linesegarray strip on the ZIP-SURGERY paths.

linesegarray is HWP's per-paragraph precomputed LINE-LAYOUT CACHE. When it is
STALE (after a slot fill, placeholder text replacement, or chapter transplant
into a document with different page geometry) HWP renders the cached segment
positions, cramming text onto one line and ignoring 자간 until a manual relayout
(space key). When the element is ABSENT, Hangul Office recomputes accurate
layout on open.

v3.12.0 stripped linesegarray only in the XML-first BUILD + PACK paths
(build_hwpx.py / office/pack.py / fix_namespaces.py). The ZIP-surgery family
(zip_surgery.HwpxSurgeon.save, slot_filler.fill_hwpx, section_transplant) wrote
section XML verbatim and therefore kept stale linesegarray — which is why the
bug RECURS whenever a user fills a government FORM/TEMPLATE or transplants a
chapter. These tests pin every surgery output to ZERO linesegarray.

S5: HwpxSurgeon.save() strips stale linesegarray (covers unmodified siblings).
S6: slot_filler.fill_hwpx() output has ZERO linesegarray (filled + unfilled).
S7: section_transplant output strips linesegarray transplanted from source.
S8: HwpxSurgeon.save() strips ALL shapes AND validate_surgery() still passes.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

# Make scripts/ importable (mirrors test_lineseg_strip.py).
_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import zip_surgery  # noqa: E402
from slot_filler import fill_hwpx  # noqa: E402
from section_transplant import transplant_sections  # noqa: E402


# Full 15-xmlns root so section XML parses and satisfies validate_surgery
# (>=10 xmlns + standalone='no').
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

# A realistic stale linesegarray (computed for some other text / geometry).
_STALE_LSA = (
    '<hp:linesegarray><hp:lineseg textpos="0" vertpos="0" vertsize="1000"'
    ' textheight="1000" baseline="850" spacing="600" horzpos="0"'
    ' horzsize="42520" flags="393216"/></hp:linesegarray>'
)


def _section(inner: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        f"{_ROOT_OPEN}{inner}</hs:sec>"
    ).encode("utf-8")


def _para(pid: str, text: str, char: str = "0", para: str = "0", extra: str = "") -> str:
    """A <hp:p> with one run; `extra` is appended as a trailing child (e.g. lsa)."""
    return (
        f'<hp:p id="{pid}" paraPrIDRef="{para}" styleIDRef="0" pageBreak="0"'
        f' columnBreak="0" merged="0"><hp:run charPrIDRef="{char}">'
        f"<hp:t>{text}</hp:t></hp:run>{extra}</hp:p>"
    )


def _header_xml() -> bytes:
    """Minimal header with H1 (id=41, 1500) + body (id=42, 1000) for transplant."""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<hs:head xmlns:hs="http://www.hancom.co.kr/hwpml/2011/head/head"'
        ' xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head/head">'
        "<hh:docPrList><hh:charPrList>"
        '<hh:charPr id="41"><hh:fontSize size="1500" sizeAutomatic="0" lang="HANGUL"/></hh:charPr>'
        '<hh:charPr id="42"><hh:fontSize size="1000" sizeAutomatic="0" lang="HANGUL"/></hh:charPr>'
        "</hh:charPrList><hh:paraPrList>"
        '<hh:paraPr id="31"><hh:alignment type="JUSTIFY"/></hh:paraPr>'
        '<hh:paraPr id="32"><hh:alignment type="JUSTIFY"/></hh:paraPr>'
        "</hh:paraPrList></hh:docPrList></hs:head>"
    ).encode("utf-8")


def _make_hwpx(path: Path, section_bytes: bytes, header_bytes: bytes | None = None) -> Path:
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", b"application/hwp+zip")
        zf.writestr("Contents/section0.xml", section_bytes)
        if header_bytes is not None:
            zf.writestr("Contents/header.xml", header_bytes)
    return path


def _read_section(hwpx_path: Path) -> str:
    with zipfile.ZipFile(str(hwpx_path), "r") as zf:
        return zf.read("Contents/section0.xml").decode("utf-8")


# --------------------------------------------------------------------------- #
# S5: HwpxSurgeon.save() strips stale linesegarray even with NO modification.
# --------------------------------------------------------------------------- #
def test_s5_surgeon_save_strips_stale_linesegarray(tmp_path):
    src = _make_hwpx(
        tmp_path / "s5.hwpx",
        _section(_para("100", "가나다라마바사아자차카타파하" * 4, extra=_STALE_LSA)),
    )
    out = tmp_path / "s5.out.hwpx"

    surgeon = zip_surgery.HwpxSurgeon(src)
    surgeon.save(out)

    section = _read_section(out)
    assert "linesegarray" not in section, (
        "HwpxSurgeon.save() left stale linesegarray; surgery output must be ZERO"
    )


# --------------------------------------------------------------------------- #
# S6: slot_filler.fill_hwpx() output strips linesegarray on filled + unfilled.
# --------------------------------------------------------------------------- #
def test_s6_slot_filler_strips_linesegarray_all_paragraphs(tmp_path):
    inner = (
        _para("100", "", extra=_STALE_LSA)  # the slot we will fill
        + _para("200", "고정 라벨 문단", extra=_STALE_LSA)  # untouched sibling
    )
    src = _make_hwpx(tmp_path / "s6.hwpx", _section(inner))
    out = tmp_path / "s6.out.hwpx"

    unresolved = fill_hwpx(src, {"100": [("0", "채워진 긴 내용 " * 6)]}, out)

    assert unresolved == []
    section = _read_section(out)
    assert "linesegarray" not in section, (
        "slot_filler output kept stale linesegarray on an unfilled sibling paragraph"
    )
    assert "채워진 긴 내용" in section


# --------------------------------------------------------------------------- #
# S7: section_transplant strips linesegarray carried from the source document.
# --------------------------------------------------------------------------- #
def test_s7_transplant_strips_source_linesegarray(tmp_path):
    def _doc(suffix: str, lsa_on_ch2: bool) -> bytes:
        paras = [_para("100", f"표지 {suffix}", char="42", para="31")]
        for ch in range(1, 4):
            paras.append(_para(str(1000 + ch), f"{ch}. 챕터 {ch} {suffix}", char="41", para="32"))
            extra = _STALE_LSA if (lsa_on_ch2 and ch == 2) else ""
            paras.append(
                _para(str(2000 + ch), f"챕터 {ch} {suffix} 본문", char="42", para="31", extra=extra)
            )
        return _section("".join(paras))

    source = _make_hwpx(tmp_path / "s7.src.hwpx", _doc("source", lsa_on_ch2=True), _header_xml())
    target = _make_hwpx(tmp_path / "s7.tgt.hwpx", _doc("target", lsa_on_ch2=False), _header_xml())
    out = tmp_path / "s7.out.hwpx"

    transplant_sections(source, target, chapter_nums=[2], output_path=out)

    section = _read_section(out)
    assert "챕터 2 source 본문" in section, "transplant did not copy the source chapter"
    assert "linesegarray" not in section, (
        "transplant carried stale linesegarray from source into a different target geometry"
    )


# --------------------------------------------------------------------------- #
# S8: HwpxSurgeon.save() strips ALL shapes AND keeps surgery invariants valid.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "stale",
    [
        pytest.param("<hp:linesegarray/>", id="self_closing"),
        pytest.param(
            '<hp:linesegarray foo="bar"><hp:lineseg textpos="0"/></hp:linesegarray>',
            id="attrs",
        ),
        pytest.param(_STALE_LSA, id="full_element"),
    ],
)
def test_s8_surgeon_save_strips_all_shapes_and_validates(tmp_path, stale):
    src = _make_hwpx(
        tmp_path / "s8.hwpx",
        _section(_para("100", "본문 텍스트", extra=stale)),
        _header_xml(),
    )
    out = tmp_path / "s8.out.hwpx"

    surgeon = zip_surgery.HwpxSurgeon(src)
    surgeon.save(out)

    section = _read_section(out)
    assert "linesegarray" not in section, f"shape not stripped: {stale!r}"
    assert section.count("\n") == 1, "strip must not add/remove the single section newline"
    assert zip_surgery.validate_surgery(src, out) == [], "surgery invariants broken"


# --------------------------------------------------------------------------- #
# S9: validate.py must FLAG any leaked linesegarray as a hard error so the
# mandatory Phase-4 validation enforces the strip policy (root cause of the
# recurrence was reliance on a manual, un-enforced strip step).
# --------------------------------------------------------------------------- #
def test_s9_validate_flags_leaked_linesegarray(tmp_path):
    import validate as validate_mod

    src = _make_hwpx(
        tmp_path / "s9.hwpx",
        _section(_para("100", "본문", extra=_STALE_LSA)),
        _header_xml(),
    )

    errors, _warnings = validate_mod.validate(str(src))

    assert any("linesegarray" in e for e in errors), (
        f"validate() did not flag leaked linesegarray; errors={errors}"
    )
