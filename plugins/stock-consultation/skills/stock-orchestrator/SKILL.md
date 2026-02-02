---
name: stock-orchestrator
description: "주식/ETF 투자 상담 오케스트레이션 스킬. 메인 에이전트가 5개 서브에이전트를 순서대로 호출하여 Multi-agent 워크플로우를 실행하도록 안내합니다."
---

# 주식/ETF 투자 상담 오케스트레이션 스킬

이 스킬은 **메인 에이전트**가 주식/ETF 투자 상담을 오케스트레이션하는 방법을 안내합니다.

**핵심 원칙**: 메인 에이전트가 직접 분석하지 않고, Task 도구로 전문 서브에이전트를 호출합니다.

---

## 1. 워크플로우 개요

```
[사용자 요청: "삼성전자 분석해줘" / "AI 관련 ETF 추천해줘"]
     │
     ▼
[Step 0] 거시경제 분석 (macro-analysis 에이전트 재사용)
     ├── Step 0.1: index-fetcher 호출 (지수 데이터 수집)
     ├── Step 0.2: 3개 에이전트 병렬 호출
     │   ├── rate-analyst (금리/환율)
     │   ├── sector-analyst (섹터 전망)
     │   └── risk-analyst (리스크 시나리오)
     ├── Step 0.3: macro-synthesizer 호출 (거시경제 종합)
     ├── Step 0.4: macro-critic 호출 (검증)
     ├── Step 0.5: perspective-balance 호출 (Bull/Bear 균형 검증)
     └── Step 0.6: materials-organizer 호출 (옵션 - materials_path 제공 시)
     │
     ▼
[Step 1] stock-screener 호출 (종목 스크리닝 - 포트폴리오인 경우)
     │
     ▼
[Step 2] stock-valuation 호출 (밸류에이션 분석)
     │
     ▼
[Step 2.5] devil-advocate 호출 (가정 도전 및 시나리오 역전)
     │
     ▼
[Step 3] bear-case-critic 호출 (리스크 분석)
     │
     ▼
[Step 4] stock-critic 호출 (최종 검증)
     │
     ▼
[Step 5] 최종 상담 보고서 조합
```

---

## 2. 핵심 규칙 (CRITICAL)

### 2.1 직접 분석 금지 (Zero Tolerance)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⚠️ 절대 금지 사항 ⚠️                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 직접 웹검색 수행하기                                          │
│  ❌ 직접 종목 데이터 수집하기                                     │
│  ❌ 직접 밸류에이션 계산하기                                      │
│  ❌ 서브에이전트 결과를 "생성"하기 (환각)                        │
│  ❌ Task 호출 없이 결과 반환하기                                  │
│                                                                 │
│  ✅ 반드시 Task 도구로 서브에이전트 호출                         │
│  ✅ 서브에이전트 결과를 그대로 인용                              │
│  ✅ 결과 조합만 수행                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 서브에이전트 목록 (13개)

**거시경제 분석 에이전트 (macro-analysis에서 재사용):**

| 에이전트 | subagent_type | 역할 |
|----------|---------------|------|
| index-fetcher | `macro-analysis:index-fetcher` | 지수 데이터 수집 (3개 출처 교차 검증) |
| rate-analyst | `macro-analysis:rate-analyst` | 금리/환율 전망 분석 |
| sector-analyst | `macro-analysis:sector-analyst` | 섹터별 전망 (5개 섹터) |
| risk-analyst | `macro-analysis:risk-analyst` | 리스크 분석 및 시나리오 |
| macro-synthesizer | `macro-analysis:macro-synthesizer` | 거시경제 최종 보고서 작성 |
| macro-critic | `macro-analysis:macro-critic` | 거시경제 분석 검증 (지수 데이터 일치성) |

**재사용 스킬 (investments-portfolio에서 재사용):**

| 스킬 | subagent_type | 역할 |
|------|---------------|------|
| perspective-balance | `perspective-balance` | Bull/Bear 균형 분석 (시나리오 확률 검증) |
| devil-advocate | `devil-advocate` | 악마의 변호인 (가정 도전 및 시나리오 역전) |

