# Visual-Generator 플러그인 구조 개선

## TL;DR

> **Quick Summary**: visual-generator 플러그인의 에이전트 간 오케스트레이션이 실패하는 근본 원인 6가지를 수정한다. 검증 패턴 불일치, 도구 누락, 양식 강제 규칙 부재, 위임 강제 규칙 부재, Workflow Position 누락, 그리고 오케스트레이터의 commands/ 이동을 포함한다.
> 
> **Deliverables**:
> - marketplace.json visual-generator 항목 업데이트 (commands 배열 추가, agents 배열에서 orchestrator 제거)
> - orchestrator.md → commands/visual-generate.md 이동 + 위임 강제 규칙 추가
> - content-reviewer.md에 Write 도구 추가 + Workflow Position 추가
> - renderer-agent.md 검증 패턴 4개 모두 수정 + Workflow Position 추가
> - prompt-designer.md 양식 강제 규칙 추가 + 문서 헤딩 일관성 수정 + Workflow Position 추가
> - content-organizer.md에 Workflow Position 추가
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 (commands/ 검증) → Task 2 (marketplace.json + 오케스트레이터 이동) → Task 3-6 (에이전트 수정 병렬)

---

## Context

### Original Request
visual-generator 플러그인에서 에이전트 간 오케스트레이션이 작동하지 않는 문제를 해결하기 위해 6가지 구조적 개선을 수행한다. 참조 레포(wshobson/agents)의 설계 패턴(commands 디렉토리, Workflow Position)을 적용한다.

### Interview Summary
**Key Discussions**:
- `strict: true → false` 변경은 **제외**. 모든 에이전트의 도구 접근을 무분별하게 열어버리는 과도한 변경. content-reviewer에 Write 추가가 정확한 수정
- `commands/` 이동은 **포함**하되, Claude Code 플러그인 시스템에서 commands 키를 지원하는지 먼저 검증
- 테마 참조 파일(`references/themes/*.md`)은 수정 범위 제외

**Research Findings**:
- marketplace.json: `"strict": true` (line 51), agents 배열에 orchestrator.md 포함
- content-reviewer.md: `tools: Read, Glob, Grep` — Write 누락 (line 4)
- renderer-agent.md: 3개 블록의 검증 패턴 불일치 (INSTRUCTION BLOCK, CONFIGURATION BLOCK, CONTENT BLOCK) — FORBIDDEN ELEMENTS만 일치
- prompt-designer.md: 문서 헤딩 (lines 35, 56, 83, 108)이 "Block 1: INSTRUCTION BLOCK" 형식이나 실제 출력은 `## INSTRUCTION` — 내부 불일치
- renderer-agent.md에만 `파이프라인 위치:` 섹션 누락
- `commands/` 디렉토리는 honeypot 프로젝트 전체에서 한 번도 사용된 적 없음

### Metis Review
**Identified Gaps** (addressed):
- 검증 패턴 불일치가 4개 블록 중 3개(INSTRUCTION, CONFIGURATION, CONTENT)로 원래 분석보다 범위 넓음 → 4개 모두 수정
- prompt-designer 내부 문서 헤딩(line 35, 56, 83, 108)도 "BLOCK" 접미사 불일치 → 문서 헤딩도 수정
- renderer-agent에만 파이프라인 위치 섹션 누락 → Workflow Position 추가
- `commands/` 지원 여부 미검증 위험 → Task 1에서 선행 검증 후 조건부 진행
- `strict: false`는 과도한 변경 → 사용자 결정으로 제외

---

## Work Objectives

### Core Objective
visual-generator 플러그인의 에이전트 간 파이프라인(content-organizer → content-reviewer → prompt-designer → renderer-agent)이 오케스트레이터에 의해 정상적으로 위임·실행되도록 구조적 결함을 수정한다.

### Concrete Deliverables
- `marketplace.json`: visual-generator 항목에 commands 배열 추가, agents 배열에서 orchestrator.md 제거
- `commands/visual-generate.md`: 이동된 오케스트레이터 + 위임 강제 규칙
- `agents/content-reviewer.md`: Write 도구 추가 + Workflow Position
- `agents/renderer-agent.md`: 4개 검증 패턴 수정 + grep 명령어 수정 + Workflow Position
- `agents/prompt-designer.md`: 양식 강제 규칙 + 문서 헤딩 일관성 + Workflow Position
- `agents/content-organizer.md`: Workflow Position

