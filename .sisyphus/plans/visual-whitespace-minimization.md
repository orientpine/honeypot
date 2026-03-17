# Visual Generator 여백 최소화 (Canvas-Filling & Element-Scaling)

## TL;DR

> **Quick Summary**: visual-generator 플러그인의 6개 테마에서 생성되는 이미지의 불필요한 여백을 최소화한다. Scene Description에 캔버스 꽉 채우기 지시를 추가하고, Rendering Style의 공간구성 차원을 강화하며, 의미적으로 중요한 요소의 상대적 크기를 확대하는 원칙을 적용한다. 새로운 텍스트나 디자인 요소를 추가하지 않고, 기존 요소의 스케일 조정과 시각 밀도 강화만으로 달성한다.
>
> **Deliverables**:
> - prompt-designer.md에 캔버스 채우기 + 요소 스케일링 규칙 추가
> - scene-richness-spec.md에 테마별 조건부 네거티브 스페이스 타겟 테이블 추가
> - 6개 테마 SKILL.md의 공간구성 행 + Golden Reference 업데이트
> - 버전 범프 (v3.2.0 → v3.3.0) + 프로젝트 문서 업데이트
>
> **Estimated Effort**: Short (9개 .md 파일 수정)
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: Task 1 → Task 3/4/5 → Task 6 → F1-F3

---

## Context

### Original Request
visual-generator 플러그인에서 생성되는 이미지의 여백을 개선한다. 텍스트나 디자인적 요소를 더 추가하지 않더라도, 여백을 최소화하는 이미지를 생성하도록 한다. 의미적으로 중요한 요소의 크기를 상대적으로 크게 그린다. 현재 구성에서 다른 요소의 변경 없이 여백을 개선한다.

### Interview Summary
**Key Discussions**:
- Scene Description에 캔버스 꽉 채우기 지시 추가
- Rendering Style 강화 (공간구성 차원 집중)
- 기존 요소의 스케일 확대로 달성, 새 요소 추가 금지

**Research Findings**:
- 현재 whitespace 처리는 테마별로 상이: gov(20%), pitch(30%+ 의도적), seminar(breathing room), concept/whatif(full-bleed), comparison(95% fill)
- scene-richness-spec §6이 "30-40% negative space" 단일 타겟을 권장 → 테마별 조건부로 변경 필요
- prompt-designer가 Golden Reference를 먼저 학습 → rules를 두번째로 참조 → Golden Reference 업데이트가 핵심
- scene-richness-spec은 prompt-validator가 참조 (prompt-designer가 아님) → 양쪽 모두 수정 필요

### Metis Review
**Identified Gaps** (addressed):
- 3가지 여백 레이어 구분 (canvas/panel/inter-element) → canvas-level에 집중
- theme-conditional 네거티브 스페이스 타겟 필요 → 테마 그룹별 차등 적용
- Golden Reference 미업데이트 시 규칙 실효성 부족 → Golden Reference 동시 업데이트
- pitch 30%+ 어두운 여백은 design DNA → 명시적 carve-out
- comparison 이미 95% fill → 최소 변경
- title 슬라이드는 자연적으로 여백이 많음 → 소프트 가이던스

---

## Work Objectives

### Core Objective
6개 테마의 Scene Description과 Rendering Style 공간구성 차원을 강화하여, Gemini API가 생성하는 이미지에서 불필요한 여백을 최소화하고 의미적으로 중요한 요소를 더 크게 렌더링하도록 한다.

### Concrete Deliverables
- `prompt-designer.md` Scene Description Rules 섹션에 캔버스 채우기 필수 문구 추가
- `prompt-designer.md` Rendering Style Rules 섹션에 요소 스케일링 원칙 추가
- `scene-richness-spec.md` §6에 테마별 조건부 네거티브 스페이스 타겟 테이블 교체
- 6개 테마 SKILL.md의 Rendering Style 테이블 공간구성 행 강화
- 6개 테마 Golden Reference의 Scene Description + Rendering Style 공간구성 라인 업데이트
- plugin.json, marketplace.json 버전 v3.3.0 범프
- AGENTS.md, README.md 변경 이력 업데이트

### Definition of Done
- [ ] 모든 수정 파일에서 캔버스 채우기/요소 스케일링 관련 지시어가 grep으로 검출됨
- [ ] pitch 테마에 "30% 이상 의도적 어두운 여백" 문구 유지 확인
- [ ] concept 테마에 "5% 이상 안쪽" 세이프 존 문구 유지 확인
- [ ] 공간구성 이외의 Rendering Style 차원(서피스, 배경, 코너/경계, 연결선, 시각장식, 시각메타포)이 변경되지 않음

### Must Have
- 모든 6개 테마의 공간구성 행에 캔버스 채우기 언어 포함
- prompt-designer.md에 Scene Description 캔버스 채우기 필수 규칙 포함
- prompt-designer.md에 Rendering Style 요소 스케일링 규칙 포함
- scene-richness-spec.md에 테마별 조건부 네거티브 스페이스 타겟 테이블
- 각 테마 Golden Reference의 Scene Description과 Rendering Style 공간구성 업데이트