**종목 분석 에이전트 (stock-consultation 전용):**

| 에이전트 | subagent_type | 역할 |
|----------|---------------|------|
| materials-organizer | `materials-organizer` | 사용자 제공 마크다운 자료 정리 (요약/분류/키포인트) |
| stock-screener | `stock-screener` | 종목 스크리닝 (섹터/테마/밸류에이션 기준) |
| stock-valuation | `stock-valuation` | 개별 종목 밸류에이션 분석 (PER/PBR/PEG) |
| bear-case-critic | `bear-case-critic` | 반대 논거 전문가 (리스크 분석) |
| stock-critic | `stock-critic` | 최종 검증 (환각 방지, 과신 표현 탐지) |

---

## 3. 세션 폴더 생성

상담 요청 시작 전 반드시 전용 폴더를 생성합니다:

```
consultations/YYYY-MM-DD-{ticker}-{session_id}/

예시: consultations/2026-01-14-TSLA-a1b2c3/
```

**포트폴리오 요청 시:**
```
consultations/YYYY-MM-DD-portfolio-{theme}-{session_id}/

예시: consultations/2026-01-14-portfolio-AI-a1b2c3/
```

---

## 4. Step별 Task 호출 템플릿

### Step 0: 거시경제 분석 (6-Agent 워크플로우)

> **중요**: 모든 주식/ETF 상담 시 반드시 거시경제 분석을 먼저 수행합니다.
> macro-analysis 플러그인의 6개 에이전트를 재사용합니다.

#### Step 0.1: index-fetcher

```
Task(
  subagent_type="macro-analysis:index-fetcher",
  description="지수 데이터 수집 (3개 출처 교차 검증)",
  prompt="""
## 지수 데이터 수집 요청

### 수집 대상 지수
1. 미국: S&P 500, NASDAQ, Russell 2000
2. 한국: KOSPI, KOSDAQ
3. 신흥국: MSCI Emerging Markets
4. 채권: US Treasury 10Y, 한국 국채 10Y
5. 환율: USD/KRW

### 출력 경로
output_path: {session_folder}

### 요구사항
- 3개 출처 교차 검증 필수
- JSON 파일로 저장: index-data.json

**FAIL 시**: 워크플로우 중단
"""
)
```

#### Step 0.2: 3개 에이전트 병렬 호출

**병렬로 동시 호출합니다:**

```
# rate-analyst
Task(
  subagent_type="macro-analysis:rate-analyst",
  description="금리/환율 전망 분석",
  prompt="""
## 금리/환율 전망 분석 요청

### 분석 항목
1. 미국 기준금리 전망 (Fed 정책)
2. 한국 기준금리 전망 (BOK 정책)
3. 환율 전망 (USD/KRW)

### 출력 경로
output_path: {session_folder}

### 출력 파일
rate-analysis.json
"""
)

# sector-analyst
Task(
  subagent_type="macro-analysis:sector-analyst",
  description="섹터별 전망 분석",
  prompt="""
## 섹터별 전망 분석 요청

### 분석 대상 섹터 (5개)
1. 반도체 (AI 칩 수요)
2. 에너지 (유가, 재생에너지)
3. 금융 (금리 민감도)
4. 헬스케어
5. 기술 (소프트웨어, 클라우드)

### 출력 경로
output_path: {session_folder}

### 출력 파일
sector-analysis.json
"""
)

# risk-analyst
Task(
  subagent_type="macro-analysis:risk-analyst",
  description="리스크 분석 및 시나리오",
  prompt="""
## 리스크 분석 요청

### 분석 항목
1. 지정학적 리스크
2. 경제 리스크
3. 시장 리스크

### 시나리오 분석
- Bull 시나리오 (20%)
- Base 시나리오 (60%)
- Bear 시나리오 (20%)

### 출력 경로
output_path: {session_folder}

### 출력 파일
risk-analysis.json
"""
)
```

#### Step 0.3: macro-synthesizer

**Step 0.2 완료 후 호출:**

