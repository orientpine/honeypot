# wiki-gen v1.2.0: Multi-Source Sync (`wiki sync`)

## TL;DR

> **Quick Summary**: wiki-gen 플러그인에 `wiki sync` 서브커맨드를 추가하여 `sources.yaml` 기반으로 N개 프로젝트의 `doc/` 폴더에서 문서를 자동 수집하는 멀티소스 수집 파이프라인 구현.
>
> **Deliverables**:
> - `sync_sources.py` — 다중 소스 오케스트레이터 (~400줄)
> - `ingest_projects.py` — 프로젝트 doc/ 전용 ingest 헬퍼 (~350줄)
> - `ingest_common.py` — 공통 함수 모듈 (~250줄)
> - pytest 인프라 + 자동화 테스트 3개 파일
> - `sources-schema.md`, `automation-guide.md`, `absorb_delta_agent.md`(stub)
> - SKILL.md `wiki sync` 섹션 추가 (~120줄)
> - plugin.json v1.2.0 + AGENTS.md + README.md + marketplace.json 업데이트
>
> **Estimated Effort**: Medium (1.5-2일)
> **Parallel Execution**: YES — 5 waves
> **Critical Path**: Task 2 → Task 8 → Task 10 → Task 12 → Task 14 → F1-F4

---

## Context

### Original Request
`.sisyphus/plans/multi-source-sync-impl.md` (840줄 상세 구현 스펙)을 기반으로 Sisyphus 실행 가능한 작업 계획 생성.

### Interview Summary
**Key Discussions**:
- **테스트 전략**: pytest 인프라 설정 + 자동화 테스트 (기존 테스트 인프라 없음)
- **Step 7 (cha_wiki 적용)**: 제외 — 플러그인 코드만 구현
- **U1**: `ingest_common.py` 별도 모듈 추출 (DRY)
- **U2**: `sources.yaml`에 obsidian 옵션 직접 기입
- **U3**: 부분 성공 = exit 0 + warning
- **U4**: 별도 `sync_log.json` 파일

**Research Findings**:
- Entry dataclass: `ingest_obsidian.py:76-97` (18 fields, `source_type` + `extra` dict 포함)
- SHA1 ID: line 504 `sha1(rel_str)[:12]`
- `scripts/__init__.py` 이미 존재 (package marker)
- 기존 9 서브커맨드, 11 스크립트, 6 references, 4 agent templates
- 모든 기존 스크립트는 rglob/파라미터화 — `raw/entries/{source}/` 서브디렉토리 구조와 호환

### Metis Review
**Identified Gaps** (addressed):
- **Q1 (CRITICAL)**: `ingest_log.json`의 `file` 필드 — 서브디렉토리 엔트리는 `"{source_name}/{base_name}"` 형식 필수 (`verify_content.py:148` 호환)
- **Q2**: `ingest_common.py`로 추출할 함수 목록 구체화 (12개 함수/클래스 + 2개 상수)
- **G1**: `ingest_obsidian.py` zero-diff 보장 — gold-output 비교 테스트 필수
- **G3**: import 방향 단방향 강제 — `ingest_obsidian.py → ingest_common.py ← ingest_projects.py`
- **G4**: `sources.yaml` `name` 필드 검증 — `^[a-z0-9][a-z0-9_-]*$`, 중복 불가
- **E1**: symlink 무한 루프 방지 — `follow_symlinks=False`
- **R3**: `pytest.ini` testpaths에 wiki-gen 테스트 경로 추가 필요

---

## Work Objectives

### Core Objective
`sources.yaml` 설정 기반으로 여러 프로젝트의 `doc/` 폴더에서 문서를 `raw/entries/{source_name}/`로 자동 수집하는 `wiki sync` 서브커맨드 구현 (Phase 1 MVP — LLM 흡수 제외).

### Concrete Deliverables
- `plugins/wiki-gen/skills/wiki-gen/scripts/ingest_common.py` — 공통 함수 모듈
- `plugins/wiki-gen/skills/wiki-gen/scripts/ingest_projects.py` — 프로젝트 doc/ ingest 헬퍼
- `plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py` — 다중 소스 오케스트레이터
- `plugins/wiki-gen/skills/wiki-gen/tests/conftest.py` — pytest 픽스처
- `plugins/wiki-gen/skills/wiki-gen/tests/test_ingest_common.py`
- `plugins/wiki-gen/skills/wiki-gen/tests/test_ingest_projects.py`
- `plugins/wiki-gen/skills/wiki-gen/tests/test_sync_sources.py`
- `plugins/wiki-gen/skills/wiki-gen/references/sources-schema.md`
- `plugins/wiki-gen/skills/wiki-gen/references/automation-guide.md`
- `plugins/wiki-gen/skills/wiki-gen/assets/absorb_delta_agent.md` (stub)
- SKILL.md `wiki sync` 섹션 추가
- scripts/README.md 업데이트
- plugin.json v1.2.0, AGENTS.md, README.md, marketplace.json 업데이트

### Definition of Done
- [ ] `python scripts/sync_sources.py --config sources.yaml --wiki-root /tmp/wiki --dry-run` → exit 0
- [ ] `python scripts/sync_sources.py --config sources.yaml --wiki-root /tmp/wiki` → 2개 local 소스에서 엔트리 생성
- [ ] `python scripts/ingest_obsidian.py --source-root /tmp/vault --wiki-root /tmp/wiki` → 추출 전후 동일 출력 (gold-diff)
- [ ] `python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ -v` → 전체 PASS
- [ ] `python scripts/rebuild_index.py --wiki-root /tmp/wiki` → exit 0 (sync 후)
- [ ] `python scripts/check_coverage.py --wiki-root /tmp/wiki` → exit 0 (sync 후)

### Must Have
- 기존 `ingest_obsidian.py` 동작 100% 보존 (import 경로만 변경)
- Source-prefixed ID로 네임스페이스 충돌 방지
- `sources.yaml` `name` 필드 유효성 검증 (ASCII, 중복 불가)
- `sync_log.json`으로 증분 추적 (content hash 기반)
- `--dry-run`, `--force`, `--source` CLI 옵션
- 삭제 감지 (소스에서 제거된 파일의 엔트리 정리)
- 멱등성 보장 (동일 sync 2회 실행 → 변경 없음)

