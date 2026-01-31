# ISD Generator References 구조 개선

## Context

### Original Request
민감한 실제 제안서 문서를 공개하지 않으면서도 동일한 수준의 보고서를 작성할 수 있도록 `plugins/isd-generator/references/` 구조 개선

### Interview Summary
**Key Discussions**:
- examples/ 처리: 비공개 브랜치 보관 후 main에서 삭제
- 패턴 상세 수준: 구조만 제공 (AI가 내용 채움)
- 검증 엄격도: 필수 요소만 검증

**Research Findings**:
- `document_templates/` - 이미 추상적 구조로 안전 (변경 불필요)
- `guides/` - 대부분 방법론, 일부 파일에 실제 기관명 포함
- `examples/` - 실제 기업명, 기관명, VoC, 예산 등 민감 정보 다수 포함
- `example_prompts.md` (현재 위치: `examples/example_prompts.md`) - 실제 기관명 포함 (812+ lines)
- `input_template.md` - `[예: 기관명]` 형식의 플레이스홀더로 안전
- `agents/chapter1.md:399` - 예시로 실제 기업명 포함

### Momus Review (4차 - REJECT)
**Critical Issues Addressed**:
1. 비공개 백업 브랜치 보안 전제 명시 → Task 0에 private 원격 사용 또는 로컬 백업 옵션 추가
2. 보안 스캔 예외 정합성 → `input_template.md` 예외 근거 명시
3. Task 0 커밋 정책 자기모순 해소 → dirty 상태 처리 규칙 명확화
4. Task 10 파일 수 검증 결정적으로 → 정확한 기대 파일 수 23개 명시
5. 가이드 익명화 추가 발견분 처리 규칙 → Task 4, 5에 전체 grep 규칙 추가

---

## Work Objectives

### Core Objective
민감 정보가 포함된 파일들을 익명화하고 examples/ 폴더를 제거하여, 공개 가능한 상태로 동일 수준의 보고서 생성 가능하게 함

### 민감 정보 제거 범위 (CRITICAL - 명확한 정의)

| 대상 | 범위 | 처리 |
|------|------|------|
| `references/examples/` | 전체 | 삭제 (백업 브랜치 보존) |
| `references/example_prompts.md` | 기관명 | 이동 + 익명화 |
| `references/guides/prompt_guide.md` | 기관명 | 익명화 |
| `references/guides/data_collection_guide.md` | 기관명 | 익명화 |
| `agents/chapter1.md` | 네트워크 예시 기업명 | 익명화 |
| `references/input_template.md` | `[예: X]` 형식 | 유지 (플레이스홀더) |
| `references/document_templates/` | 없음 | 변경 없음 |

### Concrete Deliverables
1. 로컬 백업 브랜치 `archive/examples-backup` 생성 (원격 push 금지 - public 저장소)
2. `writing_patterns/` 폴더 5개 파일 생성
3. `content_requirements/` 폴더 5개 파일 생성 (크로스 챕터 일관성 포함)
4. `example_prompts.md` 상위 폴더로 이동 및 익명화
5. `prompt_guide.md`, `data_collection_guide.md` 익명화
6. 6개 agent 파일 경로 업데이트 + `chapter1.md` 예시 익명화
7. `AGENTS.md` 구조 문서 업데이트
8. examples/ 폴더 main에서 삭제

### Definition of Done
- [x] `git grep "examples/" -- "plugins/isd-generator/agents/*.md"` 실행 시 결과 0건
- [x] 아래 보안 스캔 모두 통과
- [x] 모든 agent 파일 경로 참조 오류 없음
- [x] 테스트: Chapter 3 agent 호출 시 경로 에러 없음 (상세 기준은 Task 10 참조)

### 보안 스캔 기준 (CRITICAL)

**허용되는 패턴** (False Positive - 무시):
- `[예: 기관명]` 형식의 플레이스홀더 (input_template.md 내)
- document_templates/ 내 모든 내용 (추상적 템플릿)

**input_template.md 예외 근거**:
- 이 파일은 사용자 입력 양식 템플릿으로, `[예: 삼성전자]`, `[예: 서울대학교]` 등의 형식은
  실제 기업/기관명이 아닌 **입력 가이드 플레이스홀더**임
- 실행자에게 "여기에 기업명을 입력하라"는 안내 목적이므로, 민감 정보 노출이 아님
- 스캔에서 `grep -v "input_template.md"`로 제외하는 이유: 플레이스홀더 형식 자체는 유지해야 함

**금지되는 패턴** (반드시 제거):
- 실제 프로젝트 콘텐츠 내 기관/기업명
- VoC 인용문 내 실제 기업명
- 네트워크/MoU 예시 내 실제 기업명
- 예산/금액 실제 데이터

