# Visual Generator 품질 복원 — PhD급 공학 프레젠테이션 수준으로

## TL;DR

> **Quick Summary**: visual-generator v2.0.0 XML-tag 전환 과정에서 발생한 프롬프트 밀도 저하, 폰트명 리터럴 렌더링, 슬라이드 간 비일관성을 해결하여 공학 박사 수준 청중(KIMM)에게 적합한 전문적 이미지 생성 능력을 복원한다.
> 
> **Deliverables**:
> - 폰트명 유출이 차단된 korean-typography-spec.md 개정
> - 최소 텍스트 밀도가 강제되는 content-organizer 개선
> - Golden Reference 인라인 포함 + 밀도 요건이 추가된 prompt-designer 강화
> - 슬라이드 간 일관성을 보장하는 Style Sheet 메커니즘
> - prompt-validator 강화 (밀도/폰트/팔레트 검증 차원 추가)
> - 6개 테마 SKILL.md 전체 타이포그래피 지침 개정
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 → Task 3 → Task 5 → Task 8 → Task 10 → F1-F4

---

## Context

### Original Request
사용자는 visual-generator v2.0.0 XML-tag 전환 이후 프롬프트 품질이 급격히 하락했다고 보고. 구체적으로: (1) 프롬프트 구성이 너무 단순해짐, (2) 슬라이드 간 일관성 없음, (3) v1.11.0의 전문성 느낌 상실, (4) prompt-validator가 시간만 소비, (5) 폰트 정보가 이미지에 그대로 렌더링됨. commit `afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb` 시점이 가장 우수한 프롬프트를 생성했다고 참조.

### Interview Summary
**Key Discussions**:
- 사용자 제공 샘플: `<text_to_render>` 항목 4개(title, subtitle, event, presenter) — Golden Reference 25항목 대비 극단적 저밀도
- 스크린샷: "Nanum Gothic ExtraBold" 텍스트가 번호 박스 옆에 이미지 내 보이는 텍스트로 렌더링됨
- 대상 청중: KIMM(한국기계연구원) 공학 박사급 — 데이터 밀도와 기술적 깊이가 핵심

**Research Findings**:
- v3 프롬프트 23개 분석: scene 7-10문장(양호), text_to_render 3-11항목(Golden Reference 25 대비 부족), 구조적 검증 100% 통과
- scene-richness-spec.md: EXCELLENT 등급 기준 잘 정의되어 있으나 **최소 텍스트 밀도 요건이 부재**
- korean-typography-spec.md: "Nanum Gothic ExtraBold", "Pretendard ExtraBold" 등 **구체적 폰트명 사용을 권장** → Gemini가 이를 이미지 내 보이는 텍스트로 렌더링하는 직접적 원인
- validation-rules-map.md: 24개 검증 포인트가 잘 문서화되어 있으나 **콘텐츠 밀도/창의적 품질은 미검증**

### Metis Review
**Identified Gaps** (addressed):
- 폰트명 유출 범위가 korean-typography-spec.md만이 아닌 6개 테마 SKILL.md + prompt-designer + scene-richness-spec Golden Reference에 걸쳐 총 10개 파일에 산재 → 전수 수정 필요
- 최소 텍스트 밀도 강제 메커니즘 부재 — 파이프라인의 구조적 근본 원인
- commit `afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb` 시점의 구버전 코드를 실제로 비교해야 함 (git diff 필요)
- prompt-validator 제거 시 검증 커버리지 감소 리스크
- content-organizer의 scene_context 최소 시각 요소 수(5개)가 enforce되지 않는 실효성 문제
- 타이틀/커버 슬라이드 vs 본문 슬라이드의 밀도 요건 차별화 필요

---

## Work Objectives

### Core Objective
visual-generator가 생성하는 XML-tag 프롬프트의 **콘텐츠 밀도**, **타이포그래피 안전성**, **슬라이드 간 일관성**을 PhD급 공학 발표에 적합한 수준으로 끌어올린다.

### Concrete Deliverables
- 개정된 `korean-typography-spec.md` (폰트명 서술적 지침으로 전환)
- 강화된 `content-organizer.md` (최소 render_text 수, scene_context 시각 요소 수 강제)
- 강화된 `prompt-designer.md` (테마별 Golden Reference 인라인, 최소 밀도 검증, Style Sheet 생성)
- 강화된 `prompt-validator.md` (불필요 차원 정리 + 밀도/폰트/팔레트 검증 추가, 7차원)
- 개정된 6개 테마 SKILL.md (폰트명 제거, 서술적 타이포그래피 힌트)
- 개정된 `scene-richness-spec.md` Golden Reference (폰트명 제거)
- 개정된 `visual-generate.md` 오케스트레이터 (Style Sheet 전달 메커니즘)
- 개정된 `content-reviewer.md` (밀도 검증 차원 추가)

### Definition of Done
- [ ] 폰트 패밀리명("Nanum Gothic ExtraBold" 등)이 모든 프롬프트 출력에서 0건
- [ ] 본문 슬라이드의 `<text_to_render>` 항목이 최소 8개 이상
- [ ] 동일 프레젠테이션 내 모든 슬라이드의 색상 팔레트가 일치
- [ ] prompt-validator가 밀도, 폰트 유출, 팔레트 일관성을 검증

### Must Have
- 폰트명 리터럴 렌더링 완전 차단
- 본문 슬라이드 최소 텍스트 밀도 강제 (8항목)
- 타이틀 슬라이드 예외 처리 (4항목 허용)
- 슬라이드 간 스타일 일관성 보장 메커니즘
- prompt-validator에 밀도/폰트/팔레트 검증 차원 추가

### Must NOT Have (Guardrails)
- pt/px 등 단위를 프롬프트에 포함하지 않음
- 마크다운 장식(**bold**, #heading)을 XML 태그 내부에 사용하지 않음
- generate_slide_images.py 스크립트를 수정하지 않음
- 새로운 테마나 레이아웃을 추가하지 않음
- Gemini API 모델(gemini-3-pro-image-preview)을 변경하지 않음
- `<typography>`에 구체적 폰트 패밀리명을 사용하지 않음 (서술적 가이드만 허용)
- 이전 v1.x 마크다운 4-block 형식으로 회귀하지 않음
- prompt-designer가 생성하는 프롬프트에 검증 코멘트나 메타정보를 포함하지 않음

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (프롬프트 품질은 주관적 + Gemini API 렌더링 의존)
- **Automated tests**: None (프롬프트 품질은 구조적 검증으로 확인)
- **Framework**: Agent-Executed QA (도구 기반 검증: Grep tool, Read tool, Glob tool)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **프롬프트 구조 검증**: Grep으로 금지 패턴 탐지, 항목 수 카운팅
- **폰트명 유출 검증**: Grep으로 "Nanum Gothic", "Pretendard", "Malgun Gothic" 등 폰트 패밀리명 탐지
- **일관성 검증**: 프롬프트 파일 간 팔레트 코드 비교
- **실제 렌더링 검증**: 삭제됨 — 렌더링 전까지만 검증 (renderer-agent는 파이프라인에 유지되나 QA에서 실행하지 않음)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation fixes):
├── Task 1: korean-typography-spec.md 폰트명→서술적 지침 전환 [quick]
├── Task 2: scene-richness-spec.md Golden Reference 폰트명 제거 [quick]
├── Task 3: content-organizer.md 최소 밀도 요건 추가 [unspecified-high]
├── Task 4: content-reviewer.md 밀도 검증 차원 추가 [quick]
└── Task 5: git diff로 v1.11.0 prompt-designer 비교분석 [unspecified-high]

