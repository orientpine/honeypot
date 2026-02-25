#!/usr/bin/env python3
"""HWPX packaging, validation, and metadata utilities.

Extracted from build_math_hwpx.py for modularity.
Handles: XML validation, metadata updates, image manifest, ZIP packaging, HWPX validation.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from lxml import etree


def validate_xml(filepath: Path) -> None:
    """Check that an XML file is well-formed."""
    try:
        etree.parse(str(filepath))
    except etree.XMLSyntaxError as e:
        raise SystemExit(f"Malformed XML in {filepath.name}: {e}")


def update_metadata(content_hpf: Path, title: str | None, creator: str | None) -> None:
    """Update title and/or creator in content.hpf."""
    if not title and not creator:
        return

    tree = etree.parse(str(content_hpf))
    root = tree.getroot()
    ns = {"opf": "http://www.idpf.org/2007/opf/"}

    if title:
        title_el = root.find(".//opf:title", ns)
        if title_el is not None:
            title_el.text = title

    now = datetime.now(timezone.utc)
    iso_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    for meta in root.findall(".//opf:meta", ns):
        name = meta.get("name", "")
        if creator and name == "creator":
            meta.text = creator
        elif creator and name == "lastsaveby":
            meta.text = creator
        elif name == "CreatedDate":
            meta.text = iso_now
        elif name == "ModifiedDate":
            meta.text = iso_now
        elif name == "date":
            meta.text = now.strftime("%Y년 %m월 %d일")

    etree.indent(root, space="  ")
    tree.write(str(content_hpf), pretty_print=True, xml_declaration=True, encoding="UTF-8")


def pack_hwpx(input_dir: Path, output_path: Path) -> None:
    """Create HWPX archive with mimetype as first entry (ZIP_STORED)."""
    mimetype_file = input_dir / "mimetype"
    if not mimetype_file.is_file():
        raise SystemExit(f"Missing 'mimetype' in {input_dir}")

    all_files = sorted(
        p.relative_to(input_dir).as_posix()
        for p in input_dir.rglob("*")
        if p.is_file()
    )

    with ZipFile(output_path, "w", ZIP_DEFLATED) as zf:
        zf.write(mimetype_file, "mimetype", compress_type=ZIP_STORED)
        for rel_path in all_files:
            if rel_path == "mimetype":
                continue
            zf.write(input_dir / rel_path, rel_path, compress_type=ZIP_DEFLATED)


def validate_hwpx(hwpx_path: Path) -> list[str]:
    """Quick structural validation of the output HWPX."""
    errors: list[str] = []
    required = [
        "mimetype",
        "Contents/content.hpf",
        "Contents/header.xml",
        "Contents/section0.xml",
    ]

    try:
        from zipfile import BadZipFile
        zf = ZipFile(hwpx_path, "r")
    except BadZipFile:
        return [f"Not a valid ZIP: {hwpx_path}"]

    with zf:
        names = zf.namelist()
        for r in required:
            if r not in names:
                errors.append(f"Missing: {r}")

        if "mimetype" in names:
            content = zf.read("mimetype").decode("utf-8").strip()
            if content != "application/hwp+zip":
                errors.append(f"Bad mimetype content: {content}")
            if names[0] != "mimetype":
                errors.append("mimetype is not the first ZIP entry")
            info = zf.getinfo("mimetype")
            if info.compress_type != ZIP_STORED:
                errors.append("mimetype is not ZIP_STORED")

        for name in names:
            if name.endswith(".xml") or name.endswith(".hpf"):
                try:
                    etree.fromstring(zf.read(name))
                except etree.XMLSyntaxError as e:
                    errors.append(f"Malformed XML: {name}: {e}")

    return errors


def _add_images_to_manifest(hpf_path: Path, image_ids: dict,
                              problems: list) -> None:
    """Add image entries to content.hpf manifest for graph PNGs."""
    tree = etree.parse(str(hpf_path))
    root = tree.getroot()
    ns = {"opf": "http://www.idpf.org/2007/opf/"}

    manifest = root.find(".//opf:manifest", ns)
    if manifest is None:
        return

    for prob_num, item_id in image_ids.items():
        img_name = f"graph_{prob_num}.png"
        item = etree.SubElement(manifest, f"{{{ns['opf']}}}item")
        item.set("id", item_id)
        item.set("href", f"BinData/{img_name}")
        item.set("media-type", "image/png")
        item.set("isEmbeded", "1")

    etree.indent(root, space="  ")
    tree.write(str(hpf_path), pretty_print=True,
               xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    # Standalone validation mode
    if len(sys.argv) < 2:
        print("Usage: python hwpx_utils.py <file.hwpx>", file=sys.stderr)
        sys.exit(1)
    errors = validate_hwpx(Path(sys.argv[1]))
    if errors:
        print(f"INVALID: {sys.argv[1]}", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"VALID: {sys.argv[1]}")
