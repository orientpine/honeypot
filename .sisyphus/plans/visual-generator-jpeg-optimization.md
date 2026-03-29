# Visual Generator JPEG Direct Save — SDK 버그 수정 + 파일 크기 최적화

## TL;DR

> **Quick Summary**: `generate_slide_images.py`의 SDK 호환성 버그(`part.as_image()`)를 수정하고, Gemini API가 반환하는 JPEG 바이트를 직접 저장하여 불필요한 PNG 변환을 제거합니다.
> 
> **Deliverables**:
> - `generate_slide_images.py` 수정 (SDK 버그 수정 + JPEG 직접 저장)
> - 하위 문서 `.png` → `.jpg` 참조 업데이트
> - 버전 3.3.1 → 3.4.0 + 메타데이터 동기화
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES — 2 waves
> **Critical Path**: Task 1,2 (parallel) → Task 3 → Task 4

---

## Context

### Original Request
`dev/doc/gemini_image_generation_bug_report.md` 버그 리포트 기반으로 `plugins/visual-generator/` 개선.

### Interview Summary
**Key Discussions**:
- 문서 Section 2: `google-genai v1.66.0`에서 `part.as_image()`가 `google.genai.types.Image`를 반환 (PIL Image 아님) → `'Image' object has no attribute 'mode'` 에러
- 문서 Section 7: JPEG 원본 바이트 직접 저장 제안 → 파일 크기 47% 절감
- Section 7이 Section 2 버그도 함께 해결 (PIL 경유 불필요)

**Research Findings**:
- 현재 소스 (`generate_slide_images.py:121`)에 `part.as_image()` 여전히 존재 — v3.3.1 변경 이력에 기록됐으나 소스에 미반영
- `import io` 누락 상태
- `_detect_image_mime()` 함수는 이미 존재 (v3.3.1 추가) — 확장자 무관하게 PIL로 MIME 감지
- `evaluate_image_quality()`는 확장자 무관 — `_detect_image_mime()`으로 동적 감지
- `isd-generator/skills/core-resources/scripts/generate_images.py:97`에 동일한 `part.as_image()` 버그 존재 → 별도 태스크로 추적

### Metis Review
**Identified Gaps** (addressed):
- **RGBA 엣지 케이스**: Section 7의 `else` 브랜치에서 RGBA 이미지를 JPEG로 저장하면 크래시 → `if pil_image.mode != "RGB"` 조건으로 수정
- **SKILL.md PNG 참조 누락**: 라인 8, 46에 "PNG" 참조 존재 → JPEG로 업데이트
- **renderer-agent.md 라인 356**: `rm` 명령에 `.png` 참조 → `.jpg`로 업데이트
- **기존 .png 파일 스킵 로직**: `.jpg`로 변경 후 기존 `.png` 파일 감지 불가 → breaking change로 문서화

---

## Work Objectives

### Core Objective
Gemini API의 JPEG 응답을 직접 저장하여 SDK 호환성 버그 수정 + 파일 크기 47% 절감.

### Concrete Deliverables
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` (7개 코드 변경)
- `plugins/visual-generator/skills/slide-renderer/SKILL.md` (2줄 업데이트)
- `plugins/visual-generator/agents/renderer-agent.md` (5줄 업데이트)
- `plugins/visual-generator/commands/visual-generate.md` (4줄 업데이트)
- 버전/메타데이터 4개 파일 업데이트

### Definition of Done
- [ ] `grep -r '\.png' plugins/visual-generator/ --include='*.py'` → 0 matches
- [ ] `grep -c '\.jpg' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` → 4 (라인 16 docstring + 152 quality_attempt + 211 cleanup + 397 output_file)
- [ ] `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('OK')"` → OK
- [ ] 4개 버전 파일 모두 동기화

### Must Have
- `part.as_image()` → `part.inline_data.data` 바이트 직접 사용
- JPEG 바이트 직접 저장 (PIL 디코딩/인코딩 없음)
- 비-JPEG fallback에서 RGBA → RGB 변환 (JPEG 호환)
- `import io` 추가
- 모든 하위 문서 `.png` → `.jpg` 업데이트

