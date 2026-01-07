# Chapter 2 웹 검색 가이드

이 문서는 Chapter 2 작성을 위한 시장, 기술, 특허 정보 검색 전략을 제공한다.

---

## 1. 검색 영역 개요

| 영역 | 검색 목적 | 수집 항목 | 목표 건수 |
|------|----------|---------|----------|
| 시장 규모 | 국내외 시장 규모 및 전망 파악 | 시장 규모, CAGR, 전망치, 지역별 점유율 | 5-10건 |
| 기업 동향 | 선도기업 현황 및 기술 사례 수집 | 기업별 제품/서비스, 성과, M&A | 15-25건 |
| 기술 동향 | 최신 기술 트렌드 파악 | 기술 발전 현황, 적용 사례 | 10-15건 |
| 특허 분석 | 특허 출원 동향 및 핵심 특허 분석 | 출원 동향, 국가별 비중, 핵심 특허 | 10-20건 |

---

## 2. 시장 규모 검색

### 2.1 국내 시장

#### 검색어 템플릿

```
[기본 검색어]
"[분야] 국내 시장 규모 2024"
"[기술] 한국 시장 전망 2030"
"[분야] 국내 시장 성장률 CAGR"
"[분야] 국내 시장 현황 보고서"

[조사기관별 검색어]
"KISTEP [분야] 시장 보고서"
"KIET [분야] 산업 동향"
"KEIT [기술] 시장 분석"
"ETRI [분야] 기술 동향"
"IITP [분야] 시장 동향"
"정보통신기획평가원 [기술] 보고서"

[사이트 검색]
site:kistep.re.kr [분야]
site:kiet.re.kr [분야] 시장
site:keit.re.kr [기술]
site:iitp.kr [분야]
site:nia.or.kr [기술]
```

#### 수집 항목

```yaml
market_data:
  current_size: "20XX년 XX억 원 / XX억 달러"
  cagr: "연평균 XX% 성장"
  forecast: "20XX년 XX억 원 / XX억 달러 전망"
  source:
    report_name: "보고서명"
    institution: "조사기관"
    year: "발행연도"
    url: "접근 URL"
```

### 2.2 글로벌 시장

#### 검색어 템플릿

```
[기본 검색어]
"[기술] global market size 2024 2025"
"[분야] market forecast 2030"
"[기술] market growth rate CAGR"
"[분야] market research report"

[조사기관별 검색어]
"IDC [분야] market forecast"
"Gartner [기술] market size"
"MarketsandMarkets [분야] report"
"Frost & Sullivan [기술] analysis"
"Statista [분야] market"
"Grand View Research [기술]"
"Precedence Research [분야]"
"Fortune Business Insights [기술]"
"Cognitive Market Research [분야]"
"Verified Market Research [기술]"
"Allied Market Research [분야]"

[산업별 검색어]
"[분야] manufacturing market size"
"[기술] financial services market"
"[분야] healthcare industry market"
```

#### 수집 항목

```yaml
global_market_data:
  total_size: "20XX년 XX억 달러"
  cagr: "CAGR XX%"
  forecast: "20XX년 XX억 달러"
  regional_share:
    north_america: "XX%"
    europe: "XX%"
    asia_pacific: "XX%"
  industry_breakdown:
    - industry: "[산업1]"
      size: "XX억 달러"
    - industry: "[산업2]"
      size: "XX억 달러"
  source:
    report_name: "보고서명"
    institution: "조사기관"
    year: "발행연도"
```

### 2.3 국가별 시장

#### 검색어 템플릿

```
[미국]
"US [기술] market size"
"United States [분야] market forecast"
"North America [기술] industry"

[독일/유럽]
"Germany [분야] market"
"Europe [기술] market size"
"EU [분야] industry report"

[중국]
"China [기술] market size"
"중국 [분야] 시장 규모"
"中国 [분야] 市场"

[일본]
"Japan [기술] market"
"일본 [분야] 시장"
"日本 [분야] 市場"
```

---

## 3. 기업 동향 검색

### 3.1 국내 기업

#### 검색어 템플릿

```
[대기업]
"삼성 [분야] 솔루션"
"LG [기술] 서비스"
"SK [분야] 플랫폼"
"현대 [기술] 시스템"
"네이버 [분야]"
"카카오 [기술]"

[중견/스타트업]
"[분야] 국내 스타트업"
"[기술] 한국 벤처기업"
"[분야] 국내 기업 사례"

[기업별 검색]
"[기업명] [분야] 출시"
"[기업명] [기술] 개발"
"[기업명] IR 자료"
"[기업명] 보도자료 [분야]"
```

