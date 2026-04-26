# Visual Generator — GPT-image-2 (OpenAI) 렌더링 경로 추가

## TL;DR

> **Quick Summary**: 기존 Gemini 단일 렌더링 경로에 OpenAI gpt-image-2 기반의 병렬 경로를 추가하고, 사용자가 프롬프트 생성 전(`pre`) 또는 후(`post`)에 렌더러를 선택할 수 있도록 오케스트레이터를 확장한다. 기존 Gemini 코드는 byte-identical 유지(완전 보존).
>
> **Deliverables**:
> - 신규 에이전트: `agents/renderer-agent-openai.md`
> - 신규 스크립트: `scripts/generate_slide_images_openai.py` (gpt-image-2 + GPT vision 평가)
> - 신규 참조: `references/openai-quality-rubric.md`
> - 수정 오케스트레이터: `commands/visual-generate.md` (`renderer`, `renderer_choice_timing` 파라미터)
> - 마켓플레이스/문서 동기화: `plugin.json` (3.4.0→3.5.0), `marketplace.json` (3.29.0→3.30.0), `README.md`, `AGENTS.md`
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: Task 1 (model 검증) → Task 5 (Python 스크립트) → Task 6 (renderer-agent-openai) → Task 7 (오케스트레이터) → Wave 4 (검증) → Final review

---

## Context

### Original Request

> ulw @plugins\visual-generator/ https://developers.openai.com/api/docs/guides/image-generation 를 참조해서 'gpt-image-2' 기반의 모델을 사용해서 가장 좋은 품질의 이미지를 생성하는 경로를 추가해줘.
> 즉, 기존에 gemini를 이용하는 경로 1) 과 gpt-image-2를 이용하는 경로 2)를 구현하고 프롬프트 생성 후, 사용자에게 선택하도록 해. 혹은, 프롬프트 생성 전 어떤 경로로 전체 이미지 생성 자동화를 할지 물어보는 기능을 함께 추가해줘.

### Interview Summary

**Key Decisions (사용자 확정)**:
- **D1 Choice UX**: pre + post 둘 다 지원 — 신규 파라미터 `renderer_choice_timing: pre|post|none`
- **D2 Both 모드**: 미지원 (단일 모델만 — `gemini` 또는 `openai` 중 하나)
- **D3 아키텍처**: 별도 에이전트 + 별도 스크립트 (`renderer-agent-openai`, `generate_slide_images_openai.py`)
- **D4 품질 평가**: GPT 계열 최고 vision 모델로 5D 평가 신규 구현 (Structured Outputs + json_schema strict)
- **D5 출력 설정**: `quality="high"`, `size="1536x1024"`, `output_format="jpeg"`

**Defaults Applied (Metis 권고 — 사용자가 override 가능)**:
- **D1 기본값**: `renderer_choice_timing="none"`, `renderer="gemini"` (백워드 호환 보장)
- **D9 비용 cap**: `--max-images` 인자 추가 (기본 30, 초과 시 확인 또는 `--yes` 필요)
- **D10 검증 우선**: 첫 작업은 OpenAI 모델 가용성 smoke test
- **D11 SYSTEM_INSTRUCTION**: Python 상수로 user prompt에 prepend (Image API 특성)
- **D12 검증 체크리스트**: 16항목은 renderer-agent.md 참조 (중복 금지)
- **D13 Hard fail**: OPENAI_API_KEY 누락 시 즉시 실패 (silent fallback 금지)

### Research Findings

**OpenAI 모델 (librarian, 2026-04 기준)**:
- 평가 모델 후보: `gpt-5.5` (2026-04-23 frontier vision) — Responses API + Structured Outputs json_schema strict mode
- 생성 모델: `gpt-image-2` (snapshot 2026-04-21), `quality="high"` + `size="1536x1024"` = **$0.165/image**
- Image base64 응답 (`b64_json` 필드), `detail: "original"`로 한글 가독성 보존
- 한글 가독성 caveat 존재 (non-Latin alphabets suboptimal) — 명시적 rubric으로 완화
- **CRITICAL**: 모델명 (특히 `gpt-5.5`)은 첫 단계에서 실제 API 호출로 검증 필수

**Codebase 현황 (explore)**:
- visual-generator 테스트 인프라 부재 (pytest.ini의 testpaths는 hwpx-generator, wiki-gen만)
- CI/CD 워크플로우 부재 (`.github/workflows/` 없음)
- OpenAI 참조 0건 (완전 Gemini-exclusive 상태)
- 4-block 프롬프트 구조는 model-agnostic, Gemini 특화 지시문은 OpenAI에 무해 (호환 가정 → A/B 검증 필요)
- `generate_slide_images.py` 5D 평가 + Korean 환각 veto 로직 (점수≥7.0 AND 한글≥5.0 AND 환각≥5.0) 보유

### Metis Review

**Identified Gaps (모두 반영)**:
- 백워드 호환: `renderer_choice_timing` 기본값 `none`으로 변경 (auto_mode 사용자 보호)
- 스코프 크립 제거: `content-organizer.md` 수정 DROP (렌더러 선택은 infrastructure)
- 비용 가드: `--max-images` 추가
- 모델명 검증: 첫 작업으로 분리
- Cross-task contamination: 보호 파일 allowlist 명시
- marketplace.json 양 버전 필드 동시 업데이트 의무
- SYSTEM_INSTRUCTION 처리 명확화 (Python 상수 prepend)

---

## Work Objectives

### Core Objective

visual-generator 플러그인에 OpenAI gpt-image-2 기반의 병렬 렌더링 경로를 추가하여 사용자가 Gemini 또는 OpenAI 중 선택할 수 있게 한다. 기존 Gemini 동작은 zero-change 보장.

### Concrete Deliverables

