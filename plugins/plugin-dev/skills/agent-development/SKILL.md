---
name: Agent Development
description: This skill should be used when the user asks to "create an agent", "add an agent", "write a subagent", "agent frontmatter", "when to use description", "agent examples", "agent tools", "agent colors", "autonomous agent", or needs guidance on agent structure, system prompts, triggering conditions, or agent development best practices for Claude Code plugins.
version: 0.1.0
---

# Agent Development for Claude Code Plugins

## Overview

Agents are autonomous subprocesses that handle complex, multi-step tasks independently. Understanding agent structure, triggering conditions, and system prompt design enables creating powerful autonomous capabilities.

**Key concepts:**
- Agents are FOR autonomous work, commands are FOR user-initiated actions
- Markdown file format with YAML frontmatter
- Triggering via description field with examples
- System prompt defines agent behavior
- Model, effort, and tool access are optional refinements

## Agent File Structure

### Complete Format

```markdown
---
name: agent-identifier
description: Use this agent when [triggering conditions]. Examples:

<example>
Context: [Situation description]
user: "[User request]"
assistant: "[How assistant should respond and use this agent]"
<commentary>
[Why this agent should be triggered]
</commentary>
</example>

<example>
[Additional example...]
</example>

model: inherit                      # optional (default: inherit)
effort: medium                      # optional
tools: ["Read", "Write", "Grep"]    # optional
color: blue                         # optional
---

You are [agent role description]...

**Your Core Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]

**Analysis Process:**
[Step-by-step workflow]

**Output Format:**
[What to return]
```

## Frontmatter Fields

### name (required)

Agent identifier used for namespacing and invocation.

**Format:** lowercase, numbers, hyphens only
**Length:** 3-50 characters
**Pattern:** Must start and end with alphanumeric

**Good examples:**
- `code-reviewer`
- `test-generator`
- `api-docs-writer`
- `security-analyzer`

**Bad examples:**
- `helper` (too generic)
- `-agent-` (starts/ends with hyphen)
- `my_agent` (underscores not allowed)
- `ag` (too short, < 3 chars)

### description (required)

Defines when Claude should trigger this agent. **This is the most critical field.**

**Must include:**
1. Triggering conditions ("Use this agent when...")
2. Multiple `<example>` blocks showing usage
3. Context, user request, and assistant response in each example
4. `<commentary>` explaining why agent triggers

**Format:**
```
Use this agent when [conditions]. Examples:

<example>
Context: [Scenario description]
user: "[What user says]"
assistant: "[How Claude should respond]"
<commentary>
[Why this agent is appropriate]
</commentary>
</example>

[More examples...]
```

**Best practices:**
- Include 2-4 concrete examples
- Show proactive and reactive triggering
- Cover different phrasings of same intent
- Explain reasoning in commentary
- Be specific about when NOT to use the agent

### model (optional)

Which model the agent should use. **Not required** — when omitted the agent inherits the parent session's model (`inherit`).

**Two kinds of values:**

| Value kind | Examples | Behavior |
|------------|----------|----------|
| Alias | `inherit`, `sonnet`, `opus`, `haiku`, `fable` | **Rolls forward** — always resolves to the newest model in that family |
| Full model ID | `claude-opus-5`, `claude-sonnet-4-6` | **Pins** one specific generation — never changes |

**Aliases:**
- `inherit` - Same model as the parent session (default)
- `sonnet` - Balanced capability and cost
- `opus` - High capability
- `haiku` - Fast and cheap
- `fable` - Most capable, but **opt-in only**: it is not available on every account or provider and it bills usage credits. Never set it as a default (기본값으로 쓰지 마십시오).

**Alias vs. pinned ID — the tradeoff:**

Aliases roll forward. On the Anthropic API `opus` currently resolves to Opus 5, `sonnet` to Sonnet 5, and `haiku` to Haiku 4.5, and those mappings move as new models ship. A full ID such as `claude-opus-5` pins that exact generation permanently. Provider mapping also differs on Bedrock / Vertex / Foundry, so an ID that resolves for one user may not exist for another.

**For distributed marketplace plugins, use aliases.** Pin a full ID only when one specific generation's behavior is a hard requirement, and expect to maintain it as models change. The official `anthropics/claude-code` plugins ship `model: opus` and `wshobson/agents` ships `model: sonnet` — rolling aliases are the norm for distributable plugins.

**Recommendation:** Omit the field (or use `inherit`) unless the agent needs specific model capabilities.

### effort (optional)

Reasoning effort for the agent — how much the model thinks before acting.

**Options:** `low`, `medium`, `high`, `xhigh`, `max`

Availability depends on the selected model; not every model supports every level. Omit the field to use the model's default.

```yaml
effort: high
```

### color (optional)

Visual identifier for the agent in the UI. **Not required** — Claude Code assigns one when omitted.

**Options:** `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`

