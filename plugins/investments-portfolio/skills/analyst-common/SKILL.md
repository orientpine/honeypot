---
name: analyst-common
description: "분석 에이전트 공통 규칙. 웹검색 직접 호출, 원문 인용, 교차 검증 프로토콜을 정의합니다. 환각 방지의 핵심 방어선."
tools: mcp_websearch_web_search_exa, WebFetch
---

# 분석 에이전트 공통 규칙

## Overview

이 스킬은 모든 분석 에이전트(index-fetcher, rate-analyst, sector-analyst, risk-analyst, leadership-analyst, macro-critic)가 공통으로 따라야 하는 규칙을 정의합니다.

**핵심 목표**: 환각(Hallucination) 방지

---

## 1. 웹검색 도구 직접 호출 필수

> **CRITICAL**: 스킬은 "지침 문서"이지 "함수"가 아닙니다.
> 에이전트가 웹검색 도구를 **직접 호출**해야 합니다.

### 올바른 사용법

```
1. web-search-verifier 스킬에서 검색 쿼리 패턴 확인
2. mcp_websearch_web_search_exa 직접 호출
   - 예: mcp_websearch_web_search_exa(query="S&P 500 price today")
   - 예: mcp_websearch_web_search_exa(query="한국은행 기준금리")
3. 검색 결과에서 숫자가 포함된 원문을 그대로 복사
4. 최소 3개 출처에서 값 확인 및 교차 검증
5. 출처 간 ±1% 이내 일치 시 사용, 불일치 시 FAIL
```

### 필수 사항 (MUST)

- `mcp_websearch_web_search_exa` **직접 호출**
- **원문 인용 필수** - 숫자가 포함된 검색 결과 문장을 그대로 복사
- 최소 3개 이상 독립 출처에서 교차 검증
- 검색 결과의 URL과 날짜 명시
- 출처 간 값이 일치하는지 확인 (±1% 이내)

### 금지 사항 (NEVER)

| 금지 | 이유 |
|------|------|
| `search_index()`, `search_rate()` 같은 함수 호출 | 존재하지 않는 가짜 함수 |
| 스킬 문서의 예시 데이터 그대로 사용 | 하드코딩된 오래된 값 |
| 웹검색 없이 데이터 사용 | 검증 불가능한 환각 |
| 기억이나 추정에 의한 값 작성 | LLM 학습 데이터는 outdated |
| **원문 없이 숫자만 보고** | 환각 위험 극대화 |

---

## 2. 원문 인용 규칙 (CRITICAL)

> **환각 방지의 핵심**: 검색 결과에서 숫자를 추출할 때 반드시 **원문을 그대로 인용**해야 합니다.

### 숫자 추출 방법

```
1. 웹검색 결과에서 숫자가 포함된 문장 찾기
2. 해당 문장을 **그대로 복사** (original_text 필드에)
3. 원문에서 숫자 추출하여 value 필드에 기록
4. value와 original_text 내 숫자가 일치하는지 확인
```

### 출력 형식 (필수)

모든 수치 데이터는 다음 형식으로 보고해야 합니다:

```json
{
  "value": 6936,
  "original_text": "The US500 fell to 6936 points on January 12, 2026",
  "source": "Trading Economics",
  "url": "https://tradingeconomics.com/united-states/stock-market"
}
```

### 검증 규칙

| 규칙 | 설명 | 위반 시 |
|:-----|:-----|:--------|
| **원문 필수** | `original_text` 필드 없으면 무효 | FAIL |
| **숫자 일치** | `value`가 `original_text` 내 숫자와 일치해야 함 | FAIL |
| **복사 금지** | 이전 결과나 예시 값을 복사하면 안 됨 | FAIL |

### 예시

**올바른 예시**:
```json
{
  "index": "S&P 500",
  "value": 6936,
  "original_text": "The main stock market index of United States, the US500, fell to 6936 points on January 12, 2026",
  "source_url": "https://tradingeconomics.com/united-states/stock-market"
}
```

**잘못된 예시 (환각)**:
```json
{
  "index": "S&P 500",
  "value": 5906,
  "original_text": null,
  "source_url": "https://tradingeconomics.com/united-states/stock-market"
}
```
→ 원문 없이 숫자만 보고하면 검증 불가능 = 환각

---

## 3. 교차 검증 프로토콜

### 검증 요구사항

