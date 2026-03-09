# Visual Generator Revival: 4-Block Restoration + v2.x Best-of-Both

## TL;DR

> **Quick Summary**: ae35fe6 커밋의 4-block 마크다운 프롬프트 형식(~100줄, 상세한 Content Placement/Rendering Style/FORBIDDEN)을 복원하되, v2.2.0의 핵심 장점(prompt-validator, Style Sheet, render_text/scene_context 분류, Golden Reference, 참조 문서 3종)을 이식한다. `### Scene Description` 서브섹션을 새로 추가하여 v2.x의 `<scene>` 품질 개선도 통합한다.
>
> **Deliverables**:
> - prompt-designer.md 전면 재작성 (ae35fe6 기반 + v2.x 기능)
> - prompt-validator.md 4-block 적응 (7차원 유지)
> - renderer-agent.md 4-block 검증 적응
> - 6개 테마 스킬 Golden Reference 4-block 변환
> - visual-generate.md 오케스트레이터 업데이트
> - content-organizer.md, content-reviewer.md 참조 업데이트
> - 참조 문서 3종 태그명 치환
> - generate_slide_images.py 버그 수정 5건
> - plugin.json + marketplace.json v3.0.0 버전 범프
> - AGENTS.md 업데이트
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 → Task 2 → Task 4 → Task 5 → Task 7 → Task 9 → Task 10 → Task 11

---

## Context

### Original Request
사용자가 ae35fe6 커밋의 visual-generator를 가장 선호함. 해당 버전의 상세한 프롬프트(~100줄)가 훨씬 정확한 이미지를 생성함. 하지만 ae35fe6에도 문제(불필요한 텍스트 렌더링, 테마 혼동, 슬라이드 간 비통일성)가 있었음. 최신 v2.2.0의 장점을 취합하되, XML-tag의 프롬프트 빈약함(~30줄)은 버리고 싶음.

### Interview Summary
**Key Discussions**:
- 프롬프트 형식: 4-block 마크다운 복원 확정 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN)
- CONTENT 블록: `key: "value"` 형식 채용 (메타데이터 렌더링 방지)
- v2.x 유지 기능: prompt-validator, Style Sheet, render_text/scene_context, Golden Reference, 참조 문서 3종
- generate_slide_images.py: SYSTEM_INSTRUCTION + 품질 재시도 유지
- 버그 수정: set -e, exclude list, color code, concept 텍스트, 강건한 렌더링 구조
- 검증: 프롬프트 구조 + 실제 Gemini 렌더링

### Metis Review
**Identified Gaps** (addressed):
- **SHOWSTOPPER**: `<scene>` 내용의 4-block 배치 → `### Scene Description` 신규 서브섹션으로 해결
- ae35fe6를 단순 복원이 아닌 **SYNTHESIS** (이전에 존재하지 않던 조합을 새로 만드는 것) → 계획에 반영
- CONTENT 블록의 flat vs hierarchical 형식 → flat `key: "value"` 확정
- Style Sheet 추출 로직 4-block 적응 필요 → Task에 포함
- 6개 Golden Reference가 TDD 앵커 역할 → 테마 변환을 최우선 배치
- v3.0.0 MAJOR 버전 범프 필수 → 마지막 Task에 포함
- 참조 문서는 태그명 치환만 (내용 재작성 금지) → 가드레일 설정

### 추가 분석: 팔레트 불일치 근본 원인 (2026-03-09)
**발견**: v2.2.0의 Style Sheet 시스템이 실제로 동작하지 않음. 두 가지 근본 원인:
1. **content-organizer 상류 문제**: `theme_recommendation.md`가 슬라이드별 다른 "무드 팔레트" 배정 (Gov: slide01=#1E3A5F, slide02=#2C3E50, slide03=#2E5090)
2. **prompt-designer 중류 문제**: Phase 2.5 Style Sheet 코드 있으나 `style_sheet.md` 실제 미생성
**해결**: (1) content-organizer에 세션 전체 고정 팔레트 규칙 추가, (2) prompt-designer에서 style_sheet.md 실제 생성+follow 보장

---

## Work Objectives

### Core Objective
ae35fe6의 상세한 4-block 프롬프트 품질을 복원하면서, v2.x의 품질 보호장치(validator, style sheet, golden reference)를 유지하여 "Best-of-Both" visual-generator v3.0.0을 완성한다.

### Concrete Deliverables
- `plugins/visual-generator/agents/prompt-designer.md` — 4-block 생성 엔진 (ae35fe6 기반 + v2.x)
- `plugins/visual-generator/agents/prompt-validator.md` — 4-block 7차원 검증
- `plugins/visual-generator/agents/renderer-agent.md` — 4-block 최종 검증
- `plugins/visual-generator/agents/content-organizer.md` — 참조 업데이트
- `plugins/visual-generator/agents/content-reviewer.md` — 참조 업데이트
- `plugins/visual-generator/commands/visual-generate.md` — 오케스트레이터 업데이트
- `plugins/visual-generator/skills/theme-{gov,seminar,concept,comparison,pitch,whatif}/SKILL.md` — 4-block Golden Reference
- `plugins/visual-generator/skills/slide-renderer/references/*.md` — 태그명 치환
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` — 버그 수정
- `plugins/visual-generator/.claude-plugin/plugin.json` — v3.0.0
- `.claude-plugin/marketplace.json` — v3.0.0 동기화
- `AGENTS.md` — 아키텍처 반영

### Definition of Done
- [ ] 생성된 body 슬라이드 프롬프트 ≥ 80줄
- [ ] 생성된 title 슬라이드 프롬프트 ≥ 50줄
- [ ] 4-block 구조 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) 100% 준수
- [ ] 6개 Golden Reference가 prompt-validator 7차원 모두 PASS
- [ ] Gemini 렌더링 품질 점수 ≥ 7.0
- [ ] 슬라이드 간 팔레트/스타일 일관성: theme_recommendation.md에 고정 팔레트 1개, style_sheet.md 실제 생성, 모든 슬라이드 동일 팔레트
- [ ] Color # 코드 이미지 미렌더링
- [ ] Concept 테마 텍스트 미렌더링
- [ ] style_sheet.md, validation_result.md 렌더링 시도 없음

### Must Have
- 4-block 마크다운 프롬프트 형식 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN)
- CONTENT 블록 `key: "value"` 형식
- `### Scene Description` 서브섹션 (INSTRUCTION 내, 5-7문장, 7요소 중 5+, negative prompting)
- `### Rendering Style` 서브섹션 (7개 요소별 상세 지시)
- `### Content Placement` 서브섹션 (CONTENT 값을 따옴표로 인용하여 배치)
- `## FORBIDDEN ELEMENTS` 블록 (15+ 금지 항목)
- prompt-validator 7차원 검증 (4-block 적응)
- Style Sheet 기반 슬라이드 간 일관성 (**실제 동작 보장** — style_sheet.md 생성 + follow 강제)
- content-organizer의 theme_recommendation.md에 세션 전체 **고정 팔레트 1개** 출력 (슬라이드별 다른 팔레트 배정 금지)
- Golden Reference 6개 테마 인라인
- generate_slide_images.py SYSTEM_INSTRUCTION + 품질 재시도

### Must NOT Have (Guardrails)
- XML 태그 (`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`) 프롬프트 출력에 사용 금지
- 참조 문서 내용 재작성 금지 (태그명 치환만)
- layout-types SKILL.md 수정 금지
- slide-renderer SKILL.md 수정 금지
- content-organizer 출력 스키마 변경 금지 (render_text/scene_context 유지)
- prompt-validator 검증 차원 추가/삭제 금지 (7차원 유지)
- generate_slide_images.py 형식 의존 로직 변경 금지 (버그 수정만)
- 프롬프트에 pt/px 단위 사용 금지
- 프롬프트에 구체적 폰트 패밀리명 사용 금지
- CONTENT 블록에 테이블/번호 목록 사용 금지

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (plugin ecosystem, no unit test framework)
- **Automated tests**: None (agent-executed QA only)
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Prompt Structure**: Use Bash (grep) — Pattern match for 4-block headers, line counts, format compliance
- **Prompt Quality**: Use Bash (python) — Run prompt-validator against generated prompts
- **Rendering**: Use Bash (python) — Run generate_slide_images.py, capture quality scores
- **File Integrity**: Use Bash (wc, grep) — Line counts, no XML tags remaining

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — 4-block format spec + first Golden Reference):
├── Task 1: Define 4-block prompt format specification in prompt-designer [deep]
├── Task 2: Convert theme-gov Golden Reference to 4-block (TDD anchor) [deep]
└── Task 3: Fix generate_slide_images.py bugs (5건) [quick]

