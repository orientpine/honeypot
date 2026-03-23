# HWPX Generator: MD 문서 구조(Indent) 보존 개선

## TL;DR

> **Quick Summary**: md_parser.py가 마크다운 들여쓰기 레벨을 버리는 근본 원인을 수정하고, xml_writer.py가 레벨별 HWPX 스타일을 자동 매핑하도록 개선하며, 다중 MD 파일 통합 시 heading 체계를 일관되게 유지하는 병합 기능을 추가한다.
> 
> **Deliverables**:
> - md_parser.py: indent_level 필드 추가 (bullet + numbered list)
> - xml_writer.py: level→style 자동 매핑 + build_numbered() 신규 함수
> - analyze_template.py: indent 레벨별 스타일 자동 추출 (--style-map 강화)
> - md_merger.py: 다중 MD 파일 heading offset 자동 계산 병합 스크립트 (신규)
> - 에이전트/스킬 문서: 새 파이프라인 반영 업데이트
> - TDD 테스트: 기존 테스트 확장 + 새 테스트 추가
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 3 → Task 5 → Task 7 → Task 9 → Task 10 → Task 11

---

## Context

### Original Request
사용자가 작성한 제안서 HWPX(제안서_최종_포맷완료_v6.hwpx)를 레퍼런스로, hwpx-generator 플러그인의 MD→HWPX 변환 시 문서 구조(indent) 보존을 강화하고자 함. 현재 두 가지 문제가 존재:
1. MD 문서의 구조(들여쓰기, heading 계층)가 HWPX에 미반영됨
2. 서로 다른 MD 문서를 통합하여 HWPX로 변환 시 문단 구조 불일치

### Interview Summary
**Key Discussions**:
- 들여쓰기 단위: 2-space per level로 확정
- 다중 MD 통합: heading offset 자동 계산 방식 채택
- 기본 들여쓰기: report 템플릿 기본값 + level 3 이상 확장 지원
- 지원 범위: bullet + heading + numbered list (blockquote 제외)
- 에이전트/스크립트 역할: 하이브리드 (스크립트 95% 결정적 + 에이전트 5% 검토)

**Research Findings**:
- 현재 BULLET_RE가 선행 공백을 완전히 무시 → indent level 정보 소실 (ROOT CAUSE)
- xml_writer.py에 style_key/left_margin/indent 오버라이드 존재하나 미사용
- HWPUNIT 변환: 1mm ≈ 283.46 HWPUNIT, 불릿 indent step ≈ 800 HWPUNIT/level
- analyze_template.py의 --style-map은 flat 스타일만 추출, indent 그룹화 없음
- 제안서 HWPX는 66개 borderFill + 47+ charPr → 복잡한 스타일 체계

### Metis Review
**Identified Gaps** (addressed):
- HWPUNIT 기본 indent step 값 미정의 → 800 HWPUNIT/level로 확정, 상수화
- string-based XML 패턴 준수 여부 → build_numbered()에도 동일 패턴 적용 명시
- linesegarray 영향 → 기존 파이프라인이 자동 처리, 변경 불필요
- numbered list 마커 패턴 다양성 (1., 2., a., ①, (1)) → 정규식 포괄 설계 필요

---

## Work Objectives

### Core Objective
마크다운 문서의 계층적 구조(heading 레벨, 불릿 들여쓰기, 번호 목록 들여쓰기)를 HWPX 변환 시 100% 보존하는 결정적 파이프라인을 구축한다.