- `plugins/visual-generator/agents/renderer-agent-openai.md` (신규)
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` (신규)
- `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md` (신규)
- `plugins/visual-generator/commands/visual-generate.md` (수정: 신규 파라미터 + 분기)
- `plugins/visual-generator/skills/slide-renderer/SKILL.md` (수정: OpenAI 섹션)
- `plugins/visual-generator/.claude-plugin/plugin.json` (3.4.0 → 3.5.0)
- `.claude-plugin/marketplace.json` (visual-generator entry version + agents 배열, metadata.version 3.29.0→3.30.0)
- `README.md` (Version 3.30.0, 변경 이력, visual-generator 섹션)
- `AGENTS.md` (Version, Generated, WHERE TO LOOK, COMMANDS, ANTI-PATTERNS)

### Definition of Done

- [ ] 사용자가 `renderer="openai"`로 시각자료 생성 시 gpt-image-2로 이미지 1개 이상 정상 생성 (smoke test 통과)
- [ ] 사용자가 신규 파라미터 없이 기존 명령 호출 시 Gemini 동작 100% 유지 (regression 통과)
- [ ] 보호 파일 6개 (renderer-agent.md, generate_slide_images.py, prompt-designer.md, content-organizer.md, content-reviewer.md, prompt-validator.md) byte-identical (`git diff` empty)
- [ ] 5개 버전 필드 (plugin.json 3.5.0, marketplace plugin entry 3.5.0, marketplace metadata 3.30.0, README Version 3.30.0, AGENTS Version 3.30.0) 모두 동기화
- [ ] marketplace.json 스키마 검증 통과 (Unrecognized keys 없음)
- [ ] 모든 QA 시나리오 evidence 파일 `.sisyphus/evidence/`에 저장됨

### Must Have

- 별도 에이전트 + 별도 스크립트 아키텍처 (D3)
- `renderer` (gemini|openai) + `renderer_choice_timing` (pre|post|none) 파라미터
- pre/post 두 시점 모두 인터랙티브 선택 가능
- gpt-image-2 quality=high, size=1536x1024, JPEG 출력
- 5D 평가 루프 (Structured Outputs json_schema strict)
- OPENAI_API_KEY 누락 시 hard fail
- `--max-images` 비용 cap (기본 30)
- SYSTEM_INSTRUCTION은 user prompt에 prepend
- 16-item 검증 renderer-agent.md 참조 (중복 금지)

### Must NOT Have (Guardrails)

- **보호 파일 수정 금지** (cross-task contamination — **기존 파일만 보호**, 신규 추가는 허용):
  - `agents/renderer-agent.md` (기존)
  - `agents/prompt-designer.md` (기존)
  - `agents/content-organizer.md` (기존)
  - `agents/content-reviewer.md` (기존)
  - `agents/prompt-validator.md` (기존)
  - `skills/slide-renderer/scripts/generate_slide_images.py` (기존)
  - `skills/slide-renderer/references/scene-richness-spec.md` (기존)
  - `skills/slide-renderer/references/validation-rules-map.md` (기존)
  - `skills/slide-renderer/references/korean-typography-spec.md` (기존)
  - `skills/theme-*/*` (전체 6개 테마 스킬, 모두 기존)
  - `skills/layout-types/*` (전체, 모두 기존)
  - **예외 (수정 허용)**: 신규 파일 `skills/slide-renderer/references/openai-quality-rubric.md` (Task 3에서 신규 생성), `skills/slide-renderer/SKILL.md` (Task 4에서 OpenAI 섹션 추가)
- **기능 확장 금지** (스코프 제한):
  - 이미지 편집/variation API
  - DALL-E, gpt-image-1/1.5/mini, 기타 모델 지원
  - Streaming responses, 마스크/inpainting
  - Batch API
  - `renderer="both"` 모드
  - 렌더러 factory 패턴, 추상 베이스 클래스
- **품질 우회 금지**:
  - silent fallback (OpenAI 실패 시 Gemini로 자동 전환 금지)
  - 모델명 placeholder 사용 (검증 전)
  - "지나가는 김에" 코드 정리
  - 기존 검증 #9, #10, #11 누락 항목 수정 (out of scope)
  - prompt-validator orphan 처리 (out of scope)
- **테스트 인프라 신규 구축 금지** (기존 컨벤션 유지)
- **`auto_mode=true`+`renderer_choice_timing="pre"` 조합 미정의 동작 금지** (자동 해결 정책 명시)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision

- **Infrastructure exists**: NO (visual-generator는 pytest 미적용)
- **Automated tests**: NONE (기존 컨벤션 유지)
- **Framework**: 없음 (Agent-Executed QA Scenarios에 의존)
- **이유**: visual-generator 기존 패턴 일치, 핵심은 실제 API 호출 검증 (단위 테스트로는 모델 응답 품질 검증 불가)

### QA Policy

모든 task는 agent-executed QA scenarios 필수. evidence 파일은 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`에 저장.

- **Python 스크립트**: PowerShell에서 `python --help` 호출 + 실제 API smoke test (--max-images=1)
- **에이전트/오케스트레이터 .md**: Python으로 파일 읽고 substring 검사 (PowerShell 호환성)
- **JSON 파일**: Python `json.load()` + 스키마 화이트리스트 검사
- **마크다운 동기화**: Python regex로 버전/날짜 일치 확인
- **보호 파일**: `git diff HEAD -- {보호파일들}` empty 확인 (git은 cross-platform)

### Shell Portability Policy (Windows + PowerShell)

> **현재 환경**: Windows + PowerShell (AGENTS.md 라인 71-103 참조). Bash 도구는 PowerShell shell을 사용.
>
> **모든 QA scenario는 아래 패턴 중 하나만 사용** (일관성 + 이식성):

| 작업 유형 | 권장 방식 | 금지 방식 |
|----------|----------|----------|
| 키워드/필드 다중 검사 | `python -c "for k in [...]: assert k in content..."` | `for X in A B C; do grep -q ... done` (bash 전용) |
| 파일 라인 수 검증 | `python -c "n = sum(1 for _ in open(f)); assert n >= N"` | `wc -l file \| awk '{...}'` (Unix 전용) |
| 첫 N줄 추출 | `python -c "lines = open(f).readlines()[:N]"` | `head -N` (Unix 전용) |
| 텍스트 검색 | `python -c "assert 'X' in open(f).read()"` 또는 `Select-String -Path f -Pattern X` | `grep` (Git Bash 의존) |
| JSON 파싱 | `python -c "import json; ..."` | jq (별도 설치 필요) |
| 디렉토리 생성 | `New-Item -ItemType Directory -Path X -Force` 또는 `python -c "import os; os.makedirs(X, exist_ok=True)"` | `mkdir -p` (PowerShell도 지원하나 옵션 다름) |
| 파일 존재 확인 | `Test-Path` (PowerShell native) 또는 `python -c "import os; assert os.path.isfile(...)"` | `test -f` (bash 전용) |
| 환경변수 확인 | `if (-not $env:KEY)` (PowerShell) 또는 `python -c "import os; assert os.getenv('KEY')"` | `if [ -z "$KEY" ]` (bash 전용) |
| 멀티라인 Python 인라인 | `python -c "..."` 한 줄에 작성 또는 `.py` 파일을 별도 작성 후 호출 | heredoc `<< 'EOF'` (bash 전용) |

**모든 task의 QA scenarios는 `Tool: Bash (PowerShell + Python)` 또는 `Tool: PowerShell` 또는 `Tool: Bash (Python only)`로 표시한다.**

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - 4 parallel — 즉시 시작):
├── Task 1: OpenAI 모델 가용성 smoke test (gpt-image-2 + gpt-5.5)  [quick]
├── Task 2: plugin.json 버전 업데이트 (3.4.0 → 3.5.0)              [quick]
├── Task 3: openai-quality-rubric.md 신규 작성 (5D 평가 가이드)     [writing]
└── Task 4: SKILL.md OpenAI 섹션 추가                              [writing]

Wave 2 (Core Implementation - 4 parallel — Wave 1 완료 후):
├── Task 5: generate_slide_images_openai.py 신규 (deps: 1, 3)      [unspecified-high]
├── Task 6: renderer-agent-openai.md 신규 (deps: 1, 3)             [unspecified-high]
├── Task 7: visual-generate.md 수정 (deps: 1)                       [unspecified-high]
└── Task 8: marketplace.json visual-generator entry (deps: 6)       [quick]

Wave 3 (Documentation Sync - 3 parallel — Wave 2 완료 후):
├── Task 9:  marketplace.json metadata.version (3.29.0→3.30.0)     [quick]
├── Task 10: README.md (Version + 변경 이력 + visual-generator)    [writing]
└── Task 11: AGENTS.md (Version + Generated + WHERE TO LOOK + COMMANDS + ANTI-PATTERNS) [writing]

Wave 4 (Verification - 4 parallel — Wave 3 완료 후):
├── Task 12: AC1 회귀 검증 (기존 Gemini 동작 보존)                [quick]
├── Task 13: AC3 Cross-contamination 검증 (보호 파일 byte-identical) [quick]
├── Task 14: AC5 버전 동기화 검증 (5개 필드 일치)                  [quick]
└── Task 15: AC7 Smoke test 실행 (실제 API 호출, both renderers)   [unspecified-high]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 5 → Task 6 → Task 7 → Task 11 → Task 15 → F1-F4 → user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 4 (Waves 1, 2, 4)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | - | 5, 6, 7 |
| 2 | - | 9, 11, 14 |
| 3 | - | 5, 6 |
| 4 | - | 11 |
| 5 | 1, 3 | 8, 12, 15 |
| 6 | 1, 3 | 8, 12, 15 |
| 7 | 1 | 12, 15 |
| 8 | 6 | 9, 13, 14 |
| 9 | 8 | 14 |
| 10 | 5, 6, 7 | 14 |
| 11 | 2, 4, 5, 6, 7 | 14 |
| 12 | 5, 6, 7 | F1-F4 |
| 13 | 8, 11 | F1-F4 |
| 14 | 9, 10, 11 | F1-F4 |
| 15 | 5, 6, 7 | F1-F4 |
| F1-F4 | 12, 13, 14, 15 | user okay |

### Agent Dispatch Summary

- **Wave 1**: T1→`quick`, T2→`quick`, T3→`writing`, T4→`writing`
- **Wave 2**: T5→`unspecified-high`, T6→`unspecified-high`, T7→`unspecified-high`, T8→`quick`
- **Wave 3**: T9→`quick`, T10→`writing`, T11→`writing`
- **Wave 4**: T12→`quick`, T13→`quick`, T14→`quick`, T15→`unspecified-high`
- **FINAL**: F1→`oracle`, F2→`unspecified-high`, F3→`unspecified-high`, F4→`deep`

---

## TODOs

- [x] 1. **OpenAI 모델 가용성 Smoke Test (gpt-image-2 + 평가 모델)**

  **What to do**:
  - 임시 검증 스크립트 작성 (`/tmp/openai_model_check.py` 또는 인라인 Python `-c`)
  - Step A: `from openai import OpenAI; client = OpenAI(); client.images.generate(model="gpt-image-2", prompt="test", size="1536x1024", quality="high", n=1)` 호출 → 성공/실패 + 응답 구조 확인 (`b64_json` 필드 존재)
  - Step B: 평가 모델 후보 검증 — `client.responses.create(model="gpt-5.5", input=...)` 시도. 모델 미존재 시 `gpt-5`, `gpt-4o` 순으로 폴백하여 사용 가능 모델 확정
  - 결과 (모델명 + 응답 구조 샘플)을 `.sisyphus/evidence/task-1-model-verification.json` 파일에 저장
  - **이 파일이 Tasks 5, 6의 입력 — 검증된 정확한 모델명만 사용 (placeholder 금지)**

  **Must NOT do**:
  - 모델명을 Task 1 검증 없이 추정/하드코딩
  - 실패한 모델명을 다음 단계로 전파
  - 검증 코드를 visual-generator 플러그인 내부 영구 파일로 저장 (임시 파일/`.sisyphus/evidence/`만 사용)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단순 검증 작업, 1-2개 API 호출 + 결과 파싱 + 파일 저장
  - **Skills**: 없음 (`[]`)
  - **Skills Evaluated but Omitted**:
    - `playwright`: API 호출이므로 브라우저 불필요

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Task 5, Task 6, Task 7 (모델명 의존)
  - **Blocked By**: None

  **References**:

  **External References**:
  - OpenAI Image API: `https://platform.openai.com/docs/guides/image-generation` — gpt-image-2 호출 패턴
  - OpenAI Responses API: `https://platform.openai.com/docs/guides/structured-outputs` — Structured Outputs json_schema strict
  - OpenAI Models page: `https://platform.openai.com/docs/models` — 현재 사용 가능한 모델 목록
  - librarian 리서치 결과 (draft `.sisyphus/drafts/visual-generator-openai-renderer.md`의 "OpenAI 리서치 결과" 섹션)

  **WHY Each Reference Matters**:
  - librarian이 보고한 `gpt-5.5` 모델명이 실제 사용 가능한지 확인 — Metis가 hallucinated model name 가능성 지적함
  - 실패 시 `gpt-5` 또는 `gpt-4o`로 폴백 (모두 vision + Structured Outputs 지원)
  - 한 번 검증된 모델명을 Tasks 5, 6에서 재사용 (반복 API 호출 방지)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: gpt-image-2 호출 성공 검증
    Tool: Bash
    Preconditions: OPENAI_API_KEY 환경변수 설정됨
    Steps:
      1. python -c "from openai import OpenAI; import json; r = OpenAI().images.generate(model='gpt-image-2', prompt='a simple white square on black background', size='1536x1024', quality='low', n=1); print(json.dumps({'has_b64': bool(r.data[0].b64_json), 'len': len(r.data[0].b64_json)}))" > .sisyphus/evidence/task-1-gpt-image-2-test.json
      2. python -c "import json; d=json.load(open('.sisyphus/evidence/task-1-gpt-image-2-test.json')); assert d['has_b64'] and d['len'] > 1000, 'invalid response'"
    Expected Result: exit 0, 응답에 b64_json 필드 존재 (>1000 chars)
    Failure Indicators: ImportError(openai 미설치), AuthenticationError(API key), 404(모델 미존재)
    Evidence: .sisyphus/evidence/task-1-gpt-image-2-test.json

  Scenario: 평가 모델 후보 결정 (gpt-5.5 → gpt-5 → gpt-4o 폴백)
    Tool: Bash (PowerShell + Python)
    Preconditions: OPENAI_API_KEY 설정
    Steps:
      1. python -c "
from openai import OpenAI
import json
client = OpenAI()
candidates = ['gpt-5.5', 'gpt-5', 'gpt-4o']
schema = {'format': {'type':'json_schema','strict':True,'json_schema':{'name':'T','schema':{'type':'object','properties':{'x':{'type':'integer'}},'required':['x'],'additionalProperties':False}}}}
selected = None
errors = {}
for model in candidates:
    try:
        client.responses.create(model=model, input='Return {\"x\": 1}', text=schema)
        selected = model
        break
    except Exception as e:
        errors[model] = str(e)[:200]
result = {'eval_model': selected, 'errors': errors}
open('.sisyphus/evidence/task-1-eval-model.txt', 'w', encoding='utf-8').write(json.dumps(result, indent=2))
assert selected, f'all candidates failed: {errors}'
print(f'EVAL_MODEL: {selected}')
"
      2. python -c "
import json
result = json.load(open('.sisyphus/evidence/task-1-eval-model.txt', encoding='utf-8'))
# 검증된 모델명을 Tasks 5, 6의 입력으로 저장
verification = {'image_model': 'gpt-image-2', 'eval_model': result['eval_model']}
open('.sisyphus/evidence/task-1-model-verification.json', 'w', encoding='utf-8').write(json.dumps(verification, indent=2))
print(f'MODELS_VERIFIED: {verification}')
"
    Expected Result: 한 모델이 성공 → evidence 파일 + verification.json에 저장
    Failure Indicators: 3개 모델 모두 실패 → Task 1 STOP (사용자에게 alternative 모델 요청)
    Evidence: .sisyphus/evidence/task-1-eval-model.txt, .sisyphus/evidence/task-1-model-verification.json
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-1-gpt-image-2-test.json` (이미지 API 응답)
  - [ ] `.sisyphus/evidence/task-1-eval-model.txt` (검증된 평가 모델명)
  - [ ] `.sisyphus/evidence/task-1-model-verification.json` (Tasks 5, 6의 입력 — `{"image_model": "gpt-image-2", "eval_model": "...검증된이름..."}`)

  **Commit**: NO (groups with Wave 1 commit `feat(visual-generator): scaffold OpenAI rendering path foundation`)

- [x] 2. **plugin.json 버전 업데이트 (3.4.0 → 3.5.0)**

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` 읽기
  - `version` 필드만 `"3.4.0"` → `"3.5.0"` 변경 (Edit 도구 사용)
  - 다른 필드 변경 절대 금지 (description, author, license 등 보존)
  - JSON syntax 유효성 즉시 검증

  **Must NOT do**:
  - description 수정 (현재 "시각자료 프롬프트 생성 및 이미지 렌더링 (Kurzgesagt/Gov/Seminar/WhatIf/Pitch/Comparison + Renderer)" 그대로 유지)
  - author/email/license 수정
  - 신규 필드 추가 (`contributors`, `maintainer` 등은 스키마 위반)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 1줄 변경
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Task 9 (marketplace metadata 동기화), Task 11 (AGENTS.md), Task 14 (버전 동기화 검증)
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — 현재 상태 (라인 1-10)
  - `AGENTS.md` `Version Management & Registry Updates` 섹션 — MINOR 변경 정책
  - `AGENTS.md` `Plugin.json Schema Compliance (CRITICAL)` 섹션 — 허용 필드 화이트리스트

  **WHY Each Reference Matters**:
  - 새 기능 추가 (gpt-image-2 경로) = MINOR 버전 (3.4.0 → 3.5.0)
  - schema 위반 시 marketplace 등록 실패 (2026-04-21 사례 학습됨)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 버전 업데이트 + 스키마 화이트리스트 검증
    Tool: Bash
    Preconditions: plugin.json 존재, version 필드는 "3.4.0"
    Steps:
      1. python -c "import json; d=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json',encoding='utf-8')); assert d['version']=='3.5.0', f'expected 3.5.0, got {d[\"version\"]}'" 
      2. python -c "import json; A = {'name','version','description','author','homepage','repository','license','keywords','skills','commands','agents','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies'}; d=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json',encoding='utf-8')); extra = set(d.keys()) - A; assert not extra, f'INVALID FIELDS: {extra}'" > .sisyphus/evidence/task-2-schema-check.txt 2>&1
    Expected Result: 두 명령 모두 exit 0, evidence 파일 비어있거나 'OK'
    Failure Indicators: AssertionError → 버전 미반영 또는 스키마 위반
    Evidence: .sisyphus/evidence/task-2-schema-check.txt

  Scenario: 다른 필드 미변경 검증 (회귀 방지)
    Tool: Bash (PowerShell + Python)
    Preconditions: git working tree 깨끗
    Steps:
      1. git diff -U0 plugins/visual-generator/.claude-plugin/plugin.json > .sisyphus/evidence/task-2-diff-full.txt
      2. python -c "
import re
diff_text = open('.sisyphus/evidence/task-2-diff-full.txt', encoding='utf-8').read()
# +/- 로 시작하는 콘텐츠 라인만 추출 (+++/--- metadata 제외)
content_lines = [l for l in diff_text.splitlines() if (l.startswith('+') or l.startswith('-')) and not (l.startswith('+++') or l.startswith('---'))]
open('.sisyphus/evidence/task-2-diff.txt', 'w', encoding='utf-8').write('\n'.join(content_lines))
assert len(content_lines) == 2, f'expected exactly 2 changed lines, got {len(content_lines)}: {content_lines}'
assert any('3.5.0' in l and l.startswith('+') for l in content_lines), 'no + 3.5.0'
assert any('3.4.0' in l and l.startswith('-') for l in content_lines), 'no - 3.4.0'
print('VERSION_BUMP_CLEAN')
"
    Expected Result: VERSION_BUMP_CLEAN (diff에 정확히 2줄)
    Failure Indicators: AssertionError → description/author 등 부주의 변경
    Evidence: .sisyphus/evidence/task-2-diff-full.txt, task-2-diff.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-2-schema-check.txt`
  - [ ] `.sisyphus/evidence/task-2-diff.txt`

  **Commit**: NO (Wave 1 합본)

- [x] 3. **`openai-quality-rubric.md` 신규 작성 (5D 평가 가이드, 인간 가독본)**

  **What to do**:
  - 신규 파일: `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md`
  - 내용 (≤80줄, 간결하게):
    - **Purpose**: gpt-image-2 생성 이미지의 5D 품질 평가 기준 정의 (Gemini 5D와 호환)
    - **Evaluation Model**: Task 1에서 검증된 모델명 사용 (placeholder X)
    - **5 Dimensions** (각 0-10점, **Gemini 스크립트 라인 252-253, 260-261, 307-311 필드명과 byte-identical**):
      1. `korean_text_readability`: 한글 자모 완전성, 폰트 명료성, 대비. veto threshold 5.0
      2. `korean_hallucination_detection`: CONTENT 외 한글 텍스트 생성 여부 (10=깨끗, 0=심각). veto threshold 5.0
      3. `content_reference_accuracy`: CONTENT key:value의 충실한 렌더링
      4. `layout_suitability`: 공간 구성, 시각적 위계
      5. `color_palette_compliance`: CONFIGURATION 색상 (#1E3A5F 등) 준수
    - **PASS Criteria**: avg ≥ 7.0 AND korean_text_readability ≥ 5.0 AND korean_hallucination_detection ≥ 5.0 (Gemini와 동일)
    - **Schema** (Structured Outputs json_schema strict): 6개 required 필드 (위 5개 + `overall_score`) + `feedback` (string, ≤200 chars)
    - **Mitigation Notes**: `detail: "original"` 사용 이유 (한글 보존), 색상 hex 명시 이유, spatial reasoning 한계 회피법
    - **Concept Theme Exemption**: korean_text_readability와 korean_hallucination_detection을 10.0으로 자동 설정 (텍스트 없는 테마)
  - frontmatter 없음 (references 폴더의 일반 가이드 파일 형식)

  **Must NOT do**:
  - SKILL.md 수준의 전체 사용법 작성 (rubric 정의에만 집중)
  - 코드 스니펫 50줄 이상 포함 (스크립트가 본체, 여기는 참조 가이드)
  - 점수 기준을 Gemini와 다르게 변경 (드리프트 방지)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 인간 가독 문서 작성 (≤80줄)
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Task 5 (스크립트가 이 rubric 참조), Task 6 (에이전트 검증 단계 참조)
  - **Blocked By**: None (Task 1 결과는 작성 시 참조하지만 모델명은 placeholder/`{Task 1에서 결정}`로 표기 후 Task 5/6 시점에 확정 가능)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/SKILL.md` 라인 81-101 — 기존 5D 평가 schema (이름/임계값 일치 필수)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 238-346 — Gemini의 evaluate_image_quality 함수 (점수 계산 로직 참고)

  **External References**:
  - OpenAI Structured Outputs: `https://platform.openai.com/docs/guides/structured-outputs` — json_schema strict mode 패턴

  **WHY Each Reference Matters**:
  - Gemini 평가 schema와 byte-identical 필드명 유지 (cross-renderer 점수 비교 가능)
  - SYSTEM_INSTRUCTION 16줄에 들어있는 한글 환각 방지 원칙을 OpenAI rubric에도 반영

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 5D 필드명 + threshold 일치성 검증 (Gemini와 byte-identical)
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 파일 작성됨
    Steps:
      1. python -c "
import re
content = open('plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md', encoding='utf-8').read()
required_fields = ['korean_text_readability', 'korean_hallucination_detection', 'content_reference_accuracy', 'layout_suitability', 'color_palette_compliance', 'overall_score']
missing = [f for f in required_fields if f not in content]
assert not missing, f'MISSING_FIELDS: {missing}'
assert '7.0' in content and '5.0' in content, 'thresholds 7.0/5.0 not documented'
lines = content.count(chr(10)) + 1
assert lines <= 80, f'too long: {lines} lines (max 80)'
print('FIELDS_AND_THRESHOLDS_OK')
" > .sisyphus/evidence/task-3-fields.txt 2>&1
    Expected Result: FIELDS_AND_THRESHOLDS_OK 출력
    Failure Indicators: AssertionError → Gemini와 필드명 어긋남 (cross-renderer 비교 불가)
    Evidence: .sisyphus/evidence/task-3-fields.txt

  Scenario: Concept theme 면제 명시 확인
    Tool: Bash (PowerShell + Python)
    Preconditions: 파일 작성됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md', encoding='utf-8').read().lower()
has_concept = 'concept' in content
has_exempt_keyword = any(kw in content for kw in ['exempt', '면제', 'skip', '10.0'])
assert has_concept and has_exempt_keyword, 'concept theme exemption not documented'
print('CONCEPT_EXEMPT_OK')
" > .sisyphus/evidence/task-3-concept-exempt.txt 2>&1
    Expected Result: CONCEPT_EXEMPT_OK
    Evidence: .sisyphus/evidence/task-3-concept-exempt.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-3-fields.txt`
  - [ ] `.sisyphus/evidence/task-3-thresholds.txt`
  - [ ] `.sisyphus/evidence/task-3-concept-exempt.txt`

  **Commit**: NO (Wave 1 합본)

- [x] 4. **`SKILL.md` OpenAI 섹션 추가 (slide-renderer 스킬)**

  **What to do**:
  - 파일: `plugins/visual-generator/skills/slide-renderer/SKILL.md`
  - 기존 Gemini 섹션은 그대로 유지 (위 또는 아래에 새 섹션 추가)
  - 신규 섹션 "## OpenAI gpt-image-2 Rendering Path" 추가:
    - **Environment Requirements**:
      | 항목 | 설명 |
      | Python | 3.8+ |
      | 패키지 | openai>=1.0, Pillow |
      | 환경변수 | `OPENAI_API_KEY` 필수 |
      | 모델 (생성) | gpt-image-2 |
      | 모델 (평가) | (Task 1에서 검증된 모델, 잠정 gpt-5.5) |
      | 출력 | 1536x1024 (16:9 근사), JPEG |
    - **CLI Documentation**:
      ```
      python scripts/generate_slide_images_openai.py \
        --prompts-dir [경로] \
        --output-dir [경로] \
        [--max-images N]  # 기본 30, 초과 시 확인
      ```
    - **Cost Notice**: high quality 1536x1024 = $0.165/image + 평가 비용 ~$0.05/image. 30장 기준 약 $6.6
    - **API Verification 사전 체크**: gpt-image-2 사용 시 OpenAI Organization Verification 필요할 수 있음 (developer console)
    - **Path Resolution**: Gemini 동일 패턴 (상대경로 → Glob 폴백)
    - **Error Handling**: OPENAI_API_KEY 미설정 → 즉시 중단 / API timeout → 5초 후 재시도 (최대 3회) / Org 미검증 (HTTP 403) → 검증 페이지 안내 후 중단
  - 5D 품질 평가는 별도 참조 — `references/openai-quality-rubric.md` 링크

  **Must NOT do**:
  - 기존 Gemini 섹션 수정 (line 38-46 환경 요구사항 등)
  - SYSTEM_INSTRUCTION 전체 복제 (스크립트가 보유)
  - 모델 ID 단정 (Task 1 검증 후 확정 — `{Task 1에서 검증된 평가 모델}` 임시 표기 OK)

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Task 11 (AGENTS.md WHERE TO LOOK 표 갱신 시 참조)
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/SKILL.md` 라인 1-123 — 기존 Gemini 섹션 패턴 준수 (테이블 형식, 명령어 블록, error handling 표)
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` — multi-engine SKILL.md 작성 패턴 참고 (참고용, 직접 복제 금지)

  **WHY Each Reference Matters**:
  - 기존 Gemini 섹션과 동일한 톤·구조 → 사용자 학습 곡선 최소화
  - 두 경로의 환경 요구사항 비교 표가 한눈에 보이도록 배치

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 신규 OpenAI 섹션 존재 + 핵심 키워드 포함
    Tool: Bash (PowerShell + Python)
    Preconditions: SKILL.md 수정됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/skills/slide-renderer/SKILL.md', encoding='utf-8').read()
assert 'OpenAI gpt-image-2' in content, 'FAIL: section missing'
required = ['OPENAI_API_KEY', 'openai>=1.0', 'gpt-image-2', '1536x1024', 'max-images', 'openai-quality-rubric.md']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
print('SECTION_AND_KEYWORDS_OK')
" > .sisyphus/evidence/task-4-keywords.txt 2>&1
    Expected Result: SECTION_AND_KEYWORDS_OK 출력
    Evidence: .sisyphus/evidence/task-4-keywords.txt

  Scenario: 기존 Gemini 섹션 보존 검증 (회귀 방지)
    Tool: Bash (PowerShell + Python)
    Preconditions: SKILL.md 수정됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/skills/slide-renderer/SKILL.md', encoding='utf-8').read()
gemini_keywords = ['GEMINI_API_KEY', 'google-genai', 'gemini-3-pro-image-preview']
preserved = [k for k in gemini_keywords if k in content]
assert len(preserved) >= 3, f'GEMINI_SECTION_DAMAGED: only {preserved} found'
print(f'GEMINI_PRESERVED: {preserved}')
" > .sisyphus/evidence/task-4-gemini-preserved.txt 2>&1
    Expected Result: GEMINI_PRESERVED 출력 (3개 키워드 모두)
    Failure Indicators: Gemini 섹션 손상 → 보호 위반
    Evidence: .sisyphus/evidence/task-4-gemini-preserved.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-4-keywords.txt`
  - [ ] `.sisyphus/evidence/task-4-gemini-preserved.txt`

  **Commit**: NO (Wave 1 합본)

- [x] 5. **`generate_slide_images_openai.py` 신규 작성 (gpt-image-2 + 평가 모델)**

  **What to do**:
  - 신규 파일: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py`
  - **구조 미러링** (기존 Gemini 스크립트와 1:1 대응):
    - Imports: `from openai import OpenAI`, `import base64`, `import argparse`, `import time`, `import re`, `import sys`, `import json`, `from pathlib import Path`, `from PIL import Image as PILImage`, `import io`, `import shutil`
    - 상수 (Task 1 검증 결과 반영):
      - `IMAGE_MODEL = "gpt-image-2"`
      - `EVAL_MODEL = "{Task 1에서 검증된 모델}"` (예: gpt-5.5)
      - `IMAGE_SIZE = "1536x1024"`
      - `IMAGE_QUALITY = "high"`
      - `OUTPUT_FORMAT = "jpeg"`
      - `QUALITY_THRESHOLD = 7.0` (Gemini 동일)
      - `KOREAN_MIN_THRESHOLD = 5.0` (Gemini 동일)
      - `MAX_QUALITY_RETRIES = 2` (Gemini 동일)
      - `API_RETRY_COUNT = 3`, `API_RETRY_DELAY = 5` (Gemini 동일)
      - `INTER_CALL_DELAY = 2` (Gemini 동일)
      - `DEFAULT_MAX_IMAGES = 30`
    - `SYSTEM_INSTRUCTION` (Gemini 스크립트 라인 36-51과 동일한 16줄, Korean Typography/Visual Composition/Negative Constraints) — Python 상수로 보유
    - `EVALUATION_SCHEMA` (Structured Outputs json_schema strict, 6개 required 필드)
  - **함수**:
    - `main()`: argparse — `--prompts-dir` (필수), `--output-dir` (필수), `--max-images` (기본 30), `--yes` (확인 스킵)
    - `process_prompts(prompts_dir, output_dir, max_images, auto_confirm)`: Gemini 동일 — 파일 필터 정규식 `^\d+_`, 제외 목록 `[prompt_index.md, 공통및특화작업구조설명.md, style_sheet.md, validation_result.md]`, 파일명 정렬, 결과 dict 반환. **사전 cost 추정**: prompts 수 > max_images 시 사용자 확인 (`--yes` 없으면 input() 또는 stderr 경고 후 stop)
    - `generate_image(client, prompt_text, output_path, max_retries=3)`: 5D 평가 루프 (Gemini 라인 147-212 미러링)
      - prompt에 SYSTEM_INSTRUCTION을 prepend (`combined_prompt = SYSTEM_INSTRUCTION + "\n\n" + prompt_text`)
      - `client.images.generate(model=IMAGE_MODEL, prompt=combined_prompt, size=IMAGE_SIZE, quality=IMAGE_QUALITY, output_format=OUTPUT_FORMAT, n=1)`
      - response.data[0].b64_json → base64.b64decode → 저장 (JPEG 직접 저장, 비-JPEG 시 PIL 변환)
      - 평가 호출 → PASS 시 종료, FAIL 시 `[품질 보정 힌트] {feedback}`을 prompt 끝에 추가하여 재시도 (최대 MAX_QUALITY_RETRIES)
      - API 에러 시 `time.sleep(API_RETRY_DELAY)` 후 재시도 (최대 API_RETRY_COUNT)
    - `evaluate_image_quality(client, image_path, prompt_text="")`:
      - image를 base64 인코딩
      - `client.responses.create(model=EVAL_MODEL, input=[{"role":"user","content":[{"type":"input_text","text":eval_prompt},{"type":"input_image","image_url":f"data:image/jpeg;base64,{data}","detail":"original"}]}], text={"format": EVALUATION_SCHEMA})`
      - response.output_text → json.loads → dict 반환
      - **Concept theme 처리**: prompt_text에 "concept" / "zero text rendering" / "zero-text rendering" 포함 시 (Gemini 동일 string match) → korean_text_readability=10.0, korean_hallucination_detection=10.0 자동 설정
      - refusal 필드 검사 (있으면 prompt 수정 후 재시도, max 1회)
  - **에러 처리**:
    - OPENAI_API_KEY 미설정 → 한국어 메시지 + exit 1 (Gemini 라인 56-59 패턴 미러링)
    - 403 (Org 미검증) → 검증 페이지 URL 안내 + exit 1
    - 429 (rate limit) → 5s/15s/45s exponential backoff
    - 400 (content policy) → generation_report에 사유 기록, 다음 prompt 진행
  - **출력 패턴** (Gemini와 동일):
    - `[OK] Saved: {path}`
    - `[FAIL] {prompt_name}: {reason}`
    - `[SKIP] Already exists: {path}`
    - `[품질 평가] 시도 N/M: 평균 X.X (한글:Y, 환각:Y, 정확도:Y, 레이아웃:Y, 색상:Y) → 통과/재시도`
  - exit code: 0 (모두 성공) / 1 (1개 이상 실패)

  **Must NOT do**:
  - 기존 `generate_slide_images.py` 한 글자도 수정 (보호 파일)
  - 5D schema 필드명 변경 (Gemini와 어긋나면 cross-renderer 비교 깨짐)
  - 임계값 변경 (7.0/5.0)
  - Concept theme 감지 로직 "개선" — string match 그대로 (false positive 포함)
  - SYSTEM_INSTRUCTION 변경 또는 일부 생략
  - `images.edit`, `images.create_variation` 사용
  - DALL-E, gpt-image-1/1.5/mini fallback 추가
  - Streaming 응답
  - `from openai import AzureOpenAI` 등 다른 SDK
  - silent fallback (OpenAI 실패 시 Gemini 호출 등 절대 금지)
  - print debug, console.log, 주석 처리된 코드
  - 일반적인 변수명 (data/result/temp) — 명확한 이름 사용 (response, image_bytes, evaluation)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 250-350줄 Python 스크립트, API 통합 + 에러 처리 + 평가 로직 + Gemini 패턴 정밀 미러링 (Gemini 스크립트와 라인별 대응 검증 필요)
  - **Skills**: 없음 (`[]`)
  - **Skills Evaluated but Omitted**:
    - `playwright`: 브라우저 무관

  **Parallelization**:
  - **Can Run In Parallel**: YES (Tasks 6, 7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8 (marketplace agents 배열 갱신 시 신규 파일 경로 필요), Task 12 (회귀 검증), Task 15 (smoke test)
  - **Blocked By**: Task 1 (모델명), Task 3 (rubric 정의)

  **References**:

  **Pattern References (CRITICAL — 라인별 미러링 필요)**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 17-35 — Imports + 상수 (구조 그대로)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 36-51 — SYSTEM_INSTRUCTION (텍스트 그대로 복사)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 56-59 — API key check 패턴 (한국어 메시지 형식)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 77-219 — generate_image() 5D 루프 구조 (논리 미러링)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 116-134 — JPEG 저장 로직 (PIL 사용 패턴)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 238-346 — evaluate_image_quality() (점수 계산 로직)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 349-437 — process_prompts() 메인 루프 (정규식 `^\d+_` + 제외 목록 그대로)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` 라인 440-466 — argparse main()

  **API/Type References**:
  - `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md` — 5D schema 정의 (Task 3 출력)
  - `.sisyphus/evidence/task-1-model-verification.json` — 검증된 모델명

  **External References**:
  - OpenAI Image API: `https://platform.openai.com/docs/guides/image-generation` — gpt-image-2 호출 + parameters
  - OpenAI Responses API: `https://platform.openai.com/docs/guides/structured-outputs` — json_schema strict
  - openai SDK changelog: `https://github.com/openai/openai-python/releases` — 1.0+ breaking changes

  **WHY Each Reference Matters**:
  - Gemini 스크립트는 Korean 환각 방지의 검증된 reference — 모든 패턴(파일 필터, retry, JPEG 저장, 5D 루프)을 미러링하여 cross-renderer 일관성 확보
  - SYSTEM_INSTRUCTION이 Gemini 라인 36-51에 정의되어 있고 Korean Typography/Negative Constraints 등 16줄 텍스트가 검증된 anti-hallucination이므로 그대로 복사
  - process_prompts의 파일 필터 정규식 `^\d+_`을 다르게 (예: `^[0-9]+_`) 작성하면 동작은 같아도 코드 리뷰 시 의심 발생

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Python syntax + 핵심 패턴 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 스크립트 작성됨
    Steps:
      1. python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py', encoding='utf-8').read()); print('SYNTAX_OK')" > .sisyphus/evidence/task-5-syntax.txt 2>&1
      2. python -c "
content = open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py', encoding='utf-8').read()
required = ['gpt-image-2', '1536x1024', 'quality=\"high\"', 'OPENAI_API_KEY', 'max-images', 'QUALITY_THRESHOLD = 7.0', 'KOREAN_MIN_THRESHOLD = 5.0', 'SYSTEM_INSTRUCTION', 'json_schema', 'detail', 'input_image', 'korean_text_readability', 'korean_hallucination_detection']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
print('ALL_KEYWORDS_FOUND')
" > .sisyphus/evidence/task-5-keywords.txt 2>&1
      3. python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --help > .sisyphus/evidence/task-5-help.txt 2>&1
      4. python -c "
help_text = open('.sisyphus/evidence/task-5-help.txt', encoding='utf-8').read()
required_args = ['prompts-dir', 'output-dir', 'max-images']
missing = [a for a in required_args if a not in help_text]
assert not missing, f'CLI_ARGS_MISSING: {missing}'
print('CLI_ARGS_OK')
" > .sisyphus/evidence/task-5-cli-check.txt 2>&1
    Expected Result: 모두 exit 0, SYNTAX_OK / ALL_KEYWORDS_FOUND / CLI_ARGS_OK 출력
    Failure Indicators: SyntaxError, 키워드 누락 → 핵심 설정 빠짐
    Evidence: .sisyphus/evidence/task-5-syntax.txt, task-5-keywords.txt, task-5-help.txt, task-5-cli-check.txt

  Scenario: OPENAI_API_KEY 미설정 hard-fail 검증
    Tool: PowerShell + Python
    Preconditions: prompts-dir에 임시 디렉토리 생성, OPENAI_API_KEY 임시 unset
    Steps:
      1. New-Item -ItemType Directory -Path .sisyphus/evidence/task-5-empty-prompts -Force | Out-Null
      2. $saved = $env:OPENAI_API_KEY; $env:OPENAI_API_KEY = ""; $output = python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --prompts-dir .sisyphus/evidence/task-5-empty-prompts --output-dir .sisyphus/evidence/task-5-out 2>&1; $exitCode = $LASTEXITCODE; $output | Out-File -FilePath .sisyphus/evidence/task-5-no-key.txt -Encoding utf8; $exitCode | Out-File -FilePath .sisyphus/evidence/task-5-no-key-exit.txt; $env:OPENAI_API_KEY = $saved
      3. python -c "
content = open('.sisyphus/evidence/task-5-no-key.txt', encoding='utf-8').read().lower()
exit_code = int(open('.sisyphus/evidence/task-5-no-key-exit.txt').read().strip())
assert 'openai_api_key' in content, f'key name not in error message: {content[:200]}'
assert exit_code == 1, f'expected exit 1, got {exit_code} (silent fallback violation)'
print('HARD_FAIL_OK')
"
    Expected Result: HARD_FAIL_OK 출력 (stderr/stdout에 OPENAI_API_KEY 언급, exit code 1)
    Failure Indicators: 다른 에러 또는 exit 0 (silent fallback) → hard-fail 정책 위반
    Evidence: .sisyphus/evidence/task-5-no-key.txt, task-5-no-key-exit.txt

  Scenario: 보호 파일 (Gemini 스크립트) byte-identical 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 스크립트 작성됨
    Steps:
      1. git diff HEAD -- plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py > .sisyphus/evidence/task-5-gemini-untouched.txt
      2. python -c "
content = open('.sisyphus/evidence/task-5-gemini-untouched.txt', encoding='utf-8').read()
assert not content.strip(), f'PROTECTED FILE MODIFIED: {content[:200]}'
print('PROTECTED_FILE_UNTOUCHED')
"
    Expected Result: PROTECTED_FILE_UNTOUCHED 출력 (diff 비어있음)
    Failure Indicators: Cross-task contamination → 즉시 revert
    Evidence: .sisyphus/evidence/task-5-gemini-untouched.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-5-syntax.txt`
  - [ ] `.sisyphus/evidence/task-5-keywords.txt`
  - [ ] `.sisyphus/evidence/task-5-help.txt`
  - [ ] `.sisyphus/evidence/task-5-no-key.txt`
  - [ ] `.sisyphus/evidence/task-5-gemini-untouched.txt`

  **Commit**: NO (Wave 2 합본 `feat(visual-generator): add gpt-image-2 renderer agent and script`)

- [x] 6. **`renderer-agent-openai.md` 신규 에이전트 작성**

  **What to do**:
  - 신규 파일: `plugins/visual-generator/agents/renderer-agent-openai.md`
  - frontmatter:
    ```yaml
    ---
    name: renderer-agent-openai
    description: "최종 4-block 프롬프트 검증 및 OpenAI gpt-image-2 기반 이미지 렌더링"
    tools: Read, Glob, Grep, Write, Bash
    model: sonnet
    ---
    ```
  - **구조 미러링** (기존 `renderer-agent.md`와 1:1 대응):
    - Overview: gpt-image-2 사용 명시, 최종 단계, prompt-designer → [renderer-agent-openai] 위치
    - Workflow Position: After prompt-designer, Before none, Enables 최종 이미지
    - Key Distinctions vs prompt-designer/content-reviewer/content-organizer (동일)
    - Input Schema: prompts_path (필수), output_path (필수), auto_mode (기본 true), max_images (기본 30)
    - Workflow Phase 0-5 (Gemini 에이전트와 동일 구조):
      - Phase 0: 출력 디렉토리 생성 (mkdir -p)
      - Phase 1: 프롬프트 파일 수집 (Glob `^\d+_*.md`, 메타 파일 제외)
      - **Phase 2: 최종 검증** — **renderer-agent.md의 16-item 체크리스트를 참조** (중복 금지). "Phase 2 검증 항목은 `renderer-agent.md`의 Validation Checklist 16항목과 동일하게 적용한다 (cross-reference, no duplication)"라고 명시 + 표 헤더만 복사 + 본문은 "→ See `agents/renderer-agent.md` 라인 158-177"
      - Phase 3: 이미지 렌더링
        - Step 3-1: OPENAI_API_KEY 환경변수 확인 (미설정 시 즉시 중단)
        - Step 3-2: 렌더링 스크립트 찾기 (상대경로 `scripts/generate_slide_images_openai.py` → Glob 폴백 `**/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` → 광역 Glob `**/generate_slide_images_openai.py`)
        - Step 3-3: 실행 `python {경로} --prompts-dir {prompts_path} --output-dir {output_path} --max-images {max_images} --yes` (auto_mode=true 시 --yes 자동 추가)
        - Step 3-4: 출력 모니터링 ([OK]/[FAIL]/[SKIP]/품질 평가 패턴)
      - Phase 4: 에러 처리 + 재시도 (Gemini 에이전트와 동일, 5초 간격 최대 3회)
      - Phase 5: generation_report.md 작성
        - 사용 모델: `gpt-image-2`
        - 평가 모델: `{Task 1 검증된 모델}`
        - 출력 사양: 1536x1024 quality=high JPEG
        - 비용 추정 (총 prompts 수 × $0.165 + 평가 비용)
    - Script & Error Handling 섹션 (Gemini 에이전트와 동일 구조):
      - 스크립트 경로 확보 패턴 3단계 폴백
      - 자체 Python 코드 작성 절대 금지 명시
      - 핵심 설정 표: openai>=1.0 / gpt-image-2 / 1536x1024 / quality=high / OUTPUT_FORMAT=jpeg
    - Output Structure (`{output_path}/01_*.jpg` + generation_report.md)
    - generation_report.md 형식 — 사용 모델 필드만 변경, 나머지 동일
    - MUST DO: 4-block 검증, OPENAI_API_KEY 확인, API 타임아웃 시 3회 재시도, 보고서 작성, 신규 스크립트 사용
    - MUST NOT DO: 검증 실패 프롬프트 수정 금지, $CLAUDE_PLUGIN_ROOT 변수 미사용, 자체 Python 코드 작성 금지, 환경변수 미설정 상태 실행 금지, 기존 이미지 덮어쓰기 금지
    - Usage Examples: 기본 사용 + 오케스트레이터 호출 (Task) + 특정 프롬프트 재렌더링

  **Must NOT do**:
  - 기존 `renderer-agent.md` 한 글자도 수정
  - 16-item 검증 체크리스트 본문 복제 (참조만)
  - GEMINI_API_KEY 언급 (이 에이전트는 OpenAI 전용)
  - "improve" 또는 "fix" 표현으로 기존 검증 항목 누락(#9, #10, #11) 수정 시도

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 350+ 줄 마크다운 에이전트 스펙, Gemini 에이전트와 정밀 패턴 미러링 + 차이 부분 명확 표시
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES (Tasks 5, 7과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8 (marketplace agents 배열에 추가), Task 12 (회귀), Task 15 (smoke test)
  - **Blocked By**: Task 1 (모델명), Task 3 (rubric)

  **References**:

  **Pattern References (CRITICAL)**:
  - `plugins/visual-generator/agents/renderer-agent.md` 전체 — Phase 0-5 구조, MUST DO/MUST NOT DO 형식, frontmatter 패턴 (1:1 미러링)
  - `plugins/visual-generator/agents/renderer-agent.md` 라인 158-177 — 16-item 체크리스트 (참조 대상, 복제 금지)

  **External References**:
  - `AGENTS.md` "SCRIPT PATH RESOLUTION (MANDATORY)" 섹션 — 3단계 경로 탐색 패턴

  **WHY Each Reference Matters**:
  - 두 렌더러 에이전트가 구조적으로 동일해야 사용자가 두 경로를 직관적으로 비교 가능
  - 16-item 체크리스트 단일 출처 유지 → 향후 검증 항목 추가 시 한 곳만 수정

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: frontmatter + 필수 섹션 존재 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 에이전트 작성됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/agents/renderer-agent-openai.md', encoding='utf-8').read()
required_sections = ['name: renderer-agent-openai', 'tools: Read, Glob, Grep, Write, Bash', '## Overview', '## Workflow', 'Phase 0:', 'Phase 1:', 'Phase 2:', 'Phase 3:', 'Phase 4:', 'Phase 5:', '## Script & Error Handling', '## MUST DO', '## MUST NOT DO', '## Usage Examples']
missing = [s for s in required_sections if s not in content]
assert not missing, f'MISSING_SECTIONS: {missing}'
print('ALL_SECTIONS_PRESENT')
" > .sisyphus/evidence/task-6-sections.txt 2>&1
    Expected Result: ALL_SECTIONS_PRESENT
    Evidence: .sisyphus/evidence/task-6-sections.txt

  Scenario: 16-item 체크리스트 참조 (중복 금지)
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 에이전트 작성됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/agents/renderer-agent-openai.md', encoding='utf-8').read()
has_cross_ref = ('renderer-agent.md' in content) or ('See.*renderer-agent' in content)
assert has_cross_ref, 'no cross-reference to renderer-agent.md'
table_header_count = content.count('| 검증 방법 |')
assert table_header_count <= 1, f'16-item table duplicated ({table_header_count} table headers found, should be 0 or 1 with reference comment)'
print(f'CROSS_REF_OK (table_headers: {table_header_count})')
" > .sisyphus/evidence/task-6-cross-ref.txt 2>&1
    Expected Result: CROSS_REF_OK
    Failure Indicators: 16개 검증 항목 본문 복제 → 향후 drift 위험
    Evidence: .sisyphus/evidence/task-6-cross-ref.txt

  Scenario: OpenAI 전용 키워드 + Gemini 키워드 부재
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 에이전트 작성됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/agents/renderer-agent-openai.md', encoding='utf-8').read()
required_openai = ['OPENAI_API_KEY', 'gpt-image-2', 'generate_slide_images_openai.py', 'max-images']
missing_openai = [k for k in required_openai if k not in content]
assert not missing_openai, f'OPENAI_KEYWORDS_MISSING: {missing_openai}'
forbidden_gemini = ['GEMINI_API_KEY', 'google-genai']
present_gemini = [k for k in forbidden_gemini if k in content]
assert not present_gemini, f'GEMINI_KEYWORDS_FOUND_IN_OPENAI_AGENT: {present_gemini}'
print('OPENAI_ONLY_OK')
" > .sisyphus/evidence/task-6-openai-kw.txt 2>&1
    Expected Result: OPENAI_ONLY_OK
    Evidence: .sisyphus/evidence/task-6-openai-kw.txt

  Scenario: 보호 파일 (renderer-agent.md) byte-identical
    Tool: Bash (PowerShell + Python)
    Preconditions: 신규 에이전트 작성됨
    Steps:
      1. git diff HEAD -- plugins/visual-generator/agents/renderer-agent.md > .sisyphus/evidence/task-6-renderer-untouched.txt
      2. python -c "
content = open('.sisyphus/evidence/task-6-renderer-untouched.txt', encoding='utf-8').read()
assert not content.strip(), f'PROTECTED FILE MODIFIED: {content[:200]}'
print('PROTECTED_FILE_UNTOUCHED')
"
    Expected Result: PROTECTED_FILE_UNTOUCHED (diff 비어있음)
    Evidence: .sisyphus/evidence/task-6-renderer-untouched.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-6-sections.txt`
  - [ ] `.sisyphus/evidence/task-6-cross-ref.txt`
  - [ ] `.sisyphus/evidence/task-6-openai-kw.txt`
  - [ ] `.sisyphus/evidence/task-6-renderer-untouched.txt`

  **Commit**: NO (Wave 2 합본)