### Must NOT Have (Guardrails)
- `evaluate_image_quality()` 로직 변경 금지 — 이미 확장자 무관
- `_detect_image_mime()` 함수 변경 금지 — 이미 정상 동작
- `SYSTEM_INSTRUCTION` 변경 금지 — 출력 포맷과 무관
- 품질 임계값/평가 기준 변경 금지 — 범위 밖
- `isd-generator` 수정 금지 — 별도 태스크
- `--format` CLI 플래그 추가 금지 — JPEG 고정
- 스크립트 리팩터링 금지 — 최소 diff, 수술적 변경만

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: NO (API 키 필요한 스크립트)
- **Automated tests**: None (Gemini API 의존)
- **Framework**: N/A

### QA Policy
Every task includes agent-executed QA scenarios.
- **Script 검증**: Python AST 파싱으로 구문 검증 + grep으로 참조 일관성 확인
- **문서 검증**: grep으로 `.png` 잔여 참조 확인
- **버전 검증**: grep으로 4개 파일 버전 동기화 확인

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 2 tasks parallel):
├── Task 1: generate_slide_images.py 코드 수정 [quick]
└── Task 2: 하위 .md 문서 업데이트 [quick]

Wave 2 (After Wave 1 — sequential):
├── Task 3: 버전 범프 + 메타데이터 동기화 [quick]
└── Task 4: Git 커밋 [quick]