### Concrete Deliverables
- `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` — indent_level + numbered list 지원
- `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` — level→style 매핑 + build_numbered()
- `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — indent 스타일 자동 추출
- `plugins/hwpx-generator/skills/hwpx-core/scripts/md_merger.py` — 다중 MD 병합 (신규)
- `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` — Workflow 7 업데이트
- `plugins/hwpx-generator/agents/hwpx-builder.md` — 새 파이프라인 반영
- `plugins/hwpx-generator/commands/hwpx-generate.md` — md_merger 단계 추가
- TDD 테스트 파일들 (기존 확장 + 신규)

### Definition of Done
- [ ] `python3 md_parser.py 5장.md` 출력에 모든 불릿의 `indent_level` 필드가 존재
- [ ] `python3 md_parser.py 5장.md` 출력에 numbered list가 `numbered_item` 타입으로 파싱됨
- [ ] `python3 xml_writer.py` 출력에서 indent_level 0/1/2 불릿이 서로 다른 left_margin 보유
- [ ] 5장.md → 제안서 양식 HWPX 변환 E2E 파이프라인 정상 작동
- [ ] 기존 테스트 (test_md_parser_complex, test_xml_writer_bullets 등) 전부 PASS
- [ ] 다중 MD 병합 시 heading level 일관성 유지

### Must Have
- indent_level 감지 정확도 100% (2-space 기준)
- 기존 md_parser.py/xml_writer.py의 하위 호환성 유지
- string-based XML 생성 패턴 준수 (lxml/ElementTree 금지)
- 기존 테스트 전부 통과 (회귀 없음)

### Must NOT Have (Guardrails)
- lxml 또는 xml.etree.ElementTree 임포트 금지 (xml_writer.py/md_parser.py)
- cell_writer.py / build_hwpx.py 수정 금지 (downstream 파이프라인)
- header.xml 수정 로직 추가 금지 (스타일 정의는 원본 유지)
- indent_level을 에이전트가 수동으로 계산하는 로직 금지 (스크립트가 결정적으로 처리)
- magic number 금지 (HWPUNIT_PER_LEVEL 등 상수화)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, conftest.py, 17+ existing test files)
- **Automated tests**: TDD (RED → GREEN → REFACTOR)
- **Framework**: pytest
- **TDD**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Scripts**: Use Bash — Run script, compare output JSON/XML, assert fields
- **E2E Pipeline**: Use Bash — Full pipeline execution, validate.py, page_guard.py

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — TDD tests + foundation):
├── Task 1: md_parser indent_level TDD 테스트 작성 [deep]
├── Task 2: md_parser numbered list TDD 테스트 작성 [deep]
├── Task 3: xml_writer indent-level 매핑 TDD 테스트 작성 [deep]
├── Task 4: md_merger TDD 테스트 작성 [deep]
├── Task 5: analyze_template indent 추출 TDD 테스트 작성 [deep]

Wave 2 (After Wave 1 — implementation, MAX PARALLEL):
├── Task 6: md_parser.py 구현 - indent_level + numbered list (depends: 1, 2) [deep]
├── Task 7: xml_writer.py 구현 - level→style 매핑 + build_numbered (depends: 3) [deep]
├── Task 8: md_merger.py 구현 - 다중 MD 병합 (depends: 4) [deep]
├── Task 9: analyze_template.py 구현 - indent 스타일 추출 (depends: 5) [deep]

Wave 3 (After Wave 2 — integration + docs):
├── Task 10: E2E 통합 테스트 (5장.md + 제안서 HWPX) (depends: 6, 7, 8, 9) [deep]
├── Task 11: 에이전트/스킬/커맨드 문서 업데이트 (depends: 6, 7, 8, 9) [unspecified-high]
├── Task 12: 버전 업데이트 (plugin.json, marketplace.json, AGENTS.md, README.md) (depends: 11) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 6 → Task 7 → Task 10 → F1-F4 → user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 6 | 1 |
| 2 | — | 6 | 1 |
| 3 | — | 7 | 1 |
| 4 | — | 8 | 1 |
| 5 | — | 9 | 1 |
| 6 | 1, 2 | 10 | 2 |
| 7 | 3 | 10 | 2 |
| 8 | 4 | 10 | 2 |
| 9 | 5 | 10 | 2 |
| 10 | 6, 7, 8, 9 | 11 | 3 |
| 11 | 6, 7, 8, 9 | 12 | 3 |
| 12 | 11 | F1-F4 | 3 |

### Agent Dispatch Summary

- **Wave 1**: **5** — T1-T5 → `deep`
- **Wave 2**: **4** — T6-T9 → `deep`
- **Wave 3**: **3** — T10 → `deep`, T11 → `unspecified-high`, T12 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs


- [x] 1. md_parser indent_level TDD 테스트 작성

  **What to do**:
  - `tests/test_md_parser_indent.py` 신규 생성
  - 테스트 케이스:
    - level 0 불릿 (`- text`) → indent_level: 0
    - level 1 불릿 (`  - text`, 2-space) → indent_level: 1
    - level 2 불릿 (`    - text`, 4-space) → indent_level: 2
    - level 3 불릿 (`      - text`, 6-space) → indent_level: 3
    - 혼합 불릿 마커 (-, *, ◦, –, □) 모두 indent_level 감지
    - 5장.md 파싱 결과에서 indent_level 0과 1이 모두 존재하는지 검증
    - 빈 줄 후 들여쓰기 리셋 검증
  - 이 시점에서 테스트는 FAIL (RED 단계)

  **Must NOT do**:
  - md_parser.py 구현 수정 금지 (RED 단계)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: [Task 6]
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_md_parser_complex.py` — 기존 md_parser 테스트 패턴 참조
  - `plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py` — fixture 패턴
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:11-14` — 현재 BULLET_RE 정규식
  - `dev/hwpx_indent/5장.md` — 실제 다단계 indent가 있는 테스트 데이터

  **Acceptance Criteria**:
  - [ ] `tests/test_md_parser_indent.py` 파일 생성됨
  - [ ] `pytest tests/test_md_parser_indent.py` 실행 시 모든 테스트가 FAIL (RED 확인)
  - [ ] 최소 8개 테스트 케이스 존재

  **QA Scenarios:**
  ```
  Scenario: TDD RED 단계 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_parser_indent.py -v 2>&1
      2. 출력에서 'FAILED' 키워드 존재 확인
      3. 'PASSED' 키워드가 0개인지 확인
    Expected Result: 모든 테스트 FAIL (구현 전이므로)
    Evidence: .sisyphus/evidence/task-1-red-phase.txt
  ```

  **Commit**: YES (groups with Task 2, 3, 4, 5)
  - Message: `test(hwpx): add TDD tests for indent-level preservation`
  - Files: `tests/test_md_parser_indent.py`

- [x] 2. md_parser numbered list TDD 테스트 작성

  **What to do**:
  - `tests/test_md_parser_numbered.py` 신규 생성
  - 테스트 케이스:
    - `1. text` → type: "numbered_item", number: "1", indent_level: 0
    - `  1. text` (2-space) → indent_level: 1
    - `a. text`, `(1)`, `①` 등 다양한 번호 패턴 감지
    - numbered + bullet 혼합 문서 파싱
    - numbered list 내부 들여쓰기 보존
  - RED 단계 (테스트 FAIL 확인)

  **Must NOT do**:
  - md_parser.py 구현 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: [Task 6]
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:12` — 현재 BULLET_RE (numbered list 미지원)
  - `dev/hwpx_indent/5장.md:151-162` — numbered list가 포함된 실제 데이터

  **Acceptance Criteria**:
  - [ ] `tests/test_md_parser_numbered.py` 파일 생성됨
  - [ ] `pytest tests/test_md_parser_numbered.py` 실행 시 모든 테스트 FAIL
  - [ ] 최소 6개 테스트 케이스 존재

  **QA Scenarios:**
  ```
  Scenario: numbered list 파싱 TDD RED 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_parser_numbered.py -v 2>&1
      2. 출력에서 'FAILED' 키워드 존재 확인
    Expected Result: 모든 테스트 FAIL
    Evidence: .sisyphus/evidence/task-2-red-phase.txt
  ```

  **Commit**: YES (groups with Task 1, 3, 4, 5)
  - Message: `test(hwpx): add TDD tests for indent-level preservation`
  - Files: `tests/test_md_parser_numbered.py`

