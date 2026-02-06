# 플러그인 구조 표준화 (Orchestrator → Commands 이동)

## TL;DR

> **Quick Summary**: 5개 멀티에이전트 플러그인의 오케스트레이터를 `agents/` → `commands/` 디렉토리로 이동하고, isd-generator의 10개 스킬을 marketplace.json에 등록한다. visual-generator에서 검증된 패턴을 그대로 적용.
> 
> **Deliverables**:
> - 5개 플러그인에 `commands/` 디렉토리 생성 + 오케스트레이터 이동
> - marketplace.json에 5개 `"commands"` 배열 추가 + agents 배열에서 오케스트레이터 제거
> - isd-generator에 `"skills"` 배열 추가
> - 각 오케스트레이터에 위임 강제 규칙 추가 (없는 경우)
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 (naming 결정) → Task 2-6 (파일 이동 병렬) → Task 7 (marketplace.json 단일 수정) → Task 8 (검증)

---

## Context

### Original Request
visual-generator 플러그인에서 성공적으로 수행한 구조 개선(orchestrator → commands/ 이동, 위임 강제 규칙 추가)을 나머지 5개 오케스트레이터 보유 플러그인에 적용한다. 추가로 isd-generator의 등록되지 않은 10개 스킬을 marketplace.json에 등록한다.

### Interview Summary
**Key Discussions**:
- 적용 범위: 오케스트레이터 있는 5개 플러그인 모두 (isd-generator, report-generator, paper-style-generator, investments-portfolio, stock-consultation)
- 개선 항목: orchestrator → commands/ 이동 + isd-generator skills 등록
- Workflow Position / Key Distinctions 추가는 이번 범위에서 제외
- stock-consultant.md는 하이브리드(상담사+오케스트레이터)이지만 전체를 commands/로 이동

**Research Findings**:
- `commands/` 키는 공식 스키마에서 지원 확인됨 (visual-generator restructure Task 1에서 검증 완료)
- 5개 오케스트레이터 모두 `Task(subagent_type=)` 위임 패턴 사용 중
- sub-agent 파일들이 오케스트레이터 `name`을 텍스트로 참조 (예: `portfolio-orchestrator`) → name 변경 불가
- isd-generator: 10개 skills 디렉토리 존재하지만 marketplace.json에 미등록

### Metis Review
**Identified Gaps** (addressed):
- 명령 파일 이름 컨벤션: visual-generator는 `visual-generate.md` (액션 지향) → [DECISION NEEDED]
- YAML frontmatter `name` 필드: sub-agent들이 텍스트로 참조하므로 변경 불가 → 유지
- paper-style-generator에 MUST NOT 섹션 부재 → 새로 생성
- git mv 사용으로 파일 이력 보존
- marketplace.json 원자적 수정: 중간 상태에서 유효하지 않은 JSON 방지
- AGENTS.md/README.md 업데이트 → 범위 외

---

## Work Objectives

### Core Objective
5개 멀티에이전트 플러그인의 오케스트레이터를 `commands/` 디렉토리로 이동하여, Claude Code 플러그인 시스템의 `commands` 기능을 활용하고 역할 분리를 명확히 한다.

### Concrete Deliverables
- `plugins/isd-generator/commands/{name}.md` — 이동된 오케스트레이터
- `plugins/report-generator/commands/{name}.md` — 이동된 오케스트레이터
- `plugins/paper-style-generator/commands/{name}.md` — 이동된 오케스트레이터
- `plugins/investments-portfolio/commands/{name}.md` — 이동된 오케스트레이터
- `plugins/stock-consultation/commands/{name}.md` — 이동된 오케스트레이터
- `.claude-plugin/marketplace.json` — 6개 변경 (5 commands + 1 skills)

### Definition of Done
- [x] 5개 `commands/` 디렉토리 생성됨
- [x] 5개 오케스트레이터 파일이 `commands/`에 존재
- [x] 5개 원본 파일이 `agents/`에서 삭제됨
- [x] marketplace.json에 5개 `"commands"` 배열 존재
- [x] marketplace.json의 `"agents"` 배열에서 오케스트레이터 제거됨
- [x] isd-generator에 `"skills"` 배열 추가됨
- [x] marketplace.json 유효한 JSON
- [x] YAML frontmatter의 `name` 필드 5개 모두 변경 없음

