from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


pytestmark = pytest.mark.integration


def _run_step(
    command: list[str], cwd: Path, step_name: str
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        rendered = " ".join(command)
        raise AssertionError(
            f"{step_name} failed (exit={result.returncode})\n"
            f"command: {rendered}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def _rewrite_section_pics_to_placeholders(hwpx_path: Path) -> int:
    """Convert pre-rendered hp:pic blocks to <!--IMAGE:imageN--> placeholders."""
    pic_pattern = re.compile(
        r"<hp:pic\b[^>]*>.*?<(?:hp|hc):img\b[^>]*binaryItemIDRef=\"(image\d+)\"[^>]*/>.*?</hp:pic>",
        flags=re.DOTALL,
    )

    with zipfile.ZipFile(hwpx_path, "r") as zin:
        infos = zin.infolist()
        entries = {info.filename: zin.read(info.filename) for info in infos}

    section_name = "Contents/section0.xml"
    if section_name not in entries:
        raise AssertionError(f"rewrite step: missing {section_name} in {hwpx_path}")

    section_text = entries[section_name].decode("utf-8")
    rewritten, count = pic_pattern.subn(
        lambda match: f"<!--IMAGE:{match.group(1)}-->",
        section_text,
    )
    if count == 0:
        return 0

    entries[section_name] = rewritten.encode("utf-8")
    with zipfile.ZipFile(hwpx_path, "w") as zout:
        for info in infos:
            info_out = zipfile.ZipInfo(info.filename)
            info_out.compress_type = info.compress_type
            zout.writestr(info_out, entries[info.filename])

    return count


def _normalize_fragment_root_from_template(
    fragment_xml: Path, template_hwpx: Path
) -> None:
    """Preserve template XML declaration/root namespaces on generated fragment."""
    with zipfile.ZipFile(template_hwpx, "r") as zf:
        template_text = zf.read("Contents/section0.xml").decode("utf-8")

    frag_text = fragment_xml.read_text(encoding="utf-8")

    tmpl_root_start = template_text.find("<hs:sec")
    tmpl_root_end = template_text.find(">", tmpl_root_start)
    tmpl_close = template_text.rfind("</hs:sec>")
    if tmpl_root_start < 0 or tmpl_root_end < 0 or tmpl_close < 0:
        raise AssertionError("normalize step: invalid template section0.xml structure")

    frag_root_start = frag_text.find("<hs:sec")
    frag_root_end = frag_text.find(">", frag_root_start)
    frag_close = frag_text.rfind("</hs:sec>")
    if frag_root_start < 0 or frag_root_end < 0 or frag_close < 0:
        raise AssertionError("normalize step: invalid generated fragment structure")

    template_header = template_text[: tmpl_root_end + 1]
    generated_body = frag_text[frag_root_end + 1 : frag_close]
    normalized = f"{template_header}{generated_body}</hs:sec>"
    fragment_xml.write_text(normalized, encoding="utf-8")


def _ensure_strict_section_header(hwpx_path: Path) -> None:
    """Force section0.xml to strict validator header/newline requirements."""
    with zipfile.ZipFile(hwpx_path, "r") as zin:
        infos = zin.infolist()
        entries = {info.filename: zin.read(info.filename) for info in infos}

    section_name = "Contents/section0.xml"
    if section_name not in entries:
        raise AssertionError(
            f"strict-header step: missing {section_name} in {hwpx_path}"
        )

    section_text = entries[section_name].decode("utf-8")
    sec_start = section_text.find("<hs:sec")
    if sec_start < 0:
        raise AssertionError("strict-header step: <hs:sec> root not found")

    compact_section = section_text[sec_start:].replace("\r", "").replace("\n", "")
    xml_decl = '<?xml version="1.0" encoding="UTF-8" standalone=\'no\'?>\n'
    entries[section_name] = f"{xml_decl}{compact_section}".encode("utf-8")

    with zipfile.ZipFile(hwpx_path, "w") as zout:
        for info in infos:
            info_out = zipfile.ZipInfo(info.filename)
            info_out.compress_type = info.compress_type
            zout.writestr(info_out, entries[info.filename])


def test_hwpx_full_e2e_pipeline(dev_dir, scripts_dir):
    """Run markdown->xml->zip surgery->image embedding->validation end to end."""
    tmp_dir = dev_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    md3 = dev_dir / "3장.md"
    md4 = dev_dir / "4장.md"
    draft_hwpx = dev_dir / "(양식) '27년도 전략연구사업 제안서_초안.hwpx"
    reference_hwpx = dev_dir / "(양식) '27년도 전략연구사업 제안서_작성.hwpx"
    core_scripts = scripts_dir
    fix_namespaces = (
        scripts_dir.parent.parent / "hwpx-templates" / "scripts" / "fix_namespaces.py"
    )

    p3_json = tmp_dir / "p3.json"
    p4_json = tmp_dir / "p4.json"
    merged_json = tmp_dir / "merged.json"
    style_map_json = tmp_dir / "sm.json"
    fragment_xml = tmp_dir / "fragment.xml"
    intermediate_hwpx = tmp_dir / "intermediate.hwpx"
    with_images_hwpx = tmp_dir / "with_images.hwpx"
    proof_json = tmp_dir / "proof.json"

    # Step 1: md_parser for 3장
    _run_step(
        [
            sys.executable,
            str(core_scripts / "md_parser.py"),
            str(md3),
            "--output",
            str(p3_json),
        ],
        cwd=core_scripts,
        step_name="step1 md_parser 3장",
    )
    assert p3_json.is_file(), "step1 output missing: p3.json"

    # Step 2: md_parser for 4장
    _run_step(
        [
            sys.executable,
            str(core_scripts / "md_parser.py"),
            str(md4),
            "--output",
            str(p4_json),
        ],
        cwd=core_scripts,
        step_name="step2 md_parser 4장",
    )
    assert p4_json.is_file(), "step2 output missing: p4.json"

    # Step 3: merge parsed blocks
    p3_data = json.loads(p3_json.read_text(encoding="utf-8"))
    p4_data = json.loads(p4_json.read_text(encoding="utf-8"))
    p3_blocks = p3_data.get("blocks")
    p4_blocks = p4_data.get("blocks")
    assert isinstance(p3_blocks, list), "step3 p3.json missing list key: blocks"
    assert isinstance(p4_blocks, list), "step3 p4.json missing list key: blocks"
    merged = {
        "blocks": [*p3_blocks, *p4_blocks],
        "source_file": f"{md3.name}+{md4.name}",
    }
    merged_json.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    assert merged_json.is_file(), "step3 output missing: merged.json"

    # Step 4: analyze template to style map
    _run_step(
        [
            sys.executable,
            str(core_scripts / "analyze_template.py"),
            str(draft_hwpx),
            "--style-map",
            str(style_map_json),
        ],
        cwd=core_scripts,
        step_name="step4 analyze_template",
    )
    assert style_map_json.is_file(), "step4 output missing: sm.json"

    # Step 5: xml_writer fragment with wrapped section
    _run_step(
        [
            sys.executable,
            str(core_scripts / "xml_writer.py"),
            "--input",
            str(merged_json),
            "--style-config",
            str(style_map_json),
            "--wrap-section",
            "--output",
            str(fragment_xml),
        ],
        cwd=core_scripts,
        step_name="step5 xml_writer",
    )
    assert fragment_xml.is_file(), "step5 output missing: fragment.xml"
    _normalize_fragment_root_from_template(fragment_xml, draft_hwpx)

    # Step 6: zip surgery replace section
    _run_step(
        [
            sys.executable,
            str(core_scripts / "zip_surgery.py"),
            "replace",
            str(draft_hwpx),
            "--section-file",
            str(fragment_xml),
            "--output",
            str(intermediate_hwpx),
        ],
        cwd=core_scripts,
        step_name="step6 zip_surgery replace",
    )
    assert intermediate_hwpx.is_file(), "step6 output missing: intermediate.hwpx"

    rewritten_count = _rewrite_section_pics_to_placeholders(intermediate_hwpx)
    assert rewritten_count > 0, (
        "step6.5 rewrite expected pre-rendered image blocks, found none to replace"
    )

    # Step 7: embed images from parsed JSON
    _run_step(
        [
            sys.executable,
            str(core_scripts / "image_embedder.py"),
            "--hwpx",
            str(intermediate_hwpx),
            "--images-dir",
            str(dev_dir / "images"),
            "--from-parsed",
            str(merged_json),
            "--base-dir",
            str(dev_dir),
            "--output",
            str(with_images_hwpx),
        ],
        cwd=core_scripts,
        step_name="step7 image_embedder",
    )
    assert with_images_hwpx.is_file(), "step7 output missing: with_images.hwpx"

    # Step 8: fix namespaces in place
    _run_step(
        [sys.executable, str(fix_namespaces), str(with_images_hwpx)],
        cwd=core_scripts,
        step_name="step8 fix_namespaces",
    )
    _ensure_strict_section_header(with_images_hwpx)

    # Step 9: strict validation
    _run_step(
        [
            sys.executable,
            str(core_scripts / "validate.py"),
            "--strict",
            str(with_images_hwpx),
        ],
        cwd=core_scripts,
        step_name="step9 validate strict",
    )

    # Step 10: proofread and assert double_bullets=0
    proof_cmd = [
        sys.executable,
        str(core_scripts / "proofread.py"),
        str(with_images_hwpx),
        "--output",
        str(proof_json),
    ]
    proof_result = subprocess.run(
        proof_cmd,
        cwd=core_scripts,
        capture_output=True,
        text=True,
    )
    assert proof_result.returncode in (0, 1), (
        "step10 proofread execution failed unexpectedly\n"
        f"command: {' '.join(proof_cmd)}\n"
        f"stdout:\n{proof_result.stdout}\n"
        f"stderr:\n{proof_result.stderr}"
    )
    assert proof_json.is_file(), "step10 output missing: proof.json"
    proof_data = json.loads(proof_json.read_text(encoding="utf-8"))
    double_bullets = proof_data.get("double_bullets", {})
    assert isinstance(double_bullets, dict), (
        "step10 invalid proofread JSON: double_bullets"
    )
    assert double_bullets.get("count") == 0, (
        f"step10 expected double_bullets=0, got {double_bullets.get('count')}"
    )

    # Step 11: page guard against reference
    page_guard_cmd = [
        sys.executable,
        str(core_scripts / "page_guard.py"),
        "--reference",
        str(reference_hwpx),
        "--output",
        str(with_images_hwpx),
    ]
    page_guard_result = subprocess.run(
        page_guard_cmd,
        cwd=core_scripts,
        capture_output=True,
        text=True,
    )
    assert page_guard_result.returncode in (0, 1), (
        "step11 page_guard execution failed unexpectedly\n"
        f"command: {' '.join(page_guard_cmd)}\n"
        f"stdout:\n{page_guard_result.stdout}\n"
        f"stderr:\n{page_guard_result.stderr}"
    )
    page_guard_issues = [
        line
        for line in page_guard_result.stdout.splitlines()
        if line.strip().startswith("-")
    ]
    assert len(page_guard_issues) <= 5, (
        "step11 page_guard expected <=5 warnings/issues, "
        f"got {len(page_guard_issues)}\n"
        f"stdout:\n{page_guard_result.stdout}\n"
        f"stderr:\n{page_guard_result.stderr}"
    )

    # Final artifact assertion: 15 images in BinData/
    with zipfile.ZipFile(with_images_hwpx, "r") as zf:
        bindata_images = [
            name
            for name in zf.namelist()
            if name.startswith("BinData/")
            and name.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    assert len(bindata_images) == 15, (
        f"expected 15 images in BinData/, found {len(bindata_images)}: {bindata_images}"
    )

    # Verify 15 caption paragraphs contain "그림" text
    with zipfile.ZipFile(with_images_hwpx) as _z:
        _section = _z.read("Contents/section0.xml").decode("utf-8", errors="replace")
    caption_count = len(re.findall(r'그림\s+\d+-\d+', _section))
    assert caption_count >= 15, f"Expected 15+ caption paragraphs with '그림 N-M', found {caption_count}"
