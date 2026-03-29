# visual-generator 텍스트 환각/깨짐 방지 개선

## TL;DR

> **Quick Summary**: visual-generator에서 Gemini가 빈 CONTENT 블록에 환각 텍스트를 생성하는 문제를 프롬프트 규칙 강화(6.1) + 평가 로직 CONTENT 전달(6.2)로 해결
> 
> **Deliverables**:
> - prompt-designer.md: 빈 블록 방지 규칙 + FORBIDDEN 강화
> - prompt-validator.md: 빈 블록 검증 차원 추가
> - validation-rules-map.md: Rule 14 추가
> - generate_slide_images.py: CONTENT 추출 함수 + 평가 프롬프트 주입
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 5 → F1-F4

---

## Context

### Original Request
`dev/doc/09_숙련자_노하우_디지털화_텍스트깨짐_분석보고서.md` 분석 보고서에서 식별된 텍스트 환각/깨짐 문제의 근본 원인 2가지(6.1 프롬프트 빈 블록, 6.2 평가 로직 CONTENT 미전달)를 해결하는 계획.

### Interview Summary
**Key Discussions**:
- 구현 범위: 6.1(프롬프트 계층키) + 6.2(평가로직 CONTENT 전달). 6.3(한글 의미 검증)은 제외
- 계층 키는 기존 underscore prefix 컨벤션 유지 (dot-notation 미도입), "빈 블록 방지 규칙" 형태로 구현
- prompt-designer 에이전트에 규칙 내장 (문서화만이 아닌 에이전트 행동 변경)

**Research Findings**:
- `evaluate_image_quality()` (lines 238-346): `prompt_text` 받지만 `is_concept` 체크에만 사용. API에 CONTENT 미전달 → 5개 기준 중 3개 사실상 무효
- CONTENT 포맷: 이미 prefix 기반 플랫 구조(box1_item1, section2_kpi). 문제는 하위 텍스트 없는 블록 존재
- 3층 환각 방지 체계 존재하나 "빈 블록 검증" 규칙 누락
- golden reference 프롬프트(`assets/theme-examples/prompts/`)를 CONTENT 추출 테스트 fixture로 활용 가능

### Metis Review
**Identified Gaps** (addressed):
- 플랫 키 구조에서 부모-자식 관계 감지 패턴 정의 필요 → 테마별 부모키 패턴 목록으로 해결
- 소스 자료에 하위 개념 없을 때 prompt-designer가 추론하는 행동 규칙 필요 → Rule 7에 추론 허용 조건 명시
- 품질 보정 힌트 append된 prompt에서도 CONTENT 추출 정상 동작 필요 → `## CONTENT` ~ `## FORBIDDEN` 범위로 파싱
- 테마별 빈블록 규칙 면제 조건 필요 → concept 테마 전면 면제, comparison/title 슬라이드 면제
- backward compatibility 보장 → prompt_text 빈 값일 때 기존 동작 유지

---

## Work Objectives

### Core Objective
CONTENT 빈 블록으로 인한 Gemini 텍스트 환각을 프롬프트 생성 단계에서 방지하고, 평가 단계에서 환각을 탐지할 수 있도록 CONTENT 원문을 평가 모델에 전달한다.

### Concrete Deliverables
- `plugins/visual-generator/agents/prompt-designer.md` — Korean Text Safety Rule 7 + FORBIDDEN 18-19
- `plugins/visual-generator/agents/prompt-validator.md` — Dimension 8 빈 블록 서브체크
- `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — Rule 14
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` — `extract_content_section()` + `evaluate_image_quality()` 수정

### Definition of Done
- [ ] prompt-designer.md에 Rule 7 + FORBIDDEN 18-19 존재
- [ ] prompt-validator.md Dimension 8에 빈 블록 체크 존재
- [ ] validation-rules-map.md에 Rule 14 존재
- [ ] `extract_content_section()` 함수가 4-block 마크다운에서 CONTENT 추출
- [ ] `evaluate_image_quality()` API 호출 시 CONTENT 참조 포함
- [ ] prompt_text 빈 값일 때 기존 동작과 동일 (backward compatible)
- [ ] concept 테마에서 is_concept 오버라이드 로직 유지