### Must NOT Have (Guardrails)
- 기존 10개 스크립트 수정 금지 (`ingest_obsidian.py` import 라인 외)
- `classify_source()`, `parse_info_callout()`, `walk_markdown()`, `load_submodule_paths()` 추출/일반화 금지 — Obsidian 전용
- retry 라이브러리, circuit breaker, 복잡한 에러 핸들링 금지 — simple try/except + warning
- GitHub Actions `.yml` 파일 생성 금지 — `automation-guide.md` 레퍼런스 문서만
- Phase 3 absorb_delta 로직 구현 금지 — stub 파일만
- `finalize.py`, `generate_batches.py` 등 기존 스크립트에 sync 검증 통합 금지
- `ingest_common.py → ingest_obsidian.py` 방향 import 금지 (단방향만)
- `ingest_log.json` 스키마 버전 필드/포맬 마이그레이션 금지
- AI slop: 과도한 주석, 불필요한 추상화 레이어, generic 변수명

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (greenfield)
- **Automated tests**: YES (Tests-after)
- **Framework**: pytest (표준 Python 테스트 프레임워크)
- **pytest.ini**: 기존 파일에 testpaths 추가 (`plugins/wiki-gen/skills/wiki-gen/tests`)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Scripts**: Use Bash — `python plugins/wiki-gen/skills/wiki-gen/scripts/xxx.py ...`, assert exit code + output content
- **Tests**: Use Bash — `python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ -v`, assert PASS
- **Files**: Use Bash — `test -f path`, `wc -l`, `python -c "import json; ..."`
- **Regression**: Use Bash — gold-output diff comparison
- **❗ Script Path Convention**: 모든 QA 시나리오에서 `scripts/xxx.py`는 `plugins/wiki-gen/skills/wiki-gen/scripts/xxx.py`의 약어. 프로젝트 루트(현재 작업 디렉토리)에서 실행.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation + docs, 7 parallel):
├── Task 1: pytest infrastructure setup [quick]
├── Task 2: ingest_common.py extraction + backward compat [deep]
├── Task 3: sources-schema.md reference doc [writing]
├── Task 4: automation-guide.md reference doc [writing]
├── Task 5: absorb_delta_agent.md stub [quick]
├── Task 6: SKILL.md wiki sync section [writing]
└── Task 7: scripts/README.md update [quick]

Wave 2 (After Wave 1 — core ingest, 2 parallel):
├── Task 8: ingest_projects.py implementation (depends: 2) [deep]
└── Task 9: test_ingest_common.py + regression tests (depends: 1, 2) [unspecified-high]

Wave 3 (After Wave 2 — orchestrator + ingest tests, 2 parallel):
├── Task 10: sync_sources.py implementation (depends: 2, 8) [deep]
└── Task 11: test_ingest_projects.py (depends: 1, 8) [unspecified-high]

Wave 4 (After Wave 3 — integration testing, 2 parallel):
├── Task 12: test_sync_sources.py + integration tests (depends: 1, 10) [unspecified-high]
└── Task 13: Pipeline compatibility verification (depends: 10) [unspecified-high]

Wave 5 (After Wave 4 — finalization, 1 task):
└── Task 14: Version/registry/docs update (depends: all) [quick]

Wave FINAL (After ALL — 4 parallel reviews, then user okay):
├── F1: Plan compliance audit (oracle)
├── F2: Code quality review (unspecified-high)
├── F3: Real manual QA (unspecified-high)
└── F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay

Critical Path: T2 → T8 → T10 → T12 → T14 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 7 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| **1** | — | 9, 11, 12 | 1 |
| **2** | — | 8, 9, 10 | 1 |
| **3** | — | — | 1 |
| **4** | — | — | 1 |
| **5** | — | — | 1 |
| **6** | — | — | 1 |
| **7** | — | — | 1 |
| **8** | 2 | 10, 11 | 2 |
| **9** | 1, 2 | — | 2 |
| **10** | 2, 8 | 12, 13 | 3 |
| **11** | 1, 8 | — | 3 |
| **12** | 1, 10 | — | 4 |
| **13** | 10 | — | 4 |
| **14** | all | — | 5 |

### Agent Dispatch Summary

