# hwpx-generator: HWPX 통합 플러그인 (3개 레포 장점 취합)

## TL;DR

> **Quick Summary**: 3개 GitHub 레포(hwpxskill, gonggong_hwpxskills, hwpxskill-math)의 장점만을 취합하여 XML-first 빌드 + ZIP-level 치환 + 수학 수식을 통합한 `hwpx-generator` 플러그인을 생성하고, 기존 `hwpx-converter`를 대체한다.
>
> **Deliverables**:
> - `plugins/hwpx-generator/` — Agent(2) + Skill(3) + Command(1) 완전한 플러그인
> - `hwpx-core` 스킬: XML-first 빌드, 5개 템플릿, 6개 유틸 스크립트
> - `hwpx-templates` 스킬: ZIP 치환 워크플로우, 네임스페이스 후처리, 스타일 가이드
> - `hwpx-math` 스킬: 한컴 수식 지원, 시험지 빌더, 그래프/도형 생성
> - `hwpx-builder` 에이전트: XML-first 문서 생성 전문가
> - `hwpx-analyzer` 에이전트: 레퍼런스 HWPX 분석/역공학 전문가
> - `hwpx-generate` 커맨드: 문서 생성 오케스트레이터
> - `marketplace.json` 업데이트 (hwpx-converter 제거, hwpx-generator 추가)
> - `AGENTS.md` 업데이트
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 → Task 2 → Task 6/8 → Task 11/12 → Task 13 → Task 14 → F1-F4

---

## Context

### Original Request
사용자가 3개의 HWPX 관련 GitHub 레포를 분석하고 장점만 취합하여 새 플러그인을 만들어 `plugins/`에 추가해달라고 요청. 기존 양식을 기초로 해서 새로운 플러그인을 만드는 것.

### Interview Summary
**Key Discussions**:
- 기존 `hwpx-converter` (pypandoc-hwpx 기반 단순 변환)를 **완전 대체**
- 플러그인 구성: **Agent + Skill + Command** (최대 기능)
- 플러그인 이름: **hwpx-generator**

**Research Findings**:
- **Repo 1 (hwpxskill)**: XML 직접 작성 중심. build_hwpx.py 핵심 빌더, analyze_template.py 역공학, 5개 템플릿(base/gonmun/report/minutes/proposal), unpack/pack/validate/extract 유틸. python-hwpx API 버그 완전 우회.
- **Repo 2 (gonggong_hwpxskills)**: python-hwpx + ZIP-level 치환. fix_namespaces.py(없으면 빈 페이지!), 양식 우선 정책, ObjectFinder 텍스트 전수 조사, 순차 치환, 보고서 템플릿(표지+목차+섹션), 공문서 스타일 가이드.
- **Repo 3 (hwpxskill-math)**: JSON→HWPX 수학 문제지. hp:equation + 한컴 수식 스크립트 완전 레퍼런스, 2열 시험지 레이아웃, 학력평가/수능 형식, 그래프/도형 생성(matplotlib), 모듈화 코드(primitives→helpers→layout→section→build).
- **기존 hwpx-converter**: pypandoc-hwpx CLI 래퍼. MD→HWPX만 지원. 매우 제한적.

### Metis Review
**Identified Gaps** (addressed):
- **SKILL.md 크기 폭발**: repo3 SKILL.md 750+ 줄 → 수식 레퍼런스/도형 스펙을 `references/`로 분리
- **스킬 간 스크립트 의존**: math → core validate.py → SKILL.md에 교차참조 패턴 문서화
- **ZIP 치환 시 플레이스홀더 분할 리스크**: ObjectFinder 사전 스캔 필수 단계 보존
- **템플릿 충돌**: repo1과 repo3 모두 `templates/base/` → repo3는 `templates/math-base/`로 rename
- **fix_namespaces.py 적용 범위 혼동**: XML-first에는 불필요, ZIP-level에만 필요 → 각 SKILL.md에 명확히 문서화
- **하드코딩된 샌드박스 경로**: repo2의 `/mnt/skills/`, `/home/claude/` → `$SKILL_DIR` 상대경로로 교체
- **fix_namespaces.py regex 접근**: lxml 리팩토링 금지 (ns0 재도입 방지를 위한 의도적 설계)

---

## Work Objectives

### Core Objective
3개 GitHub 레포(Canine89/hwpxskill, Canine89/gonggong_hwpxskills, Canine89/hwpxskill-math)의 장점을 취합하여 HWPX 문서 생성/편집/분석을 위한 통합 플러그인 `hwpx-generator`를 생성하고, 기존 `hwpx-converter`를 대체한다.

### Concrete Deliverables
- `plugins/hwpx-generator/.claude-plugin/plugin.json`
- `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` + scripts(6개) + templates(5개 세트) + references(1개)
- `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md` + scripts(1개) + assets(1개) + references(3개)
- `plugins/hwpx-generator/skills/hwpx-math/SKILL.md` + scripts(7개) + templates(1개 세트) + references(2개) + examples(3+개)
- `plugins/hwpx-generator/agents/hwpx-builder.md`
- `plugins/hwpx-generator/agents/hwpx-analyzer.md`
- `plugins/hwpx-generator/commands/hwpx-generate.md`
- 업데이트된 `.claude-plugin/marketplace.json`
- 업데이트된 `AGENTS.md`
- `plugins/hwpx-converter/` 삭제

### Definition of Done
- [ ] `plugins/hwpx-generator/` 디렉토리 구조가 AGENTS.md 표준 준수
- [ ] 3개 SKILL.md 각각 500줄 이하 (초과 내용은 references/ 분리)
- [ ] 모든 스크립트 참조가 상대경로 우선 + Glob 폴백 패턴 준수
- [ ] marketplace.json에 hwpx-generator 등록, hwpx-converter 제거
- [ ] AGENTS.md의 STRUCTURE, WHERE TO LOOK, UNIQUE STYLES 섹션 업데이트

### Must Have
- XML-first 문서 생성 워크플로우 (build_hwpx.py 기반)
- ZIP-level 텍스트 치환 워크플로우 (fix_namespaces.py 포함)
- 수학 수식 지원 (hp:equation + 한컴 수식 스크립트 레퍼런스)
- 5개 문서 템플릿 (base, gonmun, report, minutes, proposal)
- 레퍼런스 기반 역분석 워크플로우 (analyze_template.py)
- unpack/pack/validate/text_extract 유틸리티
- 2열 시험지 레이아웃 + 학력평가/수능 형식
- 그래프/도형 생성 (matplotlib 기반)
- 에이전트 2개 + 커맨드 1개 + 스킬 3개

