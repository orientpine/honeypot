# visual-generator Korean Text Hallucination 방지 개선

## TL;DR

> **Quick Summary**: Gemini의 한글 텍스트 hallucination을 3중 방어로 차단한다 — (1) 프롬프트 생성 시 Korean Safety Rules 6조 적용, (2) API 호출 시 SYSTEM_INSTRUCTION에 anti-hallucination 지시 삽입, (3) 생성 후 5차원 품질 평가로 한글 결함 감지. 빈 공간은 시각적 요소(아이콘, 일러스트)로 채워 Gemini의 space-filling 행동을 구조적으로 차단한다.
> 
> **Deliverables**:
> - prompt-designer.md에 Korean Text Safety Rules 6조 + 빈 공간 시각 충전 규칙 추가
> - generate_slide_images.py의 품질 평가를 3차원 평균 → 5차원 개별 임계값 체계로 교체
> - renderer-agent.md에 한글 hallucination 검증 항목 2개 추가
> - prompt-validator.md에 8번째 검증 차원 (한글 환각 위험 검출) 추가
> - scene-richness-spec.md에 빈 공간 방지 가이드라인 추가
> - slide-renderer/SKILL.md에 5차원 품질 평가 문서 추가
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 5 → Task 6 → Task 7

---

## Context

### Original Request
Gemini 한글 텍스트 Hallucination 결함 보고서에 기반하여 `plugins/visual-generator/`를 개선한다. 15개 정부 R&D 제안서 이미지 중 4개에서 한글 깨짐/hallucination이 발생. 사용자는 시각적 요소(아이콘, 일러스트, 모델 렌더링, 예시 화면)가 풍부한 방향을 선호한다.

### Interview Summary
**Key Discussions**:
- 결함 보고서의 모든 제안을 그대로 적용하지 않고, 적절한 것만 필터링하여 적용
- 빈 공간을 채우는 방식으로 박스 분해(Strategy A)보다 아이콘/일러스트 충전(Strategy B)을 채택 — 사용자의 시각 풍부 선호와 일치
- 3차원 산술 평균의 "평균 함정" 문제를 개별 임계값으로 해결

**Research Findings**:
- `prompt-designer.md` (587줄): Korean Safety Rules 없음, 빈 공간 방지 규칙 없음
- `renderer-agent.md` (341줄): 12개 검증 항목, 한글 hallucination 관련 없음
- `generate_slide_images.py` (392줄): 3차원 평가 (korean/layout/color), 단순 평균 ≥ 7.0
- `prompt-validator.md` (149줄): 7차원 검증, Korean hallucination 미포함
- `scene-richness-spec.md` (376줄): 네거티브 스페이스 가이드만 존재, 빈 공간 방지 가이드 없음
- `slide-renderer/SKILL.md` (76줄): 기본 실행 가이드만 존재
- **CRITICAL 발견**: prompt-validator가 오케스트레이터 파이프라인에 포함되어 있지 않음 → renderer-agent에도 한글 검증 추가 필요

### Metis Review
**Identified Gaps** (addressed):
- prompt-validator가 오케스트레이터에 미포함 → renderer-agent에 한글 hallucination 검증 추가 (in-pipeline 보장)
- 5차원 단순 평균도 여전히 masking 가능 → 한글 차원별 최소 임계값(≥ 5.0) 도입 (veto 방식)
- SYSTEM_INSTRUCTION 미수정 → generate_slide_images.py의 SYSTEM_INSTRUCTION에 anti-hallucination 지시 추가 (inference-time 방어)
- concept 테마 면제 필요 → 모든 한글 규칙에 concept 테마 예외 조항 추가
- 정확한 5개 평가 차원 미정의 → korean_text_readability, korean_hallucination_detection, content_reference_accuracy, layout_suitability, color_palette_compliance로 확정

---

## Work Objectives

### Core Objective
Gemini의 한글 hallucination을 **3중 방어 체계**로 차단한다: 프롬프트 생성 시(upstream), API 호출 시(inference), 생성 후(downstream).

### Concrete Deliverables
- `plugins/visual-generator/agents/prompt-designer.md` — Korean Text Safety Rules 6조 섹션 신설
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` — 5차원 품질 평가 + SYSTEM_INSTRUCTION 업데이트
- `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — 빈 공간 방지 가이드라인 섹션 신설
- `plugins/visual-generator/agents/prompt-validator.md` — 8번째 차원 (한글 환각 위험 검출) 추가
- `plugins/visual-generator/agents/renderer-agent.md` — 검증 항목 #15, #16 추가
- `plugins/visual-generator/skills/slide-renderer/SKILL.md` — 5차원 품질 평가 문서 섹션 추가
- `plugins/visual-generator/.claude-plugin/plugin.json` — 버전 3.0.0 → 3.1.0
- `.claude-plugin/marketplace.json` — visual-generator 항목 버전 3.1.0으로 동기화

### Definition of Done
- [ ] 모든 6개 파일 수정 완료
- [ ] `grep "Korean.*Safety\|한글.*안전" prompt-designer.md` → 1건 이상 매치
- [ ] `grep "korean_hallucination_detection" generate_slide_images.py` → 1건 이상 매치
- [ ] `grep "KOREAN_MIN_THRESHOLD\|korean.*5\.0" generate_slide_images.py` → 1건 이상 매치
- [ ] `python -c "import ast; ast.parse(open('generate_slide_images.py').read())"` → 구문 오류 없음
- [ ] plugin.json과 marketplace.json 모두 "3.1.0" 표시