### Must Have
- 빈 블록 방지 규칙이 prompt-designer에 generative rule로 존재 (하위 키 추론 허용)
- CONTENT 추출이 `[품질 보정 힌트]` 등 append된 텍스트를 무시
- evaluation prompt의 기존 rubric 텍스트 변경 없음 (CONTENT 참조만 append)

### Must NOT Have (Guardrails)
- ❌ CONTENT 키 포맷 변경 (dot-notation 도입 금지, 기존 underscore prefix 유지)
- ❌ content-organizer, content-reviewer 에이전트 수정
- ❌ SYSTEM_INSTRUCTION 변경 (lines 36-51)
- ❌ 품질 임계값 변경 (QUALITY_THRESHOLD=7.0, KOREAN_MIN_THRESHOLD=5.0)
- ❌ 새 평가 기준 추가 (korean_semantic_validity 등 — 6.3 범위 밖)
- ❌ 팔레트 hex 코드 추출 (별도 개선 건)
- ❌ Scene Description 누출 방지 로직 (간접적으로 빈 블록 방지로 완화됨)
- ❌ is_concept 오버라이드 로직 수정 (concept 테마 면제 유지)
- ❌ 평가 rubric 문구 변경 (CONTENT 참조만 append)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (generate_slide_images.py에 테스트 없음)
- **Automated tests**: None (Python 스크립트에 테스트 인프라 없음)
- **Framework**: none
- **Agent-Executed QA**: ALWAYS — 모든 태스크에 QA 시나리오 포함

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Agent markdown files**: Bash (grep/read) — 규칙 존재 여부, 포맷 정합성 검증
- **Python script**: Bash (python -c) — 함수 import, CONTENT 추출 테스트, backward compatibility 검증

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 독립 작업 4건):
├── Task 1: generate_slide_images.py에 extract_content_section() 함수 추가 [quick]
├── Task 2: prompt-designer.md에 Rule 7 + FORBIDDEN 18-19 추가 [quick]
├── Task 3: prompt-validator.md Dimension 8에 빈 블록 서브체크 추가 [quick]
└── Task 4: validation-rules-map.md에 Rule 14 추가 [quick]

