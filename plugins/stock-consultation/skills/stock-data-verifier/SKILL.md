---
name: stock-data-verifier
description: "주식/ETF 데이터 3개 출처 교차검증 프로토콜. 환각 방지 첫 번째 방어선."
tools: mcp_exa_web_search_exa, mcp_websearch_web_search_exa, WebFetch
---

# 주식/ETF 데이터 교차검증 스킬

## ⚠️ CRITICAL: 스킬 사용 방법 (반드시 숙지)

> **이 스킬은 "함수"가 아닙니다. 지침 문서입니다.**
> 
> - ❌ `search_stock("삼성전자")` 같은 함수 호출은 **작동하지 않습니다**
> - ✅ 에이전트가 `mcp_exa_web_search_exa` 또는 `mcp_websearch_web_search_exa` 도구를 **직접 호출**해야 합니다
> - ✅ 이 스킬은 **검색 쿼리 패턴과 검증 절차**를 안내하는 문서입니다

### 올바른 사용 방법

```
1. 이 스킬 문서를 읽고 검색 쿼리 패턴 파악
2. mcp_exa_web_search_exa 또는 mcp_websearch_web_search_exa 도구를 직접 호출
3. 검색 결과에서 데이터 추출
4. 최소 2개 출처 교차 검증 수행
5. 출력 스키마에 맞춰 결과 포장
```

### 잘못된 사용 방법 (환각 발생)

```
❌ "search_stock() 호출" (존재하지 않는 함수)
❌ "스킬이 알아서 검색해줌" (스킬은 문서일 뿐)
❌ 예시 데이터의 숫자를 그대로 사용 (하드코딩된 오래된 값)
```

---

## Overview

이 스킬은 주식/ETF 데이터(가격, PER, 배당률, 운용보수 등) 수집 시 **환각을 방지**하기 위한 표준 프로토콜입니다.
모든 수치 데이터는 **에이전트가 직접 웹검색 도구를 호출**하여 **최소 2개 이상의 독립 출처에서 교차 검증** 후에만 사용 가능합니다.

---

## 절대 규칙 (Zero Tolerance)

### 금지 사항 (NEVER)
- ❌ 웹검색 없이 숫자 생성 → 즉시 FAIL
- ❌ 단일 출처만으로 확정 → 최소 2개 필수
- ❌ 출처 URL 없이 데이터 반환 → 검증 불가
- ❌ 7일 이상 오래된 데이터 사용 (가격 데이터) → 최신성 위반
- ❌ Blocklist 출처 사용 → 신뢰도 위반

### 필수 사항 (MUST)
- ✅ 최소 2개 독립 출처에서 교차 검증
- ✅ 1차 출처(공식) 최소 1개 필수 포함
- ✅ 출처 간 ±5% 이내 일치 확인
- ✅ 모든 데이터에 [출처: URL, 날짜] 태그 포함
- ✅ 검증 실패 시 FAIL 반환 (추정값 금지)
- ✅ **원문 인용 필수** - 숫자를 포함한 검색 결과 원문을 그대로 인용

---

## ⚠️ 원문 인용 규칙 (CRITICAL)

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
  "value": 58000,
  "original_text": "삼성전자 종가 58,000원 (2026.01.14 기준)",
  "source": "네이버 금융",
  "url": "https://finance.naver.com/item/main.naver?code=005930"
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
  "stock": "삼성전자",
  "per": {
    "value": 12.5,
    "original_text": "삼성전자 PER 12.5배 (2026.01.14 기준)",
    "source": "네이버 금융",
    "url": "https://finance.naver.com/item/main.naver?code=005930"
  }
}
```

**❌ 잘못된 예시 (환각 위험)**:
```json
{
  "stock": "삼성전자",
  "per": {
    "value": 12.5,
    "original_text": null,
    "source": "네이버 금융",
    "url": "https://finance.naver.com/item/main.naver?code=005930"
  }
}
```
→ 원문 없이 숫자만 보고하면 검증 불가능

---

## 검색 프로토콜

### 1. 한국 주식 데이터 검색

**데이터 유형**: 한국 상장 주식 (KOSPI, KOSDAQ)

> ⚠️ 아래는 **검색 패턴 가이드**입니다. `search_korean_stock()`라는 함수는 **존재하지 않습니다**.
> 반드시 `mcp_exa_web_search_exa` 또는 `mcp_websearch_web_search_exa`를 **직접 호출**하세요.

**지원 데이터**:
- 현재가, 시가, 고가, 저가, 거래량
- PER, PBR, ROE, EPS
- 배당률, 배당수익률
- 시가총액, 상장주식수

**검색 쿼리 패턴** (2개 병렬 실행):

| # | 패턴 | 대상 출처 |
|:-:|:-----|:---------|
| 1 | `"[종목명] 주가 site:finance.naver.com"` | 네이버 금융 (1차) |
| 2 | `"[종목명] 시세 site:data.krx.co.kr OR site:kind.krx.co.kr"` | KRX (1차) |
| 3 | `"[종목명] 주가 site:securities.miraeasset.com OR site:securities.samsung.com"` | 증권사 (2차) |

**검증 절차**:
1. 2개 이상 검색 결과에서 수치 추출
2. 날짜 일치 확인 (동일 거래일)
3. 값 일치 확인 (±5% 이내)
4. 1차 출처 포함 확인

**출력 스키마**:
```json
{
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "price": {
    "value": "[SEARCH_RESULT - 웹검색 결과로 대체]",
    "unit": "KRW",
    "date": "[SEARCH_DATE - 검색 시점 날짜]",
    "original_text": "[REQUIRED - 숫자를 포함한 검색 결과 원문]"
  },
  "per": {
    "value": "[SEARCH_RESULT]",
    "original_text": "[REQUIRED]"
  },
  "pbr": {
    "value": "[SEARCH_RESULT]",
    "original_text": "[REQUIRED]"
  },
  "dividend_yield": {
    "value": "[SEARCH_RESULT]",
    "unit": "%",
    "original_text": "[REQUIRED]"
  },
  "verified": true,
  "variance": "[CALCULATED - 출처 간 편차 계산]",
  "sources": [
    {
      "name": "네이버 금융",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE - 이 출처에서 숫자가 포함된 문장]",
      "tier": 1
    },
    {
      "name": "KRX",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE]",
      "tier": 1
    }
  ]
}