### Must Have
- Korean Safety Rules 6조가 prompt-designer.md에 명시적 섹션으로 존재
- SYSTEM_INSTRUCTION에 anti-hallucination 지시 포함
- 5차원 품질 평가에서 한글 차원 최소 임계값 5.0 적용 (veto 방식)
- concept 테마 면제 조항이 모든 한글 규칙에 존재
- 빈 공간 처리 가이드라인이 scene-richness-spec.md에 존재

### Must NOT Have (Guardrails)
- `visual-generate.md` (오케스트레이터) 수정 금지
- `theme-*/SKILL.md` (테마별 스킬) 수정 금지
- 박스 분해(Strategy A) 도입 금지 — 사용자 시각 선호와 충돌
- `--verify-only` 모드 추가 금지 — 별도 관심사
- 재시도 전략 로직 변경 금지 — 현행 유지
- 플러그인 소스 파일 신규 생성 금지 — `plugins/` 및 `.claude-plugin/` 내 기존 파일만 수정 (단, `.sisyphus/evidence/` 경로의 QA 증빙 파일은 예외 — 검증 프로토콜에 의해 자동 생성됨)
- CONTENT에 문장형 텍스트 렌더링 강제 — 기존 "개조식 명사구" 규칙 유지

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (에이전트/프롬프트 시스템, 유닛 테스트 프레임워크 없음)
- **Automated tests**: NO
- **Framework**: none
- **QA Policy**: Agent-executed QA scenarios — Grep/Read/AST 기반 구조 검증

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Agent/Skill .md 파일**: Use Grep — 필수 키워드/패턴 존재 확인, 금지 패턴 부재 확인
- **Python 스크립트**: Use Bash (python -c "import ast; ...") — 구문 검증 + 키워드 확인
- **버전 파일**: Use Grep — 버전 번호 일치 확인

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 독립 수정 3건, MAX PARALLEL):
├── Task 1: Korean Safety Rules 6조 in prompt-designer.md [writing]
├── Task 2: Space-filling prevention in scene-richness-spec.md [writing]
└── Task 3: 5-dimension quality + SYSTEM_INSTRUCTION in generate_slide_images.py [deep]

Wave 2 (After Wave 1 — 의존성 있는 검증 계층 2건):
├── Task 4: 8th dimension in prompt-validator.md (depends: T1) [writing]
└── Task 5: Validation checks #15, #16 in renderer-agent.md (depends: T1, T2) [writing]

Wave 3 (After Wave 2 — 문서화 + 마무리):
├── Task 6: Quality evaluation reference in slide-renderer/SKILL.md (depends: T3, T5) [writing]
└── Task 7: Version bump 3.0.0 → 3.1.0 (depends: T6) [quick]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 5 → Task 6 → Task 7 → F1-F4
Parallel Speedup: ~40% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|:----:|
| T1: Korean Safety Rules | — | T4, T5 | 1 |
| T2: Space-filling prevention | — | T5 | 1 |
| T3: 5-dim quality evaluation | — | T6 | 1 |
| T4: prompt-validator 8th dim | T1 | — | 2 |
| T5: renderer-agent checks | T1, T2 | T6 | 2 |
| T6: slide-renderer SKILL.md | T3, T5 | T7 | 3 |
| T7: Version bump | T6 | — | 3 |

### Agent Dispatch Summary

