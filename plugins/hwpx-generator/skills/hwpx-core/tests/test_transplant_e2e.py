import importlib
import re
import sys
import warnings
import zipfile
from pathlib import Path
from typing import Callable, cast


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
transplant_sections = cast(
    Callable[..., dict[str, object]],
    importlib.import_module("section_transplant").transplant_sections,
)


def _make_hwpx_with_source_ids(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
    suffix: str,
    chapters: int = 3,
) -> Path:
    make_paragraph = cast(
        Callable[..., str],
        importlib.import_module("zip_surgery").make_paragraph,
    )

    if suffix == "source":
        char_id_h1, char_id_body = "41", "42"
        char_styles = [(41, 1500, True), (42, 1000, False)]
        para_styles = [(31, "JUSTIFY"), (32, "JUSTIFY")]
        para_id_body, para_id_h1 = "31", "32"
    else:
        char_id_h1, char_id_body = "51", "52"
        char_styles = [(51, 1500, True), (52, 1000, False)]
        para_styles = [(61, "JUSTIFY"), (62, "JUSTIFY")]
        para_id_body, para_id_h1 = "61", "62"

    paragraphs = [
        make_paragraph(
            "100", "표지", paraPrIDRef=para_id_body, charPrIDRef=char_id_body
        )
    ]
    for ch in range(1, chapters + 1):
        paragraphs.append(
            make_paragraph(
                str(1000 + ch),
                f"{ch}. 챕터 {ch} {suffix}",
                paraPrIDRef=para_id_h1,
                charPrIDRef=char_id_h1,
            )
        )
        paragraphs.append(
            make_paragraph(
                str(2000 + ch),
                f"챕터 {ch} {suffix} 본문",
                paraPrIDRef=para_id_body,
                charPrIDRef=char_id_body,
            )
        )

    section_bytes = make_section_xml(paragraphs)
    header_bytes = make_header_xml(char_styles, para_styles)

    hwpx_path = tmp_path / f"test_{suffix}.hwpx"
    with zipfile.ZipFile(str(hwpx_path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Contents/section0.xml", section_bytes)
        zf.writestr("Contents/header.xml", header_bytes)
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types/>')
    return hwpx_path


def test_full_transplant_synthetic(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source", chapters=3
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    transplant_sections(source, target, chapter_nums=[2], output_path=output)
    assert output.exists()
    with zipfile.ZipFile(str(output)) as zf:
        section_text = zf.read("Contents/section0.xml").decode("utf-8")
    assert "챕터 2 source 본문" in section_text


def test_transplant_preserves_non_target(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source", chapters=3
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    transplant_sections(source, target, chapter_nums=[2], output_path=output)
    with zipfile.ZipFile(str(output)) as zf:
        section_text = zf.read("Contents/section0.xml").decode("utf-8")
    assert "챕터 1 target 본문" in section_text
    assert "챕터 3 target 본문" in section_text


def test_transplant_remaps_all_ids(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source", chapters=3
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    transplant_sections(source, target, chapter_nums=[2], output_path=output)
    with zipfile.ZipFile(str(output)) as zf:
        section_text = zf.read("Contents/section0.xml").decode("utf-8")
    assert not re.search(r'charPrIDRef="41"', section_text)
    assert not re.search(r'charPrIDRef="42"', section_text)


def test_zip_metadata_preserved(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source", chapters=3
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    transplant_sections(source, target, chapter_nums=[2], output_path=output)

    with zipfile.ZipFile(str(target)) as tgt_zf:
        tgt_infos = {info.filename: info for info in tgt_zf.infolist()}
    with zipfile.ZipFile(str(output)) as out_zf:
        out_infos = {info.filename: info for info in out_zf.infolist()}

    for name in tgt_infos:
        if "section" not in name:
            assert name in out_infos
            assert tgt_infos[name].compress_type == out_infos[name].compress_type


def test_dry_run_no_output(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source"
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target"
    )
    output = tmp_path / "should_not_exist.hwpx"
    result = transplant_sections(source, target, chapter_nums=[2], dry_run=True)
    assert not output.exists()
    assert result["output_path"] is None
    assert "mapping" in result
    mapping = cast(dict[str, dict[str, str]], result["mapping"])
    assert "charPrIDRef" in mapping


def test_missing_chapter_warning(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    source = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "source", chapters=2
    )
    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        transplant_sections(source, target, chapter_nums=[99], output_path=output)
        warning_msgs = [str(item.message) for item in captured]
        assert any("99" in msg for msg in warning_msgs)


def test_image_reference_warning(
    make_section_xml: Callable[[list[str]], bytes],
    make_header_xml: Callable[
        [list[tuple[int, int, bool]], list[tuple[int, str]]], bytes
    ],
    tmp_path: Path,
) -> None:
    make_paragraph = cast(
        Callable[..., str],
        importlib.import_module("zip_surgery").make_paragraph,
    )
    pic_paragraph = (
        '<hp:p id="9001" paraPrIDRef="32" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="42">'
        "<hp:pic><hc:inst><hp:img></hp:img></hc:inst></hp:pic>"
        "</hp:run>"
        "</hp:p>"
    )
    paragraphs = [
        make_paragraph("1001", "1. 이미지 챕터", paraPrIDRef="32", charPrIDRef="41"),
        pic_paragraph,
    ]
    section_bytes = make_section_xml(paragraphs)
    header_bytes = make_header_xml(
        [(41, 1500, True), (42, 1000, False)],
        [(31, "JUSTIFY"), (32, "JUSTIFY")],
    )

    source = tmp_path / "source_with_pic.hwpx"
    with zipfile.ZipFile(str(source), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Contents/section0.xml", section_bytes)
        zf.writestr("Contents/header.xml", header_bytes)
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types/>')

    target = _make_hwpx_with_source_ids(
        make_section_xml, make_header_xml, tmp_path, "target", chapters=3
    )
    output = tmp_path / "result.hwpx"
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        transplant_sections(source, target, chapter_nums=[1], output_path=output)
        warning_msgs = [str(item.message) for item in captured]
        assert any(
            "pic" in msg.lower() or "image" in msg.lower() for msg in warning_msgs
        )