### Must NOT Have (Guardrails)
- pypandoc-hwpx 의존성 (기존 converter 방식 배제)
- fix_namespaces.py를 lxml로 리팩토링 (regex 접근이 의도적 설계)
- 하드코딩된 경로 (`/mnt/skills/`, `/home/claude/`, `/mnt/user-data/` 등)
- 플러그인 루트에 scripts/, references/, assets/, templates/ 폴더 (skills/ 내부에만)
- SKILL.md 500줄 초과 (references/로 분리)
- LaTeX 수식 문법 (한컴 수식 스크립트만 사용)
- python-hwpx `HwpxDocument.open()` 직접 사용 권장 (ZIP-level 치환 우선)
- AI slop: 과도한 주석, 불필요한 추상화, 제네릭 이름(data/result/temp)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (플러그인은 .md + .py 파일들이므로 별도 테스트 프레임워크 불필요)
- **Automated tests**: None (unit test 없음, QA scenarios로 대체)
- **Framework**: N/A
- **Validation**: validate.py 스크립트가 HWPX 구조 검증 담당

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **파일 구조**: Bash (ls, tree) — 디렉토리 구조 검증
- **SKILL.md 포맷**: Bash (head, grep) — frontmatter 검증, 줄 수 확인
- **스크립트**: Bash (python -c "import ast; ast.parse(open('...').read())") — 구문 검증
- **marketplace.json**: Bash (python -c "import json; json.load(open('...'))") — JSON 유효성
- **AGENTS.md**: Grep — 필수 섹션 존재 확인

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation + core skill):
├── Task 1: Plugin scaffold + plugin.json [quick]
├── Task 2: hwpx-core SKILL.md [deep]
├── Task 3: hwpx-core scripts (6개 fetch+adapt) [deep]
├── Task 4: hwpx-core templates (5 template sets) [unspecified-high]
└── Task 5: hwpx-core references (hwpx-format.md) [unspecified-high]

Wave 2 (After Wave 1 — specialized skills, MAX PARALLEL):
├── Task 6: hwpx-templates SKILL.md + scripts [deep]
├── Task 7: hwpx-templates references + assets [unspecified-high]
├── Task 8: hwpx-math SKILL.md [deep]
├── Task 9: hwpx-math scripts (7 modules fetch+adapt) [deep]
└── Task 10: hwpx-math templates + references + examples [unspecified-high]

Wave 3 (After Wave 2 — agents + command):
├── Task 11: hwpx-builder agent [deep]
├── Task 12: hwpx-analyzer agent [deep]
└── Task 13: hwpx-generate command [deep]

Wave 4 (After Wave 3 — registry + cleanup):
├── Task 14: Update marketplace.json + delete hwpx-converter [quick]
└── Task 15: Update AGENTS.md [quick]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 2 → Task 6/8 → Task 11/12 → Task 13 → Task 14 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Waves 1 & 2)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2-5 | 1 |
| 2 | 1 | 6, 8, 11, 12, 13 | 1 |
| 3 | 1 | 6, 9, 11, 12 | 1 |
| 4 | 1 | 7, 10 | 1 |
| 5 | 1 | 6, 8 | 1 |
| 6 | 2, 3, 5 | 11, 13 | 2 |
| 7 | 4 | 13 | 2 |
| 8 | 2, 5 | 11, 13 | 2 |
| 9 | 3 | 11, 13 | 2 |
| 10 | 4 | 13 | 2 |
| 11 | 2, 3, 6, 8, 9 | 13 | 3 |
| 12 | 2, 3, 6 | 13 | 3 |
| 13 | 6, 7, 8, 9, 10, 11, 12 | 14 | 3 |
| 14 | 13 | F1-F4 | 4 |
| 15 | 14 | F1-F4 | 4 |

### Agent Dispatch Summary

- **Wave 1**: **5** — T1 → `quick`, T2 → `deep`, T3 → `deep`, T4 → `unspecified-high`, T5 → `unspecified-high`
- **Wave 2**: **5** — T6 → `deep`, T7 → `unspecified-high`, T8 → `deep`, T9 → `deep`, T10 → `unspecified-high`
- **Wave 3**: **3** — T11 → `deep`, T12 → `deep`, T13 → `deep`
- **Wave 4**: **2** — T14 → `quick`, T15 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

### Source Repositories (CRITICAL — fetch content from these)

모든 스크립트, 템플릿, 레퍼런스 파일은 아래 3개 레포에서 가져온다. **자체 작성 금지.**

| Repo | Raw URL Base | 용도 |
|------|-------------|------|
| hwpxskill | `https://raw.githubusercontent.com/Canine89/hwpxskill/main/` | XML-first 핵심 (scripts/, templates/, references/) |
| gonggong_hwpxskills | `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/` | ZIP 치환 (scripts/, assets/, references/) |
| hwpxskill-math | `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/` | 수식/시험지 (scripts/, templates/, examples/) |

**스크립트 가져오기 패턴**: webfetch로 raw content 다운로드 → 경로 수정($SKILL_DIR 기반) → 저장
**SKILL.md 작성 패턴**: 3개 레포의 SKILL.md에서 해당 영역 내용 추출 → 통합/편집 → 500줄 이하로 압축

---

### Wave 1 Tasks (Foundation — start immediately, 5 parallel)

- [ ] 1. Plugin scaffold + plugin.json

  **What to do**:
  - Create directory structure:
    ```
    plugins/hwpx-generator/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── agents/
    ├── commands/
    └── skills/
        ├── hwpx-core/
        │   ├── scripts/
        │   │   └── office/
        │   ├── templates/
        │   └── references/
        ├── hwpx-templates/
        │   ├── scripts/
        │   ├── assets/
        │   └── references/
        └── hwpx-math/
            ├── scripts/
            ├── templates/
            │   └── math-base/
            ├── references/
            └── examples/
    ```
  - Create `plugin.json`:
    ```json
    {
      "name": "hwpx-generator",
      "version": "1.0.0",
      "description": "HWPX 문서 생성/편집/분석 통합 플러그인. XML-first 빌드 + ZIP 치환 + 수학 수식 지원.",
      "author": { "name": "Baekdong Cha", "email": "orientpine@gmail.com" },
      "license": "MIT"
    }
    ```

  **Must NOT do**:
  - 플러그인 루트에 scripts/, references/, assets/ 폴더 생성 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 디렉토리 생성 + 단순 JSON 파일 작성
  - **Skills**: []
  - **Skills Evaluated but Omitted**: N/A

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: [Tasks 2, 3, 4, 5]
  - **Blocked By**: None (can start immediately)

  **References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — plugin.json 포맷 참고 (프로젝트 표준)
  - AGENTS.md `Plugin Root Directory Structure` 섹션 — 허용 폴더 4개만 (`.claude-plugin/`, `agents/`, `commands/`, `skills/`)

  **Acceptance Criteria**:
  - [ ] `plugins/hwpx-generator/.claude-plugin/plugin.json` 존재, 유효 JSON
  - [ ] `author.email` = `orientpine@gmail.com`
  - [ ] 플러그인 루트에 `.claude-plugin/`, `agents/`, `commands/`, `skills/` 이외 폴더 없음

  **QA Scenarios:**
  ```
  Scenario: plugin.json 유효성 검증
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('plugins/hwpx-generator/.claude-plugin/plugin.json')); assert d['name']=='hwpx-generator'; assert d['author']['email']=='orientpine@gmail.com'; print('PASS')"
    Expected Result: PASS 출력
    Evidence: .sisyphus/evidence/task-1-plugin-json.txt

  Scenario: 디렉토리 구조 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/ — .claude-plugin/, agents/, commands/, skills/ 만 존재 확인
      2. ls plugins/hwpx-generator/skills/ — hwpx-core/, hwpx-templates/, hwpx-math/ 존재 확인
    Expected Result: 정확히 해당 폴더들만 존재
    Evidence: .sisyphus/evidence/task-1-directory-structure.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(hwpx-generator): scaffold plugin directory structure`
  - Files: `plugins/hwpx-generator/**`

