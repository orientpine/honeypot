"""Tests for ingest_common.py — Entry dataclass, slugify, frontmatter parsing, tag/alias coercion."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ingest_common import (  # noqa: E402
    Entry,
    coerce_alias_list,
    coerce_tag_list,
    extract_heading_title,
    extract_tags,
    parse_yaml_frontmatter,
    slugify,
)


# ---------------------------------------------------------------------------
# Test 1: Entry.to_markdown() produces valid YAML frontmatter
# ---------------------------------------------------------------------------
def test_entry_to_markdown():
    e = Entry(
        id="abc123",
        date="2026-01-15",
        time="00:00:00",
        title="Test",
        source_type="project",
        source_path="",
        source_relative="doc/test.md",
        source_top="Test",
        source_category="Project",
        source_subcategory="",
    )
    md = e.to_markdown()
    assert md.startswith("---\n")
    assert "id: abc123" in md
    assert "title: Test" in md
    assert "date: '2026-01-15'" in md or "date: 2026-01-15" in md
    # body should appear after the closing ---
    parts = md.split("---")
    assert len(parts) >= 3  # opening ---, yaml, closing ---


# ---------------------------------------------------------------------------
# Test 2: slugify() basic
# ---------------------------------------------------------------------------
def test_slugify_basic():
    assert slugify("Hello World") == "Hello_World"
    assert slugify("test/file:name") == "test_file_name"


# ---------------------------------------------------------------------------
# Test 3: slugify() Korean characters preserved
# ---------------------------------------------------------------------------
def test_slugify_korean():
    result = slugify("한국어 테스트")
    assert "한국어" in result
    assert "테스트" in result


# ---------------------------------------------------------------------------
# Test 4: slugify() edge cases
# ---------------------------------------------------------------------------
def test_slugify_edge_cases():
    # Empty string → 'entry'
    assert slugify("") == "entry"
    # Only unsafe chars → 'entry'
    assert slugify("///***") == "entry"
    # Truncation to max_length
    long_text = "A" * 100
    result = slugify(long_text, max_length=20)
    assert len(result) <= 20


# ---------------------------------------------------------------------------
# Test 5: parse_yaml_frontmatter() valid
# ---------------------------------------------------------------------------
def test_parse_yaml_frontmatter_valid():
    text = "---\ntitle: My Note\ntags: [a, b]\n---\nBody text"
    fm, body = parse_yaml_frontmatter(text)
    assert fm is not None
    assert fm["title"] == "My Note"
    assert fm["tags"] == ["a", "b"]
    assert "Body text" in body


# ---------------------------------------------------------------------------
# Test 6: parse_yaml_frontmatter() no frontmatter
# ---------------------------------------------------------------------------
def test_parse_yaml_frontmatter_none():
    text = "Just plain text"
    fm, body = parse_yaml_frontmatter(text)
    assert fm is None
    assert body == text


# ---------------------------------------------------------------------------
# Test 7: parse_yaml_frontmatter() malformed YAML
# ---------------------------------------------------------------------------
def test_parse_yaml_frontmatter_malformed():
    text = "---\n: [invalid yaml\n---\nBody"
    fm, body = parse_yaml_frontmatter(text)
    # Should gracefully return None on YAML parse error
    assert fm is None
    assert body == text


# ---------------------------------------------------------------------------
# Test 8: coerce_tag_list() various inputs
# ---------------------------------------------------------------------------
def test_coerce_tag_list():
    assert coerce_tag_list(["#tag1", "tag2"]) == ["tag1", "tag2"]
    assert coerce_tag_list("tag1, tag2") == ["tag1", "tag2"]
    assert coerce_tag_list(None) == []
    # Single non-list, non-string value
    assert coerce_tag_list(42) == ["42"]


# ---------------------------------------------------------------------------
# Test 9: coerce_alias_list() various inputs
# ---------------------------------------------------------------------------
def test_coerce_alias_list():
    assert coerce_alias_list(["alias1", "alias2"]) == ["alias1", "alias2"]
    assert coerce_alias_list("single") == ["single"]
    assert coerce_alias_list(None) == []
    # Empty string
    assert coerce_alias_list("") == []


# ---------------------------------------------------------------------------
# Test 10: extract_heading_title() extracts H1
# ---------------------------------------------------------------------------
def test_extract_heading_title():
    text = "# My Title\n\nBody content"
    title, remaining = extract_heading_title(text)
    assert title == "My Title"
    assert "Body content" in remaining


def test_extract_heading_title_no_heading():
    text = "No heading here\nJust text"
    title, remaining = extract_heading_title(text)
    assert title is None
    assert remaining == text


# ---------------------------------------------------------------------------
# Test 11: extract_tags() finds inline #tags
# ---------------------------------------------------------------------------
def test_extract_tags():
    text = "This has #python and #데이터 tags, but not #123"
    tags = extract_tags(text)
    assert "python" in tags
    assert "데이터" in tags
    # Pure digit tags are excluded
    assert "123" not in tags


# ---------------------------------------------------------------------------
# Test 12 (regression): ingest_obsidian.py produces entries from test vault
# ---------------------------------------------------------------------------
def test_ingest_obsidian_regression(tmp_path: Path):
    vault = tmp_path / "vault" / "notes"
    vault.mkdir(parents=True)
    (vault / "note1.md").write_text(
        "---\ntitle: Note One\ntags: [test]\ndate: 2026-01-15\n---\nBody of note one\n",
        encoding="utf-8",
    )
    wiki = tmp_path / "wiki"
    wiki.mkdir()

    scripts_dir = Path(__file__).parent.parent / "scripts"
    result = subprocess.run(
        [
            sys.executable,
            str(scripts_dir / "ingest_obsidian.py"),
            "--source-root",
            str(tmp_path / "vault"),
            "--wiki-root",
            str(wiki),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ingest_obsidian failed: {result.stderr}"

    log_path = tmp_path / "raw" / "ingest_log.json"
    assert log_path.exists(), "ingest_log.json was not created"

    log_data = json.loads(log_path.read_text(encoding="utf-8"))
    assert len(log_data["entries"]) >= 1
    assert log_data["entries"][0]["title"] == "Note One"

    # Verify the entry file was actually written
    entries_dir = tmp_path / "raw" / "entries"
    entry_files = list(entries_dir.glob("*.md"))
    assert len(entry_files) >= 1
