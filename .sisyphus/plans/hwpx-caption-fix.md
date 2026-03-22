# HWPX 이미지 캡션 누락 수정

## TL;DR

> **Quick Summary**: `xml_writer.py`의 `build_fragment()`가 `image_ref` 블록 처리 시 캡션 텍스트 문단을 출력하지 않아 HWPX 결과물에서 이미지 캡션 15개가 전부 누락됨. `build_fragment()`에 `paragraph_from_segments()` 기반 캡션 문단 출력을 추가하고, dead code 정리 및 E2E 검증을 보강함.
>
> **Deliverables**:
> - `xml_writer.py` — `build_fragment()` 캡션 출력 로직 추가 + dead code (`build_image_with_caption()`) 삭제
> - `test_xml_writer_images.py` — dead code 테스트 제거 + 새 캡션 동작 테스트 추가
> - `validate.py` — 캡션 카운트 E2E 검증 함수 추가
>
> **Estimated Effort**: Short (4 tasks, ~2시간)
> **Parallel Execution**: YES — 2 waves + Final
> **Critical Path**: Task 1 (RED) → Task 2 (GREEN) → Task 3/4 (parallel) → F1-F4

---

## Context

### Original Request
HWPX 출력물에 이미지 캡션(`*그림 3-1: ...*`) 15개 전부 누락되는 버그 수정. 사용자가 상세 원인 분석 및 수정 방안 A를 제안함.

### Interview Summary
**Key Discussions**:
- **근본 원인**: `build_fragment()` L575-577이 `build_image_placeholder(image_counter)`만 호출하여 `<!--IMAGE:imageN-->` HTML 코멘트만 출력. `block["caption"]`, `block["caption_id"]` 데이터가 버려짐.
- **수정 방안**: 방안 A 채택 — 플레이스홀더 뒤에 캡션 `<hp:p>` 문단 추가. `image_embedder.py` 수정 불필요.
- **Dead code**: `build_image_with_caption()` (L419-497)은 dead code. 네임스페이스 불일치(`hp:para` vs `hp:p`)로 재활용 불가. 삭제 결정.

**Research Findings**:
- `md_parser.py`: 두 가지 파싱 경로 확인. Legacy `<그림 N-M: text>` 형식은 `id` 필드만 사용 (NO `caption_id`). Markdown `![alt](path)` + `*그림 N-M: text*` 형식은 `caption_id` 필드 사용.
- `xml_escape()`: L53-60에 로컬 정의. 사용 가능.
- `IdGenerator`: L559에서 `build_fragment()` 내 생성. `next_paragraph_id()` 사용 가능.
- `paragraph_from_segments()`: L171-210 정의. 모든 블록 타입이 사용하는 표준 헬퍼.
- `image_embedder.py`: `load_mapping_from_parsed()`에서 `caption: ""` 하드코딩하지만, 캡션은 xml_writer에서 처리하므로 수정 불필요.
- 테스트: pytest 7.0+, `test_xml_writer_images.py` (dead code 테스트), `test_e2e_pipeline.py` (11단계 통합 테스트, L360-361 캡션 카운트 검증).

### Metis Review
**Identified Gaps** (addressed):
- **CRITICAL — `caption_id` vs `id` 필드명 불일치**: Legacy 형식은 `caption_id` 키가 없고 `id`만 존재. 수정 코드에서 `block.get("caption_id") or block.get("id")` 패턴 필수. → Guardrail로 반영.
- **`paragraph_from_segments()` 사용 권장**: raw XML 대신 기존 헬퍼 함수 사용으로 `<hp:p>` 6개 필수 속성 보장 + 코드 패턴 일관성. → 구현 방식 변경 반영.
- **빈 캡션 가드**: `caption_id`와 `caption` 모두 falsy일 때 캡션 문단 생략 필수. `.strip()` 적용. → Guardrail로 반영.
- **E2E 테스트 현재 실패 추정**: L360-361의 `caption_count >= 15` 단언이 캡션 전부 누락 상태에서 실패 중일 가능성 높음. → 회귀 검증 게이트로 활용.

---

## Work Objectives

### Core Objective
`build_fragment()`에서 `image_ref` 블록의 캡션 데이터를 `<hp:p>` 문단으로 출력하여, HWPX 결과물에 이미지 캡션이 정상적으로 포함되도록 수정한다.

### Concrete Deliverables
- `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` — 캡션 출력 로직 추가 + dead code 삭제
- `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py` — 테스트 업데이트
- `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py` — 캡션 카운트 검증 추가