**Guidelines:**
- Choose distinct colors for different agents in same plugin
- Use consistent colors for similar agent types
- Blue/cyan: Analysis, review
- Green: Success-oriented tasks
- Yellow: Caution, validation
- Red: Critical, security
- Magenta: Creative, generation

### tools (optional)

Restrict agent to specific tools.

**Format:** Array of tool names

```yaml
tools: ["Read", "Write", "Grep", "Bash"]
```

**Default:** If omitted, agent has access to all tools

**Best practice:** Limit tools to minimum needed (principle of least privilege)

**Common tool sets:**
- Read-only analysis: `["Read", "Grep", "Glob"]`
- Code generation: `["Read", "Write", "Grep"]`
- Testing: `["Read", "Bash", "Grep"]`
- Full access: Omit field or use `["*"]`

### disallowedTools (optional)

Blocklist counterpart to `tools`. Use it to keep broad access while removing a few dangerous tools.

```yaml
disallowedTools: ["Bash", "Write"]
```

### maxTurns (optional)

Caps how many agent turns run before the agent is stopped — a runaway guard for agents that iterate over many files.

```yaml
maxTurns: 30
```

### skills (optional)

Skills the agent is allowed to load. Restricting this keeps the agent's context focused on its domain.

```yaml
skills: ["agent-development", "plugin-structure"]
```

### memory (optional)

Whether the agent retains memory across invocations.

### background (optional)

Run the agent as a background task so the main session keeps working while it runs.

### isolation (optional)

**Only supported value:** `worktree` — runs the agent in a separate git worktree, so its edits never touch the user's working tree until they are merged.

```yaml
isolation: worktree
```

### Unsupported fields

`hooks`, `mcpServers`, and `permissionMode` are **silently ignored** on plugin-shipped agents. Declaring them produces no error and no effect, which makes the resulting bug hard to find.

- Hooks belong in `hooks/hooks.json` — see the hook-development skill
- MCP servers belong in `.mcp.json` or `plugin.json` — see the mcp-integration skill

## System Prompt Design

The markdown body becomes the agent's system prompt. Write in second person, addressing the agent directly.

### Structure

**Standard template:**
```markdown
You are [role] specializing in [domain].

**Your Core Responsibilities:**
1. [Primary responsibility]
2. [Secondary responsibility]
3. [Additional responsibilities...]

**Analysis Process:**
1. [Step one]
2. [Step two]
3. [Step three]
[...]

**Quality Standards:**
- [Standard 1]
- [Standard 2]

**Output Format:**
Provide results in this format:
- [What to include]
- [How to structure]

**Edge Cases:**
Handle these situations:
- [Edge case 1]: [How to handle]
- [Edge case 2]: [How to handle]
```

### Best Practices

✅ **DO:**
- Write in second person ("You are...", "You will...")
- Be specific about responsibilities
- Provide step-by-step process
- Define output format
- Include quality standards
- Address edge cases
- Keep under 10,000 characters

❌ **DON'T:**
- Write in first person ("I am...", "I will...")
- Be vague or generic
- Omit process steps
- Leave output format undefined
- Skip quality guidance
- Ignore error cases

## Creating Agents

### Method 1: AI-Assisted Generation

Use this prompt pattern (extracted from Claude Code):

```
Create an agent configuration based on this request: "[YOUR DESCRIPTION]"

Requirements:
1. Extract core intent and responsibilities
2. Design expert persona for the domain
3. Create comprehensive system prompt with:
   - Clear behavioral boundaries
   - Specific methodologies
   - Edge case handling
   - Output format
4. Create identifier (lowercase, hyphens, 3-50 chars)
5. Write description with triggering conditions
6. Include 2-3 <example> blocks showing when to use

Return JSON with:
{
  "identifier": "agent-name",
  "whenToUse": "Use this agent when... Examples: <example>...</example>",
  "systemPrompt": "You are..."
}
```

Then convert to agent file format with frontmatter.

See `examples/agent-creation-prompt.md` for complete template.

### Method 2: Manual Creation

1. Choose agent identifier (3-50 chars, lowercase, hyphens)
2. Write description with examples
3. Select model only if needed (omit for `inherit`)
4. Choose color only if you want a fixed one
5. Define tools (if restricting access)
6. Write system prompt with structure above
7. Save as `agents/agent-name.md`

## Validation Rules

### Identifier Validation

```
✅ Valid: code-reviewer, test-gen, api-analyzer-v2
❌ Invalid: ag (too short), -start (starts with hyphen), my_agent (underscore)
```

**Rules:**
- 3-50 characters
- Lowercase letters, numbers, hyphens only
- Must start and end with alphanumeric
- No underscores, spaces, or special characters

### Description Validation

**Length:** 10-5,000 characters
**Must include:** Triggering conditions and examples
**Best:** 200-1,000 characters with 2-4 examples

### System Prompt Validation

**Length:** 20-10,000 characters
**Best:** 500-3,000 characters
**Structure:** Clear responsibilities, process, output format

## Agent Organization