#### 수집 항목

```yaml
domestic_company:
  name: "기업명"
  products_services:
    - name: "제품/서비스명"
      description: "설명"
  achievements: "성과 (매출, 수상, 고객사 등)"
  outlook: "전망"
  source: "출처"
```

### 3.2 글로벌 기업

#### 검색어 템플릿

```
[빅테크]
"Microsoft [기술] solution"
"Google [분야] platform"
"Amazon [기술] service"
"OpenAI [분야]"
"Anthropic [기술]"

[산업별 선도기업]
"Siemens [분야]"
"SAP [기술]"
"Oracle [분야]"
"IBM [기술]"
"Autodesk [분야]"
"Dassault [기술]"
"PTC [분야]"
"ANSYS [기술]"

[기업 정보]
"[기업명] annual report"
"[기업명] investor relations"
"[기업명] press release [분야]"
"[기업명] [기술] case study"
```

### 3.3 M&A 동향

#### 검색어 템플릿

```
"[분야] acquisition 2024"
"[기술] merger 2023 2024"
"[분야] M&A 동향"
"[기업명] acquires [기술]"
"[분야] partnership announcement"
"[기술] strategic alliance"
```

#### 수집 항목

```yaml
ma_info:
  acquirer: "인수 기업"
  target: "피인수 기업"
  type: "인수/합병/파트너십"
  value: "거래 금액"
  year: "연도"
  expected_benefit: "기대 효과"
  source: "출처"
```

---

## 4. 기술 동향 검색

### 4.1 기술 트렌드

#### 검색어 템플릿

```
[일반 트렌드]
"[기술] technology trend 2024 2025"
"[분야] innovation 2024"
"[기술] development roadmap"
"[분야] future outlook"

[기술 적용]
"[기술] enterprise adoption"
"[분야] industry application"
"[기술] use case"
"[분야] implementation example"

[기술 수준]
"[기술] TRL technology readiness level"
"[분야] 기술 수준 비교"
"[기술] maturity assessment"
```

### 4.2 연구기관/대학 동향

#### 검색어 템플릿

```
[국내 연구기관]
"ETRI [분야] 연구"
"KIST [기술] 개발"
"KAIST [분야] 논문"
"서울대 [기술] 연구"

[해외 연구기관]
"MIT [기술] research"
"Stanford [분야] study"
"Carnegie Mellon [기술]"
"Technical University Munich [분야]"
"Fraunhofer [기술]"
```

---

## 5. 특허 분석 검색

### 5.1 특허 동향

#### 검색어 템플릿

```
[특허 동향]
"[분야] patent analysis"
"[기술] 특허 출원 동향"
"[분야] patent landscape"
"[기술] IP trend"

[국가별 특허]
"[분야] US patent"
"[기술] 중국 특허"
"[분야] 일본 특허"
"[기술] EPO patent"

[기업별 특허]
"[기업명] [분야] patent"
"[기업명] [기술] IP portfolio"
```

### 5.2 특허 데이터베이스

#### 검색 사이트

```
[국내]
- KIPRIS (특허정보넷): https://www.kipris.or.kr
- KIPO (특허청): https://www.kipo.go.kr

[해외]
- Google Patents: https://patents.google.com
- USPTO: https://www.uspto.gov
- EPO Espacenet: https://worldwide.espacenet.com
- WIPO: https://www.wipo.int
```

#### 수집 항목

```yaml
patent_analysis:
  yearly_trend:
    - year: "20XX"
      count: "XX건"
  country_share:
    - country: "미국"
      percentage: "XX%"
    - country: "중국"
      percentage: "XX%"
  technology_classification:
    - technology: "[기술A]"
      count: "XX건"
  key_patents:
    - patent_number: "특허번호"
      title: "특허명"
      applicant: "출원인"
      year: "출원연도"
      summary: "핵심 내용 요약"
```

---

## 6. 출처 우선순위

### 1순위: 글로벌 조사기관