### Must NOT Have (Guardrails)
- ❌ pitch 테마의 "30% 이상 의도적 어두운 여백" 변경 금지 — 이것은 Apple Keynote DNA
- ❌ concept 테마의 "5% 이상 안쪽" 세이프 존 변경 금지 — 요소 완결성 보장
- ❌ CONTENT 최대/최소 항목 수 변경 금지 (gov 25, pitch 18, body ≥8, title ≥3)
- ❌ Typography 차원 변경 금지
- ❌ 공간구성 이외의 Rendering Style 6개 차원 변경 금지
- ❌ FORBIDDEN ELEMENTS 템플릿 변경 금지
- ❌ prompt-validator.md 변경 금지 (8개 차원 유지)
- ❌ layout-types SKILL.md 변경 금지
- ❌ content-organizer.md, content-reviewer.md 변경 금지
- ❌ renderer-agent.md 변경 금지
- ❌ 새로운 텍스트 항목, UI 구성 요소, 기존에 없는 디자인 패턴 추가 금지

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (all changes are .md files, no test framework)
- **Automated tests**: None — this is prompt directive refactoring
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Directive Files (.md)**: Use Bash (grep/diff) — Verify directive presence, guard term preservation, dimension isolation

---

## Execution Strategy

### Theme-Conditional Negative Space Targets (핵심 결정)

| 테마 그룹 | 테마 | 기존 타겟 | 신규 타겟 | 근거 |
|-----------|------|-----------|-----------|------|
| Full-bleed | concept, whatif | ~30-40% | **≤20%** | 배경이 이미 edge-to-edge. 요소 스케일 확대로 채움 |
| Full-bleed | comparison | ~5% (이미 95% fill) | **≤10%** | 이미 거의 최대. 미세 조정만 |
| Structured | gov, seminar | 20-30% | **≤15%** | 격자/에디토리얼에서 그리드 확장, 요소 크기 증가 |
| Intentional-margin | pitch | 30%+ 의도적 | **30%+ 유지** | 어두운 여백이 hero metric 부각 = 디자인 DNA |

### Parallel Execution Waves