Wave 2 (Parallel theme conversions + validator adaptation):
├── Task 4: Convert theme-seminar Golden Reference [quick]
├── Task 5: Convert theme-concept Golden Reference [quick]
├── Task 6: Convert theme-whatif Golden Reference [quick]
├── Task 7: Convert theme-pitch Golden Reference [quick]
├── Task 8: Convert theme-comparison Golden Reference [quick]
└── Task 9: Adapt prompt-validator to 4-block (7 dimensions) [deep]

Wave 3 (Core pipeline adaptation):
├── Task 10: Full prompt-designer rewrite (ae35fe6 base + v2.x) [deep]
├── Task 11: Adapt renderer-agent to 4-block validation [unspecified-high]
├── Task 12: Update orchestrator + supporting agents [unspecified-high]
└── Task 13: Update reference docs (tag name replacement) [quick]

Wave 4 (Integration + version bump):
├── Task 14: End-to-end integration test with Gemini rendering [deep]
└── Task 15: Version bump v3.0.0 + AGENTS.md + registry updates [quick]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA with Gemini rendering (unspecified-high + slide-renderer skill)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 2 → Task 9 → Task 10 → Task 11 → Task 14 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 6 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2, 4-8, 10 | 1 |
| 2 | 1 | 9, 10 | 1 |
| 3 | — | 14 | 1 |
| 4 | 1 | 14 | 2 |
| 5 | 1 | 14 | 2 |
| 6 | 1 | 14 | 2 |
| 7 | 1 | 14 | 2 |
| 8 | 1 | 14 | 2 |
| 9 | 1, 2 | 10, 11, 14 | 2 |
| 10 | 1, 2, 9 | 11, 14 | 3 |
| 11 | 9, 10 | 14 | 3 |
| 12 | 10 | 14 | 3 |
| 13 | — | 14, 15 | 3 |
| 14 | 3-13 | 15 | 4 |
| 15 | 14 | F1-F4 | 4 |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T1 `deep`, T2 `deep`, T3 `quick`
- **Wave 2**: 6 tasks — T4-T8 `quick`, T9 `deep`
- **Wave 3**: 4 tasks — T10 `deep`, T11 `unspecified-high`, T12 `unspecified-high`, T13 `quick`
- **Wave 4**: 2 tasks — T14 `deep`, T15 `quick`
- **FINAL**: 4 tasks — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. Define 4-Block Prompt Format Specification

  **What to do**:
  - `plugins/visual-generator/agents/prompt-designer.md`의 상단 "4-Block Prompt Structure" 섹션을 새로 작성 (ae35fe6의 4-block 템플릿 구조를 기반으로)
  - 아래 INSTRUCTION 서브섹션 6개를 정의:
    1. `### Image Purpose` — 이미지 목적/용도
    2. `### Target Audience` — 대상 청중
    3. `### Key Message` — 핵심 메시지
    4. `### Scene Description` — **신규** (v2.x `<scene>` 대체, 5-7문장, Scene Guide 7요소 중 5+, negative prompting 필수)
    5. `### Rendering Style` — 7요소별 상세 지시 (서피스/배경/코너/연결선/시각장식/공간구성/시각메타포)
    6. `### Content Placement` — CONTENT 값을 따옴표로 인용하여 배치 위치와 방식 설명
  - CONFIGURATION 서브섹션 4개: `### Canvas Settings`, `### Background Treatment`, `### Color Palette`, `### Typography`
  - CONTENT 블록: `key: "value"` 형식만 허용 (테이블/번호 목록 금지, `### subsection` 금지)
  - FORBIDDEN ELEMENTS 블록: 15+ 금지 항목 템플릿 (ae35fe6의 FORBIDDEN 기반 + 폰트명 금지 + color code 금지 추가)
  - Style Sheet 관리 섹션: style_sheet_mode="create" / "follow" 로직 명시
  - 이 Task에서는 형식 사양(spec)만 작성. 전체 prompt-designer 재작성은 Task 10에서 수행.

  **Must NOT do**:
  - 전체 prompt-designer를 재작성하지 않음 (형식 사양만)
  - XML 태그를 프롬프트 형식에 사용하지 않음

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 아키텍처 결정이 포함된 설계 작업. ae35fe6 코드와 현재 코드를 모두 읽고 통합해야 함.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `slide-renderer`: 참조 문서 읽기가 필요하지만 에이전트가 직접 Read로 접근 가능

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 1 기반 태스크)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 2, 4-8, 10
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `git show ae35fe6:plugins/visual-generator/agents/prompt-designer.md` — ae35fe6의 4-block 템플릿 구조 (767줄). "4-Block Prompt Structure" 섹션의 Block 1-4 정의, 테마별 규칙, Text Density Rules, concept 특별 규칙을 참조하여 형식 사양의 기반으로 삼는다.
  - `plugins/visual-generator/agents/prompt-designer.md` (현재 HEAD) — XML-tag 구조 (214줄). Scene Description 요구사항(`<scene>` 최소 5문장, 7요소 중 5+, negative prompting), Style Sheet 관리 섹션(Phase 2.5), 최소 텍스트 밀도 규칙을 4-block 형식에 이식한다.

  **API/Type References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — Scene Description 품질 기준 (EXCELLENT 등급: 5문장+, 7요소 중 5+, negative prompting). `### Scene Description` 서브섹션 요구사항을 이 문서에서 도출한다.
  - `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` — Typography 서브섹션에 포함할 한글 렌더링 필수 문구.

  **External References**:
  - `assets/theme-examples/prompts/02_theme_gov.md` — ae35fe6가 생성한 실제 gov 프롬프트 (106줄). 목표 프롬프트 상세도의 기준선.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 4-block 형식 사양이 prompt-designer.md에 존재
    Tool: Bash (grep)
    Preconditions: Task 완료 후 prompt-designer.md 저장됨
    Steps:
      1. grep -c "## INSTRUCTION\|## CONFIGURATION\|## CONTENT\|## FORBIDDEN ELEMENTS" plugins/visual-generator/agents/prompt-designer.md
      2. grep -c "### Scene Description" plugins/visual-generator/agents/prompt-designer.md
      3. grep -c "### Rendering Style" plugins/visual-generator/agents/prompt-designer.md
      4. grep -c "### Content Placement" plugins/visual-generator/agents/prompt-designer.md
      5. grep -c 'key: "value"' plugins/visual-generator/agents/prompt-designer.md
    Expected Result: Step 1 ≥ 4, Steps 2-5 각각 ≥ 1
    Failure Indicators: 4-block 헤더 누락, Scene Description 서브섹션 없음
    Evidence: .sisyphus/evidence/task-1-format-spec-check.txt

  Scenario: XML 태그가 형식 사양에 없음
    Tool: Bash (grep)
    Preconditions: prompt-designer.md 저장됨
    Steps:
      1. grep -c "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: 0 (XML 태그 패턴 없음, 또는 "이전 형식" 비교 설명 내에서만)
    Evidence: .sisyphus/evidence/task-1-no-xml-tags.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): define 4-block prompt format spec`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`

