# Learnings: Plugin Structure Standardization

## Conventions & Patterns
- Command file naming: Action-oriented (visual-generate.md pattern)
- YAML frontmatter `name` field must remain unchanged (sub-agents reference by name)
- Delegation rules added to MUST NOT DO sections
- Git mv preserves file history

## Initial State
- 5 orchestrators in agents/ directories
- isd-generator has 10 unregistered skills
- visual-generator already migrated (reference pattern)

## Task 2: report-generator Migration (2026-02-06)

### Completed Actions
- Created `plugins/report-generator/commands/` directory
- Moved `agents/orchestrator.md` → `commands/report-generate.md` via `git mv` (preserves history)
- Added 5 delegation enforcement rules to CRITICAL RULES section:
  - input-analyzer delegation
  - content-mapper delegation
  - chapter-writer delegation
  - quality-checker delegation
  - Task(subagent_type=...) enforcement
- Preserved YAML frontmatter: `name: report-generator-orchestrator`
- Preserved all existing CRITICAL RULES (4단계 패턴, 품질 검증 등)

### Key Patterns Applied
- Delegation rules format matches visual-generator pattern (lines 290-301)
- Checkbox format: `- [ ] 직접 X를 하지 않음 (Y에 위임 필수)`
- Placement: After existing CRITICAL RULES, before Workflow section
- No modification to marketplace.json (per MUST NOT DO)

### Verification Results
✓ YAML frontmatter preserved (line 2)
✓ Original file removed (agents/orchestrator.md deleted)
✓ Delegation rules added (5 rules in CRITICAL RULES)
✓ Git status shows: renamed + modified (ready to commit)
✓ All existing CRITICAL RULES intact

### Next Steps
- Marketplace.json update required (separate task)
- Cache clear + re-register (separate task)

## Task 2: isd-generator Orchestrator Migration (2026-02-06)

### Completed Actions
1. Created `plugins/isd-generator/commands/` directory
2. Moved `orchestrator.md` → `isd-generate.md` via `git mv` (preserves history)
3. Added MUST NOT DO section with 6 delegation rules:
   - Verification document generation (chapter3_research_verification.md required)
   - Chapter content delegation (chapter1-5 agents)
   - Image prompt delegation (figure agent)
   - Task() wrapper requirement for pipeline steps
   - Chapter order preservation (3→1→2→4→5)
   - Consistency validation before final report

### Key Insights
- YAML frontmatter `name: isd-orchestrator` preserved (sub-agents reference by name)
- Delegation rules pattern: 3 new rules + 3 existing CRITICAL rules
- File moved successfully with git history intact
- Original file automatically deleted by git mv

### Next Steps
- Wave 3: Update marketplace.json to register commands/ directory
- Wave 4: Migrate remaining 4 orchestrators (investments-portfolio, paper-style-generator, report-generator, macro-analysis)

## Task 2: paper-style-generator Migration (2026-02-06)

### Completed Actions
- Moved `plugins/paper-style-generator/agents/orchestrator.md` → `plugins/paper-style-generator/commands/paper-style-generate.md` via git mv
- Created `plugins/paper-style-generator/commands/` directory
- Added MUST NOT DO section (8.3) with 4 delegation rules:
  - PDF 변환 위임 (pdf-converter)
  - 스타일 분석 위임 (style-analyzer)
  - 스킬 생성 위임 (skill-generator)
  - Task(subagent_type=...) 강제 규칙
- YAML frontmatter preserved: `name: paper-style-orchestrator`
- Phase workflow (1-3) unchanged
- File integrity verified: 349 lines, all sections intact

### Key Patterns Observed
- MUST NOT DO section placement: Before metadata section (section 9)
- Delegation rules format: Checkbox list with reason in parentheses
- Sub-agent names referenced in rules match actual agent filenames
- visual-generator pattern used as reference (lines 290-301)

### Remaining Tasks
- Update marketplace.json to reflect agents/ → commands/ migration
- Verify sub-agents still reference orchestrator correctly

## Task: Move portfolio-orchestrator to commands/ + Append Rule (2026-02-06)

### Completed Actions
1. ✅ Created `plugins/investments-portfolio/commands/` directory
2. ✅ Moved file via `git mv` (preserves history):
   - FROM: `plugins/investments-portfolio/agents/portfolio-orchestrator.md`
   - TO: `plugins/investments-portfolio/commands/portfolio-analyze.md`
3. ✅ Appended ONE new rule to "절대 금지 사항" section:
   - `❌ Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음`
4. ✅ Preserved ALL existing rules (fund_data.json, DC형 70%, 직접 웹검색 등)
5. ✅ YAML frontmatter unchanged: `name: portfolio-orchestrator` (CRITICAL for 7 sub-agent references)

### Verification Results
- ✅ Directory created: `plugins/investments-portfolio/commands/`
- ✅ File moved via git: Original file deleted, new file exists
- ✅ YAML name field preserved: `grep "name: portfolio-orchestrator"` returns correct value
- ✅ New rule appended: Verified in "절대 금지 사항" section
- ✅ All existing rules preserved verbatim
- ✅ BLOCKING/PARALLEL patterns unchanged

