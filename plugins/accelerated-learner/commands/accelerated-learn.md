# accelerated-learn 커맨드

48시간 가속 학습 파이프라인을 실행합니다. 소스 자료를 분석하고 멘탈모델을 추출하며 논쟁을 매핑하고 판별 질문을 설계한 후 소크라틱 튜터링을 진행합니다.

## 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|:----:|-------|------|
| `source_path` | O | - | 소스 자료 폴더 또는 파일 경로 |
| `subject_name` | O | - | 학습 주제명 (출력 폴더명 결정) |
| `output_dir` | - | `./output/` | 출력 디렉토리 |
| `auto_mode` | - | `false` | true 시 튜터링 건너뜀 |

## 워크플로우

```text
[Phase 0: 초기화]
    +-- Step 0-1. 파라미터 검증 (source_path 존재, subject_name 비어있지 않음)
    +-- Step 0-2. 출력 디렉토리 생성: {output_dir}/{subject_name}/

[Phase 1: 소스 종합]
    +-- Step 1-1. Task(subagent_type="accelerated-learner::source-synthesizer")
                  Prompt: "source_path={source_path}, output_dir={output_dir}/{subject_name}/"
    +-- Step 1-2. 결과 검증: {output_dir}/{subject_name}/00-source-synthesis.md 존재 확인
    +-- Step 1-3. 실패 시: 재시도 1회 → 재실패 시 사용자에게 알리고 중단

[Phase 2: 멘탈모델 + 논쟁 (병렬 실행)]
    +-- Step 2-1. Task(subagent_type="accelerated-learner::mental-model-extractor") // 병렬
    +-- Step 2-2. Task(subagent_type="accelerated-learner::controversy-mapper")     // 병렬
    +-- Step 2-3. 결과 검증: 01-mental-models.md + 02-controversies.md 모두 존재 확인

[Phase 3: 판별 질문 생성]
    +-- Step 3-1. Task(subagent_type="accelerated-learner::question-architect")
    +-- Step 3-2. 결과 검증: 03-discriminating-questions.md 존재 확인

[Phase 4: 소크라틱 튜터링] (auto_mode=true 시 건너뜀)
    +-- Step 4-0. auto_mode 확인 → true이면 Phase 5로 건너뜀
    +-- Step 4-1. Task(subagent_type="accelerated-learner::socratic-tutor")
    +-- Step 4-2. 세션 완료 후 sessions/ 디렉토리 + 05-mastery-summary.md 검증

[Phase 5: 완료]
    +-- 전체 산출물 요약 출력
    +-- {output_dir}/{subject_name}/ 내 파일 목록 표시
    +-- 학습 완료 메시지 표시
```

## 상세 실행 절차

### Phase 0. 초기화

1. `source_path`, `subject_name`, `output_dir`, `auto_mode`를 파싱합니다.
2. `source_path`가 존재하지 않으면 즉시 중단하고 오류를 보고합니다.
3. `subject_name`이 비어있거나 공백만 포함하면 즉시 중단하고 오류를 보고합니다.
4. `{output_dir}/{subject_name}/` 디렉토리를 생성합니다.

### Phase 1. 소스 종합

1. 아래 프롬프트로 에이전트를 호출합니다.

Use the Task tool with subagent_type="accelerated-learner::source-synthesizer"
Prompt: """
source_path: {source_path}
output_dir: {output_dir}/{subject_name}/

소스 자료를 분석하여 00-source-synthesis.md를 생성해주세요.
"""

2. `{output_dir}/{subject_name}/00-source-synthesis.md` 존재를 검증합니다.
3. 파일이 없으면 동일 호출을 **정확히 1회 재시도**합니다.
4. 재시도 후에도 파일이 없으면 오류를 보고하고 전체 파이프라인을 중단합니다.

### Phase 2. 멘탈모델 + 논쟁 매핑 (병렬)

1. 아래 두 Task를 **반드시 병렬(parallel/동시) 실행**합니다. 순차 실행 금지.

