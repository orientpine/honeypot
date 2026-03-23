import sys
import importlib
import warnings
import zipfile
from collections.abc import Callable
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
transplant_sections = importlib.import_module("section_transplant").transplant_sections


def test_transplant_sections_basic(make_test_hwpx: Callable[..., Path], tmp_path: Path):
    source = make_test_hwpx(chapters=3)
    target = make_test_hwpx(chapters=3)
    output = tmp_path / "result.hwpx"

    result = transplant_sections(source, target, chapter_nums=[2], output_path=output)

    assert output.exists()
    assert result["output_path"] == output


def test_transplant_source_chapter_text_in_result(
    make_test_hwpx: Callable[..., Path], tmp_path: Path
):
    source = make_test_hwpx(chapters=3)
    target = make_test_hwpx(chapters=3)
    output = tmp_path / "result.hwpx"

    transplant_sections(source, target, chapter_nums=[2], output_path=output)

    with zipfile.ZipFile(str(output)) as zf:
        section_bytes = zf.read("Contents/section0.xml")

    section_text = section_bytes.decode("utf-8")
    assert "챕터 2의 본문" in section_text


def test_transplant_preserves_non_transplanted_chapters(
    make_test_hwpx: Callable[..., Path], tmp_path: Path
):
    source = make_test_hwpx(chapters=3)
    target = make_test_hwpx(chapters=3)
    output = tmp_path / "result.hwpx"

    transplant_sections(source, target, chapter_nums=[2], output_path=output)

    with zipfile.ZipFile(str(output)) as zf:
        result_section = zf.read("Contents/section0.xml")

    result_text = result_section.decode("utf-8")
    assert "챕터 1의 본문" in result_text
    assert "챕터 3의 본문" in result_text


def test_transplant_dry_run_no_output(
    make_test_hwpx: Callable[..., Path], tmp_path: Path
):
    source = make_test_hwpx(chapters=3)
    target = make_test_hwpx(chapters=3)
    output = tmp_path / "should_not_exist.hwpx"

    result = transplant_sections(source, target, chapter_nums=[2], dry_run=True)

    assert not output.exists()
    assert result["output_path"] is None
    assert "mapping" in result
    assert "source_ranges" in result
    assert "target_ranges" in result


def test_transplant_missing_chapter_warns(
    make_test_hwpx: Callable[..., Path], tmp_path: Path
):
    source = make_test_hwpx(chapters=2)
    target = make_test_hwpx(chapters=3)
    output = tmp_path / "result.hwpx"

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        transplant_sections(source, target, chapter_nums=[99], output_path=output)
        assert any("99" in str(w.message) for w in caught)
