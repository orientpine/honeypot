---
name: theme-gov
description: "visual-generator gov 테마 무드 팔레트와 XML-tag 장면 가이드. Use when theme=gov."
---

# Gov Theme

정부/공공기관 발표 톤의 정돈된 인포그래픽 테마다.

## Mood Palette (9)

| mood | primary | secondary | accent | background |
|------|---------|-----------|--------|------------|
| technical-report | #1E3A5F | #4A90A4 | #E07B39 | #F5F7FA |
| growth | #1B4332 | #2D6A4F | #40916C | #F0F4F0 |
| clarity | #2C3E50 | #5D6D7E | #F39C12 | #FAFAFA |
| connection | #4A1A6B | #7B2CBF | #E040FB | #F8F5FA |
| innovation | #0B525B | #3A9D7A | #B4D6C1 | #F0FAF5 |
| tech-focus | #2C6AA0 | #415A77 | #3BC9DB | #F5F7FA |
| knowledge | #2E5090 | #5D6D7E | #E07B39 | #FAFAFA |
| presentation | #D35400 | #1E3A5F | #F39C12 | #F5F7FA |
| workshop | #117A65 | #1B4332 | #3A9D7A | #F0FAF5 |

## Scene Guide (Rendering Style -> `<scene>`)

`<scene>`에는 아래 요소를 자연어로 기술한다.
- 서피스: 직각 박스와 질서 있는 패널
- 배경: 밝은 중립 배경과 상단 배너 감성
- 코너: 선명한 직각 경계
- 연결선: 굵고 명확한 흐름 화살표
- 시각장식: 절제된 플랫 아이콘과 구조선
- 공간구성: 규칙적인 격자와 균등 분배
- 시각메타포: 신뢰, 제도, 실행 체계 강조

## Positive Scene Direction

- 기관 식별 요소 없이 공공 문서 톤만 유지한다
- 비교 장면이 필요한 경우 좌우 균형과 통합 하단 영역을 명시한다
- 메시지는 구조적 배치와 핵심 수치로 전달한다

## 한글 타이포그래피 가이드

- 권장 힌트: `Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)`
- 위계 비율: 제목 > 부제목 > 본문 > 보조수치
- 가독성 키워드: `Crisp anti-aliased Korean typography`, `Professional typesetting`
- 번호/지표는 동일 계열 폰트로 통일한다

## XML-Tag 출력 매핑

- `<scene>`: 공공 발표 톤 장면 설명
- `<text_to_render>`: 최대 25항목, 키워드/수치 중심
- `<typography>`: 한글 가독성 힌트와 위계
- `<canvas>`: 3840x2160, 16:9, 무드 팔레트
- `<layout>`: 인용 텍스트 중심 배치 설명

무드 톤 가이드:
- `technical-report`: 가장 공식적이고 차분한 톤
- `innovation`: 변화와 전환을 부드럽게 강조
- `clarity`: 설명 중심, 높은 판독성 유지