Wave 2 (After Wave 1 — core improvements):
├── Task 6: 6개 테마 SKILL.md 타이포그래피 지침 일괄 개정 [unspecified-high]
├── Task 7: prompt-designer.md 대폭 강화 (Golden Ref + 밀도 강제 + Style Sheet) [deep]
├── Task 8: prompt-validator.md 강화 (불필요 차원 정리 + 밀도/폰트/팔레트 검증 추가) [unspecified-high]
└── Task 9: visual-generate.md 오케스트레이터 Style Sheet 메커니즘 추가 [quick]

Wave 3 (After Wave 2 — integration + verification):
├── Task 10: 통합 테스트 — 실제 프롬프트 생성 + 구조적 검증 (렌더링 전까지) [deep]
└── Task 11: plugin.json + marketplace.json 버전 업데이트 + AGENTS.md 동기화 [quick]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 6 → Task 7 → Task 10 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 6, 7 |
| 2 | — | 7 |
| 3 | — | 7 |
| 4 | — | — |
| 5 | — | 7 |
| 6 | 1 | 7, 10 |
| 7 | 1, 2, 3, 5, 6 | 10 |
| 8 | — | 9, 10 |
| 9 | 8 | 10 |
| 10 | 6, 7, 9 | F1-F4 |
| 11 | 10 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: **5** — T1 `quick`, T2 `quick`, T3 `unspecified-high`, T4 `quick`, T5 `unspecified-high`
- **Wave 2**: **4** — T6 `unspecified-high`, T7 `deep`, T8 `unspecified-high`, T9 `quick`
- **Wave 3**: **2** — T10 `deep`, T11 `quick`
- **FINAL**: **4** — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

---

