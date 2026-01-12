---
name: web-search-verifier
description: "3개 출처 교차검증 웹검색 프로토콜. 환각 방지 첫 번째 방어선. 모든 거시경제 데이터 수집 시 필수 사용."
tools: exa_web_search_exa, websearch_web_search_exa, WebFetch
---

# 웹검색 교차검증 스킬

## Overview

이 스킬은 거시경제 데이터(지수, 금리, 환율) 수집 시 **환각을 방지**하기 위한 표준 프로토콜입니다.
모든 수치 데이터는 이 스킬을 통해 **3개 이상의 독립 출처에서 교차 검증** 후에만 사용 가능합니다.

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

---

## 검색 프로토콜

### 1. 지수 데이터 검색

**함수**: `search_index(index_name)`

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

**출력 스키마**:
```json
{
  "index": "S&P 500",
  "value": 6966.28,
  "unit": "pt",
  "date": "2026-01-09",
  "verified": true,
  "variance": "0.01%",
  "sources": [
    {"name": "Trading Economics", "url": "https://...", "value": 6966.70, "tier": 2},
    {"name": "Bloomberg", "url": "https://...", "value": 6966.28, "tier": 1},
    {"name": "Yahoo Finance", "url": "https://...", "value": 6966.28, "tier": 2}
  ]
}
```

### 2. 금리 데이터 검색

**함수**: `search_rate(rate_type)`

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

**출력 스키마**:
```json
{
  "rate_type": "fed_funds",
  "value": "4.25-4.50%",
  "decision_date": "2025-12-18",
  "next_meeting": "2026-01-29",
  "verified": true,
  "sources": [
    {"name": "Federal Reserve", "url": "https://...", "value": "4.25-4.50%", "official": true},
    {"name": "Trading Economics", "url": "https://...", "value": "4.25%", "official": false}
  ]
}
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

1. web-search-verifier 스킬 로드 확인
2. S&P 500 수집:
   - search_index("S&P 500") 호출
   - verified: true 확인
   - 결과 사용
3. KOSPI 수집:
   - search_index("KOSPI") 호출
   - verified: true 확인
   - 결과 사용

## 검증 실패 시

verified: false인 경우:
- 해당 지수는 "데이터 수집 실패" 명시
- 추정값 생성 금지
- 에러 코드 전달
```

---

## 리소스

- `references/allowed-sources.md`: 허용 출처 상세 목록
- `references/search-patterns.md`: 검색 쿼리 패턴 상세

---

## 메타 정보

```yaml
version: "1.0"
created: "2026-01-12"
author: "Claude"
purpose: "환각 방지 웹검색 표준화"
dependencies:
  - exa_web_search_exa
  - websearch_web_search_exa
  - WebFetch
consumers:
  - index-fetcher
  - rate-analyst
  - sector-analyst
```
