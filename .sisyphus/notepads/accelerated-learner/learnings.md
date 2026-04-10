# learnings.md — accelerated-learner

## 프로젝트 컨벤션

- plugin.json: `author.email: orientpine@gmail.com`, version: 1.0.0
- marketplace.json 항목: `"skills": ["./skills"]` (trailing slash 금지)
- 에이전트 frontmatter: name, description("Use when..." 포함), model, tools, skills
- 스킬 name = 디렉토리명 = `learning-methodology` (소문자+하이픈만)
- 커맨드 파일: frontmatter 없음
- 모든 출력: 한국어 (영어 소스 허용)
- 버전 목표: 3.22.0 (marketplace, AGENTS.md, README.md)

## 이번 작업 메모

- 새 플러그인은 `plugins/{name}/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` 등록만으로도 뼈대가 먼저 잡힌다.
- marketplace의 `agents` 경로는 파일이 아직 없어도 선등록 가능하다.
- JSON 검증은 현재 환경에서 LSP biome가 없어서 실패했으므로, node JSON parse로 대체 검증했다.
- `learning-methodology` 스킬은 7개 필수 섹션을 고정 뼈대로 두고, 상세 교육 이론/질문 패턴은 `references/methodology-framework.md`로 분리해야 500줄 제한을 안정적으로 지킨다.
- 가드레일 증거는 단순 섹션 존재 확인이 아니라 금지 규칙 문구별 grep 결과를 별도 파일(`task-2-guardrails.txt`)로 남겨야 재검증 시 추적성이 높다.
- 소크라틱 튜터 에이전트는 `AskUserQuestion`를 전 턴 루프 진입점으로 명시해야 대화형 UX 요구사항을 충족한다.
- 세션 운영 규칙(최대 15회, 5연속 우수 조기 종료, 사용자 종료 키워드)은 Workflow 본문과 종료 조건 섹션 양쪽에 명시할수록 누락 가능성이 줄어든다.
- 세션 로그는 종료 시 일괄 기록이 아니라 매 교환 직후 즉시 기록임을 문구로 못박아야 검증 grep에서 안정적으로 확인된다.
- 오케스트레이터 커맨드는 frontmatter 없이 시작해야 하며, 첫 줄에 커맨드 제목을 두면 검증 시 혼동이 줄어든다.
- Phase 2 병렬 조건은 ASCII 다이어그램/상세 절차/MUST NOT DO에 중복 명시해야 순차 실행 오해를 줄일 수 있다.
- auto_mode 처리(튜터링 skip)는 파라미터 표와 Phase 4 조건 분기 둘 다에 넣어야 누락 방지에 효과적이다.
- 에이전트 호출 증거 파일은 `subagent_type.*accelerated-learner` 카운트 + 개별 에이전트 grep을 한 파일로 저장하면 회귀 점검이 빠르다.
- README/AGENTS의 플러그인 소개는 본문 섹션 + 프로젝트 구조 + 변경 이력까지 함께 갱신해야 버전 동기화 검증이 단순해진다.

- 2026-03-30 audit: accelerated-learner satisfies 5-stage pipeline, AskUserQuestion-based tutoring, sessions/session-N.md logging, auto_mode skip, Korean-only outputs, and no root-level scripts/references/assets.
