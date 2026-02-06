# 펀드 데이터 업데이트 스크립트

## 개요

과학기술공제회 퇴직연금 CSV 데이터를 JSON 형식으로 변환하는 스크립트들입니다.

## 스크립트 목록

### 1. update_fund_data.py

CSV 파일에서 펀드 데이터를 추출하여 JSON 파일을 생성합니다.

**기능:**
- CSV 파일 파싱 및 검증
- fund_data.json 생성 (펀드 기본 정보 및 수익률)
- fund_fees.json 생성 (펀드 수수료 정보)
- fund_classification.json 자동 생성 (기본 분류)
- 기존 파일 자동 백업 (archive/ 디렉토리)

**사용법:**

```bash
# Dry-run (미리보기)
python scripts/update_fund_data.py \
  --file "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv" \
  --dry-run

# 실제 실행
python scripts/update_fund_data.py \
  --file "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv" \
  --output-dir "funds"

# 출력 디렉토리 지정
python scripts/update_fund_data.py \
  --file "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv" \
  --output-dir "/path/to/output"
```

**옵션:**
- `--file`: CSV 파일 경로 (필수)
- `--output-dir`: 출력 디렉토리 (기본값: 자동 감지)
- `--dry-run`: 미리보기 모드 (파일 생성 없이 결과만 출력)

**출력:**
- `fund_data.json`: 펀드 기본 정보
- `fund_fees.json`: 펀드 수수료 정보
- `fund_classification.json`: 펀드 분류 정보 (기본)

### 2. classify_funds.py

fund_data.json을 기반으로 향상된 펀드 분류를 수행합니다.

**기능:**
- 키워드 기반 펀드 카테고리 분류
- 테마 자동 태깅
- 위험자산/안전자산 분류
- 지역 및 자산군 분류

**사용법:**

```bash
# 기본 사용
python scripts/classify_funds.py \
  --fund-data "funds/fund_data.json"

# 출력 경로 지정
python scripts/classify_funds.py \
  --fund-data "funds/fund_data.json" \
  --output "funds/fund_classification.json"
```

**옵션:**
- `--fund-data`: fund_data.json 파일 경로 (필수)
- `--output`: 출력 파일 경로 (기본값: fund_data.json과 같은 디렉토리)

**분류 규칙:**

1. **우선순위 1: 특정 테마 키워드**
   - 반도체, HBM, AI, 방산, 원자력, 전력, 태양광, ESS, 신재생, 수소, 금, 골드, 로봇 등

2. **우선순위 2: 광범위한 주식형 키워드**
   - ETF 브랜드: KODEX, TIGER, ARIRANG, KINDEX, KBSTAR, RISE, HANARO, PLUS, UNICORN, SOL
   - 지역 키워드: 코리아, 한국, 글로벌, 월드, 미국, 중국, 일본, 유럽, 신흥국
   - 지수: KOSPI, KOSDAQ, S&P, NASDAQ

3. **우선순위 3: 안전자산**
   - 채권, 국공채, 회사채, 크레딧, MMF, 머니마켓, 단기금융

4. **우선순위 4: 일반 패턴**
   - 증권상장지수투자신탁[주식]
   - 증권투자신탁[주식]
   - 증권자투자신탁(주식)

5. **우선순위 5: 위험등급 기반 폴백**
   - 1-3등급: 주식형 (위험자산)
   - 5-6등급: 채권형 (안전자산)
   - 4등급: 혼합형

## 워크플로우

### 정기 업데이트 (매월)

1. CSV 파일 다운로드
   ```bash
   # resource/ 디렉토리에 저장
   cp "다운로드된_CSV파일" "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv"
   ```

2. Dry-run 실행 (검증)
   ```bash
   python scripts/update_fund_data.py \
     --file "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv" \
     --dry-run
   ```

3. 실제 업데이트 실행
   ```bash
   python scripts/update_fund_data.py \
     --file "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv" \
     --output-dir "funds"
   ```

4. 분류 검증 및 재생성 (필요시)
   ```bash
   python scripts/classify_funds.py \
     --fund-data "funds/fund_data.json" \
     --output "funds/fund_classification.json"
   ```

### 분류만 업데이트

fund_data.json은 그대로 두고 분류만 재생성하는 경우:

```bash
python scripts/classify_funds.py \
  --fund-data "funds/fund_data.json"
```

## 에러 처리