- **Wave 1**: **3** — T1 → `writing`, T2 → `writing`, T3 → `deep`
- **Wave 2**: **2** — T4 → `writing`, T5 → `writing`
- **Wave 3**: **2** — T6 → `writing`, T7 → `quick` + `git-master`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Korean Safety Rules 6조를 prompt-designer.md에 추가

  **What to do**:
  - `## Text Density Rules` 섹션 뒤 (line 430 근처)에 새로운 `## Korean Text Safety Rules` 섹션을 추가한다
  - 6개 규칙을 명시한다:
    1. **CONTENT-ONLY 원칙**: 이미지에 렌더링되는 모든 한글 텍스트는 CONTENT 블록에 명시적으로 나열되어야 한다. CONTENT에 없는 한글은 이미지에 나타나서는 안 된다.
    2. **라벨 길이 제한**: CONTENT의 각 value는 최대 15자로 제한 (8자 이하 권장, 16자 이상 분할 필수)
    3. **빈 공간 시각 충전**: Scene Description에서 모든 주요 박스/영역의 빈 공간 처리를 명시해야 한다. 텍스트가 없는 영역은 아이소메트릭 아이콘, 미니 일러스트, 장비 실루엣, 데이터 시각화 요소, 또는 테마에 맞는 장식 도형으로 채운다. "정돈되어 배치", "키워드 포함", "설명 텍스트" 등 암시적 텍스트 생성 유도 표현 금지.
    4. **분야/카테고리 헤더 명시**: 이미지에 렌더링될 모든 한글은 CONTENT에 있어야 한다. Gemini 추론에 맡기면 유사 자형 혼동(난↔산) 발생.
    5. **Scene Description anti-hallucination 필수 문구**: 모든 프롬프트의 Scene Description 마지막에 다음 문구를 반드시 포함: "CRITICAL: Only render the exact text strings listed in the CONTENT block below. Do NOT generate, infer, or add any additional Korean text beyond what is explicitly written in CONTENT. If a box or area has no CONTENT text assigned, fill it with icons or illustrations — never with AI-generated Korean sentences."
    6. **FORBIDDEN ELEMENTS 필수 항목**: 모든 프롬프트의 FORBIDDEN ELEMENTS에 다음 항목을 반드시 포함: "AI가 자체 생성한 한글 설명문: CONTENT 블록에 명시되지 않은 어떤 한글 텍스트도 이미지 내부에 렌더링하는 것을 절대 금지"
  - Scene Description Rules 섹션 (line 174-195)에 추가: "Scene Description must describe ONLY visual composition and spatial arrangement. Never include CONTENT block values or renderable Korean text strings in Scene Description."
  - concept 테마 면제 조항 추가: "concept 테마는 텍스트 항목 0개이므로 Korean Text Safety Rules를 적용하지 않는다."

  **Must NOT do**:
  - `## INSTRUCTION` 블록의 구조 변경 금지
  - 기존 CONTENT 블록 key:value 형식 규칙 변경 금지
  - 기존 FORBIDDEN ELEMENTS 15개 항목 삭제 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 마크다운 에이전트 파일에 정밀한 규칙 삽입 — 기존 구조와 충돌 없이 통합 필요
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 프론트엔드 작업 아님

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:409-430` — Text Density Rules 섹션. 새 섹션은 이 뒤에 위치해야 함. 같은 포맷(규칙 표, 설명 문단)으로 작성.
  - `plugins/visual-generator/agents/prompt-designer.md:174-195` — Scene Description Rules 섹션. 여기에 CONTENT 값 포함 금지 규칙을 추가해야 함.
  - `plugins/visual-generator/agents/prompt-designer.md:276-296` — FORBIDDEN ELEMENTS 템플릿. 17번째 항목으로 AI 생성 한글 금지를 추가.
  - `plugins/visual-generator/agents/prompt-designer.md:344-358` — concept Theme Rules. concept 면제 패턴을 여기서 참조.

  **External References**:
  - 결함 보고서 §6.6 — Korean Safety Rules 6조 원문 (프롬프트에 포함된 보고서 참조)
  - 결함 보고서 §4.1 — Scene Description 필수 지시문 원문
  - 결함 보고서 §4.3 — CONTENT 블록 설계 원칙 (라벨 길이, 키워드 원칙)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Korean Safety Rules 섹션 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 1 완료
    Steps:
      1. grep -c "Korean Text Safety Rules" plugins/visual-generator/agents/prompt-designer.md
      2. grep -c "CONTENT-ONLY\|CONTENT.*ONLY\|CONTENT에 없는" plugins/visual-generator/agents/prompt-designer.md
      3. grep -c "15자\|라벨 길이" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: 각각 ≥ 1
    Failure Indicators: 어떤 grep에서도 0 반환
    Evidence: .sisyphus/evidence/task-1-korean-safety-rules.txt

  Scenario: concept 테마 면제 조항 확인
    Tool: Bash (grep)
    Preconditions: Task 1 완료
    Steps:
      1. grep -c "concept.*적용하지\|concept.*exempt\|concept.*면제" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-1-concept-exemption.txt

  Scenario: Scene Description에 CONTENT 값 포함 금지 규칙 확인
    Tool: Bash (grep)
    Preconditions: Task 1 완료
    Steps:
      1. grep -c "Scene Description must describe ONLY\|Scene Description.*CONTENT.*금지\|renderable.*text.*Scene" plugins/visual-generator/agents/prompt-designer.md
    Expected Result: ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-1-scene-desc-rule.txt
  ```

  **Commit**: YES (groups with 2, 3)
  - Message: `feat(visual-generator): add Korean hallucination prevention rules and 5D quality evaluation`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`
  - Pre-commit: N/A (마크다운)

- [x] 2. 빈 공간 방지 가이드라인을 scene-richness-spec.md에 추가

  **What to do**:
  - Implementation Checklist 뒤 (line 360 근처)에 새로운 `## 11. Space-Filling Prevention (Visual Enrichment)` 섹션을 추가한다
  - 포함 내용:
    1. **Visual Enrichment Strategy**: 박스/패널 내부에 텍스트 배치 후 빈 공간이 40% 이상이면, 아이소메트릭 아이콘, 미니 일러스트, 장비 실루엣, 데이터 시각화 요소, 또는 테마에 맞는 장식 도형으로 채운다. 빈 공간을 추가 텍스트로 채우지 않는다.
    2. **Theme-Specific Visual Elements 가이드**: gov=단색 플랫 아이콘(채워진 원+흰색 심볼), 번호 배지, 표 요소 | seminar=아이소메트릭 3D icons, 프로스티드 글래스 카드, mini props | concept=추상 기하 도형, 흐르는 리본, 연결 노드 | whatif=홀로그래픽 HUD 요소, 발광 패널 | pitch=프로스티드 글래스 카드, 거대 숫자 강조 | comparison=대비 분할 아이콘, 상태 변화 시각화
    3. **Forbidden Space-Filling Patterns**: 빈 공간에 추가 한글 텍스트 삽입 금지, CONTENT 값 반복 금지, meta-label이나 placeholder 텍스트 추가 금지
    4. **Icon Density Guide**: 패널당 1-3개 플랫 아이콘, 주요 섹션당 1개 isometric 요소, 전체 슬라이드당 최대 8개 시각 요소
    5. **Scene Description Integration Pattern**: 빈 공간에 시각 요소를 채울 때 Scene Description에서 어떻게 기술하는지 예시 제공 — "블록 내부에는 '{라벨}' 텍스트 아래에 {아이콘 설명} 아이콘이 배치된다. 아이콘 외의 빈 공간에는 텍스트를 렌더링하지 않는다."
  - Negative Space 섹션 (line 170-200)에 보완 추가: "When negative space exceeds 50% within a content panel, apply visual enrichment (icons, illustrations, silhouettes) rather than additional text to prevent Korean text hallucination."
  - Implementation Checklist (line 349-360)에 체크 항목 추가: "- [ ] Space-filling prevention applied (no empty panels >40% without visual elements)"

  **Must NOT do**:
  - 기존 네거티브 스페이스 30-40% 가이드라인 삭제 금지
  - 기존 Golden Examples 수정 금지
  - Quality Grading Criteria 기준 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 참조 문서에 가이드라인 섹션 추가 — 기존 구조와 일관성 유지 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:170-200` — Negative Space 섹션. 여기에 50% 초과 시 visual enrichment 규칙을 추가.
  - `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md:349-360` — Implementation Checklist. space-filling prevention 체크 항목 추가.
  - `plugins/visual-generator/skills/theme-gov/SKILL.md:169-183` — Rendering Style 표. 테마별 시각 요소 스타일 참조 (gov=단색 플랫 아이콘 등).

  **External References**:
  - 결함 보고서 §6.5 — 빈 공간 방지 전략 (Strategy A/B, 아이콘 유형 가이드)
  - 결함 보고서 §4.4 — Scene Description 작성 가이드라인 (충전 전/후 비교)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Space-Filling Prevention 섹션 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 2 완료
    Steps:
      1. grep -c "Space-Filling Prevention\|Visual Enrichment" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. grep -c "isometric\|아이소메트릭\|mini.*illustration\|미니.*일러스트\|silhouette\|실루엣" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
    Expected Result: 각각 ≥ 1
    Failure Indicators: 어떤 grep에서도 0 반환
    Evidence: .sisyphus/evidence/task-2-space-filling.txt

  Scenario: Theme-specific visual elements 가이드 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 2 완료
    Steps:
      1. grep -c "gov.*플랫\|gov.*flat" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
      2. grep -c "seminar.*isometric\|seminar.*아이소메트릭" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
    Expected Result: 각각 ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-2-theme-visuals.txt
  ```

  **Commit**: YES (groups with 1, 3)
  - Message: `feat(visual-generator): add Korean hallucination prevention rules and 5D quality evaluation`
  - Files: `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`

