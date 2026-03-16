# Must-Render Registry + Variation Space: 테마별 필수 렌더링 요소 명시화

## TL;DR

> **Quick Summary**: 4개 테마(seminar, whatif, pitch, comparison)에 `## 필수 렌더링 요소` 섹션을 추가하여 암묵적이던 제목/핵심 요소 렌더링을 명시화한다. "WHAT은 고정, HOW는 선택지" 패턴으로 창의성과 명시성을 동시에 달성한다.
> 
> **Deliverables**:
> - 4개 테마 SKILL.md에 `## 필수 렌더링 요소 (Must-Render Elements)` 섹션 추가
> - prompt-designer.md에 title 필수 CONTENT key 규칙 추가
> - visual-generator 버전 3.1.0 → 3.2.0
> - marketplace metadata 2.4.0 → 3.5.0 (README 트랙 동기화, drift 해소)
> - README.md 3.4.0 → 3.5.0
> 
> - AGENTS.md 버전 동기화 규칙 수정 (marketplace metadata ↔ README Version 일치 의무화)
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1-5 (parallel) → Task 6+7 (parallel) → F1+F2

---

## Context

### Original Request
사용자가 theme-gov와 theme-seminar의 제목 렌더링 규칙을 비교 분석한 결과, gov만 Rendering Style에서 "배너 안에 문서 제목을 배치한다"고 명시하고 나머지 4개 테마는 Golden Reference에 title key가 있지만 명시적 렌더링 규칙이 없는 gap을 발견. 모든 암묵적 요소를 명시화하되 창의성을 고정하지 않는 접근법을 요청.

### Interview Summary
**Key Discussions**:
- 완전한 명세를 원하되 천편일률적 결과물이 나오면 안 됨
- "창의성을 명시적으로 실행" — 규칙이 창의성을 활성화해야지 고정시키면 안 됨
- prompt-designer.md에 title 필수 key 규칙 추가 → 확인
- 다양한 디자인 variation을 가지도록 할 것

**Research Findings**:
- gov: 상단 배너에 title 배치 → Rendering Style L176에 명시 ✅
- seminar: title/subtitle/lead_message 존재 → 명시 규칙 없음 ❌
- whatif: title/subtitle 존재 → 명시 규칙 없음 ❌
- pitch: `main_number`가 primary, `card_title`이 보조 → title key 자체가 다른 이름 ❌
- comparison: `before_title`/`after_title` 쌍 → 슬라이드 레벨 title 없음 ❌

### Metis Review
**Identified Gaps** (addressed):
- pitch 테마에 `title:` key가 없음 → hero_statement(main_number + main_description)를 필수 요소로 등록
- comparison 테마에 단일 title이 없음 → before_title + after_title 쌍을 필수 요소로 등록
- Golden Reference 코드 블록 수정 금지 → Registry는 기존 Golden Reference를 기술하는 것이지 새 키를 추가하는 게 아님
- subtitle/lead_message는 필수 목록에 미포함 → 권장(recommended) 표기로 분류
- Output Structure Mapping의 Title Area와 중복 방지 → Must-Render는 WHAT/WHY, Output Structure는 HOW(4-block 구조 내 형식)

---

## Work Objectives

### Core Objective
4개 테마 SKILL.md에 `## 필수 렌더링 요소` 섹션을 추가하여 암묵적 렌더링 규칙을 명시화하고, prompt-designer.md에 title 필수 key 규칙을 추가한다.

### Concrete Deliverables
- `theme-seminar/SKILL.md`: 필수 렌더링 요소 섹션 (title + subtitle + lead_message 변형)
- `theme-whatif/SKILL.md`: 필수 렌더링 요소 섹션 (title + subtitle 변형)
- `theme-pitch/SKILL.md`: 필수 렌더링 요소 섹션 (hero_statement + card_title 변형)
- `theme-comparison/SKILL.md`: 필수 렌더링 요소 섹션 (before_title + after_title 변형)
- `prompt-designer.md`: CONTENT Block Generation에 title 필수 key 규칙
- `plugin.json` + `marketplace.json`: 3.1.0 → 3.2.0