### Definition of Done
- [x] content-reviewer가 review_result.md를 Write 도구로 작성 가능
- [x] renderer-agent 검증이 prompt-designer 출력 포맷과 100% 일치
- [x] 모든 에이전트에 Workflow Position 섹션 존재
- [x] 오케스트레이터가 직접 작업 수행 금지 규칙 명시
- [x] marketplace.json이 유효한 JSON이며 모든 참조 파일 존재

### Must Have
- content-reviewer.md에 Write 도구 추가
- renderer-agent.md의 4개 블록 검증 패턴 모두 수정
- prompt-designer.md에 출력 포맷 강제 규칙 추가
- 오케스트레이터에 위임 강제 규칙 추가
- 4개 서브에이전트 모두에 Workflow Position 섹션

### Must NOT Have (Guardrails)
- `strict: true → false` 변경 금지 (사용자 결정으로 제외)
- 테마 참조 파일(`references/themes/*.md`) 수정 금지
- `scripts/generate_slide_images.py` 수정 금지
- visual-generator 외 다른 플러그인 수정 금지
- 4-phase 파이프라인 행동 변경 금지 (content-organizer → content-reviewer → prompt-designer → renderer-agent 순서 유지)
- Workflow Position 추가 시 기존 `파이프라인 위치:` 섹션 삭제 금지 — 기존 섹션은 유지하고 새 섹션을 추가

---

## Verification Strategy

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None (마크다운 에이전트 정의 파일 수정)
- **Framework**: none

### Agent-Executed QA (Simplified)
모든 검증은 grep 및 JSON 파싱 명령어로 수행한다. 각 Task별 Acceptance Criteria에 구체적 검증 명령어 포함.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
└── Task 1: commands/ 디렉토리 지원 여부 검증

Wave 2 (After Wave 1):
└── Task 2: marketplace.json 수정 + 오케스트레이터 이동 (Task 1 결과에 따라 조건부)

Wave 3 (After Wave 2):
├── Task 3: content-reviewer.md 수정
├── Task 4: renderer-agent.md 수정
├── Task 5: prompt-designer.md 수정
└── Task 6: content-organizer.md 수정

Critical Path: Task 1 → Task 2 → Tasks 3-6
Parallel Speedup: Wave 3에서 4개 파일 동시 수정
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2 | None |
| 2 | 1 | 3, 4, 5, 6 | None |
| 3 | 2 | None | 4, 5, 6 |
| 4 | 2 | None | 3, 5, 6 |
| 5 | 2 | None | 3, 4, 6 |
| 6 | 2 | None | 3, 4, 5 |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1 | delegate_task(category="quick", load_skills=[]) |
| 2 | 2 | delegate_task(category="quick", load_skills=[]) |
| 3 | 3, 4, 5, 6 | 4x delegate_task(category="quick", load_skills=[], run_in_background=true) |

---

## TODOs

- [x] 1. commands/ 디렉토리 지원 여부 검증

  **What to do**:
  - Claude Code의 marketplace.json 스키마에서 `"commands"` 키가 지원되는지 검증
  - 검증 방법 1: Claude Code 공식 문서에서 marketplace.json schema 확인 (웹 검색)
  - 검증 방법 2: 실험적으로 `commands/` 디렉토리와 `"commands"` 키를 marketplace.json에 추가한 후 플러그인 로드 테스트
  - 검증 방법 3: wshobson/agents 레포의 marketplace.json 구조 확인 (GitHub 접근)

  **조건부 분기**:
  - **commands 지원 확인됨**: Task 2를 commands/ 이동으로 진행
  - **commands 미지원 확인됨**: Task 2를 대안(오케스트레이터를 agents/에 유지하되 위임 강제 규칙만 추가)으로 진행. marketplace.json 변경 불필요.

  **Must NOT do**:
  - 검증 없이 commands/ 이동을 진행하지 않음
  - 다른 플러그인의 marketplace.json 항목 수정하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
    - 웹 검색과 파일 탐색만 필요
  - **Skills Evaluated but Omitted**:
    - `playwright`: 웹 문서 확인에 유용할 수 있으나, 웹 검색 도구로 충분

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (단독)
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `.claude-plugin/marketplace.json:38-60` - visual-generator 플러그인의 현재 등록 구조. "agents"와 "skills" 키만 사용됨. "commands" 키 추가 가능 여부 확인 필요

  **Documentation References**:
  - wshobson/agents GitHub 레포 — commands 패턴의 원본 참조. `commands/full-stack-feature.md` 형태로 오케스트레이터 등록

  **Acceptance Criteria**:

  - [ ] commands 키 지원 여부에 대한 결론 도출 (지원/미지원)
  - [ ] 결론에 따른 Task 2 진행 방향 결정
  - [ ] 검증 과정 및 결론을 `/home/cha/Documents/honeypot/.sisyphus/notepads/visual-generator-restructure/decisions.md`에 기록

  **Commit**: NO

