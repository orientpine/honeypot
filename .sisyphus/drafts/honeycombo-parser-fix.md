# HoneyCombo 파서 수정 가이드: 멀티라인 Summary 지원

## 문제 현상

link-curator 플러그인으로 기사를 제출하면 제목과 요약이 모두 `## 개요`로 표시됨. 실제 한국어 요약 내용은 유실됨.

**제출한 Issue body:**
```markdown
### Summary

## 개요
AI 에이전트를 프로덕션 환경에서 활용하는 실전 분석 기사

## 주요 내용
- 에이전트 아키텍처 설계 패턴
- 프로덕션 배포 시 고려사항

## 시사점
실무에서 바로 적용 가능한 에이전트 구축 가이드
```

**HoneyCombo에 표시된 결과:**
- 제목: `## 개요`
- 요약: `## 개요`
- 실제 내용: 없음

## 근본 원인

### 1. 파서가 첫 줄만 읽음

`scripts/process-submission.ts`의 `parseIssueBody` (lines 81-116)가 `### Summary` 섹션에서 **첫 번째 비어있지 않은 줄만** 캡처함.

```
### Summary
                    ← 빈 줄 (스킵)
## 개요             ← 첫 번째 비어있지 않은 줄 → note = "## 개요"
AI 에이전트를...     ← 이후 전부 무시됨
```

### 2. note 값이 제목으로도 사용됨

`processSubmission` (lines 290-310)이 파싱된 `note` 값을 비-YouTube 제출의 **제목(title)**으로도 사용. 결과: 제목 = 요약 = `## 개요`.

### 3. 테스트 코드에서 확인됨

`tests/process-submission.test.ts:69-79`가 이 동작을 명시적으로 테스트:
- 입력: `## 개요\n실제 내용...`
- 기대값: `note: '## 개요'` (첫 줄만)

## 수정 방향

### `parseIssueBody` 수정

`### Summary` 이후 **다음 `###` 헤더 또는 body 끝(EOF)까지의 전체 텍스트**를 `note`로 캡처하도록 변경.

**Before (현재):**
```
### Summary 이후 첫 번째 비어있지 않은 줄만 캡처
→ note = "## 개요"
```

**After (수정 후):**
```
### Summary 이후 다음 ### 헤더 또는 EOF까지 전체 텍스트 캡처
→ note = "## 개요\nAI 에이전트를...\n\n## 주요 내용\n- 에이전트...\n\n## 시사점\n실무에서..."
```

### 제목 파생 로직 수정

멀티라인 `note`를 받을 경우 제목을 별도로 파생하는 로직 필요:
- 옵션 A: `note`의 첫 줄에서 `## ` 접두사를 제거한 텍스트를 제목으로 사용
- 옵션 B: URL의 `<title>` 태그를 제목으로 사용 (oEmbed 등)
- 옵션 C: `note` 전체를 요약으로만 사용하고 제목은 URL 기반으로 자동 생성

### 테스트 업데이트

`process-submission.test.ts:69-79`의 기대값을 멀티라인 note로 변경:
```typescript
// Before
expect(result.note).toBe('## 개요');

// After
expect(result.note).toContain('## 개요');
expect(result.note).toContain('## 주요 내용');
expect(result.note).toContain('## 시사점');
```

## 수정하지 않아야 하는 것

**link-curator 플러그인은 변경 불필요.** 플러그인은 제출 매뉴얼 스펙(`### Summary` 아래에 `## 개요` / `## 주요 내용` / `## 시사점` 구조)을 정확히 따르고 있음.

## 영향 범위

| 항목 | 영향 |
|------|------|
| 단건 제출 (single submit) | `### Summary` 멀티라인 파싱 필요 |
| 대량 제출 (bulk submit) | 영향 없음 (이미 단일 행 `\|` 구분 포맷) |
| YouTube 제출 | 영향 없음 (oEmbed 제목 사용) |
| 기존 단일 행 제출 | 하위 호환 유지 필요 (첫 줄만 있는 경우에도 정상 동작) |