### Must Have
- 5개 오케스트레이터의 commands/ 이동
- marketplace.json의 commands 배열 추가 + agents 배열에서 제거
- isd-generator skills 등록
- 위임 강제 규칙 (MUST NOT DO에 추가/생성)

### Must NOT Have (Guardrails)
- YAML frontmatter의 `name`, `model`, `tools`, `skills` 필드 변경 금지
- sub-agent 파일 수정 금지 (chapter1-5.md, fund-portfolio.md 등)
- 기존 절대 금지 사항 / CRITICAL RULES 섹션 재작성 금지 (추가만 허용)
- Workflow Position / Key Distinctions 추가 금지 (이번 범위 외)
- 버전 번호 변경 금지
- strict: true 변경 금지
- AGENTS.md / README.md 수정 금지
- 스크립트/스킬 파일 수정 금지
- 워크플로우 Phase 로직 재작성 금지

---

## Verification Strategy

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None (마크다운 파일 이동 + JSON 수정)
- **Framework**: none

### Agent-Executed QA (Simplified)
모든 검증은 bash + grep + python3 명령어로 수행.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
└── Task 1: 명령 파일 이름 결정 (사용자 질문 불필요 시 즉시 결정)

Wave 2 (After Wave 1, 5개 병렬):
├── Task 2: isd-generator orchestrator 이동
├── Task 3: report-generator orchestrator 이동
├── Task 4: paper-style-generator orchestrator 이동
├── Task 5: investments-portfolio orchestrator 이동
└── Task 6: stock-consultation orchestrator 이동

Wave 3 (After Wave 2, 순차):
├── Task 7: marketplace.json 단일 원자적 수정 (6개 변경사항)
└── Task 8: 최종 검증
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2-6 | None |
| 2 | 1 | 7 | 3, 4, 5, 6 |
| 3 | 1 | 7 | 2, 4, 5, 6 |
| 4 | 1 | 7 | 2, 3, 5, 6 |
| 5 | 1 | 7 | 2, 3, 4, 6 |
| 6 | 1 | 7 | 2, 3, 4, 5 |
| 7 | 2-6 | 8 | None |
| 8 | 7 | None | None |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1 | 직접 결정 (질문 불필요 시) |
| 2 | 2-6 | 5x delegate_task(category="quick", load_skills=[], run_in_background=true) |
| 3 | 7, 8 | delegate_task(category="quick") 순차 실행 |

---

## TODOs

- [x] 1. 명령 파일 이름 컨벤션 결정

  **What to do**:
  - **결정됨: 액션 지향 이름 (visual-generator 패턴)**
  - `isd-generate.md` — isd-generator
  - `report-generate.md` — report-generator
  - `paper-style-generate.md` — paper-style-generator
  - `portfolio-analyze.md` — investments-portfolio
  - `stock-consult.md` — stock-consultation

  **Must NOT do**:
  - YAML frontmatter의 `name` 필드를 파일명과 맞추려고 변경하지 않음

  **Recommended Agent Profile**:
  - **Category**: N/A (즉시 결정)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (단독)
  - **Blocks**: Tasks 2-6
  - **Blocked By**: None

  **References**:
  - `plugins/visual-generator/commands/visual-generate.md` — 참조 패턴 (액션 지향 이름)
  - `.claude-plugin/marketplace.json:52` — `"commands": ["./commands/visual-generate.md"]`

  **Acceptance Criteria**:
  - [x] 5개 파일의 목표 이름 결정됨

  **Commit**: NO

---

