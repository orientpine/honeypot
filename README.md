# Honeypot

> Claude Code 플러그인 마켓플레이스 - ISD 연구계획서, 시각자료, 논문 스타일, 연금 포트폴리오 분석

**Version**: 2.0.0  
**Author**: [Baekdong Cha](https://github.com/orientpine)  
**License**: MIT

---

## 주요 기능

| 플러그인 | 설명 | 유형 |
|----------|------|:----:|
| **isd-generator** | ISD 연구계획서 전체 생성 (5개 Chapter + 이미지) | Agent |
| **visual-generator** | TED/정부 스타일 시각자료 프롬프트 생성 + Gemini 렌더링 | Skill |
| **paper-style-generator** | PDF 논문 분석 → 논문 작성 스킬 세트 자동 생성 | Agent |
| **report-generator** | 연구 노트 → 국가기관 제출용 연구 보고서 자동 생성 | Agent |
| **investments-portfolio** | DC 연금 포트폴리오 분석 멀티 에이전트 시스템 | Agent |
| **macro-analysis** | 거시경제 분석 공용 에이전트 (지수/금리/섹터/리스크/리더십) | Agent |
| **general-agents** | 범용 에이전트 (인터뷰 등) | Agent |
| **stock-consultation** | 주식/ETF 투자 상담 Multi-Agent 시스템. 거시경제 분석 → 종목 스크리닝 → 밸류에이션 → 반대 논거 → 최종 검증 워크플로우. Bogle/Vanguard 철학 기반. | Agent |
| **equity-research** | Professional equity research analysis with institutional-grade formatting. 티커와 함께 호출하면 기관급 주식 분석 리포트를 생성합니다. | Agent |
| **hwpx-converter** | Markdown 파일을 한글 문서(HWPX)로 변환합니다. pypandoc-hwpx 기반. 단일 파일 및 폴더 배치 변환 지원. | Skill |
| **worktree-workflow** | Git worktree를 활용한 Claude Code 병렬 실행 워크플로우 | Agent |

---

## 빠른 시작

### 1. 마켓플레이스 등록

```bash
# Claude Code에서 실행
/plugin marketplace add C:\path\to\honeypot
```

### 2. 플러그인 사용

```bash
# 예: ISD 연구계획서 생성
@isd-generator 오케스트레이터를 사용해서 연구계획서를 생성해줘

# 예: DC 연금 포트폴리오 분석
@investments-portfolio 포트폴리오 분석을 시작해줘
```

---

## 프로젝트 구조

```
honeypot/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 레지스트리 (10개 플러그인)
├── plugins/
│   ├── isd-generator/            # ISD 연구계획서 생성
│   │   ├── agents/               # 7 agents (orchestrator, chapter1-5, figure)
│   │   ├── references/           # 템플릿, 예시, 가이드
│   │   ├── assets/               # 출력 템플릿
│   │   └── scripts/              # Gemini 이미지 생성 스크립트
│   ├── visual-generator/         # 시각자료 생성
│   │   ├── skills/               # 4 skills (prompt-concept, prompt-gov, prompt-seminar, renderer)
│   │   └── scripts/              # 이미지 생성 스크립트
│   ├── paper-style-generator/    # 논문 스타일 스킬 생성
│   │   ├── agents/               # 4 agents (orchestrator, pdf-converter, style-analyzer, skill-generator)
│   │   ├── scripts/              # MinerU 변환, 스타일 추출
│   │   └── templates/            # Jinja2 스킬 템플릿 (10개)
│   ├── report-generator/         # 연구 보고서 생성
│   │   ├── agents/               # 5 agents (orchestrator, input-analyzer, content-mapper, chapter-writer, quality-checker)
│   │   ├── references/           # 문서 템플릿, 키워드
│   │   └── assets/               # 출력 템플릿
│   ├── macro-analysis/            # 거시경제 분석 공용 에이전트
│   │   └── agents/                # 7 agents (index, rate, sector, risk, leadership, synthesizer, critic)
│   ├── investments-portfolio/    # DC 연금 포트폴리오
│   │   └── agents/               # 5 agents (orchestrator, fund, compliance, output, material)
│   ├── general-agents/           # 범용 에이전트
│   │   └── agents/               # interview.md
│   ├── stock-consultation/       # 주식/ETF 투자 상담
│   │   ├── agents/               # 6 agents
│   │   └── skills/               # 3 skills
│   ├── equity-research/          # 기관급 주식 분석
│   │   └── agents/               # 1 agent
│   ├── hwpx-converter/           # Markdown→HWPX 변환
│   │   └── skills/               # 2 skills
│   └── worktree-workflow/        # Git worktree 워크플로우
│       └── agents/               # 1 agent
├── resource/                     # 개발 참고 자료
├── AGENTS.md                     # 프로젝트 상세 문서
└── README.md                     # 이 문서
```

---

## 플러그인 상세

### isd-generator

**ISD (기업부설연구소) 연구계획서 자동 생성**

- **워크플로우**: Chapter 3 → 1 → 2 → 4 → 5 순서로 생성
- **출력**: `output/[프로젝트명]/chapter_{1-5}/`
- **이미지 생성**: Gemini API로 캡션 기반 이미지 자동 생성

| Agent | 역할 |
|-------|------|
| orchestrator | 전체 워크플로우 조율 |
| chapter1-5 | 각 챕터별 콘텐츠 생성 |
| figure | 캡션 추출 + 이미지 프롬프트 생성 |

### visual-generator

**시각자료 프롬프트 생성 및 렌더링**

| Skill | 스타일 | 용도 |
|-------|--------|------|
| prompt-concept | TED 스타일 | 미니멀 인포그래픽 |
| prompt-gov | 정부/공공기관 | PPT 슬라이드 |
| prompt-seminar | 세미나 스타일 | 세미나/발표 자료 |
| renderer | - | Gemini API 이미지 생성 |

### paper-style-generator

**PDF 논문 → 논문 작성 스킬 세트 생성 (메타-플러그인)**

1. MinerU로 PDF → Markdown 변환
2. 스타일 패턴 추출 (Voice, Tense, 전환어 등)
3. 10개 독립 스킬 세트 생성:
   - `{name}-common`, `{name}-abstract`, `{name}-introduction`
   - `{name}-methodology`, `{name}-results`, `{name}-discussion`
   - `{name}-caption`, `{name}-title`, `{name}-verify`
   - `{name}-orchestrator` (전체 논문 자동 생성)

### report-generator

**연구 노트 → 국가기관 제출용 연구 보고서 생성**

- **입력**: 폴더, 파일, 코드베이스
- **출력**: 최대 9개 챕터 전문 보고서
- **문장 패턴**: 4단계 패턴 적용 (What → Why → How → Impact)

### investments-portfolio

**DC형 퇴직연금 포트폴리오 분석 멀티 에이전트 시스템**

| Agent Group | Agents | 역할 |
|-------------|--------|------|
| Coordinator | portfolio-orchestrator | 전체 워크플로우 조율 |
| Macro Analysis (macro-analysis) | index-fetcher, rate-analyst, sector-analyst, risk-analyst, leadership-analyst | 거시경제 분석 |
| Synthesizers (macro-analysis) | macro-synthesizer, macro-critic | 분석 종합 및 검증 |
| Portfolio | fund-portfolio, compliance-checker | 펀드 추천 및 규제 검증 |
| Verification | output-critic | 출력 검증 |

---

## Submodule 사용법

이 저장소를 다른 프로젝트의 하위 디렉토리로 추가하여 사용할 수 있습니다.

### Submodule 추가

```bash
cd your-project
git submodule add https://github.com/orientpine/honeypot.git honeypot
git commit -m "Add honeypot as submodule"
```

### Submodule 클론

```bash
# 방법 A: 처음부터 submodule과 함께
git clone --recurse-submodules https://github.com/username/your-project.git

# 방법 B: 이미 클론 후 초기화
git submodule update --init --recursive
```

### Submodule 업데이트

```bash
# 최신 버전으로 업데이트
git submodule update --remote --merge

# 메인 프로젝트에 반영 (필수!)
git add honeypot
git commit -m "Update honeypot submodule"
git push
```

### 자주 사용하는 명령어

| 명령어 | 설명 |
|--------|------|
| `git submodule status` | 상태 확인 |
| `git submodule update --init --recursive` | 초기화 |
| `git submodule update --remote --merge` | 최신화 |
| `git diff --submodule` | 변경사항 확인 |

### 전역 설정 (권장)

```bash
# 앞으로 git 작업 시 submodule 자동 업데이트
git config --global submodule.recurse true
```

---

## 개발 가이드

### 새 플러그인 추가 시

1. `plugins/{plugin-name}/` 디렉토리 생성
2. `agents/` 또는 `skills/` 하위에 `.md` 파일 작성
3. `.claude-plugin/marketplace.json`에 플러그인 등록
4. 캐시 클리어 후 재등록:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue
# Claude Code: /plugin marketplace remove honeypot
# Claude Code: /plugin marketplace add C:\path\to\honeypot
```

### 주의사항

- marketplace.json은 **루트에 하나만** 유지
- 모든 `.md` 파일은 **LF 줄바꿈** 사용
- description에 특수문자 포함 시 **큰따옴표**로 감싸기
- Agent/Skill 파일 추가/삭제 시 **marketplace.json 동기화 필수**

상세 개발 가이드는 [AGENTS.md](./AGENTS.md) 참조

---

## 참고 링크

- [Git Submodule 공식 문서](https://git-scm.com/book/ko/v2/Git-%EB%8F%84%EA%B5%AC-%EC%84%9C%EB%B8%8C%EB%AA%A8%EB%93%88)
- [Claude Code 플러그인 문서](https://docs.anthropic.com/claude-code/plugins)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|:----:|:----:|----------|
| 2.0.0 | 2026-01-11 | README 완전 재작성, 6개 플러그인 문서화 |
| 1.0.0 | 2026-01-08 | 최초 작성 |