| Wave | Tasks | Categories |
|------|-------|------------|
| **1** | 7 | T1 → `quick`, T2 → `deep`, T3-4 → `writing`, T5 → `quick`, T6 → `writing`, T7 → `quick` |
| **2** | 2 | T8 → `deep`, T9 → `unspecified-high` |
| **3** | 2 | T10 → `deep`, T11 → `unspecified-high` |
| **4** | 2 | T12 → `unspecified-high`, T13 → `unspecified-high` |
| **5** | 1 | T14 → `quick` |
| **FINAL** | 4 | F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep` |

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **Base spec reference**: `.sisyphus/plans/multi-source-sync-impl.md` — 모든 태스크는 이 스펙의 상세 설계를 따름.

- [x] 1. pytest 인프라 설정

  **What to do**:
  - `plugins/wiki-gen/skills/wiki-gen/tests/` 디렉토리 생성
  - `tests/conftest.py` 작성: `tmp_wiki_root`, `tmp_source_dir`, `sample_sources_yaml`, `sample_project_docs` 픽스처
  - 프로젝트 루트의 `pytest.ini` 수정: `testpaths`에 `plugins/wiki-gen/skills/wiki-gen/tests` 추가
  - `tests/__init__.py` 빈 파일 생성
  - 픽스처에서 `tmp_path` 사용 (하드코딩 경로 금지)

  **Must NOT do**:
  - 기존 hwpx-generator 테스트 설정 수정 금지
  - 네트워크 의존 테스트 작성 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단순 파일 생성 + 설정 수정. 복잡한 로직 없음.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-7)
  - **Blocks**: Tasks 9, 11, 12
  - **Blocked By**: None (can start immediately)

  **References**:
  - **Pattern**: `pytest.ini` (프로젝트 루트) — 기존 testpaths 구조 확인 후 wiki-gen 경로 추가
  - **Pattern**: `plugins/wiki-gen/skills/wiki-gen/scripts/__init__.py` — 기존 package marker 참고
  - **Spec**: `multi-source-sync-impl.md` §6 테스트 계획 — 필요한 픽스처 유형 파악

  **Acceptance Criteria**:
  - [ ] `tests/conftest.py` 파일 존재, 4개 이상 픽스처 정의
  - [ ] `pytest.ini`에 wiki-gen 테스트 경로 포함
  - [ ] `python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ --collect-only` → exit 0 (수집 성공, 테스트 0개)

  **QA Scenarios:**
  ```
  Scenario: pytest가 wiki-gen 테스트 디렉토리를 인식
    Tool: Bash
    Preconditions: pytest.ini에 testpaths 추가 완료
    Steps:
      1. python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ --collect-only
      2. exit code 확인
    Expected Result: exit 0, "no tests ran" 또는 "0 items collected"
    Evidence: .sisyphus/evidence/task-1-pytest-collect.txt

  Scenario: conftest.py 픽스처가 유효한 Python
    Tool: Bash
    Preconditions: conftest.py 작성 완료
    Steps:
      1. python -c "import ast; ast.parse(open('plugins/wiki-gen/skills/wiki-gen/tests/conftest.py').read()); print('VALID')"
    Expected Result: stdout에 "VALID" 출력
    Evidence: .sisyphus/evidence/task-1-conftest-valid.txt
  ```

  **Commit**: YES
  - Message: `test(wiki-gen): add pytest infrastructure for v1.2.0`
  - Files: `tests/conftest.py`, `tests/__init__.py`, `pytest.ini`

---

- [x] 2. ingest_common.py 공통 함수 추출 + backward compat 보장

  **What to do**:
  - `scripts/ingest_common.py` 생성 — 아래 함수/클래스/상수를 `ingest_obsidian.py`에서 추출:
    - **클래스**: `Entry` dataclass + `to_markdown()` (lines 76-126)
    - **함수**: `log()`, `parse_csv_set()`, `slugify()`, `parse_yaml_frontmatter()`, `extract_heading_title()`, `extract_tags()`, `_valid_date()`, `_extract_path_year()`, `parse_date_fields()`, `coerce_tag_list()`, `coerce_alias_list()`, `count_markdown_files()`, `format_breakdown()`
    - **상수**: `DEFAULT_SKIP_DIR_NAMES` (lines 34-61), `DATE_YYYYMMDD`, `ISO_DATETIME` (lines 69-72)
  - `ingest_obsidian.py` 수정: 추출된 함수/클래스/상수의 **정의를 제거**하고 `from ingest_common import ...`로 교체
  - **허용 범위**: 함수 정의 삭제 + import 문 추가. 나머지 로직(호출부, 조건문, main 등)은 1줄도 수정 금지
  - 결과적으로 `ingest_obsidian.py`의 **동작(입력→출력)**은 추출 전과 100% 동일해야 함
  - **Gold-output 회귀 테스트 순서 (CRITICAL)**:
    1. **FIRST**: 테스트 데이터 생성 + 현재(추출 전) `ingest_obsidian.py` 실행 → `/tmp/gold/raw/ingest_log.json` 저장
    2. **THEN**: 함수 추출 + import 교체 수행
    3. **FINALLY**: 동일 입력으로 수정된 `ingest_obsidian.py` 실행 → `/tmp/post/raw/ingest_log.json` 저장 → 비교

  **Must NOT do**:
  - `classify_source()`, `parse_info_callout()`, `walk_markdown()`, `load_submodule_paths()` 추출 금지 (Obsidian 전용)
  - `ingest_obsidian.py`의 로직/호출부 변경 금지 (함수 정의 삭제 + import 추가만 허용)
  - `ingest_common.py`에서 `ingest_obsidian.py` import 금지 (단방향: obsidian → common)
  - `walk_markdown()` 일반화/추상화 시도 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 기존 코드 리팩토링 + 회귀 방지가 핵심. 세심한 코드 분석 필요.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-7)
  - **Blocks**: Tasks 8, 9, 10
  - **Blocked By**: None (can start immediately)

  **References**:
  - **Source**: `plugins/wiki-gen/skills/wiki-gen/scripts/ingest_obsidian.py` — 전체 파일. 특히:
    - Lines 34-61: `DEFAULT_SKIP_DIR_NAMES` 상수
    - Lines 69-72: `DATE_YYYYMMDD`, `ISO_DATETIME` 정규식
    - Lines 76-126: `Entry` dataclass + `to_markdown()`
    - Lines 152-176: `log()`, `parse_csv_set()`, `slugify()`
    - Lines 179-253: YAML 파싱, heading 추출, tag 추출
    - Lines 256-373: 날짜 파싱, tag/alias 변환
    - Lines 392-397: `count_markdown_files()`
    - Line 504: SHA1 ID 생성 (추출하지 않음 — obsidian 전용)
    - Lines 555-558: `format_breakdown()`
  - **Spec**: `multi-source-sync-impl.md` §4.2 공유 코드 전략 — 추출 대상 목록, 방식 A 확정
  - **Metis Q2**: 추출할 함수 12개 + 유지할 함수 6개 구체 목록
  - **Metis G1**: Zero-diff 보장 프로토콜 — gold-output 비교 방법
  - **Metis G3**: import 방향 단방향 강제

  **Acceptance Criteria**:
  - [ ] `scripts/ingest_common.py` 존재, ~200-250줄
  - [ ] `ingest_obsidian.py`에서 추출된 함수 직접 정의 제거, `from ingest_common import ...`로 교체
  - [ ] `python scripts/ingest_obsidian.py --help` → exit 0 (기존과 동일 인터페이스)
  - [ ] Gold-output 회귀 테스트 통과 (아래 QA 시나리오)

  **QA Scenarios:**
  ```
  Scenario: Gold-output 회귀 테스트 — 추출 전후 동일 출력
    Tool: Bash
    Preconditions:
      - 구현 순서에 따라 gold baseline이 이미 캐프처됨:
        Step A (BEFORE 추출): 테스트 데이터 생성 + 현재 ingest_obsidian.py 실행 → /tmp/gold/raw/ingest_log.json
        Step B (AFTER 추출): 함수 추출 + import 교체 완료
    Steps:
      1. mkdir -p /tmp/test_vault/notes /tmp/post/wiki
      2. echo -e "---\ntitle: Note One\ntags: [test, alpha]\ndate: 2026-01-15\n---\nFirst note body" > /tmp/test_vault/notes/note1.md
      3. echo -e "---\ntitle: Note Two\ntags: [test, beta]\ndate: 2026-02-20\n---\nSecond note body" > /tmp/test_vault/notes/note2.md
      4. echo -e "---\ntitle: Note Three\ntags: [gamma]\n---\nThird note body" > /tmp/test_vault/notes/note3.md
      5. python scripts/ingest_obsidian.py --source-root /tmp/test_vault --wiki-root /tmp/post/wiki
      6. python -c "
         import json
         a = json.load(open('/tmp/gold/raw/ingest_log.json'))  # Step A에서 캐프처된 baseline
         b = json.load(open('/tmp/post/raw/ingest_log.json'))  # Step 5에서 생성된 추출 후 결과
         for log in (a, b):
           log.pop('ingested_at', None)
           for e in log.get('entries', []): e.pop('ingested_at', None)
         for ea, eb in zip(sorted(a['entries'], key=lambda x: x['id']), sorted(b['entries'], key=lambda x: x['id'])):
           assert ea['id'] == eb['id'], f'ID mismatch: {ea["id"]} vs {eb["id"]}'
           assert ea['title'] == eb['title'], f'Title mismatch for {ea["id"]}'
         print(f'PASS: {len(a["entries"])} entries matched')"
    Expected Result: stdout에 "PASS: 3 entries matched" — 추출 전후 동일한 엔트리 생성 확인
    Failure Indicators: AssertionError (추출로 인한 동작 변경), ImportError (잘못된 import)
    Evidence: .sisyphus/evidence/task-2-gold-diff.txt

  Scenario: import 방향 검증 — ingest_common이 ingest_obsidian을 import하지 않음
    Tool: Bash
    Steps:
      1. python -c "
         content = open('plugins/wiki-gen/skills/wiki-gen/scripts/ingest_common.py').read()
         assert 'from ingest_obsidian' not in content, 'FORBIDDEN: ingest_common imports from ingest_obsidian'
         assert 'import ingest_obsidian' not in content, 'FORBIDDEN: ingest_common imports ingest_obsidian'
         print('PASS: no reverse imports')"
    Expected Result: "PASS: no reverse imports"
    Evidence: .sisyphus/evidence/task-2-import-direction.txt
  ```

  **Commit**: YES
  - Message: `refactor(wiki-gen): extract shared functions to ingest_common.py`
  - Files: `scripts/ingest_common.py`, `scripts/ingest_obsidian.py`
  - Pre-commit: `python scripts/ingest_obsidian.py --help`

---

- [x] 3. sources-schema.md 레퍼런스 문서

  **What to do**:
  - `references/sources-schema.md` 생성 — `sources.yaml`의 전체 스키마 문서화
  - 각 필드의 타입, 필수 여부, 기본값, 예시 포함
  - `type: git | local | obsidian` 별 필수/선택 필드 구분
  - `settings` 블록 설명
  - `name` 필드 검증 규칙: `^[a-z0-9][a-z0-9_-]*$`, 중복 불가 (Metis G4)
  - 예제 `sources.yaml` 2-3개 소스 포함

  **Recommended Agent Profile**: `writing` | **Skills**: []
  **Parallelization**: Wave 1 | **Blocks**: 없음 | **Blocked By**: 없음

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.3 — 전체 스키마 + 예제 (lines 324-374)
  - **Spec**: §4.7 — sources-schema.md 포함 내용 (lines 521-531)

  **QA Scenarios:**
  ```
  Scenario: 문서 필수 섹션 존재 확인
    Tool: Bash
    Steps:
      1. python -c "
         content = open('plugins/wiki-gen/skills/wiki-gen/references/sources-schema.md').read()
         for section in ['type', 'name', 'settings', 'git', 'local', 'obsidian']:
           assert section in content.lower(), f'Missing section: {section}'
         print('PASS: all sections present')"
    Expected Result: "PASS: all sections present"
    Evidence: .sisyphus/evidence/task-3-schema-doc.txt
  ```
  **Commit**: NO (groups with Tasks 3-7)

---

- [x] 4. automation-guide.md 레퍼런스 문서 (Phase 2)

  **What to do**:
  - `references/automation-guide.md` 생성 — GitHub Actions + systemd timer 설정 가이드
  - 스펙 §4.8의 내용 그대로 작성 (workflow YAML, service/timer 예시, 토큰 관리)
  - 레퍼런스 문서만 — 실제 `.yml` 파일 생성 금지

  **Recommended Agent Profile**: `writing` | **Skills**: []
  **Parallelization**: Wave 1 | **Blocks**: 없음 | **Blocked By**: 없음

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.8 (lines 537-577)

  **QA Scenarios:**
  ```
  Scenario: 문서 존재 + GitHub Actions 예시 포함
    Tool: Bash
    Steps:
      1. test -f plugins/wiki-gen/skills/wiki-gen/references/automation-guide.md
      2. grep -q "github" plugins/wiki-gen/skills/wiki-gen/references/automation-guide.md
    Expected Result: 두 명령 모두 exit 0
    Evidence: .sisyphus/evidence/task-4-automation-guide.txt
  ```
  **Commit**: NO (groups with Tasks 3-7)

---

- [x] 5. absorb_delta_agent.md stub (Phase 3 placeholder)

  **What to do**:
  - `assets/absorb_delta_agent.md` 생성 — 20-30줄 stub
  - Phase 3 구현 시 사용할 에이전트 템플릿 방향성만 기술
  - 스펙 §4.6의 설계 방향 반영
  - 실제 로직 구현 금지

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 1 | **Blocks**: 없음 | **Blocked By**: 없음

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.6 (lines 508-518)
  - **Pattern**: `assets/absorb_agent.md` — 기존 에이전트 템플릿 스타일 참고

  **QA Scenarios:**
  ```
  Scenario: stub 파일 존재 + Phase 3 명시
    Tool: Bash
    Steps:
      1. wc -l < plugins/wiki-gen/skills/wiki-gen/assets/absorb_delta_agent.md
      2. grep -qi "phase 3\|placeholder\|stub" plugins/wiki-gen/skills/wiki-gen/assets/absorb_delta_agent.md
    Expected Result: 20-30줄, Phase 3/placeholder 문구 포함
    Evidence: .sisyphus/evidence/task-5-absorb-stub.txt
  ```
  **Commit**: NO (groups with Tasks 3-7)

---

- [x] 6. SKILL.md `wiki sync` 섹션 추가

  **What to do**:
  - SKILL.md의 `## Command: wiki rebuild-index` 바로 앞에 `## Command: wiki sync` 섹션 삽입 (~120줄)
  - 스펙 §4.5의 내용 그대로 사용 (Quick Start, What It Does, Incremental Sync, Automation Levels, ID Strategy, Deletion Handling, When to Run, See Also)
  - 10번째 서브커맨드로 등록

  **Recommended Agent Profile**: `writing` | **Skills**: []
  **Parallelization**: Wave 1 | **Blocks**: 없음 | **Blocked By**: 없음

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.5 (lines 412-504) — 삽입할 전체 내용
  - **Target**: `plugins/wiki-gen/skills/wiki-gen/SKILL.md` lines 197 (`## Command: wiki rebuild-index`) 앞에 삽입

  **QA Scenarios:**
  ```
  Scenario: wiki sync 섹션 존재 + 10개 서브커맨드 확인
    Tool: Bash
    Steps:
      1. grep -c "## Command:" plugins/wiki-gen/skills/wiki-gen/SKILL.md
      2. grep -q "wiki sync" plugins/wiki-gen/skills/wiki-gen/SKILL.md
    Expected Result: 10개 커맨드 섹션, "wiki sync" 포함
    Evidence: .sisyphus/evidence/task-6-skill-md.txt
  ```
  **Commit**: NO (groups with Tasks 3-7)

