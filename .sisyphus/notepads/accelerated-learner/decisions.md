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
