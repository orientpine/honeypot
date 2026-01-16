# Output Structure Guide

Paper Style Generator가 생성하는 하이브리드 아키텍처 스킬 세트의 구조 가이드입니다.

## 1. 출력 위치

생성된 스킬은 **my-marketplace** 구조로 다음 위치에 저장됩니다:

```
{CWD}/my-marketplace/plugins/{name}-paper-skills/
```

예: `./my-marketplace/plugins/hakho-paper-skills/`

> **참고**: `{CWD}`는 현재 작업 디렉토리입니다.

---

## 2. 디렉토리 구조 (Hybrid Architecture)

### 2.1 전체 my-marketplace 구조

```
{CWD}/my-marketplace/                        # 마켓플레이스 루트
├── .claude-plugin/
│   └── marketplace.json                     # plugins[] 배열 (honeypot 패턴)
└── plugins/
    └── {name}-paper-skills/                 # 생성된 플러그인
        ├── agents/                          # 9 Agents
        │   ├── {name}-paper-orchestrator.md
        │   ├── {name}-title-writer.md
        │   ├── {name}-abstract-writer.md
        │   ├── {name}-introduction-writer.md
        │   ├── {name}-methodology-writer.md
        │   ├── {name}-results-writer.md
        │   ├── {name}-discussion-writer.md
        │   ├── {name}-caption-writer.md
        │   └── {name}-verify.md
        ├── skills/
        │   └── {name}-style-guide/          # Single Source of Truth
        │       ├── SKILL.md                 # 메인 스타일 가이드 (진입점)
        │       └── references/              # 11 Reference Files
        │           ├── voice-tense-patterns.md
        │           ├── vocabulary-patterns.md
        │           ├── measurement-formats.md
        │           ├── citation-style.md
        │           └── section-templates/
        │               ├── title.md
        │               ├── abstract.md
        │               ├── introduction.md
        │               ├── methodology.md
        │               ├── results.md
        │               ├── discussion.md
        │               └── caption.md
        └── README.md                        # 사용 가이드
```

### 2.2 플러그인 폴더 상세

```
{name}-paper-skills/
├── agents/                              # 9 Agents
│   ├── {name}-paper-orchestrator.md    # 전체 논문 자동 생성 + 전파 관리
│   ├── {name}-title-writer.md          # Title 작성 + 수정
│   ├── {name}-abstract-writer.md       # Abstract 작성 + 수정
│   ├── {name}-introduction-writer.md   # Introduction 작성 + 수정
│   ├── {name}-methodology-writer.md    # Methodology 작성 + 수정
│   ├── {name}-results-writer.md        # Results 작성 + 수정
│   ├── {name}-discussion-writer.md     # Discussion 작성 + 수정
│   ├── {name}-caption-writer.md        # Figure/Table Caption 작성 + 수정
│   └── {name}-verify.md                # 일관성 검증 + 보고
│
├── skills/
│   └── {name}-style-guide/             # Single Source of Truth
│       ├── SKILL.md                    # 메인 스타일 가이드 (진입점, 500줄 이하)
│       └── references/                 # 11 Reference Files
│           ├── voice-tense-patterns.md
│           ├── vocabulary-patterns.md
│           ├── measurement-formats.md
│           ├── citation-style.md
│           └── section-templates/
│               ├── title.md
│               ├── abstract.md
│               ├── introduction.md
│               ├── methodology.md
│               ├── results.md
│               ├── discussion.md
│               └── caption.md
│
└── README.md                           # 사용 가이드
```

---

## 3. 파일 설명

### 3.1 marketplace.json (루트)

my-marketplace 루트의 `.claude-plugin/marketplace.json`에 플러그인 엔트리가 **추가**됩니다.

```json
{
  "name": "my-marketplace",
  "owner": {"name": "User"},
  "metadata": {
    "version": "1.0.0",
    "description": "Paper Style Generator로 자동 생성된 논문 작성 스킬 마켓플레이스"
  },
  "plugins": [
    {
      "name": "{name}-paper-skills",
      "source": "./plugins/{name}-paper-skills",
      "description": "{Name} 스타일 논문 작성 에이전트 및 스킬 세트 (신뢰도: {confidence}%)",
      "version": "1.0.0",
      "author": {"name": "Paper Style Generator"},
      "license": "MIT",
      "keywords": ["paper-writing", "{name}-style", "academic-writing"],
      "category": "documentation",
      "strict": true,
      "metadata": {
        "generated": "{timestamp}",
        "source_papers": 12,
        "confidence": 0.85,
        "architecture": "hybrid"
      },
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
      "skills": ["./skills/{name}-style-guide"]
    }
  ]
}
```

