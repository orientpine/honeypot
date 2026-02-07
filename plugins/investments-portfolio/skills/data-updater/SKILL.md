---
name: data-updater
description: "CSV에서 펀드 데이터를 추출하여 fund_data.json, fund_fees.json, fund_classification.json을 생성/업데이트하는 스킬. 예금금리 데이터(deposit_rates.json) 업데이트도 지원한다. 펀드 데이터 업데이트가 필요하거나 CSV 파일을 JSON으로 변환하고 싶을 때 사용한다."
tools: Bash, Read, Write, mcp_question
---

# Fund Data Updater

## Overview

과학기술공제회 퇴직연금 CSV 파일을 읽어 Python 스크립트를 통해
펀드 데이터 JSON 파일을 자동 생성하는 스킬이다.

핵심 기능:
- CSV 파일 파싱 및 검증
- fund_data.json 생성 (펀드 기본 정보 및 수익률)
- fund_fees.json 생성 (펀드 수수료 정보)
- fund_classification.json 자동 생성 (펀드 분류)
- **투자 가능 펀드 필터링** (investable_codes.json 기반)
- **funds/all/ 폴더에 전체 펀드 데이터 저장** (2015개)
- **deposit_rates.json 업데이트 (예금금리 - 사용자 입력 필수)**
- 기존 파일 자동 백업 (archive/ 디렉토리)

> **⚠️ 중요**: 예금금리 데이터는 웹 검색으로 얻을 수 **없습니다**.
> 과학기술인공제회 내부 금리이므로 반드시 **사용자에게 직접 확인**해야 합니다.

---

## 사용자 입력 스키마

### 필수 입력

| 항목 | 설명 | 예시 |
|------|------|------|
| CSV 파일 경로 | 과학기술공제회 퇴직연금 CSV 파일 | `resource/26년01월_상품제안서_퇴직연금(DCIRP).csv` |

### 선택 입력

| 항목 | 설명 | 기본값 |
|------|------|--------|
| 출력 디렉토리 | JSON 파일 저장 위치 | 자동 감지 (investments/funds/) |
| dry-run 모드 | 미리보기 (파일 생성 없이 결과만 출력) | false |

---

## Workflow

```
[Phase 0: 입력 검증]
    |
    +-- Step 0-1. CSV 파일 확인
    |   +-- 사용자 제공 경로 존재 여부 확인
    |   +-- 파일 확장자 (.csv) 확인
    |   +-- 인코딩 검증 (UTF-8 필수)
    |
    +-- Step 0-2. 출력 폴더 설정
    |   +-- funds/ 폴더 존재 확인 (없으면 생성)
    |   +-- archive/ 폴더 존재 확인 (없으면 생성)
    |   +-- 기존 JSON 파일 백업 준비
    |
    +-- Step 0-3. Python 환경 확인
        +-- Python 3.10+ 설치 여부 확인
        +-- 필수 패키지: 표준 라이브러리만 (외부 패키지 불필요)

[Phase 1: Dry-run 실행 (권장)]
    |
    +-- Step 1-1. 미리보기 실행
    |   +-- --dry-run 옵션으로 스크립트 실행
    |   +-- CSV 메타데이터 확인 (사업자명, 기준일 등)
    |   +-- 펀드 개수 확인
    |
    +-- Step 1-2. 샘플 데이터 검토
        +-- 처음 3개 펀드 데이터 미리보기
        +-- 사용자에게 확인 요청 (진행 여부)

[Phase 2: 데이터 변환]
    |
    +-- Step 2-1. Python 스크립트 찾기 및 실행
    |   +-- 상대경로 참조: scripts/update_fund_data.py (스킬 루트 기준)
    |   +-- 실패 시 Glob 폴백: **/investments-portfolio/skills/data-updater/scripts/update_fund_data.py
    |   +-- Glob도 실패 시: Glob: **/update_fund_data.py
    |   +-- 찾은 경로로 실행: python {경로} --file [csv_file_path]
    |   +-- 스크립트를 찾지 못하면: 즉시 중단, 사용자에게 경로 확인 요청
    |   +-- 절대 금지: 스크립트를 못 찾았을 때 자체 Python 코드를 작성하여 대체하지 않음
    |
    +-- Step 2-2. 자동 분류 실행
    |   +-- update_fund_data.py가 자동으로 classify_funds.py 호출
    |   +-- fund_classification.json 자동 생성
    |
    +-- Step 2-3. 결과 확인
        +-- 생성된 JSON 파일 목록 확인
        +-- 펀드 개수 및 분류 통계 확인

[Phase 3: 검증]
    |
    +-- Step 3-1. 파일 검증
    |   +-- fund_data.json 존재 및 JSON 유효성 확인
    |   +-- fund_fees.json 존재 및 JSON 유효성 확인
    |   +-- fund_classification.json 존재 확인
    |
    +-- Step 3-2. 메타데이터 검증
        +-- _meta.version 확인 (CSV 기준일과 일치)
        +-- _meta.recordCount 확인 (펀드 개수)
        +-- _meta.updatedAt 확인 (현재 시간)

[Phase 4: 완료 보고]
    |
    +-- Step 4-1. 실행 보고서 생성
    |   +-- 포함 내용:
    |       - 입력 CSV 파일명 및 기준일
    |       - 생성된 JSON 파일 목록
    |       - 펀드 개수 및 분류 통계
    |       - 아카이브된 파일 목록
    |
    +-- Step 4-2. 사용자 안내
        +-- 생성 완료 알림
        +-- funds/ 폴더 위치 안내
        +-- 다음 단계 안내 (포트폴리오 분석 등)

[Phase 5: 예금금리 업데이트 (선택)]
    |
    +-- Step 5-0. 예금금리 업데이트 필요 여부 확인
    |   +-- deposit_rates.json 존재 확인
    |   +-- _meta.version 기준 경과일 계산
    |   +-- 30일 이상 경과 시 업데이트 권장
    |
    +-- Step 5-1. 사용자에게 예금금리 확인 요청 (mcp_question 사용)
    |   +-- ⚠️ 웹 검색 불가 - 사용자 직접 입력 필수
    |   +-- 질문: "과학기술인공제회 퇴직연금 예금금리를 입력해주세요"
    |   +-- 필수 입력 항목:
    |       - 과학기술인공제회 1년 정기예금 금리 (%)
    |       - 우리은행 1년 정기예금 금리 (%) - 선택
    |
    +-- Step 5-2. deposit_rates.json 업데이트
    |   +-- _meta.version: 현재 날짜 (YYYY-MM-DD)
    |   +-- _meta.updatedAt: 현재 ISO 8601 타임스탬프
    |   +-- rates 배열 업데이트
    |
    +-- Step 5-3. 업데이트 완료 확인
        +-- JSON 유효성 검사
        +-- 업데이트 내역 보고
```

