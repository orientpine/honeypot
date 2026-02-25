---
name: patent-analysis-viz
description: "특허 데이터 3축 분류, 트렌드 분석, 시각화 대시보드 생성. Use when: (1) 수집된 특허 데이터 분류/분석/시각화 시, (2) '특허 분류', 'analyze patent trends', 'visualize patent data', 'create patent dashboard', 'generate patent report' 요청 시, (3) 차트, 히트맵, 트렌드 분석 필요 시, (4) 화이트 스페이스 분석이나 경쟁 인텔리전스 필요 시, (5) Excel/Markdown 특허 데이터 인사이트 추출 시."
---

# patent-analysis-viz

수집된 특허 데이터를 3축으로 분류하고, 트렌드를 분석하며, 정적/인터랙티브 시각화 대시보드를 생성하는 스킬입니다.

이 스킬은 3단계 파이프라인의 **L3 (Analysis)** 단계입니다.

---

## Pipeline

```
Load
  ↓  Excel / JSON 특허 데이터 읽기
Classify (IPC + keyword)
  ↓  3축 레이블 부여
Filter (domain / institution)
  ↓  도메인 제외, 기관 필터
Analyze (5 types)
  ↓  분포, 교차표, 연도별 트렌드, 화이트스페이스, 기관 랭킹
Visualize
  ↓  Matplotlib 정적 차트 + Plotly 인터랙티브 대시보드
Export
  ↓  Excel, Markdown, PNG, HTML
```

---

## 3-Axis Classification

### Axis 1: Processing Layer

| 레이어 | IPC 코드 | 보조 키워드 |
|--------|----------|------------|
| **OnSensor** | G06N 3/065, G06N 3/067 | 뉴로모픽, neuromorphic, in-sensor, 센서 내 처리, analog neural |
| **OnDevice** | G06N 3/063 | 온디바이스, on-device, edge AI, 에지 AI, MCU, TinyML, 경량화 |
| **Cloud/Other** | G06N 3/04, G06N 3/08, 기타 | 클라우드, cloud inference, 서버 기반 |

### Axis 2: Function

| 기능 | 주요 키워드 |
|------|------------|
| **Adaptive Learning** | 전이학습, federated learning, 온라인 학습, continual learning, meta-learning |
| **Inference** | 추론 최적화, inference engine, 가속기, accelerator, 런타임 |
| **Lightweight** | 경량화, 양자화, quantization, pruning, knowledge distillation, NAS |
| **Training** | 학습 알고리즘, backpropagation, SGD, optimizer, 역전파 |

---

## Classification Logic

분류는 IPC 우선 → 키워드 폴백 → "Other" 순서로 적용됩니다.

```python
def classify_patent(row):
    # 1. IPC 코드 매핑 (최우선)
    ipc = row.get("ipc_code", "")
    if "G06N3/065" in ipc or "G06N3/067" in ipc:
        layer = "OnSensor"
    elif "G06N3/063" in ipc:
        layer = "OnDevice"
    else:
        # 2. 키워드 폴백
        text = f"{row.get('title', '')} {row.get('abstract', '')}"
        if any(kw in text for kw in ONSENSOR_KEYWORDS):
            layer = "OnSensor"
        elif any(kw in text for kw in ONDEVICE_KEYWORDS):
            layer = "OnDevice"
        else:
            # 3. 미분류
            layer = "Other"
    return layer
```

---

## Domain Exclusion

아래 40+ 키워드가 제목 또는 초록에 포함된 특허는 분석에서 제외합니다.

| 카테고리 | 제외 키워드 (예시) |
|----------|------------------|
| LLM / 생성 AI | GPT, BERT, transformer, LLM, diffusion, generative |
| Medical | 의료, 진단, 병원, 신약, 방사선, 영상 판독 |
| Security | 침입 탐지, 사이버 보안, 악성코드, 암호화, IDS |
| Recommendation | 추천 시스템, 협업 필터링, 콘텐츠 기반 필터링 |
| Analytics | BI, 데이터 웨어하우스, OLAP, 비즈니스 인텔리전스 |

---

## Institution Filter

개인 발명가를 제외하고 기업/학술 기관만 유지합니다.

- **유지**: 삼성, LG, SK, 현대, 대학교, 연구원, Inc., Corp., Ltd., GmbH
- **제거**: 개인 이름 패턴 (홍길동, John Doe 형태)