| 기관 | 전문 분야 | 신뢰도 |
|------|---------|-------|
| IDC | IT/소프트웨어/AI | 최상 |
| Gartner | IT/엔터프라이즈 | 최상 |
| MarketsandMarkets | 전 산업 | 상 |
| Frost & Sullivan | 기술/산업 | 상 |
| Statista | 통계 데이터 | 상 |
| Grand View Research | 전 산업 | 상 |
| Precedence Research | 전 산업 | 상 |
| Fortune Business Insights | 전 산업 | 상 |
| Cognitive Market Research | 전 산업 | 상 |
| Verified Market Research | 전 산업 | 상 |
| Allied Market Research | 전 산업 | 상 |

### 2순위: 공인 연구기관

| 기관 | 전문 분야 | 신뢰도 |
|------|---------|-------|
| KISTEP | 과학기술정책 | 최상 |
| KIET | 산업경제 | 최상 |
| KEIT | 산업기술 | 최상 |
| ETRI | ICT/전자 | 최상 |
| IITP (정보통신기획평가원) | ICT/SW/AI | 최상 |
| KISTI | 과학기술정보 | 상 |
| KIEP | 국제경제 | 상 |
| NIA (한국지능정보사회진흥원) | 디지털/AI | 상 |

### 3순위: 기업 공식 자료

- 기업 보도자료
- IR(투자자 관계) 자료
- 기술 백서(White Paper)
- 연례 보고서(Annual Report)

### 4순위: 학술/특허

- IEEE, ACM 학술 논문
- Nature, Science 논문
- 특허청 KIPRIS
- Google Patents

### 5순위: 전문 매체

- ZDNet, TechCrunch
- 전자신문, 디지털타임스
- 매일경제, 한국경제

---

## 7. 검색 실행 순서

### Step 1: 키워드 정의

Chapter 3와 Chapter 1에서 추출한 키워드로 검색어 구성

```
[예시]
기술 분야: AI Agent, 생성형 AI
적용 산업: 제조업, 엔지니어링
주요 키워드: 설계 자동화, LLM, 협업 플랫폼
```

### Step 2: 시장 규모 검색 (5-10건)

1. 글로벌 시장 규모 (IDC, MarketsandMarkets)
2. 국내 시장 규모 (KISTEP, KIET)
3. 산업별 시장 세분화
4. 지역별 시장 점유율

### Step 3: 기업 동향 검색 (15-25건)

1. 글로벌 선도기업 (10개 이상)
2. 국내 주요 기업 (5개 이상)
3. M&A 동향 (5건 이상)

### Step 4: 기술 동향 검색 (10-15건)

1. 기술 트렌드
2. 기술 적용 사례
3. 연구기관/대학 동향

### Step 5: 특허 분석 검색 (10-20건)

1. 연도별 출원 동향
2. 국가별 비중
3. 기술별 분류
4. 핵심 특허 (10-20건)

---

## 8. 데이터 기록 형식

### 시장 데이터

```markdown
## 시장 조사 결과

### 글로벌 시장

| 항목 | 데이터 | 출처 |
|------|-------|------|
| 시장 규모 (2024) | XX억 달러 | IDC, 2024 |
| CAGR | XX% | IDC, 2024 |
| 전망 (2030) | XX억 달러 | IDC, 2024 |
| 북미 점유율 | XX% | MarketsandMarkets, 2024 |
```

### 기업 데이터

```markdown
## 기업 동향 조사 결과

### 글로벌 기업

| 기업명 | 제품/서비스 | 성과 | 출처 |
|--------|-----------|------|------|
| Microsoft | Copilot | XX억 달러 매출 | 연례보고서, 2024 |
```

### 특허 데이터

```markdown
## 특허 분석 결과

### 출원 동향

| 연도 | 출원 건수 |
|------|---------|
| 2020 | XX건 |
| 2021 | XX건 |
| 2022 | XX건 |
| 2023 | XX건 |
| 2024 | XX건 |

### 핵심 특허

| 특허번호 | 특허명 | 출원인 | 연도 | 핵심 내용 |
|---------|-------|-------|------|---------|
| US20XX... | [특허명] | [기업명] | 20XX | [요약] |
```

---

## 9. 검색 시 주의사항

1. 최신 데이터 우선 (2023-2025년)
2. 공식 출처만 사용 (개인 블로그 배제)
3. 데이터 교차 검증 (2개 이상 출처 확인)
4. URL 기록 필수
5. 한글/영문 병행 검색으로 포괄적 수집
