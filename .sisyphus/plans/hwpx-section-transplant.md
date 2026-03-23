# HWPX Section Transplant — 범용 챕터 이식 도구

## TL;DR

> **Quick Summary**: HWPX 파일 간 챕터 단위 콘텐츠 이식 도구 구축. zip_surgery.py P0 버그 수정 + section_transplant.py 신규 스크립트 + HwpxSurgeon 확장.
> 
> **Deliverables**:
> - zip_surgery.py ZipInfo 전체 메타데이터 보존 (P0 fix)
> - section_transplant.py 범용 CLI + 라이브러리
> - HwpxSurgeon.transplant_from() 고수준 메서드
> - 자동 스타일 매핑 (header.xml 분석 기반)
> - 테스트 스위트
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 (ZIP fix) → Task 3 (chapter detection) → Task 5 (style remap) → Task 7 (assembly + CLI) → Task 9 (integration test)

---

## Context

### Original Request
HWPX 파일 두 개 사이에서 특정 챕터들을 추출하여 스타일 ID를 리맵핑한 뒤 재조립하는 스크립트가 필요. 즉각적인 사용 케이스는 제안서_최종_포맷완료_v6.hwpx에서 3~6장, 8~9장을 v1.2_cbd.hwpx로 이식하는 것이지만, 완전 범용 도구로 구현.

### Interview Summary
**Key Discussions**:
- header.xml 처리: 실행 에이전트가 두 파일의 header.xml 비교 분석 후 판단
- 구현 형태: 독립 CLI + HwpxSurgeon 클래스 확장 둘 다
- 챕터 1, 2, 7: 이미 v1.2_cbd에 포함됨 — 3,4,5,6,8,9만 이식
- 범용성: 완전 범용 도구 — 자동 스타일 매핑 포함

**Research Findings**:
- section0.xml은 flat sequential `<hp:p>` 구조 (nested elements 아님)
- 챕터 경계는 H1 heading(최대 fontSize) 문단으로 식별
- zip_surgery.py의 extract_children()이 depth-counted parsing 제공
- HWPX_GENERATION_LESSONS.md에서 v24 파이프라인의 ZIP 보존 레시피 검증됨
- 기존 테스트 인프라 존재 (18개 테스트, conftest.py fixtures)

### Metis Review
**Identified Gaps** (addressed):
- paragraph id 충돌: 이식 시 기존 ID 유지 (한글은 id 중복 허용)
- hp:secPr 처리: 이식 문단에서 secPr 제거, 타겟의 secPr 유지
- charPrIDRef="0" 보호: ID "0"은 모든 리맵에서 제외
- 바이너리 데이터(이미지): v1은 XML만 이식, 이미지 참조 경고 출력
- 챕터 경계 탐지: fontSize 기반 + 텍스트 패턴(`N. 제목`) 이중 검증
- 첫 H1 이전 콘텐츠(표지 등): 타겟 소유, 이식 대상 아님

---

## Work Objectives

### Core Objective
어떤 HWPX 파일 간에도 챕터 단위 콘텐츠를 안전하게 이식할 수 있는 범용 도구를 hwpx-core 스킬에 추가한다.

### Concrete Deliverables
- `plugins/hwpx-generator/skills/hwpx-core/scripts/section_transplant.py` (CLI + 라이브러리)
- `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` (P0 fix)
- `tests/test_zip_surgery_metadata.py` (ZIP 메타데이터 보존 테스트)
- `tests/test_chapter_detection.py` (챕터 경계 탐지 테스트)
- `tests/test_style_remap.py` (스타일 ID 리맵 테스트)
- `tests/test_transplant_e2e.py` (통합 테스트)

### Definition of Done
- [ ] `python section_transplant.py --source a.hwpx --target b.hwpx --chapters 3,4,5 --output result.hwpx` 실행 성공
- [ ] `python zip_surgery.py validate target.hwpx result.hwpx` 통과 (section 외 바이트 동일)
- [ ] 이식된 챕터 텍스트가 결과 파일에 존재
- [ ] 소스 전용 스타일 ID가 결과 파일에 없음 (모두 리맵됨)
- [ ] 비이식 챕터(1,2,7)가 타겟과 바이트 동일

### Must Have
- depth-counted paragraph boundary detection (기존 extract_children 패턴)
- attribute-scoped regex for style remapping (bare string replace 절대 금지)
- charPrIDRef/paraPrIDRef/borderFillIDRef/styleIDRef 4종 리맵
- ID "0" 리맵 제외
- --dry-run 모드 (실제 파일 변경 없이 매핑 테이블 출력)
- 이미지 참조 경고 (hp:pic 발견 시 WARNING)

