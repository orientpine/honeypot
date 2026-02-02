---
name: file-save-protocol-stock
description: "주식/ETF 분석 결과 파일 저장 프로토콜. Write 도구 사용 규칙, 저장 경로 컨벤션, 실패 시 응답 형식을 정의합니다."
tools: Write
---

# 파일 저장 프로토콜 (주식/ETF 분석용)

## Overview

이 스킬은 주식/ETF 분석 에이전트가 결과를 파일로 저장할 때 따라야 하는 규칙을 정의합니다.

**핵심 목표**: 분석 결과의 영속성 보장 및 환각 방지

---

## 1. 파일 저장 필수 규칙 (CRITICAL)

> **환각 방지의 핵심**: 분석 결과를 **반드시 파일로 저장**해야 합니다.
> 프롬프트로만 반환하면 데이터 손실 및 환각 발생 위험이 있습니다.

### 왜 파일 저장이 필수인가?

| 문제 | 설명 |
|------|------|
| **컨텍스트 손실** | 긴 대화에서 이전 분석 결과가 잘릴 수 있음 |
| **재현 불가** | 파일 없이는 분석 결과를 재검증할 수 없음 |
| **환각 위험** | 저장 없이 "저장됨"이라고 응답하면 환각 |
| **워크플로우 중단** | 다음 에이전트가 입력 파일을 찾지 못함 |

### 필수 사항 (MUST)

- 모든 분석 결과는 `Write` 도구로 파일 저장
- 저장 경로는 coordinator가 제공하는 `output_path` 사용
- 저장 성공 여부 확인 후 응답
- 저장 실패 시 명시적 FAIL 응답

### 금지 사항 (NEVER)

- 파일 저장 없이 분석 결과 "완료" 응답
- 저장 실패를 무시하고 진행
- `output_path` 무시하고 임의 경로 사용

---

## 1.5 Markdown 저장 규칙 (MANDATORY)

JSON 저장은 **항상 필수**이며, 사람이 읽기 위한 Markdown 요약도 **반드시** 저장합니다.

### 필수 규칙

- JSON과 MD 모두 저장 (둘 중 하나라도 누락 시 FAIL)
- MD는 JSON 내용을 요약/정리만 수행 (새 수치/새 출처 추가 금지)
- 파일명은 **번호 접두어 고정**:
  - `{output_path}/{NN}-{base}.md` (base = JSON 파일명에서 `.json` 제거)

---

## 2. 저장 프로세스

### Step-by-Step

```
Step 1: 분석 완료 후 JSON 객체 생성

Step 2: Write 도구로 파일 저장
        Write(
          file_path="{output_path}/{filename}.json",
          content=JSON.stringify(analysis_result, null, 2)
        )

Step 3: 저장 성공 확인
        └─ 성공: 정상 응답 반환
        └─ 실패: FAIL 응답 반환 (환각 데이터 생성 금지)
```

### 저장 경로 컨벤션

coordinator(stock-consultant)가 제공하는 `output_path`를 사용합니다:

```
consultations/{session_folder}/{filename}

예시:
consultations/2026-01-14-TSLA-abc123/
├── index-data.json               # index-fetcher 출력
├── rate-analysis.json            # rate-analyst 출력
├── sector-analysis.json          # sector-analyst 출력
├── risk-analysis.json            # risk-analyst 출력
├── leadership-analysis.json      # leadership-analyst 출력
├── material-summary.md           # material-organizer 출력 (옵셔널)
├── macro-outlook.json            # macro-synthesizer 출력
├── 00-macro-outlook.md           # macro-synthesizer 출력
├── 00-materials-summary.md       # 자료 정리 (materials_path 제공 시)
├── 01-stock-screening.json       # stock-screener 출력
├── 02-valuation-report.json      # stock-valuation 출력
├── 03-bear-case.json             # bear-case-critic 출력
├── 04-final-verification.json    # stock-critic 출력
└── 05-consultation-summary.md    # 최종 상담 보고서
```

### 에이전트별 출력 파일

