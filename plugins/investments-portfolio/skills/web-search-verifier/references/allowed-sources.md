# 허용 출처 목록 (Allowlist)

web-search-verifier 스킬에서 사용 가능한 출처 상세 목록입니다.

---

## Tier 1: 공식 출처 (Primary Sources)

> **필수**: 모든 데이터 수집에 최소 1개 Tier 1 출처 포함 필수

### 미국 금융 데이터

| 출처 | URL | 데이터 유형 | 우선순위 |
|:-----|:----|:-----------|:--------:|
| FRED (St. Louis Fed) | fred.stlouisfed.org | S&P 500, 금리, 경제지표 | 1 |
| Federal Reserve | federalreserve.gov | 기준금리, FOMC 성명 | 1 |
| SEC EDGAR | sec.gov/edgar | 기업 공시 | 1 |

### 한국 금융 데이터

| 출처 | URL | 데이터 유형 | 우선순위 |
|:-----|:----|:-----------|:--------:|
| 한국거래소 (KRX) | krx.co.kr | KOSPI, KOSDAQ | 1 |
| 한국은행 | bok.or.kr | 기준금리, 경제통계 | 1 |
| 금융감독원 | fss.or.kr | 금융통계 | 1 |

### 글로벌 금융 데이터

| 출처 | URL | 데이터 유형 | 우선순위 |
|:-----|:----|:-----------|:--------:|
| Bloomberg | bloomberg.com | 글로벌 시장 | 1 |
| IMF | imf.org | 글로벌 경제 전망 | 1 |
| World Bank | worldbank.org | 경제 개발 지표 | 1 |

---

## Tier 2: 교차검증 출처 (Secondary Sources)

> **권장**: Tier 1과 함께 교차검증에 사용

### 금융 데이터 플랫폼

| 출처 | URL | 강점 | 우선순위 |
|:-----|:----|:-----|:--------:|
| Trading Economics | tradingeconomics.com | 글로벌 지수, 환율, 금리 | 2 |
| Investing.com | investing.com | 실시간 시세, 글로벌 커버리지 | 2 |
| Yahoo Finance | finance.yahoo.com | 미국 주식, 지수 | 2 |
| MarketWatch | marketwatch.com | 미국 시장 뉴스 | 2 |
| CNBC | cnbc.com | 미국 금융 뉴스 | 2 |

### 환율 데이터

| 출처 | URL | 강점 | 우선순위 |
|:-----|:----|:-----|:--------:|
| XE.com | xe.com | 실시간 환율 | 2 |
| OANDA | oanda.com | 외환 데이터 | 2 |

---

## Tier 3: 보조 출처 (Tertiary Sources)

> **참고용**: Tier 1-2 불충분 시 보조

### 한국 언론

| 출처 | URL | 강점 | 우선순위 |
|:-----|:----|:-----|:--------:|
| 연합뉴스 | yna.co.kr | 한국 경제 속보 | 3 |
| 한국경제 | hankyung.com | 한국 금융 시장 | 3 |
| 매일경제 | mk.co.kr | 한국 경제 뉴스 | 3 |
| 서울경제 | sedaily.com | 한국 금융 | 3 |

### 글로벌 언론

| 출처 | URL | 강점 | 우선순위 |
|:-----|:----|:-----|:--------:|
| Reuters | reuters.com | 글로벌 금융 뉴스 | 3 |
| Financial Times | ft.com | 글로벌 금융 분석 | 3 |
| Wall Street Journal | wsj.com | 미국 금융 | 3 |

---

## Blocklist: 금지 출처

> **절대 금지**: 아래 유형의 출처는 사용 불가

### 금지 유형

| 유형 | 이유 | 예시 |
|:-----|:-----|:-----|
| 개인 블로그 | 신뢰도 미검증 | tistory, naver blog, medium 개인 글 |
| 위키피디아 | 실시간 데이터 부정확 | wikipedia.org (실시간 지수용) |
| 커뮤니티 | 비전문가 의견 | reddit, 네이버 카페, DC인사이드 |
| 소셜미디어 | 확인 불가 | twitter/X, facebook |
| 뉴스 집계 사이트 | 원본 출처 불분명 | google news 집계 결과 |
| AI 생성 콘텐츠 | 환각 위험 | ChatGPT 생성 텍스트 |

### 특별 주의

| 출처 | 허용/금지 | 조건 |
|:-----|:----------|:-----|
| 위키피디아 | 조건부 허용 | 역사적 사실만 (실시간 데이터 X) |
| 뉴스 기사 | 허용 | Tier 3 언론사 + 기자 실명 기사만 |
| 리서치 리포트 | 허용 | 기관/투자은행 공식 발간물만 |

---

## 출처 검증 체크리스트

데이터 수집 시 아래 항목 확인:

### Tier 1 출처 확인
- [ ] 공식 기관/거래소 웹사이트인가?
- [ ] URL이 공식 도메인(.gov, .or.kr, .com 공식)인가?
- [ ] 데이터 발행 기관이 명시되어 있는가?

### Tier 2-3 출처 확인
- [ ] 허용 출처 목록에 포함되어 있는가?
- [ ] 데이터 갱신 일자가 7일 이내인가?
- [ ] 원본 출처(Tier 1)를 인용하고 있는가?

### Blocklist 확인
- [ ] 개인 블로그/커뮤니티가 아닌가?
- [ ] 위키피디아에서 실시간 데이터를 가져오지 않았는가?
- [ ] AI 생성 콘텐츠가 아닌가?

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|:----:|:----:|:----------|
| 1.0 | 2026-01-12 | 최초 작성 |