### Must NOT Have (Guardrails)
- lxml, xml.etree.ElementTree, BeautifulSoup 등 XML 파서 import 금지
- 소스/타겟 원본 파일 수정 금지 (항상 --output으로 출력)
- bare string replace로 스타일 ID 치환 금지 (숫자 텍스트 내용 훼손 위험)
- child elements 사이에 newline 삽입 금지
- multi-section 파일(section1.xml) 처리 금지 (v1 범위 외)
- linesegarray 생성/수정 금지 (원본 보존)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (18 tests, conftest.py)
- **Automated tests**: TDD — RED → GREEN → REFACTOR
- **Framework**: pytest (기존 패턴 따름)
- **Each task**: 테스트 먼저 작성 → 구현 → 테스트 통과

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Script/Module**: Use Bash (python3 CLI) — Run command, assert exit code + output
- **Library**: Use Bash (pytest) — Run unit tests, verify pass count

---

### Working Directory

> **Base**: `plugins/hwpx-generator/skills/hwpx-core/` (skill root)
> All task paths are relative to this base unless prefixed with repo root.
> - Scripts: `scripts/section_transplant.py`, `scripts/zip_surgery.py`
> - Tests: `tests/test_*.py`, `tests/conftest.py`
> - Template: `../hwpx-templates/assets/report-template.hwpx`
> - Repo-root files (AGENTS.md, README.md): use `../../../../` prefix or absolute path

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: zip_surgery.py ZipEntry P0 fix [deep]
├── Task 2: Test fixtures for transplant tests [quick]
└── Task 3: Chapter boundary detection module [deep]

Wave 2 (After Wave 1 — core logic):
├── Task 4: Header.xml style map extraction [deep]
├── Task 5: Style ID remapping engine [deep]
└── Task 6: Section assembly (replace chapter ranges) [deep]

Wave 3a (After Wave 2 — CLI):
└── Task 7: CLI + HwpxSurgeon extension [unspecified-high]

Wave 3b (After Wave 3a — integration test):
└── Task 8: Integration test suite [deep]

Wave 3c (After Wave 3b — docs):
└── Task 9: Version bump + docs [quick]

Wave FINAL (After ALL tasks):
├── F1: Plan compliance audit [oracle]
├── F2: Code quality review [unspecified-high]
├── F3: Real manual QA [unspecified-high]
└── F4: Scope fidelity check [deep]
-> Present results -> Get explicit user okay

Critical Path: T1 → T3 → T5 → T6 → T7 → T8 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Waves 1 & 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| T1 | — | T6, T7, T8 |
| T2 | — | T3, T4, T5, T6 |
| T3 | T2 | T5, T6 |
| T4 | T2 | T5 |
| T5 | T3, T4 | T6, T7 |
| T6 | T1, T5 | T7, T8 |
| T7 | T6 | T8 |
| T8 | T7 | T9 |
| T9 | T8 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T1 `deep`, T2 `quick`, T3 `deep`
- **Wave 2**: 3 tasks — T4 `deep`, T5 `deep`, T6 `deep`
- **Wave 3**: 3 tasks — T7 `unspecified-high`, T8 `deep`, T9 `quick`
- **FINAL**: 4 tasks — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs


- [x] 1. zip_surgery.py ZipInfo 메타데이터 전체 보존 (P0 Fix)

  **What to do**:
  - `ZipEntry` dataclass에 `date_time`, `external_attr`, `create_system`, `create_version`, `extract_version`, `flag_bits`, `comment`, `extra`, `internal_attr`, `volume` 필드 추가
  - `read_zip()`에서 새 필드들을 `zipfile.ZipInfo`에서 읽어오도록 수정
  - `write_zip()`에서 `ZipInfo` 생성 시 모든 속성을 복사하도록 수정 (L113 부근)
  - 테스트 파일 `tests/test_zip_surgery_metadata.py` 작성 (먼저 RED, 구현 후 GREEN)
  - 테스트: `report-template.hwpx`를 round-trip하여 모든 ZipInfo 속성 동일성 검증

  **Must NOT do**:
  - `ZipEntry`의 기존 API (filename, data, compress_type) 변경 금지
  - `HwpxSurgeon` 클래스의 동작 변경 금지 (이 태스크는 순수하게 ZipEntry/read_zip/write_zip만)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 기존 코드 수정 + 테스트 작성, 하위 호환성 보장 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T2, T3)
  - **Parallel Group**: Wave 1
  - **Blocks**: T6, T7, T8
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:52-58` — `ZipEntry` dataclass 정의 (현재 3개 필드만)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:74-93` — `read_zip()` 함수 (ZipInfo에서 compress_type만 읽음)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:96-116` — `write_zip()` 함수 (ZipInfo 생성 시 속성 누락)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:416-467` — `HwpxSurgeon` 클래스 (이 태스크에서는 건드리지 않음)
  - `plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx` — round-trip 테스트용 HWPX 파일
  - 외부 지식: `HWPX_GENERATION_LESSONS.md` (isd-project-2027 외부 폴더)의 ZIP 보존 레시피 — 필수 복사 속성: date_time, compress_type, external_attr(0x01800000), create_system(3), create_version(20), extract_version, flag_bits(0x0000), comment, extra(b''), internal_attr, volume

  **Acceptance Criteria**:
  - [ ] `ZipEntry` dataclass에 10개 새 필드 추가됨
  - [ ] `pytest tests/test_zip_surgery_metadata.py` → PASS
  - [ ] round-trip 테스트: `report-template.hwpx` 읽기 → 쓰기 → 모든 entry의 external_attr, create_system 등 동일

  **QA Scenarios:**
  ```
  Scenario: ZIP round-trip preserves all metadata
    Tool: Bash (python3)
    Preconditions: Working directory = plugins/hwpx-generator/skills/hwpx-core/
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python3 -c "import sys; sys.path.insert(0,'scripts'); from zip_surgery import read_zip, write_zip; e,o = read_zip('../hwpx-templates/assets/report-template.hwpx'); write_zip('/tmp/rt.hwpx', e, o)"
      2. python3 -c "import zipfile; a=zipfile.ZipFile('../hwpx-templates/assets/report-template.hwpx'); b=zipfile.ZipFile('/tmp/rt.hwpx'); [print(f'{ai.filename}: ext={ai.external_attr==bi.external_attr} cs={ai.create_system==bi.create_system}') for ai,bi in zip(a.infolist(),b.infolist())]"
    Expected Result: All entries show True for all attribute comparisons
    Evidence: .sisyphus/evidence/task-1-zip-roundtrip.txt
  ```

  **Commit**: YES (group 1)
  - Message: `fix(hwpx-core): preserve all ZipInfo metadata in zip_surgery.py`
  - Files: `scripts/zip_surgery.py`, `tests/test_zip_surgery_metadata.py`
  - Pre-commit: `pytest tests/test_zip_surgery_metadata.py`

- [x] 2. 트랜스플랜트 테스트 픽스처 + 챕터 탐지 테스트 (RED)

  **What to do**:
  - conftest.py에 테스트 픽스처 추가:
    - `make_test_hwpx()`: 합성 HWPX 생성 (3개 챕터, 알려진 스타일 ID, 테이블 포함)
    - `make_section_xml()`: 단락 리스트로 section0.xml 생성
    - `make_header_xml()`: 스타일 정의를 포함한 header.xml 생성
  - `tests/test_chapter_detection.py` 작성 (RED 상태):
    - test_find_h1_headings: H1 단락 탐지
    - test_chapter_boundaries: 챕터 시작/끝 인덱스
    - test_empty_chapter: 빈 챕터 처리
    - test_content_before_first_h1: 표지 영역 처리
    - test_nested_hp_p_in_table: depth-counted 탐지

  **Must NOT do**:
  - 구현 코드 작성 금지 (테스트만)
  - 실제 HWPX 파일 의존 금지 (합성 데이터만)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 테스트 픽스처 + 테스트 코드 작성만, 단순 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T3)
  - **Parallel Group**: Wave 1
  - **Blocks**: T3, T4, T5, T6
  - **Blocked By**: None

  **References**:
  - `tests/conftest.py` — 기존 픽스처 패턴 (project_root, scripts_dir, golden_dir, open_hwpx)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:208-218` — `assemble_section()` — section XML 조립 방법
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:237-258` — `make_paragraph()` — 테스트 단락 생성 형식
  - `plugins/hwpx-generator/skills/hwpx-core/templates/base/Contents/section0.xml` — 기본 section0.xml 구조 참조

  **Acceptance Criteria**:
  - [ ] conftest.py에 `make_test_hwpx()`, `make_section_xml()`, `make_header_xml()` 픽스처 존재
  - [ ] `pytest tests/test_chapter_detection.py` 실행 시 5개 테스트 모두 FAIL (구현 없으므로)

  **QA Scenarios:**
  ```
  Scenario: Test fixtures create valid synthetic HWPX
    Tool: Bash (pytest)
    Preconditions: conftest.py updated with new fixtures
    Steps:
      1. pytest tests/test_chapter_detection.py --collect-only
      2. Verify 5 test items collected
      3. pytest tests/test_chapter_detection.py (expect all FAIL)
    Expected Result: 5 collected, 5 FAILED (ImportError for section_transplant)
    Evidence: .sisyphus/evidence/task-2-test-fixtures.txt
  ```

  **Commit**: YES (group 2)
  - Message: `test(hwpx-core): add transplant test fixtures and chapter detection tests`
  - Files: `tests/conftest.py`, `tests/test_chapter_detection.py`