- [x] 2. Convert theme-gov Golden Reference to 4-Block (TDD Anchor)

  **What to do**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md`의 "Golden Reference Example" 섹션을 4-block 형식으로 변환
  - 현재 XML Golden Reference (약 50줄)를 ae35fe6 스타일의 4-block Golden Reference (≥80줄)로 확장
  - 4-block 구조: `## INSTRUCTION` (Image Purpose, Target Audience, Key Message, Scene Description, Rendering Style, Content Placement) → `## CONFIGURATION` (Canvas, Background, Color Palette, Typography) → `## CONTENT` (key: "value" 형식) → `## FORBIDDEN ELEMENTS`
  - Scene Description: 현재 `<scene>` 내용을 자연어 5-7문장으로 변환, scene-richness-spec.md 7요소 중 5+ 포함
  - Content Placement: CONTENT의 모든 value를 따옴표로 인용하여 위치/크기/방식 설명
  - FORBIDDEN: ae35fe6 패턴 + 폰트명 금지 + color code 금지 추가
  - Mood Palette 테이블, Scene Guide, Positive Scene Direction, 한글 타이포그래피 가이드 섹션은 유지 (Golden Reference만 변환)
  - **이 Golden Reference가 나머지 5개 테마 변환의 템플릿 역할을 함 (TDD 앵커)**

  **Must NOT do**:
  - Mood Palette, Scene Guide 등 기존 테마 가이드 섹션 삭제/변경 금지
  - Golden Reference에 XML 태그 사용 금지
  - CONTENT에 테이블/번호 목록 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: ae35fe6 예시 프롬프트와 현재 XML Golden Reference를 모두 참조하여 통합해야 함
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Task 1 완료 후)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4-8, 9, 10
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `assets/theme-examples/prompts/02_theme_gov.md` — ae35fe6의 실제 gov 프롬프트 (106줄). Content Placement 상세도, Rendering Style 7요소, FORBIDDEN 15+항목의 참조 기준.
  - `plugins/visual-generator/skills/theme-gov/SKILL.md:68-131` — 현재 XML Golden Reference. `<scene>` 영문 장면 묘사와 `<text_to_render>` key:value 목록을 4-block으로 변환한다.

  **API/Type References**:
  - Task 1에서 정의한 4-block 형식 사양 — Golden Reference가 이 형식을 정확히 따라야 함

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: Golden Reference가 4-block 구조를 따름
    Tool: Bash (grep, wc)
    Preconditions: theme-gov/SKILL.md 저장됨
    Steps:
      1. Golden Reference 코드블록 내에서 "## INSTRUCTION", "## CONFIGURATION", "## CONTENT", "## FORBIDDEN ELEMENTS" 4개 헤더 존재 확인
      2. Golden Reference 코드블록 줄 수 카운트
      3. CONTENT 영역에 key: "value" 형식만 존재 확인 (테이블/번호 없음)
      4. FORBIDDEN 영역에 색상 코드 금지 항목 존재 확인
    Expected Result: 4개 헤더 존재, ≥80줄, key:"value" only, color code 금지 포함
    Failure Indicators: 헤더 누락, 줄 수 부족, 테이블 잔존
    Evidence: .sisyphus/evidence/task-2-gov-golden-ref.txt

  Scenario: XML 태그가 Golden Reference에 없음
    Tool: Bash (grep)
    Steps:
      1. grep "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/skills/theme-gov/SKILL.md
    Expected Result: 0 matches (XML tag references 제거됨)
    Evidence: .sisyphus/evidence/task-2-gov-no-xml.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): convert theme-gov Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-gov/SKILL.md`

- [x] 3. Fix generate_slide_images.py Bugs (5건)

  **What to do**:
  - **Bug 1: exclude 목록 수정** — `style_sheet.md`, `validation_result.md`, `prompt_index.md`를 exclude_files 목록에 추가
  - **Bug 2: 강건한 렌더링 대상 선별** — 화이트리스트 방식 도입: `NN_*.md` 패턴(예: `01_`, `02_`)에 매칭되는 파일만 렌더링 대상으로 인식. 또는 exclude를 보강하여 비프롬프트 파일을 확실히 걸러냄
  - **Bug 3: set -e 중단 방지** — 스크립트 내 개별 렌더링 실패 시 전체 중단 대신 해당 파일만 스킵하고 계속 진행하도록 에러 핸들링 강화 (try/except 패턴 확인)
  - **Bug 4: Color # 코드 렌더링 방지** — SYSTEM_INSTRUCTION에 "Never render hex color codes like #XXXXXX as visible text in the image" 문구 추가
  - **Bug 5: Concept 테마 텍스트 렌더링 방지** — SYSTEM_INSTRUCTION에 concept 테마용 "This is a Kurzgesagt-style illustration. Render ZERO text" 조건부 지시 추가 (또는 프롬프트 자체에서 해결 — Task 5와 연계)
  - 기존 SYSTEM_INSTRUCTION, 품질 임계값(7.0), 재시도 로직(MAX_QUALITY_RETRIES=2) 유지

  **Must NOT do**:
  - SYSTEM_INSTRUCTION 전체 삭제/재작성 금지
  - 품질 임계값/재시도 로직 변경 금지
  - 4-block/XML 형식 의존 파싱 로직 추가 금지 (스크립트는 형식 무관하게 전체 .md를 읽음)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Python 스크립트 버그 수정 5건, 명확한 변경 범위
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (Tasks 1, 2와 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:1-50` — 현재 스크립트 상단. SYSTEM_INSTRUCTION, API 설정, exclude 로직 위치 확인
  - `개선사항.md` — 사용자가 보고한 5가지 구체적 버그 (Ctrl+C 중단, exclude 누락, color code 렌더링, concept 텍스트, 통일성)

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: exclude 목록에 메타데이터 파일 포함
    Tool: Bash (grep)
    Steps:
      1. grep -c "style_sheet\|validation_result\|prompt_index" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: ≥ 3 (3개 파일 모두 exclude에 포함)
    Evidence: .sisyphus/evidence/task-3-exclude-list.txt

  Scenario: SYSTEM_INSTRUCTION에 color code 금지 문구
    Tool: Bash (grep)
    Steps:
      1. grep -i "hex color\|color code\|#[A-F0-9]" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: ≥ 1 match (금지 문구 존재)
    Evidence: .sisyphus/evidence/task-3-color-code-ban.txt
  ```

  **Commit**: YES
  - Message: `fix(visual-gen): fix generate_slide_images.py exclude list and rendering robustness`
  - Files: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`

- [x] 4. Convert theme-seminar Golden Reference to 4-Block

  **What to do**:
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md`의 Golden Reference를 4-block 형식으로 변환
  - Task 2에서 완성한 theme-gov Golden Reference를 템플릿으로 사용
  - 현재 XML Golden Reference를 ae35fe6 스타일 4-block으로 확장 (≥80줄)
  - seminar 테마 고유 특성 반영: 에디토리얼 매거진 × 아이소메트릭 3D, 포토리얼리스틱 3D 아이콘
  - Scene Description: seminar `<scene>` 내용을 5-7문장 자연어로 변환, 7요소 중 5+
  - CONTENT: `key: "value"` 형식만 허용
  - FORBIDDEN: 15+ 항목 (폰트명, color code, 비정형 텍스트 등)
  - Mood Palette, Scene Guide 등 기존 테마 가이드 섹션 유지 (Golden Reference만 변환)

  **Must NOT do**:
  - Mood Palette, Scene Guide 등 기존 섹션 삭제/변경 금지
  - Golden Reference에 XML 태그 사용 금지
  - CONTENT에 테이블/번호 목록 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task 2의 gov 패턴을 그대로 따르는 반복 작업. 테마별 색상/스타일만 다름.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (Tasks 4-8과 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2에서 완성한 4-block Golden Reference. 이 파일의 Golden Reference 구조를 그대로 복제하되, seminar 테마에 맞게 내용만 교체.
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md` — 현재 XML Golden Reference (117줄). Mood Palette/Scene Guide 유지, Golden Reference 섹션만 변환.
  - `assets/theme-examples/prompts/03_theme_seminar.md` — ae35fe6의 seminar 프롬프트. 상세도 기준 참조.

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: seminar Golden Reference 4-block 구조 확인
    Tool: Bash (grep, wc)
    Preconditions: theme-seminar/SKILL.md 저장됨
    Steps:
      1. Golden Reference 내 "## INSTRUCTION", "## CONFIGURATION", "## CONTENT", "## FORBIDDEN ELEMENTS" 4개 헤더 존재 확인
      2. Golden Reference 줄 수 ≥80
      3. CONTENT에 key: "value" 형식만 존재
    Expected Result: 4개 헤더, ≥80줄, key:"value" only
    Evidence: .sisyphus/evidence/task-4-seminar-golden-ref.txt

  Scenario: XML 태그 미존재
    Tool: Bash (grep)
    Steps:
      1. grep "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/skills/theme-seminar/SKILL.md
    Expected Result: 0 matches
    Evidence: .sisyphus/evidence/task-4-seminar-no-xml.txt
  ```

  **Commit**: YES (group with Tasks 5-8)
  - Message: `refactor(visual-gen): convert theme-seminar Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-seminar/SKILL.md`

- [x] 5. Convert theme-concept Golden Reference to 4-Block

  **What to do**:
  - `plugins/visual-generator/skills/theme-concept/SKILL.md`의 Golden Reference를 4-block 형식으로 변환
  - Task 2의 theme-gov Golden Reference를 템플릿으로 사용
  - **concept 특수 규칙**: Kurzgesagt 스타일이므로 CONTENT 섹션에 scene elements만 포함 (render_text 없음), FORBIDDEN에 "ALL text rendering" 강조
  - Scene Description: concept `<scene>` 내용을 시각적 장면 묘사 5-7문장으로 확장
  - CONTENT: `key: "value"` 형식이되, value가 scene element 설명 (텍스트가 아닌 시각 요소)
  - FORBIDDEN: 최우선 "DO NOT render any text" + 15+ 추가 항목
  - 기존 테마 가이드 섹션 유지

  **Must NOT do**:
  - concept CONTENT에 render_text 항목 포함 금지 (scene_context only)
  - FORBIDDEN에 "zero text" 규칙 누락 금지
  - 기존 테마 가이드 섹션 삭제/변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task 2 패턴 따르되, concept 특수 규칙(zero text)만 적용하는 변형 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (Tasks 4-8과 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2 완성 4-block Golden Reference 템플릿
  - `plugins/visual-generator/skills/theme-concept/SKILL.md` — 현재 XML Golden Reference (92줄). concept 전용 `<scene>` 묘사와 scene_context 분류 참조.
  - `assets/theme-examples/prompts/01_theme_concept.md` — ae35fe6의 concept 프롬프트 (98줄). Scene Elements 테이블 구조, Kurzgesagt 스타일 묘사 상세도 참조.

  **API/Type References**:
  - Task 1의 4-block 형식 사양 내 "concept 특수 규칙" — CONTENT에 render_text 없고 scene elements만 포함

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: concept Golden Reference 4-block 구조 + zero text 규칙
    Tool: Bash (grep, wc)
    Steps:
      1. 4-block 4개 헤더 존재 확인
      2. Golden Reference ≥80줄
      3. FORBIDDEN 영역에 "text" 또는 "render" 관련 금지 항목 존재 확인
      4. CONTENT 영역에 "render_text" 키가 없음 확인
    Expected Result: 4개 헤더, ≥80줄, zero-text FORBIDDEN 존재, render_text 미포함
    Evidence: .sisyphus/evidence/task-5-concept-golden-ref.txt
  ```

  **Commit**: YES (group with Tasks 4, 6-8)
  - Message: `refactor(visual-gen): convert theme-concept Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-concept/SKILL.md`

