# TOOLBOX PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-19T00:00:00+09:00
**Version:** 3.12.0
**Branch:** main

## OVERVIEW

AI agent skill/plugin toolbox for Korean government R&D proposal (ISD) auto-generation, presentation figure creation, academic paper writing style extraction, and **meta-plugin for auto-generating paper writing skill sets**. Claude plugin ecosystem with orchestrated multi-agent workflows.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Generate full ISD proposal | `plugins/isd-generator/commands/isd-generate.md` | Uses `skills/input-template/` |
| Generate single ISD chapter | `plugins/isd-generator/agents/chapter{N}.md` | Chapter 3 first, then 1→2→4→5 |
| Generate figures from `<caption>` | `plugins/isd-generator/agents/figure.md` | Gemini API required |
| Generate visual materials | `plugins/visual-generator/commands/visual-generate.md` | Multi-agent pipeline. 4-block 마크다운(INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) 기반 |
| Visual generator scene richness spec | `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` | Scene complexity validation rules |
| Visual generator validation rules | `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` | Prompt validation checklist |
| Visual generator Korean typography | `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` | Korean text rendering guidelines |
| **Generate paper writing skills from PDFs** | `plugins/paper-style-generator/commands/paper-style-generate.md` | MinerU + Jinja2 templates |
| Portfolio analysis | `plugins/investments-portfolio/commands/portfolio-analyze.md` | Korean DC pension multi-agent |
| Generate research report | `plugins/report-generator/commands/report-generate.md` | 연구노트 → 보고서 자동 생성 |
| Stock/ETF consultation | `plugins/stock-consultation/commands/stock-consult.md` | Bogle/Vanguard 철학 기반 |
| General interview agent | `plugins/general-agents/agents/interview.md` | Deep interview + execution |
| Equity research analysis | `plugins/equity-research/agents/equity-research-analyst.md` | 기관급 주식 분석 |
| HWPX 문서 생성 | `plugins/hwpx-generator/commands/hwpx-generate.md` | XML-first + ZIP치환 |
| HWPX XML-first 빌드 | `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` | build_hwpx.py + cell_writer.py 기반, 레퍼런스 복원 우선 |
| HWPX ZIP-level surgery | `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` | 안전한 ZIP-level 편집 (stdlib only, lxml 불필요), HwpxSurgeon 클래스 |
| HWPX surgery 가이드 | `plugins/hwpx-generator/skills/hwpx-core/references/zip-surgery-guide.md` | 10가지 안전 규칙 명세 |
| HWPX linesegarray 생성 | `plugins/hwpx-generator/skills/hwpx-core/scripts/cell_writer.py` | build_hwpx/pack 파이프라인 통합, 실패 시 strip 폴백 |
| HWPX 페이지 가드 | `plugins/hwpx-generator/skills/hwpx-core/scripts/page_guard.py` | 레퍼런스 대비 페이지 드리프트 위험 검사 |
| HWPX 템플릿 치환 | `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md` | fix_namespaces.py 필수, ZIP surgery 후 cell_writer 금지 |
| HWPX 마크다운 파싱 | `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` | Markdown → JSON blocks (Workflow 7) |
| HWPX XML 작성 | `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` | JSON + style config → HWPX XML fragment |
| HWPX 이미지 임베딩 | `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` | PNG embedding into HWPX (Workflow 7) |
| Plugin development toolkit | `plugins/plugin-dev/commands/create-plugin.md` | Hook, MCP, 구조, 설정, 커맨드/에이전트/스킬 개발 |
| Patent trend analysis | `plugins/patent-trend-analyzer/commands/analyze-patents.md` | KIPRIS API 기반 계획→검색→분석 파이프라인 |
| PPTX design styles (30 styles) | `plugins/pptx-design-styles/skills/pptx-design-styles/SKILL.md` | Glassmorphism, Neo-Brutalism 등 30가지 디자인 스타일 가이드 |
| Obsidian Markdown 작성 | `plugins/obsidian-skills/skills/obsidian-markdown/SKILL.md` | Wikilinks, embeds, callouts, properties |
| Obsidian Bases 작성 | `plugins/obsidian-skills/skills/obsidian-bases/SKILL.md` | .base 파일 뷰/필터/수식 |
| JSON Canvas 작성 | `plugins/obsidian-skills/skills/json-canvas/SKILL.md` | .canvas 노드/엣지/그룹 |
| Obsidian CLI | `plugins/obsidian-skills/skills/obsidian-cli/SKILL.md` | vault 조작, 플러그인 개발 |
| 웹 페이지 클린 추출 | `plugins/obsidian-skills/skills/defuddle/SKILL.md` | Defuddle CLI 마크다운 추출 |
| Plugin registry | `.claude-plugin/marketplace.json` | All 14 plugins listed |