---

## 스크립트 실행 방식

### 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/update_fund_data.py
scripts/classify_funds.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
```bash
python scripts/update_fund_data.py --file [csv_file_path]
python scripts/classify_funds.py --fund-data "funds/fund_data.json"
```

**Step 2. 상대경로 실패 시 Glob 폴백**
```
Glob: **/investments-portfolio/skills/data-updater/scripts/update_fund_data.py
Glob: **/investments-portfolio/skills/data-updater/scripts/classify_funds.py
```

**Step 3. Glob도 실패 시 확장 탐색**
```
Glob: **/update_fund_data.py
Glob: **/classify_funds.py
```

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.

### 실행 명령어

```bash
# Dry-run (미리보기) - 권장
python scripts/update_fund_data.py \
  --file [csv_file_path] \
  --dry-run

# 실제 실행 (자동 경로 감지)
python scripts/update_fund_data.py \
  --file [csv_file_path]

# 실제 실행 (출력 경로 지정)
python scripts/update_fund_data.py \
  --file [csv_file_path] \
  --output-dir [output_directory]
```

### 분류만 재실행 (선택)

```bash
python scripts/classify_funds.py \
  --fund-data "funds/fund_data.json"
```

### 스크립트 옵션

| 스크립트 | 옵션 | 필수 | 설명 |
|---------|------|:----:|------|
| update_fund_data.py | `--file` | O | CSV 파일 경로 |
| update_fund_data.py | `--output-dir` | X | 출력 디렉토리 (기본: 자동 감지) |
| update_fund_data.py | `--dry-run` | X | 미리보기 모드 |
| classify_funds.py | `--fund-data` | O | fund_data.json 파일 경로 |
| classify_funds.py | `--output` | X | 출력 파일 경로 |

### 의존성

- Python 3.10+
- 표준 라이브러리만 사용 (외부 패키지 불필요)

---

## Output Structure

### 출력 디렉토리 구조

```
funds/
├── fund_data.json              # 필터링된 펀드 (206개)
├── fund_fees.json              # 필터링된 수수료 정보
├── fund_classification.json    # 필터링된 펀드 분류
├── investable_codes.json       # 투자 가능 펀드 코드 목록
├── deposit_rates.json          # 예금금리 정보
├── all/                        # 전체 펀드 데이터
│   ├── all_fund_data.json      # 전체 펀드 (2015개)
│   ├── all_fund_fees.json      # 전체 수수료 정보
│   └── all_fund_classification.json  # 전체 펀드 분류
└── archive/                    # 이전 버전 백업
    ├── fund_data_2026-01-01.json
    └── fund_fees_2026-01-01.json
```