- [x] 6. Convert theme-whatif Golden Reference to 4-Block

  **What to do**:
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md`의 Golden Reference를 4-block 형식으로 변환
  - Task 2의 theme-gov 패턴 따름
  - whatif 테마 고유 특성: 공상과학 HUD UI, 빛나는 네온, 홀로그래피 효과
  - Scene Description: whatif `<scene>` 내용을 SF UI 장면 묘사 5-7문장으로 변환
  - dfec5c3에서 수정된 whatif 테마 혼동 문제가 재발하지 않도록 Rendering Style에 whatif 전용 시각 요소 명시
  - CONTENT: `key: "value"`, FORBIDDEN: 15+ 항목

  **Must NOT do**:
  - 기존 테마 가이드 섹션 삭제/변경 금지
  - Golden Reference에 XML 태그 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task 2 패턴 반복 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (Tasks 4-8과 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2 완성 4-block Golden Reference 템플릿
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md` — 현재 XML Golden Reference (101줄)
  - `git show dfec5c3:plugins/visual-generator/skills/theme-whatif/SKILL.md` — whatif 테마 혼동 수정 커밋. 이 수정 사항이 4-block 변환 후에도 유지되는지 확인.

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: whatif Golden Reference 4-block 구조 확인
    Tool: Bash (grep, wc)
    Steps:
      1. 4-block 4개 헤더 존재 확인
      2. Golden Reference ≥80줄
      3. Rendering Style에 whatif 테마 전용 키워드 ("HUD", "holograph", "neon" 중 1+) 존재
    Expected Result: 4개 헤더, ≥80줄, whatif 전용 시각 요소 명시됨
    Evidence: .sisyphus/evidence/task-6-whatif-golden-ref.txt
  ```

  **Commit**: YES (group with Tasks 4-5, 7-8)
  - Message: `refactor(visual-gen): convert theme-whatif Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-whatif/SKILL.md`

- [x] 7. Convert theme-pitch Golden Reference to 4-Block

  **What to do**:
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md`의 Golden Reference를 4-block 형식으로 변환
  - Task 2의 theme-gov 패턴 따름
  - pitch 테마 고유 특성: Apple 키노트 스타일, 어두운 그래디언트, 거대한 숫자, 프로스티드 글래스 카드
  - Scene Description: pitch `<scene>` 내용을 5-7문장 자연어 변환
  - CONTENT: `key: "value"`, FORBIDDEN: 15+ 항목

  **Must NOT do**:
  - 기존 테마 가이드 섹션 삭제/변경 금지
  - Golden Reference에 XML 태그 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task 2 패턴 반복 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (Tasks 4-8과 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2 완성 4-block Golden Reference 템플릿
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md` — 현재 XML Golden Reference (102줄)

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: pitch Golden Reference 4-block 구조 확인
    Tool: Bash (grep, wc)
    Steps:
      1. 4-block 4개 헤더 존재 확인
      2. Golden Reference ≥80줄
      3. Rendering Style에 pitch 전용 키워드 ("gradient", "frosted", "glass" 중 1+) 존재
    Expected Result: 4개 헤더, ≥80줄, pitch 전용 시각 요소 명시됨
    Evidence: .sisyphus/evidence/task-7-pitch-golden-ref.txt
  ```

  **Commit**: YES (group with Tasks 4-6, 8)
  - Message: `refactor(visual-gen): convert theme-pitch Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-pitch/SKILL.md`

- [x] 8. Convert theme-comparison Golden Reference to 4-Block

  **What to do**:
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md`의 Golden Reference를 4-block 형식으로 변환
  - Task 2의 theme-gov 패턴 따름
  - comparison 테마 고유 특성: IMAX 분할 화면, 좌우 풀블리드 이미지, Before/After 핵심 수치
  - Scene Description: comparison `<scene>` 내용을 좌우 대비 장면 5-7문장으로 변환
  - CONTENT: `key: "value"`, FORBIDDEN: 15+ 항목

  **Must NOT do**:
  - 기존 테마 가이드 섹션 삭제/변경 금지
  - Golden Reference에 XML 태그 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task 2 패턴 반복 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (Tasks 4-8과 병렬)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2 완성 4-block Golden Reference 템플릿
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md` — 현재 XML Golden Reference (130줄)

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: comparison Golden Reference 4-block 구조 확인
    Tool: Bash (grep, wc)
    Steps:
      1. 4-block 4개 헤더 존재 확인
      2. Golden Reference ≥80줄
      3. Rendering Style에 comparison 전용 키워드 ("split", "before", "after" 중 1+) 존재
    Expected Result: 4개 헤더, ≥80줄, comparison 전용 시각 요소 명시됨
    Evidence: .sisyphus/evidence/task-8-comparison-golden-ref.txt
  ```

  **Commit**: YES (group with Tasks 4-7)
  - Message: `refactor(visual-gen): convert theme-comparison Golden Reference to 4-block`
  - Files: `plugins/visual-generator/skills/theme-comparison/SKILL.md`

- [x] 9. Adapt prompt-validator to 4-Block Format (7 Dimensions)

  **What to do**:
  - `plugins/visual-generator/agents/prompt-validator.md` 전체를 4-block 형식에 맞게 재조정
  - **description 변경**: "XML-tag 프롬프트" → "4-block 마크다운 프롬프트"
  - **Overview 변경**: "XML-tag 프롬프트의 콘텐츠 품질을 검증" → "4-block 마크다운 프롬프트의 콘텐츠 품질을 검증"
  - **7개 차원 유지, 검증 대상만 변경** (차원 추가/삭제 금지):
    1. **Scene Richness**: `<scene>` → `### Scene Description` 서브섹션 기준. 최소 5문장/concept 7문장, 7요소 중 5+ 그대로 유지.
    2. **Content Completeness**: `<text_to_render>` → `## CONTENT` 블록의 `key: "value"` 쌍 기준. 플레이스홀더/메타라벨/빈값 검출 규칙 동일.
    3. **Cross-Tag Consistency**: `<text_to_render>` ↔ `<layout>` → `## CONTENT` value ↔ `### Content Placement` 인용 검증. orphan/ghost 로직 동일.
    4. **Logical Completeness**: `<scene>`/`<canvas>`/`<typography>` → `### Scene Description`/`### Canvas Settings`/`### Typography` 기준.
    5. **Font Name Leakage**: `<typography>` → `### Typography` 서브섹션 기준. 금지 패턴 4종 동일.
    6. **Text Density**: `<text_to_render>` 항목 수 → `## CONTENT` key:value 쌍 수. body≥8/title≥3 기준 동일.
    7. **Palette Consistency**: `<canvas>` → `### Color Palette` 서브섹션 기준. style_sheet.md 대조 동일.
  - **MUST NOT DO 섹션**: "XML 구조 검증을 구현하지 않는다" → "4-block 마크다운 헤더 구조 검증을 구현하지 않는다 (renderer-agent 책임)"
  - **Golden Reference 패스 테스트**: Task 2에서 완성한 theme-gov 4-block Golden Reference를 이 validator로 검증 시 7차원 모두 PASS 해야 함

  **Must NOT do**:
  - 7개 검증 차원의 추가/삭제 금지 (이름과 목적 보존)
  - 자동 수정 정책 변경 금지 (REJECT-only 유지)
  - 참조 문서 로드 경로 변경 금지 (Step 1-3 폴백 유지)
  - 검증 임계값 변경 금지 (body≥8, title≥3 등)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 7개 검증 차원의 XML→4-block 매핑을 정확하게 해야 함. 논리적 일관성이 중요.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Tasks 4-8과 병렬)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10, 11, 14
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-validator.md` (현재 HEAD, 142줄) — 7개 차원 정의, Workflow, REJECT-only policy, MUST DO/NOT DO. 이 파일의 구조를 유지하되, 모든 XML 태그 참조를 4-block 섹션 참조로 치환.
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — Task 2 완성 4-block Golden Reference. validator 재조정 후 이 Golden Reference가 7차원 PASS하는지 검증.

  **API/Type References**:
  - Task 1의 4-block 형식 사양 — 어떤 서브섹션이 어떤 검증 차원에 매핑되는지 기준

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 7개 검증 차원이 4-block 참조로 업데이트됨
    Tool: Bash (grep)
    Preconditions: prompt-validator.md 저장됨
    Steps:
      1. grep -c "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/agents/prompt-validator.md
      2. grep -c "Scene Description\|## CONTENT\|Content Placement\|Canvas Settings\|### Typography\|Color Palette" plugins/visual-generator/agents/prompt-validator.md
      3. grep -c "REJECT-only\|자동 수정 금지" plugins/visual-generator/agents/prompt-validator.md
    Expected Result: Step 1 = 0 (XML 태그 참조 제거), Step 2 ≥ 6 (4-block 참조), Step 3 ≥ 1 (REJECT-only 정책 유지)
    Failure Indicators: XML 태그 참조 잔존, 4-block 참조 부족
    Evidence: .sisyphus/evidence/task-9-validator-4block.txt

  Scenario: theme-gov Golden Reference가 validator 7차원 PASS (수동 추적)
    Tool: Bash (grep)
    Steps:
      1. prompt-validator.md의 각 차원별 REJECT 기준을 theme-gov Golden Reference에 대입하여 위반 여부 확인
      2. Scene Description ≥5문장, 7요소 중 5+ 확인
      3. CONTENT key:value 비어있지 않음 확인
      4. Content Placement에서 CONTENT value 인용 확인
      5. Typography에 폰트 패밀리명 없음 확인
    Expected Result: 모든 차원 PASS
    Evidence: .sisyphus/evidence/task-9-gov-validation-pass.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): adapt prompt-validator to 4-block format`
  - Files: `plugins/visual-generator/agents/prompt-validator.md`

