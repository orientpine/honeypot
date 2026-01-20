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

---

## [2026-01-20T17:20] Tasks 1, 2, 3: 3개 스킬 업데이트 (병렬 실행)

### Task 1: prompt-seminar (성공)
- ✅ 레이아웃 참조 경로 변경: `../../references/layout_types.md`
- ✅ Old layout file 삭제
- ✅ 9개 신규 레이아웃 활용 가이드 추가
- **성공 요인**: 이미 최신 구조 (4-block, 9 themes) → 최소 변경만 필요

### Task 2: prompt-concept (재시도 후 성공)
- ✅ 렌더링 방지 검증 단계 추가 (lines 148, 326)
- ✅ 9개 테마로 확장 (knowledge, presentation, workshop 추가)
- ✅ pt/px 제거 (prompt_style_guide.md)
- ✅ Old layout file 삭제
- **재시도 이유**: 초기 시도에서 old file 미삭제, 테마 7개만 추가
- **성공 패턴**: 명시적 검증 명령 제공 후 재위임

### Task 3: prompt-gov (재시도 후 성공)
- ✅ 4-block 구조 재구성 (INSTRUCTION, CONFIGURATION, CONTENT, FORBIDDEN)
- ✅ 9개 테마로 확장 (Gov 색상 코드 보존: #1E3A5F 등)
- ✅ Old layout file 삭제
- ✅ pt/px 제거
- **재시도 이유**: 초기 시도에서 4-block 미구현, 테마 2개만 존재
- **성공 패턴**: 구체적 구조 예시 + 검증 명령 제공

### 병렬 실행 성과
- **시간 절약**: 3개 태스크 동시 실행 (sequential 대비 ~30분 단축)
- **독립성 확인**: 각 스킬 폴더 간 충돌 없음
- **재시도 효율**: 실패한 2개만 개별 재위임

### 발견한 패턴
- **Subagent 검증 필수**: "완료" 보고만 믿지 말고 PROJECT-LEVEL 검증 필수
- **구체적 fix prompt**: "fix XYZ" 보다 "run these commands, verify with these" 가 효과적
- **Gov 색상 보존**: 테마명 통일해도 기존 색상 코드(#1E3A5F)는 유지해야 Gov 정체성 보존

---

## [2026-01-20T17:35] Task 4: 최종 검증 완료

### 검증 항목 (전부 통과)
✅ **pt/px 제거**: 0건 (CONTENT 블록에서 완전 제거)
✅ **공통 레이아웃 참조**: 3/3 스킬 모두 `../../references/layout_types.md` 참조
✅ **테마 통일**: prompt-seminar(11), prompt-concept(9), prompt-gov(9) - 모두 9개 이상
✅ **렌더링 체크리스트**: 3/3 스킬 모두 존재
✅ **중복 파일 삭제**: Old layout_types.md 0건 (3개 스킬에서 모두 삭제)
✅ **4-block 구조**: 3/3 스킬 모두 INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN 구조

### 최종 성과
- **24종 공통 레이아웃**: 15 기존 + 4 Gov 고유 + 5 신규 트렌드
- **3개 스킬 현대화**: prompt-seminar (최신), prompt-concept (업데이트), prompt-gov (재구성)
- **렌더링 안전성**: pt/px 완전 제거, 크기 등급제 적용
- **유지보수성**: 단일 참조 파일로 중복 제거

### 프로젝트 통계
- **총 태스크**: 5개 (0, 1, 2, 3, 4)
- **병렬 실행**: Tasks 1, 2, 3 동시 처리
- **재시도**: Tasks 2, 3 각 1회 (검증 기반 수정)
- **커밋**: 2개 (Task 0, Tasks 1+2+3 grouped)
- **삭제된 중복**: 3,170 lines (old layout files)
- **추가된 기능**: 440 lines (shared layouts + modern structure)
