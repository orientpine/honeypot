# accelerated-learner 플러그인 구축

## TL;DR

> **Quick Summary**: MIT 대학원생의 "48시간 딥러닝" 방법론을 Claude 플러그인으로 체계화. 소스 자료 분석 → 멘탈모델 추출 → 논쟁 매핑 → 판별 질문 생성 → 소크라틱 튜터링의 5단계 파이프라인.
> 
> **Deliverables**:
> - 플러그인 `plugins/accelerated-learner/` (5 에이전트, 1 커맨드, 1 스킬)
> - marketplace.json 등록 + AGENTS.md/README.md 업데이트
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: T1(skeleton) → T2(skill) → T3-T7(agents parallel) → T8(orchestrator) → T9(docs) → F1-F4

---

## Context

### Original Request
MIT 대학원생이 NotebookLM으로 한 학기 분량을 48시간에 압축한 학습법을 Claude 플러그인으로 만들어 달라는 요청. 핵심 철학: "한 학기와 48시간의 차이는 콘텐츠의 양이 아니라, 어떤 질문을 던져야 하는지를 아는 것."

### Interview Summary
**Key Discussions**:
- **플러그인 이름**: accelerated-learner
- **언어**: 한국어 전용 (에이전트 프롬프트, 출력물 모두)
- **소스 자료**: 폴더 경로 + 개별 파일 모두 지원 (`.md`, `.txt`, `.pdf`)
- **출력**: 마크다운 지식 베이스 (6개 구조화된 MD 파일)
- **튜터링**: 대화형 (질문 하나씩 → 사용자 답변 → 피드백)
- **진도 추적**: 세션별 기록 (session-log.md)

**Research Findings**:
- 기존 플러그인 패턴 (isd-generator, report-generator, paper-style-generator) 분석 완료
- 커맨드: Phase-numbered + `Task(subagent_type="plugin::agent")` 위임
- 에이전트: frontmatter(name, description, tools, model, skills) + Workflow 본문
- 스킬: `skills/{name}/SKILL.md` 구조, 상대경로 → Glob 폴백
- 인터랙션: `AskUserQuestion` 기반 다회전 대화 패턴
- 통신: 파일 기반 JSON/MD 체인

### Metis Review
**Identified Gaps** (addressed):

1. **방법론 정의 부재** → `learning-methodology/SKILL.md`에 5단계 프레임워크로 명시적 코드화
2. **소스 크기 제한 미정의** → source-synthesizer에 청킹/요약 전략 + 최대 토큰 예산 지침 추가
3. **멘탈모델/질문 수 경직** → "최대 5개", "최대 10개"로 유연화 (주제에 따라 적게 가능)
4. **논쟁 없는 주제 처리** → controversy-mapper에 "논쟁 없음" 출력 허용
5. **세션 경계 미정의** → 최대 15회 상호작용, 5연속 정답 시 조기 마스터리
6. **마스터리 정의 부재** → 정성적 평가 (질적 판단, 점수화 아님)
7. **다중 세션 덮어쓰기** → `sessions/` 하위 디렉토리 + 번호 매김
8. **소스 언어 혼재** → 영어 소스 허용, 출력은 항상 한국어
9. **중단 시 데이터 손실** → 매 Q&A 교환 후 즉시 session-log에 기록
10. **빈 폴더/비텍스트 파일** → Phase 0 검증 + 파일 필터링

---

## Work Objectives

### Core Objective
"어떤 질문을 던지는가"를 체계화한 가속 학습 플러그인을 구축하여, 사용자가 소스 자료를 제공하면 멘탈모델 → 논쟁 → 판별 질문 → 소크라틱 튜터링의 파이프라인을 통해 해당 분야의 깊은 이해에 도달하도록 안내한다.

### Concrete Deliverables
```
plugins/accelerated-learner/
├── .claude-plugin/plugin.json
├── agents/
│   ├── source-synthesizer.md
│   ├── mental-model-extractor.md
│   ├── controversy-mapper.md
│   ├── question-architect.md
│   └── socratic-tutor.md
├── commands/
│   └── accelerated-learn.md
└── skills/
    └── learning-methodology/
        ├── SKILL.md
        └── references/
            └── methodology-framework.md
```

### Definition of Done
- [ ] `ls plugins/accelerated-learner/{.claude-plugin,agents,commands,skills}` → 모든 디렉토리 존재
- [ ] 5개 에이전트 .md 파일 각각 유효한 frontmatter 포함
- [ ] marketplace.json에 accelerated-learner 항목 등록 (strict: true, 5 에이전트 경로)
- [ ] AGENTS.md의 `WHERE TO LOOK` 테이블에 항목 추가
- [ ] README.md에 플러그인 설명 + 변경 이력 추가
- [ ] 모든 버전 번호 동기화 (plugin.json, marketplace.json, AGENTS.md, README.md)

### Must Have
- 5단계 학습 파이프라인 (소스 분석 → 멘탈모델 → 논쟁 → 질문 → 튜터링)
- 소크라틱 튜터링의 대화형 인터랙션 (AskUserQuestion)
- 세션별 학습 기록 (session-log.md)
- 자료 출처 기반 분석만 수행 (웹 검색으로 보충 금지)
- 유연한 멘탈모델/질문 수 (주제 복잡도에 따라 조절)
- `auto_mode` 파라미터: true일 때 튜터링 단계 건너뛰고 지식 베이스만 출력
- 한국어 전용 출력 (영어 소스 자료 허용)

