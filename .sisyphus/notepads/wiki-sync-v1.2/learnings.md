# Learnings — wiki-sync-v1.2

## [2026-04-10] Initial Setup

### Project Structure
- Plugin root: `plugins/wiki-gen/skills/wiki-gen/`
- Scripts: `scripts/` (10 existing scripts: check_coverage.py, consolidate_analyze.py, diag_uncovered.py, diag_wikilink_resolution.py, finalize.py, generate_batches.py, ingest_obsidian.py, __init__.py, plan_batches.py, rebuild_index.py, verify_content.py + README.md)
- References: `references/` (command-details.md, ingest-spec.md, migration.md, scale-mode.md, taxonomy.md, writing-standards.md)
- Assets: `assets/` (absorb_agent.md, breakdown_agent.md, cleanup_agent.md, README.md, remediation_agent.md)

### Key Files
- `scripts/ingest_obsidian.py`: 674 lines — source of functions to extract
- `SKILL.md`: 249 lines — insertion point at line 197 (`## Command: wiki rebuild-index`)
- `scripts/README.md`: ~60 lines — needs 3 new script entries
- `pytest.ini`: exists at project root, has hwpx paths, needs wiki-gen paths added
- `plugins/wiki-gen/.claude-plugin/plugin.json`: currently v1.1.0

### Functions to EXTRACT to ingest_common.py
- Class: `Entry` dataclass + `to_markdown()` (lines 76-127)
- Constants: `DEFAULT_SKIP_DIR_NAMES` (lines 34-61), `DATE_YYYYMMDD`, `ISO_DATETIME` (lines 69-72)
- Functions: `log()`, `parse_csv_set()`, `slugify()`, `parse_yaml_frontmatter()`, `extract_heading_title()`, `extract_tags()`, `_valid_date()`, `_extract_path_year()`, `parse_date_fields()`, `coerce_tag_list()`, `coerce_alias_list()`, `count_markdown_files()`, `format_breakdown()`

### Functions to NOT EXTRACT (obsidian-specific)
- `parse_info_callout()` — Obsidian [!info] callout parser
- `walk_markdown()` — Obsidian vault walker
- `load_submodule_paths()` — git submodule specific
- `classify_source()` — Obsidian directory structure specific

### Import Direction Rule (CRITICAL)
- ALLOWED: `ingest_obsidian.py` → imports from `ingest_common.py`
- ALLOWED: `ingest_projects.py` → imports from `ingest_common.py`
- FORBIDDEN: `ingest_common.py` → imports from `ingest_obsidian.py`

### Metis Critical Issues
- **Q1**: `ingest_log.json` `file` field MUST be `"{source_name}/{base_name}"` format (not just `base_name`) — `verify_content.py:148` needs this
- **G4**: `sources.yaml` `name` field regex: `^[a-z0-9][a-z0-9_-]*$`, no duplicates
- **E1**: symlink infinite loop prevention: use `follow_symlinks=False`

### ingest_log.json Schema for source-prefixed entries
```json
{
  "file": "test_proj/guide.md",   // CRITICAL: source_name prefix REQUIRED
  "source_name": "test_proj",
  "id": "a1b2c3d4e5f6"           // 12 hex chars
}
```

### sync_log.json Location
- `wiki_root.parent / 'sync_log.json'` (NOT inside wiki/)

### subprocess Pattern (from finalize.py:44-49)
```python
subprocess.run([sys.executable, str(script_dir / 'xxx.py'), ...], check=True)
```

### ID Strategy
- Obsidian: `sha1(rel_str.encode())[:12]` (unchanged)
- Projects: `sha1(f"{source_name}:{rel_path}".encode())[:12]`

## [2026-04-10] Pytest Infrastructure

### Test Setup Notes
- `plugins/wiki-gen/skills/wiki-gen/tests/` added as a dedicated test package with `__init__.py` and `conftest.py`.
- Fixtures remain function-scoped and use `tmp_path` only; `sample_sources_yaml` returns a dict-shaped sources config with two local sources.
- `pytest.ini` now includes both hwpx core tests and wiki-gen tests in `testpaths`.
- `python3 -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ --collect-only` completed successfully with 0 collected items.
- `python3 -c "import ast; ..."` validated `conftest.py` syntax as `VALID`.

## [2026-04-10] Task 2 extraction

- Gold-output regression stayed stable after moving shared constants, Entry dataclass, and utility helpers into `scripts/ingest_common.py`.
- `ingest_obsidian.py` can keep script-mode compatibility with a top-level `from ingest_common import ...` because Python adds the script directory to `sys.path` when executed by path.

## [2026-04-10] Task 8 ingest_projects

- `ingest_projects.py` writes project-source entries under `raw/entries/{source_name}/`, keeping multi-source raw entries partitioned by source.
- `ingest_log.json` `entries[].file` must stay in `{source_name}/{base_name}` form; downstream `verify_content.py` resolves entry bodies from that prefixed path.
- Source-prefixed IDs via `sha1(f"{source_name}:{rel_path}")[:12]` avoid collisions when different project sources reuse the same relative doc path.

## [2026-04-10] Task 10 sync_sources

- `sync_sources.py` can stay idempotent by diffing `sync_log.json` content hashes first and skipping subprocess ingest when a source has no added/updated/deleted files.
- For project/local sources, backing up `raw/entries/{source_name}/` before re-running `ingest_projects.py` avoids stale filenames when titles or dates change and still lets the script restore state on ingest failure.
- `--dry-run` verification should check both `raw/ingest_log.json` and `sync_log.json`; they live at `wiki_root.parent`, not inside `wiki/`.
