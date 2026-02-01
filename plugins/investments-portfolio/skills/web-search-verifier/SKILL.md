---
name: web-search-verifier
description: "3개 출처 교차검증 웹검색 프로토콜. 환각 방지 첫 번째 방어선. 모든 거시경제 데이터 수집 시 필수 사용."
tools: mcp_websearch_web_search_exa, WebFetch
---

# 웹검색 교차검증 스킬

## ⚠️ CRITICAL: 스킬 사용 방법 (반드시 숙지)

> **이 스킬은 "함수"가 아닙니다. 지침 문서입니다.**
> 
> - ❌ `search_rate("fed_funds")` 같은 함수 호출은 **작동하지 않습니다**
> - ✅ 에이전트가 `mcp_websearch_web_search_exa` 도구를 **직접 호출**해야 합니다
> - ✅ 이 스킬은 **검색 쿼리 패턴과 검증 절차**를 안내하는 문서입니다

### 올바른 사용 방법

```
1. 이 스킬 문서를 읽고 검색 쿼리 패턴 파악
2. mcp_websearch_web_search_exa 도구를 직접 호출
3. 검색 결과에서 데이터 추출
4. 3개 출처 교차 검증 수행
5. 출력 스키마에 맞춰 결과 포장
```

### 잘못된 사용 방법 (환각 발생)

```
❌ "search_rate() 호출" (존재하지 않는 함수)
❌ "스킬이 알아서 검색해줌" (스킬은 문서일 뿐)
❌ 예시 데이터의 숫자를 그대로 사용 (하드코딩된 오래된 값)
```

---

## Overview

이 스킬은 거시경제 데이터(지수, 금리, 환율) 수집 시 **환각을 방지**하기 위한 표준 프로토콜입니다.
모든 수치 데이터는 **에이전트가 직접 웹검색 도구를 호출**하여 **3개 이상의 독립 출처에서 교차 검증** 후에만 사용 가능합니다.

---

## 절대 규칙 (Zero Tolerance)

### 금지 사항 (NEVER)
- ❌ 웹검색 없이 숫자 생성 → 즉시 FAIL
- ❌ 단일 출처만으로 확정 → 최소 3개 필수
- ❌ 출처 URL 없이 데이터 반환 → 검증 불가
- ❌ 7일 이상 오래된 데이터 사용 → 최신성 위반
- ❌ Blocklist 출처 사용 → 신뢰도 위반

### 필수 사항 (MUST)
- ✅ 최소 3개 독립 출처에서 교차 검증
- ✅ 1차 출처(공식) 최소 1개 필수 포함
- ✅ 출처 간 ±1% 이내 일치 확인
- ✅ 모든 데이터에 [출처: URL, 날짜] 태그 포함
- ✅ 검증 실패 시 FAIL 반환 (추정값 금지)
- ✅ **원문 인용 필수** (v2.0 신규) - 숫자를 포함한 검색 결과 원문을 그대로 인용

---

## ⚠️ 원문 인용 규칙 (v2.0 신규 - CRITICAL)

> **환각 방지의 핵심**: 검색 결과에서 숫자를 추출할 때 반드시 **원문을 그대로 인용**해야 합니다.
> 원문과 보고 값이 일치하지 않으면 **FAIL**입니다.

### 올바른 숫자 추출 방법

```
1. 웹검색 실행
2. 검색 결과에서 숫자가 포함된 문장을 **그대로 복사**
3. 원문에서 숫자 추출
4. 추출한 숫자와 원문을 함께 보고
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

### 원문 인용 예시

**✅ 올바른 예시**:
```json
{
  "index": "S&P 500",
  "value": 6936,
  "original_text": "The main stock market index of United States, the US500, fell to 6936 points on January 12, 2026",
  "source_url": "https://tradingeconomics.com/united-states/stock-market"
}
```

**❌ 잘못된 예시 (환각 위험)**:
```json
{
  "index": "S&P 500",
  "value": 5906,
  "original_text": null,
  "source_url": "https://tradingeconomics.com/united-states/stock-market"
}
```
→ 원문 없이 숫자만 보고하면 검증 불가능

---

## 검색 프로토콜

### 1. 지수 데이터 검색

**데이터 유형**: 지수 (Index)

> ⚠️ 아래는 **검색 패턴 가이드**입니다. `search_index()`라는 함수는 **존재하지 않습니다**.
> 반드시 `mcp_websearch_web_search_exa`를 **직접 호출**하세요.

**지원 지수**:
- S&P 500, NASDAQ, Dow Jones
- KOSPI, KOSDAQ
- USD/KRW, EUR/KRW, JPY/KRW

**검색 쿼리 패턴** (3개 병렬 실행):

| # | 패턴 | 대상 출처 |
|:-:|:-----|:---------|
| 1 | `"[index] price today site:investing.com OR site:bloomberg.com"` | 글로벌 금융 |
| 2 | `"[지수] 종가 site:tradingeconomics.com"` | 금융 데이터 |
| 3 | `"[index] quote site:finance.yahoo.com OR site:marketwatch.com"` | 시세 사이트 |

**검증 절차**:
1. 3개 검색 결과에서 수치 추출
2. 날짜 일치 확인 (동일 거래일)
3. 값 일치 확인 (±1% 이내)
4. 1차 출처 포함 확인

**출력 스키마 (v2.0 업데이트)**:
```json
{
  "index": "S&P 500",
  "value": "[SEARCH_RESULT - 웹검색 결과로 대체]",
  "unit": "pt",
  "date": "[SEARCH_DATE - 검색 시점 날짜]",
  "verified": true,
  "variance": "[CALCULATED - 출처 간 편차 계산]",
  "original_text": "[REQUIRED - 숫자를 포함한 검색 결과 원문]",
  "sources": [
    {
      "name": "Trading Economics",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE - 이 출처에서 숫자가 포함된 문장]",
      "tier": 2
    },
    {
      "name": "Bloomberg",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE]",
      "tier": 1
    }
  ]
}