- [x] 10. Full prompt-designer Rewrite (ae35fe6 Base + v2.x Features)

  **What to do**:
  - `plugins/visual-generator/agents/prompt-designer.md`를 **전면 재작성** (현재 214줄 → ae35fe6 기반 확장)
  - **기반**: ae35fe6의 prompt-designer (767줄)에서 가져올 것:
    - 테마별 4-block 생성 규칙 (gov/seminar/concept/whatif/pitch/comparison 별도 지침)
    - Text Density Rules (ae35fe6의 Global Text Rules)
    - Content Placement 상세 생성 지시 (각 텍스트별 위치/크기/방식)
    - Rendering Style 7요소별 생성 가이드
    - FORBIDDEN Elements 15+ 항목 생성 규칙
    - 이미지 플레이스홀더 방지 규칙
  - **v2.x에서 이식할 것**:
    - Phase 2.5 Style Sheet 관리 — **실제 동작 보장 필수**:
      - style_sheet_mode="create": 첫 슬라이드 생성 후 반드시 `{output_path}/style_sheet.md` 파일을 Write로 저장
      - style_sheet_mode="follow": 반드시 style_sheet.md를 Read로 읽고 팔레트/스타일 일치시킴
      - style_sheet.md 내용: palette (primary/secondary/accent/bg), surface_style, lighting_direction, icon_style, corner_radius
      - **기존 v2.2.0에서 style_sheet.md가 실제로 생성되지 않는 버그 확인됨** — 이 재작성에서 반드시 해결
    - Scene Description 생성 규칙 (5-7문장, 7요소 중 5+, negative prompting)
    - render_text/scene_context 분류 인식 (content-organizer 출력 활용)
    - 최소 텍스트 밀도 (body≥8, title≥3)
    - Golden Reference 참조 지시 (테마 스킬 로드)
    - 폰트명 유출 방지 규칙
  - **Task 1의 형식 사양**을 이 재작성의 기반 아키텍처로 사용
  - **Workflow 구조** (ae35fe6 기반 + v2.x 확장):
    1. Phase 1: 입력 로드 (content-organizer 출력 + 테마 스킬)
    2. Phase 2: Golden Reference 학습 (테마 스킬에서 4-block 예시 로드)
    3. Phase 2.5: Style Sheet 관리 (첫 슬라이드 create, 이후 follow)
    4. Phase 3: 4-block 프롬프트 생성 (슬라이드별)
    5. Phase 4: 자체 품질 점검 (줄 수, key:value 형식, FORBIDDEN 항목 수)
  - **description 변경**: "XML-tag 5개 기반" → "4-block 마크다운 프롬프트 생성 에이전트"
  - **목표 줄 수**: 400-600줄 (ae35fe6 767줄의 핵심을 압축하되 v2.x 기능 추가)

  **Must NOT do**:
  - XML 태그를 프롬프트 출력 형식으로 사용 금지
  - content-organizer 출력 스키마 가정 변경 금지 (render_text/scene_context 유지)
  - Task 1의 형식 사양 구조 변경 금지
  - layout-types SKILL.md 참조 방식 변경 금지
  - 프롬프트에 pt/px 단위 포함 금지
  - 프롬프트에 구체적 폰트 패밀리명 포함 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 가장 핵심적이고 큰 작업. ae35fe6 (767줄)과 현재 HEAD (214줄)를 모두 읽고, Task 1 사양과 Task 2 Golden Reference를 참조하여 통합 재작성.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `slide-renderer`: 직접 Read로 참조 문서 접근 가능

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 11, 14
  - **Blocked By**: Tasks 1, 2, 9

  **References**:

  **Pattern References**:
  - `git show ae35fe6:plugins/visual-generator/agents/prompt-designer.md` — ae35fe6의 prompt-designer (767줄). 테마별 4-block 생성 규칙, Text Density Rules, Content Placement 지시, Rendering Style 가이드, FORBIDDEN 생성 규칙, concept 특수 규칙. 이 파일이 재작성의 **주 기반**.
  - `plugins/visual-generator/agents/prompt-designer.md` (현재 HEAD, 214줄) — v2.x Phase 2.5 Style Sheet, Scene Description 규칙, 최소 텍스트 밀도, 폰트명 방지. 이 기능들을 ae35fe6 기반에 이식.

  **API/Type References**:
  - Task 1 결과물 (prompt-designer.md 내 형식 사양 섹션) — 4-block 구조 정의, 서브섹션 목록
  - Task 2 결과물 (theme-gov 4-block Golden Reference) — 생성 목표 상세도 기준

  **External References**:
  - `assets/theme-examples/prompts/02_theme_gov.md` — ae35fe6 gov 프롬프트 (106줄). 최종 생성물 품질 기준선.
  - `assets/theme-examples/prompts/01_theme_concept.md` — ae35fe6 concept 프롬프트 (98줄). concept 특수 규칙 적용 기준.
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — Scene Description 품질 기준

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: prompt-designer.md가 4-block 생성 엔진으로 완성됨
    Tool: Bash (grep, wc)
    Steps:
      1. wc -l plugins/visual-generator/agents/prompt-designer.md
      2. grep -c "Style Sheet\|style_sheet" plugins/visual-generator/agents/prompt-designer.md
      3. grep -c "Scene Description" plugins/visual-generator/agents/prompt-designer.md
      4. grep -c "Rendering Style" plugins/visual-generator/agents/prompt-designer.md
      5. grep -c "Content Placement" plugins/visual-generator/agents/prompt-designer.md
      6. grep -c "FORBIDDEN" plugins/visual-generator/agents/prompt-designer.md
      7. grep -c "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: Step 1 ≥ 400줄, Steps 2-6 각각 ≥ 1, Step 7 = 0
    Failure Indicators: 줄 수 부족 (< 400), Style Sheet 누락, Scene Description 누락, XML 태그 잔존
    Evidence: .sisyphus/evidence/task-10-prompt-designer-rewrite.txt

  Scenario: concept 특수 규칙 포함
    Tool: Bash (grep)
    Steps:
      1. grep -i "concept.*zero.*text\|concept.*no.*text\|concept.*텍스트.*금지" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: ≥ 1 match (concept zero-text 규칙 존재)
    Evidence: .sisyphus/evidence/task-10-concept-rule.txt

  Scenario: 6개 테마별 규칙 존재
    Tool: Bash (grep)
    Steps:
      1. grep -c "gov\|seminar\|concept\|whatif\|pitch\|comparison" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: ≥ 12 (각 테마 최소 2회 언급)
    Evidence: .sisyphus/evidence/task-10-theme-rules.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): rewrite prompt-designer for 4-block generation`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`

