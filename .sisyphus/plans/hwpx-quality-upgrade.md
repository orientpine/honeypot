# hwpx-generator 품질 대폭 개선: 30년 한글 전문가 수준 문서 생성

## TL;DR

> **Quick Summary**: hwpx-generator의 Workflow 7(MD→양식 채우기) 파이프라인을 전면 개선하여, 어떤 양식 HWPX든 이중 글머리·폰트 불일치·표 깨짐 없이, 이미지+캡션까지 전문가 수준으로 생성하는 품질 업그레이드.
> 
> **Deliverables**:
> - md_parser.py 개선: 표준 마크다운 이미지, 블록인용, 이미지-캡션 페어링, circle-numbered 소제목
> - xml_writer.py 개선: hs:sec 래퍼, 이중 불릿 제거, 표 colSpan, 이미지+캡션 XML 생성
> - image_embedder.py 개선: 표준 마크다운 이미지 경로 지원, 캡션 연동, JPEG 지원
> - analyze_template.py 개선: 스타일맵 추출 정확도 향상
> - NEW proofread.py: 생성 후 품질 검증 (이중 불릿, 폰트 일관성, 고아 플레이스홀더 등)
> - hwpx-builder.md / hwpx-generate.md 에이전트 지침 업데이트
> - dev/ 데이터 기반 E2E 통합 테스트
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 -> Task 3,4 -> Task 6,7,8 -> Task 13 -> F1-F4

---

## Context

### Original Request
hwpx-generator 플러그인을 개선하여, 어떤 양식 HWPX 문서를 제공하더라도 30년 한글 문서 작성 전문가가 작성한 것처럼 표와 그림이 깔끔하고, 문단 구조와 글머리가 깔끔하게 작성할 수 있도록 한다. 이미지도 전문가처럼 캡션과 함께 삽입하는 기능 포함.

### Interview Summary
**Key Discussions**:
- 사용자 식별 문제점 (우선순위): 1.문단/글머리 2중 배치 2.폰트 통일성 3.교정 부재 4.양식 인식 실패 5.표 깨짐
- 사용자가 이중 글머리 근본 원인 분석 제공: heading type="BULLET" 자동 불릿 + 텍스트 내 명시적 불릿 = 78개 단락 이중 렌더링 (paraPrIDRef 45/92/93)
- 권장 해결안: 텍스트에서 명시적 불릿 문자 strip, 단락 스타일 자동 불릿만 유지
- 이미지+캡션 전문가 삽입 기능 추가 요청
- dev/ 폴더: 작성.hwpx(골든 레퍼런스), 초안.hwpx(빈 양식), 3장.md(98줄), 4장.md(311줄), images/(15 PNG)

**Research Findings**:
- xml_writer.py가 hwpx-fragment 생성하나 hs:sec 래퍼 없음 -> section0.xml에 직접 삽입 불가
- md_parser.py가 커스텀 포맷만 지원, 표준 마크다운 `![alt](path)` 미지원 -> dev/ 샘플과 포맷 불일치
- 표(table) colSpan/rowSpan 미지원, 균등 분할만 가능
- analyze_template.py 스타일맵이 빈도 기반 휴리스틱 -> 복잡한 템플릿에서 오매핑
- image_embedder.py: PNG만 지원, 정렬 제어 없음, 캡션 연동 없음
- 후처리(교정) 단계 전무 -- validate.py는 구조 검증만

### Metis Review
**Identified Gaps** (addressed):
- 이미지 참조 포맷 불일치 -> md_parser 개선에 포함
- 이미지-캡션 페어링 미구현 -> md_parser + xml_writer 개선에 포함
- fix_namespaces.py Workflow 7 호출 누락 가능성 -> hwpx-builder.md 업데이트에 포함
- page_guard.py 임계값이 템플릿 채우기에 부적합 -> 태스크별 임계값 오버라이드 추가
- circle-numbered 소제목, bold 섹션 라벨, blockquote+인라인 서식 -> md_parser 개선에 포함

---

## Work Objectives

### Core Objective
Workflow 7(MD->양식 채우기) 파이프라인의 파서, 라이터, 이미지 임베더, 분석기, 검증기를 전면 개선하여 전문가 수준 HWPX 문서를 생성한다.

### Concrete Deliverables
- 개선된 스크립트 6개: md_parser.py, xml_writer.py, image_embedder.py, analyze_template.py, page_guard.py, validate.py
- 신규 스크립트 1개: proofread.py
- 업데이트된 에이전트 2개: hwpx-builder.md, hwpx-generate.md
- E2E 테스트: dev/ 데이터 기반 전체 파이프라인 검증

### Definition of Done
- [ ] `validate.py --strict` PASS on generated output
- [ ] `proofread.py` returns: double_bullets=0, font_consistency=true, orphaned_placeholders=0
- [ ] `page_guard.py` 기본 모드로 골든 레퍼런스(작성.hwpx) 대비 비교: PASS (5 warnings 이하)
- [ ] 15개 PNG 이미지 모두 캡션과 함께 정확한 위치에 삽입됨
- [ ] E2E 파이프라인: 초안.hwpx + 3장.md + 4장.md + images/ -> valid HWPX

### Must Have
- 이중 글머리 제거 (heading type=BULLET 단락에서 텍스트 선행 불릿 문자 strip)
- 표준 마크다운 이미지 문법 지원 (`![alt](path)` + 이탤릭 캡션 페어링)
- 이미지+캡션 전문가 삽입 (이미지 본문 삽입 + 캡션 단락 생성 + 중앙 정렬)
- xml_writer 출력에 hs:sec 래퍼 포함
- 블록인용 + 인라인 서식 파싱
- 생성 후 품질 검증 (proofread.py)
- 스타일 ID를 템플릿 분석에서 동적 추출 (하드코딩 금지)

