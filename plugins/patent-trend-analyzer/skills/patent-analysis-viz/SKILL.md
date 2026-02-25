---
name: patent-analysis-viz
description: "특허 데이터 다축 분류, 트렌드 분석, 시각화 대시보드 생성. Use when: (1) 수집된 특허 데이터 분류/분석/시각화 시, (2) '특허 분류', 'analyze patent trends', 'visualize patent data', 'create patent dashboard', 'generate patent report' 요청 시, (3) 차트, 히트맵, 트렌드 분석 필요 시, (4) 화이트 스페이스 분석이나 경쟁 인텔리전스 필요 시, (5) Excel/Markdown 특허 데이터 인사이트 추출 시."
---

# patent-analysis-viz

수집된 특허 데이터를 분류 체계에 따라 분류하고, 트렌드를 분석하며, 정적/인터랙티브 시각화 대시보드를 생성하는 스킬입니다.

이 스킬은 3단계 파이프라인의 **L3 (Analysis)** 단계입니다.

---

## Pipeline

```
Load
  ↓  Excel / JSON 특허 데이터 읽기
Classify (IPC + keyword)
  ↓  분류 축 레이블 부여
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

## Classification Framework

L1 (patent-research-planning) 에서 정의한 분류 체계를 적용합니다. 분류 축과 카테고리는 연구 주제에 따라 결정됩니다.

### 분류 축 구성

연구 주제에 맞게 2개 이상의 분류 축을 정의합니다.

```
Axis 1: [연구 주제의 처리 방식, 적용 계층, 구현 환경 등]
  - Category A: [설명 및 관련 IPC/키워드]
  - Category B: [설명 및 관련 IPC/키워드]
  - Other: [미분류]

Axis 2: [연구 주제의 기능, 목적, 응용 분야 등]
  - Category X: [설명 및 관련 키워드]
  - Category Y: [설명 및 관련 키워드]
  - Other: [미분류]
```

---

## Classification Logic

분류는 IPC 우선 → 키워드 폴백 → "Other" 순서로 적용됩니다.

```python
def classify_patent(row, axis1_rules, axis2_rules):
    # 1. IPC 코드 매핑 (최우선)
    ipc = row.get("ipc_code", "")
    label_axis1 = None
    for category, ipc_list in axis1_rules["ipc"].items():
        if any(code in ipc for code in ipc_list):
            label_axis1 = category
            break

    if label_axis1 is None:
        # 2. 키워드 폴백
        text = f"{row.get('title', '')} {row.get('abstract', '')}"
        for category, keywords in axis1_rules["keywords"].items():
            if any(kw in text for kw in keywords):
                label_axis1 = category
                break
        else:
            # 3. 미분류
            label_axis1 = "Other"

    # Axis 2: 키워드 기반 분류
    label_axis2 = "Other"
    text = f"{row.get('title', '')} {row.get('abstract', '')}"
    for category, keywords in axis2_rules["keywords"].items():
        if any(kw in text for kw in keywords):
            label_axis2 = category
            break

    return label_axis1, label_axis2
```

`axis1_rules` 및 `axis2_rules` 는 L1에서 정의한 분류 체계를 딕셔너리 형태로 전달합니다.

---

## Domain Exclusion

연구 범위 외 특허를 필터링합니다. 제외 키워드는 연구 주제에 따라 정의합니다.

| 카테고리 | 제외 기준 |
|----------|-----------|
| [제외 도메인 1] | [해당 도메인 대표 키워드] |
| [제외 도메인 2] | [해당 도메인 대표 키워드] |
| ... | ... |

필요 시 분석 대상 외 도메인 키워드를 제외 목록으로 정의합니다. 제외 목록이 필요하지 않은 연구 주제의 경우 이 단계를 생략합니다.

---

## Institution Filter

개인 발명가를 제외하고 기업/학술 기관만 유지합니다.

```python
def is_institution(applicant: str) -> bool:
    institutional_suffixes = [
        "주식회사", "㈜", "Inc.", "Corp.", "Ltd.", "GmbH",
        "대학교", "연구원", "연구소", "institute", "university"
    ]
    return any(s in applicant for s in institutional_suffixes)
```

특정 기업명 필터는 연구 목적에 따라 추가할 수 있습니다.

---

## 5 Analysis Types

### 1. Distribution Analysis (분포 분석)
- 분류 축 1별 비율 (파이차트 + 바차트)
- 분류 축 2별 비율
- 국가별 비율

### 2. Cross-tabulation (교차 분석)
- 분류 축 1 × 분류 축 2 교차표 (히트맵)
- 각 셀: 특허 수 + 전체 대비 비율

### 3. Yearly Trends (연도별 트렌드)
- 연도별 출원 건수 추이 (라인차트)
- 분류 축 1 × 연도 스택 바차트
- 분류 축 2 × 연도 스택 바차트

### 4. White Space Analysis (화이트 스페이스)
- 특허 밀도가 낮은 (축 1, 축 2) 조합 식별
- 임계값 이하 셀 = 기회 영역으로 표시
- 출원 건수가 적은 카테고리 조합이 화이트 스페이스 후보

### 5. Institutional Ranking (기관 랭킹)
- 출원 건수 Top 20 기관
- 기관 × 분류 축 1 분포
- 최근 3년 vs 전체 기간 성장률 비교

---

## Visualization

### Static Charts (Matplotlib, 150 DPI)

| 파일명 | 내용 |
|--------|------|
| `axis1_distribution.png` | 분류 축 1 파이차트 |
| `axis2_distribution.png` | 분류 축 2 바차트 |
| `axis1_axis2_heatmap.png` | 축 1 × 축 2 히트맵 |
| `yearly_trend.png` | 연도별 출원 추이 |
| `axis1_yearly_stacked.png` | 축 1 × 연도 스택 바 |
| `axis2_yearly_stacked.png` | 축 2 × 연도 스택 바 |
| `white_space_map.png` | 화이트 스페이스 시각화 |
| `top_institutions.png` | 기관 랭킹 수평 바 |

설정:

```python
plt.rcParams["font.family"] = "NanumGothic"  # 한글 폰트
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"
```

### Color Palettes

분류 카테고리별 색상은 연구 주제에 따라 정의합니다. 아래는 예시 구조입니다.

```python
AXIS1_COLORS = {
    "Category A": "#FF6B6B",
    "Category B": "#4ECDC4",
    "Other":      "#95A5A6"
}

AXIS2_COLORS = {
    "Category X": "#3498DB",
    "Category Y": "#2ECC71",
    "Category Z": "#F39C12",
    "Other":      "#9B59B6"
}
```

### Interactive HTML Dashboard (Plotly)

`patent_dashboard.html` 에 포함되는 인터랙티브 요소:

- 드롭다운 필터 (국가, 연도 범위, 분류 축 1, 분류 축 2)
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
│   ├── axis1_distribution.png
│   ├── axis2_distribution.png
│   ├── axis1_axis2_heatmap.png
│   ├── yearly_trend.png
│   ├── axis1_yearly_stacked.png
│   ├── axis2_yearly_stacked.png
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

## 2. 분류 축 1 분포
| 카테고리 | 건수 | 비율 |
...

## 3. 분류 축 2 분포
...

## 4. 화이트 스페이스 요약
...

## 5. 주요 출원인 Top 10
...
```