- [x] 3. xml_writer indent-level 매핑 TDD 테스트 작성

  **What to do**:
  - `tests/test_xml_writer_indent.py` 신규 생성
  - 테스트 케이스:
    - indent_level 0 불릿 → style_config의 `bullet_level_0` 스타일 적용
    - indent_level 1 불릿 → `bullet_level_1` 스타일, left_margin 더 큼
    - indent_level 2 불릿 → `bullet_level_2` 스타일
    - style_config에 해당 레벨이 없으면 → 가장 깊은 정의된 레벨 사용 + HWPUNIT_PER_LEVEL만큼 left_margin 증가
    - numbered_item 타입 → build_numbered() 호출, 번호 마커 + 내용 분리
    - 기존 bullet (indent_level 없음) → 하위 호환: 기존 동작 유지
  - RED 단계

  **Must NOT do**:
  - xml_writer.py 구현 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: [Task 7]
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:240-283` — 현재 build_bullet() 구현
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:171-211` — paragraph_from_segments() (left_margin, indent 지원)
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_bullets.py` — 기존 불릿 테스트 패턴

  **Acceptance Criteria**:
  - [ ] `tests/test_xml_writer_indent.py` 파일 생성됨
  - [ ] `pytest tests/test_xml_writer_indent.py` 실행 시 모든 테스트 FAIL
  - [ ] 최소 8개 테스트 케이스 (indent 3레벨 + numbered + 하위호환 + 폴백)

  **QA Scenarios:**
  ```
  Scenario: xml_writer indent TDD RED 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_xml_writer_indent.py -v 2>&1
      2. FAILED 키워드 존재 확인
    Expected Result: 모든 테스트 FAIL
    Evidence: .sisyphus/evidence/task-3-red-phase.txt
  ```

  **Commit**: YES (groups with Task 1, 2, 4, 5)
  - Message: `test(hwpx): add TDD tests for indent-level preservation`
  - Files: `tests/test_xml_writer_indent.py`

- [x] 4. md_merger TDD 테스트 작성

  **What to do**:
  - `tests/test_md_merger.py` 신규 생성
  - 테스트 케이스:
    - 단일 MD 파일: 구조 변경 없이 통과
    - 2개 MD 파일: heading offset 자동 계산 (# = target section level)
    - heading level 충돌 해결: 두 MD 모두 `#`으로 시작하되 target이 `##`인 경우
    - 섹션 경계 마커 삽입 확인
    - 빈 MD 파일 처리 (에러 없이 스킵)
    - heading 없는 MD 파일 (본문만) 처리
  - RED 단계

  **Must NOT do**:
  - md_merger.py 구현 생성 금지 (테스트만)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: [Task 8]
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:124-247` — parse_markdown() 함수 (병합 시 재사용)
  - `plugins/hwpx-generator/commands/hwpx-generate.md:8` — content_md 파라미터 (여러 파일 경로 리스트)

  **Acceptance Criteria**:
  - [ ] `tests/test_md_merger.py` 파일 생성됨
  - [ ] `pytest tests/test_md_merger.py` 실행 시 모든 테스트 FAIL
  - [ ] 최소 6개 테스트 케이스

  **QA Scenarios:**
  ```
  Scenario: md_merger TDD RED 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_merger.py -v 2>&1
      2. FAILED 키워드 존재 확인
    Expected Result: 모든 테스트 FAIL
    Evidence: .sisyphus/evidence/task-4-red-phase.txt
  ```

  **Commit**: YES (groups with Task 1, 2, 3, 5)
  - Message: `test(hwpx): add TDD tests for indent-level preservation`
  - Files: `tests/test_md_merger.py`

- [x] 5. analyze_template indent 추출 TDD 테스트 작성

  **What to do**:
  - `tests/test_analyze_indent.py` 신규 생성
  - 테스트 케이스:
    - 제안서 HWPX에서 --style-map 실행 시 `bullet_level_0`, `bullet_level_1` 등 키 존재
    - 각 레벨의 paraPrIDRef, charPrIDRef, left_margin 값이 존재
    - 레벨 간 left_margin이 단조증가
    - 기본 템플릿(report)에서도 레벨별 추출 작동
    - 템플릿에 레벨별 스타일이 없으면 기본값(HWPUNIT_PER_LEVEL 기반) 생성
  - RED 단계

  **Must NOT do**:
  - analyze_template.py 구현 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: [Task 9]
  - **Blocked By**: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — 현재 구현
  - `dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx` — E2E 테스트 fixture
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:130-178` — 기존 스타일 ID 맵

  **Acceptance Criteria**:
  - [ ] `tests/test_analyze_indent.py` 파일 생성됨
  - [ ] `pytest tests/test_analyze_indent.py` 실행 시 모든 테스트 FAIL
  - [ ] 최소 5개 테스트 케이스

  **QA Scenarios:**
  ```
  Scenario: analyze_template indent TDD RED 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_analyze_indent.py -v 2>&1
      2. FAILED 키워드 존재 확인
    Expected Result: 모든 테스트 FAIL
    Evidence: .sisyphus/evidence/task-5-red-phase.txt
  ```

  **Commit**: YES (groups with Task 1, 2, 3, 4)
  - Message: `test(hwpx): add TDD tests for indent-level preservation`
  - Files: `tests/test_analyze_indent.py`

