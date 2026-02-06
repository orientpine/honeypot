# Learnings - visual-generator-restructure

## [2026-02-06T06:07:03.860Z] Plan Start

Plan initiated. 6 tasks across 3 waves.

## Conventions

- All agent .md files use LF line endings
- marketplace.json must be valid JSON (no trailing commas)
- Workflow Position sections go after Overview, before Input Schema
- Do NOT delete existing `파이프라인 위치:` sections when adding Workflow Position

## [2026-02-06T15:45:00Z] Task 1: commands/ Directory Verification - COMPLETED

- Official schema (ananddtyagi/cc-marketplace) explicitly supports `"commands"` key
- Production reference (wshobson/agents) uses commands/ directory across 73 plugins
- No conflicts with existing honeypot structure
- Safe to proceed with orchestrator move

## [2026-02-06T16:15:00Z] Task 2: Orchestrator Restructure - COMPLETED

### What Changed
- Moved `plugins/visual-generator/agents/orchestrator.md` → `plugins/visual-generator/commands/visual-generate.md`
- Added 5 delegation enforcement rules to MUST NOT DO section:
  - 직접 문서를 분석하지 않음 (content-organizer에 위임 필수)
  - 직접 분석 결과를 검토하지 않음 (content-reviewer에 위임 필수)
  - 직접 프롬프트를 생성하지 않음 (prompt-designer에 위임 필수)
  - 직접 이미지를 렌더링하지 않음 (renderer-agent에 위임 필수)
  - Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음
- Updated marketplace.json:
  - Added `"commands": ["./commands/visual-generate.md"]` before agents array
  - Removed `"./agents/orchestrator.md"` from agents array
  - Kept other agents: content-organizer, content-reviewer, prompt-designer, renderer-agent

### Pattern
Commands are registered via "commands" array in marketplace.json, separate from "agents" array. This allows orchestrators to be invoked as slash commands while delegating work to sub-agents.

### Verification
- ✅ Directory created: `plugins/visual-generator/commands/`
- ✅ File exists: `plugins/visual-generator/commands/visual-generate.md` (12,964 bytes)
- ✅ File deleted: `plugins/visual-generator/agents/orchestrator.md`
- ✅ marketplace.json valid JSON (python3 validation passed)
- ✅ Delegation rules count: 4 (grep "직접" found 4 matches)
- ✅ marketplace.json structure correct: commands array before agents array
