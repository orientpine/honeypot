# Learnings — hwpx-section-transplant

## [2026-03-23] Session start

### Codebase state
- `zip_surgery.py` ZipEntry has only 3 fields: filename, data, compress_type (P0 bug)
- `write_zip()` creates `zipfile.ZipInfo(name)` but only sets `compress_type` — all other metadata lost
- `read_zip()` reads `compress_type` from ZipInfo but nothing else
- HwpxSurgeon class is at lines 416–491; existing methods must NOT be broken
- Test infra: 21 test files, conftest.py has fixtures: project_root, dev_dir, scripts_dir, golden_dir, open_hwpx, load_json, compare_json
- Templates dir: `plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx` (round-trip test fixture)
- Working dir for all scripts: `plugins/hwpx-generator/skills/hwpx-core/`

### Key patterns
- ALL XML ops: string/regex only — NO lxml, no xml.etree, no BeautifulSoup
- `extract_children()` uses depth-counted parsing (lines 159–205)
- `assemble_section()` joins children with NO newlines between them
- `parse_section()` uses rfind for closing tag

### ZIP metadata fields needed (from HWPX_GENERATION_LESSONS.md)
Required fields: date_time, compress_type, external_attr(0x01800000), create_system(3), create_version(20), extract_version, flag_bits(0x0000), comment, extra(b''), internal_attr, volume

## [2026-03-23] T2 完了 — Test Fixtures + Chapter Detection Tests

### Deliverables
- ✅ conftest.py: 3 fixtures appended (make_header_xml, make_section_xml, make_test_hwpx)
- ✅ test_chapter_detection.py: 5 RED tests created
- ✅ pytest --collect-only: 5 tests collected
- ✅ pytest run: 5/5 FAIL (ModuleNotFoundError: section_transplant)
- ✅ Evidence saved: .sisyphus/evidence/task-2-test-fixtures.txt
- ✅ Git commit: bbae758

### Test Coverage
1. test_find_h1_headings — detect_headings() finds all H1 paragraphs
2. test_chapter_boundaries — extract_chapter_ranges() returns correct start/end indices
3. test_empty_chapter — handles chapters with only heading (no body)
4. test_content_before_first_h1 — cover page before first H1 detected
5. test_nested_hp_p_in_table — depth-counted parsing ignores nested hp:p in table cells

### Fixture Patterns
- make_header_xml(char_styles, para_styles) → bytes
  - char_styles: [(id, fontSize, bold=False), ...]
  - para_styles: [(id, align="JUSTIFY"), ...]
  - Returns: header.xml bytes with <hh:charPr>, <hh:paraPr> elements

- make_section_xml(paragraphs) → bytes
  - paragraphs: list of raw <hp:p>...</hp:p> strings
  - Returns: section0.xml bytes with <hs:sec> root

- make_test_hwpx(chapters=3, char_styles=None, para_styles=None, extra_paragraphs=None) → Path
  - Creates synthetic HWPX ZIP with:
    - Cover page paragraph (ID 100)
    - N chapters, each with H1 heading (ID 1000+ch_num) + body (ID 2000+ch_num)
    - Default styles: ID 1 = H1 (fontSize=1500, bold), ID 2 = body (fontSize=1000)
  - Returns: tmp_path / "test_synthetic.hwpx"

### Key Insights
- All fixtures use string-based XML (no lxml) — consistent with zip_surgery.py patterns
- make_test_hwpx imports zip_surgery.make_paragraph dynamically to avoid circular imports
- Tests import section_transplant functions dynamically (will exist in T3)
- HeadingInfo dataclass interface: h.index, h.text (needed for section_transplant.py)
- Depth-counted parsing already exists in zip_surgery.extract_children() (lines 159–205)

### Next Steps (T3)
- Implement section_transplant.py with:
  - detect_headings(children: list[str], header_bytes: bytes) → list[HeadingInfo]
  - extract_chapter_ranges(children: list[str], headings: list[HeadingInfo]) → dict[int, tuple[int, int]]
  - HeadingInfo dataclass with index, text, charPrIDRef fields

## [2026-03-23] T1 완료
- `ZipEntry`를 기존 3필드 순서를 유지한 채 메타데이터 10필드로 확장함.
- `read_zip()`에서 ZipInfo 메타데이터(date_time, external_attr, create_system, create_version, extract_version, flag_bits, comment, extra, internal_attr, volume) 전부 로드하도록 반영함.
- `write_zip()`에서 ZipInfo 생성 시 메타데이터를 복사하도록 반영함 (`volume`은 ZipInfo 속성이 아니므로 저장만).
- 신규 테스트 `tests/test_zip_surgery_metadata.py` 추가 후 RED→GREEN 완료, 최종 `3 passed`.
- `report-template.hwpx` round-trip 검증 결과: `external_attr/create_system` 불일치 0건 (`entries=14`).