- [x] 6. md_parser.py 구현 — indent_level + numbered list 지원

  **What to do**:
  - `BULLET_RE`를 수정하여 선행 공백을 캡처하고, 공백 수 / 2 = indent_level로 계산
  - 새 정규식 `NUMBERED_RE` 추가: `1.`, `2.`, `a.`, `(1)`, `①` 등 다양한 번호 패턴
  - `parse_markdown()` 내부에 numbered list 파싱 블록 추가
  - 불릿/numbered item 출력에 `indent_level` 필드 추가
  - 기존 필드 (`type`, `marker`, `text`, `segments`) 유지 → 하위 호환성
  - indent_level이 없는 레거시 불릿은 indent_level: 0 기본값
  - 모든 Wave 1 테스트(Task 1, 2) PASS 확인
  - 기존 test_md_parser_complex.py도 전부 PASS 확인 (회귀 방지)

  **Must NOT do**:
  - lxml 또는 xml.etree.ElementTree 임포트 금지
  - 기존 block 타입(`heading`, `paragraph`, `table`, `image_ref` 등)의 출력 구조 변경 금지
  - indent_level 필드가 없는 블록에 indent_level 추가 금지 (불릿/numbered만 대상)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2에서 Task 7, 8, 9와 병렬)
  - **Parallel Group**: Wave 2
  - **Blocks**: [Task 10]
  - **Blocked By**: [Task 1, Task 2]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:11-14` — 현재 BULLET_RE, BLOCKQUOTE_RE 정규식
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:206-214` — 현재 bullet 파싱 블록
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py:124-247` — parse_markdown() 전체 구조
  - `dev/hwpx_indent/5장.md` — 2-space indent가 있는 실제 MD 데이터

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_md_parser_indent.py` ALL PASS
  - [ ] `pytest tests/test_md_parser_numbered.py` ALL PASS
  - [ ] `pytest tests/test_md_parser_complex.py` ALL PASS (회귀 없음)
  - [ ] 5장.md 파싱 결과에서 indent_level 0, 1이 모두 존재

  **QA Scenarios:**
  ```
  Scenario: indent_level 감지 GREEN 단계
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_parser_indent.py tests/test_md_parser_numbered.py -v
      2. ALL PASS 확인
    Expected Result: 모든 테스트 PASS
    Evidence: .sisyphus/evidence/task-6-green-phase.txt

  Scenario: 5장.md 실제 파싱 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python3 scripts/md_parser.py ../../../../dev/hwpx_indent/5장.md -o /tmp/parsed_5.json
      2. python3 -c "import json; d=json.load(open('/tmp/parsed_5.json')); bullets=[b for b in d['blocks'] if b['type']=='bullet']; levels=set(b.get('indent_level',0) for b in bullets); assert len(levels)>=2, f'Only {levels}'"
    Expected Result: 2개 이상의 distinct indent_level 존재
    Evidence: .sisyphus/evidence/task-6-5jang-parse.txt

  Scenario: 회귀 테스트
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_parser_complex.py -v
      2. ALL PASS 확인
    Expected Result: 기존 테스트 전부 통과
    Evidence: .sisyphus/evidence/task-6-regression.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx): add indent_level detection and numbered list support to md_parser`
  - Files: `scripts/md_parser.py`