- [x] 2. isd-generator: orchestrator → commands/ 이동

  **What to do**:
  1. `mkdir -p plugins/isd-generator/commands`
  2. `git mv plugins/isd-generator/agents/orchestrator.md plugins/isd-generator/commands/isd-generate.md`
  3. 이동된 파일의 MUST NOT DO 섹션에 위임 강제 규칙 추가 (기존 검증문서 규칙 유지, 추가만):
     ```markdown
     - [ ] 직접 Chapter 내용을 생성하지 않음 (chapter1-5에 위임 필수)
     - [ ] 직접 이미지 프롬프트를 생성하지 않음 (figure에 위임 필수)
     - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
     ```

  **Must NOT do**:
  - YAML frontmatter 변경 금지 (name: isd-orchestrator, model: sonnet, tools, skills 유지)
  - 기존 워크플로우 Phase 로직 변경 금지
  - chapter1-5.md, figure.md 등 sub-agent 수정 금지
  - 기존 CRITICAL 규칙(검증문서 필수) 재작성 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md:290-301` — 위임 강제 규칙 참조 패턴
  - `plugins/isd-generator/agents/orchestrator.md` — 현재 오케스트레이터 (이동 대상)

  **WHY Each Reference Matters**:
  - visual-generate.md: 위임 강제 규칙의 정확한 형태와 위치 결정
  - orchestrator.md: 이동할 파일의 현재 구조 확인. MUST NOT DO 섹션 위치 파악

  **Acceptance Criteria**:
  - [x] `plugins/isd-generator/commands/isd-generate.md` 파일 존재
  - [x] `plugins/isd-generator/agents/orchestrator.md` 삭제됨
  - [x] YAML frontmatter `name: isd-orchestrator` 유지: `grep "name: isd-orchestrator" plugins/isd-generator/commands/isd-generate.md`
  - [x] 위임 강제 규칙 존재: `grep -c "위임 필수" plugins/isd-generator/commands/isd-generate.md` → 2 이상
  - [x] Task(subagent_type) 규칙 존재: `grep "Task(subagent_type" plugins/isd-generator/commands/isd-generate.md`

  **Commit**: YES (groups with Tasks 3-6)
  - Message: `refactor: move 5 orchestrators from agents/ to commands/`
  - Files: 5 moved files
  - Pre-commit: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"`

---

- [x] 3. report-generator: orchestrator → commands/ 이동

  **What to do**:
  1. `mkdir -p plugins/report-generator/commands`
  2. `git mv plugins/report-generator/agents/orchestrator.md plugins/report-generator/commands/report-generate.md`
  3. 이동된 파일의 MUST NOT DO 또는 CRITICAL RULES 섹션에 위임 강제 규칙 추가:
     ```markdown
     - [ ] 직접 입력 자료를 분석하지 않음 (input-analyzer에 위임 필수)
     - [ ] 직접 콘텐츠 맵핑을 수행하지 않음 (content-mapper에 위임 필수)
     - [ ] 직접 챕터를 작성하지 않음 (chapter-writer에 위임 필수)
     - [ ] 직접 품질 검증을 수행하지 않음 (quality-checker에 위임 필수)
     - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
     ```

  **Must NOT do**:
  - YAML frontmatter 변경 금지 (name: report-generator-orchestrator, model: sonnet)
  - 기존 CRITICAL RULES 재작성 금지 (4단계 패턴 규칙 등)
  - sub-agent 파일 수정 금지
  - AskUserQuestion 도구 제거 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 4, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:
  - `plugins/report-generator/agents/orchestrator.md` — 이동 대상
  - `plugins/visual-generator/commands/visual-generate.md:290-301` — 위임 규칙 패턴

  **Acceptance Criteria**:
  - [x] `plugins/report-generator/commands/report-generate.md` 존재
  - [x] `plugins/report-generator/agents/orchestrator.md` 삭제됨
  - [x] YAML frontmatter `name: report-generator-orchestrator` 유지
  - [x] 위임 강제 규칙 4개 이상: `grep -c "위임 필수" plugins/report-generator/commands/report-generate.md` → 4 이상

  **Commit**: YES (groups with Tasks 2, 4-6)

---