- [x] 1. korean-typography-spec.md — 폰트명→서술적 가이드 전환

  **What to do**:
  - `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md`를 읽는다
  - Section 1 Mandatory Typography Directive에서 **구체적 폰트 패밀리명을 모두 제거**한다:
    - "Nanum Gothic ExtraBold" → 삭제
    - "Pretendard ExtraBold" → 삭제
    - "Apple SD Gothic Neo Bold" → 삭제
    - "Malgun Gothic Bold" → 삭제
  - 대신 서술적 지침으로 대체한다: "heavy-weight Gothic-style sans-serif Korean font at 800+ weight" (폰트명 없이)
  - Section 4 Font Family Recommendations에서 "Preferred" 목록의 구체적 폰트명을 **서술적 카테고리**로 대체:
    - 기존: "Nanum Gothic ExtraBold / Bold" → 변경: "Heavy-weight Korean Gothic sans-serif at ExtraBold (800+) or Bold (700)"
  - Section 6 Phonetic Anchoring의 Typography 예시에서도 폰트명 제거
  - Section 2, 3, 7의 Anti-Pattern 예시에서 폰트명을 일반화 ("specific Gothic-style Korean font" 등)
  - 문서 전체에서 `Nanum Gothic`, `Pretendard`, `Apple SD Gothic Neo`, `Malgun Gothic` 4종의 구체적 폰트명이 0건이 되도록 한다
  - **새로 추가**: "CRITICAL: Never include specific font family names in `<typography>` output. Gemini renders font names as visible text in the image. Use only descriptive style hints." 경고문을 Section 1 상단에 추가

  **Must NOT do**:
  - 폰트 무게(weight) 숫자 가이드(800+, 700, 500 등)는 유지한다 (삭제 금지)
  - Gothic-style, sans-serif 등 일반적 스타일 카테고리는 유지한다
  - 문서 구조 자체를 변경하지 않는다 (섹션 순서, 제목 유지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 텍스트 치환 작업, 논리적 판단 최소
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: 브라우저 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: Tasks 6, 7
  - **Blocked By**: None (can start immediately)

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` — 전체 파일. 폰트 패밀리명이 포함된 모든 위치를 식별해야 함

  **WHY Each Reference Matters**:
  - 이 파일이 폰트명 유출의 최상위 원본. 여기서 폰트명을 제거해야 다른 모든 하류 파일의 수정이 의미를 가짐

  **Acceptance Criteria**:
  - [ ] `korean-typography-spec.md`에서 `Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic` Grep 결과 0건
  - [ ] "CRITICAL: Never include specific font family names" 경고문 존재
  - [ ] weight 숫자 가이드(800+, 700, 500)가 여전히 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 폰트명 완전 제거 확인
    Tool: Grep tool
    Preconditions: Task 1 완료 후
    Steps:
      1. Grep: "Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic" in korean-typography-spec.md
      2. Assert: 0 matches
      3. Grep: "800+|700|500" in korean-typography-spec.md
      4. Assert: ≥ 3 matches (weight 가이드 유지 확인)
    Expected Result: 폰트명 0건, weight 가이드 3건 이상
    Failure Indicators: 폰트명이 1건이라도 남아있거나, weight 가이드가 삭제됨
    Evidence: .sisyphus/evidence/task-1-font-removal.txt
  ```

  **Commit**: YES (groups with 2)
  - Message: `fix(visual-gen): remove literal font names from typography spec and golden refs`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md`

- [x] 2. scene-richness-spec.md Golden Reference — 폰트명 제거 + 밀도 기준 추가

  **What to do**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`를 읽는다
  - Section 8 Golden XML Examples의 2개 예시에서:
    - `<typography>` 내부의 모든 구체적 폰트 패밀리명을 서술적 지침으로 대체
    - 예: "Font family: Nanum Gothic Bold, Pretendard ExtraBold" → "Heavy-weight Gothic-style Korean sans-serif at ExtraBold (800+) for titles, Bold (700) for headers"
  - Section 6 Negative Space Density Guide에 **최소 텍스트 밀도 기준 추가**:
    - 새 하위 섹션: "### Minimum Text Density"
    - 본문 슬라이드: `<text_to_render>` 최소 8항목
    - 타이틀/커버 슬라이드: `<text_to_render>` 최소 3항목
    - 테마별 상한은 기존 유지 (seminar 25, pitch 18 등)
  - Section 7 Quality Grading Criteria의 EXCELLENT 등급에 밀도 조건 추가:
    - "✅ Text density: ≥ 8 items for body slides, ≥ 3 items for title slides"

  **Must NOT do**:
  - Golden Reference의 `<scene>`, `<text_to_render>`, `<layout>` 구조를 변경하지 않는다
  - 기존 7요소 체크리스트를 수정하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 텍스트 치환 + 소규모 섹션 추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:243-314` — Golden Reference Example 1 (폰트명 위치 확인)
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:172-197` — Negative Space Density Guide (밀도 기준 추가 위치)

  **Acceptance Criteria**:
  - [ ] scene-richness-spec.md에서 `Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic` Grep 결과 0건
  - [ ] "Minimum Text Density" 하위 섹션 존재
  - [ ] EXCELLENT 등급에 text density 조건 포함

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: Golden Reference 폰트명 제거 + 밀도 기준 존재
    Tool: Grep tool
    Steps:
      1. Grep: "Nanum Gothic|Pretendard" in scene-richness-spec.md → 0건
      2. Grep: "Minimum Text Density" in scene-richness-spec.md → ≥ 1건
      3. Grep: "≥ 8 items" in scene-richness-spec.md → ≥ 1건
    Expected Result: 폰트명 0건, 밀도 기준 존재
    Evidence: .sisyphus/evidence/task-2-golden-ref-fix.txt
  ```

  **Commit**: YES (groups with 1)
  - Message: `fix(visual-gen): remove literal font names from typography spec and golden refs`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`

- [x] 3. content-organizer.md — 최소 텍스트 밀도 + 시각 요소 수 강제

  **What to do**:
  - `plugins/visual-generator/agents/content-organizer.md`를 읽는다
  - concepts.md Schema 섹션에 **최소 밀도 요건**을 추가한다:
    - `render_text` 최소 항목 수: 본문 슬라이드 8개, 타이틀 슬라이드 3개
    - `scene_context` 최소 구체 시각 요소: 7개 (기존 5개에서 상향)
  - **슬라이드 유형 분류 규칙** 추가:
    - 타이틀 슬라이드: 제목, 부제목, 발표자명, 행사명 등 메타 정보만 포함하는 첫 번째/마지막 슬라이드
    - 본문 슬라이드: 나머지 모든 슬라이드 (데이터, 분석, 프로세스, 비교 등)
  - slide_plan.md Schema의 테이블에 `slide_type` 컬럼 추가 (`title` | `body`)
  - MUST DO 섹션에 추가:
    - `render_text` 항목이 최소 요건 미달 시 추가 데이터 포인트를 추출하거나, 핵심 메시지를 KPI/수치/세부 항목으로 분해한다
    - 추상적 문장("기술 혁신을 선도한다")을 구체적 데이터("연 매출 150억, 특허 23건, 기술이전 12건")로 변환한다
  - **PhD급 청중 데이터 밀도 지침** 추가:
    - "공학 박사 수준 청중은 추상적 선언보다 구체적 수치, 방법론 키워드, 성과 지표를 기대한다"
    - "가능하면 각 슬라이드에 최소 2개의 정량적 지표(수치, 비율, 기간)를 포함한다"

  **Must NOT do**:
  - 프롬프트를 직접 생성하지 않는다 (content-organizer 역할 범위 유지)
  - 기존 Text Classification Rule을 삭제하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 에이전트 사양 설계 변경, 새 분류 규칙 추가 등 중간 복잡도
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/agents/content-organizer.md` — 전체 파일 (현재 concepts.md Schema, slide_plan.md Schema, MUST DO 확인)
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:243-314` — Golden Reference의 text_to_render 25항목을 밀도 벤치마크로 참조

  **Acceptance Criteria**:
  - [ ] content-organizer.md에 `slide_type` 분류 규칙 존재 (title/body)
  - [ ] 본문 슬라이드 `render_text` 최소 8항목 요건 명시
  - [ ] scene_context 최소 시각 요소 7개 명시
  - [ ] PhD급 청중 데이터 밀도 지침 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 밀도 요건 명시 확인
    Tool: Grep tool
    Steps:
      1. Grep: "slide_type" in content-organizer.md → ≥ 1건
      2. Grep: "최소 8" OR "minimum 8" OR "min.*8" in content-organizer.md → ≥ 1건
      3. Grep: "시각 요소.*7" OR "visual.*element.*7" in content-organizer.md → ≥ 1건
    Expected Result: 3개 요건 모두 명시
    Evidence: .sisyphus/evidence/task-3-density-enforcement.txt

  Scenario: 기존 Text Classification Rule 보존 확인
    Tool: Grep tool
    Steps:
      1. Grep: "Text Classification Rule" in content-organizer.md → ≥ 1건
    Expected Result: 기존 규칙 유지
    Evidence: .sisyphus/evidence/task-3-classification-preserved.txt
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(visual-gen): enforce minimum text density in upstream pipeline`
  - Files: `plugins/visual-generator/agents/content-organizer.md`

---

- [x] 4. content-reviewer.md — 텍스트 밀도 검증 차원 추가

  **What to do**:
  - `plugins/visual-generator/agents/content-reviewer.md`를 읽는다
  - Review Dimensions에 **6번째 차원: 텍스트 밀도 충족성** 추가:
    - `render_text` 항목 수가 `slide_type`에 따른 최소 요건을 충족하는가 (body ≥ 8, title ≥ 3)
    - `render_text`에 정량적 지표(KPI, 수치, 비율)가 최소 2개 포함되어 있는가
    - 미달 시 2점 감점
  - PASS/REJECT Logic에 밀도 차원 포함:
    - Hard Reject 조건 추가: `render_text` 항목 수가 최소 요건의 50% 미만 시 즉시 REJECT
  - 검증 결과 테이블에 6번째 행 추가

  **Must NOT do**:
  - 기존 5개 차원을 수정하지 않는다
  - organizer 출력 파일을 직접 수정하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일에 섹션 추가, 기존 구조 유지
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/agents/content-reviewer.md` — 전체 파일 (현재 5개 차원 확인, PASS/REJECT 로직 확인)

  **Acceptance Criteria**:
  - [ ] 6번째 검증 차원 "텍스트 밀도 충족성" 존재
  - [ ] Hard Reject 조건에 밀도 미달 50% 조건 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 밀도 차원 추가 확인
    Tool: Grep tool
    Steps:
      1. Grep: "텍스트 밀도" OR "text density" in content-reviewer.md → ≥ 1건
      2. Grep: "Hard Reject" in content-reviewer.md → ≥ 2건 (기존 1 + 새로운 1)
    Expected Result: 밀도 차원 존재, Hard Reject 조건 2개 이상
    Evidence: .sisyphus/evidence/task-4-reviewer-density.txt
  ```

  **Commit**: YES (groups with 3)
  - Message: `feat(visual-gen): enforce minimum text density in upstream pipeline`
  - Files: `plugins/visual-generator/agents/content-reviewer.md`

- [x] 5. git diff 비교분석 — v1.11.0 prompt-designer의 핵심 강점 추출

  **전제조건**: 이 태스크는 git 히스토리가 포함된 클론에서만 실행 가능합니다. 현재 워크스페이스에 `.git`이 없으면 대체 경로(B)를 따릅니다.

  **What to do**:
  - **경로 A (git 히스토리 존재 시)**:
    - `git show afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb:plugins/visual-generator/agents/prompt-designer.md`로 구버전 prompt-designer를 읽는다
    - `git show afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb:plugins/visual-generator/commands/visual-generate.md`로 구버전 오케스트레이터를 읽는다
  - **경로 B (git 히스토리 없을 시 — 대체 경로)**:
    - GitHub 웹에서 해당 커밋의 파일을 직접 조회: `https://github.com/orientpine/honeypot/blob/afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb/plugins/visual-generator/agents/prompt-designer.md`
    - 또는 현재 prompt-designer.md의 파일 내 주석/이력에서 v1.11.0 �을 추론
    - 또는 `validation-rules-map.md`의 v1.9.0~v1.11.0 규칙 매핑을 기반으로 v1.11.0의 핵심 패턴을 역추적
  - 현재 버전과 비교하여 다음을 식별:
    - v1.11.0에서 사라진 프롬프트 작성 지침 (장면 풍부함, 레이아웃 상세도, 텍스트 구성 방식)
    - v1.11.0의 INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN 4-block 형식의 핵심 장점
    - v1.11.0에서 사용했던 Golden Reference 또는 예시 프롬프트
  - 분석 결과를 `.sisyphus/drafts/v1-v2-comparison.md`에 저장
  - Task 7 (prompt-designer 강화)에 반영할 핵심 발견사항을 구조화

  **Must NOT do**:
  - 구버전으로 회귀하지 않는다 (XML-tag 유지)
  - 파일을 수정하지 않는다 (분석만 수행)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: git 이력 탐색 또는 웹 조회 + 비교 분석이 필요한 조사 작업
  - **Skills**: [`git-master`]
    - `git-master`: git show, git diff 명령으로 커밋 간 차이 분석에 필수 (경로 A 시)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - 현재 `plugins/visual-generator/agents/prompt-designer.md` — 현재 버전 (199줄)
  - 현재 `plugins/visual-generator/commands/visual-generate.md` — 현재 오케스트레이터 (68줄)
  - commit `afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb` — 사용자가 지정한 최적 품질 시점
  - `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — v1.9.0~v1.11.0 규칙 매핑 (경로 B 시 핵심 참조)

  **Acceptance Criteria**:
  - [ ] `.sisyphus/drafts/v1-v2-comparison.md` 생성됨
  - [ ] v1.11.0의 핵심 강점 3개 이상 식별됨
  - [ ] Task 7에 반영할 구체적 권고사항 포함

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 비교 분석 문서 생성 확인
    Tool: Read tool
    Steps:
      1. Read: .sisyphus/drafts/v1-v2-comparison.md
      2. Assert: 파일 존재 + 핵심 강점 섹션 존재 + 권고사항 섹션 존재
    Expected Result: 구조화된 비교 분석 문서
    Evidence: .sisyphus/evidence/task-5-comparison-doc.txt
  ```

  **Commit**: NO (드래프트 문서, Task 7의 입력으로만 사용)

---

- [x] 6. 6개 테마 SKILL.md — 폰트명 제거 + 서술적 타이포그래피 힌트로 전환

  **What to do**:
  - 6개 테마 SKILL.md를 모두 읽어 폰트 패밀리명을 식별하고 대체한다:
    - `plugins/visual-generator/skills/theme-seminar/SKILL.md`
    - `plugins/visual-generator/skills/theme-gov/SKILL.md`
    - `plugins/visual-generator/skills/theme-pitch/SKILL.md`
    - `plugins/visual-generator/skills/theme-whatif/SKILL.md`
    - `plugins/visual-generator/skills/theme-concept/SKILL.md`
    - `plugins/visual-generator/skills/theme-comparison/SKILL.md`
  - 각 테마의 **한글 타이포그래피 가이드** 섹션에서:
    - "Nanum Gothic", "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic" 등 제거
    - 대체: "Heavy-weight Gothic-style Korean sans-serif" + weight 숫자(800+, 700, 500) 유지
  - 각 테마의 **Golden Reference Example** (`<typography>` 태그 내부)에서:
    - 구체적 폰트명을 서술적 지침으로 대체
    - 예: "Font family: Nanum Gothic Bold" → "Heavy-weight Korean Gothic sans-serif at Bold (700)"
  - 각 테마에 **폰트명 유출 경고** 추가:
    - "⚠️ Gemini는 `<typography>` 내 구체적 폰트 패밀리명을 이미지 내 보이는 텍스트로 렌더링합니다. 절대 폰트명을 사용하지 마세요."
  - Task 1의 korean-typography-spec.md 개정 결과와 일관성 확인

  **Must NOT do**:
  - 뫀드 팔레트(색상 코드)를 변경하지 않는다
  - Scene Guide 7요소를 수정하지 않는다
  - Golden Reference의 `<scene>`, `<text_to_render>`, `<layout>` 내용을 변경하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 6개 파일 동시 수정, 테마별 Golden Reference 확인 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9)
  - **Blocks**: Task 7, 10
  - **Blocked By**: Task 1

  **References**:
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md` — seminar 테마 (한글 타이포 가이드 + Golden Ref)
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` — gov 테마
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md` — pitch 테마
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md` — whatif 테마
  - `plugins/visual-generator/skills/theme-concept/SKILL.md` — concept 테마
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md` — comparison 테마

  **Acceptance Criteria**:
  - [ ] 6개 테마 SKILL.md 전체에서 `Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic` Grep 결과 0건
  - [ ] 각 테마에 폰트명 유출 경고문 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 6개 테마 폰트명 완전 제거
    Tool: Grep tool
    Steps:
      1. Grep: "Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic" in plugins/visual-generator/skills/theme-*/SKILL.md
      2. Assert: 0 matches across ALL 6 files
      3. Grep: "폰트 패밀리명" OR "font family name" in each SKILL.md
      4. Assert: ≥ 1 match per file (경고문 존재)
    Expected Result: 폰트명 0건, 경고문 6건
    Evidence: .sisyphus/evidence/task-6-theme-font-cleanup.txt
  ```

  **Commit**: YES
  - Message: `fix(visual-gen): replace font family names with descriptive typography hints across all themes`
  - Files: 6개 theme-*/SKILL.md

