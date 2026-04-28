# Decisions — wiki-sync-v1.2

## [2026-04-10] Initial Architecture Decisions

### U1: ingest_common.py separate module (CONFIRMED)
Reason: DRY principle — shared by ingest_obsidian.py and ingest_projects.py

### U2: sources.yaml has obsidian options (CONFIRMED)
Format: `type: obsidian | local | git`

### U3: Partial success = exit 0 + warning (CONFIRMED)
Behavior: If one source fails, others succeed. exit 0 + stderr warning.

### U4: Separate sync_log.json (CONFIRMED)
Location: `wiki_root.parent / 'sync_log.json'`

### Test Strategy (CONFIRMED)
- pytest, tests-after approach
- No network tests (git clone mocked/skipped)
- Fixtures use tmp_path (no hardcoded paths)

### Gold-output test protocol (CRITICAL ORDER)
1. FIRST capture gold: run ingest_obsidian.py BEFORE extraction → save /tmp/gold/
2. THEN do extraction
3. THEN compare with /tmp/post/

## [2026-04-10] Task 2 refactor decision

- Kept `parse_info_callout`, `classify_source`, `load_submodule_paths`, and `walk_markdown` inside `ingest_obsidian.py` to preserve Obsidian-specific behavior and single-direction imports.

## [2026-04-10] Task 8 project ingest shape

- Kept `ingest_projects.py` as a separate lightweight walker instead of generalizing `walk_markdown()`, so project-doc ingestion stays independent from Obsidian-only behaviors.
- Preserved script execution compatibility by supporting direct-path execution for `ingest_common` imports while still allowing package-style relative imports.

## [2026-04-10] Task 10 sync orchestration shape

- Kept `sync_sources.py` as a subprocess orchestrator over `ingest_projects.py` / `ingest_obsidian.py` rather than re-implementing entry rendering, so source-specific ingest behavior stays centralized in the existing scripts.
- Used per-source temp ingest logs plus a final merged `raw/ingest_log.json`, which preserves downstream compatibility while letting unchanged sources reuse prior merged entries.