| 항목 | 기준 |
|------|------|
| 최소 출처 수 | 3개 이상 |
| 값 일치 허용 범위 | ±1% |
| 1차 출처 | 공식 출처(Fed, BOK, KRX 등) 1개 이상 권장 |
| 날짜 일치 | 동일 거래일 데이터 |

### 검증 절차

```
Step 1: 첫 번째 출처에서 값 수집
└─ mcp_websearch_web_search_exa(query="...")
         
Step 2: 두 번째 출처에서 값 수집
         └─ mcp_websearch_web_search_exa(query="... site:다른출처")
        
Step 3: 값 비교
        └─ 차이 = |값1 - 값2| / 평균값 * 100
        
Step 4: 판정
        └─ 차이 ≤ 1%: 검증 성공 (verified: true)
        └─ 차이 > 1%: 검증 실패, 추가 출처 검색 또는 FAIL
```

### 검증 실패 시 처리

검증 실패 시 **절대 임의 수치를 생성하지 않습니다**:

```json
{
  "status": "FAIL",
  "failed_items": ["KOSPI"],
  "reason": "교차 검증 실패 - 출처 간 값 불일치",
  "detail": {
    "source1": {"name": "A", "value": 4500},
    "source2": {"name": "B", "value": 4735},
    "variance": "5.2%"
  }
}
```

---

## 4. 검증 체크리스트 (MANDATORY)

모든 분석 에이전트는 결과 제출 전 아래 체크리스트를 확인해야 합니다.

### 웹검색 직접 호출 확인
- [ ] `mcp_websearch_web_search_exa`를 **직접 호출**했는가?
- [ ] `search_index()`, `search_rate()` 같은 가짜 함수를 호출하지 않았는가?
- [ ] 스킬 예시 데이터를 그대로 사용하지 않았는가?

### 원문 인용 확인
- [ ] 모든 수치에 `original_text` 필드가 있는가?
- [ ] `value`가 `original_text` 내 숫자와 일치하는가?
- [ ] 이전 결과나 예시 값을 복사하지 않았는가?

### 교차 검증 확인
- [ ] 모든 수치에 최소 3개 출처가 있는가?
- [ ] 출처 간 값이 ±1% 이내로 일치하는가?
- [ ] 모든 값에 출처 URL이 포함되어 있는가?

### 실패 처리 확인
- [ ] 교차 검증 실패 시 FAIL 목록에 추가했는가?
- [ ] 추정값을 생성하지 않았는가?

---

## 5. 허용 출처 (Allowlist)

### Tier 1: 공식 출처 (1개 이상 권장)

| 데이터 | 출처 | URL |
|:-------|:-----|:----|
| 미국 주식/경제 | FRED | fred.stlouisfed.org |
| 미국 금리 | Federal Reserve | federalreserve.gov |
| 한국 주식 | 한국거래소 | krx.co.kr |
| 한국 금리 | 한국은행 | bok.or.kr |
| 글로벌 | Bloomberg | bloomberg.com |

### Tier 2: 교차검증 출처

| 출처 | URL | 커버리지 |
|:-----|:----|:---------|
| Trading Economics | tradingeconomics.com | 글로벌 |
| Investing.com | investing.com | 글로벌 |
| Yahoo Finance | finance.yahoo.com | 글로벌 |
| MarketWatch | marketwatch.com | 미국 중심 |

### Tier 3: 보조 출처

| 출처 | URL | 용도 |
|:-----|:----|:-----|
| 한국경제 | hankyung.com | 한국 시장 |
| 연합뉴스 | yna.co.kr | 한국 경제 |
| Reuters | reuters.com | 글로벌 뉴스 |
| FT | ft.com | 글로벌 금융 |

### Blocklist (금지)

- 개인 블로그
- 위키피디아 (실시간 데이터용)
- 커뮤니티 사이트
- 신뢰도 미검증 사이트

---

## 메타 정보

```yaml
version: "1.0"
created: "2026-01-14"
purpose: "분석 에이전트 공통 규칙 통합 - 코드 중복 제거"
consumers:
  - index-fetcher
  - rate-analyst
  - sector-analyst
  - risk-analyst
  - leadership-analyst
  - macro-critic
extracted_from:
  - "웹검색 도구 직접 호출 필수 섹션"
  - "원문 인용 규칙 섹션"
  - "교차 검증 프로토콜"
  - "Verification Checklist"
dependencies:
  - mcp_websearch_web_search_exa
  - mcp_websearch_web_search_exa
  - WebFetch
```