---

- [x] 7. scripts/README.md 업데이트

  **What to do**:
  - `scripts/README.md`에 `sync_sources.py`, `ingest_projects.py`, `ingest_common.py` 3개 항목 추가
  - 스펙 §4.9 (lines 584-600) 내용 반영
  - 기존 70줄 문서에 ~20줄 추가

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 1 | **Blocks**: 없음 | **Blocked By**: 없음

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.9 (lines 584-600)
  - **Target**: `plugins/wiki-gen/skills/wiki-gen/scripts/README.md` — 현재 70줄

  **QA Scenarios:**
  ```
  Scenario: 3개 스크립트 문서화 확인
    Tool: Bash
    Steps:
      1. grep -c "sync_sources\|ingest_projects\|ingest_common" plugins/wiki-gen/skills/wiki-gen/scripts/README.md
    Expected Result: 3 이상 (각 스크립트명 1회 이상 언급)
    Evidence: .sisyphus/evidence/task-7-readme.txt
  ```

  **Commit**: YES (Tasks 3-7 묶음)
  - Message: `docs(wiki-gen): add wiki sync documentation and SKILL.md section`
  - Files: `references/sources-schema.md`, `references/automation-guide.md`, `assets/absorb_delta_agent.md`, `SKILL.md`, `scripts/README.md`