Wave FINAL (After ALL tasks):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 3, 4 | 1 |
| 2 | — | 3, 4 | 1 |
| 3 | 1, 2 | 4 | 2 |
| 4 | 3 | — | 2 |

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 → `quick`, T2 → `quick`
- **Wave 2**: **2** — T3 → `quick`, T4 → `quick` + `git-master`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. JPEG 직접 저장 최적화 적용 — `generate_slide_images.py`

  **What to do**:
  1. `import io`를 기존 `import re` (라인 23)와 `import shutil` (라인 24) 사이에 추가 (사실상 라인 23 뒤에 새 줄 삽입)
     - 참고: 현재 import 순서: `os, sys, time, json, re, shutil, argparse` — 알파벳 순 삽입
  2. 라인 16 독스트링: `(.png)` → `(.jpg)`
  3. 라인 115 주석: `PNG로 명시적 변환` → `원본 포맷 직접 저장`
  4. 라인 121~129 이미지 저장 로직 교체 (핵심 변경):
     ```python
     if source_mime == "image/jpeg":
         # JPEG 원본 바이트 직접 저장 (디코딩/재인코딩 없음)
         with open(save_path, "wb") as img_f:
             img_f.write(part.inline_data.data)
         print(f"  [저장] JPEG 원본 직접 저장")
     else:
         # JPEG이 아닌 경우만 PIL 경유 변환
         pil_image = PILImage.open(io.BytesIO(part.inline_data.data))
         if pil_image.mode != "RGB":
             pil_image = pil_image.convert("RGB")
         pil_image.save(save_path, format="JPEG", quality=95)
         print(f"  [변환] {source_mime} → JPEG")
     ```
     **주의**: `else` 브랜치의 모드 체크는 `if pil_image.mode != "RGB":` (RGBA 안전 — 원본 Section 7 문서의 코드와 다름!)
  5. 라인 152: `.png` → `.jpg` (품질 재시도 임시파일)
  6. 라인 211: `.png` → `.jpg` (임시파일 정리)
  7. 라인 397: `.png` → `.jpg` (최종 출력 파일)

  **Must NOT do**:
  - `evaluate_image_quality()` 변경 금지
  - `_detect_image_mime()` 변경 금지
  - `SYSTEM_INSTRUCTION` 변경 금지
  - 스크립트 전체 리팩터링 금지 — 문서 Section 7에 명시된 변경 지점만 수술적으로 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일, 7개 정확한 변경 지점, diff가 문서에 명시됨
  - **Skills**: []
    - 추가 스킬 불필요 — 변경 사항이 명확

  **Parallelization**:
  - **Can Run In Parallel**: YES (Task 2와 병렬)
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3, 4
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `dev/doc/gemini_image_generation_bug_report.md` Section 7.3 — 정확한 diff 코드가 제공됨. 단, **`else` 브랜치의 RGBA 안전 수정은 이 문서와 다름** — `if pil_image.mode not in ("RGB", "RGBA", "L"):` 대신 `if pil_image.mode != "RGB":` 사용
  - `dev/doc/gemini_image_generation_bug_report.md` Section 7.2 — 5개 변경 지점 라인 번호 테이블

  **API/Type References**:
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:115-130` — 현재 이미지 저장 로직 (교체 대상)
  - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py:218-231` — `_detect_image_mime()` (변경하지 않음, 참조용)

  **WHY Each Reference Matters**:
  - 버그 리포트의 diff는 정확한 코드를 제공하지만 RGBA 엣지 케이스 수정이 필요
  - `_detect_image_mime()`가 이미 확장자 무관하게 동작하므로 추가 수정 불필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Python 구문 검증
    Tool: Bash
    Preconditions: generate_slide_images.py 수정 완료
    Steps:
      1. python3 -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('Syntax OK')"
    Expected Result: "Syntax OK" 출력, exit code 0
    Failure Indicators: SyntaxError, IndentationError
    Evidence: .sisyphus/evidence/task-1-syntax-check.txt

  Scenario: import io 존재 확인
    Tool: Bash
    Preconditions: generate_slide_images.py 수정 완료
    Steps:
      1. grep -n 'import io' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: 정확히 1줄 매치 (import 섹션에 위치)
    Failure Indicators: 0 matches 또는 2+ matches
    Evidence: .sisyphus/evidence/task-1-import-check.txt

  Scenario: .png 참조 제거 확인
    Tool: Bash
    Preconditions: generate_slide_images.py 수정 완료
    Steps:
      1. grep -c '\.png' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: 0 (SYSTEM_INSTRUCTION 내부의 "png" 문자열은 `.png`가 아니므로 매치 안 됨)
    Failure Indicators: 1 이상
    Evidence: .sisyphus/evidence/task-1-png-removal.txt

  Scenario: .jpg 참조 정확성
    Tool: Bash
    Preconditions: generate_slide_images.py 수정 완료
    Steps:
      1. grep -n '\.jpg' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: 정확히 4줄: 라인 ~16 (docstring), ~152 (quality_attempt), ~211 (cleanup), ~397 (output_file)
    Failure Indicators: 4가 아닌 수
    Evidence: .sisyphus/evidence/task-1-jpg-refs.txt

  Scenario: part.as_image() 완전 제거 확인
    Tool: Bash
    Preconditions: generate_slide_images.py 수정 완료
    Steps:
      1. grep -c 'as_image' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
    Expected Result: 0
    Failure Indicators: 1 이상
    Evidence: .sisyphus/evidence/task-1-as-image-removal.txt

  Scenario: RGBA 안전 변환 검증 (모의 테스트)
    Tool: Bash
    Preconditions: Pillow 설치 완료
    Steps:
      1. python3 -c "
      import io
      from PIL import Image as PILImage
      # RGBA 이미지 생성
      img = PILImage.new('RGBA', (100,100), (255,0,0,128))
      # JPEG 변환 테스트 (스크립트의 else 브랜치 로직 시뮬레이션)
      if img.mode != 'RGB':
          img = img.convert('RGB')
      buf = io.BytesIO()
      img.save(buf, format='JPEG', quality=95)
      print(f'RGBA→RGB→JPEG OK, size={len(buf.getvalue())} bytes')
      "
    Expected Result: "RGBA→RGB→JPEG OK, size=NNN bytes" 출력
    Failure Indicators: 에러 발생
    Evidence: .sisyphus/evidence/task-1-rgba-safety.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `fix(visual-generator): JPEG direct save — SDK bug fix + 47% file size reduction`
  - Files: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`
  - Pre-commit: `python3 -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read())"`

---