### Definition of Done
- [ ] 4개 테마 SKILL.md에 `## 필수 렌더링 요소` 섹션 존재
- [ ] 각 테마의 필수 요소가 해당 Golden Reference CONTENT 블록과 1:1 대응
- [ ] prompt-designer.md에 title 필수 규칙 + concept 면제 포함
- [ ] visual-generator 3.2.0 + marketplace/README 3.5.0 동기화
- [ ] AGENTS.md 버전 동기화 규칙 수정 완료

### Must Have
- 각 테마에 최소 3개 이상의 배치 변형(Variation) 옵션
- 변형이 해당 테마의 시각 정체성을 반영할 것
- concept 면제 명시
- 단일 테이블 포맷 (요소 | 역할 | 필수 | 배치 변형) 4개 테마 동일 구조
- "사용자가 명시적으로 제목 생략을 요청한 경우 존중" escape clause

### Must NOT Have (Guardrails)
- Golden Reference Example 코드 블록 수정 금지
- prompt-validator.md, renderer-agent.md, validation-rules-map.md 수정 금지
- CONTENT key 이름 강제 금지 (pitch의 main_number, comparison의 before_title 등 테마 고유 이름 존중)
- subtitle/lead_message를 "필수"로 분류 금지 (권장으로만)
- theme-gov/SKILL.md, theme-concept/SKILL.md 외 테마 SKILL 수정 금지
- visual-generate.md 수정 금지

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: NO (markdown documentation files)
- **Automated tests**: None
- **Framework**: N/A
- **QA**: grep-based verification + structural consistency checks

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 4 theme SKILL.md changes + prompt-designer, ALL PARALLEL):
├── Task 1: theme-seminar Must-Render Registry [quick]
├── Task 2: theme-whatif Must-Render Registry [quick]
├── Task 3: theme-pitch Must-Render Registry [quick]
├── Task 4: theme-comparison Must-Render Registry [quick]
└── Task 5: prompt-designer.md title 필수 key 규칙 [quick]

Wave 2 (After Wave 1 — version bump + docs, ALL PARALLEL):
├── Task 6: Version bump + marketplace/README 동기화 [quick]
└── Task 7: AGENTS.md 버전 동기화 규칙 수정 [quick]

Wave FINAL (After ALL tasks — 2 parallel reviews):
├── Task F1: Cross-theme consistency audit (oracle)
└── Task F2: Scope fidelity + Golden Reference alignment check (deep)

Critical Path: Task 1-5 (parallel) → Task 6+7 (parallel) → F1+F2 (parallel)
Parallel Speedup: Wave 1 runs all 5 tasks simultaneously
Max Concurrent: 5 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1-5 | None | 6, 7 |
| 6 | 1-5 | F1, F2 |
| 7 | 1-5 | F1, F2 |
| F1 | 6, 7 | — |
| F2 | 6, 7 | — |

### Agent Dispatch Summary

- **Wave 1**: 5 tasks — T1-T5 → `quick`
- **Wave 2**: 2 tasks — T6 → `quick`, T7 → `quick`
- **FINAL**: 2 tasks — F1 → `oracle`, F2 → `deep`

---

## TODOs