- [x] 3. 챕터 경계 탐지 모듈 구현

  **What to do**:
  - `section_transplant.py`에 챕터 탐지 함수 구현:
    - `detect_headings(children: list[str], header_xml: bytes) -> list[HeadingInfo]`:
      - header.xml에서 charPr fontSize 추출, 최대 fontSize = H1
      - 각 `<hp:p>`에서 charPrIDRef 추출, H1과 매치 시 heading으로 판단
      - 텍스트 패턴 검증: `r'^[0-9]+\.'` 또는 `r'^\d+\.'` (이중 확인)
    - `extract_chapter_ranges(children, headings) -> dict[int, tuple[int, int]]`:
      - 챕터 번호 → (start_idx, end_idx) 매핑
      - 첫 H1 이전 콘텐츠 = 표지/서문 (챕터 0으로 취급)
      - 마지막 H1부터 다음 H1 전까지 = 해당 챕터 범위
  - T2의 RED 테스트를 GREEN으로 전환

  **Must NOT do**:
  - XML 파서 사용 금지 (regex + string 조작만)
  - extract_children() 재구현 금지 (기존 zip_surgery.py 것 import)
  - charPrIDRef 매칭을 위해 header.xml을 수정하는 것 금지 (읽기만)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: depth-counted 파싱 로직, header.xml 분석, 엣지 케이스 처리 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T2 — but 실질적으로 T2 완료 후 시작)
  - **Parallel Group**: Wave 1
  - **Blocks**: T5, T6
  - **Blocked By**: T2 (테스트 픽스처 필요)

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:159-205` — `extract_children()` depth-counted parser (이 패턴 그대로 사용)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:124-156` — `parse_section()` 루트 태그 분리
  - 스타일 분석 리포트 패턴: `스타일_분석_리포트_v3.md` 섬션 10 (문서 내 제목 구조) — 챕터 heading은 charPr fontSize > 1200 (주로 15pt=1500)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` L626 부근 — heading 탐지 기존 fontSize 로직 참조

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_chapter_detection.py` → 5/5 PASS
  - [ ] detect_headings()가 합성 HWPX에서 H1 heading 정확히 탐지
  - [ ] 빈 챕터, 표지 영역, 중첩 hp:p 케이스 모두 처리

  **QA Scenarios:**
  ```
  Scenario: Chapter detection with 3-chapter synthetic HWPX
    Tool: Bash (pytest)
    Preconditions: test fixtures from T2, section_transplant.py from this task
    Steps:
      1. pytest tests/test_chapter_detection.py -v
      2. Verify all 5 tests pass
      3. Check test output for correct chapter indices
    Expected Result: 5 passed, 0 failed
    Evidence: .sisyphus/evidence/task-3-chapter-detection.txt
  ```

  **Commit**: YES (group 3)
  - Message: `feat(hwpx-core): add chapter boundary detection to section_transplant.py`
  - Files: `scripts/section_transplant.py`
  - Pre-commit: `pytest tests/test_chapter_detection.py`