- [x] 4. paper-style-generator: orchestrator → commands/ 이동

  **What to do**:
  1. `mkdir -p plugins/paper-style-generator/commands`
  2. `git mv plugins/paper-style-generator/agents/orchestrator.md plugins/paper-style-generator/commands/paper-style-generate.md`
  3. paper-style-generator에는 MUST NOT DO 섹션이 **없으므로** 새로 생성:
     ```markdown
     ## MUST NOT DO
     
     - [ ] 직접 PDF 변환을 수행하지 않음 (pdf-converter에 위임 필수)
     - [ ] 직접 스타일 분석을 수행하지 않음 (style-analyzer에 위임 필수)
     - [ ] 직접 스킬을 생성하지 않음 (skill-generator에 위임 필수)
     - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
     ```

  **Must NOT do**:
  - YAML frontmatter 변경 금지 (name: paper-style-orchestrator, model: opus)
  - 기존 Phase 워크플로우 재작성 금지 (Phase 1-3 순서 유지)
  - sub-agent 파일 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:
  - `plugins/paper-style-generator/agents/orchestrator.md` — 이동 대상 (MUST NOT DO 섹션 부재 확인)
  - `plugins/visual-generator/commands/visual-generate.md:290-301` — MUST NOT DO 패턴

  **Acceptance Criteria**:
  - [x] `plugins/paper-style-generator/commands/paper-style-generate.md` 존재
  - [x] `plugins/paper-style-generator/agents/orchestrator.md` 삭제됨
  - [x] YAML frontmatter `name: paper-style-orchestrator` 유지
  - [x] MUST NOT DO 섹션 존재: `grep "## MUST NOT DO" plugins/paper-style-generator/commands/paper-style-generate.md`
  - [x] 위임 강제 규칙 3개 이상: `grep -c "위임 필수" plugins/paper-style-generator/commands/paper-style-generate.md` → 3 이상

  **Commit**: YES (groups with Tasks 2, 3, 5, 6)

---

- [x] 5. investments-portfolio: portfolio-orchestrator → commands/ 이동

  **What to do**:
  1. `mkdir -p plugins/investments-portfolio/commands`
  2. `git mv plugins/investments-portfolio/agents/portfolio-orchestrator.md plugins/investments-portfolio/commands/portfolio-analyze.md`
  3. 이미 강력한 "절대 금지 사항" 섹션이 있으므로, 기존 섹션 끝에만 추가:
     ```markdown
     - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
     ```

  **Must NOT do**:
  - YAML frontmatter 변경 금지 (name: portfolio-orchestrator, model: opus)
  - 기존 절대 금지 사항 재작성 금지 (fund_data.json 분석, DC형 70% 계산 등)
  - sub-agent 파일 수정 금지 (7개 파일이 `portfolio-orchestrator` 이름 참조 중)
  - BLOCKING/PARALLEL 패턴 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 4, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:
  - `plugins/investments-portfolio/agents/portfolio-orchestrator.md` — 이동 대상. 강력한 절대 금지 섹션 존재
  - Sub-agents 참조 목록 (변경 불가):
    - `macro-synthesizer.md`: "portfolio-orchestrator 통해서만 호출"
    - `fund-portfolio.md`: `coordinator: portfolio-orchestrator`
    - `material-organizer.md`: `coordinator: "portfolio-orchestrator"`
    - `compliance-checker.md`: "portfolio-orchestrator에서 호출될 때"
    - `output-critic.md`: "portfolio-orchestrator에서 호출될 때"

  **WHY Sub-agent references matter**:
  - 이 참조들은 `name` 필드 기반 텍스트 참조. 파일 경로가 아닌 논리적 이름이므로 이동해도 안전
  - 하지만 `name` 필드 변경 시 이 모든 참조가 깨짐 → name 변경 절대 금지

  **Acceptance Criteria**:
  - [x] `plugins/investments-portfolio/commands/portfolio-analyze.md` 존재
  - [x] `plugins/investments-portfolio/agents/portfolio-orchestrator.md` 삭제됨
  - [x] YAML frontmatter `name: portfolio-orchestrator` 유지: `grep "name: portfolio-orchestrator" plugins/investments-portfolio/commands/portfolio-analyze.md`
  - [x] 기존 절대 금지 사항 유지: `grep "fund_data.json" plugins/investments-portfolio/commands/portfolio-analyze.md`
  - [x] Task(subagent_type) 규칙 추가됨: `grep "Task(subagent_type" plugins/investments-portfolio/commands/portfolio-analyze.md`

  **Commit**: YES (groups with Tasks 2-4, 6)

---

