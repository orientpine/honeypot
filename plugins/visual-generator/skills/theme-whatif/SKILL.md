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

## Positive Scene Direction

- 장면은 After 상태 하나만 묘사한다
- 행위자, 행동, 환경, 성과, 시간 단서를 함께 담는다
- 성과 수치는 장면 안 UI 요소로 자연스럽게 배치한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 선언문 > KPI > 라벨 > 보조텍스트
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`

## XML-Tag 출력 매핑

- `<scene>`: 미래 비전 장면을 3~5문장으로 명확히 묘사
- `<text_to_render>`: 최대 20항목, UI/KPI 문자열만 포함
- `<typography>`: 한글 힌트와 숫자 강조 규칙
- `<canvas>`: 3840x2160, 16:9, 전용 팔레트
- `<layout>`: 인용 문자열 배치와 시선 흐름 설명

무드 톤 가이드:
- 기본 톤은 역동적이되 과밀하지 않게 유지
- 기술 시나리오는 차분한 미래 톤
- 비전 강조 시 장면 대비를 강하게 부여