```
Wave 1 (Start Immediately — central rules, 2 parallel):
├── Task 1: prompt-designer.md 중앙 규칙 [quick]
└── Task 2: scene-richness-spec.md §6 업데이트 [quick]

Wave 2 (After Wave 1 — theme updates, 3 parallel):
├── Task 3: gov + seminar 테마 (structured 그룹) [quick]
├── Task 4: concept + whatif 테마 (full-bleed 그룹) [quick]
└── Task 5: pitch + comparison 테마 (intentional-margin 그룹) [quick]

Wave 3 (After Wave 2 — docs):
└── Task 6: 버전 범프 + 프로젝트 문서 업데이트 [quick]

Wave FINAL (After ALL tasks — verification, 3 parallel):
├── Task F1: Plan Compliance Audit (oracle)
├── Task F2: Regression Guard Check (unspecified-high)
└── Task F3: Scope Fidelity Check (deep)

Critical Path: Task 1 → Tasks 3,4,5 → Task 6 → F1-F3
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 3 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 3, 4, 5 | 1 |
| 2 | — | 3, 4, 5 | 1 |
| 3 | 1, 2 | 6 | 2 |
| 4 | 1, 2 | 6 | 2 |
| 5 | 1, 2 | 6 | 2 |
| 6 | 3, 4, 5 | F1, F2, F3 | 3 |
| F1 | 6 | — | FINAL |
| F2 | 6 | — | FINAL |
| F3 | 6 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: 2 — T1 → `quick`, T2 → `quick`
- **Wave 2**: 3 — T3 → `quick`, T4 → `quick`, T5 → `quick`
- **Wave 3**: 1 — T6 → `quick`
- **FINAL**: 3 — F1 → `oracle`, F2 → `unspecified-high`, F3 → `deep`

---

## TODOs

- [x] 1. prompt-designer.md 중앙 규칙 강화 (Scene Description + Rendering Style)

  **What to do**:
  - `prompt-designer.md`의 **Scene Description Rules** 섹션(L172-196 부근)에 캔버스 채우기 필수 규칙을 추가한다:
    - "모든 Scene Description에는 캔버스 전체를 시각 요소로 빈틈없이 채우는 구도 지시를 반드시 포함한다" 류의 필수 문구
    - "의미적으로 중요한 요소(핵심 숫자, 제목, 주요 아이콘)는 할당 영역보다 상대적으로 크게 묘사하여 캔버스 내 빈 공간을 최소화한다" 류의 요소 스케일링 원칙
    - "캔버스 채우기는 기존 요소의 스케일 확대와 시각 요소 보강으로 달성한다. 새로운 텍스트 항목이나 기존에 없는 디자인 패턴을 추가하지 않는다" 류의 가드레일 문구
    - pitch 테마의 의도적 어두운 여백은 이 규칙에서 예외임을 명시하는 carve-out
    - title 슬라이드는 body 슬라이드 대비 소프트한 적용 (여백 허용 범위 상향)
  - `prompt-designer.md`의 **Rendering Style Rules** 섹션(L199-213 부근)에 공간구성 차원에 대한 강화 지시를 추가한다:
    - "공간구성 차원에서는 핵심 시각 요소가 캔버스의 최대 면적을 차지하도록 스케일을 설정한다" 류의 원칙
    - "불필요한 여백보다 요소의 크기와 밀도를 우선한다" 류의 우선순위 원칙

  **Must NOT do**:
  - Scene Description의 기존 규칙(5-7문장, 7요소 중 5개, 네거티브 프롬프팅 등) 변경 금지
  - Rendering Style의 다른 6개 차원(서피스, 배경, 코너/경계, 연결선, 시각장식, 시각메타포) 규칙 변경 금지
  - Text Density Rules, CONTENT Block Generation, FORBIDDEN ELEMENTS 등 다른 섹션 변경 금지
  - Korean Text Safety Rules 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 내 2개 섹션에 텍스트 삽입. 기존 구조 유지하며 문구 추가.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 4, 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:172-196` — Scene Description Rules 섹션. 여기에 캔버스 채우기 규칙을 추가. 기존 "non-concept 슬라이드: 5-7문장으로 작성한다" 등의 규칙 뒤에 삽입.
  - `plugins/visual-generator/agents/prompt-designer.md:199-213` — Rendering Style Rules 섹션. "반드시 아래 7개 항목을 각각 별도 줄로 작성한다" 뒤에 공간구성 강화 원칙 삽입.
  - `plugins/visual-generator/agents/prompt-designer.md:320-326` — gov Theme Rules의 Scene Description 추가 규칙 패턴 참조. 이 형식을 따라 공통 규칙을 작성.

  **External References**:
  - 없음 (기존 파일 내부 수정만)

  **WHY Each Reference Matters**:
  - L172-196: Scene Description은 Gemini가 읽는 핵심 구도 청사진. 여기에 캔버스 채우기 지시가 없으면 Gemini가 기본 여백을 유지함.
  - L199-213: Rendering Style의 공간구성은 각 테마별 규칙의 "상위 규칙". 여기서 원칙을 세우면 테마별 규칙이 이를 따라야 함.
  - L320-326: 테마별 추가 규칙 패턴을 참조하여 공통 규칙의 작성 스타일을 일관되게 유지.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 캔버스 채우기 규칙 존재 확인
    Tool: Bash (grep)
    Preconditions: prompt-designer.md 수정 완료
    Steps:
      1. grep -c "캔버스.*채우\|canvas.*fill\|꽉 채\|빈틈없이 채" plugins/visual-generator/agents/prompt-designer.md
      2. Assert count ≥ 1
    Expected Result: 최소 1건 이상의 캔버스 채우기 관련 문구 검출
    Failure Indicators: count가 0이면 캔버스 채우기 규칙이 누락된 것
    Evidence: .sisyphus/evidence/task-1-canvas-fill-grep.txt

  Scenario: 요소 스케일링 원칙 존재 확인
    Tool: Bash (grep)
    Preconditions: prompt-designer.md 수정 완료
    Steps:
      1. grep -c "스케일.*확대\|크기.*확대\|상대적으로 크게\|크게.*묘사\|크게.*렌더링" plugins/visual-generator/agents/prompt-designer.md
      2. Assert count ≥ 1
    Expected Result: 최소 1건 이상의 요소 스케일링 관련 문구 검출
    Failure Indicators: count가 0이면 스케일링 원칙이 누락된 것
    Evidence: .sisyphus/evidence/task-1-scale-grep.txt

  Scenario: pitch 예외 carve-out 존재 확인
    Tool: Bash (grep)
    Preconditions: prompt-designer.md 수정 완료
    Steps:
      1. grep -c "pitch.*예외\|pitch.*적용.*않\|pitch.*의도적.*여백" plugins/visual-generator/agents/prompt-designer.md
      2. Assert count ≥ 1
    Expected Result: pitch 테마 예외 문구가 존재함
    Failure Indicators: pitch carve-out이 없으면 pitch 여백이 의도치 않게 축소될 위험
    Evidence: .sisyphus/evidence/task-1-pitch-carveout-grep.txt

  Scenario: 기존 Scene Description 규칙 보존 확인
    Tool: Bash (grep)
    Preconditions: prompt-designer.md 수정 완료
    Steps:
      1. grep "5-7문장" plugins/visual-generator/agents/prompt-designer.md
      2. grep "최소 5개" plugins/visual-generator/agents/prompt-designer.md
      3. grep "네거티브 프롬프팅" plugins/visual-generator/agents/prompt-designer.md
      4. Assert all 3 greps return matches
    Expected Result: 기존 3개 핵심 규칙이 모두 보존됨
    Failure Indicators: 기존 규칙 중 하나라도 사라지면 regression
    Evidence: .sisyphus/evidence/task-1-existing-rules-preserved.txt
  ```

  **Evidence to Capture:**
  - [ ] task-1-canvas-fill-grep.txt
  - [ ] task-1-scale-grep.txt
  - [ ] task-1-pitch-carveout-grep.txt
  - [ ] task-1-existing-rules-preserved.txt

  **Commit**: YES — C1
  - Message: `refactor(visual-generator): add canvas-filling and element-scaling directives to prompt-designer`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`
  - Pre-commit: `grep "캔버스" plugins/visual-generator/agents/prompt-designer.md`