```
Task(
  subagent_type="macro-analysis:macro-synthesizer",
  description="거시경제 최종 보고서 작성",
  prompt="""
## 거시경제 최종 보고서 작성 요청

### 입력 파일 (직접 Read 필수)
- {session_folder}/index-data.json
- {session_folder}/rate-analysis.json
- {session_folder}/sector-analysis.json
- {session_folder}/risk-analysis.json

### 출력 경로
output_path: {session_folder}

### 출력 파일
00-macro-outlook.md

### 요구사항
- 모든 수치는 JSON 파일에서 그대로 복사
- 주목 섹터 및 리스크 요인 포함
"""
)
```

#### Step 0.4: macro-critic

```
Task(
  subagent_type="macro-analysis:macro-critic",
  description="거시경제 분석 검증",
  prompt="""
## 거시경제 분석 검증 요청

### 검증 대상 파일
- {session_folder}/index-data.json
- {session_folder}/00-macro-outlook.md

### 검증 항목
1. 지수 데이터 일치성
2. 논리 일관성
3. 출처 검증

### PASS/FAIL 반환
FAIL 시 → macro-synthesizer 재호출 (최대 2회)
"""
)
```

#### Step 0.5: materials-organizer (옵션)

**materials_path 제공 시에만 실행:**

```
Task(
  subagent_type="materials-organizer",
  description="사용자 제공 자료 정리 (요약/분류/키포인트)",
  prompt="""
## 자료 정리 요청

### 입력 경로
materials_path: {user_provided_materials_path}

### 분석 항목
1. 마크다운 파일 요약
2. 자료 분류 (테마별/섹터별)
3. 핵심 키포인트 추출

### 출력 경로
output_path: {session_folder}

### 출력 파일
00-materials-summary.md
"""
)
```

### Step 1: stock-screener

**포트폴리오 요청인 경우에만 실행**

```
Task(
  subagent_type="stock-screener",
  description="종목 스크리닝 (섹터/테마/밸류에이션 기준)",
  prompt="""
## 종목 스크리닝 요청

### 스크리닝 조건
- 테마/섹터: {user_specified_theme}
- 자산 유형: {korean_stock|us_stock|etf}
- 목표 종목 수: {N}

### 스크리닝 기준 (최대 10개)
한국주식: PER, PBR, ROE, 부채비율, 시가총액
미국주식: P/E, P/B, ROE, Debt/Equity, Market Cap
ETF: TER, AUM, 추적오차, 거래량

### 거시경제 컨텍스트
{macro_outlook_summary}
- 주목 섹터: {recommended_sectors}
- 지역 배분: {region_allocation}

### 출력 경로
output_path: {session_folder}

### 출력 파일
01-stock-screening.md

### 출력 형식
JSON:
{
  "status": "PASS|FAIL",
  "verified": true|false,
  "skill_used": "stock-data-verifier",
  "candidates": [
    {
      "ticker": "005930",
      "name": "삼성전자",
      "market": "KRX",
      "metrics": {
        "per": {"value": 12.5, "original_text": "...", "source": "네이버 금융"},
        "pbr": {"value": 1.2, "original_text": "...", "source": "..."},
        "roe": {"value": 15.3, "original_text": "...", "source": "..."}
      },
      "screening_score": 85
    }
  ],
  "issues": []
}
"""
)
```

### Step 2: stock-valuation

**단일 종목 또는 스크리닝 후 후보 종목 각각에 대해 실행**

