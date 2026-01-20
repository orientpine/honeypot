# Visual Prompt Skills 개선 계획

## Context

### Original Request
Visual-generator 플러그인의 prompt-* 스킬들 개선:
1. prompt-gov, prompt-concept에 prompt-seminar의 최신 기법 적용 (pt/px 렌더링 방지 등)
2. 3개 스킬 간 차별점 강화 (prompt-seminar 구조 기준)
3. 레이아웃을 공통 참조 파일로 통합 + 5개 신규 레이아웃 추가
4. 언어 규칙 통일 (병기 금지, 단일 언어 원칙)
5. 테마 수 통일 (모두 9개)

### Interview Summary
**Key Discussions**:
- prompt-seminar가 최신 구조 (4블록, pt/px 방지, 렌더링 체크리스트)
- prompt-concept, prompt-gov는 오래된 구조 (pt/px 노출, hint 병기 허용)
- 레이아웃 중복: seminar 15종, concept 12종, gov 12종 + gov 고유 4종
- 사용자 결정: 공통 레이아웃 통합, 병기 금지, 테마 9개 통일

**Research Findings**:
- 2024-2025 트렌드 레이아웃: Bento Grid, Sankey, Z-Pattern, Mind Map, Stacked Progress
- Gov 고유 레이아웃 4종: Pyramid, Exploded View, Timeline, Org-Network (통합 대상)
- KRDS (한국 정부 디자인 시스템) 참조 가능

### Metis Review
**Identified Gaps** (addressed):
- 테마 통일 방식: seminar의 9개 테마로 표준화 (gov 테마명 매핑)
- 언어 규칙 명확화: "병기 금지"는 CONTENT 블록에만 적용, INSTRUCTION의 AI hint는 허용
- prompt-concept은 이미 4블록 구조 → 구조 변경 최소화
- Gov 고유 레이아웃 4종을 공통 파일에 추가

---

## Work Objectives

### Core Objective
Visual-generator 플러그인의 3개 prompt-* 스킬을 현대화하고, 공통 레이아웃 참조 시스템을 구축하여 유지보수성과 일관성을 개선한다.

### Concrete Deliverables
1. `plugins/visual-generator/references/layout_types.md` - 공통 레이아웃 파일 (24종)
2. 업데이트된 `prompt-seminar/SKILL.md` - 공통 레이아웃 참조
3. 업데이트된 `prompt-concept/SKILL.md` - 최신 기법 적용, 공통 레이아웃 참조
4. 업데이트된 `prompt-gov/SKILL.md` - 4블록 구조 적용, 공통 레이아웃 참조
5. 업데이트된 각 스킬의 `prompt_style_guide.md` - pt/px 제거, 테마 9개 통일
6. 업데이트된 각 스킬의 `prompt_template.md` - 4블록 구조 통일

### Definition of Done
- [ ] `grep -rE "\d+pt|\d+px" plugins/visual-generator/skills/*/` CONTENT 블록에서 0건
- [ ] 모든 SKILL.md에 `[INSTRUCTION BLOCK]`, `[CONFIGURATION BLOCK]`, `[CONTENT BLOCK]`, `[FORBIDDEN ELEMENTS]` 존재
- [ ] 공통 레이아웃 파일에 24종 레이아웃 존재
- [ ] 각 prompt_style_guide.md에 9개 테마 정의
- [ ] 각 SKILL.md에 "렌더링 방지 체크리스트" 섹션 존재

### Must Have
- pt/px 값이 CONTENT 블록에 포함되지 않음 (크기 등급제: 대형/중형/소형)
- 단일 언어 원칙 (CONTENT 블록에서 병기 금지)
- 공통 레이아웃 참조 구조
- 렌더링 방지 체크리스트

### Must NOT Have (Guardrails)
- pt/px 값이 프롬프트 템플릿에 직접 포함됨
- CONTENT 블록에 언어 병기 (예: "굴착기 (Excavator)")
- 스킬별 중복된 레이아웃 정의
- renderer 스킬 또는 scripts 변경
- marketplace.json 또는 AGENTS.md 변경

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO (테스트 프레임워크 없음)
- **User wants tests**: Manual-only
- **QA approach**: 수동 검증 + Gemini API 렌더링 테스트

### Manual QA Procedures
각 TODO 완료 후:
1. grep 명령으로 pt/px 패턴 검색
2. SKILL.md 구조 검증 (4블록 존재 확인)
3. 최종: 샘플 프롬프트 생성 후 Gemini API로 렌더링 테스트

---

## Task Flow