- [x] 1. theme-seminar/SKILL.md에 필수 렌더링 요소 섹션 추가

  **What to do**:
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md`를 읽는다
  - `## 렌더링 스타일 (Rendering Style)` 섹션 직후, `### 아이소메트릭 3D + 2D 레이아웃 하이브리드 구분` 직전에 새 섹션을 삽입한다
  - 아래 내용을 삽입:

  ```markdown
  ## 필수 렌더링 요소 (Must-Render Elements)

  이 테마에서 이미지에 반드시 렌더링되어야 하는 요소 목록이다.
  prompt-designer는 아래 요소를 CONTENT에 반드시 포함하고, Content Placement에서 배치를 지시해야 한다.

  > **escape clause**: 사용자가 명시적으로 제목 생략을 요청한 경우, prompt-designer는 이를 존중한다.

  | 요소 | 역할 | 필수 | 배치 변형 (슬라이드 컨텍스트에 맞게 하나를 선택) |
  |------|------|:----:|--------------------------------------------------|
  | title | 슬라이드 주제의 시각적 앵커 | ✅ | ① 좌상단 대형 매거진 헤드라인 — 잡지 표지처럼 시선을 끌며 3D 아이콘과 나란히 배치 ② 상단 풀와이드 텍스트 밴드 — 넓게 펼쳐진 제목 아래로 콘텐츠가 전개 ③ 대형 3D 아이콘 사이 삽입형 — 텍스트와 아이콘이 얽히는 에디토리얼 구성 ④ 중앙 상단 대형 볼드 — 좌우 대칭의 클래식 헤드라인 배치 |
  | subtitle | 맥락 보조 (행사명, 연도 등) | 권장 | ① title 직하단 보조색 중간 크기 ② title 우측 하단 소형 정렬 ③ 프로스티드 글래스 배지 안에 배치 |
  | lead_message | 핵심 방향 한 문장 | 권장 | ① title 하단 보조 문장으로 자연스럽게 연결 ② 별도 소프트 라운딩 배너에 독립 배치 ③ 슬라이드 하단 각주 영역에 강조색으로 배치 |
  ```

  **Must NOT do**:
  - Golden Reference Example 코드 블록 수정 금지
  - 기존 Rendering Style 테이블 내용 변경 금지
  - 다른 섹션 순서 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:164-178` — 렌더링 스타일 테이블 (삽입 위치 직전)
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:181` — 아이소메트릭 3D + 2D 구분 (삽입 위치 직후)
  - `plugins/visual-generator/skills/theme-seminar/SKILL.md:409-411` — Golden Reference title/subtitle/lead_message keys
  - `plugins/visual-generator/skills/theme-gov/SKILL.md:176` — gov의 명시적 제목 규칙 (참조 패턴)

  **Acceptance Criteria**:
  - [ ] `grep -c "필수 렌더링 요소" plugins/visual-generator/skills/theme-seminar/SKILL.md` ≥ 1
  - [ ] `grep -c "배치 변형" plugins/visual-generator/skills/theme-seminar/SKILL.md` ≥ 1
  - [ ] `grep -c "매거진 헤드라인\|에디토리얼\|3D 아이콘 사이" plugins/visual-generator/skills/theme-seminar/SKILL.md` ≥ 2

  **Commit**: YES (groups with Tasks 2, 3, 4)
  - Message: `feat(visual-generator): add Must-Render Registry to 4 theme skills`

- [x] 2. theme-whatif/SKILL.md에 필수 렌더링 요소 섹션 추가

  **What to do**:
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md`를 읽는다
  - `## 렌더링 스타일 (Rendering Style)` 테이블 직후 `---` 구분선과 `## 콘텐츠 표현 규칙` 사이에 새 섹션을 삽입한다
  - 아래 내용을 삽입:

  ```markdown
  ## 필수 렌더링 요소 (Must-Render Elements)

  이 테마에서 이미지에 반드시 렌더링되어야 하는 요소 목록이다.
  prompt-designer는 아래 요소를 CONTENT에 반드시 포함하고, Content Placement에서 배치를 지시해야 한다.

  > **escape clause**: 사용자가 명시적으로 제목 생략을 요청한 경우, prompt-designer는 이를 존중한다.

  | 요소 | 역할 | 필수 | 배치 변형 (슬라이드 컨텍스트에 맞게 하나를 선택) |
  |------|------|:----:|--------------------------------------------------|
  | title | 비전 선언문 — 미래가 이미 실현된 톤의 단정문 | ✅ | ① 상단 중앙 선언형 대형 — HUD 느낌의 글로우 효과와 함께 ② 장면 상단 홀로그래픽 오버레이 — 배경 장면 위에 떠 있는 미래 UI 텍스트 ③ 좌상단 대형 + 장면이 우측으로 전개 — 시네마틱 타이틀 카드 구성 ④ 화면 중앙 풀블리드 — 장면 전체를 관통하는 대형 선언문 |
  | subtitle | 현재 상태/부제 | 권장 | ① title 직하단 밝은 톤 중간 크기 ② 글래스모피즘 패널 내부 상단에 배치 ③ 장면 속 대시보드 UI 요소로 자연스럽게 통합 |
  ```

  **Must NOT do**:
  - Golden Reference Example 코드 블록 수정 금지
  - 기존 Rendering Style 테이블 내용 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md:164-178` — 렌더링 스타일 테이블
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md:181` — 콘텐츠 표현 규칙 (삽입 위치 직후)
  - `plugins/visual-generator/skills/theme-whatif/SKILL.md:369-370` — Golden Reference title/subtitle keys

  **Acceptance Criteria**:
  - [ ] `grep -c "필수 렌더링 요소" plugins/visual-generator/skills/theme-whatif/SKILL.md` ≥ 1
  - [ ] `grep -c "선언문\|HUD\|홀로그래픽\|시네마틱" plugins/visual-generator/skills/theme-whatif/SKILL.md` ≥ 2

  **Commit**: YES (groups with Tasks 1, 3, 4)

