# Visual Generator 멀티 에이전트 전환 및 신규 테마 추가

## TL;DR

> **Quick Summary**: visual-generator 플러그인을 스킬 기반에서 멀티 에이전트 아키텍처로 전환하고, 3개 신규 테마(whatif, pitch, comparison)를 추가하며, renderer의 스크립트 경로 문제를 해결합니다.
> 
> **Deliverables**:
> - 5개 Agent 파일 (orchestrator, content-organizer, content-reviewer, prompt-designer, renderer-agent)
> - 3개 스킬별 테마 파일 이관 (gov.md, seminar.md, concept.md - 각각 9개 무드 테마 포함)
> - 3개 신규 용도별 테마 파일 (whatif.md, pitch.md, comparison.md - 각각 단일 4색 팔레트)
> - 업데이트된 marketplace.json
> - 수정된 renderer 경로 (${CLAUDE_PLUGIN_ROOT} 사용)
> - 엔드투엔드 테스트 완료
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 2 → Tasks 3-7 (parallel) → Task 8 → Task 9 → Task 10

---

## Context

### Original Request
- 각 이미지 생성용 프롬프트의 구성력 부족을 보완하기 위한 멀티 에이전트 구성 필요
- renderer가 항상 잘못된 script 경로를 참조하는 문제 해결
- prompt-gov, prompt-seminar, prompt-concept 이외에 2가지 정도 새로운 테마 추가 (최종 3개로 확정)

### Interview Summary
**Key Discussions**:
- 아키텍처: 완전 Agent 전환 (모든 스킬 → agents/)
- 실행 방식: 자동 파이프라인 (중간 확인 없이 전체 워크플로우 실행)
- 신규 테마: whatif (시나리오 시뮬레이션), pitch (Pitch Deck), comparison (Before/After)
- 기존 스킬: 완전 삭제 (layout-types만 유지)
- Renderer: Agent로 통합
- 테스트: 엔드투엔드 (Gemini API 호출 포함)
- 에이전트 수: 5개 (orchestrator + 4 sub-agents)

**Research Findings**:
- Claude Code 플러그인은 설치 시 캐시 디렉토리로 복사됨
- `../` 경로 사용 불가 (복사 시 포함 안 됨)
- hooks/mcpServers에서 `${CLAUDE_PLUGIN_ROOT}` 변수 사용 가능
- 공식 문서에서 agent 파일 내 스크립트 참조 시 동일 변수 사용 권장