## [2026-03-23] T3 완료
- `header.xml`의 `<hh:charPr>` 블록별 `fontSize`를 regex로 파싱해 최대 폰트 크기 집합(H1 후보 ID)을 안정적으로 산출함.
- `detect_headings()`는 `extract_children()` 결과(최상위 `<hp:p>` 목록)를 기준으로 동작하며, nested `<hp:p>`가 있는 경우 첫 nested 시작점 이전만 검사해 테이블 내부 가짜 H1 오검출을 차단함.
- `extract_chapter_ranges()`는 각 heading 인덱스를 시작점으로, 다음 heading 직전 또는 문서 끝까지의 inclusive 범위를 챕터 번호로 매핑함.
- `tests/test_chapter_detection.py` 최종 결과 5/5 PASS, 증적 파일 `.sisyphus/evidence/task-3-chapter-detection.txt` 생성 확인.

## [2026-03-23] T4 완료
- `section_transplant.py`에 `CharStyle`, `ParaStyle`, `StyleMap` dataclass를 추가해 `header.xml` 스타일 정보를 구조화함.
- `parse_header_styles()`를 regex-only로 구현해 `<hh:charPr>`/`<hh:paraPr>`를 파싱하고, char는 `(font_size, bold)`, para는 `align` 정보를 추출함.
- `build_style_mapping()`은 ID `"0"`을 모든 attr 타입에서 강제 `"0"→"0"`으로 고정하고, char는 `(font_size, bold)`, para는 `align` 기준으로 매핑함.
- 매칭 실패 시 원본 ID 유지 + `warnings.warn` 처리로 보수적 리매핑 정책을 적용함(추측 매핑 금지).
- `tests/test_style_remap.py` 추가: T4 5개 GREEN(`parse/build/zero/unmatched`), T5 2개 RED(`remap_style_ids` 미구현).
- 증적 저장: `.sisyphus/evidence/task-4-style-map.txt` (`5 passed, 2 failed`, 실패 원인 `ImportError: remap_style_ids`).

## [2026-03-23] T5 완료
- `remap_style_ids()`를 attribute-scoped regex 방식으로 구현해 `charPrIDRef/paraPrIDRef/borderFillIDRef/styleIDRef` 값만 치환하고 `<hp:t>` 텍스트는 보존함.
- bare `str.replace()` 없이 속성 값만 치환되도록 하여 `<hp:t>45명의 연구원</hp:t>` 같은 숫자 포함 본문 텍스트 손상을 방지함.
- ID `"0"`은 함수 내부에서 강제 보호(`src_id == "0"`일 때 원문 유지)하여 universal ID 치환을 차단함.
- `remap_chapters()`를 추가해 `<hp:secPr` 포함 단락은 drop, `<hp:pic` 포함 단락은 WARNING 후 리매핑 진행하도록 구현함.
- `pytest tests/test_style_remap.py -v` 재실행 결과 7/7 PASS, 증적 파일 `.sisyphus/evidence/task-5-remap-scoped.txt` 갱신 완료.
- 추가 검증 스니펫으로 `charPrIDRef="45"→"48"`, `paraPrIDRef="34"→"38"`, 텍스트 `45명의 연구원` 보존을 확인함.

## [2026-03-23] T6 완료
- `section_transplant.py` 끝에 `_import_zip_surgery()`와 `transplant_sections()`를 추가해 ZIP 로드→챕터 탐지→스타일 매핑/리매핑→범위 교체→section 재조립→output 저장 파이프라인을 연결함.
- `style_map` 미지정 시 header.xml 기반 자동 매핑을 사용하고, header 부재 시 ID `"0"` 보호 기본 매핑으로 폴백하도록 구성함.
- `dry_run=True`에서는 파일을 생성하지 않고 `mapping/source_ranges/target_ranges/output_path(None)`만 반환하도록 구현함.
- `tests/test_transplant_assembly.py`를 신규 추가해 기본 이식, 소스 텍스트 반영, 비이식 챕터 보존, dry-run 무출력, 누락 챕터 warning의 5개 시나리오를 검증함.
- `pytest tests/test_transplant_assembly.py -v` 결과 5/5 PASS, 증적 파일 `.sisyphus/evidence/task-6-assembly.txt` 갱신 완료.

