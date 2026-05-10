# State Schema — `deep-interview` 사이드카

`SKILL.md` 본문에서 참조되는 JSON 사이드카 명세. 트랜스크립트 `.md`가 권위적이며, 이 사이드카는 **재구성 가능한 캐시**입니다. 사이드카가 손상되거나 누락되어도 트랜스크립트로부터 복원 가능해야 합니다.

## 경로

```
.claude/plans/interview-{slug}-{ts}.md         (트랜스크립트 + 명세, 권위적)
.claude/plans/interview-{slug}-{ts}.state.json  (캐시, 선택적)
```

- `{slug}`: 초기 사용자 입력에서 파생된 lowercase ASCII slug. 한글 → 음역(romanize). 음역 실패 시 짧은 해시(SHA-1 8자) 폴백.
- `{ts}`: ISO 8601 단축 형식 `YYYYMMDD-HHMMSS` (UTC 또는 로컬 — 둘 중 하나로 일관 사용)

## JSON 스키마

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "deep-interview state cache",
  "type": "object",
  "required": [
    "interview_id",
    "version",
    "profile",
    "type",
    "slug",
    "started_at",
    "transcript_path",
    "rounds",
    "dimensions",
    "gates",
    "current_stage"
  ],
  "properties": {
    "interview_id": {
      "type": "string",
      "description": "UUID v4. 충돌 방지용 고유 식별자."
    },
    "version": {
      "type": "string",
      "const": "2.0.0",
      "description": "스키마 버전. 향후 마이그레이션을 위함."
    },
    "profile": {
      "type": "string",
      "enum": ["quick", "standard", "deep"]
    },
    "type": {
      "type": "string",
      "enum": ["greenfield", "brownfield"]
    },
    "slug": { "type": "string" },
    "started_at": {
      "type": "string",
      "format": "date-time"
    },
    "transcript_path": {
      "type": "string",
      "description": "권위적 트랜스크립트 .md 경로. 사이드카 재구성의 원천."
    },
    "rounds": {
      "type": "array",
      "description": "라운드 단위 이벤트 로그.",
      "items": {
        "type": "object",
        "required": ["round_n", "stage", "target_dimension", "domain_lens", "user_claim", "pressure_type", "evidence_obtained", "state_delta"],
        "properties": {
          "round_n": { "type": "integer", "minimum": 1 },
          "stage": { "type": "string", "enum": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"] },
          "target_dimension": {
            "type": "string",
            "enum": ["intent", "outcome", "scope", "constraints", "success", "context", "non_goals", "decision_boundaries"]
          },
          "domain_lens": {
            "type": ["string", "null"],
            "enum": ["technical", "ui_ux", "concerns", "tradeoffs", null]
          },
          "user_claim": { "type": "string" },
          "pressure_type": {
            "type": ["string", "null"],
            "enum": ["evidence", "assumption", "boundary", "root_cause", null]
          },
          "evidence_obtained": { "type": "string" },
          "state_delta": { "type": "string" }
        }
      }
    },
    "dimensions": {
      "type": "object",
      "description": "현재 차원 버킷 값. 키는 차원 이름, 값은 0/0.25/0.50/0.75/1.0.",
      "additionalProperties": {
        "type": "object",
        "required": ["bucket", "evidence_quote", "remaining_gap"],
        "properties": {
          "bucket": {
            "type": "number",
            "enum": [0.0, 0.25, 0.50, 0.75, 1.0]
          },
          "evidence_quote": {
            "type": "string",
            "description": "버킷을 정당화하는 트랜스크립트 인용."
          },
          "remaining_gap": {
            "type": "string",
            "description": "이 차원에서 아직 명확하지 않은 것."
          }
        }
      }
    },
    "gates": {
      "type": "object",
      "description": "5개 불리언 readiness 게이트.",
      "required": [
        "non_goals_explicit",
        "decision_boundaries_explicit",
        "pressure_pass_complete",
        "closure_audit_pass",
        "contradiction_audit_pass"
      ],
      "properties": {
        "non_goals_explicit":         { "type": "boolean" },
        "decision_boundaries_explicit": { "type": "boolean" },
        "pressure_pass_complete":     { "type": "boolean" },
        "closure_audit_pass":         { "type": "boolean" },
        "contradiction_audit_pass":   { "type": "boolean" }
      }
    },
    "ambiguity": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "현재 가중치 모호성. 1 - Σ(bucket × weight). 표시용; 게이트가 우선."
    },
    "threshold": {
      "type": "number",
      "description": "프로파일 임계값. quick=0.30, standard=0.20, deep=0.15."
    },
    "max_rounds": {
      "type": "integer",
      "description": "프로파일 최대 라운드 수. quick=5, standard=12, deep=20."
    },
    "current_stage": {
      "type": "string",
      "enum": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
    },
    "challenge_modes_used": {
      "type": "array",
      "items": { "type": "string", "enum": ["contrarian", "simplifier", "ontologist"] },
      "description": "이미 사용된 챌린지 모드 (재사용 방지)."
    },
    "provenance_audit": {
      "type": "object",
      "description": "Iconoclast의 Evidence Ratio를 보완적 audit으로 통합.",
      "properties": {
        "fact_coverage":              { "type": "number", "minimum": 0, "maximum": 1 },
        "judgment_coverage":          { "type": "number", "minimum": 0, "maximum": 1 },
        "unresolved_inference_count": { "type": "integer", "minimum": 0 }
      }
    },
    "context_snapshot_path": {
      "type": ["string", "null"],
      "description": "사전 컨텍스트가 oversized라 요약했을 때 그 요약 파일 경로."
    }
  }
}
```

## 원자적 쓰기 규약

상태 사이드카는 **세 가드**로 손상을 방지합니다:

1. **G1 단일 작성자 불변식** — 인터뷰는 반드시 메인 세션에서 실행 (서브에이전트 호출 금지). 동시 작성자 없음.
2. **G2 Slug 유일성** — `{slug}-{ts}` 조합은 인터뷰별 고유.
3. **G3 원자적 rename** — 사이드카 갱신은 다음 패턴으로 수행:
   ```
   write    .claude/plans/interview-{slug}-{ts}.state.json.tmp
   rename   .claude/plans/interview-{slug}-{ts}.state.json.tmp  →  .claude/plans/interview-{slug}-{ts}.state.json
   ```
   POSIX `rename(2)`는 원자적. NTFS `MoveFileEx` (또는 `os.replace` in Python)도 같은 디렉토리 내에서는 원자적.

## 재구성 절차 (사이드카 누락/손상 시)

1. 트랜스크립트 `.md`를 처음부터 읽기
2. 각 round를 순서대로 파싱 → `rounds[]` 재생성
3. 마지막 라운드의 dimension 상태로 `dimensions` 채우기
4. 게이트 평가를 트랜스크립트 증거로 다시 수행 → `gates` 채우기
5. ambiguity = `1 - Σ(bucket × weight)` 재계산
6. `current_stage`는 트랜스크립트의 마지막 명시적 단계 마커로 추론

이 절차는 트랜스크립트가 단계 진입/종료를 명시적으로 마킹하는 한 결정적입니다. SKILL.md의 트랜스크립트 작성 규약은 이를 보장합니다.

## 사용자 환경 .gitignore 권장사항

이 사이드카는 사용자 프로젝트의 `.claude/plans/` 디렉토리에 작성됩니다. 사용자 프로젝트의 `.gitignore`에 다음을 추가할 것을 권장합니다:

```gitignore
# deep-interview 런타임 캐시 (트랜스크립트로부터 재구성 가능)
.claude/plans/*.state.json
```

트랜스크립트 `.md` 파일 자체는 팀과 공유할 가치가 있을 수 있으므로 무시하지 않습니다.

## 버전 관리

이 스키마는 `version: "2.0.0"` 필드로 식별됩니다. 향후 변경 시:
- MAJOR: 필드 제거, 타입 변경 — 마이그레이션 스크립트 필요
- MINOR: 필드 추가 (선택적) — 하위 호환
- PATCH: 문서/주석 수정만