---

- [ ] 2. hwpx-core SKILL.md 작성

  **What to do**:
  - Repo 1 (hwpxskill)의 SKILL.md에서 핵심 내용을 추출하여 hwpx-core SKILL.md 작성
  - **소스**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/SKILL.md` 를 webfetch로 읽기
  - 포함할 내용:
    - frontmatter: `name: hwpx-core`, description 작성
    - 환경 설정 (VENV, SKILL_DIR)
    - 디렉토리 구조 (이 스킬 기준으로 수정)
    - 워크플로우 1: XML-first 문서 생성 (build_hwpx.py 사용법)
    - section0.xml 작성 가이드 (필수 구조, 문단, 빈 줄, 서식 혼합, 표, ID 규칙)
    - header.xml 수정 가이드 (charPr 추가, 폰트 참조)
    - 템플릿별 스타일 ID 맵 (base, gonmun, report, minutes, proposal)
    - 워크플로우 2: 기존 문서 편집 (unpack→Edit→pack)
    - 워크플로우 3: 읽기/텍스트 추출
    - 워크플로우 4: 검증
    - 워크플로우 5: 레퍼런스 기반 문서 생성
    - 스크립트 요약표
    - 단위 변환표
    - Critical Rules
  - **500줄 이하로 압축** — 상세 표 크기 계산, 심층 XML 레퍼런스는 `references/hwpx-format.md`로 분리
  - 모든 스크립트 경로를 `scripts/` 상대경로 기준으로 작성
  - 스크립트 참조 시 3단계 패턴 포함 (상대경로 → Glob 폴백 → 확장 탐색)
  - `$SKILL_DIR` 기반 경로만 사용, 하드코딩 경로 금지

  **Must NOT do**:
  - SKILL.md 500줄 초과
  - `/mnt/skills/`, `/home/claude/` 등 하드코딩 경로
  - pypandoc-hwpx 관련 내용 포함
  - fix_namespaces.py 언급 (이것은 hwpx-templates 스킬 영역)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 750+ 줄 원본을 500줄 이하로 정보 손실 없이 압축하는 고급 편집 작업
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: 브라우저 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: [Tasks 6, 8, 11, 12, 13]
  - **Blocked By**: [Task 1] (디렉토리 존재 필요)

  **References**:

  **Pattern References**:
  - **원본 SKILL.md**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/SKILL.md` — 전체 내용을 webfetch로 읽고 핵심 추출
  - `plugins/visual-generator/skills/slide-renderer/SKILL.md` — 스크립트 경로 참조 3단계 패턴 모범 사례

  **API/Type References**:
  - AGENTS.md `Skill File Structure` 섹션 — SKILL.md frontmatter 필수 필드 (name, description)
  - AGENTS.md `SKILL.md frontmatter 필드` 표 — name 규칙 (소문자+하이픈, 디렉토리명 일치)

  **Acceptance Criteria**:
  - [ ] `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` 존재
  - [ ] frontmatter에 `name: hwpx-core`, `description` 포함
  - [ ] 줄 수 ≤ 500
  - [ ] 5개 워크플로우 모두 포함 (생성, 편집, 읽기, 검증, 레퍼런스 기반)
  - [ ] 5개 템플릿 스타일 ID 맵 포함
  - [ ] 스크립트 경로 3단계 패턴 포함
  - [ ] 하드코딩 경로 없음

  **QA Scenarios:**
  ```
  Scenario: SKILL.md frontmatter 유효성
    Tool: Bash
    Steps:
      1. head -5 plugins/hwpx-generator/skills/hwpx-core/SKILL.md — '---' 로 시작, name: hwpx-core 포함
      2. grep -c 'name: hwpx-core' 해당 파일 — 1 이상
    Expected Result: frontmatter 올바름
    Evidence: .sisyphus/evidence/task-2-frontmatter.txt

  Scenario: 줄 수 500 이하
    Tool: Bash
    Steps:
      1. wc -l plugins/hwpx-generator/skills/hwpx-core/SKILL.md — 숫자 확인
    Expected Result: 500 이하
    Evidence: .sisyphus/evidence/task-2-linecount.txt

  Scenario: 하드코딩 경로 없음
    Tool: Bash (grep)
    Steps:
      1. grep -n '/mnt/skills\|/home/claude\|/mnt/user-data' SKILL.md — 매칭 0건
    Expected Result: 매칭 없음
    Failure Indicators: 매칭 1건 이상
    Evidence: .sisyphus/evidence/task-2-no-hardcoded.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(hwpx-generator): scaffold plugin directory structure`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/SKILL.md`

---

- [ ] 3. hwpx-core scripts (6개 fetch + adapt)

  **What to do**:
  - Repo 1 (hwpxskill)에서 6개 Python 스크립트를 가져와 경로 수정 후 저장
  - **소스 base URL**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/`
  - 가져올 스크립트 목록:
    1. `build_hwpx.py` ← `scripts/build_hwpx.py` — 핵심 빌더
    2. `analyze_template.py` ← `scripts/analyze_template.py` — 레퍼런스 분석
    3. `validate.py` ← `scripts/validate.py` — 구조 검증
    4. `text_extract.py` ← `scripts/text_extract.py` — 텍스트 추출
    5. `office/unpack.py` ← `scripts/office/unpack.py` — HWPX→디렉토리
    6. `office/pack.py` ← `scripts/office/pack.py` — 디렉토리→HWPX
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-core/scripts/`
  - **경로 수정**: 하드코딩된 절대경로 → 상대경로로 변경 (있는 경우)
  - **의존성**: lxml 필요 (pip install lxml)

  **Must NOT do**:
  - 스크립트 자체 작성 (반드시 GitHub에서 fetch)
  - 스크립트 로직 변경 (경로 수정만 허용)
  - lxml 외 추가 의존성 도입

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 6개 스크립트를 GitHub에서 fetch하고 경로 적응 필요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: [Tasks 6, 9, 11, 12]
  - **Blocked By**: [Task 1]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/build_hwpx.py` — 핵심 빌더 원본
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/analyze_template.py` — 분석 도구 원본
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/validate.py` — 검증 도구 원본
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/text_extract.py` — 추출 도구 원본
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/office/unpack.py` — 언팩 원본
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/scripts/office/pack.py` — 팩 원본
  - AGENTS.md `SCRIPT PATH RESOLUTION` 섹션 — 스크립트 못 찾으면 자체 코드 작성 절대 금지

  **Acceptance Criteria**:
  - [ ] 6개 스크립트 모두 존재
  - [ ] 모든 스크립트 `python -c "import ast; ast.parse(...)"` 통과
  - [ ] 하드코딩 절대경로 없음

  **QA Scenarios:**
  ```
  Scenario: 모든 스크립트 존재 + 구문 유효
    Tool: Bash
    Steps:
      1. for f in build_hwpx.py analyze_template.py validate.py text_extract.py office/unpack.py office/pack.py; do python -c "import ast; ast.parse(open('plugins/hwpx-generator/skills/hwpx-core/scripts/'+'$f').read())" && echo "OK: $f"; done
    Expected Result: 6개 모두 OK
    Evidence: .sisyphus/evidence/task-3-scripts-valid.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/**`

---

- [ ] 4. hwpx-core templates (5 template sets fetch)

  **What to do**:
  - Repo 1 (hwpxskill)에서 5개 템플릿 세트를 가져와 저장
  - **소스 base URL**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/templates/`
  - 가져올 템플릿:
    1. `base/` — 기본 스켈레톤 (mimetype, META-INF/*, version.xml, settings.xml, Preview/*, Contents/header.xml, Contents/section0.xml, Contents/content.hpf)
    2. `gonmun/` — 공문 오버레이 (Contents/header.xml, Contents/section0.xml)
    3. `report/` — 보고서 오버레이
    4. `minutes/` — 회의록 오버레이
    5. `proposal/` — 제안서 오버레이
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-core/templates/`
  - 레포의 `templates/` 디렉토리 구조를 그대로 재현
  - **base 템플릿은 필수** — 다른 템플릿은 base 위에 오버라이드하는 구조

  **Must NOT do**:
  - 템플릿 XML 내용 수정 (원본 그대로 가져오기)
  - base/ 이외 템플릿에 전체 파일 포함 (오버레이 파일만)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 다수의 XML/바이너리 파일을 GitHub에서 fetch하여 정확한 구조로 저장
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: [Tasks 7, 10]
  - **Blocked By**: [Task 1]

  **References**:
  - GitHub repo tree: `https://github.com/Canine89/hwpxskill/tree/main/templates` — 전체 템플릿 구조
  - Repo 1 SKILL.md 참조: base 템플릿 = ZIP 스켈레톤, 오버레이 템플릿 = header.xml + section0.xml만 오버라이드

  **Acceptance Criteria**:
  - [ ] `templates/base/` 디렉토리에 mimetype, META-INF/, Contents/ 존재
  - [ ] 5개 템플릿 디렉토리 모두 존재 (base, gonmun, report, minutes, proposal)
  - [ ] base/Contents/header.xml, base/Contents/section0.xml 존재

  **QA Scenarios:**
  ```
  Scenario: 템플릿 디렉토리 구조 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-core/templates/ — base/, gonmun/, report/, minutes/, proposal/ 확인
      2. ls plugins/hwpx-generator/skills/hwpx-core/templates/base/ — mimetype 등 핵심 파일 확인
    Expected Result: 5개 디렉토리 + base 내 필수 파일 존재
    Evidence: .sisyphus/evidence/task-4-templates.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Files: `plugins/hwpx-generator/skills/hwpx-core/templates/**`

---

- [ ] 5. hwpx-core references (hwpx-format.md fetch)

  **What to do**:
  - Repo 1 (hwpxskill)에서 OWPML XML 요소 레퍼런스 문서를 가져옴
  - **소스**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/references/hwpx-format.md`
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-core/references/hwpx-format.md`
  - 추가로 SKILL.md에서 분리한 심층 내용(표 크기 계산 상세 등)이 있으면 별도 reference 파일 생성

  **Must NOT do**:
  - reference 내용 자체 작성 (GitHub에서 fetch)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: GitHub에서 레퍼런스 문서 fetch + 필요시 SKILL.md 초과분 분리
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: [Tasks 6, 8]
  - **Blocked By**: [Task 1]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill/main/references/hwpx-format.md` — OWPML XML 레퍼런스 원본

  **Acceptance Criteria**:
  - [ ] `plugins/hwpx-generator/skills/hwpx-core/references/hwpx-format.md` 존재
  - [ ] 파일이 비어있지 않음 (10줄 이상)

  **QA Scenarios:**
  ```
  Scenario: hwpx-format.md 존재 및 내용 검증
    Tool: Bash
    Steps:
      1. wc -l plugins/hwpx-generator/skills/hwpx-core/references/hwpx-format.md — 10줄 이상
    Expected Result: 10줄 이상
    Evidence: .sisyphus/evidence/task-5-reference.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Files: `plugins/hwpx-generator/skills/hwpx-core/references/hwpx-format.md`

---

### Wave 2 Tasks (Specialized Skills — after Wave 1, 5 parallel)


- [ ] 6. hwpx-templates SKILL.md + scripts

  **What to do**:
  - Repo 2 (gonggong_hwpxskills)의 SKILL.md에서 ZIP-level 치환 워크플로우 내용을 추출하여 통합
  - **소스 SKILL.md**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/SKILL.md`
  - **소스 스크립트**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/scripts/fix_namespaces.py`
  - SKILL.md 포함할 내용:
    - frontmatter: `name: hwpx-templates`, description
    - 양식 선택 정책 (사용자 업로드 > 기본 양식 > new())
    - 필수 워크플로우 (양식복사 - ObjectFinder조사 - ZIP치환 - 네임스페이스 - 검증)
    - `zip_replace()` 함수 (일괄 치환) - 인라인 코드 포함
    - `zip_replace_sequential()` 함수 (순차 치환) - 인라인 코드 포함
    - ObjectFinder 텍스트 전수 조사 방법
    - 기본 양식(report-template.hwpx) 활용 가이드
    - 사용자 업로드 양식 활용 가이드
    - 필수 후처리: fix_namespaces.py 설명
    - Quick Reference 표
    - 주의사항 (10개)
  - **경로 수정 필수**: 모든 `/mnt/skills/user/hwpx/` -> `$SKILL_DIR/`, `/home/claude/` -> 상대경로로 변경
  - fix_namespaces.py를 `scripts/fix_namespaces.py`로 저장
  - **중요**: fix_namespaces.py는 regex/string 방식 유지 (lxml 리팩토링 절대 금지 - ns0 재도입 방지)
  - **중요**: fix_namespaces.py는 ZIP-level 치환 후에만 필요, XML-first 빌드(hwpx-core)에는 불필요함을 명시

  **Must NOT do**:
  - fix_namespaces.py를 lxml 기반으로 리팩토링 (regex 접근이 의도적 설계)
  - python-hwpx `HwpxDocument.open()` 사용 권장 (ZIP-level 치환 우선)
  - 하드코딩 경로 (`/mnt/skills/`, `/home/claude/`, `/mnt/user-data/`)
  - SKILL.md 500줄 초과

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: repo2의 워크플로우를 새 컨텍스트에 맞게 재구성 + 경로 수정 + 통합
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Tasks 2, 3, 5]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/SKILL.md` - ZIP 치환 워크플로우 원본
  - `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/scripts/fix_namespaces.py` - 네임스페이스 후처리 스크립트
  - Task 2의 hwpx-core SKILL.md - 교차 참조 확인 (워크플로우 영역 분리)

  **Acceptance Criteria**:
  - [ ] SKILL.md 존재, frontmatter `name: hwpx-templates`
  - [ ] 줄 수 <= 500
  - [ ] zip_replace, zip_replace_sequential 함수 포함
  - [ ] fix_namespaces.py 스크립트 존재
  - [ ] 하드코딩 경로 없음
  - [ ] fix_namespaces.py에 lxml import 없음 (regex/re 사용)

  **QA Scenarios:**
  ```
  Scenario: fix_namespaces.py가 regex 방식인지 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c 'import lxml' plugins/hwpx-generator/skills/hwpx-templates/scripts/fix_namespaces.py - 0 기대
      2. grep -c 'import re' 같은 파일 - 1 이상 기대
    Expected Result: lxml 0건, re 1건 이상
    Evidence: .sisyphus/evidence/task-6-fix-namespaces-regex.txt

  Scenario: SKILL.md에 하드코딩 경로 없음
    Tool: Bash (grep)
    Steps:
      1. grep -n '/mnt/skills\|/home/claude\|/mnt/user-data' plugins/hwpx-generator/skills/hwpx-templates/SKILL.md
    Expected Result: 매칭 0건
    Evidence: .sisyphus/evidence/task-6-no-hardcoded.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(hwpx-generator): add hwpx-templates and hwpx-math skills`
  - Files: `plugins/hwpx-generator/skills/hwpx-templates/**`

---

- [ ] 7. hwpx-templates references + assets

  **What to do**:
  - Repo 2 (gonggong_hwpxskills)에서 스타일 가이드와 템플릿 자산을 가져옴
  - **소스 레퍼런스**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/references/`
    1. `report-style.md` - 보고서 스타일 가이드
    2. `official-doc-style.md` - 공문서 스타일 가이드
    3. `xml-internals.md` - 저수준 XML 조작 가이드
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-templates/references/`
  - **소스 자산**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/assets/report-template.hwpx`
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx`
  - report-template.hwpx는 바이너리 파일이므로 `curl -L -o` 사용

  **Must NOT do**:
  - 레퍼런스 내용 자체 작성

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 8, 9, 10)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Task 4]

  **References**:
  - `https://github.com/Canine89/gonggong_hwpxskills/tree/main/references` - 레퍼런스 디렉토리
  - `https://github.com/Canine89/gonggong_hwpxskills/tree/main/assets` - 자산 디렉토리

  **Acceptance Criteria**:
  - [ ] `references/report-style.md` 존재
  - [ ] `references/official-doc-style.md` 존재
  - [ ] `references/xml-internals.md` 존재
  - [ ] `assets/report-template.hwpx` 존재 (0 bytes 아님)

  **QA Scenarios:**
  ```
  Scenario: 레퍼런스 + 자산 파일 존재 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-templates/references/ - 3개 .md 파일
      2. ls -la plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx - 0 bytes 아님
    Expected Result: 3개 reference + 1개 asset 모두 비어있지 않음
    Evidence: .sisyphus/evidence/task-7-refs-assets.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 8. hwpx-math SKILL.md 작성

  **What to do**:
  - Repo 3 (hwpxskill-math)의 SKILL.md에서 핵심 내용을 추출하여 hwpx-math SKILL.md 작성
  - **소스**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md`
  - SKILL.md 포함할 내용:
    - frontmatter: `name: hwpx-math`, description
    - 환경 설정 (VENV, SKILL_DIR, HWPX_SKILL_DIR -> hwpx-core 스킬 경로)
    - 핵심 워크플로우: JSON -> HWPX 문제지 (빌드 명령어)
    - 문제 JSON 형식 (학력평가 + worksheet)
    - 필드 설명표
    - 수식 XML 구조 (hp:equation 간략 설명, 상세는 references로)
    - 2단 레이아웃 설정 + 페이지 설정
    - 스타일 ID 맵 (charPr/paraPr/tabPr/borderFill)
    - 학력평가 시험지 레이아웃 구조
    - hwpx-core 스킬과의 연동 안내 (validate.py, unpack/pack 교차참조)
    - 단위 변환표 (문제지 특화)
    - Critical Rules
  - **500줄 이하로 압축** - 수식 스크립트 레퍼런스(기본~미적분/기하)는 `references/equation-reference.md`로 분리
  - **500줄 이하로 압축** - 도형 그래프 스펙(삼각형/원/사각형/좌표/입체)은 `references/geometry-reference.md`로 분리
  - hwpx-core 스킬의 validate.py 교차참조 패턴 포함:
    ```
    ### hwpx-core 스킬 검증 도구 사용
    Step 1. 상대경로: ../hwpx-core/scripts/validate.py
    Step 2. Glob 폴백: **/hwpx-core/scripts/validate.py
    Step 3. Glob: **/validate.py
    ```

  **Must NOT do**:
  - SKILL.md 500줄 초과
  - 수식 스크립트에 LaTeX 문법 사용 (한컴 문법만)
  - 하드코딩 경로

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 750+ 줄 원본을 500줄로 압축 + references 분리 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 9, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Tasks 2, 5]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md` - 수학 스킬 원본 (750+줄)
  - Task 2의 hwpx-core SKILL.md - 교차참조 확인 (검증 도구 경로)

  **Acceptance Criteria**:
  - [ ] SKILL.md 존재, frontmatter `name: hwpx-math`
  - [ ] 줄 수 <= 500
  - [ ] hwpx-core 교차참조 패턴 포함
  - [ ] 수식 스크립트 레퍼런스는 `references/`로 분리됨

  **QA Scenarios:**
  ```
  Scenario: SKILL.md 줄 수 + 교차참조 검증
    Tool: Bash
    Steps:
      1. wc -l plugins/hwpx-generator/skills/hwpx-math/SKILL.md - <= 500
      2. grep -c 'hwpx-core' 같은 파일 - 1 이상 (교차참조 존재)
    Expected Result: 500 이하 + 교차참조 1건 이상
    Evidence: .sisyphus/evidence/task-8-math-skill.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 9. hwpx-math scripts (7 modules fetch + adapt)

  **What to do**:
  - Repo 3 (hwpxskill-math)에서 7개 Python 모듈을 가져와 저장
  - **소스 base URL**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/scripts/`
  - 가져올 스크립트:
    1. `build_math_hwpx.py` - CLI + 오케스트레이션
    2. `xml_primitives.py` - IDGen, STYLE 상수, 기본 문단/수식 생성기
    3. `exam_helpers.py` - 시험지 전용 XML 생성기
    4. `table_layout.py` - 투명 테이블 레이아웃
    5. `section_generators.py` - worksheet/exam section0.xml 조립
    6. `hwpx_utils.py` - 검증/패키징/메타데이터
    7. `graph_generator.py` - 그래프 PNG 생성 (matplotlib)
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-math/scripts/`
  - **의존성**: lxml, matplotlib

  **Must NOT do**:
  - 스크립트 자체 작성 (반드시 GitHub에서 fetch)
  - 모듈 간 의존 구조 변경 (primitives -> helpers -> layout -> section -> build 순서 유지)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Task 3]

  **References**:
  - `https://github.com/Canine89/hwpxskill-math/tree/main/scripts` - 전체 스크립트 목록
  - Repo 3 SKILL.md `모듈 의존 구조` 섹션 - 순환 없는 의존 그래프

  **Acceptance Criteria**:
  - [ ] 7개 스크립트 모두 존재
  - [ ] 모든 스크립트 AST 파싱 통과

  **QA Scenarios:**
  ```
  Scenario: 7개 모듈 존재 + 구문 유효
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-math/scripts/*.py | wc -l - 7개 이상
      2. python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('plugins/hwpx-generator/skills/hwpx-math/scripts/*.py')]" - 오류 없음
    Expected Result: 7개 존재, 모두 파싱 통과
    Evidence: .sisyphus/evidence/task-9-math-scripts.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 10. hwpx-math templates + references + examples

  **What to do**:
  - Repo 3에서 템플릿, 레퍼런스, 예제를 가져와 저장
  - **템플릿**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/templates/base/` -> `templates/math-base/` (이름 변경! hwpx-core의 base와 충돌 방지)
  - **레퍼런스** (SKILL.md에서 분리한 내용으로 작성):
    1. `references/equation-reference.md` - 한컴 수식 스크립트 전체 레퍼런스 (기본 규칙, 분수/루트, 첨자, 적분/합, 극한, 괄호, 행렬, 연립, 장식, 그리스문자, 특수기호, 폰트, 내장함수, 학년별 예시)
    2. `references/geometry-reference.md` - 도형 그래프 타입 5개 전체 스펙 (triangle, circle, quadrilateral, coordinate, solid3d)
  - **예제**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/examples/` 에서 sample JSON + 빌드 스크립트 fetch
  - 레퍼런스 작성 시 Repo 3 SKILL.md의 해당 섹션을 그대로 추출하여 저장

  **Must NOT do**:
  - math 템플릿을 `base/`로 저장 (반드시 `math-base/`)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Task 4]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md` - 수식/도형 섹션 추출 원본
  - `https://github.com/Canine89/hwpxskill-math/tree/main/templates` - 템플릿 원본
  - `https://github.com/Canine89/hwpxskill-math/tree/main/examples` - 예제 원본

  **Acceptance Criteria**:
  - [ ] `templates/math-base/` 디렉토리 존재 (base/ 아님!)
  - [ ] `references/equation-reference.md` 존재 (100+ 줄)
  - [ ] `references/geometry-reference.md` 존재 (50+ 줄)
  - [ ] `examples/` 내 sample JSON 1개 이상 존재

  **QA Scenarios:**
  ```
  Scenario: 템플릿 디렉토리 이름 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-math/templates/ - math-base/ 존재, base/ 없음
    Expected Result: math-base 존재, base 없음
    Evidence: .sisyphus/evidence/task-10-math-templates.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

### Wave 3 Tasks (Agents + Command - after Wave 2, 3 parallel)

---

- [ ] 11. hwpx-builder agent 작성

  **What to do**:
  - HWPX 문서를 XML-first 방식으로 생성하는 전문 에이전트 작성
  - 파일: `plugins/hwpx-generator/agents/hwpx-builder.md`
  - 에이전트 역할:
    - 사용자 요청을 분석하여 적절한 문서 유형 결정 (공문/보고서/회의록/제안서/수학문제지)
    - hwpx-core 스킬의 build_hwpx.py를 사용한 XML-first 빌드
    - hwpx-templates 스킬의 ZIP 치환 워크플로우 활용
    - hwpx-math 스킬의 수학 문제지 생성
  - frontmatter: `name: hwpx-builder`, description에 "Use PROACTIVELY when..." 포함, `model: sonnet`
  - 에이전트 구조:
    - Purpose: HWPX 문서 생성 전문가
    - Capabilities: XML-first 빌드, ZIP 치환, 수식 문제지
    - Workflow: 문서 유형 판별 -> 템플릿 선택 -> 콘텐츠 생성 -> 빌드 -> 검증
    - Constraints: HWPX만 (HWP 미지원), 검증 필수, 네임스페이스 후처리 (ZIP 치환 시)

  **Must NOT do**:
  - 에이전트가 직접 XML 코드 하드코딩 (스킬의 스크립트 사용)
  - HWP 파일 처리 약속

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 3개 스킬을 조합하는 복잡한 에이전트 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Tasks 2, 3, 6, 8, 9]

  **References**:
  - `plugins/isd-generator/agents/chapter1.md` - 에이전트 .md 포맷 참고 (프로젝트 표준)
  - Task 2 (hwpx-core SKILL.md) - 빌드 워크플로우 이해
  - Task 6 (hwpx-templates SKILL.md) - ZIP 치환 워크플로우 이해
  - Task 8 (hwpx-math SKILL.md) - 수학 문제지 워크플로우 이해
  - AGENTS.md `Agent File Structure` 섹션 - frontmatter 필드 규칙

  **Acceptance Criteria**:
  - [ ] `agents/hwpx-builder.md` 존재
  - [ ] frontmatter에 name, description, model 포함
  - [ ] description에 "Use when" 또는 "Use PROACTIVELY when" 포함
  - [ ] 3개 스킬 모두 참조

  **QA Scenarios:**
  ```
  Scenario: 에이전트 frontmatter + 스킬 참조 검증
    Tool: Bash
    Steps:
      1. head -10 plugins/hwpx-generator/agents/hwpx-builder.md - frontmatter 확인
      2. grep -c 'hwpx-core\|hwpx-templates\|hwpx-math' 같은 파일 - 3 이상
    Expected Result: frontmatter 올바름 + 3개 스킬 참조
    Evidence: .sisyphus/evidence/task-11-builder-agent.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(hwpx-generator): add agents and orchestrator command`

---

- [ ] 12. hwpx-analyzer agent 작성

  **What to do**:
  - 기존 HWPX 파일을 분석하고 역공학하는 전문 에이전트 작성
  - 파일: `plugins/hwpx-generator/agents/hwpx-analyzer.md`
  - 에이전트 역할:
    - 사용자 제공 HWPX 파일을 analyze_template.py로 심층 분석
    - 스타일 ID, 표 구조, 레이아웃 패턴을 추출
    - 분석 결과를 기반으로 동일 레이아웃의 새 문서 생성 가이드 제공
    - unpack/pack을 사용한 기존 문서 편집
  - frontmatter: `name: hwpx-analyzer`, description에 "Use when..." 포함, `model: sonnet`
  - 에이전트 구조:
    - Purpose: HWPX 문서 분석/역공학 전문가
    - Capabilities: 심층 분석, 스타일 추출, 레이아웃 복제, 문서 편집
    - Workflow: HWPX 수신 -> analyze_template.py 실행 -> header.xml 추출 -> 분석 리포트 -> 새 문서 생성 또는 편집
    - Constraints: HWPX만, 원본 스타일 ID 보존, charPrIDRef/paraPrIDRef 정합성

  **Must NOT do**:
  - HWP 파일 처리 약속
  - 스타일 ID 임의 변경 권장

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 11, 13)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Tasks 2, 3, 6]

  **References**:
  - Task 2 (hwpx-core SKILL.md) - 워크플로우 5: 레퍼런스 기반 문서 생성 이해
  - `plugins/general-agents/agents/interview.md` - 에이전트 포맷 참고

  **Acceptance Criteria**:
  - [ ] `agents/hwpx-analyzer.md` 존재
  - [ ] frontmatter에 name, description, model 포함
  - [ ] analyze_template.py 참조 포함

  **QA Scenarios:**
  ```
  Scenario: 에이전트 파일 + analyze 참조 검증
    Tool: Bash
    Steps:
      1. head -10 plugins/hwpx-generator/agents/hwpx-analyzer.md - frontmatter 확인
      2. grep -c 'analyze_template' 같은 파일 - 1 이상
    Expected Result: frontmatter 올바름 + analyze 참조 존재
    Evidence: .sisyphus/evidence/task-12-analyzer-agent.txt
  ```

  **Commit**: YES (groups with Wave 3)

---

- [ ] 13. hwpx-generate command 작성

  **What to do**:
  - HWPX 문서 생성 전체를 오케스트레이션하는 커맨드 작성
  - 파일: `plugins/hwpx-generator/commands/hwpx-generate.md`
  - 커맨드 워크플로우:
    - Phase 1: 요구사항 파악 (문서 유형, 내용, 양식)
    - Phase 2: 양식 선택 (사용자 업로드 > 기본 양식 > XML-first)
    - Phase 3: 문서 생성
      - 양식 있으면 -> hwpx-builder (ZIP 치환 모드)
      - 양식 없으면 -> hwpx-builder (XML-first 모드)
      - 수학 문제지면 -> hwpx-builder (hwpx-math 모드)
    - Phase 4: 검증 (validate.py)
    - Phase 5: 결과 전달
  - $ARGUMENTS로 사용자 입력 받기
  - Task tool로 hwpx-builder, hwpx-analyzer 에이전트 호출
  - frontmatter 없음 (커맨드는 frontmatter 없음)

  **Must NOT do**:
  - 커맨드에 frontmatter 추가 (커맨드는 frontmatter 없음)
  - 에이전트 로직 직접 포함 (Task tool로 위임)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 3개 스킬 + 2개 에이전트를 조합하는 오케스트레이터 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (agents 완성 후)
  - **Parallel Group**: Wave 3
  - **Blocks**: [Tasks 14, 15]
  - **Blocked By**: [Tasks 6, 7, 8, 9, 10, 11, 12]

  **References**:
  - `plugins/isd-generator/commands/isd-generate.md` - 커맨드 포맷 참고 (프로젝트 표준 오케스트레이터)
  - `plugins/visual-generator/commands/visual-generate.md` - 또 다른 커맨드 참고
  - AGENTS.md `Commands (커맨드)` 섹션 - 커맨드 구조 규칙

  **Acceptance Criteria**:
  - [ ] `commands/hwpx-generate.md` 존재
  - [ ] frontmatter 없음
  - [ ] Phase 1-5 워크플로우 포함
  - [ ] Task tool로 에이전트 호출 패턴 포함
  - [ ] $ARGUMENTS 사용

  **QA Scenarios:**
  ```
  Scenario: 커맨드 파일 구조 검증
    Tool: Bash
    Steps:
      1. head -3 plugins/hwpx-generator/commands/hwpx-generate.md - '---'로 시작하지 않음 (frontmatter 없음)
      2. grep -c 'Task tool\|subagent_type' 같은 파일 - 1 이상
      3. grep -c 'ARGUMENTS' 같은 파일 - 1 이상
    Expected Result: frontmatter 없음 + Task tool 참조 + ARGUMENTS 참조
    Evidence: .sisyphus/evidence/task-13-command.txt
  ```

  **Commit**: YES (groups with Wave 3)

---

### Wave 4 Tasks (Registry + Cleanup - after Wave 3, 2 sequential)

---

- [ ] 14. Update marketplace.json + delete hwpx-converter

  **What to do**:
  - `.claude-plugin/marketplace.json`에서:
    1. `hwpx-converter` 항목 제거
    2. `hwpx-generator` 항목 추가:
       ```json
       {
         "name": "hwpx-generator",
         "source": "./plugins/hwpx-generator",
         "description": "HWPX 문서 생성/편집/분석 통합 플러그인. XML-first 빌드 + ZIP 치환 + 수학 수식 지원.",
         "version": "1.0.0",
         "strict": true,
         "agents": [
           "./agents/hwpx-builder.md",
           "./agents/hwpx-analyzer.md"
         ],
         "skills": ["./skills"]
       }
       ```
  - `plugins/hwpx-converter/` 디렉토리 전체 삭제
  - marketplace.json metadata.version은 변경 불필요 (기존 플러그인 교체는 마켓플레이스 MINOR 아님)

  **Must NOT do**:
  - marketplace.json의 다른 플러그인 항목 수정
  - hwpx-converter 삭제 전 백업 생성 (git에 히스토리 있음)
  - `"skills": ["./skills/"]` (trailing slash 금지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: JSON 편집 + 디렉토리 삭제
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: [Task 15, F1-F4]
  - **Blocked By**: [Task 13]

  **References**:
  - `.claude-plugin/marketplace.json` (현재 파일) - 기존 구조 확인
  - AGENTS.md `marketplace.json plugin 항목 필드` 표 - 필수 필드 확인
  - AGENTS.md `Forbidden Patterns` - `"skills": ["./skills/"]` trailing slash 금지

  **Acceptance Criteria**:
  - [ ] marketplace.json에 hwpx-generator 존재
  - [ ] marketplace.json에 hwpx-converter 없음
  - [ ] marketplace.json이 유효한 JSON
  - [ ] `plugins/hwpx-converter/` 디렉토리 없음
  - [ ] `"strict": true` 설정
  - [ ] `"skills": ["./skills"]` (trailing slash 없음)

  **QA Scenarios:**
  ```
  Scenario: marketplace.json 유효성 + 플러그인 교체 검증
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in d['plugins']]; assert 'hwpx-generator' in names; assert 'hwpx-converter' not in names; print('PASS')"
      2. ls plugins/hwpx-converter/ 2>&1 - "No such file or directory" 기대
    Expected Result: PASS + 디렉토리 없음
    Evidence: .sisyphus/evidence/task-14-marketplace.txt

  Scenario: hwpx-generator 항목 상세 검증
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); p=[x for x in d['plugins'] if x['name']=='hwpx-generator'][0]; assert p['strict']==True; assert './skills' in p.get('skills',[]); assert len(p.get('agents',[]))>=2; print('PASS')"
    Expected Result: PASS
    Evidence: .sisyphus/evidence/task-14-generator-entry.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx-generator): register plugin and replace hwpx-converter`
  - Files: `.claude-plugin/marketplace.json`, `plugins/hwpx-converter/` (deleted)

---

- [ ] 15. Update AGENTS.md

  **What to do**:
  - `AGENTS.md` 업데이트:
    1. **Generated 날짜** 업데이트 (현재 날짜)
    2. **STRUCTURE 섹션**: `hwpx-converter` 트리 제거, `hwpx-generator` 트리 추가
       - agents/ (hwpx-builder.md, hwpx-analyzer.md)
       - commands/ (hwpx-generate.md)
       - skills/ (hwpx-core/, hwpx-templates/, hwpx-math/)
    3. **WHERE TO LOOK 표**: hwpx-converter 행 교체 -> hwpx-generator 행들 추가
       - HWPX 문서 생성: `plugins/hwpx-generator/commands/hwpx-generate.md`
       - HWPX XML-first 빌드: `plugins/hwpx-generator/skills/hwpx-core/SKILL.md`
       - HWPX 템플릿 치환: `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md`
       - 수학 수식 문제지: `plugins/hwpx-generator/skills/hwpx-math/SKILL.md`
    4. **COMMANDS 섹션**: 기존 hwpx 관련 명령어 업데이트
    5. **UNIQUE STYLES 섹션**: hwpx-generator 특이사항 추가 (fix_namespaces 필수, 한컴 수식 스크립트)
    6. **README.md 표**: hwpx-converter -> hwpx-generator로 교체

  **Must NOT do**:
  - AGENTS.md의 다른 섹션 불필요하게 수정
  - README.md 외 다른 파일 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 기존 문서의 특정 섹션만 교체/추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Task 14 후)
  - **Parallel Group**: Wave 4
  - **Blocks**: [F1-F4]
  - **Blocked By**: [Task 14]

  **References**:
  - `AGENTS.md` (현재 파일) - 기존 구조 확인
  - AGENTS.md `MANDATORY: AGENTS.md 최신화` 섹션 - 업데이트 트리거 및 절차

  **Acceptance Criteria**:
  - [ ] AGENTS.md Generated 날짜 업데이트됨
  - [ ] STRUCTURE에 hwpx-generator 포함, hwpx-converter 없음
  - [ ] WHERE TO LOOK에 hwpx-generator 관련 행 포함

  **QA Scenarios:**
  ```
  Scenario: AGENTS.md 업데이트 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c 'hwpx-generator' AGENTS.md - 3 이상
      2. grep -c 'hwpx-converter' AGENTS.md - 0
    Expected Result: hwpx-generator 3+ 건, hwpx-converter 0건
    Evidence: .sisyphus/evidence/task-15-agents-md.txt
  ```

  **Commit**: YES
  - Message: `docs: update AGENTS.md and README.md for hwpx-generator`
  - Files: `AGENTS.md`, `README.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read SKILL.md, check scripts exist, verify marketplace.json entry). For each "Must NOT Have": search codebase for forbidden patterns (hardcoded paths, lxml in fix_namespaces, pypandoc dependency). Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Verify: All Python scripts pass `python -c "import ast; ast.parse(open('...').read())"`. All SKILL.md files have valid YAML frontmatter (name, description). No hardcoded paths. No `as any`/empty catches equivalent. No placeholder text remaining. Check AI slop: excessive comments, over-abstraction.
  Output: `Scripts [N/N valid] | SKILL.md [N/N valid] | Paths [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Verify plugin directory structure matches AGENTS.md standard. Verify all marketplace.json paths resolve. Verify SKILL.md cross-references (e.g., math references core validate.py path). Check each template directory has required files. Verify AGENTS.md sections are updated and accurate.
  Output: `Structure [PASS/FAIL] | Marketplace [PASS/FAIL] | Cross-refs [N/N] | AGENTS.md [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual files created. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Verify no files were created outside `plugins/hwpx-generator/`, `marketplace.json`, and `AGENTS.md`. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Scope [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(hwpx-generator): scaffold plugin structure and hwpx-core skill` — plugins/hwpx-generator/**
- **Wave 2**: `feat(hwpx-generator): add hwpx-templates and hwpx-math skills` — plugins/hwpx-generator/skills/**
- **Wave 3**: `feat(hwpx-generator): add agents and orchestrator command` — plugins/hwpx-generator/agents/**, plugins/hwpx-generator/commands/**
- **Wave 4**: `feat(hwpx-generator): register plugin and replace hwpx-converter` — .claude-plugin/marketplace.json, AGENTS.md, plugins/hwpx-converter/ (deleted)

---

## Success Criteria

### Verification Commands
```bash
# Plugin structure exists
ls plugins/hwpx-generator/.claude-plugin/plugin.json  # Expected: file exists
ls plugins/hwpx-generator/agents/hwpx-builder.md      # Expected: file exists
ls plugins/hwpx-generator/agents/hwpx-analyzer.md     # Expected: file exists
ls plugins/hwpx-generator/commands/hwpx-generate.md   # Expected: file exists
ls plugins/hwpx-generator/skills/hwpx-core/SKILL.md   # Expected: file exists
ls plugins/hwpx-generator/skills/hwpx-templates/SKILL.md  # Expected: file exists
ls plugins/hwpx-generator/skills/hwpx-math/SKILL.md   # Expected: file exists

# Old plugin removed
ls plugins/hwpx-converter/  # Expected: directory does not exist

# marketplace.json valid
python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in d['plugins']]; assert 'hwpx-generator' in names; assert 'hwpx-converter' not in names; print('OK')"

# SKILL.md line counts (each < 500)
wc -l plugins/hwpx-generator/skills/*/SKILL.md  # Expected: each < 500

# All Python scripts syntactically valid
find plugins/hwpx-generator -name "*.py" -exec python -c "import ast,sys; ast.parse(open(sys.argv[1]).read()); print(f'OK: {sys.argv[1]}')" {} \;
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Plugin structure follows AGENTS.md conventions
- [ ] AGENTS.md updated with new plugin info
- [ ] marketplace.json updated and valid JSON
- [ ] hwpx-converter deleted
