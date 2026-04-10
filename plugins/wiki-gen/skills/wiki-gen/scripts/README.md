# wiki-gen Helper Scripts

Battle-tested Python scripts for the wiki-gen pipeline. All scripts accept CLI arguments — no hardcoded paths.

## Requirements
- Python 3.10+
- PyYAML (`pip install pyyaml`)

## Scripts

### Pipeline (run in order)

**ingest_obsidian.py** — Ingest an Obsidian vault into `raw/entries/`.
```bash
python ingest_obsidian.py --source-root /path/to/vault --wiki-root /path/to/project/wiki
```

**generate_batches.py** — Generate batch manifests from `raw/ingest_log.json`.
```bash
python generate_batches.py --wiki-root /path/to/project/wiki
```

**rebuild_index.py** — Rebuild `wiki/_index.md` and `wiki/_backlinks.json`.
```bash
python rebuild_index.py --wiki-root /path/to/project/wiki
```

**check_coverage.py** — Verify citation coverage and write `_absorb_log.json`.
```bash
python check_coverage.py --wiki-root /path/to/project/wiki
```

**verify_content.py** — Verify soft content coverage beyond direct citations.
```bash
python verify_content.py --wiki-root /path/to/project/wiki --entries-dir /path/to/project/raw/entries
```

**consolidate_analyze.py** — Analyze duplicates, stubs, bloated articles, and orphans.
```bash
python consolidate_analyze.py --wiki-root /path/to/project/wiki
```

**finalize.py** — Run the verification pipeline and write `_FINAL_REPORT.md`.
```bash
python finalize.py --wiki-root /path/to/project/wiki
```

### Planning / support

**plan_batches.py** — Print a grouped size summary and save `raw/batch_plan.json`.
```bash
python plan_batches.py --entries-dir /path/to/project/raw/entries --ingest-log /path/to/project/raw/ingest_log.json
```

### Diagnostics / remediation helpers

**diag_wikilink_resolution.py** — Diagnose whether `_index.md` wikilinks resolve by filename, alias, title-only, or not at all.
```bash
python diag_wikilink_resolution.py --wiki-root /path/to/project/wiki
```

**diag_uncovered.py** — Group uncovered entry IDs by batch and write `raw/uncovered_by_batch.json`.
```bash
python diag_uncovered.py --wiki-root /path/to/project/wiki --batches-dir /path/to/project/raw/batches
```

## Notes
- `--wiki-root` should point to the `wiki/` directory.
- Unless overridden, scripts derive `raw/` paths from `wiki_root.parent / "raw"`.
- All paths use `pathlib.Path` and work on Linux, macOS, and Windows.