- [x] 7. **`visual-generate.md` 오케스트레이터 수정 (renderer 파라미터 + 분기)**

  **What to do**:
  - 파일: `plugins/visual-generator/commands/visual-generate.md`
  - **Input Schema 표 갱신** (라인 14-22 인접):
    - 신규 행 1: `renderer` — 렌더링 엔진 선택 (`gemini`, `openai`) — 필수 X — 기본 `gemini`
    - 신규 행 2: `renderer_choice_timing` — 렌더러 선택 시점 (`pre`, `post`, `none`) — 필수 X — **기본 `none`** (Metis 권고: 백워드 호환)
    - 신규 행 3: `max_images` — OpenAI 경로 비용 cap (정수) — 필수 X — 기본 30
  - **Phase 0.5 신규 추가** (Phase 0 직후, Phase 1 전):
    - 조건: `renderer_choice_timing == "pre"` AND `renderer` 미지정
    - 동작: 사용자에게 Question 도구로 선택 받기 ("Gemini" 또는 "OpenAI gpt-image-2 (가장 좋은 품질)")
    - `auto_mode == true` AND 위 조건 → 자동 해결: `renderer = "gemini"` (기본값) + 경고 로그
  - **Phase 3.5 신규 추가** (Phase 3 직후, Phase 4 전):
    - 조건: `renderer_choice_timing == "post"` AND `renderer` 미지정
    - 동작: 프롬프트 폴더 경로 + 프롬프트 수 표시 → Question 도구로 선택 받기
    - `auto_mode == true` AND 위 조건 → 자동 해결: `renderer = "gemini"` + 경고 로그
  - **Phase 4 분기 로직 추가** (라인 111-129):
    - `renderer == "gemini"` → 기존 동작 유지 — `Task(subagent_type="visual-generator:renderer-agent")`
    - `renderer == "openai"` → 신규 — `Task(subagent_type="visual-generator:renderer-agent-openai")`, max_images 전달
    - 잘못된 renderer 값 → 즉시 중단 + 한국어 에러
  - **Sub-Agent References 표 갱신** (라인 239-244): renderer-agent-openai 행 추가
  - **MUST DO 추가**: renderer 값 검증, OPENAI_API_KEY 확인 (renderer="openai" 시), max_images cost 사전 안내
  - **MUST NOT DO 추가**: silent fallback (OpenAI → Gemini 자동 전환 금지), renderer_choice_timing 기본값을 pre/post로 변경 금지 (백워드 호환), 단일 명령에서 두 렌더러 동시 실행 금지

  **Must NOT do**:
  - 기존 Phase 1-5 본문 수정 (Phase 4 안에서 분기 추가만)
  - auto_mode 동작 표 (라인 153-160) 기존 행 변경 — 새 행만 추가 (renderer 관련)
  - Output Structure (라인 213-235) 변경
  - 체크포인트 형식 변경
  - `renderer="both"` 관련 어떤 언급도 추가 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 약 50줄 추가/수정 + 기존 324줄 보존 정밀도, 표 갱신 + 새 Phase 추가 + 분기 로직 + auto_mode 호환
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES (Tasks 5, 6과 동시)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 12 (회귀 검증), Task 15 (smoke test)
  - **Blocked By**: Task 1 (renderer 값 매핑 — `openai` 외 다른 명칭 변경 가능성 차단)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/commands/visual-generate.md` 라인 14-22 — Input Schema 표 형식
  - `plugins/visual-generator/commands/visual-generate.md` 라인 37-150 — Workflow ASCII 트리 패턴
  - `plugins/visual-generator/commands/visual-generate.md` 라인 153-173 — auto_mode + Error Handling 표
  - `plugins/visual-generator/commands/visual-generate.md` 라인 239-244 — Sub-Agent References 패턴

  **WHY Each Reference Matters**:
  - 기존 표/트리 형식과 정확히 일치해야 사용자 학습 일관성
  - auto_mode 처리 명세는 백워드 호환의 핵심 — 표에 신규 동작 명시

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 신규 파라미터 + Phase + 분기 모두 존재
    Tool: Bash (PowerShell + Python)
    Preconditions: visual-generate.md 수정됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
required = ['renderer', 'renderer_choice_timing', 'max_images', 'Phase 0.5', 'Phase 3.5', 'renderer-agent-openai', 'OPENAI_API_KEY']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
# 분기 로직 검증 (정확한 quote escaping은 작성 방식에 따라 다양 — 하나라도 매칭하면 OK)
branching_patterns = ['renderer == \"openai\"', \"renderer == 'openai'\", 'renderer=openai', 'renderer: openai']
has_branching = any(p in content for p in branching_patterns)
assert has_branching, f'no branching logic found (any of: {branching_patterns})'
print('PARAMS_AND_BRANCHING_OK')
" > .sisyphus/evidence/task-7-keywords.txt 2>&1
    Expected Result: PARAMS_AND_BRANCHING_OK
    Evidence: .sisyphus/evidence/task-7-keywords.txt

  Scenario: 백워드 호환 — 기본값 정확성 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. python -c "
import re
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
# renderer_choice_timing 기본값이 'none'으로 명시되어 있는지
timing_default_patterns = [r'renderer_choice_timing[^\n]{0,100}기본[^\n]{0,30}none', r'기본값[^\n]{0,30}none[^\n]{0,100}renderer_choice_timing', r'백워드 호환', r'backward.compat']
timing_doc = any(re.search(p, content, re.IGNORECASE) for p in timing_default_patterns)
assert timing_doc, 'renderer_choice_timing default=none not documented'
# renderer 기본값이 'gemini'로 명시되어 있는지
renderer_default_patterns = [r'renderer[^\n]{0,100}기본[^\n]{0,30}gemini', r'기본값[^\n]{0,30}gemini[^\n]{0,100}renderer']
renderer_doc = any(re.search(p, content, re.IGNORECASE) for p in renderer_default_patterns)
assert renderer_doc, 'renderer default=gemini not documented'
print('DEFAULTS_DOCUMENTED')
" > .sisyphus/evidence/task-7-default-none.txt 2>&1
    Expected Result: DEFAULTS_DOCUMENTED
    Failure Indicators: 기본값 문서화 누락 → 사용자 혼란
    Evidence: .sisyphus/evidence/task-7-default-none.txt

  Scenario: silent fallback 금지 명시
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. python -c "
import re
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
patterns = [r'silent fallback', r'자동 전환 금지', r'hard.?fail', r'즉시 중단']
matches = [p for p in patterns if re.search(p, content, re.IGNORECASE)]
assert matches, f'hard-fail policy not documented (none of: {patterns})'
print(f'HARD_FAIL_DOCUMENTED: {matches}')
" > .sisyphus/evidence/task-7-no-fallback.txt 2>&1
    Expected Result: HARD_FAIL_DOCUMENTED
    Evidence: .sisyphus/evidence/task-7-no-fallback.txt

  Scenario: 기존 Phase 1-5 본문 보존 (회귀)
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
required_phases = ['Phase 1: 문서 분석', 'Phase 2: 콘텐츠 검토', 'Phase 3: 프롬프트 생성', 'Phase 4: 이미지 렌더링', 'Phase 5: 최종 보고서 생성']
missing = [p for p in required_phases if p not in content]
assert not missing, f'PHASES_REMOVED: {missing}'
print('ALL_PHASES_PRESERVED')
" > .sisyphus/evidence/task-7-phases-preserved.txt 2>&1
    Expected Result: ALL_PHASES_PRESERVED
    Evidence: .sisyphus/evidence/task-7-phases-preserved.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-7-keywords.txt`
  - [ ] `.sisyphus/evidence/task-7-default-none.txt`
  - [ ] `.sisyphus/evidence/task-7-no-fallback.txt`
  - [ ] `.sisyphus/evidence/task-7-phases-preserved.txt`

  **Commit**: NO (Wave 2 합본)