Use the Task tool TWICE IN PARALLEL:

첫 번째: subagent_type="accelerated-learner::mental-model-extractor"
Prompt: """
output_dir: {output_dir}/{subject_name}/
00-source-synthesis.md를 읽어 멘탈모델을 추출하고 01-mental-models.md를 생성해주세요.
"""

두 번째: subagent_type="accelerated-learner::controversy-mapper"
Prompt: """
output_dir: {output_dir}/{subject_name}/
00-source-synthesis.md를 읽어 논쟁 지형을 매핑하고 02-controversies.md를 생성해주세요.
"""

2. 두 작업이 모두 완료된 뒤 아래 파일 존재를 검증합니다.
   - `{output_dir}/{subject_name}/01-mental-models.md`
   - `{output_dir}/{subject_name}/02-controversies.md`
3. 둘 중 하나라도 없으면 누락된 작업만 **정확히 1회 재시도**합니다.
4. 재시도 후에도 누락 파일이 있으면 오류를 보고하고 중단합니다.

### Phase 3. 판별 질문 생성

1. 아래 프롬프트로 에이전트를 호출합니다.

Use the Task tool with subagent_type="accelerated-learner::question-architect"
Prompt: """
output_dir: {output_dir}/{subject_name}/
01-mental-models.md + 02-controversies.md를 읽어 판별 질문을 설계하고 03-discriminating-questions.md를 생성해주세요.
"""

2. `{output_dir}/{subject_name}/03-discriminating-questions.md` 존재를 검증합니다.
3. 파일이 없으면 **정확히 1회 재시도** 후, 재실패 시 오류 보고 후 중단합니다.

### Phase 4. 소크라틱 튜터링 (조건부)

1. `auto_mode` 값을 확인합니다.
2. `auto_mode=true`이면 튜터링 단계를 생략(건너뜀/skip)하고 Phase 5로 이동합니다.
3. `auto_mode=false`이면 아래 프롬프트로 에이전트를 호출합니다.

Use the Task tool with subagent_type="accelerated-learner::socratic-tutor"
Prompt: """
output_dir: {output_dir}/{subject_name}/
03-discriminating-questions.md + 01-mental-models.md + 02-controversies.md를 읽어 소크라틱 튜터링 세션을 진행해주세요.
"""

4. 완료 후 아래를 검증합니다.
   - `{output_dir}/{subject_name}/sessions/` 디렉토리 존재
   - `{output_dir}/{subject_name}/05-mastery-summary.md` 존재
5. 누락 시 **정확히 1회 재시도** 후, 재실패 시 오류 보고 후 중단합니다.

### Phase 5. 완료 처리

1. 생성된 산출물을 요약하여 출력합니다.
2. `{output_dir}/{subject_name}/` 하위 파일 목록을 표시합니다.
3. 학습 파이프라인 완료 메시지를 출력합니다.

## 에러 처리 규칙

- 각 Phase의 핵심 산출물 검증 실패 시, 해당 Phase Task를 1회 재시도합니다.
- 재시도 후에도 실패하면 실패 원인(누락 파일/디렉토리)을 명시하고 즉시 중단합니다.
- 상위 Phase 산출물이 없으면 하위 Phase를 실행하지 않습니다.

## 출력 산출물

기본 산출물 경로: `{output_dir}/{subject_name}/`

- `00-source-synthesis.md`
- `01-mental-models.md`
- `02-controversies.md`
- `03-discriminating-questions.md`
- `sessions/` (소크라틱 튜터링 로그)
- `05-mastery-summary.md` (auto_mode=false일 때)

## MUST NOT DO

- 오케스트레이터가 직접 소스 분석/멘탈모델 추출/논쟁 매핑/질문 생성/튜터링 수행 금지
- 웹 검색으로 소스 자료 보충 금지
- Phase 2의 두 에이전트를 순차 실행 금지 — 반드시 병렬
- 에러 발생 시 재시도 없이 즉시 포기 금지 — 반드시 1회 재시도