```
Task(
  subagent_type="stock-valuation",
  description="밸류에이션 분석 (PER/PBR/PEG)",
  prompt="""
## 밸류에이션 분석 요청

### 분석 대상
- 티커: {ticker}
- 종목명: {name}
- 시장: {KRX|NYSE|NASDAQ}

### 분석 항목 (단순 모델만)
- PER: 업종평균 대비 평가
- PBR: 자산가치 대비 평가
- PEG: 성장 대비 가격
- 배당수익률 (해당 시)

### 거시경제 컨텍스트
{macro_outlook_summary}
- 섹터 전망: {sector_forecast}
- 리스크 요인: {key_risks}

### 데이터 소스 (화이트리스트만)
한국: 네이버 금융, KRX, 증권사 리서치
미국: Yahoo Finance, Bloomberg, MarketWatch

### 출력 경로
output_path: {session_folder}

### 출력 파일
02-valuation-report.md

### 출력 형식
JSON:
{
  "status": "PASS|FAIL",
  "verified": true|false,
  "ticker": "005930",
  "valuation": {
    "per": {"value": 12.5, "industry_avg": 18.2, "assessment": "저평가", "original_text": "..."},
    "pbr": {"value": 1.2, "industry_avg": 2.1, "assessment": "저평가", "original_text": "..."},
    "peg": {"value": 0.8, "assessment": "적정", "original_text": "..."}
  },
  "fair_value_range": {"low": 75000, "high": 85000},
  "opinion": "현재 가격 대비 10-20% 저평가로 판단됩니다.",
  "disclaimer": "본 분석은 참고용이며, 투자 권유가 아닙니다.",
  "issues": []
}

### 금지 사항
- DCF, Monte Carlo, Sum-of-Parts 등 복잡한 모델 금지
- 구체적 목표가 제시 금지 (범위만 제시)
- 매수/매도 강력 추천 금지
"""
)
```

### Step 3: bear-case-critic

```
Task(
  subagent_type="bear-case-critic",
  description="반대 논거 전문가 (리스크 분석)",
  prompt="""
## 반대 논거 분석 요청

### 분석 대상
- 티커: {ticker}
- 종목명: {name}
- stock-valuation 결과: {valuation_result}

### 분석 항목
- 밸류에이션 리스크 (고평가 가능성)
- 업황/섹터 리스크
- 기업 고유 리스크 (경쟁, 규제, 기술 변화)
- 거시경제 역풍

### 거시경제 컨텍스트
{macro_outlook_summary}
- 리스크 요인: {identified_risks}

### 출력 경로
output_path: {session_folder}

### 출력 파일
03-bear-case.md

### 출력 형식
JSON:
{
  "status": "PASS|FAIL",
  "verified": true|false,
  "ticker": "005930",
  "bear_cases": [
    {
      "category": "밸류에이션 리스크",
      "risk": "메모리 반도체 사이클 하락 시 PER 급등 가능",
      "severity": "HIGH|MEDIUM|LOW",
      "source": "삼성증권 리서치",
      "original_text": "..."
    }
  ],
  "issues": []
}

### 금지 사항
- 일반적인 시장 비관론 금지 (분석 대상 종목에만 집중)
- 음모론적 리스크 제시 금지
- 근거 없는 리스크 나열 금지
"""
)
```

### Step 4: stock-critic

```
Task(
  subagent_type="stock-critic",
  description="최종 검증 (환각 방지, 과신 표현 탐지)",
  prompt="""
## 최종 검증 요청

### 검증 대상
- stock-screener 결과: {screener_output}
- stock-valuation 결과: {valuation_outputs}
- bear-case-critic 결과: {bear_case_outputs}

### 검증 항목
1. **original_text 검증**: 모든 숫자에 출처 존재 여부
2. **데이터 소스 검증**: 화이트리스트 준수 확인
3. **과신 표현 탐지**: "반드시", "확실히", "무조건" 등
4. **면책조항 검증**: 존재 여부
5. **보고서 길이**: 종목당 3페이지 이하

### 데이터 소스 화이트리스트
한국: 네이버 금융, KRX, 증권사 리서치 (삼성, 미래에셋, KB)
미국: Yahoo Finance, Bloomberg, MarketWatch

### 데이터 소스 블랙리스트
개인 블로그, 커뮤니티 (클리앙, 뽐뿌), 유튜브, 위키피디아

### 출력 경로
output_path: {session_folder}

### 출력 파일
04-final-verification.md

### 출력 형식
JSON:
{
  "status": "PASS|FAIL",
  "verified": true|false,
  "checks": {
    "original_text_present": {"pass": true, "missing_count": 0},
    "source_whitelist": {"pass": true, "violations": []},
    "overconfidence_phrases": {"pass": true, "detected": []},
    "disclaimer_present": {"pass": true},
    "report_length": {"pass": true, "pages": 2.5}
  },
  "confidence_score": 92,
  "issues": []
}
"""
)
```

### Step 5: 최종 상담 보고서 조합

**메인 에이전트가 직접 수행:**

