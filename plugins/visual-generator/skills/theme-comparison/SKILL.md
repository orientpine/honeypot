---
name: theme-comparison
description: "visual-generator comparison 목적 테마 장면 가이드와 XML-tag 매핑. Use when theme=comparison."
---

# Comparison Theme

Before/After 차이를 한 화면에서 직관적으로 비교하는 테마다.

## Palette

| role | color |
|------|-------|
| primary | #2D3436 |
| secondary | #00B894 |
| accent | #FF7675 |
| background | #F5F6FA |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`는 좌우 장면을 분리해 자연어로 기술한다.
- LEFT: 기존 상태의 밀도, 문제, 낮은 성과
- RIGHT: 개선 상태의 정돈, 효율, 높은 성과
- 서피스: 풀블리드 이미지와 오버레이 텍스트
- 배경: 50:50 분할 구조
- 코너: 직각 분할 경계
- 연결선: 중앙 전환 화살표 또는 VS 배지
- 시각장식: 최소 아이콘, 핵심 수치 강조

**품질 기준**: `scene-richness-spec.md` (최소 5문장: LEFT 2~3문장 + RIGHT 2~3문장, negative prompting, split structure)

## Positive Scene Direction

- 좌우 장면은 동일 주제를 다른 상태로 명확히 묘사한다
- 장면 설명에는 환경, 주체, 행동, 톤을 포함한다
- 텍스트는 오버레이 수치와 짧은 라벨만 유지한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 좌우 제목 > 핵심 수치 > 보조 라벨
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- **상세 기준**: `korean-typography-spec.md` (Heavy Gothic-style Hangul, text-on-background contrast for both panels)

## XML-Tag 출력 매핑

- `<scene>`: LEFT/RIGHT 장면을 각각 1~2문장으로 기술
- `<text_to_render>`: 최대 12항목, 대응 수치/라벨만 포함
- `<typography>`: 비교용 위계와 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 분할 대비 톤
- `<layout>`: 인용 문자열을 좌우 오버레이에 대응 배치
**검증 규칙**: `validation-rules-map.md` (LEFT/RIGHT 대응 orphan 방지, 비교쌍 완전성 검증)

무드 톤 가이드:
- LEFT는 차분하고 무거운 톤
- RIGHT는 밝고 선명한 톤
- 변화 강조는 중앙 전환 요소로 처리

---

## Golden Reference Example

**주제**: 기존 공정 vs AI 공정 비교
**레이아웃**: `split_comparison` | **테마**: comparison

```xml
<scene>
LEFT side shows a traditional factory floor with heavy steel machinery, dim fluorescent lighting casting yellow shadows on oil-stained concrete, workers in hardhats manually inspecting products on a slow conveyor belt with clipboards. RIGHT side depicts a modern AI-enhanced production line with sleek white robotic arms, bright LED panel lighting, holographic quality dashboards floating above the line, and a single engineer monitoring multiple screens. A bold circular VS badge sits at the center dividing the two worlds with a sharp vertical split. No cartoon style, no flat illustration, no watermark, no border, no text outside overlay zones.
</scene>

<text_to_render>
before_title: "기존 수동 공정"
before_stat1: "불량률 12.4%"
before_stat2: "공정 시간 48h"
before_label1: "수작업 검수"
before_label2: "사후 대응"
before_badge: "LEGACY"
after_title: "AI 스마트 공정"
after_stat1: "불량률 1.8%"
after_stat2: "공정 시간 12h"
after_label1: "실시간 AI 검수"
after_label2: "예측 정비"
after_badge: "AI-DRIVEN"
</text_to_render>

<typography>
Font family: Heavy Gothic-style Korean Sans-serif (Nanum Gothic ExtraBold, Pretendard Black)
before_title / after_title: 64pt, bold, ALL-CAPS badge style
before_stat1, before_stat2 / after_stat1, after_stat2: 80pt, extra-bold, key metric emphasis
before_label1, before_label2 / after_label1, after_label2: 36pt, medium weight, descriptive sub-label
before_badge / after_badge: 28pt, uppercase, rounded pill background
LEFT panel text: white (#FFFFFF) on dark overlay for contrast against heavy industrial background
RIGHT panel text: dark charcoal (#2D3436) on light frosted overlay for contrast against bright clean background
Crisp anti-aliased Korean typography, Professional typesetting, no pixelation
</typography>

<canvas>
Width: 3840
Height: 2160
Aspect ratio: 16:9
Color palette: primary #2D3436, secondary #00B894, accent #FF7675, background #F5F6FA
Split structure: 50:50 vertical divide
LEFT panel: darker industrial tone with muted warm overlay (#2D3436 at 60% opacity)
RIGHT panel: lighter clean tone with bright cool overlay (#F5F6FA at 40% opacity)
Center divider: 4px solid #00B894 vertical line with VS badge
</canvas>

<layout>
LEFT half (x: 0–1920):
  "기존 수동 공정" — top-left (x:120, y:140), left-aligned
  "LEGACY" — pill badge below title (x:120, y:240)
  "불량률 12.4%" — center-left hero stat (x:960, y:800), center-aligned
  "공정 시간 48h" — below hero stat (x:960, y:1000), center-aligned
  "수작업 검수" — lower-left label (x:300, y:1500)
  "사후 대응" — lower-left label (x:300, y:1650)

RIGHT half (x: 1920–3840):
  "AI 스마트 공정" — top-right (x:2040, y:140), left-aligned
  "AI-DRIVEN" — pill badge below title (x:2040, y:240)
  "불량률 1.8%" — center-right hero stat (x:2880, y:800), center-aligned
  "공정 시간 12h" — below hero stat (x:2880, y:1000), center-aligned
  "실시간 AI 검수" — lower-right label (x:2220, y:1500)
  "예측 정비" — lower-right label (x:2220, y:1650)

CENTER (x: 1920):
  VS badge — circular, centered vertically (y:900), #00B894 background, white text
</layout>
```