---

- [x] 8. ingest_projects.py 구현

  **What to do**:
  - `scripts/ingest_projects.py` 생성 (~350줄) — 프로젝트 `doc/` 전용 ingest 헬퍼
  - `ingest_common.py`에서 Entry, slugify, parse_yaml_frontmatter, parse_date_fields 등 import
  - Source-prefixed ID: `sha1(f"{source_name}:{rel_path}")[:12]`
  - 자체 `walk_project_docs()` 함수 구현 (rglob('*.md') + skip_dirs, follow_symlinks=False)
  - CLI: `--source-root`, `--wiki-root`, `--source-name`, `--source-top`, `--source-category`, `--source-commit`, `--ingest-log`, `--skip-dirs`
  - 엔트리 출력: `raw/entries/{source_name}/` 서브디렉토리
  - **CRITICAL (Metis Q1)**: `ingest_log.json`의 `file` 필드를 `"{source_name}/{base_name}"` 형식으로 작성 (플랫 `base_name`만 쓰면 `verify_content.py:148`에서 파일을 찾지 못함)
  - 추가 frontmatter: `source_name`, `source_commit`, `source_url`, `aggregated_at`, `original_path`
  - 스펙 §4.2의 의사코드 + CLI + 엔트리 frontmatter 스펙 따름

  **Must NOT do**:
  - `walk_markdown()` 재사용/일반화 금지 — 자체 단순 walk 구현
  - Obsidian callout 파싱 포함 금지
  - `classify_source()` 호출 금지 — CLI args에서 직접 받음

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 신규 스크립트 350줄. ingest_common 통합 + ID 전략 + frontmatter 스펙 준수 필요.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2, with Task 9)
  - **Blocks**: Tasks 10, 11
  - **Blocked By**: Task 2 (ingest_common.py)

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.2 전체 (lines 205-320) — CLI, 차이점 표, 공유 코드, frontmatter, ID 충돌 가드
  - **Source**: `scripts/ingest_obsidian.py` lines 561-670 — `main()` 구조 참고 (argparse → validation → walk → entry → log)
  - **Source**: `scripts/ingest_common.py` (Task 2에서 생성) — import 대상
  - **Metis Q1**: `file` 필드 형식 `"{source_name}/{base_name}"` 필수 — `verify_content.py:148` 호환
  - **Metis E1**: symlink 무한 루프 방지 — `follow_symlinks=False`

  **Acceptance Criteria**:
  - [ ] `python scripts/ingest_projects.py --help` → exit 0
  - [ ] 2개 테스트 파일로 엔트리 생성 확인
  - [ ] 엔트리 ID가 source-prefixed 형식 (12자리 hex)
  - [ ] `ingest_log.json`의 `file` 필드에 `source_name/` 접두사 포함

  **QA Scenarios:**
  ```
  Scenario: 단일 프로젝트 소스로 엔트리 생성
    Tool: Bash
    Preconditions: /tmp/test_proj/doc/guide.md 생성 (frontmatter + 본문)
    Steps:
      1. mkdir -p /tmp/test_proj/doc /tmp/ingest_wiki
      2. echo -e "---\ntitle: Crawler Guide\ntags: [sim]\ndate: 2026-04-05\n---\nSimulation content" > /tmp/test_proj/doc/guide.md
      3. python scripts/ingest_projects.py --source-root /tmp/test_proj/doc --wiki-root /tmp/ingest_wiki --source-name test_proj --source-top Test --source-category Project
      4. ls /tmp/ingest_wiki/../raw/entries/test_proj/
      5. python -c "
         import json
         log = json.load(open('/tmp/ingest_wiki/../raw/ingest_log.json'))
         e = log['entries'][0]
         assert e.get('source_name') == 'test_proj', f'source_name mismatch: {e.get("source_name")}'
         assert 'test_proj/' in e.get('file', ''), f'file field missing prefix: {e.get("file")}'
         assert len(e['id']) == 12, f'ID length wrong: {len(e["id"])}'
         print(f'PASS: entry {e["id"]} with file={e["file"]}')"
    Expected Result: 1개 엔트리 생성, source_name + file 필드 정확
    Evidence: .sisyphus/evidence/task-8-ingest-projects.txt

  Scenario: Source-prefixed ID 충돌 방지 검증
    Tool: Bash
    Steps:
      1. python -c "
         import hashlib
         id_a = hashlib.sha1('src_a:doc/guide.md'.encode()).hexdigest()[:12]
         id_b = hashlib.sha1('src_b:doc/guide.md'.encode()).hexdigest()[:12]
         assert id_a != id_b, f'COLLISION: {id_a} == {id_b}'
         print(f'PASS: {id_a} != {id_b}')"
    Expected Result: 두 ID가 다름
    Evidence: .sisyphus/evidence/task-8-id-collision.txt
  ```

  **Commit**: YES
  - Message: `feat(wiki-gen): add ingest_projects.py for project doc/ ingestion`
  - Files: `scripts/ingest_projects.py`
  - Pre-commit: `python scripts/ingest_projects.py --help`