- [x] 11. Adapt renderer-agent to 4-Block Validation

  **What to do**:
  - `plugins/visual-generator/agents/renderer-agent.md`의 XML Validation Checklist를 4-block 검증으로 전환
  - **description 변경**: "최종 XML 프롬프트 검증" → "최종 4-block 프롬프트 검증 및 이미지 렌더링"
  - **Overview 변경**: "XML-tag 프롬프트를 검증" → "4-block 마크다운 프롬프트를 검증"
  - **Validation Checklist 8개 항목 변환**:
    1. `<scene>` 등 5개 태그 존재 → `## INSTRUCTION`, `## CONFIGURATION`, `## CONTENT`, `## FORBIDDEN ELEMENTS` 4개 블록 존재
    2. `<text_to_render>` key:value → `## CONTENT` key: "value" 형식 검증
    3. `<layout>`에서 value 인용 → `### Content Placement`에서 CONTENT value 인용
    4. 번호 목록 패턴 부재 → CONTENT 영역 내 번호 목록 부재
    5. `pt`/`px` 단위 부재 → 동일 유지
    6. 마크다운 포맷 부재 → CONTENT 값 내 마크다운 부재
    7. 테마별 항목 상한 → CONTENT key:value 쌍 수 기준 (Theme Limits 테이블 유지)
    8. `<typography>` 한글 힌트 → `### Typography` 한글 힌트 확인
  - **추가 유지 검증 변환**:
    - Check 12: `<scene>` 최소 문장 수 → `### Scene Description` 최소 문장 수
    - Check 13: `<text_to_render>` ↔ `<layout>` → `## CONTENT` ↔ `### Content Placement`
    - Check 14: `<text_to_render>` 빈 값 → `## CONTENT` 빈 값
  - **Workflow**: Phase 2의 "파일별 XML 검증" → "파일별 4-block 검증"
  - **MUST DO/NOT DO 변환**: "XML 태그 검증" → "4-block 구조 검증"
  - Theme Limits 테이블, Script Path Rule, 렌더링 워크플로우 유지

  **Must NOT do**:
  - Theme Limits 테이블 값 변경 금지
  - Script Path Rule 변경 금지
  - generate_slide_images.py 관련 렌더링 워크플로우 변경 금지
  - 환각 URL/플레이스홀더/언어 혼입 검출 삭제 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 14개 검증 항목의 XML→4-block 매핑. prompt-validator보다 단순하지만 정확성 필요.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Task 10 이후)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 9, 10

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/renderer-agent.md` (현재 HEAD, 101줄) — 8개 기본 검증 + 추가 3개 검증 + Theme Limits + Workflow + Script Path Rule. 구조 유지하면서 XML 참조만 4-block으로 변환.
  - `plugins/visual-generator/agents/prompt-validator.md` (Task 9 결과물) — prompt-validator의 4-block 매핑을 참조하여 일관성 유지.

  **API/Type References**:
  - Task 1의 4-block 형식 사양 — 각 블록/서브섹션 이름과 구조

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: renderer-agent 검증 항목이 4-block 기준으로 변환됨
    Tool: Bash (grep)
    Steps:
      1. grep -c "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/agents/renderer-agent.md
      2. grep -c "INSTRUCTION\|CONFIGURATION\|CONTENT\|FORBIDDEN ELEMENTS" plugins/visual-generator/agents/renderer-agent.md
      3. grep -c "Content Placement\|Scene Description\|Canvas Settings\|Typography" plugins/visual-generator/agents/renderer-agent.md
    Expected Result: Step 1 = 0, Step 2 ≥ 4, Step 3 ≥ 3
    Evidence: .sisyphus/evidence/task-11-renderer-4block.txt

  Scenario: Theme Limits 테이블 보존
    Tool: Bash (grep)
    Steps:
      1. grep -c "concept.*0\|gov.*25\|seminar.*25\|whatif.*20\|pitch.*18\|comparison.*12" plugins/visual-generator/agents/renderer-agent.md
    Expected Result: ≥ 4 (대부분의 테마 리밋 값 유지)
    Evidence: .sisyphus/evidence/task-11-theme-limits.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): adapt renderer-agent to 4-block validation`
  - Files: `plugins/visual-generator/agents/renderer-agent.md`

- [x] 12. Update Orchestrator + Supporting Agents

  **What to do**:
  - **`plugins/visual-generator/commands/visual-generate.md`** (77줄):
    - Overview: "XML-tag 프롬프트를 생성" → "4-block 마크다운 프롬프트를 생성"
    - Phase 3: "XML-tag 형식 생성을 명시" → "4-block 형식 생성을 명시"
    - Phase 4: "XML-tag 검증 수행 지시" → "4-block 검증 수행 지시"
    - MUST DO: "XML-tag 형식 생성을 명시" → "4-block 형식 생성을 명시", "XML-tag 검증 수행을 명시" → "4-block 검증 수행을 명시"
    - style_sheet_mode, Phase 3.5 validator 재실행, Phase 구조 자체는 변경 없음
  - **`plugins/visual-generator/agents/content-organizer.md`** (151줄):
    - 파이프라인 설명 내 XML-tag 참조만 4-block 참조로 변경 (있을 경우)
    - render_text/scene_context 분류 로직 유지 (분류 스키마 변경 금지)
    - description이 XML 참조를 포함하면 4-block으로 변경
    - **[신규] 세션 전체 고정 팔레트 규칙 추가** (MUST DO 섹션):
      - `theme_recommendation.md`에 "슬라이드별 무드 팔레트 배정" 대신 **세션 전체 "고정 팔레트" 1개만 출력**
      - 형식: comparison 테마의 `theme_recommendation.md`처럼 `## 고정 팔레트` 섹션에 primary/secondary/accent/bg 4색 지정
      - 슬라이드별 "무드"는 유지 가능하되, **팔레트 색상 코드는 세션 내 동일**해야 함
      - 근거: gov 테마에서 slide01=#1E3A5F, slide02=#2C3E50, slide03=#2E5090으로 각기 다른 팔레트가 배정되어 슬라이드 간 통일감이 없었음
  - **`plugins/visual-generator/agents/content-reviewer.md`** (103줄):
    - 파이프라인 설명 내 XML-tag 참조만 4-block 참조로 변경 (있을 경우)
    - 리뷰 기준 유지

  **Must NOT do**:
  - content-organizer render_text/scene_context 분류 스키마 변경 금지 (팔레트 고정 규칙 추가는 허용)
  - Phase 구조/순서 변경 금지
  - style_sheet_mode 로직 변경 금지
  - content-reviewer 리뷰 기준 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 3개 파일의 XML 참조를 4-block으로 치환하는 작업. 범위가 명확하지만 3개 파일 동시 수정.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Task 11과 병렬 가능)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Task 10

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md` (77줄) — Phase 구조, style_sheet_mode 로직, MUST DO/NOT DO. XML 참조만 치환.
  - `plugins/visual-generator/agents/content-organizer.md` (151줄) — render_text/scene_context 분류, 파이프라인 설명
  - `plugins/visual-generator/agents/content-reviewer.md` (103줄) — 리뷰 기준, 파이프라인 설명

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 3개 파일에서 XML 참조 제거
    Tool: Bash (grep)
    Steps:
      1. grep -c "XML-tag\|XML tag\|XML 태그" plugins/visual-generator/commands/visual-generate.md plugins/visual-generator/agents/content-organizer.md plugins/visual-generator/agents/content-reviewer.md
    Expected Result: 0 total (XML 참조 제거됨)
    Evidence: .sisyphus/evidence/task-12-no-xml-refs.txt

  Scenario: 4-block 참조 존재
    Tool: Bash (grep)
    Steps:
      1. grep -c "4-block\|4블록\|INSTRUCTION.*CONFIGURATION.*CONTENT.*FORBIDDEN" plugins/visual-generator/commands/visual-generate.md
    Expected Result: ≥ 1 (4-block 참조 존재)
    Evidence: .sisyphus/evidence/task-12-4block-refs.txt

  Scenario: content-organizer 분류 스키마 보존 + 고정 팔레트 규칙 추가
    Tool: Bash (grep)
    Steps:
      1. grep -c "render_text\|scene_context" plugins/visual-generator/agents/content-organizer.md
      2. grep -ic "고정 팔레트\|fixed palette\|세션.*팔레트\|session.*palette" plugins/visual-generator/agents/content-organizer.md
    Expected Result: Step 1 ≥ 2 (render_text/scene_context 분류 유지), Step 2 ≥ 1 (고정 팔레트 규칙 존재)
    Evidence: .sisyphus/evidence/task-12-schema-and-palette.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): update orchestrator and supporting agents for 4-block`
  - Files: `plugins/visual-generator/commands/visual-generate.md`, `plugins/visual-generator/agents/content-organizer.md`, `plugins/visual-generator/agents/content-reviewer.md`

