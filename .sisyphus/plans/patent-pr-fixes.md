# PR #2 patent-trend-analyzer 전체 수정 계획

## TL;DR

> **Quick Summary**: PR #2(patent-trend-analyzer)에서 발견된 14개 이슈 + 데드코드 제거 + 리베이스를 직접 수정하여 머지 가능 상태로 만듦.
> 
> **Deliverables**:
> - 리베이스 완료된 PR 브랜치 (main 2.3.0 기반)
> - 14개 이슈 수정 + patent_sim.py 제거
> - 5개 원자적 커밋 (rebase 포함 6개)
> - AGENTS.md + README.md 업데이트
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 0 (rebase) → Task 1-2 → Task 3-7 → Task 8-10 → Task 11-12 → Final Verification

---

## Context

### Original Request
PR #2 심층 리뷰에서 발견된 모든 이슈(MUST 5 + SHOULD 5 + NICE TO HAVE 4 = 14건)를 직접 수정.

### Interview Summary
**Key Discussions**:
- 수정 범위: 전체 14건 포함
- 실행 방식: PR 브랜치 체크아웃 후 직접 코드 수정 + 커밋
- author.email: orientpine@gmail.com으로 변경, contributor 필드에 원저자 보존
- 머지 충돌: Rebase 방식으로 해결
- patent_sim.py: 데드코드이므로 제거 (+ scikit-learn, networkx, fastapi 의존성 정리)

### Metis Review
**Identified Gaps** (addressed):
- PR이 main 2.1.0 기반이라 현재 main(2.3.0)과 충돌 → Phase 0에 rebase 추가
- marketplace.json 버전이 2.3.0이 아니라 2.4.0이어야 함 → 버전 수정
- patent_sim.py가 데드코드 + 내부 URL 노출 위험 → 제거 결정
- foreign/batch_export_tool.py만 코드 중복 (다른 2개는 정상) → 범위 축소
- basicConfig 3곳 중복 호출 → 전부 정리

---

## Work Objectives

### Core Objective
PR #2를 머지 가능한 상태로 만들기: 리베이스 + 14개 이슈 수정 + 데드코드 제거 + 문서 업데이트.

### Concrete Deliverables
- 수정 완료된 PR 브랜치 (6개 커밋)
- 깨끗한 `git status` (충돌 없음)
- 모든 Python 파일 구문 검증 통과

### Definition of Done
- [ ] `gh pr view 2 --json mergeable` → `"MERGEABLE"` 또는 충돌 없음
- [ ] 모든 Python 파일 `py_compile.compile()` 통과
- [ ] 모든 JSON 파일 `json.load()` 통과
- [ ] `plugin.json` author.email = orientpine@gmail.com
- [ ] `marketplace.json` version = 2.4.0

### Must Have
- 14개 리뷰 이슈 전체 수정
- patent_sim.py 제거 + 관련 의존성 정리
- 리베이스 완료 (main 2.3.0 기반)
- AGENTS.md / README.md 업데이트

### Must NOT Have (Guardrails)
- 도구 등록명, MCP 프로토콜 동작 변경 금지
- patent-trend-analyzer 외 플러그인 코드 수정 금지 (marketplace.json, AGENTS.md, README.md 제외)
- 새 기능 추가 금지
- `--force` push 금지 (사전 확인 없이)
- 기존 테스트 삭제 금지

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (플러그인 .md + Python MCP 서버, KIPRIS API 키 필요)
- **Automated tests**: YES (TDD — 테스트 먼저 생성 후 개발)
- **Framework**: Python assertion 스크립트 (`tests/test_pr_fixes.py`)
- **TDD 워크플로우**: 각 Task는 반드시 아래 순서를 따름:
  1. **RED**: QA 시나리오의 assertion 스크립트를 먼저 작성하여 **현재 버그/이슈가 감지되는지 확인** (테스트 실패 = 버그 존재 확인)
  2. **GREEN**: 코드 수정 적용 → assertion 스크립트 재실행 → **PASS 확인**
  3. **REFACTOR**: 불필요한 코드 정리 (해당 시)

### TDD 실행 방식
각 Task의 QA 시나리오 자체가 TDD artifact입니다. 별도 테스트 파일을 생성하지 않습니다.

**RED-GREEN 워크플로우 (각 Task에서 반드시 수행)**:
1. **RED**: 수정 **전에** 해당 Task의 QA assertion 명령을 실행 → **실패** 확인 (버그가 존재함을 증명)
   - evidence 파일: `.sisyphus/evidence/task-{N}-{slug}-RED.txt`
2. **GREEN**: 코드 수정 적용 → QA assertion 재실행 → **성공** 확인
   - evidence 파일: `.sisyphus/evidence/task-{N}-{slug}.txt` (기존 경로)
3. RED evidence와 GREEN evidence 모두 보존하여 수정 전후 차이를 기록

**예시** (Task 4 — api/utils.py 오탈자):
```bash
# RED: 수정 전 — 오탈자 존재 확인 (의도적 실패)
python3 -c "content=open('...utils.py').read(); assert 'connectoin' not in content" > .sisyphus/evidence/task-4-RED.txt 2>&1
# → AssertionError (오탈자 존재 = 테스트 실패 = RED)

# 코드 수정: "connectoin" → "connection"

# GREEN: 수정 후 — 오탈자 제거 확인
python3 -c "content=open('...utils.py').read(); assert 'connectoin' not in content; print('OK')" > .sisyphus/evidence/task-4-utils-fixes.txt 2>&1
# → "OK" (테스트 통과 = GREEN)
```

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

**Evidence 파일 생성 규칙 (MANDATORY — ALL TASKS)**:
- Task 0에서 `mkdir -p .sisyphus/evidence` 실행 (디렉토리 생성)
- **모든** QA 시나리오의 **모든** 명령은 반드시 `> .sisyphus/evidence/task-{N}-{slug}.txt 2>&1` 리다이렉션을 **포함**해야 함
- 아래 개별 Task QA 시나리오에 리다이렉션이 표기되지 않은 경우에도, 실행 시 반드시 해당 Evidence 경로로 리다이렉션 적용
- QA 스크립트 내 `print('OK')` 호출 결과가 evidence 파일에 기록되어야 함
- Final Verification Wave에서 evidence 파일 존재 여부를 확인
- backtick으로 감싼 명령(`` `cmd` ``)은 실제 실행 시 리터럴 명령으로 해석하고 evidence 파일로 리다이렉션

