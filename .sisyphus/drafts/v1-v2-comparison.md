# V1.11.0 vs V2.x Prompt-Designer Comparison

## Summary
- v1.11.0 reference commit: afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb
- Current version commit: 2e6e917 (visual-generator update)
- 비교 대상: prompt-designer.md, visual-generate.md

## V1.11.0 핵심 강점 (V2.x에서 손실된 것들)

### 강점 1: 인라인 Golden Reference Example
**V1.11.0**: 파일 내에 완전한 예시 프롬프트 포함 (gov/technical-report 스타일 90+ 줄)
- INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN 전체 블록을 실제 내용으로 채운 예시
- "AI 기반 스마트 제조 시스템" 예시 — 제목, 비전박스, 연구영역×3, 기대효과×3, 성과지표 포함 (9개 이상 항목)

**현재 V2.x 상태**: 인라인 예시 없음 (Output Format에 빈 틀만 표시)

**영향**: 에이전트가 얼마나 상세하게 작성해야 하는지 기준점 없음 → 저밀도 프롬프트 생성

### 강점 2: 구성용 텍스트 분리 원칙 (CRITICAL 섹션)
**V1.11.0**: `구성용 텍스트 분리 원칙` 전용 섹션 존재
- CONTENT BLOCK에 절대 넣으면 안 되는 6가지 유형 명시
- 올바른/잘못된 CONTENT BLOCK 예시 비교 쌍 제공
- `검증 체크리스트` 6항목 포함

**현재 V2.x 상태**: 단편적 MUST NOT DO 규칙만 존재 (체계적 분리 원칙 부재)

**영향**: 에이전트가 위치지시자, 레이아웃명, 색상코드를 text_to_render에 포함하는 오류 발생

### 강점 3: 밀도 초과 시 처리 절차 명시
**V1.11.0**: `밀도 초과 시 처리` 섹션 — 4단계 절차 명시
1. 핵심 메시지 우선순위 재검토
2. 유사 항목 병합
3. 보조 정보 제거
4. 복수 슬라이드 분리 고려

**현재 V2.x 상태**: 최대 항목 수 테이블만 있음, 초과 시 처리 절차 없음

**영향**: 에이전트가 밀도 초과 시 임의로 항목 삭제 → 핵심 내용 소실

### 강점 4: 출력 포맷 강제 규칙 명시 (MANDATORY)
**V1.11.0**: `출력 포맷 강제 규칙` 섹션 — 파일 헤더, 메타 정보, 블록 구분자, 서브섹션까지 정확한 형태 명시
- `## INSTRUCTION`이 아닌 `# INSTRUCTION BLOCK` 형태 금지 등 상세 규칙
- INSTRUCTION 필수 서브섹션 7개, CONFIGURATION 필수 서브섹션 5개 열거

**현재 V2.x 상태**: Output Format 섹션에 XML 구조만 간단히 표시

**영향**: XML 태그 구조는 유지되나 내용의 상세도가 낮아짐

### 강점 5: 폰트명 금지 명시 (부분)
**V1.11.0**: FORBIDDEN ELEMENTS에 `폰트 지정 (예: "Arial", "Pretendard")` 명시

**현재 V2.x 상태**: `<typography>` 섹션에 `Heavy-weight Gothic-style Hangul (Pretendard ExtraBold, Nanum Gothic ExtraBold, 800+ weight)` — 역설적으로 폰트명 권장!

**영향**: prompt-designer 자체가 폰트명을 typography 태그에 넣도록 유도 → 이미지 내 폰트명 렌더링 직접 원인

## V2.x가 V1.11.0보다 나은 점 (유지해야 할 것)
- XML-tag 5개 구조 (`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`)
- render_text/scene_context 명확한 분리
- validation-rules-map.md 참조 통합
- 번호 참조 체계, orphan/ghost 방지 규칙

## Task 7 (prompt-designer 강화) 반영 권고사항

### 권고 1: Golden Reference 인라인 추가
- seminar 테마 기준 body 슬라이드 예시를 XML-tag 형식으로 파일 내에 추가
- 최소 8항목 이상의 text_to_render를 포함한 완전한 예시
- `scene-richness-spec.md`의 25항목 Golden Reference를 참조 기준으로 명시

### 권고 2: 최소 밀도 강제 규칙 추가 (MUST DO)
- body 슬라이드 `<text_to_render>` 최소 8항목 명시
- title 슬라이드 최소 3항목 명시
- 밀도 부족 시 보강 방법 (KPI 분해, 데이터 포인트 3배 확장) 명시

### 권고 3: 폰트명 금지 규칙 MUST NOT DO에 추가
- `<typography>`에 Nanum Gothic, Pretendard, Apple SD Gothic Neo, Malgun Gothic 사용 금지
- 현재 line 54의 폰트명 권장 → 서술적 표현으로 교체 필수
- 교체 텍스트: "heavy-weight Gothic-style sans-serif Korean font at 800+ weight"

### 권고 4: Style Sheet 생성 메커니즘 추가
- 첫 번째 슬라이드 생성 시 palette/surface_style/lighting/icon_style 추출
- `{output_path}/style_sheet.md`에 저장
- 이후 슬라이드는 Style Sheet를 읽고 동일 스타일 적용

### 권고 5: PhD급 청중 품질 지침 추가
- "공학 박사 수준 청중을 위한 시각자료는 구체적 수치, 방법론 키워드, 성과 지표로 채워져야 한다"
- "각 슬라이드에 최소 2개의 정량적 지표(%, 건, 억원, 초 등)를 포함"

## 재현 불필요 패턴 (XML-tag 유지)
- 4-block 마크다운(INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) 형식으로 회귀 금지
- XML-tag 5개 구조 유지 (`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`)
- render_text/scene_context 분리 체계 유지
