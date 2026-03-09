---
name: theme-gov
description: "visual-generator gov 테마 무드 팔레트와 XML-tag 장면 가이드. Use when theme=gov."
---

# Gov Theme

정부/공공기관 발표 톤의 정돈된 인포그래픽 테마다.

## Mood Palette (9)

| mood | primary | secondary | accent | background |
|------|---------|-----------|--------|------------|
| technical-report | #1E3A5F | #4A90A4 | #E07B39 | #F5F7FA |
| growth | #1B4332 | #2D6A4F | #40916C | #F0F4F0 |
| clarity | #2C3E50 | #5D6D7E | #F39C12 | #FAFAFA |
| connection | #4A1A6B | #7B2CBF | #E040FB | #F8F5FA |
| innovation | #0B525B | #3A9D7A | #B4D6C1 | #F0FAF5 |
| tech-focus | #2C6AA0 | #415A77 | #3BC9DB | #F5F7FA |
| knowledge | #2E5090 | #5D6D7E | #E07B39 | #FAFAFA |
| presentation | #D35400 | #1E3A5F | #F39C12 | #F5F7FA |
| workshop | #117A65 | #1B4332 | #3A9D7A | #F0FAF5 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`에는 아래 요소를 자연어로 기술한다.
- 서피스: 직각 박스와 질서 있는 패널
- 배경: 밝은 중립 배경과 상단 배너 감성
- 코너: 선명한 직각 경계
- 연결선: 굵고 명확한 흐름 화살표
- 시각장식: 절제된 플랫 아이콘과 구조선
- 공간구성: 규칙적인 격자와 균등 분배
- 시각메타포: 신뢰, 제도, 실행 체계 강조

**품질 기준**: `scene-richness-spec.md` (최소 5문장, 7요소 중 5+ 포함, negative prompting 필수)

## Positive Scene Direction

- 기관 식별 요소 없이 공공 문서 톤만 유지한다
- 비교 장면이 필요한 경우 좌우 균형과 통합 하단 영역을 명시한다
- 메시지는 구조적 배치와 핵심 수치로 전달한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, Bold/ExtraBold weight Korean sans-serif)`
- 위계 비율: 제목 > 부제목 > 본문 > 보조수치
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- 번호/지표는 동일 계열 폰트로 통일한다
- **상세 기준**: `korean-typography-spec.md` (Heavy Gothic-style Hangul 필수, 자모분리 방지)

> ⚠️ **TYPOGRAPHY CRITICAL**: `<typography>` 태그에 구체적 폰트명 금지. Heavy-weight Gothic-style Korean sans-serif at 800+ weight 등 서술적 표현만 사용.

## XML-Tag 출력 매핑

- `<scene>`: 공공 발표 톤 장면 설명
- `<text_to_render>`: 최대 25항목, 키워드/수치 중심
- `<typography>`: 한글 가독성 힌트와 위계
- `<canvas>`: 3840x2160, 16:9, 무드 팔레트
- `<layout>`: 인용 텍스트 중심 배치 설명

**검증 규칙**: `validation-rules-map.md` (orphan/ghost 방지, 메타라벨 금지)

무드 톤 가이드:
- `technical-report`: 가장 공식적이고 차분한 톤
- `innovation`: 변화와 전환을 부드럽게 강조
- `clarity`: 설명 중심, 높은 판독성 유지

---

## Golden Reference Example

**Topic**: 디지털 전환 추진 현황
**Layout**: `grid_4`
**Mood**: `technical-report`

```xml
<scene>
A precisely ordered government infographic displayed on a bright neutral background with a navy banner strip across the top. Four equal-width rectangular panels sit in a strict horizontal grid, each outlined with sharp 2px borders in deep navy. Every panel carries a large Roman numeral header in the upper-left corner and a bold percentage or count figure at its centre, rendered in teal. Thin horizontal progress bars run beneath each figure, their filled portions coloured in warm orange against a light grey track. A slim summary strip spans the full width at the bottom, containing two lines of secondary statistics separated by vertical dividers. The overall composition conveys institutional reliability through geometric repetition and measured whitespace. No gradients, no 3D effects, no decorative illustrations—only flat colour fills, crisp edges, and typographic hierarchy.
</scene>

<text_to_render>
title: "디지털 전환 추진 현황"
subtitle: "2025년 상반기 주요 성과"
section_1: "I. 전자정부 혁신"
section_1_desc: "행정서비스 디지털화"
metric_1_label: "온라인 민원처리율"
metric_1_value: "94.7%"
metric_1_delta: "전년대비 +12.3%p"
section_2: "II. 데이터 기반 행정"
section_2_desc: "공공데이터 개방 확대"
metric_2_label: "개방 데이터셋"
metric_2_value: "48,520건"
metric_2_note: "활용건수 1,240만"
section_3: "III. 클라우드 전환"
section_3_desc: "정보시스템 클라우드 이전"
metric_3_label: "전환율"
metric_3_value: "67.2%"
metric_3_note: "목표 대비 89% 달성"
section_4: "IV. AI 행정 도입"
section_4_desc: "지능형 행정 서비스 확산"
metric_4_label: "도입 기관 수"
metric_4_value: "127개 기관"
metric_4_note: "챗봇 상담 320만건 처리"
footer_left: "디지털 역량강화 교육 이수 공무원 45,800명"
footer_right: "하반기 목표: 클라우드 전환율 80% · AI 도입 200개 기관"
</text_to_render>

<typography>
Heavy Gothic-style Korean sans-serif at ExtraBold (800+) for titles, Bold (700) for headers. Title at extra-large scale in #1E3A5F. Roman numeral headers at large bold scale. Metric figures at hero scale in #4A90A4. Sub-labels at medium weight scale. Bottom summary strip at small regular scale. Crisp anti-aliased Korean typography with professional typesetting. All numerals in the same Gothic family for visual unity.
</typography>

<canvas>
3840x2160 px, 16:9 aspect ratio. Primary #1E3A5F (deep navy), Secondary #4A90A4 (teal), Accent #E07B39 (warm orange), Background #F5F7FA (light grey-white). Navy banner strip across top 12% of canvas. Four panel grid occupies central 70% height. Bottom summary strip in last 10%.
</canvas>

<layout>
"디지털 전환 추진 현황" centred in the navy banner at top. "2025년 상반기 주요 성과" as subtitle directly below the banner, left-aligned.

Four equal columns spanning the central area, each 22% canvas width with 2.5% gutters:

Column 1 — "I. 전자정부 혁신" as header top-left inside the panel. "행정서비스 디지털화" as sub-header below. "온라인 민원처리율" as metric label centred. "94.7%" as the large centred figure. "전년대비 +12.3%p" as annotation below the figure. Orange progress bar at ~95% fill near panel bottom.

Column 2 — "II. 데이터 기반 행정" as header. "공공데이터 개방 확대" sub-header. "개방 데이터셋" label. "48,520건" large figure. "활용건수 1,240만" annotation below.

Column 3 — "III. 클라우드 전환" as header. "정보시스템 클라우드 이전" sub-header. "전환율" label. "67.2%" large figure. "목표 대비 89% 달성" annotation. Orange progress bar at ~67% fill.

Column 4 — "IV. AI 행정 도입" as header. "지능형 행정 서비스 확산" sub-header. "도입 기관 수" label. "127개 기관" large figure. "챗봇 상담 320만건 처리" annotation below.

Bottom summary strip spanning full width: "디지털 역량강화 교육 이수 공무원 45,800명" left-aligned, vertical divider, "하반기 목표: 클라우드 전환율 80% · AI 도입 200개 기관" right-aligned.
</layout>
```