**Note**: Original `examples/` folder with real company names archived in local branch `archive/examples-backup` (not pushed to public repository).

## SKILLS VS AGENTS: 개념적 구분 (개발 지침)

플러그인 개발 요청 시 아래 구분을 고려하여 적합한 유형을 선택해야 합니다.

| 구분 | Skills (스킬) | Agents (에이전트) |
|------|---------------|-------------------|
| **목적** | 특정 전문 지식/절차 제공 | 자율적인 문제 해결 주체 |
| **작동 방식** | 메인 에이전트의 컨텍스트 내에서 필요할 때 자동으로 로드되는 지침 및 리소스 | 자체적인 실행 흐름을 가지고 독립적으로 작동하는 작업자 |
| **구성 요소** | 지침(Markdown), 스크립트, 리소스 파일 등으로 구성된 폴더 | LLM(Claude 모델), 도구(Tools), 실행 환경(샌드박스), 상황 관리(Context management)로 구성 |
| **컨텍스트** | 메인 컨텍스트(대화창)의 일부로 간주됨 (토큰 소비에 영향) | 별도의 격리된 컨텍스트에서 실행되어 메인 컨텍스트를 보존함 |
| **사용 예시** | "PR 리뷰는 우리 회사의 코딩 표준을 따르세요"와 같은 특정 가이드라인 적용 | "코드베이스를 분석하고 이 버그를 수정하세요"와 같은 복잡한 작업 위임 |

### 선택 기준

**Skill을 선택해야 하는 경우:**
- 정해진 절차나 템플릿에 따라 문서/코드를 생성해야 할 때
- 특정 스타일 가이드나 규칙을 적용해야 할 때
- 사용자와의 대화 맥락을 유지하며 작업해야 할 때
- 단일 작업 워크플로우가 필요할 때

**Agent를 선택해야 하는 경우:**
- 복잡한 분석이나 다단계 추론이 필요할 때
- 메인 컨텍스트의 토큰을 보존해야 할 때
- 여러 전문 에이전트 간 협업이 필요할 때 (Multi-Agent)
- 자율적인 탐색과 문제 해결이 필요할 때

---

## CONVENTIONS

### Skill File Structure
- Each skill plugin: `plugins/{plugin}/skills/SKILL.md` (main), `references/`, `assets/output_template/`
- SKILL.md frontmatter: `name`, `description`, `tools`, `model` (optional)
- Verification docs: `chapter{N}_research_verification.md` - NEVER skip

### Agent File Structure
- Each agent plugin: `plugins/{plugin}/agents/{agent-name}.md`
- Agent frontmatter: `name`, `description`, `tools`, `model`

### Document Language
- All ISD content: Korean (한글)
- All presentations: Korean with English technical terms
- Agent definitions: Korean

### Critical Workflow Rules
- ISD chapter order: **3 → 1 → 2 → 4 → 5** (Chapter 3 first)
- Verification docs: Generate BEFORE main content (절대 스킵 금지)
- Task delegation: Use `Task(subagent_type=...)` - never analyze directly
- Auto mode: `auto_mode=true` skips user confirmations
- `/start-work` 완료 후: 모든 작업이 끝나면 반드시 `git push`를 실행하여 원격 저장소에 반영

### Windows Bash 명령어 실행 규칙 (CRITICAL)

> **배경**: 이 프로젝트의 개발 환경은 Windows (cmd.exe / PowerShell)입니다. Bash 도구(터미널)로 명령을 실행할 때 Unix 전용 `export` 구문을 사용하면 **모든 명령이 실패**합니다. 모델이 git 명령에 환경변수 프리픽스를 자동 생성하는 패턴이 고착되어 있으므로, 아래 규칙을 **반드시** 준수해야 합니다.

**셸 환경**: `C:\WINDOWS\system32\cmd.exe` (PowerShell에서 opencode 실행 시에도 Bash 도구는 cmd.exe 사용)

#### 절대 금지

```
# NEVER — Unix 전용 구문, Windows에서 즉시 실패
export CI=true GIT_TERMINAL_PROMPT=0; git status
export VAR=value; any-command
```

#### 올바른 사용법

```
# CORRECT — 명령어만 직접 실행 (환경변수 프리픽스 없이)
git status
git add -A
git commit -m "message"
git push
git log --oneline -5
```

#### 환경변수가 필요한 경우 (Windows 구문)

```
# cmd.exe에서 환경변수 설정 시
set GIT_TERMINAL_PROMPT=0 & git status

# PowerShell에서 환경변수 설정 시
$env:GIT_TERMINAL_PROMPT=0; git status
```

#### 플랫폼 차이 요약