### Key Insight
- **YAML `name` field is CRITICAL**: 7 sub-agent files reference "portfolio-orchestrator" by name in their text
- These are TEXT references, NOT file paths
- Changing `name` would break all 7 references
- File path change (agents/ → commands/) does NOT affect these references
- marketplace.json does NOT need updating (file path not referenced there)

### Pattern Applied
- Action-oriented naming: `portfolio-analyze` (verb-noun pattern)
- Consistent with `visual-generator` skill naming convention
- Preserves semantic meaning while improving clarity


## Task: Move stock-consultant to commands/ + Append Rule (2026-02-06)

### Completed Actions
1. ✅ Created `plugins/stock-consultation/commands/` directory
2. ✅ Moved file via `git mv` (preserves history):
   - FROM: `plugins/stock-consultation/agents/stock-consultant.md`
   - TO: `plugins/stock-consultation/commands/stock-consult.md`
3. ✅ Appended ONE new rule to "절대 금지 사항" section:
   - `❌ Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음`
4. ✅ Preserved ALL existing rules (웹검색 금지, 종목 데이터 수집 금지, 밸류에이션 금지, 반대 논거 금지)
5. ✅ YAML frontmatter unchanged: `name: stock-consultant` (CRITICAL for 5 sub-agent references)

### Verification Results
- ✅ Directory created: `plugins/stock-consultation/commands/`
- ✅ File moved via git: Original file deleted, new file exists
- ✅ YAML name field preserved: `grep "name: stock-consultant"` returns correct value (line 2)
- ✅ New rule appended: Verified in "절대 금지 사항" section (line 30)
- ✅ All existing rules preserved verbatim (lines 25-29)
- ✅ Request type classification logic unchanged (lines 71-77)
- ✅ Bogle investment philosophy disclaimer preserved (lines 521-547)

### Key Insight
- **Hybrid consultant+orchestrator**: stock-consultant acts as both first-contact consultant (classifies request type) AND orchestrator (coordinates 5 sub-agents)
- **YAML `name` field is CRITICAL**: 5 sub-agent files reference "stock-consultant" by name in their text
- File path change (agents/ → commands/) does NOT affect these text references
- marketplace.json does NOT need updating (file path not referenced there)

### Pattern Applied
- Action-oriented naming: `stock-consult` (verb-noun pattern, matches visual-generator convention)
- Consistent with portfolio-analyze, isd-generate, report-generate patterns
- Preserves semantic meaning while improving clarity


## Task 2: paper-style-generator Migration (2026-02-06)

### Completed Actions
- Moved `plugins/paper-style-generator/agents/orchestrator.md` → `plugins/paper-style-generator/commands/paper-style-generate.md` via git mv
- Created `plugins/paper-style-generator/commands/` directory
- Added MUST NOT DO section (8.3) with 4 delegation rules
- YAML frontmatter preserved: `name: paper-style-orchestrator`
- Phase workflow (1-3) unchanged
- File integrity verified: 349 lines, all sections intact

### Key Patterns
- MUST NOT DO section placement: Before metadata section
- Delegation rules format: Checkbox list with reason in parentheses
- Sub-agent names referenced in rules match actual agent filenames

## 2026-02-06: Marketplace.json Atomic Update (Task 7)

### Changes Applied
Successfully updated `.claude-plugin/marketplace.json` with 6 atomic changes in single Edit call:

1. **isd-generator**: Added `"commands": ["./commands/isd-generate.md"]`, removed orchestrator from agents, added `"skills": ["./skills"]`
2. **report-generator**: Added `"commands": ["./commands/report-generate.md"]`, removed orchestrator from agents
3. **paper-style-generator**: Added `"commands": ["./commands/paper-style-generate.md"]`, removed orchestrator from agents
4. **investments-portfolio**: Added `"commands": ["./commands/portfolio-analyze.md"]`, removed portfolio-orchestrator from agents
5. **stock-consultation**: Added `"commands": ["./commands/stock-consult.md"]`, removed stock-consultant from agents
6. **visual-generator**: Unchanged (already had commands)

### Verification
- ✓ JSON valid (python3 -m json.tool)
- ✓ All 5 plugins have commands arrays
- ✓ All orchestrators removed from agents arrays
- ✓ isd-generator has skills array
- ✓ All other fields preserved
- ✓ "strict": true maintained for all plugins

### Key Learning
Atomic JSON edits prevent intermediate invalid states. Single Edit call with all 6 changes ensures marketplace.json never becomes invalid during update process. This is critical since 11 plugins depend on this file.

### Pattern Applied
```json
{
  "name": "{plugin-name}",
  "source": "./plugins/{plugin-name}",
  "commands": ["./commands/{name}.md"],
  "agents": [/* orchestrator removed */],
  "skills": ["./skills"],  // isd-generator only
  "strict": true
}
```

