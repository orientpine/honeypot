#!/usr/bin/env python3
"""Embed image files into HWPX files via ZIP-level edits.

This script adds image files to BinData/, updates Contents/content.hpf and
Contents/header.xml, and replaces <!--IMAGE:imageN--> placeholders in
Contents/section0.xml with <hp:pic> elements.
"""

import argparse
import io
import json
import os
import re
import shutil
import struct
import warnings
import zipfile

from PIL import Image, UnidentifiedImageError


PLACEHOLDER_RE = re.compile(r"<!--IMAGE:(image\d+)-->")
SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
A4_BODY_WIDTH = 42520
MAX_IMAGE_HEIGHT = 70000


def png_dimensions(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        _ = f.read(16)
        width_raw, height_raw = struct.unpack(">II", f.read(8))
    width = int(width_raw)
    height = int(height_raw)
    return width, height


def jpeg_dimensions(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        data = f.read()

    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        raise ValueError(f"Invalid JPEG file: {path}")

    index = 2
    while index + 1 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue

        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break

        marker = data[index]
        index += 1

        if marker in (0xD8, 0xD9):
            continue

        if marker == 0xDA:
            break

        if index + 1 >= len(data):
            break

        segment_length = (data[index] << 8) + data[index + 1]
        if segment_length < 2:
            raise ValueError(f"Invalid JPEG segment length in: {path}")

        segment_start = index + 2
        segment_end = segment_start + segment_length - 2
        if segment_end > len(data):
            raise ValueError(f"Invalid JPEG segment bounds in: {path}")

        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB):
            if segment_start + 4 >= segment_end:
                raise ValueError(f"Invalid JPEG SOF segment in: {path}")
            height = (data[segment_start + 1] << 8) + data[segment_start + 2]
            width = (data[segment_start + 3] << 8) + data[segment_start + 4]
            return int(width), int(height)

        index = segment_end

    raise ValueError(f"JPEG dimensions not found: {path}")


def normalize_image_extension(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image extension: {ext}")
    return ext


def ensure_png_format(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext != ".png":
        return path

    try:
        with Image.open(path) as img:
            if (img.format or "").upper() == "PNG":
                return path

            if img.mode in ("CMYK", "P"):
                converted = img.convert("RGB")
            else:
                converted = img.copy()

            converted.save(path, format="PNG")
            converted.close()
    except (UnidentifiedImageError, OSError):
        return path

    return path


def image_media_type(path: str) -> str:
    ext = normalize_image_extension(path)
    if ext == ".png":
        return "image/png"
    return "image/jpeg"


def image_dimensions(path: str) -> tuple[int, int]:
    ext = normalize_image_extension(path)
    if ext == ".png":
        return png_dimensions(path)
    return jpeg_dimensions(path)


def is_supported_image_file(name: str) -> bool:
    return name.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)


def load_mapping_from_parsed(
    parsed_path: str, base_dir: str
) -> dict[str, dict[str, str]]:
    with open(parsed_path, "r", encoding="utf-8") as f:
        data: object = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Parsed JSON must be an object")

    blocks = data.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("Parsed JSON must contain a 'blocks' list")

    result: dict[str, dict[str, str]] = {}
    for block_obj in blocks:
        if not isinstance(block_obj, dict):
            continue
        if block_obj.get("type") != "image_ref":
            continue

        path_value = block_obj.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            continue

        resolved_path = os.path.abspath(os.path.join(base_dir, path_value.strip()))
        file_name = os.path.basename(resolved_path)
        if not file_name:
            continue

        number = extract_image_number(file_name)
        if number is None:
            continue

        image_key = f"image{number}"
        if image_key in result:
            continue

        result[image_key] = {"file": file_name, "caption": "", "path": resolved_path}

    return result


def calc_hwpx_height(width: int, height: int, target_width: int = A4_BODY_WIDTH) -> int:
    if width <= 0:
        raise ValueError("Image width must be positive")

    result = int((height / width) * target_width)
    if result > MAX_IMAGE_HEIGHT:
        warnings.warn(
            f"Calculated image height {result} exceeds max {MAX_IMAGE_HEIGHT} HWP units. "
            f"Source image: {width}x{height}px. Auto-capping to {MAX_IMAGE_HEIGHT}.",
            stacklevel=2,
        )
        result = MAX_IMAGE_HEIGHT
    return result


def extract_body_width(section_xml: str) -> int:
    """Extract body width from section XML (pageSz - margins). Fallback: 42520 (A4)."""
    try:
        page_w_m = re.search(r'<hp:pageSz[^>]*\bwidth="(\d+)"', section_xml)
        left_m = re.search(r'<hp:pageMargin[^>]*\bleft="(\d+)"', section_xml)
        right_m = re.search(r'<hp:pageMargin[^>]*\bright="(\d+)"', section_xml)
        if page_w_m and left_m and right_m:
            return int(page_w_m.group(1)) - int(left_m.group(1)) - int(right_m.group(1))
    except Exception:
        pass
    return A4_BODY_WIDTH


def maybe_resize_image(path: str, max_width: int | None, quality: int = 85) -> bytes:
    """Load image, optionally resize if wider than max_width, return bytes.

    Args:
        path: Path to the image file
        max_width: Maximum width in pixels. If None, no resizing.
        quality: JPEG quality (used only when saving as JPEG)

    Returns:
        Image bytes (original if no resize, resized if max_width exceeded)
    """
    if max_width is None:
        with open(path, "rb") as f:
            return f.read()

    img = Image.open(path)
    if img.width <= max_width:
        with open(path, "rb") as f:
            return f.read()

    # Resize maintaining aspect ratio
    ratio = max_width / img.width
    new_height = int(img.height * ratio)
    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Save to bytes in the same format
    buf = io.BytesIO()
    fmt = getattr(img, "format", None)
    if fmt is None:
        # Detect format from file extension
        ext = os.path.splitext(path)[1].lower()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
    if fmt.upper() == "JPEG":
        img.save(buf, format="JPEG", quality=quality)
    else:
        img.save(buf, format="PNG")
    return buf.getvalue()


def extract_image_number(name: str) -> int | None:
    match = re.search(r"(\d+)", name)
    if not match:
        return None
    return int(match.group(1))


def image_sort_key(image_key: str) -> tuple[int, int | str]:
    number = extract_image_number(image_key)
    if number is None:
        return (1, image_key)
    return (0, number)


def load_mapping(mapping_path: str) -> dict[str, dict[str, str]]:
    with open(mapping_path, "r", encoding="utf-8") as f:
        data: object = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Mapping JSON must be an object keyed by imageN")

    data_dict: dict[object, object] = data
    result: dict[str, dict[str, str]] = {}
    for key, value in data_dict.items():
        if not re.fullmatch(r"image\d+", str(key)):
            continue
        if isinstance(value, dict) and isinstance(value.get("file"), str):
            file_name = value.get("file", "")
            caption_value = value.get("caption", "")
            caption = caption_value if isinstance(caption_value, str) else ""
        elif isinstance(value, str):
            file_name = value
            caption = ""
        else:
            continue
        if not file_name:
            continue
        result[str(key)] = {"file": str(file_name), "caption": str(caption)}
    return result


def auto_map_images(
    placeholders: set[str],
    images_dir: str,
    existing: dict[str, dict[str, str]] | None = None,
) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = dict(existing or {})
    image_files: list[str] = []
    for name in os.listdir(images_dir):
        if is_supported_image_file(name):
            image_files.append(name)
    image_files.sort()

    used_files: set[str] = set()
    for item in mapping.values():
        used_files.add(item["file"])

    placeholders_sorted = sorted(placeholders, key=image_sort_key)

    for file_name in image_files:
        if file_name in used_files:
            continue
        number = extract_image_number(file_name)
        if number is None:
            continue
        key = f"image{number}"
        if key in placeholders and key not in mapping:
            mapping[key] = {"file": file_name, "caption": ""}
            used_files.add(file_name)

    remaining_files = [f for f in image_files if f not in used_files]
    file_idx = 0
    for key in placeholders_sorted:
        if key in mapping:
            continue
        if file_idx >= len(remaining_files):
            break
        mapping[key] = {"file": remaining_files[file_idx], "caption": ""}
        file_idx += 1

    return mapping


def make_pic_xml(
    bin_id: str,
    cur_width: int,
    cur_height: int,
    org_width: int,
    org_height: int,
    pixel_width: int,
    pixel_height: int,
    pic_id: int,
    inst_id: int,
    para_id: int,
    filename: str,
    z_order: int,
    dim_width: int,
    dim_height: int,
) -> str:
    """Generate <hp:p><hp:run><hp:pic>...</hp:pic></hp:run></hp:p> XML.

    hp:pic MUST be inside <hp:run> — 한/글 ignores section-level hp:pic.

    Args:
        bin_id: Binary data ID (e.g. "image1")
        cur_width: Display width in HWP units (A4 body = 42520)
        cur_height: Display height in HWP units
        org_width: Original image width in HWP units (pixel_width × 36)
        org_height: Original image height in HWP units (pixel_height × 36)
        pixel_width: Original image width in pixels
        pixel_height: Original image height in pixels
        pic_id: Unique picture element ID
        inst_id: Unique instance ID
        para_id: Unique paragraph ID for the wrapper <hp:p>
        filename: Original image file name for shapeComment
        z_order: zOrder value for hp:pic
        dim_width: imgDim width (pixel_width × 75)
        dim_height: imgDim height (pixel_height × 75)
    """
    # scaMatrix = curSz / orgSz (scaling ratio from original to display)
    sca_x = cur_width / org_width if org_width > 0 else 1.0
    sca_y = cur_height / org_height if org_height > 0 else 1.0
    center_x = cur_width // 2
    center_y = cur_height // 2

    return (
        f'<hp:p id="{para_id}" paraPrIDRef="4" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="1">'
        f'<hp:pic id="{pic_id}" zOrder="{z_order}" instid="{inst_id}" reverse="0" '
        f'numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" '
        f'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
        f'href="" groupLevel="0">'
        # 1. hp:offset
        f'<hp:offset x="0" y="0"/>'
        # 2. hp:orgSz
        f'<hp:orgSz width="{org_width}" height="{org_height}"/>'
        # 3. hp:curSz
        f'<hp:curSz width="{cur_width}" height="{cur_height}"/>'
        # 4. hp:flip
        f'<hp:flip horizontal="0" vertical="0"/>'
        # 5. hp:rotationInfo
        f'<hp:rotationInfo angle="0" centerX="{center_x}" centerY="{center_y}" rotateimage="1"/>'
        # 6. hp:renderingInfo
        f"<hp:renderingInfo>"
        f'<hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        f'<hc:scaMatrix e1="{sca_x:.6f}" e2="0" e3="0" e4="0" e5="{sca_y:.6f}" e6="0"/>'
        f'<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        f"</hp:renderingInfo>"
        # 7. hc:img
        f'<hc:img binaryItemIDRef="{bin_id}" bright="0" contrast="0" '
        f'effect="REAL_PIC" alpha="0"/>'
        # 8. hp:imgRect (orgSz coordinate system)
        f"<hp:imgRect>"
        f'<hc:pt0 x="0" y="0"/><hc:pt1 x="{org_width}" y="0"/>'
        f'<hc:pt2 x="{org_width}" y="{org_height}"/><hc:pt3 x="0" y="{org_height}"/>'
        f"</hp:imgRect>"
        # 9. hp:imgClip (imgDim coordinate system)
        f'<hp:imgClip left="0" right="{dim_width}" top="0" bottom="{dim_height}"/>'
        # 10. hp:inMargin
        f'<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        # 11. hp:imgDim
        f'<hp:imgDim dimwidth="{dim_width}" dimheight="{dim_height}"/>'
        # 12. hp:effects
        f"<hp:effects/>"
        # 13. hp:sz
        f'<hp:sz width="{cur_width}" widthRelTo="ABSOLUTE" height="{cur_height}" '
        f'heightRelTo="ABSOLUTE" protect="0"/>'
        # 14. hp:pos
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
        f'allowOverlap="0" holdAnchorAndSO="0" '
        f'vertRelTo="PARA" horzRelTo="COLUMN" '
        f'vertAlign="TOP" horzAlign="LEFT" '
        f'vertOffset="0" horzOffset="0"/>'
        # 15. hp:outMargin
        f'<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        # 16. hp:shapeComment
        f"<hp:shapeComment>{filename} {pixel_width}x{pixel_height}</hp:shapeComment>"
        f"</hp:pic>"
        f"</hp:run>"
        f"</hp:p>"
    )


def update_content_hpf(content_hpf: str, image_entries: dict[str, str]) -> str:
    insert_pos = content_hpf.find("</opf:manifest>")
    if insert_pos == -1:
        raise ValueError("</opf:manifest> not found in Contents/content.hpf")

    add_lines: list[str] = []
    for key in sorted(image_entries.keys()):
        if f'id="{key}"' in content_hpf:
            continue
        href = image_entries[key]
        media_type = image_media_type(href)
        add_lines.append(
            f'<opf:item id="{key}" href="{href}" media-type="{media_type}" isEmbeded="1"/>'
        )

    if not add_lines:
        return content_hpf

    chunk = "\n    " + "\n    ".join(add_lines)
    return content_hpf[:insert_pos] + chunk + "\n  " + content_hpf[insert_pos:]


def parse_args() -> tuple[
    str, str, str | None, str | None, str, bool, str, int | None, int
]:
    parser = argparse.ArgumentParser(description="Embed image files into HWPX")
    _ = parser.add_argument("--hwpx", required=True, help="Input .hwpx path")
    _ = parser.add_argument(
        "--images-dir", required=True, help="Directory of PNG images"
    )
    _ = parser.add_argument(
        "--mapping", help="JSON mapping file for imageN -> file/caption"
    )
    _ = parser.add_argument(
        "--from-parsed",
        help="Parsed JSON from md_parser.py (collects type=='image_ref' paths)",
    )
    _ = parser.add_argument(
        "--base-dir",
        default=".",
        help=(
            "Base directory for resolving relative paths in --from-parsed "
            "(default: current directory)"
        ),
    )
    _ = parser.add_argument(
        "--auto-map",
        action="store_true",
        help="Automatically map placeholders to image filenames",
    )
    _ = parser.add_argument("--output", required=True, help="Output .hwpx path")
    _ = parser.add_argument(
        "--max-width",
        type=int,
        default=None,
        help="Maximum image width in pixels. Wider images will be proportionally resized. Default: no resize.",
    )
    _ = parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality when compressing (0-100). Default: 85.",
    )
    args = parser.parse_args()
    return (
        str(args.hwpx),
        str(args.images_dir),
        str(args.mapping) if args.mapping else None,
        str(args.from_parsed) if args.from_parsed else None,
        str(args.base_dir),
        bool(args.auto_map),
        str(args.output),
        int(args.max_width) if args.max_width is not None else None,
        int(args.quality),
    )


def validate_inputs(
    hwpx: str,
    images_dir: str,
    mapping_path: str | None,
    from_parsed: str | None,
    auto_map: bool,
    base_dir: str,
) -> None:
    if not os.path.isfile(hwpx):
        raise SystemExit(f"Error: HWPX file not found: {os.path.abspath(hwpx)}")
    if not os.path.isdir(images_dir):
        raise SystemExit(
            f"Error: images directory not found: {os.path.abspath(images_dir)}"
        )
    if not mapping_path and not from_parsed and not auto_map:
        raise SystemExit("Error: provide --mapping, --from-parsed, or --auto-map")
    if mapping_path and not os.path.isfile(mapping_path):
        raise SystemExit(
            f"Error: mapping file not found: {os.path.abspath(mapping_path)}"
        )
    if from_parsed and not os.path.isfile(from_parsed):
        raise SystemExit(
            f"Error: parsed JSON not found: {os.path.abspath(from_parsed)}"
        )
    if not os.path.isdir(base_dir):
        raise SystemExit(
            f"Error: base directory not found: {os.path.abspath(base_dir)}"
        )


def build_mapping(
    mapping_path: str | None,
    from_parsed: str | None,
    base_dir: str,
    auto_map: bool,
    images_dir: str,
    placeholders: set[str],
) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    if mapping_path:
        mapping = load_mapping(mapping_path)

    if from_parsed:
        parsed_mapping = load_mapping_from_parsed(from_parsed, base_dir)
        for key, value in parsed_mapping.items():
            if key not in mapping:
                mapping[key] = value

    if auto_map:
        mapping = auto_map_images(placeholders, images_dir, existing=mapping)

    if not mapping:
        raise SystemExit("Error: no images mapped for embedding")

    filtered = {}
    for key, value in mapping.items():
        if key in placeholders:
            filtered[key] = value

    if not filtered:
        raise SystemExit(
            "Error: mapping has no keys matching placeholders in section0.xml"
        )

    missing = [k for k in placeholders if k not in filtered]
    if missing:
        raise SystemExit(
            "Error: missing mapping for placeholders: "
            + ", ".join(sorted(missing, key=image_sort_key))
        )

    return filtered


def embed_images(
    hwpx: str,
    images_dir: str,
    mapping_path: str | None,
    from_parsed: str | None,
    base_dir: str,
    auto_map: bool,
    output: str,
    max_width: int | None = None,
    quality: int = 85,
) -> None:
    with zipfile.ZipFile(hwpx, "r") as zin:
        infos = zin.infolist()
        entries: dict[str, bytes] = {}
        for info in infos:
            entries[info.filename] = zin.read(info.filename)

    if "Contents/section0.xml" not in entries:
        raise SystemExit("Error: Contents/section0.xml not found in input HWPX")
    if "Contents/content.hpf" not in entries:
        raise SystemExit("Error: Contents/content.hpf not found in input HWPX")
    has_header_xml = "Contents/header.xml" in entries

    section_text = entries["Contents/section0.xml"].decode("utf-8")
    content_hpf = entries["Contents/content.hpf"].decode("utf-8")
    body_width = extract_body_width(section_text)
    header_xml = (
        entries["Contents/header.xml"].decode("utf-8") if has_header_xml else ""
    )
    if has_header_xml:
        header_xml = re.sub(
            r"<hh:binDataList\b[^>]*>.*?</hh:binDataList>",
            "",
            header_xml,
            flags=re.DOTALL,
        )
        header_xml = re.sub(r"<hh:binDataList\b[^>]*/>", "", header_xml)

    placeholders = set(PLACEHOLDER_RE.findall(section_text))
    if not placeholders:
        raise SystemExit(
            "Error: no <!--IMAGE:imageN--> placeholders found in section0.xml"
        )

    mapping = build_mapping(
        mapping_path, from_parsed, base_dir, auto_map, images_dir, placeholders
    )

    image_paths: dict[str, str] = {}
    image_entries: dict[str, str] = {}
    image_heights: dict[str, int] = {}
    image_pixel_dims: dict[str, tuple[int, int]] = {}
    image_filenames: dict[str, str] = {}

    sorted_keys = sorted(mapping.keys(), key=image_sort_key)
    for key in sorted_keys:
        map_item = mapping[key]
        file_name = map_item["file"]
        path_value = map_item.get("path", "")
        if path_value:
            image_path = path_value
        elif os.path.isabs(file_name):
            image_path = file_name
        else:
            image_path = os.path.join(images_dir, file_name)

        if not os.path.isfile(image_path):
            raise SystemExit(
                f"Error: image file not found for {key}: {os.path.abspath(image_path)}"
            )

        image_path = ensure_png_format(image_path)
        pixel_w, pixel_h = image_dimensions(image_path)
        hwpx_height = calc_hwpx_height(pixel_w, pixel_h, target_width=body_width)
        ext = normalize_image_extension(image_path)
        bin_data_name = f"{key}{ext}"

        image_paths[key] = image_path
        image_heights[key] = hwpx_height
        image_pixel_dims[key] = (pixel_w, pixel_h)
        image_filenames[key] = os.path.basename(image_path)
        image_entries[key] = f"BinData/{bin_data_name}"

    para_id_base = 7000000001
    for index, key in enumerate(sorted_keys):
        pic_id = 8000000001 + index
        inst_id = 8100000001 + index
        para_id = para_id_base + index
        z_order = 40 + index
        bin_id = key
        pixel_w, pixel_h = image_pixel_dims[key]
        org_width = pixel_w * 36
        org_height = pixel_h * 36
        dim_width = pixel_w * 75
        dim_height = pixel_h * 75
        pic_xml = make_pic_xml(
            bin_id=bin_id,
            cur_width=body_width,
            cur_height=image_heights[key],
            org_width=org_width,
            org_height=org_height,
            pixel_width=pixel_w,
            pixel_height=pixel_h,
            pic_id=pic_id,
            inst_id=inst_id,
            para_id=para_id,
            filename=image_filenames[key],
            z_order=z_order,
            dim_width=dim_width,
            dim_height=dim_height,
        )
        section_text = section_text.replace(f"<!--IMAGE:{key}-->", pic_xml)

    content_hpf = update_content_hpf(content_hpf, image_entries)

    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.abspath(hwpx) == os.path.abspath(output):
        tmp_out = output + ".tmp"
    else:
        tmp_out = output

    with zipfile.ZipFile(tmp_out, "w") as zout:
        for info in infos:
            info_out = zipfile.ZipInfo(info.filename)
            info_out.compress_type = info.compress_type

            if info.filename == "Contents/section0.xml":
                data = section_text.encode("utf-8")
            elif info.filename == "Contents/content.hpf":
                data = content_hpf.encode("utf-8")
            elif has_header_xml and info.filename == "Contents/header.xml":
                data = header_xml.encode("utf-8")
            else:
                data = entries[info.filename]

            zout.writestr(info_out, data)

        for key in sorted_keys:
            image_entry = image_entries[key]
            info_out = zipfile.ZipInfo(image_entry)
            info_out.compress_type = zipfile.ZIP_DEFLATED
            image_data = maybe_resize_image(image_paths[key], max_width, quality)
            zout.writestr(info_out, image_data)

    if tmp_out != output:
        _ = shutil.move(tmp_out, output)

    print(f"Embedded {len(mapping)} image(s) into {output}")


def main() -> None:
    (
        hwpx,
        images_dir,
        mapping_path,
        from_parsed,
        base_dir,
        auto_map,
        output,
        max_width,
        quality,
    ) = parse_args()
    validate_inputs(hwpx, images_dir, mapping_path, from_parsed, auto_map, base_dir)
    embed_images(
        hwpx,
        images_dir,
        mapping_path,
        from_parsed,
        base_dir,
        auto_map,
        output,
        max_width=max_width,
        quality=quality,
    )


if __name__ == "__main__":
    main()