---

- [x] 9. test_ingest_common.py + ingest_obsidian.py 회귀 테스트

  **What to do**:
  - `tests/test_ingest_common.py` 생성 — 추출된 공통 함수 단위 테스트
  - 테스트 대상: `Entry.to_markdown()`, `slugify()`, `parse_yaml_frontmatter()`, `parse_date_fields()`, `coerce_tag_list()`, `coerce_alias_list()`
  - `ingest_obsidian.py` 회귀 테스트: 실제 파일 ingest 후 출력 검증
  - `conftest.py` 픽스처 활용 (`tmp_wiki_root`, `tmp_source_dir`)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 테스트 설계 + 회귀 방지 검증. 공통 함수 동작 이해 필요.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2, with Task 8)
  - **Blocks**: 없음
  - **Blocked By**: Tasks 1, 2

  **References**:
  - **Source**: `scripts/ingest_common.py` (Task 2) — 테스트 대상 함수 목록
  - **Source**: `scripts/ingest_obsidian.py` — 회귀 테스트용 CLI 인터페이스
  - **Metis AC1**: Gold-output 회귀 테스트 패턴 참고

  **Acceptance Criteria**:
  - [ ] `python -m pytest tests/test_ingest_common.py -v` → 전체 PASS
  - [ ] 최소 8개 테스트 케이스 (6개 함수 + 2개 엣지)

  **QA Scenarios:**
  ```
  Scenario: pytest 실행 + 전체 PASS
    Tool: Bash
    Steps:
      1. python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/test_ingest_common.py -v --tb=short 2>&1
    Expected Result: exit 0, 마지막 줄에 "passed" 포함, "failed" 없음
    Evidence: .sisyphus/evidence/task-9-test-common.txt
  ```

  **Commit**: YES
  - Message: `test(wiki-gen): add ingest_common and regression tests`
  - Files: `tests/test_ingest_common.py`
  - Pre-commit: `python -m pytest tests/test_ingest_common.py -v`

---

- [x] 10. sync_sources.py 다중 소스 오케스트레이터 구현

  **What to do**:
  - `scripts/sync_sources.py` 생성 (~400줄) — 스펙 §4.1 의사코드 기반
  - `sources.yaml` 파서 + 검증: `name` 필드 `^[a-z0-9][a-z0-9_-]*$`, 중복 불가 (Metis G4)
  - type별 분기: `obsidian` → `ingest_obsidian.py` subprocess, `git`/`local` → `ingest_projects.py` subprocess
  - Git sparse clone: `git clone --depth 1 --filter=blob:none --sparse`, `.sync_cache/` 캐싱
  - `sync_log.json` 증분 추적 (content hash 기반)
  - `ingest_log.json` 병합 (소스별 개별 로그 → 통합 로그)
  - 삭제 감지: 소스에서 제거된 파일의 엔트리 정리
  - CLI: `--config`, `--wiki-root`, `--source`, `--dry-run`, `--force`
  - Exit code: 부분 성공 = exit 0 + stderr warning (U3 확정)
  - `sync_log.json` 위치: `wiki_root.parent / 'sync_log.json'` (Metis Q3)
  - subprocess 패턴: `finalize.py:44-49` 참고 — `subprocess.run([sys.executable, str(script_dir / 'xxx.py'), ...])`
  - post_sync: `rebuild_index.py` + `check_coverage.py` 자동 실행

  **Must NOT do**:
  - retry 라이브러리/circuit breaker 금지 — simple try/except + warning
  - `finalize.py`에 sync 검증 통합 금지
  - `generate_batches.py` source-aware 그룹핑 금지
  - GitHub Actions `.yml` 파일 생성 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 가장 복잡한 스크립트. 다중 소스 오케스트레이션 + git clone + 증분 추적 + 병합 + 삭제 감지.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (critical path)
  - **Parallel Group**: Wave 3 (with Task 11)
  - **Blocks**: Tasks 12, 13
  - **Blocked By**: Tasks 2, 8

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §4.1 전체 (lines 101-201) — 의사코드, 설계 결정, sync_log 스키마, sparse clone, 삭제 감지
  - **Spec**: §4.3 sources.yaml 스키마 (lines 324-374) — type별 동작 표
  - **Spec**: §4.4 ingest_log.json 병합 (lines 377-408)
  - **Pattern**: `scripts/finalize.py` lines 44-49, 72-77 — subprocess 호출 패턴
  - **Metis G4**: source name 검증 규칙
  - **Metis Q3**: sync_log.json 위치 = `wiki_root.parent`

  **Acceptance Criteria**:
  - [ ] `python scripts/sync_sources.py --help` → exit 0
  - [ ] 2개 local 소스 sync → `raw/entries/{source}/` 생성 + `sync_log.json` + 병합된 `ingest_log.json`
  - [ ] `--dry-run` → 파일 변경 없음
  - [ ] 멱등성: 동일 sync 2회 → unchanged 카운트

  **QA Scenarios:**
  ```
  Scenario: 2개 local 소스 end-to-end sync
    Tool: Bash
    Preconditions: /tmp/src_a/doc/guide.md, /tmp/src_b/doc/readme.md 생성
    Steps:
      1. mkdir -p /tmp/src_a/doc /tmp/src_b/doc /tmp/sync_wiki
      2. echo -e "---\ntitle: Guide A\n---\nContent A" > /tmp/src_a/doc/guide.md
      3. echo -e "---\ntitle: Readme B\n---\nContent B" > /tmp/src_b/doc/readme.md
      4. cat > /tmp/test_sources.yaml << 'YAML'
         sources:
           - name: test_a
             type: local
             path: /tmp/src_a
             doc_path: doc/
             source_top: Test
             source_category: Project
           - name: test_b
             type: local
             path: /tmp/src_b
             doc_path: doc/
             source_top: Test
             source_category: Project
         settings:
           entries_subdir: true
           id_strategy: source_prefixed
         YAML
      5. python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/sync_wiki
      6. python -c "
         import json, pathlib
         assert pathlib.Path('/tmp/sync_wiki/../raw/entries/test_a').is_dir()
         assert pathlib.Path('/tmp/sync_wiki/../raw/entries/test_b').is_dir()
         log = json.load(open('/tmp/sync_wiki/../raw/ingest_log.json'))
         assert len(log['entries']) == 2, f'Expected 2, got {len(log["entries"])}'
         sync = json.load(open('/tmp/sync_wiki/../sync_log.json'))
         assert 'test_a' in sync['sources']
         assert 'test_b' in sync['sources']
         print('PASS: 2 sources synced')"
    Expected Result: "PASS: 2 sources synced"
    Evidence: .sisyphus/evidence/task-10-sync-e2e.txt

  Scenario: 멱등성 검증
    Tool: Bash
    Steps:
      1. python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/sync_wiki 2>&1 | tee /tmp/sync_idempotent.log
      2. grep -i "unchanged" /tmp/sync_idempotent.log
    Expected Result: stdout에 "unchanged: 2" 또는 유사 메시지
    Evidence: .sisyphus/evidence/task-10-idempotent.txt

  Scenario: 삭제 감지
    Tool: Bash
    Steps:
      1. rm /tmp/src_a/doc/guide.md
      2. python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/sync_wiki
      3. python -c "
         import json, glob
         entries = glob.glob('/tmp/sync_wiki/../raw/entries/test_a/*.md')
         assert len(entries) == 0, f'Entry not deleted: {entries}'
         log = json.load(open('/tmp/sync_wiki/../raw/ingest_log.json'))
         test_a = [e for e in log['entries'] if e.get('source_name') == 'test_a']
         assert len(test_a) == 0, 'Deleted entry still in log'
         print('PASS: deletion detected')"
    Expected Result: "PASS: deletion detected"
    Evidence: .sisyphus/evidence/task-10-deletion.txt
  ```

  **Commit**: YES
  - Message: `feat(wiki-gen): add sync_sources.py multi-source orchestrator`
  - Files: `scripts/sync_sources.py`
  - Pre-commit: `python scripts/sync_sources.py --help`

