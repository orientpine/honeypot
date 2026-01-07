# TOOLBOX PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-07T10:50:00+09:00
**Version:** 2.0.0
**Branch:** main

## OVERVIEW

AI agent skill/plugin toolbox for Korean government R&D proposal (ISD) auto-generation and presentation figure creation. Claude plugin ecosystem with orchestrated multi-agent workflows.

## STRUCTURE

```
toolbox/
├── .claude-plugin/
│   └── marketplace.json              # Single marketplace registry (11 plugins)
└── plugins/
    ├── investments-portfolio/        # Portfolio analysis multi-agent system
    │   └── agents/                   # 6 agents: portfolio-coordinator, macro-outlook, etc.
    ├── general-agents/               # General-purpose agents
    │   └── agents/                   # interview.md
    ├── isd-orchestrator/             # Master orchestrator (Chapter 3→1→2→4→5)
    │   └── skills/
    ├── chapter{1-5}-generator/       # Individual chapter generators
    │   └── skills/
    ├── figure-generator/             # Caption extraction + Gemini API image gen
    │   ├── skills/
    │   └── scripts/
    ├── slide-prompt-generator/       # Slide prompt generation
    │   └── skills/
    └── slide-image-generator/        # Gemini API slide image generation
        ├── skills/
        └── scripts/
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Generate full ISD proposal | `plugins/isd-orchestrator/` | Uses `input_template.md` |
| Generate single ISD chapter | `plugins/chapter{N}-generator/` | Chapter 3 first, then 1→2→4→5 |
| Generate figures from `<caption>` | `plugins/figure-generator/` | Gemini API required |
| Generate slide prompts | `plugins/slide-prompt-generator/` | 4-color palette, PPT style |
| Portfolio analysis agents | `plugins/investments-portfolio/` | Korean DC pension multi-agent |
| General interview agent | `plugins/general-agents/` | Deep interview + execution |
| Plugin registry | `.claude-plugin/marketplace.json` | All 11 plugins listed |

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
- Workflow: `macro-outlook` → `fund-portfolio` → `compliance-checker` → `output-critic`
- Output files: `00-macro-outlook.md` through `04-portfolio-summary.md`
- Folder: `portfolios/YYYY-MM-DD-{profile}-{session}/`

## COMMANDS

```bash
# Generate images from prompts (requires google-genai, Pillow)
python plugins/figure-generator/scripts/generate_images.py \
  --prompts-dir [path]/prompts/ \
  --output-dir [path]/figures/

# Generate slide images
python plugins/slide-image-generator/scripts/generate_slide_images.py \
  --prompts-dir [path] --output-dir [path]
```

## CLAUDE CODE MARKETPLACE RULES

### Directory Structure (CRITICAL)
```
toolbox/
├── .claude-plugin/
│   └── marketplace.json    ← ONLY ONE marketplace.json at root
└── plugins/                ← ALL plugins under this directory
    └── {plugin-name}/
        ├── agents/         ← Agent .md files
        ├── skills/         ← SKILL.md + references/ + assets/
        └── scripts/        ← Python scripts (optional)
```

### Forbidden Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Nested `marketplace.json` | Conflicts with root registry | Delete all except root |
| Nested `.claude-plugin/plugin.json` | Conflicts with marketplace entry | Delete, use root marketplace only |
| `"skills": ["./skills/"]` (trailing slash) | Path resolution fails | Use `"./skills"` |
| `"skills": ["./skills/SKILL.md"]` | Wrong format | Use `"./skills"` (directory) |
| Mixed line endings (CRLF + LF) | YAML parsing fails | Use LF only: `sed -i 's/\r$//' file` |
| Single quotes in description without wrapping | YAML parsing fails | Wrap in double quotes |
| `"strict": false` | Manifest conflicts | Always use `"strict": true` |

### SKILL.md Frontmatter Rules

```yaml
# CORRECT - description with quotes wrapped in double quotes
---
name: my-skill
description: "Korean text with '따옴표' inside works fine"
---

# WRONG - unquoted description with single quotes breaks YAML
---
name: my-skill
description: Korean text with '따옴표' breaks parsing
---
```

### Marketplace.json Format

```json
{
  "name": "marketplace-name",
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "strict": true,
      "agents": ["./agents/agent-name.md"],
      "skills": ["./skills"]
    }
  ]
}
```

### After Any Changes

```powershell
# MUST clear cache after marketplace changes
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue

