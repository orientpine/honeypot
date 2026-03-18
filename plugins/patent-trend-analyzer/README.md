# patent-trend-analyzer

> ⚠️ **해외 특허 서비스 신규 구독 시 주의**: KIPRIS Plus에서 해외특허 API를 새로 구독하면 서버 전파에 1~2일이 소요됩니다. 전파 완료 전에는 로드밸런서에 따라 간헐적으로 `AccessKey Not Registered` 에러가 발생할 수 있습니다. 한국 특허 API는 즉시 사용 가능합니다.

> KIPRIS API 기반 특허 동향 분석 플러그인 — 키워드 최적화, 검색, 다축 분류, 시각화 대시보드 생성

**Version**: 1.3.0  
**License**: MIT

---

## 개요

특정 기술 도메인에 종속되지 않는 **범용 특허 동향 분석** 플러그인입니다. 연구 주제를 입력하면 3단계 파이프라인(계획 → 검색 → 분석)을 거쳐 분류, 트렌드 분석, 시각화 대시보드까지 자동으로 생성합니다.

```
L1 Planning ──→ L2 Search ──→ L3 Analysis
  키워드 최적화      KIPRIS 검색      분류 + 시각화
  IPC 매핑           배치 내보내기    차트 + 대시보드
  검색 전략           중복 제거        Excel + 보고서
```

---

## 사전 준비

### 1. KIPRIS Open API 키 발급

