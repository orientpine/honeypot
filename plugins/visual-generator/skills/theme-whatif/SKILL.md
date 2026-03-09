---
name: theme-whatif
description: "visual-generator whatif 목적 테마 장면 가이드와 XML-tag 매핑. Use when theme=whatif."
---

# What-If Theme

이미 구현된 미래를 단일 장면으로 몰입시켜 보여주는 테마다.

## Palette

| role | color |
|------|-------|
| primary | #1A535C |
| secondary | #4ECDC4 |
| accent | #FF6B35 |
| background | #F7FFF7 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`는 아래 요소를 자연어로 설명한다.
- 서피스: 반투명 UI 패널과 미래 장면 결합
- 배경: 어두움에서 밝음으로 이동하는 방향성
- 코너: 둥근 모서리와 부드러운 레이어
- 연결선: 빛 흐름 또는 HUD 스트림
- 시각장식: 미세한 보케와 인터페이스 오버레이
- 공간구성: 단일 몰입 장면, 분할 최소화
- 시각메타포: 이미 실현된 미래 일상

**품질 기준**: `scene-richness-spec.md` (최소 5문장, 7요소 중 5+, single immersive future scene, negative prompting)

## Positive Scene Direction

- 장면은 After 상태 하나만 묘사한다
- 행위자, 행동, 환경, 성과, 시간 단서를 함께 담는다
- 성과 수치는 장면 안 UI 요소로 자연스럽게 배치한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, Bold/ExtraBold weight Korean sans-serif)`
- 위계 비율: 선언문 > KPI > 라벨 > 보조텍스트
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

- **상세 기준**: `korean-typography-spec.md` (Heavy Gothic-style Hangul, HUD UI text clarity)

> ⚠️ **TYPOGRAPHY CRITICAL**: `<typography>` 태그에 구체적 폰트명 금지. Heavy-weight Gothic-style Korean sans-serif at 800+ weight 등 서술적 표현만 사용.
## XML-Tag 출력 매핑

- `<scene>`: 미래 비전 장면을 3~5문장으로 명확히 묘사
- `<text_to_render>`: 최대 20항목, UI/KPI 문자열만 포함
- `<typography>`: 한글 힌트와 숫자 강조 규칙
- `<canvas>`: 3840x2160, 16:9, 전용 팔레트
- `<layout>`: 인용 문자열 배치와 시선 흐름 설명

**검증 규칙**: `validation-rules-map.md` (orphan/ghost 방지, 단일 몰입 장면 유지)

무드 톤 가이드:
- 기본 톤은 역동적이되 과밀하지 않게 유지
- 기술 시나리오는 차분한 미래 톤
- 비전 강조 시 장면 대비를 강하게 부여


## Golden Reference Example

**Topic**: 자율주행 물류 센터 2030
**Layout**: `single_focus`
**Theme**: whatif

```xml
<scene>
A vast autonomous logistics mega-hub in the year 2030, already fully operational, with dozens of self-driving cargo vehicles gliding silently along luminous guidance tracks embedded in polished dark concrete floors. Towering vertical storage racks stretch upward into a ceiling crisscrossed by translucent HUD overlay beams projecting real-time throughput data, route optimization paths, and package tracking identifiers in soft teal and orange holographic light. Human supervisors stand on elevated glass-floored observation decks, casually monitoring floating dashboard panels that display system-wide KPIs — delivery completion rates, energy consumption graphs, and fleet utilization percentages — all rendered as sleek frosted-glass UI elements hovering at eye level. Robotic arms along the sorting corridors move with fluid precision, each surrounded by faint circular progress indicators and status halos in the whatif palette tones of deep teal and vibrant coral. The entire scene radiates a calm, achieved-future atmosphere with warm ambient lighting transitioning from deep shadows at the periphery to a bright, optimistic core where the central command hologram projects the day's logistics network map across the Asian continent.
</scene>

<text_to_render>
title: "자율주행 물류 센터 2030"
kpi_1: "일 처리량: 1,200,000 건"
kpi_2: "배송 완료율: 99.7%"
kpi_3: "무인 차량 가동률: 98.2%"
kpi_4: "에너지 효율: 42% 절감"
kpi_5: "평균 배송 시간: 2.4시간"
kpi_6: "실시간 경로 최적화"
kpi_7: "AI 수요 예측 정확도: 96.1%"
kpi_8: "탄소 배출 감축: 58%"
kpi_9: "로봇 분류 정확도: 99.95%"
kpi_10: "센터 가동 시간: 24/7/365"
kpi_11: "인력 대비 처리량: 15x"
kpi_12: "네트워크 커버리지: 아시아 12개국"
kpi_13: "고객 만족도: 4.9/5.0"
</text_to_render>

<typography>
All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts. Headline in Bold heavy-weight Gothic-style Korean sans-serif at ExtraBold (800+) at 120pt for title. KPI numbers in tabular-lining numerals at 72pt, high-contrast white on dark teal panels. KPI labels in Medium weight Gothic Korean at 36pt, secondary #4ECDC4 color. Body labels in Regular weight Korean Sans-serif at 28pt, muted white with 80% opacity. Crisp anti-aliased Korean typography, Professional typesetting, HUD-style UI text clarity. KPI numerals glow with subtle outer luminance matching accent #FF6B35.
</typography>

<canvas>
3840x2160 pixels, 16:9 aspect ratio. Color palette — primary: #1A535C (deep teal), secondary: #4ECDC4 (bright teal), accent: #FF6B35 (coral orange), background: #F7FFF7 (mint white). Achieved future atmosphere with calm technological confidence. Dark-to-light gradient from periphery to bright optimistic core.
</canvas>

<layout>
Position "자율주행 물류 센터 2030" as the title at top-center, floating above the central holographic command display with subtle glow effect. The central hologram projects a continental logistics network map as the main focal point. Arrange "일 처리량: 1,200,000 건", "배송 완료율: 99.7%", "무인 차량 가동률: 98.2%", and "에너지 효율: 42% 절감" as a KPI cluster in a left frosted-glass panel at 20% from left edge. Arrange "평균 배송 시간: 2.4시간", "실시간 경로 최적화", "AI 수요 예측 정확도: 96.1%", and "탄소 배출 감축: 58%" as a KPI cluster in a right frosted-glass panel at 80% from left edge. Place "로봇 분류 정확도: 99.95%", "센터 가동 시간: 24/7/365", "인력 대비 처리량: 15x", "네트워크 커버리지: 아시아 12개국", and "고객 만족도: 4.9/5.0" as a horizontal ticker bar across bottom 10% of canvas. Depth layers progress from background warehouse through mid-ground vehicles and sorting corridors to foreground observation deck with floating UI panels. Eye flow guides from top title through central hologram to left KPI panel, right KPI panel, and down to bottom ticker strip.
</layout>
```