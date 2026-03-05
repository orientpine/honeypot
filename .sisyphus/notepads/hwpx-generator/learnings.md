# hwpx-generator Learnings

## [2026-02-25] Session: ses_36b3577d0ffes3u0vrQ95zfEu6

### Source Repositories
- **Repo 1 (hwpxskill)**: `https://raw.githubusercontent.com/Canine89/hwpxskill/main/` — XML-first core
- **Repo 2 (gonggong_hwpxskills)**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/` — ZIP replacement
- **Repo 3 (hwpxskill-math)**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/` — Math/exam

### Key Architecture Decisions
- 3 Skills: hwpx-core, hwpx-templates, hwpx-math
- 2 Agents: hwpx-builder, hwpx-analyzer
- 1 Command: hwpx-generate
- Template collision fix: Repo3 templates/base/ → renamed to templates/math-base/
- fix_namespaces.py: regex/string approach ONLY (lxml forbidden — ns0 reintroduction risk)
- fix_namespaces.py: only needed for ZIP-level ops, NOT for XML-first builds

### Conventions
- SKILL.md ≤ 500 lines each
- No hardcoded paths (/mnt/skills/, /home/claude/, /mnt/user-data/)
- Scripts fetched from GitHub, NOT self-written
- "skills": ["./skills"] — no trailing slash
- author.email = orientpine@gmail.com

## [2026-02-25] Task 3 script import

- Fetched 6 scripts directly from `Canine89/hwpxskill` raw URLs into `plugins/hwpx-generator/skills/hwpx-core/scripts/`.
- Confirmed no forbidden absolute paths (`/mnt/skills/`, `/home/claude/`, `/mnt/user-data/`) in imported scripts.
- Saved AST validation evidence for all 6 scripts at `.sisyphus/evidence/task-3-scripts-valid.txt`.

## [2026-02-25] Task 2: hwpx-core SKILL.md
- Created  as XML-first core skill.
- Preserved 5 mandatory workflows and compressed guidance to keep SKILL.md maintainable.
- Embedded 3-step script resolution (relative -> Glob fallback -> extended search) with  references only.
- Added 5 template style ID maps (base, gonmun, report, minutes, proposal) and 6-script summary table.
- Kept deep XML explanations delegated to  note instead of inflating core file.

## [2026-02-25] Task 2 correction
- Created plugins/hwpx-generator/skills/hwpx-core/SKILL.md as XML-first core skill.
- Path references use SKILL_DIR consistently; no sandbox hardcoded paths.
- Deep XML details intentionally deferred to references directory notes.

## [2026-02-25] Task 6: hwpx-templates SKILL + fix_namespaces
- Added `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md` with valid frontmatter (`name: hwpx-templates`, `Use when...`).
- Included required template policy, ObjectFinder pre-scan, `zip_replace()`, `zip_replace_sequential()`, and ZIP-level-only namespace post-processing guidance.
- Added mandatory 3-step script resolution flow for `scripts/fix_namespaces.py` (relative -> plugin glob -> extended glob).
- Imported `plugins/hwpx-generator/skills/hwpx-templates/scripts/fix_namespaces.py` using regex (`import re`) and verified no `lxml` import.
- Stored grep evidence at `.sisyphus/evidence/task-6-fix-namespaces-regex.txt`.

## [2026-02-25] Task 9: hwpx-math script import
- Pulled 7 scripts from  raw URLs into .
- Captured AST parse evidence at  (ALL OK).
- Confirmed required count with 7 = 7.

## [2026-02-25] Task 9: hwpx-math script import
- Pulled 7 scripts from Canine89/hwpxskill-math raw URLs into plugins/hwpx-generator/skills/hwpx-math/scripts/.
- Captured AST parse evidence at .sisyphus/evidence/task-9-math-scripts.txt (ALL OK).
- Confirmed required count with ls plugins/hwpx-generator/skills/hwpx-math/scripts/*.py | wc -l = 7.

## [2026-02-25] Task 11: hwpx-builder agent authoring
- Added `plugins/hwpx-generator/agents/hwpx-builder.md` with standard frontmatter (`name`, `description`, `model`) and required sections (Purpose, Capabilities, Workflow, Constraints).
- Encoded routing logic: document type detection -> template selection -> generation path (`hwpx-templates`/`hwpx-core`/`hwpx-math`) -> validation.
- Explicitly documented HWPX-only scope and mandatory `hwpx-core/scripts/validate.py` execution.
- Stored proof artifact at `.sisyphus/evidence/task-11-builder-agent.txt` with header snapshot and skill reference count.


## [2026-02-25] Task 12: hwpx-analyzer agent authoring
- Added  with required frontmatter (, , ) and sections (Purpose, Capabilities, Workflow, Constraints).
- Workflow explicitly anchors reference-based analysis path:  intake ->  ->  ID map -> analysis report -> generation/edit branch.
- Constraints lock HWPX-only scope and preserve original style IDs with / consistency.
- Saved verification artifact at .


## [2026-02-25] Task 12 correction
- Added plugins/hwpx-generator/agents/hwpx-analyzer.md with required frontmatter fields (name, description, model) and all required sections.
- Workflow explicitly includes scripts/analyze_template.py and header.xml style-map extraction before report and branch execution.
- Constraints enforce HWPX-only handling and preservation of charPrIDRef and paraPrIDRef consistency.
- Verification evidence stored at .sisyphus/evidence/task-12-analyzer-agent.txt with analyze_template reference count >= 1.

## [2026-02-25] Task 13: hwpx-generate command authoring
- Added `plugins/hwpx-generator/commands/hwpx-generate.md` without frontmatter, following command-orchestrator style.
- Implemented Phase 1-5 flow with required delegation points: `hwpx-generator::hwpx-analyzer` and `hwpx-generator::hwpx-builder` via Task tool.
- Embedded strict format-selection priority (user template > default template > XML-first) and mandatory `validate.py` verification phase.
- Saved proof artifact at `.sisyphus/evidence/task-13-command.txt` (head snapshot + Task/subagent_type count + ARGUMENTS count).
