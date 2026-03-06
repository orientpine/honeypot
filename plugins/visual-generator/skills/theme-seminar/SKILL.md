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

## Positive Scene Direction

- 장면 묘사는 3D 아이콘, 프로스티드 글래스 카드, 정돈된 레이아웃 중심으로 작성한다
- 연구/발표 맥락은 공간 소품과 오브젝트로 표현한다
- 텍스트는 `<text_to_render>`에만 담고, `<scene>`은 장면 설명만 유지한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 제목 > 부제목 > 카드라벨 > KPI
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- 숫자 강조는 굵게, 본문은 중간 굵기로 균형 유지

## XML-Tag 출력 매핑

- `<scene>`: 무드 톤과 장면 메타포를 3~5문장으로 기술
- `<text_to_render>`: 최대 25항목, 렌더링 문자열만 `key: "value"`
- `<typography>`: 한글 서체 힌트와 위계 규칙
- `<canvas>`: 3840x2160, 16:9, 해당 무드 팔레트
- `<layout>`: `<text_to_render>` 값을 큰따옴표로 인용해 위치 지정

무드 톤 가이드:
- `technical-report`: 차분하고 정밀한 분위기
- `innovation`: 역동적이되 과장 없는 대비
- `presentation`: 명확한 시선 유도와 중간 대비