- [x] 8. **`marketplace.json` visual-generator entry 갱신 (version + agents 배열)**

  **What to do**:
  - 파일: `.claude-plugin/marketplace.json` (root)
  - visual-generator 플러그인 entry 찾기 (`name == "visual-generator"`)
  - **변경 1**: `version` 필드 `"3.4.0"` → `"3.5.0"` (plugin entry 내)
  - **변경 2**: `agents` 배열에 `"./agents/renderer-agent-openai.md"` 추가 (기존 5개 에이전트 보존)
  - 다른 visual-generator 필드 (`description`, `source`, `strict`, `skills`, `commands`, `category`, `tags` 등) 절대 변경 금지
  - 다른 플러그인 entry는 한 글자도 수정 금지

  **Must NOT do**:
  - metadata.version (root 레벨) 변경 — 이는 Task 9에서 처리
  - 다른 플러그인 (isd-generator, hwpx-generator 등) entry 변경
  - 신규 필드 추가 (스키마 위반)
  - JSON 포맷팅 변경 (들여쓰기, 키 순서 등)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: JSON 파일 2곳 정밀 변경 + 스키마 검증
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: NO with Task 6 (신규 에이전트 파일 경로 의존)
  - **Parallel Group**: Wave 2 (Tasks 5, 7과 동시 가능, Task 6 완료 후 시작)
  - **Blocks**: Task 9 (marketplace metadata도 같은 파일), Task 13 (cross-contamination), Task 14 (버전 동기화)
  - **Blocked By**: Task 6 (신규 파일 경로 확정)

  **References**:

  **Pattern References**:
  - `.claude-plugin/marketplace.json` — 현재 visual-generator entry 구조
  - `AGENTS.md` "Plugin.json Schema Compliance (CRITICAL)" — 허용 필드 화이트리스트 + 검증 명령
  - `AGENTS.md` "CRITICAL: Agent/Skill/Command File Changes Checklist" — agents 배열 갱신 의무

  **WHY Each Reference Matters**:
  - 2026-04-21 사례: `contributors` 같은 비표준 필드로 등록 실패 — 화이트리스트만 사용
  - agents 배열에 신규 파일 추가하지 않으면 Claude가 새 에이전트를 인식하지 못함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: visual-generator entry 갱신 + 스키마 검증
    Tool: Bash
    Preconditions: marketplace.json 수정됨
    Steps:
      1. python -c "import json; mp=json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); vg=next(p for p in mp['plugins'] if p['name']=='visual-generator'); assert vg['version']=='3.5.0', f'expected 3.5.0, got {vg[\"version\"]}'; assert './agents/renderer-agent-openai.md' in vg.get('agents', []), f'new agent missing in {vg.get(\"agents\")}'" > .sisyphus/evidence/task-8-entry.txt 2>&1
      2. python -c "import json; mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8')); M = {'name','source','description','strict','agents','skills','version','author','license','category','homepage','keywords','tags','commands','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies','repository'}; vg = next(p for p in mp['plugins'] if p['name'] == 'visual-generator'); extra = set(vg.keys()) - M; assert not extra, f'INVALID FIELDS: {extra}'" >> .sisyphus/evidence/task-8-entry.txt 2>&1
    Expected Result: 두 명령 모두 exit 0
    Failure Indicators: AssertionError → 버전 미반영 / 에이전트 누락 / 스키마 위반
    Evidence: .sisyphus/evidence/task-8-entry.txt

  Scenario: 다른 플러그인 entry 미변경 검증
    Tool: Bash
    Preconditions: git working tree에 marketplace.json 변경만 존재
    Steps:
      1. git diff .claude-plugin/marketplace.json > .sisyphus/evidence/task-8-diff.txt
      2. python -c "import json; diff=open('.sisyphus/evidence/task-8-diff.txt',encoding='utf-8').read(); other_plugins = ['isd-generator', 'hwpx-generator', 'report-generator', 'pptx-design-styles', 'wiki-gen', 'patent-trend-analyzer', 'paper-style-generator', 'investments-portfolio', 'stock-consultation', 'equity-research', 'macro-analysis', 'plugin-dev', 'worktree-workflow', 'general-agents', 'obsidian-skills', 'accelerated-learner', 'link-curator']; affected=[n for n in other_plugins if f'\"name\": \"{n}\"' in diff]; assert not affected, f'OTHER PLUGINS AFFECTED: {affected}'"
    Expected Result: visual-generator만 변경, 다른 17개 플러그인 entry 미변경
    Failure Indicators: cross-task contamination
    Evidence: .sisyphus/evidence/task-8-diff.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-8-entry.txt`
  - [ ] `.sisyphus/evidence/task-8-diff.txt`

  **Commit**: NO (Wave 2 합본)

- [x] 9. **`marketplace.json` metadata.version 갱신 (3.29.0 → 3.30.0)**

  **What to do**:
  - 파일: `.claude-plugin/marketplace.json`
  - root level `metadata.version` 필드 `"3.29.0"` → `"3.30.0"` 변경
  - 다른 metadata 필드 (name, description, author 등) 절대 변경 금지
  - plugins 배열 (Task 8에서 갱신됨) 변경 금지

  **Must NOT do**:
  - metadata 외 다른 root 필드 변경
  - plugin entry 다시 수정
  - SemVer MAJOR 변경 (3.x.x → 4.x.x 절대 금지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 1줄 변경
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 10, 11 (다른 파일들)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14 (버전 동기화 검증)
  - **Blocked By**: Task 8 (같은 파일이므로 시간차 적용)

  **References**:

  **Pattern References**:
  - `.claude-plugin/marketplace.json` — metadata.version 위치
  - `AGENTS.md` "Version Management & Registry Updates" — 마켓플레이스 MINOR 정책 (개별 플러그인 MINOR ≥ 변경 시 마켓플레이스 MINOR)

  **WHY Each Reference Matters**:
  - visual-generator MINOR 변경 (3.4.0→3.5.0) → 마켓플레이스도 MINOR (3.29.0→3.30.0)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: metadata.version 갱신 검증
    Tool: Bash
    Preconditions: marketplace.json 수정됨
    Steps:
      1. python -c "import json; mp=json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); v=mp.get('metadata',{}).get('version','MISSING'); assert v=='3.30.0', f'expected 3.30.0, got {v}'" > .sisyphus/evidence/task-9-metadata.txt 2>&1
    Expected Result: exit 0
    Evidence: .sisyphus/evidence/task-9-metadata.txt

  Scenario: visual-generator entry 보존 (Task 8 결과 유지)
    Tool: Bash
    Preconditions: 수정됨
    Steps:
      1. python -c "import json; mp=json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); vg=next(p for p in mp['plugins'] if p['name']=='visual-generator'); assert vg['version']=='3.5.0' and './agents/renderer-agent-openai.md' in vg.get('agents',[]), 'Task 8 changes regressed'"
    Expected Result: exit 0
    Failure Indicators: Task 8 변경 재훼손
    Evidence: (Task 9에서 위 검증 자체가 evidence)
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-9-metadata.txt`

  **Commit**: NO (Wave 3 합본 `docs(visual-generator): document OpenAI rendering path and bump versions`)