- [x] 3. theme-pitch/SKILL.md에 필수 렌더링 요소 섹션 추가

  **What to do**:
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md`를 읽는다
  - `## 렌더링 스타일 (Rendering Style)` 테이블 직후 `---` 구분선과 `### 다크 테마 시인성 규칙` 사이에 새 섹션을 삽입한다
  - pitch 테마는 숫자 > 제목 위계이므로 `hero_statement`가 primary, `title`이 secondary이다
  - 아래 내용을 삽입:

  ```markdown
  ## 필수 렌더링 요소 (Must-Render Elements)

  이 테마에서 이미지에 반드시 렌더링되어야 하는 요소 목록이다.
  prompt-designer는 아래 요소를 CONTENT에 반드시 포함하고, Content Placement에서 배치를 지시해야 한다.

  > **escape clause**: 사용자가 명시적으로 제목 생략을 요청한 경우, prompt-designer는 이를 존중한다.
  > **pitch 위계**: 이 테마에서 숫자(hero_statement)가 제목보다 크다. 제목은 숫자를 보조하는 맥락 역할.

  | 요소 | 역할 | 필수 | 배치 변형 (슬라이드 컨텍스트에 맞게 하나를 선택) |
  |------|------|:----:|--------------------------------------------------|
  | hero_statement | 핵심 임팩트 숫자/선언 — 화면의 30%+ 차지 | ✅ | ① 중앙 대형 스노우 화이트 — 어두운 배경 위 극강의 대비 ② 좌상단 대형 + Z-패턴 우하단 CTA — 시선 흐름 최적화 ③ 상단 중앙 대형 + 하단 프로스티드 글래스 카드에 보조 정보 ④ 우측 대형 + 좌측에 맥락 텍스트 — 비대칭 임팩트 구성 |
  | title | 맥락 보조 — hero_statement를 설명하는 한 줄 | ✅ | ① hero 직하단 세미볼드 중간 크기 (#F5F5F7) ② hero 상단 소형 레이블 — 숫자의 카테고리 표시 ③ 프로스티드 글래스 카드 상단 헤더 — 카드 내부 맥락 제공 |
  ```

  **Must NOT do**:
  - Golden Reference Example 코드 블록 수정 금지
  - hero_metric 이름을 title로 강제 변경 금지
  - 숫자 > 제목 위계 뒤집기 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:125-139` — 렌더링 스타일 테이블
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:142` — 다크 테마 시인성 규칙 (삽입 위치 직후)
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:136` — 타이포그래피: "숫자가 가장 크다. 핵심 메트릭이 화면의 30% 이상"
  - `plugins/visual-generator/skills/theme-pitch/SKILL.md:293-300` — Golden Reference main_number/card_title keys

  **Acceptance Criteria**:
  - [ ] `grep -c "필수 렌더링 요소" plugins/visual-generator/skills/theme-pitch/SKILL.md` ≥ 1
  - [ ] `grep -c "hero_statement\|핵심 임팩트\|숫자.*제목보다" plugins/visual-generator/skills/theme-pitch/SKILL.md` ≥ 2
  - [ ] `grep -c "프로스티드 글래스\|Z-패턴\|스노우 화이트" plugins/visual-generator/skills/theme-pitch/SKILL.md` ≥ 2

  **Commit**: YES (groups with Tasks 1, 2, 4)

- [x] 4. theme-comparison/SKILL.md에 필수 렌더링 요소 섹션 추가

  **What to do**:
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md`를 읽는다
  - `## 렌더링 스타일 (Rendering Style)` 테이블 직후 `---` 구분선과 `### 이미지 중심 원칙` 사이에 새 섹션을 삽입한다
  - comparison 테마는 좌/우 분할 구조이므로 before_title + after_title 쌍이 필수이다
  - 아래 내용을 삽입:

  ```markdown
  ## 필수 렌더링 요소 (Must-Render Elements)

  이 테마에서 이미지에 반드시 렌더링되어야 하는 요소 목록이다.
  prompt-designer는 아래 요소를 CONTENT에 반드시 포함하고, Content Placement에서 배치를 지시해야 한다.

  > **escape clause**: 사용자가 명시적으로 제목 생략을 요청한 경우, prompt-designer는 이를 존중한다.
  > **dual-title 구조**: 이 테마에는 슬라이드 레벨 단일 제목이 없다. 좌측(Before)과 우측(After) 각각의 패널 제목이 필수이다.

  | 요소 | 역할 | 필수 | 배치 변형 (슬라이드 컨텍스트에 맞게 하나를 선택) |
  |------|------|:----:|--------------------------------------------------|
  | before_title | Before 패널의 상태 식별자 | ✅ | ① 좌측 오버레이 상단 볼드 흰색 — 이미지 위 반투명 그라데이션 위에 배치 ② 좌측 오버레이 중앙 대형 — 패널 중심에 존재감 있게 ③ 좌측 상단 배지형 — 라운드 배경 안에 짧은 라벨로 배치 |
  | after_title | After 패널의 상태 식별자 | ✅ | ① 우측 오버레이 상단 볼드 흰색 — before_title과 대칭 배치 ② 우측 오버레이 중앙 대형 — 패널 중심에 존재감 있게 ③ 우측 상단 배지형 — 라운드 배경 안에 짧은 라벨로 배치 |
  ```

  **Must NOT do**:
  - Golden Reference Example 코드 블록 수정 금지
  - 슬라이드 레벨 단일 title key 강제 추가 금지
  - 기존 이미지 중심 원칙 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md:132-146` — 렌더링 스타일 테이블
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md:149` — 이미지 중심 원칙 (삽입 위치 직후)
  - `plugins/visual-generator/skills/theme-comparison/SKILL.md:349-352` — Golden Reference before_title/after_title keys

  **Acceptance Criteria**:
  - [ ] `grep -c "필수 렌더링 요소" plugins/visual-generator/skills/theme-comparison/SKILL.md` ≥ 1
  - [ ] `grep -c "before_title\|after_title\|dual-title" plugins/visual-generator/skills/theme-comparison/SKILL.md` ≥ 3
  - [ ] `grep -c "오버레이.*볼드\|배지형\|대칭" plugins/visual-generator/skills/theme-comparison/SKILL.md` ≥ 2

  **Commit**: YES (groups with Tasks 1, 2, 3)