### Must NOT Have (Guardrails)
- ❌ 웹 검색으로 소스 자료 보충 — 제공된 자료만 사용
- ❌ 인용, 전문가 이름, 논쟁 입장 날조 — 소스에 근거한 내용만
- ❌ 주제가 지원하지 않는데 정확히 5개 모델/10개 질문 강제 생성
- ❌ 세션 로그 덮어쓰기 — sessions/ 하위 디렉토리 사용
- ❌ 소크라틱 튜터의 무한 루프 — 최대 15회 상호작용
- ❌ 튜터가 주제 범위 밖 질문에 답변
- ❌ MCQ/O-X 형식 질문 — 개방형 "왜 X인지 설명하세요" 형식만
- ❌ 마스터리 점수화/인증서/배지 — 정성적 자기평가만
- ❌ 오케스트레이터가 직접 분석 수행 — 반드시 에이전트에 위임
- ❌ 플러그인 루트에 scripts/references/assets 폴더 — 스킬 내부에만

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (플러그인은 마크다운 에이전트 파일로 구성)
- **Automated tests**: None (구조 검증으로 대체)
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **플러그인 구조**: Bash (ls, grep) — 파일 존재, frontmatter 유효성
- **마켓플레이스 등록**: Bash (grep) — marketplace.json 항목 확인
- **에이전트 품질**: Bash (grep) — 필수 섹션, 도구 목록, 워크플로우 구조

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Plugin skeleton + plugin.json + marketplace.json [quick]
└── Task 2: Learning methodology skill (SKILL.md + references) [deep]

Wave 2 (After Wave 1 — all 5 agents in parallel):
├── Task 3: source-synthesizer agent [unspecified-high]
├── Task 4: mental-model-extractor agent [unspecified-high]
├── Task 5: controversy-mapper agent [unspecified-high]
├── Task 6: question-architect agent [unspecified-high]
└── Task 7: socratic-tutor agent [deep]

Wave 3 (After Wave 2 — orchestrator):
└── Task 8: accelerated-learn.md command (orchestrator) [deep]

Wave 4 (After Wave 3 — documentation):
└── Task 9: AGENTS.md, README.md, version sync [quick]

Wave FINAL (After ALL tasks):
├── F1: Plan compliance audit [oracle]
├── F2: Code quality review [unspecified-high]
├── F3: Real manual QA [unspecified-high]
└── F4: Scope fidelity check [deep]
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| T1 | — | T3-T8 | 1 |
| T2 | — | T3-T7 | 1 |
| T3 | T1, T2 | T8 | 2 |
| T4 | T1, T2 | T8 | 2 |
| T5 | T1, T2 | T8 | 2 |
| T6 | T1, T2 | T8 | 2 |
| T7 | T1, T2 | T8 | 2 |
| T8 | T3-T7 | T9 | 3 |
| T9 | T8 | F1-F4 | 4 |
| F1-F4 | T9 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 → `quick`, T2 → `deep`
- **Wave 2**: **5** — T3-T6 → `unspecified-high`, T7 → `deep`
- **Wave 3**: **1** — T8 → `deep`
- **Wave 4**: **1** — T9 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.

- [x] 1. 플러그인 스켈레톤 + plugin.json + marketplace.json 등록

  **What to do**:
  - `plugins/accelerated-learner/` 디렉토리 구조 생성: `.claude-plugin/`, `agents/`, `commands/`, `skills/learning-methodology/`
  - `.claude-plugin/plugin.json` 생성 (name: accelerated-learner, version: 1.0.0, author.email: orientpine@gmail.com)
  - `.claude-plugin/marketplace.json`에 accelerated-learner 항목 추가:
    ```json
    {
      "name": "accelerated-learner",
      "source": "./plugins/accelerated-learner",
      "description": "48시간 가속 학습 — 소스 자료 분석, 멘탈모델 추출, 논쟁 매핑, 판별 질문, 소크라틱 튜터링",
      "version": "1.0.0",
      "strict": true,
      "agents": [
        "./agents/source-synthesizer.md",
        "./agents/mental-model-extractor.md",
        "./agents/controversy-mapper.md",
        "./agents/question-architect.md",
        "./agents/socratic-tutor.md"
      ],
      "skills": ["./skills"]
    }
    ```
  - `skills/learning-methodology/references/` 디렉토리도 함께 생성

  **Must NOT do**:
  - 플러그인 루트에 scripts/references/assets 폴더 생성 금지
  - marketplace.json의 skills에 trailing slash 금지 (`"./skills"` O, `"./skills/"` X)
  - `strict: false` 사용 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 디렉토리 생성 + JSON 파일 2개 작성의 단순 구조 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (T2와 동시)
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: T3, T4, T5, T6, T7, T8
  - **Blocked By**: None (can start immediately)

  **References**:
  - `plugins/report-generator/.claude-plugin/plugin.json` — plugin.json 형식 참조
  - `.claude-plugin/marketplace.json` — 기존 항목 형식 참조 (특히 agents/skills 배열 형식)
  - `AGENTS.md` > `CLAUDE CODE MARKETPLACE RULES` > `Per-Plugin plugin.json` — 필수 필드 규칙
  - `AGENTS.md` > `Marketplace Registration Checklist` — 등록 체크리스트

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 플러그인 디렉토리 구조 검증
    Tool: Bash
    Preconditions: Wave 1 완료
    Steps:
      1. ls plugins/accelerated-learner/.claude-plugin/plugin.json → 파일 존재
      2. ls plugins/accelerated-learner/agents/ → 디렉토리 존재
      3. ls plugins/accelerated-learner/commands/ → 디렉토리 존재
      4. ls plugins/accelerated-learner/skills/learning-methodology/ → 디렉토리 존재
    Expected Result: 4개 경로 모두 존재, exit code 0
    Failure Indicators: No such file or directory 에러
    Evidence: .sisyphus/evidence/task-1-directory-structure.txt

  Scenario: plugin.json 필수 필드 검증
    Tool: Bash (grep)
    Steps:
      1. grep '"name"' plugins/accelerated-learner/.claude-plugin/plugin.json → "accelerated-learner"
      2. grep '"email"' plugins/accelerated-learner/.claude-plugin/plugin.json → "orientpine@gmail.com"
      3. grep '"version"' plugins/accelerated-learner/.claude-plugin/plugin.json → "1.0.0"
    Expected Result: 3개 필드 모두 존재하고 올바른 값
    Evidence: .sisyphus/evidence/task-1-plugin-json.txt

  Scenario: marketplace.json 등록 검증
    Tool: Bash (grep)
    Steps:
      1. grep 'accelerated-learner' .claude-plugin/marketplace.json → 항목 존재
      2. grep '"strict": true' 해당 항목 → strict 설정 확인
    Expected Result: marketplace에 항목 등록됨, strict: true
    Evidence: .sisyphus/evidence/task-1-marketplace.txt
  ```

  **Commit**: YES
  - Message: `feat(accelerated-learner): add plugin skeleton and marketplace registration`
  - Files: `plugins/accelerated-learner/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  - Pre-commit: `ls plugins/accelerated-learner/{.claude-plugin,agents,commands,skills}`