- [x] 3. 품질 평가를 5차원 개별 임계값 체계로 업그레이드 + SYSTEM_INSTRUCTION 업데이트

  **What to do**:
  - **SYSTEM_INSTRUCTION 업데이트** (line 34-47): 기존 내용 유지 + 다음 추가:
    ```
    Korean Text Hallucination Prevention: Never generate gibberish or randomly formed Korean characters to fill empty space in the image. If a content area appears empty, fill it with flat icons, isometric illustrations, or decorative visual elements rather than fabricated Korean text. Every Korean character rendered in the final image must correspond to a specific text item from the prompt's CONTENT section. Do not infer, translate, or generate any Korean text beyond what is explicitly provided in the prompt.
    ```
  - **evaluate_image_quality()** (line 190-268) 수정:
    1. 평가 프롬프트 (line 195-208)를 5차원으로 교체:
       - `korean_text_readability` (0-10): 한글 텍스트의 선명도, 자모 결합 정확성, 가독성
       - `korean_hallucination_detection` (0-10): CONTENT에 없는 한글이 이미지에 존재하는지 (10=깨끗, 0=심각한 hallucination)
       - `content_reference_accuracy` (0-10): CONTENT에 명시된 텍스트가 이미지에 정확히 렌더링되었는지
       - `layout_suitability` (0-10): 레이아웃 구성 적합성
       - `color_palette_compliance` (0-10): 지정 팔레트 준수 여부
    2. 평가 프롬프트에 CONTENT 텍스트 목록을 함께 전달하도록 수정 (대조 검증 기반)
    3. 스코어링 로직 수정: 단순 평균에서 **tiered evaluation**으로 변경
       - `KOREAN_MIN_THRESHOLD = 5.0` 상수 추가
       - 한글 관련 2개 차원 (korean_text_readability, korean_hallucination_detection)이 각각 5.0 미만이면 평균과 무관하게 자동 FAIL
       - 전체 평균은 5차원 평균으로 계산, QUALITY_THRESHOLD (7.0) 유지
       - passed = (avg >= QUALITY_THRESHOLD) AND (korean_text >= KOREAN_MIN) AND (korean_hallu >= KOREAN_MIN)
    4. criteria dict (line 245-253)를 5개 필드로 확장
    5. 콘솔 출력 포맷 (line 158-168) 업데이트: 5개 점수 모두 표시
    6. concept 테마 감지: 프롬프트에 "concept" 테마 마커가 있거나 "zero text rendering" 포함 시 한글 차원을 10.0으로 설정 (면제)
  - **generate_image()** (line 72-187): evaluate_image_quality 호출 시 프롬프트 원문(prompt_text)을 함께 전달하도록 시그니처 수정

  **Must NOT do**:
  - `MODEL_NAME`, API 클라이언트 초기화, 파일 I/O 로직 변경 금지
  - `QUALITY_THRESHOLD` 값 변경 금지 (7.0 유지)
  - `MAX_QUALITY_RETRIES` 변경 금지
  - 재시도 로직 변경 금지
  - 새 CLI 인자 추가 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Python 스크립트의 핵심 로직 수정 — 기존 함수 시그니처 변경, 새 상수 추가, JSON 파싱 로직 확장 등 주의 깊은 구현 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:34-47` — 현재 SYSTEM_INSTRUCTION. 여기에 Korean Text Hallucination Prevention 단락을 추가.
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:190-268` — 현재 evaluate_image_quality() 함수. 3차원 → 5차원으로 리팩토링 대상.
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:48-49` — QUALITY_THRESHOLD, MAX_QUALITY_RETRIES 상수. KOREAN_MIN_THRESHOLD를 여기에 추가.
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:134-187` — generate_image() 함수의 quality 평가 호출부. evaluate_image_quality에 prompt_text 전달 추가.
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:157-169` — 콘솔 출력 포맷. 5개 점수 표시로 변경.

  **External References**:
  - 결함 보고서 §3.3 — 품질 평가 실패 원인 분석 (평균 함정, 자기 평가 맹점)
  - 결함 보고서 §4.5-A — 렌더링 스크립트 개선 제안 (차원별 최소 임계값 + 가중 평균)
  - 결함 보고서 §6.2 — 품질 평가 프롬프트 템플릿 개선안

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Python 구문 검증
    Tool: Bash (python)
    Preconditions: Task 3 완료
    Steps:
      1. python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('SYNTAX OK')"
    Expected Result: "SYNTAX OK" 출력
    Failure Indicators: SyntaxError 발생
    Evidence: .sisyphus/evidence/task-3-syntax-check.txt

  Scenario: 5차원 평가 차원 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 3 완료
    Steps:
      1. grep -c "korean_hallucination_detection" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
      2. grep -c "content_reference_accuracy" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
      3. grep -c "KOREAN_MIN_THRESHOLD" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: 각각 ≥ 1
    Failure Indicators: 어떤 grep에서도 0 반환
    Evidence: .sisyphus/evidence/task-3-five-dimensions.txt

  Scenario: SYSTEM_INSTRUCTION anti-hallucination 확인
    Tool: Bash (grep)
    Preconditions: Task 3 완료
    Steps:
      1. grep -c "Korean Text Hallucination Prevention\|fabricated Korean\|gibberish.*Korean" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-3-system-instruction.txt

  Scenario: Veto 로직 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 3 완료
    Steps:
      1. grep -c "KOREAN_MIN_THRESHOLD\|korean.*min\|veto\|auto.*fail\|자동.*FAIL" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-3-veto-logic.txt
  ```

  **Commit**: YES (groups with 1, 2)
  - Message: `feat(visual-generator): add Korean hallucination prevention rules and 5D quality evaluation`
  - Files: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`
  - Pre-commit: `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read())"`

