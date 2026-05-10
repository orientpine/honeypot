# Handoff Contracts — `deep-interview` 종료 후 다음 단계

`SKILL.md`의 단계 S7 (Crystallize)이 완료되면, 이 파일에 정의된 5개 핸드오프 옵션을 사용자에게 제시합니다. 원본 `deep-interview` 스킬의 OMX 전용 핸드오프(`$ralplan`, `$autopilot`, `$ralph`, `$team`, `$ultragoal`, `$autoresearch-goal`, `$performance-goal`)는 표준 Claude Code 환경에 존재하지 않으므로, 양 환경(omo + 표준 Claude Code)에서 모두 가용한 패턴으로 대체합니다.

## 결정화 직후 사용자 질의

```
질문: "인터뷰가 완료되었습니다. 다음 단계를 선택해 주세요."
header: "다음 단계"
options:
  - label: "계획만 작성하고 종료"
    description: "기본 안전 옵션. 계획 문서를 검토 후 별도 워크플로우로 실행"
  - label: "특정 영역 더 논의"
    description: "잔존 모호성 해소 또는 결정 경계 재확인"
  - label: "계획 작성 후 직접 실행"
    description: "옵트인 실행. 컨텍스트 손실 위험 안내 후 진행"
  - label: "다른 에이전트로 핸드오프"
    description: "전문 에이전트(예: 구현/리뷰 에이전트)에게 명세 전달"
  - label: "종료 + 잔존 위험 메모"
    description: "낮은 명확성으로 마감, 위험 명시 + 재개 가능"
```

위 5개 옵션은 영문 키 `plan-only` / `refine-further` / `execute` / `delegate-handoff` / `terminate-with-risks`로 매핑됩니다 (트랜스크립트/사이드카 기록용).

---

## 옵션 1 — `plan-only` — 계획만 작성하고 종료

### Input Artifact
`.claude/plans/interview-{slug}-{ts}.md` (결정화된 명세)

### Invocation
없음. 인터뷰 에이전트가 명세를 마지막 메시지로 출력하고 종료.

### Skipped / Already-satisfied stages
- 요구사항 명확화 (완료됨)
- 모호성 게이팅 (통과 또는 명시적 잔존 위험 수용)

### Expected output
- 사용자가 명세를 검토 후 별도로 실행 결정
- 명세는 다른 사람/에이전트가 재사용 가능한 자기충족적 산출물

### Best when
- 사용자가 직접 검토하고 수동으로 다음 단계 결정하려 할 때
- 명세를 다른 팀원/에이전트에게 전달하고 싶을 때
- 즉시 구현 시작이 위험할 때 (인터뷰 컨텍스트 소모 큼)

### Next recommended step
- 사용자 검토 후 옵션 3 (직접 실행) 또는 옵션 4 (위임) 중 선택

### Default ✓
이 옵션이 기본값입니다. 사용자가 명시적으로 다른 옵션을 선택하지 않는 한 `plan-only`로 처리.

---

## 옵션 2 — `refine-further` — 특정 영역 더 논의

### Input Artifact
현재 트랜스크립트 + 사이드카 (`.claude/plans/interview-{slug}-{ts}.{md,state.json}`)

### Invocation
인터뷰 루프 재진입. 새 인터뷰가 아닌 **기존 인터뷰 재개**.

### Skipped / Already-satisfied stages
- S1 사전 컨텍스트 (재사용)
- 이미 captured 된 차원/게이트 상태 (재사용; 갱신만)

### Expected output
- 더 낮은 모호성을 가진 갱신된 명세
- 추가 결정 경계, 비목표(non-goals), 또는 압력 패스 결과 추가

### Best when
- 잔존 모호성이 여전히 너무 높을 때
- 위 임계값 / 조기 종료 경고가 너무 큰 위험을 시사할 때
- 사용자가 더 강한 명확성을 원할 때

### Next recommended step
- 명확성 충분 시 옵션 1, 3, 또는 4 중 하나로 이동

---

## 옵션 3 — `execute` — 계획 작성 후 직접 실행

### Input Artifact
`.claude/plans/interview-{slug}-{ts}.md` (결정화된 명세, 불변)

### Invocation
**옵트인**. 사용자가 명시적으로 이 옵션을 선택해야 함. 인터뷰 에이전트가 명세 검토 후 구현 단계로 전환:
- 표준 Claude Code: 동일 메인 세션에서 `Read` / `Edit` / `Write` / `Bash` 도구 사용 (단, agent의 tools 화이트리스트가 허용하는 경우만)
- omo / opencode: `task(subagent_type="general", prompt="execute spec at .claude/plans/...")` 또는 `task(category="quick", load_skills=[...])` 위임

### Skipped / Already-satisfied stages
- 모든 인터뷰 단계 (완료)

### Expected output
- 명세에 따른 코드/문서/설정 변경
- 검증 결과 (테스트 통과, 빌드 성공, 등)
- 변경된 파일 목록

### Best when
- 명세가 충분히 명확하고 작은 범위 (1-3 파일)
- 인터뷰가 짧았던 경우 (`--quick` 프로파일)
- 사용자가 즉시 결과를 보고 싶을 때

### Risks (사용자에게 안내)
- 인터뷰가 길었다면 컨텍스트 토큰이 소진된 상태일 수 있음 — LLM 환각 위험
- 명세는 불변(immutable)이지만 구현 중 모호성 발견 시 동기적 "pause-and-clarify" 가능 (새 spec revision 발행)