### Definition of Done
- [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v` — ALL PASS
- [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py` — 단위 테스트 전체 PASS
- [ ] (조건부) dev/ 픽스처 존재 시: `python -m pytest ...test_e2e_pipeline.py -v -m integration` — PASS

### Must Have
- 캡션 `<hp:p>` 문단이 `<!--IMAGE:imageN-->` 플레이스홀더 뒤에 출력됨
- `caption_id`/`id` 필드명 불일치 모두 처리 (`block.get("caption_id") or block.get("id")`)
- `paragraph_from_segments()` 사용 (raw XML 금지)
- 빈 캡션 가드 (caption_id/caption 모두 falsy → 문단 생략)
- `xml_escape()` 적용
- Dead code `build_image_with_caption()` (L419-497) 삭제
- 캡션 카운트 E2E 검증 (`validate.py`)

### Must NOT Have (Guardrails)
- `md_parser.py` 수정 — 기존 파싱 로직 정상 작동
- `image_embedder.py` 수정 — 캡션은 xml_writer에서 처리
- `require_styles()`에 `image_caption` 추가 — `body` 폴백이 의도된 설계
- `hp:para`, `hp:align="CENTER"` 사용 — dead code의 비표준 네임스페이스
- raw XML 문자열 연결 in `build_fragment()` — `paragraph_from_segments()` 사용
- `build_image_placeholder()` 변경 — `<!--IMAGE:imageN-->` 코멘트는 `image_embedder.py`가 필요
- `image_counter`를 캡션 ID 폴백으로 사용 — `그림 1` 형식은 `\d+-\d+` regex 패턴 불일치

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest 7.0+)
- **Automated tests**: TDD (RED → GREEN → REFACTOR)
- **Framework**: pytest
- **Each task follows**: RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence: 실행 에이전트가 QA 커맨드 출력을 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`에 **직접 저장**해야 함.
Evidence 저장 방법: 각 QA 커맨드 실행 후 stdout/stderr 출력을 Write 도구로 에비던스 파일에 기록.

### 환경 주의사항
- **Shell**: Windows `cmd.exe` — Unix `grep`/`ls`/`export` 사용 금지
- **대체 도구**: Grep 도구 (내장 테스트 검색), Read/Glob 도구 (파일 찾기), `python -c` (크로스 플랫폼 명령)
- F1-F4 QA 시나리오는 에이전트의 내장 도구(Grep, Read, Glob, Bash) 또는 `python -c`를 사용하여 실행

- **Unit tests**: Use Bash (`python -m pytest ...`) — run tests, assert PASS/FAIL counts
- **E2E pipeline**: Use Bash (`python -m pytest ... -m integration`) — run full pipeline, verify caption count

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — TDD RED phase):
└── Task 1: Add failing unit tests for caption emission [quick]

Wave 2 (After Wave 1 — TDD GREEN + REFACTOR):
└── Task 2: Implement caption emission + delete dead code [deep]

Wave 3 (After Wave 2 — parallel validation):
├── Task 3: Add caption count validation to validate.py [quick]
└── Task 4: Run full test suite + verify E2E regression gate [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 2 → Task 3/4 → F1-F4 → user okay
Parallel Speedup: Wave 3 runs 2 tasks concurrently
Max Concurrent: 2 (Wave 3)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2 | 1 |
| 2 | 1 | 3, 4 | 2 |
| 3 | 2 | F1-F4 | 3 |
| 4 | 2 | F1-F4 | 3 |

### Agent Dispatch Summary

- **Wave 1**: 1 task — T1 → `quick`
- **Wave 2**: 1 task — T2 → `deep`
- **Wave 3**: 2 tasks — T3 → `quick`, T4 → `quick`
- **FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs


- [x] 1. [RED] 캡션 출력 실패 테스트 추가 — `test_xml_writer_images.py`

  **What to do**:
  - `test_xml_writer_images.py`에 `build_fragment()` 캡션 동작을 검증하는 새 테스트 함수 4개 추가:
    1. `test_build_fragment_caption_markdown_format` — Markdown 형식 블록(`caption_id="3-1"`, `caption="비전 개념도"`)에서 `build_fragment()` 호출 시 `<!--IMAGE:image1-->` 뒤에 `그림 3-1: 비전 개념도` 텍스트가 포함된 `<hp:p>` 문단이 출력되는지 검증
    2. `test_build_fragment_caption_legacy_format` — Legacy 형식 블록(`id="3-1"`, `caption="비전 개념도"`, `caption_id` 키 없음)에서도 동일하게 `그림 3-1: 비전 개념도` 캡션 출력 검증
    3. `test_build_fragment_caption_empty_skip` — `caption=""`, `caption_id=None`, `id=None` 블록에서 캡션 `<hp:p>` 문단이 생성되지 않는지 검증 (플레이스홀더만 출력)
    4. `test_build_fragment_caption_xml_escape` — `caption="A & B <=> C"` 특수문자가 `&amp;`, `&lt;`, `&gt;`로 올바르게 이스케이프되는지 검증
  - 기존 `sample_styles()` 픽스처를 재사용하되, `image_caption` 키 유무에 따른 body 폴백도 테스트
  - 테스트 블록 구조: `{"type": "image_ref", "path": "./images/01.png", "caption": "...", "caption_id": "3-1", "filename": "01.png"}` + heading/paragraph 블록과 함께 `{"blocks": [...]}` 형태로 전달
  - 이 시점에서 테스트는 **FAIL해야 함** (아직 `build_fragment()`에 캡션 로직 없음)

  **Must NOT do**:
  - `build_image_with_caption()` 관련 기존 테스트 수정 (Task 2에서 처리)
  - `xml_writer.py` 구현 코드 수정 (이 태스크는 테스트만 추가)
  - `build_fragment()` 외부에서 캡션 생성하는 테스트 작성 (캡션은 반드시 `build_fragment()` 내부에서 처리)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 테스트 파일에 4개 테스트 함수 추가. 기존 패턴(`sample_styles()`, `importlib` 로딩) 그대로 사용.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - N/A (프로젝트 내부 Python 테스트, 외부 스킬 불필요)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (단독)
  - **Blocks**: Task 2
  - **Blocked By**: None (즉시 시작 가능)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py` 전체 — 기존 테스트 구조, `sample_styles()` 픽스처 (L16-44), `sample_image_block()` 픽스처 (L47-60), `importlib.util.spec_from_file_location()` 모듈 로딩 패턴 (L6-13)
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_tables.py:test_build_fragment_table_merge_from_cell_dict` — `build_fragment()` 호출 패턴 (`build_fragment(parsed, styles)`), 결과 XML 파싱 방법
  - `plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py` — 공유 픽스처 (`project_root`, `scripts_dir` 경로)

  **API/Type References** (contracts to implement against):
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:build_fragment()` (L553-586) — 함수 시그니처 `build_fragment(parsed: dict, config: dict, wrap_section: bool = False) -> str`
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` L156-180 — `image_ref` 블록 구조 (Markdown 형식: `type`, `id`, `path`, `alt`, `caption`, `caption_id`, `filename`)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` L148-154 — `image_ref` 블록 구조 (Legacy 형식: `type`, `id`, `caption` — `caption_id` 키 없음)

  **Test References** (testing patterns to follow):
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py:test_build_image_with_caption_structure` (L63-80) — `assert "그림" in output` 패턴, XML 속성 검증 패턴

  **WHY Each Reference Matters**:
  - `test_xml_writer_images.py`: 모듈 로딩 방식(`spec_from_file_location`), 스타일 픽스처 구조, 단언 패턴을 그대로 복사해야 함
  - `build_fragment()` 시그니처: 테스트에서 올바른 인자(`parsed dict`, `styles dict`)를 전달해야 함
  - `md_parser.py` 블록 구조: 테스트 입력 데이터의 정확한 필드명과 타입을 알아야 함. 특히 Legacy vs Markdown 형식의 필드 차이가 핵심

  **Acceptance Criteria**:

  **TDD (RED phase):**
  - [ ] 4개 테스트 함수 작성 완료
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "build_fragment_caption"` → 4 FAILED (캡션 로직 미구현 상태)
  - [ ] 기존 테스트(`test_build_image_with_caption_*`)는 여전히 PASS

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: RED 테스트 4개 실패 확인
    Tool: Bash
    Preconditions: xml_writer.py 미수정 상태
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "build_fragment_caption" 2>&1
      2. 출력에서 "4 failed" 확인
      3. 기존 테스트 확인: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "not build_fragment_caption" 2>&1
      4. 출력에서 "passed" 확인, "failed" 없음
    Expected Result: 새 테스트 4개 FAIL + 기존 테스트 전부 PASS
    Failure Indicators: 새 테스트가 PASS하면 버그가 아니거나 테스트가 잘못됨. 기존 테스트가 FAIL하면 테스트 추가 과정에서 기존 코드를 깨뜨림.
    Evidence: .sisyphus/evidence/task-1-red-tests-fail.txt
  ```

  **Evidence to Capture:**
  - [ ] task-1-red-tests-fail.txt — pytest 출력 (4 FAILED 확인)
  - [ ] task-1-existing-tests-pass.txt — 기존 테스트 PASS 확인

  **Commit**: YES
  - Message: `test(hwpx): add failing tests for caption emission in build_fragment`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py`
  - Pre-commit: `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "not build_fragment_caption"` (기존 테스트 PASS 확인)

