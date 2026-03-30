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