**QA 도구별 사용법**:
- **Config/JSON**: Use Bash (python3 -c) — Parse JSON, assert field values
- **Python Code**: Use Bash (py_compile) — Syntax validation, content assertions
- **Markdown**: Use Bash (grep/python) — Format verification

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (Sequential — MUST be first):
└── Task 0: Rebase PR onto current main [quick]

Wave 1 (After Wave 0 — metadata fixes, 2 parallel):
├── Task 1: plugin.json author + contributor (depends: 0) [quick]
└── Task 2: marketplace.json author + version 2.4.0 (depends: 0) [quick]

Wave 2 (After Wave 1 — bug fixes, 5 parallel):
├── Task 3: _sse.py hardcoded URL fix (depends: 0) [quick]
├── Task 4: api/utils.py Exception + typo + json roundtrip (depends: 0) [quick]
├── Task 5: _sse.py request._send fix (depends: 0) [quick]
├── Task 6: Logging normalization — 3 files (depends: 0) [quick]
└── Task 7: _core.py AttributeError narrowing (depends: 0) [quick]

Wave 3 (After Wave 2 — refactor + enhancements, 3 parallel):
├── Task 8: _base.py hook + rate limit + batch_export refactor (depends: 0) [unspecified-high]
├── Task 9: pyproject.toml deps + patent_sim.py 제거 (depends: 0) [quick]
└── Task 10: result_deduplicator MD parsing 개선 (depends: 0) [quick]

Wave 4 (After Wave 3 — docs, 2 parallel):
├── Task 11: analyze-patents.md command format alignment (depends: 0) [quick]
└── Task 12: AGENTS.md + README.md update (depends: 1,2) [quick]

Wave 5 (After Wave 4 — commits + verification):
├── Task 13: 5 atomic commits 생성 [quick]
└── Task 14: Final verification [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 0 → Task 1-2 → Task 3-7 → Task 8-10 → Task 11-12 → Task 13 → Task 14 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 0 | — | 1-12 |
| 1 | 0 | 12, 13 |
| 2 | 0 | 12, 13 |
| 3-7 | 0 | 13 |
| 8-10 | 0 | 13 |
| 11 | 0 | 13 |
| 12 | 1, 2 | 13 |
| 13 | 1-12 | 14 |
| 14 | 13 | F1-F4 |

### Agent Dispatch Summary

- **Wave 0**: 1 task → `quick` (git rebase)
- **Wave 1**: 2 tasks → `quick` (JSON 편집)
- **Wave 2**: 5 tasks → `quick` (Python 코드 수정)
- **Wave 3**: 3 tasks → `unspecified-high` (1), `quick` (2)
- **Wave 4**: 2 tasks → `quick` (Markdown 편집)
- **Wave 5**: 2 tasks → `quick` (1), `deep` (1)
- **FINAL**: 4 tasks → `oracle` (1), `unspecified-high` (2), `deep` (1)

---

## TODOs

- [x] 0. PR #2 브랜치 체크아웃 및 Rebase

  **What to do**:
  - `gh pr checkout 2`로 PR 브랜치를 로컬에 체크아웃 (실패 시 폴백: `git fetch origin pull/2/head:pr-2 && git checkout pr-2`)
  - **HARD STOP**: 체크아웃 후 `plugins/patent-trend-analyzer/` 디렉토리 존재 확인. 없으면 즉시 중단하고 사용자에게 보고.
  - `git rebase main`으로 현재 main(2.3.0) 위에 리베이스
  - 충돌 발생 시 해결: marketplace.json은 main 버전 유지 + PR의 patent-trend-analyzer 항목 추가, AGENTS.md는 main 버전 유지 + PR의 patent-trend-analyzer 섹션 추가
  - `git rebase --continue`로 리베이스 완료
  - `git status`로 clean 상태 확인

  **Must NOT do**:
  - `--force` push 없이 rebase만 수행
  - main 브랜치의 기존 내용 손상 금지
  - 다른 플러그인 설정 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`git-master`]
    - `git-master`: 리베이스, 충돌 해결에 특화

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 0 (Sequential, must be first)
  - **Blocks**: Tasks 1-12
  - **Blocked By**: None

  **References**:
  - **Pattern References**: 없음 (git 작업)
  - **Conflict Files**: `.claude-plugin/marketplace.json` — main이 12개 플러그인, PR이 12개(다른 구성). 정확한 병합 필요.
  - **Conflict Files**: `AGENTS.md` — main이 v2.8.0, PR이 v2.8.0 이전 버전 기반. main 유지 + PR의 patent-trend-analyzer 섹션만 추가.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Rebase 성공 + 파일 존재 확인
    Tool: Bash
    Preconditions: PR #2 체크아웃 완료
    Steps:
      1. mkdir -p .sisyphus/evidence
      2. git status > .sisyphus/evidence/task-0-rebase-status.txt 2>&1
      3. 출력에 "nothing to commit, working tree clean" 포함 확인
      4. git log --oneline -3 >> .sisyphus/evidence/task-0-rebase-status.txt
      5. 핵심 파일 존재 확인:
         python3 -c "
         import os, sys
         paths = [
             'plugins/patent-trend-analyzer/.claude-plugin/plugin.json',
             'plugins/patent-trend-analyzer/agents/patent-planner.md',
             'plugins/patent-trend-analyzer/commands/analyze-patents.md',
             'plugins/patent-trend-analyzer/skills/patent-mcp-setup/SKILL.md',
             'plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py',
             'plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/api/utils.py',
             'plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/_base.py',
         ]
         missing = [p for p in paths if not os.path.exists(p)]
         if missing:
             print(f'MISSING: {missing}', file=sys.stderr)
             sys.exit(1)
         print(f'All {len(paths)} critical files exist')
         " >> .sisyphus/evidence/task-0-rebase-status.txt 2>&1
    Expected Result: clean working tree, PR 커밋이 main 최신 위에, 모든 핵심 파일 존재
    Failure Indicators: "CONFLICT", "rebase in progress", "MISSING"
    Evidence: .sisyphus/evidence/task-0-rebase-status.txt

  Scenario: marketplace.json JSON 파싱 유효성
    Tool: Bash
    Preconditions: Rebase 완료
    Steps:
      1. python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print(f'Parsed OK, {len(d[\"plugins\"])} plugins')" > .sisyphus/evidence/task-0-marketplace-valid.txt 2>&1
      2. JSON 파싱 성공 확인 (플러그인 수는 Task 2에서 검증)
    Expected Result: "Parsed OK, N plugins" (N은 rebase 시점의 값)
    Failure Indicators: JSONDecodeError
    Evidence: .sisyphus/evidence/task-0-marketplace-valid.txt
  ```

  **Commit**: NO (rebase 자체가 커밋 재적용)

- [x] 1. plugin.json author 정책 수정 + contributor 추가

  **What to do**:
  - `plugins/patent-trend-analyzer/.claude-plugin/plugin.json` 수정:
    - `author.name`: `"Gunju Park"` → `"Baekdong Cha"`
    - `author.email`: `"uio88890@gmail.com"` → `"orientpine@gmail.com"`
    - `contributors` 배열 추가: `[{"name": "Gunju Park", "email": "uio88890@gmail.com"}]`

  **Must NOT do**:
  - version, description, name, license 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 12, 13
  - **Blocked By**: Task 0

  **References**:
  - **Pattern References**: `plugins/isd-generator/.claude-plugin/plugin.json` — 기존 plugin.json 형식 참조 (author.email = orientpine@gmail.com)
  - **Target File**: `plugins/patent-trend-analyzer/.claude-plugin/plugin.json` — 현재 10줄, 전체 수정 필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: plugin.json 필드 검증
    Tool: Bash
    Preconditions: Task 0 완료
    Steps:
      1. python3 -c "import json; d=json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json')); assert d['author']['email']=='orientpine@gmail.com', f'Wrong: {d[\"author\"][\"email\"]}'; assert d['author']['name']=='Baekdong Cha'; assert 'contributors' in d; assert d['contributors'][0]['name']=='Gunju Park'; assert d['contributors'][0]['email']=='uio88890@gmail.com'; print('OK')" > .sisyphus/evidence/task-1-plugin-json.txt 2>&1
    Expected Result: "OK" 출력
    Failure Indicators: AssertionError, KeyError, JSONDecodeError
    Evidence: .sisyphus/evidence/task-1-plugin-json.txt
  ```

  **Commit**: YES (groups with Task 2 → C1)
  - Message: `fix(patent-trend-analyzer): update author policy and marketplace version`
  - Files: `plugins/patent-trend-analyzer/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  - Pre-commit: `python3 -c "import json; json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json')); print('Valid')"`

- [x] 2. marketplace.json author 수정 + version 2.4.0

  **What to do**:
  - `.claude-plugin/marketplace.json` 수정:
    - `metadata.version`: 현재 값 → `"2.4.0"` (새 플러그인 추가 = MINOR bump)
    - patent-trend-analyzer 항목의 `author.email` → `"orientpine@gmail.com"`
    - patent-trend-analyzer 항목의 `author.name` → `"Baekdong Cha"`
    - `contributors` 배열 추가: `[{"name": "Gunju Park", "email": "uio88890@gmail.com"}]`

  **Must NOT do**:
  - 다른 플러그인 항목 수정 금지
  - patent-trend-analyzer 항목의 agents, skills, description 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 12, 13
  - **Blocked By**: Task 0

  **References**:
  - **Pattern References**: `.claude-plugin/marketplace.json` 내 다른 플러그인 항목 형식 참조
  - **AGENTS.md 규칙**: 새 플러그인 추가 시 marketplace MINOR 버전 올림

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: marketplace.json 버전 및 author 검증
    Tool: Bash
    Preconditions: Task 0 완료
    Steps:
      1. python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); assert d['metadata']['version']=='2.4.0', f'Wrong version: {d[\"metadata\"][\"version\"]}'; pt=[p for p in d['plugins'] if p['name']=='patent-trend-analyzer'][0]; assert pt['author']['email']=='orientpine@gmail.com'; assert 'contributors' in pt; print('OK')" > .sisyphus/evidence/task-2-marketplace-json.txt 2>&1
    Expected Result: "OK" 출력
    Failure Indicators: AssertionError, KeyError
    Evidence: .sisyphus/evidence/task-2-marketplace-json.txt

  Scenario: 13개 플러그인 + 무변경 확인
    Tool: Bash
    Preconditions: marketplace.json 수정 완료
    Steps:
      1. python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in d['plugins']]; assert 'isd-generator' in names; assert 'visual-generator' in names; assert 'patent-trend-analyzer' in names; assert len(d['plugins'])==13, f'Expected 13, got {len(d[\"plugins\"])}'; print(f'{len(d[\"plugins\"])} plugins OK')" > .sisyphus/evidence/task-2-marketplace-integrity.txt 2>&1
    Expected Result: "13 plugins OK"
    Failure Indicators: 플러그인 수 변경, 기존 플러그인 누락
    Evidence: .sisyphus/evidence/task-2-marketplace-integrity.txt
  ```

  **Commit**: YES (groups with Task 1 → C1)

