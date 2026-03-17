#!/usr/bin/env python3
"""Embed PNG images into HWPX files via ZIP-level edits.

This script adds PNG files to BinData/, updates Contents/content.hpf,
and replaces <!--IMAGE:imageN--> placeholders in Contents/section0.xml
with <hp:pic> elements.
"""

import argparse
import json
import os
import re
import shutil
import struct
import zipfile


PLACEHOLDER_RE = re.compile(r"<!--IMAGE:(image\d+)-->")


def png_dimensions(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        _ = f.read(16)
        width_raw, height_raw = struct.unpack(">II", f.read(8))
    width = int(width_raw)
    height = int(height_raw)
    return width, height


def calc_hwpx_height(width: int, height: int) -> int:
    if width <= 0:
        raise ValueError("PNG width must be positive")
    return int((height / width) * 42520)


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
        if name.lower().endswith(".png"):
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


def make_pic_xml(image_key: str, height: int, pic_id: int) -> str:
    return (
        f'<hp:pic id="{pic_id}" zOrder="1" numberingType="PICTURE" '
        f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        f'dropcapstyle="None" href="" groupLevel="0">'
        f'<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="42520" y="0"/>'
        f'<hc:pt2 x="42520" y="{height}"/><hc:pt3 x="0" y="{height}"/>'
        f'</hp:imgRect><hp:imgClip left="0" right="0" top="0" bottom="0"/>'
        f'<hp:imgDim dimwidth="42520" dimheight="{height}"/>'
        f'<hc:img binaryItemIDRef="{image_key}" bright="0" contrast="0" '
        f'effect="REAL_PIC" alpha="0"/>'
        f'<hp:sz width="42520" widthRelTo="ABSOLUTE" height="{height}" '
        f'heightRelTo="ABSOLUTE" protect="0"/>'
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
        f'allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" '
        f'horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" '
        f'vertOffset="0" horzOffset="0"/></hp:pic>'
    )


def update_content_hpf(content_hpf: str, image_keys: list[str]) -> str:
    insert_pos = content_hpf.find("</opf:manifest>")
    if insert_pos == -1:
        raise ValueError("</opf:manifest> not found in Contents/content.hpf")

    add_lines: list[str] = []
    for key in image_keys:
        if f'id="{key}"' in content_hpf:
            continue
        add_lines.append(
            f'<opf:item id="{key}" href="BinData/{key}.png" media-type="image/png" isEmbeded="1"/>'
        )

    if not add_lines:
        return content_hpf

    chunk = "\n    " + "\n    ".join(add_lines)
    return content_hpf[:insert_pos] + chunk + "\n  " + content_hpf[insert_pos:]


def parse_args() -> tuple[str, str, str | None, bool, str]:
    parser = argparse.ArgumentParser(description="Embed PNG images into HWPX")
    _ = parser.add_argument("--hwpx", required=True, help="Input .hwpx path")
    _ = parser.add_argument(
        "--images-dir", required=True, help="Directory of PNG images"
    )
    _ = parser.add_argument(
        "--mapping", help="JSON mapping file for imageN -> file/caption"
    )
    _ = parser.add_argument(
        "--auto-map",
        action="store_true",
        help="Automatically map placeholders to image filenames",
    )
    _ = parser.add_argument("--output", required=True, help="Output .hwpx path")
    args = parser.parse_args()
    return (
        str(args.hwpx),
        str(args.images_dir),
        str(args.mapping) if args.mapping else None,
        bool(args.auto_map),
        str(args.output),
    )


def validate_inputs(
    hwpx: str, images_dir: str, mapping_path: str | None, auto_map: bool
) -> None:
    if not os.path.isfile(hwpx):
        raise SystemExit(f"Error: HWPX file not found: {hwpx}")
    if not os.path.isdir(images_dir):
        raise SystemExit(f"Error: images directory not found: {images_dir}")
    if not mapping_path and not auto_map:
        raise SystemExit("Error: provide --mapping or --auto-map")
    if mapping_path and not os.path.isfile(mapping_path):
        raise SystemExit(f"Error: mapping file not found: {mapping_path}")


def build_mapping(
    mapping_path: str | None,
    auto_map: bool,
    images_dir: str,
    placeholders: set[str],
) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    if mapping_path:
        mapping = load_mapping(mapping_path)

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
    auto_map: bool,
    output: str,
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

    section_text = entries["Contents/section0.xml"].decode("utf-8")
    content_hpf = entries["Contents/content.hpf"].decode("utf-8")

    placeholders = set(PLACEHOLDER_RE.findall(section_text))
    if not placeholders:
        raise SystemExit(
            "Error: no <!--IMAGE:imageN--> placeholders found in section0.xml"
        )

    mapping = build_mapping(mapping_path, auto_map, images_dir, placeholders)

    image_paths: dict[str, str] = {}
    image_heights: dict[str, int] = {}
    for key in sorted(mapping.keys(), key=image_sort_key):
        file_name = mapping[key]["file"]
        image_path = os.path.join(images_dir, file_name)
        if not os.path.isfile(image_path):
            raise SystemExit(f"Error: image file not found for {key}: {image_path}")

        width, height = png_dimensions(image_path)
        image_paths[key] = image_path
        image_heights[key] = calc_hwpx_height(width, height)

    for index, key in enumerate(sorted(mapping.keys(), key=image_sort_key)):
        pic_id = 8000000001 + index
        pic_xml = make_pic_xml(key, image_heights[key], pic_id)
        section_text = section_text.replace(f"<!--IMAGE:{key}-->", pic_xml)

    content_hpf = update_content_hpf(
        content_hpf, sorted(mapping.keys(), key=image_sort_key)
    )

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
            else:
                data = entries[info.filename]

            zout.writestr(info_out, data)

        for key in sorted(mapping.keys(), key=image_sort_key):
            image_entry = f"BinData/{key}.png"
            info_out = zipfile.ZipInfo(image_entry)
            info_out.compress_type = zipfile.ZIP_DEFLATED
            with open(image_paths[key], "rb") as f:
                zout.writestr(info_out, f.read())

    if tmp_out != output:
        _ = shutil.move(tmp_out, output)

    print(f"Embedded {len(mapping)} image(s) into {output}")


def main() -> None:
    hwpx, images_dir, mapping_path, auto_map, output = parse_args()
    validate_inputs(hwpx, images_dir, mapping_path, auto_map)
    embed_images(hwpx, images_dir, mapping_path, auto_map, output)


if __name__ == "__main__":
    main()