**최종 검증 명령어** (Task 10에서 실행):
```bash
# 1. 현대 계열 스캔 (examples/ 삭제 후, 전체 isd-generator 대상)
grep -rn "현대위아\|현대자동차\|현대중공업\|HD현대\|HMC" plugins/isd-generator/ \
  | grep -v "input_template.md"
# 예상: 0건

# 2. 프로젝트 예시 기관명 스캔
grep -rn "SKKU\|성균관대학교\|삼성서울병원\|삼성병원\|Harvard\|MGH" plugins/isd-generator/ \
  | grep -v "input_template.md"
# 예상: 0건

# 3. examples/ 참조 스캔
git grep "examples/" -- "plugins/isd-generator/"
# 예상: 0건
```

### Must Have
- 모든 민감 정보 제거 (위 범위 표 참조)
- 6개 agent 파일 경로 업데이트
- 패턴 기반 참조 파일 생성
- 로컬 백업 브랜치 생성 (원격 push 금지)

### Must NOT Have (Guardrails)
- `document_templates/` 폴더 변경 금지
- `input_template.md` 변경 금지 (`[예: X]` 형식은 플레이스홀더로 허용)
- Agent 로직/워크플로우 변경 금지 (경로 및 예시 텍스트만 수정)
- 가짜 "현실적" 예시 생성 금지 (명확한 플레이스홀더 사용: `[대기업A]`, `[협력기관1]`)
- 로컬 백업 브랜치 생성 전 examples/ 삭제 금지
- **백업 브랜치를 public 원격(origin)에 push 금지** (민감 정보 노출 방지)

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO (마크다운 문서 작업)
- **User wants tests**: Manual-only
- **Framework**: none

### Manual QA Procedure

각 TODO 완료 후 해당 검증 수행 (Task별 Acceptance Criteria 참조)

---

## Task Flow

