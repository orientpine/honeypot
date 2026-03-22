from __future__ import annotations

import importlib.util
import json
import re
import shutil
import struct
import zipfile
from pathlib import Path

import pytest


def load_image_embedder_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("image_embedder", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_minimal_png(path: Path, width: int = 64, height: int = 32) -> None:
    data = (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\x0dIHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
    )
    path.write_bytes(data)


def write_minimal_jpeg(path: Path, width: int = 64, height: int = 32) -> None:
    app0 = b"\xff\xe0\x00\x10" + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof0 = (
        b"\xff\xc0\x00\x11\x08"
        + struct.pack(">H", height)
        + struct.pack(">H", width)
        + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00"
    )
    path.write_bytes(b"\xff\xd8" + app0 + sof0 + b"\xff\xd9")


def create_input_hwpx(path: Path, placeholder: str = "image1") -> None:
    section = f"<root><!--IMAGE:{placeholder}--></root>"
    content = "<opf:package><opf:manifest></opf:manifest></opf:package>"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("Contents/section0.xml", section.encode("utf-8"))
        zf.writestr("Contents/content.hpf", content.encode("utf-8"))


@pytest.fixture
def create_png():
    """Create a minimal PNG file and return its path."""

    def _create_png(base_dir, name, width, height):
        path = base_dir / name
        write_minimal_png(path, width=width, height=height)
        return path

    return _create_png


@pytest.fixture
def embed(scripts_dir):
    """Embed images into HWPX using auto-mapping."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    def _embed(hwpx, images_dir, output):
        embedder.embed_images(hwpx, images_dir, None, None, ".", True, output)

    return _embed


def test_from_parsed_collects_image_ref_paths(scripts_dir, tmp_path):
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    png_path = images_dir / "01_vision.png"
    write_minimal_png(png_path)

    parsed_json = tmp_path / "parsed.json"
    parsed_json.write_text(
        json.dumps(
            {
                "blocks": [
                    {
                        "type": "image_ref",
                        "path": "./images/01_vision.png",
                        "caption": "sample",
                        "caption_id": "3-1",
                    }
                ],
                "source_file": "dev/3장.md",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        None,
        str(parsed_json),
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        content_hpf = zf.read("Contents/content.hpf").decode("utf-8")
        assert 'href="BinData/image1.png"' in content_hpf
        assert 'media-type="image/png"' in content_hpf
        assert "BinData/image1.png" in zf.namelist()


def test_jpeg_files_use_image_jpeg_media_type(scripts_dir, tmp_path):
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    jpg_path = images_dir / "image1.jpg"
    write_minimal_jpeg(jpg_path)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.jpg", "caption": ""}}),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        content_hpf = zf.read("Contents/content.hpf").decode("utf-8")
        assert 'href="BinData/image1.jpg"' in content_hpf
        assert 'media-type="image/jpeg"' in content_hpf
        assert "BinData/image1.jpg" in zf.namelist()


def test_mapping_mode_png_remains_compatible(scripts_dir, tmp_path):
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    png_path = images_dir / "image1.png"
    write_minimal_png(png_path)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(json.dumps({"image1": "image1.png"}), encoding="utf-8")

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        content_hpf = zf.read("Contents/content.hpf").decode("utf-8")
        assert 'href="BinData/image1.png"' in content_hpf
        assert 'media-type="image/png"' in content_hpf
        assert "BinData/image1.png" in zf.namelist()


def test_pic_wrapped_in_run_and_paragraph(scripts_dir, tmp_path):
    """hp:pic must be wrapped in <hp:p><hp:run> — 한/글 ignores section-level hp:pic."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    png_path = images_dir / "image1.png"
    write_minimal_png(png_path, width=640, height=480)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        section = zf.read("Contents/section0.xml").decode("utf-8")

        # hp:pic must be inside <hp:p><hp:run>
        assert "<hp:p " in section, "hp:pic must be wrapped in <hp:p>"
        assert "<hp:run " in section, "hp:pic must be wrapped in <hp:run>"
        assert "</hp:run></hp:p>" in section, "hp:pic wrapper must close correctly"

        # Verify correct nesting: <hp:p>...<hp:run>...<hp:pic>
        p_pos = section.find("<hp:p ")
        run_pos = section.find("<hp:run ", p_pos)
        pic_pos = section.find("<hp:pic ", run_pos)
        assert p_pos < run_pos < pic_pos, "hp:p > hp:run > hp:pic nesting required"


def test_orgSz_uses_pixel_dimensions(scripts_dir, tmp_path):
    """orgSz must reflect original pixel dimensions (×36 HWP units, 200 DPI), not display size."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    pixel_w, pixel_h = 640, 480
    png_path = images_dir / "image1.png"
    write_minimal_png(png_path, width=pixel_w, height=pixel_h)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        section = zf.read("Contents/section0.xml").decode("utf-8")

        # orgSz = pixel dimensions × 36 (200 DPI)
        org_w = pixel_w * 36  # 23040
        org_h = pixel_h * 36  # 17280
        assert f'orgSz width="{org_w}" height="{org_h}"' in section

        # curSz = display size (A4 body width)
        cur_w = 42520
        assert f'curSz width="{cur_w}"' in section

        # orgSz != curSz (the core defect that was fixed)
        assert f'orgSz width="{cur_w}"' not in section


def test_scaMatrix_reflects_scaling_ratio(scripts_dir, tmp_path):
    """scaMatrix e1/e5 must be curSz/orgSz, not identity."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    pixel_w, pixel_h = 640, 480
    png_path = images_dir / "image1.png"
    write_minimal_png(png_path, width=pixel_w, height=pixel_h)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        section = zf.read("Contents/section0.xml").decode("utf-8")

        # scaMatrix must NOT be identity (that was the defect)
        assert 'scaMatrix e1="1" ' not in section
        assert 'scaMatrix e1="1.0" ' not in section

        # scaMatrix should have a ratio > 1 since orgSz(200DPI) < curSz(A4 body)
        import re

        sca_match = re.search(r'scaMatrix e1="([^"]+)"', section)
        assert sca_match is not None, "scaMatrix must be present"
        sca_value = float(sca_match.group(1))
        assert sca_value > 1.0, f"scaMatrix e1 should be >1 (upscale), got {sca_value}"


def test_imgDim_has_pixel_values(scripts_dir, tmp_path):
    """imgDim must have pixel × 75 dimensions (96 DPI), not raw pixels or 0×0."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    pixel_w, pixel_h = 640, 480
    png_path = images_dir / "image1.png"
    write_minimal_png(png_path, width=pixel_w, height=pixel_h)

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        section = zf.read("Contents/section0.xml").decode("utf-8")

        # imgDim must have pixel × 75 values (96 DPI)
        assert f'dimwidth="{pixel_w * 75}"' in section
        assert f'dimheight="{pixel_h * 75}"' in section
        # Must NOT be 0×0 (the old defect)
        assert 'dimwidth="0"' not in section


# ── New tests: auto_resize + compression ─────────────────────────────


def test_auto_resize_max_height(scripts_dir):
    """calc_hwpx_height must auto-cap instead of raising ValueError when MAX_IMAGE_HEIGHT exceeded."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    # width=100, height=10000 -> result = (10000/100) * 42520 = 4252000
    # which far exceeds MAX_IMAGE_HEIGHT=70000
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = embedder.calc_hwpx_height(100, 10000)
        # Should NOT raise, should return capped value
        assert result <= embedder.MAX_IMAGE_HEIGHT
        assert result == embedder.MAX_IMAGE_HEIGHT  # capped to max
        # Should have issued a warning
        assert len(w) >= 1
        assert any(
            "exceeds" in str(warning.message).lower()
            or "cap" in str(warning.message).lower()
            for warning in w
        )


def test_auto_resize_normal_height_unchanged(scripts_dir):
    """calc_hwpx_height must return exact value when within MAX_IMAGE_HEIGHT."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    # width=640, height=480 -> result = (480/640) * 42520 = 31890
    # well within MAX_IMAGE_HEIGHT=70000
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = embedder.calc_hwpx_height(640, 480)
        assert result == int((480 / 640) * 42520)
        # No warning should be issued
        height_warnings = [
            x
            for x in w
            if "exceeds" in str(x.message).lower() or "cap" in str(x.message).lower()
        ]
        assert len(height_warnings) == 0


def test_compression_max_width_resizes_large_images(scripts_dir, tmp_path):
    """When --max-width is set, images wider than the limit must be resized."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    from PIL import Image

    images_dir = tmp_path / "images"
    images_dir.mkdir()

    # Create a 3000x2000 PNG image (wider than max_width=1000)
    large_img = images_dir / "image1.png"
    img = Image.new("RGB", (3000, 2000), color=(255, 0, 0))
    img.save(str(large_img), "PNG")

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
        max_width=1000,
        quality=85,
    )

    assert output_hwpx.exists()

    # Verify embedded image was actually resized
    import io

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        for name in zf.namelist():
            if name.startswith("BinData/"):
                embedded_data = zf.read(name)
                embedded_img = Image.open(io.BytesIO(embedded_data))
                assert embedded_img.width <= 1000, (
                    f"Embedded image width {embedded_img.width} exceeds max_width 1000"
                )
                # Aspect ratio preserved: 3000:2000 = 3:2, so 1000 -> ~667
                expected_height = int(2000 * (1000 / 3000))
                assert abs(embedded_img.height - expected_height) <= 1