- [x] 5. prompt-designer.md에 title 필수 CONTENT key 규칙 추가

  **What to do**:
  - `plugins/visual-generator/agents/prompt-designer.md`를 읽는다
  - `### CONTENT Block Generation` 섹션 내, 테마별 key 설계 규칙 영역(현재 line 269-275 부근)에 새 규칙을 추가한다
  - 아래 내용을 삽입 (기존 CONTENT 생성 규칙 직후, 테마별 분기 규칙 직전):

  ```markdown
  필수 CONTENT key 규칙:

  - concept 테마를 제외한 모든 테마에서 **title 역할의 key는 필수**이다.
  - 각 테마의 `## 필수 렌더링 요소 (Must-Render Elements)` 목록에서 "필수" 표시된 요소를 CONTENT에 반드시 포함한다.
  - title key의 이름은 테마별로 다를 수 있다: seminar/whatif는 `title:`, pitch는 `hero_statement:` 또는 `main_number:`, comparison은 `before_title:` + `after_title:`.
  - concept 테마는 텍스트 항목 0개 원칙이므로 이 규칙을 적용하지 않는다.
  ```

  **Must NOT do**:
  - 기존 CONTENT Block Generation 규칙 삭제/변경 금지
  - Theme Branch Rules 변경 금지
  - Korean Text Safety Rules 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/agents/prompt-designer.md:269-275` — 테마별 key 설계 규칙 (삽입 위치 근처)
  - `plugins/visual-generator/agents/prompt-designer.md:437-472` — Korean Text Safety Rules (수정 금지, 참조만)

  **Acceptance Criteria**:
  - [ ] `grep -c "title.*필수\|필수.*key\|필수 CONTENT" plugins/visual-generator/agents/prompt-designer.md` ≥ 1
  - [ ] `grep -c "concept.*제외\|concept.*적용하지\|concept.*텍스트 항목 0" plugins/visual-generator/agents/prompt-designer.md` ≥ 2 (기존 Korean Safety + 새 규칙)

  **Commit**: YES (단독 commit 2)
  - Message: `feat(visual-generator): add mandatory title CONTENT key rule to prompt-designer`

