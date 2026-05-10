---
name: deep-interview
description: 한국어 심층 인터뷰로 모호한 요구사항을 실행 가능한 명세로 변환합니다. 다음과 같은 경우 사용 — '인터뷰해줘', '심층 인터뷰', '전부 다 물어봐줘', '가정하지 마' 같은 요청, 막연하거나 수용 기준이 불명확한 작업, ralph/team/plan/autopilot 워크플로우 전 명확화 필요 시. 5개 불리언 게이트(non-goals/decision-boundaries/pressure-pass/closure-audit/contradiction-audit) + 가중치 기반 모호성 게이팅 + 7단계 상태 머신 + 4개 한국어 도메인 렌즈(기술/UI-UX/위험/트레이드오프) 적용. omo와 표준 Claude Code 양 환경 호환. 결과는 .claude/plans/interview-{slug}-{ts}.md 명세로 결정화.
license: MIT
---

<!--
Adapted from: Yeachan-Heo/oh-my-codex skills/deep-interview/SKILL.md
Pinned commit: 09d6fd05cd10e66eca1e1a9e3e50d60ca4d94362 (main as of 2026-05-10)
License: MIT
Substantive changes: see ../../NOTICE.md for full attribution and change list.
-->

<Purpose>
이 스킬은 사용자의 모호한 아이디어를 실행 가능한 명세로 바꾸는 **의도-우선 소크라틱 명확화 루프**입니다. 무엇을 하고자 하는지(intent), 어디까지 갈지(scope), 무엇은 명시적으로 제외할지(non-goals), 그리고 에이전트가 사용자 확인 없이 결정해도 되는 영역(decision boundaries)을 체계적으로 묻습니다. 산출물은 ralph / team / autopilot / plan 등 후속 워크플로우가 그대로 사용할 수 있는 명세입니다.
</Purpose>

<Use_When>
- 요청이 막연하거나 구체적인 수용 기준이 누락된 경우
- 사용자가 "심층 인터뷰", "인터뷰해줘", "전부 다 물어봐줘", "가정하지 마", "인터뷰부터" 등으로 명시적 요청
- 요구사항이 부정확해 후속 구현이 어긋날 위험이 있는 경우
- ralph / autopilot / team / plan 핸드오프 전에 요구사항 산출물이 필요한 경우
</Use_When>

<Do_Not_Use_When>
- 요청에 이미 구체적 파일/심볼 타깃과 명확한 수용 기준이 있는 경우
- 사용자가 명시적으로 계획/인터뷰를 건너뛰고 즉시 실행하라고 요청한 경우
- 가벼운 브레인스토밍만 원하는 경우 (`plan` 모드 사용)
- 완성된 PRD/계획이 이미 존재하고 실행만 시작하면 되는 경우
- **호출 컨텍스트가 서브에이전트일 때** (Task / 백그라운드 / team worker) — 사용자에게 직접 질문 불가. 부모/리드에게 미해결 질문을 반환하고 부모/리드가 이 스킬을 직접 호출하도록 요청
</Do_Not_Use_When>

---

## 깊이 프로파일

| 플래그 | 임계값 (`ambiguity ≤`) | 최대 라운드 | 용도 |
|---|---:|---:|---|
| `--quick` | 0.30 | 5 | 가벼운 사전 PRD; 위험 수용 가능 |
| `--standard` (기본값) | 0.20 | 12 | 일반 요구사항 인터뷰 |
| `--deep` | 0.15 | 20 | 고난이도/고위험; 정밀 명세 필요 |

플래그 미지정 시 `--standard`. 명령어 진입점은 `commands/interview.md` 참조.

---

## Question Primitive — Try-Then-Fall-Back

질문 도구는 **시도-후-폴백 지시 패턴**으로 처리합니다 (런타임 도구 탐지가 아니라 **지시 패턴**입니다).

```
1. AskUserQuestion 1회 시도
2. 실패 / 도구 미가용 / 빈 응답 시 → 즉시 평문 질문으로 폴백
3. 평문 폴백: 사용자의 다음 대화 턴 = 답변
4. 절대 동일 도구를 재시도하지 마라. 폴백은 1회 결정.
```

