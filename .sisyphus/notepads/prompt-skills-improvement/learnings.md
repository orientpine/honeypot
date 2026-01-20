# Learnings: prompt-skills-improvement

## [2026-01-20T16:15] Task 0: 공통 레이아웃 파일 생성

### 성공 패턴
- **Copy-and-adapt 접근**: seminar의 15개 레이아웃을 베이스로 사용, 포맷이 가장 완전함
- **ASCII 다이어그램**: 각 레이아웃에 시각 구성을 ASCII로 표현하여 이해도 향상
- **크기 등급제**: pt/px 대신 "대형/중형/소형" 사용, Gemini 렌더링 방지 효과적

### 발견한 규칙
- **레이아웃 구조**: 핵심 아이디어 → ASCII → 시각화 원칙 → 권장 사양 테이블 → 적합/부적합 케이스 (5섹션 고정)
- **테이블 포맷**: 요소, 설명, 권장 수량 (3컬럼) - 크기 컬럼 제거함
- **Gov 고유 레이아웃 4종**: Pyramid, Exploded View, Horizontal Timeline, Org-Network (통합 완료)

### 신규 레이아웃 추가 (5종)
1. **Bento Grid**: Apple 스타일 모듈형 그리드 - Hero 타일 중심 구조
2. **Sankey**: 흐름 두께로 비율 표현 - 예산/자원 배분에 적합
3. **Z-Pattern**: 자연스러운 시선 흐름 (좌상→우상→좌하→우하) - 4코너 앵커
4. **Mind Map**: 방사형 분기 - 아이디어 탐색/주제 확장
5. **Stacked Progress**: 누적 구성 - 진행/구성 비중 표현

### 파일 위치
- **생성**: `plugins/visual-generator/references/layout_types.md` (공통 참조)
- **삭제 대상** (Tasks 1,2,3): 각 스킬의 중복 layout_types.md 파일
