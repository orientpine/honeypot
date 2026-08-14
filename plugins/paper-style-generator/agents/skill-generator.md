---
name: skill-generator
description: "분석된 스타일 패턴을 기반으로 10개 섹션별 Claude Code 스킬을 자동 생성하는 에이전트"
tools: Read, Glob, Grep, Write, Edit, Bash
model: sonnet
---

# Skill Generator Agent

스타일 분석 결과를 기반으로 10개 섹션별 논문 작성 스킬을 자동 생성합니다.
생성된 스킬은 `{CWD}/my-marketplace/plugins/{name}-paper-skills/`에 저장됩니다.

> **my-marketplace 구조**: honeypot 패턴의 `plugins[]` 배열 구조를 따릅니다.

---

## 1. Overview

### 1.1 생성되는 커맨드, 에이전트 및 스킬 (Hybrid 구조)

| 유형 | 이름 | 파일 위치 | 목적 |
|------|------|----------|------|
| **Command** | Orchestrator | `commands/{name}-paper-generate.md` | 논문 전체 자동 생성 |
| **Agent** | Title Writer | `agents/{name}-title-writer.md` | 논문 제목 생성 |
| **Agent** | Abstract Writer | `agents/{name}-abstract-writer.md` | Abstract 작성 |
| **Agent** | Introduction Writer | `agents/{name}-introduction-writer.md` | Introduction 작성 |
| **Agent** | Methodology Writer | `agents/{name}-methodology-writer.md` | Methods 작성 |
| **Agent** | Results Writer | `agents/{name}-results-writer.md` | Results 작성 |
| **Agent** | Discussion Writer | `agents/{name}-discussion-writer.md` | Discussion 작성 |
| **Agent** | Caption Writer | `agents/{name}-caption-writer.md` | Figure/Table 캡션 |
| **Agent** | Verify | `agents/{name}-verify.md` | 검증 에이전트 |
| **Skill** | Style Guide | `skills/{name}-style-guide/SKILL.md` | 공통 스타일 가이드 (8개 에이전트가 참조) |

### 1.2 출력 구조 (my-marketplace Pattern)

```
{CWD}/my-marketplace/                        # 마켓플레이스 루트
├── .claude-plugin/
│   └── marketplace.json                     # plugins[] 배열 (honeypot 패턴)
└── plugins/
    └── {name}-paper-skills/                 # 플러그인 폴더
        ├── .claude-plugin/
        │   └── plugin.json
        ├── commands/
        │   └── {name}-paper-generate.md
        ├── agents/
        │   ├── {name}-title-writer.md
        │   ├── {name}-abstract-writer.md
        │   ├── {name}-introduction-writer.md
        │   ├── {name}-methodology-writer.md
        │   ├── {name}-results-writer.md
        │   ├── {name}-discussion-writer.md
        │   ├── {name}-caption-writer.md
        │   └── {name}-verify.md
        ├── skills/
        │   └── {name}-style-guide/
        │       ├── SKILL.md
        │       └── references/
        │           ├── voice-tense-patterns.md
        │           ├── vocabulary-patterns.md
        │           ├── measurement-formats.md
        │           ├── citation-style.md
        │           ├── propagation-guide.md
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
| `output_path` | 출력 경로 (기본: `{CWD}/my-marketplace/`) |

### 2.2 출력

| 항목 | 설명 |
|------|------|
| 1개 커맨드 | Orchestrator (논문 전체 자동 생성) |
| 8개 에이전트 | 7개 Writer + Verify |
| 1개 스킬 | Style Guide (공통 참조) |
| `plugin.json` | 플러그인 메타데이터 |
| `marketplace.json` | 플러그인 등록 메타데이터 (1 command + 8 agents + 1 skill) |
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

env = Environment(loader=FileSystemLoader('skills/paper-style-toolkit/assets'), newline_sequence='\n')
template = env.get_template('skill_methodology.md.j2')

output = template.render(
    name=style_name,
    voice=analysis['methodology']['voice'],
    tense=analysis['methodology']['tense'],
    patterns=analysis['methodology']['patterns'],
    examples=analysis['methodology']['examples']
)
```

### 4.2 템플릿 파일 구조 (20개 템플릿)