- [x] 13. Update Reference Docs (Tag Name Replacement Only)

  **What to do**:
  - **3개 참조 문서의 XML 태그명만 4-block 섹션명으로 치환** (내용 재작성 금지):
  - **`plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`**:
    - `<scene>` → `### Scene Description` (또는 "Scene Description 서브섹션")
    - 품질 기준(EXCELLENT/GOOD/POOR 등급, 7요소 목록, 문장 수) 내용 유지
  - **`plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md`**:
    - XML 태그 참조를 4-block 섹션 참조로 치환
    - 검증 규칙 내용 유지
  - **`plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md`**:
    - `<typography>` → `### Typography` 서브섹션 참조
    - 한글 렌더링 가이드라인 내용 유지
  - **치환 방법**: 단순 문자열 치환 (sed/replace). 문장 재구성 금지.

  **Must NOT do**:
  - 참조 문서 내용 재작성 금지 (guardrail)
  - 품질 기준/검증 규칙/가이드라인 값 변경 금지
  - 새로운 섹션 추가 금지
  - 파일 삭제 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 3개 파일의 단순 문자열 치환. 내용 변경 없음.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Tasks 10-12와 병렬)
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 14, 15
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — Scene 품질 기준. `<scene>` → Scene Description 치환 대상.
  - `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — 검증 규칙 맵. XML 태그 참조 치환 대상.
  - `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` — 한글 타이포그래피 가이드. `<typography>` 참조 치환 대상.

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 3개 참조 문서에서 XML 태그 제거
    Tool: Bash (grep)
    Steps:
      1. grep -rn "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/skills/slide-renderer/references/
    Expected Result: 0 matches
    Evidence: .sisyphus/evidence/task-13-no-xml-in-refs.txt

  Scenario: 4-block 참조로 대체됨
    Tool: Bash (grep)
    Steps:
      1. grep -c "Scene Description\|Content\|Typography\|Content Placement" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. grep -c "Scene Description\|Content\|Typography\|Content Placement" plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md
    Expected Result: Step 1 ≥ 1, Step 2 ≥ 1
    Evidence: .sisyphus/evidence/task-13-4block-refs-in-docs.txt

  Scenario: 내용 무결성 (줄 수 유사)
    Tool: Bash (wc)
    Steps:
      1. wc -l plugins/visual-generator/skills/slide-renderer/references/*.md
    Expected Result: 줄 수가 원본 대비 ±5줄 이내 (태그명 치환이므로 줄 수 거의 동일)
    Evidence: .sisyphus/evidence/task-13-line-count-integrity.txt
  ```

  **Commit**: YES
  - Message: `refactor(visual-gen): update reference docs tag names for 4-block`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`, `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md`, `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md`

- [ ] 14. End-to-End Integration Test with Gemini Rendering

  **What to do**:
  - **목적**: 전체 파이프라인(content-organizer → content-reviewer → prompt-designer → prompt-validator → renderer-agent)이 4-block 형식으로 정상 동작하는지 검증
  - **테스트 시나리오 1 (gov 테마)**:
    1. 테스트 입력 문서 준비 (간단한 3-4슬라이드 주제)
    2. visual-generate 오케스트레이터 실행
    3. 생성된 프롬프트 검증: 4-block 구조, ≥80줄(body), ≥50줄(title)
    4. prompt-validator 7차원 PASS 확인
    5. Gemini 렌더링 실행 (generate_slide_images.py)
    6. 품질 점수 ≥ 7.0 확인
    7. Color # 코드 이미지 미렌더링 확인 (육안 + 로그)
    8. style_sheet.md 제외 확인 (렌더링 시도 안 함)
  - **테스트 시나리오 2 (concept 테마)**:
    1. 동일 입력으로 concept 테마 실행
    2. CONTENT에 render_text 없음 확인
    3. FORBIDDEN에 "all text" 금지 존재 확인
    4. Gemini 렌더링 후 텍스트 미렌더링 확인
  - **테스트 시나리오 3 (슬라이드 간 팔레트 일관성 — 핵심 검증)**:
    1. gov 테마 3+ 슬라이드 생성
    2. theme_recommendation.md에 "고정 팔레트" 섹션 존재 확인 (슬라이드별 다른 팔레트 아님)
    3. style_sheet.md 생성 확인 (v2.2.0에서 미생성 버그 → v3.0.0에서 반드시 생성)
    4. 모든 슬라이드 프롬프트의 Color Palette 색상 코드 추출 → 전부 동일한지 확인
    5. 2번째+ 슬라이드 Color Palette가 style_sheet.md와 일치 확인
  - **증거 수집**: 프롬프트 파일, 렌더링 이미지, 품질 점수, 로그를 `.sisyphus/evidence/` 에 저장

  **Must NOT do**:
  - 테스트를 위한 코드 수정 금지 (이 Task는 검증만)
  - 실패 시 자동 수정 금지 (실패 보고 후 관련 Task 재실행)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 전체 파이프라인 end-to-end 실행 + 품질 검증 + 다중 시나리오. Gemini API 호출 포함.
  - **Skills**: [`slide-renderer`]
    - `slide-renderer`: generate_slide_images.py 실행 경로, SYSTEM_INSTRUCTION 이해

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 3-13 (모든 구현 태스크)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md` — 오케스트레이터 워크플로우 (파이프라인 실행 순서)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` — 렌더링 스크립트 (SYSTEM_INSTRUCTION, 품질 임계값, 재시도)

  **External References**:
  - `assets/theme-examples/prompts/02_theme_gov.md` — 기대 프롬프트 상세도 기준 (106줄)
  - `assets/theme-examples/prompts/01_theme_concept.md` — concept 프롬프트 기준 (98줄)

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: gov 테마 end-to-end 파이프라인
    Tool: Task tool (subagent_type invocation) + Bash (grep, wc)
    Preconditions: Tasks 1-13 완료, GEMINI_API_KEY 환경변수 설정됨
    Steps:
      1. 테스트 입력 문서 작성: Write ".sisyphus/evidence/task-14-test-input.md" with 간단한 스마트 팩토리 소개 문서 (3 문단, 핵심 수치 포함)
      2. Task tool로 오케스트레이터 호출:
         Task(subagent_type="visual-generator:visual-generate",
              prompt="input_document=.sisyphus/evidence/task-14-test-input.md theme=gov output_folder=.sisyphus/evidence/task-14-gov-output auto_mode=true")
      3. 생성된 프롬프트 줄 수 확인 (파일명 패턴: NN_*.md, 예: 01_gov_overview.md):
         Bash: wc -l .sisyphus/evidence/task-14-gov-output/prompts/0[2-9]_*.md → body 슬라이드 각 ≥80줄
         Bash: wc -l .sisyphus/evidence/task-14-gov-output/prompts/01_*.md → title 슬라이드 ≥50줄
         (참고: 오케스트레이터 출력 패턴은 01_*.md, 02_*.md, ... + prompt_index.md, style_sheet.md)
      4. 4-block 헤더 확인:
         Bash: grep -c "^## INSTRUCTION$\|^## CONFIGURATION$\|^## CONTENT$\|^## FORBIDDEN ELEMENTS$" .sisyphus/evidence/task-14-gov-output/prompts/*.md → 각 파일 4개
      5. 렌더링 스크립트 실행 (절대경로 사용):
         Bash: python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --prompts-dir .sisyphus/evidence/task-14-gov-output/prompts --output-dir .sisyphus/evidence/task-14-gov-output/images
      6. 품질 점수 확인: 스크립트 stdout/stderr 파싱하여 quality ≥ 7.0
    Expected Result: body ≥80줄, 4-block 헤더 4개, 품질 ≥7.0, 이미지 파일 생성됨
    Failure Indicators: 줄 수 부족, 헤더 누락, 품질 <7.0, 렌더링 에러, 오케스트레이터 실패
    Evidence: .sisyphus/evidence/task-14-gov-e2e.txt (grep/wc 출력), .sisyphus/evidence/task-14-gov-output/ (프롬프트+이미지)

  Scenario: concept 테마 zero-text 검증
    Tool: Task tool (subagent_type invocation) + Bash (grep)
    Steps:
      1. Task tool로 오케스트레이터 호출:
         Task(subagent_type="visual-generator:visual-generate",
              prompt="input_document=.sisyphus/evidence/task-14-test-input.md theme=concept output_folder=.sisyphus/evidence/task-14-concept-output auto_mode=true")
      2. Bash: grep "render_text" .sisyphus/evidence/task-14-concept-output/prompts/*.md → 0 matches
      3. Bash: grep -i "text\|font\|render" .sisyphus/evidence/task-14-concept-output/prompts/*.md → FORBIDDEN 섹션 내 ≥1 match
      4. 렌더링:
         Bash: python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --prompts-dir .sisyphus/evidence/task-14-concept-output/prompts --output-dir .sisyphus/evidence/task-14-concept-output/images
    Expected Result: render_text 없음, FORBIDDEN에 text 금지 존재, 이미지 생성됨
    Evidence: .sisyphus/evidence/task-14-concept-e2e.txt, .sisyphus/evidence/task-14-concept-output/

  Scenario: 슬라이드 간 팔레트 일관성 (핵심 — v2.2.0 실패 사례 재발 방지)
    Tool: Bash (grep, diff)
    Preconditions: gov 테마 3+ 슬라이드 생성 완료
    Steps:
      1. grep -i "고정 팔레트\|fixed" .sisyphus/evidence/task-14-gov-output/analysis/theme_recommendation.md → "고정 팔레트" 섹션 존재
      2. ls .sisyphus/evidence/task-14-gov-output/prompts/style_sheet.md → 파일 존재 확인 (v2.2.0에서 미생성 → v3.0.0에서 반드시 생성)
      3. 모든 슬라이드 프롬프트에서 "### Color Palette" (또는 4-block의 팔레트 라인) 추출
      4. 추출된 팔레트 간 diff → 전부 동일해야 함
      5. style_sheet.md의 팔레트와 각 슬라이드 팔레트 diff → 일치
    Expected Result: theme_recommendation.md에 고정 팔레트 존재, style_sheet.md 생성됨, 모든 슬라이드 팔레트 동일, style_sheet와 일치
    Failure Indicators: theme_recommendation.md에 슬라이드별 다른 팔레트 배정, style_sheet.md 미생성, 슬라이드 간 색상 불일치
    Evidence: .sisyphus/evidence/task-14-palette-consistency.txt
  ```

  **Commit**: YES
  - Message: `test(visual-gen): end-to-end integration test with Gemini rendering`
  - Files: `.sisyphus/evidence/task-14-*` (증거 파일만 커밋, output/ 디렉토리는 gitignored이므로 .sisyphus/evidence/ 내에 출력)