- [x] 7. xml_writer.py 구현 — level→style 매핑 + build_numbered()

  **What to do**:
  - `HWPUNIT_PER_LEVEL = 800` 상수 추가 (매직 넘버 금지)
  - `build_bullet()` 수정: block에 `indent_level`이 있으면 `bullet_level_{N}` 스타일 참조
  - indent_level N에 해당하는 스타일이 style_config에 없으면 → 가장 깊은 정의된 레벨의 left_margin + (N - max_defined) * HWPUNIT_PER_LEVEL
  - `build_numbered()` 신규 함수 추가: 번호 마커 + 내용 이중 run 구조, indent_level 반영
  - `build_fragment()` 수정: `numbered_item` 타입 분기 추가
  - string-based XML 방식 유지 (lxml/ET 금지)
  - 하위 호환: indent_level 없는 기존 불릿 → 현재 동작 그대로
  - Wave 1의 Task 3 테스트 전부 PASS + 기존 test_xml_writer_bullets.py PASS

  **Must NOT do**:
  - lxml/ElementTree 임포트 금지
  - 기존 build_heading/build_paragraph/build_table 함수 시그니처 변경 금지
  - magic number 사용 금지 (상수화 필수)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: [Task 10]
  - **Blocked By**: [Task 3]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:240-283` — 현재 build_bullet()
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:556-589` — build_fragment() (분기 로직)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:171-211` — paragraph_from_segments()
  - Metis 리뷰: HWPUNIT_PER_LEVEL = 800, 1mm ≈ 283.46 HWPUNIT

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_xml_writer_indent.py` ALL PASS
  - [ ] `pytest tests/test_xml_writer_bullets.py` ALL PASS (회귀 없음)
  - [ ] HWPUNIT_PER_LEVEL 상수 존재 확인 (grep)
  - [ ] build_numbered() 함수 존재 확인 (grep)

  **QA Scenarios:**
  ```
  Scenario: xml_writer indent GREEN 단계
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_xml_writer_indent.py tests/test_xml_writer_bullets.py -v
      2. ALL PASS 확인
    Expected Result: 모든 테스트 PASS
    Evidence: .sisyphus/evidence/task-7-green-phase.txt

  Scenario: HWPUNIT_PER_LEVEL 상수 확인
    Tool: Bash
    Steps:
      1. grep -n 'HWPUNIT_PER_LEVEL' scripts/xml_writer.py
      2. 출력에 '800' 포함 확인
    Expected Result: 상수 정의 존재
    Evidence: .sisyphus/evidence/task-7-constant-check.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx): add indent-level style mapping and build_numbered() to xml_writer`
  - Files: `scripts/xml_writer.py`

- [x] 8. md_merger.py 구현 — 다중 MD 병합 스크립트 (신규)

  **What to do**:
  - `scripts/md_merger.py` 신규 생성
  - 기능:
    - 여러 MD 파일 경로 입력 → 각 MD를 md_parser.py로 파싱 → heading offset 자동 계산 → 통합 JSON 출력
    - `--target-level N` 옵션: 통합 시 최상위 heading을 level N으로 조정
    - 섹션 경계에 `separator` 블록 삽입
    - 각 MD의 heading level을 target에 맞게 offset 적용 (예: MD의 # → target ## 이면 모든 heading +1)
    - 불릿/numbered list의 indent_level은 변경 없이 유지
  - CLI: `python3 md_merger.py file1.md file2.md --target-level 2 --output merged.json`
  - Task 4 테스트 전부 PASS 확인

  **Must NOT do**:
  - 기존 md_parser.py 수정 금지 (md_parser를 import하여 사용)
  - 내부에서 XML 생성 금지 (순수 JSON 처리만)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: [Task 10]
  - **Blocked By**: [Task 4]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` — parse_markdown() 함수 (재사용)
  - `plugins/hwpx-generator/commands/hwpx-generate.md:8` — content_md 파라미터 형식

  **Acceptance Criteria**:
  - [ ] `scripts/md_merger.py` 파일 생성됨
  - [ ] `pytest tests/test_md_merger.py` ALL PASS
  - [ ] CLI `--target-level` 옵션 작동
  - [ ] 2개 파일 병합 시 heading offset 정확

  **QA Scenarios:**
  ```
  Scenario: md_merger GREEN 단계
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_merger.py -v
      2. ALL PASS 확인
    Expected Result: 모든 테스트 PASS
    Evidence: .sisyphus/evidence/task-8-green-phase.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx): add md_merger.py for multi-MD heading offset merge`
  - Files: `scripts/md_merger.py`

- [x] 9. analyze_template.py 구현 — indent 스타일 자동 추출

  **What to do**:
  - `--style-map` 출력 JSON에 `bullet_level_0`, `bullet_level_1`, ... 키 추가
  - 템플릿 section0.xml에서 불릿 문단들의 paraPr를 분석하여 left_margin 값 기준으로 레벨 그룹화
  - left_margin이 단조증가하는 paraPr 세트를 발견하면 → level 0, 1, 2, ... 로 매핑
  - 레벨별 스타일이 불충분하면 → HWPUNIT_PER_LEVEL(800) 기반 기본값 생성
  - numbered list용 `numbered_level_0`, `numbered_level_1`, ... 도 추출 (존재 시)
  - 기존 --style-map 출력 필드(`heading_1`, `body`, `bullet`, `table_header` 등) 유지 → 하위 호환
  - Task 5 테스트 전부 PASS 확인

  **Must NOT do**:
  - 기존 --style-map 출력 필드 제거/이름 변경 금지
  - 템플릿의 header.xml 수정 금지 (읽기 전용)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2
  - **Blocks**: [Task 10]
  - **Blocked By**: [Task 5]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — 현재 구현
  - `dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx` — 실제 다단계 indent 템플릿

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_analyze_indent.py` ALL PASS
  - [ ] 제안서 HWPX에서 `bullet_level_0`, `bullet_level_1` 추출 확인
  - [ ] 기존 --style-map 필드 보존 확인

  **QA Scenarios:**
  ```
  Scenario: analyze_template indent GREEN 단계
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_analyze_indent.py -v
      2. ALL PASS 확인
    Expected Result: 모든 테스트 PASS
    Evidence: .sisyphus/evidence/task-9-green-phase.txt

  Scenario: 제안서 HWPX 실제 추출 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python3 scripts/analyze_template.py ../../../../dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx --style-map /tmp/styles.json
      2. python3 -c "import json; d=json.load(open('/tmp/styles.json')); assert 'bullet_level_0' in d, 'Missing bullet_level_0'"
    Expected Result: bullet_level_0 키 존재
    Evidence: .sisyphus/evidence/task-9-real-template.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx): add indent-level style extraction to analyze_template`
  - Files: `scripts/analyze_template.py`