### 일반적인 에러

**1. File not found**
```
Error: CSV file not found: resource/파일명.csv
```
- 원인: CSV 파일 경로가 잘못됨
- 해결: 경로 확인, 절대 경로 사용

**2. UnicodeDecodeError**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```
- 원인: CSV 파일 인코딩이 UTF-8이 아님
- 해결: CSV 파일을 UTF-8로 재저장 후 재시도

**3. Header not found**
```
ValueError: Header row with '펀드코드' not found in CSV file
```
- 원인: CSV 파일 형식이 예상과 다름
- 해결: CSV 파일 헤더 확인 (8행째에 "펀드코드" 포함되어야 함)

**4. Output directory not found**
```
Error: Could not auto-detect output directory
```
- 원인: 출력 디렉토리 자동 감지 실패
- 해결: `--output-dir` 옵션으로 명시적 지정

### 디버깅

```bash
# CSV 파일 헤더 확인
head -10 "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv"

# 파일 인코딩 확인
file -i "resource/26년01월_상품제안서_퇴직연금(DCIRP).csv"

# 출력 디렉토리 확인
ls -la funds/
```

## CSV 파일 형식

### 예상 구조

```
Row 1: 사업자명     | 미래에셋증권
Row 2: 제도유형     | DC/IRP
Row 3: 상품유형     | 실적배당형 상품(펀드/ETF)
Row 4: 기준일       | 2026-01-01, 제로인
Row 5-7: (빈 행 또는 기타)
Row 8: 헤더         | 펀드코드 | 펀드명 | 운용회사명 | ...
Row 9+: 데이터      | K55105EC1749 | 펀드명 | 운용사 | ...
```

### 필수 컬럼

- 펀드코드
- 펀드명
- 운용회사명
- 위험등급
- 순자산총액(억원)
- 수익률(6M), (1Y), (3Y), (5Y), (7Y), (10Y)
- 설정일
- 비율(%) - 총보수
- 1년투자비용(원)
- 계열사 여부
- 비고

## 의존성

- Python 3.10+
- 표준 라이브러리만 사용 (외부 패키지 불필요)
  - csv
  - json
  - pathlib
  - datetime
  - re
  - shutil

## 성능

- 2,015개 펀드 처리 시간: 약 1-2초
- 메모리 사용량: 약 50MB

## 버전 관리

스크립트는 생성된 JSON 파일에 메타데이터를 포함합니다:

```json
{
  "_meta": {
    "version": "2026-01-01",           // CSV 기준일
    "sourceFile": "26년01월_상품제안서_퇴직연금(DCIRP).csv",
    "updatedAt": "2026-01-21T22:07:46.467353+09:00",
    "recordCount": 2015
  }
}
```

## 백업 정책

- 기존 JSON 파일은 자동으로 `archive/` 디렉토리에 백업
- 백업 파일명: `fund_data_YYYY-MM-DD_HHMMSS.json`
- 수동 삭제 전까지 영구 보관

## 테스트

### 수동 테스트

```bash
# 1. Dry-run으로 변환 검증
python scripts/update_fund_data.py --file "test.csv" --dry-run

# 2. 샘플 데이터 확인
python -c "
import json
with open('funds/fund_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'Total funds: {len(data[\"funds\"])}')
    print(f'Sample: {data[\"funds\"][0]}')
"

# 3. 분류 통계 확인
python -c "
import json
with open('funds/fund_classification.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    cats = {}
    for info in data.values():
        cat = info['category']
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f'{cat}: {count}')
"
```

## 문제 해결

### 분류가 부정확한 경우

`classify_funds.py` 스크립트의 키워드 규칙을 수정하세요:

1. `classify_funds.py` 파일 열기
2. `classify_fund()` 함수의 키워드 딕셔너리 수정
3. 재실행:
   ```bash
   python scripts/classify_funds.py --fund-data "funds/fund_data.json"
   ```

### 새로운 테마 추가

`classify_funds.py`의 `thematic_keywords` 딕셔너리에 추가:

```python
thematic_keywords = {
    # 기존 키워드...
    '새로운테마': ('주식형', True, 'equity', 'domestic', ['new_theme']),
}
```

## 관련 문서

- [AGENTS.md](../AGENTS.md): 데이터 업데이트 에이전트 가이드
- [funds/README.md](../funds/README.md): 펀드 데이터 설명

## 라이선스

MIT License
