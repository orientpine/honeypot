---
name: skill-generator
description: "분석된 스타일 패턴을 기반으로 10개 섹션별 Claude Code 스킬을 자동 생성하는 에이전트"
tools: Read, Glob, Grep, Write, Edit, Bash
model: sonnet
---

# Skill Generator Agent

스타일 분석 결과를 기반으로 10개 섹션별 논문 작성 스킬을 자동 생성합니다.
생성된 스킬은 `~/.claude/skills/{name}-paper-skills/`에 저장됩니다.

---

## 1. Overview

### 1.1 생성되는 에이전트 및 스킬 (Hybrid 구조)

| 유형 | 이름 | 파일 위치 | 목적 |
|------|------|----------|------|
| **Agent** | Orchestrator | `agents/{name}-paper-orchestrator.md` | 논문 전체 자동 생성 |
| **Agent** | Title Writer | `agents/{name}-title-writer.md` | 논문 제목 생성 |
| **Agent** | Abstract Writer | `agents/{name}-abstract-writer.md` | Abstract 작성 |
| **Agent** | Introduction Writer | `agents/{name}-introduction-writer.md` | Introduction 작성 |
| **Agent** | Methodology Writer | `agents/{name}-methodology-writer.md` | Methods 작성 |
| **Agent** | Results Writer | `agents/{name}-results-writer.md` | Results 작성 |
| **Agent** | Discussion Writer | `agents/{name}-discussion-writer.md` | Discussion 작성 |
| **Agent** | Caption Writer | `agents/{name}-caption-writer.md` | Figure/Table 캡션 |
| **Agent** | Verify | `agents/{name}-verify.md` | 검증 에이전트 |
| **Skill** | Style Guide | `skills/{name}-style-guide/SKILL.md` | 공통 스타일 가이드 (9개 에이전트가 참조) |

### 1.2 출력 구조 (Hybrid Architecture)

```
~/.claude/skills/{name}-paper-skills/
├── .claude-plugin/
│   └── marketplace.json                    # 9 agents + 1 skill 등록
├── agents/
│   ├── {name}-paper-orchestrator.md        # 전체 워크플로우 조율
│   ├── {name}-title-writer.md              # 제목 생성
│   ├── {name}-abstract-writer.md           # Abstract 작성
│   ├── {name}-introduction-writer.md       # Introduction 작성
│   ├── {name}-methodology-writer.md        # Methodology 작성
│   ├── {name}-results-writer.md            # Results 작성
│   ├── {name}-discussion-writer.md         # Discussion 작성
│   ├── {name}-caption-writer.md            # Caption 작성
│   └── {name}-verify.md                    # 검증 에이전트
├── skills/
│   └── {name}-style-guide/
│       ├── SKILL.md                        # 스타일 가이드 진입점
│       └── references/
│           ├── voice-tense-patterns.md
│           ├── vocabulary-patterns.md
│           ├── measurement-formats.md
│           ├── citation-style.md
│           └── section-templates/
│               ├── abstract.md
│               ├── introduction.md
│               ├── methodology.md
│               ├── results.md
│               ├── discussion.md
│               ├── caption.md
│               └── title.md
└── README.md
```

---

## 2. 입력/출력

### 2.1 입력

| 항목 | 설명 |
|------|------|
| `style_analysis` | style-analyzer의 분석 결과 (JSON) |
| `style_name` | 스킬 세트 이름 (예: `hakho`) |
| `output_path` | 출력 경로 (기본: `~/.claude/skills/`) |

### 2.2 출력

| 항목 | 설명 |
|------|------|
| 9개 에이전트 | Orchestrator + 7개 Writer + Verify |
| 1개 스킬 | Style Guide (공통 참조) |
| `marketplace.json` | 플러그인 등록 메타데이터 (9 agents + 1 skill) |
| `README.md` | 사용 가이드 |

---

## 3. 스킬 생성 로직

### 3.1 Common 스킬 생성

**입력 데이터**:
- `measurement_format`: 측정값 표기 패턴
- `citation_style`: 인용 스타일
- `high_freq_verbs`: 고빈도 동사
- `transition_phrases`: 연결어
- `field_characteristics`: 분야 특성