- [x] 4. prompt-validator.md에 8번째 검증 차원 (한글 환각 위험 검출) 추가

  **What to do**:
  - Dimension 7 (Palette Consistency Check) 뒤 (line 98 이후)에 새로운 차원을 추가:
    ```
    ### 8) Korean Hallucination Risk Detection (한글 환각 위험 검출)
    ```
  - 검증 대상: `## CONTENT` values + `### Scene Description`
  - 검증 항목 4가지:
    1. Scene Description에 CONTENT value 문자열이 직접 포함되어 있는지 (cross-contamination 검출)
    2. CONTENT value가 15자를 초과하는 한글 텍스트인지 (hallucination 위험 증가)
    3. Scene Description에 anti-hallucination negative prompting이 포함되어 있는지 ("No gibberish Korean" 또는 동등 표현)
    4. Content Placement에 빈 공간 시각 충전 지시가 있는지 (아이콘/일러스트 참조 존재)
  - REJECT 기준: 4가지 중 하나라도 실패
  - concept 테마 면제: "concept theme은 이 차원을 SKIP한다."
  - 전체 판정 (line 121) 업데이트: "all 7 pass" → "all 8 pass"
  - Workflow Phase 2 (line 112-122) 업데이트: Dimension 8 추가

  **Must NOT do**:
  - 기존 7개 차원의 기준/로직 변경 금지
  - REJECT-only 정책 변경 금지 (자동 수정 금지)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 기존 7차원 검증 패턴을 정확히 따라 8번째 차원을 추가해야 함
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: None
  - **Blocked By**: Task 1 (Korean Safety Rules 정의 필요)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-validator.md:92-98` — Dimension 7 (Palette Consistency). 동일한 형식으로 Dimension 8을 추가.
  - `plugins/visual-generator/agents/prompt-validator.md:112-122` — Workflow Phase 2. Dimension 8을 추가.
  - `plugins/visual-generator/agents/prompt-validator.md:121` — "all 7 pass" → "all 8 pass"로 변경.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 8번째 차원 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 4 완료
    Steps:
      1. grep -c "Korean Hallucination Risk Detection\|한글 환각 위험 검출" plugins/visual-generator/agents/prompt-validator.md
      2. grep -c "all 8 pass\|8개.*pass\|8.*차원" plugins/visual-generator/agents/prompt-validator.md
      3. grep -c "concept.*SKIP\|concept.*면제" plugins/visual-generator/agents/prompt-validator.md
    Expected Result: 각각 ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-4-eighth-dimension.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(visual-generator): add Korean hallucination validation to prompt-validator and renderer-agent`
  - Files: `plugins/visual-generator/agents/prompt-validator.md`