- [x] 3. _sse.py 하드코딩 URL 수정

  **What to do**:
  - `server/_sse.py:80-98` 의 `well_known_mcp` 함수 수정
  - 하드코딩된 `"https://psm.greennuri.info/sse"`, `"https://psm.greennuri.info/messages"` 제거
  - `request.base_url`에서 동적으로 URL 생성하도록 변경:
    ```python
    async def well_known_mcp(request):
        base = str(request.base_url).rstrip("/")
        body = json.dumps({
            "mcpVersion": "2024-01-01",
            "capabilities": ["sse"],
            "sse": {
                "url": f"{base}/sse",
                "message_url": f"{base}/messages",
            },
        })
        # ... 나머지 동일
    ```

  **Must NOT do**:
  - `.well-known/mcp` 엔드포인트 자체 제거 금지
  - SSE 트랜스포트 로직 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5, 6, 7)
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target File**: `plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py:80-98`
  - **Starlette docs**: `request.base_url` — Starlette Request 객체의 공식 속성

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 하드코딩 URL 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py').read(); assert 'psm.greennuri.info' not in content, 'Hardcoded URL present'; assert 'request.base_url' in content or 'base_url' in content, 'Dynamic URL not implemented'; print('OK')" > .sisyphus/evidence/task-3-hardcoded-url.txt 2>&1
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-3-hardcoded-url.txt
  ```

  **Commit**: YES (groups with Tasks 4, 5 → C2)

- [x] 4. api/utils.py Exception 버그 + 오탈자 + JSON 라운드트립 수정

  **What to do**:
  - **Exception 버그** (라인 81): `raise Exception("... [%s] ... [%s]", url, response_text[0:100])` → `raise Exception(f"response is not xml. check query url [{mask_sensitive_data(url)}] response [{response_text[:100]}]")`
  - **오탈자** (라인 91): `"connectoin Error"` → `"connection Error"`
  - **JSON 라운드트립 제거** (라인 82, 131): `json.loads(json.dumps(dict_type))` → `dict(dict_type)` 또는 직접 사용 (OrderedDict → dict 변환이 목적이라면 `dict()` 캐스팅으로 충분. 중첩 OrderedDict 대응이 필요하면 재귀 변환 함수 사용)
  - **보안**: Exception 메시지에서 URL 노출 시 `mask_sensitive_data()` 적용

  **Must NOT do**:
  - 에러 핸들링 구조(try/except 블록) 변경 금지
  - `get_response`, `get_response_async` 함수 시그니처 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target File**: `plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/api/utils.py`
  - **Line 81**: sync `get_response()` 내 Exception
  - **Line 91**: 오탈자
  - **Line 82, 131**: json.loads(json.dumps()) 패턴 — `get_response()`와 `get_response_async()` 모두

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: utils.py 3가지 수정 확인
    Tool: Bash
    Steps:
      1. python3 -c "
      content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/api/utils.py').read()
      assert 'connectoin' not in content, 'Typo still present'
      assert 'json.loads(json.dumps(' not in content, 'JSON roundtrip still present'
      lines=content.split(chr(10))
      for i,l in enumerate(lines):
          if 'raise Exception(' in l and '%s' in l:
              raise AssertionError(f'Line {i+1}: Exception uses tuple args')
      assert 'mask_sensitive_data' in content, 'Missing URL masking'
      print('OK')
      "
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-4-utils-fixes.txt

  Scenario: 구문 검증
    Tool: Bash
    Steps:
      1. python3 -c "import py_compile; py_compile.compile('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/api/utils.py', doraise=True); print('Syntax OK')"
    Expected Result: "Syntax OK"
    Evidence: .sisyphus/evidence/task-4-utils-syntax.txt
  ```

  **Commit**: YES (groups with Tasks 3, 5 → C2)

