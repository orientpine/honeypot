---
name: theme-concept
description: "visual-generator concept 테마 무드 팔레트와 XML-tag 장면 가이드. Use when theme=concept."
---

# Concept Theme

Kurzgesagt 풍 장면 스토리텔링 전용 테마다. 핵심 원칙은 텍스트 없이 장면으로만 설명하는 것이다.

## Mood Palette (9)

| mood | primary | secondary | accent | foreground |
|------|---------|-----------|--------|------------|
| technical-report | #1B2838 | #00BCD4 | #FF6F00 | #E0F7FA |
| clarity | #0D2137 | #26C6DA | #FFCA28 | #ECEFF1 |
| tech-focus | #0A1628 | #2979FF | #00E5FF | #E8EAF6 |
| growth | #1B3A2D | #66BB6A | #FFD54F | #E8F5E9 |
| connection | #1A1A3E | #AB47BC | #26C6DA | #F3E5F5 |
| innovation | #212121 | #FF7043 | #FF4081 | #FFF3E0 |
| knowledge | #0D1B2A | #1E88E5 | #FFC107 | #E3F2FD |
| presentation | #0E3B43 | #E53935 | #FFEE58 | #E0F2F1 |
| workshop | #2E3B2E | #FF8A65 | #4DD0E1 | #FFF8E1 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`는 아래 요소를 번호 없이 자연어로 작성한다.
- 서피스: 플랫 벡터 도형과 캐릭터
- 배경: 어두운 단색/미세 그라데이션
- 코너: 큰 라운딩 기반
- 연결선: 화살표 대신 입자 흐름/행동 연쇄
- 시각장식: 글로우, 보케, 리듬감 있는 레이어
- 공간구성: 풀블리드, 전경-중경-후경
- 시각메타포: 추상 개념을 물리 장면으로 번역

**Concept 테마 특칙**: `scene-richness-spec.md` (최소 7문장, 7요소 전부 포함 목표, 시각 메타포 집중, negative prompting 필수)

## Positive Scene Direction

- 핵심 메시지는 캐릭터/행동/환경/결과의 시각 대비로 전달한다
- 텍스트 라벨 대신 오브젝트 관계와 스케일로 의미를 표현한다
- 장면 요소는 캔버스 경계 안에서 완결되게 배치한다

## 한글 타이포그래피 가이드

concept는 기본적으로 텍스트 렌더링을 사용하지 않는다.
- `<typography>`에는 다음 힌트를 최소로 유지한다: `Korean Sans-serif (Gothic style)`
- 필요 시 캡션 수준의 최소 문자열만 허용하며 가독성 키워드를 포함한다
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- **상세 기준**: `korean-typography-spec.md` (Heavy Gothic-style Hangul, 자모분리 방지)

## XML-Tag 출력 매핑

- `<scene>`: 중심 장면을 **최소 7문장**으로 상세 기술 (concept 특칙)
- `<text_to_render>`: 비워 둔다 (항목 0개)
- `<typography>`: 텍스트 최소 사용 원칙과 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 무드 팔레트 반영
- `<layout>`: 장면 요소 위치를 자연어로 기술

**검증 규칙**: `validation-rules-map.md` (text_to_render 항목 수 = 0 엄격 준수, ghost reference 방지)

무드 톤 가이드:
- `technical-report`: 구조적이고 차분한 탐구 장면
- `innovation`: 강한 대비와 전환 순간 강조
- `knowledge`: 발견과 학습의 깊이감 강조

## Golden Reference Example

**Topic**: 탄소중립 도시 비전
**Layout**: `full_bleed`
**Theme**: concept / mood: `knowledge`

```xml
<scene>
A vast aerial view of a futuristic carbon-neutral city stretches across the entire canvas, rendered in Kurzgesagt flat-vector style against a deep navy (#0D1B2A) background with subtle radial gradient toward the center. In the foreground, oversized translucent leaf-shaped solar collectors rise from geometric rooftops, their surfaces glowing with soft cerulean (#1E88E5) energy pulses that flow downward through luminous conduit lines embedded in building walls. The mid-ground reveals a network of elevated green corridors connecting tower clusters, where tiny flat-vector citizens walk among miniature forests growing on bridge surfaces — each tree canopy rendered as layered concentric circles in graduating emerald-to-lime tones with gentle bokeh particles drifting upward like fireflies. A colossal wind turbine array occupies the right third of the scene, blades abstracted into sweeping golden (#FFC107) arcs that trail particle streams suggesting perpetual rotation, their bases wrapped in moss-textured geometric patterns. Below street level, a cross-section cutaway exposes an underground hydrogen pipeline network illustrated as glowing blue capillaries branching through earth layers rendered in warm brown gradients, with tiny animated spark nodes at each junction point pulsing rhythmically. The sky transitions from deep navy at the edges to a hopeful dawn gradient at the horizon line, populated by simplified bird silhouettes and a large circular sun motif composed of concentric golden rings with a white-hot center. Negative space is used deliberately: no text, no labels, no numbers appear anywhere — the entire narrative of carbon neutrality is conveyed purely through the visual metaphor of organic energy flowing from nature into human infrastructure and back again, creating a closed-loop visual cycle that the viewer traces naturally from solar collectors to buildings to underground networks to turbines to sky and back down.
</scene>

<text_to_render>
</text_to_render>

<typography>
Korean Sans-serif (Gothic style). Crisp anti-aliased Korean typography. Professional typesetting. No text elements rendered on canvas.
</typography>

<canvas>
3840x2160 pixels, 16:9 aspect ratio. Background: deep navy #0D1B2A. Color palette — primary: #0D1B2A, secondary: #1E88E5, accent: #FFC107, foreground: #E3F2FD. Subtle radial gradient from center. Rich layered depth with foreground-midground-background separation.
</canvas>

<layout>
Full-bleed composition with no margins. Left third: solar collector towers and building cluster with green corridors. Center: elevated walkways and citizen activity zone with bokeh particle field. Right third: wind turbine array with golden arc trails. Lower quarter: underground cross-section cutaway showing hydrogen pipeline network. Upper edge: dawn gradient sky with bird silhouettes and concentric sun motif. Visual flow guides the eye in a clockwise loop from top-left solar panels through center activity to right turbines, down through underground pipes, and back up.
</layout>
```
