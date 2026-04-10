"""Tests for ingest_projects.py — project doc/ markdown ingestion."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
INGEST_PROJECTS = str(SCRIPTS_DIR / "ingest_projects.py")


def test_help():
    result = subprocess.run(
        [sys.executable, INGEST_PROJECTS, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "source-root" in result.stdout


def test_basic_entry_creation(tmp_path):
    doc = tmp_path / "project" / "doc"
    doc.mkdir(parents=True)
    (doc / "guide.md").write_text(
        "---\ntitle: Guide\ntags: [test]\ndate: 2026-01-15\n---\nContent"
    )
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            INGEST_PROJECTS,
            "--source-root",
            str(doc),
            "--wiki-root",
            str(wiki),
            "--source-name",
            "my_proj",
            "--source-top",
            "Test",
            "--source-category",
            "Project",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    entries_dir = tmp_path / "raw" / "entries" / "my_proj"
    assert entries_dir.is_dir()
    entry_files = list(entries_dir.glob("*.md"))
    assert len(entry_files) == 1


def test_source_prefixed_id(tmp_path):
    doc = tmp_path / "doc"
    doc.mkdir()
    (doc / "note.md").write_text("---\ntitle: Note\n---\nBody")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    subprocess.run(
        [
            sys.executable,
            INGEST_PROJECTS,
            "--source-root",
            str(doc),
            "--wiki-root",
            str(wiki),
            "--source-name",
            "src_test",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    log = json.loads((tmp_path / "raw" / "ingest_log.json").read_text())
    e = log["entries"][0]
    assert len(e["id"]) == 12
    assert all(c in "0123456789abcdef" for c in e["id"])


def test_file_field_has_source_prefix(tmp_path):
    doc = tmp_path / "doc"
    doc.mkdir()
    (doc / "readme.md").write_text("---\ntitle: Readme\n---\nContent")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    subprocess.run(
        [
            sys.executable,
            INGEST_PROJECTS,
            "--source-root",
            str(doc),
            "--wiki-root",
            str(wiki),
            "--source-name",
            "my_source",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    log = json.loads((tmp_path / "raw" / "ingest_log.json").read_text())
    e = log["entries"][0]
    assert e["file"].startswith("my_source/"), f"file field missing prefix: {e['file']}"
    assert e["source_name"] == "my_source"


def test_empty_doc_dir(tmp_path):
    doc = tmp_path / "doc"
    doc.mkdir()
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            INGEST_PROJECTS,
            "--source-root",
            str(doc),
            "--wiki-root",
            str(wiki),
            "--source-name",
            "empty_src",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    log_path = tmp_path / "raw" / "ingest_log.json"
    if log_path.exists():
        log = json.loads(log_path.read_text())
        assert len(log.get("entries", [])) == 0


def test_id_no_collision_different_sources():
    id_a = hashlib.sha1("src_a:doc/guide.md".encode()).hexdigest()[:12]
    id_b = hashlib.sha1("src_b:doc/guide.md".encode()).hexdigest()[:12]
    assert id_a != id_b, f"ID collision: {id_a} == {id_b}"


def test_multiple_files(tmp_path):
    doc = tmp_path / "doc"
    doc.mkdir()
    for i in range(3):
        (doc / f"file{i}.md").write_text(f"---\ntitle: File {i}\n---\nContent {i}")
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    subprocess.run(
        [
            sys.executable,
            INGEST_PROJECTS,
            "--source-root",
            str(doc),
            "--wiki-root",
            str(wiki),
            "--source-name",
            "multi_src",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    log = json.loads((tmp_path / "raw" / "ingest_log.json").read_text())
    assert len(log["entries"]) == 3