⚠️ CRITICAL:
1. `original_text` 필드는 **필수**입니다. 없으면 FAIL.
2. `value`는 반드시 `original_text` 내의 숫자와 일치해야 합니다.
3. 예시 값을 그대로 사용하지 마세요.
```

### 2. 미국 주식 데이터 검색

**데이터 유형**: 미국 상장 주식 (NYSE, NASDAQ)

> ⚠️ 아래는 **검색 패턴 가이드**입니다. `search_us_stock()`라는 함수는 **존재하지 않습니다**.
> 반드시 `mcp_exa_web_search_exa` 또는 `mcp_websearch_web_search_exa`를 **직접 호출**하세요.

**지원 데이터**:
- Price, Open, High, Low, Volume
- P/E Ratio, P/B Ratio, ROE, EPS
- Dividend Yield, Payout Ratio
- Market Cap, Shares Outstanding

**검색 쿼리 패턴**:

| # | 패턴 | 대상 출처 |
|:-:|:-----|:---------|
| 1 | `"[ticker] stock price site:finance.yahoo.com"` | Yahoo Finance (1차) |
| 2 | `"[ticker] quote site:bloomberg.com OR site:marketwatch.com"` | Bloomberg/MarketWatch (1차) |
| 3 | `"[ticker] stock site:seekingalpha.com"` | Seeking Alpha (2차) |

**검증 절차**:
1. 2개 이상 검색 결과에서 수치 추출
2. 날짜 일치 확인 (동일 거래일)
3. 값 일치 확인 (±5% 이내)
4. 1차 출처 포함 확인

**출력 스키마**:
```json
{
  "ticker": "NVDA",
  "stock_name": "NVIDIA Corporation",
  "price": {
    "value": "[SEARCH_RESULT - 웹검색 결과로 대체]",
    "unit": "USD",
    "date": "[SEARCH_DATE - 검색 시점 날짜]",
    "original_text": "[REQUIRED - 숫자를 포함한 검색 결과 원문]"
  },
  "pe_ratio": {
    "value": "[SEARCH_RESULT]",
    "original_text": "[REQUIRED]"
  },
  "pb_ratio": {
    "value": "[SEARCH_RESULT]",
    "original_text": "[REQUIRED]"
  },
  "dividend_yield": {
    "value": "[SEARCH_RESULT]",
    "unit": "%",
    "original_text": "[REQUIRED]"
  },
  "verified": true,
  "variance": "[CALCULATED - 출처 간 편차 계산]",
  "sources": [
    {
      "name": "Yahoo Finance",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE - 이 출처에서 숫자가 포함된 문장]",
      "tier": 1
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

⚠️ CRITICAL:
1. `original_text` 필드는 **필수**입니다. 없으면 FAIL.
2. `value`는 반드시 `original_text` 내의 숫자와 일치해야 합니다.
3. 예시 값을 그대로 사용하지 마세요.
```

### 3. ETF 데이터 검색

**데이터 유형**: ETF (상장지수펀드)

> ⚠️ 아래는 **검색 패턴 가이드**입니다. `search_etf()`라는 함수는 **존재하지 않습니다**.
> 반드시 `mcp_exa_web_search_exa` 또는 `mcp_websearch_web_search_exa`를 **직접 호출**하세요.

**지원 데이터**:
- NAV (순자산가치), 시장가격
- 총보수 (Expense Ratio)
- 추적오차 (Tracking Error)
- 배당률, 배당주기
- 운용자산 (AUM)

**검색 쿼리 패턴**:

| 자산 | 1차 출처 쿼리 | 2차 출처 쿼리 |
|:-----|:-------------|:-------------|
| **한국 ETF** | `"[ETF명] site:finance.naver.com"` | `"[ETF명] site:krx.co.kr"` |
| **미국 ETF** | `"[ticker] ETF site:etf.com"` | `"[ticker] site:finance.yahoo.com"` |

**운용사 공식 페이지 (필수 확인)**:

| 운용사 | URL 패턴 | 확인 데이터 |
|:-------|:---------|:-----------|
| 삼성자산운용 | `site:samsungfund.com` | 총보수, 운용보수 |
| 미래에셋자산운용 | `site:miraeassetfund.co.kr` | 총보수, 운용보수 |
| BlackRock | `site:ishares.com` | Expense Ratio |
| Vanguard | `site:vanguard.com` | Expense Ratio |

**검증 절차**:
1. 운용사 공식 페이지에서 총보수 확인 (필수)
2. 금융 데이터 사이트에서 NAV/가격 확인
3. 값 일치 확인 (±5% 이내)
4. 총보수는 운용사 공식 값 우선

**출력 스키마**:
```json
{
  "etf_code": "360750",
  "etf_name": "TIGER 미국S&P500",
  "nav": {
    "value": "[SEARCH_RESULT - 웹검색 결과로 대체]",
    "unit": "KRW",
    "date": "[SEARCH_DATE - 검색 시점 날짜]",
    "original_text": "[REQUIRED - 숫자를 포함한 검색 결과 원문]"
  },
  "expense_ratio": {
    "value": "[SEARCH_RESULT]",
    "unit": "%",
    "original_text": "[REQUIRED - 운용사 공식 페이지 원문]",
    "source": "운용사 공식"
  },
  "tracking_error": {
    "value": "[SEARCH_RESULT]",
    "unit": "%",
    "original_text": "[REQUIRED]"
  },
  "dividend_yield": {
    "value": "[SEARCH_RESULT]",
    "unit": "%",
    "original_text": "[REQUIRED]"
  },
  "aum": {
    "value": "[SEARCH_RESULT]",
    "unit": "KRW",
    "original_text": "[REQUIRED]"
  },
  "verified": true,
  "variance": "[CALCULATED - 출처 간 편차 계산]",
  "sources": [
    {
      "name": "삼성자산운용",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE - 이 출처에서 숫자가 포함된 문장]",
      "tier": 1,
      "official": true
    },
    {
      "name": "네이버 금융",
      "url": "[ACTUAL_URL]",
      "value": "[ACTUAL_VALUE]",
      "original_text": "[EXACT_QUOTE]",
      "tier": 1,
      "official": false
    }
  ]
}

⚠️ CRITICAL:
1. `original_text` 필드는 **필수**입니다. 없으면 FAIL.
2. `value`는 반드시 `original_text` 내의 숫자와 일치해야 합니다.
3. 총보수는 반드시 운용사 공식 페이지에서 확인해야 합니다.
4. 예시 값을 그대로 사용하지 마세요.
```

---

## 허용 출처 (Allowlist)

### Tier 1: 공식 출처 (필수 1개 이상)

#### 한국 주식/ETF

| 데이터 | 출처 | URL |
|:-------|:-----|:----|
| 주식 시세 | 네이버 금융 | finance.naver.com |
| 주식 시세 | KRX | data.krx.co.kr, kind.krx.co.kr |
| 공시 정보 | DART | dart.fss.or.kr |
| ETF 정보 | 삼성자산운용 | samsungfund.com |
| ETF 정보 | 미래에셋자산운용 | miraeassetfund.co.kr |

#### 미국 주식/ETF

| 데이터 | 출처 | URL |
|:-------|:-----|:----|
| 주식 시세 | Yahoo Finance | finance.yahoo.com |
| 주식 시세 | Bloomberg | bloomberg.com |
| 주식 분석 | MarketWatch | marketwatch.com |
| ETF 정보 | ETF.com | etf.com |
| ETF 정보 | BlackRock (iShares) | ishares.com |
| ETF 정보 | Vanguard | vanguard.com |

### Tier 2: 교차검증 출처

#### 한국 증권사

| 출처 | URL | 커버리지 |
|:-----|:----|:---------|
| 삼성증권 | securities.samsung.com | 한국 주식 |
| 미래에셋증권 | securities.miraeasset.com | 한국 주식 |
| 키움증권 | kiwoom.com | 한국 주식 |
| NH투자증권 | nhqv.com | 한국 주식 |

#### 미국 금융 데이터

| 출처 | URL | 커버리지 |
|:-----|:----|:---------|
| Seeking Alpha | seekingalpha.com | 미국 주식 분석 |
| Morningstar | morningstar.com | 펀드/ETF 분석 |
| CNBC | cnbc.com | 미국 시장 뉴스 |

### Tier 3: 보조 출처

#### 한국 언론

| 출처 | URL | 용도 |
|:-----|:----|:-----|
| 한국경제 | hankyung.com | 한국 주식 뉴스 |
| 매일경제 | mk.co.kr | 한국 주식 뉴스 |
| 연합뉴스 | yna.co.kr | 한국 경제 속보 |

#### 글로벌 언론

| 출처 | URL | 용도 |
|:-----|:----|:-----|
| Reuters | reuters.com | 글로벌 주식 뉴스 |
| Financial Times | ft.com | 글로벌 금융 분석 |
| Wall Street Journal | wsj.com | 미국 주식 뉴스 |

### Blocklist (금지)

**절대 사용 금지 출처**:

| 유형 | 이유 | 예시 |
|:-----|:-----|:-----|
| **개인 블로그** | 신뢰도 미검증 | tistory, naver blog, medium 개인 글 |
| **커뮤니티** | 비전문가 의견 | 네이버 카페, 다음 카페, Reddit r/wallstreetbets, DC인사이드 |
| **YouTube** | 검증 불가 | 개인 유튜버 주식 분석 |
| **위키피디아** | 실시간 데이터 부정확 | wikipedia.org (실시간 주가용) |
| **소셜미디어** | 확인 불가 | Twitter/X, Facebook |

---

## 교차 검증 프로토콜

### 검증 기준

| 데이터 유형 | 최소 출처 수 | 허용 오차 | 우선 출처 |
|:-----------|:----------:|:--------:|:---------|
| **주가** | 2개 | ±5% | 1차 출처 (네이버/Yahoo) |
| **PER/PBR** | 2개 | ±5% | 1차 출처 |
| **배당률** | 2개 | ±5% | 1차 출처 |
| **총보수** | 1개 (운용사) | 0% | 운용사 공식 페이지 |
| **시가총액** | 2개 | ±5% | 1차 출처 |

### 검증 절차

```
1. 최소 2개 출처에서 데이터 수집
2. 각 출처에서 original_text 추출
3. 수치 일치 확인 (±5% 이내)
4. 불일치 시:
   - 5% 이내: 평균값 사용
   - 5% 초과: 가장 최신 출처 우선
   - 10% 초과: FAIL 반환
5. verified: true/false 설정
```

### 불일치 처리

| 편차 | 대응 |
|:----:|:-----|
| **0~5%** | 평균값 사용, verified: true |
| **5~10%** | 최신 출처 우선, verified: true, 경고 포함 |
| **10%+** | FAIL 반환, verified: false, 수동 확인 요청 |

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
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "price": null,
  "verified": false,
  "error": {
    "code": "VALUE_MISMATCH",
    "reason": "출처 간 8.2% 차이 (허용: ±5%)",
    "details": {
      "source1": {"name": "네이버 금융", "value": 58000},
      "source2": {"name": "KRX", "value": 62800}
    }
  },
  "recommendation": "수동 확인 필요"
}
```

---

## 사용 예시

### 에이전트에서 스킬 사용

```markdown
# stock-analyzer 에이전트

## 데이터 수집

1. stock-data-verifier 스킬 로드 확인 (검색 패턴 가이드로 참조)
2. 삼성전자 데이터 수집:
   - mcp_exa_web_search_exa(query="삼성전자 주가 site:finance.naver.com") **직접 호출**
   - 검색 결과에서 original_text 추출
   - verified: true 확인
3. NVIDIA 데이터 수집:
   - mcp_exa_web_search_exa(query="NVDA stock price site:finance.yahoo.com") **직접 호출**
   - 검색 결과에서 original_text 추출
   - verified: true 확인

## 검증 실패 시

verified: false인 경우:
- 해당 종목은 "데이터 수집 실패" 명시
- 추정값 생성 금지
- 에러 코드 전달
```

---

## 메타 정보

```yaml
version: "1.0"
created: "2026-01-14"
updated: "2026-01-14"
author: "Claude"
purpose: "주식/ETF 데이터 환각 방지 표준화"
dependencies:
  - mcp_exa_web_search_exa
  - mcp_websearch_web_search_exa
  - WebFetch
consumers:
  - stock-analyzer
  - etf-analyzer
  - portfolio-builder
changes_v1.0:
  - "최초 작성"
  - "한국/미국 주식, ETF 검색 프로토콜 정의"
  - "original_text 필수화"
  - "2개 출처 교차검증 (±5% 허용)"
```