[KIPRIS Plus 포털](https://plus.kipris.or.kr/portal/main.do)에서 아래 5단계를 따릅니다.

| 단계 | 작업 | 상세 |
|:----:|------|------|
| **STEP 1** | 회원 가입 | 개인 또는 단체로 가입. 법인계좌/카드 이용 시 단체회원으로 가입 |
| **STEP 2** | 서비스 조회 | Open API 메뉴 클릭 → 데이터 상품 조회 → 원하는 상품 선택 |
| **STEP 3** | 구매 신청 | 장바구니에서 서비스 이용 조건·할인 유형 정보 입력. 관리자 승인 후 결제 가능 상태 (마이 페이지 확인) |
| **STEP 4** | 수수료 결제 | 마이페이지에서 견적서 출력 및 수수료 결제 (계좌이체/신용카드). 결제 오류·환불은 담당자 문의 |
| **STEP 5** | 서비스 이용 | 마이 페이지 > **APIKEY 관리**에서 인증키 확인 후 서비스 이용 |

### 2. 시스템 요구사항

- Python 3.11 이상
- Claude Code 또는 OpenCode (마켓플레이스 등록 필요)
- Python 패키지: `pandas`, `matplotlib`, `seaborn`, `plotly`, `openpyxl`

---

## 설치

### Step 1. 마켓플레이스 등록

```bash
# Claude Code / OpenCode에서 실행
/plugin marketplace add /path/to/honeypot
```

### Step 2. MCP 서버 설치 및 설정 (자동)

아래 명령 한 줄로 MCP 서버 설치 + 설정 파일 등록이 자동으로 수행됩니다.

```
/patent-trend-analyzer:patent-mcp-setup {발급받은_API_키} 설정해줘
```

자동 설정 스킬이 수행하는 작업:
1. API 키가 없으면 KIPRIS Plus 발급 절차 안내
2. Python venv 생성 (`~/.kipris-mcp-venv`) 및 패키지 설치
3. Claude Code / OpenCode 설정 파일에 MCP 서버 등록 (각 클라이언트별 올바른 형식으로)
4. 18개 도구 등록 확인

완료 후 클라이언트를 재시작하면 MCP 서버가 연결됩니다.

<details>
<summary>수동 설정 (참고)</summary>

#### 패키지 설치

시스템 Python에 직접 설치하면 `externally-managed-environment` 오류가 발생할 수 있습니다. venv를 사용하세요.

```bash
# uv가 있는 경우 (권장)
uv venv ~/.kipris-mcp-venv --python 3.12
uv pip install -e /path/to/honeypot/plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/ \
  --python ~/.kipris-mcp-venv/bin/python3

# uv가 없는 경우
python3 -m venv ~/.kipris-mcp-venv
~/.kipris-mcp-venv/bin/pip install -e /path/to/honeypot/plugins/patent-trend-analyzer/skills/patent-mcp-setup/scripts/
```

#### Claude Code 설정

설정 파일: `~/.claude/settings.json`

`mcpServers` 섹션에 아래 항목을 추가합니다.

```json
{
  "mcpServers": {
    "kipris": {
      "command": "/home/user/.kipris-mcp-venv/bin/python3",
      "args": ["-m", "mcp_kipris.server"],
      "env": {
        "KIPRIS_API_KEY": "발급받은_API_키"
      }
    }
  }
}
```

#### OpenCode 설정

설정 파일: `~/.config/opencode/opencode.json`

> **주의**: OpenCode는 Claude Code와 설정 형식이 다릅니다 (`"mcp"` 키, `"command"` 배열, `"environment"` 키).

`mcp` 섹션에 아래 항목을 추가합니다.

```json
{
  "mcp": {
    "kipris": {
      "type": "local",
      "command": ["/home/user/.kipris-mcp-venv/bin/python3", "-m", "mcp_kipris.server"],
      "enabled": true,
      "environment": {
        "KIPRIS_API_KEY": "발급받은_API_키"
      }
    }
  }
}
```

</details>

### Step 3. 설치 확인

```bash
KIPRIS_API_KEY=your_key ~/.kipris-mcp-venv/bin/python3 -c "
from mcp_kipris.kipris._registry import get_all_tools
tools = get_all_tools()
print(f'{len(tools)} tools registered')
"
```

정상 출력: `18 tools registered`

---

## 사용법

### 전체 파이프라인 실행 (권장)

```
@patent-trend-analyzer "자율주행 라이다 센서" 주제로 특허 동향 분석을 해줘.
대상 국가는 한국, 미국이고 분석 기간은 2020-2025년이야.
```

오케스트레이터가 3개 에이전트를 순서대로 호출합니다:

1. **patent-planner** → 키워드 최적화 + IPC 매핑 + 검색 전략 수립
2. **patent-searcher** → KIPRIS API 검색 실행 + 중복 제거
3. **patent-analyzer** → 분류 + 트렌드 분석 + 시각화

### 개별 단계 실행

각 단계를 독립적으로 실행할 수도 있습니다.

#### L1. 검색 계획 수립만

```
@patent-trend-analyzer 의 patent-planner를 사용해서 "전고체 배터리" 관련 특허 검색 전략을 세워줘.
IPC 코드 H01M 중심으로, 한국/미국/유럽 대상, 2019-2024년.
```

#### L2. 검색 실행만 (L1 결과 필요)

```
@patent-trend-analyzer 의 patent-searcher를 사용해서 위에서 만든 검색 계획대로 특허 검색을 실행해줘.
```

#### L3. 분석/시각화만 (L2 결과 필요)

```
@patent-trend-analyzer 의 patent-analyzer를 사용해서 output/deduplicated_patents.xlsx 파일을 분석해줘.
```

---

## 입력 파라미터

| 파라미터 | 필수 | 설명 | 예시 |
|----------|:----:|------|------|
| 연구 주제 | O | 분석할 기술 분야 | "CRISPR 유전자 편집" |
| 대상 국가 | - | 검색 대상 국가 | 한국, 미국, 유럽 (기본값) |
| 분석 기간 | - | 출원일 기준 기간 | 2020-2025 |
| IPC 코드 | - | 특정 IPC 코드 지정 | G06N, H01M 10/ |

---

## 파이프라인 상세

### Phase 1: Research Planning (patent-planner)

| 단계 | 작업 | 사용 도구 |
|------|------|-----------|
| 1 | 연구 주제 파악 및 범위 설정 | - |
| 2 | 키워드 최적화 (동의어 확장, 중복 제거) | `patent_keyword_optimizer` |
| 3 | IPC 코드 매핑 및 분류 체계 설계 | `patent_keyword_optimizer` |
| 4 | 검색 전략 수립 (IPC x 키워드 x 국가) | `patent_search_planner` |
| 5 | 검색 계획 제시 및 사용자 확인 | - |

**출력물:**
- 최적화된 키워드 목록 (한영 병기)
- IPC 코드 매핑 테이블
- 검색 전략 테이블 (우선순위 포함)
- API 호출 예산 분석

### Phase 2: Search & Collection (patent-searcher)

| 단계 | 작업 | 사용 도구 |
|------|------|-----------|
| 1 | 검색 계획 파싱 | - |
| 2 | 검색 실행 (결과 수에 따라 자동 선택) | `patent_batch_export`, `patent_free_search` 등 |
| 3 | 다국가 순차 검색 (US → EP → JP → CN → KR) | `foreign_patent_batch_export` 등 |
| 4 | 교차 쿼리 중복 제거 | `patent_result_deduplicator` |
| 5 | 수집 통계 보고서 생성 | - |

**검색 방식 자동 선택:**
- 예상 결과 > 30건 → **배치 내보내기** (자동 페이지네이션)
- 예상 결과 ≤ 30건 → **빠른 검색** (단일 페이지)

**출력물:**
- `output/deduplicated_patents.xlsx` — 중복 제거된 통합 데이터
- 국가별/쿼리별 개별 Excel 파일
- 수집 통계 보고서

### Phase 3: Analysis & Visualization (patent-analyzer)

| 단계 | 작업 | 결과물 |
|------|------|--------|
| 1 | 데이터 로드 및 검증 | - |
| 2 | 분류 체계 적용 (IPC 우선 → 키워드 폴백) | 분류 레이블 |
| 3 | 도메인 필터링 + 기관 필터링 | 정제된 데이터셋 |
| 4 | 5종 분석 (분포/교차/트렌드/화이트스페이스/기관) | 분석 결과 |
| 5 | 정적 차트 생성 (Matplotlib, 150 DPI) | PNG 8장 + 통합 대시보드 |
| 6 | 인터랙티브 대시보드 생성 (Plotly) | HTML 1개 |
| 7 | Excel + Markdown 보고서 내보내기 | xlsx + md |

**5종 분석:**

| 분석 유형 | 설명 |
|-----------|------|
| Distribution | 분류 축별 비율 분석 |
| Cross-tabulation | 축 1 × 축 2 교차표 히트맵 |
| Yearly Trends | 연도별 출원 추이 |
| White Space | 특허 밀도 낮은 영역 = 기회 영역 |
| Institutional Ranking | Top 20 출원인 + 카테고리별 분포 |

---

## 출력 구조

```
output/
├── deduplicated_patents.xlsx            # 중복 제거된 원본 데이터
├── patent_analysis_report.xlsx          # 다중시트 분석 보고서
│   ├── Sheet: Raw                       #   원본 + 분류 레이블
│   ├── Sheet: Distribution              #   분포 집계
│   ├── Sheet: CrossTab                  #   교차표
│   ├── Sheet: YearlyTrend               #   연도별 추이
│   ├── Sheet: WhiteSpace                #   화이트스페이스
│   └── Sheet: TopInstitutions           #   기관 랭킹
├── patent_classification_summary.md     # Markdown 요약 보고서
├── search_statistics.md                 # 검색 통계 보고서
└── visualizations/
    ├── axis1_distribution.png           # 분류 축 1 파이차트
    ├── axis2_distribution.png           # 분류 축 2 바차트
    ├── cross_tabulation_heatmap.png     # 축 1 × 축 2 히트맵
    ├── yearly_trend.png                 # 연도별 출원 추이
    ├── white_space_analysis.png         # 화이트스페이스 시각화
    ├── top_institutions.png             # 기관 랭킹 바차트
    ├── institution_by_category.png      # 카테고리별 기관 분포
    ├── combined_dashboard.png           # 통합 대시보드 (3x3)
    └── patent_dashboard.html            # 인터랙티브 대시보드
```

---

## 플러그인 구성

### Agents (3)

| Agent | 역할 | Model |
|-------|------|:-----:|
| `patent-planner` | 키워드 최적화, IPC 매핑, 검색 전략 수립 | sonnet |
| `patent-searcher` | KIPRIS API 검색 실행, 배치 내보내기, 중복 제거 | sonnet |
| `patent-analyzer` | 분류 체계 적용, 트렌드 분석, 시각화, 보고서 생성 | sonnet |

### Command (1)

| Command | 설명 |
|---------|------|
| `analyze-patents` | 전체 파이프라인 오케스트레이터 (L1 → L2 → L3) |

### Skills (5)

| Skill | 설명 |
|-------|------|
| `patent-mcp-setup` | KIPRIS MCP 서버 설치 및 설정 가이드 |
| `patent-research-planning` | 키워드 최적화, IPC 매핑, 검색 전략 수립 절차 |
| `patent-search-collect` | 특허 검색 실행, 배치 내보내기, 중복 제거 절차 |
| `patent-analysis-viz` | 분류, 트렌드 분석, 시각화 대시보드 생성 절차 |
| `ipc-classification-guide` | IPC/CPC 코드 구조 및 기술 분야별 코드 가이드 |

### MCP Tools (18)

#### 한국 특허 검색 (8)

| 도구 | 설명 |
|------|------|
| `patent_free_search` | 자유 키워드 검색 |
| `patent_applicant_search` | 출원인 기반 검색 |
| `patent_application_number_search` | 출원번호 기반 검색 |
| `patent_search` | IPC + 키워드 통합 검색 |
| `patent_detail_search` | 특허 상세 정보 조회 |
| `patent_summary_search` | 요약 기반 검색 |
| `patent_righter_search` | 권리자 기반 검색 |
| `patent_batch_export` | 배치 내보내기 (Excel) |

#### 해외 특허 검색 (7)

| 도구 | 설명 |
|------|------|
| `foreign_patent_free_search` | 국가별 자유 키워드 검색 |
| `foreign_patent_applicant_search` | 국가별 출원인 검색 |
| `foreign_patent_application_number_search` | 국가별 출원번호 검색 |
| `foreign_international_application_number_search` | PCT 국제출원번호 검색 |
| `foreign_international_open_number_search` | PCT 국제공개번호 검색 |
| `foreign_patent_batch_export` | 해외 특허 배치 내보내기 |
| `foreign_patent_ipc_batch_export` | IPC 기반 해외 배치 내보내기 |

#### 전처리 (3)

| 도구 | 설명 |
|------|------|
| `patent_search_planner` | 검색 전략 수립 도우미 |
| `patent_keyword_optimizer` | 키워드 최적화 도우미 |
| `patent_result_deduplicator` | 검색 결과 중복 제거 |

---

## IPC 코드 가이드

### IPC 코드 구조

```
 H   01   L    21  /  331
 |    |    |    |      |
 |    |    |    |      +-- Subgroup (세부 기술)
 |    |    |    +-- Main Group (기술 영역)
 |    |    +-- Subclass (전문 분야)
 |    +-- Class (주요 분야)
 +-- Section (대분류, A-H)
```

### 주요 기술 분야별 IPC 코드

| 분야 | 주요 IPC 코드 |
|------|--------------|
| AI / 머신러닝 | G06N 3/ (신경망), G06N 20/ (기계학습), G06F 18/ (패턴 인식) |
| 반도체 | H01L 21/ (제조), H01L 27/ (집적회로), H10B (메모리) |
| 배터리 | H01M 4/ (전극), H01M 10/ (이차전지), H02J 7/ (충전) |
| 바이오/의료 | A61B 5/ (진단), C12N 15/ (유전공학), G01N 33/ (면역분석) |
| 자율주행 | B60W 60/ (자율주행), G05D 1/ (이동체 제어) |
| 통신 | H04L 1/ (통신), H04W 4/ (무선서비스), H04B 7/ (무선전송) |

> 상세 IPC 코드 체계는 `skills/ipc-classification-guide/references/g06n-scheme.md` 참조 (현재 G06N 지원).  
> 다른 기술 분야가 필요하면 [WIPO IPC](https://www.wipo.int/classifications/ipc/en/)에서 확인 후 `references/`에 추가할 수 있습니다.

---

## 사용 팁

- **넓게 시작해서 좁히기**: 처음엔 상위 IPC 코드(예: `H01M 10/`)로 시작하고, 결과가 많으면 하위 코드로 좁힙니다.
- **최신순 정렬**: `desc_sort=true` + `sort_spec="AD"` 조합으로 최신 출원 우선 정렬.
- **배치 자동 종료**: 배치 내보내기는 빈 페이지 감지 시 자동 중단됩니다.
- **다국어 병행**: 같은 개념도 한국어/영어 키워드의 검색 결과가 다를 수 있으므로 병행 검색을 권장합니다.
- **중간 저장**: API 호출은 비용이 발생하므로 중간 결과를 자주 저장하세요.
- **단계별 실행**: 각 Phase는 독립 실행 가능합니다. 중간에 실패해도 해당 Phase만 재실행하면 됩니다.

---

## 트러블슈팅

### MCP 서버가 연결되지 않을 때

1. Python 버전 확인: `python3 --version` (3.11 이상)
2. venv 확인: `ls ~/.kipris-mcp-venv/bin/python3`
3. 패키지 설치 확인: `~/.kipris-mcp-venv/bin/pip show mcp-kipris`
4. API 키 확인: 설정 파일에서 `KIPRIS_API_KEY` 값 확인
5. 직접 실행 테스트: `KIPRIS_API_KEY=your_key ~/.kipris-mcp-venv/bin/python3 -m mcp_kipris.server`

### API 인증 오류 (401/403)

- data.go.kr 서비스 신청 승인 상태 확인 (1~2일 소요)
- `KIPRIS_API_KEY` 환경변수가 올바르게 설정되어 있는지 확인

### 도구 수가 18개 미만일 때

```bash
# uv가 있는 경우
uv pip install -e /path/to/skills/patent-mcp-setup/scripts/ \
  --python ~/.kipris-mcp-venv/bin/python3 --force-reinstall

# uv가 없는 경우
~/.kipris-mcp-venv/bin/pip install -e /path/to/skills/patent-mcp-setup/scripts/ --force-reinstall
```

이후 클라이언트 재시작.

### 한글 폰트 깨짐 (차트)

Matplotlib이 NanumGothic 폰트를 찾지 못하는 경우:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum

# 폰트 캐시 갱신
python -c "import matplotlib; matplotlib.font_manager._load_fontmanager(try_read_cache=False)"
```
