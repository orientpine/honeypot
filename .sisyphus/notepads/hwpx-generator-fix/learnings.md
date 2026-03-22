# HWPX Generator Fix — Learnings

## 2026-03-22 Session ses_2eb91c2a4ffexyHOxBUOKoTk9n

### analyze_template.py Key Facts
- `charpr_map` at lines 407-416: currently stores `{"fontSize_hu": int, "bold": bool}`
- Body filter at lines 655-665: BUGGY — uses hardcoded `cpr != "5"` exclusion
- table_cell selection at lines 780-806: uses raw most_common() without borderFill filtering
- table_header selection at lines 752-778: same issue
- Tests use lxml.etree (not stdlib xml.etree.ElementTree) — keep that pattern

### xml_writer.py Key Facts  
- Line 326: `left="283" right="283" top="141" bottom="141"` → WRONG, should all be 141
- Line 329: `textWidth="{max(width - 566, 0)}"` → WRONG, should be `width - 282`
- Test file: `tests/test_xml_writer_tables.py` — has existing tests that need value updates

### image_embedder.py Key Facts
- PIL is already imported (line 17): `from PIL import Image, UnidentifiedImageError`
- `parse_args()` at line 415: returns tuple of 7 values
- `MAX_IMAGE_HEIGHT = 70000` at line 23: currently raises ValueError when exceeded
- `calc_hwpx_height()` at lines 176-186: raises ValueError — needs to auto-resize + warn
- `load_mapping_from_parsed()` at lines 134-173: resolved_path error handling needs improvement
- No existing compression/--max-width flag

### hwpx-builder.md Facts
- Currently 426 lines (too long, need ≤ 350)
- Core 3 forbidden items to KEEP: lxml, 자체스크립트, hp:pic placement
- Add: 치환 우선 편집 (replace_text priority), 이중삽입 3원칙, 불릿 계층 규칙

### Test Infrastructure
- Tests use pytest
- conftest.py provides `scripts_dir` fixture
- Tests load modules via `importlib.util.spec_from_file_location`
- Tests are in `plugins/hwpx-generator/skills/hwpx-core/tests/`
- Existing test file for image_embedder: `test_image_embedder.py`

### Windows Path Notes
- Working directory: `C:\Users\BaekdongCha\Documents\honeypot`
- No `export` syntax — use direct commands
- Use `python -m pytest` from project root

- 2026-03-22 task-1: Replaced hardcoded body exclusion () with cascading charPr filter (non-bold+black -> black -> non-bold -> most-common warning); added borderFill color exclusion helper for table_header/table_cell and parsed charPr textColor from both attribute and hh:fontColor.
- 2026-03-22 task-1 correction: removed hardcoded body exclusion cpr != "5" and replaced with cascading data-driven filters by bold/text color.