- [x] 2. scene-richness-spec.md §6 네거티브 스페이스 타겟 업데이트

  **What to do**:
  - `scene-richness-spec.md`의 **Section 6: Negative Space (White Space) Density Guide** (L170-203)를 수정한다:
    - 기존 단일 "30-40% negative space" 권장을 **테마별 조건부 타겟 테이블**로 교체:
      | 테마 그룹 | 테마 | 네거티브 스페이스 타겟 |
      |-----------|------|----------------------|
      | Full-bleed | concept, whatif | ≤20% |
      | Full-bleed (image-dominant) | comparison | ≤10% |
      | Structured | gov, seminar | ≤15% |
      | Intentional-margin | pitch | 30%+ (의도적 어두운 여백 유지) |
    - "Above 50%: Content feels sparse" 규칙은 유지
    - "Below 30%: Content feels cramped" 규칙은 제거하거나 "structured 테마에만 해당" 조건부로 변경
    - 캔버스 채우기 원칙 추가: "의미적으로 중요한 시각 요소(핵심 숫자, 주요 아이콘, 타이틀)의 크기를 확대하여 캔버스를 채운다. 새로운 텍스트나 디자인 요소를 추가하는 방식은 지양한다."
    - Title 슬라이드 예외 조항 추가: "Title/Cover 슬라이드는 body 슬라이드 대비 네거티브 스페이스 허용 범위를 10%p 상향한다"
  - **Section 9: Implementation Checklist** (L350-363)에 캔버스 채우기 항목 추가

  **Must NOT do**:
  - Section 1-5 (Sentence Count, Scene Guide, Forbidden Phrases, Negative Prompting, Composition Principles) 변경 금지
  - Section 7 (Quality Grading), Section 8 (Golden Examples) 변경 금지
  - Section 11 (Space-Filling Prevention) 변경 금지 — 이것은 panel-level 규칙이며 별도 관심사

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일의 1개 섹션 수정. 테이블 교체 + 문구 추가.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 3, 4, 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:170-203` — Section 6 전체. 현재 "30-40% negative space: Optimal for readability" (L176) 부분을 테마별 조건부 테이블로 교체.
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:350-363` — Section 9 Implementation Checklist. 마지막에 캔버스 채우기 체크 항목 추가.

  **WHY Each Reference Matters**:
  - L170-203: prompt-validator Dimension 1이 이 문서를 참조하여 Scene Richness를 평가. 타겟이 변경되면 검증 기준이 자동으로 업데이트됨.
  - L350-363: 체크리스트는 prompt-designer와 prompt-validator 모두 참조하는 실무 가이드.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 테마별 조건부 타겟 테이블 존재 확인
    Tool: Bash (grep)
    Preconditions: scene-richness-spec.md 수정 완료
    Steps:
      1. grep -c "Full-bleed\|Structured\|Intentional-margin" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. Assert count ≥ 3
    Expected Result: 3개 테마 그룹이 모두 존재
    Failure Indicators: 테마 그룹이 누락되면 단일 타겟이 유지된 것
    Evidence: .sisyphus/evidence/task-2-theme-conditional-grep.txt

  Scenario: 기존 단일 "30-40%" 타겟 교체 확인
    Tool: Bash (grep)
    Preconditions: scene-richness-spec.md 수정 완료
    Steps:
      1. grep "30-40% negative space" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. Assert: 기존 단일 권장 문구가 사라졌거나 조건부로 변경됨
    Expected Result: "30-40% negative space: Optimal for readability" 문장이 삭제/대체됨
    Failure Indicators: 기존 문구가 그대로 남아있으면 교체 실패
    Evidence: .sisyphus/evidence/task-2-old-target-removed.txt

  Scenario: pitch 30%+ 타겟 유지 확인
    Tool: Bash (grep)
    Preconditions: scene-richness-spec.md 수정 완료
    Steps:
      1. grep "pitch.*30%\|30%.*pitch\|Intentional.*30" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. Assert match found
    Expected Result: pitch 테마의 30%+ 타겟이 테이블에 명시됨
    Failure Indicators: pitch 예외가 없으면 pitch 여백이 축소될 위험
    Evidence: .sisyphus/evidence/task-2-pitch-preserved.txt
  ```

  **Evidence to Capture:**
  - [ ] task-2-theme-conditional-grep.txt
  - [ ] task-2-old-target-removed.txt
  - [ ] task-2-pitch-preserved.txt

  **Commit**: YES — C2
  - Message: `refactor(visual-generator): replace fixed negative space target with theme-conditional density table`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`
  - Pre-commit: `grep "Structured\|Full-bleed" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`