def test_compression_no_max_width_unchanged(scripts_dir, tmp_path):
    """When --max-width is NOT set, images should not be modified."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    from PIL import Image

    images_dir = tmp_path / "images"
    images_dir.mkdir()

    # Create a 3000x2000 PNG image
    large_img = images_dir / "image1.png"
    img = Image.new("RGB", (3000, 2000), color=(255, 0, 0))
    img.save(str(large_img), "PNG")

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    # max_width=None (default) -> no resizing
    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
    )

    assert output_hwpx.exists()

    # Verify embedded image is still original size
    import io

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        for name in zf.namelist():
            if name.startswith("BinData/"):
                embedded_data = zf.read(name)
                embedded_img = Image.open(io.BytesIO(embedded_data))
                assert embedded_img.width == 3000
                assert embedded_img.height == 2000


def test_compression_small_image_not_resized(scripts_dir, tmp_path):
    """When --max-width is set but image is smaller, no resize should occur."""
    embedder = load_image_embedder_module(scripts_dir / "image_embedder.py")

    from PIL import Image

    images_dir = tmp_path / "images"
    images_dir.mkdir()

    # Create a 500x300 PNG image (smaller than max_width=1000)
    small_img = images_dir / "image1.png"
    img = Image.new("RGB", (500, 300), color=(0, 255, 0))
    img.save(str(small_img), "PNG")

    input_hwpx = tmp_path / "input.hwpx"
    output_hwpx = tmp_path / "output.hwpx"
    create_input_hwpx(input_hwpx, placeholder="image1")

    mapping_json = tmp_path / "mapping.json"
    mapping_json.write_text(
        json.dumps({"image1": {"file": "image1.png", "caption": ""}}),
        encoding="utf-8",
    )

    embedder.embed_images(
        str(input_hwpx),
        str(images_dir),
        str(mapping_json),
        None,
        str(tmp_path),
        False,
        str(output_hwpx),
        max_width=1000,
        quality=85,
    )

    assert output_hwpx.exists()

    # Image should remain original size since it's within max_width
    import io

    with zipfile.ZipFile(output_hwpx, "r") as zf:
        for name in zf.namelist():
            if name.startswith("BinData/"):
                embedded_data = zf.read(name)
                embedded_img = Image.open(io.BytesIO(embedded_data))
                assert embedded_img.width == 500
                assert embedded_img.height == 300


# ── Helper: HWPX with header.xml ─────────────────────────────────────


def create_input_hwpx_with_header(tmp_path: Path) -> Path:
    """Create a minimal HWPX with both section0.xml and header.xml."""
    hwpx_path = tmp_path / "input_with_header.hwpx"
    with zipfile.ZipFile(hwpx_path, "w") as zf:
        zf.writestr("mimetype", "application/hwp+zip")
        zf.writestr(
            "Contents/content.hpf",
            '<?xml version="1.0"?>'
            "<opf:package><opf:manifest></opf:manifest></opf:package>",
        )
        zf.writestr("Contents/section0.xml", "<root><!--IMAGE:image1--></root>")
        # header.xml with existing binDataList (should be stripped)
        zf.writestr(
            "Contents/header.xml",
            '<?xml version="1.0"?><hh:head><hh:refList>'
            '<hh:binDataList itemCnt="1">'
            '<hh:binItem id="0" Type="Embedding" '
            'BinData="BIN0001.png" Format="PNG"/>'
            "</hh:binDataList>"
            "</hh:refList></hh:head>",
        )
    return hwpx_path


# ── New tests: structural integrity + coordinate system ─────────────


def test_no_binDataList_in_output(tmp_path, embed, create_png):
    """Output header.xml must not contain binDataList."""
    img = create_png(tmp_path, "image1.png", 100, 80)
    images_dir = tmp_path / "imgs"
    images_dir.mkdir()
    shutil.copy(img, images_dir / "image1.png")
    hwpx = create_input_hwpx_with_header(tmp_path)
    out = tmp_path / "output.hwpx"
    embed(str(hwpx), str(images_dir), output=str(out))
    with zipfile.ZipFile(out) as zf:
        header = zf.read("Contents/header.xml").decode()
    assert "<hh:binDataList" not in header, "header.xml must not contain binDataList"


def test_binaryItemIDRef_matches_content_hpf(tmp_path, embed, create_png):
    """binaryItemIDRef in section must match opf:item id in content.hpf."""
    img = create_png(tmp_path, "image1.png", 100, 80)
    images_dir = tmp_path / "imgs"
    images_dir.mkdir()
    shutil.copy(img, images_dir / "image1.png")
    hwpx_path = tmp_path / "input.hwpx"
    create_input_hwpx(hwpx_path)
    out = tmp_path / "output.hwpx"
    embed(str(hwpx_path), str(images_dir), output=str(out))
    with zipfile.ZipFile(out) as zf:
        section = zf.read("Contents/section0.xml").decode()
        content_hpf = zf.read("Contents/content.hpf").decode()
    # Extract binaryItemIDRef
    refs = re.findall(r'binaryItemIDRef="([^"]+)"', section)
    assert refs, "No binaryItemIDRef found in section"
    # Each ref must appear as opf:item id in content.hpf
    for ref in refs:
        assert f'id="{ref}"' in content_hpf, (
            f'binaryItemIDRef="{ref}" not found in content.hpf'
        )


def test_element_order_hc_img_before_imgRect(tmp_path, embed, create_png):
    """hc:img must appear before hp:imgRect in the XML output."""
    img = create_png(tmp_path, "image1.png", 100, 80)
    images_dir = tmp_path / "imgs"
    images_dir.mkdir()
    shutil.copy(img, images_dir / "image1.png")
    hwpx_path = tmp_path / "input.hwpx"
    create_input_hwpx(hwpx_path)
    out = tmp_path / "output.hwpx"
    embed(str(hwpx_path), str(images_dir), output=str(out))
    with zipfile.ZipFile(out) as zf:
        section = zf.read("Contents/section0.xml").decode()
    img_pos = section.find("<hc:img")
    rect_pos = section.find("<hp:imgRect")
    assert img_pos != -1, "<hc:img not found"
    assert rect_pos != -1, "<hp:imgRect not found"
    assert img_pos < rect_pos, f"hc:img ({img_pos}) must precede hp:imgRect ({rect_pos})"


def test_numberingType_is_PICTURE(tmp_path, embed, create_png):
    """hp:pic must have numberingType='PICTURE'."""
    img = create_png(tmp_path, "image1.png", 100, 80)
    images_dir = tmp_path / "imgs"
    images_dir.mkdir()
    shutil.copy(img, images_dir / "image1.png")
    hwpx_path = tmp_path / "input.hwpx"
    create_input_hwpx(hwpx_path)
    out = tmp_path / "output.hwpx"
    embed(str(hwpx_path), str(images_dir), output=str(out))
    with zipfile.ZipFile(out) as zf:
        section = zf.read("Contents/section0.xml").decode()
    assert 'numberingType="PICTURE"' in section


def test_shapeComment_has_info(tmp_path, embed, create_png):
    """shapeComment must contain filename and pixel dimensions."""
    img = create_png(tmp_path, "image1.png", 100, 80)
    images_dir = tmp_path / "imgs"
    images_dir.mkdir()
    shutil.copy(img, images_dir / "image1.png")
    hwpx_path = tmp_path / "input.hwpx"
    create_input_hwpx(hwpx_path)
    out = tmp_path / "output.hwpx"
    embed(str(hwpx_path), str(images_dir), output=str(out))
    with zipfile.ZipFile(out) as zf:
        section = zf.read("Contents/section0.xml").decode()
    m = re.search(r"<hp:shapeComment>([^<]*)</hp:shapeComment>", section)
    assert m, "shapeComment element not found or empty"
    comment = m.group(1)
    assert "image1.png" in comment or "image1" in comment, (
        f"filename not in shapeComment: {comment}"
    )
    assert "100" in comment and "80" in comment, (
        f"pixel dims not in shapeComment: {comment}"
    )
