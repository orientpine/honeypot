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

## Positive Scene Direction

- 핵심 메시지는 캐릭터/행동/환경/결과의 시각 대비로 전달한다
- 텍스트 라벨 대신 오브젝트 관계와 스케일로 의미를 표현한다
- 장면 요소는 캔버스 경계 안에서 완결되게 배치한다

## 한글 타이포그래피 가이드

concept는 기본적으로 텍스트 렌더링을 사용하지 않는다.
- `<typography>`에는 다음 힌트를 최소로 유지한다: `Korean Sans-serif (Gothic style)`
- 필요 시 캡션 수준의 최소 문자열만 허용하며 가독성 키워드를 포함한다
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

## XML-Tag 출력 매핑

- `<scene>`: 중심 장면을 3~5문장으로 상세 기술
- `<text_to_render>`: 비워 둔다 (항목 0개)
- `<typography>`: 텍스트 최소 사용 원칙과 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 무드 팔레트 반영
- `<layout>`: 장면 요소 위치를 자연어로 기술

무드 톤 가이드:
- `technical-report`: 구조적이고 차분한 탐구 장면
- `innovation`: 강한 대비와 전환 순간 강조
- `knowledge`: 발견과 학습의 깊이감 강조