---

- [x] 2. [GREEN+REFACTOR] 캡션 출력 구현 + dead code 삭제 — `xml_writer.py` + `test_xml_writer_images.py`

  **What to do**:
  - **GREEN**: `xml_writer.py`의 `build_fragment()` L575-577 영역을 수정하여 `image_ref` 블록 처리 시 캡션 `<hp:p>` 문단을 출력:
    ```python
    elif btype == "image_ref":
        out.append(build_image_placeholder(image_counter))
        # 캡션이 있으면 paragraph_from_segments()로 텍스트 문단 출력
        caption_id = block.get("caption_id") or block.get("id")
        caption = (block.get("caption") or "").strip()
        if caption_id or caption:
            caption_text = (
                f"그림 {caption_id}: {caption}"
                if caption_id and caption
                else f"그림 {caption_id}" if caption_id
                else caption
            )
            caption_style = styles.get(
                "image_caption", styles.get("body", {})
            )
            out.append(
                paragraph_from_segments(
                    pid=ids.next_paragraph_id(),
                    para_pr_id=str(caption_style.get("paraPrIDRef", "0")),
                    default_char_pr_id=str(
                        caption_style.get("charPrIDRef", "0")
                    ),
                    bold_char_pr_id=str(
                        styles["bold"]["charPrIDRef"]
                    ),
                    segments=[{"text": caption_text, "type": "plain"}],
                )
            )
        image_counter += 1
    ```
  - **REFACTOR**: dead code `build_image_with_caption()` 함수 (L419-497) 삭제
  - **REFACTOR**: `test_xml_writer_images.py`에서 dead code 관련 테스트 3개 삭제:
    - `test_build_image_with_caption_structure`
    - `test_build_image_with_caption_uses_image_caption_style`
    - `test_build_image_with_caption_falls_back_to_body`
    - `sample_image_block()` 픽스처도 사용처 없으면 삭제
  - Task 1에서 추가한 4개 테스트가 모두 PASS하는지 확인

  **Must NOT do**:
  - `md_parser.py` 수정
  - `image_embedder.py` 수정
  - `require_styles()`에 `image_caption` 추가
  - `hp:para`, `hp:align="CENTER"` 사용
  - `build_image_placeholder()` 변경
  - raw XML 문자열 연결 (`f'<hp:p ...'` 형태) — 반드시 `paragraph_from_segments()` 사용

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 핵심 버그 수정 + dead code 삭제 + 테스트 정리. 정확한 필드명 처리(`caption_id`/`id` 불일치), `paragraph_from_segments()` 호출 패턴, dead code 삭제 시 참조 무결성 보장이 필요.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - N/A

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (단독)
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: Task 1

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:build_paragraph()` (L229-237) — `paragraph_from_segments()` 호출 패턴. `pid=ids.next_paragraph_id()`, `para_pr_id=str(body["paraPrIDRef"])`, `default_char_pr_id=str(body["charPrIDRef"])`, `bold_char_pr_id=str(styles["bold"]["charPrIDRef"])`, `segments=normalize_segments(block)` 구조를 그대로 따라야 함
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:paragraph_from_segments()` (L171-210) — 캡션 문단 생성에 사용할 헬퍼 함수. `<hp:p id="{pid}" paraPrIDRef="{para_pr_id}" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">` 형식의 6개 필수 속성을 자동 생성
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:build_fragment()` (L553-586) — `elif btype == "image_ref":` 분기 (L575-577)가 수정 대상. `ids`, `styles`, `image_counter` 변수 스코프 확인
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:xml_escape()` (L53-60) — XML 특수문자 이스케이프 (paragraph_from_segments 내부에서 자동 호출됨 — segments 텍스트에 이미 적용 필요 없음 확인 필요)

  **API/Type References** (contracts to implement against):
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:build_image_with_caption()` (L419-497) — 삭제 대상. L465 `config.get("image_caption", config.get("body", {}))` 캡션 스타일 해석 패턴 참조 (새 코드에서 동일 패턴 사용)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py:IdGenerator` (L63-78) — `next_paragraph_id()` 반환 타입: `str`
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` L148-180 — 두 가지 `image_ref` 블록 형식. Legacy: `{"type": "image_ref", "id": "3-1", "caption": "text"}`. Markdown: `{"type": "image_ref", "id": None, "path": "...", "caption": "text", "caption_id": "3-1", "filename": "..."}`. **`block.get("caption_id") or block.get("id")` 패턴 필수**

  **Test References**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py` — Task 1에서 추가한 4개 테스트가 이 태스크의 성공 기준. dead code 테스트 3개 (`test_build_image_with_caption_*`) 삭제 대상.

  **External References**:
  - 없음 (프로젝트 내부 수정)

  **WHY Each Reference Matters**:
  - `build_paragraph()` L229-237: `paragraph_from_segments()` 호출의 정확한 인자 패턴. 이 패턴을 벗어나면 필수 속성 누락 발생
  - `paragraph_from_segments()` L171-210: `segments` 파라미터가 `[{"text": ..., "type": "plain"}]` 형식인지, 내부에서 `xml_escape` 처리하는지 확인 필요
  - `build_image_with_caption()` L419-497: 삭제할 코드 범위. 이 함수가 참조하는 다른 함수/변수가 없는지 확인 (dead code 삭제의 안전성)
  - md_parser 블록 구조: `caption_id` vs `id` 필드명 차이가 이번 수정의 핵심

  **Acceptance Criteria**:

  **TDD (GREEN phase):**
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "build_fragment_caption"` → 4 PASSED
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v` → ALL PASSED (dead code 테스트 삭제 후 에러 없음)
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py` → ALL PASSED
  - [ ] `build_image_with_caption` 함수가 xml_writer.py에서 완전히 제거됨
  - [ ] `build_image_with_caption` 참조가 test_xml_writer_images.py에서 완전히 제거됨

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: GREEN — 캡션 테스트 4개 통과
    Tool: Bash
    Preconditions: Task 1 완료 (4개 실패 테스트 존재)
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "build_fragment_caption" 2>&1
      2. 출력에서 "4 passed" 확인
    Expected Result: 4 PASSED, 0 FAILED
    Failure Indicators: 1개라도 FAIL → build_fragment() 캡션 로직 오류
    Evidence: .sisyphus/evidence/task-2-green-tests-pass.txt

  Scenario: Dead code 삭제 후 전체 테스트 통과
    Tool: Bash
    Preconditions: build_image_with_caption() 삭제, 관련 테스트 삭제
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v 2>&1
      2. 출력에서 "failed" 없음, "error" 없음 확인
      3. ast_grep_search로 xml_writer.py에서 "build_image_with_caption" 참조 없음 확인
    Expected Result: ALL PASSED, dead function 완전 제거
    Failure Indicators: ImportError 또는 NameError → 삭제 범위 부정확
    Evidence: .sisyphus/evidence/task-2-dead-code-removed.txt

  Scenario: Legacy 형식(`id` only) 캡션 처리
    Tool: Bash
    Preconditions: build_fragment() 수정 완료
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "legacy_format" 2>&1
      2. 출력에서 "1 passed" 확인
    Expected Result: Legacy 형식 블록에서 `block.get("caption_id") or block.get("id")` → `id` 값 사용, 캡션 정상 출력
    Failure Indicators: `그림 None:` 출력 → `id` 필드 폴백 누락
    Evidence: .sisyphus/evidence/task-2-legacy-format.txt
  ```

  **Evidence to Capture:**
  - [ ] task-2-green-tests-pass.txt — 4 PASSED
  - [ ] task-2-dead-code-removed.txt — 전체 테스트 PASS + dead code 부재 확인
  - [ ] task-2-legacy-format.txt — Legacy 형식 캡션 처리 확인

  **Commit**: YES
  - Message: `fix(hwpx): emit caption paragraph after image placeholder + remove dead code`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py`, `plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py`
  - Pre-commit: `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py`

---

- [x] 3. 캡션 카운트 검증 추가 — `validate.py`

  **What to do**:
  - `validate.py`에 `_caption_checks()` 함수 추가:
    ```python
    def _caption_checks(section_xml: str, parsed_path: str | None, errors: list, warnings: list) -> None:
        """Validate image caption count matches parsed blocks."""
        if not parsed_path:
            return
        import json
        with open(parsed_path, encoding="utf-8") as f:
            parsed = json.load(f)
        md_caption_count = sum(
            1 for b in parsed.get("blocks", [])
            if b.get("type") == "image_ref"
            and (b.get("caption_id") or b.get("id"))
            and (b.get("caption", "").strip())
        )
        import re
        hwpx_caption_count = len(re.findall(r"그림\s*\d+-\d+", section_xml))
        if md_caption_count != hwpx_caption_count:
            errors.append(
                f"Caption count mismatch: MD has {md_caption_count} captions, "
                f"HWPX has {hwpx_caption_count} caption paragraphs"
            )
    ```
  - `validate()` 메인 함수에서 `--parsed` CLI 인자를 새로 추가하고, section0.xml 읽은 후 `_caption_checks()` 호출
  - `--parsed` 인자가 없으면 캡션 검증 스킵 (기존 동작 유지)

  **Must NOT do**:
  - `validate.py`의 기존 검증 로직 수정
  - `--parsed` 인자를 필수로 만들기 (선택적이어야 함)
  - `image_embedder.py` 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 함수 추가 + CLI 인자 1개 추가. 기존 validate.py 패턴(`_image_checks`, `_structure_checks` 함수 구조) 따르기.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 4)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 2

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py:_image_checks()` (L117-244) — 기존 이미지 검증 함수 구조 (`errors`, `warnings` 리스트 인자 패턴, section XML 파싱 방법)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py` CLI 인자 처리 — `argparse` 사용 패턴, `--strict` 등 기존 인자 구조

  **API/Type References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` L148-180 — `image_ref` 블록의 `caption_id`/`id` 필드 구조 (검증 로직에서 두 필드 모두 체크)

  **WHY Each Reference Matters**:
  - `_image_checks()`: 동일한 `errors`/`warnings` 리스트 패턴을 따라야 메인 검증 루프와 호환됨
  - md_parser 블록 구조: 캡션 카운트 계산 시 `caption_id` or `id` 로직 필요

  **Acceptance Criteria**:

  - [ ] `_caption_checks()` 함수 추가됨
  - [ ] `--parsed` CLI 인자 추가됨 (선택적)
  - [ ] `--parsed` 없이 실행 시 기존 동작과 동일
  - [ ] 캡션 카운트 불일치 시 에러 메시지 출력

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 캡션 카운트 불일치 감지 (단위 테스트)
    Tool: Bash
    Preconditions: Task 2 완료, _caption_checks() 함수 추가됨
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'plugins/hwpx-generator/skills/hwpx-core/scripts'); from validate import _caption_checks; import json, tempfile, os; parsed = {'blocks': [{'type': 'image_ref', 'caption_id': '3-1', 'caption': 'test'}]}; tf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False); json.dump(parsed, tf); tf.close(); errors = []; _caption_checks('<root></root>', tf.name, errors, []); os.unlink(tf.name); print('ERRORS:', errors); assert len(errors) == 1 and 'Caption count mismatch' in errors[0], f'Expected mismatch error, got: {errors}'"
      2. 출력에서 "ERRORS: ['Caption count mismatch: MD has 1 captions, HWPX has 0 caption paragraphs']" 확인
    Expected Result: 캡션 1개 있는 parsed JSON vs 캡션 0개인 section XML → 에러 1개 발생
    Failure Indicators: assert 실패 → _caption_checks() 로직 오류. ImportError → 함수 미구현 또는 이름 오류.
    Evidence: .sisyphus/evidence/task-3-caption-validation.txt

  Scenario: --parsed 없이 실행 시 기존 동작 유지 (단위 테스트)
    Tool: Bash
    Preconditions: validate.py 수정 완료
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'plugins/hwpx-generator/skills/hwpx-core/scripts'); from validate import _caption_checks; errors=[]; _caption_checks('<root></root>', None, errors, []); print('ERRORS:', errors); assert len(errors)==0, f'Unexpected errors without parsed: {errors}'"
      2. 출력에서 "ERRORS: []" 확인 (parsed_path=None 이면 캡션 검증 스킵)
    Expected Result: parsed_path가 None이면 함수가 즉시 리턴하여 에러 0개
    Failure Indicators: 에러 발생 → None 가드 로직 미작동
    Evidence: .sisyphus/evidence/task-3-backward-compat.txt
  ```

  **Evidence to Capture:**
  - [ ] task-3-caption-validation.txt — 불일치 감지 확인
  - [ ] task-3-backward-compat.txt — 하위 호환성 확인

  **Commit**: YES
  - Message: `feat(hwpx): add caption count validation to validate.py`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py`
  - Pre-commit: `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py`

