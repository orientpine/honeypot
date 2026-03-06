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

## Positive Scene Direction

- 핵심 숫자를 장면의 시각 중심으로 배치한다
- 각 슬라이드는 메시지 하나만 강조한다
- 텍스트는 짧고 즉시 해석 가능한 성과 문구 중심으로 구성한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 핵심숫자 > 제목 > 보조설명 > CTA
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

## XML-Tag 출력 매핑

- `<scene>`: 다크 프리미엄 톤을 3~5문장으로 기술
- `<text_to_render>`: 최대 18항목, 숫자 중심 키워드
- `<typography>`: 숫자 우선 위계와 한글 힌트
- `<canvas>`: 3840x2160, 16:9, 다크 팔레트
- `<layout>`: 인용 문자열 위치를 명확히 지정

무드 톤 가이드:
- 기본 톤은 강한 대비와 절제된 장식
- 성과 강조는 거대 숫자와 단문 조합
- CTA는 마지막 시선 지점에 배치
