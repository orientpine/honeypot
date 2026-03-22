# Issues — hwpx-quality-upgrade

## Known Issues (from plan research)
1. xml_writer.py outputs hwpx-fragment without hs:sec wrapper → cannot insert into section0.xml directly
2. md_parser.py only supports custom format, not `![alt](path)` → dev/ sample mismatch
3. Table colSpan/rowSpan not supported — equal split only
4. analyze_template.py style map uses frequency heuristics → wrong mapping on complex templates
5. image_embedder.py: PNG-only, no alignment control, no caption linking
6. No post-processing (proofreading) step

## Ongoing
(Updated as issues discovered)

## F3 Manual QA Findings (2026-03-19)

### CRITICAL: image_embedder <-> xml_writer integration gap
- **xml_writer** generates full `<hp:pic>` elements with `binaryItemIDRef="imageN"` refs
- **image_embedder** expects `<!--IMAGE:imageN-->` placeholder comments (PLACEHOLDER_RE)
- Result: `image_embedder --from-parsed` fails with "no <!--IMAGE:imageN--> placeholders found"
- **Workaround**: Manual ZIP embedding of BinData/ + content.hpf manifest update
- **Root cause**: Task 8 (xml_writer image+caption) generates hp:pic directly, Task 9 (image_embedder) wasn't updated to handle pre-generated hp:pic
- **Fix needed**: image_embedder should detect binaryItemIDRef refs as fallback when no placeholders found

### MEDIUM: fix_namespaces.py doesn't inject missing xmlns for xml_writer output
- xml_writer generates only 4 xmlns (hp, hc, hs, hh)
- Original HWPX section0.xml has 15 xmlns declarations
- fix_namespaces.py only renames nsN prefixes, doesn't add missing namespaces
- validate --strict fails: "Only 4 xmlns declarations on root tag (expected >=10)"
- **Workaround**: Manual namespace injection

### MEDIUM: fix_namespaces.py doesn't add XML declaration
- xml_writer output has no `<?xml ... ?>` declaration
- validate --strict expects `standalone='no'` (but original has 'yes' - possible validate bug)
- **Workaround**: Manual `<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>` prepend

### LOW: validate --strict standalone='no' check is false positive
- validate expects `standalone='no'` but ALL HWPX files (original template, golden reference) use `standalone="yes"`
- Both 초안.hwpx and 작성.hwpx fail this same strict check
- This is a validate.py bug, not a pipeline issue

### INFO: proofread font_consistency check overly sensitive
- Golden reference (작성.hwpx) fails font_consistency: score=0.7313, 29/80 groups failed
- Our generated output scores BETTER: 0.8773, 1/6 groups failed
- The metric's threshold is too strict for real HWPX documents with intentional mixed formatting

## Task 2 Follow-up (2026-03-22)
- `python -m pytest plugins/hwpx-generator/skills/hwpx-core/tests/ -v --ignore=...` 실행 시 `dev/3장.md`, `dev/4장.md` 파일 부재로 `test_md_parser_complex.py`, `test_md_parser_images.py`에서 `FileNotFoundError` 3건 발생.
- 이번 변경 범위(xml_writer/test_xml_writer_images)와 무관한 환경 데이터 이슈이며, `test_xml_writer_images.py` 대상 4개 테스트는 모두 PASS.
