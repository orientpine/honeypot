"""Tests for sync_sources.py CLI."""

# pyright: reportMissingImports=false, reportMissingModuleSource=false
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
SYNC_SOURCES = str(SCRIPTS_DIR / "sync_sources.py")


def test_help() -> None:
    """--help exits 0 and mentions config."""
    result = subprocess.run(
        [sys.executable, SYNC_SOURCES, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "config" in result.stdout


def test_valid_source_name(tmp_path: Path, sample_sources_yaml: object) -> None:
    """Valid sources.yaml passes name validation in dry-run."""
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(dict(sample_sources_yaml)))  # type: ignore[arg-type]
    wiki = tmp_path / "wiki"
    wiki.mkdir(exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_invalid_source_name(tmp_path: Path) -> None:
    """Uppercase source name is rejected."""
    config = {
        "sources": [
            {
                "name": "INVALID-NAME",
                "type": "local",
                "path": str(tmp_path),
                "doc_path": "doc/",
            }
        ],
        "settings": {},
    }
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(config))
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_duplicate_source_name(tmp_path: Path) -> None:
    """Duplicate source names are rejected."""
    config = {
        "sources": [
            {
                "name": "dup",
                "type": "local",
                "path": str(tmp_path),
                "doc_path": "doc/",
            },
            {
                "name": "dup",
                "type": "local",
                "path": str(tmp_path),
                "doc_path": "doc/",
            },
        ],
        "settings": {},
    }
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(config))
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_two_local_sources_e2e(tmp_path: Path) -> None:
    """Two local sources sync end-to-end producing entries and logs."""
    src_a = tmp_path / "src_a" / "doc"
    src_b = tmp_path / "src_b" / "doc"
    src_a.mkdir(parents=True)
    src_b.mkdir(parents=True)
    (src_a / "guide.md").write_text("---\ntitle: Guide A\n---\nContent A")
    (src_b / "readme.md").write_text("---\ntitle: Readme B\n---\nContent B")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    config = {
        "sources": [
            {
                "name": "test_a",
                "type": "local",
                "path": str(src_a.parent),
                "doc_path": "doc/",
                "source_top": "Test",
                "source_category": "Project",
            },
            {
                "name": "test_b",
                "type": "local",
                "path": str(src_b.parent),
                "doc_path": "doc/",
                "source_top": "Test",
                "source_category": "Project",
            },
        ],
        "settings": {"entries_subdir": True, "id_strategy": "source_prefixed"},
    }
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(config))
    result = subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (tmp_path / "raw" / "entries" / "test_a").is_dir()
    assert (tmp_path / "raw" / "entries" / "test_b").is_dir()
    log = json.loads((tmp_path / "raw" / "ingest_log.json").read_text())
    assert len(log["entries"]) == 2
    sync_log = json.loads((tmp_path / "sync_log.json").read_text())
    assert "test_a" in sync_log["sources"]
    assert "test_b" in sync_log["sources"]


def test_dry_run(tmp_path: Path) -> None:
    """--dry-run produces no entry files."""
    src = tmp_path / "src" / "doc"
    src.mkdir(parents=True)
    (src / "note.md").write_text("---\ntitle: Note\n---\nContent")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    config = {
        "sources": [
            {
                "name": "dry_src",
                "type": "local",
                "path": str(src.parent),
                "doc_path": "doc/",
            }
        ],
        "settings": {},
    }
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(config))
    result = subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    entries_dir = tmp_path / "raw" / "entries" / "dry_src"
    assert not entries_dir.exists() or len(list(entries_dir.glob("*.md"))) == 0


def test_sync_log_structure(tmp_path: Path) -> None:
    """sync_log.json has expected top-level keys after sync."""
    src = tmp_path / "src" / "doc"
    src.mkdir(parents=True)
    (src / "note.md").write_text("---\ntitle: Note\n---\nContent")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    config = {
        "sources": [
            {
                "name": "log_src",
                "type": "local",
                "path": str(src.parent),
                "doc_path": "doc/",
            }
        ],
        "settings": {},
    }
    config_file = tmp_path / "sources.yaml"
    config_file.write_text(yaml.dump(config))
    subprocess.run(
        [
            sys.executable,
            SYNC_SOURCES,
            "--config",
            str(config_file),
            "--wiki-root",
            str(wiki),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    sync_log_path = tmp_path / "sync_log.json"
    assert sync_log_path.exists()
    sync_log = json.loads(sync_log_path.read_text())
    assert "last_sync" in sync_log
    assert "sources" in sync_log
    assert "log_src" in sync_log["sources"]
