---
name: data-updater
description: "CSV에서 펀드 데이터를 추출하여 fund_data.json, fund_fees.json, fund_classification.json을 생성/업데이트하는 스킬. 펀드 데이터 업데이트가 필요하거나 CSV 파일을 JSON으로 변환하고 싶을 때 사용한다."
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
- 기존 파일 자동 백업 (archive/ 디렉토리)

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
    +-- Step 2-1. Python 스크립트 실행
    |   +-- 스크립트 경로: plugins/investments-portfolio/scripts/update_fund_data.py
    |   +-- 실행 명령어:
    |       python plugins/investments-portfolio/scripts/update_fund_data.py \
    |         --file [csv_file_path]
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
```

---

## 스크립트 실행 방식

### 실행 명령어

```bash
# Dry-run (미리보기) - 권장
python plugins/investments-portfolio/scripts/update_fund_data.py \
  --file [csv_file_path] \
  --dry-run

# 실제 실행 (자동 경로 감지)
python plugins/investments-portfolio/scripts/update_fund_data.py \
  --file [csv_file_path]

# 실제 실행 (출력 경로 지정)
python plugins/investments-portfolio/scripts/update_fund_data.py \
  --file [csv_file_path] \
  --output-dir [output_directory]

# submodule로 사용하는 경우 (예: honeypot을 submodule로 추가한 경우)
python honeypot/plugins/investments-portfolio/scripts/update_fund_data.py \
  --file [csv_file_path]
```

**주의**: 스크립트는 이 플러그인의 `scripts/` 폴더에 위치합니다. 프로젝트 구조에 맞게 경로를 조정하세요.

### 분류만 재실행 (선택)

```bash
python plugins/investments-portfolio/scripts/classify_funds.py \
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
├── fund_data.json              # 펀드 마스터 데이터 (수익률 포함)
├── fund_fees.json              # 펀드 수수료 정보
├── fund_classification.json    # 펀드 분류 (위험/안전자산)
└── archive/                    # 이전 버전 백업
    ├── fund_data_2025-12-01.json
    └── fund_fees_2025-12-01.json
```

### fund_data.json 구조

```json
{
  "_meta": {
    "version": "2026-01-01",
    "sourceFile": "26년01월_상품제안서_퇴직연금(DCIRP).csv",
    "updatedAt": "2026-01-21T21:00:00+09:00",
    "recordCount": 2015
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

---

## Usage Example

### 입력 예시

```
data-updater 스킬을 사용해서 펀드 데이터를 업데이트해줘.
CSV 파일: resource/26년01월_상품제안서_퇴직연금(DCIRP).csv
```

또는 간단히:

```
펀드 데이터 업데이트해줘
```

### 수행 절차

1. **Phase 0**: CSV 파일 확인, UTF-8 인코딩 검증
2. **Phase 1**: Dry-run으로 미리보기, 2015개 펀드 발견
3. **Phase 2**: Python 스크립트 실행, JSON 파일 생성
4. **Phase 3**: 생성된 파일 검증
5. **Phase 4**: 완료 보고서 생성

### 출력 파일

1. `funds/fund_data.json`: 펀드 마스터 데이터 (2015개)
2. `funds/fund_fees.json`: 펀드 수수료 정보
3. `funds/fund_classification.json`: 펀드 분류 정보

---

## 에러 처리

| 에러 | 원인 | 해결 |
|------|------|------|
| `File not found` | CSV 파일 경로 오류 | 경로 확인, 절대 경로 사용 |
| `UnicodeDecodeError` | 인코딩 오류 | CSV 파일을 UTF-8로 재저장 |
| `Header not found` | CSV 형식 오류 | "펀드코드" 포함 헤더 확인 |
| `Output directory not found` | 경로 감지 실패 | `--output-dir` 옵션 사용 |

상세한 에러 처리 및 디버깅 방법은 `../../scripts/README.md` 참조.

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
| portfolio-coordinator | 포트폴리오 분석 오케스트레이터 | fund_data.json 사용 |
| fund-portfolio | 펀드 추천 | fund_data.json, fund_classification.json 사용 |
| compliance-checker | DC 규제 검증 | fund_classification.json 사용 |
| data-updater | 데이터 변환 | 현재 스킬 |

---

## Resources

### 스크립트 위치

- **메인 스크립트**: `plugins/investments-portfolio/scripts/update_fund_data.py`
- **분류 스크립트**: `plugins/investments-portfolio/scripts/classify_funds.py`
- **스킬 파일 기준 상대 경로**: `../../scripts/update_fund_data.py`
- **상세 문서**: `../../scripts/README.md`

### 성능

- 2,015개 펀드 처리 시간: 약 1-2초
- 메모리 사용량: 약 50MB