---

- [x] 2. marketplace.json 수정 + 오케스트레이터 이동 (Task 1 결과에 따라 조건부)

  **What to do**:

  **경로 A: commands/ 지원 확인됨**:
  1. `plugins/visual-generator/commands/` 디렉토리 생성
  2. `plugins/visual-generator/agents/orchestrator.md` → `plugins/visual-generator/commands/visual-generate.md` 복사
  3. 이동된 파일의 내용 수정:
     - MUST NOT DO 섹션에 위임 강제 규칙 추가:
       ```
       - [ ] 직접 문서를 분석하지 않음 (content-organizer에 위임)
       - [ ] 직접 분석 결과를 검토하지 않음 (content-reviewer에 위임)
       - [ ] 직접 프롬프트를 생성하지 않음 (prompt-designer에 위임)
       - [ ] 직접 이미지를 렌더링하지 않음 (renderer-agent에 위임)
       - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
       ```
  4. marketplace.json 수정:
     - agents 배열에서 `"./agents/orchestrator.md"` 제거
     - `"commands": ["./commands/visual-generate.md"]` 추가
  5. 원본 `agents/orchestrator.md` 삭제
  6. marketplace.json이 유효한 JSON인지 검증

  **경로 B: commands/ 미지원 확인됨**:
  1. `plugins/visual-generator/agents/orchestrator.md` 직접 수정
  2. MUST NOT DO 섹션에 위임 강제 규칙 추가 (경로 A와 동일한 규칙)
  3. marketplace.json 변경 불필요

  **Must NOT do**:
  - strict: true를 false로 변경하지 않음
  - 다른 플러그인의 marketplace.json 항목 수정하지 않음
  - 오케스트레이터의 기존 워크플로우 로직 변경하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `git-master`: 파일 이동에 유용하나 단순 copy+delete로 충분

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (단독)
  - **Blocks**: Tasks 3, 4, 5, 6
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `.claude-plugin/marketplace.json:38-60` - visual-generator의 현재 agents 배열. 여기서 `"./agents/orchestrator.md"` 제거하고 commands 배열 추가
  - `plugins/visual-generator/agents/orchestrator.md:281-296` - 현재 MUST NOT DO 섹션. 위임 강제 규칙 추가할 위치

  **API/Type References**:
  - `.claude-plugin/marketplace.json` 전체 — JSON 구조 유지 필요

  **WHY Each Reference Matters**:
  - marketplace.json: 에이전트 등록의 단일 진실 소스. 파일 이동과 동시에 업데이트 필수
  - orchestrator.md MUST NOT DO: 기존 규칙에 위임 강제를 추가해야 하므로 현재 규칙 확인 필요

  **Acceptance Criteria**:

  **경로 A일 경우:**
  - [ ] `plugins/visual-generator/commands/visual-generate.md` 파일 존재
  - [ ] `plugins/visual-generator/agents/orchestrator.md` 파일 삭제됨
  - [ ] marketplace.json에서 visual-generator의 agents 배열에 orchestrator.md 없음: `grep "orchestrator" .claude-plugin/marketplace.json` → visual-generator 섹션에서 결과 없음
  - [ ] marketplace.json에 commands 배열 존재: `grep "commands" .claude-plugin/marketplace.json` → 결과 있음
  - [ ] marketplace.json 유효한 JSON: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"`
  - [ ] visual-generate.md MUST NOT DO에 위임 규칙: `grep "직접.*분석\|직접.*생성\|직접.*검토\|직접.*렌더링" plugins/visual-generator/commands/visual-generate.md` → 4개 이상 일치

  **경로 B일 경우:**
  - [ ] `plugins/visual-generator/agents/orchestrator.md` MUST NOT DO에 위임 규칙: `grep "직접.*분석\|직접.*생성\|직접.*검토\|직접.*렌더링" plugins/visual-generator/agents/orchestrator.md` → 4개 이상 일치
  - [ ] marketplace.json 변경 없음

  **Commit**: YES
  - Message: `fix(visual-generator): add delegation enforcement to orchestrator`
  - Files: marketplace.json, orchestrator 파일(경로에 따라 다름)
  - Pre-commit: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"`

