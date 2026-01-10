# 서브에이전트

> Claude Code에서 특화된 AI 서브에이전트를 생성하고 사용하여 작업별 워크플로우 및 향상된 컨텍스트 관리를 구현합니다.

Claude Code의 커스텀 서브에이전트는 특정 유형의 작업을 처리하기 위해 호출할 수 있는 특화된 AI 어시스턴트입니다. 커스텀된 시스템 프롬프트, 도구 및 별도의 컨텍스트 윈도우를 제공하는 작업별 구성을 통해 더 효율적인 문제 해결을 가능하게 합니다.

## 서브에이전트란 무엇인가요?

서브에이전트는 Claude Code가 작업을 위임할 수 있는 사전 구성된 AI 성격입니다. 각 서브에이전트는:

* 특정 목적과 전문 분야를 가지고 있습니다
* 주 대화와 분리된 자체 컨텍스트 윈도우를 사용합니다
* 사용할 수 있는 특정 도구로 구성할 수 있습니다
* 동작을 안내하는 커스텀 시스템 프롬프트를 포함합니다

Claude Code가 서브에이전트의 전문 분야와 일치하는 작업을 만나면, 그 작업을 특화된 서브에이전트에 위임할 수 있으며, 서브에이전트는 독립적으로 작동하고 결과를 반환합니다.

## 주요 이점

<CardGroup cols={2}>
  <Card title="컨텍스트 보존" icon="layer-group">
    각 서브에이전트는 자체 컨텍스트에서 작동하여 주 대화의 오염을 방지하고 고수준 목표에 집중하도록 유지합니다.
  </Card>

  <Card title="특화된 전문성" icon="brain">
    서브에이전트는 특정 도메인에 대한 상세한 지침으로 미세 조정할 수 있으므로 지정된 작업에서 더 높은 성공률을 달성합니다.
  </Card>

  <Card title="재사용성" icon="rotate">
    한 번 생성되면 다양한 프로젝트에서 서브에이전트를 사용하고 팀과 공유하여 일관된 워크플로우를 구현할 수 있습니다.
  </Card>

  <Card title="유연한 권한" icon="shield-check">
    각 서브에이전트는 다양한 도구 접근 수준을 가질 수 있으므로 강력한 도구를 특정 서브에이전트 유형으로 제한할 수 있습니다.
  </Card>
</CardGroup>

## 빠른 시작

첫 번째 서브에이전트를 생성하려면:

<Steps>
  <Step title="서브에이전트 인터페이스 열기">
    다음 명령을 실행합니다:

    ```
    /agents
    ```
  </Step>

  <Step title="'새 에이전트 생성' 선택">
    프로젝트 수준 또는 사용자 수준 서브에이전트를 생성할지 선택합니다
  </Step>

  <Step title="서브에이전트 정의">
    * **권장**: 먼저 Claude로 생성한 다음 커스터마이징하여 자신의 것으로 만듭니다
    * Claude가 언제 사용해야 하는지를 포함하여 서브에이전트를 자세히 설명합니다
    * 접근 권한을 부여할 도구를 선택하거나, 모든 도구를 상속하려면 비워둡니다
    * 인터페이스는 사용 가능한 모든 도구를 표시합니다
    * Claude로 생성하는 경우 `e`를 눌러 자신의 편집기에서 시스템 프롬프트를 편집할 수도 있습니다
  </Step>

  <Step title="저장 및 사용">
    이제 서브에이전트를 사용할 수 있습니다. Claude는 적절할 때 자동으로 사용하거나 명시적으로 호출할 수 있습니다:

    ```
    > Use the code-reviewer subagent to check my recent changes
    ```
  </Step>
</Steps>

## 서브에이전트 구성

### 파일 위치

서브에이전트는 YAML 프론트매터가 있는 마크다운 파일로 저장되며 두 가지 가능한 위치에 있습니다:

| 유형              | 위치                  | 범위              | 우선순위 |
| :-------------- | :------------------ | :-------------- | :--- |
| **프로젝트 서브에이전트** | `.claude/agents/`   | 현재 프로젝트에서 사용 가능 | 최고   |
| **사용자 서브에이전트**  | `~/.claude/agents/` | 모든 프로젝트에서 사용 가능 | 낮음   |