- [x] 5. _sse.py request._send 프라이빗 속성 수정

  **What to do**:
  - `server/_sse.py:103` 수정:
    - `request._send` → `request.send` (ASGI 퍼블릭 인터페이스)
    - 만약 `request.send`가 Starlette에서 지원되지 않으면, ASGI scope에서 직접 send를 추출하는 방식 사용
    - MCP SDK의 `SseServerTransport.connect_sse()` 시그니처 확인 필요: `scope, receive, send` 세 인자를 받는 ASGI 표준

  **Must NOT do**:
  - SSE 연결/해제 로직 변경 금지
  - 다른 라우트 핸들러 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target File**: `plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py:100-118`
  - **MCP SDK**: `SseServerTransport.connect_sse(scope, receive, send)` — ASGI 표준 3인자
  - **Starlette Request**: `request.scope`, `request.receive` 는 퍼블릭. `request._send`는 프라이빗이나 `send` 인자는 `handle_sse` 함수 파라미터로 받을 수 없으므로 ASGI 미들웨어 패턴 확인 필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: _send 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py').read(); assert 'request._send' not in content, '_send still present'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-5-send-fix.txt
  ```

  **Commit**: YES (groups with Tasks 3, 4 → C2)

- [x] 6. 로깅 정규화 (3개 파일 basicConfig 중복 제거 + DEBUG → INFO)

  **What to do**:
  - **`server/_core.py:19`**: `logging.basicConfig(level=logging.DEBUG)` 제거. `logger = logging.getLogger("mcp-kipris")` 만 유지. 로깅 설정은 엔트리포인트(`__main__.py` 또는 `_sse.py main()`)에서 한 번만 수행.
  - **`kipris/api/utils.py:14-18`**: `logging.basicConfig(...)` 블록 전체 제거. `logger = logging.getLogger("mcp-kipris")` 만 유지.
  - **`kipris/api/abs_class.py:16-20`**: `logging.basicConfig(...)` 블록 전체 제거. `logger = logging.getLogger("mcp-kipris")` 만 유지.
  - **엔트리포인트 설정**: `server/__main__.py` 또는 `server/_sse.py`의 `main()` 함수 시작부에 `logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")` 한 번만 설정.

  **Must NOT do**:
  - 로그 메시지 내용 변경 금지
  - logger 이름("mcp-kipris") 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target Files**:
    - `server/_core.py:19` — basicConfig(DEBUG)
    - `kipris/api/utils.py:14-18` — basicConfig(INFO)
    - `kipris/api/abs_class.py:16-20` — basicConfig(INFO)
    - `server/__main__.py` 또는 `server/_sse.py:173` — main() 엔트리포인트

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: basicConfig 중복 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "
      import glob
      count=0
      for f in glob.glob('plugins/patent-trend-analyzer/**/*.py', recursive=True):
          c=open(f).read()
          count+=c.count('basicConfig')
      assert count<=1, f'basicConfig found {count} times (expected <=1)'
      print(f'basicConfig count: {count} OK')
      "
    Expected Result: "basicConfig count: 1 OK" (엔트리포인트에만 1개)
    Evidence: .sisyphus/evidence/task-6-logging.txt

  Scenario: DEBUG 레벨 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "
      import glob
      for f in glob.glob('plugins/patent-trend-analyzer/**/*.py', recursive=True):
          if 'basicConfig' in open(f).read() and 'DEBUG' in open(f).read():
              raise AssertionError(f'{f}: DEBUG level in basicConfig')
      print('No DEBUG basicConfig OK')
      "
    Expected Result: "No DEBUG basicConfig OK"
    Evidence: .sisyphus/evidence/task-6-no-debug.txt
  ```

  **Commit**: YES (groups with Task 7 → C3)

- [x] 7. _core.py AttributeError 과도 캐치 축소

  **What to do**:
  - `server/_core.py:57` 수정:
    ```python
    # Before
    except (AttributeError, NotImplementedError) as e:
    
    # After
    except NotImplementedError as e:
    ```
  - `AttributeError`를 제거하여 실제 버그가 삼켜지지 않도록 함. `NotImplementedError`만 캐치하면 `_execute_async` 미구현 시에만 sync 폴백.

  **Must NOT do**:
  - sync/async 폴백 로직 자체 제거 금지
  - 에러 핸들링 메시지 변경 금지 (이유 설명만 수정 가능)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target File**: `server/_core.py:54-59`

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: AttributeError 캐치 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_core.py').read(); assert 'AttributeError' not in content, 'AttributeError still caught'; assert 'NotImplementedError' in content, 'NotImplementedError must remain'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-7-attributeerror.txt
  ```

  **Commit**: YES (groups with Task 6 → C3)

