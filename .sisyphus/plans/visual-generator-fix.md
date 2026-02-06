# Visual Generator 프롬프트 품질 개선 계획

## TL;DR

> **Quick Summary**: visual-generator 플러그인에서 생성되는 프롬프트의 3가지 심각한 품질 문제(구성용 텍스트 렌더링, 환각 데이터, 참조/예시 누락)를 해결하기 위해 **모든 관련 에이전트 및 테마 파일**을 수정합니다.
> 
> **Deliverables**:
> - prompt-designer.md에 구성용 텍스트 렌더링 방지 규칙 추가
> - **renderer-agent.md에 구성용 텍스트 검증 로직 추가** (NEW)
> - **content-reviewer.md에 구성용 텍스트 검토 기준 추가** (NEW)
> - content-organizer.md에 환각 데이터 방지 규칙 추가
> - 모든 테마 파일(6개)에 렌더링 금지 경고 추가
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 6

---

## Context

### Original Request
visual-generator 플러그인에서 생성된 프롬프트 파일들에 심각한 문제가 발견됨:
1. 구성용 텍스트(`[하단 결론1]`, `Whatif Scenario Grid`)가 이미지에 렌더링됨
2. 환각 데이터(`www.ai-design-innovator.com`)가 포함됨
3. 참조 지시 및 예시 파일 누락

### 문제 증거 파일
| 파일 경로 | 문제 유형 | 문제 내용 |
|-----------|----------|----------|
| `output/visual-test/comparison/prompts/01_설계_비교.md` | 구성용 텍스트 | `[하단 결론1]`, `[왼쪽 제목]` 등 위치 지시자가 CONTENT에 포함 |
| `output/visual-test/whatif/prompts/01_미래_설계_프로세스.md` | 구성용 텍스트 | `Whatif Scenario Grid` 레이아웃 유형명이 CONFIGURATION에 포함되어 렌더링 |
| `output/visual-test/pitch/prompts/01_플랫폼_피치.md` | 환각 데이터 | `www.ai-design-innovator.com` 존재하지 않는 URL |
| `output/visual-test/pitch/prompts/01_플랫폼_피치.md` | 구성용 텍스트 | `[A-1]`, `[B-2]`, `(#0A2540)`, `48pt equivalent` 등 |

### 근본 원인 분석
1. **prompt-designer.md**: FORBIDDEN ELEMENTS에 구성용 텍스트 유형 정의가 불완전함
2. **renderer-agent.md**: 검증 단계에서 위치 지시자, 레이아웃 유형명, 색상 코드 검증 없음
3. **content-reviewer.md**: 검토 기준에 구성용 텍스트 검출 기준 없음
4. **content-organizer.md**: 실제 존재하지 않는 URL/데이터 생성 금지 규칙 없음
5. **테마 파일들**: 레이아웃 힌트/위치 지시자 사용 시 렌더링 금지 경고 없음

---

## Work Objectives

### Core Objective
visual-generator 플러그인이 생성하는 프롬프트에서 구성용 텍스트, 환각 데이터가 이미지에 렌더링되지 않도록 **파이프라인의 모든 단계**(생성 → 검토 → 검증 → 렌더링)에 명확한 규칙을 추가한다.

### Concrete Deliverables
- `plugins/visual-generator/agents/prompt-designer.md` 수정
- `plugins/visual-generator/agents/renderer-agent.md` 수정 **(NEW)**
- `plugins/visual-generator/agents/content-reviewer.md` 수정 **(NEW)**
- `plugins/visual-generator/agents/content-organizer.md` 수정
- `plugins/visual-generator/references/themes/*.md` 6개 파일 수정