- [x] 10. E2E 통합 테스트 (5장.md + 제안서 HWPX)

  **What to do**:
  - `tests/test_e2e_indent.py` 신규 생성
  - 전체 파이프라인 E2E 테스트:
    1. analyze_template.py → style_config.json 추출
    2. md_parser.py 5장.md → parsed.json (indent_level 포함)
    3. xml_writer.py → fragment.xml (level별 다른 leftMargin)
    4. fragment.xml에서 indent_level 0 불릿과 level 1 불릿의 leftMargin 값이 다른지 검증
    5. heading 계층 보존 검증 (# > ## > ###)
  - 다중 MD 병합 E2E 테스트:
    1. md_merger.py로 2개 MD 병합
    2. 병합 결과의 heading level 일관성 검증
  - Full E2E (fragment → temp HWPX 생성 → validate.py 통과 확인):
    1. xml_writer.py --wrap-section → fragment.xml 생성
    2. zip_surgery.py로 제안서 HWPX 복사본에 fragment 삽입 → /tmp/test_e2e_indent.hwpx
    3. validate.py /tmp/test_e2e_indent.hwpx → PASS 확인
    4. /tmp 파일은 테스트 teardown에서 자동 삭제

  **Must NOT do**:
  - 영구 HWPX 파일 생성 (임시 파일만 허용, teardown 시 삭제)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (모든 Wave 2 태스크 완료 후)
  - **Parallel Group**: Wave 3 (with Tasks 11, 12)
  - **Blocks**: [F1-F4]
  - **Blocked By**: [Task 6, 7, 8, 9]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py` — 기존 E2E 테스트 패턴
  - `dev/hwpx_indent/5장.md` — 입력 데이터
  - `dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx` — 템플릿 fixture

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_e2e_indent.py` ALL PASS
  - [ ] 전체 테스트 스위트 `pytest tests/ -v` ALL PASS

  **QA Scenarios:**
  ```
  Scenario: E2E indent 보존 확인
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_e2e_indent.py -v
      2. ALL PASS 확인
    Expected Result: E2E 파이프라인 정상 작동
    Evidence: .sisyphus/evidence/task-10-e2e.txt

  Scenario: 전체 회귀 테스트
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/ -v
      2. ALL PASS 확인 (신규 + 기존 모두)
    Expected Result: 0 failures
    Evidence: .sisyphus/evidence/task-10-full-regression.txt
  ```

  **Commit**: YES
  - Message: `test(hwpx): add E2E indent preservation tests with real fixtures`
  - Files: `tests/test_e2e_indent.py`

- [x] 11. 에이전트/스�/커맨드 문서 업데이트

  **What to do**:
  - `skills/hwpx-core/SKILL.md` 업데이트:
    - Workflow 7 흐름에 md_merger.py 단계 추가
    - 스크립트 요약 표에 md_merger.py 추가
    - indent_level 관련 설명 추가 (style_config의 bullet_level_N 키)
    - numbered list 지원 설명 추가
  - `agents/hwpx-builder.md` 업데이트:
    - Workflow 7 단계에 md_merger.py 사용법 추가
    - 에이전트 역할: style_config 검토/보정만 담당임을 명시
    - indent_level을 에이전트가 수동 계산하지 않도록 금지 규칙 추가
  - `commands/hwpx-generate.md` 업데이트:
    - content_md 다중 파일 시 md_merger.py 자동 호출 로직 추가

  **Must NOT do**:
  - 스크립트 코드 수정 금지 (문서만 수정)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3, Task 10, 12와 병렬)
  - **Parallel Group**: Wave 3
  - **Blocks**: [Task 12]
  - **Blocked By**: [Task 6, 7, 8, 9]

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:724-762` — Workflow 7 현재 내용
  - `plugins/hwpx-generator/agents/hwpx-builder.md:39-46` — Workflow 7 현재 내용
  - `plugins/hwpx-generator/commands/hwpx-generate.md:30` — MD 채우기 분기

  **Acceptance Criteria**:
  - [ ] SKILL.md에 md_merger.py 언급 존재
  - [ ] SKILL.md에 indent_level, bullet_level_N 설명 존재
  - [ ] hwpx-builder.md에 md_merger.py 사용법 존재
  - [ ] hwpx-generate.md에 다중 MD 시 md_merger 호출 로직 존재

  **QA Scenarios:**
  ```
  Scenario: 문서 업데이트 검증
    Tool: Bash
    Steps:
      1. grep -c 'md_merger' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      2. grep -c 'indent_level' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      3. grep -c 'md_merger' plugins/hwpx-generator/agents/hwpx-builder.md
      4. 모든 count가 1 이상인지 확인
    Expected Result: 모든 문서에 새 기능 언급 존재
    Evidence: .sisyphus/evidence/task-11-docs-check.txt
  ```

  **Commit**: YES
  - Message: `docs(hwpx): update agent/skill/command docs for indent pipeline`
  - Files: `skills/hwpx-core/SKILL.md, agents/hwpx-builder.md, commands/hwpx-generate.md`

- [x] 12. 버전 업데이트 (plugin.json, marketplace.json, AGENTS.md, README.md)

  **What to do**:
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` MINOR 버전 증가
  - `.claude-plugin/marketplace.json` 해당 항목 버전 + metadata.version 증가
  - `AGENTS.md` Version + Generated 날짜 + WHERE TO LOOK 표 + COMMANDS 섹션 업데이트
  - `README.md` Version + 변경 이력 + hwpx-generator 설명 업데이트

  **Must NOT do**:
  - MAJOR 버전 증가 금지 (MINOR 수준 변경)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Task 11 후)
  - **Blocks**: [F1-F4]
  - **Blocked By**: [Task 11]

  **References**:
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` — 현재 버전
  - `.claude-plugin/marketplace.json` — 마켓플레이스 레지스트리
  - `AGENTS.md` — 프로젝트 지식 베이스
  - `README.md` — 프로젝트 README

  **Acceptance Criteria**:
  - [ ] plugin.json 버전 증가 확인
  - [ ] marketplace.json 버전 동기화 확인
  - [ ] AGENTS.md Version/Generated 업데이트 확인
  - [ ] README.md 변경 이력 추가 확인

  **QA Scenarios:**
  ```
  Scenario: 버전 동기화 확인
    Tool: Bash
    Steps:
      1. grep 'version' plugins/hwpx-generator/.claude-plugin/plugin.json
      2. 버전이 증가되었는지 확인
    Expected Result: MINOR 버전 증가
    Evidence: .sisyphus/evidence/task-12-version-check.txt
  ```

  **Commit**: YES
  - Message: `chore(hwpx): bump version for indent-preserve feature`
  - Files: `plugin.json, marketplace.json, AGENTS.md, README.md`
## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns.

  **QA Scenarios:**
  ```
  Scenario: Must Have 검증
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && grep -c 'indent_level' scripts/md_parser.py
      2. grep -c 'HWPUNIT_PER_LEVEL' scripts/xml_writer.py
      3. grep -c 'build_numbered' scripts/xml_writer.py
      4. test -f scripts/md_merger.py && echo 'EXISTS' || echo 'MISSING'
      5. 모든 count가 1 이상, md_merger.py EXISTS 확인
    Expected Result: 모든 Must Have 항목 존재
    Evidence: .sisyphus/evidence/f1-must-have.txt

  Scenario: Must NOT Have 검증
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && grep -c 'from lxml' scripts/md_parser.py scripts/xml_writer.py scripts/md_merger.py; echo "exit:$?"
      2. grep -c 'import xml.etree' scripts/md_parser.py scripts/xml_writer.py scripts/md_merger.py; echo "exit:$?"
      3. 모든 count가 0인지 확인 (금지된 임포트 없음)
    Expected Result: lxml/ElementTree 임포트 0건
    Evidence: .sisyphus/evidence/f1-must-not-have.txt

  Scenario: evidence 파일 존재 확인
    Tool: Bash
    Steps:
      1. ls .sisyphus/evidence/task-*.txt | wc -l
      2. count가 10 이상인지 확인
    Expected Result: 최소 10개 evidence 파일 존재
    Evidence: .sisyphus/evidence/f1-evidence-check.txt
  ```
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run full test suite. Review changed files for quality issues.

  **QA Scenarios:**
  ```
  Scenario: 전체 테스트 스위트
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/ -v --tb=short 2>&1
      2. FAILED 키워드가 0건인지 확인
    Expected Result: ALL PASS, 0 failures
    Evidence: .sisyphus/evidence/f2-test-suite.txt

  Scenario: magic number 검사
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && grep -n '800' scripts/xml_writer.py | grep -v 'HWPUNIT_PER_LEVEL'
      2. 출력이 비어있거나, 해당 800이 HWPUNIT_PER_LEVEL 상수 정의 줄인지 확인
    Expected Result: magic number 800 미사용
    Evidence: .sisyphus/evidence/f2-magic-numbers.txt

  Scenario: 하위 호환성 검증
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/test_md_parser_complex.py tests/test_xml_writer_bullets.py tests/test_xml_writer_section.py -v
      2. ALL PASS 확인 (기존 테스트 회귀 없음)
    Expected Result: 기존 테스트 100% 통과
    Evidence: .sisyphus/evidence/f2-backward-compat.txt
  ```
  Output: `Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Execute full pipeline: md_parser → xml_writer → zip_surgery → validate using 제안서 HWPX.

  **QA Scenarios:**
  ```
  Scenario: 전체 파이프라인 E2E 실행
    Tool: Bash
    Steps:
      1. cd plugins/hwpx-generator/skills/hwpx-core
      2. python3 scripts/analyze_template.py ../../../../dev/hwpx_indent/제안서_최종_포맷완료_v6.hwpx --style-map /tmp/f3_styles.json
      3. python3 scripts/md_parser.py ../../../../dev/hwpx_indent/5장.md -o /tmp/f3_parsed.json
      4. python3 scripts/xml_writer.py --input /tmp/f3_parsed.json --style-config /tmp/f3_styles.json --output /tmp/f3_fragment.xml --wrap-section
      5. grep -c 'leftMargin' /tmp/f3_fragment.xml (다양한 leftMargin 값 확인)
    Expected Result: fragment.xml에 2개 이상의 다른 leftMargin 값 존재
    Evidence: .sisyphus/evidence/f3-e2e-pipeline.txt

  Scenario: indent level 보존 검증
    Tool: Bash
    Steps:
      1. python3 -c "import json; d=json.load(open('/tmp/f3_parsed.json')); bullets=[b for b in d['blocks'] if b['type']=='bullet']; levels=set(b.get('indent_level',0) for b in bullets); print(f'Levels: {levels}'); assert len(levels)>=2"
    Expected Result: 2개 이상 distinct indent_level
    Evidence: .sisyphus/evidence/f3-indent-preserved.txt
  ```
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read spec vs actual diff. Verify nothing beyond spec was built.

  **QA Scenarios:**
  ```
  Scenario: 범위 초과 변경 검사
    Tool: Bash
    Steps:
      1. git diff --name-only HEAD~4 (or appropriate range)
      2. 변경된 파일이 플랜의 Deliverables 목록과 일치하는지 확인
      3. 플랜에 없는 파일이 변경되었으면 flag
    Expected Result: 모든 변경이 플랜 범위 내
    Evidence: .sisyphus/evidence/f4-scope-check.txt

  Scenario: 에이전트 결정론 오버라이드 검사
    Tool: Bash
    Steps:
      1. grep -c 'indent_level.*수동' plugins/hwpx-generator/agents/hwpx-builder.md
      2. 결과가 0인지 확인 (에이전트가 indent_level을 수동 계산하도록 하는 지시가 없음)
    Expected Result: 에이전트 수동 계산 지시 없음 (0건)
    Evidence: .sisyphus/evidence/f4-determinism-check.txt
  ```
  Output: `Tasks [N/N compliant] | VERDICT`

