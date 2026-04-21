---
name: plugin-structure
description: "Scaffold and organize Claude Code plugins with the correct directory layout, plugin.json manifest, component types (commands, agents, skills, hooks, MCP servers), portable path references, and auto-discovery conventions. Use when creating a plugin, setting up plugin.json, organizing plugin components, configuring auto-discovery, or using ${CLAUDE_PLUGIN_ROOT}."
---

# Plugin Structure for Claude Code

## Overview

Claude Code plugins follow a standardized directory structure with automatic component discovery. Understanding this structure enables creating well-organized, maintainable plugins that integrate seamlessly with Claude Code.

**Key concepts:**
- Conventional directory layout for automatic discovery
- Manifest-driven configuration in `.claude-plugin/plugin.json`
- Component-based organization (commands, agents, skills, hooks)
- Portable path references using `${CLAUDE_PLUGIN_ROOT}`
- Explicit vs. auto-discovered component loading

## Directory Structure

Every Claude Code plugin follows this organizational pattern:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: Plugin manifest
├── commands/                 # Slash commands (.md files)
├── agents/                   # Subagent definitions (.md files)
├── skills/                   # Agent skills (subdirectories)
│   └── skill-name/
│       └── SKILL.md         # Required for each skill
├── hooks/
│   └── hooks.json           # Event handler configuration
├── .mcp.json                # MCP server definitions
└── scripts/                 # Helper scripts and utilities
```

**Critical rules:**

1. **Manifest location**: The `plugin.json` manifest MUST be in `.claude-plugin/` directory
2. **Component locations**: All component directories (commands, agents, skills, hooks) MUST be at plugin root level, NOT nested inside `.claude-plugin/`
3. **Optional components**: Only create directories for components the plugin actually uses
4. **Naming convention**: Use kebab-case for all directory and file names

## Plugin Manifest (plugin.json)

The manifest defines plugin metadata and configuration. Located at `.claude-plugin/plugin.json`:

### Required Fields

```json
{
  "name": "plugin-name"
}
```

**Name requirements:** kebab-case, unique across installed plugins (e.g. `code-review-assistant`, `test-runner`).

### Recommended Metadata

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief explanation of plugin purpose",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/user/plugin-name",
  "license": "MIT",
  "keywords": ["testing", "automation", "ci-cd"]
}
```

### Component Path Configuration

Specify custom paths for components (supplements default directories):

```json
{
  "name": "plugin-name",
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**Important**: Custom paths supplement defaults—they don't replace them. Paths must be relative (start with `./`) and support arrays for multiple locations.

## Component Organization

### Commands

**Location**: `commands/` directory
**Format**: Markdown files with YAML frontmatter
**Auto-discovery**: All `.md` files in `commands/` load automatically

**Example structure**:
```
commands/
├── review.md        # /review command
├── test.md          # /test command
└── deploy.md        # /deploy command
```

**File format**:
```markdown
---
name: command-name
description: Command description
---

Command implementation instructions...
```

**Usage**: Commands integrate as native slash commands in Claude Code

### Agents

**Location**: `agents/` directory
**Format**: Markdown files with YAML frontmatter
**Auto-discovery**: All `.md` files in `agents/` load automatically

**Example structure**:
```
agents/
├── code-reviewer.md
├── test-generator.md
└── refactorer.md
```

**File format**:
```markdown
---
description: Agent role and expertise
capabilities:
  - Specific task 1
  - Specific task 2
---

Detailed agent instructions and knowledge...
```

**Usage**: Users can invoke agents manually, or Claude Code selects them automatically based on task context

### Skills

**Location**: `skills/` directory with subdirectories per skill
**Format**: Each skill in its own directory with `SKILL.md` file
**Auto-discovery**: All `SKILL.md` files in skill subdirectories load automatically

**Example structure**:
```
skills/
├── api-testing/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── test-runner.py
│   └── references/
│       └── api-spec.md
└── database-migrations/
    ├── SKILL.md
    └── examples/
        └── migration-template.sql
```

**SKILL.md format**:
```markdown
---
name: Skill Name
description: When to use this skill
version: 1.0.0
---

Skill instructions and guidance...
```

**Supporting files**: Skills can include scripts, references, examples, or assets in subdirectories

**Usage**: Claude Code autonomously activates skills based on task context matching the description

### Hooks

**Location**: `hooks/hooks.json` or inline in `plugin.json`
**Format**: JSON configuration defining event handlers
**Registration**: Hooks register automatically when plugin enables

**Example structure**:
```
hooks/
├── hooks.json           # Hook configuration
└── scripts/
    ├── validate.sh      # Hook script
    └── check-style.sh   # Hook script
