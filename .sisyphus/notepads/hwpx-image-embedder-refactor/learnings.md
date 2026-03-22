# Learnings — hwpx-image-embedder-refactor

## [2026-03-22] Session ses_2ea8507bcffeWx5XC7Zbt0CHof

### Key Facts from Plan
- DPI 변환 계수: orgSz = pixel×36 (200DPI), imgDim = pixel×75 (96DPI)
- BODY_WIDTH: 동적 추출 (pageSz width - pageMargin left - right), fallback A4=42520
- binDataList: header.xml에 추가 금지, 기존 것도 제거 (매뉴얼 section 8, step 6)
- binaryItemIDRef: BIN0001→imageN 형식 (content.hpf id와 일치)
- 16개 요소 순서 (section 5): offset→orgSz→curSz→flip→rotationInfo→renderingInfo→hc:img→imgRect→imgClip→inMargin→imgDim→effects→sz→pos→outMargin→shapeComment
- numberingType="PICTURE", paraPrIDRef="4", charPrIDRef="1"
- rotationInfo centerX/Y = curSz/2
- imgRect는 orgSz 좌표, imgClip은 imgDim 좌표
- `<hp:p><hp:run><hp:pic>` 래퍼 구조는 절대 변경 금지 (v3.5.0 critical fix)
- 매뉴얼: `dev/HWPX_IMAGE_EMBEDDING_MANUAL.md` (로컬에 있음, 597줄)

### Forbidden (Must NOT Touch)
- zip_surgery.py, md_parser.py, xml_writer.py, page_guard.py, proofread.py
- `<!--IMAGE:imageN-->` 플레이스홀더 패턴
- load_mapping, auto_map_images, build_mapping (매핑 시스템)
- parse_args() CLI 인수
- PIL 로직 (ensure_png_format, maybe_resize_image)
- conftest.py
- lxml/ElementTree (문자열/정규식 기반만 사용)

## [2026-03-22] Task T1 execution notes

### Refactor outcomes
- `make_pic_xml()` 시그니처를 `filename`, `z_order`, `dim_width`, `dim_height` 포함으로 확장하고 16요소 순서를 매뉴얼 section 5와 동일하게 고정함.
- `hp:pic` 속성은 `numberingType="PICTURE"`, `zOrder`, `paraPrIDRef="4"`, `charPrIDRef="1"`, `allowOverlap="0"`로 전환.
- 좌표계 분리 적용: `orgSz = pixel×36`, `imgDim = pixel×75`, `imgRect=orgSz`, `imgClip=imgDim`.
- `rotationInfo centerX/Y`는 `curSz` 기준 절반값(`//2`)으로 계산.

### Header/binData policy
- `update_header_xml()`를 제거하고 `embed_images()`에서 header.xml의 기존 `<hh:binDataList ...>` / self-closing 패턴을 정규식으로 strip.
- `binaryItemIDRef`와 `content.hpf` `opf:item id`를 모두 `imageN` 키로 통일 (`BIN0001` 계열 제거).

### Body width extraction
- `extract_body_width(section_xml)` 신규 추가: `pageSz.width - pageMargin.left - pageMargin.right`, 실패 시 `A4_BODY_WIDTH=42520` fallback.
- `calc_hwpx_height()` 호출에 동적 `target_width=body_width`를 전달해 템플릿 본문 폭 연동.

### QA evidence
- `.sisyphus/evidence/task-1-element-order.txt`: 640x480 케이스에서 요소 순서/좌표계(23040x17280, 48000x36000) 검증.
- `.sisyphus/evidence/task-1-no-bindatalist.txt`: header.xml binDataList 제거 + `binaryItemIDRef="image1"` 검증.
- `.sisyphus/evidence/task-1-bodywidth.txt`: 추출값 48190 및 fallback 42520 검증.

## [2026-03-22] Task T2 execution notes

### Test assertion updates (3 tests)
- test_orgSz_uses_pixel_dimensions: pixel*100 -> pixel*36 (23040, 17280)
- test_scaMatrix_reflects_scaling_ratio: < 1.0 -> > 1.0 (upscale: orgSz=23040 < curSz=42520)
- test_imgDim_has_pixel_values: raw pixel -> pixel*75 (48000, 36000)

### New infrastructure added
- create_png fixture: returns Path after write_minimal_png
- embed fixture: wraps embed_images with auto_map=True for concise tests
- create_input_hwpx_with_header(): plain function (not fixture), creates HWPX with header.xml containing binDataList

### New tests (6)
- test_no_binDataList_in_output: header.xml binDataList stripping
- test_binaryItemIDRef_matches_content_hpf: imageN id consistency
- test_element_order_hc_img_before_imgRect: XML element ordering
- test_numberingType_is_PICTURE: hp:pic attribute
- test_shapeComment_has_info: filename + pixel dims in comment

### QA evidence
- .sisyphus/evidence/task-2-pytest-all-pass.txt: 17 passed in 0.49s, 0 failures

## [2026-03-22] Task T3 execution notes

### validate.py check #4 reversal
- binDataList absent = OK (no error). binDataList present = `[image][WARN]` deprecation message.
- Logic reversed: was "missing = error", now "present = warning".
- Aligns with manual section 8 step 6 and section 9 checklist item #4 ("binDataList가 없는가").

### validate.py check #5 rewrite (binaryItemIDRef cross-ref)
- Old: binaryItemIDRef → header.xml `hh:binItem BinData` refs
- New: binaryItemIDRef → content.hpf `opf:item id` refs
- Regex: `re.findall(r'<opf:item[^>]+\bid="([^"]+)"', hpf_text)`
- Aligns with manual section 9 checklist items #2 and #3.

### QA evidence
- `.sisyphus/evidence/task-3-validate-pass.txt`: valid HWPX (no binDataList, cross-ref OK) → exit 0
- `.sisyphus/evidence/task-3-crossref.txt`: 3 cases — valid exit=0, missing ref exit=1, deprecated binDataList exit=1