### Definition of Done
- [ ] prompt-designer.md에 "구성용 텍스트 분리 원칙" 섹션 추가됨
- [ ] renderer-agent.md에 구성용 텍스트 검증 패턴 추가됨
- [ ] content-reviewer.md에 구성용 텍스트 검토 기준 추가됨
- [ ] content-organizer.md에 "환각 데이터 방지" 규칙 추가됨
- [ ] 모든 테마 파일에 "렌더링 금지 요소" 경고 섹션 추가됨
- [ ] 수정된 파일들의 마크다운 문법 오류 없음

### Must Have
- CONTENT BLOCK에 위치 지시자(`[상단]`, `[하단 결론1]`) 포함 금지 규칙
- CONTENT BLOCK에 레이아웃 유형명(`Whatif Scenario Grid`, `Contrast`) 포함 금지 규칙
- CONTENT BLOCK에 색상 코드(`#FF6B35`), 크기 힌트(`48pt`) 포함 금지 규칙
- 가상 URL/이메일/전화번호 등 환각 데이터 생성 금지 규칙
- **renderer-agent에서 위 패턴 검출 시 FAIL 처리 로직**
- **content-reviewer에서 위 패턴 검출 시 감점 처리 로직**

### Must NOT Have (Guardrails)
- 기존 기능(4-block 구조, 테마 색상 팔레트 등) 변경 없음
- 새로운 파일 생성 없음 (기존 파일 수정만)
- 테스트 코드 작성 없음

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: NO
- **Framework**: none

### Agent-Executed QA Scenarios (MANDATORY)

**모든 수정은 파일 내용 검증으로 확인합니다.**

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: prompt-designer.md 수정 (핵심)
├── Task 2: renderer-agent.md 수정 (NEW - 검증 로직)
├── Task 3: content-reviewer.md 수정 (NEW - 검토 기준)
├── Task 4: content-organizer.md 수정
└── Task 5: 테마 파일 6개 수정 (병렬)

Wave 2 (After Wave 1):
└── Task 6: 전체 검증 및 커밋
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 6 | 2, 3, 4, 5 |
| 2 | None | 6 | 1, 3, 4, 5 |
| 3 | None | 6 | 1, 2, 4, 5 |
| 4 | None | 6 | 1, 2, 3, 5 |
| 5 | None | 6 | 1, 2, 3, 4 |
| 6 | 1, 2, 3, 4, 5 | None | None (final) |

---

## TODOs