- [x] 8. BaseBatchExportTool 훅 패턴 + 레이트 리밋 + ForeignBatchExport 리팩터

  **What to do**:
  - **`_base.py`에 post-processing 훅 추가**:
    ```python
    def _post_process(self, df: pd.DataFrame, validated_args) -> pd.DataFrame:
        """Override for post-processing (e.g., IPC filter). Default: no-op."""
        return df
    ```
    `_execute_async` 내에서 dedup 후, trim 전에 `df = self._post_process(df, validated_args)` 호출.

  - **`_base.py`에 레이트 리밋 추가**:
    `_execute_async`의 페이지 순회 루프에 `await asyncio.sleep(0.5)` 추가 (KIPRIS API 보호).
    `import asyncio` 추가.

  - **`foreign/batch_export_tool.py` 리팩터**:
    `_execute_async` 메서드(105-202줄) 전체를 삭제하고, `_post_process` 오버라이드로 IPC 필터 로직만 구현:
    ```python
    def _post_process(self, df, validated_args):
        if validated_args.ipc_filter and "ipc" in df.columns:
            ipc_pattern = validated_args.ipc_filter.upper()
            before = len(df)
            df = df[df["ipc"].fillna("").str.upper().str.contains(ipc_pattern, regex=False)]
            logger.info(f"[{self.name}] IPC filter '{validated_args.ipc_filter}': {before} -> {len(df)}")
            if df.empty:
                return df  # 빈 결과 처리는 부모 클래스에서
        return df
    ```
    `_generate_filepath` 오버라이드로 IPC suffix 로직 유지.

  **Must NOT do**:
  - KoreanBatchExport, IpcBatchExport 등 다른 서브클래스 변경 금지
  - 도구 이름, 등록, inputSchema 변경 금지
  - 기존 IPC 필터 동작의 의미론적 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
    - 리팩터링은 동작 보존이 중요하므로 신중한 접근 필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 10)
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target Files**:
    - `kipris/tools/_base.py:52-106` — BaseBatchExportTool._execute_async (수정 대상)
    - `kipris/tools/foreign/batch_export_tool.py:105-202` — 중복 코드 (삭제 대상)
  - **Pattern Reference**: `kipris/tools/korean/patent_batch_export_tool.py` — 정상적으로 부모 클래스를 사용하는 구현. 이 패턴을 따라야 함.
  - **동작 보존 확인**: IPC 필터가 적용된 경우 결과 메시지에 "IPC 필터" 정보 포함, filepath에 IPC suffix 포함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 중복 코드 제거 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/foreign/batch_export_tool.py').read(); assert 'consecutive_empty' not in content, 'Pagination loop still duplicated'; assert '_post_process' in content or 'super()' in content, 'Hook pattern not applied'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-8-dedup.txt

  Scenario: _base.py 훅 + 레이트 리밋 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/_base.py').read(); assert '_post_process' in content, 'Hook method missing'; assert 'asyncio.sleep' in content or 'sleep' in content, 'Rate limiting missing'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-8-base-hook.txt

  Scenario: 구문 검증
    Tool: Bash
    Steps:
      1. python3 -c "import py_compile; py_compile.compile('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/_base.py', doraise=True); py_compile.compile('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/foreign/batch_export_tool.py', doraise=True); print('Syntax OK')"
    Expected Result: "Syntax OK"
    Evidence: .sisyphus/evidence/task-8-syntax.txt
  ```

  **Commit**: YES (groups with Tasks 9, 10 → C4)

- [x] 9. pyproject.toml 의존성 정리 + patent_sim.py 제거

  **What to do**:
  - **patent_sim.py 삭제**: `utils/patent_sim.py` 파일 삭제 (293줄 데드코드, 내부 Ollama URL 하드코딩, 미등록 도구)
  - **pyproject.toml 의존성 제거**:
    - `scikit-learn>=1.6.1` 삭제 (patent_sim.py 전용)
    - `networkx>=3.4.2` 삭제 (patent_sim.py 전용)
    - `fastapi>=0.115.14` 삭제 (코드에서 미사용, starlette 직접 사용. mcp[cli]가 starlette 포함)
  - **utils/__init__.py 확인**: patent_sim 관련 import가 있으면 제거

  **Must NOT do**:
  - 실제 사용 중인 의존성 제거 금지 (mcp, requests, pandas, openpyxl 등)
  - patent_sim.py 외 다른 utils/ 파일 삭제 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 10)
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target Files**:
    - `skills/patent-mcp-setup/scripts/pyproject.toml:12-24` — dependencies 섹션
    - `skills/patent-mcp-setup/scripts/src/mcp_kipris/utils/patent_sim.py` — 삭제 대상
  - **의존성 확인**: `kipris/_registry.py:22-41` — _TOOL_MODULES 목록에 patent_sim 미포함 확인
  - **import 확인**: 전체 코드베이스에서 `patent_sim` import 없음 확인 필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: patent_sim.py 삭제 확인
    Tool: Bash
    Steps:
      1. python3 -c "import os; assert not os.path.exists('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/utils/patent_sim.py'), 'File still exists'; print('Deleted OK')"
    Expected Result: "Deleted OK"
    Evidence: .sisyphus/evidence/task-9-deleted.txt

  Scenario: pyproject.toml 의존성 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/pyproject.toml').read(); assert 'scikit-learn' not in content, 'scikit-learn still present'; assert 'networkx' not in content, 'networkx still present'; assert 'fastapi' not in content, 'fastapi still present'; assert 'pandas' in content, 'pandas missing'; assert 'mcp' in content, 'mcp missing'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-9-deps.txt

  Scenario: patent_sim import 없음 확인
    Tool: Bash
    Steps:
      1. python3 -c "import glob; files=glob.glob('plugins/patent-trend-analyzer/**/*.py',recursive=True); found=[f for f in files if 'patent_sim' in open(f).read()]; assert not found, f'patent_sim imported in: {found}'; print('No imports OK')"
    Expected Result: "No imports OK"
    Evidence: .sisyphus/evidence/task-9-no-imports.txt
  ```

  **Commit**: YES (groups with Tasks 8, 10 → C4)