| 에이전트 | 출력 파일 | 필수 |
|----------|----------|:----:|
| stock-screener | `01-stock-screening.json` | O (포트폴리오 요청 시) |
| stock-valuation | `02-valuation-report.json` | O |
| bear-case-critic | `03-bear-case.json` | O |
| stock-critic | `04-final-verification.json` | O |

### 거시경제 분석 출력 파일 (macro-analysis 재사용)

| 에이전트 | 출력 파일 | 필수 |
|----------|----------|:----:|
| index-fetcher | `index-data.json` | O |
| rate-analyst | `rate-analysis.json` | O |
| sector-analyst | `sector-analysis.json` | O |
| risk-analyst | `risk-analysis.json` | O |
| leadership-analyst | `leadership-analysis.json` | O |
| material-organizer | `material-summary.md` | X (옵셔널) |
| macro-synthesizer | `macro-outlook.json`, `00-macro-outlook.md` | O |

---

## 3. 저장 실패 시 응답

저장이 실패하면 **절대 "저장됨"으로 응답하지 않습니다**:

```json
{
  "status": "FAIL",
  "error": "FILE_SAVE_FAILED",
  "detail": "{filename} 저장 실패",
  "attempted_path": "{output_path}/{filename}",
  "action": "재시도 필요"
}
```

### 실패 유형별 대응

| 실패 유형 | 코드 | 대응 |
|:----------|:-----|:-----|
| 경로 없음 | `PATH_NOT_FOUND` | coordinator에 경로 확인 요청 |
| 권한 오류 | `PERMISSION_DENIED` | 경로 권한 확인 |
| 디스크 공간 | `DISK_FULL` | 공간 확보 후 재시도 |
| 알 수 없음 | `UNKNOWN_ERROR` | 에러 메시지 포함하여 보고 |

---

## 4. Write 도구 사용법

### 기본 사용법

```
Write(
  file_path="consultations/{session_folder}/02-valuation-report.json",
  content="{\"status\": \"PASS\", \"ticker\": \"005930\", ...}"
)
```

### JSON 포맷팅

```python
# 들여쓰기 2칸으로 포맷팅
JSON.stringify(analysis_result, null, 2)
```

### 파일 확장자 규칙

| 데이터 유형 | 확장자 |
|-------------|--------|
| 구조화된 분석 데이터 | `.json` |
| 마크다운 보고서 | `.md` |
| 원시 텍스트 | `.txt` |

---

## 5. 저장 확인 체크리스트 (MANDATORY)

### 저장 전 확인
- [ ] `output_path`가 coordinator로부터 전달되었는가?
- [ ] 저장할 데이터가 완전한가 (모든 필수 필드 포함)?
- [ ] JSON 형식이 올바른가?

### 저장 후 확인
- [ ] Write 도구가 에러 없이 완료되었는가?
- [ ] 저장 경로를 응답에 포함했는가?
- [ ] 저장 실패 시 FAIL 응답을 반환했는가?

### 절대 금지
- [ ] 파일 저장 실패 시 "저장된 것처럼" 응답하지 않았는가?
- [ ] 저장 없이 분석 "완료"로 응답하지 않았는가?

---

## 6. 응답 템플릿

### 성공 시 응답

```json
{
  "status": "PASS",
  "output_file": "{output_path}/{filename}.json",
  "summary": {
    // 분석 결과 요약
  }
}
```

### 실패 시 응답

```json
{
  "status": "FAIL",
  "error": "FILE_SAVE_FAILED",
  "detail": "02-valuation-report.json 저장 실패",
  "attempted_path": "consultations/2026-01-14-TSLA-abc123/02-valuation-report.json",
  "action": "재시도 필요"
}
```

---

## 메타 정보

```yaml
version: "1.0"
created: "2026-01-20"
purpose: "파일 저장 프로토콜 통합 - 코드 중복 제거"
based_on: "investments-portfolio/skills/file-save-protocol"
consumers:
  - stock-screener
  - stock-valuation
  - bear-case-critic
  - stock-critic
extracted_from:
  - "파일 저장 필수 섹션 (investments-portfolio)"
  - "저장 프로세스 섹션"
  - "저장 실패 시 응답 형식"
dependencies:
  - Write
output_path_pattern: "consultations/{YYYY-MM-DD}-{ticker}-{session_id}/"
```