```
Task 0 (공통 레이아웃 생성)
    ↓
┌───┴───┬───────────┐
↓       ↓           ↓
Task 1  Task 2      Task 3
(seminar)(concept)  (gov)
    ↓       ↓           ↓
    └───────┴───────────┘
            ↓
        Task 4 (검증)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 1, 2, 3 | 각 스킬 독립적으로 수정 가능 (Task 0 완료 후) |

| Task | Depends On | Reason |
|------|------------|--------|
| 1, 2, 3 | 0 | 공통 레이아웃 파일 필요 |
| 4 | 1, 2, 3 | 모든 스킬 수정 완료 후 검증 |

---

## TODOs

- [x] 0. 공통 레이아웃 파일 생성 (24종)

  **What to do**:
  - `plugins/visual-generator/references/` 폴더 생성
  - `layout_types.md` 생성 (24종 레이아웃)
  - 기존 15종 (seminar) + gov 고유 4종 + 신규 5종
  - 각 레이아웃: 핵심 아이디어, ASCII 시각 구성, 시각화 원칙, 권장 사양, 적합/부적합 케이스

  **신규 5종 레이아웃**:
  1. **Bento Grid**: Apple 스타일 모듈형 박스 그리드, 다양한 크기 조합
  2. **Sankey**: 흐름의 두께로 비율 표현, 예산/에너지 흐름
  3. **Z-Pattern**: 자연스러운 시선 흐름 (좌상→우상→좌하→우하)
  4. **Mind Map**: 중심에서 방사형 분기, 아이디어 탐색
  5. **Stacked Progress**: 누적 막대 또는 진행률, 구성 비율

  **Gov 고유 4종 (통합)**:
  1. 계층형 피라미드 (Pyramid)
  2. 3D 분해도 (Exploded View)
  3. 수평 타임라인 (Horizontal Timeline)
  4. 조직도+네트워크 (Org-Network)

  **Must NOT do**:
  - pt/px 값 포함 금지 (크기 등급만 사용)
  - 특정 스킬에 종속된 표현 금지

  **Parallelizable**: NO (이 태스크가 먼저 완료되어야 함)

  **References**:
  
  **Pattern References**:
  - `plugins/visual-generator/skills/prompt-seminar/references/layout_types.md` - 기존 15종 레이아웃 정의 (가장 완전한 버전)
  - `plugins/visual-generator/skills/prompt-gov/references/layout_types.md` - Gov 고유 레이아웃 4종 (Pyramid, Exploded View, Timeline, Org-Network)
  
  **External References**:
  - Bento Grid: https://mockuuups.studio/blog/post/best-bento-grid-design-examples/
  - Sankey: https://developers.google.com/chart/interactive/docs/gallery/sankey
  - Z-Pattern: https://interaction-design.org/literature/article/visual-hierarchy-organizing-content-to-follow-natural-eye-movement-patterns

  **Acceptance Criteria**:
  - [x] `plugins/visual-generator/references/` 폴더 존재
  - [x] `layout_types.md` 파일에 24종 레이아웃 정의
  - [x] 각 레이아웃에 ASCII 다이어그램, 권장 사양 테이블 포함
  - [x] `grep -E "\d+pt|\d+px" plugins/visual-generator/references/layout_types.md` → 0건

  **Commit**: YES
  - Message: `feat(visual-generator): add shared layout reference with 24 layouts`
  - Files: `plugins/visual-generator/references/layout_types.md`

---

- [ ] 1. prompt-seminar 업데이트 (공통 레이아웃 참조)

  **What to do**:
  - SKILL.md에서 레이아웃 참조 경로 변경: `references/layout_types.md` → `../../references/layout_types.md`
  - 기존 `references/layout_types.md` 삭제 (공통 파일로 대체)
  - 9개 신규 레이아웃 활용 가이드 추가 (Gov 4종 + 신규 5종)

  **Must NOT do**:
  - 기존 4블록 구조 변경 금지 (이미 최신)
  - prompt_style_guide.md의 테마 변경 금지 (이미 9개)

  **Parallelizable**: YES (with 2, 3) - Task 0 완료 후

  **References**:
  
  **Pattern References**:
  - `plugins/visual-generator/skills/prompt-seminar/SKILL.md:110-131` - 현재 레이아웃 참조 섹션

  **Acceptance Criteria**:
  - [ ] SKILL.md에서 공통 레이아웃 파일 참조
  - [ ] 기존 `references/layout_types.md` 삭제됨
  - [ ] 신규 레이아웃 9종에 대한 활용 가이드 존재

  **Commit**: YES (groups with 2, 3)
  - Message: `refactor(prompt-seminar): use shared layout reference`
  - Files: `plugins/visual-generator/skills/prompt-seminar/SKILL.md`

---

- [ ] 2. prompt-concept 업데이트 (최신 기법 적용)

  **What to do**:
  - **SKILL.md 업데이트**:
    - 레이아웃 참조 경로 변경 → 공통 파일
    - Step 4-5 "렌더링 방지 검증" 단계 추가
    - "렌더링 방지 체크리스트" 섹션 추가
    - 언어 규칙 명확화: "병기 금지" → CONTENT 블록에만 적용
  
  - **prompt_style_guide.md 업데이트**:
    - pt/px 숫자 제거 (lines 313-318 테이블)
    - 크기 등급제 적용: "대형/중형/소형" 또는 "prominent/medium/small"
    - 테마 9개로 확장 (knowledge, presentation, workshop 추가)
    - "렌더링 방지 규칙" 섹션 강화
  
  - **prompt_template.md 업데이트**:
    - CONFIGURATION 블록의 pt/px 숫자 제거
    - 크기 등급만 사용하도록 변경

  - 기존 `references/layout_types.md` 삭제 (공통 파일로 대체)

  **Must NOT do**:
  - 4블록 구조 자체 변경 금지 (이미 존재)
  - 텍스트 밀도 규칙 변경 금지 (12-15개 유지)
  - 스킬 철학 변경 금지 ("3초 핵심 파악" 유지)

  **Parallelizable**: YES (with 1, 3) - Task 0 완료 후

  **References**:
  
  **Pattern References**:
  - `plugins/visual-generator/skills/prompt-seminar/SKILL.md:161-167` - 렌더링 방지 검증 단계
  - `plugins/visual-generator/skills/prompt-seminar/SKILL.md:385-403` - 렌더링 방지 체크리스트
  - `plugins/visual-generator/skills/prompt-seminar/references/prompt_style_guide.md:112-129` - 9개 테마 정의
  
  **Files to Modify**:
  - `plugins/visual-generator/skills/prompt-concept/SKILL.md`
  - `plugins/visual-generator/skills/prompt-concept/references/prompt_style_guide.md`
  - `plugins/visual-generator/skills/prompt-concept/assets/output_template/prompt_template.md`

  **Acceptance Criteria**:
  - [ ] SKILL.md에 "렌더링 방지 검증" 단계 존재 (Step 4-5)
  - [ ] SKILL.md에 "렌더링 방지 체크리스트" 섹션 존재
  - [ ] prompt_style_guide.md에 9개 테마 정의
  - [ ] `grep -E "\d+pt|\d+px" plugins/visual-generator/skills/prompt-concept/references/` → 0건 (CONTENT 블록)
  - [ ] 기존 `references/layout_types.md` 삭제됨

  **Commit**: YES (groups with 1, 3)
  - Message: `refactor(prompt-concept): apply modern rendering rules and 9 themes`
  - Files: prompt-concept/ 하위 파일들

---

- [ ] 3. prompt-gov 업데이트 (4블록 구조 + 최신 기법)

  **What to do**:
  - **SKILL.md 대폭 업데이트**:
    - 12섹션 구조 → 4블록 구조로 재구성
    - 레이아웃 참조 경로 변경 → 공통 파일
    - "렌더링 방지 검증" 단계 추가
    - "렌더링 방지 체크리스트" 섹션 추가
    - 언어 규칙 명확화: CONTENT에서 병기 금지, INSTRUCTION에서 AI hint 허용
  
  - **prompt_style_guide.md 업데이트**:
    - 테마 명명 통일 (gov-blue → technical-report 스타일로)
    - pt/px 숫자 제거
    - 크기 등급제 적용
    - 테마 9개로 확장 (기존 5개 + 4개 추가)
    - 영어 hint 패턴 → INSTRUCTION 블록으로 이동 명시
  
  - **prompt_template.md 업데이트**:
    - 4블록 구조로 재구성
    - pt/px 숫자 제거

  - 기존 `references/layout_types.md` 삭제 (공통 파일로 대체)

  **테마 매핑** (Gov → Unified):
  | Gov 테마 | 통일 테마 | 비고 |
  |---------|----------|------|
  | gov-blue (#1E3A5F) | technical-report (#2C3E50) | 색상 유지, 명칭 통일 |
  | tech-green (#1B4332) | growth (#00B894) | 유사 개념 |
  | industry-gray (#2C3E50) | clarity (#2D3436) | 유사 개념 |
  | research-purple (#4A1A6B) | connection (#6C5CE7) | 유사 개념 |
  | eco-mint (#0B525B) | innovation (#E17055) | 개념 매핑 필요 |
  
  **주의**: Gov 고유 색상(#1E3A5F 등)은 유지하되 테마명만 통일

  **Must NOT do**:
  - Gov 고유 색상 코드 변경 금지
  - 텍스트 밀도 규칙 변경 금지 (~25개 유지)
  - 스킬 철학 변경 금지 (정부/공공기관 스타일 유지)

  **Parallelizable**: YES (with 1, 2) - Task 0 완료 후

  **References**:
  
  **Pattern References**:
  - `plugins/visual-generator/skills/prompt-seminar/SKILL.md` - 4블록 구조 전체 참조
  - `plugins/visual-generator/skills/prompt-seminar/references/prompt_style_guide.md` - 테마 정의 형식
  - `plugins/visual-generator/skills/prompt-seminar/assets/output_template/prompt_template.md` - 템플릿 형식
  
  **Files to Modify**:
  - `plugins/visual-generator/skills/prompt-gov/SKILL.md`
  - `plugins/visual-generator/skills/prompt-gov/references/prompt_style_guide.md`
  - `plugins/visual-generator/skills/prompt-gov/assets/output_template/prompt_template.md`

  **Acceptance Criteria**:
  - [ ] SKILL.md에 4블록 구조 (`[INSTRUCTION BLOCK]`, `[CONFIGURATION BLOCK]`, `[CONTENT BLOCK]`, `[FORBIDDEN ELEMENTS]`)
  - [ ] SKILL.md에 "렌더링 방지 검증" 단계 존재
  - [ ] SKILL.md에 "렌더링 방지 체크리스트" 섹션 존재
  - [ ] prompt_style_guide.md에 9개 테마 정의
  - [ ] `grep -E "\d+pt|\d+px" plugins/visual-generator/skills/prompt-gov/references/` → 0건 (CONTENT 블록)
  - [ ] prompt_template.md가 4블록 구조
  - [ ] 기존 `references/layout_types.md` 삭제됨

  **Commit**: YES (groups with 1, 2)
  - Message: `refactor(prompt-gov): restructure to 4-block format with modern rendering rules`
  - Files: prompt-gov/ 하위 파일들

---

- [ ] 4. 최종 검증 및 정리

  **What to do**:
  - 전체 pt/px 패턴 검색 (CONTENT 블록)
  - 각 스킬 4블록 구조 확인
  - 공통 레이아웃 참조 확인
  - 테마 수 확인 (각 9개)
  - 렌더링 체크리스트 존재 확인
  - 삭제된 layout_types.md 파일 확인 (3개 스킬에서)

  **Must NOT do**:
  - 추가 기능 구현 금지
  - 새로운 파일 생성 금지 (검증만)

  **Parallelizable**: NO (1, 2, 3 완료 후)

  **References**:
  - 위 모든 태스크의 Acceptance Criteria

  **Acceptance Criteria**:
  
  **전체 검증**:
  - [ ] `grep -rE "\d+pt|\d+px" plugins/visual-generator/skills/*/` → CONTENT 블록에서 0건
  - [ ] 3개 스킬 모두 공통 레이아웃 파일 참조
  - [ ] 3개 스킬 모두 9개 테마 정의
  - [ ] 3개 스킬 모두 렌더링 방지 체크리스트 존재
  - [ ] `ls plugins/visual-generator/skills/*/references/layout_types.md` → 0건 (모두 삭제됨)
  
  **Gemini API 테스트 (선택)**:
  - [ ] 각 스킬로 샘플 프롬프트 생성
  - [ ] Gemini API로 이미지 렌더링
  - [ ] 생성된 이미지에 pt/px 텍스트 없음 확인

  **Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | `feat(visual-generator): add shared layout reference with 24 layouts` | references/layout_types.md | grep pt/px = 0 |
| 1, 2, 3 | `refactor(visual-generator): modernize prompt skills with shared layouts` | 3개 스킬 하위 파일들 | grep pt/px = 0, 4블록 구조 확인 |

---

## Success Criteria

### Verification Commands
```bash
# pt/px 패턴 검색 (0건이어야 함)
grep -rE "\d+pt|\d+px" plugins/visual-generator/skills/*/

# 공통 레이아웃 파일 존재 확인
ls plugins/visual-generator/references/layout_types.md

# 스킬별 layout_types.md 삭제 확인 (0건이어야 함)
ls plugins/visual-generator/skills/*/references/layout_types.md 2>/dev/null | wc -l

# 4블록 구조 확인
grep -l "INSTRUCTION BLOCK" plugins/visual-generator/skills/*/SKILL.md | wc -l
# Expected: 3

# 테마 수 확인
grep -c "테마.*:" plugins/visual-generator/skills/*/references/prompt_style_guide.md
# Expected: 각 9개 이상
```

### Final Checklist
- [ ] 공통 레이아웃 파일 (24종) 존재
- [ ] 모든 스킬 4블록 구조 적용
- [ ] 모든 스킬 pt/px 제거 (CONTENT 블록)
- [ ] 모든 스킬 9개 테마 정의
- [ ] 모든 스킬 렌더링 방지 체크리스트 존재
- [ ] 스킬별 중복 layout_types.md 삭제됨
- [ ] 모든 "Must NOT Have" 항목 준수