### Must NOT Have (Guardrails)
- Workflow 1-6 기존 동작 변경 또는 퇴행
- stdlib-only 스크립트(zip_surgery, xml_writer, md_parser, image_embedder, fix_namespaces)에 lxml 의존성 추가
- python-hwpx 라이브러리를 쓰기(writing) 용도로 도입
- cell_writer.py를 ZIP surgery 이후 호출
- 스타일 ID 하드코딩 (charPrIDRef=30-34 등)
- dev/3장.md, 4장.md에 없는 마크다운 구문 지원 (ordered list, code block, footnote 등)
- linesegarray strip 통합 또는 HWPX pack 통합 (기술부채 문서화만)
- multi-section HWPX (section1.xml+) 지원
- 자동 목차(TOC), 교차참조, 쪽번호 자동 갱신
- build_hwpx.py 템플릿 어셈블리 로직 수정 (Workflow 1,5 경로)
- ElementTree(ET) 사용 -- zip_surgery의 문자열 기반 XML 패턴 준수

---

### Prerequisites (MUST exist before Task 1)
- `dev/` 폴더가 프로젝트 루트에 존재해야 함 (확인됨: `C:\Users\BaekdongCha\Documents\honeypot\dev/`)
- 포함 파일: `(양식) '27년도 전략연구사업 제안서_작성.hwpx` (골든 레퍼런스), `(양식)..._초안.hwpx` (빈 양식), `3장.md`, `4장.md`, `images/` (15 PNG)
- 이 파일들은 사용자가 제공한 개발용 샘플이며, 모든 태스크의 테스트 데이터 기반임

## Verification Strategy

> **ZERO HUMAN INTERVENTION** -- ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: YES (Tests-after, pytest)
- **Framework**: pytest
- **Golden Reference**: `dev/(양식) '27년도 전략연구사업 제안서_작성.hwpx`

### QA Policy

> **스크립트 경로 규칙**: 모든 QA 시나리오에서 스크립트를 호출할 때는 항상 `plugins/hwpx-generator/skills/hwpx-core/scripts/` 전체 경로를 사용하거나, workdir를 해당 scripts/ 디렉토리로 지정합니다.
> 약어: `SCRIPTS=plugins/hwpx-generator/skills/hwpx-core/scripts`
> fix_namespaces.py만 `plugins/hwpx-generator/skills/hwpx-templates/scripts/`에 위치.

- **Scripts**: Bash (python $SCRIPTS/script.py) -- 출력 JSON/XML 파싱, 필드 검증
- **HWPX 구조**: Bash (python $SCRIPTS/validate.py) -- ZIP 구조, XML 무결성
- **품질 검증**: Bash (python $SCRIPTS/proofread.py) -- 이중 불릿, 폰트 일관성
- **비교 검증**: Bash (python $SCRIPTS/page_guard.py) -- 골든 레퍼런스 대비 드리프트

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (Foundation):
  Task 1: 골든 레퍼런스 분석 + 스타일맵 추출 [deep]
  Task 2: pytest 테스트 인프라 구축 [quick]

Wave 1 (Parser + Analyzer, MAX PARALLEL):
  Task 3: md_parser 표준 이미지 + 캡션 페어링 (depends: 1,2) [deep]
  Task 4: md_parser 블록인용 + circle-numbered + bold 라벨 (depends: 1,2) [deep]
  Task 5: analyze_template 스타일맵 정확도 향상 (depends: 1) [deep]

Wave 2 (Writer + Embedder + Proofreader, MAX PARALLEL):
  Task 6: xml_writer hs:sec 래퍼 + fragment 통합 (depends: 3,4,5) [deep]
  Task 7: xml_writer 이중 불릿 제거 + 표 colSpan (depends: 5,6) [deep]
  Task 8: xml_writer 이미지+캡션 XML 생성 (depends: 3,5,6) [deep]
  Task 9: image_embedder 표준 이미지 경로 + JPEG (depends: 3) [deep]
  Task 10: proofread.py 신규 품질 검증 (depends: 1) [deep]

Wave 3 (Integration):
  Task 11: page_guard + validate 확장 (depends: 10) [unspecified-high]
  Task 12: hwpx-builder.md + hwpx-generate.md 업데이트 (depends: 6-10) [writing]
  Task 13: E2E 통합 테스트 (depends: ALL) [deep]

Wave FINAL (4 parallel reviews, then user okay):
  F1: Plan compliance audit [oracle]
  F2: Code quality review [unspecified-high]
  F3: Real manual QA [unspecified-high]
  F4: Scope fidelity check [deep]
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | -- | 3,4,5,6,7,8,9,10 | 0 |
| 2 | -- | 3,4 | 0 |
| 3 | 1,2 | 6,8,9 | 1 |
| 4 | 1,2 | 6 | 1 |
| 5 | 1 | 6,7,8 | 1 |
| 6 | 3,4,5 | 7,8,12,13 | 2 |
| 7 | 5,6 | 12,13 | 2 |
| 8 | 3,5,6 | 12,13 | 2 |
| 9 | 3 | 12,13 | 2 |
| 10 | 1 | 11,12,13 | 2 |
| 11 | 10 | 13 | 3 |
| 12 | 6-10 | 13 | 3 |
| 13 | ALL | F1-F4 | 3 |

### Agent Dispatch Summary