Wave 2 (After Task 1 — 평가 로직 통합):
└── Task 5: evaluate_image_quality()에 CONTENT 주입 로직 추가 [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── F1: Plan Compliance Audit (oracle)
├── F2: Code Quality Review (unspecified-high)
├── F3: Real Manual QA (unspecified-high)
└── F4: Scope Fidelity Check (deep)
→ Present results → Get explicit user okay

Critical Path: Task 1 → Task 5 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 4 (Wave 1)
```

### Dependency Matrix

| Task | Blocked By | Blocks |
|------|-----------|--------|
| 1 | — | 5 |
| 2 | — | F1-F4 |
| 3 | — | F1-F4 |
| 4 | — | F1-F4 |
| 5 | 1 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: **4** — T1 → `quick`, T2 → `quick`, T3 → `quick`, T4 → `quick`
- **Wave 2**: **1** — T5 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. generate_slide_images.py에 `extract_content_section()` 함수 추가

  **What to do**:
  - `generate_slide_images.py` 파일의 `evaluate_image_quality()` 함수 위에 새 함수 `extract_content_section(prompt_text: str) -> str` 추가
  - 4-block 마크다운 프롬프트에서 `## CONTENT` 와 다음 `## ` 헤더(보통 `## FORBIDDEN ELEMENTS`) 사이의 텍스트를 추출
  - 파싱 로직:
    - `prompt_text`가 None이거나 빈 문자열이면 빈 문자열 반환
    - `## CONTENT` 헤더를 찾고, 다음 `## ` 헤더(또는 문자열 끝)까지의 내용 반환
    - `[품질 보정 힌트]` 등 append된 텍스트는 자연스럽게 무시됨 (FORBIDDEN 이후에 위치하므로)
  - 기존 `extract_prompt_content()` 함수(lines 62-74)와 혼동 금지 — 그 함수는 파일 전체를 읽는 용도

  **Must NOT do**:
  - 기존 함수/변수 이름 변경
  - import 추가 (re 모듈은 이미 사용 가능 여부 확인 후 필요시만 추가)
  - 다른 함수 수정 (이 태스크는 함수 추가만)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 함수 추가, 파일 1개 수정, 15줄 이내 코드
  - **Skills**: []
    - 추가 스킬 불필요 — 순수 Python 텍스트 파싱

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Task 5
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:62-74` — 기존 `extract_prompt_content()` 함수. 이 함수는 파일 전체를 읽는 용도이므로 혼동하지 말 것. 새 함수는 프롬프트 문자열 내에서 CONTENT 섹션만 추출
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:238-247` — `evaluate_image_quality()` 시작 부분. 새 함수를 이 위에 배치

  **API/Type References**:
  - 프롬프트 4-block 마크다운 구조: `## INSTRUCTION` → `## CONFIGURATION` → `## CONTENT` → `## FORBIDDEN ELEMENTS` 순서
  - CONTENT 섹션 포맷: `key: "value"` 형식의 한 줄씩 나열 (prompt-designer.md line 268-278 참조)

  **Test References**:
  - `assets/theme-examples/prompts/` — golden reference 프롬프트 파일들 (repo root 기준). CONTENT 추출 테스트에 실제 fixture로 활용 가능

  **WHY Each Reference Matters**:
  - generate_slide_images.py: 새 함수의 정확한 삽입 위치와 기존 코드 스타일(들여쓰기, docstring 형식) 참조
  - 4-block 구조: 파싱 대상의 정확한 포맷을 알아야 정규식/분할 로직 작성 가능
  - golden reference: 실제 프롬프트로 추출 결과 검증

  **Acceptance Criteria**:
  - [ ] `extract_content_section` 함수가 `evaluate_image_quality` 위에 존재
  - [ ] `extract_content_section('')` → `''` 반환
  - [ ] `extract_content_section(None)` → `''` 반환
  - [ ] golden reference 프롬프트 파일에서 CONTENT 섹션 정상 추출

  **QA Scenarios:**

  ```
  Scenario: 정상 프롬프트에서 CONTENT 추출 (happy path)
    Tool: Bash (python3 -c)
    Preconditions: generate_slide_images.py에 extract_content_section 함수 존재
    Steps:
      1. golden reference 프롬프트 파일 1개를 읽어서 extract_content_section()에 전달
         python3 -c "
         import sys; sys.path.insert(0, 'plugins/visual-generator/skills/slide-renderer/scripts')
         from generate_slide_images import extract_content_section
         prompt = open('assets/theme-examples/prompts/02_theme_gov.md').read()
         result = extract_content_section(prompt)
         assert len(result) > 0, 'CONTENT should not be empty'
         assert 'title:' in result or 'box1' in result, 'Should contain CONTENT keys'
         assert '## FORBIDDEN' not in result, 'Should not include FORBIDDEN section'
         print('PASS')"
      2. 추출된 CONTENT에 key: "value" 형식 라인이 포함되는지 확인
    Expected Result: 'PASS' 출력, CONTENT 키-값 쌍만 포함, FORBIDDEN 섹션 미포함
    Failure Indicators: ImportError, AssertionError, FORBIDDEN 텍스트가 결과에 포함
    Evidence: .sisyphus/evidence/task-1-content-extraction-happy.txt

  Scenario: 빈 프롬프트에서 빈 문자열 반환 (edge case)
    Tool: Bash (python3 -c)
    Preconditions: 동일
    Steps:
      1. python3 -c "
         import sys; sys.path.insert(0, 'plugins/visual-generator/skills/slide-renderer/scripts')
         from generate_slide_images import extract_content_section
         assert extract_content_section('') == '', 'Empty string should return empty'
         assert extract_content_section(None) == '', 'None should return empty'
         assert extract_content_section('no content here') == '', 'No CONTENT header should return empty'
         print('PASS')"
    Expected Result: 'PASS' 출력
    Failure Indicators: AssertionError, TypeError on None input
    Evidence: .sisyphus/evidence/task-1-content-extraction-edge.txt
  ```

  **Commit**: YES (groups with Task 5)
  - Message: `fix(visual-gen): pass CONTENT to evaluate_image_quality for hallucination detection`
  - Files: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`
  - Pre-commit: `python3 -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('syntax OK')"`

---

- [ ] 2. prompt-designer.md에 빈 블록 방지 규칙 + FORBIDDEN 강화

  **What to do**:
  - Korean Text Safety Rules 섹션에 **Rule 7: 빈 블록 방지(Empty Block Prevention)** 추가
    - 규칙 내용: "모든 시각적 블록(stepN, boxN, caseN, phaseN 등)은 최소 1개의 자식 키를 가져야 함"
    - 추론 허용 조건 명시: "소스 자료에 하위 개념이 없으면, 블록 라벨과 주변 맥락에서 1-2개 키워드 수준의 하위 항목을 추론. 추론된 항목은 소스 문서에 이미 존재하거나 블록 라벨에서 직접 유추 가능한 용어만 사용"
    - 테마별 면제 조건: concept 테마 전면 면제, comparison 테마의 before_/after_ 단독 키 허용, title/cover 슬라이드(CONTENT ≤5개) 면제
    - PASS/FAIL 예시 포함
  - FORBIDDEN ELEMENTS 템플릿 섹션의 **"공통 필수 추가 항목"** 서브헤더 아래(기존 항목 17 이후)에 **항목 18, 19** 추가
    - 18: "블록 내부의 설명 문구, 부연 텍스트, 서술적 문장 (CONTENT에 명시된 라벨만 배치)"
    - 19: "Scene Description의 서술적 표현을 렌더링 텍스트로 사용 (메타 지시는 시각 구성 가이드일 뿐 렌더링 대상이 아님)"
  - FORBIDDEN 최소 항목 수 카운트(line 296 부근 `최소 16개 항목`) → `최소 19개 항목`으로 업데이트

  **Must NOT do**:
  - 기존 Rule 1-6 수정
  - 기존 FORBIDDEN 항목 1-17 수정
  - CONTENT 키 포맷(underscore prefix) 변경
  - content-organizer 또는 content-reviewer 에이전트 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 마크다운 에이전트 파일 1개 수정, 규칙 텍스트 추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: F1-F4
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:454-489` — 기존 Korean Text Safety Rules 1-6. Rule 7을 동일한 포맷으로 추가
  - `plugins/visual-generator/agents/prompt-designer.md:299-323` — 기존 FORBIDDEN ELEMENTS 템플릿 (항목 1-17). 항목 18-19를 동일 포맷으로 추가
  - `plugins/visual-generator/agents/prompt-designer.md:279-285` — 테마별 CONTENT 키 패턴. Rule 7의 "시각적 블록" 정의에 참조

  **Analysis References**:
  - `dev/doc/09_숙련자_노하우_디지털화_텍스트깨짐_분석보고서.md:59-72` — 3.1절 1차 원인 분석. step1/step2는 하위 텍스트 있어 정상, step3~5/case1~3은 없어서 환각 발생한 패턴
  - `dev/doc/09_숙련자_노하우_디지털화_텍스트깨짐_분석보고서.md:193-248` — 6.1절 계층 키 표기법 제안. 구체적 개선 예시 참조 (단, dot-notation은 채택하지 않음)

  **WHY Each Reference Matters**:
  - Korean Text Safety Rules: 기존 6개 규칙의 포맷, 톤, 구체성 수준을 맞춰야 일관성 유지
  - FORBIDDEN 템플릿: 기존 17개 항목과 동일한 "한 줄 서술" 스타일로 작성
  - 분석 보고서: 실제 환각 발생 패턴과 원인을 이해한 상태에서 규칙 작성

  **Acceptance Criteria**:
  - [ ] Rule 7이 Korean Text Safety Rules 섹션에 존재 (기존 Rule 6 이후)
  - [ ] Rule 7에 추론 허용 조건 + 면제 조건 + PASS/FAIL 예시 포함
  - [ ] FORBIDDEN 항목 18, 19가 템플릿에 존재
  - [ ] 기존 Rule 1-6, FORBIDDEN 1-17 변경 없음

  **QA Scenarios:**

  ```
  Scenario: Rule 7 존재 및 내용 검증 (happy path)
    Tool: Bash (grep + read)
    Preconditions: prompt-designer.md가 수정된 상태
    Steps:
      1. grep -n 'Rule 7' plugins/visual-generator/agents/prompt-designer.md
         → 라인 번호 확인
      2. grep -c '추론' plugins/visual-generator/agents/prompt-designer.md
         → ≥1 (추론 허용 조건 존재)
      3. grep -c 'concept.*면제\|면제.*concept' plugins/visual-generator/agents/prompt-designer.md
         → ≥1 (concept 테마 면제 조건 존재)
      4. grep -c '항목 18\|항목 19\|18\.\|19\.' plugins/visual-generator/agents/prompt-designer.md
         → ≥1 (FORBIDDEN 18-19 존재)
    Expected Result: Rule 7 라인 존재 + 추론/면제/FORBIDDEN 18-19 모두 확인
    Failure Indicators: grep 결과 0건
    Evidence: .sisyphus/evidence/task-2-rule7-verification.txt

  Scenario: 기존 규칙 미변경 확인 (regression check)
    Tool: Bash (git diff)
    Preconditions: 수정 전 커밋이 존재
    Steps:
      1. git diff plugins/visual-generator/agents/prompt-designer.md에서
         삭제된 라인(-로 시작) 중 'Rule 1' ~ 'Rule 6' 포함 라인이 0건인지 확인
      2. 삭제된 라인 중 기존 FORBIDDEN 항목 텍스트가 0건인지 확인
    Expected Result: 기존 규칙에 대한 삭제(-) 라인 0건
    Failure Indicators: 기존 규칙 텍스트가 삭제되거나 수정됨
    Evidence: .sisyphus/evidence/task-2-no-regression.txt
  ```

  **Commit**: YES
  - Message: `feat(visual-gen): add empty-block prevention rule to prompt-designer`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`
  - Pre-commit: `grep -c 'Rule 7' plugins/visual-generator/agents/prompt-designer.md`

---

- [ ] 3. prompt-validator.md Dimension 8에 빈 블록 서브체크 추가

  **What to do**:
  - Dimension 8 (Korean Hallucination Risk) 섹션에 **5번째 서브체크: 빈 블록 검증** 추가
  - 체크 내용:
    - CONTENT의 블록 수준 키(boxN, sectionN, stepN, caseN, phaseN 등)가 최소 1개의 자식 키(boxN_*, sectionN_* 등)를 갖는지 확인
    - 자식 키 감지 패턴: 부모키 prefix + underscore (`box1_item1`, `section2_kpi`)
    - 면제 조건:
      - concept 테마: 전체 면제 (scene_element만 사용)
      - comparison 테마: `before_*` / `after_*` 단독 키 허용
      - title/cover 슬라이드: CONTENT 항목 5개 이하면 면제
      - `title`, `subtitle`, `lead_message`, `footnote_*` 등 단독 메타 키는 블록이 아님
    - REJECT 메시지: "빈 블록 발견: {key}. 하위 키({key}_item1, {key}_sub1 등)를 추가하세요."
  - Dimension 8의 기존 4개 서브체크(교차오염, 길이제한, anti-hallucination 프롬프트, 시각 채움 지시) 변경 금지

  **Must NOT do**:
  - Dimension 1-7 수정
  - Dimension 8 기존 서브체크 수정
  - 새로운 Dimension (9번) 추가 — 반드시 Dimension 8 내부에 서브체크로 추가

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 마크다운 파일 1개 수정, 검증 규칙 텍스트 추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: F1-F4
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-validator.md:36-108` — 기존 8개 Dimension. Dimension 8 내부 포맷과 서브체크 구조 참조
  - `plugins/visual-generator/agents/prompt-designer.md:279-285` — 테마별 CONTENT 키 패턴. 블록/자식 키 감지 패턴 정의에 활용

  **WHY Each Reference Matters**:
  - prompt-validator.md: 서브체크의 포맷(테이블, 체크 항목 구조, REJECT 메시지 스타일)을 기존과 일치시켜야 함
  - 키 패턴: 어떤 키가 "블록"이고 어떤 키가 "자식"인지 판별하는 규칙 정의의 근거

  **Acceptance Criteria**:
  - [ ] Dimension 8에 5번째 서브체크 "빈 블록 검증" 존재
  - [ ] 면제 조건 3개(concept, comparison, title/cover) 명시
  - [ ] REJECT 메시지에 구체적 블록명 포함
  - [ ] Dimension 1-7 및 Dimension 8 기존 체크 4개 미변경

  **QA Scenarios:**

  ```
  Scenario: 빈 블록 서브체크 존재 확인 (happy path)
    Tool: Bash (grep + read)
    Preconditions: prompt-validator.md 수정 완료
    Steps:
      1. grep -n '빈 블록\|Empty Block\|empty.block' plugins/visual-generator/agents/prompt-validator.md
         → 라인 번호 확인
      2. grep -c 'concept.*면제\|면제.*concept' plugins/visual-generator/agents/prompt-validator.md
         → ≥1
      3. grep -c 'REJECT' plugins/visual-generator/agents/prompt-validator.md 에서
         수정 전 대비 증가 확인 (새 REJECT 메시지 추가)
    Expected Result: 빈 블록 체크 + 면제조건 + REJECT 메시지 모두 존재
    Failure Indicators: grep 0건 또는 Dimension 8 이외 위치에 추가됨
    Evidence: .sisyphus/evidence/task-3-validator-check.txt
  ```

  **Commit**: YES (groups with Task 4)
  - Message: `feat(visual-gen): add empty-block validation to prompt-validator + rules-map`
  - Files: `plugins/visual-generator/agents/prompt-validator.md`, `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md`
  - Pre-commit: `grep -c '빈 블록' plugins/visual-generator/agents/prompt-validator.md`

---

- [ ] 4. validation-rules-map.md에 Rule 14 추가

  **What to do**:
  - validation-rules-map.md의 규칙 목록에 **Rule 14: 빈 블록 방지(Empty Block Prevention)** 추가
  - 기존 Rule 13(Circle-Number Marker Prohibition) 이후에 배치
  - Rule 14 내용:
    - 규칙명, 도입 버전, 영향 범위(prompt-designer + prompt-validator)
    - 점검 방법: CONTENT의 블록 수준 키에 대해 자식 키 존재 여부 확인
    - PASS/FAIL 예시
    - 면제 조건(concept, comparison, title/cover)
  - Summary Table(lines 437-453): Rule 14 항목 추가 + 총 규칙 수 `13 Rules` → `14 Rules`로 업데이트
  - Integration 섹션(lines 457-483): `24 validation points (8 + 3 + 13)` → `25 validation points (8 + 3 + 14)`로 업데이트
  - 기존 Rule 1-13 변경 금지
  **Must NOT do**:
  - 기존 Rule 1-13 수정
  - Rule 14 이외의 규칙 추가

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 참조 문서 1개에 규칙 1건 추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: F1-F4
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — 기존 13개 규칙 목록. 동일한 포맷(테이블, 설명, 예시 구조)으로 Rule 14 추가

  **Acceptance Criteria**:
  - [ ] Rule 14가 Rule 13 이후에 존재
  - [ ] Rule 14에 면제 조건, PASS/FAIL 예시 포함
  - [ ] 기존 Rule 1-13 변경 없음

  **QA Scenarios:**

  ```
  Scenario: Rule 14 존재 확인
    Tool: Bash (grep)
    Preconditions: validation-rules-map.md 수정 완료
    Steps:
      1. grep -n 'Rule 14\|14\.' plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md
         → 라인 번호 확인
      2. grep -c 'Empty Block\|빈 블록' plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md
         → ≥1
    Expected Result: Rule 14 존재 + 빈 블록 관련 키워드 확인
    Failure Indicators: grep 0건
    Evidence: .sisyphus/evidence/task-4-rule14-check.txt
  ```

  **Commit**: YES (groups with Task 3)
  - Message: `feat(visual-gen): add empty-block validation to prompt-validator + rules-map`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md`
  - Pre-commit: `grep -c 'Rule 14' plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md`

---

- [ ] 5. evaluate_image_quality()에 CONTENT 주입 로직 추가

  **What to do**:
  - `evaluate_image_quality()` 함수(line 238~) 내부에서 `extract_content_section(prompt_text)` 호출하여 CONTENT 추출
  - **삽입 위치**: evaluation_prompt 문자열 정의(line 267 `"""` 종료) 직후, `try:` 블록(line 269) 직전 — 즉 line 267-269 사이에 삽입
  - 추출된 CONTENT가 비어있지 않으면 evaluation_prompt에 참조 텍스트 append:
    ```
    content_section = extract_content_section(prompt_text)
    if content_section:
        evaluation_prompt += (
            "\n\n[참조 CONTENT - 이 텍스트만 이미지에 존재해야 함]\n"
            + content_section
        )
    ```
  - CONTENT가 비어있으면(빈 문자열, concept 테마, None 등) 기존 동작 유지 (아무것도 append 안 함)
  - `is_concept` 로직(line 243-247) 및 score override(line 322-324) 변경 금지
  - evaluation_prompt 변수의 기존 rubric 텍스트(line 249-267) 변경 금지
  - API 호출 구조(line 270-285)에서 contents 배열의 첫 번째 Part에 사용되는 `evaluation_prompt` 변수에 CONTENT가 포함되므로 API 호출 자체는 수정 불필요

  **Must NOT do**:
  - evaluation_prompt 기존 rubric 텍스트 변경 (CONTENT 참조만 append)
  - `is_concept` 로직 수정
  - score override 로직 수정
  - API 호출 구조(contents 배열) 변경
  - QUALITY_THRESHOLD, KOREAN_MIN_THRESHOLD 변경
  - 팔레트 hex 코드 추출 (별도 개선건)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 함수 내부 5줄 추가, 발신 경로 명확
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (단독)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1 (extract_content_section 함수 필요)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:238-346` — `evaluate_image_quality()` 전체. 특히 lines 249-267(evaluation_prompt), lines 270-285(API 호출), lines 243-247(is_concept), lines 322-324(score override)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:162-164` — `generate_image()` 내부에서 `evaluate_image_quality()` 호출 지점. `prompt_text=current_prompt` 전달 확인
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:203-204` — 품질 보정 힌트 append 로직. CONTENT 추출이 이 케이스에서도 정상 동작해야 함

  **Analysis References**:
  - `dev/doc/09_숙련자_노하우_디지털화_텍스트깨짐_분석보고서.md:136-151` — 4.2절 치명적 결함. API 호출에서 prompt_text가 빠진 코드 스니펫
  - `dev/doc/09_숙련자_노하우_디지털화_텍스트깨짐_분석보고서.md:258-287` — 6.2절 개선안. 변경 전/후 코드 예시

  **WHY Each Reference Matters**:
  - evaluate_image_quality 전체: CONTENT 주입 위치(evaluation_prompt 정의 직후), 수정 금지 영역(rubric, API 호출, is_concept)을 정확히 식별
  - generate_image 호출 지점: prompt_text가 이미 전달되고 있음을 확인 — 추가 인자 변경 불필요
  - 분석 보고서: 정확한 문제 지점과 기대 결과 확인

  **Acceptance Criteria**:
  - [ ] `evaluate_image_quality()` 내부에 `extract_content_section()` 호출 존재
  - [ ] CONTENT 비어있지 않을 때 evaluation_prompt에 `참조 CONTENT` 섹션 append
  - [ ] CONTENT 비어있을 때 기존 동작과 동일
  - [ ] 기존 rubric 텍스트 변경 없음
  - [ ] is_concept 로직 변경 없음

  **QA Scenarios:**

  ```
  Scenario: CONTENT 주입 확인 (happy path)
    Tool: Bash (python3 -c)
    Preconditions: Task 1의 extract_content_section + Task 5의 수정이 모두 적용된 상태
    Steps:
      1. python3 -c "
         import sys; sys.path.insert(0, 'plugins/visual-generator/skills/slide-renderer/scripts')
         import ast
         source = open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()
         tree = ast.parse(source)
         # evaluate_image_quality 함수 내부에서 extract_content_section 호출 확인
         found = False
         for node in ast.walk(tree):
             if isinstance(node, ast.Call) and hasattr(node, 'func'):
                 if hasattr(node.func, 'id') and node.func.id == 'extract_content_section':
                     found = True
         assert found, 'extract_content_section call not found in script'
         # '참조 CONTENT' 문자열 존재 확인
         assert '참조 CONTENT' in source, 'CONTENT reference string not found'
         print('PASS')"
    Expected Result: 'PASS' 출력
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-5-content-injection.txt

  Scenario: backward compatibility — 빈 prompt_text (edge case)
    Tool: Bash (python3 -c)
    Preconditions: 동일
    Steps:
      1. python3 -c "
         import sys; sys.path.insert(0, 'plugins/visual-generator/skills/slide-renderer/scripts')
         source = open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()
         # evaluation_prompt의 기존 rubric 텍스트가 유지되는지 확인
         assert 'korean_text_readability' in source, 'Original rubric criterion missing'
         assert 'korean_hallucination_detection' in source, 'Original rubric criterion missing'
         assert 'content_reference_accuracy' in source, 'Original rubric criterion missing'
         # if content_section 조건문이 있어 빈 CONTENT일 때 기존 동작 유지 보장
         assert 'if content_section' in source or 'if len(content_section)' in source, 'No guard for empty CONTENT'
         print('PASS')"
    Expected Result: 'PASS' 출력
    Failure Indicators: AssertionError, 기존 rubric 기준명이 사라지거나 변경됨
    Evidence: .sisyphus/evidence/task-5-backward-compat.txt
  ```

  **Commit**: YES (groups with Task 1)
  - Message: `fix(visual-gen): pass CONTENT to evaluate_image_quality for hallucination detection`
  - Files: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`
  - Pre-commit: `python3 -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('syntax OK')"`

---
## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, grep for rule text). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read())"` for syntax check. Review changed files for: unused imports, empty catches, commented-out code. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Syntax [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute EVERY QA scenario from EVERY task. Verify extract_content_section() with golden reference prompts. Verify backward compatibility with empty prompt_text. Verify CONTENT injection format. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git diff). Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|------------|
| 1 | `feat(visual-gen): add empty-block prevention rule to prompt-designer` | prompt-designer.md | grep "Rule 7" in file |
| 2 | `feat(visual-gen): add empty-block validation to prompt-validator + rules-map` | prompt-validator.md, validation-rules-map.md | grep "빈 블록" in files |
| 3 | `fix(visual-gen): pass CONTENT to evaluate_image_quality for hallucination detection` | generate_slide_images.py | python syntax check |

---

## Success Criteria

### Verification Commands
```bash
# prompt-designer Rule 7 존재
grep -c "Rule 7" plugins/visual-generator/agents/prompt-designer.md  # Expected: ≥1

# prompt-validator 빈 블록 체크 존재  
grep -c "빈 블록" plugins/visual-generator/agents/prompt-validator.md  # Expected: ≥1

# validation-rules-map Rule 14 존재
grep -c "Rule 14" plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md  # Expected: ≥1

# extract_content_section 함수 존재
grep -c "def extract_content_section" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py  # Expected: 1

# CONTENT 참조 주입 코드 존재
grep -c "참조 CONTENT" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py  # Expected: ≥1

# backward compatibility — 빈 prompt_text에서 에러 없음
python3 -c "
import sys; sys.path.insert(0, 'plugins/visual-generator/skills/slide-renderer/scripts')
from generate_slide_images import extract_content_section
assert extract_content_section('') == ''
assert extract_content_section(None) == ''
print('OK')
"  # Expected: OK
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All 4 deliverable files updated
- [ ] Backward compatible with empty prompt_text
- [ ] concept theme exemption preserved