```
Task 0 (백업 브랜치 생성 + 원격 push)
    ↓
Task 1, 2 (새 폴더 구조 생성) ← 병렬 가능
    ↓
Task 3 (example_prompts.md 이동)
    ↓
Task 4, 5, 6 (익명화) ← 병렬 가능
    ↓
Task 7 (Agent 파일 경로 업데이트)
    ↓
Task 8 (examples/ 삭제)
    ↓
Task 9 (AGENTS.md 업데이트)
    ↓
Task 10 (최종 검증)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 1, 2 | 독립적인 폴더 생성 |
| B | 4, 5, 6 | 독립적인 파일 익명화 |

| Task | Depends On | Reason |
|------|------------|--------|
| 3 | 0 | 백업 완료 후 파일 이동 |
| 4, 5, 6 | 3 | 파일 이동 후 익명화 (4는 3에 직접 의존, 5,6은 병렬) |
| 7 | 1, 2, 4, 5, 6 | 새 경로 및 익명화 완료 후 참조 업데이트 |
| 8 | 0, 7 | 백업 및 참조 업데이트 완료 후 삭제 |
| 9 | 8 | 최종 구조 확정 후 문서화 |
| 10 | 9 | 모든 변경 완료 후 검증 |

---

## TODOs

- [x] 0. 백업 브랜치 생성 (로컬 백업)

  **What to do**:
  - 현재 main 브랜치에서 `archive/examples-backup` 브랜치 생성
  - **로컬에만 보관** (원격 push 금지 - honeypot 저장소가 public이므로)
  - main 브랜치로 복귀

  **보안 전제 (CRITICAL)**:
  - 현재 원격(`origin`)은 `github.com/orientpine/honeypot.git`로 **public 저장소**임
  - 민감 정보가 포함된 백업 브랜치를 public 원격에 push하면 목적이 무효화됨
  - 따라서 백업 브랜치는 **로컬에만 보관**하고, 원격 push는 **금지**
  - 별도 private 원격이 필요하면 사용자가 추후 수동으로 추가할 수 있음

  **사전 조건 (dirty 상태 처리 규칙)**:
  - `git status`로 작업 디렉토리 상태 확인
  - **Dirty 상태인 경우**:
    - **모든 변경 사항을 stash**로 임시 저장: `git stash -u`
    - 브랜치 생성 완료 후 main 복귀 시 `git stash pop`
    - **stash pop 충돌/실패 시 처리**:
      - `git stash apply`로 시도 (stash 보존)
      - 충돌 발생 시: 충돌 파일 수동 해결 후 `git stash drop`
      - 최악의 경우: `git stash show -p | git apply --3way` 사용
      - **원칙**: 백업 브랜치 생성이 최우선, stash 복구는 후순위
    - (참고: 이 Task의 Commit은 NO이며, dirty 상태를 해결하기 위한 커밋은 만들지 않음)
  - **Clean 상태인 경우**: 바로 브랜치 생성

  **실행 명령어**:
  ```bash
  # 0. 상태 확인
  git status
  
  # 1. (Dirty인 경우) stash로 임시 저장
  # git stash -u
  
  # 2. 백업 브랜치 생성 (로컬만)
  git checkout -b archive/examples-backup
  
  # 3. main으로 복귀
  git checkout main
  
  # 4. (필요시) stash pop
  # git stash pop
  ```

  **Must NOT do**:
  - main 브랜치에서 파일 삭제하지 않음 (백업만)
  - **원격에 백업 브랜치 push 금지** (public 저장소이므로)
  - dirty 상태 해결을 위한 커밋 생성 금지 (stash만 사용)

  **Parallelizable**: NO (첫 번째 작업)

  **References**:
  - 없음 (Git 기본 명령)

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `git branch -a | grep archive/examples-backup` → 로컬 브랜치 존재
  - [ ] `git ls-remote --heads origin archive/examples-backup 2>&1 | wc -l` → 0 (원격에 없음 확인)
  - [ ] `git branch --show-current` → `main` (현재 브랜치 복귀 확인)
  - [ ] `git status` → clean 또는 stash pop 후 예상된 변경만 존재

  **Commit**: NO (브랜치 생성만, 커밋 및 원격 push 없음)

---

- [x] 1. writing_patterns/ 폴더 생성

  **What to do**:
  - `plugins/isd-generator/references/writing_patterns/` 폴더 생성
  - 5개 파일 생성:
    1. `sentence_patterns.md` - 문장 구조 패턴
    2. `table_patterns.md` - 표 구조 패턴
    3. `section_patterns.md` - 섹션 구조 패턴
    4. `vocabulary_glossary.md` - 용어/어휘 사전
    5. `voc_template.md` - VoC 작성 템플릿

  **파일 내용 필수 구조**:
  ```markdown
  # [파일 제목]

  ## 개요
  [이 파일의 목적 1-2문장]

  ## 패턴 1: [패턴명]

  ### 구조
  [골격 구조 설명]

  ### 사용 예시
  - `[주어]`는 `[목적어]`를 `[동사]`한다.

  ## 패턴 2: [패턴명]
  ...
  ```

  **Must NOT do**:
  - 실제 기업명/기관명 사용 금지
  - 가짜 "현실적" 예시 생성 금지
  - 플레이스홀더 형식: `[대기업A]`, `[중견기업B]`, `[주관기관]`, `[기술명]`

  **Parallelizable**: YES (with 2)

  **References**:

  **Pattern References** (existing code to follow):
  - `plugins/isd-generator/references/input_template.md` - 플레이스홀더 형식 참고 (`[예: ...]`)
  - `plugins/isd-generator/references/document_templates/chapter1_template.md:26-42` - 문장 구조 패턴
  - `plugins/isd-generator/references/document_templates/chapter3_template.md:299-320` - 섹션 패턴

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `ls plugins/isd-generator/references/writing_patterns/` → 5개 파일 존재
  - [ ] `grep -rn "현대\|삼성\|LG\|KIMM\|SKKU" plugins/isd-generator/references/writing_patterns/` → 0건
  - [ ] 각 파일 구조 검증:
    ```bash
    for f in plugins/isd-generator/references/writing_patterns/*.md; do
      echo "=== $f ===" 
      grep -c "^# " "$f"        # 1 이상
      grep -c "^## 개요" "$f"   # 1
      grep -c "^## 패턴" "$f"   # 1 이상
    done
    ```
    모든 파일에서 위 패턴 존재 확인

  **Commit**: NO (groups with 2)

---

- [x] 2. content_requirements/ 폴더 생성

  **What to do**:
  - `plugins/isd-generator/references/content_requirements/` 폴더 생성
  - 5개 파일 생성:
    1. `chapter1_requirements.md` - 개발대상 및 필요성 요구사항
    2. `chapter2_requirements.md` - 국내외 동향 요구사항
    3. `chapter3_requirements.md` - 연구목표 요구사항
    4. `chapter4_requirements.md` - 기대효과 요구사항
    5. `chapter5_requirements.md` - 참고자료 요구사항

  **파일 내용 필수 구조** (크로스 챕터 일관성 포함):
  ```markdown
  # Chapter N 콘텐츠 요구사항

  ## 필수 섹션
  - [ ] 섹션 1: [섹션명]
  - [ ] 섹션 2: [섹션명]

  ## 데이터 요구사항
  | 섹션 | 필요 데이터 | 출처 유형 | 최소 개수 |
  |------|------------|----------|----------|
  | [섹션명] | [데이터 유형] | [웹/논문/내부] | [N개] |

  ## 크로스 챕터 일관성 체크리스트
  - [ ] 기관 목록 일치: 참여기관 명칭이 Ch1, Ch3, Ch4에서 동일한가?
  - [ ] 정량 목표 일치: 연구비, 기간, 성과지표가 Ch3, Ch4에서 동일한가?
  - [ ] 핵심 기술 일치: 세부기술 명칭이 전 챕터에서 동일한가?
  - [ ] 용어 일관성: 약어, 기술명이 전 챕터에서 통일되었는가?

  ## 검증 체크리스트
  - [ ] 필수 섹션 모두 포함
  - [ ] 각 섹션에 최소 데이터 존재
  - [ ] 출처 명시 완료
  - [ ] 크로스 챕터 일관성 확인 완료
  ```

  **Must NOT do**:
  - 실제 콘텐츠 예시 포함 금지
  - 정량 기준 과도하게 엄격하게 설정 금지

  **Parallelizable**: YES (with 1)

  **References**:

  **Pattern References**:
  - `plugins/isd-generator/references/document_templates/chapter1_template.md` - 섹션 구조
  - `plugins/isd-generator/references/document_templates/chapter3_template.md` - 섹션 구조
  - `plugins/isd-generator/references/guides/verification_rules.md` - 검증 규칙 형식

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `ls plugins/isd-generator/references/content_requirements/` → 5개 파일 존재
  - [ ] 각 파일 구조 검증:
    ```bash
    for f in plugins/isd-generator/references/content_requirements/*.md; do
      echo "=== $f ==="
      grep -c "^## 필수 섹션" "$f"                    # 1
      grep -c "^## 데이터 요구사항" "$f"              # 1
      grep -c "^## 크로스 챕터 일관성" "$f"           # 1
      grep -c "^## 검증 체크리스트" "$f"              # 1
    done
    ```
    모든 파일에서 4개 섹션 존재 확인

  **Commit**: YES
  - Message: `feat(isd): add writing_patterns and content_requirements folders`
  - Files: `plugins/isd-generator/references/writing_patterns/*`, `plugins/isd-generator/references/content_requirements/*`
  - Pre-commit: 없음

---

- [x] 3. example_prompts.md 파일 이동

  **What to do**:
  - `plugins/isd-generator/references/examples/example_prompts.md` 파일을
  - `plugins/isd-generator/references/example_prompts.md` 로 이동 (git mv)

  **실행 명령어**:
  ```bash
  git mv plugins/isd-generator/references/examples/example_prompts.md \
         plugins/isd-generator/references/example_prompts.md
  ```

  **Must NOT do**:
  - 파일 내용 수정 (이동만, 익명화는 Task 4에서)
  - 복사 후 삭제 (git mv 사용하여 히스토리 보존)

  **Parallelizable**: NO (depends on 0)

  **References**:

  **Source File**:
  - `plugins/isd-generator/references/examples/example_prompts.md` (현재 위치)

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `ls plugins/isd-generator/references/example_prompts.md` → 파일 존재
  - [ ] `ls plugins/isd-generator/references/examples/example_prompts.md 2>&1` → "No such file"
  - [ ] `git status` → renamed 상태

  **Commit**: NO (Task 4와 함께)

---

- [x] 4. example_prompts.md 익명화

  **What to do**:
  - `plugins/isd-generator/references/example_prompts.md` 파일 (1054 lines) 익명화

  **치환 목록 (CRITICAL - 순서대로 적용)**:
  
  복합 패턴을 먼저 치환하여 중복 치환 방지:
  
  | 순서 | 원본 | 치환 | 비고 |
  |:---:|------|------|------|
  | 1 | `SKKU (성균관대학교)` | `[주관기관]` | 복합 패턴 먼저 |
  | 2 | `SKKU (중심)` | `[주관기관] (중심)` | 복합 패턴 |
  | 3 | `Harvard/MGH` | `[협력기관2]` | 복합 패턴 |
  | 4 | `성균관대학교` | `[주관기관]` | 단일 패턴 |
  | 5 | `SKKU` | `[주관기관]` | 단일 패턴 |
  | 6 | `삼성서울병원` | `[협력기관1]` | |
  | 7 | `삼성병원` | `[협력기관1]` | 약칭 |
  | 8 | `Harvard` | `[협력기관2]` | 단일 패턴 |
  | 9 | `MGH` | `[협력기관2]` | 단일 패턴 |

  **ASCII 다이어그램 보존 규칙**:
  - 박스 테두리 문자 (`┌`, `┐`, `└`, `┘`, `│`, `─`, `├`, `┤`, `┬`, `┴`, `┼`) 는 변경 금지
  - 박스 내부 텍스트만 치환
  - 치환 후 문자열 길이가 다를 경우: 공백 패딩으로 박스 폭 유지 권장 (필수 아님, 레이아웃 깨짐 허용)

  **추가 발견분 처리 규칙 (CRITICAL)**:
  - 위 치환 목록은 **최소 수정 대상**임
  - 치환 적용 후 아래 grep 검증 실행
  - **검증 결과 0건이 아닌 경우**: 동일 규칙으로 남은 모든 항목 추가 치환
  - 반복: grep 결과가 0건이 될 때까지 치환 → 검증 반복

  **Must NOT do**:
  - 파일 구조 변경 금지
  - 프롬프트 템플릿 로직 변경 금지
  - 색상 코드, 크기 값 변경 금지

  **Parallelizable**: YES (with 5, 6)

  **References**:

  **Source File**:
  - `plugins/isd-generator/references/example_prompts.md` (Task 3 이후 경로)

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `grep -c "SKKU\|성균관대학교" plugins/isd-generator/references/example_prompts.md` → 0
  - [ ] `grep -c "삼성서울병원\|삼성병원" plugins/isd-generator/references/example_prompts.md` → 0
  - [ ] `grep -c "Harvard\|MGH" plugins/isd-generator/references/example_prompts.md` → 0
  - [ ] `grep -c "\[주관기관\]" plugins/isd-generator/references/example_prompts.md` → 1 이상
  - [ ] `grep -c "\[협력기관" plugins/isd-generator/references/example_prompts.md` → 1 이상
  - [ ] `wc -l plugins/isd-generator/references/example_prompts.md` → 1000+ lines (구조 유지)

  **Commit**: YES
  - Message: `security(isd): move and anonymize example_prompts.md`
  - Files: `plugins/isd-generator/references/example_prompts.md`
  - Pre-commit: grep 스캔

---

- [x] 5. guides 파일 익명화 (prompt_guide.md, data_collection_guide.md)

  **What to do**:
  - `plugins/isd-generator/references/guides/prompt_guide.md` 익명화
  - `plugins/isd-generator/references/guides/data_collection_guide.md` 익명화

  **prompt_guide.md 최소 대상 라인** (추가 발견분도 동일 규칙 적용):
  - Line 374: `"성균관대학교", "삼성서울병원"` → `"[주관기관]", "[협력기관1]"`
  - Line 419: `"SKKU 중심의 산학연 협력"` → `"[주관기관] 중심의 산학연 협력"`
  - Line 466: `"SKKU, 삼성서울병원, Harvard/MGH"` → `"[주관기관], [협력기관1], [협력기관2]"`

  **data_collection_guide.md 최소 대상 라인**:
  - Line 247: `HD현대중공업` → `[대기업A]`

  **추가 발견분 처리 규칙 (CRITICAL)**:
  - 위 라인은 **최소 수정 대상**임
  - 수정 후 아래 grep 검증 실행
  - **검증 결과 0건이 아닌 경우**: 남은 모든 항목을 Task 4와 동일한 치환 규칙으로 처리
    - 성균관대학교/SKKU → `[주관기관]`
    - 삼성서울병원/삼성병원 → `[협력기관1]`
    - Harvard/MGH → `[협력기관2]`
    - HD현대중공업/현대중공업 → `[대기업A]`
  - 반복: grep 결과가 0건이 될 때까지 치환 → 검증 반복

  **Must NOT do**:
  - 가이드 설명 로직 변경 금지
  - 포맷팅 규칙 변경 금지

  **Parallelizable**: YES (with 4, 6)

  **References**:

  **Source Files**:
  - `plugins/isd-generator/references/guides/prompt_guide.md:374, 419, 466`
  - `plugins/isd-generator/references/guides/data_collection_guide.md:247`

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `grep -c "SKKU\|성균관대학교\|삼성서울병원\|Harvard\|MGH" plugins/isd-generator/references/guides/prompt_guide.md` → 0
  - [ ] `grep -c "HD현대중공업\|현대중공업" plugins/isd-generator/references/guides/data_collection_guide.md` → 0

  **Commit**: YES
  - Message: `security(isd): anonymize institution names in guide files`
  - Files: `plugins/isd-generator/references/guides/prompt_guide.md`, `plugins/isd-generator/references/guides/data_collection_guide.md`
  - Pre-commit: grep 스캔

---

- [x] 6. Agent 파일 예시 익명화 (chapter1.md)

  **What to do**:
  - `plugins/isd-generator/agents/chapter1.md:399` 익명화
  - 현재: `- 네트워크: LG전자, 현대자동차, 현대위아 등 MoU`
  - 변경: `- 네트워크: [대기업A], [대기업B], [중견기업A] 등 MoU`

  **Must NOT do**:
  - Agent 로직 변경 금지
  - 예시 외 다른 텍스트 수정 금지

  **Parallelizable**: YES (with 4, 5)

  **References**:

  **Source File**:
  - `plugins/isd-generator/agents/chapter1.md:399`

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `grep -c "LG전자\|현대자동차\|현대위아" plugins/isd-generator/agents/chapter1.md` → 0
  - [ ] `grep -c "\[대기업" plugins/isd-generator/agents/chapter1.md` → 1 이상 (prefix 매칭)
  - [ ] `grep -c "\[중견기업" plugins/isd-generator/agents/chapter1.md` → 1 이상 (prefix 매칭)

  **Commit**: YES
  - Message: `security(isd): anonymize example company names in chapter1 agent`
  - Files: `plugins/isd-generator/agents/chapter1.md`
  - Pre-commit: grep 스캔

---

- [x] 7. Agent 파일 경로 업데이트

  **What to do**:
  - 6개 agent 파일의 `examples/` 참조를 새 경로로 변경:
    1. `plugins/isd-generator/agents/chapter1.md`
    2. `plugins/isd-generator/agents/chapter2.md`
    3. `plugins/isd-generator/agents/chapter3.md`
    4. `plugins/isd-generator/agents/chapter4.md`
    5. `plugins/isd-generator/agents/chapter5.md`
    6. `plugins/isd-generator/agents/figure.md`

  **경로 변경 규칙**:
  - `references/examples/chapter{N}_example_*.md` → `references/content_requirements/chapter{N}_requirements.md`
  - `references/examples/example_prompts.md` → `references/example_prompts.md`

  **중복 라인 처리 규칙**:
  - 기존에 같은 챕터의 여러 예시(예: `chapter1_example_aiagent.md`, `chapter1_example_ultracold.md`)가 있는 경우:
    - 첫 번째 예시 경로 → `content_requirements/chapter{N}_requirements.md`로 변경
    - 두 번째 예시 라인 → 삭제 (중복 제거)
  - 설명 텍스트 수정 허용 범위:
    - 경로 라벨만 변경 (예: "AI Agent 예시" → "Chapter 1 요구사항")
    - 설명 문장 자체는 유지

  **Must NOT do**:
  - Agent 로직/워크플로우 변경 금지
  - 새로운 기능 추가 금지

  **Parallelizable**: NO (depends on 1, 2, 4, 5, 6)

  **References**:

  **수정 대상 Agent 파일**:
  - `plugins/isd-generator/agents/chapter1.md` - examples/ 참조 포함
  - `plugins/isd-generator/agents/chapter2.md` - examples/ 참조 포함
  - `plugins/isd-generator/agents/chapter3.md` - examples/ 참조 포함
  - `plugins/isd-generator/agents/chapter4.md` - examples/ 참조 포함
  - `plugins/isd-generator/agents/chapter5.md` - examples/ 참조 포함
  - `plugins/isd-generator/agents/figure.md` - example_prompts.md 참조 포함

  **Tool Recommendations**:
  - `grep -rn "examples/" plugins/isd-generator/agents/` 로 대상 라인 확인
  - Edit 도구로 개별 수정

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `git grep "examples/" -- "plugins/isd-generator/agents/*.md"` → 0건
  - [ ] 각 chapter agent 파일에 `content_requirements/` 참조 존재
  - [ ] figure.md에 `references/example_prompts.md` 참조 존재 (examples/ 제거)

  **Commit**: YES
  - Message: `refactor(isd): update agent file paths from examples to new structure`
  - Files: `plugins/isd-generator/agents/*.md`
  - Pre-commit: `git grep "examples/" -- "plugins/isd-generator/agents/*.md"` → 0건

---

- [x] 8. examples/ 폴더 삭제

  **What to do**:
  - `plugins/isd-generator/references/examples/` 폴더 전체 삭제
  - Git에서 추적 제거

  **삭제 대상 파일 (example_prompts.md 제외 - 이미 이동됨)**:
  ```
  plugins/isd-generator/references/examples/
  ├── chapter1_example_aiagent.md
  ├── chapter1_example_ultracold.md
  ├── chapter2_example_aiagent.md
  ├── chapter2_example_ultracold.md
  ├── chapter3_example_aiagent.md
  ├── chapter3_example_multiagent.md
  ├── chapter4_example_aiagent.md
  ├── chapter4_example_ultracold.md
  ├── chapter5_example_aiagent.md
  └── chapter5_example_ultracold.md
  ```

  **실행 명령어**:
  ```bash
  rm -rf plugins/isd-generator/references/examples/
  git add -u plugins/isd-generator/references/examples/
  ```

  **Must NOT do**:
  - 로컬 백업 브랜치 생성 전 삭제 금지 (Task 0 완료 필수)
  - 다른 폴더 삭제 금지

  **Parallelizable**: NO (depends on 0, 7)

  **References**:
  - Task 0 완료 확인: `git branch | grep archive/examples-backup` (로컬 브랜치 존재)

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `ls plugins/isd-generator/references/examples/ 2>&1` → "No such file or directory"
  - [ ] `git status` → examples/ 폴더 삭제됨

  **Commit**: YES
  - Message: `security(isd): remove sensitive example files from main branch`
  - Files: `plugins/isd-generator/references/examples/` (삭제)
  - Pre-commit: `git branch | grep archive/examples-backup` → 출력 있음 (로컬 백업 확인)

---

- [x] 9. AGENTS.md 업데이트

  **What to do**:
  - 프로젝트 루트의 `AGENTS.md` 파일에서 구조 변경 반영
  - "WHERE TO LOOK" 테이블에서 examples 관련 항목 제거/수정
  - "STRUCTURE" 섹션에 새 폴더 구조 반영
  - 백업 브랜치 존재 명시

  **수정 대상**:
  - `AGENTS.md` 내 `examples/` 언급 → `archive/examples-backup 브랜치에 보관` 언급
  - `AGENTS.md` 내 구조 다이어그램 → `writing_patterns/`, `content_requirements/` 추가

  **Must NOT do**:
  - 다른 플러그인 문서 수정 금지
  - 구조 외 다른 내용 수정 금지

  **Parallelizable**: NO (depends on 8)

  **References**:

  **수정 대상**:
  - `AGENTS.md` - "STRUCTURE" 섹션
  - `AGENTS.md` - "WHERE TO LOOK" 테이블

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] `grep "examples/" AGENTS.md | grep -v "archive\|backup\|브랜치\|보관"` → 0건
  - [ ] `grep "writing_patterns\|content_requirements" AGENTS.md` → 존재

  **Commit**: YES
  - Message: `docs(isd): update AGENTS.md with new references structure`
  - Files: `AGENTS.md`
  - Pre-commit: 없음

---

- [x] 10. 최종 검증 및 테스트

  **What to do**:
  - 전체 보안 스캔 실행
  - Agent 파일 참조 무결성 검증
  - Chapter 3 agent 호출 테스트 (선택, 권장)

  **보안 스캔 명령어**:
  ```bash
  # 1. 현대 계열 스캔 (전체 isd-generator 대상)
  grep -rn "현대위아\|현대자동차\|현대중공업\|HD현대\|HMC" plugins/isd-generator/ \
    | grep -v "input_template.md"
  # 예상: 0건

  # 2. 프로젝트 예시 기관명 스캔
  grep -rn "SKKU\|성균관대학교\|삼성서울병원\|삼성병원\|Harvard\|MGH" plugins/isd-generator/ \
    | grep -v "input_template.md"
  # 예상: 0건

  # 3. 대기업명 스캔 (input_template.md 제외)
  grep -rn "LG전자\|삼성전자\|네이버\|카카오" plugins/isd-generator/ \
    | grep -v "input_template.md"
  # 예상: 0건

  # 4. examples/ 참조 스캔
  git grep "examples/" -- "plugins/isd-generator/"
  # 예상: 0건
  ```

  **폴더 구조 검증**:
  ```bash
  # 새 폴더 존재 확인
  ls plugins/isd-generator/references/writing_patterns/
  ls plugins/isd-generator/references/content_requirements/
  
  # 파일 개수 확인
  find plugins/isd-generator/references/ -type f -name "*.md" | wc -l
  # 예상: 정확히 24개
  # 계산: 현재 24개 - examples/ 삭제 10개 + 새 폴더 10개 = 24개
  # (example_prompts.md는 examples/ → references/로 이동하므로 총수 불변)
  # (examples/ 삭제 시 example_prompts.md는 이미 이동됨, 나머지 10개만 삭제)
  
  # 기대 파일 목록 검증 (삭제되어야 할 폴더)
  ls plugins/isd-generator/references/examples/ 2>&1
  # 예상: "No such file or directory"
  
  # 기대 파일 목록 검증 (존재해야 할 폴더/파일)
  # - references/document_templates/ (5개 파일)
  # - references/guides/ (7개 파일)
  # - references/input_template.md (1개)
  # - references/example_prompts.md (1개, 이동됨)
  # - references/writing_patterns/ (5개 파일, 새로 생성)
  # - references/content_requirements/ (5개 파일, 새로 생성)
  # 총합: 5 + 7 + 1 + 1 + 5 + 5 = 24개
  ```

  **Chapter 3 Agent 호출 테스트** (선택, 권장):
  
  **호출 방법** (marketplace.json 기준):
  - 플러그인: `isd-generator` 
  - 에이전트: `chapter3`
  - 호출 방식: Claude Code에서 `@isd-generator chapter3`를 사용하거나, Task 도구로 `subagent_type="chapter3"` (isd-generator 플러그인 활성화 상태에서)
  
  **테스트 입력**:
  ```
  연구 아이디어: 테스트 프로젝트
  핵심기술: 기술A, 기술B, 기술C
  연구기간: 5년
  ```
  
  **검증 기준**:
  - [ ] Agent 호출 시 "파일을 찾을 수 없음" 에러 없음 (경로 참조 정상)
  - [ ] 또는 간단히: `grep -l "content_requirements" plugins/isd-generator/agents/chapter3.md` → 파일 존재 (경로 업데이트 확인)

  **Must NOT do**:
  - 테스트 결과에 따른 추가 기능 개발 금지
  - 검증 외 다른 변경 금지

  **Parallelizable**: NO (최종 작업)

  **References**:

  **검증 기준**:
  - `plugins/isd-generator/references/guides/verification_rules.md` - 검증 규칙
  - `.claude-plugin/marketplace.json` - 플러그인 등록 정보

  **Acceptance Criteria**:

  **Manual Execution Verification:**
  - [ ] 보안 스캔 1~4: 모두 0건
  - [ ] 폴더 구조: 예상 파일 수 일치 (정확히 24개)
  - [ ] `references/examples/` 폴더 부재 확인
  - [ ] (선택) Chapter 3 경로 참조 확인: `grep "content_requirements" plugins/isd-generator/agents/chapter3.md` → 존재

  **Commit**: NO (검증만)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 2 | `feat(isd): add writing_patterns and content_requirements folders` | `references/writing_patterns/*`, `references/content_requirements/*` | `ls references/` |
| 4 | `security(isd): move and anonymize example_prompts.md` | `references/example_prompts.md` | grep 스캔 |
| 5 | `security(isd): anonymize institution names in guide files` | `references/guides/*.md` | grep 스캔 |
| 6 | `security(isd): anonymize example company names in chapter1 agent` | `agents/chapter1.md` | grep 스캔 |
| 7 | `refactor(isd): update agent file paths from examples to new structure` | `agents/*.md` | `git grep examples/` |
| 8 | `security(isd): remove sensitive example files from public branch` | `references/examples/` | `ls references/examples/` |
| 9 | `docs(isd): update AGENTS.md with new references structure` | `AGENTS.md` | `grep writing_patterns` |

---

## Success Criteria

### Verification Commands
```bash
# 1. 현대 계열 스캔
grep -rn "현대위아\|현대자동차\|현대중공업\|HD현대\|HMC" plugins/isd-generator/ \
  | grep -v "input_template.md"
# 예상: 0건

# 2. 프로젝트 기관명 스캔
grep -rn "SKKU\|성균관대학교\|삼성서울병원\|삼성병원\|Harvard\|MGH" plugins/isd-generator/ \
  | grep -v "input_template.md"
# 예상: 0건

# 3. 대기업명 스캔
grep -rn "LG전자\|삼성전자\|네이버\|카카오" plugins/isd-generator/ \
  | grep -v "input_template.md"
# 예상: 0건

# 4. examples/ 참조 스캔
git grep "examples/" -- "plugins/isd-generator/"
# 예상: 0건

# 5. 백업 브랜치 로컬 확인 (원격 push 금지)
git branch | grep archive/examples-backup
# 예상: 출력 있음 (로컬 브랜치)
```

### Final Checklist
- [x] 백업 브랜치(`archive/examples-backup`)가 **로컬에** 존재 (원격 push 금지 - public 저장소)
- [x] examples/ 폴더가 main에서 삭제됨
- [x] writing_patterns/ 폴더 5개 파일 생성됨 (구조 검증 통과)
- [x] content_requirements/ 폴더 5개 파일 생성됨 (크로스 챕터 일관성 포함)
- [x] example_prompts.md가 상위로 이동 및 익명화됨
- [x] prompt_guide.md, data_collection_guide.md 익명화됨
- [x] chapter1.md 예시 기업명 익명화됨
- [x] 6개 agent 파일 경로 업데이트됨
- [x] AGENTS.md 업데이트됨
- [x] 모든 보안 스캔 (1~4) 통과
- [x] 모든 커밋 완료됨