---

- [x] 4. 단위 테스트 스위트 + 조건부 E2E 회귀 검증

  **What to do**:
  - **필수**: 단위 테스트 스위트 실행 (dev 픽스처 의존 테스트 제외):
    ```bash
    python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_dev_data_exists.py
    ```
  - **조건부**: dev/ 픽스처 존재 여부 확인 후, 존재 시만 E2E 실행:
    ```bash
    python -c "import os; exists = all(os.path.exists(p) for p in ['dev/3\uc7a5.md', 'dev/4\uc7a5.md']); print('DEV_FIXTURES:', 'PRESENT' if exists else 'ABSENT')"
    # PRESENT 시만: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py -v -m integration
    ```
  - `test_e2e_pipeline.py`, `test_dev_data_exists.py`는 `dev/` 픽스처 필요. 현재 저장소에 없을 수 있음.
  - **픽스처 부재 시**: 단위 테스트만 PASS하면 충분. 에비던스에 "픽스처 부재로 E2E 스킵" 기록.

  **Must NOT do**:
  - 코드 수정
  - E2E 테스트 단언 기준 변경
  - 픽스처 부재 시 픽스처 생성 (스코프 밖)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 3)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 2

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py` L357-361 — 캡션 카운트 단언 (픽스처 존재 시)
  - `plugins/hwpx-generator/skills/hwpx-core/tests/` — 전체 테스트 디렉토리

  **Acceptance Criteria**:
  - [ ] 단위 테스트 (E2E/dev_data 제외) → ALL PASSED
  - [ ] 픽스처 존재 시: E2E PASSED / 부재 시: "스킵" 에비던스
  - [ ] 0 errors, 0 import failures

  **QA Scenarios (MANDATORY):**
  ```
  Scenario: 단위 테스트 스위트 통과
    Tool: Bash
    Preconditions: Task 1, 2, 3 완료
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_dev_data_exists.py 2>&1
      2. 출력에서 "failed" 없음, "error" 없음 확인
    Expected Result: ALL PASSED
    Evidence: .sisyphus/evidence/task-4-full-suite.txt

  Scenario: 조건부 E2E 캡션 회귀 게이트
    Tool: Bash
    Steps:
      1. python -c "import os; exists = all(os.path.exists(p) for p in ['dev/3\uc7a5.md', 'dev/4\uc7a5.md']); print('DEV_FIXTURES:', 'PRESENT' if exists else 'ABSENT'); exit(0 if exists else 1)" 2>&1
      2-a. PRESENT: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py -v -m integration 2>&1 → "PASSED" 확인
      2-b. ABSENT: echo "E2E skipped: dev fixtures not present" → 에비던스 기록
    Expected Result: 픽스처 있으면 E2E PASSED, 없으면 스킵 기록
    Evidence: .sisyphus/evidence/task-4-e2e-captions.txt
  ```

  **Evidence to Capture:**
  - [ ] task-4-full-suite.txt
  - [ ] task-4-e2e-captions.txt

  **Commit**: NO (검증만 수행)

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`

  **QA Scenarios:**
  ```
  Scenario: Must Have 항목 준수 확인
    Tool: Grep 도구 + Read 도구 + Glob 도구
    Steps:
      1. Grep 도구로 xml_writer.py에서 "paragraph_from_segments" 검색 → 캡션 문단에서 사용 확인
      2. Grep 도구로 xml_writer.py에서 "caption_id" 검색 → caption_id/id 이중 처리 확인
      3. Grep 도구로 xml_writer.py scripts/에서 "build_image_with_caption" 검색 → 0 결과 (dead code 삭제)
      4. Grep 도구로 validate.py에서 "_caption_checks" 검색 → 캡션 검증 함수 존재
      5. Glob 도구로 .sisyphus/evidence/task-*.txt 패턴 검색 → 에비던스 파일 존재 확인
      6. 겁증 결과를 Write 도구로 .sisyphus/evidence/final-qa/f1-compliance.txt에 저장
    Expected Result: Must Have 7개 항목 중 7개 충족, evidence 파일 전부 존재
    Evidence: .sisyphus/evidence/final-qa/f1-compliance.txt

  Scenario: Must NOT Have 항목 미위반 확인
    Tool: Grep 도구 + Bash (git diff)
    Steps:
      1. Grep 도구로 xml_writer.py에서 "hp:para" 검색 → 0 결과
      2. Grep 도구로 xml_writer.py에서 "hp:align" 검색 → 0 결과
      3. Bash: git diff HEAD~3 --name-only → md_parser.py, image_embedder.py 변경 없음 확인
      4. 겁증 결과를 Write 도구로 .sisyphus/evidence/final-qa/f1-guardrails.txt에 저장
    Expected Result: Must NOT Have 7개 항목 중 7개 미위반
    Evidence: .sisyphus/evidence/final-qa/f1-guardrails.txt
  ```
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`

  **QA Scenarios:**
  ```
  Scenario: 전체 테스트 통과 + 코드 품질 검사
    Tool: Bash + Grep 도구
    Steps:
      1. Bash: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py 2>&1 → ALL PASSED
      2. Grep 도구로 xml_writer.py에서 "type: ignore|noqa" 검색 → 0 결과
      3. Grep 도구로 xml_writer.py에서 "^\s*print\(" 검색 → __main__ 외 프로덕션 print 없음
      4. Read 도구로 xml_writer.py의 변경된 영역 읽어 불필요한 주석/추상화 없음 확인
      5. 검사 결과를 Write 도구로 .sisyphus/evidence/final-qa/f2-quality.txt에 저장
    Expected Result: 테스트 전체 통과, 코드 품질 이슈 0개
    Evidence: .sisyphus/evidence/final-qa/f2-quality.txt
  ```
  Output: `Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`

  **QA Scenarios:**
  ```
  Scenario: Task 1-4 QA 시나리오 전수 재실행
    Tool: Bash
    Steps:
      1. Bash: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v -k "build_fragment_caption" 2>&1 → 4 PASSED
      2. Bash: python -c (Task 3 Scenario 1의 _caption_checks 단위 테스트) → assert 통과
      3. Bash: python -c (Task 3 Scenario 2의 _caption_checks parsed_path=None 테스트) → 에러 0개
      4. (조건부) Bash: python -c "import os; print('PRESENT' if all(os.path.exists(p) for p in ['dev/3\uc7a5.md']) else 'ABSENT')" → PRESENT이면 E2E 실행, ABSENT이면 스킵
      5. 모든 출력을 Write 도구로 .sisyphus/evidence/final-qa/f3-full-qa.txt에 저장
    Expected Result: 3개 필수 시나리오 통과 + 조건부 E2E
    Evidence: .sisyphus/evidence/final-qa/f3-full-qa.txt

  Scenario: Cross-task 통합 검증 — dead code 완전 제거 확인
    Tool: Grep 도구 + Bash
    Steps:
      1. Grep 도구로 plugins/hwpx-generator/ 전체에서 "build_image_with_caption" 검색 → 0 결과
      2. Grep 도구로 tests/에서 "sample_image_block" 검색 → 사용처 없으면 삭제 확인
      3. Bash: python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --tb=short --ignore=...test_e2e_pipeline.py --ignore=...test_dev_data_exists.py 2>&1 → 전체 PASSED
      4. 결과를 Write 도구로 .sisyphus/evidence/final-qa/f3-integration.txt에 저장
    Expected Result: Dead code 잔재 없음, 전체 테스트 정상
    Evidence: .sisyphus/evidence/final-qa/f3-integration.txt
  ```
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`

  **QA Scenarios:**
  ```
  Scenario: 변경 범위 정확성 확인
    Tool: Bash (git diff) + Read 도구
    Steps:
      1. Bash: git diff HEAD~3 --name-only 2>&1 → 변경된 파일 목록 확인
      2. 예상 파일: xml_writer.py, test_xml_writer_images.py, validate.py (3개만)
      3. 예상 외 파일이 있으면 Read 도구로 해당 파일 변경 내용 확인 → Must NOT do 위반 여부 판단
      4. Read 도구로 xml_writer.py의 변경 영역 확인 → 캡션 로직 추가 + dead code 삭제만 허용
      5. 결과를 Write 도구로 .sisyphus/evidence/final-qa/f4-scope.txt에 저장
    Expected Result: 변경 파일 3개, 모든 변경이 플랜 범위 내, Must NOT do 위반 0건
    Failure Indicators: md_parser.py 또는 image_embedder.py 변경 → 스코프 위반
    Evidence: .sisyphus/evidence/final-qa/f4-scope.txt
  ```
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Commit | Type | Message | Files | Pre-commit |
|--------|------|---------|-------|------------|
| 1 | test | `test(hwpx): add failing tests for caption emission in build_fragment` | `test_xml_writer_images.py` | `python -m pytest ... -x` (expect FAIL) |
| 2 | fix+refactor | `fix(hwpx): emit caption paragraph after image placeholder + remove dead code` | `xml_writer.py`, `test_xml_writer_images.py` | `python -m pytest ... -v` (expect PASS) |
| 3 | feat | `feat(hwpx): add caption count validation to validate.py` | `validate.py` | `python -m pytest ... -v` (expect PASS) |

---

## Success Criteria

### Verification Commands
```bash
python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_xml_writer_images.py -v
# Expected: ALL PASS (new caption tests + style fallback tests)

python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py -v -m integration
# Expected: PASSED if dev/ fixtures exist; skip if absent

python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_e2e_pipeline.py --ignore=plugins/hwpx-generator/skills/hwpx-core/tests/test_dev_data_exists.py
# Expected: ALL PASS, 0 errors, 0 import failures (픽스처 독립 단위 테스트)
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Dead code `build_image_with_caption()` (L419-497) fully removed
- [ ] No `hp:para` or `hp:align` in new code
- [ ] `paragraph_from_segments()` used for caption paragraph