- **Wave 0**: 2 agents -- T1 `deep`, T2 `quick`
- **Wave 1**: 3 agents -- T3,T4,T5 `deep`
- **Wave 2**: 5 agents -- T6-T10 `deep`
- **Wave 3**: 3 agents -- T11 `unspecified-high`, T12 `writing`, T13 `deep`
- **FINAL**: 4 agents -- F1 `oracle`, F2-F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. 골든 레퍼런스 분석 + 스타일맵 추출 (Ground Truth 확보)

  **What to do**:
  - `analyze_template.py --style-map`을 작성.hwpx(골든)와 초안.hwpx(빈 양식) 양쪽 모두에 실행
  - 작성.hwpx의 section0.xml을 `HwpxSurgeon(path).section_bytes()` 또는 CLI `python zip_surgery.py extract 작성.hwpx --output section0.xml`로 추출하여 역분석: 단락 구조, 표 구조, 이미지+측션 XML 구조, 불릿 스타일
  - heading type="BULLET"인 paraPr을 식별하고 paraPrIDRef 45/92/93이 불릿 자동생성인지 확인
  - 이미지+캡션이 작성.hwpx에서 어떤 XML 구조인지 파악: `hp:pic` 위치, 캡션 단락 스타일, 정렬 방식, BinData 참조 구조
  - 3장.md(3개) + 4장.md(12개) = 15개 이미지 경로와 dev/images/ 내 파일 1:1 교차검증
  - 결과를 `dev/golden/*.json`에 저장 (style_map, paragraph_inventory, table_structures, image_structures, bullet_styles)

  **Must NOT do**: 어떤 스크립트도 수정 안 함 (분석 전용). 추측 결과 금지.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 0 (Task 2와 병렬). Blocks: 3-10. Blocked By: None.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` -- `extract_style_map()` 함수 (lines 392-621) 출력 형식이 이후 모든 스크립트의 style-config 입력 포맷
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` -- `HwpxSurgeon.extract_children(tag)` / `replace_children(children)` 메서드로 section0.xml 내부 요소 추출/교체. CLI: `python zip_surgery.py extract INPUT --output PATH` / `replace INPUT --section PATH --output PATH`. `section_bytes()` 속성으로 raw section0.xml 접근
  - `plugins/hwpx-generator/skills/hwpx-templates/references/xml-internals.md` -- HWPX ZIP 구조, namespace 맵

  **Acceptance Criteria**:
  - [ ] `dev/golden/style_map_초안.json` 생성, 6개 필수 키(heading_1, heading_2, body, bullet, table_header, table_cell) 포함
  - [ ] `dev/golden/style_map_작성.json` 생성
  - [ ] `dev/golden/paragraph_inventory.json` 생성 (작성.hwpx의 전체 단락 유형 + paraPrIDRef)
  - [ ] `dev/golden/image_structures.json` 생성 (hp:pic 요소 + 캡션 단락 구조 + BinData 참조)
  - [ ] `dev/golden/bullet_styles.json` 생성 (heading type=BULLET인 paraPr ID + 연관 불릿 문자)
  - [ ] 15개 이미지 경로 교차검증 통과

  **QA Scenarios**:
  ```
  Scenario: 스타일맵 추출 성공
    Tool: Bash
    Steps:
      1. python analyze_template.py "dev/(양식) '27년도 전략연구사업 제안서_초안.hwpx" --style-map dev/golden/style_map_초안.json
      2. JSON 파싱하여 6개 필수 키 존재 확인
      3. 각 값에 charPrIDRef, paraPrIDRef 양의 정수 포함 확인
    Expected Result: 6개 키 모두 존재, 값은 양의 정수
    Evidence: .sisyphus/evidence/task-1-style-map.json

  Scenario: 이중 불릿 대상 식별
    Tool: Bash
    Steps:
      1. zip_surgery.py로 작성.hwpx에서 section0.xml 추출
      2. paraPrIDRef 45/92/93 단락의 첫 hp:t에서 불릿 문자 존재 확인
    Expected Result: 이중 불릿 단락 수와 분포가 bullet_styles.json에 기록
    Evidence: .sisyphus/evidence/task-1-bullet-inventory.json
  ```

  **Commit**: YES
  - Message: `chore(hwpx): extract golden reference data from dev/ samples`
  - Files: `dev/golden/*.json`

---

- [ ] 2. pytest 테스트 인프라 구축

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/` 디렉토리 생성
  - `conftest.py`: dev/ 경로 fixture, HWPX 열기/section0.xml 추출 helper, JSON 비교 helper (Windows 경로 호환)
  - `test_dev_data_exists.py`: dev/ 폴더 전체 파일(2 hwpx, 2 md, 15 png) 존재 확인 smoke test
  - pytest 설정 파일 (pyproject.toml 또는 pytest.ini)

  **Must NOT do**: 스크립트 수정 없음. lxml 추가 없음.

  **Recommended Agent Profile**: Category: `quick`. Skills: [].

  **Parallelization**: Wave 0 (Task 1과 병렬). Blocks: 3,4. Blocked By: None.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/` -- 테스트 대상 스크립트 CLI 인터페이스 (argparse)

  **Acceptance Criteria**:
  - [ ] `plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py` 존재
  - [ ] `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_dev_data_exists.py -v` PASS (5+ tests)

  **QA Scenarios**:
  ```
  Scenario: 테스트 인프라 정상 동작
    Tool: Bash
    Steps:
      1. python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v
      2. "passed" 키워드 확인, 0 failures
    Expected Result: 5+ tests passed
    Evidence: .sisyphus/evidence/task-2-test-infra.txt
  ```

  **Commit**: YES
  - Message: `chore(hwpx): add pytest test infrastructure for hwpx-core`
  - Files: `tests/conftest.py`, `tests/test_dev_data_exists.py`

---

