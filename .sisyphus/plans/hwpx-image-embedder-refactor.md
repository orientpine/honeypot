# HWPX Image Embedder 매뉴얼 기반 리팩토링

## TL;DR

> **Quick Summary**: `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md` (역공학 검증된 사양)을 기준으로 `image_embedder.py`의 좌표계, 요소 순서, header.xml 처리를 전면 교체하고, `validate.py` 검증 로직과 테스트를 동기화한다.
> 
> **Deliverables**:
> - `image_embedder.py` — 매뉴얼 기반 좌표계(pixel×36/pixel×75), 요소 순서, binDataList 제거, 동적 BODY_WIDTH
> - `validate.py` — binDataList 검사 역전, content.hpf 기반 참조 검증
> - `test_image_embedder.py` — 새 좌표계 assertion으로 업데이트
> - `SKILL.md` — 규칙/문서 동기화
> - 버전 업데이트 (plugin.json, marketplace.json, AGENTS.md, README.md)
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 7 → Task 8 → F1-F4

---

## Context

### Original Request
사용자가 `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md` (역공학 기반 검증된 사양)을 기준으로 `plugins/hwpx-generator/`의 이미지 임베딩 시스템을 개선 요청.

### Interview Summary
**Key Discussions**:
- header.xml binDataList: 매뉴얼 방식 전면 적용 (추가 금지, 기존 것도 제거)
- 치수 좌표계: orgSz=pixel×36(200DPI), imgDim=pixel×75(96DPI)로 전환
- BODY_WIDTH: 템플릿 pageSz-margins 동적 추출 (fallback: 42520)

**Research Findings**:
- 매뉴얼은 `(양식) '27년도 전략연구사업 제안서_작성.hwpx`에서 역공학 검증됨
- 현재 코드는 v3.4.0~v3.5.0에서 7대 결함 수정 이력 있음 — 좌표계 혼동이 근본 원인
- 테스트 fixture `create_input_hwpx()`는 header.xml 미포함 — header.xml 경로 미검증
- DPI 변환 계수(×36, ×75)는 HWPUNIT 표준 (1 HWPUNIT = 1/7200 inch)이므로 템플릿 무관

### Metis Review
**Identified Gaps** (addressed):
- validate.py check #5 (binaryItemIDRef→binItem 교차 참조) — binDataList 제거 시 orphan됨 → content.hpf 기반으로 재작성
- 테스트 fixture에 header.xml 미포함 → 새 fixture 함수 추가
- 동적 BODY_WIDTH 추출 실패 시 fallback 필요 → A4 기본값 fallback
- 기존 binDataList가 있는 템플릿 처리 → 매뉴얼 step 6에 따라 제거
- image_embedder.py 상단 중복 import (lines 9-24) → 정리

---

## Work Objectives

### Core Objective
`image_embedder.py`를 역공학 검증된 매뉴얼 사양에 맞춰 전면 리팩토링하여 한/글에서 이미지가 정확히 렌더링되도록 한다.

### Concrete Deliverables
- `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` (리팩토링)
- `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py` (검증 로직 수정)
- `plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py` (assertion 업데이트)
- `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` (규칙/문서 동기화)
- `plugins/hwpx-generator/.claude-plugin/plugin.json` (버전)
- `.claude-plugin/marketplace.json` (버전)
- `AGENTS.md` (버전, 변경이력)
- `README.md` (버전, 변경이력)

### Definition of Done
- [ ] `pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -v` → ALL PASS
- [ ] `python validate.py output.hwpx` → exit 0 (binDataList 없는 파일)
- [ ] make_pic_xml() 출력의 요소 순서가 매뉴얼 section 5와 일치
- [ ] orgSz = pixel×36, imgDim = pixel×75, imgRect = orgSz 좌표, imgClip = imgDim 좌표
- [ ] header.xml에 binDataList 추가 없음 (기존 것도 strip)
- [ ] binaryItemIDRef가 content.hpf의 opf:item id와 일치