---

- [x] 11. test_ingest_projects.py 테스트

  **What to do**:
  - `tests/test_ingest_projects.py` 생성 — ingest_projects.py 단위 테스트
  - 테스트: 엔트리 생성, source-prefixed ID, frontmatter 정확성, `file` 필드 형식 (`"{source}/{base}"`), 빈 doc/ 처리, symlink 처리
  - `conftest.py` 픽스처 활용

  **Recommended Agent Profile**: `unspecified-high` | **Skills**: []
  **Parallelization**: Wave 3 (with Task 10) | **Blocks**: 없음 | **Blocked By**: Tasks 1, 8

  **References**:
  - **Source**: `scripts/ingest_projects.py` (Task 8) — 테스트 대상
  - **Metis Q1**: `file` 필드 형식 검증 필수
  - **Metis E2**: 빈 doc/ 디렉토리 엣지케이스

  **QA Scenarios:**
  ```
  Scenario: pytest 실행 + 전체 PASS
    Tool: Bash
    Steps:
      1. python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/test_ingest_projects.py -v --tb=short 2>&1
    Expected Result: exit 0, "passed" 포함
    Evidence: .sisyphus/evidence/task-11-test-projects.txt
  ```

  **Commit**: YES
  - Message: `test(wiki-gen): add ingest_projects tests`
  - Files: `tests/test_ingest_projects.py`

---

- [x] 12. test_sync_sources.py + 통합 테스트

  **What to do**:
  - `tests/test_sync_sources.py` 생성 — sync 통합 테스트
  - 테스트: sources.yaml 파싱, name 검증 (유효/무효), 중복 name 거부, 2개 local 소스 e2e sync, 멱등성, 삭제 감지, sync_log.json 구조, ingest_log.json 병합, --dry-run 검증
  - Git clone 테스트는 네트워크 의존이므로 mock 또는 skip (Metis)

  **Recommended Agent Profile**: `unspecified-high` | **Skills**: []
  **Parallelization**: Wave 4 (with Task 13) | **Blocks**: 없음 | **Blocked By**: Tasks 1, 10

  **References**:
  - **Source**: `scripts/sync_sources.py` (Task 10) — 테스트 대상
  - **Spec**: `multi-source-sync-impl.md` §6.1-6.2 테스트 계획 (lines 638-656)
  - **Metis E3, E4**: name 유효성 검증 엣지케이스

  **QA Scenarios:**
  ```
  Scenario: pytest 전체 실행 + PASS
    Tool: Bash
    Steps:
      1. python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/test_sync_sources.py -v --tb=short 2>&1
    Expected Result: exit 0, "passed" 포함
    Evidence: .sisyphus/evidence/task-12-test-sync.txt
  ```

  **Commit**: NO (groups with Task 13)

---

- [x] 13. 파이프라인 호환성 검증

  **What to do**:
  - sync 후 기존 파이프라인 스크립트 전체 실행 검증:
    - `rebuild_index.py --wiki-root` → exit 0
    - `check_coverage.py --wiki-root` → exit 0
    - `generate_batches.py` → 멀티소스 엔트리로 배치 생성 성공
  - 스펙 §5 호환성 보장 내용 (lines 604-633) 실제 검증

  **Recommended Agent Profile**: `unspecified-high` | **Skills**: []
  **Parallelization**: Wave 4 (with Task 12) | **Blocks**: 없음 | **Blocked By**: Task 10

  **References**:
  - **Spec**: `multi-source-sync-impl.md` §5 호환성 보장 (lines 604-633) — rglob 확인, flat/subdirectory 공존
  - **Source**: `scripts/rebuild_index.py`, `scripts/check_coverage.py` — 실행 대상

  **QA Scenarios:**
  ```
  Scenario: sync 후 기존 파이프라인 스크립트 전체 exit 0
    Tool: Bash
    Preconditions: Task 10 QA 시나리오의 sync 완료 상태 (/tmp/sync_wiki 에 2개 소스 엔트리 존재)
    Steps:
      1. python scripts/rebuild_index.py --wiki-root /tmp/sync_wiki
      2. python scripts/check_coverage.py --wiki-root /tmp/sync_wiki
    Expected Result: 두 명령 모두 exit 0
    Evidence: .sisyphus/evidence/task-13-pipeline-rebuild-coverage.txt

  Scenario: generate_batches.py가 멀티소스 엔트리로 배치 생성
    Tool: Bash
    Preconditions: Task 10 sync 완료 상태, /tmp/sync_wiki/../raw/ingest_log.json 에 2개 엔트리 존재
    Steps:
      1. python scripts/generate_batches.py --wiki-root /tmp/sync_wiki --target-batches 1 --max-entries-per-batch 10
      2. python -c "
         import json, glob
         batches = glob.glob('/tmp/sync_wiki/../raw/batches/batch_*.json')
         assert len(batches) >= 1, f'No batch files generated: {batches}'
         batch = json.load(open(batches[0]))
         assert len(batch.get('entry_files', batch.get('entries', []))) >= 1, 'Batch has no entry_files'
         key = 'entry_files' if 'entry_files' in batch else 'entries'
         print(f'PASS: {len(batches)} batch(es), {len(batch[key])} items in first batch')"
    Expected Result: 1개 이상 배치 파일 생성, 엔트리 포함
    Evidence: .sisyphus/evidence/task-13-generate-batches.txt
  ```

  **Commit**: YES (Tasks 12-13 묶음)
  - Message: `test(wiki-gen): add integration tests and pipeline verification`
  - Files: `tests/test_sync_sources.py`
  - Pre-commit: `python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ -v`