- [x] 2. 하위 문서 `.png` → `.jpg` 참조 업데이트

  **What to do**:
  1. `plugins/visual-generator/skills/slide-renderer/SKILL.md`:
     - 라인 8: `"4K 16:9 PNG 이미지로 변환"` → `"4K 16:9 JPEG 이미지로 변환"`
     - 라인 46: `"4K, 16:9 비율 PNG"` → `"4K, 16:9 비율 JPEG"`
  2. `plugins/visual-generator/agents/renderer-agent.md`:
     - 라인 262: `01_비전_다이어그램.png` → `.jpg`
     - 라인 263: `02_기술_스펙.png` → `.jpg`
     - 라인 289: `01_비전_다이어그램.png` → `.jpg`
     - 라인 290: `02_기술_스펙.png` → `.jpg`
     - 라인 356: `rm ./output/visuals/images/03_기술_스펙.png` → `.jpg`
  3. `plugins/visual-generator/commands/visual-generate.md`:
     - 라인 121: `{output_folder}/images/01_*.png` → `.jpg`
     - 라인 122: `{output_folder}/images/02_*.png` → `.jpg`
     - 라인 227: `01_비전_다이어그램.png` → `.jpg`
     - 라인 228: `02_기술_스펙.png` → `.jpg`

  **Must NOT do**:
  - prompt-designer, content-organizer 등 다른 에이전트 수정 금지
  - scene-richness-spec, validation-rules 등 참조 문서 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 3개 파일, 단순 텍스트 치환, 각 파일 수 줄씩
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Task 1과 병렬)
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3, 4
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/slide-renderer/SKILL.md:8,46` — PNG 참조 2곳
  - `plugins/visual-generator/agents/renderer-agent.md:262,263,289,290,356` — PNG 참조 5곳
  - `plugins/visual-generator/commands/visual-generate.md:121,122,227,228` — PNG 참조 4곳

  **WHY Each Reference Matters**:
  - 이 참조들은 문서의 파일 트리 예시와 명령어 예시로, 실제 출력 확장자 변경을 반영해야 함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 전체 visual-generator .md 파일에서 .png 잔여 참조 확인
    Tool: Bash
    Preconditions: 3개 .md 파일 수정 완료
    Steps:
      1. grep -rn '\.png' plugins/visual-generator/ --include='*.md'
    Expected Result: 0 matches (모든 .png 참조가 .jpg로 교체됨)
    Failure Indicators: 1개 이상 매치
    Evidence: .sisyphus/evidence/task-2-md-png-check.txt

  Scenario: SKILL.md PNG→JPEG 변경 확인
    Tool: Bash
    Preconditions: SKILL.md 수정 완료
    Steps:
      1. grep -c 'JPEG' plugins/visual-generator/skills/slide-renderer/SKILL.md
    Expected Result: 2 이상 (라인 8, 46)
    Failure Indicators: 0 또는 1
    Evidence: .sisyphus/evidence/task-2-skill-jpeg.txt

  Scenario: renderer-agent.md .jpg 참조 확인
    Tool: Bash
    Preconditions: renderer-agent.md 수정 완료
    Steps:
      1. grep -c '\.jpg' plugins/visual-generator/agents/renderer-agent.md
    Expected Result: 5 (lines 262, 263, 289, 290, 356)
    Failure Indicators: 5가 아닌 수
    Evidence: .sisyphus/evidence/task-2-renderer-jpg.txt

  Scenario: visual-generate.md .jpg 참조 확인
    Tool: Bash
    Preconditions: visual-generate.md 수정 완료
    Steps:
      1. grep -c '\.jpg' plugins/visual-generator/commands/visual-generate.md
    Expected Result: 4 (lines 121, 122, 227, 228)
    Failure Indicators: 4가 아닌 수
    Evidence: .sisyphus/evidence/task-2-vg-jpg.txt
  ```

  **Commit**: YES (groups with Task 1)
  - Message: `fix(visual-generator): JPEG direct save — SDK bug fix + 47% file size reduction`
  - Files: `plugins/visual-generator/skills/slide-renderer/SKILL.md`, `plugins/visual-generator/agents/renderer-agent.md`, `plugins/visual-generator/commands/visual-generate.md`

