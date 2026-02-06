# Visual Generator: CWD Path Resolution Fix

## TL;DR

> **Quick Summary**: Fix broken `Read()` calls in visual-generator agents caused by CWD mismatch when spawned via `Task()`. Move `references/themes/` content into `skills/themes/SKILL.md` so the plugin system auto-loads themes into agent context, eliminating path-dependent file reads entirely.
> 
> **Deliverables**:
> - New `plugins/visual-generator/skills/themes/SKILL.md` containing all 6 theme definitions
> - Updated marketplace.json registering the new themes skill
> - Updated agent/command files with broken Read() calls removed and docs corrected
> - Deleted `references/` directory (themes moved + duplicate layout_types.md removed)
> 
> **Estimated Effort**: Short (~30-45 min)
> **Parallel Execution**: NO — sequential (each step depends on prior)
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6

---

## Context

### Original Request
Fix CWD path resolution bug: when agents spawn via `Task(subagent_type=...)`, they run in the user's CWD (e.g., `/home/orientpine/playground/work/`), not the plugin root. The `references/` directory is NOT part of the plugin path resolution system — only registered `skills/` and `agents/` get automatic path resolution. This causes `Read(plugins/visual-generator/references/themes/{style}.md)` to fail.

### Interview Summary
**Key Discussions**:
- User proposed: move `references/themes/` to `skills/themes/` and register as a skill
- User identified all affected files and exact line numbers
- User confirmed `references/layout_types.md` is a duplicate of `skills/layout-types/SKILL.md`

**Research Findings**:
- **Confirmed**: `renderer-agent.md` has zero theme references — only 3 agents + 1 command file affected
- **Confirmed**: `references/layout_types.md` is identical to `skills/layout-types/SKILL.md` (minus YAML frontmatter)
- **Confirmed**: Current marketplace.json only registers `"./skills/layout-types"` — themes not registered
- **Structure precedent**: `layout-types` uses a single monolithic SKILL.md (all 24 layouts inline), confirming plugin system loads only SKILL.md, not sibling files in the directory