- [x] 10. **`README.md` 업데이트 (Version + 변경 이력 + visual-generator 섹션)**

  **What to do**:
  - 파일: `README.md` (root)
  - **변경 1**: 상단 Version 필드 `**Version**: 3.29.0` → `**Version**: 3.30.0`
  - **변경 2**: `## visual-generator` 섹션 갱신:
    - `> 입력 문서를 분석하여 6개 테마 시각자료 프롬프트를 생성하고 Gemini API로 렌더링합니다.` → `> ... Gemini 또는 OpenAI gpt-image-2로 렌더링합니다.` (또는 동등한 표현)
    - 사용법 예시에 `renderer: openai` 옵션 시연 추가
    - 파라미터 표에 `renderer`, `renderer_choice_timing`, `max_images` 행 추가
    - "에이전트 파이프라인" 다이어그램 갱신: `... → renderer-agent` → `... → renderer-agent | renderer-agent-openai (사용자 선택)`
    - "구성 요소" 섹션 (5 Agents → 6 Agents)
    - **비용 안내**: "OpenAI 경로 사용 시: gpt-image-2 high 1536x1024 ≈ $0.165/image + 평가 비용 ~$0.05/image. 기본 30장 cap (`max_images`로 조절)"
    - **사전 준비**: `OPENAI_API_KEY` 환경변수 설정 + `pip install openai>=1.0` 안내
  - **변경 3**: `## 변경 이력` 표 최상단 행 추가:
    - `| 3.30.0 | 2026-04-26 | visual-generator v3.5.0: OpenAI gpt-image-2 기반 렌더링 경로 추가 — `renderer` (gemini\|openai) + `renderer_choice_timing` (pre\|post\|none) 파라미터로 사용자 선택, 별도 에이전트 (renderer-agent-openai) + 별도 스크립트 (generate_slide_images_openai.py), 5D 평가 (Structured Outputs json_schema strict, 평가 모델 {Task 1 검증}), 1536x1024 quality=high JPEG 출력, --max-images 비용 cap (기본 30), OPENAI_API_KEY 미설정 hard-fail. 기존 Gemini 경로 byte-identical 보존 (백워드 호환). |`

  **Must NOT do**:
  - 다른 플러그인 섹션 변경
  - 변경 이력 기존 행 수정 또는 삭제
  - 프로젝트 구조 트리 (visual-generator agents 5→6 외의) 변경
  - Author/License/링크 변경
  - 시각적 갤러리 (theme-examples) 변경
  - 기존 visual-generator 사용 예시 삭제 (추가만)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 한국어 문서 작성 + 표/다이어그램 정밀 갱신
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 9, 11 (다른 파일들)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14 (버전 동기화 검증)
  - **Blocked By**: Tasks 5, 6, 7 (구현 완료 후 정확한 동작 문서화)

  **References**:

  **Pattern References**:
  - `README.md` 라인 1-10 — Version 위치
  - `README.md` "## visual-generator" 섹션 — 기존 구조
  - `README.md` "## 변경 이력" 표 — 행 형식 (날짜, 버전, 변경 내용)
  - `AGENTS.md` "MANDATORY: README.md 최신화" — 업데이트 트리거 + 원칙

  **WHY Each Reference Matters**:
  - 변경 이력의 일관된 형식 — 사용자가 변경사항 추적 가능
  - "MANDATORY" 섹션 명시: 플러그인 워크플로우 변경 → README.md 업데이트 필수

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Version + 변경 이력 + visual-generator 섹션 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: README.md 수정됨
    Steps:
      1. python -c "
