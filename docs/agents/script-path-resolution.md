# Script Path Resolution (MANDATORY)

> **언제 읽나요**: 스킬(`SKILL.md`)이나 에이전트(`*.md`)에서 스크립트 경로를 참조하거나, 새로운 스킬에 `scripts/` 폴더를 추가할 때.
> **상위 문서**: [AGENTS.md](../../AGENTS.md)

> **배경**: 에이전트가 스킬 내 스크립트 경로를 찾지 못하면 자체 Python 코드를 작성하는 문제가 반복 발생함. 자체 작성 코드는 구버전 패키지 사용, 핵심 설정 누락 등 치명적 결함을 유발함.

## 규칙: Agent Skills Spec 상대경로 우선, Glob 폴백

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

## 에이전트에서 스크립트 참조 시

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

## 금지 패턴

| 금지 | 문제 | 올바른 방법 |
|------|------|------------|
| `python plugins/xxx/scripts/yyy.py` (하드코딩) | 서브모듈/경로 변경 시 실패 | 상대경로 → Glob 폴백 |
| `{이_스킬의_scripts_경로}` (플레이스홀더) | 에이전트가 해석 못 함 | 구체적 상대경로 명시 |
| 스크립트 못 찾으면 자체 코드 작성 | 구버전 패키지, 설정 누락 | 즉시 중단 + 사용자 안내 |

## 참조 구현

`plugins/visual-generator/skills/slide-renderer/SKILL.md`를 모범 사례로 참조하세요.