### Metis Review
**Identified Gaps** (addressed):
- **File count correction**: User said "3 agent files with Read() calls" — actual count is 2 (`content-organizer.md`, `prompt-designer.md`). `content-reviewer.md` only has doc tables, no Read() calls to themes. Fixed in task breakdown.
- **Misleading MUST DO instructions**: After auto-loading, agent instructions saying "반드시 테마 파일 Read()" become misleading. Updated in scope.
- **Error handling dead code**: `content-organizer.md:352` error handler "테마 참조 파일 없음" becomes impossible with auto-loading. Updated in scope.
- **AGENTS.md/README.md staleness**: Already stale from prior refactor (references `prompt-concept/`, `prompt-gov/` etc. that don't exist). Explicitly OUT of scope — separate task.

---

## Work Objectives

### Core Objective
Eliminate CWD-dependent `Read()` calls in visual-generator agents by consolidating all theme definitions into a registered skill that the plugin system auto-loads into agent context.

### Concrete Deliverables
- `plugins/visual-generator/skills/themes/SKILL.md` — new consolidated themes skill (~1,130 lines)
- `.claude-plugin/marketplace.json` — updated with `"./skills/themes"` registration
- `plugins/visual-generator/agents/content-organizer.md` — broken Read() removed, docs updated
- `plugins/visual-generator/agents/prompt-designer.md` — broken Read() removed, docs updated
- `plugins/visual-generator/agents/content-reviewer.md` — doc table updated
- `plugins/visual-generator/commands/visual-generate.md` — doc table updated
- `plugins/visual-generator/references/` — entire directory deleted

### Definition of Done
- [ ] Zero occurrences of `references/themes` in any file under `plugins/visual-generator/`
- [ ] Zero occurrences of `references/layout_types` in any file under `plugins/visual-generator/`
- [ ] `plugins/visual-generator/references/` directory does not exist
- [ ] `plugins/visual-generator/skills/themes/SKILL.md` exists with valid YAML frontmatter
- [ ] marketplace.json includes `"./skills/themes"` in visual-generator's skills array
- [ ] All 6 theme contents preserved in SKILL.md (concept, gov, seminar, whatif, pitch, comparison)
- [ ] `renderer-agent.md` unchanged (git diff shows no modifications)
- [ ] No Read() calls remain that reference theme files in any agent

### Must Have
- All 6 theme file contents preserved verbatim in the consolidated SKILL.md
- YAML frontmatter with `name` and `description` (description in double quotes per project convention)
- Clear section headers per theme for agent navigation (agents receive `{style}` parameter and must locate correct section)
- LF line endings on all modified/created files
- marketplace.json `"strict": true` preserved

### Must NOT Have (Guardrails)
- **DO NOT modify `renderer-agent.md`** — confirmed zero theme references
- **DO NOT modify `AGENTS.md` or `README.md`** — already stale from prior refactor, separate cleanup task
- **DO NOT change theme file content** — only relocate/consolidate. No reformatting, no rewriting
- **DO NOT introduce `${CLAUDE_PLUGIN_ROOT}` or any new absolute path pattern** — themes are auto-loaded, no path needed
- **DO NOT modify any workflow logic, prompt rules, or rendering behavior** in agents
- **DO NOT add YAML frontmatter to individual theme sections** — only SKILL.md gets frontmatter
- **DO NOT touch files outside `plugins/visual-generator/` except `.claude-plugin/marketplace.json`**
- **DO NOT leave any `Read()` call that references theme files** — themes are auto-loaded now

---

## Verification Strategy

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.

### Test Decision
- **Infrastructure exists**: N/A (no test framework needed — this is config/docs refactoring)
- **Automated tests**: None (file operations + grep verification)
- **Framework**: Bash commands for verification

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

**Verification Tool**: Bash (grep, test, git diff)

```
Scenario: No broken references remain
  Tool: Bash (grep)
  Steps:
    1. grep -r "references/themes" plugins/visual-generator/
    2. Assert: zero matches
    3. grep -r "references/layout_types" plugins/visual-generator/
    4. Assert: zero matches
  Expected Result: Zero matches for old paths
  Failure Indicators: Any match found

Scenario: New skill properly structured
  Tool: Bash
  Steps:
    1. test -f plugins/visual-generator/skills/themes/SKILL.md
    2. Assert: exit code 0 (file exists)
    3. head -1 plugins/visual-generator/skills/themes/SKILL.md
    4. Assert: output is "---"
    5. grep -c "^# Concept\|^# Gov\|^# Seminar\|^# What-If\|^# Pitch\|^# Comparison" plugins/visual-generator/skills/themes/SKILL.md
    6. Assert: 6 (all themes present)
  Expected Result: SKILL.md exists with valid frontmatter and all 6 themes
  
Scenario: references/ directory fully removed
  Tool: Bash
  Steps:
    1. test -d plugins/visual-generator/references
    2. Assert: exit code 1 (directory does not exist)
  Expected Result: Directory gone

Scenario: marketplace.json correctly updated
  Tool: Bash (grep)
  Steps:
    1. grep '"./skills/themes"' .claude-plugin/marketplace.json
    2. Assert: match found
    3. grep '"./skills/layout-types"' .claude-plugin/marketplace.json
    4. Assert: still present (not accidentally removed)
  Expected Result: Both skills registered

Scenario: Only expected files modified
  Tool: Bash (git diff)
  Steps:
    1. git diff --name-only
    2. Assert: exactly these files changed/added/deleted:
       - .claude-plugin/marketplace.json (modified)
       - plugins/visual-generator/agents/content-organizer.md (modified)
       - plugins/visual-generator/agents/content-reviewer.md (modified)
       - plugins/visual-generator/agents/prompt-designer.md (modified)
       - plugins/visual-generator/commands/visual-generate.md (modified)
       - plugins/visual-generator/skills/themes/SKILL.md (added)
       - plugins/visual-generator/references/ (deleted: 7 files)
    3. git diff plugins/visual-generator/agents/renderer-agent.md
    4. Assert: empty (no changes)
  Expected Result: Only planned files touched
```

---

## Execution Strategy

### Sequential Execution (No Parallelism)

Each task depends on the prior for verification integrity. These run one at a time.

```
Task 1: Create skills/themes/SKILL.md
    ↓
Task 2: Update marketplace.json
    ↓
Task 3: Edit content-organizer.md (2 Read() removals + doc table + MUST DO + error handling)
    ↓
Task 4: Edit prompt-designer.md (1 Read() removal + doc table + MUST DO)
    ↓
Task 5: Edit content-reviewer.md + visual-generate.md (doc tables only)
    ↓
Task 6: Delete references/ directory + final verification
```

---

## TODOs

- [ ] 1. Create consolidated themes SKILL.md

  **What to do**:
  - Create directory `plugins/visual-generator/skills/themes/`
  - Create `SKILL.md` with YAML frontmatter:
    ```yaml
    ---
    name: themes
    description: "visual-generator 에이전트가 공유하는 6종 테마 팔레트 정의. 스타일별 색상 팔레트, 무드 가이드, 시각적 톤앤매너를 포함합니다."
    ---
    ```
  - Add a **Theme Selection Guide** section at the top:
    ```markdown
    # 테마 팔레트 (Theme Palettes)

    ## 개요
    visual-generator 에이전트가 공유하는 6종 테마 정의입니다.
    
    **스타일별 테마 유형:**
    | 유형 | 스타일 | 설명 |
    |------|--------|------|
    | 무드 테마 (9종 선택) | concept, gov, seminar | 각 스타일별 9종 무드, 각 4색 팔레트 |
    | 목적 테마 (단일) | whatif, pitch, comparison | 단일 팔레트 + 레이아웃/씬 구성 가이드 |
    
    **사용 방법**: `{style}` 파라미터에 해당하는 섹션을 참조하세요.
    
    > ⚠️ 이 파일은 스킬로 자동 로드됩니다. Read() 호출이 필요하지 않습니다.
    > 새 테마를 추가할 때는 반드시 이 SKILL.md 파일 내에 섹션으로 추가하세요.
    ```
  - Concatenate all 6 theme file contents below the guide, separated by `---` dividers and clear `#`-level headers:
    1. `# Concept 스타일 테마 팔레트` (from `references/themes/concept.md`)
    2. `# Gov 스타일 테마 팔레트` (from `references/themes/gov.md`)
    3. `# Seminar 스타일 테마 팔레트` (from `references/themes/seminar.md`)
    4. `# What-If (미래 비전 스냅샷) 테마` (from `references/themes/whatif.md`)
    5. `# Pitch (투자 임팩트) 테마` (from `references/themes/pitch.md`)
    6. `# Comparison (Before/After 비교) 테마` (from `references/themes/comparison.md`)
  - **Theme file contents must be copied VERBATIM** — do not reformat, rewrite, or summarize
  - Ensure LF line endings (not CRLF)

  **Must NOT do**:
  - Do NOT modify theme content in any way (only add SKILL.md wrapper and section headers that match existing H1 titles)
  - Do NOT add YAML frontmatter to individual theme sections
  - Do NOT create separate SKILL.md files per theme

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward file creation — copy 6 files into one with a thin wrapper
  - **Skills**: []
    - No special skills needed — just Read and Write operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: Tasks 2-6
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/skills/layout-types/SKILL.md:1-5` — YAML frontmatter pattern to follow (name, description fields)
  - `plugins/visual-generator/skills/layout-types/SKILL.md:6-10` — Top-level overview section pattern to follow

  **Source Content References**:
  - `plugins/visual-generator/references/themes/concept.md` — Full file, copy verbatim (193 lines, concept style 9 moods)
  - `plugins/visual-generator/references/themes/gov.md` — Full file, copy verbatim (192 lines, gov style 9 moods)
  - `plugins/visual-generator/references/themes/seminar.md` — Full file, copy verbatim (187 lines, seminar style 9 moods)
  - `plugins/visual-generator/references/themes/whatif.md` — Full file, copy verbatim (244 lines, what-if purpose theme)
  - `plugins/visual-generator/references/themes/pitch.md` — Full file, copy verbatim (146 lines, pitch purpose theme)
  - `plugins/visual-generator/references/themes/comparison.md` — Full file, copy verbatim (157 lines, comparison purpose theme)

  **WHY Each Reference Matters**:
  - `layout-types/SKILL.md` frontmatter: Shows the exact YAML structure expected by the plugin system — follow this format for `name` and `description` fields
  - Each theme file: Source content to consolidate — must be copied verbatim into the new SKILL.md

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: SKILL.md created with valid structure
    Tool: Bash
    Steps:
      1. test -f plugins/visual-generator/skills/themes/SKILL.md && echo "EXISTS" || echo "MISSING"
      2. Assert: "EXISTS"
      3. head -4 plugins/visual-generator/skills/themes/SKILL.md
      4. Assert: lines 1 and 3 are "---" (valid YAML frontmatter delimiters)
      5. grep "^name: themes" plugins/visual-generator/skills/themes/SKILL.md
      6. Assert: match found

  Scenario: All 6 theme contents present
    Tool: Bash (grep)
    Steps:
      1. grep -c "기술 보고서 (technical-report)" plugins/visual-generator/skills/themes/SKILL.md
      2. Assert: 3 (once in concept, gov, seminar sections)
      3. grep "핵심 원칙" plugins/visual-generator/skills/themes/SKILL.md
      4. Assert: match found (whatif section present)
      5. grep "투자 임팩트" plugins/visual-generator/skills/themes/SKILL.md
      6. Assert: match found (pitch section present)
      7. grep "Before/After" plugins/visual-generator/skills/themes/SKILL.md
      8. Assert: match found (comparison section present)
    Expected Result: All 6 themes confirmed present

  Scenario: Content integrity — concept theme spot check
    Tool: Bash (grep)
    Steps:
      1. grep "#2C3E50" plugins/visual-generator/skills/themes/SKILL.md
      2. Assert: match found (concept technical-report palette preserved)
      3. grep "#2980B9" plugins/visual-generator/skills/themes/SKILL.md
      4. Assert: match found
    Expected Result: Color codes preserved verbatim
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `refactor(visual-generator): move themes from references/ to skills/ for auto-loading`
  - Files: `plugins/visual-generator/skills/themes/SKILL.md`
  - Pre-commit: `grep -c "^---" plugins/visual-generator/skills/themes/SKILL.md` → 2

---

- [ ] 2. Update marketplace.json

  **What to do**:
  - Edit `.claude-plugin/marketplace.json`
  - Find the `visual-generator` plugin entry (currently around line 38)
  - Change `"skills": ["./skills/layout-types"]` to `"skills": ["./skills/layout-types", "./skills/themes"]`

  **Must NOT do**:
  - Do NOT remove `"./skills/layout-types"` — it must remain
  - Do NOT add trailing slash (`"./skills/themes/"` is WRONG)
  - Do NOT change `"strict": true`
  - Do NOT modify any other plugin entries

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single line edit in a JSON file
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2)
  - **Blocks**: Tasks 3-6
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `.claude-plugin/marketplace.json:37-39` — Current visual-generator skills array (change target)
  - `.claude-plugin/marketplace.json:25` — `isd-generator` uses `"skills": ["./skills"]` as reference for multi-skill array syntax

  **WHY Each Reference Matters**:
  - Line 38: Exact location of the edit — current value is `["./skills/layout-types"]`, must become `["./skills/layout-types", "./skills/themes"]`
  - Line 25: Shows that multiple skill paths in an array are valid in this project's conventions

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: marketplace.json has both skills registered
    Tool: Bash (grep + jq if available)
    Steps:
      1. grep '"./skills/themes"' .claude-plugin/marketplace.json
      2. Assert: match found
      3. grep '"./skills/layout-types"' .claude-plugin/marketplace.json
      4. Assert: match found (not accidentally removed)
      5. python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))" 2>&1
      6. Assert: no error (valid JSON)
    Expected Result: Both skills registered, valid JSON

  Scenario: No other plugin entries modified
    Tool: Bash (git diff)
    Steps:
      1. git diff .claude-plugin/marketplace.json | grep "^[+-]" | grep -v "^[+-][+-][+-]" | grep -v "skills/themes\|skills/layout-types"
      2. Assert: empty (only the skills line changed)
    Expected Result: Only the skills array line was modified
  ```

  **Commit**: YES (group with Task 1)
  - Message: `refactor(visual-generator): move themes from references/ to skills/ for auto-loading`
  - Files: `.claude-plugin/marketplace.json`
  - Pre-commit: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"`

---

- [ ] 3. Edit content-organizer.md — Remove broken Read() calls, update docs

  **What to do**:

  **3a. Remove Read() at line 157** (Phase 3, Step 3-1: theme file load):
  - **Current** (lines 156-159):
    ```
        +-- Step 3-1. 테마 참조 파일 로드
        |   +-- Read(plugins/visual-generator/references/themes/{style}.md)
        |   +-- concept/gov/seminar: 9종 무드 확인
        |   +-- whatif/pitch/comparison: 단일 목적 테마(팔레트 4색) 확인
    ```
  - **Replace with**:
    ```
        +-- Step 3-1. 테마 팔레트 확인
        |   +-- 자동 로드된 themes 스킬에서 {style}에 해당하는 섹션 참조
        |   +-- concept/gov/seminar: 9종 무드 확인
        |   +-- whatif/pitch/comparison: 단일 목적 테마(팔레트 4색) 확인
    ```

  **3b. Remove redundant Read() at line 173** (Phase 4, Step 4-1: layout load):
  - **Current** (lines 172-174):
    ```
        +-- Step 4-1. 레이아웃 참조 파일 로드
        |   +-- Read(plugins/visual-generator/skills/layout-types/SKILL.md)
        |   +-- 24종 레이아웃 정의 확인
    ```
  - **Replace with**:
    ```
        +-- Step 4-1. 레이아웃 정의 확인
        |   +-- 자동 로드된 layout-types 스킬에서 24종 레이아웃 정의 참조
        |   +-- 24종 레이아웃 정의 확인
    ```

  **3c. Update Resources documentation table** (lines 289-297):
  - **Current**:
    ```markdown
    | 경로 | 설명 |
    |------|------|
    | `plugins/visual-generator/skills/layout-types/SKILL.md` | 24종 레이아웃 유형 상세 정의 |
    | `plugins/visual-generator/references/themes/concept.md` | concept 스타일 테마 (9종 무드, 각 4색 팔레트) |
    | `plugins/visual-generator/references/themes/gov.md` | gov 스타일 테마 (9종 무드, 각 4색 팔레트) |
    | `plugins/visual-generator/references/themes/seminar.md` | seminar 스타일 테마 (9종 무드, 각 4색 팔레트) |
    | `plugins/visual-generator/references/themes/whatif.md` | whatif 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/pitch.md` | pitch 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/comparison.md` | comparison 목적 테마 (단일 팔레트) |
    ```
  - **Replace with**:
    ```markdown
    > 아래 참조 파일들은 모두 스킬로 등록되어 에이전트 컨텍스트에 자동 로드됩니다. 별도의 Read() 호출이 필요하지 않습니다.

    | 스킬 | 설명 |
    |------|------|
    | `layout-types` | 24종 레이아웃 유형 상세 정의 |
    | `themes` | 6종 테마 팔레트 (concept/gov/seminar: 9종 무드, whatif/pitch/comparison: 단일 목적 테마) |
    ```

  **3d. Update MUST DO section** (line 303):
  - **Current**: `- [ ] 테마 선택 시 참조 파일(themes/{style}.md) 반드시 로드`
  - **Replace with**: `- [ ] 테마 선택 시 자동 로드된 themes 스킬에서 해당 스타일 섹션 참조`

  **3e. Update Error Handling table** (line 352):
  - **Current**: `| 테마 참조 파일 없음 | 기본값(technical-report) 적용, 경고 메시지 |`
  - **Replace with**: `| 테마 스킬 미로드 | 기본값(technical-report) 적용, 경고 메시지 |`

  **3f. Update MUST NOT DO** (line 313):
  - **Current**: `- [ ] \`${CLAUDE_PLUGIN_ROOT}\` 변수 사용하지 않음 (상대 경로 사용)`
  - **Replace with**: `- [ ] \`${CLAUDE_PLUGIN_ROOT}\` 변수 사용하지 않음 (스킬은 자동 로드, Read 불필요)`

  **Must NOT do**:
  - Do NOT modify any workflow logic (Phase sequence, agent responsibilities)
  - Do NOT change the Theme Moods table (lines 200-230) or Layout Types table (lines 232-278) — these are agent-internal reference, not file paths
  - Do NOT modify the Mood Selection Guide or Layout Selection Guide sections

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Multiple targeted text replacements in a single file — no complexity, just precision
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: Tasks 4-6
  - **Blocked By**: Tasks 1-2

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-organizer.md:155-159` — Phase 3 Step 3-1 Read() to remove
  - `plugins/visual-generator/agents/content-organizer.md:172-174` — Phase 4 Step 4-1 redundant Read() to remove
  - `plugins/visual-generator/agents/content-organizer.md:289-297` — Resources doc table to replace
  - `plugins/visual-generator/agents/content-organizer.md:303` — MUST DO item to update
  - `plugins/visual-generator/agents/content-organizer.md:313` — MUST NOT DO item to update
  - `plugins/visual-generator/agents/content-organizer.md:352` — Error handling row to update

  **WHY Each Reference Matters**:
  - Lines 155-159: Contains the broken `Read(plugins/visual-generator/references/themes/{style}.md)` that fails when agent runs from user CWD — PRIMARY BUG
  - Lines 172-174: Contains redundant `Read(plugins/visual-generator/skills/layout-types/SKILL.md)` — skills are auto-loaded
  - Lines 289-297: Doc table still lists old `references/themes/` paths — must reflect new auto-loaded skill
  - Lines 303, 313, 352: Agent instructions that reference old file-loading behavior — must reflect auto-loading

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: No references to old theme paths
    Tool: Bash (grep)
    Steps:
      1. grep "references/themes" plugins/visual-generator/agents/content-organizer.md
      2. Assert: zero matches
      3. grep "Read(plugins/visual-generator/skills/layout-types" plugins/visual-generator/agents/content-organizer.md
      4. Assert: zero matches

  Scenario: Auto-load instructions present
    Tool: Bash (grep)
    Steps:
      1. grep "자동 로드된 themes 스킬" plugins/visual-generator/agents/content-organizer.md
      2. Assert: at least 2 matches (workflow step + MUST DO)
      3. grep "자동 로드된 layout-types 스킬" plugins/visual-generator/agents/content-organizer.md
      4. Assert: at least 1 match (workflow step)
    Expected Result: Old Read() instructions replaced with auto-load references

  Scenario: Workflow structure preserved
    Tool: Bash (grep)
    Steps:
      1. grep -c "^\[Phase" plugins/visual-generator/agents/content-organizer.md
      2. Assert: 5 (Phase 0 through Phase 5 still present)
      3. grep "Step 3-1" plugins/visual-generator/agents/content-organizer.md
      4. Assert: match found (step exists but with updated content)
    Expected Result: Workflow structure intact, only Read() details changed
  ```

  **Commit**: YES (groups with Tasks 4, 5)
  - Message: `fix(visual-generator): remove broken Read() calls, update docs for auto-loaded skills`
  - Files: `plugins/visual-generator/agents/content-organizer.md`
  - Pre-commit: `grep -c "references/themes" plugins/visual-generator/agents/content-organizer.md` → 0

---

- [ ] 4. Edit prompt-designer.md — Remove broken Read() call, update docs

  **What to do**:

  **4a. Remove Read() at line 258** (Phase 1, Step 1-3: theme file load):
  - **Current** (lines 257-259):
    ```
        +-- Step 1-3. 테마 파일 로드
            +-- Read(plugins/visual-generator/references/themes/{style}.md)
            +-- 해당 theme의 색상 팔레트 추출
    ```
  - **Replace with**:
    ```
        +-- Step 1-3. 테마 팔레트 확인
            +-- 자동 로드된 themes 스킬에서 {style}에 해당하는 섹션 참조
            +-- 해당 theme의 색상 팔레트 추출
    ```

  **4b. Update Theme Reference documentation table** (lines 316-323):
  - **Current**:
    ```markdown
    | 스타일 | 파일 경로 |
    |--------|----------|
    | concept | `plugins/visual-generator/references/themes/concept.md` |
    | gov | `plugins/visual-generator/references/themes/gov.md` |
    | seminar | `plugins/visual-generator/references/themes/seminar.md` |
    | whatif | `plugins/visual-generator/references/themes/whatif.md` |
    | pitch | `plugins/visual-generator/references/themes/pitch.md` |
    | comparison | `plugins/visual-generator/references/themes/comparison.md` |
    ```
  - **Replace with**:
    ```markdown
    > 테마 팔레트는 `themes` 스킬로 등록되어 에이전트 컨텍스트에 자동 로드됩니다. 별도의 Read() 호출이 필요하지 않습니다.
    > 각 스타일에 해당하는 섹션을 참조하세요.

    | 스타일 | SKILL.md 내 섹션 |
    |--------|-----------------|
    | concept | `# Concept 스타일 테마 팔레트` |
    | gov | `# Gov 스타일 테마 팔레트` |
    | seminar | `# Seminar 스타일 테마 팔레트` |
    | whatif | `# What-If (미래 비전 스냅샷) 테마` |
    | pitch | `# Pitch (투자 임팩트) 테마` |
    | comparison | `# Comparison (Before/After 비교) 테마` |
    ```

  **4c. Update MUST DO** (line 377):
  - **Current**: `- [ ] 스타일별 테마 파일에서 정확한 색상 팔레트 추출`
  - **Replace with**: `- [ ] 자동 로드된 themes 스킬에서 해당 스타일 섹션의 정확한 색상 팔레트 추출`

  **Must NOT do**:
  - Do NOT modify the 4-block prompt structure rules
  - Do NOT modify text density rules, rendering prevention rules, or content separation rules
  - Do NOT change the example output

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Targeted text replacements — same pattern as Task 3 but in a different file
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 4)
  - **Blocks**: Tasks 5-6
  - **Blocked By**: Tasks 1-3

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/prompt-designer.md:257-259` — Phase 1 Step 1-3 Read() to remove
  - `plugins/visual-generator/agents/prompt-designer.md:316-323` — Theme Reference doc table to replace
  - `plugins/visual-generator/agents/prompt-designer.md:377` — MUST DO item to update

  **WHY Each Reference Matters**:
  - Lines 257-259: Contains the broken `Read(plugins/visual-generator/references/themes/{style}.md)` — same CWD bug
  - Lines 316-323: Doc table lists old paths per style — must point to SKILL.md sections instead
  - Line 377: Instruction references "테마 파일" — must reference auto-loaded skill

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: No references to old theme paths
    Tool: Bash (grep)
    Steps:
      1. grep "references/themes" plugins/visual-generator/agents/prompt-designer.md
      2. Assert: zero matches

  Scenario: Auto-load instructions present
    Tool: Bash (grep)
    Steps:
      1. grep "자동 로드된 themes 스킬" plugins/visual-generator/agents/prompt-designer.md
      2. Assert: at least 2 matches (workflow step + MUST DO)
    Expected Result: Old Read() replaced with auto-load reference
  ```

  **Commit**: YES (group with Tasks 3, 5)
  - Message: `fix(visual-generator): remove broken Read() calls, update docs for auto-loaded skills`
  - Files: `plugins/visual-generator/agents/prompt-designer.md`
  - Pre-commit: `grep -c "references/themes" plugins/visual-generator/agents/prompt-designer.md` → 0

---

- [ ] 5. Edit content-reviewer.md + visual-generate.md — Update doc tables only

  **What to do**:

  **5a. Edit `content-reviewer.md` — Update Resources table** (lines 384-392):
  - **Current**:
    ```markdown
    | 경로 | 설명 |
    |------|------|
    | `plugins/visual-generator/skills/layout-types/SKILL.md` | 24종 레이아웃 유형 정의 |
    | `plugins/visual-generator/references/themes/concept.md` | concept 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/gov.md` | gov 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/seminar.md` | seminar 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/whatif.md` | whatif 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/pitch.md` | pitch 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/comparison.md` | comparison 목적 테마 (단일 팔레트) |
    ```
  - **Replace with**:
    ```markdown
    > 아래 참조 파일들은 모두 스킬로 등록되어 에이전트 컨텍스트에 자동 로드됩니다.

    | 스킬 | 설명 |
    |------|------|
    | `layout-types` | 24종 레이아웃 유형 정의 |
    | `themes` | 6종 테마 팔레트 (concept/gov/seminar: 9종 무드, whatif/pitch/comparison: 단일 목적 테마) |
    ```

  **5b. Edit `commands/visual-generate.md` — Update Resources table** (lines 258-265):
  - Apply the same pattern: replace old `references/themes/` path table with auto-loaded skill references
  - **Current** (check exact content at runtime — lines ~258-265 should have a similar table):
    ```markdown
    | `plugins/visual-generator/references/themes/concept.md` | concept 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/gov.md` | gov 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/seminar.md` | seminar 스타일 테마 (9종) |
    | `plugins/visual-generator/references/themes/whatif.md` | whatif 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/pitch.md` | pitch 목적 테마 (단일 팔레트) |
    | `plugins/visual-generator/references/themes/comparison.md` | comparison 목적 테마 (단일 팔레트) |
    ```
  - **Replace with** same compact auto-loaded format as 5a

  **Must NOT do**:
  - Do NOT modify review criteria, scoring, or decision logic in content-reviewer.md
  - Do NOT modify workflow/command logic in visual-generate.md

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Two doc table updates, no logic changes
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 5)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 1-4

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/agents/content-reviewer.md:384-392` — Resources doc table to replace
  - `plugins/visual-generator/commands/visual-generate.md:258-265` — Resources doc table to replace
  - Task 3 output (content-organizer.md Resources section) — Follow the same replacement pattern for consistency

  **WHY Each Reference Matters**:
  - content-reviewer lines 384-392: Documentation table listing old `references/themes/` paths — misleading, must update
  - visual-generate lines 258-265: Same stale paths in command documentation
  - Task 3 pattern: Ensure all 4 files use the same updated table format for consistency

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: No old theme paths in either file
    Tool: Bash (grep)
    Steps:
      1. grep "references/themes" plugins/visual-generator/agents/content-reviewer.md
      2. Assert: zero matches
      3. grep "references/themes" plugins/visual-generator/commands/visual-generate.md
      4. Assert: zero matches
    Expected Result: Both files cleaned of old paths

  Scenario: New auto-load notice present
    Tool: Bash (grep)
    Steps:
      1. grep "자동 로드" plugins/visual-generator/agents/content-reviewer.md
      2. Assert: at least 1 match
    Expected Result: Updated documentation references auto-loading
  ```

  **Commit**: YES (group with Tasks 3, 4)
  - Message: `fix(visual-generator): remove broken Read() calls, update docs for auto-loaded skills`
  - Files: `plugins/visual-generator/agents/content-reviewer.md`, `plugins/visual-generator/commands/visual-generate.md`
  - Pre-commit: `grep -rc "references/themes" plugins/visual-generator/` → 0

---

- [ ] 6. Delete references/ directory + Final verification

  **What to do**:

  **6a. Verify references/ contents before deletion**:
  - List all files in `plugins/visual-generator/references/`
  - Confirm exactly 7 files exist:
    1. `themes/concept.md`
    2. `themes/gov.md`
    3. `themes/seminar.md`
    4. `themes/whatif.md`
    5. `themes/pitch.md`
    6. `themes/comparison.md`
    7. `layout_types.md`
  - If ANY unexpected files are found, STOP and report to user

  **6b. Delete the entire references/ directory**:
  - `rm -rf plugins/visual-generator/references/`

  **6c. Run comprehensive final verification** (all scenarios from Verification Strategy above):
  - Verify zero `references/themes` matches in entire `plugins/visual-generator/`
  - Verify zero `references/layout_types` matches in entire `plugins/visual-generator/`
  - Verify `plugins/visual-generator/references/` directory does not exist
  - Verify `plugins/visual-generator/skills/themes/SKILL.md` exists
  - Verify marketplace.json has both skills
  - Verify `renderer-agent.md` unchanged
  - Verify `git diff --name-only` shows only expected files

  **Must NOT do**:
  - Do NOT delete references/ if it contains unexpected files — report and ask user
  - Do NOT use `rm -rf` without first listing contents

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Directory deletion + verification — straightforward bash operations
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 6 — final)
  - **Blocks**: None
  - **Blocked By**: Tasks 1-5

  **References**:

  **Pattern References**:
  - `plugins/visual-generator/references/` — Directory to delete (7 files total)
  - Task 1 output — SKILL.md must exist before deletion (confirms theme content is preserved)

  **WHY Each Reference Matters**:
  - `references/` directory: Contains the files being relocated — must verify contents match expectations before deletion
  - Task 1 dependency: Theme content must already be consolidated in SKILL.md before originals are deleted

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: references/ directory fully removed
    Tool: Bash
    Steps:
      1. test -d plugins/visual-generator/references && echo "FAIL" || echo "PASS"
      2. Assert: "PASS"
    Expected Result: Directory does not exist

  Scenario: Comprehensive path audit
    Tool: Bash (grep)
    Steps:
      1. grep -r "references/" plugins/visual-generator/ 2>/dev/null
      2. Assert: zero matches (no stale references anywhere)
    Expected Result: Zero references to old directory in any file

  Scenario: Only expected files modified (full diff check)
    Tool: Bash (git)
    Steps:
      1. git diff --name-only
      2. Assert: list contains ONLY:
         - .claude-plugin/marketplace.json
         - plugins/visual-generator/agents/content-organizer.md
         - plugins/visual-generator/agents/content-reviewer.md
         - plugins/visual-generator/agents/prompt-designer.md
         - plugins/visual-generator/commands/visual-generate.md
      3. git diff --name-only --diff-filter=A
      4. Assert: plugins/visual-generator/skills/themes/SKILL.md
      5. git diff --name-only --diff-filter=D
      6. Assert: 7 files under plugins/visual-generator/references/
      7. git diff plugins/visual-generator/agents/renderer-agent.md
      8. Assert: empty (unchanged)
    Expected Result: Exactly the planned changes, nothing more
  ```

  **Commit**: YES (standalone — deletion commit)
  - Message: `chore(visual-generator): delete references/ directory (content moved to skills/)`
  - Files: `plugins/visual-generator/references/` (deleted)
  - Pre-commit: `test ! -d plugins/visual-generator/references`

---

## Commit Strategy

| After Task(s) | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1-2 | `refactor(visual-generator): move themes from references/ to skills/ for auto-loading` | `skills/themes/SKILL.md`, `marketplace.json` | `grep '"./skills/themes"' .claude-plugin/marketplace.json` |
| 3-5 | `fix(visual-generator): remove broken Read() calls, update docs for auto-loaded skills` | `content-organizer.md`, `prompt-designer.md`, `content-reviewer.md`, `visual-generate.md` | `grep -rc "references/themes" plugins/visual-generator/` → 0 |
| 6 | `chore(visual-generator): delete references/ directory (content moved to skills/)` | `references/` (deleted) | `test ! -d plugins/visual-generator/references` |

---

## Success Criteria

### Verification Commands
```bash
# 1. No broken references remain
grep -r "references/themes" plugins/visual-generator/
# Expected: zero matches

# 2. No duplicate layout_types reference
grep -r "references/layout_types" plugins/visual-generator/
# Expected: zero matches

# 3. New skill exists and is valid
test -f plugins/visual-generator/skills/themes/SKILL.md && echo "OK"
# Expected: OK

# 4. All 6 themes present
grep -c "^# " plugins/visual-generator/skills/themes/SKILL.md
# Expected: >= 7 (overview + 6 themes)

# 5. marketplace.json updated
grep '"./skills/themes"' .claude-plugin/marketplace.json
# Expected: match

# 6. references/ gone
test -d plugins/visual-generator/references && echo "FAIL" || echo "PASS"
# Expected: PASS

# 7. renderer-agent untouched
git diff plugins/visual-generator/agents/renderer-agent.md
# Expected: empty
```

### Final Checklist
- [ ] All "Must Have" present (6 themes in SKILL.md, marketplace registered, docs updated)
- [ ] All "Must NOT Have" absent (no renderer-agent changes, no AGENTS.md/README.md changes, no content modifications)
- [ ] Zero stale path references in entire visual-generator directory
- [ ] 3 clean commits with descriptive messages

---

## Out of Scope (Explicitly Deferred)

| Item | Reason | When to Address |
|------|--------|-----------------|
| Fix AGENTS.md structure tree (references `prompt-concept/` etc.) | Already stale from prior refactor, unrelated to CWD bug | Separate cleanup task |
| Fix README.md visual-generator section | Same staleness | Separate cleanup task |
| Restructure agent workflow logic | Feature change, not a bug fix | If needed later |
| Add selective theme loading mechanism | Would require plugin system changes | Future enhancement |