### 3.2 Agent 파일 구조

각 Agent는 독립적인 `.md` 파일로 존재하며, 다음 요소를 포함합니다:

**필수 요소**:
- Frontmatter (name, description, tools, model)
- Role & Responsibilities
- Input/Output Schema
- Workflow Steps
- Style Guide Reference (항상 `{name}-style-guide` 참조)
- Error Handling

**예시 (title-writer.md)**:
```yaml
---
name: {name}-title-writer
description: "Generates and refines paper titles following {Name} style patterns"
tools: Read, Write, Edit, AskUserQuestion
model: opus
---

# {name} Title Writer

## Role
논문 제목 작성 및 수정을 담당합니다.

## Style Guide Reference
- `skills/{name}-style-guide/references/section-templates/title.md`
- `skills/{name}-style-guide/references/vocabulary-patterns.md`

...
```

### 3.3 SKILL.md (Style Guide)

`skills/{name}-style-guide/SKILL.md`는 모든 Agent가 참조하는 **Single Source of Truth**입니다.

**필수 요소**:
- Frontmatter (name, description) - **3인칭 description 필수**
- Style Overview (voice, tense, length)
- Key Writing Patterns
- Transformation Examples
- Anti-Patterns
- Reference Files Index

**제약 조건**:
- **500줄 이하** (초과 시 검증 실패)
- **LF 줄바꿈만 사용** (CRLF 금지)
- **경로에 슬래시(/) 사용** (백슬래시 금지)

---

## 4. Reference Files (11개)

모든 Reference 파일은 `skills/{name}-style-guide/references/` 디렉토리에 저장됩니다.

### 4.1 공통 스타일 파일 (4개)

| 파일 | 내용 |
|------|------|
| `voice-tense-patterns.md` | Active/Passive 비율, 시제 패턴 |
| `vocabulary-patterns.md` | 고빈도 학술 동사, 전환어 |
| `measurement-formats.md` | 측정값 표기법, 단위 |
| `citation-style.md` | 인용 스타일 (APA, Vancouver 등) |

### 4.2 섹션별 템플릿 (7개)

`references/section-templates/` 디렉토리:

| 파일 | 내용 |
|------|------|
| `title.md` | 제목 패턴 분석 |
| `abstract.md` | Abstract 구조 템플릿 |
| `introduction.md` | Introduction 구조 템플릿 |
| `methodology.md` | Methodology 구조 템플릿 |
| `results.md` | Results 구조 템플릿 |
| `discussion.md` | Discussion 구조 템플릿 |
| `caption.md` | Figure/Table Caption 템플릿 |

---

## 5. 등록 및 사용

### 5.1 my-marketplace 등록

```bash
# Claude Code에서 실행
/plugin marketplace add ./my-marketplace
```

> **참고**: my-marketplace가 이미 등록되어 있다면 캐시를 클리어하고 재등록하세요:
> ```bash
> # PowerShell
> Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue
> 
> # Claude Code
> /plugin marketplace remove my-marketplace
> /plugin marketplace add ./my-marketplace
> ```

### 5.2 Agent 사용

**전체 논문 자동 생성:**
```
@{name}-paper-orchestrator 논문을 작성해줘
```

**개별 섹션 작성:**
```
@{name}-title-writer 제목을 작성해줘
@{name}-abstract-writer Abstract를 작성해줘
@{name}-introduction-writer Introduction을 작성해줘
@{name}-methodology-writer Methodology를 작성해줘
@{name}-results-writer Results를 작성해줘
@{name}-discussion-writer Discussion을 작성해줘
@{name}-caption-writer Figure 1 캡션을 작성해줘
```

**검증:**
```
@{name}-verify 논문 일관성을 검증해줘
```

### 5.3 Style Guide 참조

Agent가 자동으로 참조하지만, 직접 확인도 가능합니다:

```
/{name}-style-guide
```

