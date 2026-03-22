# HWPX Generator Plugin — 6대 버그 수정 + 에이전트 단순화

## TL;DR

> **Quick Summary**: HWPX 생성기의 표 색상(파란→흰), 본문 굵기(bold→plain), 이미지 미삽입, 이중삽입지점 역전, 에이전트 과잉지침 등 6대 결함을 수정한다. `analyze_template.py`에 데이터 기반 필터 추가, `xml_writer.py` 하드코딩 수정, `image_embedder.py` 압축 기능 추가, `hwpx-builder.md` 필수 규칙만 남기고 단순화.
> 
> **Deliverables**:
> - `analyze_template.py` — charpr_map textColor 확장, body/table_cell 필터, borderFill 교차검증
> - `xml_writer.py` — cellMargin 141 고정, textWidth 동기화
> - `image_embedder.py` — --max-width/--quality 압축, 경로 해석, MAX_HEIGHT 자동축소
> - `hwpx-builder.md` — 350줄 이하로 단순화, "치환 우선 편집" 원칙 도입, 필수 규칙만 유지
> - `SKILL.md` + 버전 bump
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 2 waves + docs + final
> **Critical Path**: T1 → T3 → T4 → T5 → F1-F4

---

## Context

### Original Request
Workflow 7 사용 중 6가지 결함:
1. 표가 파란색 (흰색이어야 함)
2. 본문이 bold (plain이어야 함)
3. 이미지 미삽입
4. 양식 문단 구조 미보존
5. 이중삽입지점 역전 (요약표에 전체내용, 본문에 플레이스홀더)
6. hwpx-builder 에이전트 과잉 지침으로 오류 유발

*(레퍼런스 파일과 이슈보고서는 리포지토리 외부에 위치. 분석 결과는 아래 "핵심 분석 결과" 섹션에 인라인됨)*

### 핵심 분석 결과
- 수정5: cellMargin=141/141/141/141, body charPr textColor=#000000, borderFillIDRef=46(투명)
- 수정3(실패): charPr 69 textColor=#0000FF(파랑) — 색상 역전이 원인
- analyze_template.py: 빈도 기반 휴리스틱이 bold charPr, 유색 borderFill 무필터 선택
- image_embedder.py: base_dir 해석 문제, 압축 부재, MAX_HEIGHT 초과 시 에러
- 이슈보고서 분석: 불릿 렌더링 = idRef(문자) + hc:left(여백) + level(자동들여쓰기) + leftMargin override. paraPr 교환 시 여백값도 함께 교환 필수. regex 치환으로 XML 손상 위험 (ET.fromstring 검증 필수)
- Canine89/hwpxskill 비교: "치환 우선 편집" 원칙 도입 필요 (HwpxSurgeon.replace_text() 활용), vertAlign 감지 누락, cellMargin은 템플릿마다 다름(510/142 vs 141 vs 0)

### Metis/Momus 반영사항
- charpr_map에 textColor 추가 (data-driven filter)
- borderFill 교차검증 (배경색만)
- 캐스케이딩 fallback: non-bold+검정 → 검정만 → non-bold만 → 최빈+경고
- cellMargin은 141 고정 (수정5 기준, 복잡한 추출 불필요)
- textWidth = width - 282 동기화
- 이미지 압축은 opt-in CLI 플래그
- hwpx-builder.md 단순화 (350줄 이하)
- "치환 우선 편집": HwpxSurgeon.replace_text()로 텍스트만 교체, 구조 보존

---

## Work Objectives

### Must Have
1. charpr_map에 textColor 필드 추가
2. body 스타일: bold charPr 제외 + 비검정 textColor 제외 (캐스케이딩 fallback)
3. table_cell borderFillIDRef: 유색 배경 제외 (header.xml borderFill 교차검증)
4. cellMargin left="141" right="141" top="141" bottom="141"
5. textWidth = width - 282
6. 이미지 압축 --max-width, --quality (opt-in)
7. MAX_HEIGHT 초과 시 자동축소 (에러 대신)
8. hwpx-builder.md ≤ 350줄, "치환 우선 편집" 원칙, 이중삽입 3원칙, 불릿 계층 규칙

### Must NOT Have
- 새 하드코딩 charPr ID 제외 (`cpr != "7"` 등)
- 새 Python 스크립트 생성
- extract_style_map() 전체 리팩토링
- cell_writer.py / hwpx-analyzer.md 변경
- 기존 테스트 삭제
- hwpx-builder.md 핵심 금지 3개(lxml/자체스크립트/hp:pic) 삭제
- 이미지 압축 기본값 변경 (opt-in 유지)