- [x] 7. prompt-designer.md — 대폭 강화 (Golden Reference 인라인 + 밀도 강제 + Style Sheet)

  **What to do**:
  - `plugins/visual-generator/agents/prompt-designer.md`를 읽고, Task 5의 비교 분석 결과(`.sisyphus/drafts/v1-v2-comparison.md`)를 참조한다
  - **A. 최소 밀도 강제 룰** 추가:
    - MUST DO에: "본문 슬라이드의 `<text_to_render>`는 최소 8항목, 타이틀 슬라이드는 최소 3항목"
    - 밀도 부족 시 자동 보강 지침: 핵심 메시지를 KPI/수치/세부 항목으로 분해
    - "추상적 선언 1개보다 구체적 데이터 포인트 3개가 낫다" 원칙 명시
  - **B. PhD급 청중 프롬프트 품질 지침** 추가:
    - "공학 박사 수준 청중을 위한 시각자료는 구체적 수치, 방법론 키워드, 성과 지표로 채워져야 한다"
    - "각 슬라이드에 최소 2개의 정량적 지표(%, 건, 억원, 초 등)를 포함"
  - **C. 폰트명 유출 차단 규칙** 추가:
    - MUST NOT DO에: "`<typography>`에 구체적 폰트 패밀리명(Nanum Gothic, Pretendard, Malgun Gothic, Apple SD Gothic Neo)을 사용하지 않는다. Gemini가 이미지 내 보이는 텍스트로 렌더링한다."
    - 대신 서술적 지침: "heavy-weight Gothic-style sans-serif Korean font at 800+ weight"
  - **D. Style Sheet 생성 메커니즘** 추가:
    - Phase 2 신규: "첫 번째 슬라이드 생성 시 Presentation Style Sheet를 함께 생성"
    - Style Sheet 항목: `palette` (primary, secondary, accent, background), `surface_style`, `lighting_direction`, `icon_style`, `glass_effect`, `corner_radius`
    - 이후 슬라이드는 Style Sheet을 읽고 동일한 스타일을 적용
    - Style Sheet는 `{output_path}/style_sheet.md`에 저장
  - **E. 기존 Resources 테이블에 scene-richness-spec.md 참조 강화**:
    - "시각 품질 어드바이저: scene-richness-spec.md의 EXCELLENT 등급을 목표로 한다"
  - **F. 검증 내재화** (prompt-validator에서 이전):
    - Phase 3 품질 검증에 밀도 검증 추가: `<text_to_render>` 항목 수 확인, 폰트명 부재 확인

  **Must NOT do**:
  - 기존 Theme Branch Rules를 삭제하지 않는다
  - 기존 Text Density Rules 테이블(최대 항목 수)을 변경하지 않는다
  - XML-Tag Prompt Structure 5개 태그 구조를 변경하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 복수 참조 파일 통합, 새 메커니즘 설계, v1.11.0 장점 통합 등 높은 복잡도
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 2의 마지막 작업 - Task 6 완료 후)
  - **Parallel Group**: Wave 2 (after Task 6 completes)
  - **Blocks**: Task 10
  - **Blocked By**: Tasks 1, 2, 3, 5, 6

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md` — 현재 전체 파일 (199줄). XML-Tag Prompt Structure, Theme Branch Rules, MUST DO/NOT DO 확인
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:69-117` — Golden Reference Example (seminar hero_number). 텍스트 밀도 벤치마크 (24항목)
  - `.sisyphus/drafts/v1-v2-comparison.md` — Task 5에서 생성된 v1.11.0 강점 분석. prompt-designer 강화의 핵심 입력

  **API/Type References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:205-216` — EXCELLENT 등급 기준 (목표 품질)
  - `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` — 개정된 타이포그래피 지침 (Task 1 결과)

  **Acceptance Criteria**:
  - [ ] prompt-designer.md에 최소 밀도 규칙 명시 ("최소 8항목" 또는 "minimum 8")
  - [ ] prompt-designer.md에 폰트명 금지 규칙 명시
  - [ ] prompt-designer.md에 "Style Sheet" 또는 "style_sheet" 메커니즘 존재
  - [ ] prompt-designer.md에서 `Nanum Gothic|Pretendard` Grep 결과 0건
  - [ ] PhD급 청중 품질 지침 존재 ("박사" OR "PhD" OR "정량적 지표")

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: prompt-designer 강화 항목 전수 확인
    Tool: Grep tool
    Steps:
      1. Grep: "최소 8항목|minimum 8" in prompt-designer.md → ≥ 1건
      2. Grep: "폰트 패밀리명|font family name" in prompt-designer.md MUST NOT DO → ≥ 1건
      3. Grep: "style_sheet|Style Sheet" in prompt-designer.md → ≥ 1건
      4. Grep: "Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic" in prompt-designer.md → 0건
      5. Grep: "박사|정량적 지표|PhD" in prompt-designer.md → ≥ 1건
    Expected Result: 5개 조건 모두 충족
    Failure Indicators: 누락된 강화 항목 존재, 폰트명 잔존, Style Sheet 부재
    Evidence: .sisyphus/evidence/task-7-designer-enhancement.txt

  Scenario: 폰트명 유출 내재화 검증
    Tool: Grep tool
    Steps:
      1. Grep: "Nanum Gothic|Pretendard|Apple SD|Malgun" across ALL plugins/visual-generator/ files
      2. Assert: 0 total matches
    Expected Result: visual-generator 전체에서 폰트명 0건
    Evidence: .sisyphus/evidence/task-7-font-free-total.txt
  ```

  **Commit**: YES
  - Message: `feat(visual-gen): inline golden references, minimum density enforcement, style sheet generation`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`

---

- [x] 8. prompt-validator.md — 불필요 차원 정리 + 핵심 차원 강화 (밀도/폰트/일관성 검증 추가)

  **What to do**:
  - `plugins/visual-generator/agents/prompt-validator.md`를 읽는다
  - 현재 7개 검증 차원을 분석하여 **불필요한 차원을 정리하고, 더 의미있는 차원을 추가**하여 강화한다:
  - **제거 대상 차원** (불필요 또는 prompt-designer에 내재화):
    - v1.11.0 Compliance → 더 이상 유효하지 않음 (v2.x 기반)
    - Korean Text Quality → prompt-designer MUST DO에 통합 (중복 검증)
  - **유지 차원** (기존 7차원 중 유효한 것):
    - Scene Richness — scene-richness-spec.md의 EXCELLENT 등급 기준 검증
    - Content Completeness — slide_plan 대비 누락 검증
    - Logical Completeness — 태그 간 논리적 정합성
    - Cross-Tag Consistency — orphan/ghost 항목 검증
  - **신규 추가 차원** (3개):
    - **Font Name Leakage Detection** — `<typography>` 내 구체적 폰트 패밀리명(Nanum Gothic, Pretendard, Apple SD Gothic Neo, Malgun Gothic) 존재 시 즉시 REJECT
    - **Text Density Validation** — `<text_to_render>` 항목 수가 최소 요건 미달 시 REJECT (본문 슬라이드 ≥ 8, 타이틀 슬라이드 ≥ 3)
    - **Palette Consistency Check** — 동일 프레젠테이션 내 슬라이드들의 `<canvas>` 팔레트 색상 코드 일치 검증 (style_sheet.md 참조)
  - 최종 차원 구성: **7차원** (4개 유지 + 3개 신규 - 2개 제거)
  - REJECT-only 정책 유지: 하나라도 FAIL 시 REJECT + 사유 반환
  - 검증 결과 테이블을 7행으로 재구성

  **Must NOT do**:
  - 에이전트 자체를 삭제하지 않는다 (파이프라인에서 제거 금지)
  - scene-richness-spec.md의 기준을 이 파일 내에 중복 정의하지 않는다 (참조만)
  - PASS/REJECT 외의 결과(WARN 등)를 추가하지 않는다
  - 이미지 렌더링 결과를 검토하는 기능을 추가하지 않는다 (렌더링 전 프롬프트 검증만)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 기존 검증 로직 분석 + 차원 재설계 + 신규 밀도/폰트/팔레트 검증 로직 설계 필요
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: 브라우저 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7)
  - **Blocks**: Task 9
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-validator.md` — 현재 전체 파일. 7개 검증 차원, REJECT/PASS 로직, 결과 테이블 구조 확인
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:205-216` — EXCELLENT 등급 기준 (Scene Richness 차원의 참조 원본)
  - `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — v1.9.0~v1.11.0 검증 규칙 13개 (orphan/ghost 규칙 출처)

  **WHY Each Reference Matters**:
  - prompt-validator.md: 현재 7차원 구조를 이해하고 어떤 차원을 정리하고 어떤 차원을 추가할지 판단
  - scene-richness-spec.md: Scene Richness 차원 검증의 구체적 기준 출처
  - validation-rules-map.md: Cross-Tag Consistency의 orphan/ghost 규칙 원본

  **Acceptance Criteria**:
  - [ ] prompt-validator.md에 검증 차원이 7개 (4개 유지 + 3개 신규)
  - [ ] Font Name Leakage Detection 차원에 4개 폰트명 패턴이 명시됨
  - [ ] Text Density Validation 차원에 최소 밀도 수치(≥8, ≥3) 명시됨
  - [ ] Palette Consistency Check 차원에 style_sheet.md 참조 명시됨
  - [ ] v1.11.0 Compliance, Korean Text Quality 차원이 제거됨
  - [ ] REJECT-only 정책 유지

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 차원 정리 + 강화 확인
    Tool: Grep tool
    Steps:
      1. Grep: "Font.*Leakage|폰트.*유출" in prompt-validator.md → ≥ 1건
      2. Grep: "Text Density|텍스트 밀도|최소.*8" in prompt-validator.md → ≥ 1건
      3. Grep: "Palette Consistency|팔레트 일관" in prompt-validator.md → ≥ 1건
      4. Grep: "v1.11.0 Compliance|Korean Text Quality" in prompt-validator.md → 0건 (제거 확인)
    Expected Result: 신규 3차원 존재, 제거 2차원 0건
    Failure Indicators: 신규 차원 부재, 제거 차원 잔존
    Evidence: .sisyphus/evidence/task-8-validator-strengthen.txt

  Scenario: REJECT-only 정책 유지 확인
    Tool: Grep tool
    Steps:
      1. Grep: "REJECT|PASS" in prompt-validator.md → ≥ 2건
      2. Grep: "WARN|WARNING" in prompt-validator.md → 0건
    Expected Result: REJECT/PASS만 존재, WARN 없음
    Evidence: .sisyphus/evidence/task-8-reject-only.txt
  ```

  **Commit**: YES (groups with 9)
  - Message: `feat(visual-gen): strengthen validator with density, font leakage, palette consistency checks`
  - Files: `plugins/visual-generator/agents/prompt-validator.md`

---

- [x] 9. visual-generate.md — Style Sheet 전달 메커니즘 추가

  **What to do**:
  - `plugins/visual-generator/commands/visual-generate.md`를 읽는다
  - Phase 3 (prompt-designer 호출 단계)에 **Style Sheet 메커니즘**을 추가:
    - **첫 번째 슬라이드 생성 시**:
      - prompt-designer에 `style_sheet_mode: "create"` 파라미터 전달
      - prompt-designer가 첫 슬라이드의 palette, surface_style, lighting, icon_style 등을 `{output_path}/style_sheet.md`에 저장
    - **두 번째 슬라이드부터**:
      - prompt-designer에 `style_sheet_mode: "follow"` + `style_sheet_path: "{output_path}/style_sheet.md"` 전달
      - prompt-designer가 Style Sheet를 읽고 동일 스타일 적용
  - Phase 3의 슬라이드 반복 루프에서 **첫 슬라이드 여부를 판별**하는 조건 추가:
    - `is_first_slide: true/false` 또는 `slide_index: 0/1/2...`
  - **prompt-designer subagent 호출 시 전달 파라미터 추가**:
    - 기존: slide_plan, concepts, theme, layout
    - 추가: `style_sheet_mode`, `style_sheet_path` (첫 슬라이드가 아닌 경우)

  **Must NOT do**:
  - 다른 Phase(1, 2, 4, 5)를 변경하지 않는다
  - renderer-agent 호출 방식을 변경하지 않는다
  - prompt-validator 호출을 제거하지 않는다 (강화된 7차원 검증 유지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일에 파라미터 추가 + 조건 분기 추가, 구조 변경 최소
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (after Task 8)
  - **Blocks**: Task 10
  - **Blocked By**: Task 8

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md` — 현재 전체 파일 (68줄). Phase 3 구조, subagent 호출 방식 확인
  - `plugins/visual-generator/agents/prompt-designer.md` — Task 7에서 추가될 Style Sheet 생성 로직 참조 (파라미터 인터페이스 일치 확인)

  **WHY Each Reference Matters**:
  - visual-generate.md: Phase 3 루프 구조를 이해하고 style_sheet_mode 파라미터 삽입 위치 결정
  - prompt-designer.md: Task 7에서 설계된 Style Sheet 인터페이스와 파라미터명 일치 보장

  **Acceptance Criteria**:
  - [ ] visual-generate.md에 `style_sheet` 또는 `style_sheet_mode` 언급 존재
  - [ ] 첫 번째 슬라이드 판별 조건 존재 (`is_first_slide` 또는 `slide_index`)
  - [ ] Phase 3의 prompt-designer 호출에 style_sheet 관련 파라미터 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: Style Sheet 메커니즘 존재 확인
    Tool: Grep tool
    Steps:
      1. Grep: "style_sheet" in visual-generate.md → ≥ 2건 (create + follow)
      2. Grep: "first_slide|slide_index|is_first" in visual-generate.md → ≥ 1건
      3. Grep: "style_sheet_mode" in visual-generate.md → ≥ 1건
    Expected Result: Style Sheet 관련 지시 존재, 첫 슬라이드 판별 존재
    Failure Indicators: style_sheet 미언급, 첫 슬라이드 분기 부재
    Evidence: .sisyphus/evidence/task-9-style-sheet-orchestration.txt
  ```

  **Commit**: YES (groups with 8)
  - Message: `refactor(visual-gen): streamline validator to 3 core dimensions, add style sheet orchestration`
  - Files: `plugins/visual-generator/commands/visual-generate.md`

---

- [x] 10. 통합 테스트 — 실제 프롬프트 생성 + 구조적 검증 (렌더링 전까지)

  **What to do**:
  - Tasks 1-9 완료 후 개선 효과를 검증한다
  - **테스트 입력 준비**:
    - 기존 `visual-output-v3/` 생성 시 사용한 것과 동일한 주제 문서를 사용하거나, 공학 발표용 테스트 문서를 간단히 작성 (5+ 슬라이드 구성)
    - 테마: `seminar` (Golden Reference가 가장 상세한 테마)
  - **프롬프트 생성 실행 (단계별 수동 호출)**:
    - visual-generate 커맨드를 직접 호출하지 않고, 각 에이전트를 순차적으로 호출하여 renderer-agent 전까지만 실행:
      1. **content-organizer** 호출: 테스트 문서 + seminar 테마 → concepts.md + slide_plan.md 생성
      2. **content-reviewer** 호출: concepts.md + slide_plan.md 검토 → PASS/REJECT
      3. **prompt-designer** 호출: slide_plan.md + concepts.md + seminar 테마 → 5+ 슬라이드 프롬프트 생성 (첫 슬라이드에서 style_sheet.md 생성)
      4. **prompt-validator** 호출: 각 프롬프트 검증 → PASS/REJECT
      5. **renderer-agent는 호출하지 않는다** (Gemini 렌더링 없음)
  - **구조적 검증** (각 생성된 프롬프트 파일에 대해):
    - `<text_to_render>` 항목 수 카운트: Grep tool로 본문 슬라이드 ≥ 8, 타이틀 슬라이드 ≥ 3 확인
    - `<typography>` 내 폰트 패밀리명: Grep tool로 `Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic` → 0건 확인
    - `<scene>` 문장 수: Read tool로 문장 수 ≥ 5 확인
    - 슬라이드 간 palette 색상 코드 비교: Grep tool로 각 `<canvas>` 내 색상 코드 추출 후 style_sheet.md와 대조
  - **결과 기록**: 모든 검증 결과를 `.sisyphus/evidence/task-10-integration-test.md`에 저장

  **Must NOT do**:
  - 플러그인 파일을 수정하지 않는다 (검증만 수행)
  - Gemini API 렌더링을 실행하지 않는다 (프롬프트 구조 검증만)
  - renderer-agent를 호출하지 않는다
  - 5장 미만의 슬라이드로 테스트하지 않는다

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 4개 에이전트 순차 호출 + 다차원 구조적 검증의 복합 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential)
  - **Blocks**: Task 11, F1-F4
  - **Blocked By**: Tasks 6, 7, 9

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md` — Task 9에서 개정된 오케스트레이터 (각 Phase의 에이전트 호출 방식 참조)
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — Task 2에서 추가된 밀도 기준 참조

  **External References**:
  - 기존 테스트 출력: `C:\Users\BaekdongCha\Documents\git-obsidian\001_KIMM_PARA\Project\020_2026타운홀미팅\working\visual-output-v3\prompts\` — v2.1.1 프롬프트 (비교 기준선)

  **WHY Each Reference Matters**:
  - visual-generate.md: 각 Phase의 에이전트 호출 방식과 파라미터를 참조하여 단계별 수동 호출 실행
  - scene-richness-spec.md: 밀도 기준 숫자 참조 (≥8, ≥3)
  - v3 기존 프롬프트: 개선 전후 비교를 위한 기준선

  **Acceptance Criteria**:
  - [ ] 5개 이상 슬라이드 프롬프트 생성 완료
  - [ ] 모든 본문 슬라이드의 `<text_to_render>` ≥ 8항목
  - [ ] 전체 프롬프트에서 폰트 패밀리명 0건
  - [ ] 슬라이드 간 팔레트 색상 코드 일치 (style_sheet.md 존재)
  - [ ] `<scene>` 문장 수 ≥ 5

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 프롬프트 밀도 검증 (Happy Path)
    Tool: Grep tool + Read tool (도구 기반, CLI 명령 아님)
    Preconditions: 단계별 에이전트 호출 완료, 프롬프트 파일 5+ 개 존재
    Steps:
      1. Glob tool로 생성된 프롬프트 파일 목록 확인
      2. 각 프롬프트 파일을 Read tool로 읽고 `<text_to_render>` 내부 항목 수 카운트
      3. Grep tool: "Nanum Gothic|Pretendard|Apple SD Gothic Neo|Malgun Gothic" → 0건 확인
    Expected Result: 밀도 ≥ 8 (body), 폰트명 0건
    Failure Indicators: body 슬라이드에 8항목 미만, 폰트명 1건+
    Evidence: .sisyphus/evidence/task-10-density-check.txt

  Scenario: 슬라이드 간 팔레트 일관성 검증
    Tool: Read tool + Grep tool (도구 기반)
    Preconditions: style_sheet.md 생성됨
    Steps:
      1. Read tool로 style_sheet.md에서 palette 색상 코드 추출
      2. Grep tool로 각 프롬프트의 `<canvas>` 내 색상 코드 확인
      3. Assert: 모든 슬라이드의 primary/secondary/accent 색상 코드 일치
    Expected Result: 전 슬라이드 동일 팔레트
    Failure Indicators: 슬라이드 간 색상 코드 불일치
    Evidence: .sisyphus/evidence/task-10-palette-consistency.txt
  ```

  **Commit**: NO (검증만 수행, 파일 변경 없음)