- [ ] 3. md_parser.py: 표준 마크다운 이미지 + 캡션 페어링

  **What to do**:
  - 기존 커스텀 이미지 포맷 유지하면서 `![alt](path)` 문법 파싱하는 IMAGE_MD_RE 정규식 추가
  - 이미지 블록 다음 줄이 이탤릭(`*그림 N-M: caption*`)이면 같은 블록의 caption/caption_id 필드로 병합
  - caption_id 추출: "그림 3-1" -> "3-1"
  - path 필드에서 파일명 추출하여 image_embedder용 매핑 키 생성
  - 테스트: 3장 3개, 4장 12개 = 15개 이미지+캡션 정확히 파싱

  **Must NOT do**: 기존 커스텀 포맷 제거 금지. lxml 추가 금지. 이미지 실존 여부 검증 안 함(embedder 역할).

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 1 (Task 4,5와 병렬). Blocks: 6,8,9. Blocked By: 1,2.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` -- IMAGE_REF_RE (line ~14), parse_blocks() 블록 분류 로직
  - `dev/3장.md:13-14` -- 이미지+캡션 예시: `![비전 개념도](./images/01_비전_개념도.png)` 다음 줄 `*그림 3-1: ...*`
  - `dev/4장.md:5-6,26-27,48-49` -- 4장 이미지+캡션 (12개)

  **Acceptance Criteria**:
  - [ ] 3장.md 파싱 시 image_ref 블록 3개 (각각 path, alt, caption, caption_id 포함)
  - [ ] 4장.md 파싱 시 image_ref 블록 12개
  - [ ] caption_id: "3-1","3-2","3-3" (3장), "4-1"~"4-12" (4장)
  - [ ] 기존 커스텀 포맷 하위호환 테스트 통과

  **QA Scenarios**:
  ```
  Scenario: 15개 이미지+캡션 파싱
    Tool: Bash
    Steps:
      1. python md_parser.py dev/3장.md --output dev/tmp/p3.json
      2. image_ref 블록 수 == 3 확인
      3. python md_parser.py dev/4장.md --output dev/tmp/p4.json
      4. image_ref 블록 수 == 12 확인
      5. 각 블록에 path, alt, caption, caption_id 4개 필드 확인
    Expected Result: 총 15개 이미지 블록, 각각 4개 필드 완비
    Evidence: .sisyphus/evidence/task-3-image-parsing.json
  ```

  **Commit**: YES
  - Message: `fix(md_parser): support standard markdown image + caption pairing`
  - Files: `md_parser.py`, `tests/test_md_parser_images.py`

---

- [ ] 4. md_parser.py: 블록인용 + circle-numbered + bold 라벨

  **What to do**:
  - 블록인용 개선: `> **목표**: text` 형식에서 인라인 서식을 segments로 분리 (bold segment 생성)
  - circle-numbered 소제목: `#### (1) ...` 형태의 H4에서 fullwidth 숫자 보존
  - bold 섹션 라벨: `**[재난 분야]**` 단독 bold 라인을 is_bold_label 플래그 또는 bold_label 타입으로 인식
  - 수평선(---) separator 블록 생성 확인
  - 테스트: 4장.md -- blockquote 4+개, circle headings 12+개, bold labels 6+개

  **Must NOT do**: 중첩 불릿 추가 안 함. 코드블록/각주 안 함.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 1 (Task 3,5와 병렬). Blocks: 6. Blocked By: 1,2.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` -- BLOCKQUOTE_RE, HEADING_RE, parse_inline_segments()
  - `dev/4장.md:12` -- blockquote 예시
  - `dev/4장.md:43` -- circle-numbered 예시
  - `dev/4장.md:121` -- bold 라벨 예시

  **Acceptance Criteria**:
  - [ ] blockquote 블록 4+개, segments에 bold segment 포함
  - [ ] H4 블록에 circle number 문자 보존
  - [ ] bold 라벨 6+개 별도 인식
  - [ ] separator 블록 정상 생성

  **QA Scenarios**:
  ```
  Scenario: 4장.md 복잡 구조 파싱
    Tool: Bash
    Steps:
      1. python md_parser.py dev/4장.md --output dev/tmp/p4.json
      2. blockquote 블록 수 >= 4 확인
      3. 첫 blockquote의 segments에 bold 스타일 존재 확인
      4. H4 블록 중 circle number 문자 포함 확인
    Expected Result: 모든 복잡 구조가 정확히 파싱됨
    Evidence: .sisyphus/evidence/task-4-complex-parsing.json
  ```

  **Commit**: YES
  - Message: `fix(md_parser): handle blockquote, circle-numbered, bold labels`
  - Files: `md_parser.py`, `tests/test_md_parser_complex.py`

---

- [ ] 5. analyze_template.py: 스타일맵 정확도 향상

  **What to do**:
  - 추출된 스타일 ID에 confidence 점수 추가 ("confirmed"/"estimated"/"fallback")
  - 빈도 휴리스틱 실패 시 폴백 전략 (이름 기반 매칭, 크기 기반 매칭)
  - 이미지 캡션 스타일 탐지 추가: 작성.hwpx에서 캡션 단락의 paraPr/charPr 추출
  - blockquote 스타일 탐지 추가
  - 불릿 스타일 탐지 강화: heading type="BULLET" paraPr 자동 식별
  - dev/ 템플릿에서 no-fallback 추출 테스트

  **Must NOT do**: analyze_template.py는 lxml 사용 OK (기존에 사용 중). 다른 stdlib-only 스크립트에 lxml 추가 금지.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 1 (Task 3,4와 병렬). Blocks: 6,7,8. Blocked By: 1.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` -- extract_style_map() (lines 392-621), lxml 기반
  - `dev/golden/style_map_초안.json` (Task 1 산출물) -- 정확도 검증 기준
  - `dev/golden/image_structures.json` (Task 1 산출물) -- 캡션 스타일 참조

  **Acceptance Criteria**:
  - [ ] style_map에 confidence 필드 추가
  - [ ] dev/ 초안.hwpx에서 fallback 없이 6개 필수 스타일 추출
  - [ ] image_caption 스타일 키 추가
  - [ ] bullet_auto 스타일 키 추가 (heading type=BULLET인 paraPr 식별)

  **QA Scenarios**:
  ```
  Scenario: 스타일맵 정확도
    Tool: Bash
    Steps:
      1. python analyze_template.py "dev/(양식) '27년도 전략연구사업 제안서_초안.hwpx" --style-map dev/tmp/sm.json
      2. JSON에서 "_comment" 또는 "fallback" 포함된 키 수 카운트
      3. image_caption, bullet_auto 키 존재 확인
    Expected Result: fallback 키 0개, image_caption + bullet_auto 키 존재
    Evidence: .sisyphus/evidence/task-5-style-accuracy.json
  ```

  **Commit**: YES
  - Message: `feat(analyze_template): improve style-map extraction accuracy`
  - Files: `analyze_template.py`, `tests/test_analyze_template.py`

---

