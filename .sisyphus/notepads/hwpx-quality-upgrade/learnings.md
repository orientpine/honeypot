# Learnings — hwpx-quality-upgrade

## Project Structure
- Scripts dir: `plugins/hwpx-generator/skills/hwpx-core/scripts/`
- fix_namespaces.py: `plugins/hwpx-generator/skills/hwpx-templates/scripts/`
- Dev data: `dev/` (작성.hwpx, 초안.hwpx, 3장.md, 4장.md, images/ 15 PNG)

## Key Constraints (from plan)
- stdlib-only for: zip_surgery, xml_writer, md_parser, image_embedder, fix_namespaces
- NO lxml in stdlib-only scripts
- NO ElementTree (ET) — string-based XML only
- analyze_template.py CAN use lxml (already does)
- proofread.py: string-based XML, read-only
- NO python-hwpx for writing
- NO cell_writer.py after ZIP surgery

## Windows-specific
- Use full Windows paths in scripts
- No `export VAR=value` syntax — Windows cmd only
- dev/ filenames contain Korean and spaces: `(양식) '27년도 전략연구사업 제안서_작성.hwpx`

## Evidence Paths
- `.sisyphus/evidence/task-{N}-*.{json|txt|xml}`

## [2026-03-18] Task 1: Golden Reference Analysis
- `analyze_template.py --style-map` 기본 출력에는 `image_caption`, `bullet_auto`가 없으므로, section0/header XML 역분석으로 후처리 보강이 필요함.
- 골든 `작성.hwpx`의 실제 `hp:pic`는 3개이며, 캡션 스타일의 대표값은 `paraPrIDRef=118`, `charPrIDRef=121`로 수렴함.
- `heading type=BULLET` paraPr ID는 문서별로 다르며(초안/작성 차이), 자동 불릿 대상 ID는 header.xml에서 직접 추출해야 정확함.
- 골든 문서에서 이중 불릿(자동 불릿 + 텍스트 선행 불릿 문자) 케이스는 0건으로 확인됨.
- `dev/images`는 PNG 15개가 맞지만 02~14 파일명은 계획의 기대명과 실제명이 다르므로 매핑 테이블이 필요함.