- [x] 6. 버전 범프 + marketplace/README 동기화

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json`에서 `"version": "3.1.0"` → `"version": "3.2.0"`
  - `.claude-plugin/marketplace.json`에서 visual-generator 항목의 `"version": "3.1.0"` → `"version": "3.2.0"`
  - `.claude-plugin/marketplace.json`에서 `metadata.version`을 `"2.4.0"` → `"3.5.0"` (README 버전 트랙에 동기화, 기존 drift 해소)
  - `README.md`에서 상단 `**Version**: 3.4.0` → `**Version**: 3.5.0`
  - `README.md` 변경 이력 테이블에 새 행 추가: `| 3.5.0 | 2026-03-17 | visual-generator v3.2.0: Must-Render Registry 추가 (4개 테마 필수 렌더링 요소 명시화), marketplace metadata 버전 동기화 (2.4.0→3.5.0) |`

  **Must NOT do**:
  - 다른 플러그인의 버전 변경 금지
  - marketplace.json의 name, owner, description 등 다른 필드 변경 금지
  - README.md의 프로젝트 구조 트리, 플러그인 상세 섹션 등 다른 영역 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential after Wave 1)
  - **Blocks**: F1, F2
  - **Blocked By**: Tasks 1-5

  **References**:
  - `.claude-plugin/marketplace.json:7-8` — metadata.version 현재 "2.4.0"
  - `README.md:5` — 현재 "Version: 3.4.0"
  - `README.md:453-456` — 변경 이력 테이블 (최상단에 새 행 추가)

  **Acceptance Criteria**:
  - [ ] `grep '"3.2.0"' plugins/visual-generator/.claude-plugin/plugin.json` → match
  - [ ] `grep -A5 '"visual-generator"' .claude-plugin/marketplace.json | grep '"3.2.0"'` → match
  - [ ] `grep -A2 '"metadata"' .claude-plugin/marketplace.json | grep '"3.5.0"'` → match
  - [ ] `grep 'Version.*3.5.0' README.md` → match
  - [ ] `grep '3.5.0.*Must-Render' README.md` → match (변경 이력 행)

  **Commit**: YES (단독 commit 3)
  - Message: `chore(visual-generator): bump to v3.2.0, sync marketplace+README to 3.5.0`

- [x] 7. AGENTS.md 버전 동기화 규칙 수정

  **What to do**:
  - `AGENTS.md`의 `#### marketplace.json 메타데이터 버전` 섹션 (line 694-702)을 수정한다
  - 현재 상태: marketplace metadata와 README Version이 독립 트랙으로 운영되어 drift 발생 (README 3.4.0 vs marketplace 2.4.0)
  - 수정 내용: 섹션 제목을 `#### marketplace.json 메타데이터 버전 + README.md Version 동기화 (CRITICAL)`로 변경하고, 두 버전이 항상 일치해야 한다는 규칙을 명시

  기존 내용 (line 694-702):
  ```
  #### marketplace.json 메타데이터 버전

  루트 `marketplace.json`의 `metadata.version`은 **마켓플레이스 전체**의 버전입니다.

  | 변경 | 업데이트 |
  |------|----------|
  | 기존 플러그인 수정 (PATCH/MINOR) | 마켓플레이스 버전 변경 불필요 |
  | 새 플러그인 추가 | 마켓플레이스 MINOR 버전 올림 |
  | 플러그인 삭제 또는 마켓플레이스 구조 변경 | 마켓플레이스 MAJOR 버전 올림 |
  ```

  변경 후:
  ```
  #### marketplace.json 메타데이터 버전 + README.md Version 동기화 (CRITICAL)

  루트 `marketplace.json`의 `metadata.version`과 `README.md`의 `**Version**` 필드는 **동일한 프로젝트 버전**을 추적한다.
  두 값은 **항상 일치**해야 한다.

  | 변경 | 업데이트 |
  |------|----------|
  | 기존 플러그인 수정 (PATCH/MINOR) | marketplace `metadata.version` + README `Version` 동시 MINOR 올림 |
  | 새 플러그인 추가 | marketplace `metadata.version` + README `Version` 동시 MINOR 올림 |
  | 플러그인 삭제 또는 마켓플레이스 구조 변경 | marketplace `metadata.version` + README `Version` 동시 MAJOR 올림 |

  **동기화 규칙**:
  - `marketplace.json` → `metadata.version` 필드
  - `README.md` → 상단 `**Version**: X.Y.Z` 필드
  - `README.md` → `변경 이력` 테이블에 새 행 추가
  - 세 곳이 **동일한 버전**을 표시해야 한다
  ```

  - AGENTS.md 상단 `**Generated**` 날짜도 현재 날짜로 업데이트한다

  **Must NOT do**:
  - AGENTS.md의 다른 섹션 변경 금지
  - marketplace.json 메타데이터 버전 외의 규칙 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 6)
  - **Blocks**: F1, F2
  - **Blocked By**: Tasks 1-5

  **References**:
  - `AGENTS.md:694-702` — 현재 marketplace.json 메타데이터 버전 규칙 (수정 대상)
  - `AGENTS.md:1067` — "README.md Version과 실제 버전 불일치 | marketplace 버전과 동기화" (기존 README 규칙 — 이제 양방향 동기화로 강화)
  - `AGENTS.md:3` — Generated 날짜 (업데이트 대상)

  **Acceptance Criteria**:
  - [ ] `grep -c "README.md Version 동기화\|동일한 프로젝트 버전\|항상 일치" AGENTS.md` ≥ 2
  - [ ] `grep -c "동시 MINOR 올림\|동시 MAJOR 올림" AGENTS.md` ≥ 2
  - [ ] `grep "Generated" AGENTS.md | head -1` → 오늘 날짜

  **Commit**: YES (commit 3과 합침 또는 commit 4 단독)
  - Message: `docs: sync marketplace metadata + README version tracking rule in AGENTS.md`