- [x] 3. gov + seminar 테마 공간구성 강화 (Structured 그룹)

  **What to do**:
  - **theme-gov/SKILL.md**:
    - Rendering Style 테이블의 **공간구성 행** (L181)을 강화: "엣지-투-엣지 격자 + 20% 여백" → "엣지-투-엣지 격자. 네거티브 스페이스 ≤15%. 격자 박스가 캔버스의 최대 면적을 차지하도록 확장한다. 의미적으로 중요한 박스(핵심 성과, 주요 전략)는 다른 박스 대비 10-20% 크게 배치한다. 상단 배너 + 본문 그리드 + 하단 주석의 3단 구조." 류로 업데이트
    - Golden Reference의 **Scene Description** (L346-347)에 캔버스 채우기 문장 1개 추가: "네 개의 전략 박스가 캔버스 면적을 최대한 활용하도록 확장되어 배치되며, 박스 사이 여백은 내용 구분에 필요한 최소한으로 제한한다." 류 삽입
    - Golden Reference의 **Rendering Style 공간구성** (L355)에 스케일 원칙 반영
  - **theme-seminar/SKILL.md**:
    - Rendering Style 테이블의 **공간구성 행** (L176)을 강화: 기존 "매거진 에디토리얼 레이아웃" 뒤에 "3D 아이콘과 텍스트 블록이 캔버스 면적을 최대한 활용하도록 배치한다. 의미적으로 중요한 3D 아이콘은 할당 영역보다 10-20% 크게 렌더링하여 캔버스 밀도를 높인다. 네거티브 스페이스 ≤15%." 류 추가
    - 단, "여백은 빈 공간이 아니라 시각적 숨 쉴 틈" (L237) 철학은 유지 — "시각적 리듬을 위한 최소한의 여백은 유지하되, 불필요한 빈 공간은 요소 크기 확대로 대체한다" 류의 조화 문구
    - Golden Reference의 **Scene Description** (L384-385)에 캔버스 채우기 문장 1개 추가
    - Golden Reference의 **Rendering Style 공간구성** (L393)에 스케일 원칙 반영

  **Must NOT do**:
  - 공간구성 이외의 Rendering Style 6개 차원 변경 금지
  - CONTENT 항목 수 규칙 변경 금지
  - Golden Reference의 CONTENT 블록, CONFIGURATION 블록, FORBIDDEN ELEMENTS 블록 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 2개 파일의 동일 패턴 수정. Rendering Style 행 + Golden Reference 2곳.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md:169-182` — Rendering Style 테이블. L181 공간구성 행 수정.
  - `plugins/visual-generator/skills/theme-gov/SKILL.md:346-356` — Golden Reference Scene Description + Rendering Style.
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:164-177` — Rendering Style 테이블. L176 공간구성 행 수정.
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:384-394` — Golden Reference Scene Description + Rendering Style.
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:237` — "여백 활용" 철학 — 이 원칙을 존중하면서 캔버스 밀도 강화.

  **WHY Each Reference Matters**:
  - 공간구성 행: prompt-designer가 Phase 2에서 직접 읽는 규칙. 이것이 바뀌면 생성 결과가 직접 변경됨.
  - Golden Reference: prompt-designer가 Phase 2에서 먼저 학습하는 예시. 규칙보다 Golden Reference가 더 강한 영향력을 가짐.
  - L237 여백 철학: seminar의 디자인 DNA. 이것을 존중하면서 밀도를 높이는 균형이 필요.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: gov 공간구성 캔버스 채우기 지시어 확인
    Tool: Bash (grep)
    Preconditions: theme-gov/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-gov/SKILL.md
      2. Assert output contains "캔버스" or "면적" or "채우" or "확장" or "≤15%"
    Expected Result: 공간구성 행에 캔버스 채우기 관련 언어 포함
    Evidence: .sisyphus/evidence/task-3-gov-spatial.txt

  Scenario: seminar 공간구성 캔버스 채우기 지시어 확인
    Tool: Bash (grep)
    Preconditions: theme-seminar/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-seminar/SKILL.md
      2. Assert output contains "캔버스" or "면적" or "밀도" or "≤15%"
    Expected Result: 공간구성 행에 캔버스 밀도 강화 언어 포함
    Evidence: .sisyphus/evidence/task-3-seminar-spatial.txt

  Scenario: seminar "숨 쉴 틈" 철학 보존 확인
    Tool: Bash (grep)
    Preconditions: theme-seminar/SKILL.md 수정 완료
    Steps:
      1. grep "숨 쉴 틈\|breathing" plugins/visual-generator/skills/theme-seminar/SKILL.md
      2. Assert match found
    Expected Result: 여백 철학이 유지됨
    Evidence: .sisyphus/evidence/task-3-seminar-breathing-preserved.txt

  Scenario: gov/seminar Rendering Style 다른 차원 미변경 확인
    Tool: Bash (grep)
    Preconditions: 수정 완료
    Steps:
      1. git diff plugins/visual-generator/skills/theme-gov/SKILL.md | grep "^[+-]" | grep -v "공간 구성\|공간구성\|Scene Description\|Rendering Style\|캔버스\|면적\|확장\|밀도\|스케일"
      2. Assert: 공간구성/Scene Description/Rendering Style 관련 외의 변경이 없음
    Expected Result: diff에서 관련 키워드 외의 변경 라인이 없음
    Evidence: .sisyphus/evidence/task-3-dimension-isolation.txt
  ```

  **Evidence to Capture:**
  - [ ] task-3-gov-spatial.txt
  - [ ] task-3-seminar-spatial.txt
  - [ ] task-3-seminar-breathing-preserved.txt
  - [ ] task-3-dimension-isolation.txt

  **Commit**: YES — C3
  - Message: `refactor(visual-generator): strengthen 공간구성 for gov and seminar themes`
  - Files: `plugins/visual-generator/skills/theme-gov/SKILL.md`, `plugins/visual-generator/skills/theme-seminar/SKILL.md`
  - Pre-commit: `grep "캔버스\|면적\|채우\|확장" plugins/visual-generator/skills/theme-gov/SKILL.md`

- [x] 4. concept + whatif 테마 공간구성 강화 (Full-bleed 그룹)

  **What to do**:
  - **theme-concept/SKILL.md**:
    - Rendering Style 테이블의 **공간구성 행** (L183)을 강화: 기존 "풀블리드(edge-to-edge) 장면" 뒤에 "전경-중경-후경의 시각 요소가 캔버스 면적의 80% 이상을 차지하도록 구성한다. 핵심 캐릭터와 주요 오브젝트는 장면에서 가능한 한 크게 묘사하여 캔버스를 시각적으로 채운다. 네거티브 스페이스 ≤20%." 류 추가
    - **5% 세이프 존 규칙은 그대로 보존**: "세이프 존: 모든 핵심 시각 요소는 캔버스 가장자리에서 5% 이상 안쪽에 완전히 포함되어야 한다" — 이 문구를 삭제하거나 수정하지 않음
    - Golden Reference의 **Scene Description** (L382-388 부근)에 요소 스케일 확대 문장 1개 추가
    - Golden Reference의 **Rendering Style 공간구성** (L388)에 밀도 원칙 반영
  - **theme-whatif/SKILL.md**:
    - Rendering Style 테이블의 **공간구성 행** (L176)을 강화: 기존 "풀블리드(edge-to-edge) 장면" 뒤에 "시네마틱 장면의 시각 요소(배경 환경, HUD UI, 인물/실루엣)가 캔버스 면적을 최대한 채우도록 구성한다. 핵심 시각 요소는 화면에서 가능한 한 크게 배치한다. 네거티브 스페이스 ≤20%." 류 추가
    - Golden Reference의 **Scene Description** (L351 부근)에 캔버스 밀도 문장 추가
    - Golden Reference의 **Rendering Style 공간구성** (L348)에 밀도 원칙 반영

  **Must NOT do**:
  - concept의 "5% 이상 안쪽" 세이프 존 규칙 변경 금지
  - concept의 "캔버스 완결성" 섹션(L218-228) 변경 금지
  - concept의 "잘림 금지" 규칙 변경 금지
  - 공간구성 이외의 Rendering Style 6개 차원 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 2개 파일의 동일 패턴 수정.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 5)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-concept/SKILL.md:183` — 공간구성 행. "풀블리드(edge-to-edge) 장면. 전체 캔버스를 하나의 연속된 장면으로 활용." — 이 뒤에 밀도 강화 문구 추가.
  - `plugins/visual-generator/skills/theme-concept/SKILL.md:218-228` — 캔버스 완결성 섹션. 5% 세이프 존, 잘림 금지 규칙 — 변경 금지 대상.
  - `plugins/visual-generator/skills/theme-concept/SKILL.md:382-388` — Golden Reference Rendering Style. 공간구성 라인 업데이트.
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md:176` — 공간구성 행. "풀블리드(edge-to-edge) 장면. 배경이 화면 끝까지 채워진다." — 밀도 강화 문구 추가.
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md:342-351` — Golden Reference Rendering Style + Scene Description.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: concept 공간구성 밀도 강화 확인
    Tool: Bash (grep)
    Preconditions: theme-concept/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-concept/SKILL.md | head -3
      2. Assert output contains "80%\|면적\|크게\|채우\|밀도\|≤20%"
    Expected Result: 공간구성에 캔버스 밀도 강화 언어 포함
    Evidence: .sisyphus/evidence/task-4-concept-spatial.txt

  Scenario: concept 5% 세이프 존 보존 확인
    Tool: Bash (grep)
    Preconditions: theme-concept/SKILL.md 수정 완료
    Steps:
      1. grep "5% 이상 안쪽" plugins/visual-generator/skills/theme-concept/SKILL.md
      2. Assert match found
    Expected Result: 세이프 존 규칙이 보존됨
    Failure Indicators: 문구가 사라지면 critical regression
    Evidence: .sisyphus/evidence/task-4-concept-safezone.txt

  Scenario: whatif 공간구성 밀도 강화 확인
    Tool: Bash (grep)
    Preconditions: theme-whatif/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-whatif/SKILL.md | head -3
      2. Assert output contains "면적\|크게\|채우\|밀도\|≤20%"
    Expected Result: 공간구성에 캔버스 밀도 강화 언어 포함
    Evidence: .sisyphus/evidence/task-4-whatif-spatial.txt
  ```

  **Evidence to Capture:**
  - [ ] task-4-concept-spatial.txt
  - [ ] task-4-concept-safezone.txt
  - [ ] task-4-whatif-spatial.txt

  **Commit**: YES — C4
  - Message: `refactor(visual-generator): strengthen 공간구성 for concept and whatif themes`
  - Files: `plugins/visual-generator/skills/theme-concept/SKILL.md`, `plugins/visual-generator/skills/theme-whatif/SKILL.md`
  - Pre-commit: `grep "5% 이상 안쪽" plugins/visual-generator/skills/theme-concept/SKILL.md`

- [x] 5. pitch + comparison 테마 공간구성 강화 (Intentional-margin 그룹)

  **What to do**:
  - **theme-pitch/SKILL.md**:
    - Rendering Style 테이블의 **공간구성 행** (L137)을 미세 조정: 기존 "30% 이상 의도적 어두운 여백" 규칙은 **그대로 유지**하면서, "핵심 숫자(hero_statement)가 화면의 30% 이상을 차지하도록 스케일을 최대화한다. 프로스티드 글래스 카드와 보조 텍스트의 크기도 가능한 한 확대하여 콘텐츠 영역 내 빈 공간을 최소화한다." 류 추가
    - 핵심: pitch의 여백은 "의도적"이므로 줄이지 않되, **콘텐츠 영역 내부의 요소 크기를 키운다**
    - Golden Reference의 Scene Description + Rendering Style 공간구성에 요소 스케일 강조 반영
  - **theme-comparison/SKILL.md**:
    - 이미 95% fill이므로 **최소한의 변경만**: Rendering Style 테이블의 **공간구성 행** (L144)에 "좌우 이미지가 캔버스를 빈틈없이 채우며, 텍스트 오버레이 영역도 최소 면적으로 제한한다. 네거티브 스페이스 ≤10%." 류의 명시적 수치화만 추가
    - Golden Reference의 Scene Description에 캔버스 밀도 확인 문장 1개 추가

  **Must NOT do**:
  - pitch의 "30% 이상 의도적 어두운 여백" 삭제 또는 수치 변경 절대 금지
  - pitch의 "어두운 배경의 깊이감이 콘텐츠를 더욱 부각시킨다" 문구 변경 금지
  - comparison의 "이미지 95% + 텍스트 오버레이 5%" 비율 변경 금지
  - 공간구성 이외의 Rendering Style 차원 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 2개 파일. pitch는 세심한 보존 필요, comparison은 최소 변경.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:137` — 공간구성 행. "대담한 비대칭. 핵심 숫자가 좌측 또는 중앙 상단에 매우 크게. 나머지 요소들이 어두운 공간에 작게 흩어진다. Z-패턴 시선 유도. 30% 이상 의도적 어두운 여백." — 30%+ 여백 유지하면서 요소 스케일 강화.
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:83-85` — "여백 활용" 섹션. "최소 30% 여백: 어두운 여백이 메시지의 무게감을 증폭" — 변경 금지 대상.
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md:144` — 공간구성 행. "이미지 95% + 텍스트 오버레이 5%." — 명시적 수치화만 추가.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: pitch "30% 이상 의도적" 문구 보존 확인
    Tool: Bash (grep)
    Preconditions: theme-pitch/SKILL.md 수정 완료
    Steps:
      1. grep "30% 이상 의도적" plugins/visual-generator/skills/theme-pitch/SKILL.md
      2. Assert match found
    Expected Result: 30% 의도적 여백 문구가 보존됨
    Failure Indicators: 이 문구가 사라지면 CRITICAL regression
    Evidence: .sisyphus/evidence/task-5-pitch-30-preserved.txt

  Scenario: pitch 요소 스케일 강화 확인
    Tool: Bash (grep)
    Preconditions: theme-pitch/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-pitch/SKILL.md | head -3
      2. Assert output contains "스케일\|최대화\|크게\|확대\|30% 이상.*차지"
    Expected Result: 공간구성에 요소 스케일 강화 언어 추가됨
    Evidence: .sisyphus/evidence/task-5-pitch-scale.txt

  Scenario: comparison 공간구성 수치 명시화 확인
    Tool: Bash (grep)
    Preconditions: theme-comparison/SKILL.md 수정 완료
    Steps:
      1. grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-comparison/SKILL.md | head -3
      2. Assert output contains "≤10%\|빈틈없이\|최소 면적"
    Expected Result: 네거티브 스페이스 수치 명시됨
    Evidence: .sisyphus/evidence/task-5-comparison-spatial.txt
  ```

  **Evidence to Capture:**
  - [ ] task-5-pitch-30-preserved.txt
  - [ ] task-5-pitch-scale.txt
  - [ ] task-5-comparison-spatial.txt

  **Commit**: YES — C5
  - Message: `refactor(visual-generator): strengthen 공간구성 for pitch and comparison themes preserving intentional margins`
  - Files: `plugins/visual-generator/skills/theme-pitch/SKILL.md`, `plugins/visual-generator/skills/theme-comparison/SKILL.md`
  - Pre-commit: `grep "30% 이상 의도적" plugins/visual-generator/skills/theme-pitch/SKILL.md`

- [x] 6. 버전 범프 + 프로젝트 문서 업데이트

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json`: version "3.2.0" → "3.3.0"
  - `.claude-plugin/marketplace.json`: visual-generator 항목의 version "3.2.0" → "3.3.0"
  - `.claude-plugin/marketplace.json`: metadata.version 동기화 ("3.5.0" → "3.6.0")
  - `AGENTS.md`: Generated 날짜 업데이트, Version 업데이트
  - `README.md`: Version 업데이트, 변경 이력 테이블에 새 항목 추가: "3.6.0 | 2026-03-17 | visual-generator v3.3.0: 여백 최소화 — Scene Description 캔버스 채우기 지시 추가, Rendering Style 공간구성 강화, 테마별 조건부 네거티브 스페이스 타겟"

  **Must NOT do**:
  - 다른 플러그인의 버전 변경 금지
  - AGENTS.md/README.md에서 visual-generator 관련 외 섹션 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 버전 숫자 교체 + 변경 이력 1줄 추가. 정형화된 작업.
  - **Skills**: [`git-master`]
    - `git-master`: 최종 커밋 생성 시 사용.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential after Wave 2)
  - **Blocks**: F1, F2, F3
  - **Blocked By**: Tasks 3, 4, 5

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — version 필드
  - `.claude-plugin/marketplace.json` — visual-generator 항목 + metadata.version
  - `AGENTS.md:3` — Version 필드
  - `README.md:5` — Version 필드, 변경 이력 테이블

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: visual-generator 버전 3.3.0 확인
    Tool: Bash (grep)
    Preconditions: 버전 범프 완료
    Steps:
      1. grep "3.3.0" plugins/visual-generator/.claude-plugin/plugin.json
      2. Assert match found
    Expected Result: plugin.json에 3.3.0 버전 기재
    Evidence: .sisyphus/evidence/task-6-version-bump.txt

  Scenario: README 변경 이력 항목 확인
    Tool: Bash (grep)
    Preconditions: README 업데이트 완료
    Steps:
      1. grep "여백 최소화\|whitespace\|캔버스 채우기" README.md
      2. Assert match found
    Expected Result: 변경 이력에 여백 최소화 관련 항목 존재
    Evidence: .sisyphus/evidence/task-6-readme-changelog.txt
  ```

  **Evidence to Capture:**
  - [ ] task-6-version-bump.txt
  - [ ] task-6-readme-changelog.txt

  **Commit**: YES — C6
  - Message: `chore(visual-generator): bump version to v3.3.0 and update project documentation`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`
  - Pre-commit: —

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 3 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, grep for directive). For each "Must NOT Have": search codebase for forbidden changes — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Regression Guard Check** — `unspecified-high`
  Run these exact checks:
  1. `grep "30% 이상 의도적" plugins/visual-generator/skills/theme-pitch/SKILL.md` → MUST find match
  2. `grep "5% 이상 안쪽" plugins/visual-generator/skills/theme-concept/SKILL.md` → MUST find match
  3. For each theme SKILL.md, verify that ONLY the 공간구성 row in the Rendering Style table was modified — 서피스, 배경, 코너/경계, 연결선, 시각장식, 시각메타포 rows MUST be identical to pre-change
  4. Verify prompt-validator.md has zero changes (8 dimensions intact)
  5. Verify CONTENT max/min counts unchanged in prompt-designer.md
  Output: `Pitch Guard [PASS/FAIL] | Concept Guard [PASS/FAIL] | Dimension Isolation [N/6 PASS] | Validator Intact [PASS/FAIL] | VERDICT`

