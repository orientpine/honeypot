# Draft: HWPX Generator Plugin 버그 수정 및 개선

## Requirements (confirmed)
- 표를 올바르게 그리지 못함 → 수정5 레퍼런스 수준 이상의 표 품질 필요
- 표를 그린 후 파란색으로 색칠함 → 흰색(무채색/무배경)으로 변경
- 내용을 채운 후 bold 처리함 → plain text로 유지, bold 금지
- 이미지를 올바르게 삽입하지 못함 → 이미지 크기 압축 후 동일 위치에 삽입
- 양식의 문단 구조를 그대로 유지 → parent 보존, child 추가만 허용
- 레퍼런스 파일: 제안서_최종_수정5.hwpx (사용자가 수동 수정한 최소 품질 기준)

## Technical Decisions
- 사용 워크플로우: Workflow 7 (마크다운 → HWPX 템플릿 채우기 + 이미지 임베딩)
- 문서 유형: 제안서 (proposal)
- 수정 대상: Python 스크립트 + 에이전트 지침 (hwpx-builder.md, SKILL.md)

## Research Findings (Current Session — Deep Analysis)

### Bug 1: 표 파란색 문제 — Root Cause Confirmed
- **analyze_template.py lines 780-806**: `extract_style_map()`이 template의 가장 많은 table cell의 borderFillIDRef를 선택
- 템플릿에 파란색 셀이 있으면 → 모든 생성 표에 파란색 적용
- **xml_writer.py line 322**: `borderFillIDRef="{style["borderFillIDRef"]}"` — 스타일 설정을 그대로 사용
- **수정 방향**: analyze_template.py에서 faceColor가 있는 borderFill 제외 → 흰색/무배경만 선택

### Bug 2: 본문 Bold 처리 문제 — Root Cause Confirmed
- **analyze_template.py lines 655-665**: body 스타일 선택 시 blue charPr(id=5) 필터는 있지만 bold charPr 필터 없음
- 템플릿의 가장 빈번한 body charPr가 bold면 → 모든 생성 본문이 bold
- **xml_writer.py line 234**: `default_char_pr_id=str(body["charPrIDRef"])` — body 스타일 그대로 사용
- **수정 방향**: body 후보에서 charpr_map의 bold=True인 ID 제외

### Bug 3: 이미지 삽입 실패 — Pipeline 문제
- xml_writer.py line 576: `build_image_placeholder()` → `<!--IMAGE:imageN-->` 플레이스홀더 정상 생성
- image_embedder.py: 플레이스홀더 찾아서 `<hp:pic>` XML로 교체하는 로직 존재
- **문제 원인 후보**:
  1. `--from-parsed` 모드에서 base_dir이 잘못 설정 (CWD vs 마크다운 파일 디렉토리)
  2. extract_image_number()가 파일명에서 숫자 추출 실패
  3. 이미지 경로가 상대경로이고 base_dir이 안 맞으면 silent skip
  4. 이미지 압축/리사이징 로직 부재 — 대용량 이미지 시 MAX_HEIGHT 초과 에러
- **수정 방향**: path resolution 개선, 이미지 자동 압축, 에러 메시지 개선

### Bug 4: 양식 문단 구조 미보존 — Architectural Issue
- 현재 Workflow 7 흐름: md_parser → xml_writer(새 section 생성) → zip_surgery(전체 교체)
- **문제**: xml_writer가 완전히 새로운 section XML을 생성하여 zip_surgery가 템플릿 전체를 교체
- HwpxSurgeon은 extract_children() → modify → replace_children() 지원하지만 현재 미사용
- hwpx-builder.md에 Template-Aware Markdown Insertion (lines 128-205) 지침 존재하지만 스크립트 미구현
- **수정 방향**: zip_surgery의 replace 대신 insert 방식으로 전환. 템플릿 children 추출 → 삽입점 식별 → 내용 삽입 → children 교체

### 코드 위치 요약
| 파일 | 핵심 함수/라인 | 관련 버그 |
|------|---------------|----------|
| analyze_template.py:655-665 | body style 선택 (blue 필터만) | Bug 2 |
| analyze_template.py:730-750 | bold style 선택 | Bug 2 |
| analyze_template.py:780-806 | table_cell borderFillIDRef 선택 | Bug 1 |
| xml_writer.py:322 | tc borderFillIDRef 적용 | Bug 1 |
| xml_writer.py:325-326 | cellSz height, cellMargin (하드코딩) | Bug 1 |
| xml_writer.py:392-394 | table sz height (하드코딩) | Bug 1 |
| xml_writer.py:576 | image placeholder 생성 | Bug 3 |
| image_embedder.py:134-173 | load_mapping_from_parsed (path 해석) | Bug 3 |
| image_embedder.py:547-551 | placeholder 검색 | Bug 3 |
| zip_surgery.py:446-449 | replace_children (전체 교체) | Bug 4 |

## Open Questions (Resolved)
- 수정5의 정확한 표 구조/색상/스타일 → 분석 에이전트 진행 중 (bg_d046d9d6)
- 이미지 압축: PIL/Pillow resize → image_embedder.py에 --compress 옵션 추가
- 수정 범위: 전체 플러그인 (스크립트 + 에이전트 지침 + SKILL.md)

## Scope Boundaries
- INCLUDE: analyze_template.py, xml_writer.py, image_embedder.py 스크립트 수정
- INCLUDE: hwpx-builder.md 에이전트 지침 수정
- INCLUDE: SKILL.md 스킬 문서 수정
- INCLUDE: 표 구조/색상, 텍스트 스타일, 이미지 임베딩, 템플릿 구조 보존
- EXCLUDE: 새 워크플로우 추가 (기존 Workflow 7 개선만)
- EXCLUDE: 다른 플러그인 변경
- EXCLUDE: 기존 template XML 파일 변경
