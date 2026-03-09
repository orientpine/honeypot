---
name: theme-seminar
description: "visual-generator seminar 테마 무드 팔레트와 XML-tag 장면 가이드. Use when theme=seminar."
---

# Seminar Theme

세미나/학술 발표용 에디토리얼 3D 톤을 위한 스킬이다.

## Mood Palette (9)

| mood | primary | secondary | accent | background |
|------|---------|-----------|--------|------------|
| technical-report | #2C3E50 | #5D6D7E | #2980B9 | #F8F9FA |
| clarity | #2D3436 | #636E72 | #74B9FF | #FAFAFA |
| tech-focus | #0984E3 | #2D3436 | #00CEC9 | #F5F6FA |
| growth | #00B894 | #1E3A3A | #55EFC4 | #F8FFFC |
| connection | #6C5CE7 | #3D3D6B | #A29BFE | #F8F7FF |
| innovation | #E17055 | #6B3A3A | #FDCB6E | #FFFAF5 |
| knowledge | #1E3A5F | #6B5B95 | #E07B39 | #FFFFFF |
| presentation | #0D4F4F | #5D6D7E | #FF6B6B | #F8F9FA |
| workshop | #2D5A3D | #6B6B6B | #4ECDC4 | #FFFEF5 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`는 아래 요소를 번호 없이 자연어로 묘사한다.
- 서피스: 아이소메트릭 3D 아이콘과 프로스티드 카드
- 배경: 밝은 중성 배경과 은은한 그라데이션
- 코너: 소프트 라운딩 카드 경계
- 연결선: 얇고 정돈된 흐름선
- 시각장식: 미니 소품, 아이콘, 글래스 레이어
- 공간구성: 텍스트와 3D 오브젝트의 에디토리얼 혼합
- 시각메타포: 세미나실 장면이 아닌 평면 인포그래픽 슬라이드

**품질 기준 참조**: `scene-richness-spec.md` (최소 5문장, 7요소 중 5+ 포함, negative prompting 필수)

## Positive Scene Direction

- 장면 묘사는 3D 아이콘, 프로스티드 글래스 카드, 정돈된 레이아웃 중심으로 작성한다
- 연구/발표 맥락은 공간 소품과 오브젝트로 표현한다
- 텍스트는 `<text_to_render>`에만 담고, `<scene>`은 장면 설명만 유지한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, Bold/ExtraBold weight Korean sans-serif)`
- 위계 비율: 제목 > 부제목 > 카드라벨 > KPI
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- 숫자 강조는 굵게, 본문은 중간 굵기로 균형 유지
- **상세 기준 참조**: `korean-typography-spec.md` (Heavy Gothic-style Hangul 필수, 자모분리 방지)
- Heavy Gothic-style Hangul (800+ weight) 권장
- Thin/Light Korean serif 회피
> ⚠️ **TYPOGRAPHY CRITICAL**: `<typography>` 태그에 구체적 폰트명 금지. Heavy-weight Gothic-style Korean sans-serif at 800+ weight 등 서술적 표현만 사용.

## XML-Tag 출력 매핑

- `<scene>`: 무드 톤과 장면 메타포를 3~5문장으로 기술
- `<text_to_render>`: 최대 25항목, 렌더링 문자열만 `key: "value"`
- `<typography>`: 한글 서체 힌트와 위계 규칙
- `<canvas>`: 3840x2160, 16:9, 해당 무드 팔레트
- `<layout>`: `<text_to_render>` 값을 큰따옴표로 인용해 위치 지정

**검증 규칙 참조**: `validation-rules-map.md` (orphan/ghost 방지, 이중렌더링 방지, 메타라벨 금지)

무드 톤 가이드:
- `technical-report`: 차분하고 정밀한 분위기
- `innovation`: 역동적이되 과장 없는 대비
- `presentation`: 명확한 시선 유도와 중간 대비


## Golden Reference Example

**주제**: Smart Factory AI 품질검사 시스템
**레이아웃**: hero_number
**테마 무드**: technical-report

```xml
<scene>
A sleek isometric 3D AI quality inspection control room bathed in cool blue-white lighting, with frosted glass panels displaying real-time defect detection feeds. The foreground features a robotic inspection arm with neon-blue sensor beams scanning a factory conveyor belt, casting sharp shadows on a metallic grey surface. In the midground, multiple holographic data dashboards show quality metrics with animated bar graphs and heat maps against a light neutral background. A deep perspective grid recedes toward a bright vanishing point in the background, creating depth. Visual hierarchy draws the eye from the robot arm to the central KPI display. No watermarks, no blurry text, no numbered lists as visual elements, no meta-labels, no artifacts.
</scene>

<text_to_render>
hero_stat: "99.7%"
hero_label: "불량 검출 정확도"
title: "AI 품질검사 시스템"
subtitle: "스마트 팩토리 실시간 모니터링"
kpi_1_value: "0.3%"
kpi_1_label: "불량률"
kpi_2_value: "4K"
kpi_2_label: "초당 검사 이미지"
kpi_3_value: "98초"
kpi_3_label: "불량 감지 반응시간"
section_1: "AI 비전 시스템"
item_1: "딥러닝 기반 결함 분류"
item_2: "멀티스펙트럼 이미징"
item_3: "실시간 엣지 컴퓨팅"
section_2: "도입 효과"
effect_1: "생산성 47% 향상"
effect_2: "검사 비용 62% 절감"
effect_3: "불량 유출 98% 감소"
section_3: "적용 분야"
field_1: "반도체 웨이퍼 검사"
field_2: "자동차 부품 검사"
field_3: "식품 이물 탐지"
footer: "2026년 스마트 제조 혁신 사례"
</text_to_render>

<typography>
All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts. Each Korean syllable block must be complete and legible. Font hierarchy: hero_stat (ExtraBold 900, 72pt scale), title (ExtraBold 800, 48pt scale), section headers (Bold 700, 24pt scale), body items (Medium 500, 18pt scale). "99.7%" hero statistic rendered in large accent color (#2980B9) with high contrast. Korean labels in Bold Modern Korean sans-serif at ExtraBold (800+).
</typography>

<canvas>
3840x2160 pixels, 16:9 aspect ratio. Background: light neutral #F8F9FA with subtle top-to-bottom gradient. Primary color #2C3E50 for structural elements and borders. Secondary #5D6D7E for supporting panels. Accent #2980B9 for hero statistics and highlights. Maintain 35% negative space for clean readability. Frosted glass card effects with soft rounded corners.
</canvas>

<layout>
Position "99.7%" as the dominant hero statistic in the upper-center, extra-large scale (occupying 20% of canvas height). Place "불량 검출 정확도" as the hero label directly below "99.7%" in medium scale. Position "AI 품질검사 시스템" as the slide title in upper-left quadrant. Arrange "딥러닝 기반 결함 분류", "멀티스펙트럼 이미징", "실시간 엣지 컴퓨팅" as bulleted items in the left column under "AI 비전 시스템". Arrange "생산성 47% 향상", "검사 비용 62% 절감", "불량 유출 98% 감소" in the center column under "도입 효과". Arrange "반도체 웨이퍼 검사", "자동차 부품 검사", "식품 이물 탐지" in the right column under "적용 분야". Place "스마트 팩토리 실시간 모니터링" as subtitle below the title. Position "0.3%", "4K", "98초" as KPI values with "불량률", "초당 검사 이미지", "불량 감지 반응시간" labels in a bottom row. Place "2026년 스마트 제조 혁신 사례" as footer text at the bottom center.
</layout>
```