- [x] 4. Header.xml 스타일 맵 추출 및 비교

  **What to do**:
  - `section_transplant.py`에 스타일 분석 함수 추가:
    - `parse_header_styles(header_bytes: bytes) -> StyleMap`:
      - header.xml에서 charPr 목록 추출 (id, fontSize, bold, fontRef)
      - paraPr 목록 추출 (id, align, heading type/level, bulletRef)
      - borderFill 목록 추출 (id, background color, border style)
    - `build_style_mapping(source_styles: StyleMap, target_styles: StyleMap) -> dict`:
      - charPr 매칭: fontSize + bold + fontRef가 동일한 쌍 찾기
      - paraPr 매칭: 연관 기반 (H1 charPr와 함께 쓰이는 paraPr를 매칭)
      - borderFill 매칭: background color + border style로 매칭
      - ID "0"은 항상 "0"으로 매핑 (리맵 제외)
      - 매칭 실패 시 경고 + 원본 ID 유지 (폴백)
  - `tests/test_style_remap.py` 테스트 작성 (RED)

  **Must NOT do**:
  - XML 파서로 header.xml 파싱 금지 (regex만 사용)
  - header.xml 수정 금지 (읽기만)
  - 애매한 매칭에서 추측하여 잘못 매핑하는 것 금지 (매칭 실패 = 원본 유지)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: header.xml 구조 분석, 스타일 속성 비교 로직
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T5, T6 in Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: T5
  - **Blocked By**: T2 (테스트 픽스처)

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — 기존 스타일 추출 로직 (extract_style_map, charpr_map 패턴)
  - `plugins/hwpx-generator/skills/hwpx-core/references/hwpx-format.md` — HWPX header.xml charPr/paraPr/borderFill 구조
  - 스타일_분석_리포트_v3.md 섬션 4-5 — paraPr ID 전체 스펙, charPr ID 전체 스펙 (글꼴 크기/볼드/색상 매핑)
  - style_map.json (김병진차백동/output/) — v1.2_cbd 스타일 맵 예시

  **Acceptance Criteria**:
  - [ ] parse_header_styles()가 charPr, paraPr, borderFill 정확히 추출
  - [ ] build_style_mapping()이 동일 fontSize+bold 쌍을 정확히 매칭
  - [ ] ID "0"은 매핑에서 제외됨
  - [ ] 매칭 실패 시 경고 출력 + 원본 ID 유지

  **QA Scenarios:**
  ```
  Scenario: Style map extraction from synthetic headers
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/test_style_remap.py::test_parse_header_styles -v
      2. pytest tests/test_style_remap.py::test_build_mapping -v
    Expected Result: All pass, correct charPr matching by fontSize+bold
    Evidence: .sisyphus/evidence/task-4-style-map.txt

  Scenario: ID 0 excluded from remapping
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/test_style_remap.py::test_id_zero_excluded -v
    Expected Result: mapping['charPrIDRef']['0'] == '0' always
    Evidence: .sisyphus/evidence/task-4-id-zero.txt
  ```

  **Commit**: YES (group 4)
  - Message: `feat(hwpx-core): add style map extraction and comparison`
  - Files: `scripts/section_transplant.py`, `tests/test_style_remap.py`

- [x] 5. 스타일 ID 리매핑 엔진

  **What to do**:
  - `section_transplant.py`에 리매핑 함수 추가:
    - `remap_style_ids(paragraph_xml: str, mapping: dict) -> str`:
      - attribute-scoped regex: `r'(charPrIDRef=")(\d+)(")'` 패턴으로 치환
      - 4종 리매핑: charPrIDRef, paraPrIDRef, borderFillIDRef, styleIDRef
      - ID "0" 제외
      - 테이블 셀 내부의 중첩 단락도 처리 (하나의 hp:p 문자열 내 모든 속성 리매핑)
    - `remap_chapters(chapters_xml: list[str], mapping: dict) -> list[str]`:
      - 각 챕터의 모든 단락에 remap_style_ids 적용
      - hp:secPr 단락 발견 시 제거 (타깃의 secPr 유지)
      - hp:pic 발견 시 WARNING 출력 (이미지 참조 끊김 경고)
  - T4의 RED 테스트를 GREEN으로 전환

  **Must NOT do**:
  - bare string replace 사용 금지 (텍스트 콘텐츠의 숫자 훼손 위험)
  - `<hp:t>` 내부 텍스트 내용 수정 금지
  - 타깃 파일의 secPr 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: regex 로직 정확성, 엣지 케이스(ID=0, 중첩 단락, secPr)
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after T3+T4
  - **Blocks**: T6, T7
  - **Blocked By**: T3, T4

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:303-315` — `replace_text_in_section()` 패턴 (단, bare replace는 부적합)
  - `plugins/hwpx-generator/skills/hwpx-core/references/zip-surgery-guide.md` — 안전 규칙 (string-only, no parser)
  - Metis 분석 — G3 guardrail: attribute-scoped regex 필수

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_style_remap.py` → ALL PASS
  - [ ] charPrIDRef="45"가 charPrIDRef="48"로 치환되지만, `<hp:t>45명</hp:t>` 텍스트는 변경 없음
  - [ ] ID "0" 처리: charPrIDRef="0"은 치환되지 않음
  - [ ] secPr 단락 발견 시 제거됨
  - [ ] hp:pic 발견 시 WARNING 메시지 출력

  **QA Scenarios:**
  ```
  Scenario: Attribute-scoped regex remapping
    Tool: Bash (python3)
    Steps:
      1. 합성 XML: '<hp:p paraPrIDRef="34"><hp:run charPrIDRef="45"><hp:t>45명의 연구원</hp:t></hp:run></hp:p>'
      2. remap_style_ids(xml, {'charPrIDRef': {'45':'48'}, 'paraPrIDRef': {'34':'38'}})
      3. 결과에서 charPrIDRef="48", paraPrIDRef="38" 확인
      4. 결과에서 "45명의 연구원" 텍스트 보존 확인
    Expected Result: 속성만 변경, 텍스트 보존
    Evidence: .sisyphus/evidence/task-5-remap-scoped.txt
  ```

  **Commit**: YES (group 4)
  - Message: `feat(hwpx-core): add style ID remapping engine`
  - Files: `scripts/section_transplant.py`, `tests/test_style_remap.py`