### Next recommended step
- 실행 결과 검증 후 종료
- 추가 작업 필요 시 새 인터뷰 시작 (`--quick` 권장)

---

## 옵션 4 — `delegate-handoff` — 다른 에이전트로 핸드오프

### Input Artifact
`.claude/plans/interview-{slug}-{ts}.md`

### Invocation
환경에 따라 다음 중 하나:

**표준 Claude Code:**
```
task(
    subagent_type="general",
    prompt="Implement the spec at .claude/plans/interview-{slug}-{ts}.md. The spec contains acceptance criteria, decision boundaries, and out-of-scope items. Do not deviate from these. Report progress after each major file change."
)
```
또는 더 전문화된 서브에이전트 (`oracle`, `librarian` 등) 사용:
```
task(
    subagent_type="oracle",
    prompt="Review the implementation plan in the spec at .claude/plans/interview-{slug}-{ts}.md and identify potential issues before execution begins."
)
```

**omo / opencode:**
```
task(
    category="quick",                    # 또는 ultrabrain / unspecified-high
    load_skills=["git-master"],          # 작업에 적합한 스킬 추가
    prompt="Implement the spec at .claude/plans/interview-{slug}-{ts}.md. Read the entire spec first; treat its acceptance criteria and out-of-scope items as binding constraints.",
    run_in_background=false
)
```

### Skipped / Already-satisfied stages
- 모든 요구사항 도출 단계
- 모호성 게이팅

### Expected output
- 위임받은 에이전트가 명세 기반으로 작업 수행
- 결과는 호출자(인터뷰 에이전트의 사용자)에게 보고

### Best when
- 명세가 길거나 복잡 (`--standard` / `--deep` 프로파일)
- 작업이 특수한 도메인 전문성 요구 (frontend / debugging / architecture)
- 사용자가 인터뷰 컨텍스트를 보존하고 싶을 때 (구현은 별도 컨텍스트에서)

### Risks (사용자에게 안내)
- 위임받은 에이전트는 사용자에게 직접 질문 불가 (`AskUserQuestion` 차단). 명세에 모든 결정이 포함되어 있어야 함.
- 명세에 없는 결정은 위임받은 에이전트가 추론하므로, 핵심 결정 경계가 명시적이어야 함 (gate `decision_boundaries_explicit` 필수).

### Next recommended step
- 위임 결과 검증
- 부분 통과 시 옵션 2 (refine) 또는 새 인터뷰

---

## 옵션 5 — `terminate-with-risks` — 종료 + 잔존 위험 메모

### Input Artifact
`.claude/plans/interview-{slug}-{ts}.md` (잔존 위험 섹션 포함)

### Invocation
인터뷰 강제 종료. 트랜스크립트 마지막에 다음 추가:
```markdown
## ⚠️ 잔존 위험 (Residual Risks)

### 미해결 사항
- [ ] [차원 이름]: [무엇이 명확하지 않은가]
- [ ] [차원 이름]: [무엇이 명확하지 않은가]

### 위반된 게이트
- [ ] non_goals_explicit (이유)
- [ ] decision_boundaries_explicit (이유)

### 권장 후속 조치
- 이 명세를 사용해 직접 실행하지 마십시오
- 옵션 2 (refine) 로 재개하거나 새 인터뷰 시작 권장
```

### Skipped / Already-satisfied stages
- 일부 단계만 완료

### Expected output
- 부분 명세 + 잔존 위험 라벨링
- 다음 호출자(다른 에이전트 / 사용자 본인)가 이 위험을 인지하도록 강제

### Best when
- 사용자가 시간 제약 등으로 조기 종료해야 할 때
- 하드 캡(max_rounds 도달) 시 자동 진입
- 인터뷰 도중 사용자가 외부 정보를 가지고 와야 할 때 (예: "팀과 상의 후 다시 옴")

### Next recommended step
- 사용자가 외부에서 정보 보강 후 옵션 2 (refine)
- 또는 잔존 위험을 수용하고 옵션 3 (execute) 강행 (권장하지 않음)

---

## 핸드오프 결정 트리 (요약)

```
S7 결정화 완료
  ├─ 모든 게이트 통과 + ambiguity ≤ threshold
  │    ├─ 사용자가 즉시 결과 원함 + 작은 범위 → 옵션 3 (execute)
  │    ├─ 작업 복잡 / 도메인 특수 → 옵션 4 (delegate-handoff)
  │    └─ 검토 후 결정 → 옵션 1 (plan-only) ✓ default
  ├─ 일부 게이트 통과 + 잔존 모호성 큼
  │    └─ 옵션 2 (refine-further)
  └─ 하드 캡 / 사용자 조기 종료
       └─ 옵션 5 (terminate-with-risks)
```

## 명세 불변성 (Immutability)

S7에서 결정화된 명세는 **불변(immutable)**입니다. 이는 deep-interview의 핵심 안전 속성입니다:
- 옵션 3 (execute) 도중 모호성 발견 → 새 spec revision (`v_{n+1}`) 발행 후 영향받은 작업 재검증
- 옵션 2 (refine-further) → 기존 명세를 갱신, 단 이전 버전은 트랜스크립트 history로 보존
- 옵션 4 (delegate-handoff) → 위임받은 에이전트는 명세를 단지 읽기만 가능 (override 금지)

이 규칙은 비동기 변경(async mutation) 경쟁 상태를 방지합니다.