```markdown
# 최종 상담 보고서 조합 (05-consultation-summary.md)

1. 모든 에이전트 결과 파일 읽기:
   - 00-macro-outlook.md
   - 00-materials-summary.md (있는 경우)
   - 01-stock-screening.md (포트폴리오인 경우)
   - 02-valuation-report.md
   - 03-bear-case.md
   - 04-final-verification.md

2. 결과 통합 (원본 그대로 인용)

3. Bogle 원칙 면책조항 추가

4. Write로 저장: {session_folder}/05-consultation-summary.md
```

---

## 5. 출력 파일 구조

| 파일명 | 생성 주체 | 설명 |
|--------|-----------|------|
| `index-data.json` | index-fetcher | 지수 데이터 (JSON) |
| `rate-analysis.json` | rate-analyst | 금리/환율 분석 (JSON) |
| `sector-analysis.json` | sector-analyst | 섹터 분석 (JSON) |
| `risk-analysis.json` | risk-analyst | 리스크 분석 (JSON) |
| `00-macro-outlook.md` | macro-synthesizer | 거시경제 종합 보고서 |
| `00-materials-summary.md` | materials-organizer | 자료 정리 (옵션) |
| `01-stock-screening.md` | stock-screener | 종목 스크리닝 (포트폴리오) |
| `02-valuation-report.md` | stock-valuation | 밸류에이션 분석 |
| `03-bear-case.md` | bear-case-critic | 반대 논거 |
| `04-final-verification.md` | stock-critic | 출력 검증 및 신뢰도 |
| `05-consultation-summary.md` | 메인 에이전트 | 최종 통합 보고서 |

---

## 6. 에러 처리

### FAIL 시 재시도 규칙

| 에이전트 | 최대 재시도 | FAIL 시 액션 |
|----------|:-----------:|--------------|
| index-fetcher | 3회 | 워크플로우 중단 |
| rate/sector/risk-analyst | 3회 | 해당 에이전트만 재시도 |
| macro-synthesizer | 2회 | macro-critic FAIL 시 재시도 |
| macro-critic | - | synthesizer 재호출 트리거 |
| materials-organizer | 2회 | SKIP (없어도 진행) |
| stock-screener | 3회 | 워크플로우 중단 (포트폴리오인 경우) |
| stock-valuation | 3회 | 해당 종목만 제외 후 진행 |
| bear-case-critic | 3회 | 해당 종목만 제외 후 진행 |
| stock-critic | 1회 | 경고만 표시 후 진행 |

### 거시경제 분석 실패

```
IF macro-critic.verified == false AND retry_count >= 2:
    결과에 경고 추가:
    """
    ⚠️ 거시경제 분석 검증 실패
    
    2회 재시도 후에도 검증 불가.
    상담 진행 불가능.
    
    사용자 조치:
    - 나중에 다시 시도
    - 또는 거시경제 분석 없이 단순 종목 정보만 확인
    """
```

### stock-critic 검증 실패

```
IF stock_critic.verified == false OR stock_critic.confidence_score < 50:
    결과에 면책조항 강화:
    """
    ⚠️ 데이터 검증 불완전
    
    다음 항목에서 검증 문제 발견:
    - [issues 목록]
    
    신뢰도 점수: [confidence_score]점
    
    해당 분석은 참고용으로만 사용하시고,
    투자 전 반드시 공식 증권사 및 금융기관에서 최신 정보를 확인하세요.
    """
```

### 전체 실패 시

3회 연속 실패 → 워크플로우 중단 → 사용자에게 에스컬레이션

---

## 7. 코디네이터 행동 규칙

### 7.1 필수 규칙 (MUST)

| # | 규칙 | 위반 시 |
|:-:|------|--------|
| 1 | **Task 도구로 하위 에이전트 호출** | 환각 발생, 결과 무효 |
| 2 | **순차 실행**: 거시경제 → screener → valuation → bear-case → critic | 검증 누락 |
| 3 | **실패 시 재시도**: macro-critic FAIL 시 최대 2회 재시도 | 분석 불완전 |
| 4 | **결과 원본 인용**: 에이전트 결과 수정 금지 | 데이터 왜곡 |
| 5 | **면책조항**: 모든 보고서에 필수 포함 | 철학 위반 |