서브에이전트 이름이 충돌할 때 프로젝트 수준 서브에이전트가 사용자 수준 서브에이전트보다 우선합니다.

### 플러그인 에이전트

[플러그인](/ko/plugins)은 Claude Code와 원활하게 통합되는 커스텀 서브에이전트를 제공할 수 있습니다. 플러그인 에이전트는 사용자 정의 에이전트와 동일하게 작동하며 `/agents` 인터페이스에 나타납니다.

**플러그인 에이전트 위치**: 플러그인은 `agents/` 디렉토리(또는 플러그인 매니페스트에 지정된 커스텀 경로)에 에이전트를 포함합니다.

**플러그인 에이전트 사용**:

* 플러그인 에이전트는 커스텀 에이전트와 함께 `/agents`에 나타납니다
* 명시적으로 호출할 수 있습니다: "Use the code-reviewer agent from the security-plugin"
* Claude가 적절할 때 자동으로 호출할 수 있습니다
* `/agents` 인터페이스를 통해 관리(보기, 검사)할 수 있습니다

플러그인 에이전트 생성에 대한 자세한 내용은 [플러그인 컴포넌트 참조](/ko/plugins-reference#agents)를 참조하세요.

### CLI 기반 구성

`--agents` CLI 플래그를 사용하여 서브에이전트를 동적으로 정의할 수도 있으며, 이는 JSON 객체를 허용합니다:

```bash  theme={null}
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

**우선순위**: CLI로 정의된 서브에이전트는 프로젝트 수준 서브에이전트보다 낮은 우선순위를 가지지만 사용자 수준 서브에이전트보다 높은 우선순위를 가집니다.

**사용 사례**: 이 접근 방식은 다음에 유용합니다:

* 서브에이전트 구성의 빠른 테스트
* 저장할 필요가 없는 세션별 서브에이전트
* 커스텀 서브에이전트가 필요한 자동화 스크립트
* 문서 또는 스크립트에서 서브에이전트 정의 공유

JSON 형식 및 사용 가능한 모든 옵션에 대한 자세한 정보는 [CLI 참조 문서](/ko/cli-reference#agents-flag-format)를 참조하세요.

### 파일 형식

각 서브에이전트는 다음 구조의 마크다운 파일에 정의됩니다:

```markdown  theme={null}
---
name: your-sub-agent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted
model: sonnet  # Optional - specify model alias or 'inherit'
permissionMode: default  # Optional - permission mode for the subagent
skills: skill1, skill2  # Optional - skills to auto-load
---

Your subagent's system prompt goes here. This can be multiple paragraphs
and should clearly define the subagent's role, capabilities, and approach
to solving problems.

Include specific instructions, best practices, and any constraints
the subagent should follow.
```

#### 구성 필드

| 필드               | 필수  | 설명                                                                                                                                             |
| :--------------- | :-- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`           | 예   | 소문자 및 하이픈을 사용하는 고유 식별자                                                                                                                         |
| `description`    | 예   | 서브에이전트의 목적에 대한 자연어 설명                                                                                                                          |
| `tools`          | 아니오 | 특정 도구의 쉼표로 구분된 목록입니다. 생략하면 주 스레드의 모든 도구를 상속합니다                                                                                                 |
| `model`          | 아니오 | 이 서브에이전트에 사용할 모델입니다. 모델 별칭(`sonnet`, `opus`, `haiku`) 또는 주 대화의 모델을 사용하려면 `'inherit'`일 수 있습니다. 생략하면 [구성된 서브에이전트 모델](/ko/model-config)로 기본 설정됩니다 |
| `permissionMode` | 아니오 | 서브에이전트의 권한 모드입니다. 유효한 값: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`, `ignore`. 서브에이전트가 권한 요청을 처리하는 방식을 제어합니다             |
| `skills`         | 아니오 | 서브에이전트가 시작할 때 자동으로 로드할 스킬 이름의 쉼표로 구분된 목록입니다. 서브에이전트는 부모 대화에서 스킬을 상속하지 않습니다. 생략하면 스킬이 미리 로드되지 않습니다.                                             |
| `hooks`          | 아니오 | 이 서브에이전트의 라이프사이클에 범위가 지정된 훅을 정의합니다. `PreToolUse`, `PostToolUse` 및 `Stop` 이벤트를 지원합니다. [서브에이전트에 대한 훅 정의](#define-hooks-for-subagents)를 참조하세요.    |

### 모델 선택

`model` 필드를 사용하면 서브에이전트가 사용하는 [AI 모델](/ko/model-config)을 제어할 수 있습니다:

* **모델 별칭**: 사용 가능한 별칭 중 하나를 사용합니다: `sonnet`, `opus` 또는 `haiku`
* **`'inherit'`**: 주 대화와 동일한 모델을 사용합니다(일관성을 위해 유용함)
* **생략**: 지정하지 않으면 서브에이전트에 대해 구성된 기본 모델(`sonnet`)을 사용합니다

<Note>
  `'inherit'`를 사용하는 것은 서브에이전트가 주 대화의 모델 선택에 적응하도록 하려는 경우 특히 유용하며, 전체 세션에서 일관된 기능과 응답 스타일을 보장합니다.
</Note>

### 사용 가능한 도구

서브에이전트는 Claude Code의 내부 도구에 접근할 수 있습니다. 사용 가능한 도구의 전체 목록은 [도구 문서](/ko/settings#tools-available-to-claude)를 참조하세요.

<Tip>
  **권장**: `/agents` 명령을 사용하여 도구 접근을 수정합니다. 연결된 MCP 서버 도구를 포함한 사용 가능한 모든 도구를 나열하는 대화형 인터페이스를 제공하므로 필요한 도구를 더 쉽게 선택할 수 있습니다.
</Tip>

도구 구성에는 두 가지 옵션이 있습니다:

* **`tools` 필드 생략** - 주 스레드의 모든 도구(기본값)를 상속합니다(MCP 도구 포함)
* **개별 도구 지정** - 더 세밀한 제어를 위해 쉼표로 구분된 목록으로 지정합니다(`/agents`를 통해 수동으로 또는 편집 가능)

**MCP 도구**: 서브에이전트는 구성된 MCP 서버의 MCP 도구에 접근할 수 있습니다. `tools` 필드를 생략하면 서브에이전트는 주 스레드에서 사용 가능한 모든 MCP 도구를 상속합니다.

### 서브에이전트에 대한 훅 정의

서브에이전트는 서브에이전트의 라이프사이클 동안 실행되는 훅을 정의할 수 있습니다. `hooks` 필드를 사용하여 `PreToolUse`, `PostToolUse` 또는 `Stop` 핸들러를 지정합니다:

```yaml  theme={null}
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

서브에이전트에 정의된 훅은 해당 서브에이전트의 실행으로 범위가 지정되며 서브에이전트가 완료되면 자동으로 정리됩니다.

전체 훅 구성 형식은 [훅](/ko/hooks)을 참조하세요.

## 서브에이전트 관리

### /agents 명령 사용(권장)

`/agents` 명령은 서브에이전트 관리를 위한 포괄적인 인터페이스를 제공합니다:

```
/agents
```

이는 다음을 수행할 수 있는 대화형 메뉴를 엽니다:

* 사용 가능한 모든 서브에이전트 보기(기본 제공, 사용자 및 프로젝트)
* 안내된 설정으로 새 서브에이전트 생성
* 도구 접근을 포함한 기존 커스텀 서브에이전트 편집
* 커스텀 서브에이전트 삭제
* 중복이 있을 때 활성 서브에이전트 확인
* **도구 권한 관리** - 사용 가능한 도구의 전체 목록 포함

### 직접 파일 관리

서브에이전트 파일로 직접 작업하여 서브에이전트를 관리할 수도 있습니다:

```bash  theme={null}
# 프로젝트 서브에이전트 생성
mkdir -p .claude/agents
echo '---
name: test-runner
description: Use proactively to run tests and fix failures
---

You are a test automation expert. When you see code changes, proactively run the appropriate tests. If tests fail, analyze the failures and fix them while preserving the original test intent.' > .claude/agents/test-runner.md

# 사용자 서브에이전트 생성
mkdir -p ~/.claude/agents
# ... 서브에이전트 파일 생성
```

<Note>
  파일을 수동으로 추가하여 생성된 서브에이전트는 다음 Claude Code 세션을 시작할 때 로드됩니다. 다시 시작하지 않고 즉시 서브에이전트를 생성하고 사용하려면 `/agents` 명령을 대신 사용하세요.
</Note>

### 특정 서브에이전트 비활성화

`Task(AgentName)` 권한 규칙 구문을 사용하여 특정 기본 제공 또는 커스텀 서브에이전트를 비활성화할 수 있습니다. 이러한 규칙을 [설정](/ko/settings#permission-settings)의 `deny` 배열에 추가하거나 `--disallowedTools` CLI 플래그를 사용합니다.

**예제 settings.json 구성:**

```json  theme={null}
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(Plan)"]
  }
}
```

**예제 CLI 사용:**

```bash  theme={null}
claude --disallowedTools "Task(Explore)"
```

이는 보안상의 이유로 또는 특정 워크플로우를 적용하기 위해 Claude가 특정 서브에이전트에 작업을 위임하는 것을 방지하려는 경우에 유용합니다.

자세한 내용은 [IAM 문서](/ko/iam#tool-specific-permission-rules)를 참조하세요.

## 서브에이전트를 효과적으로 사용하기

### 자동 위임

Claude Code는 다음을 기반으로 작업을 사전에 위임합니다:

* 요청의 작업 설명
* 서브에이전트 구성의 `description` 필드
* 현재 컨텍스트 및 사용 가능한 도구

<Tip>
  더 많은 사전 서브에이전트 사용을 장려하려면 `description` 필드에 "use PROACTIVELY" 또는 "MUST BE USED"와 같은 구문을 포함하세요.
</Tip>

### 명시적 호출

명령에서 특정 서브에이전트를 언급하여 요청합니다:

```
> Use the test-runner subagent to fix failing tests
> Have the code-reviewer subagent look at my recent changes
> Ask the debugger subagent to investigate this error
```

## 기본 제공 서브에이전트

Claude Code에는 기본으로 사용 가능한 기본 제공 서브에이전트가 포함되어 있습니다:

### 범용 서브에이전트

범용 서브에이전트는 탐색과 작업 모두를 필요로 하는 복잡한 다단계 작업을 위한 유능한 에이전트입니다. Explore 서브에이전트와 달리 파일을 수정하고 더 넓은 범위의 작업을 실행할 수 있습니다.

**주요 특징:**

* **모델**: 더 강력한 추론을 위해 Sonnet을 사용합니다
* **도구**: 모든 도구에 접근할 수 있습니다
* **모드**: 파일을 읽고 쓸 수 있으며, 명령을 실행하고, 변경을 수행할 수 있습니다
* **목적**: 복잡한 연구 작업, 다단계 작업, 코드 수정

**Claude가 사용하는 경우:**

Claude는 다음 경우에 범용 서브에이전트에 위임합니다:

* 작업에 탐색과 수정이 모두 필요한 경우
* 검색 결과를 해석하기 위해 복잡한 추론이 필요한 경우
* 초기 검색이 실패하면 여러 전략이 필요할 수 있는 경우
* 작업이 서로 의존하는 여러 단계를 가진 경우

**예제 시나리오:**

```
User: Find all the places where we handle authentication and update them to use the new token format

Claude: [Invokes general-purpose subagent]
[Agent searches for auth-related code across codebase]
[Agent reads and analyzes multiple files]
[Agent makes necessary edits]
[Returns detailed writeup of changes made]
```

### Plan 서브에이전트

Plan 서브에이전트는 계획 모드에서 사용하도록 설계된 특화된 기본 제공 에이전트입니다. Claude가 계획 모드(비실행 모드)에서 작동할 때 Plan 서브에이전트를 사용하여 계획을 제시하기 전에 코드베이스에 대한 연구를 수행하고 정보를 수집합니다.

**주요 특징:**

* **모델**: 더 강력한 분석을 위해 Sonnet을 사용합니다
* **도구**: 코드베이스 탐색을 위해 Read, Glob, Grep 및 Bash 도구에 접근할 수 있습니다
* **목적**: 파일을 검색하고, 코드 구조를 분석하고, 컨텍스트를 수집합니다
* **자동 호출**: Claude는 계획 모드에 있고 코드베이스를 연구해야 할 때 자동으로 이 에이전트를 사용합니다

**작동 방식:**
계획 모드에 있고 Claude가 계획을 작성하기 위해 코드베이스를 이해해야 할 때, 연구 작업을 Plan 서브에이전트에 위임합니다. 이는 에이전트의 무한 중첩을 방지합니다(서브에이전트는 다른 서브에이전트를 생성할 수 없음). 동시에 Claude가 필요한 컨텍스트를 수집할 수 있도록 합니다.

**예제 시나리오:**

```
User: [In plan mode] Help me refactor the authentication module

Claude: Let me research your authentication implementation first...
[Internally invokes Plan subagent to explore auth-related files]
[Plan subagent searches codebase and returns findings]
Claude: Based on my research, here's my proposed plan...
```

<Tip>
  Plan 서브에이전트는 계획 모드에서만 사용됩니다. 일반 실행 모드에서 Claude는 범용 에이전트 또는 생성한 다른 커스텀 서브에이전트를 사용합니다.
</Tip>

### Explore 서브에이전트

Explore 서브에이전트는 코드베이스 검색 및 분석에 최적화된 빠르고 가벼운 에이전트입니다. 엄격한 읽기 전용 모드에서 작동하며 빠른 파일 검색 및 코드 탐색을 위해 설계되었습니다.

**주요 특징:**

* **모델**: 빠르고 낮은 지연 시간의 검색을 위해 Haiku를 사용합니다
* **모드**: 엄격한 읽기 전용 - 파일을 생성, 수정 또는 삭제할 수 없습니다
* **사용 가능한 도구**:
  * Glob - 파일 패턴 일치
  * Grep - 정규식을 사용한 콘텐츠 검색
  * Read - 파일 콘텐츠 읽기
  * Bash - 읽기 전용 명령만(ls, git status, git log, git diff, find, cat, head, tail)

**Claude가 사용하는 경우:**

Claude는 코드베이스를 검색하거나 이해해야 하지만 변경할 필요가 없을 때 Explore 서브에이전트에 위임합니다. 탐색 프로세스 중에 발견된 콘텐츠가 주 대화를 부풀리지 않으므로 주 에이전트가 여러 검색 명령을 직접 실행하는 것보다 더 효율적입니다.

**철저함 수준:**

Explore 서브에이전트를 호출할 때 Claude는 철저함 수준을 지정합니다:

* **Quick** - 최소한의 탐색으로 빠른 검색입니다. 대상 조회에 좋습니다.
* **Medium** - 적당한 탐색입니다. 속도와 철저함의 균형을 맞춥니다.
* **Very thorough** - 여러 위치 및 명명 규칙에 걸친 포괄적인 분석입니다. 대상이 예상치 못한 위치에 있을 수 있을 때 사용됩니다.

**예제 시나리오:**

```
User: Where are errors from the client handled?

Claude: [Invokes Explore subagent with "medium" thoroughness]
[Explore uses Grep to search for error handling patterns]
[Explore uses Read to examine promising files]
[Returns findings with absolute file paths]
Claude: Client errors are handled in src/services/process.ts:712...
```

```
User: What's the codebase structure?

Claude: [Invokes Explore subagent with "quick" thoroughness]
[Explore uses Glob and ls to map directory structure]
[Returns overview of key directories and their purposes]
```

## 예제 서브에이전트

### 코드 리뷰어

```markdown  theme={null}
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### 디버거

```markdown  theme={null}
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### 데이터 과학자

```markdown  theme={null}
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

## 모범 사례

* **Claude 생성 에이전트로 시작**: Claude로 초기 서브에이전트를 생성한 다음 반복하여 자신의 것으로 만드는 것을 강력히 권장합니다. 이 접근 방식은 최고의 결과를 제공합니다. 특정 요구 사항에 맞게 커스터마이징할 수 있는 견고한 기초입니다.

* **집중된 서브에이전트 설계**: 하나의 서브에이전트가 모든 것을 하도록 하려고 하기보다는 단일하고 명확한 책임을 가진 서브에이전트를 생성합니다. 이는 성능을 향상시키고 서브에이전트를 더 예측 가능하게 만듭니다.

* **상세한 프롬프트 작성**: 시스템 프롬프트에 특정 지침, 예제 및 제약 조건을 포함합니다. 제공하는 지침이 많을수록 서브에이전트의 성능이 더 좋습니다.

* **도구 접근 제한**: 서브에이전트의 목적에 필요한 도구만 부여합니다. 이는 보안을 향상시키고 서브에이전트가 관련 작업에 집중하도록 도와줍니다.

* **버전 제어**: 프로젝트 서브에이전트를 버전 제어에 확인하여 팀이 협력적으로 이점을 얻고 개선할 수 있도록 합니다.

## 고급 사용

### 서브에이전트 체이닝

복잡한 워크플로우의 경우 여러 서브에이전트를 체인할 수 있습니다:

```
> First use the code-analyzer subagent to find performance issues, then use the optimizer subagent to fix them
```

### 동적 서브에이전트 선택

Claude Code는 컨텍스트를 기반으로 지능적으로 서브에이전트를 선택합니다. 최상의 결과를 위해 `description` 필드를 구체적이고 작업 지향적으로 만드세요.

### 재개 가능한 서브에이전트

서브에이전트를 재개하여 이전 대화를 계속할 수 있으며, 이는 여러 호출에 걸쳐 계속해야 하는 장기 실행 연구 또는 분석 작업에 특히 유용합니다.

**작동 방식:**

* 각 서브에이전트 실행에는 고유한 `agentId`가 할당됩니다
* 에이전트의 대화는 별도의 트랜스크립트 파일에 저장됩니다: `agent-{agentId}.jsonl`
* `resume` 매개변수를 통해 `agentId`를 제공하여 이전 에이전트를 재개할 수 있습니다
* 재개되면 에이전트는 이전 대화의 전체 컨텍스트로 계속됩니다

**예제 워크플로우:**

초기 호출:

```
> Use the code-analyzer agent to start reviewing the authentication module

[Agent completes initial analysis and returns agentId: "abc123"]
```

에이전트 재개:

```
> Resume agent abc123 and now analyze the authorization logic as well

[Agent continues with full context from previous conversation]
```

**사용 사례:**

* **장기 실행 연구**: 큰 코드베이스 분석을 여러 세션으로 분할합니다
* **반복적 개선**: 컨텍스트를 잃지 않고 서브에이전트의 작업을 계속 개선합니다
* **다단계 워크플로우**: 서브에이전트가 컨텍스트를 유지하면서 순차적으로 관련 작업을 수행하도록 합니다

**기술 세부 사항:**

* 에이전트 트랜스크립트는 프로젝트 디렉토리에 저장됩니다
* 메시지 중복을 방지하기 위해 재개 중에 기록이 비활성화됩니다
* 동기 및 비동기 에이전트 모두 재개할 수 있습니다
* `resume` 매개변수는 이전 실행의 에이전트 ID를 허용합니다

**프로그래밍 방식 사용:**

Agent SDK를 사용하거나 AgentTool과 직접 상호 작용하는 경우 `resume` 매개변수를 전달할 수 있습니다:

```typescript  theme={null}
{
  "description": "Continue analysis",
  "prompt": "Now examine the error handling patterns",
  "subagent_type": "code-analyzer",
  "resume": "abc123"  // Agent ID from previous execution
}
```

<Tip>
  나중에 재개할 수 있는 작업의 에이전트 ID를 추적하세요. Claude Code는 서브에이전트가 작업을 완료할 때 에이전트 ID를 표시합니다.
</Tip>

## 성능 고려 사항

* **컨텍스트 효율성**: 에이전트는 주 컨텍스트를 보존하여 더 긴 전체 세션을 가능하게 합니다
* **지연 시간**: 서브에이전트는 호출될 때마다 깨끗한 상태로 시작하며 효과적으로 작업을 수행하기 위해 필요한 컨텍스트를 수집할 때 지연 시간을 추가할 수 있습니다.

## 관련 문서

* [플러그인](/ko/plugins) - 플러그인을 통해 커스텀 에이전트로 Claude Code 확장
* [슬래시 명령](/ko/slash-commands) - 다른 기본 제공 명령에 대해 알아보기
* [설정](/ko/settings) - Claude Code 동작 구성
* [훅](/ko/hooks) - 이벤트 핸들러로 워크플로우 자동화


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://code.claude.com/docs/llms.txt