- [x] 6. 섹션 조립 (챕터 범위 교체)

  **What to do**:
  - `section_transplant.py`에 조립 함수 추가:
    - `transplant_sections(source_hwpx, target_hwpx, chapter_nums, output_path, style_map=None, dry_run=False)`:
      - 1. 소스/타깃 ZIP에서 section0.xml + header.xml 추출
      - 2. extract_children()로 단락 리스트 분리
      - 3. detect_headings()로 챕터 경계 탐지
      - 4. style_map 없으면 build_style_mapping()으로 자동 생성
      - 5. remap_chapters()로 소스 챕터 리매핑
      - 6. 타깃의 해당 챕터 범위를 리매핑된 소스로 교체
      - 7. assemble_section()로 새 section0.xml 생성
      - 8. write_zip()로 HWPX 패키징 (수정된 zip_surgery 사용)
    - dry_run 모드: 파일 생성 없이 매핑 테이블 + 챕터 정보 출력
  - 테스트 추가: `tests/test_transplant_assembly.py`

  **Must NOT do**:
  - 소스/타깃 원본 파일 수정 금지 (output_path 필수)
  - child elements 사이 newline 삽입 금지
  - 비이식 챕터(1,2,7) 내용 수정 금지 (바이트 동일 유지)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 모든 컨포넌트 통합, 다단계 파이프라인, 엣지 케이스
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after T5
  - **Blocks**: T7, T8
  - **Blocked By**: T1, T5

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:208-218` — `assemble_section()` 조립 패턴
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:96-116` — `write_zip()` (T1에서 수정된 버전 사용)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:74-93` — `read_zip()` (T1에서 수정된 버전 사용)
  - Metis 분석 E5 — hp:secPr 처리: 이식 단락에서 secPr 제거
  - Metis 분석 E2 — 첫 H1 이전 콘텐츠: 타깃 소유, 이식 대상 아님

  **Acceptance Criteria**:
  - [ ] transplant_sections()이 합성 HWPX 두 개로 성공적으로 이식 실행
  - [ ] 결과 파일에 소스 챕터 텍스트 존재
  - [ ] 결과 파일에 소스 전용 스타일 ID 없음 (리매핑 완료)
  - [ ] 비이식 챕터는 타깃과 바이트 동일
  - [ ] dry_run 모드에서 파일 생성 없음

  **QA Scenarios:**
  ```
  Scenario: Full transplant with synthetic HWPX
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/test_transplant_assembly.py -v
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-6-assembly.txt

  Scenario: Non-transplanted chapters preserved
    Tool: Bash (python3)
    Steps:
      1. 합성 source(3챕터) + target(3챕터) 생성
      2. transplant_sections(source, target, chapters=[2], output='/tmp/result.hwpx')
      3. result의 챕터 1 텍스트 == target의 챕터 1 텍스트
    Expected Result: 비이식 챕터 바이트 동일
    Evidence: .sisyphus/evidence/task-6-preservation.txt
  ```

  **Commit**: YES (group 5)
  - Message: `feat(hwpx-core): add section assembly and full transplant pipeline`
  - Files: `scripts/section_transplant.py`, `tests/test_transplant_assembly.py`

- [x] 7. CLI 인터페이스 + HwpxSurgeon 확장

  **What to do**:
  - `section_transplant.py`에 CLI 추가:
    - `argparse` 기반, 기존 zip_surgery.py CLI 패턴 따름
    - `--source`: 소스 HWPX 파일경로 (required)
    - `--target`: 타깃 HWPX 파일경로 (required)
    - `--chapters`: 이식할 챕터 번호 (콤마 구분, required)
    - `--style-map`: 외부 JSON 스타일 맵 (선택. 없으면 자동 생성)
    - `--output`: 결과 HWPX 경로 (--dry-run 이 아닌 경우 required)
    - `--dry-run`: 매핑 테이블만 출력, 파일 생성 없음 (`--output` 불필요)
    - Exit codes: 0=성공, 1=런타임 오류, 2=검증 오류
  - `zip_surgery.py`의 `HwpxSurgeon` 클래스에 `transplant_from()` 메서드 추가:
    - `def transplant_from(self, source_path, chapters, style_map=None, dry_run=False)`
    - 내부적으로 section_transplant 모듈 호출
    - 결과를 self._modified에 저장 (기존 save() 워크플로우 활용)

  **Must NOT do**:
  - --dry-run 이 아닌데 --output 누락 시 오류 반환 (기본값 덮어쓰기 금지)
  - HwpxSurgeon의 기존 메서드(extract_children, replace_children 등) 동작 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: CLI 설계 + 클래스 확장, 기존 코드와의 통합 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (Sequential after T6)
  - **Blocks**: T8
  - **Blocked By**: T6

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:498-567` — 기존 CLI 패턴 (argparse subcommands)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:416-491` — HwpxSurgeon 클래스 (확장 대상)

  **Acceptance Criteria**:
  - [ ] `python section_transplant.py --help` 실행 성공
  - [ ] `python section_transplant.py --source a --target b --chapters 1,2 --output c` 실행 성공
  - [ ] --dry-run 시 파일 생성 없음 + 매핑 테이블 stdout 출력
  - [ ] --dry-run 없이 --output 없이 실행 시 exit code 1 + 오류 메시지
  - [ ] --dry-run 시 --output 없어도 exit code 0 (출력 파일 불필요)
  - [ ] HwpxSurgeon('target.hwpx').transplant_from('source.hwpx', [3,4,5]) 실행 성공

  **QA Scenarios:**
  ```
  Scenario: CLI --dry-run (no output required)
    Tool: Bash
    Preconditions: Working directory = plugins/hwpx-generator/skills/hwpx-core/
    Steps:
      1. python3 scripts/section_transplant.py --source /tmp/test_source.hwpx --target /tmp/test_target.hwpx --chapters 1,2 --dry-run
      2. echo $? → 종료 코드 0 확인
      3. stdout에 매핑 테이블 존재 확인
      4. ls /tmp/result_*.hwpx 2>/dev/null → 없음 확인
    Expected Result: Exit 0, mapping printed, no output file
    Evidence: .sisyphus/evidence/task-7-cli-dryrun.txt
  ```

  **Commit**: YES (group 6)
  - Message: `feat(hwpx-core): add CLI and HwpxSurgeon.transplant_from()`
  - Files: `scripts/section_transplant.py`, `scripts/zip_surgery.py`

- [x] 8. 통합 테스트 스위트

  **What to do**:
  - `tests/test_transplant_e2e.py` 작성:
    - test_full_transplant_synthetic: 합성 HWPX 3챕터 → 3챕터 이식
    - test_transplant_preserves_non_target: 비이식 챕터 바이트 동일
    - test_transplant_remaps_all_ids: 소스 전용 ID 부재 검증
    - test_zip_metadata_preserved: external_attr 등 메타데이터 보존
    - test_dry_run_no_output: dry-run 파일 생성 없음
    - test_missing_chapter_warning: 존재하지 않는 챕터 번호 요청 시 경고
    - test_image_reference_warning: hp:pic 포함 챕터 이식 시 WARNING
  - report-template.hwpx 기반 실제 파일 테스트 (가능한 경우)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 통합 테스트, 다양한 시나리오 커버
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (Sequential after T7)
  - **Blocks**: T9
  - **Blocked By**: T7

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_transplant_e2e.py -v` → 7/7 PASS
  - [ ] 모든 엣지 케이스 커버됨 (ID=0, secPr, hp:pic, 빈챕터, 누락챕터)

  **QA Scenarios:**
  ```
  Scenario: Full E2E test suite
    Tool: Bash (pytest)
    Steps:
      1. pytest tests/test_transplant_e2e.py -v --tb=short
    Expected Result: 7 passed, 0 failed
    Evidence: .sisyphus/evidence/task-8-e2e.txt
  ```

  **Commit**: YES (group 7)
  - Message: `test(hwpx-core): add end-to-end transplant integration tests`
  - Files: `tests/test_transplant_e2e.py`

