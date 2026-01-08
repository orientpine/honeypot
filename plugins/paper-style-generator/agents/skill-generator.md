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

### 1.1 생성되는 스킬 (10개)

| 스킬 | 파일명 | 목적 |
|------|--------|------|
| Common | `{name}-common` | 공통 스타일 가이드 |
| Abstract | `{name}-abstract` | Abstract 작성 |
| Introduction | `{name}-introduction` | Introduction 작성 |
| Methodology | `{name}-methodology` | Methods 작성 |
| Results | `{name}-results` | Results 작성 |
| Discussion | `{name}-discussion` | Discussion 작성 |
| Caption | `{name}-caption` | Figure/Table 캡션 |
| Title | `{name}-title` | 논문 제목 생성 |
| Verify | `{name}-verify` | 검증 스킬 |
| **Orchestrator** | `{name}-orchestrator` | **논문 전체 자동 생성** |

### 1.2 출력 구조

```
~/.claude/skills/{name}-paper-skills/
├── .claude-plugin/
│   └── marketplace.json
├── {name}-common/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       ├── SKILL.md
│       └── references/
│           ├── style-guide.md
│           └── vocabulary-patterns.md
├── {name}-abstract/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       ├── SKILL.md
│       └── assets/
│           └── input-template.md
├── {name}-introduction/
│   └── skills/...
├── {name}-methodology/
│   └── skills/...
├── {name}-results/
│   └── skills/...
├── {name}-discussion/
│   └── skills/...
├── {name}-caption/
│   └── skills/...
├── {name}-title/
│   └── skills/...
├── {name}-verify/
│   └── skills/...
├── {name}-orchestrator/           # 논문 전체 자동 생성
│   └── skills/
│       ├── SKILL.md
│       └── assets/
│           └── input-template.md
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
| 10개 스킬 폴더 | 각 섹션별 완전한 스킬 구조 + Orchestrator |
| `marketplace.json` | 플러그인 등록 메타데이터 |
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

### 4.2 템플릿 파일 구조

```
templates/
├── skill_common.md.j2
├── skill_abstract.md.j2
├── skill_introduction.md.j2
├── skill_methodology.md.j2
├── skill_results.md.j2
├── skill_discussion.md.j2
├── skill_caption.md.j2
├── skill_title.md.j2
├── skill_verify.md.j2
├── skill_orchestrator.md.j2    # 논문 전체 자동 생성
├── marketplace.json.j2
├── plugin.json.j2
└── readme.md.j2
```

---

## 5. 생성 프로세스

### Phase 1: 디렉토리 구조 생성

```bash
mkdir -p ~/.claude/skills/{name}-paper-skills/.claude-plugin
mkdir -p ~/.claude/skills/{name}-paper-skills/{name}-common/skills/references
mkdir -p ~/.claude/skills/{name}-paper-skills/{name}-abstract/skills/assets
mkdir -p ~/.claude/skills/{name}-paper-skills/{name}-orchestrator/skills/assets
# ... 나머지 10개 스킬 폴더
```

### Phase 2: marketplace.json 생성

```json
{
  "name": "{name}-paper-skills",
  "owner": {
    "name": "Auto-generated by Paper Style Generator"
  },
  "metadata": {
    "version": "1.0.0",
    "description": "{Name} 스타일 논문 작성 스킬 세트",
    "generated": "{timestamp}",
    "source_papers": {paper_count},
    "confidence": {confidence_score}
  },
  "plugins": [
    {
      "name": "{name}-common",
      "source": "./{name}-common",
      "description": "공통 스타일 가이드",
      "strict": true,
      "skills": ["./skills"]
    },
    // ... 나머지 8개 플러그인
  ]
}
```

### Phase 3: 각 스킬 생성

각 스킬에 대해:
1. plugin.json 생성
2. SKILL.md 생성 (템플릿 + 분석 데이터)
3. references/ 또는 assets/ 생성

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

| Skill | Command | Description |
|-------|---------|-------------|
| Common | `/{name}-common` | 스타일 가이드 참조 |
| Abstract | `/{name}-abstract` | Abstract 작성 |
| Introduction | `/{name}-introduction` | Introduction 작성 |
| Methodology | `/{name}-methodology` | Methods 작성 |
| Results | `/{name}-results` | Results 작성 |
| Discussion | `/{name}-discussion` | Discussion 작성 |
| Caption | `/{name}-caption` | Figure/Table 캡션 |
| Title | `/{name}-title` | 논문 제목 생성 |
| Verify | `/{name}-verify` | 일관성 검증 |
| **Orchestrator** | `/{name}-orchestrator` | **논문 전체 자동 생성** |

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

### 6.1 생성된 스킬 검증

- [ ] 모든 10개 스킬 폴더 존재 (orchestrator 포함)
- [ ] 각 스킬의 SKILL.md 존재
- [ ] marketplace.json 유효한 JSON
- [ ] plugin.json 각 스킬에 존재
- [ ] SKILL.md frontmatter 유효

### 6.2 내용 검증

- [ ] Voice/Tense 비율이 분석 결과와 일치
- [ ] 예시가 실제 논문에서 추출됨
- [ ] 패턴이 구체적이고 실행 가능

---

## 7. 메타데이터

```yaml
version: "1.1.0"
template_engine: "jinja2"
skills_generated: 10
output_structure:
  - marketplace.json
  - 10 skill folders (including orchestrator)
  - README.md
validation:
  - json_validity
  - frontmatter_validity
  - content_completeness
```