### fund_data.json 구조

```json
{
  "_meta": {
    "version": "2026-01-01",
    "sourceFile": "26년01월_상품제안서_퇴직연금(DCIRP).csv",
    "updatedAt": "2026-01-21T21:00:00+09:00",
    "recordCount": 206,
    "missing": []
  },
  "funds": [
    {
      "fundCode": "K55105EC1749",
      "name": "펀드명",
      "company": "운용사명",
      "riskLevel": 2,
      "riskName": "높은위험",
      "return10y": "",
      "return7y": "",
      "return5y": "",
      "return3y": "70.34",
      "return1y": "178.03",
      "return6m": "30.03",
      "netAssets": "50840000",
      "inceptionDate": "20220627",
      "isAffiliate": false,
      "fundType": "ETF"
    }
  ]
}
```

### fund_classification.json 구조

```json
{
  "펀드명": {
    "category": "해외주식형",
    "riskAsset": true,
    "assetClass": "equity",
    "region": "global",
    "themes": ["semiconductor", "ai"],
    "hedged": false,
    "riskLevel": 2,
    "source": "fund_data.json + keyword classification",
    "generatedAt": "2026-01-21"
  }
}
```

### deposit_rates.json 구조

```json
{
  "_meta": {
    "version": "2026-01-31",
    "source": "과학기술인공제회 퇴직연금 원리금보장형 운용방법 안내",
    "updatedAt": "2026-01-31T12:00:00+09:00",
    "recordCount": 4,
    "freshnessThresholdDays": 30,
    "note": "30일 경과 시 데이터 업데이트 필요"
  },
  "rates": [
    {
      "id": "sema-1y",
      "institution": "과학기술인공제회",
      "productName": "과학기술인공제회 퇴직연금 운용방법 (1년)",
      "type": "원리금보장형운용방법",
      "term": "1년",
      "termMonths": 12,
      "rate": 4.9,
      "unit": "%"
    },
    {
      "id": "woori-1y",
      "institution": "우리은행",
      "productName": "우리은행 정기예금 1년",
      "type": "원리금보장형운용방법",
      "term": "1년",
      "termMonths": 12,
      "rate": 2.75,
      "unit": "%"
    }
  ],
  "summary": {
    "highestRate": {
      "institution": "과학기술인공제회",
      "rate": 4.9,
      "term": "1년"
    },
    "institutions": ["과학기술인공제회", "우리은행"]
  }
}
```

---

## 예금금리 업데이트 (Phase 5)

### ⚠️ 중요: 웹 검색 불가

**예금금리 데이터는 웹 검색으로 얻을 수 없습니다.**

- 과학기술인공제회 내부 금리는 공개 웹에 게시되지 않음
- 회원 전용 포털 또는 고객센터에서만 확인 가능
- 따라서 **사용자에게 직접 확인 요청**이 필수

### 사용자 질문 예시 (mcp_question 사용)

```json
{
  "questions": [
    {
      "header": "예금금리 업데이트",
      "question": "과학기술인공제회 퇴직연금 1년 정기예금 금리(%)를 입력해주세요. (예: 4.9)",
      "options": [
        {"label": "4.9%", "description": "현재 저장된 금리"},
        {"label": "5.0%", "description": ""},
        {"label": "4.8%", "description": ""},
        {"label": "4.7%", "description": ""}
      ]
    }
  ]
}
```

또는 직접 입력을 받는 경우:

```
사용자에게 예금금리 확인을 요청합니다.

과학기술인공제회 퇴직연금 포털에서 현재 예금금리를 확인해주세요:
- 과학기술인공제회 1년 정기예금 금리: _____ %
- (선택) 우리은행 1년 정기예금 금리: _____ %

확인 방법:
1. 과학기술인공제회 퇴직연금 포털 로그인
2. 원리금보장형 운용방법 안내 페이지 확인
3. 현재 금리 입력
```

### 업데이트 수행 방법

사용자로부터 금리 정보를 받은 후:

```python
# deposit_rates.json 업데이트
import json
from datetime import datetime

# 현재 파일 읽기
with open('funds/deposit_rates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 메타데이터 업데이트
data['_meta']['version'] = datetime.now().strftime('%Y-%m-%d')
data['_meta']['updatedAt'] = datetime.now().isoformat()

# 금리 업데이트 (사용자 입력값 사용)
for rate in data['rates']:
    if rate['id'] == 'sema-1y':
        rate['rate'] = 4.9  # 사용자 입력값
    elif rate['id'] == 'woori-1y':
        rate['rate'] = 2.75  # 사용자 입력값

# 요약 업데이트
data['summary']['highestRate']['rate'] = max(r['rate'] for r in data['rates'])

# 저장
with open('funds/deposit_rates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## Usage Example

### 입력 예시 1: 펀드 데이터 업데이트

```
data-updater 스킬을 사용해서 펀드 데이터를 업데이트해줘.
CSV 파일: resource/26년01월_상품제안서_퇴직연금(DCIRP).csv
```

또는 간단히:

```
펀드 데이터 업데이트해줘
```

### 입력 예시 2: 예금금리 업데이트

```
예금금리 데이터도 업데이트해줘
```

또는:

```
data-updater 스킬로 예금금리 업데이트 해줘.
과학기술인공제회 1년: 4.9%
우리은행 1년: 2.75%
```

### 수행 절차

**펀드 데이터 업데이트 (Phase 0-4):**
1. **Phase 0**: CSV 파일 확인, UTF-8 인코딩 검증
2. **Phase 1**: Dry-run으로 미리보기, 2015개 펀드 발견
3. **Phase 2**: Python 스크립트 실행, JSON 파일 생성
4. **Phase 3**: 생성된 파일 검증
5. **Phase 4**: 완료 보고서 생성

**예금금리 업데이트 (Phase 5, 선택):**
6. **Phase 5**: 사용자에게 예금금리 확인 요청 → deposit_rates.json 업데이트

### 출력 파일

1. `funds/fund_data.json`: 펀드 마스터 데이터 (2015개)
2. `funds/fund_fees.json`: 펀드 수수료 정보
3. `funds/fund_classification.json`: 펀드 분류 정보
4. `funds/deposit_rates.json`: 예금금리 정보 (Phase 5 실행 시)

---

## 에러 처리

| 에러 | 원인 | 해결 |
|------|------|------|
| `File not found` | CSV 파일 경로 오류 | 경로 확인, 절대 경로 사용 |
| `UnicodeDecodeError` | 인코딩 오류 | CSV 파일을 UTF-8로 재저장 |
| `Header not found` | CSV 형식 오류 | "펀드코드" 포함 헤더 확인 |
| `Output directory not found` | 경로 감지 실패 | `--output-dir` 옵션 사용 |

상세한 에러 처리 및 디버깅 방법은 `./scripts/README.md` 참조.

---

## CSV 파일 형식

### 예상 구조

```
Row 1: 사업자명     | 미래에셋증권
Row 2: 제도유형     | DC/IRP
Row 3: 상품유형     | 실적배당형 상품(펀드/ETF)
Row 4: 기준일       | 2026-01-01, 제로인
Row 5-7: (빈 행 또는 기타)
Row 8: 헤더         | 펀드코드 | 펀드명 | 운용회사명 | 위험등급 | ...
Row 9+: 데이터      | K55105EC1749 | 펀드명 | 운용사 | 2등급(높은위험) | ...
```

### 필수 컬럼

| 컬럼명 | 용도 |
|--------|------|
| 펀드코드 | 고유 식별자 |
| 펀드명 | 펀드 이름 |
| 운용회사명 | 운용사 |
| 위험등급 | "N등급(위험명)" 형식 |
| 순자산총액(억원) | 순자산 (억원 단위) |
| 수익률(6M), (1Y), (3Y), (5Y), (7Y), (10Y) | 기간별 수익률 |
| 설정일 | 펀드 설정일 |
| 비율(%) | 총보수 |
| 1년투자비용(원) | 연간 비용 |

---

## 관련 플러그인

| 플러그인/에이전트 | 역할 | 연계 |
|------------------|------|------|
| portfolio-orchestrator | 포트폴리오 분석 오케스트레이션 스킬 | fund_data.json, deposit_rates.json 신선도 검사 |
| fund-portfolio | 펀드 추천 | fund_data.json, fund_classification.json, deposit_rates.json 사용 |
| compliance-checker | DC 규제 검증 | fund_classification.json, deposit_rates.json 사용 |
| fund-selection-criteria | 펀드 선택 기준 | deposit_rates.json으로 예금 vs 채권 비교 |
| data-updater | 데이터 변환 | 현재 스킬 |

---

## Resources

### 스크립트 위치

- **메인 스크립트**: `scripts/update_fund_data.py` (Glob으로 절대경로 확보 후 실행)
- **분류 스크립트**: `scripts/classify_funds.py` (Glob으로 절대경로 확보 후 실행)
- **상세 문서**: `scripts/README.md`

### 성능

- 2,015개 펀드 처리 시간: 약 1-2초
- 메모리 사용량: 약 50MB