### Metis Review
**Identified Gaps** (addressed):
- ${CLAUDE_PLUGIN_ROOT} agent 컨텍스트 검증 → Task 1로 분리
- Agent 역할 경계 명확화 → 각 agent 파일에 MUST/MUST NOT 섹션 추가
- 기존 스킬 소비자 확인 → breaking change 고지 포함
- 테마 데이터 구조 보존 → references/themes/*.md로 이관
- 에러 핸들링 전략 → renderer-agent에 재시도 로직 명시

---

## Work Objectives

### Core Objective
visual-generator 플러그인을 멀티 에이전트 아키텍처로 전환하여 프롬프트 생성 품질을 향상시키고, 3개 신규 테마를 추가합니다.

### Concrete Deliverables
- `plugins/visual-generator/agents/orchestrator.md`
- `plugins/visual-generator/agents/content-organizer.md`
- `plugins/visual-generator/agents/content-reviewer.md`
- `plugins/visual-generator/agents/prompt-designer.md`
- `plugins/visual-generator/agents/renderer-agent.md`
- `plugins/visual-generator/references/themes/whatif.md`
- `plugins/visual-generator/references/themes/pitch.md`
- `plugins/visual-generator/references/themes/comparison.md`
- 기존 테마 파일 이관 (`gov.md`, `seminar.md`, `concept.md`)
- 업데이트된 `.claude-plugin/marketplace.json`
- 삭제: `skills/prompt-concept/`, `skills/prompt-gov/`, `skills/prompt-seminar/`, `skills/renderer/`

### Definition of Done
- [ ] 5개 Agent 파일이 모두 생성됨
- [ ] 6개 테마 파일이 references/themes/에 존재:
  - 스킬별 3개: gov.md, seminar.md, concept.md (각 9개 무드 테마)
  - 용도별 3개: whatif.md, pitch.md, comparison.md (각 단일 4색 팔레트)
- [ ] marketplace.json이 agents를 올바르게 참조
- [ ] 테스트 프롬프트 생성 시 4-block 구조 유지
- [ ] Gemini API를 통해 최소 1개 이미지 생성 성공
- [ ] 기존 스킬 폴더 삭제됨 (layout-types 제외)

### Must Have
- 기존 24개 레이아웃 타입 완전 보존 (layout-types 스킬)
- 기존 9개 무드 테마 + 색상 팔레트 완전 보존 (각 스킬별 테마 파일에 9개씩)
- 4-block 프롬프트 구조 유지 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN)
- 텍스트 밀도 규칙 유지 (gov: 25개, concept: 15개, seminar: 30개)
- 렌더링 방지 검증 로직 유지 (pt/px 금지, 언어 병기 금지)
- Python 스크립트 API 유지 (--prompts-dir, --output-dir)

### Must NOT Have (Guardrails)
- Python 스크립트에 새 의존성 추가 금지
- generate_slide_images.py의 API 변경 금지 (경로 변수만 수정)
- 4개 이상의 신규 테마 추가 금지 (scope creep)
- prompt-designer에서 테마/레이아웃 선택 로직 포함 금지 (content-organizer 역할)
- final-reviewer 로직을 prompt-designer에 병합 금지 (역할 분리)

---

## Verification Strategy (MANDATORY)

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.

### Test Decision
- **Infrastructure exists**: NO (unit test 없음)
- **Automated tests**: NO (Agent QA 시나리오만)
- **Framework**: none
- **Agent-Executed QA**: ALWAYS (mandatory)

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

**Verification Tool by Deliverable Type:**

| Type | Tool | How Agent Verifies |
|------|------|-------------------|
| **Agent .md files** | Bash (grep, cat) | Verify frontmatter, required sections exist |
| **Theme .md files** | Bash (grep) | Verify color codes, structure |
| **marketplace.json** | Bash (jq, python) | Parse and validate JSON schema |
| **Prompt output** | Bash (grep) | Verify 4-block structure, no pt/px |
| **Image generation** | Bash (python) | Run script, check exit code and output |

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
└── Task 1: ${CLAUDE_PLUGIN_ROOT} 검증 (blocker)

Wave 2 (After Wave 1):
├── Task 2: 테마 데이터 이관 (references/themes/)
└── Task 3: layout-types 스킬 유지 확인

Wave 3 (After Wave 2):
├── Task 4: orchestrator.md 생성
├── Task 5: content-organizer.md 생성
├── Task 6: content-reviewer.md 생성
├── Task 7: prompt-designer.md 생성
└── Task 8: renderer-agent.md 생성

Wave 4 (After Wave 3):
└── Task 9: 신규 테마 생성 (whatif, pitch, comparison)

Wave 5 (After Wave 4):
├── Task 10: marketplace.json 업데이트
└── Task 11: 기존 스킬 삭제

Wave 6 (Final):
└── Task 12: 엔드투엔드 테스트
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2-12 | None |
| 2 | 1 | 4-9 | 3 |
| 3 | 1 | None | 2 |
| 4 | 2 | 10 | 5, 6, 7, 8 |
| 5 | 2 | 4 | 4, 6, 7, 8 |
| 6 | 2 | 4 | 4, 5, 7, 8 |
| 7 | 2 | 4, 9 | 4, 5, 6, 8 |
| 8 | 2 | 10 | 4, 5, 6, 7 |
| 9 | 7 | 10 | None |
| 10 | 4, 8, 9 | 12 | 11 |
| 11 | 10 | 12 | 10 |
| 12 | 10, 11 | None | None |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1 | delegate_task(category="quick", load_skills=[], ...) |
| 2 | 2, 3 | delegate_task(category="unspecified-low", load_skills=[], ...) |
| 3 | 4-8 | delegate_task(category="writing", load_skills=[], ...) |
| 4 | 9 | delegate_task(category="writing", load_skills=[], ...) |
| 5 | 10, 11 | delegate_task(category="quick", load_skills=[], ...) |
| 6 | 12 | delegate_task(category="unspecified-high", load_skills=[], ...) |

---

## TODOs

---

### - [x] 1. ${CLAUDE_PLUGIN_ROOT} 변수 검증

**What to do**:
- Claude Code 문서에서 agent 파일 내 ${CLAUDE_PLUGIN_ROOT} 사용 가능 여부 재확인
- 테스트용 간단한 agent 파일 생성하여 스크립트 경로 참조 테스트
- 불가능할 경우 대안 방안 수립 (환경변수, 상대경로 등)

**Must NOT do**:
- 실제 플러그인 구조 변경 (검증만)

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: 단순 검증 작업, 1개 파일 테스트
- **Skills**: `[]`
  - 필요 없음

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 1 (standalone)
- **Blocks**: Tasks 2-12 (전체 계획의 전제조건)
- **Blocked By**: None

**References**:
- `https://code.claude.com/docs/en/skills` - SKILL.md 내 스크립트 참조 방법
- `https://code.claude.com/docs/en/plugin-marketplaces` - ${CLAUDE_PLUGIN_ROOT} 사용 예시

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: ${CLAUDE_PLUGIN_ROOT} 변수가 agent 파일에서 해석되는지 확인
  Tool: Bash
  Preconditions: 없음
  Steps:
    1. Claude Code 공식 문서에서 agent 파일 내 변수 사용 예시 검색
    2. 검색 결과 분석
    3. 가능/불가능 판정
  Expected Result: 사용 가능 여부 명확히 판정
  Evidence: 문서 발췌 또는 테스트 결과 캡처

Scenario: 대안 방안 수립 (불가능 시)
  Tool: Bash
  Preconditions: ${CLAUDE_PLUGIN_ROOT} 사용 불가 확정
  Steps:
    1. 환경변수 기반 경로 전달 방안 검토
    2. 상대경로 + symlink 방안 검토
    3. 선택된 대안 문서화
  Expected Result: 대안 방안 1개 이상 확보
  Evidence: 대안 방안 설명 기록
```

**Commit**: NO

---

### - [x] 2. 테마 데이터 이관 (references/themes/)

**What to do**:
- `references/themes/` 디렉토리 생성
- 스킬별 테마 파일 생성 (3개):
  - `gov.md`: prompt-gov 스킬의 9개 무드 테마 이관 (technical-report, growth, clarity, connection, innovation, tech-focus, knowledge, presentation, workshop)
  - `seminar.md`: prompt-seminar 스킬의 9개 무드 테마 이관
  - `concept.md`: prompt-concept 스킬의 9개 무드 테마 이관
- 각 파일에 9개 무드 테마 × 4색 팔레트 (주조/보조/강조/배경) 포함
- 각 무드별 적용 맥락 및 스타일 노트 포함

**Must NOT do**:
- 색상 HEX 코드 변경
- 무드 테마 수 변경 (각 파일 9개 유지)
- 스타일 규칙 변경

**Recommended Agent Profile**:
- **Category**: `unspecified-low`
  - Reason: 데이터 마이그레이션, 복잡한 로직 없음
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Task 3)
- **Blocks**: Tasks 4-9
- **Blocked By**: Task 1

**References**:
- `plugins/visual-generator/skills/prompt-concept/SKILL.md:482-627` - 9개 테마 정의
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:208-287` - gov 테마 정의
- `plugins/visual-generator/skills/prompt-seminar/SKILL.md:559-696` - seminar 테마 정의

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: 테마 디렉토리 및 파일 생성 확인
  Tool: Bash
  Preconditions: Task 1 완료
  Steps:
    1. ls -la plugins/visual-generator/references/themes/
    2. Assert: gov.md, seminar.md, concept.md 존재
  Expected Result: 3개 스킬별 테마 파일 존재
  Evidence: ls 출력 결과

Scenario: 테마 파일 색상 코드 검증 (각 파일에 9개 무드 × 4색)
  Tool: Bash
  Preconditions: 테마 파일 생성됨
  Steps:
    1. for f in gov seminar concept; do
         count=$(grep -c "#[0-9A-Fa-f]\{6\}" plugins/visual-generator/references/themes/${f}.md)
         echo "${f}.md: ${count} colors"
         if [ "$count" -lt 36 ]; then echo "FAIL: ${f}.md has less than 36 colors"; exit 1; fi
       done
    2. Assert: 각 파일 최소 36개 HEX 코드 (9 무드 × 4 색상)
  Expected Result: 각 테마 파일에 36개 이상 색상 코드 포함
  Evidence: grep 출력 결과

Scenario: 무드 테마 섹션 검증
  Tool: Bash
  Preconditions: 테마 파일 생성됨
  Steps:
    1. grep -c "#### 테마 [0-9]" plugins/visual-generator/references/themes/gov.md
    2. Assert: 9개 (9개 무드 테마 섹션)
  Expected Result: 9개 무드 테마 섹션 존재
  Evidence: grep 출력 결과
```

**Commit**: YES
- Message: `feat(visual-generator): migrate theme data to references/themes/`
- Files: `plugins/visual-generator/references/themes/*.md`
- Pre-commit: `ls plugins/visual-generator/references/themes/`

---

### - [x] 3. layout-types 스킬 유지 확인

**What to do**:
- `skills/layout-types/SKILL.md` 파일 존재 확인
- 24개 레이아웃 타입 완전성 검증
- 향후 agent 파일에서 참조 가능하도록 경로 확인

**Must NOT do**:
- layout-types 내용 수정
- 파일 위치 변경

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: 단순 검증 작업
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Task 2)
- **Blocks**: None
- **Blocked By**: Task 1

**References**:
- `plugins/visual-generator/skills/layout-types/SKILL.md` - 24종 레이아웃 정의

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: layout-types 스킬 존재 확인
  Tool: Bash
  Preconditions: 없음
  Steps:
    1. test -f plugins/visual-generator/skills/layout-types/SKILL.md && echo "EXISTS"
    2. Assert: "EXISTS" 출력
  Expected Result: 파일 존재 확인
  Evidence: test 명령 출력

Scenario: 24개 레이아웃 타입 완전성 검증
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "^## [0-9]" plugins/visual-generator/skills/layout-types/SKILL.md
    2. Assert: 24 출력
  Expected Result: 24개 레이아웃 섹션 존재
  Evidence: grep 출력 결과
```

**Commit**: NO

---

### - [x] 4. orchestrator.md Agent 생성

**What to do**:
- `agents/orchestrator.md` 파일 생성
- 역할: 전체 워크플로우 조율 (content-organizer → content-reviewer → prompt-designer → renderer-agent)
- 입력 스키마 정의 (입력 문서, 테마 선택, 레이아웃 선택, 출력 폴더)
- auto_mode=true로 자동 파이프라인 실행
- 에러 핸들링 및 롤백 로직 포함

**Must NOT do**:
- 직접 프롬프트 생성
- 직접 이미지 렌더링
- 테마/레이아웃 선택 (content-organizer 역할)

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Agent 정의 문서 작성
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Tasks 5-8)
- **Blocks**: Task 10
- **Blocked By**: Task 2

**References**:
- `plugins/isd-generator/agents/orchestrator.md` - 유사한 orchestrator 패턴
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:38-58` - 워크플로우 Phase 구조 참조

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: orchestrator.md 파일 생성 확인
  Tool: Bash
  Preconditions: Task 2 완료
  Steps:
    1. test -f plugins/visual-generator/agents/orchestrator.md && echo "EXISTS"
    2. Assert: "EXISTS" 출력
  Expected Result: 파일 존재
  Evidence: test 명령 출력

Scenario: orchestrator frontmatter 검증
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. head -20 plugins/visual-generator/agents/orchestrator.md
    2. grep -c "name:\|description:\|tools:" 출력에서
    3. Assert: 3개 이상 필드 존재
  Expected Result: 유효한 frontmatter
  Evidence: grep 출력

Scenario: 워크플로우 단계 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "content-organizer\|content-reviewer\|prompt-designer\|renderer-agent" plugins/visual-generator/agents/orchestrator.md
    2. Assert: 4개 이상 (각 에이전트 최소 1회 언급)
  Expected Result: 4개 sub-agent 참조
  Evidence: grep 출력
```

**Commit**: YES (groups with 5, 6, 7, 8)
- Message: `feat(visual-generator): add multi-agent orchestrator`
- Files: `plugins/visual-generator/agents/orchestrator.md`
- Pre-commit: `head -10 plugins/visual-generator/agents/orchestrator.md`

---

### - [x] 5. content-organizer.md Agent 생성

**What to do**:
- `agents/content-organizer.md` 파일 생성
- 역할: 입력 문서 분석, 핵심 개념 추출, 테마 선택, 레이아웃 선택
- 입력: 원본 문서 또는 토픽
- 출력: 구조화된 content-analysis 객체 (개념 목록, 선택된 테마, 선택된 레이아웃)
- 6개 테마 참조 (`references/themes/*.md`)

**Must NOT do**:
- 프롬프트 텍스트 생성
- 검토/피드백 제공 (content-reviewer 역할)
- 이미지 렌더링

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Agent 정의 문서 작성
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Tasks 4, 6, 7, 8)
- **Blocks**: Task 4
- **Blocked By**: Task 2

**References**:
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:40-58` - Phase 1: 문서 분석 워크플로우
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:60-76` - Phase 2: 테마 선택 로직
- `plugins/visual-generator/skills/layout-types/SKILL.md` - 24종 레이아웃 선택 기준

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: content-organizer.md 파일 생성 확인
  Tool: Bash
  Preconditions: Task 2 완료
  Steps:
    1. test -f plugins/visual-generator/agents/content-organizer.md && echo "EXISTS"
  Expected Result: 파일 존재
  Evidence: test 명령 출력

Scenario: 테마 참조 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "references/themes" plugins/visual-generator/agents/content-organizer.md
    2. Assert: 1개 이상
  Expected Result: 테마 디렉토리 참조
  Evidence: grep 출력

Scenario: 출력 구조 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "테마\|레이아웃\|개념" plugins/visual-generator/agents/content-organizer.md
    2. Assert: 6개 이상 (각 요소 2회 이상 언급)
  Expected Result: 핵심 출력 요소 정의
  Evidence: grep 출력
```

**Commit**: YES (groups with 4, 6, 7, 8)
- Message: `feat(visual-generator): add content-organizer agent`
- Files: `plugins/visual-generator/agents/content-organizer.md`

---

### - [x] 6. content-reviewer.md Agent 생성

**What to do**:
- `agents/content-reviewer.md` 파일 생성
- 역할: content-organizer 출력 검토, 피드백 제공
- 검토 항목: 개념 추출 적절성, 테마 선택 적합성, 레이아웃 선택 적합성
- 통과/반려 결정 및 피드백 제공

**Must NOT do**:
- 직접 content 수정 (피드백만)
- 프롬프트 생성
- 렌더링 방지 검증 (final-reviewer/renderer-agent 역할)

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Agent 정의 문서 작성
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Tasks 4, 5, 7, 8)
- **Blocks**: Task 4
- **Blocked By**: Task 2

**References**:
- `plugins/investments-portfolio/agents/macro-critic.md` - 유사한 reviewer 패턴

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: content-reviewer.md 파일 생성 확인
  Tool: Bash
  Preconditions: Task 2 완료
  Steps:
    1. test -f plugins/visual-generator/agents/content-reviewer.md && echo "EXISTS"
  Expected Result: 파일 존재
  Evidence: test 명령 출력

Scenario: 검토 기준 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "검토\|피드백\|통과\|반려" plugins/visual-generator/agents/content-reviewer.md
    2. Assert: 4개 이상
  Expected Result: 검토 로직 정의
  Evidence: grep 출력
```

**Commit**: YES (groups with 4, 5, 7, 8)
- Message: `feat(visual-generator): add content-reviewer agent`
- Files: `plugins/visual-generator/agents/content-reviewer.md`

---

### - [x] 7. prompt-designer.md Agent 생성

**What to do**:
- `agents/prompt-designer.md` 파일 생성
- 역할: 4-block 프롬프트 생성 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN)
- 입력: content-organizer 출력 (개념, 테마, 레이아웃)
- 테마별 색상 팔레트 적용 (`references/themes/*.md` 참조)
- 텍스트 밀도 규칙 적용 (gov: 25개, concept: 15개, seminar: 30개)
- 렌더링 방지 규칙 적용 (pt/px 금지, 언어 병기 금지)

**Must NOT do**:
- 테마/레이아웃 선택 (이미 결정됨)
- 최종 검증 (renderer-agent 역할)
- 이미지 렌더링

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Agent 정의 문서 작성, 가장 복잡한 로직 포함
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Tasks 4, 5, 6, 8)
- **Blocks**: Tasks 4, 9
- **Blocked By**: Task 2

**References**:
- `plugins/visual-generator/skills/prompt-concept/SKILL.md:120-189` - 프롬프트 구조 정의
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:85-127` - 4-block 형식
- `plugins/visual-generator/skills/prompt-gov/SKILL.md:289-324` - 텍스트 등급 및 렌더링 방지 체크리스트

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: prompt-designer.md 파일 생성 확인
  Tool: Bash
  Preconditions: Task 2 완료
  Steps:
    1. test -f plugins/visual-generator/agents/prompt-designer.md && echo "EXISTS"
  Expected Result: 파일 존재
  Evidence: test 명령 출력

Scenario: 4-block 구조 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "INSTRUCTION\|CONFIGURATION\|CONTENT\|FORBIDDEN" plugins/visual-generator/agents/prompt-designer.md
    2. Assert: 4개 이상
  Expected Result: 4-block 구조 참조
  Evidence: grep 출력

Scenario: 렌더링 방지 규칙 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "pt\|px\|병기\|금지" plugins/visual-generator/agents/prompt-designer.md
    2. Assert: 4개 이상
  Expected Result: 렌더링 방지 규칙 포함
  Evidence: grep 출력

Scenario: 텍스트 밀도 규칙 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "25\|15\|30" plugins/visual-generator/agents/prompt-designer.md
    2. Assert: 3개 이상 (각 테마별 밀도)
  Expected Result: 테마별 텍스트 밀도 정의
  Evidence: grep 출력
```

**Commit**: YES (groups with 4, 5, 6, 8)
- Message: `feat(visual-generator): add prompt-designer agent`
- Files: `plugins/visual-generator/agents/prompt-designer.md`

---

### - [x] 8. renderer-agent.md Agent 생성

**What to do**:
- `agents/renderer-agent.md` 파일 생성
- 역할: 최종 검증 (렌더링 방지 검증) + 이미지 렌더링
- 최종 검증: 4-block 구조, pt/px 패턴, 언어 병기 검사
- 스크립트 호출: `${CLAUDE_PLUGIN_ROOT}/scripts/generate_slide_images.py` 사용
- 에러 핸들링: 재시도 로직, 실패 보고

**Must NOT do**:
- 프롬프트 수정 (플래그만)
- 테마/레이아웃 선택

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Agent 정의 문서 작성
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Tasks 4, 5, 6, 7)
- **Blocks**: Task 10
- **Blocked By**: Task 2

**References**:
- `plugins/visual-generator/skills/renderer/SKILL.md` - 기존 renderer 워크플로우
- `plugins/visual-generator/scripts/generate_slide_images.py` - Python 스크립트 API

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: renderer-agent.md 파일 생성 확인
  Tool: Bash
  Preconditions: Task 2 완료
  Steps:
    1. test -f plugins/visual-generator/agents/renderer-agent.md && echo "EXISTS"
  Expected Result: 파일 존재
  Evidence: test 명령 출력

Scenario: ${CLAUDE_PLUGIN_ROOT} 경로 참조 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "CLAUDE_PLUGIN_ROOT" plugins/visual-generator/agents/renderer-agent.md
    2. Assert: 1개 이상
  Expected Result: 경로 변수 사용
  Evidence: grep 출력

Scenario: 최종 검증 로직 정의 확인
  Tool: Bash
  Preconditions: 파일 존재
  Steps:
    1. grep -c "검증\|4-block\|pt\|px" plugins/visual-generator/agents/renderer-agent.md
    2. Assert: 4개 이상
  Expected Result: 검증 로직 포함
  Evidence: grep 출력
```

**Commit**: YES (groups with 4, 5, 6, 7)
- Message: `feat(visual-generator): add renderer-agent with final validation`
- Files: `plugins/visual-generator/agents/renderer-agent.md`

---

### - [x] 9. 신규 테마 생성 (whatif, pitch, comparison)

**What to do**:
- 3개 신규 용도별 테마 파일 생성 (기존 스킬별 테마와 다른 목적):
- `references/themes/whatif.md` 생성
  - 용도: 시나리오 시뮬레이션 - 제안 내용이 구현된 장면 + 설명 오버레이
  - 4색 팔레트 정의 (주조/보조/강조/배경)
  - 적합 레이아웃 권장 (Section-Flow, Z-Pattern)
  - 스타일 노트 및 적합/부적합 케이스 포함
- `references/themes/pitch.md` 생성
  - 용도: Pitch Deck 스타일 - 문제→해결→시장→팀
  - 4색 팔레트 정의
  - 간결하고 임팩트 있는 시각 요소
  - 핵심 숫자 강조 가이드
- `references/themes/comparison.md` 생성
  - 용도: Before/After 비교 레이아웃
  - 4색 팔레트 정의
  - 나란히 배치, 차이점 강조
  - 대비 메타포 권장

**참고**: 신규 테마 파일은 "무드 테마 9개 포함" 형식이 아닌 "단일 용도 테마" 형식임

**Must NOT do**:
- 기존 테마 파일(gov.md, seminar.md, concept.md) 수정
- 4개 이상 신규 테마 추가

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: 테마 정의 문서 작성
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4 (sequential)
- **Blocks**: Task 10
- **Blocked By**: Task 7

**References**:
- `plugins/visual-generator/references/themes/concept.md` (Task 2에서 생성) - 테마 파일 구조 참조
- `plugins/visual-generator/skills/layout-types/SKILL.md:119-154` - 대비 메타포 (comparison용)
- `plugins/visual-generator/skills/layout-types/SKILL.md:492-526` - Section-Flow 메타포 (whatif용)
- `plugins/visual-generator/skills/layout-types/SKILL.md:792-827` - Z-Pattern 메타포 (pitch용)

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: 3개 신규 테마 파일 생성 확인
  Tool: Bash
  Preconditions: Task 7 완료
  Steps:
    1. ls plugins/visual-generator/references/themes/
    2. Assert: whatif.md, pitch.md, comparison.md 존재
  Expected Result: 3개 신규 테마 파일 존재
  Evidence: ls 출력

Scenario: 신규 테마 색상 팔레트 확인 (각 파일 4색)
  Tool: Bash
  Preconditions: 파일 생성됨
  Steps:
    1. for f in whatif pitch comparison; do
         count=$(grep -c "#[0-9A-Fa-f]\{6\}" plugins/visual-generator/references/themes/${f}.md)
         echo "${f}.md: ${count} colors"
         if [ "$count" -lt 4 ]; then echo "FAIL: ${f}.md has less than 4 colors"; exit 1; fi
       done
    2. Assert: 각 파일 최소 4개 색상 코드 (단일 용도 테마의 4색 팔레트)
  Expected Result: 각 신규 테마 파일에 4색 팔레트 정의
  Evidence: grep 출력

Scenario: whatif 테마 권장 레이아웃 확인
  Tool: Bash
  Preconditions: whatif.md 존재
  Steps:
    1. grep -c "Section-Flow\|Z-Pattern" plugins/visual-generator/references/themes/whatif.md
    2. Assert: 1개 이상
  Expected Result: 권장 레이아웃 명시
  Evidence: grep 출력
```

**Commit**: YES
- Message: `feat(visual-generator): add 3 new themes (whatif, pitch, comparison)`
- Files: `plugins/visual-generator/references/themes/whatif.md`, `pitch.md`, `comparison.md`

---

### - [x] 10. marketplace.json 업데이트

**What to do**:
- `.claude-plugin/marketplace.json`에서 visual-generator 플러그인 정의 수정
- `skills` 배열 → `agents` 배열로 변경
- 5개 agent 파일 경로 추가
- `skills` 배열에 layout-types만 유지
- version 업데이트 (1.0.0 → 2.0.0)

**Must NOT do**:
- 다른 플러그인 항목 수정

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: JSON 파일 단순 수정
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 5 (with Task 11)
- **Blocks**: Task 12
- **Blocked By**: Tasks 4, 8, 9

**References**:
- `.claude-plugin/marketplace.json:37-53` - 현재 visual-generator 정의
- `https://code.claude.com/docs/en/plugin-marketplaces` - marketplace.json 스키마

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: marketplace.json 유효성 검증
  Tool: Bash
  Preconditions: Tasks 4, 8, 9 완료
  Steps:
    1. python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"
    2. Assert: Exit code 0
  Expected Result: 유효한 JSON
  Evidence: 명령 출력

Scenario: visual-generator agents 배열 확인
  Tool: Bash
  Preconditions: JSON 유효
  Steps:
    1. grep -A 20 '"visual-generator"' .claude-plugin/marketplace.json | grep -c "agents"
    2. Assert: 1개
  Expected Result: agents 배열 존재
  Evidence: grep 출력

Scenario: 5개 agent 경로 확인
  Tool: Bash
  Preconditions: JSON 유효
  Steps:
    1. grep -A 30 '"visual-generator"' .claude-plugin/marketplace.json | grep -c "./agents/"
    2. Assert: 5개
  Expected Result: 5개 agent 경로
  Evidence: grep 출력

Scenario: skills 배열에 layout-types만 존재 확인
  Tool: Bash
  Preconditions: JSON 유효
  Steps:
    1. grep -A 30 '"visual-generator"' .claude-plugin/marketplace.json | grep '"skills"' -A 3
    2. Assert: layout-types 포함, prompt-* 미포함
  Expected Result: skills에 layout-types만
  Evidence: grep 출력
```

**Commit**: YES
- Message: `chore(marketplace): update visual-generator to agent architecture`
- Files: `.claude-plugin/marketplace.json`

---

### - [x] 11. 기존 스킬 삭제

**What to do**:
- `skills/prompt-concept/` 디렉토리 삭제
- `skills/prompt-gov/` 디렉토리 삭제
- `skills/prompt-seminar/` 디렉토리 삭제
- `skills/renderer/` 디렉토리 삭제
- `skills/layout-types/` 유지

**Must NOT do**:
- layout-types 삭제
- references/ 삭제

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: 파일 삭제만
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 5 (with Task 10)
- **Blocks**: Task 12
- **Blocked By**: Task 10

**References**:
- `plugins/visual-generator/skills/` - 현재 디렉토리 구조

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: 기존 스킬 삭제 확인
  Tool: Bash
  Preconditions: Task 10 완료
  Steps:
    1. ls plugins/visual-generator/skills/
    2. Assert: prompt-concept, prompt-gov, prompt-seminar, renderer 미존재
  Expected Result: 4개 스킬 삭제됨
  Evidence: ls 출력

Scenario: layout-types 유지 확인
  Tool: Bash
  Preconditions: 삭제 완료
  Steps:
    1. test -d plugins/visual-generator/skills/layout-types && echo "EXISTS"
    2. Assert: "EXISTS"
  Expected Result: layout-types 유지
  Evidence: test 출력
```

**Commit**: YES
- Message: `refactor(visual-generator): remove legacy skills, keep layout-types`
- Files: `plugins/visual-generator/skills/` (삭제 기록)

---

### - [x] 12. 엔드투엔드 테스트

**What to do**:
- 테스트 입력 문서 준비 (간단한 연구 개요)
- orchestrator를 통해 전체 파이프라인 실행
- 생성된 프롬프트 검증: 4-block 구조, pt/px 없음, 언어 병기 없음
- Gemini API를 통해 이미지 생성 (GEMINI_API_KEY 필요)
- 최종 이미지 파일 존재 확인

**Must NOT do**:
- 테스트 실패 시 계획 외 수정

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: 전체 파이프라인 테스트, 외부 API 호출
- **Skills**: `[]`

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 6 (final)
- **Blocks**: None
- **Blocked By**: Tasks 10, 11

**References**:
- `plugins/visual-generator/agents/orchestrator.md` (Task 4에서 생성)
- `plugins/visual-generator/scripts/generate_slide_images.py`

**Acceptance Criteria**:

**Agent-Executed QA Scenarios:**

```
Scenario: 테스트 프롬프트 생성
  Tool: Bash
  Preconditions: Tasks 10, 11 완료
  Steps:
    1. @visual-generator orchestrator로 테스트 입력 처리
    2. ls test_output/prompts/*.md
    3. Assert: 최소 1개 프롬프트 파일 존재
  Expected Result: 프롬프트 파일 생성
  Evidence: ls 출력

Scenario: 프롬프트 4-block 구조 검증
  Tool: Bash
  Preconditions: 프롬프트 생성됨
  Steps:
    1. for f in test_output/prompts/*.md; do
         blocks=$(grep -c "INSTRUCTION BLOCK\|CONFIGURATION BLOCK\|CONTENT BLOCK\|FORBIDDEN ELEMENTS" "$f")
         if [ "$blocks" -ne 4 ]; then echo "FAIL: $f"; exit 1; fi
       done
    2. echo "PASS"
  Expected Result: 모든 프롬프트 4-block 구조
  Evidence: 스크립트 출력

Scenario: 렌더링 방지 검증 (pt/px 없음)
  Tool: Bash
  Preconditions: 프롬프트 생성됨
  Steps:
    1. grep -E "[0-9]+pt|[0-9]+px" test_output/prompts/*.md || echo "PASS"
    2. Assert: "PASS" 또는 빈 출력
  Expected Result: pt/px 패턴 없음
  Evidence: grep 출력

Scenario: Gemini API 이미지 생성
  Tool: Bash
  Preconditions: GEMINI_API_KEY 설정됨, 프롬프트 존재
  Steps:
    1. python plugins/visual-generator/scripts/generate_slide_images.py \
         --prompts-dir test_output/prompts \
         --output-dir test_output/figures
    2. Assert: Exit code 0
    3. ls test_output/figures/*.png
    4. Assert: 최소 1개 PNG 존재
  Expected Result: 이미지 생성 성공
  Evidence: 스크립트 출력, ls 출력

Scenario: 최종 파일 구조 검증
  Tool: Bash
  Preconditions: 모든 테스트 완료
  Steps:
    1. tree plugins/visual-generator/
    2. Assert: agents/ (5개), skills/layout-types/, references/themes/ (6개), scripts/ 존재
  Expected Result: 예상 구조 일치
  Evidence: tree 출력
```

**Commit**: NO (테스트 결과물은 커밋하지 않음)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 2 | `feat(visual-generator): migrate theme data to references/themes/` | references/themes/*.md | ls -la |
| 4-8 | `feat(visual-generator): add multi-agent architecture` | agents/*.md | head -10 each file |
| 9 | `feat(visual-generator): add 3 new themes (whatif, pitch, comparison)` | references/themes/whatif.md, pitch.md, comparison.md | ls -la |
| 10 | `chore(marketplace): update visual-generator to agent architecture` | .claude-plugin/marketplace.json | python -c "import json; ..." |
| 11 | `refactor(visual-generator): remove legacy skills, keep layout-types` | skills/ | ls skills/ |

---

## Success Criteria

### Verification Commands
```bash
# 1. Agent 파일 존재 확인
ls plugins/visual-generator/agents/
# Expected: orchestrator.md, content-organizer.md, content-reviewer.md, prompt-designer.md, renderer-agent.md

# 2. 테마 파일 존재 확인
ls plugins/visual-generator/references/themes/
# Expected: gov.md, seminar.md, concept.md, whatif.md, pitch.md, comparison.md

# 3. marketplace.json 유효성
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print('valid')"
# Expected: valid

# 4. 기존 스킬 삭제 확인
ls plugins/visual-generator/skills/
# Expected: layout-types only

# 5. 엔드투엔드 테스트 (API 키 필요)
python plugins/visual-generator/scripts/generate_slide_images.py --prompts-dir test_output/prompts --output-dir test_output/figures && ls test_output/figures/*.png
# Expected: At least 1 PNG file
```

### Final Checklist
- [ ] 5개 Agent 파일 생성됨
- [ ] 6개 테마 파일 존재 (3 기존 + 3 신규)
- [ ] marketplace.json 업데이트됨
- [ ] 기존 prompt-*/renderer 스킬 삭제됨
- [ ] layout-types 스킬 유지됨
- [ ] 엔드투엔드 테스트 통과
- [ ] 모든 프롬프트 4-block 구조 유지
- [ ] pt/px 패턴 없음 검증됨