```

**Configuration format**:
```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.sh",
      "timeout": 30
    }]
  }]
}
```

**Available events**: PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification

**Usage**: Hooks execute automatically in response to Claude Code events

### MCP Servers

**Location**: `.mcp.json` at plugin root or inline in `plugin.json`
**Format**: JSON configuration for MCP server definitions
**Auto-start**: Servers start automatically when plugin enables

**Example format**:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**Usage**: MCP servers integrate seamlessly with Claude Code's tool system

## Portable Path References

### ${CLAUDE_PLUGIN_ROOT}

Use `${CLAUDE_PLUGIN_ROOT}` environment variable for all intra-plugin path references:

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh"
}
```

**Where to use it**:
- Hook command paths
- MCP server command arguments
- Script execution references
- Resource file paths

**Never use**: hardcoded absolute paths, relative paths from working directory, or home directory shortcuts (`~/`).

### Path Resolution Rules

**In manifest JSON fields** (hooks, MCP servers):
```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/tool.sh"
```

**In component files** (commands, agents, skills):
```markdown
Reference scripts at: ${CLAUDE_PLUGIN_ROOT}/scripts/helper.py
```

**In executed scripts**:
```bash
#!/bin/bash
# ${CLAUDE_PLUGIN_ROOT} available as environment variable
source "${CLAUDE_PLUGIN_ROOT}/lib/common.sh"
```

## File Naming Conventions

### Component Files

**Commands**: Use kebab-case `.md` files
- `code-review.md` → `/code-review`
- `run-tests.md` → `/run-tests`
- `api-docs.md` → `/api-docs`

**Agents**: Use kebab-case `.md` files describing role
- `test-generator.md`
- `code-reviewer.md`
- `performance-analyzer.md`

**Skills**: Use kebab-case directory names
- `api-testing/`
- `database-migrations/`
- `error-handling/`

All supporting files (scripts, docs, config) should also use kebab-case naming.

## Auto-Discovery Mechanism

Claude Code automatically discovers components when a plugin is enabled — no restart required, changes take effect on next session. Custom paths in `plugin.json` supplement (not replace) default directories.

## Best Practices

- **Minimal manifest**: Rely on auto-discovery for standard layouts; only specify custom paths when necessary.
- **Consistent naming**: If a command is `test-runner`, name the related agent `test-runner-agent`. Match skill directory names to their purpose.
- **Descriptive names**: Good: `api-integration-testing/`, `code-quality-checker.md`. Avoid: `utils/`, `misc.md`.
- **Always use `${CLAUDE_PLUGIN_ROOT}`**: Never hardcode paths. Document external dependencies.

## Common Patterns

### Minimal Plugin

Single command with no dependencies:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # Just name field
└── commands/
    └── hello.md       # Single command
```

### Full-Featured Plugin

Complete plugin with all component types:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # User-facing commands
├── agents/            # Specialized subagents
├── skills/            # Auto-activating skills
├── hooks/             # Event handlers
│   ├── hooks.json
│   └── scripts/
├── .mcp.json          # External integrations
└── scripts/           # Shared utilities
```

### Skill-Focused Plugin

Plugin providing only skills:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    └── skill-two/
        └── SKILL.md
```

## Troubleshooting

**Component not loading**:
- Verify file is in correct directory with correct extension
- Check YAML frontmatter syntax (commands, agents, skills)
- Ensure skill has `SKILL.md` (not `README.md` or other name)
- Confirm plugin is enabled in Claude Code settings

**Path resolution errors**:
- Replace all hardcoded paths with `${CLAUDE_PLUGIN_ROOT}`
- Verify paths are relative and start with `./` in manifest
- Check that referenced files exist at specified paths
- Test with `echo $CLAUDE_PLUGIN_ROOT` in hook scripts

**Auto-discovery not working**:
- Confirm directories are at plugin root (not in `.claude-plugin/`)
- Check file naming follows conventions (kebab-case, correct extensions)
- Verify custom paths in manifest are correct
- Restart Claude Code to reload plugin configuration

**Conflicts between plugins**:
- Use unique, descriptive component names
- Namespace commands with plugin name if needed
- Document potential conflicts in plugin README
- Consider command prefixes for related functionality

---

For detailed examples and advanced patterns, see files in `references/` and `examples/` directories.