- [x] 5. renderer-agent.md에 한글 hallucination 검증 항목 #15, #16 추가

  **What to do**:
  - Validation Checklist 테이블 (line 153-166)에 2개 항목 추가:
    ```
    | 15 | Anti-hallucination Negative Prompt | Scene Description에 anti-hallucination negative prompt 포함 확인 ("Only render the exact text strings listed in the CONTENT block" 또는 동등 표현) | 미포함 |
    | 16 | CONTENT-Scene Cross-contamination | Scene Description에 CONTENT value가 직접 포함되어 있는지 확인 | CONTENT value 발견 |
    ```
  - Workflow Phase 2 (line 67-97)에 Step 2-7, Step 2-8 추가:
    - Step 2-7: Anti-hallucination directive 검증 — `grep "Only render.*exact.*CONTENT\|CONTENT block\|gibberish Korean" prompt.md`
    - Step 2-8: Cross-contamination 검증 — CONTENT 블록에서 value 추출 후 Scene Description에 해당 value가 직접 포함되어 있는지 확인
  - concept 테마 면제: checks 15-16은 concept 테마에서 SKIP

  **Must NOT do**:
  - 기존 14개(실제 12개) 검증 항목 변경 금지
  - Phase 3 (이미지 렌더링) 로직 변경 금지
  - MUST DO / MUST NOT DO 섹션 삭제 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 기존 검증 체크리스트 패턴을 정확히 따라 새 항목을 추가해야 함
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/renderer-agent.md:153-166` — Validation Checklist 테이블. 동일한 형식(#, 검증 항목, 검증 방법, FAIL 조건)으로 #15, #16 추가.
  - `plugins/visual-generator/agents/renderer-agent.md:67-97` — Workflow Phase 2 Steps. Step 2-7, 2-8을 동일 형식으로 추가.
  - `plugins/visual-generator/agents/renderer-agent.md:178-206` — 검증 명령어 예시. 새 항목에 대응하는 bash 검증 예시 추가.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 검증 항목 #15, #16 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 5 완료
    Steps:
      1. grep -c "Anti-hallucination Negative Prompt\|anti.*hallucination" plugins/visual-generator/agents/renderer-agent.md
      2. grep -c "Cross-contamination\|cross.*contamination" plugins/visual-generator/agents/renderer-agent.md
      3. grep "| 15 \|| 16 " plugins/visual-generator/agents/renderer-agent.md | wc -l
    Expected Result: 첫 두 grep 각각 ≥ 1, 세 번째 ≥ 2
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-5-renderer-checks.txt
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(visual-generator): add Korean hallucination validation to prompt-validator and renderer-agent`
  - Files: `plugins/visual-generator/agents/renderer-agent.md`