- [ ] 1. prompt-designer.md FORBIDDEN ELEMENTS 강화

  **What to do**:
  - `## Rendering Prevention Rules` 섹션의 `### 절대 금지 패턴` 테이블에 다음 패턴 추가:
    - `[하단 결론1]` → 위치 지시자 렌더링 → 실제 결론 텍스트만 작성
    - `[왼쪽 제목]`, `[오른쪽 제목]` → 위치 라벨 렌더링 → 실제 제목 텍스트만 작성
    - `Whatif Scenario Grid` → 레이아웃 유형명 렌더링 → CONFIGURATION에서만 사용
    - `Contrast`, `Section-Flow` → 메타포 이름 렌더링 → CONFIGURATION에서만 사용
  - `### 절대 금지 패턴` 테이블 뒤에 새로운 섹션 추가: `### 구성용 텍스트 분리 원칙 (CRITICAL)`
    - CONTENT BLOCK에는 오직 "이미지에 실제로 보여야 할 텍스트"만 포함
    - 위치 지시자, 레이아웃 유형명, 크기 힌트, 색상 지정, 역할 설명 금지
    - 올바른/잘못된 CONTENT BLOCK 예시 제공

  **Must NOT do**:
  - 기존 4-block 구조 변경
  - Text Density Rules 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 수정, 기존 섹션에 내용 추가
  - **Skills**: []
    - 특별한 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:156-175` - 기존 Rendering Prevention Rules 섹션
  - `plugins/visual-generator/agents/prompt-designer.md:108-125` - 기존 FORBIDDEN ELEMENTS 블록 구조

  **문제 증거 참조**:
  - `output/visual-test/comparison/prompts/01_설계_비교.md:62-83` - `[하단 결론1]` 등 위치 지시자 포함 예시
  - `output/visual-test/whatif/prompts/01_미래_설계_프로세스.md:42` - `Whatif Scenario Grid` 포함 예시
  - `output/visual-test/pitch/prompts/01_플랫폼_피치.md:67-80` - `[A-1]`, `(#0A2540)` 등 포함 예시

  **추가할 내용 템플릿**:
  ```markdown
  ### 구성용 텍스트 분리 원칙 (CRITICAL)

  **CONTENT BLOCK에는 오직 "이미지에 실제로 보여야 할 텍스트"만 포함합니다.**

  다음은 **절대로 CONTENT BLOCK에 포함하면 안 되는** 구성용 텍스트입니다:

  | 유형 | 금지 예시 | 올바른 처리 |
  |------|-----------|------------|
  | **위치 지시자** | `[상단]`, `[하단 결론1]`, `[왼쪽 영역]` | INSTRUCTION에서 위치 설명, CONTENT에는 실제 텍스트만 |
  | **레이아웃 유형명** | `Whatif Scenario Grid`, `Before/After 비교` | CONFIGURATION의 Layout Structure에서만 언급 |
  | **메타포 이름** | `Contrast`, `Flow`, `Section-Flow` | CONFIGURATION에서만 사용 |
  | **크기 힌트** | `(대형)`, `(중형)`, `Large KPI`, `48pt` | INSTRUCTION의 스타일 설명에서만 사용 |
  | **색상 지정** | `(#FF6B35)`, `Accent Color` | CONFIGURATION의 Color Palette에서만 명시 |
  | **역할 설명** | `Main Title`, `핵심 메시지 영역` | INSTRUCTION에서 설명, CONTENT에는 실제 텍스트만 |

  **올바른 CONTENT BLOCK 예시:**

  ## CONTENT (올바름)

  1. AI 설계 플랫폼 도입 미래상
  2. 도메인 특화 LLM 엔진
  3. 설계 시간 70% 단축
  4. 오류율 90% 감소

  **잘못된 CONTENT BLOCK 예시:**

  ## CONTENT (금지)

  1. **[메인 타이틀]** AI 설계 플랫폼 도입 미래상
  2. **[Section A]** 도메인 특화 LLM 엔진
  3. **[Large KPI]** 설계 시간 70% 단축 (#FF6B35, Accent)
  4. **Whatif Scenario Grid** - 시나리오 레이아웃
  ```

  **Acceptance Criteria**:
  - [ ] `절대 금지 패턴` 테이블에 위치 지시자, 레이아웃 유형명, 메타포 이름 패턴 4개 이상 추가됨
  - [ ] `구성용 텍스트 분리 원칙 (CRITICAL)` 섹션이 추가됨
  - [ ] 올바른/잘못된 CONTENT BLOCK 예시가 포함됨
  - [ ] 파일의 마크다운 문법 오류 없음 (Read로 확인)

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: prompt-designer.md 수정 내용 검증
    Tool: Bash (grep)
    Preconditions: 파일 수정 완료
    Steps:
      1. grep -c "구성용 텍스트 분리 원칙" plugins/visual-generator/agents/prompt-designer.md
      2. Assert: 결과가 1 이상
      3. grep -c "\[하단 결론1\]" plugins/visual-generator/agents/prompt-designer.md
      4. Assert: 결과가 1 이상 (금지 패턴 테이블에 포함)
      5. grep -c "Whatif Scenario Grid" plugins/visual-generator/agents/prompt-designer.md
      6. Assert: 결과가 1 이상
    Expected Result: 모든 필수 섹션과 패턴이 파일에 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES (groups with 2, 3, 4, 5)
  - Message: `fix(visual-generator): add composition text rendering prevention rules`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`
  - Pre-commit: None

---

- [ ] 2. renderer-agent.md 검증 로직 강화 (NEW)

  **What to do**:
  - `## Validation Checklist` 테이블 (124-129줄)에 새로운 검증 항목 추가:
    - `5 | 위치 지시자 없음 | \[.*\] 대괄호 패턴 검색 | 패턴 발견`
    - `6 | 레이아웃 유형명 없음 | Grid, Flow, Pattern 등 | 패턴 발견`
    - `7 | 인라인 색상 코드 없음 | #[A-Fa-f0-9]{6} 패턴 | 패턴 발견`
    - `8 | 환각 URL 없음 | www\..* 패턴 | 패턴 발견`
  - `### 검증 명령어 예시` 섹션에 새로운 명령어 추가:
    ```bash
    # 위치 지시자 확인 (없어야 PASS)
    grep -E "\[[A-Z가-힣]+-?[0-9]*\]|\[상단\]|\[하단\]|\[왼쪽\]|\[오른쪽\]" prompt.md || echo "PASS"
    
    # 인라인 색상 코드 확인 (없어야 PASS)
    grep -E "\(#[A-Fa-f0-9]{6}\)" prompt.md || echo "PASS"
    
    # 환각 URL 확인 (없어야 PASS)
    grep -E "www\.[a-z-]+\.(com|net|org)" prompt.md || echo "PASS"
    ```

  **Must NOT do**:
  - 기존 4개 검증 항목 삭제
  - 스크립트 호출 방식 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 수정, 테이블에 행 추가
  - **Skills**: []
    - 특별한 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/renderer-agent.md:120-142` - 기존 Validation Checklist 섹션

  **추가할 내용 템플릿**:
  ```markdown
  | 5 | 위치 지시자 없음 | `grep -E "\[[A-Z가-힣].*\]"` | 패턴 발견 |
  | 6 | 레이아웃 유형명 없음 | `grep -Ei "scenario grid|section-flow|z-pattern"` | 패턴 발견 |
  | 7 | 인라인 색상 코드 없음 | `grep -E "\(#[A-Fa-f0-9]{6}\)"` | 패턴 발견 |
  | 8 | 환각 URL 없음 | `grep -E "www\.[a-z-]+\.(com|net|org)"` | 패턴 발견 |
  ```

  **Acceptance Criteria**:
  - [ ] Validation Checklist 테이블에 4개 이상의 새로운 검증 항목 추가됨
  - [ ] 검증 명령어 예시에 새로운 grep 패턴 추가됨
  - [ ] 파일의 마크다운 문법 오류 없음

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: renderer-agent.md 수정 내용 검증
    Tool: Bash (grep)
    Preconditions: 파일 수정 완료
    Steps:
      1. grep -c "위치 지시자 없음" plugins/visual-generator/agents/renderer-agent.md
      2. Assert: 결과가 1 이상
      3. grep -c "환각 URL 없음" plugins/visual-generator/agents/renderer-agent.md
      4. Assert: 결과가 1 이상
    Expected Result: 새로운 검증 항목이 파일에 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES (groups with 1, 3, 4, 5)
  - Message: `fix(visual-generator): add composition text validation to renderer`
  - Files: `plugins/visual-generator/agents/renderer-agent.md`
  - Pre-commit: None

---

- [ ] 3. content-reviewer.md 검토 기준 추가 (NEW)

  **What to do**:
  - `## Review Criteria` 섹션에 새로운 평가 카테고리 추가: `### 4. 구성용 텍스트 검출 (Composition Text Detection)`
    ```markdown
    ### 4. 구성용 텍스트 검출 (Composition Text Detection)

    | 평가 항목 | 기준 | 점수 |
    |-----------|------|:----:|
    | 위치 지시자 부재 | `[상단]`, `[하단 결론1]` 등 없음 | 1-5 |
    | 레이아웃 유형명 부재 | `Whatif Scenario Grid` 등 없음 | 1-5 |
    | 색상/크기 힌트 부재 | `(#FF6B35)`, `48pt` 등 없음 | 1-5 |
    | 환각 데이터 부재 | 가상 URL/이메일/통계 없음 | 1-5 |

    **점수 기준:**
    - 5: 깨끗함 - 구성용 텍스트 완전 부재
    - 3: 경미 - 1-2개 패턴 발견 (수정 권장)
    - 1: 심각 - 3개 이상 패턴 발견 (필수 수정)
    ```
  - `### PASS 조건` / `### REJECT 조건`에 새로운 기준 반영

  **Must NOT do**:
  - 기존 3개 평가 카테고리 변경
  - 점수 산출 방식 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 수정, 섹션 추가
  - **Skills**: []
    - 특별한 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-reviewer.md:36-96` - 기존 Review Criteria 섹션

  **Acceptance Criteria**:
  - [ ] `구성용 텍스트 검출 (Composition Text Detection)` 섹션 추가됨
  - [ ] 4개 평가 항목 테이블 포함됨
  - [ ] PASS/REJECT 조건에 새로운 기준 반영됨
  - [ ] 파일의 마크다운 문법 오류 없음

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: content-reviewer.md 수정 내용 검증
    Tool: Bash (grep)
    Preconditions: 파일 수정 완료
    Steps:
      1. grep -c "구성용 텍스트 검출" plugins/visual-generator/agents/content-reviewer.md
      2. Assert: 결과가 1 이상
      3. grep -c "Composition Text Detection" plugins/visual-generator/agents/content-reviewer.md
      4. Assert: 결과가 1 이상
    Expected Result: 새로운 검토 기준 섹션이 파일에 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES (groups with 1, 2, 4, 5)
  - Message: `fix(visual-generator): add composition text review criteria`
  - Files: `plugins/visual-generator/agents/content-reviewer.md`
  - Pre-commit: None

---

- [ ] 4. content-organizer.md 환각 데이터 방지 규칙 추가

  **What to do**:
  - `## MUST NOT DO` 섹션에 다음 규칙 추가:
    - 존재하지 않는 URL, 이메일, 전화번호 등 가상 연락처 생성 금지
    - 실제로 검증되지 않은 통계/수치 임의 생성 금지
  - 새로운 섹션 추가: `## 환각 데이터 방지 (Hallucination Prevention)`
    - 가상 URL (`www.example-company.com`) 생성 금지
    - 가상 이메일 (`contact@fake-domain.com`) 생성 금지
    - 검증되지 않은 시장 규모/성장률 임의 생성 금지
    - CTA 영역에 연락처가 필요한 경우 `[연락처 입력 필요]` 플레이스홀더 사용 지시

  **Must NOT do**:
  - 기존 워크플로우 변경
  - 테마/레이아웃 선택 로직 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 수정, 섹션 추가
  - **Skills**: []
    - 특별한 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-organizer.md:293-300` - 기존 MUST NOT DO 섹션

  **문제 증거 참조**:
  - `output/visual-test/pitch/prompts/01_플랫폼_피치.md:80` - `www.ai-design-innovator.com` 환각 URL

  **추가할 내용 템플릿**:
  ```markdown
  ## 환각 데이터 방지 (Hallucination Prevention)

  프롬프트에 포함되는 모든 데이터는 **검증 가능하거나 명시적으로 플레이스홀더로 표시**되어야 합니다.

  ### 절대 금지 (생성하지 말 것)

  | 유형 | 금지 예시 | 올바른 처리 |
  |------|-----------|------------|
  | **가상 URL** | `www.ai-design-innovator.com` | `[웹사이트 URL 입력 필요]` 또는 생략 |
  | **가상 이메일** | `contact@platform.com` | `[이메일 입력 필요]` 또는 생략 |
  | **가상 전화번호** | `02-1234-5678` | `[연락처 입력 필요]` 또는 생략 |
  | **미검증 통계** | `시장 규모 $10.2 Billion` | 출처 명시 또는 `[시장 규모 데이터 필요]` |
  | **미검증 성장률** | `CAGR 12.5%` | 출처 명시 또는 `[성장률 데이터 필요]` |

  ### 연락처/CTA 영역 처리 원칙

  - CTA(Call-to-Action) 영역에 연락처가 필요한 경우:
    1. 입력 문서에 실제 연락처가 있으면 그대로 사용
    2. 없으면 `[연락처 입력 필요]` 플레이스홀더 사용
    3. **절대로 그럴듯한 가상 연락처를 생성하지 말 것**

  - 통계/수치 사용 시:
    1. 입력 문서에서 직접 인용
    2. 인용 불가 시 `[데이터 필요]` 플레이스홀더 사용
    3. **절대로 그럴듯한 가상 수치를 생성하지 말 것**
  ```

  **Acceptance Criteria**:
  - [ ] `MUST NOT DO` 섹션에 가상 연락처/데이터 생성 금지 규칙 추가됨
  - [ ] `환각 데이터 방지 (Hallucination Prevention)` 섹션이 추가됨
  - [ ] 금지 예시와 올바른 처리 방법이 테이블로 명시됨
  - [ ] 파일의 마크다운 문법 오류 없음

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: content-organizer.md 수정 내용 검증
    Tool: Bash (grep)
    Preconditions: 파일 수정 완료
    Steps:
      1. grep -c "환각 데이터 방지" plugins/visual-generator/agents/content-organizer.md
      2. Assert: 결과가 1 이상
      3. grep -c "Hallucination Prevention" plugins/visual-generator/agents/content-organizer.md
      4. Assert: 결과가 1 이상
      5. grep -c "가상 URL" plugins/visual-generator/agents/content-organizer.md
      6. Assert: 결과가 1 이상
    Expected Result: 환각 데이터 방지 섹션이 파일에 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES (groups with 1, 2, 3, 5)
  - Message: `fix(visual-generator): add hallucination prevention rules`
  - Files: `plugins/visual-generator/agents/content-organizer.md`
  - Pre-commit: None

---

- [ ] 5. 테마 파일 6개에 렌더링 금지 경고 추가

  **What to do**:
  - 다음 6개 테마 파일 각각에 `## 렌더링 금지 요소 (CRITICAL)` 섹션 추가:
    - `plugins/visual-generator/references/themes/comparison.md`
    - `plugins/visual-generator/references/themes/whatif.md`
    - `plugins/visual-generator/references/themes/pitch.md`
    - `plugins/visual-generator/references/themes/concept.md`
    - `plugins/visual-generator/references/themes/gov.md`
    - `plugins/visual-generator/references/themes/seminar.md`
  
  - 각 테마 파일 끝에 다음 섹션 추가 (테마별 특성에 맞게 예시 조정):

  **Must NOT do**:
  - 기존 색상 팔레트 변경
  - 기존 레이아웃 권장사항 변경

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 6개 파일에 동일 패턴 섹션 추가
  - **Skills**: []
    - 특별한 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/references/themes/comparison.md` - Before/After 비교 테마, 위치 지시자 사용 많음
  - `plugins/visual-generator/references/themes/whatif.md` - 시나리오 테마, 레이아웃 유형명 포함 위험
  - `plugins/visual-generator/references/themes/pitch.md` - 투자 제안용, CTA/연락처 영역 환각 위험

  **추가할 섹션 템플릿 (각 테마 파일 끝에 추가)**:
  ```markdown
  ---

  ## 렌더링 금지 요소 (CRITICAL)

  이 테마를 사용하여 프롬프트를 생성할 때, 다음 요소들은 **CONTENT BLOCK에 절대 포함하지 마십시오**.
  이 요소들은 프롬프트 구성을 위한 것이며, 이미지에 렌더링되면 안 됩니다.

  ### 금지 패턴

  | 유형 | 금지 예시 | 설명 |
  |------|-----------|------|
  | 위치 지시자 | `[상단]`, `[하단 결론1]`, `[왼쪽 영역]` | 레이아웃 배치 힌트 |
  | 레이아웃 유형명 | `{테마별 레이아웃명}` | 메타포/레이아웃 이름 |
  | 색상 코드 | `(#HEXCODE)`, `Primary Color` | CONFIGURATION에서만 사용 |
  | 크기 힌트 | `(대형)`, `(중형)`, `48pt` | INSTRUCTION에서만 사용 |
  | 역할 라벨 | `Main Title`, `Sub-header` | INSTRUCTION에서만 사용 |

  ### 올바른 CONTENT 작성법

  **잘못된 예:**
  ```
  1. **[메인 타이틀]** 플랫폼 비전
  2. **[핵심 지표]** 70% 개선 (#FF6B35)
  ```

  **올바른 예:**
  ```
  1. 플랫폼 비전
  2. 70% 개선
  ```

  텍스트의 위치, 크기, 색상은 INSTRUCTION과 CONFIGURATION에서 설명하고,
  CONTENT에는 **순수한 텍스트 내용만** 포함합니다.
  ```

  **테마별 레이아웃명 예시 (각 파일에 맞게 조정)**:
  - comparison.md: `대비 메타포`, `Before/After 비교`, `Contrast`
  - whatif.md: `Whatif Scenario Grid`, `Section-Flow`, `Z-Pattern`
  - pitch.md: `Z-Pattern`, `Pitch Deck Layout`
  - concept.md: `TED 스타일`, `미니멀 인포그래픽`
  - gov.md: `공공기관 슬라이드`, `정부 보고서 레이아웃`
  - seminar.md: `세미나 프레젠테이션`, `강연 슬라이드`

  **Acceptance Criteria**:
  - [ ] 6개 테마 파일 모두에 `렌더링 금지 요소 (CRITICAL)` 섹션 추가됨
  - [ ] 각 테마 파일의 레이아웃명 예시가 해당 테마에 맞게 조정됨
  - [ ] 올바른/잘못된 CONTENT 예시가 모든 파일에 포함됨
  - [ ] 모든 파일의 마크다운 문법 오류 없음

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: 테마 파일 수정 내용 검증
    Tool: Bash (grep)
    Preconditions: 6개 테마 파일 수정 완료
    Steps:
      1. for f in comparison whatif pitch concept gov seminar; do
           grep -c "렌더링 금지 요소" plugins/visual-generator/references/themes/${f}.md
         done
      2. Assert: 모든 파일에서 결과가 1 이상
      3. grep -c "Whatif Scenario Grid" plugins/visual-generator/references/themes/whatif.md
      4. Assert: 결과가 1 이상 (금지 예시에 포함)
    Expected Result: 모든 테마 파일에 렌더링 금지 섹션 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES (groups with 1, 2, 3, 4)
  - Message: `fix(visual-generator): add rendering prohibition warnings to all themes`
  - Files: 
    - `plugins/visual-generator/references/themes/comparison.md`
    - `plugins/visual-generator/references/themes/whatif.md`
    - `plugins/visual-generator/references/themes/pitch.md`
    - `plugins/visual-generator/references/themes/concept.md`
    - `plugins/visual-generator/references/themes/gov.md`
    - `plugins/visual-generator/references/themes/seminar.md`
  - Pre-commit: None

---

- [ ] 6. 전체 검증 및 커밋

  **What to do**:
  - 수정된 모든 파일 읽어서 마크다운 문법 오류 없는지 확인
  - 모든 필수 섹션이 추가되었는지 grep으로 검증
  - 단일 커밋으로 모든 변경사항 커밋

  **Must NOT do**:
  - 추가 파일 수정
  - 테스트 코드 작성

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 검증 및 커밋 작업
  - **Skills**: [`git-master`]
    - git-master: 커밋 작업에 필요

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (final)
  - **Blocks**: None
  - **Blocked By**: Tasks 1, 2, 3, 4, 5

  **References**:

  **수정된 파일 목록 (총 10개)**:
  - `plugins/visual-generator/agents/prompt-designer.md`
  - `plugins/visual-generator/agents/renderer-agent.md` (NEW)
  - `plugins/visual-generator/agents/content-reviewer.md` (NEW)
  - `plugins/visual-generator/agents/content-organizer.md`
  - `plugins/visual-generator/references/themes/comparison.md`
  - `plugins/visual-generator/references/themes/whatif.md`
  - `plugins/visual-generator/references/themes/pitch.md`
  - `plugins/visual-generator/references/themes/concept.md`
  - `plugins/visual-generator/references/themes/gov.md`
  - `plugins/visual-generator/references/themes/seminar.md`

  **Acceptance Criteria**:
  - [ ] 모든 수정 파일의 마크다운 문법 오류 없음
  - [ ] 필수 섹션 존재 여부 grep으로 확인됨
  - [ ] 단일 커밋으로 모든 변경사항 커밋됨

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: 전체 수정 검증
    Tool: Bash (grep + Read)
    Preconditions: Tasks 1, 2, 3, 4, 5 완료
    Steps:
      1. grep -l "구성용 텍스트 분리 원칙" plugins/visual-generator/agents/prompt-designer.md
      2. grep -l "위치 지시자 없음" plugins/visual-generator/agents/renderer-agent.md
      3. grep -l "구성용 텍스트 검출" plugins/visual-generator/agents/content-reviewer.md
      4. grep -l "환각 데이터 방지" plugins/visual-generator/agents/content-organizer.md
      5. for f in comparison whatif pitch concept gov seminar; do
           grep -l "렌더링 금지 요소" plugins/visual-generator/references/themes/${f}.md
         done
      6. Assert: 모든 grep 명령이 파일을 반환
    Expected Result: 모든 필수 섹션이 각 파일에 존재
    Evidence: grep 명령 출력
  ```

  **Commit**: YES
  - Message: `fix(visual-generator): prevent composition text rendering and hallucination data

  - Add composition text separation rules to prompt-designer.md
  - Add composition text validation to renderer-agent.md
  - Add composition text review criteria to content-reviewer.md
  - Add hallucination prevention rules to content-organizer.md
  - Add rendering prohibition warnings to all 6 theme files
  
  Fixes: composition text like [하단 결론1], Whatif Scenario Grid being rendered
  Fixes: hallucinated URLs like www.ai-design-innovator.com being generated`
  - Files: All 10 modified files
  - Pre-commit: None

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 6 (final) | `fix(visual-generator): prevent composition text rendering and hallucination data` | 10 files | grep 검증 |

---

## Success Criteria

### Verification Commands
```bash
# 필수 섹션 존재 확인 (에이전트 파일)
grep "구성용 텍스트 분리 원칙" plugins/visual-generator/agents/prompt-designer.md
grep "위치 지시자 없음" plugins/visual-generator/agents/renderer-agent.md
grep "구성용 텍스트 검출" plugins/visual-generator/agents/content-reviewer.md
grep "환각 데이터 방지" plugins/visual-generator/agents/content-organizer.md

# 모든 테마 파일에 렌더링 금지 섹션 확인
for f in comparison whatif pitch concept gov seminar; do
  grep "렌더링 금지 요소" plugins/visual-generator/references/themes/${f}.md && echo "$f: OK"
done
```

### Final Checklist
- [ ] prompt-designer.md에 구성용 텍스트 분리 규칙 추가됨
- [ ] renderer-agent.md에 구성용 텍스트 검증 로직 추가됨
- [ ] content-reviewer.md에 구성용 텍스트 검토 기준 추가됨
- [ ] content-organizer.md에 환각 데이터 방지 규칙 추가됨
- [ ] 6개 테마 파일 모두에 렌더링 금지 경고 추가됨
- [ ] 모든 파일 마크다운 문법 오류 없음
- [ ] 단일 커밋으로 변경사항 커밋됨