- [x] 9. 버전 범프 + 문서 업데이트

  **What to do**:
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` 버전 범프 (MINOR)
  - `.claude-plugin/marketplace.json` 해당 플러그인 버전 업데이트
  - `marketplace.json` metadata.version 업데이트
  - `AGENTS.md` VERSION + COMMANDS 섬션에 section_transplant.py 추가
  - `README.md` Version + 변경 이력 표 + hwpx-generator 주요 특징에 이식 기능 추가
  - zip-surgery-guide.md에 이식 워크플로우 추가 (선택)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 문서 + 버전 업데이트만
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after T8)
  - **Blocks**: F1-F4
  - **Blocked By**: T8

  **Acceptance Criteria**:
  - [ ] plugin.json 버전 MINOR 범프됨
  - [ ] marketplace.json 버전 동기화됨
  - [ ] AGENTS.md에 section_transplant.py 커맨드 추가됨
  - [ ] README.md 변경 이력 업데이트됨

  **QA Scenarios:**
  ```
  Scenario: Version sync verification
    Tool: Bash (grep + python3)
    Steps:
      1. grep '"version"' plugins/hwpx-generator/.claude-plugin/plugin.json
      2. python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); p=[x for x in m['plugins'] if x['name']=='hwpx-generator'][0]; print(p.get('version','MISSING'))"
      3. 두 버전이 동일한지 확인
    Expected Result: plugin.json과 marketplace.json의 hwpx-generator 버전 동일
    Evidence: .sisyphus/evidence/task-9-version-sync.txt

  Scenario: AGENTS.md contains section_transplant command
    Tool: Bash (grep)
    Steps:
      1. grep 'section_transplant' AGENTS.md
    Expected Result: section_transplant.py 커맨드 항목 존재
    Evidence: .sisyphus/evidence/task-9-agents-md.txt

  Scenario: README.md changelog updated
    Tool: Bash (grep)
    Steps:
      1. grep 'section.*transplant\|이식' README.md
    Expected Result: 변경 이력 표에 이식 기능 관련 항목 존재
    Evidence: .sisyphus/evidence/task-9-readme.txt
  ```

  **Commit**: YES (group 8)
  - Message: `docs(hwpx): add section transplant docs, bump version`
  - Files: `plugin.json`, `marketplace.json`, `AGENTS.md`, `README.md`

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run linter + pytest. Review all changed files for: `import lxml`, `import xml.etree`, empty catches, bare string replace for IDs, console.log in prod, commented-out code. Check AI slop: excessive comments, over-abstraction.
  Output: `Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 match. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|------------|
