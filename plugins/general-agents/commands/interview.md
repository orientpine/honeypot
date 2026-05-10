# interview

심층 인터뷰 슬래시 명령어 — `deep-interview` 스킬을 메인 세션에서 직접 호출하여 모호한 요구사항을 실행 가능한 명세로 변환합니다.

## 사용법

```
/general-agents:interview [--quick|--standard|--deep] <초기 아이디어/주제>
```

### 깊이 프로파일

| 플래그 | 임계값 (ambiguity ≤) | 최대 라운드 | 용도 |
|---|---:|---:|---|
| `--quick` | 0.30 | 5 | 가벼운 사전 PRD; 경계 위험 수용 가능 |
| `--standard` (default) | 0.20 | 12 | 일반 요구사항 인터뷰 |
| `--deep` | 0.15 | 20 | 고난이도 / 고위험 / 핸드오프 직전 정밀 명세 |

플래그가 없으면 `--standard`를 사용합니다.

## 동작

1. `$ARGUMENTS`에서 깊이 플래그를 파싱하고, 나머지를 초기 주제로 사용
2. `deep-interview` 스킬 활성화 (자동 로딩 또는 컨텍스트 주입)
3. 메인 세션(현재 사용자와의 대화 컨텍스트)에서 7-단계 인터뷰 상태 머신 실행:
   - S1 사전 컨텍스트 → S2 초기화 → S3 인터뷰 라운드 → S4 채점 + 게이트 → S5 압력 패스 → S6 종결 감사 → S7 결정화
4. 결과 명세를 `.claude/plans/interview-{slug}-{ts}.md`에 작성
5. 5가지 핸드오프 옵션 제시 (계획만 / 더 논의 / 실행 / 다른 에이전트 / 종료)

## 환경 호환성

- **표준 Claude Code**: `AskUserQuestion` 도구 사용
- **omo (oh-my-openagent) / opencode**: `question` / `ask_user_question` / `askuserquestion` 도구 가용 시 사용
- **양쪽 모두 미가용 시**: 평문 질문 + 사용자의 다음 턴 = 답변

도구 가용성은 시도-후-폴백 패턴으로 처리됩니다 (`SKILL.md` "Question Primitive Try-Then-Fall-Back" 섹션 참조).

## 호출 제약

- **반드시 메인 세션 / 최상위 / 팀 리드** 컨텍스트에서 실행. 서브에이전트 (Task / 백그라운드 / team worker)는 사용자에게 직접 질문 불가 — 인터뷰가 차단됩니다.
- 호출 컨텍스트가 서브에이전트라면 미해결 질문을 부모/리드에게 반환하고 부모/리드가 이 명령어를 실행하도록 요청하세요.

## 예시

```
/general-agents:interview --quick 결제 모듈에 PG사 추가해줘
```
```
/general-agents:interview --deep 사내 LLM 게이트웨이를 별도 서비스로 분리할까 검토해줘
```
```
/general-agents:interview 새 알림 시스템 설계
```
(마지막은 `--standard` 적용)

## 참고

- 인터뷰 방법론 전체: `plugins/general-agents/skills/deep-interview/SKILL.md`
- 명세 JSON 스키마: `plugins/general-agents/skills/deep-interview/references/state-schema.md`
- 핸드오프 계약: `plugins/general-agents/skills/deep-interview/references/handoff-contracts.md`
- 24개 한국어 질문 은행: `plugins/general-agents/skills/deep-interview/references/question-banks-ko.md`
- 라이선스/저작자 표시: `plugins/general-agents/NOTICE.md`

## 하위 호환

기존 `@general-agents 의 interview` 호출 패턴은 그대로 동작합니다 (래퍼 에이전트가 동일 스킬을 로드). 단, v2.0.0부터 기본 동작이 **계획-only**로 변경되었으며, 실행은 인터뷰 종료 시 명시적 옵트인을 통해서만 시작됩니다.