- [x] 6. slide-renderer/SKILL.md에 5차원 품질 평가 문서 추가

  **What to do**:
  - 현재 76줄인 SKILL.md를 확장하여 2개 섹션 추가:
    1. `## Quality Evaluation Criteria` 섹션:
       - 5차원 평가 체계 문서화: korean_text_readability, korean_hallucination_detection, content_reference_accuracy, layout_suitability, color_palette_compliance
       - 각 차원 설명 및 0-10 스코어 기준
       - Tiered evaluation 로직: 평균 ≥ 7.0 + 한글 차원 각각 ≥ 5.0
       - concept 테마 면제 설명
    2. `## Korean Text Safety` 섹션:
       - prompt-designer.md의 Korean Safety Rules 참조
       - SYSTEM_INSTRUCTION의 anti-hallucination 지시 참조
       - 빈 공간 시각 충전 전략 요약
  - 기존 "스크립트 출력 해석" 테이블 업데이트: 5차원 점수 출력 포맷 반영

  **Must NOT do**:
  - 기존 "스크립트 참조 및 실행" 섹션 변경 금지
  - 기존 환경 요구사항 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 문서 작성 위주 — 기존 스킬 파일에 참조 문서 섹션 추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 7)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 3, 5

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/SKILL.md:1-76` — 전체 파일. 기존 구조 유지하며 새 섹션 추가.
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:48-49` — QUALITY_THRESHOLD, KOREAN_MIN_THRESHOLD 상수값 참조.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Quality Evaluation 섹션 존재 확인
    Tool: Bash (grep)
    Preconditions: Task 6 완료
    Steps:
      1. grep -c "Quality Evaluation Criteria" plugins/visual-generator/skills/slide-renderer/SKILL.md
      2. grep -c "korean_hallucination_detection\|content_reference_accuracy" plugins/visual-generator/skills/slide-renderer/SKILL.md
      3. grep -c "Korean Text Safety" plugins/visual-generator/skills/slide-renderer/SKILL.md
    Expected Result: 각각 ≥ 1
    Failure Indicators: 0 반환
    Evidence: .sisyphus/evidence/task-6-skill-docs.txt
  ```

  **Commit**: YES (groups with 7)
  - Message: `docs(visual-generator): update SKILL.md quality reference and bump version to 3.1.0`
  - Files: `plugins/visual-generator/skills/slide-renderer/SKILL.md`

- [x] 7. 버전 범프 3.0.0 → 3.1.0 및 레지스트리 동기화

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json`: `"version": "3.0.0"` → `"version": "3.1.0"`
  - `.claude-plugin/marketplace.json`: visual-generator 항목의 `"version": "3.0.0"` → `"version": "3.1.0"`
  - 두 파일의 버전이 정확히 일치하는지 교차 검증

  **Must NOT do**:
  - marketplace.json의 다른 플러그인 항목 변경 금지
  - plugin.json의 name, description, author 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 2개 파일에서 각 1줄 수정
  - **Skills**: [`git-master`]
    - `git-master`: 커밋 시 올바른 패턴 적용

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential after Task 6)
  - **Blocks**: None
  - **Blocked By**: Task 6

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json:3` — `"version": "3.0.0"` 변경 대상.
  - `.claude-plugin/marketplace.json` — visual-generator 항목의 version 필드 변경 대상.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 버전 일치 확인
    Tool: Bash (grep)
    Preconditions: Task 7 완료
    Steps:
      1. grep '"version"' plugins/visual-generator/.claude-plugin/plugin.json
      2. grep -A5 '"visual-generator"' .claude-plugin/marketplace.json | grep "version"
    Expected Result: 두 결과 모두 "3.1.0" 포함
    Failure Indicators: "3.0.0" 또는 불일치
    Evidence: .sisyphus/evidence/task-7-version-bump.txt
  ```

  **Commit**: YES (groups with 6)
  - Message: `docs(visual-generator): update SKILL.md quality reference and bump version to 3.1.0`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`

  **What to verify**: Every "Must Have" is implemented, every "Must NOT Have" is absent.

  ```
  Scenario: Must Have — Korean Safety Rules
    Tool: Bash (grep)
    Steps:
      1. grep -c "Korean Text Safety Rules" plugins/visual-generator/agents/prompt-designer.md
      2. grep -c "CONTENT-ONLY\|CONTENT.*ONLY" plugins/visual-generator/agents/prompt-designer.md
      3. grep -c "Korean Text Hallucination Prevention" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
      4. grep -c "korean_hallucination_detection" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
      5. grep -c "KOREAN_MIN_THRESHOLD" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
      6. grep -c "concept.*exempt\|concept.*적용하지\|concept.*SKIP" plugins/visual-generator/agents/prompt-designer.md
      7. grep -c "Space-Filling Prevention" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
    Expected: All ≥ 1
    Evidence: .sisyphus/evidence/F1-must-have.txt

  Scenario: Must NOT Have — Scope boundary compliance
    Tool: Bash (git diff)
    Steps:
      1. git diff --name-only HEAD | grep -c "visual-generate.md" (expected: 0)
      2. git diff --name-only HEAD | grep -c "theme-gov/SKILL.md\|theme-seminar/SKILL.md\|theme-concept/SKILL.md\|theme-whatif/SKILL.md\|theme-pitch/SKILL.md\|theme-comparison/SKILL.md" (expected: 0)
      3. ls .sisyphus/evidence/ | wc -l (expected: ≥ 7)
    Expected: Steps 1-2 return 0, Step 3 ≥ 7
    Evidence: .sisyphus/evidence/F1-must-not-have.txt
  ```

  Output: `Must Have [7/7] | Must NOT Have [2/2] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`

  **What to verify**: Python syntax valid, markdown structure intact, YAML frontmatter parseable.

  ```
  Scenario: Python syntax validation
    Tool: Bash (python)
    Steps:
      1. python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('SYNTAX OK')"
    Expected: "SYNTAX OK"
    Evidence: .sisyphus/evidence/F2-python-syntax.txt

  Scenario: Markdown heading structure validation
    Tool: Bash (grep)
    Steps:
      1. grep -c "^## " plugins/visual-generator/agents/prompt-designer.md (expected: consistent with pre-change count + new sections)
      2. grep -c "^### " plugins/visual-generator/agents/prompt-validator.md (expected: ≥ 8, one per dimension)
      3. grep -c "^## " plugins/visual-generator/skills/slide-renderer/SKILL.md (expected: ≥ 4, including new sections)
    Expected: All pass
    Evidence: .sisyphus/evidence/F2-markdown-structure.txt

  Scenario: YAML frontmatter validation
    Tool: Bash (grep)
    Steps:
      1. head -6 plugins/visual-generator/agents/prompt-designer.md | grep "^---"
      2. head -6 plugins/visual-generator/agents/renderer-agent.md | grep "^---"
      3. head -6 plugins/visual-generator/agents/prompt-validator.md | grep "^---"
    Expected: Each returns 2 lines (opening and closing ---)
    Evidence: .sisyphus/evidence/F2-frontmatter.txt
  ```

  Output: `Syntax [PASS/FAIL] | Markdown [PASS/FAIL] | Frontmatter [PASS/FAIL] | VERDICT`

- [x] F3. **Cross-Reference Consistency QA** — `unspecified-high`

  **What to verify**: Rules, dimensions, and exemptions are consistent across all modified files.

  ```
  Scenario: Korean Safety Rules cross-reference
    Tool: Bash (grep)
    Steps:
      1. grep -c "CONTENT-ONLY\|CONTENT.*only.*render" plugins/visual-generator/agents/prompt-designer.md (rule defined)
      2. grep -c "CONTENT.*Scene.*contamination\|Cross-contamination" plugins/visual-generator/agents/renderer-agent.md (rule enforced)
      3. grep -c "Scene Description.*CONTENT\|cross.*contamination" plugins/visual-generator/agents/prompt-validator.md (rule validated)
    Expected: All ≥ 1 — same rule appears in all 3 files
    Evidence: .sisyphus/evidence/F3-rule-cross-ref.txt

  Scenario: 5-dimension consistency
    Tool: Bash (grep)
    Steps:
      1. grep -c "korean_hallucination_detection" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py (implemented)
      2. grep -c "korean_hallucination\|hallucination.*detect" plugins/visual-generator/skills/slide-renderer/SKILL.md (documented)
    Expected: All ≥ 1
    Evidence: .sisyphus/evidence/F3-dimension-cross-ref.txt

  Scenario: concept theme exemption consistency
    Tool: Bash (grep)
    Steps:
      1. grep -c "concept.*exempt\|concept.*적용하지\|concept.*SKIP" plugins/visual-generator/agents/prompt-designer.md
      2. grep -c "concept.*exempt\|concept.*SKIP\|concept.*면제" plugins/visual-generator/agents/prompt-validator.md
      3. grep -c "concept" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected: All ≥ 1
    Evidence: .sisyphus/evidence/F3-exemption-cross-ref.txt
  ```

  Output: `Rules [3/3 consistent] | Dimensions [2/2] | Exemptions [3/3] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`

  **What to verify**: Only specified files were changed, no scope creep.

  ```
  Scenario: Changed files match plan scope
    Tool: Bash (git)
    Steps:
      1. git diff --name-only HEAD
      2. Verify output contains ONLY these files (plus .sisyphus/ evidence):
         - plugins/visual-generator/agents/prompt-designer.md
         - plugins/visual-generator/agents/renderer-agent.md
         - plugins/visual-generator/agents/prompt-validator.md
         - plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
         - plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md
         - plugins/visual-generator/skills/slide-renderer/SKILL.md
         - plugins/visual-generator/.claude-plugin/plugin.json
         - .claude-plugin/marketplace.json
    Expected: No files outside this list (except .sisyphus/)
    Evidence: .sisyphus/evidence/F4-scope-files.txt

  Scenario: Version consistency
    Tool: Bash (grep)
    Steps:
      1. grep '"version"' plugins/visual-generator/.claude-plugin/plugin.json
      2. grep -A5 '"visual-generator"' .claude-plugin/marketplace.json | grep "version"
    Expected: Both show "3.1.0"
    Evidence: .sisyphus/evidence/F4-version-check.txt
  ```

  Output: `Files [8/8 expected] | Scope [CLEAN/N unexpected] | Version [MATCH/MISMATCH] | VERDICT`

---

## Commit Strategy

- **Commit 1** (Wave 1): `feat(visual-generator): add Korean hallucination prevention rules and 5D quality evaluation`
  - Files: prompt-designer.md, scene-richness-spec.md, generate_slide_images.py
  - Pre-commit: `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read())"`

