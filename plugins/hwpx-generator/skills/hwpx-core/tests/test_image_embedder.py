from __future__ import annotations

import importlib.util
import json
import struct
import zipfile
from pathlib import Path


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
    """orgSz must reflect original pixel dimensions (×100 HWP units), not display size."""
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

        # orgSz = pixel dimensions × 100
        org_w = pixel_w * 100  # 64000
        org_h = pixel_h * 100  # 48000
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

        # scaMatrix should have a ratio < 1 since image is larger than A4 body
        import re
        sca_match = re.search(r'scaMatrix e1="([^"]+)"', section)
        assert sca_match is not None, "scaMatrix must be present"
        sca_value = float(sca_match.group(1))
        assert 0.0 < sca_value < 1.0, f"scaMatrix e1 should be <1, got {sca_value}"


def test_imgDim_has_pixel_values(scripts_dir, tmp_path):
    """imgDim must have actual pixel dimensions, not 0×0."""
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

        # imgDim must have pixel values
        assert f'dimwidth="{pixel_w}"' in section
        assert f'dimheight="{pixel_h}"' in section
        # Must NOT be 0×0 (the old defect)
        assert 'dimwidth="0"' not in section