---

- [x] 3. 버전 범프 + 메타데이터 동기화

  **What to do**:
  1. `plugins/visual-generator/.claude-plugin/plugin.json`: `"version": "3.3.1"` → `"3.4.0"`
  2. `.claude-plugin/marketplace.json`:
     - visual-generator `"version": "3.3.1"` → `"3.4.0"` (라인 32)
     - `metadata.version`: `"3.20.0"` → `"3.21.0"` (라인 8)
  3. `AGENTS.md`:
     - 상단 `**Version:** 3.20.0` → `3.21.0`
     - 상단 `**Generated:** 2026-03-23...` → `2026-03-25...`
  4. `README.md`:
     - 상단 `**Version**: 3.20.0` → `3.21.0`
     - 변경 이력 표에 새 행 추가:
       `| 3.21.0 | 2026-03-25 | visual-generator v3.4.0: JPEG 원본 직접 저장 — SDK 호환성 버그 수정(part.as_image() → inline_data.data 직접 사용), PNG 불필요 변환 제거로 파일 크기 47% 절감, RGBA 안전 변환 추가 |`

  **Must NOT do**:
  - 다른 플러그인의 버전 변경 금지
  - README 구조 변경 금지 — 버전과 변경 이력 행만 추가

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 4개 파일, 각 파일 1~3줄 변경, 패턴이 명확
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 2)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1, 2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json:3` — 현재 `"3.3.1"`
  - `.claude-plugin/marketplace.json:8,32` — metadata.version과 visual-generator version
  - `AGENTS.md:3-4` — Version과 Generated 날짜
  - `README.md` — Version 필드와 변경 이력 표

  **WHY Each Reference Matters**:
  - 프로젝트 규칙에 의해 모든 버전 필드는 동기화되어야 함 (AGENTS.md → MANDATORY: Version Management 참조)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: plugin.json 버전 확인
    Tool: Bash
    Preconditions: plugin.json 수정 완료
    Steps:
      1. grep '"3.4.0"' plugins/visual-generator/.claude-plugin/plugin.json
    Expected Result: 1 match
    Evidence: .sisyphus/evidence/task-3-plugin-version.txt

  Scenario: marketplace.json 동기화 확인
    Tool: Bash
    Preconditions: marketplace.json 수정 완료
    Steps:
      1. grep '"3.4.0"' .claude-plugin/marketplace.json
      2. grep '"3.21.0"' .claude-plugin/marketplace.json
    Expected Result: 각각 1 match (visual-generator version, metadata.version)
    Evidence: .sisyphus/evidence/task-3-marketplace-version.txt

  Scenario: AGENTS.md/README.md 버전 확인
    Tool: Bash
    Preconditions: AGENTS.md, README.md 수정 완료
    Steps:
      1. grep '3.21.0' AGENTS.md README.md
      2. grep '2026-03-25' AGENTS.md
    Expected Result: 각각 match
    Evidence: .sisyphus/evidence/task-3-docs-version.txt
  ```

  **Commit**: YES (단독)
  - Message: `chore(visual-generator): bump to v3.4.0 + sync metadata`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`

---

- [x] 4. Git 커밋 생성

  **What to do**:
  1. Commit 1 (feature): Task 1 + Task 2 파일 합쳐서 커밋
     - Message: `fix(visual-generator): JPEG direct save — SDK bug fix + 47% file size reduction`
     - Files:
       - `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py`
       - `plugins/visual-generator/skills/slide-renderer/SKILL.md`
       - `plugins/visual-generator/agents/renderer-agent.md`
       - `plugins/visual-generator/commands/visual-generate.md`
  2. Commit 2 (chore): Task 3 파일 커밋
     - Message: `chore(visual-generator): bump to v3.4.0 + sync metadata`
     - Files:
       - `plugins/visual-generator/.claude-plugin/plugin.json`
       - `.claude-plugin/marketplace.json`
       - `AGENTS.md`
       - `README.md`

  **Must NOT do**:
  - `git push` 실행 금지 — Final Verification 후 사용자 확인 후에만
  - `--force` 사용 금지
  - `.env` 또는 `dev/` 폴더 파일 커밋 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 표준 git add + commit 2회
  - **Skills**: [`git-master`]
    - `git-master`: Git 커밋 워크플로우 전문 스킬

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Wave 2, after Task 3)
  - **Blocks**: None
  - **Blocked By**: Task 3

  **References**:

  **Pattern References**:
  - `AGENTS.md` → Commit Strategy 섹션 — 프로젝트 커밋 컨벤션

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 2개 커밋 생성 확인
    Tool: Bash
    Preconditions: Task 1-3 완료
    Steps:
      1. git log --oneline -2
    Expected Result: 최근 2개 커밋이 각각 fix(visual-generator)와 chore(visual-generator)
    Evidence: .sisyphus/evidence/task-4-git-log.txt

  Scenario: working tree clean 확인 (커밋 대상 파일 기준)
    Tool: Bash
    Preconditions: 두 커밋 모두 완료
    Steps:
      1. git diff HEAD --quiet
      2. git diff --cached --quiet
    Expected Result: 두 명령 모두 exit code 0 (tracked 파일 기준 변경 없음)
    Note: .sisyphus/evidence/ 내 QA 증거 파일은 untracked 중간 산출물이며, clean-tree 판정에서 제외한다.
    Evidence: .sisyphus/evidence/task-4-git-status.txt
  ```

  **Commit**: N/A (이 태스크 자체가 커밋 생성)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run grep). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Review `generate_slide_images.py` for: syntax correctness, `import io` placement, RGBA safety, no remaining `part.as_image()`, consistent `.jpg` references. Check for `as any`/unused imports/console.log patterns.
  Output: `Build [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test grep patterns, syntax checks, version sync. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git diff). Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Commit 1**: `fix(visual-generator): JPEG direct save — SDK bug fix + 47% file size reduction` — generate_slide_images.py, SKILL.md, renderer-agent.md, visual-generate.md
- **Commit 2**: `chore(visual-generator): bump to v3.4.0 + sync metadata` — plugin.json, marketplace.json, AGENTS.md, README.md

---

## Success Criteria

### Verification Commands
```bash
# 1. Python 구문 검증
python3 -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read()); print('Syntax OK')"
# Expected: Syntax OK

