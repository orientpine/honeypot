# decisions.md — accelerated-learner

## 아키텍처 결정사항

- 5단계 파이프라인: source-synthesizer → mental-model-extractor + controversy-mapper (병렬) → question-architect → socratic-tutor
- 출력 파일 명명: 00-source-synthesis.md, 01-mental-models.md, 02-controversies.md, 03-discriminating-questions.md, 04-session-log.md, 05-mastery-summary.md
- 세션 로그: sessions/ 하위 디렉토리 (번호 매김), 매 Q&A 교환 후 즉시 기록
- auto_mode: true 시 socratic-tutor 건너뛰고 지식베이스만 생성
- 마스터리 기준: 정성적 (점수 없음), 최대 15회 상호작용, 5연속 우수 답변 시 조기 종료
- 멘탈모델 수: 2-5개 유연 (강제 5개 금지)
- 논쟁 수: 0-3개 유연, 없으면 "없음" 명시
- 판별 질문 수: 5-10개 유연 (강제 10개 금지)

## 이번 작업 결정

- 실체 구현보다 먼저 디렉토리/메타데이터 등록을 완료해 플러그인 탐색 가능 상태를 확보한다.
- 루트에 `scripts/`, `references/`, `assets/`, `templates/`는 만들지 않는다.
- `skills`는 단일 루트 배열 `['./skills']`로 유지한다.
- `learning-methodology` SKILL.md는 개요/규칙 중심으로 유지하고, 블룸/소크라틱/도메인별 질문 패턴 상세는 references 문서로 분리한다.
- 판별 질문/멘탈모델/논쟁 개수는 모두 유연 범위를 유지(2-5, 0-3, 5-10)하고 강제 채우기 금지를 가드레일에 명시한다.
- `socratic-tutor` frontmatter는 `tools`에 `AskUserQuestion`를 반드시 포함하고 `skills`는 `learning-methodology` 단일 참조로 고정한다.
- 엣지케이스는 두 축(무의미 답변, 주제 이탈)으로 분리하여 처리 규칙(2회 재요청 후 이동 / 재유도 후 이탈 논의 금지)을 명시하기로 결정했다.
- 증거 산출물은 `.sisyphus/evidence/task-7-tutor-design.txt`와 `.sisyphus/evidence/task-7-edge-cases.txt` 두 파일로 분리 저장한다.
- `accelerated-learn` 커맨드는 5개 에이전트를 모두 `Task(subagent_type="accelerated-learner::{agent}")` 형식으로 명시 호출하도록 결정했다.
- Phase 1/2/3/4 모두 산출물 존재 검증 + 실패 시 정확히 1회 재시도 후 중단 규칙을 통일 적용하기로 결정했다.
- 최종 단계에서 `{output_dir}/{subject_name}/` 파일 목록 출력과 완료 메시지를 명시해 운영 가시성을 확보하기로 결정했다.
- 문서 업데이트는 marketplace metadata 버전, AGENTS.md Generated/Version, README.md Version/섹션/변경이력을 한 번에 맞춰야 후속 검증을 한 번에 통과시킬 수 있다.

- 2026-03-30 compliance audit verdict: APPROVE. Interpreted plan line about session-log as satisfied by per-session sessions/session-N.md logs with monotonic numbering and no overwrite.