- [ ] 15. Version Bump v3.0.0 + AGENTS.md + Registry Updates

  **What to do**:
  - **`plugins/visual-generator/.claude-plugin/plugin.json`**: version "2.2.0" → "3.0.0"
  - **`.claude-plugin/marketplace.json`**: visual-generator 플러그인 항목의 version "2.2.0" → "3.0.0", description 업데이트 (XML-tag → 4-block 반영)
  - **`AGENTS.md`** 업데이트:
    - Version 필드: 현재 날짜로 Generated 업데이트
    - OVERVIEW 내 visual-generator 설명: "XML-tag v2.2.0" → "4-block v3.0.0"
    - WHERE TO LOOK 테이블: visual-generator 관련 설명 업데이트
    - ANTI-PATTERNS: XML 태그 관련 금지 패턴이 있으면 4-block 기준으로 변경
    - 변경 이력/UNIQUE STYLES 등에 v3.0.0 반영
  - **`README.md`**: visual-generator 변경 이력에 v3.0.0 추가 (4-block 복원 + v2.x 장점 통합)
  - **Marketplace.json metadata.version**: 전체 마켓플레이스 MINOR 버전 올림 (기존 플러그인의 MAJOR 변경이므로, 마켓플레이스 자체는 구조 변경 없으니 MINOR)

  **Must NOT do**:
  - 다른 플러그인의 version 변경 금지
  - marketplace.json의 플러그인 추가/삭제 금지
  - AGENTS.md에서 visual-generator 이외 플러그인 정보 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 버전 번호 치환 + 텍스트 업데이트. 단순 반복 작업.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (Task 14 이후)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 14

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — 현재 version 필드
  - `.claude-plugin/marketplace.json` — visual-generator 항목
  - `AGENTS.md` — OVERVIEW, WHERE TO LOOK, CONVENTIONS, UNIQUE STYLES 내 visual-generator 참조
  - `README.md` — visual-generator 변경 이력 섹션

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 버전 v3.0.0 일관성
    Tool: Bash (grep)
    Steps:
      1. grep '"version"' plugins/visual-generator/.claude-plugin/plugin.json
      2. grep -A2 "visual-generator" .claude-plugin/marketplace.json | grep "version"
    Expected Result: 두 파일 모두 "3.0.0"
    Evidence: .sisyphus/evidence/task-15-version-check.txt

  Scenario: AGENTS.md 업데이트
    Tool: Bash (grep)
    Steps:
      1. grep -c "v3.0.0\|3.0.0" AGENTS.md
      2. grep -c "XML-tag v2.2.0" AGENTS.md
    Expected Result: Step 1 ≥ 1, Step 2 = 0 (v2.2.0 XML-tag 참조 제거)
    Evidence: .sisyphus/evidence/task-15-agents-md.txt

  Scenario: README.md 변경 이력 추가
    Tool: Bash (grep)
    Steps:
      1. grep "3.0.0" README.md
    Expected Result: ≥ 1 (v3.0.0 변경 이력 존재)
    Evidence: .sisyphus/evidence/task-15-readme.txt
  ```

  **Commit**: YES
  - Message: `chore(visual-gen): bump to v3.0.0, update AGENTS.md and registry`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, grep pattern). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Review all changed files for: XML tags remaining, inconsistent format references, broken cross-references between agents/skills. Check no AI slop: excessive comments, over-abstraction, generic descriptions. Verify all agent descriptions updated. Verify version numbers consistent.
  Output: `Files [N clean/N issues] | XML Remnants [0/N] | VERDICT`

- [ ] F3. **Real Manual QA with Gemini Rendering** — `unspecified-high` (+ `slide-renderer` skill)
  Generate prompts for at least 2 themes (gov + concept). Render with Gemini API. Verify: body slides ≥80 lines, no color codes in images, no font names in images, concept theme has zero text, slides within same batch have consistent palette/style. Save rendered images and quality scores.
  Output: `Themes [N/N tested] | Quality [avg score] | Consistency [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec. Check guardrails: no layout-types changes, no reference doc content rewrites, no content-organizer schema changes. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Guardrails [N/N intact] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|-----------|
| 1 | `refactor(visual-gen): define 4-block prompt format spec` | prompt-designer.md (format spec section) | grep 4-block headers |
| 2 | `refactor(visual-gen): convert theme-gov Golden Reference to 4-block` | theme-gov/SKILL.md | wc -l ≥80, grep 4 blocks |
| 3 | `fix(visual-gen): fix generate_slide_images.py exclude list and rendering robustness` | generate_slide_images.py | grep exclude list |
| 4-8 | `refactor(visual-gen): convert theme-{name} Golden Reference to 4-block` | theme-{name}/SKILL.md | wc -l check, grep 4 blocks |
| 9 | `refactor(visual-gen): adapt prompt-validator to 4-block format` | prompt-validator.md | Golden Refs pass validation |
| 10 | `refactor(visual-gen): rewrite prompt-designer for 4-block generation` | prompt-designer.md | generates ≥80 line prompts |
| 11 | `refactor(visual-gen): adapt renderer-agent to 4-block validation` | renderer-agent.md | validation checklist updated |
| 12 | `refactor(visual-gen): update orchestrator and supporting agents` | visual-generate.md, content-organizer.md, content-reviewer.md | no XML references |
| 13 | `refactor(visual-gen): update reference docs tag names` | scene-richness-spec.md, validation-rules-map.md, korean-typography-spec.md | no XML tags |
| 14 | `test(visual-gen): end-to-end integration test with Gemini rendering` | output/ evidence files | quality ≥7.0 |
| 15 | `chore(visual-gen): bump to v3.0.0, update AGENTS.md and registry` | plugin.json, marketplace.json, AGENTS.md, README.md | versions consistent |

---

## Success Criteria

### Verification Commands
```bash
# 4-block structure in generated prompts (파일명 패턴: NN_*.md, 예: 01_gov_overview.md)
grep -c "^## INSTRUCTION$\|^## CONFIGURATION$\|^## CONTENT$\|^## FORBIDDEN ELEMENTS$" .sisyphus/evidence/task-14-gov-output/prompts/0[0-9]_*.md
# Expected: 4 per file

# Body slide line count (02_*.md 이후 = body 슬라이드)
wc -l .sisyphus/evidence/task-14-gov-output/prompts/0[2-9]_*.md
# Expected: ≥80 lines each

# Title slide line count (01_*.md = title 슬라이드)
wc -l .sisyphus/evidence/task-14-gov-output/prompts/01_*.md
# Expected: ≥50 lines

# No XML tags in agent/skill/command source files
grep -rn "<scene>\|<text_to_render>\|<typography>\|<canvas>\|<layout>" plugins/visual-generator/agents/*.md plugins/visual-generator/commands/*.md
# Expected: 0 matches

# No XML tags in generated prompt output
grep -rn "<scene>\|<text_to_render>" .sisyphus/evidence/task-14-gov-output/prompts/0[0-9]_*.md
# Expected: 0 matches

# Exclude list includes metadata files
grep "style_sheet\|validation_result" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
# Expected: both present in exclude list

# Style sheet actually generated
ls .sisyphus/evidence/task-14-gov-output/prompts/style_sheet.md
# Expected: file exists

# Version consistency
grep '"version"' plugins/visual-generator/.claude-plugin/plugin.json
# Expected: "3.0.0"
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] 6 Golden References pass prompt-validator 7 dimensions
- [ ] Body prompts ≥80 lines, title prompts ≥50 lines
- [ ] Gemini rendering quality ≥7.0
- [ ] Zero XML tags in agent/skill/command files (except comments)
- [ ] Version v3.0.0 in plugin.json + marketplace.json
- [ ] AGENTS.md reflects v3.0.0 architecture
