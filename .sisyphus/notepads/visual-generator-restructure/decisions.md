# Decisions - visual-generator-restructure

## [2026-02-06T06:07:03.860Z] Plan Start

### Key Architectural Decisions

1. **strict: true → false REJECTED**: User explicitly excluded this change. content-reviewer needs Write tool added, not blanket permission via strict: false.

2. **commands/ directory**: Contingent on Task 1 verification. Will conditionally move orchestrator.md → commands/visual-generate.md if supported.

3. **Theme reference files excluded**: No modifications to `references/themes/*.md` files.

## Pending Decisions

- **Task 1**: commands/ directory support verification outcome (TBD)

## [2026-02-06T15:45:00Z] Task 1: commands/ Directory Verification - COMPLETED

### Evidence Collected

#### Source 1: wshobson/agents marketplace.json (Production Reference)
- **URL**: https://raw.githubusercontent.com/wshobson/agents/main/.claude-plugin/marketplace.json
- **Finding**: Uses `"commands"` key in plugin entries
- **Example**: 
  ```json
  {
    "name": "code-documentation",
    "commands": ["./commands/doc-generate.md", "./commands/code-explain.md"],
    "agents": [...]
  }
  ```
- **Status**: ACTIVE PRODUCTION USE - 73 plugins, 112 agents, 146 skills

#### Source 2: Official Plugin Schema (ananddtyagi/cc-marketplace)
- **URL**: https://raw.githubusercontent.com/ananddtyagi/cc-marketplace/main/PLUGIN_SCHEMA.md
- **Finding**: Official schema explicitly documents `commands/` directory support
- **Key Quote**: 
  ```
  ### `commands/`
  Contains command definition files (`.md` format). Each file defines a custom slash command.
  ```
- **Schema Field**: `"commands"` (string or array of strings) - Custom command locations
- **Status**: OFFICIAL SPECIFICATION

#### Source 3: Local honeypot marketplace.json
- **Path**: `/home/cha/Documents/honeypot/.claude-plugin/marketplace.json`
- **Finding**: Currently uses ONLY `"agents"` and `"skills"` keys
- **Status**: Never used `"commands"` key (as noted in plan line 38)

### Decision

**✅ commands/ directory: FULLY SUPPORTED**

Claude Code marketplace.json schema officially supports:
1. `"commands"` key in plugin entries
2. `commands/` directory structure
3. Command definition files in `.md` format (same as agents)

### Reasoning

1. **Official Schema**: ananddtyagi/cc-marketplace PLUGIN_SCHEMA.md is the authoritative specification
2. **Production Validation**: wshobson/agents uses this pattern actively across 73 plugins
3. **No Conflicts**: `"commands"` is a distinct key from `"agents"` and `"skills"` - no namespace collision
4. **Consistent Format**: Commands use same `.md` file format as agents

### Impact on Task 2

**PROCEED WITH MOVE**: 
- Move `plugins/visual-generator/agents/orchestrator.md` → `plugins/visual-generator/commands/visual-generate.md`
- Update marketplace.json entry for visual-generator:
  ```json
  "commands": ["./commands/visual-generate.md"],
  "agents": [
    "./agents/content-organizer.md",
    "./agents/content-reviewer.md",
    "./agents/prompt-designer.md",
    "./agents/renderer-agent.md"
  ]
  ```
- This change is SAFE and SUPPORTED by official schema

### Verification Checklist

- [x] Official schema documentation found and reviewed
- [x] Production reference implementation verified (wshobson/agents)
- [x] No conflicts with existing honeypot structure
- [x] Command format matches agent format (.md files)
- [x] Decision backed by multiple authoritative sources
