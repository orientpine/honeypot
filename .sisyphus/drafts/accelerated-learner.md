# Draft: accelerated-learner 플러그인

## Requirements (confirmed)
- **플러그인 이름**: accelerated-learner
- **언어**: 한국어 전용 (에이전트 프롬프트, 출력물 모두)
- **소스 자료**: 폴더 경로 + 개별 파일 모두 지원 (PDF, MD, TXT 등)
- **출력 형태**: 마크다운 지식 베이스 (구조화된 MD 파일들)
- **튜터링 방식**: 대화형 (질문 하나씩 → 답변 → 피드백)
- **진도 추적**: 세션별 기록 (session-log.md)

## 핵심 철학
> "한 학기와 48시간의 차이는 콘텐츠의 양이 아니라, 어떤 질문을 던져야 하는지를 아는 것"

MIT 대학원생의 NotebookLM 활용 방법론:
1. 대량의 소스 자료 업로드 (교재 6권, 논문 15편, 강의 스크립트)
2. "이 분야의 모든 전문가가 공유하는 핵심 멘탈 모델 5가지" 추출
3. "전문가들이 근본적으로 의견이 갈리는 세 가지 지점" 매핑
4. "깊이 이해한 사람과 단순 암기한 사람을 구별하는 질문 10가지" 생성
5. 6시간 동안 질문에 직접 답변 + 오답 피드백
6. 결과: 지도교수와 대화 가능한 수준

## Technical Decisions
- **아키텍처**: 5 에이전트 + 1 커맨드(오케스트레이터) + 1 스킬
- **통신**: 파일 기반 (JSON/MD 체인)
- **병렬화**: source-synthesizer 완료 후 mental-model-extractor + controversy-mapper 병렬 실행 가능
- **에이전트 모델**: sonnet (분석/추론 중심), 튜터는 opus (정교한 대화)

## 에이전트 구성
1. `source-synthesizer.md` - 소스 자료 읽기 + 종합 분석문 생성
2. `mental-model-extractor.md` - 핵심 멘탈 모델 5가지 추출
3. `controversy-mapper.md` - 전문가 의견 불일치 지점 매핑
4. `question-architect.md` - 판별 질문 10가지 생성
5. `socratic-tutor.md` - 대화형 소크라틱 튜터링 + 세션 기록

## 커맨드
- `accelerated-learn.md` - 전체 워크플로우 오케스트레이터

## 스킬
- `learning-methodology/SKILL.md` - 학습 방법론, 블룸 분류체계, 소크라틱 메서드

## 출력 구조
```
output/{subject-name}/
├── 00-source-synthesis.md
├── 01-mental-models.md
├── 02-controversies.md
├── 03-discriminating-questions.md
├── 04-session-log.md
└── 05-mastery-summary.md
```

## Scope Boundaries
- INCLUDE: 소스 분석, 멘탈모델 추출, 논쟁 매핑, 판별 질문, 소크라틱 튜터링, 세션 기록
- EXCLUDE: PDF 변환 스크립트 (기존 패턴 활용), NotebookLM 연동, 음성/영상 처리

## Research Findings
- 기존 플러그인 패턴: isd-generator, report-generator, paper-style-generator 분석 완료
- 인터랙션 패턴: AskUserQuestion 기반 다회전 대화, 조건부 흐름
- 파일 처리: 외부 스크립트 기반 (자체 코드 작성 금지)
- 진행 보고: 단계별 상태 보고 패턴
