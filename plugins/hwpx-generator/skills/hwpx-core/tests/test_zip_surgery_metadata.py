#!/usr/bin/env python3
"""Round-trip metadata preservation tests for zip_surgery.py."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path


_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
_SPEC = importlib.util.spec_from_file_location(
    "zip_surgery", _SCRIPTS_DIR / "zip_surgery.py"
)
assert _SPEC and _SPEC.loader
_zip_surgery = importlib.util.module_from_spec(_SPEC)
sys.modules["zip_surgery"] = _zip_surgery
_SPEC.loader.exec_module(_zip_surgery)

read_zip = _zip_surgery.read_zip
write_zip = _zip_surgery.write_zip


def _template_hwpx_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "hwpx-templates"
        / "assets"
        / "report-template.hwpx"
    )


def _info_map(path: Path) -> dict[str, zipfile.ZipInfo]:
    with zipfile.ZipFile(path, "r") as zf:
        return {info.filename: info for info in zf.infolist()}


def test_read_zip_entries_expose_metadata_fields():
    entries, _order = read_zip(_template_hwpx_path())
    assert entries

    entry = entries[0]
    assert isinstance(entry.date_time, tuple)
    assert isinstance(entry.compress_type, int)
    assert isinstance(entry.external_attr, int)
    assert isinstance(entry.create_system, int)
    assert isinstance(entry.create_version, int)
    assert isinstance(entry.extract_version, int)
    assert isinstance(entry.flag_bits, int)
    assert isinstance(entry.comment, bytes)
    assert isinstance(entry.extra, bytes)
    assert isinstance(entry.internal_attr, int)


def test_round_trip_preserves_zipinfo_metadata(tmp_path: Path):
    source = _template_hwpx_path()
    output = tmp_path / "report-template.roundtrip.hwpx"

    entries, order = read_zip(source)
    write_zip(output, entries, order)

    original_infos = _info_map(source)
    roundtrip_infos = _info_map(output)

    assert list(original_infos.keys()) == list(roundtrip_infos.keys())

    for name, original in original_infos.items():
        roundtrip = roundtrip_infos[name]
        assert roundtrip.date_time == original.date_time
        assert roundtrip.compress_type == original.compress_type
        assert roundtrip.external_attr == original.external_attr
        assert roundtrip.create_system == original.create_system
        assert roundtrip.create_version == original.create_version
        assert roundtrip.extract_version == original.extract_version
        assert roundtrip.comment == original.comment
        assert roundtrip.extra == original.extra
        assert roundtrip.internal_attr == original.internal_attr

        assert roundtrip.external_attr == original.external_attr
        assert roundtrip.create_system == original.create_system


def test_write_zip_passes_all_metadata_to_zipinfo(tmp_path: Path, monkeypatch):
    source = tmp_path / "source.hwpx"
    output = tmp_path / "output.hwpx"

    info = zipfile.ZipInfo("Contents/section0.xml")
    info.compress_type = zipfile.ZIP_DEFLATED
    info.date_time = (2024, 1, 2, 3, 4, 6)
    info.external_attr = 0x01800000
    info.create_system = 3
    info.create_version = 63
    info.extract_version = 45
    info.flag_bits = 4
    info.comment = b"comment"
    info.extra = b"\x01\x00\x02\x00ab"
    info.internal_attr = 1

    with zipfile.ZipFile(source, "w") as zf:
        zf.writestr(info, b"payload")

    entries, order = read_zip(source)
    entry = entries[0]
    captured_infos: list[zipfile.ZipInfo] = []

    original_writestr = zipfile.ZipFile.writestr

    def capture_writestr(
        self, zinfo_or_arcname, data, compress_type=None, compresslevel=None
    ):
        if isinstance(zinfo_or_arcname, zipfile.ZipInfo):
            captured_infos.append(zinfo_or_arcname)
        return original_writestr(
            self, zinfo_or_arcname, data, compress_type, compresslevel
        )

    monkeypatch.setattr(zipfile.ZipFile, "writestr", capture_writestr)

    write_zip(output, entries, order)

    assert captured_infos
    written = captured_infos[0]
    assert written.date_time == entry.date_time
    assert written.compress_type == entry.compress_type
    assert written.external_attr == entry.external_attr
    assert written.create_system == entry.create_system
    assert written.create_version == entry.create_version
    assert written.extract_version == entry.extract_version
    assert written.flag_bits == entry.flag_bits
    assert written.comment == entry.comment
    assert written.extra == entry.extra
    assert written.internal_attr == entry.internal_attr