---

- [x] 3. content-reviewer.md 수정: Write 도구 추가 + Workflow Position

  **What to do**:
  1. **frontmatter tools 수정** (line 4):
     - 변경 전: `tools: Read, Glob, Grep`
     - 변경 후: `tools: Read, Glob, Grep, Write`
  2. **Workflow Position 섹션 추가** — `## Overview` 섹션 직후, `## Input Schema` 직전에 추가:
     ```markdown
     ## Workflow Position
     - **After**: content-organizer (문서 분석 및 개념 추출 완료)
     - **Before**: prompt-designer (4-block 프롬프트 생성)
     - **Enables**: prompt-designer가 검증된 개념으로 프롬프트 생성 가능

     ## Key Distinctions
     - **vs content-organizer**: 콘텐츠를 직접 생성하지 않음. organizer의 출력물을 평가하고 피드백만 제공
     - **vs prompt-designer**: 프롬프트를 생성하지 않음. 개념/테마/레이아웃 선택의 적절성만 검토
     - **vs renderer-agent**: pt/px 단위나 이미지 렌더링 검증하지 않음. 콘텐츠 품질만 평가
     ```

  **Must NOT do**:
  - 기존 `파이프라인 위치:` 섹션(line 14-17) 삭제하지 않음
  - content-reviewer의 검토 기준이나 Decision Logic 변경하지 않음
  - tools에 Write 외 다른 도구 추가하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 마크다운 파일 수정이므로 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 4, 5, 6)
  - **Blocks**: None
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-reviewer.md:1-6` - 현재 frontmatter. line 4의 tools 필드 수정
  - `plugins/visual-generator/agents/content-reviewer.md:10-17` - 현재 Overview + 파이프라인 위치 섹션. Workflow Position 추가 위치
  - `plugins/visual-generator/agents/content-reviewer.md:174` - `Write(analysis_path/review_result.md)` 호출. Write 도구가 frontmatter에 있어야 이 호출이 성공

  **WHY Each Reference Matters**:
  - line 4: Write 도구 추가 대상
  - line 10-17: Workflow Position 삽입 위치 결정에 필요
  - line 174: Write 도구가 필요한 이유의 증거

  **Acceptance Criteria**:

  - [ ] frontmatter에 Write 포함: `grep "^tools:" plugins/visual-generator/agents/content-reviewer.md` → "Write" 포함
  - [ ] Workflow Position 섹션 존재: `grep "## Workflow Position" plugins/visual-generator/agents/content-reviewer.md` → 일치
  - [ ] Key Distinctions 섹션 존재: `grep "## Key Distinctions" plugins/visual-generator/agents/content-reviewer.md` → 일치
  - [ ] 기존 파이프라인 위치 유지: `grep "파이프라인 위치" plugins/visual-generator/agents/content-reviewer.md` → 일치

  **Commit**: YES (groups with Tasks 4, 5, 6)
  - Message: `fix(visual-generator): add Write tool to content-reviewer and Workflow Position to all agents`
  - Files: `plugins/visual-generator/agents/content-reviewer.md`, `plugins/visual-generator/agents/renderer-agent.md`, `plugins/visual-generator/agents/prompt-designer.md`, `plugins/visual-generator/agents/content-organizer.md`
  - Pre-commit: `grep "^tools:" plugins/visual-generator/agents/content-reviewer.md | grep Write`

---

- [x] 4. renderer-agent.md 수정: 4개 블록 검증 패턴 수정 + Workflow Position

  **What to do**:
  1. **Phase 2 검증 패턴 수정** (lines 53-56):
     - 변경 전:
       ```
       +-- Grep: "INSTRUCTION BLOCK" 존재 확인
       +-- Grep: "CONFIGURATION BLOCK" 존재 확인
       +-- Grep: "CONTENT BLOCK" 존재 확인
       +-- Grep: "FORBIDDEN ELEMENTS" 존재 확인
       ```
     - 변경 후:
       ```
       +-- Grep: "## INSTRUCTION" 존재 확인
       +-- Grep: "## CONFIGURATION" 존재 확인
       +-- Grep: "## CONTENT" 존재 확인
       +-- Grep: "## FORBIDDEN ELEMENTS" 존재 확인
       ```
  2. **Validation Checklist 테이블 수정** (line 132):
     - 검증 항목 #1의 검증 방법: `Grep 4개 블록 키워드` → `Grep "## INSTRUCTION", "## CONFIGURATION", "## CONTENT", "## FORBIDDEN ELEMENTS"`
  3. **검증 명령어 수정** (line 145):
     - 변경 전: `grep -c "INSTRUCTION BLOCK\|CONFIGURATION BLOCK\|CONTENT BLOCK\|FORBIDDEN ELEMENTS" prompt.md`
     - 변경 후: `grep -c "## INSTRUCTION\|## CONFIGURATION\|## CONTENT\|## FORBIDDEN ELEMENTS" prompt.md`
  4. **Workflow Position 섹션 추가** — renderer-agent.md에는 `파이프라인 위치:` 섹션이 없으므로 `## Overview` 직후, `## Input Schema` 직전에 추가:
     ```markdown
     **파이프라인 위치:**
     ```
     content-organizer → content-reviewer → prompt-designer → [renderer-agent]
     ```

     ## Workflow Position
     - **After**: prompt-designer (4-block 프롬프트 생성 완료)
     - **Before**: 없음 (최종 단계)
     - **Enables**: 최종 이미지 파일 출력

     ## Key Distinctions
     - **vs prompt-designer**: 프롬프트를 생성하지 않음. 생성된 프롬프트를 검증하고 이미지로 렌더링만 수행
     - **vs content-reviewer**: 콘텐츠 품질을 평가하지 않음. 기술적 형식(4-block 구조, 금지 패턴) 검증만 수행
     - **vs content-organizer**: 문서 분석하지 않음. 프롬프트 파일만 입력으로 받음
     ```

  **Must NOT do**:
  - renderer-agent의 렌더링 스크립트 호출 로직 변경하지 않음
  - 에러 처리/재시도 로직 변경하지 않음
  - pt/px, 언어 병기 등 기존 검증 항목(#2-#8) 변경하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 3, 5, 6)
  - **Blocks**: None
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/renderer-agent.md:50-57` - Phase 2 Step 2-1 검증 패턴. 4개 모두 수정 필요
  - `plugins/visual-generator/agents/renderer-agent.md:130-139` - Validation Checklist 테이블. 검증 항목 #1 설명 수정
  - `plugins/visual-generator/agents/renderer-agent.md:143-161` - 검증 명령어 예시. grep 명령어의 패턴 수정
  - `plugins/visual-generator/agents/prompt-designer.md:339-362` - prompt-designer의 실제 출력 포맷. renderer 검증 패턴이 이것과 일치해야 함

  **WHY Each Reference Matters**:
  - renderer-agent lines 50-57: 직접 수정 대상. "INSTRUCTION BLOCK" → "## INSTRUCTION" 등
  - renderer-agent line 145: grep 명령어 수정 대상. 이것이 실제 검증에 사용됨
  - prompt-designer lines 339-362: 검증 패턴이 일치해야 하는 대상. `## INSTRUCTION`, `## CONFIGURATION`, `## CONTENT`, `## FORBIDDEN ELEMENTS`

  **Acceptance Criteria**:

  - [ ] "INSTRUCTION BLOCK" 패턴 제거됨: `grep "INSTRUCTION BLOCK" plugins/visual-generator/agents/renderer-agent.md` → 결과 없음 (exit code 1)
  - [ ] "CONFIGURATION BLOCK" 패턴 제거됨: `grep "CONFIGURATION BLOCK" plugins/visual-generator/agents/renderer-agent.md` → 결과 없음
  - [ ] "CONTENT BLOCK" 패턴 제거됨: `grep "CONTENT BLOCK" plugins/visual-generator/agents/renderer-agent.md` → 결과 없음
  - [ ] 새 패턴 존재: `grep "## INSTRUCTION" plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] 새 패턴 존재: `grep "## CONFIGURATION" plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] 새 패턴 존재: `grep "## CONTENT" plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] grep 명령어 수정됨: `grep 'grep -c "## INSTRUCTION' plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] Workflow Position 존재: `grep "## Workflow Position" plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] Key Distinctions 존재: `grep "## Key Distinctions" plugins/visual-generator/agents/renderer-agent.md` → 일치
  - [ ] 파이프라인 위치 추가됨: `grep "파이프라인 위치" plugins/visual-generator/agents/renderer-agent.md` → 일치

  **Commit**: YES (groups with Tasks 3, 5, 6)
  - 동일 커밋

---

- [x] 5. prompt-designer.md 수정: 양식 강제 규칙 + 문서 헤딩 일관성 + Workflow Position

  **What to do**:
  1. **MUST DO 섹션에 양식 강제 규칙 추가** (line 364 부근, 기존 MUST DO 항목들 뒤에):
     ```markdown
     - [ ] 프롬프트 파일 포맷을 정확히 준수 (아래 강제 규칙 참조)
     ```
  2. **MUST DO 섹션 직후 또는 4-Block Prompt Structure 섹션 내에 강제 규칙 추가**:
     ```markdown
     ### 출력 포맷 강제 규칙 (MANDATORY)

     모든 프롬프트 파일은 아래 포맷을 **정확히** 따라야 합니다. 변형, 약어, 재해석을 허용하지 않습니다.

     **파일 헤더** (필수):
     ```
     # {슬라이드 제목} 이미지 프롬프트
     ```

     **메타 정보** (필수, 순서 고정):
     ```
     > 생성일: {YYYY-MM-DD}
     > 스타일: {style}
     > 테마: {theme}
     > 레이아웃: {layout}
     ```

     **블록 구분자** (필수, 정확한 마크다운 헤딩 사용):
     - `## INSTRUCTION` — 반드시 이 형태. `# INSTRUCTION BLOCK`, `### INSTRUCTION`, `INSTRUCTION:` 등 금지
     - `## CONFIGURATION` — 반드시 이 형태
     - `## CONTENT` — 반드시 이 형태
     - `## FORBIDDEN ELEMENTS` — 반드시 이 형태

     **서브섹션** (INSTRUCTION 블록 내 필수):
     - `### Image Purpose`
     - `### Target Audience`
     - `### Key Message`
     - `### Visual Style`

     **서브섹션** (CONFIGURATION 블록 내 필수):
     - `### Canvas Settings`
     - `### Color Palette`
     - `### Layout Structure`
     - `### Typography`
     ```
  3. **MUST NOT DO 섹션에 금지 패턴 추가**:
     ```markdown
     - [ ] `# INSTRUCTION BLOCK` 형태 사용 금지 (올바른 형태: `## INSTRUCTION`)
     - [ ] 마크다운 헤딩 없이 블록명 사용 금지 (예: `INSTRUCTION:` 금지)
     - [ ] 블록 구분자에 "BLOCK" 접미사 사용 금지 (예: `## INSTRUCTION BLOCK` 금지)
     ```
  4. **문서 헤딩 일관성 수정** (lines 35, 56, 83, 108):
     - line 35: `### Block 1: INSTRUCTION BLOCK` → `### Block 1: INSTRUCTION`
     - line 56: `### Block 2: CONFIGURATION BLOCK` → `### Block 2: CONFIGURATION`
     - line 83: `### Block 3: CONTENT BLOCK` → `### Block 3: CONTENT`
     - line 108: `### Block 4: FORBIDDEN ELEMENTS` — 이미 올바름, 유지
  5. **Workflow Position 섹션 추가** — `## Overview` 직후, `## Input Schema` 직전:
     ```markdown
     ## Workflow Position
     - **After**: content-reviewer (콘텐츠 검토 완료, PASS 판정)
     - **Before**: renderer-agent (최종 검증 및 이미지 렌더링)
     - **Enables**: renderer-agent가 검증 가능한 4-block 프롬프트 제공

     ## Key Distinctions
     - **vs content-organizer**: 문서 분석하지 않음. 이미 분석된 concepts.md와 slide_plan.md를 입력으로 받음
     - **vs content-reviewer**: 콘텐츠 품질을 검토하지 않음. 검토 완료된 개념을 프롬프트로 변환
     - **vs renderer-agent**: 이미지를 렌더링하지 않음. Gemini API용 프롬프트 텍스트만 생성
     ```

  **Must NOT do**:
  - 4-Block 프롬프트의 실제 콘텐츠 예시(lines 386-472) 변경하지 않음
  - 텍스트 밀도 규칙 변경하지 않음
  - Rendering Prevention Rules 변경하지 않음
  - 기존 파이프라인 위치 섹션(line 14-17) 삭제하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 3, 4, 6)
  - **Blocks**: None
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:32-125` - 4-Block Prompt Structure 섹션. 문서 헤딩 수정 대상 (lines 35, 56, 83)
  - `plugins/visual-generator/agents/prompt-designer.md:339-362` - 프롬프트 파일 형식 예시. 강제 규칙이 이 형식과 일치해야 함
  - `plugins/visual-generator/agents/prompt-designer.md:364-382` - 현재 MUST DO / MUST NOT DO 섹션. 양식 강제 규칙 추가 위치
  - `plugins/visual-generator/agents/renderer-agent.md:53-56` - renderer의 검증 패턴 (Task 4에서 수정). prompt-designer의 출력이 이 패턴과 일치해야 함

  **WHY Each Reference Matters**:
  - lines 35, 56, 83: "BLOCK" 접미사 제거 대상. 실제 출력과 문서의 일관성 확보
  - lines 339-362: 강제 규칙의 기준. 이 형식을 그대로 규칙화해야 함
  - lines 364-382: 규칙 추가 위치. 기존 MUST DO/NOT DO에 통합

  **Acceptance Criteria**:

  - [ ] 양식 강제 규칙 존재: `grep "출력 포맷 강제 규칙" plugins/visual-generator/agents/prompt-designer.md` → 일치
  - [ ] "INSTRUCTION BLOCK" 문서 헤딩 수정됨: `grep "### Block 1: INSTRUCTION BLOCK" plugins/visual-generator/agents/prompt-designer.md` → 결과 없음
  - [ ] "CONFIGURATION BLOCK" 문서 헤딩 수정됨: `grep "### Block 2: CONFIGURATION BLOCK" plugins/visual-generator/agents/prompt-designer.md` → 결과 없음
  - [ ] "CONTENT BLOCK" 문서 헤딩 수정됨: `grep "### Block 3: CONTENT BLOCK" plugins/visual-generator/agents/prompt-designer.md` → 결과 없음
  - [ ] MUST NOT DO에 금지 패턴 추가: `grep "BLOCK.*접미사.*금지\|INSTRUCTION BLOCK.*금지" plugins/visual-generator/agents/prompt-designer.md` → 일치
  - [ ] Workflow Position 존재: `grep "## Workflow Position" plugins/visual-generator/agents/prompt-designer.md` → 일치
  - [ ] Key Distinctions 존재: `grep "## Key Distinctions" plugins/visual-generator/agents/prompt-designer.md` → 일치

  **Commit**: YES (groups with Tasks 3, 4, 6)
  - 동일 커밋

---

- [x] 6. content-organizer.md 수정: Workflow Position 추가

  **What to do**:
  1. **Workflow Position 섹션 추가** — `## Overview` 직후, 기존 `파이프라인 위치:` 직후, `## Input Schema` 직전:
     ```markdown
     ## Workflow Position
     - **After**: 없음 (파이프라인 첫 단계)
     - **Before**: content-reviewer (콘텐츠 검토)
     - **Enables**: content-reviewer가 검토할 분석 결과(concepts.md, slide_plan.md, theme_recommendation.md) 제공

     ## Key Distinctions
     - **vs content-reviewer**: 콘텐츠를 검토하지 않음. 원본 문서를 분석하여 구조화된 개념을 추출
     - **vs prompt-designer**: 프롬프트를 생성하지 않음. 테마, 레이아웃, 핵심 개념까지만 결정
     - **vs renderer-agent**: 이미지 관련 작업 수행하지 않음
     ```

  **Must NOT do**:
  - 기존 파이프라인 위치 섹션(line 14-17) 삭제하지 않음
  - content-organizer의 워크플로우, 테마/레이아웃 선택 로직 변경하지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 3, 4, 5)
  - **Blocks**: None
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-organizer.md:10-17` - 현재 Overview + 파이프라인 위치 섹션. Workflow Position 추가 위치
  - `plugins/visual-generator/agents/content-organizer.md:19-26` - Input Schema 시작점. Workflow Position이 이 직전에 위치

  **WHY Each Reference Matters**:
  - lines 10-17: 삽입 위치 결정. 기존 `파이프라인 위치:` 뒤, `## Input Schema` 앞에 추가

  **Acceptance Criteria**:

  - [ ] Workflow Position 존재: `grep "## Workflow Position" plugins/visual-generator/agents/content-organizer.md` → 일치
  - [ ] Key Distinctions 존재: `grep "## Key Distinctions" plugins/visual-generator/agents/content-organizer.md` → 일치
  - [ ] 기존 파이프라인 위치 유지: `grep "파이프라인 위치" plugins/visual-generator/agents/content-organizer.md` → 일치

  **Commit**: YES (groups with Tasks 3, 4, 5)
  - 동일 커밋

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 2 | `fix(visual-generator): add delegation enforcement to orchestrator` | marketplace.json, orchestrator 파일 | `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"` |
| 3+4+5+6 | `fix(visual-generator): fix validation patterns, add Write tool, format rules, and Workflow Position` | content-reviewer.md, renderer-agent.md, prompt-designer.md, content-organizer.md | `grep "INSTRUCTION BLOCK" plugins/visual-generator/agents/renderer-agent.md` (exit code 1) |