---

- [x] 11. 버전 업데이트 — plugin.json + marketplace.json → 2.2.0 + AGENTS.md 동기화

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json`의 `"version"` 필드를 `"2.2.0"`으로 변경
  - `.claude-plugin/marketplace.json`에서 visual-generator 항목의 `"version"` 필드를 `"2.2.0"`으로 변경
  - `AGENTS.md` 업데이트:
    - **Generated** 날짜를 현재 날짜로 변경
    - **Version** 을 2.7.0으로 변경 (MINOR: 기존 기능 개선)
    - visual-generator 관련 설명에 개선 사항 반영:
      - "XML-tag v2.2.0, 폰트명 유출 차단, 최소 텍스트 밀도 강제, Style Sheet 기반 슬라이드 일관성" 등
  - `README.md` 변경 이력에 새 항목 추가:
    - `| 2.5.0 | YYYY-MM-DD | visual-generator v2.2.0: 폰트명 유출 차단, 최소 텍스트 밀도(body≥8) 강제, Style Sheet 기반 슬라이드 일관성, prompt-validator 강화(밀도/폰트/팔레트 검증 추가) |`

  **Must NOT do**:
  - AGENTS.md의 다른 플러그인 섹션을 변경하지 않는다
  - marketplace.json의 다른 플러그인 항목을 변경하지 않는다
  - MAJOR 버전(3.0.0)으로 올리지 않는다 (하위 호환성 유지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 4개 파일의 버전 번호/날짜/설명만 변경하는 단순 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 10)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 10

  **References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — 현재 version 필드 확인
  - `.claude-plugin/marketplace.json` — visual-generator 항목의 version 필드 확인
  - `AGENTS.md` — Generated 날짜, Version, visual-generator 설명 위치 확인
  - `README.md` — 변경 이력 테이블 위치 확인

  **WHY Each Reference Matters**:
  - plugin.json + marketplace.json: 버전 동기화 필수 (AGENTS.md 규칙)
  - AGENTS.md: 프로젝트 단일 진실 공급원 — 반드시 최신화
  - README.md: 공개 변경 이력 — 사용자가 변경사항 추적

  **Acceptance Criteria**:
  - [ ] plugin.json version = "2.2.0"
  - [ ] marketplace.json visual-generator version = "2.2.0"
  - [ ] AGENTS.md Generated 날짜 = 현재 날짜
  - [ ] AGENTS.md Version ≥ 2.7.0
  - [ ] README.md 변경 이력에 v2.2.0 항목 존재

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 버전 동기화 확인
    Tool: Grep tool
    Steps:
      1. Grep: "2.2.0" in plugins/visual-generator/.claude-plugin/plugin.json → ≥ 1건
      2. Grep: "2.2.0" in .claude-plugin/marketplace.json → ≥ 1건 (visual-generator 항목)
      3. Grep: "2.7.0" OR higher in AGENTS.md → ≥ 1건
      4. Grep: "v2.2.0" in README.md 변경 이력 → ≥ 1건
    Expected Result: 4개 파일 모두 올바른 버전 표시
    Failure Indicators: 버전 불일치, 업데이트 누락
    Evidence: .sisyphus/evidence/task-11-version-sync.txt
  ```

  **Commit**: YES
  - Message: `chore(visual-gen): bump version to 2.2.0, update AGENTS.md`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, grep for pattern). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Review all changed .md files for: forbidden phrases (scene-richness-spec.md), font family names leakage, pt/px units, markdown inside XML tags, placeholder text. Grep all `plugins/visual-generator/` files for "Nanum Gothic ExtraBold", "Pretendard ExtraBold", "Malgun Gothic Bold", "Apple SD Gothic Neo".
  Output: `Files [N clean/N issues] | Font Leakage [CLEAN/N occurrences] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Run visual-generate command on a test document with 5+ slides (do NOT run renderer-agent / Gemini rendering). Capture all generated prompts. Verify: (1) text_to_render ≥ 8 items on body slides, (2) no font family names in any tag, (3) consistent palette across slides via style_sheet.md, (4) scene ≥ 5 sentences. Compare prompt density improvement vs v2.1.1 baseline.
  Output: `Prompts [N/N pass] | Density [N/N ≥ 8] | Font-Free [N/N] | Consistency [PASS/FAIL] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual file diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance: no new themes, no script changes, no model changes. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Creep [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| Commit | Files | Message |
|--------|-------|---------|
| 1 | korean-typography-spec.md, scene-richness-spec.md | `fix(visual-gen): remove literal font names from typography spec and golden refs` |
| 2 | content-organizer.md, content-reviewer.md | `feat(visual-gen): enforce minimum text density in upstream pipeline` |
| 3 | 6× theme-*/SKILL.md | `fix(visual-gen): replace font family names with descriptive typography hints across all themes` |
| 4 | prompt-designer.md | `feat(visual-gen): inline golden references, minimum density enforcement, style sheet generation` |
| 5 | prompt-validator.md, visual-generate.md | `feat(visual-gen): strengthen validator with density/font/palette checks, add style sheet orchestration` |
| 6 | plugin.json, marketplace.json, AGENTS.md | `chore(visual-gen): bump version to 2.2.0, update AGENTS.md` |

---

## Success Criteria

### Verification Commands

> **주의**: 아래 검증은 CLI 명령이 아닌 **도구 기반**(Grep tool, Read tool)으로 수행합니다.
> Windows cmd.exe 환경에서 Unix 명령(`grep -r`, `wc`, `diff`)은 사용하지 않습니다.

```
# 폰트명 유출 검증 (0건이어야 함)
Grep tool: pattern="Nanum Gothic ExtraBold|Pretendard ExtraBold|Malgun Gothic Bold|Apple SD Gothic Neo Bold"
  path=plugins/visual-generator/  → Expected: 0 matches

# 최소 밀도 요건 존재 확인
Grep tool: pattern="min_render_text|최소 8|≥ 8"
  path=plugins/visual-generator/agents/content-organizer.md  → Expected: ≥1 match

# prompt-validator 강화 확인
Grep tool: pattern="Font.*Leakage|Text Density|Palette Consistency"
  path=plugins/visual-generator/agents/prompt-validator.md  → Expected: ≥3 matches
```

### Final Checklist
- [ ] 모든 "Must Have" present
- [ ] 모든 "Must NOT Have" absent
- [ ] 폰트 패밀리명 0건 (Grep 검증)
- [ ] 본문 슬라이드 텍스트 밀도 ≥ 8항목
- [ ] 슬라이드 간 팔레트 일관성 보장
- [ ] plugin.json + marketplace.json 버전 동기화 (2.2.0)
- [ ] AGENTS.md 최신화
