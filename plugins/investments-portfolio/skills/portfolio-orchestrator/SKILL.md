---
name: portfolio-orchestrator
description: "퇴직연금 포트폴리오 분석 오케스트레이션 스킬. 메인 에이전트가 11개 서브에이전트를 순서대로 호출하여 Multi-agent 워크플로우를 실행하도록 안내합니다. DC형 70% 위험자산 한도 준수 및 환각 방지를 위한 교차 검증을 보장합니다."
---

# 포트폴리오 분석 오케스트레이션 스킬

이 스킬은 **메인 에이전트**가 퇴직연금 포트폴리오 분석을 오케스트레이션하는 방법을 안내합니다.

**핵심 원칙**: 메인 에이전트가 직접 분석하지 않고, Task 도구로 전문 서브에이전트를 호출합니다.

---

## 1. 워크플로우 개요

```
[사용자 요청: "포트폴리오 분석해줘"]
     │
     ▼
[Step -1] 데이터 신선도 검사 (funds/fund_data.json)
     │
     ▼
[Step 0.1] index-fetcher 호출 (지수 데이터 수집)
     │
     ▼
[Step 0.2] 4개 에이전트 병렬 호출
     ├── rate-analyst (금리/환율)
     ├── sector-analyst (섹터 전망)
     ├── risk-analyst (리스크 시나리오)
     └── leadership-analyst (정치/중앙은행)
     │
     ▼
[Step 0.3] macro-synthesizer 호출 (거시경제 종합)
     │
     ▼
[Step 0.4] macro-critic 호출 (검증)
     │
     ▼
[Step 1] fund-portfolio 호출 (펀드 추천)
     │
     ▼
[Step 2] compliance-checker 호출 (규제 검증)
     │
     ▼
[Step 3] output-critic 호출 (최종 검증)
     │
     ▼
[Step 4] 최종 보고서 조합
```

---

## 2. 핵심 규칙 (CRITICAL)

### 2.1 직접 분석 금지 (Zero Tolerance)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⚠️ 절대 금지 사항 ⚠️                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 직접 fund_data.json 읽고 분석하기                            │
│  ❌ 직접 DC형 70% 한도 계산하기                                  │
│  ❌ 직접 출처 검증하기                                           │
│  ❌ 서브에이전트 결과를 "생성"하기 (환각)                        │
│  ❌ Task 호출 없이 결과 반환하기                                  │
│                                                                 │
│  ✅ 반드시 Task 도구로 서브에이전트 호출                         │
│  ✅ 서브에이전트 결과를 그대로 인용                              │
│  ✅ 결과 조합만 수행                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 서브에이전트 목록 (11개)

| 에이전트 | subagent_type | 역할 |
|----------|---------------|------|
| index-fetcher | `investments-portfolio:index-fetcher` | 지수 데이터 수집 (3소스 교차검증) |
| rate-analyst | `investments-portfolio:rate-analyst` | 금리/환율 전망 |
| sector-analyst | `investments-portfolio:sector-analyst` | 섹터별 전망 |
| risk-analyst | `investments-portfolio:risk-analyst` | 리스크 분석 & 시나리오 |
| leadership-analyst | `investments-portfolio:leadership-analyst` | 정치 리더십/중앙은행 동향 |
| material-organizer | `investments-portfolio:material-organizer` | 수집 자료 정리 (옵셔널) |
| macro-synthesizer | `investments-portfolio:macro-synthesizer` | 거시경제 종합 보고서 |
| macro-critic | `investments-portfolio:macro-critic` | 거시경제 분석 검증 |
| fund-portfolio | `investments-portfolio:fund-portfolio` | 펀드 포트폴리오 추천 |
| compliance-checker | `investments-portfolio:compliance-checker` | DC형 규제 준수 검증 |
| output-critic | `investments-portfolio:output-critic` | 최종 출력 검증 |

---

## 3. 세션 폴더 생성

분석 시작 시 세션 폴더를 먼저 생성합니다:

```
portfolios/YYYY-MM-DD-{투자성향}-{session_id}/

예시: portfolios/2026-02-01-aggressive-abc123/
```