---

## Final Verification Wave

- [x] F1. **Cross-Theme Consistency Audit** — `oracle`
  4개 테마 SKILL.md의 `## 필수 렌더링 요소` 섹션을 읽고 비교한다. 테이블 포맷 동일성, 배치 변형이 각 테마의 시각 정체성과 일치하는지, concept 면제가 prompt-designer 규칙에 포함되었는지 검증.
  Output: `Format [4/4 consistent] | Variations [4/4 theme-aligned] | Rule [present] | VERDICT: APPROVE/REJECT`

- [x] F2. **Scope Fidelity + Golden Reference Alignment** — `deep`
  `git diff --name-only` 로 정확히 9개 파일만 변경되었는지 확인 (4 theme SKILL + prompt-designer + plugin.json + marketplace.json + README.md + AGENTS.md). 각 테마의 Golden Reference 코드 블록이 수정되지 않았는지 확인. 각 필수 요소가 해당 Golden Reference CONTENT에 존재하는지 교차 검증. 버전 3.2.0/3.5.0 동기화. AGENTS.md에 버전 동기화 규칙 존재.
  Output: `Files [9/9] | Golden Ref [4/4 untouched] | Alignment [4/4] | Version [MATCH] | AGENTS.md [sync rule present] | VERDICT: APPROVE/REJECT`

