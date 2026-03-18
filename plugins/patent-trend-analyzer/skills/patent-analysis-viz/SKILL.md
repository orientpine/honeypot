---
name: patent-analysis-viz
description: "특허 데이터 다축 분류, 트렌드 분석, 시각화 대시보드 생성. Use when: (1) 수집된 특허 데이터 분류/분석/시각화 시, (2) '특허 분류', 'analyze patent trends', 'visualize patent data', 'create patent dashboard', 'generate patent report' 요청 시, (3) 차트, 히트맵, 트렌드 분석 필요 시, (4) 화이트 스페이스 분석이나 경쟁 인텔리전스 필요 시, (5) Excel/Markdown 특허 데이터 인사이트 추출 시."
---

# patent-analysis-viz

수집된 특허 데이터를 분류 체계에 따라 분류하고, 트렌드를 분석하며, 정적/인터랙티브 시각화 대시보드를 생성하는 스킬입니다.

이 스킬은 3단계 파이프라인의 **L3 (Analysis)** 단계입니다.

---

## CRITICAL: Standard Analysis Script

이 스킬은 `scripts/analyze_patents.py` 표준 분석 스크립트를 포함합니다. patent-analyzer 에이전트는 반드시 이 스크립트를 사용하여 분석을 수행해야 합니다.

### 스크립트 참조 및 실행

스크립트는 이 스킬의 상대경로에 위치합니다:

```
scripts/analyze_patents.py
```

**실행 방법:**
```bash
python scripts/analyze_patents.py --config output/classification_config.json
```

**Step 1. 상대경로로 실행** (최우선)
스킬이 로드된 컨텍스트에서 상대경로 `scripts/analyze_patents.py`를 직접 참조하여 실행합니다.

**Step 2. 상대경로 실패 시 Glob 폴백**
Glob: `**/patent-analysis-viz/scripts/analyze_patents.py`

**Step 3. Glob도 실패 시 확장 탐색**
Glob: `**/analyze_patents.py`

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.

---

## Pipeline

```
Config Generation
  ↓  classification_config.json 생성 (에이전트의 역할)
Load Data
  ↓  Excel 특허 데이터 읽기 (단일/병합)
Classify (IPC → keyword → Other)
  ↓  분류 축 레이블 부여
Analyze (5 types)
  ↓  분포, 교차표, 연도별 트렌드, 화이트스페이스, 기관 랭킹
Visualize
  ↓  Matplotlib 8 PNG + Plotly HTML 대시보드
Export
  ↓  Excel 6시트 + Markdown 보고서
Verify
  ↓  11개 필수 출력물 검증
```

---

## Classification Config Schema

에이전트는 연구 계획(L1)에서 도출한 분류 체계를 JSON 형식으로 작성합니다.

```json
{
  "metadata": {
    "title": "연구 주제 특허 분석",
    "dashboard_title": "연구 주제 특허 분석 대시보드",
    "period": "2020-2026",
    "analysis_date": "2026년 3월"
  },
  "input": {
    "file": "output/deduplicated_patents.xlsx"
  },
  "output": {
    "dir": "output",
    "viz_dir": "output/visualizations"
  },
  "year_range": [2020, 2027],
  "classification": {
    "axis1": {
      "name": "기술 유형",
      "other_label": "기타",
      "order": ["Category A", "Category B", "기타"],
      "colors": {"Category A": "#1E88E5", "기타": "#95A5A6"},
      "ipc_map": {"Category A": ["G06N", "G06F"]},
      "keywords": {"Category A": ["keyword1", "keyword2"]}
    },
    "axis2": {
      "name": "적용 분야",
      "other_label": "기타",
      "order": ["Domain X", "Domain Y", "기타"],
      "colors": {"Domain X": "#1565C0", "기타": "#95A5A6"},
      "ipc_map": {},
      "keywords": {"Domain X": ["keyword3"]}
    }
  }
}
```

### Config 필드 설명

| 필드 | 필수 | 설명 |
|------|:----:|------|
| `metadata.title` | O | 보고서 제목 |
| `metadata.dashboard_title` | O | 대시보드 제목 |
| `metadata.period` | - | 분석 기간 텍스트 |
| `metadata.analysis_date` | - | 분석 일자 |
| `input.file` | O | 입력 Excel 파일 경로 |
| `output.dir` | - | 출력 디렉토리 (기본값: `output`) |
| `output.viz_dir` | - | 시각화 디렉토리 (기본값: `output/visualizations`) |
| `year_range` | - | [시작연도, 끝연도+1] (기본값: [2020, 2027]) |
| `classification.axis1` | O | 분류 축 1 설정 |
| `classification.axis2` | O | 분류 축 2 설정 |

### 축(axis) 설정 필드

| 필드 | 필수 | 설명 |
|------|:----:|------|
| `name` | O | 축 이름 (예: "기술 유형") |
| `other_label` | - | 미분류 레이블 (기본값: "기타") |
| `order` | O | 카테고리 정렬 순서 배열 |
| `colors` | O | 카테고리별 HEX 색상 맵 |
| `ipc_map` | - | 카테고리별 IPC 코드 접두사 배열 |
| `keywords` | - | 카테고리별 키워드 배열 |

---

## Classification Logic

분류는 IPC 우선 → 키워드 폴백 → "Other" 순서로 양 축 모두 동일하게 적용됩니다.

```
for each patent:
    for each axis:
        category = match_ipc(ipcNumber, axis.ipc_map)
                   or match_keywords(title + abstract, axis.keywords)
                   or axis.other_label
```

키워드 매칭은 점수 기반 — 가장 많은 키워드가 매칭된 카테고리가 선택됩니다.

---

## 5 Analysis Types

1. **Distribution** — 각 분류 축별 카테고리 건수 비율
2. **Cross-tabulation** — 축 1 × 축 2 교차표 히트맵
3. **Yearly Trends** — 연도별 카테고리별 출원 추이
4. **White Space** — 저밀도 (축1, 축2) 조합 식별 (임계값: 25% 분위수)
5. **Institutional Ranking** — Top 20 출원인 × 주력 기술축 분포

---

## Mandatory Output (FIXED — 파일명 변경 금지)

```
output/
├── classification_config.json          # 분류 설정 (에이전트 생성)
├── deduplicated_patents.xlsx           # 입력 데이터 (병합 시)
├── patent_analysis_report.xlsx         # Excel 보고서 (6 시트)
│   ├── Sheet: All_Patents
│   ├── Sheet: Distribution
│   ├── Sheet: Cross_Tabulation
│   ├── Sheet: Yearly_Trends
│   ├── Sheet: White_Space
│   └── Sheet: Top_Institutions
├── patent_classification_summary.md    # Markdown 요약 (7 섹션)
└── visualizations/
    ├── axis1_distribution.png          # 축 1 파이차트
    ├── axis2_distribution.png          # 축 2 수평 바차트
    ├── cross_tabulation_heatmap.png    # 축 1 × 축 2 히트맵
    ├── yearly_trend.png               # 연도별 카테고리 추이
    ├── white_space_analysis.png        # 화이트스페이스 (★ 표시)
    ├── top_institutions.png            # 상위 20 누적 바차트
    ├── institution_by_category.png     # 상위 10 그룹 바차트
    ├── combined_dashboard.png          # 3×3 종합 대시보드
    └── patent_dashboard.html           # 인터랙티브 대시보드
```

**11개 파일이 모두 생성되어야 분석 완료로 간주합니다.**