- [x] 2. learning-methodology 스킬 (SKILL.md + references)

  **What to do**:
  - `skills/learning-methodology/SKILL.md` 작성 — 48시간 가속 학습 방법론의 지적 핵심
  - frontmatter: `name: learning-methodology`, `description: "48시간 가속 학습 방법론 — 멘탈모델 추출, 논쟁 매핑, 판별 질문 생성, 소크라틱 튜터링의 교육학적 원칙과 실행 지침. Use when 학습 자료 분석, 지식 구조화, 튜터링 세션 수행 시."`
  - **SKILL.md 본문 필수 섹션:**
    1. `## 48시간 가속 학습 프레임워크` — 5단계 명시:
       - Step 1: 소스 종합 (대량 자료 → 핵심 추출)
       - Step 2: 멘탈모델 추출 (최대 5개, 전문가 사고체계)
       - Step 3: 논쟁 지형 매핑 (전문가 의견 불일치점)
       - Step 4: 판별 질문 설계 (깊은 이해 vs 암기 구별)
       - Step 5: 소크라틱 대화 (대화형 튜터링 → 마스터리)
    2. `## 멘탈모델 추출 원칙` — 각 모델은 이름 + 정의 + 예측 테스트("이것을 이해하면 X를 예측할 수 있다") 포함
    3. `## 논쟁 매핑 원칙` — 진짜 학문적 논쟁만 (날조 금지), 없으면 "논쟁 없음" 명시 허용
    4. `## 판별 질문 설계 원칙` — 개방형만 (MCQ 금지), 블룸 분류체계 상위 수준(분석/평가/창조) 타겟
    5. `## 소크라틱 튜터링 원칙` — 3가지 응답 유형(탐색적 후속질문, 교정적 피드백, 확장적 긍정), 세션 경계(최대 15회), 조기 마스터리(5연속 우수 답변)
    6. `## 소스 자료 처리 지침` — 지원 형식(.md, .txt, .pdf), 대용량 청킹 전략, 영어 소스 → 한국어 출력
    7. `## 가드레일` — 웹검색 보충 금지, 인용 날조 금지, 강제 수량 채우기 금지, 세션로그 매 교환마다 즉시 기록
  - `references/methodology-framework.md` 작성 — 블룸 분류체계 상세, 소크라틱 메서드 질문 유형, 판별 질문 예시 패턴

  **Must NOT do**:
  - SKILL.md를 500줄 이상 작성 (상세 내용은 references/로 분리)
  - 스킬 이름과 디렉토리명 불일치 (둘 다 `learning-methodology`여야 함)
  - description에서 따옴표 미처리

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 교육학적 프레임워크를 정교하게 설계해야 하는 지적 핵심 작업. 이 스킬이 모든 에이전트의 품질을 결정함.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (T1과 동시)
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: T3, T4, T5, T6, T7
  - **Blocked By**: None (can start immediately)

  **References**:
  - `plugins/isd-generator/skills/core-resources/SKILL.md` — 대규모 스킬 구조 참조 (references/ 활용 패턴)
  - `plugins/report-generator/skills/four-step-pattern/SKILL.md` — 방법론 스킬 구조 참조
  - `AGENTS.md` > `Skill File Structure` — frontmatter 필수 필드, name 규칙
  - 블룸 분류체계(Bloom's Taxonomy) 상위 3수준: 분석(Analyze), 평가(Evaluate), 창조(Create)
  - 소크라틱 메서드 질문 유형: 명확화, 가정 탐색, 증거 탐색, 관점 전환, 결과 탐색, 질문에 대한 질문

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SKILL.md 구조 검증
    Tool: Bash (grep)
    Steps:
      1. grep '^name: learning-methodology' plugins/accelerated-learner/skills/learning-methodology/SKILL.md → 매칭
      2. grep '^description:' SKILL.md → description 필드 존재
      3. grep '## 48시간 가속 학습 프레임워크' SKILL.md → 핵심 섹션 존재
      4. grep '## 멘탈모델 추출 원칙' SKILL.md → 섹션 존재
      5. grep '## 소크라틱 튜터링 원칙' SKILL.md → 섹션 존재
      6. grep '## 가드레일' SKILL.md → 가드레일 섹션 존재
      7. wc -l SKILL.md → 500줄 미만
    Expected Result: 6개 필수 섹션 모두 존재, 500줄 미만
    Failure Indicators: grep 매칭 실패, 줄 수 500 초과
    Evidence: .sisyphus/evidence/task-2-skill-structure.txt

  Scenario: references 파일 존재 검증
    Tool: Bash (ls)
    Steps:
      1. ls plugins/accelerated-learner/skills/learning-methodology/references/methodology-framework.md → 존재
    Expected Result: 파일 존재
    Evidence: .sisyphus/evidence/task-2-references.txt

  Scenario: 가드레일 내용 검증
    Tool: Bash (grep)
    Steps:
      1. grep '웹.*검색.*금지\|웹.*보충.*금지' SKILL.md → 웹검색 금지 규칙 존재
      2. grep '날조.*금지\|fabricat' SKILL.md → 날조 금지 규칙 존재
    Expected Result: 핵심 가드레일 2개 이상 명시
    Evidence: .sisyphus/evidence/task-2-guardrails.txt
  ```

  **Commit**: YES
  - Message: `feat(accelerated-learner): add learning-methodology skill`
  - Files: `skills/learning-methodology/SKILL.md`, `skills/learning-methodology/references/methodology-framework.md`
  - Pre-commit: `grep '^name:' plugins/accelerated-learner/skills/learning-methodology/SKILL.md`

- [x] 3. source-synthesizer 에이전트

  **What to do**:
  - `agents/source-synthesizer.md` 작성
  - **frontmatter**: name: source-synthesizer, description: "소스 자료 종합 분석. 폴더/파일 경로의 모든 텍스트 자료를 읽고 핵심을 추출하여 종합 분석문을 생성한다. Use when 학습 소스 자료를 처음 분석할 때.", model: sonnet, tools: [Read, Glob, Grep, Write, Bash], skills: [learning-methodology]
  - **Workflow 필수 단계:**
    1. Phase 0: 입력 검증 — 폴더/파일 존재 확인, 지원 형식 필터링(.md, .txt, .pdf), 빈 폴더 에러 처리
    2. Phase 1: 소스 읽기 — 각 파일 순회적 읽기, 파일명+요약 기록
    3. Phase 2: 청킹 전략 — 대용량 자료 시 첫 폈-테일-핵심구조 추출, 소규모 자료 시 전문 활용
    4. Phase 3: 종합 분석문 생성 — 모든 소스의 공통점+차이점+핵심논지 통합, 2000-5000단어
    5. Phase 4: 출력 — `{output_dir}/00-source-synthesis.md` 저장
  - **출력 요구사항:** 모든 소스 파일명 언급, 영어 소스도 한국어로 분석

  **Must NOT do**:
  - 웹 검색으로 소스 보충 금지 — 제공된 자료만 사용
  - 원문 복사-붙여넣기 금지 — 종합하고 재구성
  - 소스에 없는 정보 추가 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 대량의 텍스트를 읽고 종합하는 분석 작업. 참조할 파턴이 명확하므로 deep 까지는 불필요.
  - **Skills**: [`learning-methodology`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (T4, T5, T6, T7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2

  **References**:
  - `plugins/report-generator/agents/input-analyzer.md` — 입력 분석 에이전트 구조 참조 (Phase 0 검증, 파일 필터링, JSON 체크포인트)
  - `plugins/paper-style-generator/agents/pdf-converter.md` — 파일 인제스트 에이전트 패턴 참조 (PDF 처리, 품질 검증)
  - T2의 `learning-methodology/SKILL.md` — 소스 자료 처리 지침 섹션 참조

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 에이전트 frontmatter 검증
    Tool: Bash (grep)
    Steps:
      1. grep '^name: source-synthesizer' agents/source-synthesizer.md → 매칭
      2. grep '^description:' agents/source-synthesizer.md → 존재
      3. grep '^model: sonnet' agents/source-synthesizer.md → 매칭
      4. grep 'learning-methodology' agents/source-synthesizer.md → 스킬 참조 존재
    Expected Result: frontmatter 4개 필드 모두 올바름
    Evidence: .sisyphus/evidence/task-3-frontmatter.txt

  Scenario: 워크플로우 완성도 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c '## \|Phase' agents/source-synthesizer.md → 다수의 Phase/섹션 존재
      2. grep '입력.*검증\|Phase 0\|빈 폴더' agents/source-synthesizer.md → 입력 검증 단계 존재
      3. grep '청킹\|chunk\|요약' agents/source-synthesizer.md → 대용량 처리 전략 존재
    Expected Result: 입력검증 + 청킹전략 모두 포함
    Evidence: .sisyphus/evidence/task-3-workflow.txt
  ```

  **Commit**: YES (groups with T4, T5)
  - Message: `feat(accelerated-learner): add source-synthesizer agent`
  - Files: `agents/source-synthesizer.md`

- [x] 4. mental-model-extractor 에이전트

  **What to do**:
  - `agents/mental-model-extractor.md` 작성
  - **frontmatter**: name: mental-model-extractor, description: "핵심 멘탈모델 추출. 종합 분석문에서 해당 분야 전문가들이 공유하는 사고 체계를 최대 5개 추출한다. Use when 소스 종합 후 멘탈모델을 추출할 때.", model: sonnet, tools: [Read, Write, Bash], skills: [learning-methodology]
  - **Workflow:**
    1. `{output_dir}/00-source-synthesis.md` 읽기
    2. 멘탈모델 식별 — 전문가들이 공유하는 핵심 사고 프레임워크 탐색
    3. 각 모델별 구조화 — 이름, 한 줄 정의, 예측 테스트("이것을 이해하면 X를 예측할 수 있다")
    4. 품질 검증 — 모델간 중복 없음 확인, 주제가 좌소하면 적은 수 허용
    5. 출력 — `{output_dir}/01-mental-models.md` 저장
  - **출력 형식:** H2 헤딩 per 모델, 에측 테스트 필수 포함

  **Must NOT do**:
  - 정확히 5개 강제 — 주제에 따라 2-5개 유연하게
  - 소스에 근거 없는 모델 날조
  - 예측 테스트 없는 모델 작성

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 종합문에서 멘탈모델을 추출하는 분석 작업
  - **Skills**: [`learning-methodology`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (T3, T5, T6, T7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2

  **References**:
  - T3의 출력물 `00-source-synthesis.md` — 입력 자료
  - T2의 `learning-methodology/SKILL.md` > `멘탈모델 추출 원칙` 섹션

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 에이전트 frontmatter + 워크플로우 검증
    Tool: Bash (grep)
    Steps:
      1. grep '^name: mental-model-extractor' agents/mental-model-extractor.md → 매칭
      2. grep '00-source-synthesis' agents/mental-model-extractor.md → 입력 언급
      3. grep '예측 테스트\|예측할 수 있다' agents/mental-model-extractor.md → 예측 테스트 지침 존재
      4. grep '2-5\|최대 5\|유연' agents/mental-model-extractor.md → 수량 유연성 명시
    Expected Result: 4개 항목 모두 매칭
    Evidence: .sisyphus/evidence/task-4-mental-model.txt
  ```

  **Commit**: YES (groups with T3, T5)
  - Message: `feat(accelerated-learner): add analysis agents (mental-model, controversy)`
  - Files: `agents/mental-model-extractor.md`

- [x] 5. controversy-mapper 에이전트

  **What to do**:
  - `agents/controversy-mapper.md` 작성
  - **frontmatter**: name: controversy-mapper, description: "논쟁 지형 매핑. 종합 분석문에서 전문가들이 근본적으로 의견이 갈리는 지점을 식별하고 각 입장의 근거를 정리한다. Use when 소스 종합 후 논쟁 구조를 파악할 때.", model: sonnet, tools: [Read, Write, Bash], skills: [learning-methodology]
  - **Workflow:**
    1. `{output_dir}/00-source-synthesis.md` 읽기
    2. 논쟁점 식별 — 전문가 간 의견 불일치, 학문적 논쟁, 미해결 질문
    3. 각 논쟁별 구조화 — 논쟁명, 입장별 가장 강력한 논거, 현재 학계 합의 수준
    4. 논쟁 없는 주제 처리 — "이 분야에서 활발한 논쟁은 확인되지 않았습니다" + 활발한 연구 영역 대체
    5. 출력 — `{output_dir}/02-controversies.md` 저장

  **Must NOT do**:
  - 논쟁 날조 금지 — 소스에 근거 없는 논쟁 생성 절대 금지
  - "활발한 연구 영역"을 "논쟁"으로 포장 금지
  - 3개 강제 채우기 금지 — 0-3개 유연하게

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: T4와 동일한 분석 수준, 입력도 동일(00-source-synthesis.md)
  - **Skills**: [`learning-methodology`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (T3, T4, T6, T7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2

  **References**:
  - T3의 출력물 `00-source-synthesis.md` — 입력 자료
  - T2의 `learning-methodology/SKILL.md` > `논쟁 매핑 원칙` 섹션

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 논쟁 없음 처리 검증
    Tool: Bash (grep)
    Steps:
      1. grep '^name: controversy-mapper' agents/controversy-mapper.md → 매칭
      2. grep '논쟁.*없\|확인되지 않\|N/A\|없음' agents/controversy-mapper.md → 논쟁없음 처리 로직 존재
      3. grep '날조.*금지\|fabricat' agents/controversy-mapper.md → 날조 금지 규칙 존재
    Expected Result: 논쟁없음 처리 + 날조금지 모두 포함
    Evidence: .sisyphus/evidence/task-5-controversy.txt
  ```

  **Commit**: YES (groups with T3, T4)
  - Message: `feat(accelerated-learner): add analysis agents (mental-model, controversy)`
  - Files: `agents/controversy-mapper.md`


- [x] 6. question-architect 에이전트

  **What to do**:
  - `agents/question-architect.md` 작성
  - **frontmatter**: name: question-architect, description: "판별 질문 설계. 멘탈모델과 논쟁 지형을 바탕으로, 깊은 이해와 단순 암기를 구별할 수 있는 개방형 질문을 5-10개 생성한다. Use when 튜터링용 판별 질문이 필요할 때.", model: sonnet, tools: [Read, Write, Bash], skills: [learning-methodology]
  - **Workflow:**
    1. `01-mental-models.md` + `02-controversies.md` 읽기
    2. 질문 설계 — 블룸 분류체계 상위 수준(분석/평가/창조) 타겟
    3. 각 질문에 멘탈모델/논쟁 참조 링크 표시
    4. 답변 루브릭 작성 — 우수/적절/미흡 답변의 기준
    5. 출력 — `{output_dir}/03-discriminating-questions.md` 저장

  **Must NOT do**:
  - MCQ/O-X/빈칸채우기 금지 — 개방형 "설명하세요/비교하세요" 형식만
  - 10개 강제 금지 — 5-10개 유연하게
  - 암기로 답할 수 있는 단순 질문 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 멘탈모델+논쟁 2개 입력을 종합하여 질문 설계하는 분석 작업
  - **Skills**: [`learning-methodology`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (T3, T4, T5, T7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2

  **References**:
  - T4 출력 `01-mental-models.md` + T5 출력 `02-controversies.md` — 입력 자료
  - T2의 `learning-methodology/SKILL.md` > `판별 질문 설계 원칙` + `references/methodology-framework.md` > 블룸 분류체계

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 질문 형식 검증
    Tool: Bash (grep)
    Steps:
      1. grep '^name: question-architect' agents/question-architect.md → 매칭
      2. grep -i 'MCQ\|선택지\|O-X\|빈칸' agents/question-architect.md → 금지 규칙 존재
      3. grep '개방형\|설명\|비교' agents/question-architect.md → 개방형 지침 존재
      4. grep '블룸\|Bloom\|분석.*평가.*창조' agents/question-architect.md → 블룸 참조 존재
    Expected Result: MCQ금지 + 개방형지침 + 블룸참조 모두 포함
    Evidence: .sisyphus/evidence/task-6-questions.txt
  ```

  **Commit**: YES
  - Message: `feat(accelerated-learner): add question-architect agent`
  - Files: `agents/question-architect.md`

- [x] 7. socratic-tutor 에이전트 (핵심 컴포넌트)

  **What to do**:
  - `agents/socratic-tutor.md` 작성 — 플러그인의 가장 복잡하고 중요한 에이전트
  - **frontmatter**: name: socratic-tutor, description: "소크라틱 대화형 튜터링. 판별 질문을 하나씩 제시하고 사용자 답변에 피드백을 제공하며 마스터리를 향해 안내한다. Use when 사용자와 대화형 학습 세션을 진행할 때.", model: sonnet, tools: [Read, Write, Bash, AskUserQuestion], skills: [learning-methodology]
  - **핵심 설계 요소:**
    1. **세션 초기화** — 01/02/03 전부 읽기, 세션 디렉토리 `sessions/` 생성
    2. **질문 제시** — AskUserQuestion으로 1개씩 제시, 사용자 답변 대기
    3. **답변 평가** — 루브릭 기반 평가, 3가지 응답 유형 중 선택:
       - 탐색적 후속질문 (더 깊이 생각하도록)
       - 교정적 피드백 (틀린 부분 + 놓친 것 설명)
       - 확장적 긍정 (올바른 답변을 더 확장)
    4. **세션 로그 작성** — 매 Q&A 교환 후 즉시 `sessions/session-{N}.md`에 기록 (크래시 세이프)
    5. **세션 종료 조건:**
       - 최대 15회 상호작용
       - 5연속 우수 답변 시 조기 마스터리
       - 사용자 "종료"/"그만" 입력 시 좌시 종료
    6. **마스터리 요약** — 종료 시 `{output_dir}/05-mastery-summary.md` 생성
       - 각 멘탈모델별 이해도 정성적 평가
       - 강점/약점 영역 식별
       - 추가 학습 권장 영역
  - **엣지 케이스 처리:**
    - 무의미 답변 → 최대 2회 재요청 후 다음 질문으로
    - 주제 벗어난 답변 → 주제로 재유도
    - 사용자가 모든 질문에 즉시 정답 → 마스터리 조기 종료

  **Must NOT do**:
  - 무한 루프 금지 — 반드시 종료 조건 포함
  - 동일 질문 다른 표현 반복 금지
  - 주제 범위 밖 질문에 답변 금지
  - 점수 부여/인증서 생성 금지 — 정성적 자기평가만
  - 세션 종료 시에만 로그 작성 금지 — 매 교환마다 즉시 기록

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 다회전 대화, 사용자 응답 평가, 적응적 피드백 생성 등 가장 복잡한 논리 필요. 플러그인의 핵심 UX 컴포넌트.
  - **Skills**: [`learning-methodology`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (T3, T4, T5, T6과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: T8
  - **Blocked By**: T1, T2

  **References**:
  - `plugins/general-agents/agents/interview.md` — AskUserQuestion 기반 다회전 대화 패턴 참조
  - `plugins/plugin-dev/skills/command-development/references/interactive-commands.md` — 인터랙티브 패턴 5종 참조
  - T2의 `learning-methodology/SKILL.md` > `소크라틱 튜터링 원칙` 섹션
  - T6 출력 `03-discriminating-questions.md` + T4 출력 `01-mental-models.md` + T5 출력 `02-controversies.md`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 대화형 튜터링 설계 검증
    Tool: Bash (grep)
    Steps:
      1. grep 'AskUserQuestion' agents/socratic-tutor.md → 대화 도구 포함
      2. grep '탐색적\|교정적\|확장적' agents/socratic-tutor.md → 3가지 응답 유형 명시
      3. grep '최대 15\|15회' agents/socratic-tutor.md → 세션 상한 존재
      4. grep '5연속\|조기 마스터리' agents/socratic-tutor.md → 조기종료 조건 존재
      5. grep 'sessions/\|session-' agents/socratic-tutor.md → 세션별 로그 구조 존재
      6. grep '매.*교환\|즉시.*기록\|크래시' agents/socratic-tutor.md → 즉시 기록 지침 존재
    Expected Result: 6개 항목 모두 매칭
    Failure Indicators: 누락된 항목은 다시 작성 필요
    Evidence: .sisyphus/evidence/task-7-tutor-design.txt

  Scenario: 엣지케이스 처리 검증
    Tool: Bash (grep)
    Steps:
      1. grep '무의미\|nonsense\|재요청' agents/socratic-tutor.md → 무의미 답변 처리
      2. grep '주제.*벗\|재유도\|off-topic' agents/socratic-tutor.md → 주제이탈 처리
    Expected Result: 2개 엣지케이스 모두 언급
    Evidence: .sisyphus/evidence/task-7-edge-cases.txt
  ```

  **Commit**: YES
  - Message: `feat(accelerated-learner): add socratic-tutor agent`
  - Files: `agents/socratic-tutor.md`

- [x] 8. accelerated-learn.md 오케스트레이터 커맨드

  **What to do**:
  - `commands/accelerated-learn.md` 작성 — 전체 워크플로우 오케스트레이터
  - **필수 파라미터:**
    - `source_path` (O): 폴더 또는 파일 경로
    - `subject_name` (O): 학습 주제명 (출력 폴더명 결정)
    - `output_dir` (-): 출력 디렉토리 (default: `./output/`)
    - `auto_mode` (-): true일 때 튜터링 건너뛰고 지식베이스만 출력
  - **워크플로우 구조 (ASCII 다이어그램):**
    ```
    [Phase 0: 초기화]
        |
        +-- Step 0-1. 입력 검증 (source_path 존재, 파일 수 ≥ 1)
        +-- Step 0-2. 출력 디렉토리 생성 (output/{subject_name}/)
    
    [Phase 1: 소스 종합]
        |
        +-- Step 1-1. Task(subagent_type="accelerated-learner::source-synthesizer")
        +-- Step 1-2. 결과 검증: 00-source-synthesis.md 존재 확인
    
    [Phase 2: 멘탈모델 + 논쟁 (병렴)]
        |
        +-- Step 2-1. Task(subagent_type="accelerated-learner::mental-model-extractor") // 병렴
        +-- Step 2-2. Task(subagent_type="accelerated-learner::controversy-mapper")     // 병렴
        +-- Step 2-3. 결과 검증: 01 + 02 모두 존재 확인
    
    [Phase 3: 판별 질문 생성]
        |
        +-- Step 3-1. Task(subagent_type="accelerated-learner::question-architect")
        +-- Step 3-2. 결과 검증: 03-discriminating-questions.md 존재 확인
    
    [Phase 4: 소크라틱 튜터링] (auto_mode=true 시 건너뛰)
        |
        +-- Step 4-1. Task(subagent_type="accelerated-learner::socratic-tutor")
        +-- Step 4-2. 세션 완료 후 04-session-log.md + 05-mastery-summary.md 검증
    
    [Phase 5: 완료]
        +-- 전체 산출물 요약 출력
        +-- output/{subject_name}/ 내 파일 목록 표시
    ```
  - **에러 처리:** 각 Phase 실패 시 재시도 1회 → 실패 시 사용자 알림 + 부분 진행 여부 확인
  - **MUST NOT DO 체크리스트:** 오케스트레이터가 직접 분석 수행 금지, 웹검색 금지, 인용 날조 금지

  **Must NOT do**:
  - 오케스트레이터가 직접 소스 분석/멘탈모델 추출/질문 생성 수행 금지
  - frontmatter 포함 금지 (커맨드는 frontmatter 없음)
  - Phase 2의 2개 에이전트를 순차적으로 실행 금지 — 반드시 병렴

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 5개 에이전트 조율, 에러 처리, 병렴 실행 등 복잡한 오케스트레이션 논리
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 2 완료 후 순차)
  - **Parallel Group**: Wave 3 (sequential)
  - **Blocks**: T9
  - **Blocked By**: T3, T4, T5, T6, T7

  **References**:
  - `plugins/report-generator/commands/report-generate.md` — 오케스트레이터 구조 참조 (Phase 구조, Task 위임, auto_mode, 에러처리)
  - `plugins/isd-generator/commands/isd-generate.md` — 다단계 위임 + 검증 패턴 참조
  - `plugins/paper-style-generator/commands/paper-style-generate.md` — 메타 플러그인 오케스트레이터 참조
  - T3-T7의 모든 에이전트 파일 — Task() 호출 대상

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 오케스트레이터 구조 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c 'Task(subagent_type' commands/accelerated-learn.md → 5 (에이전트 5개 호출)
      2. grep 'source-synthesizer' commands/accelerated-learn.md → 매칭
      3. grep 'mental-model-extractor' commands/accelerated-learn.md → 매칭
      4. grep 'controversy-mapper' commands/accelerated-learn.md → 매칭
      5. grep 'question-architect' commands/accelerated-learn.md → 매칭
      6. grep 'socratic-tutor' commands/accelerated-learn.md → 매칭
    Expected Result: 5개 Task 호출 모두 존재
    Evidence: .sisyphus/evidence/task-8-orchestrator-tasks.txt

  Scenario: 병렴 실행 + auto_mode 검증
    Tool: Bash (grep)
    Steps:
      1. grep '병렴\|parallel\|동시' commands/accelerated-learn.md → Phase 2 병렴 명시
      2. grep 'auto_mode' commands/accelerated-learn.md → auto_mode 파라미터 존재
      3. grep '건너뛰\|skip\|생략' commands/accelerated-learn.md → 튜터링 건너뛰기 로직 존재
    Expected Result: 병렴+auto_mode+건너뛰기 모두 포함
    Evidence: .sisyphus/evidence/task-8-parallel-automode.txt

  Scenario: MUST NOT DO 검증
    Tool: Bash (grep)
    Steps:
      1. grep -i 'MUST NOT\|금지\|직접.*분석\|직접.*수행' commands/accelerated-learn.md → 금지 규칙 존재
    Expected Result: 오케스트레이터 직접 수행 금지 명시
    Evidence: .sisyphus/evidence/task-8-must-not.txt
  ```

  **Commit**: YES
  - Message: `feat(accelerated-learner): add orchestrator command`
  - Files: `commands/accelerated-learn.md`

- [x] 9. AGENTS.md + README.md 업데이트 + 버전 동기화

  **What to do**:
  - **AGENTS.md `WHERE TO LOOK` 테이블에 추가:**
    ```
    | 가속 학습 파이프라인 실행 | `plugins/accelerated-learner/commands/accelerated-learn.md` | 48시간 딥러닝 방법론 |
    | 소크라틱 튜터링 | `plugins/accelerated-learner/agents/socratic-tutor.md` | 대화형 학습 |
    ```
  - **AGENTS.md Version** 업데이트 (3.21.0 → 3.22.0)
  - **AGENTS.md Generated** 날짜 업데이트
  - **README.md에 accelerated-learner 섹션 추가:**
    - `주요 기능` 표에 항목 추가
    - `플러그인 상세` 섹션에 accelerated-learner 설명 추가
    - `프로젝트 구조` 트리에 항목 추가
    - `변경 이력` 테이블에 3.22.0 항목 추가
  - **README.md Version** 업데이트 (3.21.0 → 3.22.0)
  - **marketplace.json `metadata.version`** 업데이트 (3.21.0 → 3.22.0)
  - **plugin.json version** 확인 (1.0.0 유지)

  **Must NOT do**:
  - 불필요한 리포맷 금지 — 변경된 부분만 수정
  - 버전 불일치 금지 — 4개 파일 모두 3.22.0

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 기존 파일에 정해진 항목만 추가/수정하는 단순 작업
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 3 완료 후 순차)
  - **Parallel Group**: Wave 4 (sequential)
  - **Blocks**: F1-F4
  - **Blocked By**: T8

  **References**:
  - `AGENTS.md` — `WHERE TO LOOK` 테이블, Version 필드, Generated 날짜
  - `README.md` — 주요 기능 표, 플러그인 상세, 프로젝트 구조, 변경 이력
  - `.claude-plugin/marketplace.json` — metadata.version 필드
  - `plugins/accelerated-learner/.claude-plugin/plugin.json` — version 필드
  - 기존 플러그인들의 README 섹션 형식 참조 (사용법, 특징, 구성요소)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 버전 동기화 검증
    Tool: Bash (grep)
    Steps:
      1. grep '3.22.0' AGENTS.md → 매칭
      2. grep '3.22.0' README.md → 매칭
      3. grep '3.22.0' .claude-plugin/marketplace.json → 매칭
    Expected Result: 3개 파일 모두 3.22.0 포함
    Evidence: .sisyphus/evidence/task-9-version-sync.txt

  Scenario: AGENTS.md WHERE TO LOOK 테이블 검증
    Tool: Bash (grep)
    Steps:
      1. grep 'accelerated-learner' AGENTS.md → 항목 존재
      2. grep 'accelerated-learn' AGENTS.md → 커맨드 언급 존재
    Expected Result: accelerated-learner 관련 항목 2개 이상 존재
    Evidence: .sisyphus/evidence/task-9-agents-md.txt

  Scenario: README.md 업데이트 검증
    Tool: Bash (grep)
    Steps:
      1. grep 'accelerated-learner' README.md → 섬션 존재
      2. grep '변경 이력' README.md 직후 'accelerated-learner' → 변경이력 기록
    Expected Result: README에 플러그인 섬션 + 변경이력 모두 존재
    Evidence: .sisyphus/evidence/task-9-readme.txt
  ```

  **Commit**: YES
  - Message: `docs: update AGENTS.md, README.md for accelerated-learner plugin`
  - Files: `AGENTS.md`, `README.md`, `.claude-plugin/marketplace.json`
  - Pre-commit: `grep '3.22.0' AGENTS.md README.md .claude-plugin/marketplace.json`

---
## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, check content). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Review all agent .md files for: consistent frontmatter format, Korean language compliance, proper tool lists, workflow completeness, section structure. Check for placeholder text `[내용]`, inconsistent naming, missing sections. Verify SKILL.md follows Agent Skills Spec.
  Output: `Agents [N/N clean] | Skill [PASS/FAIL] | Command [PASS/FAIL] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Verify plugin structure: all directories exist, all files in correct locations, marketplace.json entry valid, plugin.json has required fields, AGENTS.md updated, README.md updated. Run structural validation commands.
  Output: `Structure [PASS/FAIL] | Registration [PASS/FAIL] | Docs [PASS/FAIL] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read spec, read actual file. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Flag unaccounted content.
  Output: `Tasks [N/N compliant] | Creep [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|------------|
| C1 | `feat(accelerated-learner): add plugin skeleton and marketplace registration` | plugin.json, marketplace.json, directory structure | `ls plugins/accelerated-learner/` |
| C2 | `feat(accelerated-learner): add learning-methodology skill` | SKILL.md, references/methodology-framework.md | frontmatter grep |
| C3 | `feat(accelerated-learner): add source-synthesizer agent` | agents/source-synthesizer.md | frontmatter grep |
| C4 | `feat(accelerated-learner): add analysis agents` | agents/mental-model-extractor.md, controversy-mapper.md | frontmatter grep |
| C5 | `feat(accelerated-learner): add question-architect agent` | agents/question-architect.md | frontmatter grep |
| C6 | `feat(accelerated-learner): add socratic-tutor agent` | agents/socratic-tutor.md | frontmatter + AskUserQuestion grep |
| C7 | `feat(accelerated-learner): add orchestrator command` | commands/accelerated-learn.md | Task() calls grep |
| C8 | `docs: update AGENTS.md, README.md for accelerated-learner plugin` | AGENTS.md, README.md, version bumps | version sync check |

---

## Success Criteria

### Verification Commands
```bash
# 플러그인 구조 확인
ls plugins/accelerated-learner/{.claude-plugin/plugin.json,agents/*.md,commands/*.md,skills/learning-methodology/SKILL.md}

# 에이전트 수 확인
ls plugins/accelerated-learner/agents/*.md | wc -l  # Expected: 5

# marketplace.json 등록 확인
grep -c "accelerated-learner" .claude-plugin/marketplace.json  # Expected: ≥1

# 버전 동기화 확인
grep "version" plugins/accelerated-learner/.claude-plugin/plugin.json
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] 5 agents + 1 command + 1 skill 모두 존재
- [ ] marketplace.json 등록 완료
- [ ] AGENTS.md + README.md 업데이트 완료
- [ ] 모든 버전 동기화