---

## Verification Strategy

- **Infrastructure**: YES — `plugins/hwpx-generator/skills/hwpx-core/tests/` with conftest.py
- **Automated tests**: YES (TDD) — failing test 먼저 → 수정 → 통과
- **Framework**: pytest
- **QA**: Agent-executed, evidence → `.sisyphus/evidence/`

---

## Execution Strategy

```
Wave 1 (Start Immediately — 3 parallel):
├── Task 1: analyze_template.py — textColor 확장 + body 필터 + borderFill 교차검증 [deep]
├── Task 2: xml_writer.py — cellMargin 141 + textWidth 282 [quick]
├── Task 3: image_embedder.py — 압축 + 경로 + MAX_HEIGHT [unspecified-high]

Wave 2 (After Wave 1 — 2 parallel):
├── Task 4: hwpx-builder.md — 단순화 + "치환 우선 편집" + 필수규칙만 [deep]
├── Task 5: SKILL.md + hwpx-generate.md + 버전 [quick]

Wave FINAL (After ALL — 4 parallel):
├── F1: pytest 전체 실행 (unspecified-high)
├── F2: 변경 파일 품질 검토 (unspecified-high)
├── F3: 각 Task QA 시나리오 재실행 (unspecified-high)
├── F4: Must Have/Must NOT Have 대조 (deep)
-> Present results -> Get explicit user okay
```

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 4, 5 | 1 |
| 2 | — | 4, 5 | 1 |
| 3 | — | 4, 5 | 1 |
| 4 | 1, 2, 3 | F1-F4 | 2 |
| 5 | 1, 2, 3 | F1-F4 | 2 |
| F1-F4 | 1-5 | user okay | FINAL |

---

## TODOs