| 1 | `fix(hwpx-core): preserve all ZipInfo metadata in zip_surgery.py` | zip_surgery.py, test_zip_surgery_metadata.py | pytest tests/test_zip_surgery_metadata.py |
| 2 | `test(hwpx-core): add transplant test fixtures and chapter detection tests` | conftest additions, test_chapter_detection.py | pytest tests/test_chapter_detection.py |
| 3 | `feat(hwpx-core): add chapter boundary detection to section_transplant.py` | section_transplant.py | pytest tests/test_chapter_detection.py |
| 4 | `feat(hwpx-core): add style map extraction and ID remapping` | section_transplant.py, test_style_remap.py | pytest tests/test_style_remap.py |
| 5 | `feat(hwpx-core): add section assembly and full transplant pipeline` | section_transplant.py | pytest |
| 6 | `feat(hwpx-core): add CLI and HwpxSurgeon.transplant_from()` | section_transplant.py, zip_surgery.py | pytest |
| 7 | `test(hwpx-core): add end-to-end transplant integration tests` | test_transplant_e2e.py | pytest |
| 8 | `docs(hwpx): bump version, update AGENTS.md, README.md` | plugin.json, marketplace.json, AGENTS.md, README.md | — |

---

## Success Criteria

### Verification Commands
```bash
# Working directory: plugins/hwpx-generator/skills/hwpx-core/
pytest tests/ -v                                                     # All tests pass
python3 scripts/section_transplant.py --help                          # CLI works
python3 scripts/section_transplant.py --source a.hwpx --target b.hwpx --chapters 3 --dry-run  # Dry run
python3 scripts/zip_surgery.py validate target.hwpx result.hwpx       # Validation pass
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (pytest)
- [ ] zip_surgery.py preserves all ZipInfo attributes
- [ ] section_transplant.py CLI functional
- [ ] HwpxSurgeon.transplant_from() method exists
- [ ] No XML parser imports in any modified file
- [ ] Version bumped in plugin.json + marketplace.json