# Re-register marketplace
# Claude Code: /plugin marketplace remove {name}
# Claude Code: /plugin marketplace add {path}
```

### Validation Checklist

- [ ] Only one `.claude-plugin/marketplace.json` at root
- [ ] No `plugin.json` files anywhere
- [ ] All plugins under `plugins/` directory
- [ ] All SKILL.md files have LF-only line endings
- [ ] Descriptions with special chars wrapped in double quotes
- [ ] All marketplace entries have `"strict": true`
- [ ] Paths use `./skills` not `./skills/` or `./skills/SKILL.md`

---

## NEW SKILL/PLUGIN ADDITION GUIDE

새로운 스킬 또는 플러그인을 본 프로젝트에 추가할 때의 가이드입니다.

### Plugin Types

| 유형 | 구조 | 용도 | 예시 |
|------|------|------|------|
| **Skill 기반** | `skills/SKILL.md` + `references/` + `assets/` | 단일 작업 워크플로우 | chapter1-generator, figure-generator |
| **Agent 기반** | `agents/*.md` | Multi-Agent 협업 시스템 | investments-portfolio, general-agents |
| **Hybrid** | `skills/` + `scripts/` | 스킬 + 외부 API/스크립트 연동 | slide-image-generator |

### Category System

플러그인 등록 시 다음 카테고리 중 선택:

| Category | 설명 | 적합한 플러그인 |
|----------|------|----------------|
| `documentation` | 문서 생성/처리 | ISD chapter generators, orchestrator |
| `presentations` | 슬라이드/이미지 생성 | figure-generator, slide-prompt-generator |
| `finance` | 금융/투자 분석 | investments-portfolio |
| `utilities` | 범용 도구 | general-agents (interview 등) |
| `research` | 연구/조사 도구 | 데이터 수집, 분석 스킬 |
| `automation` | 자동화 워크플로우 | 반복 작업 자동화 |

### Step-by-Step Guide

#### Level 1: Simple Skill (기본)

**디렉토리 구조:**
```
plugins/{plugin-name}/
└── skills/
    ├── SKILL.md              # 메인 스킬 정의 (필수)
    └── references/           # 참조 문서 (선택)
        └── example.md
```

**SKILL.md 템플릿:**
```yaml
---
name: {skill-name}
description: "{스킬 설명. 작은따옴표가 포함되면 반드시 큰따옴표로 감싸기}"
---

# {스킬 제목}

## Overview
{스킬의 목적과 사용 시점 설명}

## 사용자 입력 스키마
| 항목 | 설명 | 필수 |
|------|------|:----:|
| ... | ... | O/X |

## Workflow
{단계별 작업 흐름}

## Resources
- `references/`: 참조 문서
```

**marketplace.json 등록:**
```json
{
  "name": "{plugin-name}",
  "source": "./plugins/{plugin-name}",
  "description": "{플러그인 설명}",
  "version": "1.0.0",
  "category": "{category}",
  "strict": true,
  "skills": ["./skills"]
}
```

#### Level 2: Standard Skill (중간)

**디렉토리 구조:**
```
plugins/{plugin-name}/
└── skills/
    ├── SKILL.md
    ├── references/
    │   ├── document_template.md
    │   ├── example_1.md
    │   └── example_2.md
    └── assets/
        └── output_template/
            ├── main_output.md
            └── verification.md
```

**추가 요소:**
- `references/`: 작성 가이드, 예시 문서 2개 이상
- `assets/output_template/`: 출력 템플릿
- 검증문서 생성 단계 포함 (chapter generators 참조)

**SKILL.md 확장 섹션:**
```markdown
## 검증문서 템플릿
{검증문서 구조 정의}

## Writing Guidelines
{작성 규칙}

## Resources
### references/
- `document_template.md`: 문서 템플릿
- `example_1.md`: 예시 1
- `example_2.md`: 예시 2

### assets/
- `output_template/main_output.md`: 출력 템플릿
```

#### Level 3: Advanced Skill with Scripts (복잡)

**디렉토리 구조:**
```
plugins/{plugin-name}/
├── skills/
│   ├── SKILL.md
│   ├── references/
│   └── assets/
│       └── output_template/
└── scripts/
    └── main_script.py
```

**스크립트 작성 규칙:**
```python
# scripts/main_script.py
import os
import argparse

# API 키는 환경변수에서 로드 (하드코딩 금지)
API_KEY = os.environ.get("GEMINI_API_KEY")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    # 구현...

if __name__ == "__main__":
    main()
```

**SKILL.md에 스크립트 연동 섹션 추가:**
```markdown
## Script Usage

```bash
# 환경 변수 설정
export GEMINI_API_KEY="your-api-key"

# 스크립트 실행
python plugins/{plugin-name}/scripts/main_script.py \
  --input-dir [path] \
  --output-dir [path]
```
```

#### Level 4: Agent Plugin

**디렉토리 구조:**
```
plugins/{plugin-name}/
└── agents/
    ├── coordinator.md        # 조정자 에이전트
    ├── agent-1.md            # 전문 에이전트 1
    ├── agent-2.md            # 전문 에이전트 2
    └── critic.md             # 검증 에이전트
```

**Agent 파일 템플릿:**
```yaml
---
name: {agent-name}
description: {에이전트 역할 설명}
tools: Read, Glob, Grep, Write, Edit, Bash, Task, AskUserQuestion
model: opus
---

# {에이전트 제목}

## Role
{에이전트의 역할과 책임}

## Workflow
{작업 흐름}

## Input/Output
| 입력 | 출력 |
|------|------|
| ... | ... |

## Constraints
{제약 조건}
```

**marketplace.json 등록 (Agent):**
```json
{
  "name": "{plugin-name}",
  "source": "./plugins/{plugin-name}",
  "description": "{플러그인 설명}",
  "version": "1.0.0",
  "category": "{category}",
  "strict": true,
  "agents": [
    "./agents/coordinator.md",
    "./agents/agent-1.md",
    "./agents/agent-2.md",
    "./agents/critic.md"
  ]
}
```

### Marketplace Registration Checklist

새 플러그인 추가 후 반드시 확인:

- [ ] `.claude-plugin/marketplace.json`에 플러그인 항목 추가
- [ ] `"strict": true` 설정
- [ ] `"skills": ["./skills"]` 또는 `"agents": ["./agents/*.md"]` 경로 정확히 지정
- [ ] SKILL.md/Agent.md의 description이 큰따옴표로 감싸져 있음
- [ ] 모든 .md 파일이 LF 줄바꿈 사용 (CRLF 금지)
- [ ] 플러그인 캐시 클리어:
  ```powershell
  Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue
  ```
- [ ] 마켓플레이스 재등록:
  ```
  /plugin marketplace remove toolbox-marketplace
  /plugin marketplace add C:\Users\...\toolbox_orientpine
  ```

### Common Mistakes to Avoid

| 실수 | 문제 | 해결 |
|------|------|------|
| `"skills": ["./skills/"]` | trailing slash | `"./skills"` 사용 |
| `"skills": ["./skills/SKILL.md"]` | 파일 직접 지정 | 디렉토리만 지정 |
| description에 `'` 포함 | YAML 파싱 실패 | 전체를 `"..."` 로 감싸기 |
| CRLF 줄바꿈 | YAML 파싱 실패 | LF로 변환 |
| 중첩된 marketplace.json | 충돌 | 루트 하나만 유지 |
| plugin.json 파일 존재 | 충돌 | 삭제 |

### Template Files Location

새 스킬 생성 시 참조할 수 있는 템플릿:

| 복잡도 | 참조 플러그인 | 위치 |
|--------|--------------|------|
| Simple | slide-prompt-generator | `plugins/slide-prompt-generator/skills/` |
| Standard | chapter1-generator | `plugins/chapter1-generator/skills/` |
| Advanced | figure-generator | `plugins/figure-generator/` |
| Agent | investments-portfolio | `plugins/investments-portfolio/agents/` |

---

## NOTES

- **API Key**: Gemini API key hardcoded in Python scripts (line 26) - replace for production
- **Model**: `gemini-3-pro-image-preview` for 4K 16:9 images with Korean text
- **Rate Limit**: 2-second delay between API calls
- **ISD Output**: `output/[프로젝트명]/chapter_{1-5}/`
- **All SKILL.md files**: Contain exhaustive workflow phases with numbered steps