### 7.2 금지 규칙 (MUST NOT)

| # | 금지 사항 | 이유 |
|:-:|----------|------|
| 1 | 직접 웹검색 수행 | stock-screener/valuation 역할 침범 |
| 2 | 직접 밸류에이션 계산 | stock-valuation 역할 침범 |
| 3 | 직접 리스크 분석 | bear-case-critic 역할 침범 |
| 4 | 직접 출처 검증 | stock-critic 역할 침범 |
| 5 | 에이전트 결과 임의 수정 | 환각 발생 |
| 6 | Task 없이 결과 생성 | 환각 발생 |
| 7 | 면책조항 생략 | 철학 위반 |

### 7.3 결과 인용 규칙

```
✅ 올바른 인용:
"stock-critic 결과: verified=true, confidence_score=92"

❌ 잘못된 인용:
"검증 완료" (출처 없이 요약)
"신뢰도 95%" (stock-critic 결과와 다른 수치)
```

---

## 8. JSON 출력 스키마

### 최종 상담 보고서 스키마

```json
{
  "consultation_id": "2026-01-14-TSLA-abc123",
  "request_type": "single_stock|portfolio",
  "status": "PASS|FAIL",
  "verified": true|false,
  
  "macro_summary": {
    /* macro-synthesizer 출력 */
  },
  
  "screening_result": {
    /* stock-screener 출력 (포트폴리오인 경우) */
  },
  
  "valuations": [
    /* stock-valuation 출력 배열 */
  ],
  
  "bear_cases": [
    /* bear-case-critic 출력 배열 */
  ],
  
  "verification": {
    /* stock-critic 출력 */
  },
  
  "final_opinion": "...",
  
  "disclaimer": "본 분석은 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.",
  
  "output_files": [
    "consultations/2026-01-14-TSLA-abc123/00-macro-outlook.md",
    "consultations/2026-01-14-TSLA-abc123/01-stock-screening.md",
    "consultations/2026-01-14-TSLA-abc123/02-valuation-report.md",
    "consultations/2026-01-14-TSLA-abc123/03-bear-case.md",
    "consultations/2026-01-14-TSLA-abc123/04-final-verification.md",
    "consultations/2026-01-14-TSLA-abc123/05-consultation-summary.md"
  ],
  
  "issues": []
}
```

---

## 8.5 환각 방지 체크리스트

모든 Step에서 확인:

- [ ] 서브에이전트 결과를 직접 "생성"하지 않았는가?
- [ ] JSON 파일이 실제로 저장되었는가?
- [ ] 수치를 원본에서 그대로 복사했는가?
- [ ] 출처가 명시되어 있는가?
- [ ] 과신 표현(반드시, 확실히)을 사용하지 않았는가?

---

## 9. 재사용 스킬 호출 규칙

### 9.1 perspective-balance 호출

**호출 시점**: macro-synthesizer 결과 수신 후

**검증 규칙**:

| 규칙 | 설명 | 위반 시 |
|------|------|--------|
| 확률 합계 100% | Bull + Base + Bear = 100% | FAIL |
| 단일 시나리오 한도 | 어떤 시나리오도 80% 초과 금지 | 경고 |
| 균형 검증 | Bull/Bear 근거 수 ±1 | 검토 |

**호출 방법**:

```
Task(
  subagent_type="perspective-balance",
  description="거시경제 분석 결과의 Bull/Bear 균형 검증",
  prompt="""
## 관점 균형 분석 요청

### 입력 파일
- {session_folder}/00-macro-outlook.md

### 검증 항목
1. Bull/Bear 시나리오 확률 합계 = 100% 확인
2. 단일 시나리오 80% 초과 여부 확인
3. Bull/Bear 근거 수 균형 검증 (±1 범위)

### 출력 파일
perspective-balance-verification.md

### 요구사항
- 확률 합계 불일치 시 FAIL
- 단일 시나리오 80% 초과 시 경고 추가
"""
)
```

### 9.2 devil-advocate 호출

**호출 시점**: stock-valuation 결과 수신 후