---

## Commit Strategy

| Wave | Commit | Files |
|------|--------|-------|
| 1 | `test(hwpx): add TDD tests for indent-level preservation` | tests/*.py |
| 2 | `feat(hwpx): implement indent-level detection and style mapping` | scripts/*.py |
| 3 | `docs(hwpx): update agent/skill/command docs for indent pipeline` | agents/*.md, skills/*.md, commands/*.md |
| 3 | `chore(hwpx): bump version for indent-preserve feature` | plugin.json, marketplace.json, AGENTS.md, README.md |

---

## Success Criteria

### Verification Commands
```bash
# 1. 기존 테스트 회귀 없음
cd plugins/hwpx-generator/skills/hwpx-core && python -m pytest tests/ -v
# Expected: ALL PASS

# 2. md_parser indent_level 확인
python3 scripts/md_parser.py ../../../../dev/hwpx_indent/5장.md | python3 -c "
import json, sys
data = json.load(sys.stdin)
bullets = [b for b in data['blocks'] if b['type'] == 'bullet']
assert all('indent_level' in b for b in bullets), 'Missing indent_level'
levels = set(b['indent_level'] for b in bullets)
assert len(levels) >= 2, f'Expected 2+ indent levels, got {levels}'
print(f'PASS: {len(bullets)} bullets with levels {levels}')
"
# Expected: PASS with 2+ distinct indent levels

# 3. xml_writer level 구분 확인
# Expected: indent_level 0과 1의 leftMargin 값이 다름
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All existing tests pass (회귀 없음)
- [ ] New tests pass
- [ ] 5장.md E2E pipeline works end-to-end
