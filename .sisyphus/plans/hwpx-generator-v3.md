# hwpx-generator v3.0: 마크다운 → HWPX 템플릿 채우기 + 이미지 임베딩 + 포맷 보존

## TL;DR

> **Quick Summary**: hwpx-generator 플러그인에 "마크다운 콘텐츠를 HWPX 양식에 정확하게 채우는" 새 워크플로우를 추가하고, 이미지 임베딩, 불릿/들여쓰기 보존, 표 정확 변환 기능을 구현한다. 기존 워크플로우는 유지하면서 새 스크립트 3개 + 에이전트 가이드 개선으로 6가지 핵심 문제를 해결한다.
> 
> **Deliverables**:
> - 새 Python 스크립트 3개: `md_parser.py`, `xml_writer.py`, `image_embedder.py`
> - 기존 스크립트 1개 개선: `analyze_template.py` (상세 스타일 주석 출력 추가)
> - 에이전트/스킬 가이드 3개 업데이트: `hwpx-core/SKILL.md`, `hwpx-builder.md`, `hwpx-generate.md`
> - 버전/레지스트리 업데이트: `plugin.json`, `marketplace.json`, `AGENTS.md`, `README.md`
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: T1(md_parser) + T2(xml_writer) → T5(SKILL.md) → T8(integration test) → T9(registry)

---

## Context

