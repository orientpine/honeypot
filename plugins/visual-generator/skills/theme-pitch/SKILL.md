---
name: theme-pitch
description: "visual-generator pitch 목적 테마 장면 가이드와 XML-tag 매핑. Use when theme=pitch."
---

# Pitch Theme

피치덱 설득 상황에 맞는 고대비 프리미엄 비주얼 테마다.

## Palette

| role | color |
|------|-------|
| primary | #F5F5F7 |
| secondary | #86868B |
| accent | #BF5AF2 |
| accent-secondary | #0A84FF |
| background | #000000 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`는 아래 요소를 자연어로 기술한다.
- 서피스: 프로스티드 글래스 카드
- 배경: 어두운 그라데이션과 절제된 컬러 워시
- 코너: 부드러운 라운딩 카드
- 연결선: 최소화된 흐름 표시
- 시각장식: 은은한 글로우와 소형 스파크라인
- 공간구성: 대담한 비대칭, 강한 여백
- 시각메타포: 키노트 스타일 발표 무드

**품질 기준**: `scene-richness-spec.md` (최소 5문장, 7요소 중 5+, dark premium atmosphere, negative prompting)
## Positive Scene Direction

- 핵심 숫자를 장면의 시각 중심으로 배치한다
- 각 슬라이드는 메시지 하나만 강조한다
- 텍스트는 짧고 즉시 해석 가능한 성과 문구 중심으로 구성한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 핵심숫자 > 제목 > 보조설명 > CTA
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

- **상세 기준**: `korean-typography-spec.md` (Heavy Gothic-style Hangul, high-contrast dark background text)
## XML-Tag 출력 매핑

- `<scene>`: 다크 프리미엄 톤을 3~5문장으로 기술
- `<text_to_render>`: 최대 18항목, 숫자 중심 키워드
- `<typography>`: 숫자 우선 위계와 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 다크 팔레트
- `<layout>`: 인용 문자열 위치를 명확히 지정

**검증 규칙**: `validation-rules-map.md` (orphan/ghost 방지, 숫자 중심 위계 준수)

무드 톤 가이드:
- 기본 톤은 강한 대비와 절제된 장식
- 성과 강조는 거대 숫자와 단문 조합
- CTA는 마지막 시선 지점에 배치


## Golden Reference Example

**Topic**: SaaS 플랫폼 성과 지표
**Layout**: `hero_number`
**Theme**: pitch

```xml
<scene>
칠흑같은 블랙 배경 위에 거대한 숫자 247%가 화면 중앙을 지배하며 은은한 퍼플 글로우로 시선을 끌어당긴다. 프로스티드 글래스 카드 세 쌍이 히어로 넘버 좌우로 균형 잡혀 배치되고, 각 카드 안에는 핵심 KPI 숫자가 액센트 컴러로 빛난다. Apple 키노트 무대처럼 절제된 그라데이션이 하단에서 상단으로 미세하게 흐르며, 카드 경계에는 1px 반투명 보더가 깊이감을 더한다. 배경의 미세한 노이즈 텍스처와 소형 스파크라인이 데이터 중심 프리미엄 분위기를 완성한다. 텍스트 외의 장식 요소, 과도한 아이콘, 밝은 배경색은 절대 사용하지 않는다.
</scene>

<text_to_render>
hero_number: "247%"
hero_label: "연간 매출 성장률"
kpi_1_number: "₩18.3B"
kpi_1_label: "ARR"
kpi_2_number: "94.7%"
kpi_2_label: "고객 유지율"
kpi_3_number: "12,400+"
kpi_3_label: "엔터프라이즈 고객"
kpi_4_number: "3.2x"
kpi_4_label: "LTV/CAC 비율"
kpi_5_number: "₩2.1B"
kpi_5_label: "월간 반복 매출"
kpi_6_number: "68ms"
kpi_6_label: "평균 응답 속도"
subtitle: "2025 Annual Performance"
source: "내부 대시보드 기준 2025.12"
</text_to_render>

<typography>
All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts. Bold Modern Korean Sans-serif (Gothic style, e.g. Pretendard ExtraBold, Nanum Gothic Bold). Hero number "247%" at 120pt in accent purple #BF5AF2, center-aligned, extra-bold weight. Hero label "연간 매출 성장률" at 28pt in #F5F5F7, center-aligned. KPI numbers at 36pt in #0A84FF, left-aligned within frosted-glass cards. KPI labels at 16pt in #86868B, left-aligned within cards. Subtitle at 18pt in #86868B, center-bottom. Source attribution at 12pt in #86868B, right-bottom corner. Crisp anti-aliased Korean typography with professional typesetting.
</typography>

<canvas>
3840x2160 pixels, 16:9 aspect ratio. Pure black background #000000. Color palette — primary: #F5F5F7 (near-white), secondary: #86868B (medium grey), accent: #BF5AF2 (purple), accent-secondary: #0A84FF (blue). Subtle noise texture on background for depth. No bright backgrounds, no warm tones.
</canvas>

<layout>
Position "247%" as the dominant hero number at center, occupying 40% vertical height with maximum visual impact in accent purple. Place "연간 매출 성장률" as hero label directly below "247%" in center-aligned near-white text. Arrange three frosted-glass KPI cards in a horizontal row above the hero: left card contains "₩18.3B" with "ARR", center card contains "94.7%" with "고객 유지율", right card contains "12,400+" with "엔터프라이즈 고객". Arrange three more frosted-glass KPI cards in a horizontal row below the hero label: left card contains "3.2x" with "LTV/CAC 비율", center card contains "₩2.1B" with "월간 반복 매출", right card contains "68ms" with "평균 응답 속도". Place "2025 Annual Performance" as subtitle at center, 85% from top. Place "내부 대시보드 기준 2025.12" as source text at right-bottom corner, 95% from top.
</layout>
```