import re
content = open('README.md', encoding='utf-8').read()

# 1. Version 3.30.0
version_match = re.search(r'\*\*Version\*\*\s*:\s*3\.30\.0', content)
assert version_match, 'FAIL: Version not 3.30.0'
open('.sisyphus/evidence/task-10-version.txt', 'w', encoding='utf-8').write('VERSION_OK\n')

# 2. 변경 이력 표에 3.30.0 행 (2026-04 또는 그 이후)
changelog_match = re.search(r'\|\s*3\.30\.0\s*\|\s*2026-0[4-9]', content)
assert changelog_match, 'FAIL: changelog row 3.30.0 missing or wrong date'
open('.sisyphus/evidence/task-10-changelog.txt', 'w', encoding='utf-8').write('CHANGELOG_ROW_OK\n')

# 3. OpenAI 언급 (≥1)
openai_mentions = re.findall(r'renderer[^\n]{0,50}openai|gpt-image-2|OpenAI gpt-image', content, re.IGNORECASE)
assert openai_mentions, 'FAIL: no OpenAI mention in README'
open('.sisyphus/evidence/task-10-openai-mention.txt', 'w', encoding='utf-8').write(f'OPENAI_MENTIONS_OK: {len(openai_mentions)} found\n')

print('README_UPDATES_OK')
" > .sisyphus/evidence/task-10-master.txt 2>&1
    Expected Result: README_UPDATES_OK
    Evidence: .sisyphus/evidence/task-10-{version,changelog,openai-mention}.txt + master.txt

  Scenario: 다른 플러그인 섹션 미변경 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. git diff README.md > .sisyphus/evidence/task-10-full-diff.txt
      2. python -c "
import re
diff_content = open('.sisyphus/evidence/task-10-full-diff.txt', encoding='utf-8').read()
other_plugins = ['isd-generator', 'hwpx-generator', 'report-generator', 'pptx-design-styles', 'wiki-gen', 'patent-trend-analyzer', 'paper-style-generator', 'investments-portfolio', 'stock-consultation', 'equity-research', 'macro-analysis', 'plugin-dev', 'worktree-workflow', 'general-agents', 'obsidian-skills', 'accelerated-learner', 'link-curator']
# diff에서 + 또는 - 로 시작하는 ## 섹션 헤더 추출
section_changes = re.findall(r'^[+-]## (\w[\w-]+)', diff_content, re.MULTILINE)
# diff metadata (+++/---) 제외
section_changes = [s for s in section_changes if s != '##']
affected = [s for s in section_changes if s in other_plugins]
assert not affected, f'OTHER PLUGIN SECTIONS MODIFIED: {affected}'
print('OTHER_PLUGINS_PRESERVED')
" > .sisyphus/evidence/task-10-others.txt 2>&1
    Expected Result: OTHER_PLUGINS_PRESERVED
    Evidence: .sisyphus/evidence/task-10-full-diff.txt, task-10-others.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-10-version.txt`
  - [ ] `.sisyphus/evidence/task-10-changelog.txt`
  - [ ] `.sisyphus/evidence/task-10-openai-mention.txt`
  - [ ] `.sisyphus/evidence/task-10-others.txt`

  **Commit**: NO (Wave 3 합본)

- [x] 11. **`AGENTS.md` 업데이트 (Version + Generated + WHERE TO LOOK + COMMANDS + ANTI-PATTERNS)**

  **What to do**:
  - 파일: `AGENTS.md` (root)
  - **변경 1**: 상단 Version 필드 `**Version**: 3.29.0` → `**Version**: 3.30.0`
  - **변경 2**: 상단 `**Generated**` 날짜를 현재 날짜 (`2026-04-26`)로 갱신
  - **변경 3**: `## WHERE TO LOOK` 표에 새 행 추가 (visual-generator 섹션 인근):
    - `| OpenAI gpt-image-2 렌더링 | `plugins/visual-generator/agents/renderer-agent-openai.md` | 별도 에이전트 + 신규 스크립트, OPENAI_API_KEY 필요 |`
    - `| OpenAI 렌더링 스크립트 | `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` | gpt-image-2 + Structured Outputs 평가 |`
    - `| OpenAI 평가 rubric | `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md` | 5D 평가 schema (Gemini와 호환) |`
  - **변경 4**: `## COMMANDS` 섹션에 신규 명령 추가:
    ```bash
    # OpenAI gpt-image-2 기반 슬라이드 이미지 생성
    python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py \
      --prompts-dir [path] --output-dir [path] [--max-images 30] [--yes]
    ```
  - **변경 5**: `## ANTI-PATTERNS (THIS PROJECT)` 표에 새 행 추가 (**현재 표는 2컬럼: `Forbidden | Reason`**, AGENTS.md 라인 220-227 참조):
    - `| Modifying Gemini path while building OpenAI path | Cross-task contamination, Gemini 회귀 위험 (보호 파일 allowlist 준수 필수) |`
    - `| OpenAI 실패 시 silent Gemini fallback | 사용자 의도 위반, 명시적 OpenAI 선택을 무시함 (반드시 hard-fail with 한국어 에러) |`

  **Must NOT do**:
  - 기존 WHERE TO LOOK 행 수정 (추가만)
  - 기존 COMMANDS 명령 수정
  - 기존 ANTI-PATTERNS 행 수정
  - SCRIPT PATH RESOLUTION, MARKETPLACE RULES 등 다른 섹션 변경
  - 다른 플러그인 관련 정보 갱신

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 한국어 기술 문서, 5개 섹션 정밀 갱신
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 9, 10
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14 (버전 동기화)
  - **Blocked By**: Tasks 2, 4, 5, 6, 7 (구현 완료 후 정확한 경로/명령 문서화)

  **References**:

  **Pattern References**:
  - `AGENTS.md` 상단 — Version, Generated, Branch 헤더 형식
  - `AGENTS.md` "WHERE TO LOOK" 표 — 행 형식
  - `AGENTS.md` "COMMANDS" 섹션 — bash 코드블록 패턴
  - `AGENTS.md` "ANTI-PATTERNS" 표 라인 220-227 — **2컬럼 형식 (`Forbidden | Reason`)**. 3컬럼이 아님 — 새 행 추가 시 동일 형식 준수 (대안 정보는 Reason 컬럼에 괄호로 포함)
  - `AGENTS.md` "MANDATORY: AGENTS.md 최신화" — 업데이트 트리거 + 원칙

  **WHY Each Reference Matters**:
  - "MANDATORY" 규칙: 플러그인 추가/Agent 추가 → AGENTS.md 업데이트 필수, Generated 날짜 갱신 필수
  - 다른 에이전트가 다음 세션에서 OpenAI 경로 인식하려면 WHERE TO LOOK 갱신 필수

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 5개 변경 모두 적용 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: AGENTS.md 수정됨
    Steps:
      1. python -c "
import re
content = open('AGENTS.md', encoding='utf-8').read()

# 1. Version 3.30.0
version_patterns = [r'\*\*Version:?\*\*:?\s*3\.30\.0', r'\*\*Version\*\*\s*:?\s*3\.30\.0']
assert any(re.search(p, content) for p in version_patterns), 'FAIL: Version 3.30.0 not found'
open('.sisyphus/evidence/task-11-version.txt', 'w', encoding='utf-8').write('VERSION_OK\n')

# 2. Generated 날짜 (2026-04 또는 그 이후)
gen_match = re.search(r'\*\*Generated:?\*\*:?\s*(\d{4}-\d{2}-\d{2})', content)
assert gen_match and gen_match.group(1) >= '2026-04-26', f'FAIL: Generated date not updated: {gen_match.group(1) if gen_match else \"missing\"}'
open('.sisyphus/evidence/task-11-generated.txt', 'w', encoding='utf-8').write(f'GENERATED_OK: {gen_match.group(1)}\n')

# 3. WHERE TO LOOK 표에 신규 파일 3개 모두
new_files = ['renderer-agent-openai.md', 'generate_slide_images_openai.py', 'openai-quality-rubric.md']
missing_files = [f for f in new_files if f not in content]
assert not missing_files, f'WHERE_TO_LOOK_MISSING: {missing_files}'
open('.sisyphus/evidence/task-11-where-to-look.txt', 'w', encoding='utf-8').write(f'WHERE_TO_LOOK_OK: all 3 files referenced\n')

# 4. COMMANDS 섹션에 신규 스크립트 + CLI args
cmd_block = re.search(r'## COMMANDS.+?(?=\n## )', content, re.DOTALL)
assert cmd_block, 'FAIL: COMMANDS section missing'
cmd_text = cmd_block.group(0)
assert 'generate_slide_images_openai.py' in cmd_text and ('max-images' in cmd_text or 'prompts-dir' in cmd_text), 'FAIL: COMMANDS section does not document new script with CLI args'
open('.sisyphus/evidence/task-11-commands.txt', 'w', encoding='utf-8').write('COMMANDS_OK\n')

# 5. ANTI-PATTERNS 표에 새 행 (2컬럼)
anti_block = re.search(r'## ANTI-PATTERNS.+?(?=\n## )', content, re.DOTALL)
assert anti_block, 'FAIL: ANTI-PATTERNS section missing'
anti_text = anti_block.group(0)
new_anti_keywords = ['Modifying Gemini path while building OpenAI', 'silent.*fallback']
present = [k for k in new_anti_keywords if re.search(k, anti_text, re.IGNORECASE)]
assert len(present) >= 1, f'FAIL: new anti-pattern rows missing (none of: {new_anti_keywords})'
open('.sisyphus/evidence/task-11-anti-patterns.txt', 'w', encoding='utf-8').write(f'ANTI_PATTERNS_OK: {present}\n')

print('ALL_FIVE_CHANGES_OK')
" > .sisyphus/evidence/task-11-master.txt 2>&1
    Expected Result: ALL_FIVE_CHANGES_OK 출력, 5개 evidence 파일 모두 생성
    Failure Indicators: 5가지 변경 중 어느 하나라도 누락 → 즉시 fix 후 재검증
    Evidence: .sisyphus/evidence/task-11-{version,generated,where-to-look,commands,anti-patterns}.txt + master.txt

  Scenario: 다른 섹션 미변경 (회귀)
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. git diff AGENTS.md > .sisyphus/evidence/task-11-full-diff.txt
      2. python -c "