| 환경 | 우선 도구 | 폴백 |
|---|---|---|
| 표준 Claude Code 메인 세션 | `AskUserQuestion` | 평문 질문 |
| omo / opencode 메인 세션 | `question` / `ask_user_question` / `askuserquestion` | 평문 질문 |
| oh-my-codex tmux 세션 | (이 스킬은 OMX 전용 도구를 사용하지 않음) | 평문 질문 |
| 서브에이전트 / 백그라운드 / team worker | (질문 차단됨) | 부모/리드에 미해결 질문 반환 |

**라운드당 정확히 1개 질문**. AskUserQuestion 사용 시에도 `questions[]`에 1개만 (배칭 금지).

### AskUserQuestion 옵션 규칙

- 옵션 2-4개 + "직접 설명" 탈출구 추가
- `header` ≤ 12 graphemes (한글 음절 1개 = 1 grapheme; "아키텍처" = 4 graphemes)
- `label` ≤ 30 graphemes; `description` ≤ 100 graphemes

옵션 패턴 예시:

```
question: "인증 방식으로 어떤 것을 선호하시나요?"
header: "인증 방식"
options:
  - label: "세션 기반"
    description: "서버에 세션 저장, 전통적이고 안정적"
  - label: "JWT 토큰"
    description: "토큰 기반, 확장성 좋음, 상태 비저장"
  - label: "OAuth 연동"
    description: "소셜 로그인 (Google, GitHub 등)"
  - label: "직접 설명"
    description: "다른 방식 제안"
```

---

## 7-State Machine

상태 정의와 전환 규칙은 모두 **트랜스크립트로부터 검증 가능**해야 합니다. 외부 상태 API에 의존하지 않습니다 (`state_write` 등 OMX 전용 호출 없음).

### S1 — Preflight Context (사전 컨텍스트)
- **진입**: 인터뷰 호출 시점
- **행동**: 요청 파싱, 프로파일 플래그 감지, greenfield/brownfield 판별, 컨텍스트 oversized 확인
- **Oversized 처리**: 초기 컨텍스트가 토큰 예산을 위협하면 첫 질문은 **요약 요청만**. 요약이 기록되기 전까지 다른 어떤 단계도 진행하지 않음 (블로킹 게이트)
- **전환**: 컨텍스트 prompt-safe → S2

### S2 — Initialize State (초기화)
- **행동**: slug + timestamp 생성 → `.claude/plans/interview-{slug}-{ts}.md` 트랜스크립트 경로 결정. 프로파일 임계값/최대 라운드/빈 dimension 버킷/빈 게이트 boolean 초기화. (선택) JSON 사이드카 작성. 자세한 스키마: `references/state-schema.md`
- **전환**: 초기화 완료 → S3
- **Slug 파생**: 사용자 입력 lowercase + ASCII 음역. 한글 음역 실패 시 SHA-1 8자 폴백.

### S3 — Interview Round (인터뷰 라운드)
- **행동**: **인라인 매트릭스 분류 체계**로 row(차원) 1개 + column(렌즈) 1개 선택 → 사용자에게 정확히 1개 질문. AskUserQuestion 시도 → 폴백
- **전환**: 답변 수신 → S4
- **불변식**: **메인 세션/사용자-가용 컨텍스트에서만 실행**. 서브에이전트는 사용자에게 질문할 수 없음 — `<Do_Not_Use_When>` 참조