```python
def is_institution(applicant: str) -> bool:
    institutional_suffixes = [
        "주식회사", "㈜", "Inc.", "Corp.", "Ltd.", "GmbH",
        "대학교", "연구원", "연구소", "institute", "university"
    ]
    return any(s in applicant for s in institutional_suffixes)
```

---

## 5 Analysis Types

### 1. Distribution Analysis (분포 분석)
- Processing Layer별 비율 (파이차트 + 바차트)
- Function별 비율
- 국가별 비율

### 2. Cross-tabulation (교차 분석)
- Processing Layer × Function 교차표 (히트맵)
- 각 셀: 특허 수 + 전체 대비 비율

### 3. Yearly Trends (연도별 트렌드)
- 연도별 출원 건수 추이 (라인차트)
- Layer × 연도 스택 바차트
- Function × 연도 스택 바차트

### 4. White Space Analysis (화이트 스페이스)
- 특허 밀도가 낮은 (Layer, Function) 조합 식별
- 임계값 이하 셀 = 기회 영역으로 표시
- OnSensor 레이어 전체가 화이트 스페이스 후보

### 5. Institutional Ranking (기관 랭킹)
- 출원 건수 Top 20 기관
- 기관 × Layer 분포
- 최근 3년 vs 전체 기간 성장률 비교

---

## Visualization

### Static Charts (Matplotlib, 150 DPI)

| 파일명 | 내용 |
|--------|------|
| `layer_distribution.png` | Processing Layer 파이차트 |
| `function_distribution.png` | Function 바차트 |
| `layer_function_heatmap.png` | Layer × Function 히트맵 |
| `yearly_trend.png` | 연도별 출원 추이 |
| `layer_yearly_stacked.png` | Layer × 연도 스택 바 |
| `function_yearly_stacked.png` | Function × 연도 스택 바 |
| `white_space_map.png` | 화이트 스페이스 시각화 |
| `top_institutions.png` | 기관 랭킹 수평 바 |

설정:

```python
plt.rcParams["font.family"] = "NanumGothic"  # 한글 폰트
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"
```

### Color Palettes

```python
LAYER_COLORS = {
    "OnSensor": "#FF6B6B",   # 빨강 계열
    "OnDevice": "#4ECDC4",   # 청록 계열
    "Cloud/Other": "#95A5A6" # 회색 계열
}

FUNC_COLORS = {
    "Adaptive Learning": "#3498DB",  # 파랑
    "Inference": "#2ECC71",          # 초록
    "Lightweight": "#F39C12",        # 주황
    "Training": "#9B59B6"            # 보라
}
```

### Interactive HTML Dashboard (Plotly)

`patent_dashboard.html` 에 포함되는 인터랙티브 요소:

- 드롭다운 필터 (국가, 연도 범위, Layer, Function)
- 클릭 가능한 히트맵 (셀 클릭 시 해당 특허 목록 표시)
- 줌/패닝 지원 라인차트
- 툴팁에 특허 번호, 출원인, 출원일 표시

---

## Export

### Output Structure

```
output/
├── patent_analysis_report.xlsx          # 메인 분석 결과
│   ├── Sheet: Raw (원본 + 분류 레이블)
│   ├── Sheet: Distribution (분포 집계)
│   ├── Sheet: CrossTab (교차표)
│   ├── Sheet: YearlyTrend (연도별 추이)
│   ├── Sheet: WhiteSpace (화이트스페이스)
│   └── Sheet: TopInstitutions (기관 랭킹)
├── patent_classification_summary.md     # Markdown 요약 보고서
├── visualizations/
│   ├── layer_distribution.png
│   ├── function_distribution.png
│   ├── layer_function_heatmap.png
│   ├── yearly_trend.png
│   ├── layer_yearly_stacked.png
│   ├── function_yearly_stacked.png
│   ├── white_space_map.png
│   └── top_institutions.png
└── patent_dashboard.html                # 인터랙티브 대시보드
```

### Markdown Summary 구조

```markdown
# 특허 분석 보고서

## 1. 개요
- 분석 기간: YYYY-YYYY
- 총 특허 수: N건 (중복 제거 후)
- 분석 국가: KR, US, EP, JP, CN

## 2. Processing Layer 분포
| Layer | 건수 | 비율 |
...

## 3. Function 분포
...

## 4. 화이트 스페이스 요약
...

## 5. 주요 출원인 Top 10
...
```