- **Commit 2** (Wave 2): `feat(visual-generator): add Korean hallucination validation to prompt-validator and renderer-agent`
  - Files: prompt-validator.md, renderer-agent.md

- **Commit 3** (Wave 3): `docs(visual-generator): update SKILL.md quality reference and bump version to 3.1.0`
  - Files: slide-renderer/SKILL.md, plugin.json, marketplace.json

---

## Success Criteria

### Verification Commands
```bash
# Korean Safety Rules 존재
grep -c "Korean.*Safety\|한글.*안전\|Korean Text Safety" plugins/visual-generator/agents/prompt-designer.md  # Expected: ≥ 1

# SYSTEM_INSTRUCTION anti-hallucination
grep -c "Korean Text Hallucination Prevention\|fabricated Korean\|gibberish" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py  # Expected: ≥ 1

# 5차원 평가 차원
grep -c "korean_hallucination_detection\|content_reference_accuracy" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py  # Expected: ≥ 2

# 한글 최소 임계값
grep -c "KOREAN_MIN_THRESHOLD\|korean.*min.*5" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py  # Expected: ≥ 1

# Python 구문 검증
python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('OK')"  # Expected: OK

# concept 테마 면제
grep -c "concept.*exempt\|concept.*적용하지\|concept.*SKIP" plugins/visual-generator/agents/prompt-designer.md  # Expected: ≥ 1

# prompt-validator 8번째 차원
grep -c "Korean Hallucination\|한글 환각" plugins/visual-generator/agents/prompt-validator.md  # Expected: ≥ 1

# renderer-agent 새 검증 항목
grep -c "| 15 \|| 16 " plugins/visual-generator/agents/renderer-agent.md  # Expected: ≥ 2

# Space-filling prevention
grep -c "Space-Filling Prevention\|Visual Enrichment\|빈 공간 방지" plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md  # Expected: ≥ 1

# Version bump
grep '"3.1.0"' plugins/visual-generator/.claude-plugin/plugin.json  # Expected: match
```

### Final Checklist
- [ ] Korean Safety Rules 6조 present in prompt-designer.md
- [ ] SYSTEM_INSTRUCTION updated in generate_slide_images.py
- [ ] 5-dimension evaluation with per-Korean-dimension minimum ≥ 5.0
- [ ] Space-filling prevention guidelines in scene-richness-spec.md
- [ ] prompt-validator 8th dimension added
- [ ] renderer-agent checks #15, #16 added
- [ ] slide-renderer/SKILL.md quality section added
- [ ] Version 3.1.0 in plugin.json and marketplace.json
- [ ] concept theme exemption in all Korean rules
- [ ] visual-generate.md NOT modified
- [ ] theme-*/SKILL.md NOT modified
- [ ] No new plugin source files created (`.sisyphus/evidence/` QA files exempt)