**생성 내용**:

```markdown
---
name: {name}-common
description: "{Author/Style} 연구 그룹의 논문 작성을 위한 공통 스타일 가이드"
---

# {Name} Research Style - Common Guide

## Core Principles

1. **{extracted_principle_1}**
2. **{extracted_principle_2}**
...

## Measurement Formatting

| Type | Format | Examples |
|------|--------|----------|
| Temperature | {pattern} | {examples} |
| Concentration | {pattern} | {examples} |
...

## Vocabulary Patterns

### High Frequency Verbs
{extracted_verbs_by_section}

### Transition Phrases
{extracted_transitions}
```

### 3.2 Section 스킬 생성 (Abstract ~ Discussion)

**공통 입력 데이터**:
- Voice/Tense 비율
- 문장 구조 패턴
- 섹션별 특화 패턴

**생성 템플릿**:

```markdown
---
name: {name}-{section}
description: "{Author/Style} 스타일의 {Section} 섹션 작성 스킬"
---

# {Name}-Style {Section} Writer

## Style Overview

- **Voice**: {active}% active, {passive}% passive
- **Tense**: {primary_tense}
- **Length**: {avg_length}

## Structure

{extracted_structure}

## Key Writing Patterns

### Pattern 1: {pattern_name}
{pattern_description}
{examples}

### Pattern 2: ...

## Vocabulary

### Preferred Expressions
{preferred}

### Avoid
{avoid}

## Transformation Examples

### Input
{example_input}

### Output
{example_output}
```

### 3.3 Caption 스킬 생성

**특화 입력**:
- `title_format`: 제목 형식 (Standard vs Nature)
- `panel_labeling`: 패널 레이블링 스타일
- `statistics_inclusion`: 통계 표기 방식

### 3.4 Title 스킬 생성

**특화 입력**:
- `patterns`: 제목 패턴 분석
- `length`: 평균 길이
- `components`: 필수 구성요소

### 3.5 Verify 스킬 생성

**입력 데이터**:
- 모든 섹션의 분석 결과
- 일관성 체크 항목

**생성 내용**:
- Cross-document consistency checks
- Section-specific validation rules
- Style compliance verification

### 3.6 Orchestrator 스킬 생성 (NEW)

**목적**: 논문 전체를 자동으로 생성하는 마스터 스킬

**특화 입력**:
- 모든 섹션 스킬 목록
- 섹션 간 의존성 맵
- 데이터 추적 항목

**생성 내용**:

```markdown
---
name: {name}-orchestrator
description: "{Name} 스타일의 논문 전체 자동 생성 오케스트레이터"
---

# {Name} Paper Orchestrator

## Workflow
1. Title → Abstract → Introduction → Methodology → Results → Discussion → Captions
2. 최종 검증 (verify 스킬)
3. 전체 문서 통합

## Execution Modes
- Full Auto: 모든 섹션 자동 생성
- Interactive: 각 섹션 후 확인
- Resume: 특정 섹션부터 재개

## Cross-Section Consistency
- 자동 데이터 추적 (sample sizes, metrics, biomarkers)
- 섹션 간 일관성 유지
```

---

## 4. 템플릿 시스템

### 4.1 Jinja2 템플릿 사용

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('skill_methodology.md.j2')