- [x] 6. stock-consultation: stock-consultant → commands/ 이동

  **What to do**:
  1. `mkdir -p plugins/stock-consultation/commands`
  2. `git mv plugins/stock-consultation/agents/stock-consultant.md plugins/stock-consultation/commands/stock-consult.md`
  3. 이미 강력한 "절대 금지 사항" 섹션이 있으므로, 기존 섹션 끝에만 추가:
     ```markdown
     - [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
     ```

  **Must NOT do**:
  - YAML frontmatter 변경 금지 (name: stock-consultant, model: opus)
  - 기존 절대 금지 사항 재작성 금지 (웹검색 수행, 종목 데이터 수집 등)
  - 요청 유형 분류 로직 변경 금지 (단일 종목 / 포트폴리오 / 테마)
  - Bogle 투자 철학 면책조항 변경 금지
  - sub-agent 파일 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3, 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: Task 1

  **References**:
  - `plugins/stock-consultation/agents/stock-consultant.md` — 이동 대상. 하이브리드(상담사+오케스트레이터)
  - Stock skill 참조: `coordinator(stock-consultant)가 제공하는 output_path` — name 기반 참조

  **Acceptance Criteria**:
  - [x] `plugins/stock-consultation/commands/stock-consult.md` 존재
  - [x] `plugins/stock-consultation/agents/stock-consultant.md` 삭제됨
  - [x] YAML frontmatter `name: stock-consultant` 유지
  - [x] 기존 절대 금지 사항 유지: `grep "직접 웹검색" plugins/stock-consultation/commands/stock-consult.md`
  - [x] Task(subagent_type) 규칙 추가됨

  **Commit**: YES (groups with Tasks 2-5)

---

- [x] 7. marketplace.json 단일 원자적 수정 (6개 변경사항)

  **What to do**:
  marketplace.json을 **한 번에** 수정하여 6개 변경사항을 적용:

  **변경 1 - isd-generator**:
  - 추가: `"commands": ["./commands/isd-generate.md"]`
  - 제거: `"./agents/orchestrator.md"` from agents 배열
  - 추가: `"skills": ["./skills"]`

  **변경 2 - report-generator**:
  - 추가: `"commands": ["./commands/report-generate.md"]`
  - 제거: `"./agents/orchestrator.md"` from agents 배열

  **변경 3 - paper-style-generator**:
  - 추가: `"commands": ["./commands/paper-style-generate.md"]`
  - 제거: `"./agents/orchestrator.md"` from agents 배열

  **변경 4 - investments-portfolio**:
  - 추가: `"commands": ["./commands/portfolio-analyze.md"]`
  - 제거: `"./agents/portfolio-orchestrator.md"` from agents 배열

  **변경 5 - stock-consultation**:
  - 추가: `"commands": ["./commands/stock-consult.md"]`
  - 제거: `"./agents/stock-consultant.md"` from agents 배열

  **수정 순서**: 중간 상태에서도 유효한 JSON을 유지하기 위해, 한 번의 Edit 또는 Write 호출로 모든 변경사항 적용

  **Must NOT do**:
  - 다른 플러그인 항목 수정 금지
  - strict: true 변경 금지
  - 버전 번호 변경 금지
  - visual-generator 항목 수정 금지 (이미 완료)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (순차)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2-6

  **References**:
  - `.claude-plugin/marketplace.json` — 전체 파일 (250줄)
  - `.claude-plugin/marketplace.json:52` — visual-generator commands 배열 (참조 패턴)

  **WHY marketplace.json edits must be atomic**:
  - 11개 플러그인이 모두 이 파일에 의존. 유효하지 않은 JSON → 전체 마켓플레이스 로드 실패
  - 중간 수정 상태에서 파일 참조가 없는 항목이 있으면 플러그인 로드 실패 가능

  **Acceptance Criteria**:
  - [x] JSON 유효성: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"`
  - [x] 5개 plugins에 commands 배열 존재:
    ```
    python3 -c "
    import json
    with open('.claude-plugin/marketplace.json') as f:
        data = json.load(f)
    targets = ['isd-generator','report-generator','paper-style-generator','investments-portfolio','stock-consultation']
    for p in data['plugins']:
        if p['name'] in targets:
            has_cmd = 'commands' in p and len(p['commands']) > 0
            no_orch = not any('orchestrator' in a or 'stock-consultant' in a for a in p.get('agents',[]))
            print(f\"{p['name']}: commands={'PASS' if has_cmd else 'FAIL'}, orch_removed={'PASS' if no_orch else 'FAIL'}\")
    "
    ```
  - [x] isd-generator skills 등록됨:
    ```
    python3 -c "
    import json
    with open('.claude-plugin/marketplace.json') as f:
        data = json.load(f)
    for p in data['plugins']:
        if p['name'] == 'isd-generator':
            print(f\"skills: {p.get('skills', 'MISSING')}\")
    "
    ```

  **Commit**: YES
  - Message: `refactor: register commands and isd-generator skills in marketplace.json`
  - Pre-commit: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"`