---

- [x] 14. 버전/레지스트리/문서 업데이트

  **What to do**:
  - `plugins/wiki-gen/.claude-plugin/plugin.json`: version `1.1.0` → `1.2.0`
  - `.claude-plugin/marketplace.json`: wiki-gen 항목 version 업데이트 + metadata.version MINOR 버프
  - `AGENTS.md`: Version 헤더 + WHERE TO LOOK 표 (`wiki sync` 항목) + COMMANDS 섹션 (신규 스크립트 3개) + Generated 날짜
  - `README.md`: Version + wiki-gen 섹션 (10번째 서브커맨드, 신규 스크립트) + 변경 이력 표
  - 4개 파일의 버전 동기화 확인

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 5 (sequential) | **Blocks**: 없음 | **Blocked By**: Tasks 1-13 전체

  **References**:
  - **Rule**: AGENTS.md `MANDATORY: Version Management & Registry Updates` 섹션
  - **Rule**: AGENTS.md `MANDATORY: AGENTS.md 최신화` 섹션
  - **Rule**: AGENTS.md `MANDATORY: README.md 최신화` 섹션
  - **Metis R5**: 4개 파일 버전 동기화 체크리스트

  **QA Scenarios:**
  ```
  Scenario: 4개 파일 버전 동기화 확인
    Tool: Bash
    Steps:
      1. python -c "
         import json
         pj = json.load(open('plugins/wiki-gen/.claude-plugin/plugin.json'))
         assert pj['version'] == '1.2.0', f'plugin.json: {pj["version"]}'
         mj = json.load(open('.claude-plugin/marketplace.json'))
         wiki = [p for p in mj['plugins'] if p['name'] == 'wiki-gen'][0]
         assert '1.2.0' in wiki.get('version', ''), f'marketplace: {wiki.get("version")}'
         print('PASS: versions synced')"
      2. grep -q "wiki sync" AGENTS.md
      3. grep -q "sync_sources" AGENTS.md
    Expected Result: 모든 명령 exit 0
    Evidence: .sisyphus/evidence/task-14-version-sync.txt
  ```

  **Commit**: YES
  - Message: `chore(wiki-gen): bump version to 1.2.0, update registry and docs`
  - Files: `plugin.json`, `marketplace.json`, `AGENTS.md`, `README.md`
---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval.**

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ -v`. Review all new/changed files for: `as any`/type: ignore, empty catches, print() in prod code, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: empty doc/, invalid sources.yaml, symlinks.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| After Task(s) | Commit Message | Files | Pre-commit |
|---|---|---|---|
| 1 | `test(wiki-gen): add pytest infrastructure for v1.2.0` | tests/conftest.py, pytest.ini | — |
| 2 | `refactor(wiki-gen): extract shared functions to ingest_common.py` | scripts/ingest_common.py, scripts/ingest_obsidian.py | `python scripts/ingest_obsidian.py --help` (exit 0) |
| 3-7 | `docs(wiki-gen): add wiki sync documentation and SKILL.md section` | references/*, assets/*, SKILL.md, scripts/README.md | — |
| 8 | `feat(wiki-gen): add ingest_projects.py for project doc/ ingestion` | scripts/ingest_projects.py | `python scripts/ingest_projects.py --help` (exit 0) |
| 9 | `test(wiki-gen): add ingest_common and regression tests` | tests/test_ingest_common.py | `python -m pytest tests/test_ingest_common.py -v` |
| 10 | `feat(wiki-gen): add sync_sources.py multi-source orchestrator` | scripts/sync_sources.py | `python scripts/sync_sources.py --help` (exit 0) |
| 11 | `test(wiki-gen): add ingest_projects tests` | tests/test_ingest_projects.py | `python -m pytest tests/test_ingest_projects.py -v` |
| 12-13 | `test(wiki-gen): add integration tests and pipeline verification` | tests/test_sync_sources.py | `python -m pytest tests/ -v` |
| 14 | `chore(wiki-gen): bump version to 1.2.0, update registry and docs` | plugin.json, marketplace.json, AGENTS.md, README.md | — |

---

## Success Criteria

### Verification Commands
```bash
# 1. All tests pass
python -m pytest plugins/wiki-gen/skills/wiki-gen/tests/ -v  # Expected: all PASS

# 2. Sync with 2 local sources
python plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py \
  --config /tmp/test_sources.yaml --wiki-root /tmp/test_wiki  # Expected: exit 0, 2 entries created

# 3. Idempotency
python plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py \
  --config /tmp/test_sources.yaml --wiki-root /tmp/test_wiki  # Expected: unchanged: 2, added: 0

# 4. Backward compatibility
python plugins/wiki-gen/skills/wiki-gen/scripts/ingest_obsidian.py --help  # Expected: exit 0, same interface

# 5. Downstream pipeline
python plugins/wiki-gen/skills/wiki-gen/scripts/rebuild_index.py --wiki-root /tmp/test_wiki  # Expected: exit 0
python plugins/wiki-gen/skills/wiki-gen/scripts/check_coverage.py --wiki-root /tmp/test_wiki  # Expected: exit 0
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (`pytest` exit 0)
- [ ] `ingest_obsidian.py` gold-diff regression passes
- [ ] sync 멱등성 검증 통과
- [ ] 기존 파이프라인 스크립트 전부 exit 0
- [ ] plugin.json v1.2.0
- [ ] AGENTS.md, README.md, marketplace.json 동기화