- [x] F3. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Commit # | Scope | Message | Files | Pre-commit Check |
|:--------:|-------|---------|-------|------------------|
| C1 | Central rules | `refactor(visual-generator): add canvas-filling and element-scaling directives to prompt-designer` | prompt-designer.md | grep "캔버스" prompt-designer.md |
| C2 | Spec update | `refactor(visual-generator): replace fixed negative space target with theme-conditional density table` | scene-richness-spec.md | grep "테마별\|theme-conditional" scene-richness-spec.md |
| C3 | Structured themes | `refactor(visual-generator): strengthen 공간구성 for gov and seminar themes` | theme-gov/SKILL.md, theme-seminar/SKILL.md | grep "캔버스\|채우" theme-gov/SKILL.md |
| C4 | Full-bleed themes | `refactor(visual-generator): strengthen 공간구성 for concept and whatif themes` | theme-concept/SKILL.md, theme-whatif/SKILL.md | grep "스케일\|확대" theme-concept/SKILL.md |
| C5 | Intentional-margin themes | `refactor(visual-generator): strengthen 공간구성 for pitch and comparison themes` | theme-pitch/SKILL.md, theme-comparison/SKILL.md | grep "30% 이상 의도적" theme-pitch/SKILL.md |
| C6 | Version + docs | `chore(visual-generator): bump version to v3.3.0 and update project documentation` | plugin.json, marketplace.json, AGENTS.md, README.md | — |

