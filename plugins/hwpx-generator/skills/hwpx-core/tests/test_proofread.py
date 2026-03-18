from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_proofread(
    script_path: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
    )


def _make_hwpx_with_section(
    tmp_path: Path, section_xml: str, name: str = "sample.hwpx"
) -> Path:
    hwpx_path = tmp_path / name
    with zipfile.ZipFile(hwpx_path, "w") as zf:
        zf.writestr("Contents/section0.xml", section_xml.encode("utf-8"))
    return hwpx_path


def test_proofread_help_returns_zero(scripts_dir):
    script_path = scripts_dir / "proofread.py"
    result = _run_proofread(script_path, ["--help"])

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


def test_proofread_on_초안_outputs_required_keys(scripts_dir, dev_dir, tmp_path):
    script_path = scripts_dir / "proofread.py"
    input_hwpx = dev_dir / "(양식) '27년도 전략연구사업 제안서_초안.hwpx"
    output_path = tmp_path / "proofread_result.json"

    result = _run_proofread(
        script_path,
        [
            str(input_hwpx),
            "--output",
            str(output_path),
        ],
    )

    assert result.returncode in (0, 1)
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    for key in (
        "double_bullets",
        "font_consistency",
        "empty_paragraphs",
        "orphaned_placeholders",
        "table_borders",
    ):
        assert key in data
        assert "pass" in data[key]


def test_double_bullets_check_detects_manual_prefix(scripts_dir, tmp_path):
    script_path = scripts_dir / "proofread.py"
    section_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
        'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
        '<hp:p id="1" paraPrIDRef="41">'
        '<hp:run charPrIDRef="1"><hp:t>● 항목</hp:t></hp:run>'
        "</hp:p>"
        "</hs:sec>"
    )
    hwpx_path = _make_hwpx_with_section(
        tmp_path, section_xml, name="double-bullet.hwpx"
    )

    result = _run_proofread(
        script_path,
        [str(hwpx_path), "--bullet-auto-ids", "41"],
    )

    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["double_bullets"]["pass"] is False
    assert data["double_bullets"]["count"] >= 1


def test_exit_code_zero_when_all_checks_pass(scripts_dir, tmp_path):
    script_path = scripts_dir / "proofread.py"
    section_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
        'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
        '<hp:p id="1" paraPrIDRef="10">'
        '<hp:run charPrIDRef="5"><hp:t>정상 본문 텍스트</hp:t></hp:run>'
        "</hp:p>"
        "<hp:tbl>"
        '<hp:tr><hp:tc borderFillIDRef="1"></hp:tc></hp:tr>'
        "</hp:tbl>"
        "</hs:sec>"
    )
    hwpx_path = _make_hwpx_with_section(tmp_path, section_xml, name="clean.hwpx")

    result = _run_proofread(script_path, [str(hwpx_path)])

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["double_bullets"]["pass"] is True
    assert data["font_consistency"]["pass"] is True
    assert data["empty_paragraphs"]["pass"] is True
    assert data["orphaned_placeholders"]["pass"] is True
    assert data["table_borders"]["pass"] is True