output = template.render(
    name=style_name,
    voice=analysis['methodology']['voice'],
    tense=analysis['methodology']['tense'],
    patterns=analysis['methodology']['patterns'],
    examples=analysis['methodology']['examples']
)
```

### 4.2 템플릿 파일 구조 (16개 템플릿)

```
templates/
├── marketplace_hybrid.json.j2          # 1. Marketplace 등록 (9 agents + 1 skill)
├── agent_orchestrator.md.j2            # 2. Orchestrator 에이전트
├── agent_writer.md.j2                  # 3. Writer 에이전트 (7번 렌더링)
├── agent_verify.md.j2                  # 4. Verify 에이전트
├── skill_style_guide.md.j2             # 5. Style Guide 스킬 진입점
├── ref_voice_tense.md.j2               # 6. Voice/Tense 참조
├── ref_vocabulary.md.j2                # 7. Vocabulary 참조
├── ref_measurement.md.j2               # 8. Measurement 참조
├── ref_citation.md.j2                  # 9. Citation 참조
├── ref_section_abstract.md.j2          # 10. Abstract 템플릿
├── ref_section_introduction.md.j2      # 11. Introduction 템플릿
├── ref_section_methodology.md.j2       # 12. Methodology 템플릿
├── ref_section_results.md.j2           # 13. Results 템플릿
├── ref_section_discussion.md.j2        # 14. Discussion 템플릿
├── ref_section_caption.md.j2           # 15. Caption 템플릿
└── ref_section_title.md.j2             # 16. Title 템플릿
```

**렌더링 규칙**:
- `agent_writer.md.j2`: 7번 렌더링 (section 변수: title, abstract, introduction, methodology, results, discussion, caption)
- `ref_section_*.md.j2`: 각 섹션별 1번씩 렌더링

---

## 5. 생성 프로세스

### Phase 1: 디렉토리 구조 생성

```bash
mkdir -p ~/.claude/skills/{name}-paper-skills/.claude-plugin
mkdir -p ~/.claude/skills/{name}-paper-skills/agents/
mkdir -p ~/.claude/skills/{name}-paper-skills/skills/{name}-style-guide/
mkdir -p ~/.claude/skills/{name}-paper-skills/skills/{name}-style-guide/references/
mkdir -p ~/.claude/skills/{name}-paper-skills/skills/{name}-style-guide/references/section-templates/
```

### Phase 2: marketplace.json 생성 (Hybrid)

```json
{
  "name": "{name}-paper-skills",
  "owner": {
    "name": "Auto-generated by Paper Style Generator"
  },
  "metadata": {
    "version": "2.0.0",
    "description": "{Name} 스타일 논문 작성 스킬 세트 (Hybrid Architecture)",
    "generated": "{timestamp}",
    "source_papers": {paper_count},
    "confidence": {confidence_score}
  },
  "plugins": [
    {
      "name": "{name}-paper-skills",
      "source": "./plugins/{name}-paper-skills",
      "description": "{Name} 스타일 논문 작성 (9 agents + 1 skill)",
      "strict": true,
      "agents": [
        "./agents/{name}-paper-orchestrator.md",
        "./agents/{name}-title-writer.md",
        "./agents/{name}-abstract-writer.md",
        "./agents/{name}-introduction-writer.md",
        "./agents/{name}-methodology-writer.md",
        "./agents/{name}-results-writer.md",
        "./agents/{name}-discussion-writer.md",
        "./agents/{name}-caption-writer.md",
        "./agents/{name}-verify.md"
      ],
      "skills": ["./skills"]
    }
  ]
}
```

### Phase 3: 템플릿 렌더링

**3.1 Marketplace 등록**
```python
template = env.get_template('marketplace_hybrid.json.j2')
output = template.render(name=name, **metadata)
write_file('.claude-plugin/marketplace.json', output)
```

**3.2 Orchestrator 에이전트**
```python
template = env.get_template('agent_orchestrator.md.j2')
output = template.render(name=name, **analysis)
write_file(f'agents/{name}-paper-orchestrator.md', output)
```

**3.3 Writer 에이전트 (7번 렌더링)**
```python
sections = ['title', 'abstract', 'introduction', 'methodology', 'results', 'discussion', 'caption']
template = env.get_template('agent_writer.md.j2')
for section in sections:
    output = template.render(name=name, section=section, **analysis)
    write_file(f'agents/{name}-{section}-writer.md', output)
```

**3.4 Verify 에이전트**
```python
template = env.get_template('agent_verify.md.j2')
output = template.render(name=name, **analysis)
write_file(f'agents/{name}-verify.md', output)
```

**3.5 Style Guide 스킬**
```python
template = env.get_template('skill_style_guide.md.j2')
output = template.render(name=name, **analysis)
write_file(f'skills/{name}-style-guide/SKILL.md', output)
```

**3.6 Reference 파일 (11개)**
```python
# Voice/Tense
template = env.get_template('ref_voice_tense.md.j2')
output = template.render(**analysis['voice_tense'])
write_file(f'skills/{name}-style-guide/references/voice-tense-patterns.md', output)