### Must Have
- 매뉴얼 section 5의 16개 요소 순서 엄수
- orgSz=pixel×36, imgDim=pixel×75 좌표계
- header.xml binDataList 추가 금지 + 기존 것 strip
- binaryItemIDRef = content.hpf id (imageN 형식)
- 동적 BODY_WIDTH 추출 (fallback 42520)
- numberingType="PICTURE", paraPrIDRef="4", charPrIDRef="1"
- rotationInfo centerX/Y = curSz/2
- hc:img → imgRect 순서 (position 7 → 8)
- shapeComment에 파일명/픽셀 정보 포함

### Must NOT Have (Guardrails)
- zip_surgery.py, md_parser.py, xml_writer.py, page_guard.py, proofread.py 수정
- `<!--IMAGE:imageN-->` 플레이스홀더 패턴 변경
- 매핑 시스템 리팩토링 (load_mapping, auto_map_images, build_mapping)
- CLI 인수 파싱 변경 (parse_args)
- PIL 이미지 처리 변경 (ensure_png_format, maybe_resize_image)
- conftest.py 변경
- 새 이미지 포맷 추가
- EXIF DPI 감지 기능 추가
- ID 생성 체계 변경

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, test_image_embedder.py 536줄)
- **Automated tests**: Tests-after (기존 테스트 업데이트)
- **Framework**: pytest

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Scripts**: Use Bash — Run pytest, run validate.py, check exit codes
- **Structure**: Use grep/ast_grep — Verify element ordering, attribute values

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Sequential — same file, single owner):
└── Task 1: image_embedder.py 전면 리팩토링 [deep]
            (make_pic_xml + 좌표계 전환 + binDataList 제거 + BODY_WIDTH 동적 추출 + 코드 정리)

Wave 2 (After Wave 1 — parallel, 각 파일 독립):
├── Task 2: test_image_embedder.py assertion 업데이트 + 신규 테스트 추가 [unspecified-high]
├── Task 3: validate.py 이미지 검사 로직 수정 [unspecified-high]
├── Task 4: SKILL.md 이미지 임베딩 규칙/문서 동기화 [quick]
└── Task 5: hwpx-generate.md 커맨드 문서 업데이트 [quick]

