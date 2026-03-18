# Learnings — hwpx-quality-upgrade

## Project Structure
- Scripts dir: `plugins/hwpx-generator/skills/hwpx-core/scripts/`
- fix_namespaces.py: `plugins/hwpx-generator/skills/hwpx-templates/scripts/`
- Dev data: `dev/` (작성.hwpx, 초안.hwpx, 3장.md, 4장.md, images/ 15 PNG)

## Key Constraints (from plan)
- stdlib-only for: zip_surgery, xml_writer, md_parser, image_embedder, fix_namespaces
- NO lxml in stdlib-only scripts
- NO ElementTree (ET) — string-based XML only
- analyze_template.py CAN use lxml (already does)
- proofread.py: string-based XML, read-only
- NO python-hwpx for writing
- NO cell_writer.py after ZIP surgery

## Windows-specific
- Use full Windows paths in scripts
- No `export VAR=value` syntax — Windows cmd only
- dev/ filenames contain Korean and spaces: `(양식) '27년도 전략연구사업 제안서_작성.hwpx`

## Evidence Paths
- `.sisyphus/evidence/task-{N}-*.{json|txt|xml}`

## [2026-03-18] Task 1: Golden Reference Analysis
- `analyze_template.py --style-map` 기본 출력에는 `image_caption`, `bullet_auto`가 없으므로, section0/header XML 역분석으로 후처리 보강이 필요함.
- 골든 `작성.hwpx`의 실제 `hp:pic`는 3개이며, 캡션 스타일의 대표값은 `paraPrIDRef=118`, `charPrIDRef=121`로 수렴함.
- `heading type=BULLET` paraPr ID는 문서별로 다르며(초안/작성 차이), 자동 불릿 대상 ID는 header.xml에서 직접 추출해야 정확함.
- 골든 문서에서 이중 불릿(자동 불릿 + 텍스트 선행 불릿 문자) 케이스는 0건으로 확인됨.
- `dev/images`는 PNG 15개가 맞지만 02~14 파일명은 계획의 기대명과 실제명이 다르므로 매핑 테이블이 필요함.

## [2026-03-19] Task 2: pytest Infrastructure

### Completed
- Created `plugins/hwpx-generator/skills/hwpx-core/tests/` directory structure
- Implemented `conftest.py` with 6 fixtures:
  - `project_root`: Returns project root (6 levels up from test file)
  - `dev_dir`: Points to `dev/` at project root
  - `scripts_dir`: Points to `plugins/hwpx-generator/skills/hwpx-core/scripts/`
  - `golden_dir`: Points to `dev/golden/`
  - `images_dir`: Points to `dev/images/`
  - `open_hwpx()`: Helper to open HWPX files as zipfiles
  - `load_json()`: Helper to load JSON files with UTF-8 encoding
  - `compare_json()`: Helper for recursive JSON comparison with detailed diffs

- Implemented `test_dev_data_exists.py` with 17 smoke tests across 6 test classes:
  - TestDevDirectoryExists (1 test)
  - TestHWPXFiles (2 tests for 작성/초안 HWPX files)
  - TestMarkdownFiles (2 tests for 3장/4장 MD files)
  - TestImagesDirectory (4 tests: dir exists, 15 PNG count, readability, naming convention)
  - TestGoldenDirectory (6 tests: dir exists, 3 JSON files exist + valid)
  - TestScriptsDirectory (1 test)

- Created `pytest.ini` at project root with:
  - testpaths = plugins/hwpx-generator/skills/hwpx-core/tests
  - Markers for smoke/unit/integration/slow tests
  - Short traceback format

### Key Learnings
1. **Path Resolution**: Test file is 6 levels deep from project root:
   - `plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py`
   - `.parent` x6 = project root

2. **Windows Path Handling**: Pathlib handles Windows paths correctly with forward slashes in Path objects

3. **UTF-8 Encoding**: JSON files with Korean characters require explicit `encoding='utf-8'` in open()

4. **Test Organization**: Grouping tests by class (TestDevDirectoryExists, etc.) improves readability and allows selective test runs

5. **Fixture Composition**: Helper fixtures like `open_hwpx()` and `load_json()` reduce boilerplate in test functions

### Test Results
All 17 tests PASS:
- 1 dev directory existence test
- 2 HWPX file tests (작성, 초안)
- 2 Markdown file tests (3장, 4장)
- 4 image directory tests (existence, count, readability, naming)
- 6 golden reference tests (3 JSON files, each with existence + validity)
- 1 scripts directory test

### Files Created
- `plugins/hwpx-generator/skills/hwpx-core/tests/__init__.py` (empty)
- `plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py` (152 lines)
- `plugins/hwpx-generator/skills/hwpx-core/tests/test_dev_data_exists.py` (181 lines)
- `pytest.ini` (22 lines at project root)

### Next Steps
- Task 3: Add unit tests for individual scripts (md_parser.py, xml_writer.py, etc.)
- Task 4: Add integration tests for full workflows
- Task 5: Add performance benchmarks for large HWPX files

## [2026-03-18] Task 3: md_parser Standard Image+Caption
- IMAGE_MD_RE: r"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$"
- CAPTION_ITALIC_RE: r"^\s*\*그림\s+([0-9]+-[0-9]+)\s*:\s*(.*?)\*\s*$"
- Block format: {"type":"image_ref", "id":None, "path":..., "alt":..., "caption":..., "caption_id":..., "filename":...}

## [2026-03-19] Task 3 Follow-up: Test Relocation
- `test_md_parser_images.py` must live under `plugins/hwpx-generator/skills/hwpx-core/tests/` to match `pytest.ini` discovery path.
- Test path resolution is safer via `conftest.py` fixtures (`project_root`, `scripts_dir`) than hardcoded `Path.parents[...]` from file location.

## [2026-03-19] Task 4: Complex Markdown Parsing (blockquote/circle/bold_label)
- `dev/4장.md` 실제 패턴 확인 결과, 목표 라인은 `> **목표**: ...` 형태이며 기존 blockquote+inline segment 파싱이 bold/plain 분할을 이미 정확히 생성함.
- standalone 라벨(`**[재난 분야]**`, `**[농업 분야]**`, `**[건설 분야]**` 등)은 기존 규칙에서 paragraph로 흡수되므로 `BOLD_LABEL_RE`를 bullet보다 먼저 검사해야 안정적으로 `bold_label` 블록으로 분기됨.
- `HEADING_RE`는 헤딩 텍스트를 보존하므로 `#### (1) ...` 토큰 보존은 그대로 유지됨. `dev/4장.md`에서는 H4가 주로 `①/②/③` 형태로 나타남.
- 실문서 검증 결과(`.sisyphus/evidence/task-4-complex-parsing.json`): blockquote=4, bold_label=6, separator=5, circle-numbered H4=12.
