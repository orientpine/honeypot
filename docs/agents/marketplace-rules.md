# Claude Code Marketplace Rules

> **언제 읽나요**: 플러그인을 추가/수정/삭제하거나, `plugin.json`/`marketplace.json`을 변경하거나, 마켓플레이스 등록이 실패할 때.
> **상위 문서**: [AGENTS.md](../../AGENTS.md)

> **Sources**: [Agent Skills Specification](https://agentskills.io/specification), [wshobson/agents](https://github.com/wshobson/agents) (reference implementation with 73 plugins)

## Plugin Root Directory Structure (CRITICAL)

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

## Three Component Types

### 1. Agents (에이전트)

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

### 2. Commands (커맨드)

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

### 3. Skills (스킬)

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

## Per-Plugin plugin.json

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

## Plugin.json Schema Compliance (CRITICAL)

> **배경 (2026-04-21 실제 사례)**: 4개 플러그인(wiki-gen, pptx-design-styles, patent-trend-analyzer, obsidian-skills)과 root marketplace.json에 **비표준 `contributors` 필드**가 포함되어 Claude Code marketplace 등록이 `"Unrecognized keys"` 검증 에러로 실패했음. Claude Code는 **Zod strict validation**을 사용하므로 공식 스키마에 정의되지 않은 필드는 등록을 거부함.

> **출처**: [공식 Anthropic docs — plugins-reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference), [wshobson/agents](https://github.com/wshobson/agents) 78개 프로덕션 플러그인 전수 조사 결과 `contributors` 사용 0건.

### plugin.json 허용 필드 (OFFICIAL WHITELIST)

**메타데이터:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | 플러그인 식별자 (kebab-case) |
| `version` | string | No | 시맨틱 버전 (SemVer) |
| `description` | string | No | 플러그인 설명 |
| `author` | object\|string | No | `{name, email?, url?}` 또는 문자열 |
| `homepage` | string | No | 문서 URL |
| `repository` | string | No | 소스 코드 URL |
| `license` | string | No | SPDX 라이선스 식별자 |
| `keywords` | array | No | 검색 태그 |

**컴포넌트 경로 (기본 경로 오버라이드 시에만 사용):**
`skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `monitors`, `userConfig`, `channels`, `dependencies`

**위 목록에 없는 모든 필드는 INVALID.**

### 절대 금지 필드 (Zod validation이 `Unrecognized keys` 에러로 거부함)

| Forbidden Field | 이유 | 대체 방안 |
|-----------------|------|-----------|
| `contributor` / `contributors` | 스키마에 없음, 2026-04-21 실제 등록 실패 원인 | README 각주(`[^N]`) 또는 플러그인 README `## Contributors` 섹션 |
| `maintainer` / `maintainers` | 스키마에 없음 | README 각주 |
| `funding` / `sponsor` | 스키마에 없음 | README에 기록 |
| `category` (plugin.json에서) | marketplace.json 엔트리 전용 | marketplace entry의 `category` |
| `source` (plugin.json에서) | marketplace.json 엔트리 전용 | marketplace entry의 `source` |
| 그 외 임의 필드 | 스키마에 없음 | 허용 필드만 사용 |

### Attribution 보존 4가지 방안

`contributors` 배열이 없으므로 다음 방법으로 기여자를 표기:

| 방법 | 예시 | 권장 용도 |
|------|------|-----------|
| README 각주 | `[^1]: 원본 저자 X, MIT 라이선스` | 외부 upstream 포팅 (기본) |
| `author.url` | `"author": {"name": "Lead", "url": "https://github.com/team"}` | 단일 팀/저자 URL 연결 |
| 플러그인 내부 README | `plugins/{name}/README.md`의 `## Contributors` | 플러그인별 세부 기여자 |
| `description` 내 출처 | `"description": "... 원본: upstream/repo (MIT)"` | 간략 출처 표기 |

**이 프로젝트 정책**: Upstream 포팅은 메인 README.md `[^N]` 각주로, plugin-specific 기여자는 해당 플러그인 README의 `## Contributors` 섹션으로 기록.

### 검증 명령 (plugin.json 작성/수정 시 MANDATORY)

```powershell
# Step 1. JSON syntax 검증
python -c "import json, glob; [json.load(open(f, encoding='utf-8')) for f in glob.glob('plugins/*/.claude-plugin/plugin.json') + ['.claude-plugin/marketplace.json']]; print('OK')"

# Step 2. 허용 필드 화이트리스트 검사 (plugin.json)
python -c "import json, glob; A = {'name','version','description','author','homepage','repository','license','keywords','skills','commands','agents','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies'}; [print(f, '->', set(json.load(open(f,encoding='utf-8')).keys()) - A) for f in glob.glob('plugins/*/.claude-plugin/plugin.json')]"
# 각 파일 뒤 빈 set() 출력 = 정상 / 항목 존재 = 스키마 위반 (해당 필드 제거 필요)

# Step 3. 허용 필드 화이트리스트 검사 (marketplace.json 각 플러그인 엔트리)
python -c "import json; mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8')); M = {'name','source','description','strict','agents','skills','version','author','license','category','homepage','keywords','tags','commands','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies','repository'}; [print(p['name'], '->', set(p.keys()) - M) for p in mp['plugins']]"
# 각 엔트리 뒤 빈 set() 출력 = 정상 / 항목 존재 = 스키마 위반
```

### 실패 에러 패턴

다음 에러가 발생하면 즉시 허용 필드 화이트리스트 검사를 실행:

```
Plugin {name} has an invalid manifest file at .claude-plugin/plugin.json.
Validation errors: Unrecognized keys: "contributors"
```

**조치 절차**:

1. 해당 `plugin.json`과 root `marketplace.json` 엔트리에서 허용 필드 목록에 없는 **모든 키** 제거
2. 제거된 attribution 정보는 README.md 각주 또는 플러그인 README `## Contributors` 섹션으로 이동
3. 플러그인/마켓플레이스 버전을 PATCH 수준으로 올림 (`Version Management & Registry Updates` 섹션 참조)
4. 캐시 클리어 후 재등록 (`After Any Changes` 섹션 참조)

## Root Marketplace.json Format

`marketplace.json` 엔트리는 **plugin.json의 모든 필드** + **마켓플레이스 전용 필드**를 포함할 수 있습니다 ([공식 Anthropic plugins-reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference) 기준).

**마켓플레이스 전용 필드:**

| Field | Required | Description |
|-------|----------|-------------|
| `source` | Yes | 플러그인 소스 (`"./plugins/name"` 문자열 또는 `{"source":"github","repo":"..."}`/`{"source":"npm",...}` 객체) |
| `strict` | Recommended | 컴포넌트 권한 제어 (이 프로젝트는 항상 `true`) |
| `category` | No | 플러그인 카테고리 (조직화 용도) |
| `tags` | No | 검색 태그 배열 |

**plugin.json에서 상속되는 필드 (엔트리에 삽입 가능):**
- 메타데이터: `name` (Yes), `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`
- 컴포넌트 경로: `agents`, `skills`, `commands`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `monitors`, `userConfig`, `channels`, `dependencies`

**중요**: 위 두 그룹에 없는 임의 필드(`contributor`/`contributors`, `maintainer`, `funding` 등)는 plugin.json과 동일하게 **Zod validation이 거부**합니다. 실제 형식은 `.claude-plugin/marketplace.json`을 참조하세요.

## Forbidden Patterns

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
| plugin.json/marketplace.json에 `contributors`/`contributor` 필드 | Zod strict validation `Unrecognized keys` 에러로 등록 실패 (2026-04-21 실제 사례) | 필드 제거 후 README 각주/플러그인 README로 이동 (자세한 내용: `Plugin.json Schema Compliance` 섹션) |
| plugin.json에 `maintainer`/`funding`/임의 필드 | 공식 스키마에 없는 필드 = 등록 실패 | 허용 필드 화이트리스트만 사용 |
| plugin.json에 marketplace 전용 필드(`source`, `category`) | plugin.json 스키마에 없음 | marketplace.json 엔트리에만 사용 |

## After Any Changes

```powershell
# MUST clear cache after marketplace changes
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue

# Re-register marketplace
# Claude Code: /plugin marketplace remove {name}
# Claude Code: /plugin marketplace add {path}
```

## CRITICAL: Agent/Skill/Command File Changes Checklist

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

## Marketplace Registration Checklist

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
- [ ] **plugin.json/marketplace.json 엔트리에 허용되지 않은 필드(`contributors`/`contributor`/`maintainer` 등) 없음** (검증: `Plugin.json Schema Compliance` 섹션의 Python 화이트리스트 스크립트 실행)
- [ ] Attribution은 README.md 각주(`[^N]`) 또는 플러그인 README `## Contributors` 섹션에 기록됨

## MANDATORY: Version Management & Registry Updates

> **배경**: 플러그인 수정 후 `plugin.json`/`marketplace.json` 버전을 업데이트하지 않으면, 사용자가 변경사항을 감지할 수 없고 캐시 무효화가 작동하지 않음.

### Versioning 규칙

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

### 업데이트 대상 파일

| 변경 범위 | 업데이트 대상 |
|-----------|-------------|
| 플러그인 내부 변경 | `plugins/{plugin}/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` 해당 항목 |
| 마켓플레이스 수준 변경 | 위 + `marketplace.json` `metadata.version` + `README.md` `Version` + `AGENTS.md` `Version` + `README.md` 변경 이력 |

**모든 업데이트 대상의 버전은 각각 동기화되어야 합니다.**

### 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| 플러그인 수정 후 버전 미변경 | 변경사항 추적 불가, 캐시 문제 | 반드시 PATCH 이상 올림 |
| plugin.json과 marketplace.json 버전 불일치 | 혼란, 디버깅 어려움 | 두 파일 동시 업데이트 |
| marketplace metadata.version과 README/AGENTS Version 불일치 | 추적 불가 | 항상 동기화 |
| MAJOR 변경인데 PATCH만 올림 | 호환성 문제 미감지 | 변경 유형 정확히 판단 |

## Model Selection Guide

| Model | Use Case | 예시 |
|-------|----------|------|
| `opus` | 아키텍처 설계, 보안 감사, 코드 리뷰 | backend-architect, security-auditor |
| `sonnet` | 복잡한 추론, 기술 선택, 다단계 분석 | python-pro, typescript-pro |
| `haiku` | 빠른 실행, 정형화된 작업, 코드 생성 | test-automator, scaffold-generator |
| `inherit` | 부모 모델 상속 (기본값) | 대부분의 범용 에이전트 |