### Plugin Agents Directory

```
plugin-name/
└── agents/
    ├── analyzer.md
    ├── reviewer.md
    └── generator.md
```

All `.md` files in `agents/` are auto-discovered.

### Namespacing

Agents are namespaced automatically:
- Single plugin: `agent-name`
- With subdirectories: `plugin:subdir:agent-name`

## Testing Agents

### Test Triggering

Create test scenarios to verify agent triggers correctly:

1. Write agent with specific triggering examples
2. Use similar phrasing to examples in test
3. Check Claude loads the agent
4. Verify agent provides expected functionality

### Test System Prompt

Ensure system prompt is complete:

1. Give agent typical task
2. Check it follows process steps
3. Verify output format is correct
4. Test edge cases mentioned in prompt
5. Confirm quality standards are met

## Quick Reference

### Minimal Agent

```markdown
---
name: simple-agent
description: Use this agent when... Examples: <example>...</example>
---

You are an agent that [does X].

Process:
1. [Step 1]
2. [Step 2]

Output: [What to provide]
```

Only `name` and `description` are mandatory. Every other field is optional: `model` defaults to `inherit`, and the UI picks a color for you.

### Frontmatter Fields Summary

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| name | Yes | lowercase-hyphens | code-reviewer |
| description | Yes | Text + examples | Use when... <example>... |
| model | No | alias or full model ID | inherit |
| effort | No | low/medium/high/xhigh/max | high |
| maxTurns | No | Integer | 30 |
| tools | No | Array of tool names | ["Read", "Grep"] |
| disallowedTools | No | Array of tool names | ["Bash"] |
| skills | No | Array of skill names | ["plugin-structure"] |
| memory | No | Boolean | true |
| background | No | Boolean | true |
| isolation | No | `worktree` | worktree |
| color | No | Color name | blue |

`hooks`, `mcpServers`, and `permissionMode` are not supported for plugin agents.

### Command / Skill Frontmatter

Custom commands have been **merged into skills** — a skill marked `user-invocable` is what used to be a standalone slash command. Their frontmatter is a different set from agent frontmatter:

| Field | Purpose |
|-------|---------|
| `model` | Model alias or full ID (same values as agents) |
| `effort` | `low` / `medium` / `high` / `xhigh` / `max` |
| `argument-hint` | Argument hint shown in the slash-command menu |
| `allowed-tools` | Tool allowlist |
| `disallowed-tools` | Tool blocklist |
| `disable-model-invocation` | Prevent Claude from invoking it automatically |
| `user-invocable` | Expose it as a slash command |
| `context` | Additional context to load |
| `agent` | Delegate execution to a named agent |
| `background` | Run in the background |
| `paths` | Path scoping |
| `when_to_use` | Trigger guidance for automatic invocation |

**Naming difference — easy to get wrong:**

| | Allowlist | Blocklist |
|---|---|---|
| Agents | `tools` | `disallowedTools` (camelCase) |
| Commands / Skills | `allowed-tools` | `disallowed-tools` (hyphenated) |

### Best Practices

**DO:**
- ✅ Include 2-4 concrete examples in description
- ✅ Write specific triggering conditions
- ✅ Prefer rolling aliases (`inherit`, `sonnet`, `opus`) over pinned full model IDs
- ✅ Choose appropriate tools (least privilege)
- ✅ Write clear, structured system prompts
- ✅ Test agent triggering thoroughly

**DON'T:**
- ❌ Use generic descriptions without examples
- ❌ Omit triggering conditions
- ❌ Give all agents same color
- ❌ Grant unnecessary tool access
- ❌ Write vague system prompts
- ❌ Skip testing
- ❌ Default an agent to `fable` — it is opt-in only
- ❌ Declare `hooks`, `mcpServers`, or `permissionMode` (silently ignored)

## Additional Resources

### Reference Files

For detailed guidance, consult:

- **`references/system-prompt-design.md`** - Complete system prompt patterns
- **`references/triggering-examples.md`** - Example formats and best practices
- **`references/agent-creation-system-prompt.md`** - The exact prompt from Claude Code

### Example Files

Working examples in `examples/`:

- **`agent-creation-prompt.md`** - AI-assisted agent generation template
- **`complete-agent-examples.md`** - Full agent examples for different use cases

### Utility Scripts

Development tools in `scripts/`:

- **`validate-agent.sh`** - Validate agent file structure

## Implementation Workflow

To create an agent for a plugin:

1. Define agent purpose and triggering conditions
2. Choose creation method (AI-assisted or manual)
3. Create `agents/agent-name.md` file
4. Write frontmatter (`name` + `description` required; add `model`/`effort`/`tools` only when needed)
5. Write system prompt following best practices
6. Include 2-4 triggering examples in description
7. Validate with `scripts/validate-agent.sh`
8. Test triggering with real scenarios
9. Document agent in plugin README

Focus on clear triggering conditions and comprehensive system prompts for autonomous operation.