**역할 구분**:

```
bear-case-critic: 특정 티커의 4가지 리스크 카테고리 분석
                  (밸류에이션/업황/기업고유/거시경제)
                  → 웹검색 기반 실시간 리스크 데이터 수집

devil-advocate:   매수 결론에 대한 가정 도전 및 시나리오 역전
                  ("AI 투자 지속" 가정이 틀리면?)
                  → 논리적 반박 및 숨겨진 리스크 발굴
```

**호출 순서**:

```
stock-valuation → devil-advocate → bear-case-critic → stock-critic
                  (가정 도전)      (리스크 분석)      (최종 검증)
```

**호출 방법**:

```
Task(
  subagent_type="devil-advocate",
  description="매수 논거에 대한 체계적 반론 제기",
  prompt="""
## 악마의 변호인 분석 요청

### 분석 대상
- 티커: {ticker}
- 종목명: {name}
- stock-valuation 결과: {valuation_result}

### 분석 항목
1. **가정 도전**: 밸류에이션 분석의 핵심 가정 검토
   - "이 가정이 틀리면 어떻게 되는가?"
   - "반대 의견을 가진 전문가는 누구인가?"

2. **시나리오 역전**: 긍정적 전망의 반대 시나리오
   - "AI 투자 지속" 가정이 틀릴 경우
   - "경기 회복" 가정이 틀릴 경우

3. **숨겨진 리스크**: 표면적 분석에서 놓친 리스크
   - 확증 편향 방지
   - 다양한 관점 확보

### 출력 파일
devil-advocate-analysis.md

### 요구사항
- 의도적으로 반대 입장에서 분석
- 과신(Overconfidence) 방지
- 더 견고한 투자 판단 지원
"""
)
```

### 9.3 스킬 참조 방법

이 스킬들은 investments-portfolio에서 재사용됩니다:

- **perspective-balance**: Bull/Bear 균형 분석
  - 위치: `honeypot/plugins/investments-portfolio/skills/perspective-balance/SKILL.md`
  - 용도: 거시경제 분석 결과의 시나리오 균형 검증

- **devil-advocate**: 반대 논거 및 가정 도전
  - 위치: `honeypot/plugins/investments-portfolio/skills/devil-advocate/SKILL.md`
  - 용도: 매수 결론에 대한 체계적 반론 제기

---

## 메타 정보

```yaml
version: "1.1"
created: "2026-02-02"
updated: "2026-02-02"
purpose: "메인 에이전트가 주식/ETF 상담 Multi-Agent 워크플로우를 오케스트레이션하도록 안내"
changes:
  - "v1.1: 재사용 스킬 호출 규칙 추가 (perspective-balance, devil-advocate)"
  - "v1.0: Agent에서 Skill로 전환 - nested Task 제한 해결"
  
related_skills:
  - portfolio-orchestrator
  - stock-data-verifier
  - bear-case-analysis
  - perspective-balance (재사용)
  - devil-advocate (재사용)
  
workflow:
  step_0: "거시경제 분석 (index-fetcher → analysts → synthesizer → critic)"
  step_0.5: "materials-organizer (materials_path 제공 시, SKIP 가능)"
  step_1: "stock-screener (포트폴리오인 경우)"
  step_2: "stock-valuation (각 종목)"
  step_2.5: "devil-advocate (가정 도전 및 시나리오 역전)"
  step_3: "bear-case-critic (리스크 분석)"
  step_4: "stock-critic (최종 검증)"
  step_5: "최종 보고서 조합"

guardrails:
  - "PER/PBR/PEG만 사용 (복잡한 모델 금지)"
  - "종목당 최대 3페이지"
  - "original_text 필드 필수"
  - "화이트리스트 데이터 소스만 허용"
  - "블랙리스트: 블로그, 커뮤니티, 유튜브, 위키"

critical_rules:
  - "Task 도구 필수 사용"
  - "에이전트 결과 원본 인용"
  - "직접 분석 금지"
  - "면책조항 필수"
  - "perspective-balance: 확률 합계 100% 검증"
  - "devil-advocate: 가정 도전 및 시나리오 역전"
```
