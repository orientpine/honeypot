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

## Positive Scene Direction

- 좌우 장면은 동일 주제를 다른 상태로 명확히 묘사한다
- 장면 설명에는 환경, 주체, 행동, 톤을 포함한다
- 텍스트는 오버레이 수치와 짧은 라벨만 유지한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 좌우 제목 > 핵심 수치 > 보조 라벨
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

## XML-Tag 출력 매핑

- `<scene>`: LEFT/RIGHT 장면을 각각 1~2문장으로 기술
- `<text_to_render>`: 최대 12항목, 대응 수치/라벨만 포함
- `<typography>`: 비교용 위계와 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 분할 대비 톤
- `<layout>`: 인용 문자열을 좌우 오버레이에 대응 배치

무드 톤 가이드:
- LEFT는 차분하고 무거운 톤
- RIGHT는 밝고 선명한 톤
- 변화 강조는 중앙 전환 요소로 처리