- [ ] 6. xml_writer.py: hs:sec 래퍼 + fragment 통합

  **What to do**:
  - build_fragment() 출력을 hs:sec 요소로 래핑: secPr(page size, margins) 포함
  - secPr 값을 template analysis에서 받아옴 (style-config JSON에 page_width, page_height, margin_* 추가)
  - 네임스페이스 선언을 hs:sec 루트에 포함 (hp, hc, hs, hh)
  - 출력이 zip_surgery CLI `python zip_surgery.py replace INPUT --section FRAG.xml --output OUT.hwpx` 또는 `HwpxSurgeon.replace_children(children)` + `save()`로 직접 삽입 가능하도록 보장
  - 기존 hwpx-fragment 포맷과의 하위호환: --wrap-section 플래그 추가

  **Must NOT do**: ElementTree 사용 금지 -- 문자열 기반 XML 생성 유지. lxml 추가 금지.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 2 (Task 7-10과 병렬). Blocks: 7,8,12,13. Blocked By: 3,4,5.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` -- build_fragment() (line ~351), 현재 hwpx-fragment 루트 사용
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` -- CLI: `replace INPUT --section FRAG.xml --output OUT.hwpx`. Class API: `HwpxSurgeon.replace_children(children)` + `save(path)`
  - `dev/golden/style_map_초안.json` (Task 1) -- page 속성 참조

  **Acceptance Criteria**:
  - [ ] --wrap-section 시 출력 XML이 hs:sec 루트를 가짐
  - [ ] secPr에 pageWidth, pageHeight, margin 값 포함
  - [ ] 네임스페이스 선언 4개 (hp, hc, hs, hh) 포함
  - [ ] `python zip_surgery.py replace 초안.hwpx -s frag.xml -o result.hwpx` 후 `validate.py --strict result.hwpx` PASS

  **QA Scenarios**:
  ```
  Scenario: hs:sec 래퍼 생성 + ZIP 삽입
    Tool: Bash
    Steps:
      1. python xml_writer.py --input parsed.json --style-config sm.json --wrap-section --output frag.xml
      2. frag.xml에서 "hs:sec" 문자열 존재 확인
      3. zip_surgery.py로 초안.hwpx의 section0을 frag.xml로 교체
      4. python validate.py --strict result.hwpx
    Expected Result: validate PASS
    Evidence: .sisyphus/evidence/task-6-sec-wrapper.txt
  ```

  **Commit**: YES
  - Message: `fix(xml_writer): wrap fragment in hs:sec with secPr`
  - Files: `xml_writer.py`, `tests/test_xml_writer_section.py`

---

- [ ] 7. xml_writer.py: 이중 불릿 제거 + 표 colSpan

  **What to do**:
  - **이중 불릿 제거**: build_bullet() 함수에서, paraPr이 heading type=BULLET인 경우 hp:t 텍스트의 선행 불릿 문자 strip. 대상 문자: 모든 common 한글 문서 불릿 (원형, 사각, 삼각, 화살표 등)
  - style-config에서 bullet_auto 키 (Task 5 산출물)를 읽어 자동 불릿 paraPrIDRef 목록 취득
  - **표 colSpan/rowSpan**: table_cell_xml()에 colSpan/rowSpan 파라미터 추가. md_parser의 table 블록에 merge 정보가 있으면 반영
  - **가변 열 폭**: 균등 분할 대신, 각 열의 최대 텍스트 길이 비례 분배 옵션 추가

  **Must NOT do**: 불릿 문자 목록을 하드코딩하되, paraPrIDRef 목록은 style-config에서 동적 취득. ET 사용 금지.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 2. Blocks: 12,13. Blocked By: 5,6.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` -- build_bullet() (bullet 생성), table_cell_xml() (lines 207-243, colSpan=1 고정)
  - `dev/golden/bullet_styles.json` (Task 1) -- 이중 불릿 대상 paraPrIDRef 목록
  - `dev/golden/table_structures.json` (Task 1) -- 표 구조 참조

  **Acceptance Criteria**:
  - [ ] bullet_auto paraPrIDRef 사용 시 출력 hp:t에 불릿 문자 0개
  - [ ] colSpan=2 테스트 케이스 통과
  - [ ] rowSpan=2 테스트 케이스 통과
  - [ ] 가변 열 폭 분배 테스트 통과

  **QA Scenarios**:
  ```
  Scenario: 이중 불릿 0건
    Tool: Bash
    Steps:
      1. 불릿 블록이 포함된 테스트 JSON 생성 (텍스트에 명시적 불릿 포함)
      2. python xml_writer.py --input test.json --style-config sm.json --output out.xml
      3. python -c "import re; xml=open('out.xml',encoding='utf-8').read(); bullets=re.findall(r'[\u25cb\u25a0\u25a1\u25c6\u25c7\u2022\u25b6\u25ba\u2192\u203b]', xml); assert len(bullets)==0, f'found {len(bullets)} bullet chars'"
    Expected Result: 불릿 문자 매칭 0건
    Evidence: .sisyphus/evidence/task-7-no-double-bullets.txt
  ```

  **Commit**: YES
  - Message: `fix(xml_writer): strip double-bullets + add table colSpan/rowSpan`
  - Files: `xml_writer.py`, `tests/test_xml_writer_bullets.py`, `tests/test_xml_writer_tables.py`

---

- [ ] 8. xml_writer.py: 이미지+캡션 전문가 XML 생성

  **What to do**:
  - **NEW**: image_ref 블록을 받아 hp:pic 요소 + 캡션 단락을 생성하는 `build_image_with_caption()` 함수 추가
  - 이미지 크기: Pillow로 실제 PNG 크기 읽고, 템플릿 페이지 폭에 맞춰 비율 스케일링 (xml_writer는 PIL 의존성 추가 가능 -- stdlib-only 제약은 XML 파싱 라이브러리에만 적용)
  - 캡션 단락: image_caption 스타일(Task 5)로 생성, 중앙 정렬, caption_id + caption 텍스트 포함
  - BinData 참조 ID: 순차 생성 (imageN)
  - IMAGE placeholder 생성: zip_surgery 삽입 시 image_embedder가 교체할 수 있도록 placeholder 포함 옵션

  **Must NOT do**: ElementTree 사용 금지. 이미지 파일 직접 ZIP 삽입 안 함 (image_embedder 역할).

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 2 (Task 6-10과 병렬). Blocks: 12,13. Blocked By: 3,5,6.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` -- 기존 블록 타입별 build 함수 패턴 참조
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` -- IMAGE placeholder 문법, BinData 등록 방식
  - `dev/golden/image_structures.json` (Task 1) -- 작성.hwpx의 실제 이미지 XML 구조를 정확히 복제

  **Acceptance Criteria**:
  - [ ] image_ref 블록 입력 시 hp:pic 요소 + 캡션 단락 XML 생성
  - [ ] 이미지 크기가 페이지 폭 비례 스케일링 됨
  - [ ] 캡션에 caption_id + 텍스트 포함, 중앙 정렬
  - [ ] 작성.hwpx의 이미지 구조와 동일한 XML 패턴 사용

  **QA Scenarios**:
  ```
  Scenario: 이미지+캡션 XML 생성
    Tool: Bash
    Steps:
      1. image_ref 블록 1개 포함 JSON + dev/images/01_비전_개념도.png 경로로 xml_writer 실행
      2. 출력에서 hp:pic 문자열 존재 확인
      3. 캡션 단락에 "그림 3-1" 텍스트 포함 확인
    Expected Result: hp:pic + 캡션 단락 쌍 생성
    Evidence: .sisyphus/evidence/task-8-image-caption-xml.xml
  ```

  **Commit**: YES
  - Message: `feat(xml_writer): generate professional image+caption XML blocks`
  - Files: `xml_writer.py`, `tests/test_xml_writer_images.py`

---

- [ ] 9. image_embedder.py: 표준 이미지 경로 + JPEG 지원

  **What to do**:
  - md_parser의 image_ref 블록에서 path 필드를 읽어 자동 매핑 (기존 수동 --mapping 외에 --from-parsed JSON 모드 추가)
  - 표준 마크다운 상대경로 (./images/file.png) 해석: --base-dir 옵션으로 기준 디렉토리 지정
  - JPEG 지원: .jpg/.jpeg 확장자 인식, content.hpf manifest에 JPEG MIME 타입 등록
  - 캡션 placeholder 교체: image_ref의 caption을 IMAGE placeholder 영역에 연동

  **Must NOT do**: lxml 추가 금지 (기존 stdlib 유지). 이미지 크기 변환/리사이즈 안 함 (원본 그대로 삽입).

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 2. Blocks: 12,13. Blocked By: 3.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` -- IMAGE placeholder 교체 로직, BinData 등록, manifest 업데이트
  - `dev/images/` -- 15개 PNG 테스트 이미지

  **Acceptance Criteria**:
  - [ ] --from-parsed 모드로 15개 이미지 자동 매핑 + 삽입
  - [ ] content.hpf manifest에 15개 이미지 등록
  - [ ] JPEG 파일 삽입 테스트 통과 (MIME type 정확)

  **QA Scenarios**:
  ```
  Scenario: 15개 이미지 자동 삽입
    Tool: Bash
    Steps:
      1. md_parser로 3장+4장 파싱 -> parsed.json
      2. xml_writer로 fragment 생성 (IMAGE placeholder 포함)
      3. zip_surgery로 초안.hwpx에 삽입
      4. image_embedder --from-parsed parsed.json --base-dir dev/ --input result.hwpx --output final.hwpx
      5. final.hwpx의 BinData/ 디렉토리에 15개 파일 존재 확인
    Expected Result: 15개 이미지 모두 BinData에 존재, manifest 등록
    Evidence: .sisyphus/evidence/task-9-image-embed.txt
  ```

  **Commit**: YES
  - Message: `feat(image_embedder): standard paths + auto-mapping + JPEG`
  - Files: `image_embedder.py`, `tests/test_image_embedder.py`