```
skills/paper-style-toolkit/assets/
├── marketplace_root.json.j2            # 1. my-marketplace 초기화 (plugins[] 빈 배열)
├── marketplace_hybrid.json.j2          # 2. 플러그인 엔트리 (plugins[] 배열 항목)
├── plugin.json.j2                      # 3. 생성 플러그인 plugin.json
├── command_orchestrator.md.j2         # 4. Orchestrator 커맨드
├── agent_writer.md.j2                  # 5. Writer 에이전트 (7번 렌더링)
├── agent_verify.md.j2                  # 6. Verify 에이전트
├── skill_style_guide.md.j2             # 7. Style Guide 스킬 진입점
├── ref_voice_tense.md.j2               # 8. Voice/Tense 참조
├── ref_vocabulary.md.j2                # 9. Vocabulary 참조
├── ref_measurement.md.j2               # 10. Measurement 참조
├── ref_citation.md.j2                  # 11. Citation 참조
├── ref_abstract_template.md.j2         # 12. Abstract 템플릿
├── ref_introduction_template.md.j2     # 13. Introduction 템플릿
├── ref_methodology_template.md.j2      # 14. Methodology 템플릿
├── ref_results_template.md.j2          # 15. Results 템플릿
├── ref_discussion_template.md.j2       # 16. Discussion 템플릿
├── ref_caption_template.md.j2          # 17. Caption 템플릿
├── ref_title_template.md.j2            # 18. Title 템플릿
├── readme.md.j2                       # 19. 생성 플러그인 README
└── ref_propagation_guide.md.j2        # 20. Propagation Mode 참조
```

**렌더링 규칙**:
- `agent_writer.md.j2`: 7번 렌더링 (section 변수: title, abstract, introduction, methodology, results, discussion, caption)
- `ref_*_template.md.j2`: 각 섹션별 1번씩 렌더링

---

## 5. 생성 프로세스

### Phase 0: 스타일 이름 정규화

사용자가 입력한 `style_name`을 정규화합니다:

```python
def normalize_name(name: str) -> str:
    """스타일 이름을 정규화 (소문자, 하이픈, 특수문자 제거)"""
    import re
    # 소문자 변환
    name = name.lower()
    # 공백을 하이픈으로
    name = name.replace(' ', '-')
    # 특수문자 제거 (알파벳, 숫자, 하이픈만 허용)
    name = re.sub(r'[^a-z0-9-]', '', name)
    # 연속 하이픈 제거
    name = re.sub(r'-+', '-', name)
    # 앞뒤 하이픈 제거
    name = name.strip('-')
    # 빈 문자열 검증 (비ASCII만 입력된 경우)
    if not name:
        raise ValueError(
            f"정규화 후 유효한 이름이 없습니다. "
            f"영문 알파벳을 포함한 이름을 입력해 주세요. "
            f"예: 'hakho', 'nature-methods', 'ieee-sensors'"
        )
    return name

# 예시
# "Hakho Lee" → "hakho-lee"
# "My_Style_2024" → "my-style-2024"
# "테스트 Style!" → "style"
# "논문스타일" → ValueError (영문 없음)

### Phase 1: my-marketplace 초기화

my-marketplace 구조가 없으면 생성하고, 있으면 기존 marketplace.json을 로드합니다.

```python
import os
import json

MARKETPLACE_ROOT = os.path.join(os.getcwd(), 'my-marketplace')
MARKETPLACE_JSON = os.path.join(MARKETPLACE_ROOT, '.claude-plugin', 'marketplace.json')