⚠️ CRITICAL (v2.0):
1. `original_text` 필드는 **필수**입니다. 없으면 FAIL.
2. `value`는 반드시 `original_text` 내의 숫자와 일치해야 합니다.
3. 예시 값을 그대로 사용하지 마세요.
```

### 2. 금리 데이터 검색

**데이터 유형**: 금리 (Interest Rate)

> ⚠️ 아래는 **검색 패턴 가이드**입니다. `search_rate()`라는 함수는 **존재하지 않습니다**.
> 반드시 `mcp_websearch_web_search_exa`를 **직접 호출**하세요.

**지원 금리**:
- fed_funds: 미국 기준금리
- bok_base: 한국 기준금리
- us_10y_treasury: 미국 10년물 국채

**검색 쿼리 패턴**:

| 금리 | 1차 출처 쿼리 | 2차 출처 쿼리 |
|:-----|:-------------|:-------------|
| Fed | `"federal funds rate site:federalreserve.gov"` | `"fed rate site:tradingeconomics.com"` |
| BOK | `"기준금리 site:bok.or.kr"` | `"korea rate site:tradingeconomics.com"` |

**검증 절차**:
1. 공식 출처(1차) 검색
2. 교차검증 출처(2차) 검색
3. 값 일치 확인
4. FOMC/금통위 결정일 확인
5. 다음 회의 일정 확인

**출력 스키마 (v2.0 업데이트)**:
```json
{
  "rate_type": "fed_funds",
  "value": "[SEARCH_RESULT - 웹검색으로 확인한 실제 금리]",
  "decision_date": "[SEARCH_RESULT - 최근 FOMC/금통위 결정일]",
  "next_meeting": "[SEARCH_RESULT - 다음 회의 예정일]",
  "verified": true,
  "original_text": "[REQUIRED - 금리 수치가 포함된 검색 결과 원문]",
  "sources": [
    {
      "name": "Federal Reserve",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE - 공식 출처의 금리 언급 원문]",
      "official": true
    },
    {
      "name": "Trading Economics",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE]",
      "official": false
    }
  ]
}

⚠️ CRITICAL (v2.0):
1. `original_text` 필드는 **필수**입니다. 없으면 FAIL.
2. `value`는 반드시 `original_text` 내의 숫자와 일치해야 합니다.
3. 금리의 경우 "3.50-3.75%" 형식으로 범위 표기 가능.
4. 예시 값을 그대로 사용하면 환각(hallucination)이 발생합니다.
```

---

## 허용 출처 (Allowlist)

### Tier 1: 공식 출처 (필수 1개 이상)

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

## 검증 실패 처리

### 실패 유형별 대응

| 실패 유형 | 코드 | 대응 |
|:----------|:-----|:-----|
| 출처 부족 | `INSUFFICIENT_SOURCES` | 추가 검색 시도 (최대 3회) |
| 값 불일치 | `VALUE_MISMATCH` | 범위로 표현 또는 1차 출처 우선 |
| 날짜 불일치 | `DATE_MISMATCH` | 가장 최신 날짜 출처 우선 |
| 1차 출처 없음 | `NO_PRIMARY_SOURCE` | 경고 + 2차 출처로 진행 |
| 전체 실패 | `COMPLETE_FAILURE` | FAIL 반환, 수동 확인 요청 |

### 실패 출력 스키마

```json
{
  "index": "KOSPI",
  "value": null,
  "verified": false,
  "error": {
    "code": "VALUE_MISMATCH",
    "reason": "출처 간 5.2% 차이 (허용: ±1%)",
    "details": {
      "source1": {"name": "A", "value": 4500},
      "source2": {"name": "B", "value": 4735}
    }
  },
  "recommendation": "수동 확인 필요"
}
```

---

## 사용 예시

### 에이전트에서 스킬 사용

```markdown
# index-fetcher 에이전트

## 데이터 수집

1. web-search-verifier 스킬 로드 확인 (검색 패턴 가이드로 참조)
2. S&P 500 수집:
   - mcp_websearch_web_search_exa(query="S&P 500 price today") **직접 호출**
   - 검색 결과에서 original_text 추출
   - verified: true 확인
3. KOSPI 수집:
   - mcp_websearch_web_search_exa(query="KOSPI 지수 현재") **직접 호출**
   - 검색 결과에서 original_text 추출
   - verified: true 확인

## 검증 실패 시

verified: false인 경우:
- 해당 지수는 "데이터 수집 실패" 명시
- 추정값 생성 금지
- 에러 코드 전달
```

---

## 리소스

- 허용 출처: 위 "Tier 1/2/3 출처" 섹션 참조
- 검색 패턴: 위 "검색 전략" 섹션 참조

---

## 메타 정보

```yaml
version: "2.1"
created: "2026-01-12"
updated: "2026-01-12"
author: "Claude"
purpose: "환각 방지 웹검색 표준화"
dependencies:
  - mcp_websearch_web_search_exa
  - mcp_websearch_web_search_exa
  - WebFetch
consumers:
  - index-fetcher
  - rate-analyst
  - sector-analyst
  - risk-analyst
  - leadership-analyst
  - macro-synthesizer
changes_v2.1:
  - "범위 검증 (Sanity Check) 제거 - 대폭락 시 정상 데이터 reject 문제"
changes_v2.0:
  - "원문 인용 필수화 (original_text 필드)"
  - "S&P 500 첫자리 오류 환각 방지"
```