---

- [x] 8. 최종 통합 검증

  **What to do**:
  모든 변경사항에 대한 종합 검증 스크립트 실행:

  ```bash
  # 1. 5개 commands/ 디렉토리 존재
  for p in isd-generator report-generator paper-style-generator investments-portfolio stock-consultation; do
    test -d "plugins/$p/commands" && echo "PASS: $p/commands" || echo "FAIL: $p/commands missing"
  done

  # 2. 5개 원본 파일 삭제됨
  test ! -f plugins/isd-generator/agents/orchestrator.md && echo "PASS" || echo "FAIL: isd orch still exists"
  test ! -f plugins/report-generator/agents/orchestrator.md && echo "PASS" || echo "FAIL: report orch still exists"
  test ! -f plugins/paper-style-generator/agents/orchestrator.md && echo "PASS" || echo "FAIL: paper orch still exists"
  test ! -f plugins/investments-portfolio/agents/portfolio-orchestrator.md && echo "PASS" || echo "FAIL: portfolio orch still exists"
  test ! -f plugins/stock-consultation/agents/stock-consultant.md && echo "PASS" || echo "FAIL: stock consultant still exists"

  # 3. 5개 command 파일 존재
  for f in plugins/*/commands/*.md; do
    test -f "$f" && echo "PASS: $f" || echo "FAIL: $f missing"
  done

  # 4. YAML frontmatter name 필드 유지
  grep -l "name: isd-orchestrator" plugins/isd-generator/commands/*.md && echo "PASS" || echo "FAIL: isd name changed"
  grep -l "name: report-generator-orchestrator" plugins/report-generator/commands/*.md && echo "PASS" || echo "FAIL"
  grep -l "name: paper-style-orchestrator" plugins/paper-style-generator/commands/*.md && echo "PASS" || echo "FAIL"
  grep -l "name: portfolio-orchestrator" plugins/investments-portfolio/commands/*.md && echo "PASS" || echo "FAIL"
  grep -l "name: stock-consultant" plugins/stock-consultation/commands/*.md && echo "PASS" || echo "FAIL"

  # 5. marketplace.json 유효
  python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"

  # 6. 위임 규칙 존재
  for f in plugins/*/commands/*.md; do
    grep -q "Task(subagent_type" "$f" && echo "PASS: $f delegation" || echo "FAIL: $f no delegation"
  done
  ```

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (순차, Task 7 이후)
  - **Blocks**: None (최종)
  - **Blocked By**: Task 7

  **Acceptance Criteria**:
  - [x] 위 검증 스크립트의 모든 항목 PASS

  **Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 2-6 | `refactor: move 5 orchestrators from agents/ to commands/` | 5 moved files | `test -d plugins/*/commands` |
| 7 | `refactor: register commands and isd-generator skills in marketplace.json` | marketplace.json | `python3 -m json.tool .claude-plugin/marketplace.json` |

---

## Success Criteria

### Verification Commands
```bash
# 모든 오케스트레이터가 commands/에 있음
ls plugins/*/commands/*.md  # 6개 파일 (visual-generator 포함)

# agents/에 오케스트레이터 없음
for p in isd-generator report-generator paper-style-generator investments-portfolio stock-consultation; do
  ls plugins/$p/agents/*orchestrator* 2>/dev/null || ls plugins/$p/agents/stock-consultant.md 2>/dev/null
done  # 결과 없어야 함

# marketplace.json 유효
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('VALID')"

# isd-generator에 skills 등록
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); [print(p['skills']) for p in d['plugins'] if p['name']=='isd-generator']"
```

### Final Checklist
- [x] 5개 `commands/` 디렉토리 생성됨
- [x] 5개 오케스트레이터가 commands/에만 존재 (agents/에서 삭제됨)
- [x] marketplace.json에 5개 commands 배열 존재
- [x] marketplace.json의 agents 배열에 오케스트레이터 없음
- [x] isd-generator에 skills 배열 등록됨
- [x] 모든 YAML frontmatter name 필드 변경 없음
- [x] 모든 위임 강제 규칙 추가됨
- [x] marketplace.json 유효한 JSON
- [x] strict: true 유지
- [x] sub-agent 파일 수정 없음
- [x] 스크립트/스킬 파일 수정 없음