import re
diff_content = open('.sisyphus/evidence/task-11-full-diff.txt', encoding='utf-8').read()
# diff 라인 중 + 또는 -로 시작하면서 '## '가 포함된 줄 (섹션 헤더 추가/삭제)
section_changes = re.findall(r'^[+-]## [^\n]+', diff_content, re.MULTILINE)
# diff metadata 라인 (+++/---) 제외
section_changes = [l for l in section_changes if not l.startswith('+++') and not l.startswith('---')]
assert not section_changes, f'SECTION_HEADERS_CHANGED: {section_changes}'
print(f'NO_SECTION_HEADER_CHANGES (only intra-section edits)')
" > .sisyphus/evidence/task-11-section-headers.txt 2>&1
    Expected Result: NO_SECTION_HEADER_CHANGES 출력
    Failure Indicators: 새 ## 섹션 추가 또는 기존 섹션 삭제 → scope creep
    Evidence: .sisyphus/evidence/task-11-full-diff.txt, task-11-section-headers.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-11-version.txt`
  - [ ] `.sisyphus/evidence/task-11-generated.txt`
  - [ ] `.sisyphus/evidence/task-11-where-to-look.txt`
  - [ ] `.sisyphus/evidence/task-11-commands.txt`
  - [ ] `.sisyphus/evidence/task-11-anti-patterns.txt`
  - [ ] `.sisyphus/evidence/task-11-section-headers.txt`

  **Commit**: NO (Wave 3 합본)

- [x] 12. **AC1: 회귀 검증 — 기존 Gemini 동작 보존**

  **What to do**:
  - 신규 파라미터 없이 기존 명령 호출 시 Phase 1-5 시퀀스 변경 없음 검증
  - `visual-generate.md` Phase 1, 2, 3, 4, 5 헤더가 모두 보존되었는지 확인
  - 신규 Phase (0.5, 3.5)가 조건부 (renderer_choice_timing != "none" 시에만 활성화)인지 확인
  - 보호 파일들의 mtime/hash 변경 없는지 검증

  **Must NOT do**:
  - 실제 Gemini API 호출 (Task 15 smoke test에서 처리)
  - 보호 파일 직접 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: grep + python 검증 명령 5-6개 실행
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 13, 14, 15
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 5, 6, 7 (구현 완료)

  **References**:
  - `plugins/visual-generator/commands/visual-generate.md` 라인 37-150 — Phase 시퀀스
  - `plugins/visual-generator/agents/renderer-agent.md` — 보호 대상

  **WHY Each Reference Matters**:
  - 신규 추가가 기존 동작을 변경하면 사용자 신뢰 훼손 → 백워드 호환은 핵심 요구사항

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 5개 기존 Phase 헤더 보존
    Tool: Bash (PowerShell + Python)
    Preconditions: visual-generate.md 수정됨
    Steps:
      1. python -c "
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
required_phases = ['Phase 1: 문서 분석', 'Phase 2: 콘텐츠 검토', 'Phase 3: 프롬프트 생성', 'Phase 4: 이미지 렌더링', 'Phase 5: 최종 보고서 생성']
missing = [p for p in required_phases if p not in content]
assert not missing, f'REGRESSION: phases removed: {missing}'
print('REGRESSION_PASS')
" > .sisyphus/evidence/task-12-phases.txt 2>&1
    Expected Result: REGRESSION_PASS
    Evidence: .sisyphus/evidence/task-12-phases.txt

  Scenario: 신규 Phase 0.5/3.5는 조건부 활성화
    Tool: Bash (PowerShell + Python)
    Preconditions: 수정됨
    Steps:
      1. python -c "
import re
content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
# Phase 0.5와 Phase 3.5 각각의 컨텍스트 (전후 7줄) 안에 조건 키워드 존재 확인
def find_phase_context(phase_label):
    m = re.search(rf'{re.escape(phase_label)}', content)
    if not m:
        return None
    start = max(0, content.rfind('\n', 0, m.start() - 200))
    end = content.find('\n', m.end() + 500)
    return content[start:end]

phase_05 = find_phase_context('Phase 0.5')
phase_35 = find_phase_context('Phase 3.5')
assert phase_05, 'Phase 0.5 not found'
assert phase_35, 'Phase 3.5 not found'

# 조건 키워드 (renderer_choice_timing 또는 한국어 '조건:' 또는 'pre'/'post' 언급)
condition_patterns = [r'renderer_choice_timing.*?pre', r'renderer_choice_timing.*?post', r'조건:', r'when ', r'IF ']
phase_05_has_condition = any(re.search(p, phase_05, re.IGNORECASE) for p in condition_patterns)
phase_35_has_condition = any(re.search(p, phase_35, re.IGNORECASE) for p in condition_patterns)
assert phase_05_has_condition, 'Phase 0.5 not conditional'
assert phase_35_has_condition, 'Phase 3.5 not conditional'
print('PHASES_CONDITIONAL_OK')
" > .sisyphus/evidence/task-12-conditional.txt 2>&1
    Expected Result: PHASES_CONDITIONAL_OK
    Evidence: .sisyphus/evidence/task-12-conditional.txt

  Scenario: 보호 파일 6개 byte-identical
    Tool: Bash (PowerShell + Python)
    Preconditions: 모든 구현 완료
    Steps:
      1. git diff HEAD -- plugins/visual-generator/agents/renderer-agent.md plugins/visual-generator/agents/prompt-designer.md plugins/visual-generator/agents/content-organizer.md plugins/visual-generator/agents/content-reviewer.md plugins/visual-generator/agents/prompt-validator.md plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py > .sisyphus/evidence/task-12-protected.txt
      2. python -c "
diff_content = open('.sisyphus/evidence/task-12-protected.txt', encoding='utf-8').read()
assert not diff_content.strip(), f'PROTECTED FILES MODIFIED: {diff_content[:300]}'
print('PROTECTED_FILES_BYTE_IDENTICAL')
"
    Expected Result: PROTECTED_FILES_BYTE_IDENTICAL (diff 비어있음)
    Failure Indicators: cross-task contamination 발생 → 즉시 revert 필요
    Evidence: .sisyphus/evidence/task-12-protected.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-12-phases.txt`
  - [ ] `.sisyphus/evidence/task-12-conditional.txt`
  - [ ] `.sisyphus/evidence/task-12-protected.txt`

  **Commit**: NO (검증만, 변경 없음)

- [x] 13. **AC3: Cross-contamination 검증 (보호 파일 + 다른 플러그인 미변경)**

  **What to do**:
  - 보호 파일 11개 + skills/theme-* + skills/layout-types byte-identical 검증
  - 다른 플러그인 (isd-generator, hwpx-generator 등 17개) 변경 없음 검증
  - pytest.ini, .gitignore 등 root 설정 파일 변경 없음 검증

  **Must NOT do**:
  - 실제 파일 수정
  - git stash 사용 (작업 트리 보존)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: git diff + 패턴 검증
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 12, 14, 15
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 8, 11 (모든 파일 작업 완료)

  **References**:
  - draft `.sisyphus/drafts/visual-generator-openai-renderer.md` "보호 파일" 섹션 — allowlist
  - Metis review — Cross-Task Contamination Risks 섹션

  **WHY Each Reference Matters**:
  - AI agent의 "지나가는 김에" 정리 패턴 차단 — 명시적 검증으로 강제

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 보호 파일 + 디렉토리 byte-identical
    Tool: Bash
    Preconditions: 모든 구현 완료
    Steps:
      1. git diff HEAD --name-only > .sisyphus/evidence/task-13-changed-files.txt
      2. python -c "
import sys
allowed = {
  'plugins/visual-generator/agents/renderer-agent-openai.md',
  'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py',
  'plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md',
  'plugins/visual-generator/commands/visual-generate.md',
  'plugins/visual-generator/skills/slide-renderer/SKILL.md',
  'plugins/visual-generator/.claude-plugin/plugin.json',
  '.claude-plugin/marketplace.json',
  'README.md',
  'AGENTS.md',
}
changed = set(line.strip().replace('\\\\', '/') for line in open('.sisyphus/evidence/task-13-changed-files.txt') if line.strip())
unauthorized = changed - allowed
assert not unauthorized, f'UNAUTHORIZED CHANGES: {unauthorized}'
print('CONTAMINATION_CLEAN')
" > .sisyphus/evidence/task-13-allowlist.txt 2>&1
    Expected Result: 변경 파일이 allowlist 9개 중에서만 발견 (모두 변경되지 않아도 OK)
    Failure Indicators: 보호 파일 또는 다른 플러그인 변경 → 즉시 revert + 재수행
    Evidence: .sisyphus/evidence/task-13-changed-files.txt, task-13-allowlist.txt

  Scenario: 다른 플러그인 디렉토리 미변경
    Tool: Bash (PowerShell + Python)
    Preconditions: 위 시나리오 통과
    Steps:
      1. git diff HEAD --name-only -- plugins/ > .sisyphus/evidence/task-13-all-plugin-changes.txt
      2. python -c "
all_changes = [line.strip().replace('\\\\', '/') for line in open('.sisyphus/evidence/task-13-all-plugin-changes.txt', encoding='utf-8') if line.strip()]
other_plugin_changes = [c for c in all_changes if not c.startswith('plugins/visual-generator/')]
open('.sisyphus/evidence/task-13-other-plugins.txt', 'w', encoding='utf-8').write('\n'.join(other_plugin_changes) + ('\n' if other_plugin_changes else ''))
assert not other_plugin_changes, f'OTHER PLUGINS MODIFIED: {other_plugin_changes}'
print('OTHER_PLUGINS_UNTOUCHED')
"
    Expected Result: OTHER_PLUGINS_UNTOUCHED 출력 (visual-generator 외 플러그인 변경 없음)
    Evidence: .sisyphus/evidence/task-13-all-plugin-changes.txt, task-13-other-plugins.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-13-changed-files.txt`
  - [ ] `.sisyphus/evidence/task-13-allowlist.txt`
  - [ ] `.sisyphus/evidence/task-13-other-plugins.txt`

  **Commit**: NO (검증만)

- [x] 14. **AC5: 버전 동기화 검증 (5개 필드 일치)**

  **What to do**:
  - plugin.json version: 3.5.0
  - marketplace.json plugin entry version: 3.5.0
  - marketplace.json metadata.version: 3.30.0
  - README.md Version: 3.30.0
  - AGENTS.md Version: 3.30.0
  - 5개 필드 모두 일치 검증 (불일치 시 추적 불가)

  **Must NOT do**:
  - 버전 자동 수정 (검증만, 발견 시 보고 후 stop)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: grep + python 비교
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 12, 13, 15
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 2, 8, 9, 10, 11 (모든 버전 갱신 완료)

  **References**:
  - draft "마켓플레이스 버전 정책" 섹션
  - `AGENTS.md` "Version Management & Registry Updates" 섹션

  **WHY Each Reference Matters**:
  - 5개 필드 중 1개라도 불일치 시 사용자 혼란 + 캐시 무효화 실패

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: 5개 버전 필드 동시 검증
    Tool: PowerShell + Python
    Preconditions: 모든 구현 완료
    Steps:
      1. # 검증 스크립트를 임시 .py 파일로 저장 (heredoc 미사용 — PowerShell 호환)
         New-Item -ItemType Directory -Path .sisyphus/evidence -Force | Out-Null
         $checkScript = @'
import json, re, sys
results = {}
# 1. plugin.json
results['plugin.json'] = json.load(open('plugins/visual-generator/.claude-plugin/plugin.json', encoding='utf-8'))['version']
# 2. marketplace.json plugin entry
mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
vg = next(p for p in mp['plugins'] if p['name'] == 'visual-generator')
results['marketplace plugin entry'] = vg['version']
# 3. marketplace.json metadata.version
results['marketplace metadata'] = mp.get('metadata', {}).get('version', 'MISSING')
# 4. README.md Version
content = open('README.md', encoding='utf-8').read()
m = re.search(r'\*\*Version\*\*:\s*([\d.]+)', content)
results['README'] = m.group(1) if m else 'MISSING'
# 5. AGENTS.md Version
content = open('AGENTS.md', encoding='utf-8').read()
m = re.search(r'\*\*Version:?\*\*:?\s*([\d.]+)', content)
results['AGENTS'] = m.group(1) if m else 'MISSING'

print(json.dumps(results, indent=2, ensure_ascii=False))
expected = {
    'plugin.json': '3.5.0',
    'marketplace plugin entry': '3.5.0',
    'marketplace metadata': '3.30.0',
    'README': '3.30.0',
    'AGENTS': '3.30.0',
}
mismatches = {k: f'expected {expected[k]}, got {results[k]}' for k in expected if results[k] != expected[k]}
if mismatches:
    print(f'VERSION MISMATCHES: {mismatches}')
    sys.exit(1)
print('ALL_VERSIONS_SYNCED')
'@
         Set-Content -Path .sisyphus/evidence/task-14-checker.py -Value $checkScript -Encoding utf8
      2. python .sisyphus/evidence/task-14-checker.py > .sisyphus/evidence/task-14-versions.txt 2>&1
      3. python -c "content = open('.sisyphus/evidence/task-14-versions.txt', encoding='utf-8').read(); assert 'ALL_VERSIONS_SYNCED' in content, f'sync failed: {content}'"
    Expected Result: ALL_VERSIONS_SYNCED 출력
    Failure Indicators: 단 1개라도 불일치 → Tasks 2/8/9/10/11 중 누락
    Evidence: .sisyphus/evidence/task-14-checker.py, task-14-versions.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-14-versions.txt`

  **Commit**: NO (검증만)