- [x] 10. result_deduplicator Markdown 테이블 파싱 개선

  **What to do**:
  - `preprocessing/result_deduplicator_tool.py:154-160` 의 .md 파일 읽기 로직 개선:
    ```python
    # Before (취약)
    df = pd.read_csv(filepath, sep="|", skipinitialspace=True)
    df = df.dropna(how="all", axis=1)
    if len(df) > 0 and df.iloc[0].astype(str).str.contains("---").any():
        df = df.iloc[1:]
    
    # After (강건)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Markdown 테이블 행만 추출 (| 시작, --- 구분선 제외)
    table_lines = [l.strip() for l in lines if l.strip().startswith('|') and not set(l.strip().strip('|').strip()).issubset({'-', ' ', '|'})]
    if len(table_lines) >= 2:
        headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
        rows = [[c.strip() for c in row.split('|')[1:-1]] for row in table_lines[1:]]
        df = pd.DataFrame(rows, columns=headers)
    else:
        df = pd.DataFrame()
    ```

  **Must NOT do**:
  - Excel 파일 읽기 로직 변경 금지
  - 디듀플리케이션 로직 자체 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 9)
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Target File**: `preprocessing/result_deduplicator_tool.py:149-161`

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: MD 파싱 코드 개선 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/tools/preprocessing/result_deduplicator_tool.py').read(); assert 'pd.read_csv(filepath, sep=\"|\"' not in content, 'Old fragile parsing still present'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-10-md-parse.txt
  ```

  **Commit**: YES (groups with Tasks 8, 9 → C4)

- [x] 11. analyze-patents.md 커맨드 포맷 정렬

  **What to do**:
  - `commands/analyze-patents.md`를 기존 커맨드 포맷(isd-generate.md, visual-generate.md)과 일치시킴
  - **추가할 구조**:
    - `$ARGUMENTS` 플레이스홀더 추가
    - `## Input Schema` 표 추가 (연구 주제, 대상 국가, 분석 기간 등 파라미터)
    - `## Workflow` 섹션을 ASCII 트리 구조로 변환 (`+--` 인덴트 사용)
    - 각 Phase에서 `Task(subagent_type=...)` 호출 형식 통일
  - 기존 내용의 의미는 100% 유지하되, 형식만 변경

  **Must NOT do**:
  - Phase 순서(Planning → Search → Analysis) 변경 금지
  - 에이전트 호출 관계 변경 금지
  - 새 Phase 추가 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Task 12)
  - **Blocks**: Task 13
  - **Blocked By**: Task 0

  **References**:
  - **Pattern Reference**: `plugins/isd-generator/commands/isd-generate.md` — 표준 커맨드 형식 (Input Schema + ASCII 트리 Workflow)
  - **Pattern Reference**: `plugins/visual-generator/commands/visual-generate.md` — 표준 커맨드 형식
  - **Target File**: `plugins/patent-trend-analyzer/commands/analyze-patents.md` — 현재 98줄

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 커맨드 포맷 검증
    Tool: Bash
    Steps:
      1. python3 -c "content=open('plugins/patent-trend-analyzer/commands/analyze-patents.md').read(); assert '## Workflow' in content or '## Input Schema' in content, 'Missing standard sections'; assert 'Task(' in content, 'Missing Task invocations'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-11-command-format.txt
  ```

  **Commit**: YES → C5
  - Message: `style(patent-trend-analyzer): align command format with project conventions`
  - Files: `plugins/patent-trend-analyzer/commands/analyze-patents.md`

- [x] 12. AGENTS.md + README.md 업데이트

  **What to do**:
  - **AGENTS.md**:
    - `Generated` 날짜 → `2026-03-16`
    - `STRUCTURE` 섹션에 patent-trend-analyzer 트리 추가
    - `WHERE TO LOOK` 표에 특허 분석 관련 행 추가
    - `COMMANDS` 섹션에 MCP 서버 실행 명령 추가
    - 플러그인 수 12 → 13 반영 (해당 설명 업데이트)
  - **README.md**:
    - `주요 기능` 표에 patent-trend-analyzer 행 추가
    - `프로젝트 구조` 트리에 patent-trend-analyzer 추가
    - `플러그인 상세` 섹션에 patent-trend-analyzer 설명 추가
    - `변경 이력` 표에 새 항목 추가
    - 마켓플레이스 플러그인 수 업데이트

  **Must NOT do**:
  - 기존 플러그인 설명 변경 금지
  - AGENTS.md의 기존 규칙/컨벤션 섹션 변경 금지
  - README.md의 기존 설치/사용법 섹션 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Task 11)
  - **Blocks**: Task 13
  - **Blocked By**: Tasks 1, 2 (version/author 정보 필요)

  **References**:
  - **Target Files**: `AGENTS.md`, `README.md`
  - **기존 플러그인 문서화 패턴**: AGENTS.md의 기존 plugin 트리 구조 형식 참조
  - **Version Info**: marketplace 2.4.0, plugin 1.1.0

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: AGENTS.md patent-trend-analyzer 포함 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('AGENTS.md').read(); assert 'patent-trend-analyzer' in content, 'Missing in AGENTS.md'; assert '2026-03-16' in content or '2026-03' in content, 'Date not updated'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-12-agents-md.txt

  Scenario: README.md patent-trend-analyzer 포함 확인
    Tool: Bash
    Steps:
      1. python3 -c "content=open('README.md').read(); assert 'patent-trend-analyzer' in content, 'Missing in README.md'; print('OK')"
    Expected Result: "OK"
    Evidence: .sisyphus/evidence/task-12-readme-md.txt
  ```

  **Commit**: YES (포함: C5 또는 별도 C6)
  - Message: `docs: add patent-trend-analyzer to AGENTS.md and README.md`
  - Files: `AGENTS.md`, `README.md`