Wave 3 (After Wave 2 — registry + docs):
└── Task 6: 버전 업데이트 (plugin.json, marketplace.json, AGENTS.md, README.md) [quick]

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
| 1 | — | 2, 3, 4, 5 | 1 |
| 2 | 1 | 6, F1-F4 | 2 |
| 3 | 1 | 6, F1-F4 | 2 |
| 4 | 1 | 6 | 2 |
| 5 | 1 | 6 | 2 |
| 6 | 2, 3, 4, 5 | F1-F4 | 3 |
| F1-F4 | ALL | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **1** — T1 → `deep` (sequential, single file owner)
- **Wave 2**: **4** — T2 → `unspecified-high`, T3 → `unspecified-high`, T4 → `quick`, T5 → `quick`
- **Wave 3**: **1** — T6 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`
- [x] 1. image_embedder.py — 매뉴얼 기반 전면 리팩토링 (make_pic_xml + 좌표계 + binDataList + BODY_WIDTH)

  **What to do**:
  - **A. make_pic_xml() 전면 재작성** (line 322-394):
    - 요소 순서 16개 엄수 (매뉴얼 section 5): offset→orgSz→curSz→flip→rotationInfo→renderingInfo→**hc:img**→imgRect→imgClip→inMargin→imgDim→effects→sz→pos→outMargin→shapeComment
    - 속성: numberingType="PICTURE", paraPrIDRef="4", charPrIDRef="1", allowOverlap="0", zOrder 추가, centerX/Y=curSz/2
    - imgRect: curSz→orgSz 좌표. imgClip: orgSz→imgDim 좌표
    - shapeComment: 파일명/픽셀 정보 포함
    - 함수 시그니처에 filename, z_order, dim_width, dim_height 추가
  - **B. embed_images() 좌표계 전환** (line 584-733):
    - org_width = pixel_w * 36 (was *100), org_height = pixel_h * 36
    - dim_w = pixel_w * 75, dim_h = pixel_h * 75 (was raw pixel)
    - make_pic_xml() 호출부에 새 파라미터 전달
  - **C. binDataList 제거**:
    - update_header_xml() 호출 제거 (line 694-695) + 함수 본체 제거
    - header.xml에 기존 binDataList가 있으면 strip (매뉴얼 section 8, step 6)
    - binaryItemIDRef: BIN0001→imageN 형식, content.hpf id와 일치
    - bin_entries 로직 제거, bin_id = key ("image1", "image2", ...)
  - **D. BODY_WIDTH 동적 추출**:
    - extract_body_width(section_xml) 신규 함수: pageSz width - pageMargin left - right
    - 실패 시 A4_BODY_WIDTH=42520 fallback
    - embed_images()에서 동적 호출, calc_hwpx_height에 전달
  - **E. 코드 정리**: 중복 import 제거 (lines 9-24)

  **Must NOT do**:
  - `<hp:p><hp:run><hp:pic>` 래퍼 구조 변경 (v3.5.0 critical fix)
  - 매핑 시스템 (load_mapping, auto_map_images, build_mapping) 변경
  - parse_args() CLI 인수 변경
  - maybe_resize_image() / ensure_png_format() PIL 로직 변경
  - zip_surgery.py, xml_writer.py 등 다른 스크립트 수정
  - lxml/ElementTree 사용 (문자열/정규식 기반만)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 단일 파일에서 4개 영역(make_pic_xml/좌표계/binDataList/BODY_WIDTH)을 동시에 정확히 변경. 16개 요소 순서 + 10개 이상 속성값 + 좌표계 변환이 모두 정확해야 한/글 렌더링에 직결.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 1, single owner)
  - **Blocks**: Tasks 2, 3, 4, 5
  - **Blocked By**: None

  **References** (NOTE: `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md` 파일은 로컬에 존재함 — 21KB, 597줄, 2026-03-22 생성. git에 커밋되지 않았을 수 있으나 디스크에서 읽기 가능):
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:68-126` — hp:pic XML 전체 구조 (section 3)
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:189-211` — 원소 순서 16개 (section 5, CRITICAL)
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:131-185` — 치수 계산 공식 (section 4)
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:260-486` — 완전한 Python 스크립트 (section 8)
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:437-446` — binDataList 제거 코드 (step 6)
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:322-394` — 현재 make_pic_xml()
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:584-733` — 현재 embed_images()
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py:419-462` — update_header_xml() (제거 대상)

  **QA Scenarios:**
  ```
  Scenario: make_pic_xml 요소 순서 + 좌표계 검증 (640×480px)
    Tool: Bash (python -c)
    Steps:
      1. make_pic_xml() 호출 → XML 문자열 생성
      2. 요소 순서: hc:img.index < hp:imgRect.index 확인
      3. orgSz width="23040" height="17280" (640×36, 480×36)
      4. imgDim dimwidth="48000" dimheight="36000" (640×75, 480×75)
      5. imgRect pt1 x="23040" (orgSz 좌표), imgClip right="48000" (imgDim 좌표)
      6. numberingType="PICTURE", paraPrIDRef="4", charPrIDRef="1"
    Evidence: .sisyphus/evidence/task-1-element-order.txt

  Scenario: binDataList 없음 + binaryItemIDRef=imageN 확인
    Tool: Bash (python + zipfile)
    Steps:
      1. header.xml 포함 HWPX로 임베딩 실행
      2. 출력 header.xml에 "<hh:binDataList" 없음 확인
      3. content.hpf에 id="image1", section0.xml에 binaryItemIDRef="image1" 일치 확인
    Evidence: .sisyphus/evidence/task-1-no-bindatalist.txt

  Scenario: 동적 BODY_WIDTH 추출 (48190) + fallback (42520)
    Tool: Bash (python -c)
    Steps:
      1. pageSz=59528, margin left=5669, right=5669 → extract_body_width() == 48190
      2. pageSz 없는 XML → extract_body_width() == 42520 (fallback)
    Evidence: .sisyphus/evidence/task-1-bodywidth.txt
  ```

  **Commit**: YES
  - Message: `refactor(hwpx-generator): rewrite image embedder to match reverse-engineered manual`
  - Files: `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py`
  - Pre-commit: 이 커밋은 테스트 업데이트(Task 2)와 함께 실행해야 pytest가 통과함. Task 2 완료 후 함께 커밋.

---

- [x] 2. test_image_embedder.py — 새 좌표계 assertion 업데이트 + 신규 테스트

  **What to do**:
  - **기존 테스트 assertion 업데이트**:
    - test_orgSz_uses_pixel_dimensions: pixel×100 → pixel×36 (640×480 → 23040×17280)
    - test_imgDim_has_pixel_values: raw pixel → pixel×75 (640×480 → 48000×36000)
    - test_scaMatrix_reflects_scaling_ratio: orgSz 변경에 따른 비율 조정
    - test_auto_resize_max_height/normal: BODY_WIDTH 참조값 확인
  - **신규 테스트 추가**:
    - test_no_binDataList_in_output: header.xml에 binDataList 없음
    - test_binaryItemIDRef_matches_content_hpf: imageN 형식 일치
    - test_element_order_hc_img_before_imgRect: hc:img < imgRect 순서
    - test_numberingType_is_PICTURE: numberingType="PICTURE"
    - test_shapeComment_has_info: shapeComment에 파일명/픽셀 포함
    - create_input_hwpx_with_header(): header.xml 포함 fixture

  **Must NOT do**:
  - conftest.py 수정
  - 테스트 인프라(load_image_embedder_module, write_minimal_png) 변경

  **Recommended Agent Profile**: `unspecified-high` | **Skills**: []
  **Parallelization**: Wave 2 (parallel with Tasks 3, 4, 5) | **Blocked By**: Task 1

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py:207-251` — test_orgSz (수정 대상)
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py:299-337` — test_imgDim (수정 대상)
  - `plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py:40-46` — create_input_hwpx (패턴 참조)

  **QA Scenarios:**
  ```
  Scenario: 전체 테스트 스위트 통과
    Tool: Bash (pytest)
    Steps: pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -v → ALL PASS
    Evidence: .sisyphus/evidence/task-2-pytest-all-pass.txt
  ```

  **Commit**: YES (Task 1과 함께 커밋)
  - Message: `refactor(hwpx-generator): rewrite image embedder to match reverse-engineered manual`
  - Files: `image_embedder.py, test_image_embedder.py`
  - Pre-commit: `pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -v`

---

- [x] 3. validate.py — 이미지 검사 로직 매뉴얼 기반 수정

  **What to do**:
  - check #4 (lines 164-186): binDataList 없으면 에러 → 있으면 WARNING
  - check #5 (lines 188-205): binaryItemIDRef→binItem → binaryItemIDRef→content.hpf opf:item id
  - check #1, #2, #3, #6 유지 (instid, renderingInfo, hp:run 래퍼, magic bytes)

  **Must NOT do**: _strict_checks(), _run_proofread() 수정, lxml import 변경

  **Recommended Agent Profile**: `unspecified-high` | **Skills**: []
  **Parallelization**: Wave 2 (parallel with Tasks 2, 4, 5) | **Blocked By**: Task 1

  **References**:
  - `plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py:117-244` — _image_checks()
  - `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md:490-506` — 디버깅 체크리스트 (section 9)

  **QA Scenarios:**
  ```
  Scenario: binDataList 없는 HWPX로 validate.py 통과
    Tool: Bash (python validate.py output.hwpx) → exit 0
    Evidence: .sisyphus/evidence/task-3-validate-pass.txt

  Scenario: binaryItemIDRef→content.hpf 교차참조 검증
    Tool: Bash (python)
    Preconditions: Task 1 출력의 output.hwpx (image1 이미지 임베딩된 상태)
    Steps:
      1. 정상 케이스: output.hwpx를 validate.py로 실행
         python plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py output.hwpx
         → exit code 0, "[image]" 에러 없음
      2. 누락 케이스: output.hwpx를 복사하여 broken.hwpx 생성.
         broken.hwpx의 content.hpf에서 id="image1" 항목을 제거하는 완전한 Python 코드:
         python -c "
         import zipfile, shutil, re, os;
         shutil.copy('output.hwpx', 'broken.hwpx');
         zin = zipfile.ZipFile('broken.hwpx', 'r');
         infos = zin.infolist(); entries = {i.filename: zin.read(i.filename) for i in infos}; zin.close();
         hpf = entries['Contents/content.hpf'].decode('utf-8');
         hpf = re.sub(r'<opf:item[^>]*id=.image1.[^>]*/>', '', hpf);
         entries['Contents/content.hpf'] = hpf.encode('utf-8');
         zout = zipfile.ZipFile('broken.hwpx', 'w');
         [zout.writestr(zipfile.ZipInfo(i.filename, compress_type=i.compress_type), entries[i.filename]) for i in infos];
         zout.close();
         print('broken.hwpx created with image1 removed from content.hpf')
         "
      3. broken.hwpx를 validate.py로 실행
         python plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py broken.hwpx
         → exit code 1, stderr에 '[image] binaryItemIDRef="image1" not found in content.hpf' 포함
    Expected Result: 정상=PASS(exit 0), 누락=FAIL(exit 1, 에러 메시지에 image1 언급)
    Failure Indicators: 정상 케이스에서 exit 1, 또는 누락 케이스에서 exit 0 (검증 실패)
    Evidence: .sisyphus/evidence/task-3-crossref.txt
  ```

  **Commit**: YES
  - Message: `refactor(hwpx-generator): update validate.py image checks for new embedding rules`
  - Pre-commit: `pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -v`

---

- [x] 4. SKILL.md — 이미지 임베딩 규칙/문서 동기화

  **What to do**:
  - Rule #24: "3곳 동시 등록" → "2곳 등록 (BinData/ + content.hpf). header.xml binDataList 추가 금지"
  - Rule #26: make_pic_xml() 설명에 새 요소 순서 반영
  - "이미지 임베딩 필수 규칙" 표 (line 799-809): 3곳→2곳, BIN ID→imageN, orgSz pixel×36, imgDim pixel×75
  - "hp:pic 검증된 구조" XML 예시 (line 811-858): hc:img 위치, orgSz/imgDim 값, numberingType="PICTURE"
  - "header.xml binDataList" 섹션 (line 860-870) → "사용하지 않음" 명시
  - "이미지 임베딩 가이드" (line 776-797): 4단계→3단계

  **Must NOT do**: 이미지 임베딩 외 섹션 수정, Workflow 1-6 수정

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 2 (parallel with Tasks 2, 3, 5) | **Blocked By**: Task 1

  **QA Scenarios:**
  ```
  Scenario: SKILL.md 내용 정합성
    Tool: Bash (grep)
    Steps: grep "3곳 동시 등록" SKILL.md → 0, grep "2곳 등록" → 1+, grep 'numberingType="PICTURE"' → 1+
    Evidence: .sisyphus/evidence/task-4-skill-md.txt
  ```

  **Commit**: YES (Task 5와 함께)
  - Message: `docs(hwpx-generator): update SKILL.md and command docs for new image embedding`

---

- [x] 5. hwpx-generate.md — 커맨드 문서 업데이트 (no-op — 교체 대상 없음)

  **What to do**:
  - 현재 파일(144줄)에서 이미지 임베딩 관련 텍스트 확인 후 수정:
    - 구체적 검색 대상: `grep -n "header.xml\|binDataList\|3곳" hwpx-generate.md`
    - 발견 시: "3곳 등록" → "2곳 등록" 교체, "header.xml 등록" 참조 제거
    - 이미지 관련 텍스트가 없으면: 이 Task는 no-op (skip)

  **Must NOT do**: Phase 구조 변경, 비이미지 섹션 수정

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 2 (parallel with Tasks 2, 3, 4) | **Blocked By**: Task 1

  **QA Scenarios:**
  ```
  Scenario: hwpx-generate.md 구 규칙 부재 확인
    Tool: Bash (grep)
    Steps:
      1. grep -c "binDataList" hwpx-generate.md → 0 (없어야 함) 또는 새 규칙으로 교체됨
      2. grep -c "3곳 등록" hwpx-generate.md → 0
      3. 발견 없으면 no-op으로 Task 완료 처리
    Expected Result: 구 규칙 부재 또는 no-op
    Evidence: .sisyphus/evidence/task-5-command-doc.txt
  ```

  **Commit**: YES (Task 4와 함께)
  - Message: `docs(hwpx-generator): update SKILL.md and command docs for new image embedding`

---

- [x] 6. 버전 업데이트 — plugin.json, marketplace.json, AGENTS.md, README.md

  **What to do**:
  - plugin.json: 3.7.0 → 3.8.0
  - marketplace.json: hwpx-generator 3.8.0, metadata.version 3.17.0
  - AGENTS.md: Version 3.17.0, Generated 날짜 업데이트
  - README.md: Version 3.17.0, 변경이력 추가:
    `3.17.0 | YYYY-MM-DD | hwpx-generator v3.8.0: 이미지 임베딩 매뉴얼 기반 리팩토링 — 좌표계 전환(orgSz=pixel×36, imgDim=pixel×75), binDataList 제거, hc:img 요소 순서, 동적 BODY_WIDTH, validate.py 동기화`

  **Must NOT do**: 다른 플러그인 버전 변경, 변경이력 외 README 수정

  **Recommended Agent Profile**: `quick` | **Skills**: []
  **Parallelization**: Wave 3 (after Tasks 2-5) | **Blocked By**: Tasks 2, 3, 4, 5

  **QA Scenarios:**
  ```
  Scenario: 4곳 버전 동기화
    Tool: Bash (grep)
    Steps: grep '3.8.0' plugin.json → 1, grep '3.17.0' marketplace.json/AGENTS.md/README.md → 각 1+
    Evidence: .sisyphus/evidence/task-6-versions.txt
  ```

  **Commit**: YES
  - Message: `chore: bump hwpx-generator to v3.8.0, marketplace to v3.17.0`

## TODOs

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle` — APPROVE (10/10, 4/4, 8/8, 9/9)
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high` — APPROVE (Tests 17/0, Files 3 clean)
  Run `pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v`. Review all changed files for: duplicate imports, empty catches, hardcoded values that should be constants, dead code (old update_header_xml if not removed). Check AI slop: excessive comments, over-abstraction.
  Output: `Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` — APPROVE (14/14 scenarios)
  Start from clean state. Create test HWPX with image placeholder. Run image_embedder.py. Verify output ZIP contains: no binDataList in header.xml, correct orgSz/imgDim values, correct element order in hp:pic, valid content.hpf entries. Run validate.py on output.
  Output: `Scenarios [N/N pass] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep` — APPROVE (Tasks 6/6 compliant, Unaccounted CLEAN)
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|------------|
| 1 | `refactor(hwpx-generator): rewrite image embedder to match reverse-engineered manual` | image_embedder.py, test_image_embedder.py | pytest test_image_embedder.py |
| 2 | `refactor(hwpx-generator): update validate.py image checks for new embedding rules` | validate.py | pytest test_image_embedder.py |
| 3 | `docs(hwpx-generator): update SKILL.md and command docs for new image embedding` | SKILL.md, hwpx-generate.md | — |
| 4 | `chore: bump hwpx-generator to v3.8.0, marketplace to v3.17.0` | plugin.json, marketplace.json, AGENTS.md, README.md | — |

---

## Success Criteria

### Verification Commands
```bash
# 전체 테스트
pytest plugins/hwpx-generator/skills/hwpx-core/tests/test_image_embedder.py -v
# Expected: ALL PASS

# 검증
python plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py output.hwpx
# Expected: VALID

# 요소 순서 확인 (hc:img before imgRect)
# grep output should show hc:img appearing before hp:imgRect
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] validate.py passes on new output
- [ ] Versions synced across all files