---

## Commit Strategy

| # | Message | Files |
|---|---------|-------|
| 1 | `feat(visual-generator): add Must-Render Registry to 4 theme skills` | theme-seminar, theme-whatif, theme-pitch, theme-comparison SKILL.md |
| 2 | `feat(visual-generator): add mandatory title CONTENT key rule to prompt-designer` | prompt-designer.md |
| 3 | `chore(visual-generator): bump to v3.2.0, sync marketplace+README to 3.5.0` | plugin.json, marketplace.json, README.md |
| 4 | `docs: sync marketplace metadata + README version tracking rule in AGENTS.md` | AGENTS.md |

---

## Success Criteria

### Verification Commands
```bash
# 필수 렌더링 요소 섹션 존재 (4개 테마)
grep -l "필수 렌더링 요소" plugins/visual-generator/skills/theme-{seminar,whatif,pitch,comparison}/SKILL.md | wc -l
# Expected: 4

# prompt-designer title 필수 규칙
grep -c "title.*필수\|필수.*title" plugins/visual-generator/agents/prompt-designer.md
# Expected: ≥ 1

# concept 면제
grep -c "concept.*제외\|concept.*면제\|concept.*exempt" plugins/visual-generator/agents/prompt-designer.md
# Expected: ≥ 1

# 버전 동기화
grep '"3.2.0"' plugins/visual-generator/.claude-plugin/plugin.json .claude-plugin/marketplace.json | wc -l
# Expected: 2

# marketplace metadata + README 동기화
grep -A2 '"metadata"' .claude-plugin/marketplace.json | grep '"3.5.0"'
grep 'Version.*3.5.0' README.md
# Expected: 둘 다 match

# AGENTS.md 버전 동기화 규칙
grep -c "동일한 프로젝트 버전\|항상 일치" AGENTS.md
# Expected: ≥ 1

# Golden Reference 미수정 (코드 블록 내 title key가 그대로)
grep 'title:' plugins/visual-generator/skills/theme-seminar/SKILL.md | head -1
grep 'before_title:' plugins/visual-generator/skills/theme-comparison/SKILL.md | head -1
grep 'main_number:' plugins/visual-generator/skills/theme-pitch/SKILL.md | head -1
# Expected: 원본과 동일
```

### Final Checklist
- [ ] 4개 테마에 `## 필수 렌더링 요소` 섹션 존재
- [ ] 각 테마 배치 변형이 ≥ 3개
- [ ] 테마별 시각 정체성 반영됨
- [ ] prompt-designer에 title 필수 규칙 + concept 면제
- [ ] visual-generator 3.2.0 양쪽 동기화 (plugin.json + marketplace.json)
- [ ] marketplace metadata 3.5.0 + README 3.5.0 일치
- [ ] AGENTS.md에 버전 동기화 규칙 존재
- [ ] Golden Reference 코드 블록 미수정
- [ ] 9개 파일만 변경됨