- [x] 1. analyze_template.py — textColor 확장 + body 필터 + borderFill 교차검증 (TDD)

  **What to do**:
  - charpr_map에 `"textColor"` 키 추가 (기존 `"bold"`, `"fontSize_hu"` 옆)
  - body 스타일 선택 (lines 655-681): 하드코딩 `cpr != "5"` 제거, 캐스케이딩 필터 구현:
    (1) non-bold + 검정(#000000) → (2) 검정만 → (3) non-bold만 → (4) 최빈+경고
  - 헬퍼 `_has_colored_background(header_root, bf_id) → bool` 추가:
    faceColor 없거나 #FFFFFF → False(흰색), 그 외 → True(유색)
  - table_cell 선택 (lines 780-806): 유색 배경 borderFillIDRef 제외
  - table_header 선택 (lines 752-778): 동일 로직 적용
  - (hwpxskill 참고) vertAlign 추출 로직 추가 — subList의 vertAlign 저장

  **Must NOT do**:
  - 새 하드코딩 ID 제외, extract_style_map() 전체 리팩토링

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**: Wave 1 (with T2, T3) | Blocks: T4, T5 | Blocked By: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py:655-681` — body 선택. `cpr != "5"` 하드코딩
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py:407-416` — charpr_map 구조
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py:730-750` — bold 선택
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py:780-806` — table_cell 선택
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py:752-778` — table_header 선택
  - 수정5 분석: body charPr 69 → textColor=#000000(검정). 수정3: charPr 69 → #0000FF(파랑) — 색상 역전이 핵심 원인
  - 수정5 분석: borderFillIDRef=46 → 투명(흰색), =61 → #FFFFFF. proposal 템플릿 borderFill id=7 → #4472C4(파란)
  - Canine89/hwpxskill analyze_template.py: vertAlign, cellAddr 추출 로직 참고 (subList의 vertAlign 속성 추출)

  **Acceptance Criteria**:
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k body_excludes -v` → PASS
  - [ ] style_map["body"]["charPrIDRef"]가 bold=False, textColor∈{#000000, None}
  - [ ] `cpr != "5"` 코드가 제거됨
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k border_fill -v` → PASS
  - [ ] style_map["table_cell"]["borderFillIDRef"]가 무색/흰색 배경

  **QA Scenarios:**
  ```
  Scenario: Body filter — non-bold 검정 선택
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k body_excludes -v
    Expected Result: 1+ passed, 0 failed
    Evidence: .sisyphus/evidence/task-1-body-filter.txt

  Scenario: borderFill 배경색 필터
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k border_fill -v
    Expected Result: 유색 제외, 무색 선택
    Evidence: .sisyphus/evidence/task-1-borderfill.txt

  Scenario: Cascading fallback — 모든 후보가 bold
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k cascading_fallback -v
    Expected Result: 1 passed with warning
    Evidence: .sisyphus/evidence/task-1-fallback.txt
  ```

  **Commit**: `fix(hwpx): data-driven body/table style filter with textColor and borderFill`
  **Files**: `analyze_template.py`, test files

---

- [x] 2. xml_writer.py — cellMargin 141 고정 + textWidth 동기화 (TDD)

  **What to do**:
  - line 326: `left="283" right="283"` → `left="141" right="141" top="141" bottom="141"` (수정5 기준)
  - line 329: `width - 566` → `width - 282` (141×2)
  - 기존 테스트 업데이트: 283 → 141 반영

  **Must NOT do**: build_table() 구조 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**: Wave 1 (with T1, T3) | Blocks: T4, T5 | Blocked By: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:326` — `left="283" right="283"`
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:329` — `width - 566`
  - 수정5 분석: `<hp:cellMargin left="141" right="141" top="141" bottom="141"/>` (수정5는 완성된 HWPX 파일로, 이 값이 정상 렌더링의 기준)

  **Acceptance Criteria**:
  - [ ] 출력 XML에 `cellMargin left="141" right="141" top="141" bottom="141"`
  - [ ] textWidth = width - 282
  - [ ] 기존 테스트 전체 통과

  **QA Scenarios:**
  ```
  Scenario: Cell margin 검증
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_tables.py -v
    Expected Result: ALL PASSED
    Evidence: .sisyphus/evidence/task-2-margin.txt
  ```

  **Commit**: `fix(hwpx): cellMargin 283→141, textWidth width-566→width-282`
  **Files**: `xml_writer.py`, test files

---

- [x] 3. image_embedder.py — 압축 + 경로 해석 + MAX_HEIGHT 자동축소 (TDD)

  **What to do**:
  - `--max-width` CLI 추가 (기본: None = 압축안함). PIL.Image.resize() 비율유지
  - `--quality` CLI 추가 (기본: 85)
  - 경로 해석 실패 시 시도한 절대경로 포함 에러 메시지
  - MAX_IMAGE_HEIGHT 초과 시 에러 대신 자동 리사이즈 + 경고 로그

  **Must NOT do**: 기본동작 변경, 포맷 강제변환

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**: Wave 1 (with T1, T2) | Blocks: T4, T5 | Blocked By: None

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:134-173` — from-parsed 경로해석
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:176-186` — MAX_IMAGE_HEIGHT=70000
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:17` — PIL 이미 존재

  **Acceptance Criteria**:
  - [ ] --max-width 2000 → 2000px 초과 이미지 리사이즈
  - [ ] --max-width 미지정 → 기존과 동일
  - [ ] 경로 실패 에러에 절대경로 포함
  - [ ] MAX_HEIGHT 초과 → 자동축소 (에러 없음)

  **QA Scenarios:**
  ```
  Scenario: 이미지 압축
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -k compression -v
    Expected Result: PASSED
    Evidence: .sisyphus/evidence/task-3-compression.txt

  Scenario: MAX_HEIGHT 자동축소
    Tool: Bash (pytest)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -k auto_resize -v
    Expected Result: PASSED, 에러 없이 축소
    Evidence: .sisyphus/evidence/task-3-autoresize.txt
  ```

  **Commit**: `fix(hwpx): opt-in image compression, path errors, MAX_HEIGHT auto-resize`
  **Files**: `image_embedder.py`, test files

---

- [x] 4. hwpx-builder.md — 단순화 + "치환 우선 편집" + 필수규칙만

  **What to do**:
  - **핵심 원칙**: 너무 세밀한 지침은 오히려 에러 유발. 꼭 지켜야 할 것만 남기기
  - **"치환 우선 편집" 도입** (hwpxskill 참조): HwpxSurgeon.replace_text()로 텍스트만 교체하고 구조는 보존. 새 XML 생성보다 기존 구조 활용 우선
  - **이중삽입 3원칙**으로 압축: (1) 요약표 = 200자 이내 (2) 본문 = 전체내용 (3) 본문 먼저, 요약은 그 내용에서 추출
  - **불릿 계층 규칙** (이슈보고서): ◦ parent vs - child paraPrIDRef 구분 원칙
  - **과도한 예시/다이어그램 축소**: ASCII 박스 → 핵심 규칙 1줄
  - **금지 목록 정리**: 치명적 3개(lxml, 자체스크립트, hp:pic)만 "금지", 나머지는 "권장"
  - **사전검증 체크리스트**: style-map 선행추출 → xml_writer 필수사용 → validate.py 후행검증
  - **문서 편집 전문성**: 삽입 전 구조분석 → 삽입점 식별 → 내용삽입 → 검증 플로우

  **Must NOT do**:
  - 핵심 금지 3개 삭제 (lxml, 자체스크립트, hp:pic)
  - 새 상세 절차/다이어그램 추가
  - charPr 30-34 인라인 서식 규칙 삭제

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**: Wave 2 (with T5) | Blocks: F1-F4 | Blocked By: T1-T3

  **References**:
  - `plugins/hwpx-generator/agents/hwpx-builder.md` — 전체 426줄
  - `plugins/hwpx-generator/agents/hwpx-builder.md:128-205` — Template-Aware (단순화 대상)
  - `plugins/hwpx-generator/agents/hwpx-builder.md:207-282` — Dual-Zone (단순화 대상)
  - `plugins/hwpx-generator/agents/hwpx-builder.md:298-377` — 표/금지 패턴 (핵심만 유지)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py:451-456` — HwpxSurgeon.replace_text()
  - Canine89/hwpxskill SKILL.md의 "치환 우선 편집" 원칙: "새 문단/표 추가보다 기존 텍스트 노드 치환을 우선할 것" (Critical Rule 16)
  - 이슈보고서 분석: 불릿 렌더링 = idRef(문자) + hc:left(여백) + level(자동) + leftMargin override. paraPr 교환 시 여백값 함께 교환 필수

  **Acceptance Criteria**:
  - [ ] hwpx-builder.md ≤ 350줄
  - [ ] 핵심 금지 3개 존재
  - [ ] "치환 우선" 또는 "replace_text" 언급
  - [ ] 이중삽입 3원칙 존재 (요약/200자, 본문/전체, 본문먼저)
  - [ ] 불릿 계층 규칙 존재
  - [ ] 사전검증 체크리스트 존재

  **QA Scenarios:**
  ```
  Scenario: 종합 검증
    Tool: Bash (python)
    Steps:
      1. python -c "
         c=open('plugins/hwpx-generator/agents/hwpx-builder.md',encoding='utf-8').read()
         lines=len(c.splitlines())
         assert lines<=350, f'{lines}>350'
         assert 'lxml' in c
         assert '자체' in c or '생성 금지' in c
         assert 'hp:pic' in c
         assert '치환' in c or 'replace_text' in c
         assert '요약' in c and '200' in c
         assert '본문' in c and '전체' in c
         assert '먼저' in c
         assert '체크리스트' in c or '검증' in c
         print(f'ALL OK ({lines} lines)')"
    Expected Result: ALL OK (≤350 lines)
    Evidence: .sisyphus/evidence/task-4-builder-check.txt
  ```

  **Commit**: `fix(hwpx): simplify hwpx-builder, add substitution-first principle`
  **Files**: `hwpx-builder.md`

---

- [x] 5. SKILL.md + hwpx-generate.md + 버전 업데이트

  **What to do**:
  - SKILL.md: 새 CLI 플래그 반영 (--max-width, --quality)
  - SKILL.md: charpr_map textColor 확장 반영
  - SKILL.md: 불릿 계층 렌더링 원리 추가 (이슈보고서 섹션 3)
  - hwpx-generate.md: 이미지 파라미터 보강
  - plugin.json + marketplace.json: MINOR bump

  **Must NOT do**: 관련 없는 워크플로우 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**: Wave 2 (with T4) | Blocks: F1-F4 | Blocked By: T1-T3

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:100-150` — 스크립트 요약
  - `plugins/hwpx-generator/commands/hwpx-generate.md:8-11` — Config
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` — 버전
  - 이슈보고서 분석: 불릿 렌더링 = idRef + hc:left + level + leftMargin override. paraPr 87(◦, left=1500) vs 88(-, left=2500)

  **Acceptance Criteria**:
  - [ ] SKILL.md에 --max-width 문서화
  - [ ] SKILL.md에 불릿 계층 원리 포함
  - [ ] plugin.json MINOR bump

  **QA Scenarios:**
  ```
  Scenario: 문서 업데이트 확인
    Tool: Bash (python)
    Steps:
      1. python -c "c=open('plugins/hwpx-generator/skills/hwpx-core/SKILL.md',encoding='utf-8').read(); assert '--max-width' in c; print('OK')"
    Expected Result: OK
    Evidence: .sisyphus/evidence/task-5-docs.txt
  ```

  **Commit**: `docs(hwpx): update SKILL.md, version bump`
  **Files**: `SKILL.md`, `hwpx-generate.md`, `plugin.json`, `marketplace.json`

---

## Final Verification Wave

- [x] F1. **Test Suite** — `unspecified-high`
  ```bash
  python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v
  # Expected: ALL PASS, 0 failures
  # Evidence: copy output to .sisyphus/evidence/final-pytest.txt
  ```

- [x] F2. **Code Quality** — `unspecified-high`
  ```bash
  python -c "c=open('plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py',encoding='utf-8').read(); assert 'cpr != \"5\"' not in c; assert 'cpr != \"7\"' not in c; print('No hardcoded ID exclusions')"
  # Evidence: copy output to .sisyphus/evidence/final-quality.txt
  ```

- [x] F3. **QA Replay** — `unspecified-high`
  ```bash
  python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_analyze_template.py -k "body_excludes or border_fill or cascading_fallback" -v
  python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_tables.py -v
  python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -k "compression or auto_resize" -v
  # Evidence: copy each output to .sisyphus/evidence/final-qa-*.txt
  ```

- [x] F4. **Must Have/NOT Compliance** — `deep`
  ```bash
  python -c "
  at=open('plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py',encoding='utf-8').read()
  assert 'textColor' in at, 'MISSING: textColor'
  assert '_has_colored_background' in at, 'MISSING: borderFill helper'
  xw=open('plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py',encoding='utf-8').read()
  assert 'left=\"141\"' in xw, 'MISSING: cellMargin 141'
  assert 'width - 282' in xw, 'MISSING: textWidth formula'
  ie=open('plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py',encoding='utf-8').read()
  assert 'max_width' in ie or '--max-width' in ie, 'MISSING: compression'
  hb=open('plugins/hwpx-generator/agents/hwpx-builder.md',encoding='utf-8').read()
  assert len(hb.splitlines())<=350, 'TOO LONG'
  assert 'cpr != \"5\"' not in at, 'VIOLATION: hardcoded exclusion'
  print('ALL COMPLIANCE CHECKS PASSED')"
  # Evidence: copy output to .sisyphus/evidence/final-compliance.txt
  ```

- [x] F4. **Must Have/NOT Compliance** — `deep` (duplicate 체크)
  ```bash
  python -c "
  import os
  # Must Have checks
  at=open('plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py',encoding='utf-8').read()
  assert 'textColor' in at, 'MISSING: textColor in charpr_map'
  assert '_has_colored_background' in at, 'MISSING: borderFill helper'
  
  xw=open('plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py',encoding='utf-8').read()
  assert 'left=\"141\"' in xw, 'MISSING: cellMargin 141'
  assert 'width - 282' in xw, 'MISSING: textWidth formula'
  
  ie=open('plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py',encoding='utf-8').read()
  assert '--max-width' in ie or 'max_width' in ie, 'MISSING: compression flag'
  
  hb=open('plugins/hwpx-generator/agents/hwpx-builder.md',encoding='utf-8').read()
  lines=len(hb.splitlines())
  assert lines<=350, f'hwpx-builder.md too long: {lines}'
  assert '치환' in hb or 'replace_text' in hb, 'MISSING: substitution-first'
  
  # Must NOT Have checks
  assert 'cpr != \"5\"' not in at, 'VIOLATION: hardcoded ID exclusion'
  
  print('ALL COMPLIANCE CHECKS PASSED')
  " 2>&1 | tee .sisyphus/evidence/final-compliance.txt
  ```

> F1-F4 결과를 사용자에게 제시한 후 명시적 "okay"를 받아야 완료 처리.

---

## Commit Strategy

| # | Message | Files |
|---|---------|-------|
| 1 | `fix(hwpx): data-driven body/table style filter with textColor and borderFill` | analyze_template.py, tests |
| 2 | `fix(hwpx): cellMargin 283→141, textWidth width-566→width-282` | xml_writer.py, tests |
| 3 | `fix(hwpx): opt-in image compression, path errors, MAX_HEIGHT auto-resize` | image_embedder.py, tests |
| 4 | `fix(hwpx): simplify hwpx-builder, add substitution-first principle` | hwpx-builder.md |
| 5 | `docs(hwpx): update SKILL.md, version bump` | SKILL.md, hwpx-generate.md, plugin.json, marketplace.json |

---

## Success Criteria

```bash
python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v  # ALL PASS
```

- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] hwpx-builder.md ≤ 350줄
- [ ] Plugin version bumped
