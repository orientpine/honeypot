# Draft: Visual Generator 플러그인 개선

## 분석 완료 항목

### 1. 현재 구조 파악

```
plugins/visual-generator/
├── skills/
│   ├── prompt-concept/SKILL.md     # TED 스타일 개념 시각화 (12-15 요소)
│   ├── prompt-gov/SKILL.md         # 정부/공공기관 스타일 (25 요소)
│   ├── prompt-seminar/SKILL.md     # 세미나 발표 스타일 (20-30 요소)
│   ├── layout-types/SKILL.md       # 공유 레이아웃 24종 정의
│   └── renderer/SKILL.md           # Gemini API 이미지 렌더링
├── scripts/
│   └── generate_slide_images.py    # Gemini API 호출 스크립트
└── references/
    └── layout_types.md
```

### 2. 식별된 문제점

#### A. Renderer 스크립트 경로 문제
- **현재 경로**: `plugins/visual-generator/scripts/generate_slide_images.py`
- **문제**: Claude Code 플러그인은 설치 시 캐시 디렉토리로 복사됨
- **해결책**: `${CLAUDE_PLUGIN_ROOT}` 변수 사용 필요
  ```bash
  # 올바른 경로
  python ${CLAUDE_PLUGIN_ROOT}/scripts/generate_slide_images.py
  ```

#### B. 프롬프트 구성력 부족
- **현재**: 단일 스킬이 모든 프롬프트 생성 담당
- **문제**: 복잡한 시각화 요구사항에서 구성력 한계
- **제안**: 멀티 에이전트 워크플로우
  - 내용정리자 (Content Organizer)
  - 내용검토자 (Content Reviewer)
  - 디자이너 (Prompt Designer)
  - 최종검토자 (Final Reviewer)

#### C. 테마 다양성 부족
- **현재**: 3개 테마 (gov, seminar, concept)
- **요청**: 2개 신규 테마 추가

### 3. 연구 결과

#### Claude Code 플러그인 경로 규칙 (공식 문서)
1. 플러그인은 설치 시 캐시 디렉토리로 복사됨
2. `../` 경로 사용 불가 (복사 시 포함 안 됨)
3. 스크립트 참조 시 `${CLAUDE_PLUGIN_ROOT}` 변수 사용 필수
4. hooks/mcpServers에서도 동일 변수 사용

#### 2024-2025 프레젠테이션 디자인 트렌드
1. **Bento Grid**: Hero 카드 + 보조 카드 모듈형 배치
2. **Pitch Deck 스타일**: 스타트업/투자자 프레젠테이션
3. **Case Study 스타일**: Before/After 비교, 결과 중심
4. **Infographic Storytelling**: 데이터 시각화 중심 내러티브
5. **Technical Documentation**: 아키텍처/시스템 다이어그램

---

## 결정 사항

### 아키텍처 결정
- **방식**: 완전 Agent 전환 (모든 스킬 → agents/)
- **실행**: 자동 파이프라인 (사용자 요청 → 전체 워크플로우 자동 실행)

### 새 Agent 구조 (예상)
```
plugins/visual-generator/
├── agents/
│   ├── orchestrator.md          # 전체 워크플로우 조율
│   ├── content-organizer.md     # 내용 정리/구조화
│   ├── content-reviewer.md      # 내용 검토/피드백
│   ├── prompt-designer.md       # 프롬프트 생성 (테마별 분기)
│   └── final-reviewer.md        # 최종 품질 검토
├── skills/
│   └── layout-types/SKILL.md    # 레이아웃 정의 (유지, 참조용)
├── references/
│   ├── themes/                  # 테마별 스타일 가이드
│   │   ├── gov.md
│   │   ├── seminar.md
│   │   ├── concept.md
│   │   ├── whatif.md (신규)
│   │   └── [new-theme].md (신규)
│   └── output_templates/        # 출력 템플릿
└── scripts/
    └── generate_slide_images.py
```

### 신규 테마 결정 (3개)

#### 1. prompt-whatif (시나리오 시뮬레이션)
- **컨셉**: 제안된 내용이 구현된 실제 장면 + 설명용 오버레이 창
- **특징**: 영상/사진 위에 정보 레이어가 떠있는 형태
- **용도**: 기술 제안서, 비전 프레젠테이션, 미래 시나리오

#### 2. prompt-pitch (Pitch Deck 스타일)
- **컨셉**: 스타트업/투자자 프레젠테이션
- **구조**: 문제 → 해결책 → 시장 → 팀
- **특징**: 간결하고 임팩트 있는 시각 요소, 핵심 숫자 강조

#### 3. prompt-comparison (Before/After 레이아웃)
- **컨셉**: 현재 상태와 구현 후 상태 비교
- **특징**: 나란히 배치, 차이점 강조, 변환 흐름 표시
- **용도**: 개선 효과 시각화, 도입 전/후 비교

### 최종 테마 목록 (6개)
| 기존 | 신규 |
|------|------|
| gov (정부/공공) | whatif (시나리오 시뮬레이션) |
| seminar (세미나) | pitch (Pitch Deck) |
| concept (TED 스타일) | comparison (Before/After) |

### 기존 스킬 처리 결정
- **기존 prompt-* 스킬**: 완전 삭제 (agents/로 이전)
- **layout-types 스킬**: 유지 (레이아웃 정의 참조용)
- **renderer 스킬**: Agent로 통합 (renderer-agent.md)

### 테스트 전략 결정
- **엔드투엔드 테스트**: 실제 프롬프트 생성 + Gemini API 호출까지 전체 파이프라인 테스트
- marketplace.json 검증 포함
- 플러그인 재등록 테스트 포함

---

## 최종 결정 요약

| 항목 | 결정 |
|------|------|
| 아키텍처 | 완전 Agent 전환 |
| 실행 방식 | 자동 파이프라인 |
| 신규 테마 | whatif, pitch, comparison (3개) |
| 기존 스킬 | 삭제 (layout-types만 유지) |
| Renderer | Agent로 통합 |
| 테스트 | 엔드투엔드 |

---

## CLEARANCE: ALL REQUIREMENTS CLEAR
- 계획 생성 진행 가능

---

## Research Findings (외부)

### Claude Code Plugin Path Convention
- `${CLAUDE_PLUGIN_ROOT}`: 플러그인 설치 디렉토리
- hooks, mcpServers, skills에서 스크립트 참조 시 사용
- 예: `${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh`