---

## Success Criteria

### Verification Commands
```bash
# 캔버스 채우기 지시어 존재 확인 (prompt-designer)
grep -c "캔버스.*채우\|canvas.*fill\|꽉 채" plugins/visual-generator/agents/prompt-designer.md  # Expected: ≥1

# 요소 스케일링 지시어 존재 확인 (prompt-designer)
grep -c "스케일.*확대\|크기.*확대\|scale.*up\|크게.*렌더링" plugins/visual-generator/agents/prompt-designer.md  # Expected: ≥1

# 테마별 조건부 타겟 존재 확인 (scene-richness-spec)
grep -c "Full-bleed\|Structured\|Intentional" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md  # Expected: ≥3

# pitch 가드레일 보존 확인
grep "30% 이상 의도적" plugins/visual-generator/skills/theme-pitch/SKILL.md  # Expected: match

# concept 세이프 존 보존 확인
grep "5% 이상 안쪽" plugins/visual-generator/skills/theme-concept/SKILL.md  # Expected: match

# 6개 테마 공간구성 업데이트 확인
for theme in gov seminar concept whatif pitch comparison; do grep "공간 구성\|공간구성" plugins/visual-generator/skills/theme-$theme/SKILL.md | head -1; done  # Expected: 6 results
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] pitch 30%+ dark margin preserved
- [ ] concept 5% safe zone preserved
- [ ] Only 공간구성 dimension modified in Rendering Style tables
- [ ] All Golden References updated to demonstrate canvas-filling
- [ ] Version bumped to v3.3.0 in plugin.json + marketplace.json
- [ ] AGENTS.md + README.md updated with change history