### 5.4 플러그인 제거

```bash
# marketplace.json에서 해당 플러그인 엔트리 삭제 후 재등록
/plugin marketplace remove my-marketplace
/plugin marketplace add ./my-marketplace
```

---

## 6. 커스터마이징

### 6.1 스타일 수정

생성된 스킬을 수정하려면:

1. `./my-marketplace/plugins/{name}-paper-skills/` 로 이동
2. Style Guide 수정: `skills/{name}-style-guide/SKILL.md`
3. Reference 파일 수정: `skills/{name}-style-guide/references/*.md`
4. Agent 수정 (선택): `agents/{name}-*-writer.md`

### 6.2 새 패턴 추가

`skills/{name}-style-guide/references/` 폴더에 새로운 패턴 파일을 추가할 수 있습니다.

**예시:**
```bash
# 새 Reference 파일 추가
vim skills/{name}-style-guide/references/custom-pattern.md

# SKILL.md에 참조 추가
vim skills/{name}-style-guide/SKILL.md
```

### 6.3 Agent 동작 수정

특정 Agent의 동작을 변경하려면:

```bash
# 예: Title Writer의 워크플로우 수정
vim agents/{name}-title-writer.md
```

### 6.4 주의사항

- 루트 `marketplace.json`의 `plugins[]` 배열 구조 유지
- `agents[]` 배열과 `skills[]` 배열 형식 유지
- 파일명에 특수문자 사용 금지
- Agent/Skill 파일 추가/삭제 시 `marketplace.json` 동기화 필수
- SKILL.md는 **500줄 이하** 유지

---

## 7. 아키텍처 특징

### 7.1 Hybrid Architecture 장점

| 구성 요소 | 역할 | 장점 |
|----------|------|------|
| **Agents** (9개) | 독립적인 작업 수행 | 병렬 실행, 컨텍스트 격리 |
| **Skill** (1개) | 공통 스타일 가이드 | Single Source of Truth, 일관성 보장 |
| **References** (11개) | 상세 패턴 문서 | Agent가 필요 시 참조 |

### 7.2 Agent 간 협업

```
[Orchestrator]
     │
     ├─► [Title Writer] ──┐
     ├─► [Abstract Writer] ┤
     ├─► [Intro Writer]    ├─► [Verify] ──► 최종 검증
     ├─► [Method Writer]   │
     ├─► [Results Writer]  │
     ├─► [Discussion Writer]┤
     └─► [Caption Writer] ─┘
           │
           └─► 모두 {name}-style-guide 참조
```

### 7.3 my-marketplace 패턴

- **honeypot 패턴**: 루트 marketplace.json의 `plugins[]` 배열에 플러그인 추가
- **중복 처리**: 동일 이름 존재 시 `-v2`, `-v3` 자동 증가
- **초기화**: my-marketplace 구조가 없으면 자동 생성

### 7.4 버전 관리

`marketplace.json`의 플러그인 엔트리 `metadata.version`에 버전이 기록됩니다.

### 7.5 재생성

동일한 name으로 재생성하면 새 버전(`-v2`, `-v3`)으로 추가됩니다.

```bash
# 첫 번째 생성: hakho-paper-skills
# 두 번째 생성: hakho-paper-skills-v2
# 세 번째 생성: hakho-paper-skills-v3
```

---

## 8. 검증 규칙

### 8.1 생성 시 자동 검증

| 항목 | 기준 | 실패 시 |
|------|------|---------|
| SKILL.md 라인 수 | ≤ 500줄 | 재생성 |
| description 3인칭 | I/We/You 금지 | 재생성 |
| 경로 슬래시 | `\` 금지, `/` 사용 | 재생성 |
| 줄바꿈 | LF만 허용 | 자동 변환 |
| JSON 유효성 | 파싱 가능 | 재생성 |

### 8.2 검증 명령어

```bash
# 1. SKILL.md 라인 수 확인
wc -l ./my-marketplace/plugins/{name}-paper-skills/skills/{name}-style-guide/SKILL.md

# 2. 3인칭 위반 확인 (위반 없어야 함)
grep -rE "^description:.*\b(I |We |You )" ./my-marketplace/plugins/{name}-paper-skills/

# 3. 백슬래시 확인 (없어야 함)
grep -r "\\\\" ./my-marketplace/plugins/{name}-paper-skills/