**투자성향 영문 변환:**
- 공격형 → aggressive
- 중립형 → moderate  
- 안정형 → conservative

---

## 4. Step별 Task 호출 템플릿

### Step -1: 데이터 신선도 검사 (직접 수행)

```python
# 메인 에이전트가 직접 Read로 확인
Read("funds/fund_data.json")  # _meta.version 확인

# 판정 기준
# 0-30일: ✅ FRESH → 진행
# 31-60일: ⚠️ STALE → 경고 후 진행
# 61일+: 🔴 OUTDATED → 사용자 확인 요청
```

### Step 0.1: index-fetcher

```
Task(
  subagent_type="investments-portfolio:index-fetcher",
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

### Step 0.2: 4개 에이전트 병렬 호출

**병렬로 동시 호출합니다:**

```
# rate-analyst
Task(
  subagent_type="investments-portfolio:rate-analyst",
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
  subagent_type="investments-portfolio:sector-analyst",
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
  subagent_type="investments-portfolio:risk-analyst",
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

# leadership-analyst
Task(
  subagent_type="investments-portfolio:leadership-analyst",
  description="정치 리더십/중앙은행 동향 분석",
  prompt="""
## 정치 리더십 분석 요청

### 분석 대상국 (7개국)
미국, 중국, 한국, 일본, 인도, 베트남, 인도네시아

### 분석 항목
1. 지도자/경제팀 성향
2. 중앙은행 정책 방향
3. 포트폴리오 시사점

### 출력 경로
output_path: {session_folder}

### 출력 파일
leadership-analysis.json
"""
)
```

### Step 0.3: macro-synthesizer

**Step 0.2 완료 후 호출:**

```
Task(
  subagent_type="investments-portfolio:macro-synthesizer",
  description="거시경제 최종 보고서 작성",
  prompt="""
## 거시경제 최종 보고서 작성 요청

### 입력 파일 (직접 Read 필수)
- {session_folder}/index-data.json
- {session_folder}/rate-analysis.json
- {session_folder}/sector-analysis.json
- {session_folder}/risk-analysis.json
- {session_folder}/leadership-analysis.json

### 출력 경로
output_path: {session_folder}

### 출력 파일
00-macro-outlook.md

### 요구사항
- 모든 수치는 JSON 파일에서 그대로 복사
- 자산배분 권고 포함 (위험자산 비중, 환헤지 전략, 주목 섹터)
"""
)
```

### Step 0.4: macro-critic

```
Task(
  subagent_type="investments-portfolio:macro-critic",
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

### Step 1: fund-portfolio

```
Task(
  subagent_type="investments-portfolio:fund-portfolio",
  description="펀드 포트폴리오 분석",
  prompt="""
## 펀드 포트폴리오 분석 요청

### macro-outlook 파일 (직접 Read 필수)
{session_folder}/00-macro-outlook.md

### 투자자 정보
- 투자 성향: {risk_profile}
- 투자 기간: {investment_horizon}

### 제약 조건
- DC형 위험자산 한도: 70%
- 단일 펀드 집중 한도: 40%

### 데이터 소스
- funds/fund_data.json
- funds/fund_fees.json
- funds/fund_classification.json

### 출력 경로
output_path: {session_folder}

### 출력 파일
01-fund-analysis.md
"""
)
```

### Step 2: compliance-checker

```
Task(
  subagent_type="investments-portfolio:compliance-checker",
  description="규제 준수 검증",
  prompt="""
## DC형 규제 준수 검증 요청

### 검증 대상
{session_folder}/01-fund-analysis.md

### 검증 규칙
1. 위험자산 합계 ≤ 70%
2. 단일 펀드 ≤ 40%
3. 비중 합계 = 100%

### 출력 경로
output_path: {session_folder}

### 출력 파일
02-compliance-report.md

### FAIL 시
fund-portfolio 재호출 (최대 3회)
"""
)
```

### Step 3: output-critic

```
Task(
  subagent_type="investments-portfolio:output-critic",
  description="최종 출력 검증",
  prompt="""
## 최종 출력 검증 요청

### 검증 대상 파일
- {session_folder}/01-fund-analysis.md
- {session_folder}/02-compliance-report.md

### 검증 항목
1. 펀드명이 fund_data.json과 일치하는지
2. 수익률이 fund_data.json과 일치하는지
3. 출처 태그 존재 여부
4. 과신 표현 탐지

### 출력 경로
output_path: {session_folder}

### 출력 파일
03-output-verification.md

### 신뢰도 점수 산출
A등급(90+), B등급(80-89), C등급(70-79), F등급(<70)
"""
)
```

### Step 4: 최종 보고서 조합

**메인 에이전트가 직접 수행:**

```markdown
# 최종 보고서 조합 (04-portfolio-summary.md)

1. 모든 에이전트 결과 파일 읽기:
   - 00-macro-outlook.md
   - 01-fund-analysis.md
   - 02-compliance-report.md
   - 03-output-verification.md

2. 결과 통합 (원본 그대로 인용)

3. 면책조항 추가

4. Write로 저장: {session_folder}/04-portfolio-summary.md
```

---

## 5. 출력 파일 구조

| 파일명 | 생성 주체 | 설명 |
|--------|-----------|------|
| `index-data.json` | index-fetcher | 지수 데이터 (JSON) |
| `rate-analysis.json` | rate-analyst | 금리/환율 분석 (JSON) |
| `sector-analysis.json` | sector-analyst | 섹터 분석 (JSON) |
| `risk-analysis.json` | risk-analyst | 리스크 분석 (JSON) |
| `leadership-analysis.json` | leadership-analyst | 정치/중앙은행 분석 (JSON) |
| `00-macro-outlook.md` | macro-synthesizer | 거시경제 종합 보고서 |
| `01-fund-analysis.md` | fund-portfolio | 펀드 분석 및 추천 |
| `02-compliance-report.md` | compliance-checker | 규제 준수 검증 |
| `03-output-verification.md` | output-critic | 출력 검증 및 신뢰도 |
| `04-portfolio-summary.md` | 메인 에이전트 | 최종 통합 보고서 |

---

## 6. 에러 처리

### FAIL 시 재시도 규칙

| 에이전트 | 최대 재시도 | FAIL 시 액션 |
|----------|:-----------:|--------------|
| index-fetcher | 3회 | 워크플로우 중단 |
| rate/sector/risk/leadership-analyst | 3회 | 해당 에이전트만 재시도 |
| macro-synthesizer | 2회 | macro-critic FAIL 시 재시도 |
| macro-critic | - | synthesizer 재호출 트리거 |
| fund-portfolio | 3회 | compliance FAIL 시 재시도 |
| compliance-checker | - | fund-portfolio 재호출 트리거 |
| output-critic | 1회 | 경고만 표시 후 진행 |

### 전체 실패 시

3회 연속 실패 → 워크플로우 중단 → 사용자에게 에스컬레이션

---

## 7. 투자 성향별 설정

| 성향 | 위험자산 목표 | 환헤지 | 특징 |
|------|:------------:|:------:|------|
| 공격형 | 70% | 환노출 우선 | 고수익 추구, 변동성 감내 |
| 중립형 | 50% | 50/50 혼합 | 균형 추구 |
| 안정형 | 30% | 환헤지 우선 | 원금 보존 중심 |

---

## 8. 환각 방지 체크리스트

모든 Step에서 확인:

- [ ] 서브에이전트 결과를 직접 "생성"하지 않았는가?
- [ ] JSON 파일이 실제로 저장되었는가?
- [ ] 수치를 원본에서 그대로 복사했는가?
- [ ] 출처가 명시되어 있는가?
- [ ] 과신 표현(반드시, 확실히)을 사용하지 않았는가?

---

## 메타 정보

```yaml
version: "1.0"
created: "2026-02-01"
purpose: "메인 에이전트가 Multi-Agent 워크플로우를 오케스트레이션하도록 안내"
changes:
  - "v1.0: Agent에서 Skill로 전환 - nested Task 제한 해결"
related_skills:
  - file-save-protocol
  - dc-pension-rules
  - bogle-principles
```