# 2. .png 잔여 참조 확인 (스크립트)
grep -c '\.png' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
# Expected: 0

# 3. .png 잔여 참조 확인 (문서)
grep -rn '\.png' plugins/visual-generator/ --include='*.md'
# Expected: (empty)

# 4. part.as_image() 완전 제거
grep -c 'as_image' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
# Expected: 0

# 5. 버전 동기화
grep '"3.4.0"' plugins/visual-generator/.claude-plugin/plugin.json .claude-plugin/marketplace.json
# Expected: 2 matches

# 6. 메타데이터 동기화
grep '3.21.0' .claude-plugin/marketplace.json AGENTS.md README.md
# Expected: 3+ matches
```

### Final Checklist
- [ ] `part.as_image()` 완전 제거, `inline_data.data` 직접 사용
- [ ] JPEG 바이트 직접 저장 (JPEG 경로), PIL fallback (비-JPEG 경로)
- [ ] RGBA → RGB 안전 변환 (else 브랜치)
- [ ] `import io` 추가
- [ ] 모든 `.png` 참조 → `.jpg` (스크립트 + 문서)
- [ ] SKILL.md "PNG" → "JPEG"
- [ ] 버전 3.4.0 + 메타데이터 3.21.0 동기화
- [ ] 2개 atomic 커밋 생성
- [ ] working tree clean (tracked 파일 기준 — `.sisyphus/evidence/` QA 증거 파일은 untracked 중간 산출물로 제외)

---

## Follow-Up (OUT OF SCOPE)

> **isd-generator SDK 버그**: `plugins/isd-generator/skills/core-resources/scripts/generate_images.py:97`에 동일한 `part.as_image()` 버그 존재. 동일 패턴 수정 필요하나 별도 태스크로 추적.