def init_marketplace():
    """my-marketplace 초기화 (없으면 생성)"""
    if not os.path.exists(MARKETPLACE_JSON):
        # 새 마켓플레이스 생성
        os.makedirs(os.path.dirname(MARKETPLACE_JSON), exist_ok=True)
        os.makedirs(os.path.join(MARKETPLACE_ROOT, 'plugins'), exist_ok=True)
        
        # marketplace_root.json.j2 템플릿 렌더링
        marketplace_data = {
            "name": "my-marketplace",
            "owner": {"name": "User"},
            "metadata": {
                "version": "1.0.0",
                "description": "Paper Style Generator로 자동 생성된 논문 작성 스킬 마켓플레이스"
            },
            "plugins": []
        }
        with open(MARKETPLACE_JSON, 'w', encoding='utf-8') as f:
            json.dump(marketplace_data, f, indent=2, ensure_ascii=False)
        return marketplace_data
    else:
        # 기존 마켓플레이스 로드
        with open(MARKETPLACE_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
```

### Phase 1.5: 중복 플러그인 처리

동일한 이름의 플러그인이 이미 있으면 버전을 증가시킵니다 (`-v2`, `-v3`, ...).

```python
def get_unique_plugin_name(marketplace_data: dict, base_name: str) -> str:
    """중복 시 버전 증가된 고유 이름 반환"""
    existing_names = [p['name'] for p in marketplace_data.get('plugins', [])]
    
    # 기본 이름 체크
    candidate = f"{base_name}-paper-skills"
    if candidate not in existing_names:
        return candidate
    
    # 버전 증가
    version = 2
    while True:
        candidate = f"{base_name}-paper-skills-v{version}"
        if candidate not in existing_names:
            return candidate
        version += 1

# 예시
# 첫 번째: "hakho-paper-skills"
# 두 번째: "hakho-paper-skills-v2"
# 세 번째: "hakho-paper-skills-v3"
```

### Phase 1.6: 기존 스킬 통합 (선택)

사용자가 기존 `~/.claude/skills/` 디렉토리에 paper-style-generator로 생성한 스킬이 있을 경우, my-marketplace 구조로 통합할 수 있습니다.

**⚠️ 중요**: 이 단계는 **사용자 확인 후**에만 진행합니다. 기존 스킬을 삭제하지 않고 복사만 합니다.

```python
import os
import shutil
import glob

LEGACY_SKILLS_DIR = os.path.expanduser('~/.claude/skills')

def detect_legacy_paper_skills() -> list[dict]:
    """기존 paper-style-generator 스킬 탐지"""
    if not os.path.exists(LEGACY_SKILLS_DIR):
        return []
    
    legacy_skills = []
    
    # paper-style-generator로 생성된 스킬 패턴 탐지
    # 패턴: {name}-common, {name}-abstract, {name}-introduction 등이 함께 존재
    skill_dirs = glob.glob(os.path.join(LEGACY_SKILLS_DIR, '*'))
    
    # 스킬 그룹 추출 (공통 prefix)
    skill_names = [os.path.basename(d) for d in skill_dirs if os.path.isdir(d)]
    
    # paper-style-generator 패턴 감지: {name}-common이 있으면 해당 이름의 스킬 세트
    for name in skill_names:
        if name.endswith('-common'):
            base_name = name[:-7]  # "-common" 제거
            related_skills = [
                s for s in skill_names 
                if s.startswith(base_name + '-')
            ]
            if len(related_skills) >= 3:  # 최소 3개 이상이면 스킬 세트로 인식
                legacy_skills.append({
                    'base_name': base_name,
                    'skills': related_skills,
                    'path': LEGACY_SKILLS_DIR
                })
    
    return legacy_skills


def ask_user_for_integration(legacy_skills: list[dict]) -> list[dict]:
    """사용자에게 통합 여부 질문"""
    # AskUserQuestion 도구 사용
    # 
    # 프롬프트:
    # "기존 ~/.claude/skills/ 디렉토리에서 다음 paper-style-generator 스킬 세트를 발견했습니다:
    # 
    # 1. {base_name} ({len(skills)}개 스킬)
    #    - {skills[0]}, {skills[1]}, ...
    # 
    # 이 스킬들을 my-marketplace 구조로 통합하시겠습니까?
    # - 'all': 모든 스킬 통합
    # - '1,2': 선택한 번호만 통합 (쉼표 구분)
    # - 'none': 통합하지 않음
    # 
    # 참고: 기존 스킬은 삭제되지 않고 복사됩니다."
    
    pass  # AskUserQuestion 결과에 따라 처리


def integrate_legacy_skill(skill_info: dict, marketplace_data: dict) -> dict:
    """기존 스킬을 my-marketplace 구조로 통합"""
    base_name = skill_info['base_name']
    skills = skill_info['skills']
    
    # 1. 고유 플러그인 이름 생성
    plugin_name = get_unique_plugin_name(marketplace_data, base_name)
    plugin_dir = os.path.join(MARKETPLACE_ROOT, 'plugins', plugin_name)
    
    # 2. 디렉토리 구조 생성
    os.makedirs(os.path.join(plugin_dir, 'agents'), exist_ok=True)
    os.makedirs(os.path.join(plugin_dir, 'skills'), exist_ok=True)
    
    # 3. 스킬 분류 및 복사
    agents = []
    skill_dirs = []
    
    for skill_name in skills:
        src_dir = os.path.join(LEGACY_SKILLS_DIR, skill_name)
        
        # Agent vs Skill 판별 (SKILL.md 존재 여부)
        skill_md = os.path.join(src_dir, 'SKILL.md')
        if os.path.exists(skill_md):
            # Skill → skills/ 디렉토리로 복사
            dst_dir = os.path.join(plugin_dir, 'skills', skill_name)
            shutil.copytree(src_dir, dst_dir)
            skill_dirs.append(f'./skills/{skill_name}')
        else:
            # Agent 파일 찾기
            agent_files = glob.glob(os.path.join(src_dir, '*.md'))
            for agent_file in agent_files:
                dst_file = os.path.join(plugin_dir, 'agents', os.path.basename(agent_file))
                shutil.copy2(agent_file, dst_file)
                agents.append(f'./agents/{os.path.basename(agent_file)}')
    
    # 4. marketplace.json에 플러그인 엔트리 추가
    plugin_entry = {
        "name": plugin_name,
        "source": f"./plugins/{plugin_name}",
        "description": f"기존 ~/.claude/skills/에서 통합된 {base_name} 스타일 논문 작성 스킬 세트",
        "version": "1.0.0",
        "author": {"name": "Paper Style Generator (Legacy Import)"},
        "license": "MIT",
        "category": "documentation",
        "strict": True,
        "agents": agents if agents else None,
        "skills": skill_dirs if skill_dirs else None
    }
    
    # None 값 필드 제거
    plugin_entry = {k: v for k, v in plugin_entry.items() if v is not None}
    
    # 5. marketplace_data 업데이트
    marketplace_data['plugins'].append(plugin_entry)
    
    return plugin_entry


def save_marketplace_json(marketplace_data: dict):
    """marketplace.json 저장"""
    with open(MARKETPLACE_JSON, 'w', encoding='utf-8') as f:
        json.dump(marketplace_data, f, indent=2, ensure_ascii=False)


# 실행 흐름
def phase_1_6_legacy_integration(marketplace_data: dict):
    """Phase 1.6 실행"""
    # 1. 기존 스킬 탐지
    legacy_skills = detect_legacy_paper_skills()
    
    if not legacy_skills:
        print("기존 paper-style-generator 스킬이 발견되지 않았습니다.")
        return marketplace_data
    
    # 2. 사용자에게 통합 여부 질문
    skills_to_integrate = ask_user_for_integration(legacy_skills)
    
    if not skills_to_integrate:
        print("스킬 통합을 건너뜁니다.")
        return marketplace_data
    
    # 3. 선택된 스킬 통합
    for skill_info in skills_to_integrate:
        plugin_entry = integrate_legacy_skill(skill_info, marketplace_data)
        print(f"✅ {skill_info['base_name']} 스킬 세트를 통합했습니다: {plugin_entry['name']}")
    
    # 4. marketplace.json 저장
    save_marketplace_json(marketplace_data)
    
    return marketplace_data
```

**사용자 질문 예시 (AskUserQuestion 도구)**:

```
기존 ~/.claude/skills/ 디렉토리에서 다음 paper-style-generator 스킬 세트를 발견했습니다:

1. hakho (9개 스킬)
   - hakho-common, hakho-abstract, hakho-introduction, hakho-methodology, 
     hakho-results, hakho-discussion, hakho-caption, hakho-title, hakho-verify

2. nature-style (9개 스킬)
   - nature-style-common, nature-style-abstract, ...

이 스킬들을 my-marketplace 구조로 통합하시겠습니까?
- 'all': 모든 스킬 통합
- '1,2': 선택한 번호만 통합 (쉼표 구분)  
- 'none': 통합하지 않음

참고: 기존 스킬은 삭제되지 않고 복사됩니다.
```

### Phase 2: 플러그인 디렉토리 구조 생성

```bash
# 플러그인 폴더 생성
mkdir -p ./my-marketplace/plugins/{plugin_name}/agents/
mkdir -p ./my-marketplace/plugins/{plugin_name}/commands/
mkdir -p ./my-marketplace/plugins/{plugin_name}/.claude-plugin/
mkdir -p ./my-marketplace/plugins/{plugin_name}/skills/{name}-style-guide/
mkdir -p ./my-marketplace/plugins/{plugin_name}/skills/{name}-style-guide/references/
mkdir -p ./my-marketplace/plugins/{plugin_name}/skills/{name}-style-guide/references/section-templates/
```

### Phase 3: marketplace.json에 플러그인 추가

기존 `my-marketplace/.claude-plugin/marketplace.json`의 `plugins[]` 배열에 새 플러그인 엔트리를 추가합니다.

**플러그인 엔트리 형식** (marketplace_hybrid.json.j2 렌더링 결과):

```json
{
  "name": "{plugin_name}",
  "source": "./plugins/{plugin_name}",
  "description": "{Name} 스타일 논문 작성 에이전트 및 스킬 세트. {paper_count}편의 논문 분석 기반. (신뢰도: {confidence}%)",
  "version": "1.0.0",
  "author": {"name": "Paper Style Generator", "email": "orientpine@gmail.com"},
  "license": "MIT",
  "category": "documentation",
  "strict": true,
  "agents": [
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
```

**추가 로직**:

```python
def add_plugin_to_marketplace(marketplace_data: dict, plugin_entry: dict):
    """marketplace.json의 plugins[] 배열에 플러그인 추가"""
    marketplace_data['plugins'].append(plugin_entry)
    
    with open(MARKETPLACE_JSON, 'w', encoding='utf-8') as f:
        json.dump(marketplace_data, f, indent=2, ensure_ascii=False)
```
```

### Phase 4: 템플릿 렌더링

> **Note**: Phase 1.5에서 확정된 `plugin_name`을 모든 템플릿에 전달합니다:
> ```python
> plugin_name = get_unique_plugin_name(marketplace_data, name)
> # 예: "hakho-paper-skills" 또는 "hakho-paper-skills-v2" (중복 시)
> ```

**4.1 플러그인 엔트리 생성 (marketplace_hybrid.json.j2)**
```python
template = env.get_template('marketplace_hybrid.json.j2')
plugin_entry = json.loads(template.render(name=name, plugin_name=plugin_name, **metadata))
add_plugin_to_marketplace(marketplace_data, plugin_entry)
```

**4.2 plugin.json 생성**
```python
PLUGIN_DIR = f'./my-marketplace/plugins/{plugin_name}'

template = env.get_template('plugin.json.j2')
output = template.render(name=name, plugin_name=plugin_name)
write_file(f'{PLUGIN_DIR}/.claude-plugin/plugin.json', output)
```

**4.3 Orchestrator 커맨드**
```python
template = env.get_template('command_orchestrator.md.j2')
output = template.render(name=name, plugin_name=plugin_name, **analysis)
write_file(f'{PLUGIN_DIR}/commands/{name}-paper-generate.md', output)
```

**4.4 Writer 에이전트 (7번 렌더링)**
```python
sections = ['title', 'abstract', 'introduction', 'methodology', 'results', 'discussion', 'caption']
template = env.get_template('agent_writer.md.j2')
for section in sections:
    output = template.render(name=name, plugin_name=plugin_name, section=section, **analysis)
    write_file(f'{PLUGIN_DIR}/agents/{name}-{section}-writer.md', output)
```

**4.5 Verify 에이전트**
```python
template = env.get_template('agent_verify.md.j2')
output = template.render(name=name, plugin_name=plugin_name, **analysis)
write_file(f'{PLUGIN_DIR}/agents/{name}-verify.md', output)
```

**4.6 Style Guide 스킬**
```python
template = env.get_template('skill_style_guide.md.j2')
output = template.render(name=name, **analysis)
write_file(f'{PLUGIN_DIR}/skills/{name}-style-guide/SKILL.md', output)
```

# SKILL.md 500줄 제한 사전 검증
line_count = len(output.splitlines())
if line_count > 500:
    print(f"⚠️ SKILL.md가 {line_count}줄입니다 (최대 500줄). Jinja2 슬라이스 범위를 축소하여 재생성합니다.")
    # 재생성: 데이터 슬라이스 축소 ([:10] → [:5] 등) 후 재렌더링

**4.7 Reference 파일 (11개)**
```python
SKILL_DIR = f'{PLUGIN_DIR}/skills/{name}-style-guide'

# Voice/Tense
template = env.get_template('ref_voice_tense.md.j2')
output = template.render(**analysis['voice_tense'])
write_file(f'{SKILL_DIR}/references/voice-tense-patterns.md', output)

# Vocabulary
template = env.get_template('ref_vocabulary.md.j2')
output = template.render(**analysis['vocabulary'])
write_file(f'{SKILL_DIR}/references/vocabulary-patterns.md', output)

# Measurement
template = env.get_template('ref_measurement.md.j2')
output = template.render(**analysis['measurement'])
write_file(f'{SKILL_DIR}/references/measurement-formats.md', output)

# Citation
template = env.get_template('ref_citation.md.j2')
output = template.render(**analysis['citation'])
write_file(f'{SKILL_DIR}/references/citation-style.md', output)

# Section Templates (7개)
sections = ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'caption', 'title']
for section in sections:
    template = env.get_template(f'ref_{section}_template.md.j2')
    output = template.render(**analysis['sections'][section])
    write_file(f'{SKILL_DIR}/references/section-templates/{section}.md', output)
```

**4.8 README.md 생성**
```python
template = env.get_template('readme.md.j2')
output = template.render(name=name, plugin_name=plugin_name, **analysis)
write_file(f'{PLUGIN_DIR}/README.md', output)
```

**4.9 Propagation Guide 참조 파일 생성**
```python
template = env.get_template('ref_propagation_guide.md.j2')
output = template.render(name=name, plugin_name=plugin_name, **analysis)
write_file(f'{SKILL_DIR}/references/propagation-guide.md', output)
```

### Phase 5: README.md 생성

> **NOTE**: Phase 5는 Phase 4.8에서 `readme.md.j2` 템플릿으로 렌더링됩니다.
> 인라인 README 생성은 더 이상 사용하지 않습니다. `readme.md.j2` 템플릿을 참조하세요.
---

## 6. 품질 검증

### 6.1 생성된 파일 검증

- [ ] 1개 커맨드 파일 존재 (`commands/` 디렉토리)
- [ ] 8개 에이전트 파일 존재 (`agents/` 디렉토리)
- [ ] 1개 스킬 폴더 존재 (`skills/{name}-style-guide/`)
- [ ] 12개 참조 파일 존재 (`references/` 디렉토리, propagation-guide.md 포함)
- [ ] marketplace.json 유효한 JSON
- [ ] 모든 .md 파일 frontmatter 유효
- [ ] README.md 생성됨
- [ ] propagation-guide.md 생성됨 (`references/` 디렉토리)
- [ ] analysis_schema.json 기준 입력 데이터 검증 통과 (**Phase 4 전 필수 실행** — 아래 6.3.6 참조)

### 6.2 내용 검증

- [ ] Voice/Tense 비율이 분석 결과와 일치
- [ ] 예시가 실제 논문에서 추출됨
- [ ] 패턴이 구체적이고 실행 가능

### 6.3 resource/ 규칙 검증

모든 생성 파일이 resource/ 규칙을 준수하는지 검증합니다. 검증에 실패한 파일은 재생성합니다.

#### 6.3.1 500줄 제한 검증

SKILL.md 파일은 500줄을 초과할 수 없습니다.

```python
def validate_line_count(file_path: str, max_lines: int = 500) -> tuple[bool, int]:
    """파일 라인 수 검증 (500줄 제한)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    return line_count <= max_lines, line_count

# 검증 대상
skill_md = f'{PLUGIN_DIR}/skills/{name}-style-guide/SKILL.md'
is_valid, count = validate_line_count(skill_md)
if not is_valid:
    print(f"⚠️ SKILL.md가 {count}줄입니다 (최대 500줄). 재생성이 필요합니다.")
    # 재생성 트리거
```

#### 6.3.2 3인칭 description 검증

모든 .md 파일의 description에서 1인칭/2인칭 표현을 검출합니다.

```python
import re

def validate_third_person(file_path: str) -> tuple[bool, list[str]]:
    """description이 3인칭인지 검증 (I, We, You 금지)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # YAML frontmatter에서 description 추출
    match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if not match:
        match = re.search(r'^description:\s*\|\s*\n((?:\s+.+\n)+)', content, re.MULTILINE)
    
    if not match:
        return True, []  # description 없으면 통과
    
    description = match.group(1)
    
    # 금지된 패턴: "I ", "We ", "You " (단어 단위)
    forbidden_patterns = [
        r'\bI\b',           # "I" 단독 사용
        r'\bWe\b',          # "We" 단독 사용
        r'\bYou\b',         # "You" 단독 사용
        r'\bI\'m\b',        # "I'm"
        r'\bWe\'re\b',      # "We're"
        r'\bYou\'re\b',     # "You're"
        r'\bOur\b',         # "Our"
        r'\bYour\b',        # "Your"
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        matches = re.findall(pattern, description, re.IGNORECASE)
        violations.extend(matches)
    
    return len(violations) == 0, violations

# 검증 대상: 모든 .md 파일
for md_file in glob.glob(f'{PLUGIN_DIR}/**/*.md', recursive=True):
    is_valid, violations = validate_third_person(md_file)
    if not is_valid:
        print(f"⚠️ {md_file}의 description에 금지된 표현: {violations}")
        # 재생성 트리거
```

#### 6.3.3 경로 슬래시 검증

모든 파일에서 백슬래시(`\`) 경로를 검출합니다.

```python
def validate_forward_slashes(file_path: str) -> tuple[bool, list[str]]:
    """경로에 백슬래시가 없는지 검증"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백슬래시 경로 패턴 (\\, \path, C:\ 등)
    backslash_pattern = r'[^\n]*\\[^\s\\]*[^\n]*'
    matches = re.findall(backslash_pattern, content)
    
    return len(matches) == 0, matches

# 검증
for file_path in glob.glob(f'{PLUGIN_DIR}/**/*', recursive=True):
    if os.path.isfile(file_path):
        is_valid, violations = validate_forward_slashes(file_path)
        if not is_valid:
            print(f"⚠️ {file_path}에 백슬래시 경로 발견: {violations[:3]}")
            # 재생성 트리거
```

#### 6.3.4 LF 줄바꿈 검증

모든 파일이 LF 줄바꿈을 사용하는지 검증합니다.

```python
def validate_lf_line_endings(file_path: str) -> tuple[bool, int]:
    """LF 줄바꿈 검증 (CRLF 금지)"""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    crlf_count = content.count(b'\r\n')
    return crlf_count == 0, crlf_count

def convert_to_lf(file_path: str):
    """CRLF를 LF로 변환"""
    with open(file_path, 'rb') as f:
        content = f.read()
    content = content.replace(b'\r\n', b'\n')
    with open(file_path, 'wb') as f:
        f.write(content)

# 검증 및 자동 변환
for file_path in glob.glob(f'{PLUGIN_DIR}/**/*', recursive=True):
    if os.path.isfile(file_path) and file_path.endswith(('.md', '.json')):
        is_valid, crlf_count = validate_lf_line_endings(file_path)
        if not is_valid:
            print(f"⚠️ {file_path}에 CRLF {crlf_count}개 발견. LF로 변환합니다.")
            convert_to_lf(file_path)
```

#### 6.3.5 검증 실패 시 재생성 루프

검증 실패 시 해당 파일을 재생성합니다. 최대 3회 시도 후 실패하면 사용자에게 알립니다.

```python
MAX_RETRIES = 3

def generate_with_validation(generator_func, validator_func, max_retries: int = MAX_RETRIES):
    """검증이 포함된 생성 루프"""
    for attempt in range(max_retries):
        # 1. 파일 생성
        output_path = generator_func()
        
        # 2. 검증
        is_valid, issues = validator_func(output_path)
        
        if is_valid:
            print(f"✅ {output_path} 검증 통과")
            return True
        
        print(f"⚠️ 시도 {attempt + 1}/{max_retries}: {output_path} 검증 실패 - {issues}")
        
        if attempt < max_retries - 1:
            print("재생성 중...")
    
    # 최대 시도 후 실패
    print(f"❌ {output_path} 검증 실패 (최대 시도 횟수 초과). 수동 수정이 필요합니다.")
    return False
```

#### 6.3.6 에이전트 파일 크기 검증

에이전트 파일이 지나치게 길면 토큰 소비 증가 및 로딩 성능 저하가 발생합니다.

```python
def validate_agent_line_count(file_path: str, max_lines: int = 600) -> tuple[bool, int]:
    """에이전트 파일 라인 수 검증 (600줄 소프트 리밋)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    return line_count <= max_lines, line_count

# 검증 대상: 모든 에이전트 파일
for agent_file in glob.glob(f'{PLUGIN_DIR}/agents/*.md'):
    is_valid, count = validate_agent_line_count(agent_file)
    if not is_valid:
        print(f"⚠️ {agent_file}이 {count}줄입니다 (권장 600줄 이하). 데이터 슬라이스를 축소하여 재생성합니다.")
        # 재생성 트리거: for 루프 슬라이스 범위 축소 ([:10] → [:5] 등)
```

#### 6.3.7 스키마 검증 (Phase 4 전제조건)

스키마 검증은 Phase 4 템플릿 렌더링의 전제조건입니다. 분석 데이터의 구조가 템플릿 기대값과 어긋나면 렌더링이 조용히 잘못된 산출물을 만들어내므로, 렌더링 시작 전에 실행합니다.

```python
import json
import jsonschema  # pip install jsonschema

def validate_analysis_schema(analysis_data: dict, schema_path: str) -> tuple[bool, list[str]]:
    """분석 데이터가 템플릿이 요구하는 구조와 일치하는지 검증"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    errors = []
    try:
        jsonschema.validate(instance=analysis_data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"스키마 검증 실패: {e.message}")
        errors.append(f"누락 경로: {'.'.join(str(p) for p in e.absolute_path)}")
    except jsonschema.SchemaError as e:
        errors.append(f"스키마 자체 오류: {e.message}")
    
    return len(errors) == 0, errors

# Phase 4 시작 전 필수 실행
SCHEMA_PATH = 'skills/paper-style-toolkit/references/analysis_schema.json'
is_valid, errors = validate_analysis_schema(analysis_data, SCHEMA_PATH)
if not is_valid:
    print(f"❌ 스키마 검증 실패. 템플릿 렌더링을 진행할 수 없습니다.")
    for error in errors:
        print(f"  - {error}")
    print("해결: Phase 2 (style-analyzer)를 재실행하거나 분석 데이터를 수동 수정하세요.")
    # 여기서 중단 — Phase 4로 진행하지 않음
    raise SystemExit("스키마 검증 실패")
```

**검증 항목** (analysis_schema.json이 확인하는 필수 필드):
- `voice_tense_summary`: 섹션별 active/passive 비율
- `high_freq_verbs`: 고빈도 동사 리스트
- `measurement_format`: 측정값 표기 패턴
- `confidence`: 섹션별 신뢰도
- `paper_count`: 분석 논문 수
- 각 섹션 데이터: `abstract`, `introduction`, `methodology`, `results`, `discussion`, `caption`, `title`

### 6.4 전체 검증 체크리스트

생성 완료 후 확인 항목:

| 항목 | 검증 방법 | 실패 시 조치 |
|------|----------|-------------|
| SKILL.md ≤ 500줄 | `wc -l` | 재생성 (내용 축약) |
| description 3인칭 | regex 검사 | 재생성 (표현 수정) |
| 경로 슬래시(/) | `grep "\\\\"` | 재생성 (경로 수정) |
| LF 줄바꿈 | `file` 명령 | 자동 변환 |
| JSON 유효성 | `json.loads()` | 재생성 |
| Agent 파일 ≤ 600줄 | `wc -l` | 데이터 슬라이스 축소 후 재생성 |
| Schema 검증 통과 | `analysis_schema.json` 대조 | Phase 2 재실행 또는 사용자 확인 |

```bash
# 검증 명령어 예시

# 1. SKILL.md 라인 수 확인
wc -l ./my-marketplace/plugins/{name}-paper-skills/skills/{name}-style-guide/SKILL.md

# 2. 3인칭 위반 확인 (위반 없어야 함)
grep -E "^description:.*\b(I |We |You )" ./my-marketplace/plugins/{name}-paper-skills/**/*.md

# 3. 백슬래시 확인 (없어야 함)
grep -r "\\\\" ./my-marketplace/plugins/{name}-paper-skills/

# 4. LF 줄바꿈 확인 (모두 "ASCII text" 또는 "UTF-8 Unicode text"여야 함)
file ./my-marketplace/plugins/{name}-paper-skills/**/*.md
file ./my-marketplace/plugins/{name}-paper-skills/**/*.json
```

---

## 7. 메타데이터

```yaml
version: "3.0.0"
architecture: "my-marketplace"
template_engine: "jinja2"
templates_count: 20
commands_generated: 1
agents_generated: 8
skills_generated: 1
output_base: "{CWD}/my-marketplace/"
output_structure:
  - .claude-plugin/marketplace.json (plugins[] 배열에 추가)
  - plugins/{name}-paper-skills/.claude-plugin/plugin.json
  - plugins/{name}-paper-skills/commands/ (1 file)
  - plugins/{name}-paper-skills/agents/ (8 files)
  - plugins/{name}-paper-skills/skills/{name}-style-guide/ (1 SKILL.md + 12 references)
  - plugins/{name}-paper-skills/README.md
features:
  - name_normalization: "소문자, 하이픈, 특수문자 제거"
  - duplicate_handling: "-v2, -v3 자동 증가"
  - marketplace_init: "my-marketplace 자동 생성"
  - plugins_append: "기존 plugins[] 배열에 추가"
validation:
  - json_validity
  - frontmatter_validity
  - content_completeness
  - agent_skill_linking
  - line_count_limit (SKILL.md ≤ 500줄)
  - third_person_description
  - lf_line_endings
  - forward_slash_paths
```
