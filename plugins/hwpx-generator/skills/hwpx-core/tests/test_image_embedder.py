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
