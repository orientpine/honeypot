# Learnings — hwpx-indent-preserve

## Project Structure
- Scripts: `plugins/hwpx-generator/skills/hwpx-core/scripts/`
- Tests: `plugins/hwpx-generator/skills/hwpx-core/tests/`
- Dev data: `dev/hwpx_indent/` (5장.md + 제안서_최종_포맷완료_v6.hwpx)

## Key Existing Files
- `md_parser.py` — current BULLET_RE ignores leading whitespace (ROOT CAUSE)
- `xml_writer.py` — has left_margin/indent override but unused
- `analyze_template.py` — --style-map does flat extraction only
- Test suite: 11 existing test files (pytest)

## Critical Constraints
- string-based XML ONLY (no lxml, no xml.etree.ElementTree)
- HWPUNIT_PER_LEVEL = 800 (1mm ≈ 283.46 HWPUNIT)
- indent step: 2-space per level
- DO NOT modify: cell_writer.py, build_hwpx.py, header.xml logic
- Working dir for pytest: `plugins/hwpx-generator/skills/hwpx-core`

## Bullet markers to support
- -, *, ◦, –, □ (all should detect indent_level)

## Numbered list patterns
- 1., 2., a., (1), ① etc.

## 2026-03-23 RED TDD learnings
- New RED file added: `plugins/hwpx-generator/skills/hwpx-core/tests/test_md_parser_indent.py`
- RED assertions should explicitly access `bullet["indent_level"]` so current parser fails with `KeyError` until GREEN implementation lands.
- Chapter-level fixture usage validated: `project_root / "dev" / "hwpx_indent" / "5장.md"`.

## 2026-03-23 RED TDD learnings (analyze_template indent levels)
- New RED file added: `plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_indent.py`.
- Real fixture path validated in test flow: `project_root / "dev" / "hwpx_indent" / "제안서_최종_포맷완료_v6.hwpx"`.
- `extract_style_map` currently returns flat keys (`bullet`, `heading_1`, `body`) without `bullet_level_N`, so explicit `bullet_level_0/1` assertions produce intentional RED failures.

## 2026-03-23 RED TDD learnings (md_merger)
- Added RED-only test module: `plugins/hwpx-generator/skills/hwpx-core/tests/test_md_merger.py`.
- Used importlib load pattern with explicit `pytest.fail(...)` on `FileNotFoundError/ImportError` so missing `scripts/md_merger.py` reports as test FAIL (not setup ERROR).
- Captured six scenario-oriented tests for future GREEN implementation: single-file passthrough, heading offset, inter-file separator, empty-file skip, body-only merge, list indent preservation.

## 2026-03-23 RED TDD learnings (xml_writer indent mapping)
- Added RED test module: `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_indent.py`.
- `build_fragment(parsed, styles)`-only path works for all coverage; no direct internal function calls needed.
- Current `build_bullet` ignores `indent_level` and `bullet_level_N` keys, so expected paraPrIDRef/leftMargin mapping assertions fail as intended.
- Current `build_fragment` treats `numbered_item` as default paragraph path, so numbered marker assertion is a reliable RED guard for future `build_numbered()` implementation.