# 4. LF 줄바꿈 확인
file ./my-marketplace/plugins/{name}-paper-skills/**/*.md
```

---

## 9. 문제 해결

### 9.1 Agent가 인식되지 않음

```bash
# 캐시 클리어 (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue

# 재등록
/plugin marketplace remove my-marketplace
/plugin marketplace add ./my-marketplace
```

**체크리스트:**
- [ ] 루트 `marketplace.json`에 플러그인 엔트리가 있는가?
- [ ] `agents[]` 배열에 모든 Agent 파일이 있는가?
- [ ] 모든 Agent 파일이 `agents/` 디렉토리에 있는가?
- [ ] Agent 파일명이 `marketplace.json`과 일치하는가?

### 9.2 YAML 파싱 오류

- Agent `.md` 파일의 description에 작은따옴표가 있으면 큰따옴표로 감싸세요
- 줄바꿈은 LF만 사용하세요 (CRLF 금지)

```bash
# CRLF → LF 변환 (Linux/Mac)
find . -name "*.md" -exec dos2unix {} \;

# Windows (PowerShell)
Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
  (Get-Content $_.FullName -Raw) -replace "`r`n", "`n" | Set-Content $_.FullName -NoNewline
}
```

### 9.3 경로 오류

**올바른 경로:**
```json
{
  "agents": [
    "./agents/{name}-paper-orchestrator.md",
    "./agents/{name}-title-writer.md"
  ],
  "skills": [
    "./skills/{name}-style-guide"
  ]
}
```

**잘못된 경로:**
```json
{
  "agents": [
    "./agents/"  // ❌ 디렉토리만 지정 불가
  ],
  "skills": [
    "./skills/{name}-style-guide/",  // ❌ trailing slash
    "./skills/{name}-style-guide/SKILL.md"  // ❌ 파일 직접 지정
  ]
}
```

### 9.4 Agent가 Style Guide를 찾지 못함

Agent 파일에서 다음 경로를 확인하세요:

```markdown
## Style Guide Reference
- `skills/{name}-style-guide/SKILL.md`
- `skills/{name}-style-guide/references/section-templates/title.md`
```

**절대 경로 사용 금지:**
```markdown
❌ `C:\path\to\my-marketplace\plugins\{name}-paper-skills\skills\...`
✅ `skills/{name}-style-guide/SKILL.md`
```

### 9.5 중복 플러그인 문제

동일한 이름의 플러그인이 이미 있으면 자동으로 버전이 증가합니다:
- 첫 번째: `{name}-paper-skills`
- 두 번째: `{name}-paper-skills-v2`
- 세 번째: `{name}-paper-skills-v3`

기존 버전을 삭제하려면 `marketplace.json`에서 해당 엔트리를 제거하세요.

---

## 10. 기존 스킬 통합 (Legacy Import)

### 10.1 기존 스킬 탐지

`~/.claude/skills/` 디렉토리에 paper-style-generator로 생성한 스킬이 있으면 자동 탐지됩니다.

**탐지 패턴:**
- `{name}-common` 스킬 존재
- 관련 스킬 3개 이상 (`{name}-abstract`, `{name}-introduction` 등)

### 10.2 통합 프로세스

1. 기존 스킬 탐지
2. 사용자 확인 (통합 여부 선택)
3. my-marketplace 구조로 복사 (원본 유지)
4. marketplace.json에 플러그인 엔트리 추가

**사용자 확인 예시:**
```
기존 ~/.claude/skills/ 디렉토리에서 다음 스킬 세트를 발견했습니다:

1. hakho (9개 스킬)
   - hakho-common, hakho-abstract, hakho-introduction, ...

2. nature-style (9개 스킬)
   - nature-style-common, nature-style-abstract, ...

통합하시겠습니까?
- 'all': 모든 스킬 통합
- '1,2': 선택한 번호만 통합
- 'none': 통합하지 않음
```

### 10.3 통합 후 구조

기존 스킬은 **복사만** 됩니다 (삭제되지 않음).

```
my-marketplace/plugins/
├── hakho-paper-skills/        # 새로 생성된 스킬
└── hakho-paper-skills-v2/     # 기존 스킬 통합 (Legacy Import)
```