## [2026-03-23] T7 완료
- `section_transplant.py` 끝에 argparse CLI(`main()` + `_parse_chapter_list()`)를 추가함. `--source`, `--target`, `--chapters`, `--style-map`, `--output`, `--dry-run` 6개 옵션 지원.
- `--dry-run` 미지정 시 `--output` 필수 — 누락 시 `parser.error()`로 exit 2 반환.
- `_parse_chapter_list()`에서 `argparse`를 lazy import하여 파일 최상위 import 금지 규칙 준수.
- `zip_surgery.py`의 `HwpxSurgeon` 클래스에 `transplant_from()` 메서드 추가. tempfile 기반으로 현재 상태를 저장 후 `transplant_sections()` 호출, 결과를 `self._modified`에 반영하는 구조.
- `transplant_from()`은 `dry_run=True` 시 매핑만 반환하고, `False` 시 section0.xml을 교체한 후 임시 파일 정리.
- basedpyright import cycle 경고는 lazy import 패턴의 구조적 한계로, 런타임에는 안전함 (기존 `_import_zip_surgery()`와 동일).
- 증적 파일 `.sisyphus/evidence/task-7-cli-dryrun.txt` 생성 확인.

## [2026-03-23] T8 완료
- `tests/test_transplant_e2e.py`를 신규 작성해 이식 파이프라인의 E2E 시나리오 7개(기본 이식, 비대상 챕터 보존, 스타일 ID 리매핑, ZIP 메타데이터 보존, dry-run 무출력, 누락 챕터 warning, hp:pic warning)를 모두 검증함.
- 소스/타깃 간 서로 다른 스타일 ID(소스 41/42·31/32, 타깃 51/52·61/62)를 갖는 합성 HWPX helper를 테스트 파일 내부에 두어 remap 경로를 통합 수준에서 강제 검증함.
- 실행 결과 `pytest tests/test_transplant_e2e.py -v` 기준 7/7 PASS 확인, 증적 파일 `.sisyphus/evidence/task-8-e2e.txt` 생성함.

## [2026-03-23] T9 완료

- plugin.json 버전 범프: 3.10.0 → 3.11.0
- marketplace.json 메타데이터 버전: 3.19.0 → 3.20.0
- AGENTS.md 버전 및 문서 업데이트 완료
  - WHERE TO LOOK 표에 section_transplant.py 행 추가
  - COMMANDS 섹션에 2개 CLI 명령어 추가
- README.md 버전 및 문서 업데이트 완료
  - hwpx-generator 주요 특징에 챕터 이식 기능 추가
  - 변경 이력 표에 3.20.0 항목 추가
- 증적 파일 생성: .sisyphus/evidence/task-9-version-sync.txt

## [2026-03-23] Fix: borderFill extraction added
- `section_transplant.py`에 `BorderFillStyle` dataclass 및 `StyleMap.border_fill_styles`를 추가해 header.xml의 borderFill 정의를 보관하도록 확장함.
- `parse_header_styles()`가 `<hh:borderFill>` 블록에서 `fillColor.value`와 `border.type`을 regex-only로 추출하도록 반영함(파서 import 없음).
- `build_style_mapping()`에 borderFill 속성 매칭(`fill_color`, `border_style`)을 추가해 `borderFillIDRef` 자동 리매핑을 수행하고, 불일치 시 경고 + 원본 ID 유지 폴백을 적용함.
- `detect_headings()`의 1차(fontSize) + 2차(텍스트 패턴 추출) 구조는 유지됨: 숫자 패턴 미일치 H1도 heading으로 수용하며 `chapter_num=0`으로 처리됨.
- 검증 결과: `pytest tests/test_style_remap.py tests/test_chapter_detection.py tests/test_transplant_assembly.py tests/test_transplant_e2e.py -v` → 24 passed.

## [2026-03-23] Final QA rerun (F4 scope v2)
- BorderFill fix 재검증: `BorderFillStyle` 선언, `parse_header_styles()`의 borderFill 추출, `build_style_mapping()`의 `borderFillIDRef` 매핑 루프 존재를 확인함.
- 챕터 탐지는 계획 의도와 일치: `max_size` 기반 H1 식별 후 텍스트 정규식은 chapter 번호 추출 보조로만 사용, 숫자 미일치 H1은 `chapter_num=0` 처리.
- 회귀 검증: 지정된 4개 테스트 파일 전체 24/24 PASS 재확인.
- 정적 검증: LSP 기준 error 없음(경고 다수는 기존 타입 엄격도 이슈이며 본 fix 범위 외).

## [2026-03-23] Final QA rerun
- Acceptance criteria cleared after the borderFill fix: `parse_header_styles()` now extracts `<hh:borderFill>`, and `build_style_mapping()` matches border fills by `(fill_color, border_style)`, removing the prior `borderFillIDRef/styleIDRef` `0 -> 0`-only failure.
- Scope clarification confirmed: `section_transplant.py` enforces `output_path` on non-dry-run paths, while `zip_surgery.py save(output_path=None)` remains legacy API behavior and was not modified by commit `d21ef52`.
- Regression status: full transplant suite passed (`27 passed`).