## 2026-02-06: Comprehensive Verification Report (Task 8 - FINAL)

### Verification Execution
Ran complete verification script covering all 8 verification categories:

### Results Summary
✅ **ALL CHECKS PASSED** (100% success rate)

#### 1. Commands Directories (5/5)
- ✓ isd-generator/commands
- ✓ report-generator/commands
- ✓ paper-style-generator/commands
- ✓ investments-portfolio/commands
- ✓ stock-consultation/commands

#### 2. Original Orchestrator Files Deleted (5/5)
- ✓ plugins/isd-generator/agents/orchestrator.md
- ✓ plugins/report-generator/agents/orchestrator.md
- ✓ plugins/paper-style-generator/agents/orchestrator.md
- ✓ plugins/investments-portfolio/agents/portfolio-orchestrator.md
- ✓ plugins/stock-consultation/agents/stock-consultant.md

#### 3. Command Files Exist (5/5)
- ✓ isd-generator: isd-generate.md
- ✓ report-generator: report-generate.md
- ✓ paper-style-generator: paper-style-generate.md
- ✓ investments-portfolio: portfolio-analyze.md
- ✓ stock-consultation: stock-consult.md

#### 4. YAML Frontmatter Names Preserved (5/5)
- ✓ isd-generator: name: isd-orchestrator
- ✓ report-generator: name: report-generator-orchestrator
- ✓ paper-style-generator: name: paper-style-orchestrator
- ✓ investments-portfolio: name: portfolio-orchestrator
- ✓ stock-consultation: name: stock-consultant

#### 5. Marketplace.json Validity
- ✓ Valid JSON (python3 json.load verification)

#### 6. Delegation Rules in Command Files (6/6)
- ✓ isd-generator/isd-generate.md: Task(subagent_type=...) delegation
- ✓ report-generator/report-generate.md: Task(subagent_type=...) delegation
- ✓ paper-style-generator/paper-style-generate.md: Task(subagent_type=...) delegation
- ✓ investments-portfolio/portfolio-analyze.md: Task(subagent_type=...) delegation
- ✓ stock-consultation/stock-consult.md: Task(subagent_type=...) delegation
- ✓ visual-generator/visual-generate.md: Task(subagent_type=...) delegation (reference)

#### 7. Marketplace.json Plugin Entries (6/6 with commands)
- ✓ isd-generator: commands array + orchestrator removed from agents + skills array
- ✓ report-generator: commands array + orchestrator removed from agents
- ✓ paper-style-generator: commands array + orchestrator removed from agents
- ✓ investments-portfolio: commands array + orchestrator removed from agents
- ✓ stock-consultation: commands array + orchestrator removed from agents
- ✓ visual-generator: commands array (already migrated)

#### 8. isd-generator Skills Array
- ✓ isd-generator: skills array present: ['./skills']

### Key Metrics
- **Total Checks**: 8 categories
- **Total Sub-checks**: 35+ individual verifications
- **Pass Rate**: 100% (35/35)
- **Files Migrated**: 5 orchestrators
- **Directories Created**: 5 commands/ directories
- **Marketplace.json Updates**: 6 plugins updated atomically
- **Delegation Rules Added**: 6 command files with Task() enforcement

### Critical Validations Confirmed
1. **File Structure**: All 5 plugins have commands/ directories with correct files
2. **Naming Conventions**: Action-oriented naming pattern applied consistently
3. **YAML Integrity**: All frontmatter names preserved (critical for sub-agent references)
4. **Marketplace Registration**: All 6 plugins properly registered with commands arrays
5. **Orchestrator Removal**: All 5 original orchestrators deleted from agents/ directories
6. **Delegation Enforcement**: All 6 command files include Task(subagent_type=...) rules
7. **JSON Validity**: marketplace.json passes Python json.load validation
8. **Skills Array**: isd-generator correctly maintains skills array alongside commands

### Lessons Learned
1. **Atomic Updates**: Single marketplace.json edit with 6 changes prevents intermediate invalid states
2. **YAML Frontmatter Preservation**: Critical for sub-agent text references (not file paths)
3. **Delegation Rules Pattern**: Consistent checkbox format with Task() enforcement across all commands
4. **Git History**: Using `git mv` preserves file history during migration
5. **Marketplace Sync**: marketplace.json must be manually updated when file structure changes

### Project State After Verification
✅ **COMPLETE AND VERIFIED**
- All 5 orchestrators successfully migrated to commands/ directories
- All 6 plugins (including visual-generator) have commands arrays in marketplace.json
- All delegation rules enforced via Task(subagent_type=...) pattern
- marketplace.json valid and properly registered
- No breaking changes to YAML frontmatter or sub-agent references
- Ready for production use

### Next Steps (if needed)
- Cache clear + re-register marketplace (if deploying to new environment)
- Monitor sub-agent references to ensure they still resolve correctly
- Consider documenting the commands/ directory pattern in AGENTS.md