| 항목 | Unix/macOS (bash) | Windows (cmd.exe) |
|------|-------------------|-------------------|
| 환경변수 설정 | `export VAR=value` | `set VAR=value` |
| 명령 구분자 | `;` | `&` 또는 `&&` |
| 환경변수 참조 | `$VAR` | `%VAR%` |
| 올바른 git 실행 | `export GIT_TERMINAL_PROMPT=0; git status` | `git status` (프리픽스 불필요) |

**핵심 원칙**: Windows에서는 `git`, `python`, `npm` 등 명령어를 **프리픽스 없이 직접 실행**하세요. `export`는 절대 사용하지 마세요.

## SCRIPT PATH RESOLUTION (MANDATORY)

> **배경**: 에이전트가 스킬 내 스크립트 경로를 찾지 못하면 자체 Python 코드를 작성하는 문제가 반복 발생함. 자체 작성 코드는 구버전 패키지 사용, 핵심 설정 누락 등 치명적 결함을 유발함.

### 규칙: Agent Skills Spec 상대경로 우선, Glob 폴백

[Agent Skills Specification — File References](https://agentskills.io/specification#file-references)에 따라, 스킬 내 파일 참조는 **스킬 루트 기준 상대경로**를 최우선으로 사용합니다:

```markdown
Run the extraction script:
scripts/extract.py
```

스킬(`SKILL.md`)에 `scripts/` 폴더가 포함된 경우, **반드시** 아래 우선순위로 경로 해석 지침을 명시해야 합니다:

```markdown
### 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/{script-name}.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
스킬이 로드된 컨텍스트에서 상대경로 `scripts/{script-name}.py`를 직접 참조하여 실행합니다.

**Step 2. 상대경로 실패 시 Glob 폴백**
Glob: **/{plugin-name}/skills/{skill-name}/scripts/{script-name}.py

**Step 3. Glob도 실패 시 확장 탐색**
Glob: **/{script-name}.py

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.
```

### 에이전트에서 스크립트 참조 시

에이전트(`.md`)가 스킬의 스크립트를 실행하는 경우, Workflow에 상대경로 우선 + Glob 폴백 절차를 명시해야 합니다:

```
+-- Step N. 스크립트 찾기 및 실행
    +-- 상대경로 참조: scripts/{script}.py (스킬 루트 기준)
    +-- 실패 시 Glob 폴백: **/{plugin}/skills/{skill}/scripts/{script}.py
    +-- Glob도 실패 시: Glob: **/{script}.py
    +-- 찾은 경로로 실행
    +-- 스크립트를 찾지 못하면: 즉시 중단, 사용자에게 경로 확인 요청
    +-- 절대 금지: 스크립트를 못 찾았을 때 자체 Python 코드를 작성하여 대체하지 않음
```

### 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| `python plugins/xxx/scripts/yyy.py` (하드코딩) | 서브모듈/경로 변경 시 실패 | 상대경로 → Glob 폴백 |
| `{이_스킬의_scripts_경로}` (플레이스홀더) | 에이전트가 해석 못 함 | 구체적 상대경로 명시 |
| 스크립트 못 찾으면 자체 코드 작성 | 구버전 패키지, 설정 누락 | 즉시 중단 + 사용자 안내 |

### 참조 구현

`plugins/visual-generator/skills/slide-renderer/SKILL.md`를 모범 사례로 참조하세요.

---

## ANTI-PATTERNS (THIS PROJECT)

| Forbidden | Reason |
|-----------|--------|
| Skipping verification documents | Entire chapter becomes invalid |
| Direct fund_data.json analysis | Must delegate to `fund-portfolio` agent |
| Direct regulatory calculation | Must delegate to `compliance-checker` |
| Placeholder text `[내용]` in prompts | Gemini will render literally |
| Rendering hints in ASCII `(24pt)` | Will appear in generated image |
| Generating Chapter 1 before Chapter 3 | Dependency: Ch1 derives from Ch3 |

## UNIQUE STYLES

### Figure Prompt Requirements (500+ lines)
- 14 mandatory sections (1-14)
- ASCII layout for 6 regions
- 50+ text items, 8+ data tables
- 4-color palette: #1E3A5F, #4A90A4, #2E7D5A, #F5F7FA

### Multi-Agent Portfolio System
- Workflow: `macro-analysis` → `fund-portfolio` → `compliance-checker` → `output-critic`
- Output files: `00-macro-outlook.md` through `04-portfolio-summary.md`
- Folder: `portfolios/YYYY-MM-DD-{profile}-{session}/`

### Paper Style Generator (Meta-Plugin)
- **Purpose**: Analyze PDF papers (10+) and auto-generate paper writing skill sets
- **Workflow**: `paper-style-generate` (command) → `pdf-converter` → `style-analyzer` → `skill-generator`
- **Input**: PDF papers from same author/research group or same field
- **Output**: Hybrid plugin in `{CWD}/my-marketplace/plugins/{name}-paper-skills/`
  - Command (1): `{name}-paper-generate.md` (오케스트레이터)
  - Agents (8): `{name}-title-writer`, `{name}-abstract-writer`, `{name}-introduction-writer`, `{name}-methodology-writer`, `{name}-results-writer`, `{name}-discussion-writer`, `{name}-caption-writer`, `{name}-verify`
  - Skill (1): `{name}-style-guide`
  - Plugin metadata: `.claude-plugin/plugin.json`
- **Orchestrator Features**:
  - Sequential section generation: Title → Abstract → Introduction → Methodology → Results → Discussion → Captions
  - Final verification via `{name}-verify`
  - Cross-section consistency tracking (sample sizes, metrics, biomarkers)
  - Execution modes: Full Auto, Propagation Management
  - Output: `output/{paper_topic}/manuscript_complete.md`
- **Style Analysis Extracts**:
  - Voice ratio (active/passive) per section
  - Tense patterns (past/present)
  - "We" usage ratio in Results (target: ≤30%)
  - High-frequency academic verbs
  - Transition phrases by section
  - Measurement formatting patterns
  - Citation style detection
  - Field characteristics from keywords

## COMMANDS

```bash
# Generate images from prompts (requires google-genai, Pillow)
python plugins/isd-generator/skills/core-resources/scripts/generate_images.py \
  --prompts-dir [path]/prompts/ \
  --output-dir [path]/figures/

# Generate slide images
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py \
  --prompts-dir [path] --output-dir [path]

# Paper Style Generator: Convert PDFs to Markdown (requires MinerU)
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/mineru_converter.py \
  --input-dir [pdf_folder] \
  --output-dir [md_output_folder]

# Paper Style Generator: Post-process and tag sections
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/md_postprocessor.py \
  --input-dir [md_folder] \
  --output-dir [tagged_output_folder]

# Paper Style Generator: Extract style patterns
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/style_extractor.py \
  --input-dir [tagged_md_folder] \
  --output-file [analysis.json]

# HWPX Workflow 7: Parse Markdown to JSON blocks
python plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py \
  --input [markdown_file] \
  --output [json_blocks_file]

# HWPX Workflow 7: Write JSON blocks to HWPX XML fragment
python plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py \
  --blocks [json_blocks_file] \
  --style-config [style_config.json] \
  --output [hwpx_fragment.xml]

# HWPX Workflow 7: Embed PNG images into HWPX
python plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py \
  --hwpx [document.hwpx] \
  --images [image_folder] \
  --output [document_with_images.hwpx]
```

## CLAUDE CODE MARKETPLACE RULES

> **Sources**: [Agent Skills Specification](https://agentskills.io/specification), [wshobson/agents](https://github.com/wshobson/agents) (reference implementation with 73 plugins)

### Plugin Root Directory Structure (CRITICAL)

플러그인 루트에는 **오직 아래 4개 폴더만** 허용됩니다. 이 외의 폴더 (`scripts/`, `references/`, `templates/`, `assets/` 등)를 플러그인 루트에 두면 안 됩니다.

```
plugins/{plugin-name}/
├── .claude-plugin/         ← 플러그인별 plugin.json (플러그인 메타데이터)
│   └── plugin.json
├── agents/                 ← 에이전트 .md 파일들
│   ├── agent-name.md
│   └── ...
├── commands/               ← 커맨드(워크플로우) .md 파일들
│   ├── command-name.md
│   └── ...
└── skills/                 ← 스킬 폴더들 (각 스킬은 하위 디렉토리)
    ├── skill-name-1/
    │   ├── SKILL.md        ← 필수: 스킬 정의 파일
    │   ├── references/     ← 선택: 참조 문서
    │   ├── assets/         ← 선택: 템플릿, 리소스
    │   └── scripts/        ← 선택: 실행 스크립트
    └── skill-name-2/
        └── SKILL.md
```

**핵심 규칙:**
- `scripts/`, `references/`, `assets/`는 **스킬 폴더 내부**에만 위치해야 함 (플러그인 루트 ❌)
- `skills/` 아래에는 스킬 이름별 **하위 디렉토리**가 오며, 각 디렉토리에 `SKILL.md` 필수
- 최소 요구사항: 하나의 agent 또는 하나의 command 필요

### Three Component Types

#### 1. Agents (에이전트)

독립적으로 실행되는 전문 AI 에이전트. 별도의 격리된 컨텍스트에서 작동합니다.

```yaml
---
name: backend-architect
description: Expert backend architect specializing in scalable API design, microservices architecture, and distributed systems. Use PROACTIVELY when creating new backend services or APIs.
model: opus       # opus | sonnet | haiku | inherit
---

You are a backend system architect specializing in scalable, resilient, and maintainable backend systems and APIs.

## Purpose
{에이전트의 목적과 전문 분야}

## Capabilities
{에이전트가 할 수 있는 것들}

## Workflow
{작업 흐름}
```

**Agent frontmatter 필드:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | 에이전트 식별자 (hyphen-case) |
| `description` | Yes | 역할 설명 + 언제 사용해야 하는지. "Use when..." 또는 "Use PROACTIVELY when..." 포함 권장 |
| `model` | No | `opus` (아키텍처/보안/리뷰), `sonnet` (복잡한 추론), `haiku` (빠른 실행), `inherit` (부모 모델 상속) |

#### 2. Commands (커맨드)

다단계 워크플로우를 오케스트레이션하는 명령어. 여러 에이전트를 조합하여 복잡한 작업을 수행합니다.

```markdown
Orchestrate end-to-end feature development from requirements to production deployment:

## Configuration Options
{설정 옵션}

## Phase 1: Discovery & Requirements
1. Use Task tool with subagent_type="plugin::agent-name"
   - Prompt: "..."
   - Expected output: ...

## Phase 2: Implementation
1. Use Task tool with subagent_type="plugin::agent-name"
   - Prompt: "..."
```

**커맨드 특징:**
- `commands/` 폴더에 `.md` 파일로 저장
- frontmatter 없음 (에이전트/스킬과 다름)
- 여러 에이전트를 Task tool로 순차/병렬 호출하는 워크플로우 정의
- `$ARGUMENTS`로 사용자 입력을 받음

#### 3. Skills (스킬)

에이전트에게 전문 지식을 제공하는 모듈형 패키지. [Agent Skills Specification](https://agentskills.io/specification) 준수.

```yaml
---
name: api-design-principles
description: Master REST and GraphQL API design principles to build intuitive, scalable, and maintainable APIs. Use when designing new APIs, reviewing API specifications, or establishing API design standards.
---

# API Design Principles

## When to Use This Skill
- Designing new REST or GraphQL APIs
- Refactoring existing APIs for better usability
- ...

## Core Concepts
{핵심 개념}

## Best Practices
{모범 사례}

## Resources
- **references/rest-best-practices.md**: REST API design guide
- **assets/api-design-checklist.md**: Pre-implementation review checklist
- **scripts/openapi-generator.py**: Generate OpenAPI specs from code
```

**SKILL.md frontmatter 필드 (Agent Skills Spec):**

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64자. 소문자 + 숫자 + 하이픈만 허용. 부모 디렉토리명과 일치해야 함 |
| `description` | Yes | Max 1024자. 무엇을 하는지 + 언제 사용하는지 포함. "Use when..." 키워드 권장 |
| `license` | No | 라이선스 이름 또는 파일 참조 |
| `compatibility` | No | Max 500자. 환경 요구사항 (필요한 도구, 네트워크 접근 등) |
| `metadata` | No | 추가 키-값 메타데이터 (author, version 등) |
| `allowed-tools` | No | 사전 승인된 도구 목록 (실험적) |

**`name` 필드 규칙:**
- 소문자 알파벳, 숫자, 하이픈만 허용 (`a-z`, `0-9`, `-`)
- 하이픈으로 시작/끝 불가
- 연속 하이픈 (`--`) 불가
- 부모 디렉토리명과 **반드시 일치**해야 함

**Progressive Disclosure (단계적 로딩):**

| 단계 | 로딩 시점 | 토큰 사용량 |
|------|-----------|------------|
| **Metadata** | 항상 (시작 시) | ~100 토큰/스킬 |
| **Instructions** (SKILL.md body) | 스킬 활성화 시 | < 5000 토큰 권장 |
| **Resources** (references/, assets/, scripts/) | 필요 시에만 | 필요한 만큼 |

SKILL.md는 **500줄 이하** 권장. 상세 참조 자료는 별도 파일로 분리하세요.

### Per-Plugin plugin.json

각 플러그인에 `.claude-plugin/plugin.json`을 두어 플러그인별 메타데이터를 정의합니다:

```json
{
  "name": "backend-development",
  "version": "1.2.4",
  "description": "Backend API design, GraphQL architecture, workflow orchestration with Temporal, and test-driven backend development",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "license": "MIT"
}
```

**Project policy (MANDATORY):**
- Every `plugins/{plugin}/.claude-plugin/plugin.json` MUST include `author.email`.
- In this repository, set `author.email` to `orientpine@gmail.com`.

### Root Marketplace.json Format

`marketplace.json` plugin 항목 필드:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | 플러그인 식별자 |
| `source` | Yes | 플러그인 소스 경로 (상대 경로) |
| `description` | Yes | 플러그인 설명 |
| `strict` | Yes | 항상 `true` |
| `agents` | No | 에이전트 파일 경로 배열 |
| `skills` | No | 스킬 디렉토리 경로 배열 |
| `version` | No | 시맨틱 버전 |
| `author` | No | 저자 정보 |
| `license` | No | 라이선스 |
| `category` | No | 카테고리 |
| `homepage` | No | 홈페이지 URL |

실제 형식은 `.claude-plugin/marketplace.json`을 참조하세요.

### Forbidden Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| 플러그인 루트에 `scripts/` 폴더 | 표준 구조 위반 | `skills/{skill-name}/scripts/`로 이동 |
| 플러그인 루트에 `references/` 폴더 | 표준 구조 위반 | `skills/{skill-name}/references/`로 이동 |
| 플러그인 루트에 `templates/` 폴더 | 표준 구조 위반 | `skills/{skill-name}/assets/`로 이동 |
| 플러그인 루트에 `assets/` 폴더 | 표준 구조 위반 | `skills/{skill-name}/assets/`로 이동 |
| `"skills": ["./skills/"]` (trailing slash) | Path resolution fails | `"./skills"` 사용 |
| `"skills": ["./skills/SKILL.md"]` | Wrong format | `"./skills"` (디렉토리만 지정) |
| Mixed line endings (CRLF + LF) | YAML parsing fails | LF only: `sed -i 's/\r$//' file` |
| description에 `'` 포함 (unquoted) | YAML parsing fails | 큰따옴표로 감싸기 |
| `"strict": false` | Manifest conflicts | 항상 `"strict": true` |
| 대문자 스킬 이름 | Agent Skills Spec 위반 | 소문자 + 하이픈만 사용 |
| 스킬 이름 ≠ 디렉토리명 | 스킬 매칭 실패 | 반드시 일치시킬 것 |

### After Any Changes

```powershell
# MUST clear cache after marketplace changes
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue

# Re-register marketplace
# Claude Code: /plugin marketplace remove {name}
# Claude Code: /plugin marketplace add {path}
```

### CRITICAL: Agent/Skill/Command File Changes Checklist

**⚠️ MANDATORY: When adding, removing, or renaming agent/skill/command files, you MUST update marketplace.json**

This is the #1 source of plugin registration issues:

| Action | Steps |
|--------|-------|
| **Add agent** | 1. Create `.md` in `agents/` → 2. Add to marketplace.json `"agents"` array → 3. Clear cache |
| **Remove agent** | 1. Delete/archive `.md` → 2. Remove from marketplace.json → 3. Clear cache |
| **Add skill** | 1. Create `skills/{name}/SKILL.md` → 2. Ensure `"skills": ["./skills"]` in marketplace.json → 3. Clear cache |
| **Add command** | 1. Create `.md` in `commands/` → 2. Clear cache (commands are auto-discovered) |
| **Rename anything** | 1. Rename file → 2. Update marketplace.json → 3. Clear cache |

**Example: Real-World Case (2026-01-10)**

Created 6 new agents but forgot to update marketplace.json → Agents invisible in Claude. marketplace.json is NOT auto-synced with filesystem. **ALWAYS update manually.**

### Marketplace Registration Checklist

새 플러그인 추가 후 반드시 확인:

- [ ] `plugins/{name}/.claude-plugin/plugin.json` 생성
- [ ] `.claude-plugin/marketplace.json`에 플러그인 항목 추가
- [ ] `"strict": true` 설정
- [ ] 플러그인 루트에 `agents/`, `commands/`, `skills/` 이외 폴더 없음
- [ ] 모든 스킬이 `skills/{skill-name}/SKILL.md` 구조
- [ ] 스킬 name 필드 = 디렉토리 이름 (소문자 + 하이픈)
- [ ] 모든 description에 "Use when..." 키워드 포함
- [ ] SKILL.md/Agent.md의 description이 큰따옴표로 감싸져 있음
- [ ] 모든 .md 파일이 LF 줄바꿈 사용 (CRLF 금지)
- [ ] 플러그인 캐시 클리어 후 재등록

### MANDATORY: Version Management & Registry Updates

> **배경**: 플러그인 수정 후 `plugin.json`/`marketplace.json` 버전을 업데이트하지 않으면, 사용자가 변경사항을 감지할 수 없고 캐시 무효화가 작동하지 않음.

#### Versioning 규칙

모든 플러그인과 마켓플레이스는 `MAJOR.MINOR.PATCH` 형식을 사용합니다.

**플러그인 버전 (`plugin.json`):**

| 버전 구성 | 변경 시점 | 예시 |
|-----------|-----------|------|
| **PATCH** (`x.y.Z`) | 버그 수정, 문서 업데이트, 프롬프트 미세 조정 | 동작 변화 없음 |
| **MINOR** (`x.Y.0`) | 기능 추가/수정/개선 (agent, skill, command, assets 등) | 기존 참조 유지됨 |
| **MAJOR** (`X.0.0`) | agent/skill/command 삭제 또는 이름 변경, plugin.json name 변경 | 기존 참조 깨짐 |

**마켓플레이스 버전 (`marketplace.json` `metadata.version` + `README.md` `Version` + `AGENTS.md` `Version`):**

| 버전 구성 | 변경 시점 | 예시 |
|-----------|-----------|------|
| **PATCH** (`x.y.Z`) | 개별 플러그인 PATCH 수준 변경 (버그 수정, 문서 업데이트), AGENTS.md/README.md 구조 변경 | `3.6.0` → `3.6.1` |
| **MINOR** (`x.Y.0`) | 새 플러그인 추가, 개별 플러그인 MINOR 수준 이상 변경 (기능 추가/수정) | `3.6.0` → `3.7.0` |
| **MAJOR** (`X.0.0`) | 플러그인 삭제/이름 변경, 마켓플레이스 구조 변경 | `3.7.0` → `4.0.0` |

#### 업데이트 대상 파일

| 변경 범위 | 업데이트 대상 |
|-----------|-------------|
| 플러그인 내부 변경 | `plugins/{plugin}/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` 해당 항목 |
| 마켓플레이스 수준 변경 | 위 + `marketplace.json` `metadata.version` + `README.md` `Version` + `AGENTS.md` `Version` + `README.md` 변경 이력 |

**모든 업데이트 대상의 버전은 각각 동기화되어야 합니다.**

#### 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| 플러그인 수정 후 버전 미변경 | 변경사항 추적 불가, 캐시 문제 | 반드시 PATCH 이상 올림 |
| plugin.json과 marketplace.json 버전 불일치 | 혼란, 디버깅 어려움 | 두 파일 동시 업데이트 |
| marketplace metadata.version과 README/AGENTS Version 불일치 | 추적 불가 | 항상 동기화 |
| MAJOR 변경인데 PATCH만 올림 | 호환성 문제 미감지 | 변경 유형 정확히 판단 |

### Model Selection Guide

| Model | Use Case | 예시 |
|-------|----------|------|
| `opus` | 아키텍처 설계, 보안 감사, 코드 리뷰 | backend-architect, security-auditor |
| `sonnet` | 복잡한 추론, 기술 선택, 다단계 분석 | python-pro, typescript-pro |
| `haiku` | 빠른 실행, 정형화된 작업, 코드 생성 | test-automator, scaffold-generator |
| `inherit` | 부모 모델 상속 (기본값) | 대부분의 범용 에이전트 |

---

## MANDATORY: AGENTS.md 최신화 (작업 완료 시)

> **배경**: 프로젝트 구조, 플러그인 구성, 워크플로우가 변경되었음에도 AGENTS.md가 업데이트되지 않으면, 다음 세션의 에이전트가 오래된 정보를 기반으로 잘못된 판단을 내리게 됨. AGENTS.md는 이 프로젝트의 **단일 진실 공급원(Single Source of Truth)**이므로 항상 최신 상태를 유지해야 함.

### 업데이트 트리거 (아래 중 하나라도 해당 시 AGENTS.md 업데이트 필수)

| 변경 유형 | 업데이트 대상 섹션 | 예시 |
|-----------|-------------------|------|
| 플러그인 추가/삭제 | `WHERE TO LOOK`, `UNIQUE STYLES` | 새 플러그인 폴더 추가 |
| Agent/Skill/Command 추가/삭제/이름 변경 | `WHERE TO LOOK` | 에이전트 .md 파일 추가 |
| 워크플로우 순서/구조 변경 | `CONVENTIONS`, `UNIQUE STYLES` | ISD 챕터 순서 변경 |
| 새로운 스크립트/명령어 추가 | `COMMANDS` | 새 Python 스크립트 |
| 새로운 금지 패턴 발견 | `ANTI-PATTERNS` | 새로운 실수 패턴 발견 |
| 프로젝트 규칙/컨벤션 변경 | `CONVENTIONS`, 관련 규칙 섹션 | 새 코딩 규칙 추가 |
| 마켓플레이스 구조 변경 | `CLAUDE CODE MARKETPLACE RULES` | 플러그인 등록 방식 변경 |

### 업데이트 절차

```
Step 1. 작업 완료 후, 위 트리거 목록과 대조하여 AGENTS.md 업데이트가 필요한지 판단
Step 2. 업데이트가 필요하면, 해당 섹션의 기존 내용을 읽고 변경사항 반영
Step 3. AGENTS.md 상단의 **Generated** 날짜를 현재 날짜로 업데이트
Step 4. 변경 내용이 다른 섹션에도 영향을 미치는지 교차 확인
Step 5. 커밋 시 AGENTS.md 변경분을 함께 포함
```

### 업데이트 원칙

| 원칙 | 설명 |
|------|------|
| **정확성 우선** | 추측이 아닌 실제 파일 시스템 상태를 반영할 것 |
| **최소 변경** | 변경된 부분만 수정, 불필요한 리포맷 금지 |
| **일관성 유지** | 기존 문서 스타일(표, 코드블록, 한/영 혼용)을 따를 것 |
| **교차 참조** | 하나의 섹션 변경 시 관련 섹션도 함께 확인 |

### 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| 플러그인 추가 후 AGENTS.md 미업데이트 | 다음 세션에서 새 플러그인 인식 불가 | 반드시 `WHERE TO LOOK` 업데이트 |
| 워크플로우 변경 후 AGENTS.md 미업데이트 | 에이전트가 구버전 워크플로우로 작업 | 즉시 해당 섹션 업데이트 |
| AGENTS.md만 업데이트하고 실제 코드 미반영 | 문서와 코드 불일치 | 코드 변경 → AGENTS.md 순서로 진행 |
| Generated 날짜 미업데이트 | 최종 업데이트 시점 추적 불가 | 항상 현재 날짜로 갱신 |

---

## MANDATORY: README.md 최신화 (작업 완료 시)

> **배경**: README.md는 외부 사용자와 새 기여자가 프로젝트를 처음 접하는 진입점이므로, AGENTS.md와 마찬가지로 프로젝트 변경 시 반드시 최신 상태를 유지해야 함. README.md가 오래되면 사용자가 존재하지 않는 플러그인을 참조하거나, 새로 추가된 기능을 인지하지 못하게 됨.

### 업데이트 트리거 (아래 중 하나라도 해당 시 README.md 업데이트 필수)

| 변경 유형 | 업데이트 대상 섹션 | 예시 |
|-----------|-------------------|------|
| 플러그인 추가/삭제 | `주요 기능` 표, `프로젝트 구조`, `플러그인 상세` | 새 플러그인 추가 |
| Agent/Skill/Command 수 변경 | `프로젝트 구조`, 해당 `플러그인 상세` 항목 | 에이전트 추가/삭제 |
| 플러그인 워크플로우/기능 변경 | 해당 `플러그인 상세` 항목 | 새 테마 추가, 워크플로우 변경 |
| 프로젝트 버전 변경 | 상단 `Version`, `변경 이력` 표 | 메이저/마이너 릴리스 |
| 사용법/설정 방법 변경 | `빠른 시작`, `개발 가이드` | 등록 방식 변경 |
| 프로젝트 구조 변경 | `프로젝트 구조` 트리 | 디렉토리 구조 변경 |

### 업데이트 절차

```
Step 1. 작업 완료 후, 위 트리거 목록과 대조하여 README.md 업데이트가 필요한지 판단
Step 2. 업데이트가 필요하면, 해당 섹션의 기존 내용을 읽고 변경사항 반영
Step 3. README.md 상단의 **Version** 필드를 필요 시 업데이트
Step 4. `변경 이력` 표에 새 항목 추가 (날짜, 버전, 변경 내용)
Step 5. 커밋 시 README.md 변경분을 함께 포함
```

### 업데이트 원칙

| 원칙 | 설명 |
|------|------|
| **AGENTS.md와 동시 업데이트** | 두 문서의 업데이트 트리거가 겹치므로, AGENTS.md 업데이트 시 README.md도 함께 확인할 것 |
| **정확성 우선** | 실제 파일 시스템 상태 및 marketplace.json과 일치하도록 반영 |
| **최소 변경** | 변경된 부분만 수정, 불필요한 리포맷 금지 |
| **변경 이력 필수** | 사용자가 인지할 수 있는 변경은 반드시 `변경 이력` 표에 기록 |

### 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| 플러그인 추가/삭제 후 README.md 미업데이트 | 외부 사용자가 새 기능 인지 불가 | `주요 기능`, `프로젝트 구조`, `플러그인 상세` 동시 업데이트 |
| AGENTS.md만 업데이트하고 README.md 누락 | 두 문서 간 정보 불일치 | 항상 함께 확인 |
| 변경 이력 미기록 | 변경사항 추적 불가 | `변경 이력` 표에 반드시 추가 |
| README.md Version과 실제 버전 불일치 | 사용자 혼란 | marketplace 버전과 동기화 |

---

## NOTES

- **API Key**: `.env` 파일에서 `GEMINI_API_KEY` 환경변수 로드 (python-dotenv 사용)
- **Model**: `gemini-3-pro-image-preview` for 4K 16:9 images with Korean text
- **Rate Limit**: 2-second delay between API calls
- **ISD Output**: `output/[프로젝트명]/chapter_{1-5}/`
- **All SKILL.md files**: Contain exhaustive workflow phases with numbered steps