### Original Request
dev/ 폴더의 마크다운 문서(3_비전_및_목표_v2.md, 4_핵심_연구내용v_2.md)를 정부 양식 HWPX 템플릿('27년도 전략연구사업 제안서_초안_임무.hwpx)에 채우는 과정에서 발생하는 6가지 품질 문제를 해결하라.

### Interview Summary
**Key Discussions**:
- **범용 기능**: 특정 양식 전용이 아닌, 다양한 HWPX 양식에 마크다운 콘텐츠를 채우는 범용 워크플로우로 개발
- **에이전트 자동 매핑**: 양식 텍스트와 MD 제목을 매칭하여 에이전트가 자동으로 콘텐츠 위치를 결정
- **이미지 임베드**: BinData/ 폴더에 PNG 포함, content.hpf 등록, `<hp:pic>` XML 참조
- **기존 워크플로우 유지+개선**: Workflow 1~6 유지, Workflow 7 추가

**Research Findings**:
- 양식 section0.xml: 480KB, 118개 paraPr, 150+ charPr, 31개 테이블 — 에이전트가 직접 수정하기에 너무 복잡
- 이미지 임베딩 구조: `BinData/imageN.png` + `content.hpf <opf:item>` + `section0.xml <hp:pic><hc:img binaryItemIDRef="imageN"/></hp:pic>`
- 현재 v5 결과물: 이미지 1개 임베드 성공, 포맷팅 문제 다수
- 테스트 이미지: `dev/images/` 폴더에 15개 PNG (캡션 텍스트와 파일명 매칭 가능)
- 불릿 처리: paraPr의 `left` margin + `indent` 값으로 hanging indent 구현, 문자(◦, –, □) 사용

### Metis Review
**Identified Gaps** (addressed):
1. **패키징 경로 결정**: 새 워크플로우는 zip_surgery 기반으로 결정 (기존 양식 구조 최대 보존)
2. **섹션 불일치 전략**: MD 섹션 수 ≠ 템플릿 슬롯 수일 때 에이전트가 보고 + 사용자 확인
3. **charPr 폰트 크기 상속**: 템플릿 고유 ID 사용 (빌트인 예약 ID 30-34 대신 템플릿의 실제 ID)
4. **XML 이스케이핑**: md_parser.py에서 `<`, `>`, `&` 등 자동 이스케이프
5. **문단 ID 충돌 방지**: 생성 시 9000000001부터 시작하여 기존 ID와 충돌 회피

---

## Work Objectives

### Core Objective
hwpx-generator가 마크다운 콘텐츠를 HWPX 양식에 채울 때 양식의 포맷(불릿, 들여쓰기, 폰트, 표 구조)을 정확히 보존하고, 이미지를 자동 삽입하는 기능을 추가한다.

### Concrete Deliverables
- `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py`
- `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py`
- `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py`
- 수정: `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py`
- 수정: `plugins/hwpx-generator/skills/hwpx-core/SKILL.md`
- 수정: `plugins/hwpx-generator/agents/hwpx-builder.md`
- 수정: `plugins/hwpx-generator/commands/hwpx-generate.md`
- 수정: `plugins/hwpx-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`

### Definition of Done
- [ ] dev/ 폴더의 양식 + MD 2개 + 이미지 15개로 end-to-end 실행 시 한글 오피스에서 정상 열림
- [ ] 불릿(◦) 포인트가 양식의 들여쓰기 스타일과 일치 (hanging indent)
- [ ] 표가 MD 원본 데이터 그대로 생성 (불필요한 ■ 등 없음)
- [ ] 이미지 15개가 BinData/에 포함되고 캡션 위치에 표시
- [ ] 양식 고유 폰트 크기(10pt, 13pt, 16pt 등) 보존
- [ ] validate.py 통과

### Must Have
- 마크다운 → 구조화 데이터 파싱 (headings, bullets, tables, image_refs, paragraphs, bold/italic)
- 템플릿 스타일 ID 자동 추출 및 적용 (charPrIDRef, paraPrIDRef, borderFillIDRef)
- 불릿 hanging indent (paraPr left margin + indent)
- 표 faithful 변환 (셀 내용 그대로, 열 너비 균등 분배)
- 이미지 임베딩 (BinData/ + content.hpf + `<hp:pic>`)
- XML 특수문자 이스케이핑 (`<`, `>`, `&`, `"`, `'`)
- 문단 ID 충돌 방지 (9000000001부터 순차)

### Must NOT Have (Guardrails)
- 빌트인 예약 charPr ID (30-34)를 템플릿 채우기에 사용하지 않음 — 반드시 템플릿 고유 ID 사용
- 에이전트가 직접 section0.xml 전체를 작성하지 않음 — 스크립트가 XML 생성, 에이전트는 매핑만
- 표 셀에 불필요한 마커(■, ▶ 등) 추가하지 않음 — MD 원본 데이터만
- 양식 구조(문단 수, 표 구조, secPr)를 임의 변경하지 않음
- Markdown 기호(**,*,#,-,>,```)를 `<hp:t>` 텍스트에 포함하지 않음
- `.hwp` 바이너리 지원 시도하지 않음

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (pytest 없음)
- **Automated tests**: NO
- **Framework**: N/A
- **QA Policy**: Agent-Executed QA (validate.py + page_guard.py + 한글 오피스 스크린샷)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Scripts**: Bash로 실행 — 입력 데이터 제공, 출력 JSON/XML 검증, 에러 케이스 테스트
- **HWPX 결과**: validate.py + page_guard.py + 한글 오피스 열기(Playwright) 스크린샷
- **에이전트 가이드**: 실제 실행 후 결과물 품질 확인

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 4 parallel script tasks):
├── Task 1: md_parser.py [deep]
├── Task 2: xml_writer.py [deep]
├── Task 3: image_embedder.py [deep]
└── Task 4: analyze_template.py enhancement [unspecified-high]

Wave 2 (After Wave 1 — 3 parallel agent guide tasks):
├── Task 5: hwpx-core/SKILL.md update (depends: 1,2,3,4) [unspecified-high]
├── Task 6: hwpx-builder.md update (depends: 1,2,3,4) [unspecified-high]
└── Task 7: hwpx-generate.md update (depends: 5,6) [quick]

Wave 3 (After Wave 2 — integration + registry):
├── Task 8: End-to-end integration test (depends: 5,6,7) [deep]
└── Task 9: Version & registry updates (depends: 8) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| T1 (md_parser) | — | T5, T6, T8 | 1 |
| T2 (xml_writer) | — | T5, T6, T8 | 1 |
| T3 (image_embedder) | — | T5, T6, T8 | 1 |
| T4 (analyze_template) | — | T5, T6, T8 | 1 |
| T5 (SKILL.md) | T1, T2, T3, T4 | T7, T8 | 2 |
| T6 (hwpx-builder.md) | T1, T2, T3, T4 | T7, T8 | 2 |
| T7 (hwpx-generate.md) | T5, T6 | T8 | 2 |
| T8 (integration test) | T5, T6, T7 | T9 | 3 |
| T9 (registry updates) | T8 | F1-F4 | 3 |

### Agent Dispatch Summary

- **Wave 1**: **4 tasks** — T1 → `deep`, T2 → `deep`, T3 → `deep`, T4 → `unspecified-high`
- **Wave 2**: **3 tasks** — T5 → `unspecified-high`, T6 → `unspecified-high`, T7 → `quick`
- **Wave 3**: **2 tasks** — T8 → `deep`, T9 → `quick`
- **FINAL**: **4 tasks** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. md_parser.py — 마크다운 파일을 구조화된 JSON 블록으로 파싱

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` 생성
  - 마크다운 파일을 읽어 아래 블록 타입으로 파싱:
    - `heading`: level(1-4), text (# 기호 제거)
    - `paragraph`: text (일반 본문)
    - `bullet`: marker(◦, –, □ 등), text, bold_parts 배열 (인라인 **bold** 추출)
    - `table`: headers 배열, rows 2D 배열, col_count
    - `image_ref`: id("3-1"), caption 텍스트 (`<그림 N-N: 캡션>` 패턴 파싱)
    - `separator`: (--- 수평선)
    - `blockquote`: text (> 기호 제거)
  - 인라인 마크다운 서식 처리:
    - `**bold**` → `{type: "bold", text: "bold"}` 세그먼트로 분리
    - `*italic*` → `{type: "italic", text: "italic"}` 세그먼트
    - 서식 없는 텍스트 → `{type: "plain", text: "..."}` 세그먼트
    - 각 paragraph/bullet의 텍스트를 segments 배열로 분할
  - XML 특수문자 자동 이스케이핑: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;` (Metis 지적사항)
  - CLI: `python3 md_parser.py <input.md> --output <output.json>`
  - 에러 처리: 파일 미존재, 인코딩 오류, 비정상 마크다운 구문
  - stdlib만 사용 (외부 의존성 없음, `re` + `json` + `argparse`)

  **Must NOT do**:
  - 외부 마크다운 파서 라이브러리(markdown, mistune 등) 사용 금지 — stdlib만
  - 마크다운 기호를 출력 텍스트에 포함하지 않음
  - HTML 태그를 마크다운에서 해석하지 않음 (`<u>` 등은 plain text 취급)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 마크다운 파싱 로직이 다양한 엣지케이스(중첩 서식, 빈 행, 테이블 내 특수문자)를 처리해야 함
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/text_extract.py` — 기존 HWPX 텍스트 추출 스크립트. CLI 패턴, argparse 사용법 참조.
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — 기존 분석 스크립트. 출력 포맷 및 에러 처리 패턴 참조.

  **Input References** (테스트 데이터):
  - `dev/3_비전_및_목표_v2.md` — 테스트 입력 1. 포함 요소: ◦ 불릿, **bold**, 파이프 테이블, `<그림 N-N:>` 이미지 참조
  - `dev/4_핵심_연구내용v_2.md` — 테스트 입력 2. 포함 요소: 다단계 제목(##, ###, ####), > blockquote, 복잡한 테이블, 다수 이미지 참조

  **WHY Each Reference Matters**:
  - text_extract.py: CLI 구조와 argparse 패턴을 동일하게 따르면 사용자 경험 일관성 유지
  - dev/ MD 파일들: 이 파일들이 실제 테스트 케이스이므로, 파서가 이 파일들의 모든 구문을 정확히 처리해야 함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 비전_및_목표 마크다운 파싱 (happy path)
    Tool: Bash (workdir: project root)
    Preconditions: dev/3_비전_및_목표_v2.md 존재
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py dev/3_비전_및_목표_v2.md --output /tmp/parsed_ch3.json
      2. python3 -c "import json; d=json.load(open('/tmp/parsed_ch3.json')); print(len(d['blocks']))"
      3. python3 -c "import json; d=json.load(open('/tmp/parsed_ch3.json')); types=[b['type'] for b in d['blocks']]; print('heading' in types, 'bullet' in types, 'table' in types, 'image_ref' in types)"
      4. mkdir -p .sisyphus/evidence && cp /tmp/parsed_ch3.json .sisyphus/evidence/task-1-parse-ch3.json
    Expected Result: 종료코드 0, blocks 수 > 20, 모든 타입(heading, bullet, table, image_ref) True
    Failure Indicators: 종료코드 비0, KeyError, 빈 blocks, 누락된 타입
    Evidence: .sisyphus/evidence/task-1-parse-ch3.json

  Scenario: XML 특수문자 이스케이핑 (edge case)
    Tool: Bash (workdir: project root)
    Preconditions: 테스트 MD 파일에 `<`, `>`, `&` 포함
    Steps:
      1. printf '# Test\n\nA < B & C > D\n' > /tmp/test_escape.md
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py /tmp/test_escape.md --output /tmp/parsed_escape.json
      3. python3 -c "import json; d=json.load(open('/tmp/parsed_escape.json')); t=d['blocks'][1]['segments'][0]['text']; assert '&lt;' in t and '&amp;' in t and '&gt;' in t, f'Not escaped: {t}'"
      4. cp /tmp/parsed_escape.json .sisyphus/evidence/task-1-xml-escape.json
    Expected Result: 특수문자가 XML 엔티티로 이스케이프됨
    Failure Indicators: `<`, `>`, `&` 가 raw로 남아있음
    Evidence: .sisyphus/evidence/task-1-xml-escape.json

  Scenario: 존재하지 않는 파일 (error case)
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py /tmp/nonexistent.md --output /tmp/out.json 2>&1; echo "EXIT:$?"
    Expected Result: 에러 메시지 출력, 종료코드 비0
    Evidence: .sisyphus/evidence/task-1-error.txt
  ```

  **Commit**: YES (group with T2, T3, T4)
  - Message: `feat(hwpx): add md_parser.py for markdown→structured data`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py`

- [x] 2. xml_writer.py — 구조화된 JSON 블록 + 스타일 설정 → HWPX XML 프래그먼트 생성

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` 생성
  - 입력: md_parser.py 출력 JSON + 스타일 설정 JSON
  - 스타일 설정 JSON 형식:
    ```json
    {
      "heading_1": {"charPrIDRef": "48", "paraPrIDRef": "71"},
      "heading_2": {"charPrIDRef": "88", "paraPrIDRef": "38"},
      "body": {"charPrIDRef": "36", "paraPrIDRef": "41"},
      "bullet": {"charPrIDRef": "36", "paraPrIDRef": "40", "left_margin": 600, "indent": -600},
      "bold": {"charPrIDRef": "49"},
      "table_header": {"charPrIDRef": "95", "paraPrIDRef": "106", "borderFillIDRef": "4"},
      "table_cell": {"charPrIDRef": "48", "paraPrIDRef": "98", "borderFillIDRef": "3"},
      "table_width": 42520,
      "image_placeholder": {"paraPrIDRef": "0", "charPrIDRef": "0"}
    }
    ```
  - 출력: `<hp:p>` 요소들의 XML 문자열 (section0.xml에 삽입 가능한 프래그먼트)
  - **불릿 처리 (핵심)**:
    - paraPr의 left margin과 indent(음수 = hanging indent)로 깔끔한 들여쓰기 구현
    - 불릿 마커(◦, –, □ 등)를 첫 번째 run에 포함, 후속 텍스트는 별도 run
    - `<hp:p paraPrIDRef="40">` 사용 (스타일 설정에서 가져옴)
  - **표 처리 (핵심)**:
    - MD 테이블 → `<hp:tbl>` 변환
    - 열 너비: table_width를 col_count로 균등 분배 (합계 = table_width)
    - 행 높이: 기본 2400 HWPUNIT, `noAdjust="0"` + `pageBreak="CELL"` 필수
    - 헤더 행: table_header 스타일, 데이터 행: table_cell 스타일
    - 셀 내용은 MD 원본 그대로 — 불필요한 마커 추가 금지
  - **인라인 서식 처리**:
    - bold 세그먼트 → 별도 `<hp:run charPrIDRef="bold_id">` (multi-run 분할)
    - italic 세그먼트 → 별도 run
    - plain 세그먼트 → 기본 charPrIDRef run
  - **이미지 참조 위치 마킹**:
    - image_ref 블록 → `<!--IMAGE:imageN-->` 주석으로 위치 표시 (image_embedder.py가 나중에 교체)
  - **문단 ID**: 9000000001부터 순차 증가 (Metis 지적: 기존 템플릿 ID와 충돌 방지)
  - CLI: `python3 xml_writer.py --input <parsed.json> --style-config <styles.json> --output <fragment.xml>`
  - stdlib만 사용 (`xml.etree.ElementTree`는 사용 가능하나, 문자열 기반 생성 권장 — 네임스페이스 보존)
  - 외부 의존성(Pillow, lxml, markdown 등) 일절 사용 금지 — 프로젝트 컨벤션

  **Must NOT do**:
  - lxml 사용 금지 (프로젝트 컨벤션: stdlib only)
  - `ET.tostring()` / `tree.write()` 사용 금지 (AGENTS.md 규칙: 네임스페이스 깨짐)
  - 빌트인 예약 charPr ID 30-34 하드코딩 금지 — 반드시 스타일 설정 JSON에서 읽어야 함
  - 표 셀에 ■, ▶ 등 불필요한 마커 추가 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: HWPX XML 구조(네임스페이스, 속성, 중첩)를 정확히 생성해야 하며, 표/불릿/인라인 서식 모두 처리
  - **Skills**: [`hwpx-core`]
    - `hwpx-core`: HWPX XML 구조, 단위 변환, 스타일 ID 체계, 표 작성법 참조 필수

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:348-427` — section0.xml 작성 가이드: 문단, 빈 줄, 서식 혼합 런, 표 작성법의 XML 구조를 그대로 따를 것
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:430-441` — 표 크기 계산: A4 본문폭 42520, 열 너비 합 = 본문폭, 행 높이 2400~3600

  **API/Type References**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:113-124` — 단위 변환표 (1pt = 100 HWPUNIT, A4 body width = 42520)
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md:655-666` — 표 행 높이 자동 조절: `noAdjust="0"` + `pageBreak="CELL"` 필수

  **WHY Each Reference Matters**:
  - SKILL.md 348-427: XML 프래그먼트 생성의 정확한 구조 템플릿. 이 구조를 벗어나면 한글 오피스에서 열리지 않음
  - 단위 변환: 열 너비, 행 높이 등 모든 수치가 HWPUNIT 기준이므로 변환 참조 필수

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 파싱된 JSON → XML 프래그먼트 생성 (happy path)
    Tool: Bash (workdir: project root)
    Preconditions: /tmp/parsed_ch3.json (Task 1 출력 완료)
    Steps:
      1. python3 -c "import json; json.dump({'heading_1':{'charPrIDRef':'48','paraPrIDRef':'71'},'body':{'charPrIDRef':'36','paraPrIDRef':'41'},'bullet':{'charPrIDRef':'36','paraPrIDRef':'40','left_margin':600,'indent':-600},'bold':{'charPrIDRef':'49'},'table_header':{'charPrIDRef':'95','paraPrIDRef':'106','borderFillIDRef':'4'},'table_cell':{'charPrIDRef':'48','paraPrIDRef':'98','borderFillIDRef':'3'},'table_width':42520,'image_placeholder':{'paraPrIDRef':'0','charPrIDRef':'0'}}, open('/tmp/test_styles.json','w'))"
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py --input /tmp/parsed_ch3.json --style-config /tmp/test_styles.json --output /tmp/fragment.xml
      3. grep 'paraPrIDRef="71"' /tmp/fragment.xml
      4. grep 'paraPrIDRef="40"' /tmp/fragment.xml
      5. grep '<hp:tbl' /tmp/fragment.xml
      6. grep '<!--IMAGE:' /tmp/fragment.xml
      7. cp /tmp/fragment.xml .sisyphus/evidence/task-2-xml-fragment.xml
    Expected Result: 종료코드 0, heading/bullet/table/image 모두 포함된 유효한 XML
    Failure Indicators: 종료코드 비0, paraPrIDRef 누락, 빌트인 ID 30-34 사용
    Evidence: .sisyphus/evidence/task-2-xml-fragment.xml

  Scenario: 표에 불필요한 마커 없음 (regression test)
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 -c "import json; d={'blocks':[{'type':'table','headers':['A','B'],'rows':[['1','2']]}]}; json.dump(d, open('/tmp/tbl_test.json','w'))"
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py --input /tmp/tbl_test.json --style-config /tmp/test_styles.json --output /tmp/tbl_out.xml
      3. python3 -c "data=open('/tmp/tbl_out.xml').read(); assert '■' not in data and '▶' not in data, 'Found unwanted markers'"
    Expected Result: 표에 ■, ▶ 등 불필요한 마커 없음
    Evidence: .sisyphus/evidence/task-2-table-clean.xml
  ```

  **Commit**: YES (group with T1, T3, T4)
  - Message: `feat(hwpx): add xml_writer.py for structured data→HWPX XML`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py`

- [x] 3. image_embedder.py — PNG 이미지를 HWPX에 임베딩

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` 생성
  - 입력: HWPX 파일, 이미지 디렉토리, 캡션-파일 매핑 JSON
  - 매핑 JSON 형식:
    ```json
    {
      "image1": {"file": "01_비전_개념도.png", "caption": "비전 개념도 — 인구절벽..."},
      "image2": {"file": "02_최종_연구목표_체계도.png", "caption": "최종 연구목표 체계도..."}
    }
    ```
  - 처리 과정:
    1. HWPX ZIP 열기
    2. 각 이미지를 `BinData/imageN.png`로 ZIP에 추가
    3. `Contents/content.hpf`에 `<opf:item id="imageN" href="BinData/imageN.png" media-type="image/png" isEmbeded="1"/>` 추가
    4. `Contents/section0.xml`에서 `<!--IMAGE:imageN-->` 주석을 `<hp:pic>` 요소로 교체
    5. `<hp:pic>` 구조: `<hp:sz>` (본문폭 42520, 높이=원본비율유지), `<hp:pos treatAsChar="1">`, `<hc:img binaryItemIDRef="imageN"/>`
  - 이미지 크기 계산: stdlib만 사용하여 PNG 헤더 파싱 (파일의 16~24바이트에서 width/height 읽기, `struct.unpack('>II', f.read(8))`). Pillow 등 외부 의존성 사용 금지. 본문폭(42520 HWPUNIT) 기준 비율 유지하여 높이 계산 (`height_hwp = int(img_height / img_width * 42520)`)
  - CLI: `python3 image_embedder.py --hwpx <input.hwpx> --images-dir <dir> --mapping <mapping.json> --output <output.hwpx>`
  - 자동 매핑 모드: `--auto-map` 플래그 — 이미지 파일명과 캡션 텍스트를 fuzzy 매칭
  - PNG 크기 읽기 구현 예시 (stdlib only):
    ```python
    import struct
    def png_dimensions(path):
        with open(path, 'rb') as f:
            f.read(16)  # PNG signature + IHDR chunk header
            width, height = struct.unpack('>II', f.read(8))
        return width, height
    ```
  - 에러 처리: 이미지 파일 미존재, 지원하지 않는 포맷(PNG만 지원), 매핑 불일치

  **Must NOT do**:
  - lxml 사용 금지 (문자열 기반 XML 편집)
  - content.hpf 전체를 재작성하지 않음 — 기존 내용에 item 추가만
  - section0.xml의 기존 구조를 변경하지 않음 — 주석 위치에만 삽입

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: ZIP 레벨 조작 + XML 문자열 편집 + 이미지 크기 계산의 복합 작업
  - **Skills**: [`hwpx-core`]
    - `hwpx-core`: zip_surgery 패턴, content.hpf 구조, HWPUNIT 단위 참조

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` — ZIP 레벨 HWPX 편집 패턴. `HwpxSurgeon` 클래스의 ZIP 읽기/쓰기, content.hpf 업데이트 방식 참조
  - `dev/결과_27년도_전략연구사업_제안서_초안_임무_v5.hwpx` — 이미지 임베딩 성공 사례. BinData/image1.png 포함, content.hpf에 `<opf:item id="image1">` 등록, section0.xml에 `<hp:pic>...<hc:img binaryItemIDRef="image1"/></hp:pic>` 참조

  **External References**:
  - `dev/결과_...v5.hwpx`의 `<hp:pic>` XML 구조 (분석 완료):
    ```xml
    <hp:pic id="..." zOrder="48" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0">
      <hp:imgRect><hc:pt0 x="0" y="0"/>...<hc:pt3 x="0" y="73740"/></hp:imgRect>
      <hp:imgClip left="0" right="412800" top="0" bottom="230400"/>
      <hp:imgDim dimwidth="412800" dimheight="230400"/>
      <hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>
      <hp:sz width="42520" widthRelTo="ABSOLUTE" height="23718" heightRelTo="ABSOLUTE" protect="0"/>
      <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
    </hp:pic>
    ```

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 단일 이미지 임베딩 (happy path)
    Tool: Bash (workdir: project root)
    Preconditions: dev/images/01_비전_개념도.png 존재
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/build_hwpx.py --output /tmp/test_img_base.hwpx
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py extract /tmp/test_img_base.hwpx -o /tmp/test_section.xml
      3. python3 -c "data=open('/tmp/test_section.xml').read(); data=data.replace('</hs:sec>','<!--IMAGE:image1-->\n</hs:sec>'); open('/tmp/test_section_marked.xml','w').write(data)"
      4. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py replace /tmp/test_img_base.hwpx -s /tmp/test_section_marked.xml -o /tmp/test_img_marked.hwpx
      5. python3 -c "import json; json.dump({'image1':{'file':'01_비전_개념도.png','caption':'test'}}, open('/tmp/img_map.json','w'))"
      6. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py --hwpx /tmp/test_img_marked.hwpx --images-dir dev/images/ --mapping /tmp/img_map.json --output /tmp/test_with_img.hwpx
      7. python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/test_with_img.hwpx'); assert 'BinData/image1.png' in z.namelist(), 'image1.png not in BinData/'; print('PASS: image1.png found in BinData/')"
      8. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py /tmp/test_with_img.hwpx 2>&1 | tee .sisyphus/evidence/task-3-image-embed.txt
    Expected Result: BinData/image1.png 존재, validate.py PASS
    Failure Indicators: ZIP 엔트리 누락, content.hpf 미업데이트, XML 구문 오류
    Evidence: .sisyphus/evidence/task-3-image-embed.txt

  Scenario: 이미지 파일 미존재 (error case)
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 -c "import json; json.dump({'image1':{'file':'NONEXISTENT.png','caption':'test'}}, open('/tmp/bad_map.json','w'))"
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py --hwpx /tmp/test_img_marked.hwpx --images-dir dev/images/ --mapping /tmp/bad_map.json --output /tmp/out.hwpx 2>&1; echo "EXIT:$?"
    Expected Result: 에러 메시지 "NONEXISTENT.png not found" 출력, 종료코드 비0
    Evidence: .sisyphus/evidence/task-3-error.txt
  ```

  **Commit**: YES (group with T1, T2, T4)
  - Message: `feat(hwpx): add image_embedder.py for HWPX image embedding`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py`

- [x] 4. analyze_template.py 개선 — 상세 스타일 주석 출력 추가

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` 수정
  - 기존 기능 유지 + `--style-map` 옵션 추가
  - `--style-map <output.json>` 실행 시 xml_writer.py용 스타일 설정 JSON을 자동 생성:
    - 양식의 문단별 사용된 charPrIDRef, paraPrIDRef 빈도 분석
    - 가장 많이 사용된 스타일을 "body" 스타일로 추정
    - 불릿 마커(◦, –, □ 등)가 포함된 문단의 스타일을 "bullet" 스타일로 추정
    - 표 셀 내부 문단의 스타일을 "table_cell"/"table_header" 스타일로 추정
    - heading 스타일: 큰 폰트 크기(charPr height > 1200)를 사용하는 문단을 heading으로 추정
  - **paraPr 상세 추출 개선**: 각 paraPr의 left margin, indent 값을 명시적으로 출력 (현재 분석에서 N/A로 나오는 문제 해결)
  - 출력 예시:
    ```json
    {
      "heading_1": {"charPrIDRef": "48", "paraPrIDRef": "71"},
      "heading_2": {"charPrIDRef": "88", "paraPrIDRef": "38"},
      "body": {"charPrIDRef": "36", "paraPrIDRef": "41"},
      "bullet": {"charPrIDRef": "36", "paraPrIDRef": "40", "left_margin": 600, "indent": -600},
      "bold": {"charPrIDRef": "49"},
      "table_header": {"charPrIDRef": "95", "paraPrIDRef": "106", "borderFillIDRef": "4"},
      "table_cell": {"charPrIDRef": "48", "paraPrIDRef": "98", "borderFillIDRef": "3"},
      "table_width": 42520,
      "image_placeholder": {"paraPrIDRef": "0", "charPrIDRef": "0"},
      "font_sizes": {"48": "10pt", "88": "13pt", "95": "10pt bold"}
    }
    ```
  - 기존 CLI 옵션(--extract-header, --extract-section)은 그대로 유지

  **Must NOT do**:
  - 기존 기능/출력 포맷을 변경하지 않음 (하위 호환성 유지)
  - 스타일 추정이 틀릴 수 있음을 인지 — JSON 출력에 `"confidence": "estimated"` 표시

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 기존 스크립트 수정이므로 기존 로직 이해 필요, 스타일 추정 로직은 휴리스틱 기반
  - **Skills**: [`hwpx-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py` — 수정 대상 파일. 기존 분석 로직(charPr, paraPr, borderFill, 표 구조 추출) 이해 필수
  - `dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx` — 테스트 입력. 118개 paraPr, 150+ charPr 정의

  **WHY Each Reference Matters**:
  - analyze_template.py: 기존 로직에 --style-map 기능을 추가해야 하므로 전체 코드 이해 필수
  - 양식 HWPX: 이 양식에서 추출한 스타일 맵이 xml_writer.py의 입력이 되므로, 정확한 추출 검증 필요

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 양식에서 스타일 맵 추출 (happy path)
    Tool: Bash (workdir: project root)
    Preconditions: dev/(양식) HWPX 존재
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py "dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx" --style-map /tmp/styles.json
      2. python3 -c "import json; d=json.load(open('/tmp/styles.json')); keys=list(d.keys()); assert 'body' in keys and 'bullet' in keys and 'table_cell' in keys, f'Missing keys: {keys}'; print('PASS:', keys)"
    Expected Result: body, bullet, table_header, table_cell 등 키 포함
    Failure Indicators: KeyError, 빈 JSON, 필수 키 누락
    Evidence: .sisyphus/evidence/task-4-style-map.json

  Scenario: 하위 호환성 (regression test)
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py "dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx" --extract-header /tmp/h.xml --extract-section /tmp/s.xml
      2. python3 -c "import os; assert os.path.getsize('/tmp/h.xml')>1000, 'header too small'; assert os.path.getsize('/tmp/s.xml')>1000, 'section too small'; print('PASS: both extracted')"
    Expected Result: 기존 --extract-header/--extract-section 정상 동작, 파일 크기 > 1KB
    Evidence: .sisyphus/evidence/task-4-compat.txt
  ```

  **Commit**: YES (group with T1, T2, T3)
  - Message: `enhance(hwpx): add --style-map to analyze_template.py`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py`

- [x] 5. hwpx-core/SKILL.md 업데이트 — Workflow 7 + 이미지/불릿/표 가이드 추가

  **What to do**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` 수정
  - **Workflow 7 추가**: "마크다운 → HWPX 템플릿 채우기" 전체 워크플로우 문서화
    1. `analyze_template.py --style-map` → 스타일 설정 추출
    2. `md_parser.py` → 마크다운 파싱
    3. 에이전트가 MD 섹션 ↔ 템플릿 영역 매핑 결정
    4. `xml_writer.py` → 스타일 적용된 XML 프래그먼트 생성
    5. `zip_surgery.py` → 템플릿의 해당 영역에 XML 삽입
    6. `image_embedder.py` → 이미지 임베딩
    7. `validate.py` + `page_guard.py` → 검증
  - **이미지 임베딩 가이드 추가**: 새 섹션
    - HWPX 이미지 구조 설명 (BinData/ + content.hpf + `<hp:pic>`)
    - image_embedder.py 사용법
    - `<hp:pic>` XML 구조 예시
  - **불릿 포인트 가이드 강화**: 기존 "문단" 섹션에 추가
    - hanging indent 구현법: paraPr left margin + 음수 indent
    - 불릿 마커(◦, –, □)를 첫 run에 포함, 텍스트는 후속 run
    - 올바른 예시 XML과 잘못된 예시 XML 비교
  - **표 변환 가이드 강화**: 기존 "표 작성법" 섹션에 추가
    - "MD 원본 데이터 그대로" 원칙 명시
    - 금지 패턴: 셀에 불필요한 ■, ▶ 등 마커 추가
    - 열 너비 균등 분배 공식
  - **스크립트 요약 테이블 업데이트**: md_parser.py, xml_writer.py, image_embedder.py 3개 추가 (9개 → 12개)
  - **템플릿 스타일 ID 사용 원칙**: "반드시 analyze_template.py --style-map 출력의 ID를 사용, 빌트인 ID 30-34는 XML-first 전용"

  **Must NOT do**:
  - 기존 Workflow 1~6의 내용 변경 금지
  - 기존 Critical Rules 변경 금지 (추가만 가능)
  - 500줄 이상으로 팽창시키지 않음 (현재 719줄 → 상세 내용은 references/ 분리)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 기존 SKILL.md 구조를 이해하고 일관성 있게 새 내용 추가
  - **Skills**: [`hwpx-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 6)
  - **Blocks**: Tasks 7, 8
  - **Blocked By**: Tasks 1, 2, 3, 4

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` — 수정 대상. 기존 구조(Workflow 1-6, Critical Rules, 스크립트 요약) 파악 필수
  - Task 1~4의 스크립트 — 새로 추가될 스크립트의 CLI 인터페이스와 입출력을 정확히 문서화해야 함

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Workflow 7 문서 완성도 확인
    Tool: Bash (grep)
    Steps:
      1. grep -c 'Workflow 7' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      2. grep 'md_parser' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      3. grep 'xml_writer' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      4. grep 'image_embedder' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      5. grep 'hanging indent' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
    Expected Result: 모든 grep 결과 1개 이상 매치
    Evidence: .sisyphus/evidence/task-5-skill-check.txt
  ```

  **Commit**: YES (group with T6, T7)
  - Message: `docs(hwpx): add Workflow 7 and update agent guides`
  - Files: `SKILL.md`, `hwpx-builder.md`, `hwpx-generate.md`

- [x] 6. hwpx-builder.md 업데이트 — 템플릿 채우기 워크플로우 및 스타일 보존 규칙

  **What to do**:
  - `plugins/hwpx-generator/agents/hwpx-builder.md` 수정
  - **Workflow 섹션에 템플릿 채우기 모드 추가** (Step 2 "Select generation mode"에):
    - 새 모드: "마크다운 콘텐츠 + HWPX 양식" → Workflow 7 (md_parser → xml_writer → zip_surgery → image_embedder)
    - 기존 4가지 모드(기존 편집, 레퍼런스 우선, 템플릿, XML-first) 다음에 추가
  - **스타일 보존 규칙 섹션 추가**:
    - "analyze_template.py --style-map으로 추출한 스타일 ID만 사용"
    - "빌트인 예약 ID (30-34)는 XML-first 전용, 템플릿 채우기에 사용 금지"
    - "양식의 폰트 크기를 변경하지 않음"
  - **불릿 포인트 처리 규칙 추가**:
    - "◦, –, □ 등 불릿 마커는 양식 원본의 마커를 따름"
    - "들여쓰기는 paraPr의 left margin + indent로 구현, 공백 문자 사용 금지"
  - **표 생성 규칙 추가**:
    - "MD 테이블 데이터를 그대로 셀에 삽입, 불필요한 마커(■ 등) 추가 금지"
  - **이미지 삽입 섹션 추가**:
    - "MD의 `<그림 N-N:>` 캡션과 이미지 파일을 매칭하여 image_embedder.py로 임베딩"
  - **Constraints에 추가**:
    - "템플릿 채우기 시 반드시 analyze_template.py --style-map 실행 선행"
    - "xml_writer.py로 XML 생성, 에이전트가 직접 XML 작성 최소화"

  **Must NOT do**:
  - 기존 Workflow 내용 변경 금지
  - 기존 Constraints 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 에이전트 프롬프트 수정은 기존 구조와 일관성 유지가 중요
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Tasks 7, 8
  - **Blocked By**: Tasks 1, 2, 3, 4

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/agents/hwpx-builder.md` — 수정 대상. Workflow 단계(1-5), Constraints, Markdown 입력 처리 섹션 구조 파악

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 에이전트 가이드 완성도
    Tool: Bash (grep)
    Steps:
      1. grep 'style-map' plugins/hwpx-generator/agents/hwpx-builder.md
      2. grep 'image_embedder' plugins/hwpx-generator/agents/hwpx-builder.md
      3. grep 'hanging indent\|left.margin\|들여쓰기' plugins/hwpx-generator/agents/hwpx-builder.md
    Expected Result: 모든 항목 1개 이상 매치
    Evidence: .sisyphus/evidence/task-6-builder-check.txt
  ```

  **Commit**: YES (group with T5, T7)

- [x] 7. hwpx-generate.md 업데이트 — MD 입력 + 이미지 경로 파라미터 추가

  **What to do**:
  - `plugins/hwpx-generator/commands/hwpx-generate.md` 수정
  - **Configuration Options에 추가**:
    - `content_md` (optional): 마크다운 콘텐츠 파일 경로 (단일 파일 또는 디렉토리)
    - `images_dir` (optional): 이미지 파일 디렉토리 경로
  - **Phase 1 (요구사항 파악)에 추가**:
    - MD 파일 입력 감지: `content_md`가 제공되면 "마크다운 → 템플릿 채우기" 모드로 분류
  - **Phase 2 (양식 선택)에 추가**:
    - `content_md` + `template_hwpx` 조합 시 Workflow 7 경로 선택
  - **Phase 3 (문서 생성)에 추가**:
    - hwpx-builder에게 md_parser, xml_writer, image_embedder 사용을 명시적으로 위임
  - **Usage Example 추가**:
    ```
    @hwpx-generator 다음 ARGUMENTS로 HWPX 문서를 생성해줘.
    ARGUMENTS:
    - template_hwpx: ./양식.hwpx
    - content_md: ./3_비전_및_목표.md, ./4_핵심_연구내용.md
    - images_dir: ./output/visuals/images/
    - output_dir: ./output/hwpx/
    ```

  **Must NOT do**:
  - 기존 Phase 구조 변경 금지 (추가만)
  - `content_md` 없는 기존 워크플로우에 영향 주지 않음

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 파라미터 추가와 Phase 분기 추가만 필요한 간단한 수정
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after T5, T6)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 5, 6

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/commands/hwpx-generate.md` — 수정 대상. 기존 Phase 1-5 구조

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 새 파라미터 문서화 확인
    Tool: Bash (grep)
    Steps:
      1. grep 'content_md' plugins/hwpx-generator/commands/hwpx-generate.md
      2. grep 'images_dir' plugins/hwpx-generator/commands/hwpx-generate.md
    Expected Result: 각 2개 이상 매치 (Configuration + Usage)
    Evidence: .sisyphus/evidence/task-7-command-check.txt
  ```

  **Commit**: YES (group with T5, T6)

- [ ] 8. End-to-end 통합 테스트 — dev/ 파일로 전체 워크플로우 실행

  **What to do**:
  - dev/ 폴더의 실제 파일로 Workflow 7 전체를 end-to-end 실행:
    1. `analyze_template.py --style-map` → 양식에서 스타일 추출
    2. `md_parser.py` → 두 MD 파일 파싱
    3. 스타일 맵 검증 및 필요시 수동 조정 (에이전트가 판단)
    4. `xml_writer.py` → XML 프래그먼트 생성
    5. `zip_surgery.py` → 양식의 해당 영역에 삽입
    6. `image_embedder.py` → 15개 이미지 임베딩
    7. `validate.py` → 구조 검증
    8. `page_guard.py` → 페이지 드리프트 검사
  - 결과 HWPX가 한글 오피스에서 정상 열리는지 확인 (가능한 경우 Playwright)
  - **6가지 원래 문제 각각에 대한 검증**:
    1. 불릿 정렬 깔끔한지
    2. 이미지 15개 모두 포함되었는지
    3. 표에 불필요한 마커 없는지
    4. 양식 구조(◦, – 불릿) 보존되었는지
    5. 폰트 크기 양식과 일치하는지
    6. hanging indent 올바른지
  - 문제 발견 시 해당 스크립트/가이드 수정 (반복)

  **Must NOT do**:
  - 테스트 실패를 무시하고 완료 처리 금지
  - dev/ 폴더의 원본 파일 수정 금지

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 전체 워크플로우 실행 + 문제 발견 시 디버깅/수정 반복 필요
  - **Skills**: [`hwpx-core`, `hwpx-templates`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 5, 6, 7

  **References**:

  **Input References**:
  - `dev/3_비전_및_목표_v2.md` — 테스트 MD 1
  - `dev/4_핵심_연구내용v_2.md` — 테스트 MD 2
  - `dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx` — 테스트 양식
  - `dev/images/` — 15개 PNG 이미지 (01_비전_개념도.png ~ 15_세부기술_통합_연계.png). 캡션 텍스트와 파일명으로 매칭 (예: `<그림 3-1: 비전 개념도 ...>` ↔ `01_비전_개념도.png`)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 전체 워크플로우 end-to-end (happy path)
    Tool: Bash (workdir: project root)
    Preconditions: dev/ 폴더에 양식 HWPX, MD 2개, images/ 15개 PNG 존재
    NOTE: 이 태스크는 category=deep 에이전트 태스크. Step 1~7은 도구 실행(scriptable),
    Step 8은 에이전트가 XML을 읽고 편집하는 지능적 작업(agent-driven)이다.
    QA 검증은 최종 출력 기반으로 수행한다 (Step 9~).

    Steps:
      === Phase A: 도구 실행 (scriptable) ===
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/analyze_template.py "dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx" --style-map /tmp/e2e_styles.json
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py dev/3_비전_및_목표_v2.md --output /tmp/e2e_ch3.json
      3. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py dev/4_핵심_연구내용v_2.md --output /tmp/e2e_ch4.json
      4. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py --input /tmp/e2e_ch3.json --style-config /tmp/e2e_styles.json --output /tmp/e2e_ch3_frag.xml
      5. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py --input /tmp/e2e_ch4.json --style-config /tmp/e2e_styles.json --output /tmp/e2e_ch4_frag.xml
      6. cp "dev/(양식) '27년도 전략연구사업 제안서_초안_임무.hwpx" /tmp/e2e_result.hwpx
      7. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py extract /tmp/e2e_result.hwpx -o /tmp/e2e_section.xml

      === Phase B: 에이전트 XML 편집 (agent-driven) ===
      8. 에이전트가 Read 도구로 /tmp/e2e_section.xml과 analyze_template 출력을 읽고,
         "3. 비전 및 목표"와 "4. 핵심 연구내용" 영역의 시작/끝 위치를 식별한 뒤,
         아래 형태의 Python 명령을 구성·실행하여 /tmp/e2e_section_filled.xml을 생성한다:
         ```
         python3 -c "
         s = open('/tmp/e2e_section.xml').read()
         ch3 = open('/tmp/e2e_ch3_frag.xml').read()
         ch4 = open('/tmp/e2e_ch4_frag.xml').read()
         # 에이전트가 식별한 시작/끝 문자열로 영역 교체
         start3 = '<에이전트가_식별한_3장_시작_마커>'
         end3   = '<에이전트가_식별한_3장_끝_마커>'
         i3, j3 = s.index(start3), s.index(end3) + len(end3)
         s = s[:i3] + ch3 + s[j3:]
         # 4장도 동일 패턴
         open('/tmp/e2e_section_filled.xml','w').write(s)
         "
         ```
         (위 마커 값은 에이전트가 analyze_template 출력에서 실제 값으로 대체)

      === Phase C: 조립 및 검증 (scriptable) ===
      9.  python3 plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py replace /tmp/e2e_result.hwpx -s /tmp/e2e_section_filled.xml -o /tmp/e2e_result_filled.hwpx
      10. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py --hwpx /tmp/e2e_result_filled.hwpx --images-dir dev/images/ --auto-map --output /tmp/e2e_final.hwpx
      11. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py /tmp/e2e_final.hwpx 2>&1 | tee .sisyphus/evidence/task-8-e2e-validate.txt
      12. mkdir -p .sisyphus/evidence && cp /tmp/e2e_final.hwpx .sisyphus/evidence/task-8-e2e-result.hwpx

    Image Mapping: Step 10에서 --auto-map 사용. image_embedder.py가 dev/images/ 파일명과
    section XML 내 <!--IMAGE:imageN--> 주석의 캡션을 fuzzy 매칭하여 자동 매핑.
    실제 파일: 01_비전_개념도.png ~ 15_세부기술_통합_연계.png (15개)

    Expected Result: validate.py PASS, BinData/에 이미지 15개 포함, /tmp/e2e_section_filled.xml 존재
    Failure Indicators: validate.py FAIL, 이미지 누락, /tmp/e2e_section_filled.xml 미생성
    Evidence: .sisyphus/evidence/task-8-e2e-validate.txt, .sisyphus/evidence/task-8-e2e-result.hwpx

  Scenario: 6가지 문제 해결 검증
    Tool: Bash (workdir: project root)
    Preconditions: /tmp/e2e_final.hwpx 생성 완료 (위 시나리오)
    Steps:
      1. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py extract /tmp/e2e_final.hwpx -o /tmp/e2e_verify_section.xml
      2. python3 -c "data=open('/tmp/e2e_verify_section.xml').read(); assert '■' not in data, 'Found ■ marker'; print('PASS: no ■ markers')"
      3. python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/e2e_final.hwpx'); imgs=[n for n in z.namelist() if n.startswith('BinData/')]; assert len(imgs)>=15, f'Only {len(imgs)} images'; print(f'PASS: {len(imgs)} images')"
      4. python3 -c "data=open('/tmp/e2e_verify_section.xml').read(); assert 'charPrIDRef=\"30\"' not in data and 'charPrIDRef=\"31\"' not in data and 'charPrIDRef=\"32\"' not in data, 'Found builtin IDs 30-32'; print('PASS: no builtin charPr IDs')"
      5. python3 -c "data=open('/tmp/e2e_verify_section.xml').read(); import re; bullets=re.findall(r'paraPrIDRef=\"(\d+)\".*?◦', data[:50000]); print(f'Bullet style IDs found: {set(bullets) if bullets else \"none\"}')"
    Expected Result: ■ 마커 없음, 이미지 15+개, 빌트인 ID 30-34 미사용, 불릿 스타일 ID 확인
    Evidence: .sisyphus/evidence/task-8-problems-check.txt
  ```

  **Commit**: NO (테스트만, 코드 변경은 해당 스크립트 태스크에서)

- [ ] 9. 버전 및 레지스트리 업데이트

  **What to do**:
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` — version을 3.0.0으로 업데이트
  - `.claude-plugin/marketplace.json` — hwpx-generator 항목 version 업데이트, metadata.version 업데이트
  - `AGENTS.md` — Version 업데이트, WHERE TO LOOK에 새 스크립트 추가, COMMANDS에 새 명령 추가, Generated 날짜 업데이트
  - `README.md` — hwpx-generator 설명 업데이트 (이미지 임베딩, 마크다운 채우기 기능 추가), Version 업데이트, 변경 이력 추가
  - 버전 결정: 새 기능(이미지 임베딩) + 새 워크플로우 + 새 스크립트 3개 = MINOR (plugin 3.0.0), marketplace MINOR 업데이트

  **Must NOT do**:
  - 다른 플러그인의 버전 변경 금지
  - 기존 AGENTS.md/README.md의 다른 플러그인 섹션 변경 금지

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 정형화된 버전/레지스트리 업데이트
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after T8)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 8

  **References**:

  **Pattern References**:
  - `plugins/hwpx-generator/.claude-plugin/plugin.json` — 현재 버전 확인
  - `.claude-plugin/marketplace.json` — hwpx-generator 항목 위치
  - `AGENTS.md` — WHERE TO LOOK, COMMANDS 섹션
  - `README.md` — hwpx-generator 섹션, 변경 이력

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 버전 동기화 확인
    Tool: Bash
    Steps:
      1. python3 -c "import json; d=json.load(open('plugins/hwpx-generator/.claude-plugin/plugin.json')); print(d['version'])"
      2. grep 'hwpx-generator' .claude-plugin/marketplace.json | head -5
      3. grep 'Version' AGENTS.md | head -1
      4. grep 'Version' README.md | head -1
    Expected Result: 모든 버전이 동기화됨
    Evidence: .sisyphus/evidence/task-9-version-check.txt
  ```

  **Commit**: YES
  - Message: `chore(hwpx): bump hwpx-generator to v3.0.0, update registry`
  - Files: `plugin.json`, `marketplace.json`, `AGENTS.md`, `README.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`

  **What to do**: Read the plan end-to-end. Verify every "Must Have" and "Must NOT Have".

  **QA Scenarios:**
  ```
  Scenario: Must Have 검증
    Tool: Bash (workdir: project root)
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py
      2. grep 'Workflow 7' plugins/hwpx-generator/skills/hwpx-core/SKILL.md
      3. grep 'image_embedder' plugins/hwpx-generator/agents/hwpx-builder.md
      4. grep 'content_md' plugins/hwpx-generator/commands/hwpx-generate.md
      5. ls .sisyphus/evidence/task-*.* 2>/dev/null | wc -l
    Expected Result: 모든 스크립트 존재, 키워드 매치, evidence 파일 1개 이상
    Evidence: .sisyphus/evidence/F1-compliance.txt (위 명령 출력을 리다이렉트)
  
  Scenario: Must NOT Have 검증
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 -c "import ast; [ast.parse(open(f).read()) for f in ['plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py','plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py','plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py']]; print('PASS: all scripts parse')"
      2. grep -rn 'import lxml\|from lxml\|import PIL\|from PIL\|import markdown\|from markdown' plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py || echo "PASS: no forbidden imports"
    Expected Result: 금지된 import 없음
    Evidence: .sisyphus/evidence/F1-forbidden.txt
  ```
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`

  **What to do**: 새 Python 스크립트 3개의 코드 품질, 에러 처리, XML 이스케이핑 검증.

  **QA Scenarios:**
  ```
  Scenario: 스크립트 품질 검증
    Tool: Bash (workdir: project root)
    Steps:
      1. python3 -m py_compile plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py && echo "PASS: md_parser compiles"
      2. python3 -m py_compile plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py && echo "PASS: xml_writer compiles"
      3. python3 -m py_compile plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py && echo "PASS: image_embedder compiles"
      4. grep -c 'def ' plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py
    Expected Result: 모든 스크립트 컴파일 성공, 각 스크립트에 함수 정의 존재
    Evidence: .sisyphus/evidence/F2-quality.txt
  ```
  Output: `Scripts [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`

  **What to do**: 클린 상태에서 전체 워크플로우 재실행, 결과 HWPX 검증.

  **QA Scenarios:**
  ```
  Scenario: 클린 E2E 재실행
    Tool: Bash (workdir: project root)
    Steps:
      1. Task 8 QA의 전체 12단계 명령을 클린 /tmp/ 에서 재실행
      2. python3 plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py /tmp/e2e_final.hwpx 2>&1 | tee .sisyphus/evidence/F3-validate.txt
      3. python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/e2e_final.hwpx'); imgs=[n for n in z.namelist() if 'BinData' in n]; print(f'{len(imgs)} images found')" | tee -a .sisyphus/evidence/F3-validate.txt
      4. cp /tmp/e2e_final.hwpx .sisyphus/evidence/final-qa/e2e_final.hwpx
    Expected Result: validate.py PASS, 이미지 15개 포함
    Evidence: .sisyphus/evidence/F3-validate.txt, .sisyphus/evidence/final-qa/e2e_final.hwpx
  ```
  Output: `Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`

  **What to do**: 각 태스크의 "What to do" vs 실제 구현 1:1 대응 확인, 범위 초과 변경 탐지.

  **QA Scenarios:**
  ```
  Scenario: 범위 준수 검증
    Tool: Bash (workdir: project root)
    Steps:
      1. git diff --name-only HEAD~1 (또는 작업 시작 기준 커밋) | tee .sisyphus/evidence/F4-changed-files.txt
      2. 변경된 파일 목록이 플랜의 Deliverables 목록과 1:1 대응하는지 확인 (추가 파일 = 범위 초과)
      3. grep -rn 'charPrIDRef="30"\|charPrIDRef="31"\|charPrIDRef="32"\|charPrIDRef="33"\|charPrIDRef="34"' plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py || echo "PASS: no builtin IDs hardcoded"
    Expected Result: 변경 파일 = 플랜 Deliverables, 빌트인 ID 하드코딩 없음
    Evidence: .sisyphus/evidence/F4-changed-files.txt, .sisyphus/evidence/F4-scope.txt
  ```
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Task | Commit Message | Files |
|------|---------------|-------|
| T1 | `feat(hwpx): add md_parser.py for markdown→structured data` | scripts/md_parser.py |
| T2 | `feat(hwpx): add xml_writer.py for structured data→HWPX XML` | scripts/xml_writer.py |
| T3 | `feat(hwpx): add image_embedder.py for HWPX image embedding` | scripts/image_embedder.py |
| T4 | `enhance(hwpx): add detailed style annotation to analyze_template.py` | scripts/analyze_template.py |
| T5-T7 | `docs(hwpx): add Workflow 7 and update agent guides for template filling` | SKILL.md, hwpx-builder.md, hwpx-generate.md |
| T8 | `test(hwpx): verify end-to-end template filling with dev/ test case` | — |
| T9 | `chore(hwpx): bump version to 3.0.0, update registry` | plugin.json, marketplace.json, AGENTS.md, README.md |

---

## Success Criteria

### Verification Commands
```bash
SCRIPTS=plugins/hwpx-generator/skills/hwpx-core/scripts

# MD 파싱 테스트
python3 $SCRIPTS/md_parser.py dev/3_비전_및_목표_v2.md --output /tmp/parsed.json
# Expected: JSON with heading/bullet/table/image_ref blocks

# XML 생성 테스트
python3 $SCRIPTS/xml_writer.py --input /tmp/parsed.json --style-config /tmp/styles.json --output /tmp/section_fragment.xml
# Expected: Valid HWPX XML fragment with proper paraPrIDRef/charPrIDRef

# 이미지 임베딩 테스트
python3 $SCRIPTS/image_embedder.py --hwpx result.hwpx --images-dir dev/images/ --mapping /tmp/caption_map.json --output result_with_images.hwpx
# Expected: HWPX with BinData/ entries, updated content.hpf

# 구조 검증
python3 $SCRIPTS/validate.py result_with_images.hwpx
# Expected: PASS
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] validate.py PASS
- [ ] 한글 오피스에서 정상 열림 (or structural validation pass)
- [ ] 15개 이미지 BinData/ 내 존재 확인