---

- [ ] 10. proofread.py: 신규 품질 검증 스크립트

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/proofread.py` 신규 생성
  - 검사 항목:
    - double_bullets: heading type=BULLET paraPr의 hp:t에 불릿 문자 존재 시 fail
    - font_consistency: 동일 스타일 그룹 내 charPrIDRef 일관성 검사
    - empty_paragraphs: hp:t가 빈 문자열이거나 공백만인 단락 카운트
    - orphaned_placeholders: IMAGE, PLACEHOLDER 등 미교체 마커 검출
    - table_borders: 표 셀의 borderFillIDRef 존재 여부 확인
  - 입력: HWPX 파일 경로 + 선택적 --golden 골든 레퍼런스 경로
  - 출력: JSON (각 검사 항목 pass/fail + 상세 정보)
  - 종료 코드: 0(all pass), 1(any fail)

  **Must NOT do**: lxml 추가 금지 (문자열 기반 XML 검사). 파일 수정 안 함 (읽기 전용 검증).

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 2 (Task 6-9와 병렬). Blocks: 11,12,13. Blocked By: 1.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py` -- 기존 구조 검증 패턴 참조
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` -- HWPX 내부 XML 접근 패턴
  - `dev/golden/bullet_styles.json` (Task 1) -- 이중 불릿 검출 기준

  **Acceptance Criteria**:
  - [ ] proofread.py 실행 가능, --help 정상 출력
  - [ ] 골든 레퍼런스(작성.hwpx) 입력 시 double_bullets 검출 (기존에 이중 불릿 있으므로)
  - [ ] 정상 HWPX 입력 시 JSON 출력, 종료 코드 0
  - [ ] 불량 HWPX 입력 시 종료 코드 1

  **QA Scenarios**:
  ```
  Scenario: 품질 검증 JSON 출력
    Tool: Bash
    Steps:
      1. python proofread.py "dev/(양식) '27년도 전략연구사업 제안서_작성.hwpx" --output dev/tmp/proof.json
      2. JSON 파싱하여 double_bullets, font_consistency, empty_paragraphs, orphaned_placeholders, table_borders 키 확인
      3. 각 키에 pass/fail 값 존재 확인
    Expected Result: 5개 검사 항목 모두 결과 포함
    Evidence: .sisyphus/evidence/task-10-proofread.json
  ```

  **Commit**: YES
  - Message: `feat(hwpx-core): add proofread.py quality enforcement`
  - Files: `proofread.py`, `tests/test_proofread.py`

---

- [ ] 11. page_guard.py 템플릿 채우기 임계값 + validate.py 확장

  **What to do**:
  - page_guard.py에 `--mode=template-fill` 플래그 추가: 빈 템플릿을 레퍼런스로 사용할 때 완화된 임계값. 출력: PASS/FAIL (warnings 없음, 빈->채움 시 false-positive 방지용). 그 외 기본 모드는 기존과 동일 (PASS/FAIL + warning count)
  - validate.py에 `--proofread` 플래그 추가: proofread.py를 서브프로세스로 호출하여 통합 검증
  - validate.py 결과에 proofread 결과 포함 (PASS/FAIL + 세부 항목)

  **Must NOT do**: 기존 기본 임계값 변경 안 함 (새 모드 추가만). validate.py의 기존 검증 로직 수정 안 함.

  **Recommended Agent Profile**: Category: `unspecified-high`. Skills: [].

  **Parallelization**: Wave 3. Blocks: 13. Blocked By: 10.

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/page_guard.py` -- 기존 임계값 상수 위치
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py` -- 기존 검증 흐름

  **Acceptance Criteria**:
  - [ ] `page_guard.py --mode=template-fill` 시 빈->채움 시나리오에서 false-positive 없음
  - [ ] `validate.py --strict --proofread` 시 proofread 결과 포함
  - [ ] 기존 기본 모드 동작 퇴행 없음

  **QA Scenarios**:
  ```
  Scenario: 템플릿 채우기 모드
    Tool: Bash
    Steps:
      1. python page_guard.py --mode=template-fill --reference "dev/(양식) '27년도 전략연구사업 제안서_초안.hwpx" --output generated.hwpx
      2. PASS 결과 확인 (빈->채움 시나리오)
    Expected Result: PASS (false-positive 0건)
    Evidence: .sisyphus/evidence/task-11-template-fill.txt
  ```

  **Commit**: YES
  - Message: `fix(page_guard): template-fill mode + validate proofread gate`
  - Files: `page_guard.py`, `validate.py`, `tests/test_page_guard.py`

---

- [ ] 12. hwpx-builder.md + hwpx-generate.md 에이전트 지침 업데이트

  **What to do**:
  - hwpx-builder.md Workflow 7 단계에 다음 추가/수정:
    - md_parser 호출 시 새 이미지+캡션 파싱 설명
    - xml_writer 호출 시 --wrap-section 플래그 필수 명시
    - fix_namespaces.py 호출을 Workflow 7에 명시적 추가
    - image_embedder --from-parsed 모드 설명
    - proofread.py 단계 추가 (생성 -> 교정 -> 검증 순서)
    - 이중 불릿 방지: 불릿 단락에 명시적 불릿 문자를 넣지 말 것 경고
  - hwpx-generate.md Phase 3과 4 사이에 "Phase 3.5: 교정(Proofreading)" 추가
  - 이미지+캡션 삽입 워크플로우 설명 추가

  **Must NOT do**: 에이전트 .md에 코드 로직 포함 금지 (스크립트 호출 방법만 기술). Workflow 1-6 지침 수정 안 함.

  **Recommended Agent Profile**: Category: `writing`. Skills: [].

  **Parallelization**: Wave 3 (Task 11과 병렬). Blocks: 13. Blocked By: 6-10.

  **References**:
  - `plugins/hwpx-generator/agents/hwpx-builder.md` -- 현재 Workflow 7 기술 위치
  - `plugins/hwpx-generator/commands/hwpx-generate.md` -- Phase 3-5 구조
  - 개선된 스크립트들의 새 CLI 옵션 (Tasks 3-11 산출물)

  **Acceptance Criteria**:
  - [ ] hwpx-builder.md에 fix_namespaces.py 호출 명시
  - [ ] hwpx-builder.md에 proofread.py 단계 포함
  - [ ] hwpx-builder.md에 이미지+캡션 워크플로우 포함
  - [ ] hwpx-generate.md에 Phase 3.5 교정 단계 추가
  - [ ] 이중 불릿 방지 경고 포함

  **QA Scenarios**:
  ```
  Scenario: 에이전트 지침 완성도
    Tool: Bash (python -c 문자열 검색)
    Steps:
      1. python -c "assert 'fix_namespaces' in open('plugins/hwpx-generator/agents/hwpx-builder.md').read()"
      2. python -c "assert 'proofread' in open('plugins/hwpx-generator/agents/hwpx-builder.md').read()"
      3. python -c "c=open('plugins/hwpx-generator/commands/hwpx-generate.md').read(); assert '교정' in c or 'proofread' in c"
    Expected Result: 3개 핵심 키워드 모두 존재
    Evidence: .sisyphus/evidence/task-12-agent-docs.txt
  ```

  **Commit**: YES
  - Message: `docs(hwpx-builder): update Workflow 7 with proofreading + image-caption`
  - Files: `hwpx-builder.md`, `hwpx-generate.md`

---

- [ ] 13. E2E 통합 테스트: 초안 -> 3장+4장+images -> 완성 HWPX

  **What to do**:
  - 전체 파이프라인 테스트 스크립트 작성: `tests/test_e2e_pipeline.py`
  - 파이프라인 순서:
    1. md_parser.py -> 3장.json + 4장.json (각각 별도 파싱)
    2. test helper로 3장.json + 4장.json의 blocks 배열 병합 -> merged.json (단순 JSON concat)
    3. analyze_template.py 초안.hwpx --style-map style_map.json
    4. xml_writer.py --input merged.json --style-config style_map.json --wrap-section --output fragment.xml
    5. zip_surgery.py replace 초안.hwpx -s fragment.xml -o intermediate.hwpx
    6. image_embedder.py --from-parsed merged.json --base-dir dev/ --input intermediate.hwpx --output with_images.hwpx
    7. fix_namespaces.py with_images.hwpx (in-place 수정, 동일 파일이 final.hwpx 역할)
    8. validate.py --strict with_images.hwpx -> PASS
    9. proofread.py with_images.hwpx -> JSON (double_bullets=0)
    10. page_guard.py --reference 작성.hwpx --output with_images.hwpx -> PASS (5 warnings 이하, 기본 모드로 골든 레퍼런스 대비 비교)
  - 검증: 15개 이미지+캡션, 이중 불릿 0, 구조 유효

  **Must NOT do**: 파이프라인 순서 변경 금지. 중간 단계 건너뛰기 금지.

  **Recommended Agent Profile**: Category: `deep`. Skills: [].

  **Parallelization**: Wave 3 (순차 -- 모든 이전 태스크 완료 후). Blocks: F1-F4. Blocked By: ALL (1-12).

  **References**:
  - 모든 개선된 스크립트 (Tasks 3-11 산출물)
  - `dev/` 폴더 전체 (초안.hwpx, 3장.md, 4장.md, images/)
  - `dev/golden/` (Task 1 산출물) -- 골든 레퍼런스 비교 기준

  **Acceptance Criteria**:
  - [ ] E2E 파이프라인 전체 실행 성공 (exit code 0)
  - [ ] validate.py --strict PASS
  - [ ] proofread.py: double_bullets=0, font_consistency=true, orphaned_placeholders=0
  - [ ] page_guard.py 기본 모드 --reference 작성.hwpx: PASS (5 warnings 이하)
  - [ ] BinData/에 15개 이미지 존재
  - [ ] 각 이미지에 대응하는 캡션 단락 존재

  **QA Scenarios**:
  ```
  Scenario: 전체 파이프라인 E2E
    Tool: Bash
    Steps:
      1. md_parser dev/3장.md -> p3.json
      2. md_parser dev/4장.md -> p4.json
      3. analyze_template 초안.hwpx --style-map sm.json
      4. python -c "merge p3.json + p4.json blocks into merged.json" (test helper로 JSON blocks 배열 병합)
      5. xml_writer --input merged.json --style-config sm.json --wrap-section --output frag.xml
      6. zip_surgery.py replace 초안.hwpx -s frag.xml -o inter.hwpx
      7. image_embedder --from-parsed merged.json --base-dir dev/ --input inter.hwpx --output img.hwpx
      8. fix_namespaces.py img.hwpx (in-place 수정)
      9. validate.py --strict img.hwpx -> PASS
      10. proofread.py img.hwpx -> double_bullets=0
      11. page_guard.py --reference 작성.hwpx --output img.hwpx -> PASS (5 warnings 이하, 기본 모드)
    Expected Result: 전 단계 성공, 최종 HWPX 유효
    Evidence: .sisyphus/evidence/task-13-e2e-pipeline.txt

  Scenario: 이미지 15개 + 캡션 검증
    Tool: Bash
    Steps:
      1. final.hwpx를 zipfile로 열어 BinData/ 내 파일 수 카운트
      2. section0.xml에서 hp:pic 요소 수 카운트
      3. 캡션 텍스트에서 "그림" 문자열 포함 단락 수 카운트
    Expected Result: BinData 15개, hp:pic 15개, 캡션 단락 15개
    Evidence: .sisyphus/evidence/task-13-image-verification.json
  ```

  **Commit**: YES
  - Message: `test(hwpx): add E2E integration test with dev/ data`
  - Files: `tests/test_e2e_pipeline.py`

---

## Final Verification Wave (MANDATORY -- after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** -- `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** -- `unspecified-high`
  Run `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v` + `python validate.py --strict`. Review all changed scripts for: empty catches, print in prod, commented-out code, AI slop.
  Output: `Tests [N pass/N fail] | Scripts [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** -- `unspecified-high`
  Start from clean state. Execute full pipeline: 초안.hwpx + 3장+4장 + images -> output.hwpx. Run validate --strict, proofread, page_guard. Verify all 15 images with captions. Check cross-task integration.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** -- `deep`
  For each task: read "What to do", read actual diff. Verify 1:1. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| # | Commit Message | Files |
|---|---------------|-------|
| 1 | `chore(hwpx): extract golden reference data + test infrastructure` | dev/golden/, tests/ |
| 2 | `fix(md_parser): support standard markdown image + caption pairing` | md_parser.py, tests/ |
| 3 | `fix(md_parser): handle blockquote, circle-numbered, bold labels` | md_parser.py, tests/ |
| 4 | `feat(analyze_template): improve style-map extraction accuracy` | analyze_template.py, tests/ |
| 5 | `fix(xml_writer): wrap fragment in hs:sec with secPr` | xml_writer.py, tests/ |
| 6 | `fix(xml_writer): strip double-bullets + table colSpan/rowSpan` | xml_writer.py, tests/ |
| 7 | `feat(xml_writer): generate professional image+caption XML` | xml_writer.py, tests/ |
| 8 | `feat(image_embedder): standard paths + auto-mapping + JPEG` | image_embedder.py, tests/ |
| 9 | `feat(hwpx-core): add proofread.py quality enforcement` | proofread.py, tests/ |
| 10 | `fix(page_guard): template-fill mode + validate proofread gate` | page_guard.py, validate.py, tests/ |
| 11 | `docs(hwpx-builder): update Workflow 7 with proofreading + image-caption` | hwpx-builder.md, hwpx-generate.md |
| 12 | `test(hwpx): add E2E integration test with dev/ data` | tests/ |

---

## Success Criteria

### Verification Commands
```bash
# 전체 테스트
python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v  # Expected: ALL PASS

# E2E 파이프라인
python validate.py --strict output.hwpx  # Expected: PASS
python proofread.py output.hwpx  # Expected: {"double_bullets": 0, ...}
python page_guard.py --reference "dev/(양식) '27년도 전략연구사업 제안서_작성.hwpx" --output output.hwpx  # Expected: PASS (<=5 warnings)
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All pytest tests pass
- [ ] E2E pipeline produces valid HWPX from dev/ data
- [ ] 15 images embedded with professional captions
- [ ] Zero double-bullet paragraphs in output
- [ ] proofread.py returns clean report
- [ ] Workflow 1-6 unchanged (no regression)