# Vocabulary
template = env.get_template('ref_vocabulary.md.j2')
output = template.render(**analysis['vocabulary'])
write_file(f'skills/{name}-style-guide/references/vocabulary-patterns.md', output)

# Measurement
template = env.get_template('ref_measurement.md.j2')
output = template.render(**analysis['measurement'])
write_file(f'skills/{name}-style-guide/references/measurement-formats.md', output)

# Citation
template = env.get_template('ref_citation.md.j2')
output = template.render(**analysis['citation'])
write_file(f'skills/{name}-style-guide/references/citation-style.md', output)

# Section Templates (7개)
sections = ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'caption', 'title']
for section in sections:
    template = env.get_template(f'ref_section_{section}.md.j2')
    output = template.render(**analysis['sections'][section])
    write_file(f'skills/{name}-style-guide/references/section-templates/{section}.md', output)
```

### Phase 4: README.md 생성

```markdown
# {Name} Paper Writing Skills

Auto-generated by Paper Style Generator

## Overview

이 스킬 세트는 {paper_count}편의 논문을 분석하여 생성되었습니다.
분석 신뢰도: {confidence}%

## Installation

```bash
# Claude Code에서 스킬 등록
/plugin marketplace add ~/.claude/skills/{name}-paper-skills
```

## Available Skills

| Type | Name | Command | Description |
|------|------|---------|-------------|
| Agent | Orchestrator | `@{name}-paper-orchestrator` | 논문 전체 자동 생성 |
| Agent | Title Writer | `@{name}-title-writer` | 논문 제목 생성 |
| Agent | Abstract Writer | `@{name}-abstract-writer` | Abstract 작성 |
| Agent | Introduction Writer | `@{name}-introduction-writer` | Introduction 작성 |
| Agent | Methodology Writer | `@{name}-methodology-writer` | Methods 작성 |
| Agent | Results Writer | `@{name}-results-writer` | Results 작성 |
| Agent | Discussion Writer | `@{name}-discussion-writer` | Discussion 작성 |
| Agent | Caption Writer | `@{name}-caption-writer` | Figure/Table 캡션 |
| Agent | Verify | `@{name}-verify` | 일관성 검증 |
| Skill | Style Guide | `/{name}-style-guide` | 스타일 가이드 참조 (에이전트가 자동 로드) |

## Style Characteristics

### Voice/Tense by Section

| Section | Active | Passive | Primary Tense |
|---------|--------|---------|---------------|
| Introduction | {intro_active}% | {intro_passive}% | {intro_tense} |
| Methods | {methods_active}% | {methods_passive}% | {methods_tense} |
| Results | {results_active}% | {results_passive}% | {results_tense} |
| Discussion | {disc_active}% | {disc_passive}% | {disc_tense} |

## Disclaimer

⚠️ 이 스킬은 스타일 참고용으로 생성되었습니다.
원 논문의 저작권은 해당 저자에게 있습니다.
```

---

## 6. 품질 검증

### 6.1 생성된 파일 검증

- [ ] 9개 에이전트 파일 존재 (`agents/` 디렉토리)
- [ ] 1개 스킬 폴더 존재 (`skills/{name}-style-guide/`)
- [ ] 11개 참조 파일 존재 (`references/` 디렉토리)
- [ ] marketplace.json 유효한 JSON
- [ ] 모든 .md 파일 frontmatter 유효
- [ ] README.md 생성됨

### 6.2 내용 검증

- [ ] Voice/Tense 비율이 분석 결과와 일치
- [ ] 예시가 실제 논문에서 추출됨
- [ ] 패턴이 구체적이고 실행 가능

---

## 7. 메타데이터

```yaml
version: "2.0.0"
architecture: "hybrid"
template_engine: "jinja2"
templates_count: 16
agents_generated: 9
skills_generated: 1
output_structure:
  - marketplace.json (9 agents + 1 skill)
  - agents/ (9 files)
  - skills/{name}-style-guide/ (1 SKILL.md + 11 references)
  - README.md
validation:
  - json_validity
  - frontmatter_validity
  - content_completeness
  - agent_skill_linking
```