- [x] 13. 5개 원자적 커밋 생성

  **What to do**:
  - Tasks 1-12의 변경사항을 5개 원자적 커밋(C1-C5)으로 묶어 커밋
  - Task 12(AGENTS.md, README.md)는 C5에 포함하거나 별도 C6으로
  - 각 커밋 전 해당 파일의 QA 통과 확인
  - 커밋 메시지:
    - C1: `fix(patent-trend-analyzer): update author policy and marketplace version`
    - C2: `fix(patent-trend-analyzer): fix hardcoded URL, Exception bug, typo, _send, json roundtrip`
    - C3: `fix(patent-trend-analyzer): normalize logging config and narrow async fallback`
    - C4: `refactor(patent-trend-analyzer): deduplicate batch export, prune deps, rate limit, improve md parsing`
    - C5: `style(patent-trend-analyzer): align command format with project conventions`
    - C6: `docs: add patent-trend-analyzer to AGENTS.md and README.md`

  **Must NOT do**:
  - `--force` push 금지
  - `--amend` 금지 (각 커밋은 독립)
  - 커밋에 미관련 파일 포함 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5 (Sequential)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1-12

  **References**:
  - **Commit Strategy 섹션** 참조

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 커밋 히스토리 확인
    Tool: Bash
    Steps:
      1. git log --oneline -8 > .sisyphus/evidence/task-13-commits.txt 2>&1
      2. python3 -c "
      content=open('.sisyphus/evidence/task-13-commits.txt').read()
      assert 'fix(patent-trend-analyzer)' in content, 'Missing fix commits'
      assert 'refactor(patent-trend-analyzer)' in content, 'Missing refactor commit'
      print('Commit history OK')
      " >> .sisyphus/evidence/task-13-commits.txt 2>&1
    Expected Result: evidence 파일에 C1-C6 커밋 메시지 + "Commit history OK"
    Evidence: .sisyphus/evidence/task-13-commits.txt
  ```

  **Commit**: 이 Task 자체가 커밋 수행

- [x] 14. 최종 통합 검증

  **What to do**:
  - 모든 Python 파일 구문 검증: `py_compile`
  - 모든 JSON 파일 유효성 검증: `json.load()`
  - 정책 검증: author.email, version 일치
  - 데드코드 제거 검증: patent_sim.py 부재
  - 충돌 없음 검증: clean working tree
  - `git diff main --stat`으로 전체 변경 범위 확인

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5 (after Task 13)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 13

  **References**:
  - **Success Criteria 섹션** 참조

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 전체 Python 구문 검증
    Tool: Bash
    Steps:
      1. python3 -c "import py_compile,glob; files=glob.glob('plugins/patent-trend-analyzer/**/*.py',recursive=True); [py_compile.compile(f,doraise=True) for f in files]; print(f'{len(files)} files OK')" > .sisyphus/evidence/task-14-syntax.txt 2>&1
    Expected Result: "N files OK" (N = 전체 .py 파일 수)
    Evidence: .sisyphus/evidence/task-14-syntax.txt

  Scenario: 전체 JSON 유효성 검증
    Tool: Bash
    Steps:
      1. python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json')); print('JSON OK')" > .sisyphus/evidence/task-14-json.txt 2>&1
    Expected Result: "JSON OK"
    Evidence: .sisyphus/evidence/task-14-json.txt

  Scenario: 정책 종합 검증
    Tool: Bash
    Steps:
      1. python3 -c "
      import json,os
      p=json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json'))
      m=json.load(open('.claude-plugin/marketplace.json'))
      assert p['author']['email']=='orientpine@gmail.com'
      assert m['metadata']['version']=='2.4.0'
      assert not os.path.exists('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/utils/patent_sim.py')
      pt=[x for x in m['plugins'] if x['name']=='patent-trend-analyzer'][0]
      assert pt['version']==p['version']
      print('ALL CHECKS PASSED')
      " > .sisyphus/evidence/task-14-policy.txt 2>&1
    Expected Result: "ALL CHECKS PASSED"
    Evidence: .sisyphus/evidence/task-14-policy.txt

  Scenario: Working tree clean 확인
    Tool: Bash
    Steps:
      1. git status --porcelain > .sisyphus/evidence/task-14-clean.txt 2>&1
      2. python3 -c "content=open('.sisyphus/evidence/task-14-clean.txt').read().strip(); assert content=='', f'Working tree not clean: {content}'; print('Clean OK')" >> .sisyphus/evidence/task-14-clean.txt 2>&1
    Expected Result: evidence 파일에 "Clean OK"
    Evidence: .sisyphus/evidence/task-14-clean.txt
  ```

  **Commit**: NO (검증만)

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`

  **What to do**: 계획의 Must Have / Must NOT Have 항목 전수 검증.

  **QA Scenarios:**
  ```
  Scenario: Must Have 항목 전수 확인
    Tool: Bash
    Steps:
      1. python3 -c "
      import json, os, glob
      results = []
      # Must Have 1: author.email
      p=json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json'))
      results.append(('author.email', p['author']['email']=='orientpine@gmail.com'))
      # Must Have 2: marketplace version
      m=json.load(open('.claude-plugin/marketplace.json'))
      results.append(('marketplace.version', m['metadata']['version']=='2.4.0'))
      # Must Have 3: patent_sim.py 제거
      results.append(('patent_sim removed', not os.path.exists('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/utils/patent_sim.py')))
      # Must Have 4: AGENTS.md 업데이트
      results.append(('AGENTS.md updated', 'patent-trend-analyzer' in open('AGENTS.md').read()))
      # Must Have 5: README.md 업데이트
      results.append(('README.md updated', 'patent-trend-analyzer' in open('README.md').read()))
      # Must Have 6: 하드코딩 URL 제거
      sse=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/server/_sse.py').read()
      results.append(('hardcoded URL removed', 'psm.greennuri.info' not in sse))
      # Must Have 7: Evidence 파일 존재
      evidence=glob.glob('.sisyphus/evidence/task-*.txt')
      results.append(('evidence files', len(evidence)>=14))
      passed=sum(1 for _,v in results if v)
      total=len(results)
      for name,ok in results:
          print(f'  {\"PASS\" if ok else \"FAIL\"}: {name}')
      print(f'Must Have [{passed}/{total}] | VERDICT: {\"APPROVE\" if passed==total else \"REJECT\"}')" > .sisyphus/evidence/f1-compliance.txt 2>&1
    Expected Result: "Must Have [7/7] | VERDICT: APPROVE"
    Evidence: .sisyphus/evidence/f1-compliance.txt

  Scenario: Must NOT Have 항목 확인
    Tool: Bash
    Steps:
      1. python3 -c "
      import glob
      results = []
      # Must NOT 1: 다른 플러그인 코드 변경 없음
      # (git diff로 변경된 파일 중 patent-trend-analyzer 외 플러그인 파일 확인)
      # Must NOT 2: DEBUG 로깅 없음
      for f in glob.glob('plugins/patent-trend-analyzer/**/*.py', recursive=True):
          c=open(f).read()
          if 'basicConfig' in c and 'DEBUG' in c:
              results.append(('no DEBUG', False, f))
              break
      else:
          results.append(('no DEBUG', True, ''))
      # Must NOT 3: connectoin 오탈자 없음
      utils=open('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/kipris/api/utils.py').read()
      results.append(('no typo', 'connectoin' not in utils, ''))
      passed=sum(1 for _,v,_ in results if v)
      total=len(results)
      for name,ok,detail in results:
          print(f'  {\"PASS\" if ok else \"FAIL\"}: {name} {detail}')
      print(f'Must NOT Have [{passed}/{total}] | VERDICT: {\"APPROVE\" if passed==total else \"REJECT\"}')" >> .sisyphus/evidence/f1-compliance.txt 2>&1
    Expected Result: "APPROVE"
    Evidence: .sisyphus/evidence/f1-compliance.txt
  ```

- [x] F2. **Code Quality Review** — `unspecified-high`

  **What to do**: 전체 Python 파일 구문 + 품질 검사.

  **QA Scenarios:**
  ```
  Scenario: 구문 + 품질 검사
    Tool: Bash
    Steps:
      1. python3 -c "
      import py_compile, glob
      files=glob.glob('plugins/patent-trend-analyzer/**/*.py', recursive=True)
      syntax_ok=0; syntax_fail=0; quality_issues=[]
      for f in files:
          try:
              py_compile.compile(f, doraise=True)
              syntax_ok+=1
          except py_compile.PyCompileError as e:
              syntax_fail+=1; quality_issues.append(f'SYNTAX: {f}: {e}')
          content=open(f).read()
          if 'as any' in content: quality_issues.append(f'QUALITY: {f}: contains \"as any\"')
          if content.count('pass') > 5 and len(content) < 200: quality_issues.append(f'QUALITY: {f}: suspicious empty blocks')
      for issue in quality_issues: print(f'  {issue}')
      verdict='PASS' if syntax_fail==0 and len(quality_issues)==0 else 'FAIL'
      print(f'Syntax [{syntax_ok} pass/{syntax_fail} fail] | Quality [{len(files)-len(quality_issues)} clean/{len(quality_issues)} issues] | VERDICT: {verdict}')
      " > .sisyphus/evidence/f2-quality.txt 2>&1
    Expected Result: "VERDICT: PASS"
    Evidence: .sisyphus/evidence/f2-quality.txt
  ```

- [x] F3. **Real Manual QA** — `unspecified-high`

  **What to do**: 모든 Task의 QA evidence 파일을 재실행/확인.

  **QA Scenarios:**
  ```
  Scenario: 전체 evidence 재검증
    Tool: Bash
    Steps:
      1. python3 -c "
      import glob, os
      evidence_dir='.sisyphus/evidence'
      files=glob.glob(os.path.join(evidence_dir,'task-*.txt'))
      passed=0; failed=0; missing=0
      for f in sorted(files):
          content=open(f).read().strip()
          if 'OK' in content or 'PASSED' in content or 'Syntax OK' in content:
              passed+=1
          elif 'Error' in content or 'FAIL' in content or 'Assert' in content:
              failed+=1
              print(f'  FAIL: {os.path.basename(f)}')
          else:
              print(f'  UNKNOWN: {os.path.basename(f)}: {content[:80]}')
      # Check expected evidence count (at least 14 task evidence files)
      total=passed+failed
      print(f'Scenarios [{passed}/{total} pass] | VERDICT: {\"APPROVE\" if failed==0 and total>=14 else \"REJECT\"}')" > .sisyphus/evidence/f3-manual-qa.txt 2>&1
    Expected Result: "VERDICT: APPROVE"
    Evidence: .sisyphus/evidence/f3-manual-qa.txt
  ```

- [x] F4. **Scope Fidelity Check** — `deep`

  **What to do**: git diff로 변경 범위가 계획과 일치하는지 확인.

  **QA Scenarios:**
  ```
  Scenario: 변경 범위 확인
    Tool: Bash
    Steps:
      1. git diff main --name-only > .sisyphus/evidence/f4-scope.txt 2>&1
      2. python3 -c "
      changed=open('.sisyphus/evidence/f4-scope.txt').read().strip().split('\n')
      allowed_prefixes=['plugins/patent-trend-analyzer/', '.claude-plugin/marketplace.json', 'AGENTS.md', 'README.md', '.sisyphus/']
      violations=[f for f in changed if not any(f.startswith(p) for p in allowed_prefixes)]
      if violations:
          print(f'SCOPE VIOLATION: {violations}')
          print('VERDICT: REJECT')
      else:
          print(f'Changed {len(changed)} files, all within scope')
          print('VERDICT: APPROVE')
      " >> .sisyphus/evidence/f4-scope.txt 2>&1
    Expected Result: "VERDICT: APPROVE"
    Evidence: .sisyphus/evidence/f4-scope.txt
  ```

---

## Commit Strategy

| Commit | Issues | Message | Pre-commit Check |
|--------|--------|---------|------------------|
| C0 | — | `chore: rebase patent-trend-analyzer onto current main` | `git status` clean |
| C1 | #1, #2 | `fix(patent-trend-analyzer): update author policy and marketplace version` | `python3 -c "import json; ..."` |
| C2 | #3, #4, #5, #8, #14 | `fix(patent-trend-analyzer): fix hardcoded URL, Exception bug, typo, _send, json roundtrip` | `py_compile` all modified .py |
| C3 | #7, #10 | `fix(patent-trend-analyzer): normalize logging config and narrow async fallback` | `py_compile` + grep no DEBUG |
| C4 | #6, #9, #12, #13 | `refactor(patent-trend-analyzer): deduplicate batch export, prune deps, rate limit, improve md parsing` | `py_compile` + grep no patent_sim import |
| C5 | #11 | `style(patent-trend-analyzer): align command format with project conventions` | File exists + format check |

---

## Success Criteria

### Verification Commands
```bash
# JSON 유효성
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"
python3 -c "import json; json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json')); print('OK')"

# Python 구문 검증
python3 -c "import py_compile, glob; [py_compile.compile(f, doraise=True) for f in glob.glob('plugins/patent-trend-analyzer/**/*.py', recursive=True)]; print('All OK')"

# 정책 검증
python3 -c "import json; d=json.load(open('plugins/patent-trend-analyzer/.claude-plugin/plugin.json')); assert d['author']['email']=='orientpine@gmail.com'; print('Author OK')"

# 버전 검증
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); assert d['metadata']['version']=='2.4.0'; print('Version OK')"

# 데드코드 제거 검증
python3 -c "import os; assert not os.path.exists('plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/src/mcp_kipris/utils/patent_sim.py'); print('Dead code removed')"
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All Python files syntax-valid
- [ ] All JSON files valid
- [ ] 6 commits in correct order
- [ ] PR mergeable (no conflicts)