### S4 — Score and Gate Update (채점 + 게이트 갱신)
- **행동**: 답변을 트랜스크립트에 추가 (`[from-user]` / `[from-code]` / `[from-research]` 라벨링), 핵심 주장에 source label 부여, 버킷 갱신 (아래 [버킷 조회표](#버킷-조회표) 사용), `ambiguity` 재계산, 5개 불리언 게이트 갱신, contradiction audit 갱신
- **전환**:
  - 압력 패스 미완료 + 직전에 검토할 만한 핵심 주장 존재 → S5
  - 게이트 통과 + 임계값 도달 (또는 하드 캡 / 사용자 종료) → S6
  - 그 외 → S3 (다음 라운드)

### S5 — Pressure Pass (압력 패스)
- **행동**: 이전 라운드의 핵심 주장 1개를 다시 꺼내 [압력 사다리](#압력-사다리)로 검토 (증거 / 가정 / 경계 / 근본 원인). 결과는 트랜스크립트에 명시 기록 (원본 주장 + 압력 질문 + 결과 변경/확인/잔존 위험)
- **전환**: 답변 후 → S4. 한 번의 인터뷰에서 **최소 1회 압력 패스** 통과해야 S6로 갈 수 있음

### S6 — Closure Audit (종결 감사)
- **행동**: 미해결 미지수를 열거 + `blocking` / `accepted-risk` / `non-material` 분류. Contradiction audit 수행
- **전환**:
  - `blocking` 잔존 + 라운드 캡 미달 → S3
  - 모순 미해결 + 우선순위 규칙 없음 → S3
  - 사용자 조기 종료 / 하드 캡 → S7 (잔존 위험 라벨 포함)
  - 모든 게이트 통과 → S7

### S7 — Crystallize (결정화)
- **행동**: `.claude/plans/interview-{slug}-{ts}.md`에 **최종 명세** 작성 (트랜스크립트 + 결정 사항 + 잔존 위험). (선택) JSON 사이드카 갱신 (원자적 rename 패턴, `references/state-schema.md` G3 가드)
- **출력 섹션**: 메타데이터 / 의도 / 원하는 결과 / 범위 / 비목표 / 결정 경계 / 제약 / 수용 기준 / 노출된 가정 / 압력 패스 결과 / 잔존 위험 / 트랜스크립트
- **명세는 불변(immutable)**. 후속 변경은 새 revision 발행 (`v_{n+1}`)
- **종료 후**: `references/handoff-contracts.md`의 5개 옵션 중 사용자 선택 (기본값: `plan-only`)
- **터미널 상태** — 인터뷰 종료

---

## 버킷 조회표

deep-interview 원본의 decimal self-scoring을 **5단계 ordinal 버킷**으로 대체합니다. LLM이 0.73 같은 가짜 정밀도를 만드는 것을 방지하면서 가중치 공식의 단조성을 보존합니다.

| 버킷 | 값 | 트랜스크립트 증거 요건 | 가중치 공식 입력 |
|---|---:|---|---:|
| Absent | 0.00 | 차원에 대한 명시적 증거 없음 | 0.00 |
| Hinted | 0.25 | 언급/유추 가능, 사용자/소스 직접 확인 없음 | 0.25 |
| Stated | 0.50 | 명시적 진술, 단 예시/경계/증거/압력 검증 부재 | 0.50 |
| Anchored | 0.75 | 명시적 + 구체 예시/경계/수용 신호/코드·연구 인용; 미해결 모순 없음 | 0.75 |
| Validated | 1.00 | Anchored + 압력 검증 또는 독립 확인됨; 모순 해결 | 1.00 |

### Anti-gaming Caps (게임 방지 상한)

| 조건 | 최대 버킷 |
|---|---:|
| 트랜스크립트/소스 인용 없음 | 0.25 |
| 사용자 판단 항목인데 사용자 확인이나 결정 경계 없음 | 0.25 |
| 명시적이지만 내부 모순 | 0.50 |
| Brownfield 컨텍스트 주장인데 코드/연구 증거 없음 | 0.50 |
| 답변이 장황하지만 경계/예시/수용 기준 부재 | 0.50 |

### 가중치 공식 (deep-interview 원본 보존)

**Greenfield**:
```
ambiguity = 1 − (intent×0.30 + outcome×0.25 + scope×0.20 + constraints×0.15 + success×0.10)
```

**Brownfield**:
```
ambiguity = 1 − (intent×0.25 + outcome×0.20 + scope×0.20 + constraints×0.15 + success×0.10 + context×0.10)
```

가중치 합 = 1.0 (수학적 단조성 보장). 입력은 버킷 값 `{0, 0.25, 0.50, 0.75, 1.0}`만 허용. 출력 `ambiguity`는 진행도 표시용; **단독으로 핸드오프를 결정하지 못함** (불리언 게이트가 우선).

---

## 5개 불리언 Readiness 게이트

각 게이트는 트랜스크립트로부터 **결정적으로** 검증 가능해야 합니다. 게이트는 가중치 공식보다 **사전적(lexicographic)으로 우선**합니다 — 게이트가 통과하지 않으면 ambiguity 점수와 무관하게 핸드오프 불가.

| 게이트 | 통과 조건 (Boolean predicate) | 버킷 관련성 |
|---|---|---|
| `non_goals_explicit` | 트랜스크립트에 out-of-scope 항목 명시 OR 사용자가 "추가 비목표 없음" 명시적 확인 + 광범위 경고 | `non_goals` 버킷 ≥ 0.75 요구; Scope 버킷도 영향 |
| `decision_boundaries_explicit` | 트랜스크립트가 "에이전트가 결정 가능"과 "사용자에게 먼저 묻기"를 분리 기재 | `decision_boundaries` 버킷 ≥ 0.75 요구; 가중치 없음 |
| `pressure_pass_complete` | 원본 주장 + 압력 질문 + 결과(변경/확인/잔존 위험) 모두 기록 | 가중치 없음 |
| `closure_audit_pass` | 미해결 미지수가 모두 `blocking`/`accepted-risk`/`non-material`로 분류; `blocking` 0건 | 가중치 없음 |
| `contradiction_audit_pass` | 수용된 요구사항 간 미해결 충돌 없음 OR 우선순위 규칙으로 해결 | 미해결 시 영향 받는 차원 ≤ 0.50 캡 |

---

## 핸드오프 조회표

| 조건 | 결과 |
|---|---|
| 어떤 게이트라도 false + 하드 캡/사용자 종료 없음 | 인터뷰 계속 |
| `ambiguity > threshold` + 하드 캡/사용자 종료 없음 | 인터뷰 계속 |
| 하드 캡 / 사용자 조기 종료 (게이트 부분 통과) | 잔존 위험 라벨링 후 부분 명세 작성. 자동 실행 금지 |
| 게이트 모두 true + 임계값 통과 + 모든 차원 ≥ 0.50 | S7 결정화. 계획 핸드오프 허용 |
| 게이트 모두 true + Standard 임계값 + intent/outcome/scope 각 ≥ 0.75 + blocking 0 | 명시적 승인 후 실행 가능 |
| 게이트 모두 true + Deep 임계값 + 모든 가중치 차원 ≥ 0.75 + contradiction audit 통과 | 고신뢰 실행/계획 핸드오프 허용 (명시적 승인 후) |
| Quick 프로파일 통과 | 경량 계획 핸드오프; 핵심 차원 < 0.75인 경우 실행은 명시적 위험 수용 후 |

---

## 인라인 매트릭스 분류 체계

deep-interview의 **클러리티 차원(rows)** × 원본 interview agent의 **한국어 도메인 렌즈(columns)**.

### 행 (Rows) — 클러리티 차원

| 차원 | 가중치 (greenfield) | 가중치 (brownfield) | 게이트 영향 |
|---|---:|---:|---|
| `intent` | 0.30 | 0.25 | — |
| `outcome` | 0.25 | 0.20 | — |
| `scope` | 0.20 | 0.20 | non_goals 게이트와 연계 |
| `constraints` | 0.15 | 0.15 | — |
| `success` | 0.10 | 0.10 | — |
| `context` | — | 0.10 | brownfield 전용 |
| `non_goals` | (게이트만) | (게이트만) | `non_goals_explicit` |
| `decision_boundaries` | (게이트만) | (게이트만) | `decision_boundaries_explicit` |

### 열 (Columns) — 한국어 도메인 렌즈

1. **기술 구현** (Technical Implementation)
2. **UI/UX** (User Experience) — UI 없는 작업에서 스킵 가능
3. **우려사항** (Concerns & Risks)
4. **트레이드오프** (Tradeoffs)

상세 질문 패턴: `references/question-banks-ko.md` (24개 질문, 각 도메인 6개 질문 유형 × 4개 lens). 각 차원 → lens 매핑 우선순위 표도 동일 파일.

### 셀 선택 알고리즘 (per-cell scoring 아님)

```
1. 행 선택 (priority ordering):
   a. Oversized initial-context summary 게이트가 미해결이면 → 그 게이트만 추구
   b. 다른 mandatory 게이트가 미해결이면 → 해당 게이트의 차원 (non_goals / decision_boundaries / 압력 패스)
   c. 단계 우선순위:
      Stage 1: intent / outcome / scope / non_goals / decision_boundaries
      Stage 2: constraints / success
      Stage 3 (brownfield only): context
   d. 활성 단계 내에서 → 가장 낮은 버킷 차원
   e. 동률이면 → 가중치 큰 순서, 그래도 동률이면 위 차원 순서

2. 열 선택 (applicability lookup, scoring 아님):
   - `references/question-banks-ko.md`의 "도메인 렌즈 적용 가능성 표"에서 선택된 row의 1순위 lens 사용
   - 1순위 lens 적용 불가 (예: UI 없음) → 2순위 lens 폴백
```

---

## 압력 사다리 (Pressure Ladder)

각 답변 후 다음 사다리에서 1단계를 추구. 충분히 검증 전까지 같은 thread를 유지 (단순히 다음 차원으로 회전하지 않음).

1. **증거** — "이 주장의 근거가 되는 구체 예시, 반례, 또는 코드/연구 인용은?"
2. **가정** — "이 주장이 참이라고 만드는 숨은 가정/의존/믿음은?"
3. **경계/트레이드오프** — "명시적으로 하지 않을 일, 미루거나 거부할 일은?"
4. **근본 원인** — (답변이 여전히 증상을 묘사하면) "본질/근본 원인 차원으로 재구성"

---

## 챌린지 모드

각 모드는 **결정적 트리거 + 트랜스크립트 delta**가 있어야 인정됩니다. 한 인터뷰에서 동일 모드 1회만 사용 (`challenge_modes_used` 추적).

| 모드 | 트리거 | 출력 |
|---|---|---|
| **Contrarian** | 라운드 2+ OR 답변이 **검증 안 된 가정**에 의존 | 트랜스크립트에 가정 + 위험 + 해결 기록 |
| **Simplifier** | 라운드 4+ OR 결과 명확성보다 **범위 확장이 더 빠를 때** | MVP 경계 / non-goal 추가 |
| **Ontologist** | 라운드 5+ AND `ambiguity > 0.25` OR 사용자가 **계속 증상으로만 묘사**할 때 | 본질-차원 재구성, 근본 목표/최종 상태 구분 |

각 모드 사용 시 트랜스크립트에 `[challenge:contrarian]` / `[challenge:simplifier]` / `[challenge:ontologist]` 마커.

---

## Source Labels (Provenance Audit)

모든 핵심 주장에 source label을 부여합니다. Iconoclast의 Evidence Ratio를 보완적 audit으로 통합 (대체 아님).

| 라벨 | 의미 |
|---|---|
| `[from-user]` | 사용자가 직접 답변/판단 |
| `[from-code]` | 코드베이스에서 발견 (Glob/Grep/Read로 확인) |
| `[from-code][auto-confirmed]` | 코드 발견 사실에 대해 사용자가 묵시적/명시적 확인 |
| `[from-research]` | 외부 문서/웹/librarian에서 발견 |

### Provenance Audit 술어 (보완적, 대체 아님)

- `fact_coverage = supported(F) / max(1, |F|)` — 코드/연구 사실 중 인용된 비율
- `judgment_coverage = supported(J) / max(1, |J|)` — 사용자 판단 중 `[from-user]` 또는 결정 경계 내인 비율
- `unresolved_inference_count = |I_material_unconfirmed|` — 미확인 핵심 추론 수

핸드오프 요건:
- **Brownfield 실행**: 모든 핵심 코드/컨텍스트 주장이 인용되거나 확인 필요로 마킹
- **실행 핸드오프**: `unresolved_inference_count = 0` (핵심 주장에 대해)
- **사용자 의도/범위/트레이드오프 주장**: `[from-user]` 라벨 필수, 또는 명시적 결정 경계 안에 있어야 함

---

## Dialectic Rhythm Guard

연속 비-사용자 답변(`[from-code]`, `[from-code][auto-confirmed]`, `[from-research]`)을 추적합니다. **3회 연속** 비-사용자 답변 후, 다음 사용자-대면 라운드는 반드시 직접 사용자 판단(`[from-user]`)을 요청해야 합니다 — closure audit이 결정화 준비됨을 표시하지 않는 한.

이 가드는 인터뷰가 사실 발견에만 빠져 사용자 의도를 잃는 것을 방지합니다.

---

## 라운드 컨트롤

- 첫 명시적 가정 검증 + 1회 압력 follow-up 전에는 조기 종료 옵션을 제시하지 않음
- 라운드 4+: 위험 경고와 함께 명시적 조기 종료 허용
- 프로파일 중간점 (라운드 3/6/10)에서 soft 경고
- 프로파일 `max_rounds`에서 hard cap

---

## 결정화 산출물 (Crystallize Spec)

S7에서 작성하는 `.claude/plans/interview-{slug}-{ts}.md` 구조:

```markdown
# {요청 제목} 명세

## 메타데이터
- 인터뷰 ID: {uuid}
- 프로파일: quick | standard | deep
- 타입: greenfield | brownfield
- 시작/종료 시각
- 최종 ambiguity (참고용)
- 임계값 (참고용)
- 라운드 수 / 최대 라운드
- 도전 모드 사용 이력

## 의도 (Intent)
사용자가 왜 이것을 원하는가

## 원하는 결과 (Desired Outcome)

## 범위 (In-Scope)

## 비목표 (Out-of-Scope / Non-goals)

## 결정 경계 (Decision Boundaries)
| 에이전트가 결정 가능 | 사용자에게 먼저 묻기 |
|---|---|
| ... | ... |

## 제약 (Constraints)

## 수용 기준 (Testable Acceptance Criteria)

## 노출된 가정 (Exposed Assumptions) + 해결

## 압력 패스 결과 (Pressure Pass Findings)
- 원본 주장: ...
- 압력 질문: ...
- 결과: 변경/확인/잔존 위험

## Source Labels Audit
- fact_coverage: X.XX
- judgment_coverage: X.XX
- unresolved_inference_count: 0

## Brownfield 증거 vs 추론 (해당 시)

## 잔존 위험 (Residual Risks) — 하드 캡/조기 종료 시

## 트랜스크립트 (전체 또는 압축)
```

명세는 **불변(immutable)**. 후속 변경은 새 revision 발행. 자세한 핸드오프 옵션: `references/handoff-contracts.md`.

---

## 환경 호환성 요약

이 스킬은 **양 환경**에서 동일한 파일로 동작합니다:

| 항목 | 표준 Claude Code | omo / oh-my-openagent |
|---|---|---|
| 프론트매터 (`name`, `description`, `license`) | ✅ Agent Skills 스펙 준수 | ✅ 동일 스펙 + 추가 필드 무시 가능 |
| 질문 도구 | `AskUserQuestion` (메인 세션) | `question` / `ask_user_question` / `askuserquestion` (메인) |
| 폴백 | 평문 질문 → 다음 사용자 턴 | 동일 |
| 서브에이전트 / 백그라운드 | 차단됨 (질문 불가) — 부모/리드에 반환 | 동일 |
| 상태 저장 | 파일시스템 (`.claude/plans/`) | 동일 |
| 핸드오프 | `Task(subagent_type=...)` 또는 다른 에이전트 | `task(category=..., load_skills=...)` 또는 다른 에이전트 |
| OMX 전용 (`state_write`, `omx question`, `.omx/*`, `$ralplan`...) | ❌ 사용 안 함 | ❌ 사용 안 함 |

---

## 참고 파일

- **명령어 진입점**: `commands/interview.md`
- **상태 사이드카 스키마**: `references/state-schema.md`
- **5개 핸드오프 옵션**: `references/handoff-contracts.md`
- **24개 한국어 질문 은행**: `references/question-banks-ko.md`
- **라이선스/저작자 표시**: `../../NOTICE.md`
- **하위 호환 래퍼 에이전트**: `../../agents/interview.md` (기존 `@general-agents 의 interview` 호출 보존)

---

## 사용자 환경 .gitignore 권장사항

이 스킬은 사용자 프로젝트의 `.claude/plans/`에 산출물을 작성합니다. 다음을 사용자 프로젝트의 `.gitignore`에 추가할 것을 **권장**합니다 (이 honeypot 저장소 자체에는 이미 `.claude/` 전체가 무시 처리됨):

```gitignore
# deep-interview 런타임 캐시 (트랜스크립트 .md로부터 재구성 가능)
.claude/plans/*.state.json
```

트랜스크립트 `.md` 자체는 팀과 공유할 가치가 있을 수 있어 무시하지 않습니다.
