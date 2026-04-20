# Honeypot

> Claude Code 플러그인 마켓플레이스 — AI 에이전트 기반 문서 생성, 시각자료, 투자 분석, 특허 분석, 개발 도구

**Version**: 3.28.0 &nbsp;|&nbsp; **Author**: [Baekdong Cha](https://github.com/orientpine) &nbsp;|&nbsp; **License**: MIT

---

## 빠른 시작

**Step 1.** 마켓플레이스 등록

```bash
/plugin marketplace add /path/to/honeypot
```

**Step 2.** 플러그인 호출

```bash
# 시각자료 생성
/visual-generator:visual-generate 발표 자료를 만들어줘
입력 문서: ./proposal.md
테마: seminar

# 특허 동향 분석
/patent-trend-analyzer:analyze-patents "자율주행 라이다" 주제로 특허 동향 분석을 해줘

# 연구계획서 생성
/isd-generator:isd-generate 연구계획서를 생성해줘
```

---

## 플러그인 한눈에 보기

| 카테고리 | 플러그인 | 설명 |
|:--------:|----------|------|
| 문서 | [**isd-generator**](#isd-generator) | ISD 연구계획서 5개 Chapter 자동 생성 |
| 문서 | [**report-generator**](#report-generator) | 연구 노트 → 국가기관 제출용 보고서 |
| 문서 | [**hwpx-generator**](#hwpx-generator) | HWPX 한글 문서 생성/편집/분석 |
| 시각 | [**visual-generator**](#visual-generator) | 6개 테마 시각자료 프롬프트 생성 + Gemini 렌더링 |
| 시각 | [**pptx-design-styles**](#pptx-design-styles) | 30가지 모던 PPTX 디자인 스타일 가이드 (HEX, 폰트, 레이아웃) |
| 논문 | [**paper-style-generator**](#paper-style-generator) | PDF 논문 분석 → 논문 작성 스킬 세트 자동 생성 |
| 투자 | [**investments-portfolio**](#investments-portfolio) | DC형 퇴직연금 포트폴리오 멀티 에이전트 분석 |
| 투자 | [**stock-consultation**](#stock-consultation) | 주식/ETF 투자 상담 (Bogle/Vanguard 철학) |
| 투자 | [**equity-research**](#equity-research) | 기관급 주식 분석 리포트 생성 |
| 투자 | [**macro-analysis**](#macro-analysis) | 거시경제 분석 공용 에이전트 7종 |
| 분석 | [**patent-trend-analyzer**](#patent-trend-analyzer) | KIPRIS API 기반 특허 동향 분석 + 시각화 |
| 도구 | [**plugin-dev**](#plugin-dev) | Claude Code 플러그인 개발 종합 툴킷 [^1] |
| 도구 | [**worktree-workflow**](#worktree-workflow) | Git worktree 기반 병렬 실행 |
| 도구 | [**general-agents**](#general-agents) | 범용 에이전트 (심층 인터뷰 등) |
| 도구 | [**obsidian-skills**](#obsidian-skills) | Obsidian vault 파일 작성 — Markdown, Bases, Canvas, CLI, Defuddle |
| 학습 | [**accelerated-learner**](#accelerated-learner) | 48시간 가속 학습 — 소스 분석, 멘탈모델, 논쟁 매핑, 소크라틱 튜터링 |
| 도구 | [**wiki-gen**](#wiki-gen) | 개인 일기/노트를 Wikipedia 스타일 지식 위키로 컴파일 [^3] |
| 도구 | [**link-curator**](#link-curator) | URL → Korean MD summary + HoneyCombo 제출 |

---

<br>

# 문서 생성

---

## isd-generator

> ISD(기업부설연구소) 국책과제 연구계획서 5개 Chapter를 자동 생성합니다.

### 사용법

```
/isd-generator:isd-generate 연구계획서를 생성해줘
```

### 사전 준비

`input-template` 스킬 양식에 맞춰 **통합 입력 파일**을 작성해야 합니다. 입력 파일에는 프로젝트 개요, 연구 목표, 기술 내용 등의 섹션이 포함됩니다.

### 주요 특징

- **생성 순서**: Chapter 3 → 1 → 2 → 4 → 5 (의존성 기반)
- **검증문서 필수**: 각 Chapter 본문 작성 전 검증문서가 자동 생성됨
- **이미지 자동 생성**: Gemini API로 캡션 기반 이미지 생성
- **출력 경로**: `output/[프로젝트명]/chapter_{1-5}/`

<details>
<summary>구성 요소 (6 Agents · 1 Command · 11 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | chapter1, chapter2, chapter3, chapter4, chapter5, figure |
| Command | `isd-generate` (오케스트레이터) |
| Skills | chapter1~5-guide, core-resources, data-collection-guide, figure-guide, image-reference-guide, input-template, verification-rules |

</details>

---

## report-generator

> 연구 노트를 분석하여 공학 박사 수준의 국가기관 제출용 연구 보고서를 자동 생성합니다.

### 사용법

```
/report-generator:report-generate 연구 보고서를 생성해줘
입력 경로: ./research_notes/
프로젝트명: HR35_자율굴착기
```

### 주요 특징

- **다양한 입력 지원**: 폴더, 단일 파일, 코드 + 노트
- **도메인 자동 감지**: ROS2, AI/ML, 범용
- **최대 9개 챕터**: 자료 부족 챕터는 자동 생략 (최소 3개 보장)
- **4단계 문장 패턴**: What → Why → How → Impact

| 파라미터 | 필수 | 설명 | 예시 |
|----------|:----:|------|------|
| `input_path` | O | 연구 노트 경로 | `./research_notes/` |
| `project_name` | O | 프로젝트명 | `HR35_자율굴착기` |
| `code_path` | - | 코드베이스 경로 | `/home/user/ros2_ws/src/` |
| `output_dir` | - | 출력 디렉토리 | `./output/` (기본값) |
| `auto_mode` | - | 자동 진행 여부 | `true` / `false` (기본값) |

<details>
<summary>구성 요소 (4 Agents · 1 Command · 3 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | input-analyzer, content-mapper, chapter-writer, quality-checker |
| Command | `report-generate` (오케스트레이터) |
| Skills | chapter-structure, field-keywords, four-step-pattern |

</details>

---

## hwpx-generator

> HWPX(한글) 문서를 XML-first 방식으로 생성, 편집, 분석합니다. Workflow 7: 마크다운 → HWPX 템플릿 채우기 + 이미지 임베딩.

### 사용법

```
# 기본 생성
/hwpx-generator:hwpx-generate 연구 보고서 HWPX 문서를 만들어줘

# 레퍼런스 문서 스타일 참조
/hwpx-generator:hwpx-generate 이 양식과 동일한 스타일로 문서를 만들어줘
reference_hwpx: ./template.hwpx

# 템플릿 기반 생성
/hwpx-generator:hwpx-generate 이 템플릿에 내용을 채워줘
template_hwpx: ./form.hwpx

# Workflow 7: 마크다운 → HWPX 템플릿 채우기 + 이미지 임베딩
/hwpx-generator:hwpx-generate 마크다운 파일을 HWPX 템플릿에 채우고 이미지를 임베딩해줘
markdown_file: ./content.md
template_hwpx: ./form.hwpx
images_dir: ./images/
```

### 주요 특징

- **3가지 생성 경로**: 사용자 템플릿 > 기본 양식 > XML-first 자동 선택
- **ZIP-level surgery**: `zip_surgery.py`로 안전한 ZIP 내부 편집
- **네임스페이스 자동 수정**: `fix_namespaces.py` 필수 적용
- **뷰어 호환성**: `<hp:linesegarray>` 자동 생성으로 한컴오피스 외 뷰어 지원
- **Workflow 7**: 마크다운 → JSON 블록 파싱 → HWPX XML 작성 → 이미지 임베딩 (md_parser.py, xml_writer.py, image_embedder.py)
- **챕터 이식**: `section_transplant.py`로 HWPX 간 챕터 단위 콘텐츠 이식 + 스타일 자동 리매핑

| 파라미터 | 필수 | 설명 |
|----------|:----:|------|
| `ARGUMENTS` | O | 문서 유형, 목적, 포함할 내용 |
| `reference_hwpx` | - | 스타일 분석용 레퍼런스 `.hwpx` |
| `template_hwpx` | - | 사용자 업로드 템플릿 `.hwpx` |
| `output_dir` | - | 결과 폴더 (기본값: `./output/hwpx/`) |

<details>
<summary>구성 요소 (2 Agents · 1 Command · 2 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | hwpx-builder, hwpx-analyzer |
| Command | `hwpx-generate` (오케스트레이터) |
| Skills | hwpx-core, hwpx-templates |

</details>

---

<br>

# 시각자료 & 논문

---

## visual-generator

> 입력 문서를 분석하여 6개 테마 시각자료 프롬프트를 생성하고 Gemini API로 렌더링합니다.

### 사용법

```
/visual-generator:visual-generate 시각자료를 생성해줘
입력 문서: ./research_proposal.md
무드: tech-focus
테마: gov
출력 폴더: ./output/visuals/
```

| 파라미터 | 필수 | 설명 | 기본값 |
|----------|:----:|------|--------|
| `input_document` | O | 입력 문서 경로 (연구계획서, 사업계획서, 기술문서 등) | - |
| `theme` | - | 테마 유형 | `gov` |
| `mood` | - | 무드 선택 (9종) | `clarity` |
| `layout` | - | 레이아웃 유형 (24종) | 자동 선택 |
| `output_folder` | O | 출력 폴더 경로 | - |

> **테마**: `concept` · `gov` · `seminar` · `whatif` · `pitch` · `comparison`
>
> **무드**: `technical-report` · `clarity` · `tech-focus` · `growth` · `connection` · `innovation` · `knowledge` · `presentation` · `workshop`

### 에이전트 파이프라인

```
content-organizer → content-reviewer → prompt-designer → prompt-validator → renderer-agent
```

### 테마 갤러리

동일한 주제(스마트 팩토리)를 6개 테마로 시각화한 예시:

<table>
<tr>
<td width="50%">

**concept** — Kurzgesagt 풍 시각 스토리텔링

텍스트 없이 장면과 시각적 메타포만으로 개념을 전달

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/01_theme_concept.png" width="100%" alt="Concept Theme">

</td>
<td width="50%">

**gov** — 정부/공공기관 PPT

굵은 테두리 박스에 번호가 매겨진 체계적 격자

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/02_theme_gov.png" width="100%" alt="Gov Theme">

</td>
</tr>
<tr>
<td>

**seminar** — 세미나/학술 발표

에디토리얼 매거진 × 아이소메트릭 3D

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/03_theme_seminar.png" width="100%" alt="Seminar Theme">

</td>
<td>

**whatif** — 미래 비전 스냅샷

공상과학 영화 UI처럼 빛나는 HUD

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/04_theme_whatif.png" width="100%" alt="What-If Theme">

</td>
</tr>
<tr>
<td>

**pitch** — 피치덱

Apple 키노트처럼 어두운 그래디언트 위의 거대한 숫자

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/05_theme_pitch.png" width="100%" alt="Pitch Theme">

</td>
<td>

**comparison** — Before/After 비교

IMAX 분할 화면처럼 좌우 풀블리드 이미지

<img src="https://raw.githubusercontent.com/orientpine/honeypot/058be21/assets/theme-examples/images/06_theme_comparison.png" width="100%" alt="Comparison Theme">

</td>
</tr>
</table>

<details>
<summary>구성 요소 (5 Agents · 1 Command · 8 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | content-organizer, content-reviewer, prompt-designer, prompt-validator, renderer-agent |
| Command | `visual-generate` (오케스트레이터) |
| Skills | layout-types, theme-concept, theme-gov, theme-seminar, theme-whatif, theme-pitch, theme-comparison, slide-renderer |

</details>

---

## paper-style-generator

> PDF 논문 컬렉션을 분석하여 저자/연구그룹의 논문 작성 스타일을 추출하고, Claude Code 스킬 세트를 자동 생성하는 메타-플러그인입니다.

### 사용법

```
/paper-style-generator:paper-style-generate PDF 논문 폴더를 분석하여 논문 작성 스킬 세트를 생성해줘
PDF 폴더: ./papers/
플러그인 이름: mylab
```

### 사전 준비

- **PDF 논문 10편 이상** (동일 저자 또는 동일 분야)
- **MinerU** 설치 필요 (PDF → Markdown 변환용)

### 워크플로우

```
PDF 수집 → MinerU 변환 → 스타일 분석 → 플러그인 생성
```

### 생성되는 플러그인 구조

`{CWD}/my-marketplace/plugins/{name}-paper-skills/` 에 아래 구성이 자동 생성됩니다:

| 유형 | 이름 | 역할 |
|------|------|------|
| Command | `{name}-paper-generate` | 논문 전체 생성 오케스트레이터 |
| Agent | `{name}-title-writer` | 논문 제목 생성 |
| Agent | `{name}-abstract-writer` | Abstract 작성 |
| Agent | `{name}-introduction-writer` | Introduction 작성 |
| Agent | `{name}-methodology-writer` | Methods 작성 |
| Agent | `{name}-results-writer` | Results 작성 |
| Agent | `{name}-discussion-writer` | Discussion 작성 |
| Agent | `{name}-caption-writer` | Figure/Table 캡션 작성 |
| Agent | `{name}-verify` | 일관성 검증 (읽기 전용) |
| Skill | `{name}-style-guide` | 공통 스타일 가이드 + 11개 참조 문서 |

### 추출되는 스타일 패턴

- Voice ratio (능동/수동) 섹션별 비율
- Tense 패턴 (과거/현재)
- "We" 사용 비율 (Results에서 ≤30% 타겟)
- 고빈도 학술 동사, 전환어
- 측정 포맷팅, 인용 스타일, 분야 특성

<details>
<summary>구성 요소 (3 Agents · 1 Command · 1 Skill)</summary>

| 유형 | 항목 |
|------|------|
| Agents | pdf-converter, style-analyzer, skill-generator |
| Command | `paper-style-generate` (오케스트레이터) |
| Skills | paper-style-toolkit (스크립트, 템플릿, 참조자료) |

</details>

---

<br>

# 투자·금융

---

## investments-portfolio

> DC형 퇴직연금 포트폴리오를 멀티 에이전트 시스템으로 분석합니다.

### 사용법

```
/investments-portfolio:portfolio-analyze 포트폴리오 분석을 시작해줘

# 투자 프로파일 지정
/investments-portfolio:portfolio-analyze 안정형 프로파일로 포트폴리오 분석을 해줘
```

### 워크플로우

```
거시경제 분석 (macro-analysis 5종)
        ↓
    분석 종합 + 검증
        ↓
  펀드 추천 + 규제 검증 (DC 70% 한도)
        ↓
    출력 검증 + 자료 정리
```

### 주요 특징

- **거시경제 분석 통합**: 지수, 금리, 섹터, 리스크, 리더십 5개 에이전트 병렬 분석
- **Bogle/Vanguard 철학**: 저비용 인덱스 펀드 중심 추천
- **DC 규제 자동 검증**: 위험자산 70% 한도 등 규제 준수 확인
- **출력**: `portfolios/YYYY-MM-DD-{profile}-{session}/` 폴더에 5개 보고서

<details>
<summary>구성 요소 (3 Agents · 1 Command · 11 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | fund-portfolio, compliance-checker, output-critic |
| Command | `portfolio-analyze` (오케스트레이터) |
| Skills | analyst-common, bogle-principles, data-updater, dc-pension-rules, devil-advocate, file-save-protocol, fund-output-template, fund-selection-criteria, macro-output-template, perspective-balance, web-search-verifier |

**참고**: 거시경제 분석은 [macro-analysis](#macro-analysis) 플러그인의 7개 에이전트를 공유합니다.

</details>

---

## stock-consultation

> 주식/ETF 투자 상담을 Bogle/Vanguard 철학 기반 멀티 에이전트 시스템으로 수행합니다.

### 사용법

```
# 종목 상담
/stock-consultation:stock-consult AAPL 투자 상담을 해줘

# 주제별 상담
/stock-consultation:stock-consult 반도체 섹터 ETF 추천해줘

# 자료 제공 시
/stock-consultation:stock-consult TSLA 분석해줘
materials_path: ./research_data/
```

### 워크플로우

```
거시경제 분석 → 종목 스크리닝 → 밸류에이션 → 반대 논거 → 최종 검증
```

### 주요 특징

- **5단계 파이프라인**: 거시 분석부터 Bear Case까지 체계적 검증
- **Devil's Advocate**: 반대 논거 에이전트가 투자 위험을 적극 검증
- **데이터 검증**: 실시간 웹 검색 기반 수치 정확성 확인

<details>
<summary>구성 요소 (5 Agents · 1 Command · 3 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | materials-organizer, stock-screener, stock-valuation, bear-case-critic, stock-critic |
| Command | `stock-consult` (오케스트레이터) |
| Skills | analyst-common-stock, file-save-protocol-stock, stock-data-verifier |

**참고**: 거시경제 분석은 [macro-analysis](#macro-analysis) 플러그인의 7개 에이전트를 공유합니다.

</details>

---

## equity-research

> 티커와 함께 호출하면 기관급(institutional-grade) 주식 분석 리포트를 생성합니다.

### 사용법

```
# 기본 분석
@equity-research AAPL

# 상세 분석
@equity-research NVDA --detailed
```

### 주요 특징

- **Opus 모델** 기반 고품질 분석
- **3축 병렬 리서치**: 재무 성과, 시장 포지셔닝, 고급 인텔리전스
- **기관급 포맷**: 구체적 수치, 애널리스트 목표가, 기간별 메트릭 포함

| 구성 | 항목 |
|------|------|
| Agent | equity-research-analyst (단일 에이전트) |

---

## macro-analysis

> investments-portfolio, stock-consultation 등에서 공유하는 거시경제 분석 에이전트 7종입니다.

이 플러그인은 단독으로 호출하기보다 다른 투자 플러그인의 **내부 인프라**로 사용됩니다.

| Agent | 역할 |
|-------|------|
| `index-fetcher` | 주요 지수 데이터 수집 |
| `rate-analyst` | 금리 환경 분석 |
| `sector-analyst` | 섹터별 동향 분석 |
| `risk-analyst` | 시장 리스크 분석 |
| `leadership-analyst` | 리더십/정책 영향 분석 |
| `macro-synthesizer` | 5개 분석 결과 종합 |
| `macro-critic` | 종합 분석 검증 |

---

<br>

# 특허 분석

---

## patent-trend-analyzer

> KIPRIS API 기반 특허 동향 분석 — 연구 주제를 입력하면 계획 → 검색 → 분석 3단계 파이프라인을 거쳐 시각화 대시보드까지 자동 생성합니다.

> [!WARNING]
> 해외 특허 서비스 신규 구독 후 1~2일간 서버 전파 지연이 발생할 수 있습니다 (간헐적 `AccessKey Not Registered` 에러). 한국 특허는 즉시 사용 가능.

### 사용법

```
# 전체 파이프라인 실행 (권장)
/patent-trend-analyzer:analyze-patents "자율주행 라이다 센서" 주제로 특허 동향 분석을 해줘
대상 국가는 한국, 미국이고 분석 기간은 2020-2025년이야.
```

```
# L1. 검색 계획만 수립
@patent-trend-analyzer 의 patent-planner를 사용해서 "전고체 배터리" 관련 특허 검색 전략을 세워줘.
IPC 코드 H01M 중심으로, 한국/미국/유럽 대상, 2019-2024년.

# L2. 검색 실행만 (L1 결과 필요)
@patent-trend-analyzer 의 patent-searcher를 사용해서 위에서 만든 검색 계획대로 특허 검색을 실행해줘.

# L3. 분석/시각화만 (L2 결과 필요)
@patent-trend-analyzer 의 patent-analyzer를 사용해서 output/deduplicated_patents.xlsx 파일을 분석해줘.
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|:----:|------|------|
| 연구 주제 | O | 분석할 기술 분야 | "CRISPR 유전자 편집" |
| 대상 국가 | - | 검색 대상 국가 | 한국, 미국, 유럽 (기본값) |
| 분석 기간 | - | 출원일 기준 기간 | 2020-2025 |
| IPC 코드 | - | 특정 IPC 코드 지정 | G06N, H01M 10/ |

### 사전 준비: KIPRIS API 키 발급 + MCP 설정

1. [KIPRIS Plus 포털](https://plus.kipris.or.kr/portal/main.do)에서 API 키 발급 (회원 가입 → 서비스 조회 → 구매 신청 → 수수료 결제 → 인증키 확인, 승인까지 1~2 영업일)
2. MCP 서버 자동 설정:
   ```
   /patent-trend-analyzer:patent-mcp-setup {발급받은_API_키} 설정해줘
   ```
   venv 생성 + 패키지 설치 + 클라이언트 설정 파일 등록까지 자동 수행됩니다.

### 파이프라인

```
L1 Planning ──→ L2 Search ──→ L3 Analysis
 키워드 최적화     KIPRIS 검색     분류 + 시각화
 IPC 매핑          배치 내보내기   차트 + 대시보드
 검색 전략          중복 제거       Excel + 보고서
```

### 출력물

| 단계 | 주요 산출물 |
|------|-------------|
| L1 Planning | 최적화된 키워드, IPC 매핑 테이블, 검색 전략, API 호출 예산 |
| L2 Search | `deduplicated_patents.xlsx`, 국가별 Excel, 수집 통계 |
| L3 Analysis | 8개 PNG 차트, 통합 대시보드, 인터랙티브 HTML, Excel 보고서, Markdown 요약 |

> 파이프라인 상세, 출력 구조, IPC 코드 가이드, 수동 설정 등은 **[patent-trend-analyzer README](./plugins/patent-trend-analyzer/README.md)** 참조

<details>
<summary>구성 요소 (3 Agents · 1 Command · 5 Skills · 18 MCP Tools)</summary>

| 유형 | 항목 |
|------|------|
| Agents | patent-planner, patent-searcher, patent-analyzer |
| Command | `analyze-patents` (오케스트레이터) |
| Skills | patent-mcp-setup, patent-research-planning, patent-search-collect, patent-analysis-viz, ipc-classification-guide |
| MCP Tools | 한국 특허 검색 8종 + 해외 특허 검색 7종 + 전처리 3종 |

</details>

---

<br>

# 개발 도구

---

## plugin-dev

> Claude Code 플러그인(에이전트/커맨드/스킬) 개발을 위한 종합 툴킷입니다. [^1]

### 사용법

```
# 가이드 기반 플러그인 생성 (8단계 워크플로우)
/plugin-dev:create-plugin 데이터베이스 마이그레이션 관리 플러그인

# 개별 스킬 질의
@plugin-dev 플러그인에 MCP 서버를 추가하려면 어떻게 해야 해?
@plugin-dev PreToolUse hook을 만들어줘
@plugin-dev 에이전트 프론트매터 작성법을 알려줘
```

### 7개 전문 스킬

| 스킬 | 역할 |
|------|------|
| hook-development | Hook API, 이벤트 드리븐 자동화, 보안 검증 |
| mcp-integration | MCP 서버 설정, stdio/SSE/HTTP, OAuth |
| plugin-structure | 디렉토리 구조, plugin.json 매니페스트 |
| plugin-settings | `.claude/plugin-name.local.md` 설정 패턴 |
| command-development | 슬래시 커맨드 생성, 프론트매터, 인수 처리 |
| agent-development | 에이전트 생성, AI 보조 생성, 검증 |
| skill-development | 스킬 생성, Progressive Disclosure, 트리거 |

### 주요 특징

- **8단계 워크플로우**: Discovery → Component Planning → Design → Structure → Implementation → Validation → Testing → Documentation
- **AI 보조 에이전트 생성**: Claude Code의 검증된 프롬프트 기반
- **검증 유틸리티**: `validate-agent.sh`, `validate-hook-schema.sh`, `test-hook.sh`

<details>
<summary>구성 요소 (3 Agents · 1 Command · 7 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Agents | agent-creator, plugin-validator, skill-reviewer |
| Command | `create-plugin` (플러그인 생성 워크플로) |
| Skills | hook-development, mcp-integration, plugin-structure, plugin-settings, command-development, agent-development, skill-development |

</details>

---

## worktree-workflow

> Git worktree를 활용하여 Claude Code 인스턴스를 병렬로 실행하는 워크플로우입니다.

### 사용법

```
# worktree 생성
@worktree-workflow worktree 만들어줘

# 특정 브랜치로 생성
@worktree-workflow feature/new-feature 브랜치로 worktree 만들어

# 목록 조회
@worktree-workflow worktree 목록 보여줘

# 삭제
@worktree-workflow worktree 삭제해줘
```

### 주요 특징

- **브랜치명 자동 정규화**: 사용자 입력을 안전한 브랜치명으로 변환
- **tmux 세션 자동 생성**: 생성된 worktree에서 바로 작업 가능
- **한글 에러 메시지**: 직관적인 한글 안내

| 구성 | 항목 |
|------|------|
| Agent | worktree (단일 에이전트) |

---

## general-agents

> 범용 에이전트 모음입니다.

### 사용법

```
# 심층 인터뷰
@general-agents 의 interview 에이전트를 사용해서 프로젝트 요구사항을 인터뷰해줘
```

### interview 에이전트

사용자의 요청에 대해 심층 인터뷰를 진행하여 숨겨진 요구사항을 발굴한 후, 계획을 수립하고 직접 실행합니다.

- **4개 축 인터뷰**: 기술 구현, UI/UX, 우려사항, 트레이드오프
- **계획 → 실행**: 인터뷰 결과를 바탕으로 계획 문서 작성 후 직접 구현

| 구성 | 항목 |
|------|------|
| Agent | interview (단일 에이전트) |

---

<br>

## pptx-design-styles

> 30가지 모던 PPTX 디자인 스타일의 HEX 색상, 폰트 조합, 레이아웃 규칙, 시그니처 요소를 제공하는 디자인 가이드 스킬입니다.
>
> 원본: [corazzon/pptx-design-styles](https://github.com/corazzon/pptx-design-styles) by TodayCode (오늘코드) — MIT License

### 사용 예시

PPTX 슬라이드 생성 시 자동 활성화됩니다. "sleek", "modern", "trendy", "stylish" 등의 키워드에도 반응합니다.

```
# 스타일 지정
@pptx-design-styles Glassmorphism 스타일로 AI 제품 발표 자료를 구성해줘

# 자동 추천
@pptx-design-styles 스타트업 피치덱에 어울리는 스타일을 추천해줘
```

### 30가지 디자인 스타일

| # | 스타일 | 무드 | 추천 용도 |
|---|-------|------|----------|
| 01 | Glassmorphism | 프리미엄 · 테크 | SaaS, AI |
| 02 | Neo-Brutalism | 강렬함 · 스타트업 | 피치 덱 |
| 03 | Bento Grid | 모듈형 · 구조적 | 제품 기능 |
| 04 | Dark Academia | 학술적 · 세련됨 | 교육, 연구 |
| 05 | Gradient Mesh | 예술적 · 생동감 | 브랜드 런칭 |
| 06 | Claymorphism | 친근함 · 3D | 앱, 교육 |
| 07 | Swiss International | 기능적 · 기업용 | 컨설팅, 금융 |
| 08~30 | ... 23가지 추가 | 다양한 무드 | 전체 목록: SKILL.md |

### 스타일 선택 가이드

| 목적 | 추천 스타일 |
|------|-------------|
| 테크 / AI / 스타트업 | Glassmorphism, Aurora Neon, Cyberpunk, SciFi Holographic |
| 기업 / 금융 | Swiss International, Monochrome, Editorial Magazine |
| 브랜드 / 마케팅 | Gradient Mesh, Typographic Bold, Duotone Split |
| 럭셔리 / 프리미엄 | Art Deco Luxe, Monochrome Minimal, Dark Academia |

| 구성 | 항목 |
|------|------|
| Skill | pptx-design-styles (30가지 스타일 가이드 + references/styles.md) |

---

## obsidian-skills

> Obsidian vault 파일(.md, .base, .canvas) 작성/편집을 위한 Agent Skills입니다. [^2]

### 사용 예시

Obsidian vault에서 작업할 때 자동 활성화됩니다. wikilinks, callouts, frontmatter, Bases, Canvas 관련 키워드에 반응합니다.

```
# Obsidian 마크다운 작성
@obsidian-skills 새 노트를 만들어줘. wikilinks와 callouts를 포함해서.

# Bases 파일 생성
@obsidian-skills 프로젝트 태스크 트래커 .base 파일을 만들어줘

# Canvas 생성
@obsidian-skills 리서치 마인드맵을 .canvas 파일로 만들어줘

# CLI로 vault 조작
@obsidian-skills Obsidian CLI로 오늘 일일 노트에 태스크를 추가해줘
```

### 5개 스킬

| 스킬 | 설명 |
|------|------|
| obsidian-markdown | Obsidian Flavored Markdown — wikilinks, embeds, callouts, properties |
| obsidian-bases | Obsidian Bases (.base) — 뷰, 필터, 수식, 요약 |
| json-canvas | JSON Canvas (.canvas) — 노드, 엣지, 그룹, 연결 |
| obsidian-cli | Obsidian CLI — vault 읽기/쓰기/검색, 플러그인 개발 |
| defuddle | Defuddle CLI — 웹 페이지에서 클린 마크다운 추출 |

| 구성 | 항목 |
|------|------|
| Skills | obsidian-markdown, obsidian-bases, json-canvas, obsidian-cli, defuddle (5개 스킬) |

---

## accelerated-learner

> 48시간 가속 학습 파이프라인 — 소스 자료를 분석하고 멘탈모델 추출, 논쟁 매핑, 판별 질문 설계, 소크라틱 튜터링을 통해 깊은 이해에 도달합니다.

### 사용법

```
# 기본 실행 (소크라틱 튜터링 포함)
/accelerated-learner:accelerated-learn 학습을 시작해줘
source_path: ./papers/
subject_name: 강화학습

# 지식베이스만 생성 (튜터링 건너뜀)
/accelerated-learner:accelerated-learn 학습 자료를 분석해줘
source_path: ./lecture_notes/
subject_name: 운영체제
auto_mode: true
```

### 사전 준비

분석할 소스 자료를 하나의 폴더에 모아 두세요:
- **지원 형식**: `.md`, `.txt`, `.pdf`
- **권장 분량**: 3~20개 파일 (논문, 강의노트, 교재 발췌 등)
- **영어 자료 사용 가능** — 분석 결과는 항상 한국어로 출력됩니다

### 워크플로우

```
소스 종합 (Phase 1)        모든 자료를 읽고 핵심을 통합
      ↓
멘탈모델 + 논쟁 (Phase 2)  전문가 사고체계 추출 + 학문적 논쟁 매핑  ← 병렬 실행
      ↓
판별 질문 (Phase 3)        깊은 이해를 검증하는 개방형 질문 설계
      ↓
소크라틱 튜터링 (Phase 4)   1:1 대화형 학습 세션  ← auto_mode=true 시 건너뜀
```

### 주요 특징

- **5단계 파이프라인**: 소스 종합 → 멘탈모델 추출 → 논쟁 매핑 → 판별 질문 → 소크라틱 튜터링
- **대화형 학습**: 질문을 하나씩 제시하고 답변에 맞춤 피드백 (탐색적/교정적/확장적 3유형)
- **조기 마스터리**: 5연속 우수 답변 시 자동 종료, 최대 15회 상호작용 제한
- **세션 로그**: 매 Q&A 교환 후 즉시 기록, `sessions/` 하위 디렉토리로 다중 세션 관리
- **가드레일**: 웹검색 보충 금지, 소스에 없는 정보 날조 금지, MCQ 금지 (개방형 질문만)

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|:----:|-------|------|
| `source_path` | O | - | 소스 자료 폴더 또는 파일 경로 (.md, .txt, .pdf) |
| `subject_name` | O | - | 학습 주제명 (출력 폴더명으로 사용) |
| `output_dir` | - | `./output/` | 출력 디렉토리 |
| `auto_mode` | - | `false` | `true` 시 소크라틱 튜터링을 건너뛰고 지식베이스(00~03)만 생성 |

### 출력물

| 파일 | 생성 단계 | 내용 |
|------|:--------:|------|
| `00-source-synthesis.md` | Phase 1 | 모든 소스 자료의 종합 분석문 |
| `01-mental-models.md` | Phase 2 | 전문가 사고체계 2~5개 (이름 + 정의 + 예측 테스트) |
| `02-controversies.md` | Phase 2 | 학문적 논쟁 지형 0~3개 (없으면 "없음" 명시) |
| `03-discriminating-questions.md` | Phase 3 | 블룸 상위 수준 개방형 질문 5~10개 + 답변 루브릭 |
| `sessions/session-N.md` | Phase 4 | 소크라틱 튜터링 대화 기록 (매 교환 즉시 기록) |
| `05-mastery-summary.md` | Phase 4 | 멘탈모델별 이해도 정성 평가 + 추가 학습 권장 |

<details>
<summary>구성 요소 (5 Agents · 1 Command · 1 Skill)</summary>

| 유형 | 항목 | 역할 |
|------|------|------|
| Agent | source-synthesizer | 소스 자료 읽기 + 종합 분석문 생성 |
| Agent | mental-model-extractor | 전문가 멘탈모델 2~5개 추출 |
| Agent | controversy-mapper | 학문적 논쟁 지형 매핑 |
| Agent | question-architect | 블룸 분류체계 기반 판별 질문 설계 |
| Agent | socratic-tutor | 대화형 소크라틱 튜터링 진행 |
| Command | `accelerated-learn` | 5개 에이전트 오케스트레이션 |
| Skill | learning-methodology | 48시간 가속 학습 방법론 지침 |

</details>

---

## wiki-gen

> 개인 데이터(일기, 노트, 메시지 등)를 Wikipedia 스타일 개인 지식 위키로 컴파일하는 스킬입니다. [^3]

### 사용 예시

개인 일기/노트를 지식 위키로 컴파일할 때 자동 활성화됩니다. 'personal wiki', 'compile journal', 'ingest notes' 등의 키워드에 반응합니다.

```
# 원시 데이터를 raw markdown 엔트리로 변환
@wiki-gen wiki ingest 를 실행해줌. ./data/ 에 있는 일기를 처리해줌.

# 엔트리를 위키 아티클로 컴파일
@wiki-gen wiki absorb all 을 실행해서 전체 엔트리를 흡수해줌.

# 위키에 질문
@wiki-gen wiki query "2026년에 작업한 프로젝트는?"

# 기존 아티클 감사 및 재구조
@wiki-gen wiki cleanup

# 누락된 아티클 발굴 및 생성
@wiki-gen wiki breakdown

# 위키 상태 확인
@wiki-gen wiki status
```

### 지원 데이터 포맷

| 포맷 | 설명 |
|------|------|
| Day One JSON | `entries` 배열 기반 일기 앱 |
| Apple Notes | HTML/TXT/MD 내보내기 |
| Obsidian Vault | `.md` 폴더, frontmatter 보존 |
| Notion Export | `.md` 또는 `.csv` 페이지 |
| Plain Text / Markdown | 폴더 내 `.txt` / `.md` |
| iMessage Export | `.csv` 또는 채팅 로그 |
| CSV / Spreadsheet | `.csv`, `.tsv` |
| Email Export | `.mbox`, `.eml` |
| Twitter/X Archive | `tweet.js` 또는 아카이브 |

### 10개 서브커맨드 (v1.2.0)

| 커맨드 | 역할 |
|--------|------|
| `wiki ingest` | 소스 데이터 → `raw/entries/`의 개별 `.md` 엔트리로 변환 (C7 표준 제외 목록, C6 날짜 추출 우선순위) |
| `wiki absorb [date-range]` | 엔트리를 읽고 이해하여 위키 아티클로 작성/갱신 (C4 Anti-Dump, 150-line cap, 5:1 compression) |
| `wiki remediate` | **v1.1.0 신규** — citation coverage gap을 병렬 에이전트로 보완하여 100%를 달성 (I3) |
| `wiki query <question>` | 위키 안을 탐색하여 질문에 답변 (read-only, N5: type: frontmatter 기반) |
| `wiki cleanup` | 병렬 서브에이전트로 전체 아티클 감사 및 재구조, I6 orphan 정책 적용 |
| `wiki breakdown` | 누락된 아티클을 발굴하고 병렬로 생성 |
| `wiki rebuild-index` | `_index.md`와 `_backlinks.json` 재구축 (C1 `[[filename_stem\|Title]]` 형식 강제) |
| `wiki reorganize` | 위키 구조 재설계 (병합/분할/카테고리 재편성) |
| `wiki sync` | sources.yaml 기반 다중 소스 동기화 및 ingest (멀티소스 수집 파이프라인) |
| `wiki status` | 결과물 통계 (N2 표준 출력 포맷: Ingestion/Articles/Coverage/Quality) |

### 주요 원칙 (v1.1.0 강화)

- **Writer, not filing clerk**: 단순히 사실을 정리하는 것이 아니라 의미를 이해하고 내러티브로 짜내기
- **Anti-Cramming**: 하나의 큰 아티클에 계속 추가하기보다 소주제로 새 아티클을 만들기
- **Anti-Thinning**: 스텁 생성 금지, 매번 아티클을 더 풍성하게 만들기
- **Anti-Dump (v1.1.0)**: 원본 엔트리 텍스트 verbatim paste 절대 금지, 150-line cap, 5:1 압축비 유지
- **Citation Discipline (v1.1.0)**: frontmatter `sources:` (canonical) + body `## References` (human-readable) 이중 인용
- **Wikipedia Tone, Not AI**: 평이하고 사실적인 문체. 감정은 직접 인용문으로만
- **Concept Articles**: 패턴, 테마, 아크가 개별 아티클로 승격. 이것이 "mind map"의 핵심

### 번들된 리소스 (v1.1.0 신규)

- **`assets/`**: 4개 에이전트 프롬프트 템플릿 (absorb, remediation, cleanup, breakdown) + README
- **`scripts/`**: 포터블 Python 헬퍼 스크립트 (rebuild_index, check_coverage, verify_content, consolidate_analyze, ingest_obsidian, diag_wikilink_resolution, diag_uncovered, finalize 등)
- **Migration Guide**: `## Migration from v1.0.0` 섹션으로 기존 사용자 호환성 보장

| 구성 | 항목 |
|------|------|
| Skill | wiki-gen v1.2.0 (10개 서브커맨드 + 39종 카테고리 택소노미 + Writing Standards + `assets/` templates + `scripts/` helpers) |
---

## link-curator

> URL 목록을 입력하면 한국어 요약 마크다운 노트를 생성하고, 선택적으로 HoneyCombo에 gh CLI로 제출합니다.

### 사용법

```bash
# MD 노트만 생성
/link-curator:curate-links 아래 URL들을 정리해줘
https://blog.example.com/ai-agents-guide
https://youtube.com/watch?v=abc123
output_dir: ./output/links/
```

```bash
# HoneyCombo 제출까지
/link-curator:curate-links 아래 링크들 정리하고 허니콤보에 올려줘
https://blog.example.com/mcp-tutorial
output_dir: ./output/links/
```

### 주요 특징

- **2단계 워크플로우**: URL fetch → Korean MD 생성 (Phase 1) + HoneyCombo 제출 (Phase 2, opt-in)
- **병렬 fetch**: 소스별 최적 전략 (webfetch, web search, fallback placeholder)
- **HoneyCombo 한국어 요약**: 제출 시 `## 개요`, `## 주요 내용`, `## 시사점` 3섹션 구조화 (≤5000자), MD 노트는 콘텐츠에 맞는 유연한 섹션 사용
- **Single/Bulk 제출**: 1-5개 단건, 6-20개 대량, 20개 초과 분할
- **Dry Run**: `--dry-run` 플래그로 실행 전 미리보기
- **Tags 영어, Summary 한국어**: HoneyCombo 자동 검증 규격 준수

| 파라미터 | 필수 | 설명 | 예시 |
|----------|:----:|------|------|
| URLs | O | HTTP(S) URL 목록 | 인라인 입력 |
| `output_dir` | O | MD 파일 저장 경로 | `./output/links/` |
| `submit` | - | HoneyCombo 제출 여부 | `submit: true` |
| `dry_run` | - | 제출 미리보기 | `dry_run: true` |

<details>
<summary>구성 요소 (1 Command · 2 Skills)</summary>

| 유형 | 항목 |
|------|------|
| Command | `curate-links` (오케스트레이터) |
| Skill | link-summarizer (URL fetch, MD 생성) |
| Skill | honeycombo-submit (gh CLI 제출 프로토콜, 2개 bash 스크립트) |

</details>

---

# 설치 & 설정

---

## 마켓플레이스 직접 등록

```bash
/plugin marketplace add /path/to/honeypot
```

## Submodule로 추가

이 저장소를 다른 프로젝트의 하위 디렉토리로 추가하여 사용할 수 있습니다.

```bash
# 추가
cd your-project
git submodule add https://github.com/orientpine/honeypot.git honeypot
git commit -m "Add honeypot as submodule"

# 클론 (처음부터 submodule과 함께)
git clone --recurse-submodules https://github.com/username/your-project.git

# 이미 클론 후 초기화
git submodule update --init --recursive

# 최신 버전으로 업데이트
git submodule update --remote --merge
git add honeypot && git commit -m "Update honeypot submodule" && git push
```

<details>
<summary>자주 사용하는 명령어</summary>

| 명령어 | 설명 |
|--------|------|
| `git submodule status` | 상태 확인 |
| `git submodule update --init --recursive` | 초기화 |
| `git submodule update --remote --merge` | 최신화 |
| `git diff --submodule` | 변경사항 확인 |

```bash
# 전역 설정 (권장) — 앞으로 git 작업 시 submodule 자동 업데이트
git config --global submodule.recurse true
```

</details>

---

<br>

# 개발 가이드

---

## 플러그인 표준 구조

```
plugins/{plugin-name}/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 메타데이터
├── agents/                  # 에이전트 .md 파일
├── commands/                # 커맨드(워크플로우) .md 파일
└── skills/                  # 스킬 폴더 (각 스킬은 하위 디렉토리)
    └── {skill-name}/
        ├── SKILL.md         # 스킬 정의 (필수)
        ├── references/      # 참조 문서
        ├── assets/          # 템플릿, 리소스
        └── scripts/         # 실행 스크립트
```

> `scripts/`, `references/`, `assets/`는 반드시 **스킬 폴더 내부**에 위치해야 합니다 (플러그인 루트 금지).

## 새 플러그인 추가 시

1. `plugins/{plugin-name}/` 디렉토리 생성
2. `.claude-plugin/plugin.json` 생성
3. `agents/`, `commands/`, `skills/` 하위에 `.md` 파일 작성
4. `.claude-plugin/marketplace.json`에 플러그인 등록
5. 캐시 클리어 후 재등록

## 주의사항

- marketplace.json은 **루트에 하나만** 유지
- 모든 `.md` 파일은 **LF 줄바꿈** 사용
- description에 특수문자 포함 시 **큰따옴표**로 감싸기
- Agent/Skill 파일 추가/삭제 시 **marketplace.json 동기화 필수**
- 플러그인 수정 시 **plugin.json + marketplace.json 버전 동시 업데이트**

상세 개발 가이드는 [AGENTS.md](./AGENTS.md) 참조

---

## 프로젝트 구조

<details>
<summary>전체 디렉토리 트리 (클릭하여 펼치기)</summary>

```
honeypot/
├── .claude-plugin/
│   └── marketplace.json              # 마켓플레이스 레지스트리 (18개 플러그인)
├── plugins/
│   ├── isd-generator/                # ISD 연구계획서 생성
│   │   ├── agents/                   # 6 agents
│   │   ├── commands/                 # isd-generate
│   │   └── skills/                   # 11 skills
│   ├── visual-generator/             # 시각자료 생성
│   │   ├── agents/                   # 5 agents
│   │   ├── commands/                 # visual-generate
│   │   └── skills/                   # 8 skills
│   ├── paper-style-generator/        # 논문 스타일 스킬 생성
│   │   ├── agents/                   # 3 agents
│   │   ├── commands/                 # paper-style-generate
│   │   └── skills/                   # 1 skill
│   ├── report-generator/             # 연구 보고서 생성
│   │   ├── agents/                   # 4 agents
│   │   ├── commands/                 # report-generate
│   │   └── skills/                   # 3 skills
│   ├── investments-portfolio/        # DC 연금 포트폴리오
│   │   ├── agents/                   # 3 agents
│   │   ├── commands/                 # portfolio-analyze
│   │   └── skills/                   # 11 skills
│   ├── stock-consultation/           # 주식/ETF 투자 상담
│   │   ├── agents/                   # 5 agents
│   │   ├── commands/                 # stock-consult
│   │   └── skills/                   # 3 skills
│   ├── hwpx-generator/              # HWPX 문서 생성/편집/분석
│   │   ├── agents/                   # 2 agents
│   │   ├── commands/                 # hwpx-generate
│   │   └── skills/                   # 2 skills
│   ├── macro-analysis/              # 거시경제 분석 공용 에이전트
│   │   └── agents/                   # 7 agents
│   ├── obsidian-skills/              # Obsidian vault 스킬
│   │   └── skills/                   # 5 skills
│   ├── general-agents/              # 범용 에이전트
│   │   └── agents/                   # 1 agent
│   ├── accelerated-learner/         # 48시간 가속 학습
│   │   ├── agents/                   # 5 agents
│   │   ├── commands/                 # accelerated-learn
│   │   └── skills/                   # 1 skill
│   ├── equity-research/             # 기관급 주식 분석
│   │   └── agents/                   # 1 agent
│   ├── worktree-workflow/           # Git worktree 워크플로우
│   │   └── agents/                   # 1 agent
│   ├── plugin-dev/                  # 플러그인 개발 종합 툴킷
│   │   ├── agents/                   # 3 agents
│   │   ├── commands/                 # create-plugin
│   │   └── skills/                   # 7 skills
│   ├── patent-trend-analyzer/       # 특허 동향 분석
│   │   ├── agents/                   # 3 agents
│   │   ├── commands/                 # analyze-patents
│   │   └── skills/                   # 5 skills
│   ├── pptx-design-styles/          # PPTX 디자인 스타일 가이드
│   │   └── skills/                   # 1 skill (30가지 모던 디자인 스타일)
│   ├── wiki-gen/                    # 개인 지식 위키 생성 v1.2.0
│   │   └── skills/                   # 1 skill (10개 서브커맨드 + assets/ templates + scripts/ helpers)
│   └── link-curator/                 # URL → Korean MD + HoneyCombo 제출
│       ├── commands/                 # curate-links
│       └── skills/                   # 2 skills (link-summarizer, honeycombo-submit)
├── AGENTS.md                         # 프로젝트 상세 지식 베이스
└── README.md                         # 이 문서
```

</details>

---

## 참고 링크

- [Agent Skills Specification](https://agentskills.io/specification)
- [Git Submodule 공식 문서](https://git-scm.com/book/ko/v2/Git-%EB%8F%84%EA%B5%AC-%EC%84%9C%EB%B8%8C%EB%AA%A8%EB%93%88)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|:----:|:----:|----------|
| 3.27.0 | 2026-04-10 | wiki-gen v1.2.0: wiki sync 서브커맨드 추가 — sources.yaml 기반 멀티소스 수집 파이프라인 (sync_sources.py, ingest_projects.py, ingest_common.py), pytest 인프라 + 27개 자동화 테스트 |
| 3.28.0 | 2026-04-20 | link-curator 플러그인 추가 — URL fetch → Korean MD summary notes 생성 (link-summarizer) + gh CLI HoneyCombo submission (honeycombo-submit), single/bulk 제출, `--dry-run` 지원 |
| 3.26.0 | 2026-04-10 | wiki-gen v1.1.0: 1826-entry 실사용 경험 기반 18개 항목 대규모 개선 — [P0] C1 `[[filename_stem\|Title]]` wikilink 구문 (Obsidian 파일명 resolution), C2 ASCII snake_case filename convention, C3 Citation Discipline (`sources:` canonical + `## References` human-readable dual traceability), C4 Anti-Dump Rule (150-line cap, 5:1 compression, max 3 consecutive raw lines); [P1] C5 Scale Mode (Partitioned Parallel for 500+ vaults with safer canonical entity rule), C6 Date Extraction 8-tier priority (datetime validation, mtime warning threshold), C7 Standard Exclusions (.git/.obsidian/node_modules/etc), I1 Aliases Discipline, I3 `wiki remediate` 신규 명령 (citation gap closure, 9번째 서브커맨드); [P2] I2 Agent Prompt Templates (`assets/`: absorb/remediation/cleanup/breakdown), I5 rebuild-index exclusions, I6 Orphan policy (max 8 wikilinks/article); [P3] N1 checkpoint cadence by scale, N2 `wiki status` 표준 출력 포맷, N3 Frontmatter schema (legacy 관대), N4 Citation vs Content coverage, N5 type 기반 query taxonomy; [I4] `scripts/` 포터블 Python 헬퍼 스크립트; + `## Migration from v1.0.0` 섹션 (backward compatibility lint warnings) |
| 3.25.0 | 2026-04-10 | investments-portfolio v1.2.0: 출력물 명명 일관성 수정 — 03-risk-analysis.md → 99-risk-analysis.md (보조 데이터 접두어 통일), material-organizer 데드 에이전트 제거 (3 agents), file-save-protocol 접두어 규칙 문서화 + 99-*.md 보조파일 등록, deposit_rates.json 웹검색 fallback 모순 해소; macro-analysis v1.0.1, stock-consultation v1.0.1 동기화 |
| 3.24.0 | 2026-04-09 | wiki-gen 플러그인 추가 (farzaa/wiki-gen-skill 포팅, 개인 일기/노트 → Wikipedia 스타일 지식 위키 자동 컴파일 — ingest/absorb/query/cleanup/breakdown/status/rebuild-index/reorganize 8개 서브커맨드, 39종 디렉토리 택소노미, Writing Standards) |
| 3.23.0 | 2026-03-30 | investments-portfolio v1.1.0: fund-portfolio 에이전트 감사 기반 4대 개선 — [MUST] 데이터 정합성 교차검증 Gate(riskLevel↔riskAsset 모순감지), 전수비교 증적(Audit Trail) 의무화, UH/H 환헤지 비용 비교 의무화; [SHOULD] 안전자산 다각화 옵션 검토; [FIX] 출력 파일명 99-fund-analysis.md → 01-fund-analysis.md 통일 (5개 파일) |
| 3.22.0 | 2026-03-30 | accelerated-learner 플러그인 추가 — 48시간 가속 학습(소스 분석→멘탈모델→논쟁 매핑→판별 질문→소크라틱 튜터링), 5 agents + 1 command + 1 skill |
| 3.21.0 | 2026-03-25 | visual-generator v3.4.0: JPEG 원본 직접 저장 — SDK 호환성 버그 수정(part.as_image() → inline_data.data 직접 사용), PNG 불필요 변환 제거로 파일 크기 47% 절감, RGBA 안전 변환 추가 |
| 3.20.0 | 2026-03-23 | hwpx-generator v3.11.0: section_transplant.py 추가 — HWPX 챕터 이식 CLI + HwpxSurgeon.transplant_from(), zip_surgery.py ZipInfo 메타데이터 전체 보존 P0 수정 |
| 3.19.0 | 2026-03-23 | hwpx-generator v3.10.0: MD 문서 구조(Indent) 보존 — md_parser.py indent_level 감지, xml_writer.py level→style 매평 + build_numbered(), analyze_template.py indent 스타일 추출, md_merger.py 다중 MD 병합 |
| 3.18.0 | 2026-03-22 | hwpx-generator v3.9.0: 캡션 emit — 이미지 placeholder 뒤 캡션 문단 자동 생성(xml_writer.py), validate.py 캡션 개수 검증 추가 |
| 3.16.1 | 2026-03-22 | hwpx-generator v3.6.1: md_parser.py 불릿/인용문 여러 줄 이어쓰기(continuation) 지원 — 줄바꿈으로 잘리던 한국어 텍스트("카메" → "카메라") 복원, xml_writer.py 이중 불릿 마커 방지 — bullet_auto 설정과 무관하게 항상 접두사 제거, proofread.py 이중 불릿 검사를 전체 문단으로 확대 |
| 3.16.0 | 2026-03-21 | hwpx-generator v3.6.0: 이중 삽입 지점 처리(Dual-Zone Content Placement) 지침 추가 — 요약 총괄표 셀에 전체 내용 삽입 방지, 본문 상세 섹션 플레이스홀더 방치 방지, 감지→요약 생성→본문 삽입 순서 강제, hwpx-generate 오케스트레이터 MUST DO/MUST NOT DO 보강 |
| 3.15.0 | 2026-03-20 | hwpx-generator v3.5.0: image_embedder.py hp:pic 구조 7대 결함 수정 — hp:pic을 `<hp:p><hp:run>` 래퍼로 감싸 section-level 배치 방지(🔴 렌더링 안됨 해결), orgSz=pixel×100(원본 크기)·curSz=표시 크기 분리, scaMatrix=curSz/orgSz 비율 자동 계산, imgDim=실제 픽셀 크기, imgClip=orgSz 전체 범위, hc:img 순서 imgDim 뒤로 이동, validate.py hp:run 내부 배치 검증 추가 |
| 3.14.0 | 2026-03-19 | hwpx-generator v3.4.0: image_embedder.py 전면 개편 — make_pic_xml() 검증 구조 교체(pypandoc-hwpx/HwpForge 기반), header.xml hh:binDataList 자동 등록, PIL 포맷 감지+자동변환, 이미지 높이 상한 검증, validate.py 이미지 6개 검사 추가(renderingInfo/instid/binDataList/magic bytes), section0.xml 개행 검사 0개 기준으로 교정 |
| 3.13.0 | 2026-03-19 | hwpx-generator v3.3.0: xml_writer.py 필수 사용 강제 + lxml 금지 — 에이전트 자체 표 XML 재구현 방지(hc: 네임스페이스/hp:tcPr 오류), lxml 개행 삽입으로 인한 한/글 파일 깨짐 방지, generate_content.py 등 자체 스크립트 생성 금지 규칙 추가 |
| 3.12.1 | 2026-03-19 | visual-generator v3.3.1: Gemini API JPEG→PNG 명시적 변환 — `image.save(format='PNG')` 강제, CMYK/P 모드 호환 변환, `evaluate_image_quality()` MIME 타입 동적 감지 |
| 3.12.0 | 2026-03-19 | hwpx-generator v3.2.0: page_guard.py 워크플로우 모드 분기 — 오케스트레이터가 워크플로우 유형(MD 채우기/스타일 복제/XML-first)에 따라 `--mode template-fill` 자동 선택, template-fill 모드에서 표 추가/변경 구분 로직 추가, WARNING 수준 리포트 도입 |
| 3.11.0 | 2026-03-18 | hwpx-generator v3.1.0: Template-Aware Markdown Insertion — 템플릿 sub-header와 MD heading 매칭으로 헤더 이중 출현 방지, placeholder 문단 자동 정리, 적용 조건 분기 추가 |
| 3.10.0 | 2026-03-18 | patent-trend-analyzer v1.3.0: 표준 분석 스크립트(`analyze_patents.py`) 추가 — JSON config 기반 분류, 고정 출력 구조(11개 필수 파일), multi-topic 병합 규칙, 출력물 검증 체크리스트로 대시보드 일관성 보장 |
| 3.9.0 | 2026-03-18 | obsidian-skills 플러그인 추가 (kepano/obsidian-skills 포팅, Obsidian Markdown/Bases/Canvas/CLI/Defuddle 5개 스킬) |
| 3.8.0 | 2026-03-18 | pptx-design-styles 플러그인 추가 (corazzon/pptx-design-styles 포팅, 30가지 모던 PPTX 디자인 스타일 가이드 — HEX 색상, 폰트 조합, 레이아웃 규칙, 시그니처 요소) |
| 3.7.0 | 2026-03-18 | hwpx-generator v3.0.0: 마크다운→HWPX 채우기(Workflow 7), 이미지 임베딩(image_embedder.py), md_parser.py, xml_writer.py 추가 |
| 3.6.2 | 2026-03-17 | 6개 테마 예시 프롬프트를 v3.3.0 Golden Reference로 업데이트 (여백 최소화, 네거티브 스페이스 타겟, 캔버스 채우기 지시 반영) + Gemini API로 전체 이미지 재생성 |
| 3.6.1 | 2026-03-17 | AGENTS.md 구조 개선: 코드베이스에서 추론 가능한 섹션 삭제 (STRUCTURE 트리, 파일 템플릿, 플러그인 추가 가이드 등 405줄 제거), 버전 체계를 breaking-aware SemVer로 재정의 (MAJOR=삭제/breaking, MINOR=추가/기능변경, PATCH=버그수정/문서), Registration Checklist를 MARKETPLACE RULES로 이동 |
| 3.6.0 | 2026-03-17 | visual-generator v3.3.0: 여백 최소화 — Scene Description 캔버스 채우기 지시 추가, Rendering Style 공간구성 강화, 테마별 조건부 네거티브 스페이스 타겟 (gov/seminar ≤15%, concept/whatif ≤20%, comparison ≤10%, pitch 30%+ 유지) |
| 3.5.0 | 2026-03-17 | visual-generator v3.2.0: Must-Render Registry 추가 (4개 테마 필수 렌더링 요소 명시화), marketplace metadata 버전 동기화 (2.4.0→3.5.0) |
| 3.4.0 | 2026-03-16 | patent-trend-analyzer v1.2.0: MCP 설정 스킬 개선 — API 키 발급 안내, venv 기반 설치, Claude Code/OpenCode 이중 설정(형식 차이 대응), 트러블슈팅 보강 |
| 3.3.0 | 2026-03-16 | patent-trend-analyzer 플러그인 추가 (KIPRIS API 기반 특허 동향 분석, IPC 분류 가이드, 3 agents + 1 command + 5 skills) |
| 3.2.0 | 2026-03-13 | hwpx-generator v2.4.0: ZIP-level surgery 도구 추가 (zip_surgery.py, HwpxSurgeon), validate.py --strict 모드, cell_writer 금지 규칙, 표 행 높이 자동 조절, 단계적 디버깅 전략 |
| 3.1.0 | 2026-03-10 | 6개 테마 예시 프롬프트를 v3.0.0 Golden Reference로 업데이트 + Gemini API로 전체 이미지 재생성. 임시/계획 파일 정리. |
| 3.0.0 | 2026-03-09 | visual-generator v3.0.0: 4-block 마크다운 프롬프트 형식 복원 (INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) + v2.x 품질 보호 통합 (Style Sheet, Golden Reference, prompt-validator 7차원, 팔레트 세션 고정) |

<details>
<summary>이전 버전 이력</summary>

| 버전 | 날짜 | 변경 내용 |
|:----:|:----:|----------|
| 2.5.0 | 2026-03-09 | visual-generator v2.2.0: 폰트명 유출 차단, 최소 텍스트 밀도(body≥8) 강제, Style Sheet 기반 슬라이드 일관성, prompt-validator 강화(밀도/폰트/팔레트 검증 추가) |
| 2.4.1 | 2026-03-08 | visual-generator v2.1.1: Golden Reference `<text_to_render>` key:value 형식 통일(4개 테마), 파이프라인 다이어그램 prompt-validator 반영, layout-types Progressive Disclosure 분리(938→82줄 + references/layout-catalog.md), scene-richness-spec 테마명 교정, README agent 수 5개 반영 |
| 2.4.0 | 2026-03-07 | visual-generator v2.0.0: XML-tag 프롬프트 시스템 전면 개편 — 4-block 마크다운(INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) → 5-tag XML(`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`) 전환. render_text/scene_context 분류 체계, 한국어 타이포그래피 가이드 추가 |
| 2.3.5 | 2026-03-06 | visual-generator v1.11.0: Data Elements 메타라벨 방지 원칙, Content Placement 조사 문장 형식 강제, 세미나 테마 원 번호 마커 금지, renderer 검증 #12·#13 추가 |
| 2.3.4 | 2026-03-06 | visual-generator v1.10.1: renderer-agent에 번호 참조 체계·고아 항목·세미나 라벨 탈맥락화 검증 3종 추가 |
| 2.3.3 | 2026-03-06 | visual-generator v1.10.0: CONTENT↔Content Placement 전수 대응 원칙 추가 (고아 항목·Data 중복·개념 키워드 혼입 방지) |
| 2.3.2 | 2026-03-06 | visual-generator v1.9.0: 이중 렌더링 방지(번호 참조 체계), 세미나 테마 장면화 방지(테마 라벨 탈맥락화), 축 기반 레이아웃 공간-의미 역검증 추가 |
| 2.3.1 | 2026-03-05 | hwpx-generator v2.3.0: linesegarray 자동 생성으로 전환 (cell_writer.py 신규, build_hwpx/pack 통합, 뷰어 호환성 보장) |
| 2.3.0 | 2026-03-04 | plugin-dev 플러그인 추가 (Anthropic claude-code 공식 저장소에서 포팅) |
| 2.2.0 | 2026-02-27 | visual-generator 6개 테마 예시 이미지 추가 (Gemini API 생성), README 시각적 개선 |
| 2.1.0 | 2026-02-27 | README 전면 최신화: 표준 구조 반영, 11개 플러그인 문서화, visual-generator 6테마 체계 반영 |
| 2.0.0 | 2026-01-11 | README 완전 재작성, 6개 플러그인 문서화 |
| 1.0.0 | 2026-01-08 | 최초 작성 |

</details>

[^1]: [anthropics/claude-code `plugins/plugin-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev)의 내용을 참조하여 포팅하였습니다. 원본 저자: Daisy Hollman (daisy@anthropic.com), 라이선스: MIT.
[^2]: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)의 내용을 포팅하였습니다. 원본 저자: Steph Ango (stephango.com), 라이선스: MIT.
[^3]: [farzaa/wiki-gen-skill](https://gist.github.com/farzaa/c35ac0cfbeb957788650e36aabea836d)의 내용을 포팅하였습니다. 원본 저자: farzaa, 라이선스: MIT.
