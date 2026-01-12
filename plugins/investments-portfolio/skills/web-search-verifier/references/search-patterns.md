# 검색 쿼리 패턴

web-search-verifier 스킬에서 사용하는 검색 쿼리 패턴 상세입니다.

---

## 지수 데이터 검색 패턴

### S&P 500

```
# 패턴 1: 글로벌 금융 사이트
"S&P 500 price today site:investing.com OR site:bloomberg.com"

# 패턴 2: 금융 데이터 사이트
"S&P 500 index site:tradingeconomics.com"

# 패턴 3: 시세 사이트
"S&P 500 quote site:finance.yahoo.com OR site:marketwatch.com"
```

### NASDAQ

```
# 패턴 1: 글로벌 금융 사이트
"NASDAQ Composite price today site:investing.com OR site:bloomberg.com"

# 패턴 2: 금융 데이터 사이트
"NASDAQ index site:tradingeconomics.com"

# 패턴 3: 시세 사이트
"NASDAQ quote site:finance.yahoo.com OR site:marketwatch.com"
```

### KOSPI

```
# 패턴 1: 한국 뉴스
"코스피 종가 site:yna.co.kr OR site:hankyung.com"

# 패턴 2: 글로벌 금융 사이트
"KOSPI index site:investing.com OR site:bloomberg.com"

# 패턴 3: 금융 데이터 사이트
"KOSPI site:tradingeconomics.com"
```

### KOSDAQ

```
# 패턴 1: 한국 뉴스
"코스닥 종가 site:yna.co.kr OR site:hankyung.com"

# 패턴 2: 글로벌 금융 사이트
"KOSDAQ index site:investing.com"

# 패턴 3: 금융 데이터 사이트
"KOSDAQ site:tradingeconomics.com"
```

### USD/KRW 환율

```
# 패턴 1: 환율 전문 사이트
"USD KRW exchange rate site:xe.com OR site:oanda.com"

# 패턴 2: 글로벌 금융 사이트
"USD/KRW site:investing.com OR site:bloomberg.com"

# 패턴 3: 금융 데이터 사이트
"USD KRW site:tradingeconomics.com"
```

---

## 금리 데이터 검색 패턴

### 미국 기준금리 (Fed Funds Rate)

```
# 패턴 1: 공식 출처 (필수)
"federal funds rate site:federalreserve.gov"
"FOMC target rate site:federalreserve.gov"

# 패턴 2: 교차검증 출처
"fed funds rate site:tradingeconomics.com"
"US interest rate site:bloomberg.com"

# 패턴 3: 경제 데이터
"federal funds effective rate site:fred.stlouisfed.org"
```

### 한국 기준금리 (BOK Base Rate)

```
# 패턴 1: 공식 출처 (필수)
"기준금리 site:bok.or.kr"
"한국은행 기준금리 현재"

# 패턴 2: 교차검증 출처
"korea interest rate site:tradingeconomics.com"
"south korea base rate site:bloomberg.com"

# 패턴 3: 한국 뉴스
"기준금리 금통위 site:yna.co.kr"
```

### 미국 10년물 국채 금리

```
# 패턴 1: 공식 데이터
"10 year treasury yield site:fred.stlouisfed.org"

# 패턴 2: 글로벌 금융 사이트
"US 10 year treasury yield site:investing.com OR site:bloomberg.com"

# 패턴 3: 금융 데이터 사이트
"United States 10Y Treasury site:tradingeconomics.com"
```

---

## 검색 최적화 팁

### 날짜 필터링

최신 데이터 확보를 위해 날짜 필터 사용:

```
# Google 검색 날짜 필터
"S&P 500 closing price" after:2026-01-01

# 특정 기간 검색
"KOSPI 종가" daterange:2459946-2459953
```

### 정확한 수치 검색

```
# 따옴표로 정확한 구문 검색
"S&P 500: 6,966"
"KOSPI 4,586"

# 숫자 범위 검색
"S&P 500" "6,900..7,000"
```

### 다국어 검색

```
# 한국어 + 영어 병행
("코스피" OR "KOSPI") 종가 2026
("기준금리" OR "base rate") 한국 2026
```

---

## 검색 결과 파싱

### 수치 추출 패턴

```
지수 수치 추출:
- 정규식: /(\d{1,3}(,\d{3})*(\.\d+)?)\s*(pt|points?)?/
- 예시: "6,966.28 pt" → 6966.28

금리 수치 추출:
- 정규식: /(\d+(\.\d+)?)\s*%/
- 예시: "4.25%" → 4.25
- 범위 정규식: /(\d+(\.\d+)?)\s*[-–]\s*(\d+(\.\d+)?)\s*%/
- 예시: "4.25-4.50%" → (4.25, 4.50)

환율 수치 추출:
- 정규식: /(\d{1,3}(,\d{3})*(\.\d+)?)\s*(KRW|원)?/
- 예시: "1,410.50" → 1410.50
```

### 날짜 추출 패턴

```
날짜 추출:
- ISO 형식: /\d{4}-\d{2}-\d{2}/
- 한국어: /\d{4}년\s*\d{1,2}월\s*\d{1,2}일/
- 영어: /(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s*\d{4}/
```

---

## 검증 로직

### 교차 검증 알고리즘

```python
def cross_verify(values, tolerance=0.01):
    """
    3개 출처 값 교차검증
    
    Args:
        values: [v1, v2, v3] - 3개 출처의 값
        tolerance: 허용 오차 (기본 1%)
    
    Returns:
        (verified, consensus_value, variance)
    """
    if len(values) < 3:
        return (False, None, "INSUFFICIENT_SOURCES")
    
    # 평균값 계산
    avg = sum(values) / len(values)
    
    # 최대 편차 계산
    max_deviation = max(abs(v - avg) / avg for v in values)
    
    if max_deviation <= tolerance:
        return (True, avg, f"{max_deviation*100:.2f}%")
    else:
        return (False, None, f"VALUE_MISMATCH: {max_deviation*100:.2f}%")
```

### 1차 출처 확인

```python
def has_primary_source(sources):
    """
    Tier 1 출처 포함 여부 확인
    """
    tier1_domains = [
        "fred.stlouisfed.org",
        "federalreserve.gov",
        "krx.co.kr",
        "bok.or.kr",
        "bloomberg.com"
    ]
    
    for source in sources:
        for domain in tier1_domains:
            if domain in source.get("url", ""):
                return True
    
    return False
```

---

## 에러 처리

### 검색 실패 시

```
재시도 전략:
1. 첫 번째 실패: 다른 검색 패턴으로 재시도
2. 두 번째 실패: 검색 쿼리 단순화 후 재시도
3. 세 번째 실패: FAIL 반환, 수동 확인 요청

타임아웃:
- 검색 요청: 10초
- 전체 검증: 60초
```

### 출처 불일치 시

```
대응 전략:
1. 편차 1~5%: 범위로 표현 (min~max)
2. 편차 5~10%: 1차 출처 우선, 불일치 경고
3. 편차 10%+: FAIL 반환, 수동 확인 요청
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|:----:|:----:|:----------|
| 1.0 | 2026-01-12 | 최초 작성 |