- [x] 15. **AC7: Smoke Test (실제 API 호출, 두 렌더러 모두)**

  **What to do**:
  - 테스트 fixture: `theme-gov` SKILL.md 라인 332-436의 Golden Reference 4-block 프롬프트를 임시 파일로 저장 (`.sisyphus/evidence/task-15-fixture/01_smoke_test.md`)
  - Step A: Gemini 경로 회귀 — `python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --prompts-dir .sisyphus/evidence/task-15-fixture/ --output-dir .sisyphus/evidence/task-15-out-gemini/` → JPEG 1개 생성 확인
  - Step B: OpenAI 경로 신규 — `python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --prompts-dir .sisyphus/evidence/task-15-fixture/ --output-dir .sisyphus/evidence/task-15-out-openai/ --max-images 1 --yes` → JPEG 1개 생성 확인
  - 두 이미지의 file size > 10KB, JPEG magic bytes 검증
  - **API 키 누락 시 처리**: GEMINI_API_KEY 또는 OPENAI_API_KEY 미설정 시 해당 경로 SKIP + 명시적 경고 (cross-contamination/regression 검증은 skip 불가)
  - 실행 시간 + 비용 추정 보고

  **Must NOT do**:
  - 30개 이상의 fixture 생성 (max_images=1로 비용 통제)
  - 실패 시 자동 retry (검증 실패는 정직하게 보고)
  - GEMINI_API_KEY 누락 시 OpenAI로 silent fallback (or vice versa)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 실제 API 호출 + 결과 검증 + 에러 케이스 처리, 비용 발생 작업
  - **Skills**: 없음 (`[]`)

  **Parallelization**:
  - **Can Run In Parallel**: YES with Tasks 12, 13, 14
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 5, 6, 7 (구현 완료)

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/theme-gov/SKILL.md` 라인 332-436 — Golden Reference 4-block 프롬프트 (fixture 소스)

  **External References**:
  - OpenAI status page: 503 발생 시 retry 결정용

  **WHY Each Reference Matters**:
  - 검증된 Golden Reference 사용 → 4-block 호환성 검증 (D6 가정 실증)
  - 실제 API 호출 = 모델명 + 파라미터 + 인증 모두 통합 검증

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Fixture 준비 (theme-gov Golden Reference 추출)
    Tool: PowerShell + Python
    Preconditions: plugins/visual-generator/skills/theme-gov/SKILL.md 존재
    Steps:
      1. New-Item -ItemType Directory -Path .sisyphus/evidence/task-15-fixture -Force | Out-Null
      2. python -c "
import re
content = open('plugins/visual-generator/skills/theme-gov/SKILL.md', encoding='utf-8').read()
# Golden Reference Example 섹션 찾기 (라인 332-436 근방)
# ## INSTRUCTION 블록부터 다음 ## (FORBIDDEN ELEMENTS 또는 그 다음) 끝까지 추출
m = re.search(r'(## INSTRUCTION.*?## FORBIDDEN ELEMENTS.*?)(?=\n## [^F]|\n---|\Z)', content, re.DOTALL)
assert m, 'Golden Reference 4-block not found in theme-gov SKILL.md'
fixture = m.group(1).rstrip()
open('.sisyphus/evidence/task-15-fixture/01_smoke_test.md', 'w', encoding='utf-8').write(fixture)
import os
size = os.path.getsize('.sisyphus/evidence/task-15-fixture/01_smoke_test.md')
print(f'FIXTURE_READY: {size} bytes')
" > .sisyphus/evidence/task-15-fixture-ready.txt 2>&1
    Expected Result: FIXTURE_READY: N bytes 출력 (N > 1000)
    Evidence: .sisyphus/evidence/task-15-fixture-ready.txt, .sisyphus/evidence/task-15-fixture/01_smoke_test.md

  Scenario: Gemini 경로 회귀 smoke (GEMINI_API_KEY 필요)
    Tool: PowerShell + Python
    Preconditions: GEMINI_API_KEY 설정 (없으면 SKIP)
    Steps:
      1. if (-not $env:GEMINI_API_KEY) { Set-Content -Path .sisyphus/evidence/task-15-gemini.txt -Value "SKIPPED: GEMINI_API_KEY missing"; exit 0 }
      2. New-Item -ItemType Directory -Path .sisyphus/evidence/task-15-out-gemini -Force | Out-Null; $output = python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --prompts-dir .sisyphus/evidence/task-15-fixture/ --output-dir .sisyphus/evidence/task-15-out-gemini/ 2>&1; $output | Out-File -FilePath .sisyphus/evidence/task-15-gemini-stdout.txt -Encoding utf8
      3. python -c "
import os, glob
files = glob.glob('.sisyphus/evidence/task-15-out-gemini/01_*.jpg')
if not files:
    open('.sisyphus/evidence/task-15-gemini.txt', 'w').write('FAIL: no jpg generated')
    raise SystemExit(1)
size = os.path.getsize(files[0])
if size < 10000:
    open('.sisyphus/evidence/task-15-gemini.txt', 'w').write(f'FAIL: jpg too small ({size} bytes)')
    raise SystemExit(1)
open('.sisyphus/evidence/task-15-gemini.txt', 'w').write(f'PASS: gemini jpg {size} bytes - {files[0]}')
print(f'GEMINI_PASS: {size} bytes')
"
    Expected Result: GEMINI_PASS 또는 SKIPPED
    Failure Indicators: FAIL — Gemini 회귀 (구현 변경 없는데 Gemini 동작 깨짐 = AC1 위반)
    Evidence: .sisyphus/evidence/task-15-gemini.txt, task-15-gemini-stdout.txt, task-15-out-gemini/01_*.jpg

  Scenario: OpenAI 경로 신규 smoke (OPENAI_API_KEY 필요)
    Tool: PowerShell + Python
    Preconditions: OPENAI_API_KEY 설정 (없으면 SKIP)
    Steps:
      1. if (-not $env:OPENAI_API_KEY) { Set-Content -Path .sisyphus/evidence/task-15-openai.txt -Value "SKIPPED: OPENAI_API_KEY missing"; exit 0 }
      2. New-Item -ItemType Directory -Path .sisyphus/evidence/task-15-out-openai -Force | Out-Null; $output = python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --prompts-dir .sisyphus/evidence/task-15-fixture/ --output-dir .sisyphus/evidence/task-15-out-openai/ --max-images 1 --yes 2>&1; $output | Out-File -FilePath .sisyphus/evidence/task-15-openai-stdout.txt -Encoding utf8
      3. python -c "
import os, glob
files = glob.glob('.sisyphus/evidence/task-15-out-openai/01_*.jpg')
if not files:
    open('.sisyphus/evidence/task-15-openai.txt', 'w').write('FAIL: no jpg generated')
    raise SystemExit(1)
size = os.path.getsize(files[0])
if size < 10000:
    open('.sisyphus/evidence/task-15-openai.txt', 'w').write(f'FAIL: jpg too small ({size} bytes)')
    raise SystemExit(1)
open('.sisyphus/evidence/task-15-openai.txt', 'w').write(f'PASS: openai jpg {size} bytes - {files[0]}')
print(f'OPENAI_PASS: {size} bytes')
"
    Expected Result: OPENAI_PASS 또는 SKIPPED (OPENAI_API_KEY 없을 때)
    Failure Indicators: FAIL — 모델 호출 실패, 인증 실패, 응답 구조 mismatch
    Evidence: .sisyphus/evidence/task-15-openai.txt, task-15-openai-stdout.txt, task-15-out-openai/01_*.jpg

  Scenario: JPEG magic bytes 검증
    Tool: Bash (PowerShell + Python)
    Preconditions: 위 시나리오에서 PASS인 경우
    Steps:
      1. python -c "
import os
checked = []
for path in ['.sisyphus/evidence/task-15-out-gemini', '.sisyphus/evidence/task-15-out-openai']:
    if os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith('.jpg'):
                with open(os.path.join(path, f), 'rb') as fp:
                    head = fp.read(3)
                    assert head[:2] == b'\\xff\\xd8' and head[2] == 0xff, f'{path}/{f}: not JPEG (got {head})'
                    checked.append(f'{path}/{f}')
                    print(f'OK: {path}/{f}')
if not checked:
    print('NO_FILES_TO_CHECK (both paths SKIPPED)')
else:
    print(f'JPEG_MAGIC_BYTES_OK: {len(checked)} files validated')
" > .sisyphus/evidence/task-15-magic-bytes.txt 2>&1
    Expected Result: 생성된 모든 .jpg가 JPEG magic bytes로 시작 (또는 NO_FILES_TO_CHECK)
    Failure Indicators: PNG로 잘못 저장 / 손상된 파일
    Evidence: .sisyphus/evidence/task-15-magic-bytes.txt
  ```

  **Evidence to Capture**:
  - [ ] `.sisyphus/evidence/task-15-fixture-ready.txt`
  - [ ] `.sisyphus/evidence/task-15-gemini.txt`
  - [ ] `.sisyphus/evidence/task-15-gemini-stdout.txt`
  - [ ] `.sisyphus/evidence/task-15-out-gemini/01_*.jpg`
  - [ ] `.sisyphus/evidence/task-15-openai.txt`
  - [ ] `.sisyphus/evidence/task-15-openai-stdout.txt`
  - [ ] `.sisyphus/evidence/task-15-out-openai/01_*.jpg`
  - [ ] `.sisyphus/evidence/task-15-magic-bytes.txt`

  **Commit**: NO (검증만)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command, check schema). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Verify all 6 protected files have empty `git diff HEAD --`. Verify all 5 version fields are synchronized. Check evidence files in `.sisyphus/evidence/task-*`.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [15/15] | Protected Files [6/6 untouched] | Version Sync [5/5] | VERDICT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Read `generate_slide_images_openai.py` end-to-end. Check: `as any`/silent excepts/print debug statements/commented-out code/unused imports. Verify SYSTEM_INSTRUCTION is prepended (not passed as system_instruction param). Verify retry semantics match Gemini script (3 API retries × 5s). Verify hard-fail on missing OPENAI_API_KEY. Verify `--max-images` cost cap with confirmation. Run `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py').read())"`. AI slop: excessive comments, generic names (data/result/temp), over-abstraction.
  Output: `Syntax [PASS/FAIL] | API Patterns [PASS/FAIL] | Hard-fail [PASS/FAIL] | Cost-cap [PASS/FAIL] | AI Slop [N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute every QA scenario from every task — exact steps, capture evidence. Smoke tests: (1) Gemini path with no new params (regression), (2) OpenAI path with `renderer="openai"` (single image, dry-run if API key unavailable). Cross-task: switching renderer mid-deck behavior. Edge cases: missing API key, invalid renderer value, --max-images exceeded. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Regression [PASS/FAIL] | OpenAI Smoke [PASS/FAIL/SKIPPED] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Specifically check: `content-organizer.md` was NOT modified (was dropped from plan). No new tests/CI/pytest config added. No DALL-E/gpt-image-1/etc. references. No `renderer="both"` mode. No factory pattern. No `prompt-validator.md` modification. No fix to existing #9, #10, #11 validation gaps. Detect cross-task contamination: any protected file touched.
  Output: `Tasks [15/15 compliant] | Contamination [CLEAN/N issues] | Scope Creep [CLEAN/N items] | VERDICT`

---

## Commit Strategy

| # | Commit Message | Files | Pre-commit |
|---|---------------|-------|------------|
| Wave 1 | `feat(visual-generator): scaffold OpenAI rendering path foundation` | plugin.json, openai-quality-rubric.md, SKILL.md | python -c "import json; json.load(open('plugins/visual-generator/.claude-plugin/plugin.json'))" |
| Wave 2 | `feat(visual-generator): add gpt-image-2 renderer agent and script` | renderer-agent-openai.md, generate_slide_images_openai.py, visual-generate.md, marketplace.json (entry) | python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py').read())" |
| Wave 3 | `docs(visual-generator): document OpenAI rendering path and bump versions` | marketplace.json (metadata), README.md, AGENTS.md | grep "3.30.0" README.md AGENTS.md && grep "3.5.0" plugins/visual-generator/.claude-plugin/plugin.json |

---

## Success Criteria

### Verification Commands

```bash
# 1. plugin.json 스키마 화이트리스트 검사
python -c "import json; A = {'name','version','description','author','homepage','repository','license','keywords','skills','commands','agents','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies'}; d=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json',encoding='utf-8')); print('OK' if not (set(d.keys()) - A) else f'SCHEMA FAIL: {set(d.keys()) - A}')"
# Expected: OK

# 2. marketplace.json visual-generator entry 검증
python -c "import json; mp = json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); M = {'name','source','description','strict','agents','skills','version','author','license','category','homepage','keywords','tags','commands','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies','repository'}; vg = next(p for p in mp['plugins'] if p['name']=='visual-generator'); print('OK' if not (set(vg.keys()) - M) else f'SCHEMA FAIL: {set(vg.keys()) - M}'); print('AGENTS:', vg.get('agents', 'MISSING'))"
# Expected: OK / AGENTS includes ./agents/renderer-agent-openai.md

# 3. 보호 파일 byte-identical 검증
git diff HEAD -- plugins/visual-generator/agents/renderer-agent.md plugins/visual-generator/agents/prompt-designer.md plugins/visual-generator/agents/content-organizer.md plugins/visual-generator/agents/content-reviewer.md plugins/visual-generator/agents/prompt-validator.md plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
# Expected: empty output

# 4. 버전 동기화 검증 (5개 필드)
python -c "import json; print('plugin:', json.load(open('plugins/visual-generator/.claude-plugin/plugin.json',encoding='utf-8'))['version'])"
python -c "import json; mp=json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); print('mp-meta:', mp.get('metadata',{}).get('version','MISSING')); print('mp-vg:', next(p for p in mp['plugins'] if p['name']=='visual-generator')['version'])"
# Expected: plugin:3.5.0 / mp-meta:3.30.0 / mp-vg:3.5.0
# Expected README + AGENTS Version 라인 grep으로 추가 확인

# 5. 신규 Python 스크립트 syntax 검증
python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py').read()); print('OK')"
# Expected: OK

# 6. 신규 Python 스크립트 CLI parity 검증 (Gemini와 동일한 --prompts-dir, --output-dir)
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --help | grep -E "prompts-dir|output-dir|max-images"
# Expected: 3개 옵션 모두 존재
```

### Final Checklist

- [ ] 모든 "Must Have" 구현됨
- [ ] 모든 "Must NOT Have" 미존재 (보호 파일 byte-identical, 금지 기능 미구현)
- [ ] 모든 QA 시나리오 evidence 파일 존재
- [ ] 5개 버전 필드 동기화 (3.5.0/3.30.0)
- [ ] AGENTS.md/README.md MANDATORY 업데이트 규칙 준수
- [ ] Final Verification Wave 4개 모두 APPROVE
- [ ] 사용자 명시적 okay 받음