---

## Success Criteria

### Verification Commands
```bash
# 1. content-reviewer에 Write 도구 포함
grep "^tools:" plugins/visual-generator/agents/content-reviewer.md | grep -q Write && echo "PASS" || echo "FAIL"

# 2. renderer-agent에 "INSTRUCTION BLOCK" 패턴 없음
! grep -q "INSTRUCTION BLOCK" plugins/visual-generator/agents/renderer-agent.md && echo "PASS" || echo "FAIL"
! grep -q "CONFIGURATION BLOCK" plugins/visual-generator/agents/renderer-agent.md && echo "PASS" || echo "FAIL"
! grep -q "CONTENT BLOCK" plugins/visual-generator/agents/renderer-agent.md && echo "PASS" || echo "FAIL"

# 3. renderer-agent에 새 검증 패턴 존재
grep -q '## INSTRUCTION' plugins/visual-generator/agents/renderer-agent.md && echo "PASS" || echo "FAIL"

# 4. prompt-designer에 양식 강제 규칙 존재
grep -q "출력 포맷 강제 규칙" plugins/visual-generator/agents/prompt-designer.md && echo "PASS" || echo "FAIL"

# 5. 모든 에이전트에 Workflow Position 존재
for f in content-organizer content-reviewer prompt-designer renderer-agent; do
  grep -q "## Workflow Position" plugins/visual-generator/agents/$f.md && echo "$f: PASS" || echo "$f: FAIL"
done

# 6. 오케스트레이터에 위임 강제 규칙 존재 (경로는 Task 1 결과에 따라)
grep -c "직접" plugins/visual-generator/agents/orchestrator.md  # 또는 commands/visual-generate.md

# 7. marketplace.json 유효
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"
```

### Final Checklist
- [x] content-reviewer가 Write 도구로 review_result.md 작성 가능
- [x] renderer-agent 검증 패턴 4개 모두 prompt-designer 출력 포맷과 일치
- [x] prompt-designer에 출력 포맷 강제 규칙 명시
- [x] 오케스트레이터에 위임 강제 규칙 명시 (직접 작업 수행 금지)
- [x] 4개 서브에이전트 모두에 Workflow Position + Key Distinctions 섹션 존재
- [x] marketplace.json 유효한 JSON
- [x] 파이프라인 순서 변경 없음 (content-organizer → content-reviewer → prompt-designer → renderer-agent)
- [x] strict: true 유지 (변경하지 않음)
- [x] 테마 참조 파일 수정 없음
- [x] 스크립트 수정 없음
