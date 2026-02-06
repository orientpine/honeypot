# Decisions - visual-generator-improvement

## Architectural Choices & Rationale


## [2026-02-05] Task 1: ${CLAUDE_PLUGIN_ROOT} Verification

### Research Findings

**Source 1: Claude Code Official Documentation (plugins-reference)**
- URL: https://code.claude.com/docs/en/plugins-reference
- Finding: `${CLAUDE_PLUGIN_ROOT}` is documented as an environment variable available in:
  - Hooks (PostToolUse, PreToolUse, etc.)
  - MCP servers configuration
  - Scripts referenced from hooks/MCP servers

**Source 2: Plugin Caching & File Resolution (plugins-reference)**
- URL: https://code.claude.com/docs/en/plugins-reference
- Finding: "Plugins cannot reference files outside their copied directory structure"
- Finding: "Paths that traverse outside the plugin root (such as `../shared-utils`) will not work after installation"
- Finding: `${CLAUDE_PLUGIN_ROOT}` is used in hooks and MCP servers to ensure correct paths

**Source 3: Agent File Structure (plugins-reference)**
- Agent files are Markdown files in `agents/` directory
- Agent files contain:
  - YAML frontmatter (name, description, capabilities)
  - Markdown content describing agent role and capabilities
  - **NO mention of environment variable substitution in agent content**

**Source 4: Existing Implementation Pattern**
- File: `plugins/isd-generator/agents/figure.md` (line 91-93)
- Current approach: Uses relative paths like `python plugins/isd-generator/scripts/generate_images.py`
- Pattern: Assumes execution from project root directory
- **Does NOT use ${CLAUDE_PLUGIN_ROOT}**

**Source 5: Renderer Skill Documentation**
- File: `plugins/visual-generator/skills/renderer/SKILL.md` (line 71-75, 119-127)
- Current approach: Uses relative paths like `plugins/visual-generator/scripts/generate_slide_images.py`
- Alternative: `honeypot/plugins/visual-generator/scripts/generate_slide_images.py` (for submodule usage)
- **Does NOT use ${CLAUDE_PLUGIN_ROOT}**

### Verdict: **NO - Cannot use ${CLAUDE_PLUGIN_ROOT} in agent file content**

### Evidence

1. **Official Documentation Scope**: `${CLAUDE_PLUGIN_ROOT}` is explicitly documented ONLY for:
   - Hook configurations (JSON)
   - MCP server configurations (JSON)
   - Scripts executed by hooks/MCP servers
   
2. **Agent File Limitations**: Agent files are Markdown documents that:
   - Contain instructions for Claude to execute
   - Are NOT processed for environment variable substitution
   - Are loaded as plain text content into Claude's context
   - Do NOT have access to environment variables during execution

3. **Plugin Caching Behavior**: 
   - Plugins are copied to cache directory
   - Relative paths like `../` don't work after installation
   - But `${CLAUDE_PLUGIN_ROOT}` is only available in hook/MCP contexts, NOT in agent markdown content

4. **Current Implementation Pattern**:
   - Both `figure.md` agent and `renderer` skill use relative paths from project root
   - No existing agent files use `${CLAUDE_PLUGIN_ROOT}` in their markdown content
   - This suggests the pattern is intentional and necessary

### Why It Doesn't Work in Agent Files

Agent files are **instructions for Claude**, not **configuration files**. When Claude reads an agent file:
1. The file is loaded as plain text into Claude's context
2. Claude reads the instructions and executes them
3. Environment variables are NOT substituted in the markdown content
4. Claude must construct the correct path based on the instructions provided

### Alternatives (Ranked by Feasibility)

#### **Option 1: User Provides Full Path (RECOMMENDED)**
- **Pros**: Works immediately, no changes needed, user has control
- **Cons**: Requires user to know full path
- **Implementation**: Agent asks user for script path or output directory
- **Example**:
  ```
  사용자 입력:
  스크립트 경로: /home/user/honeypot/plugins/visual-generator/scripts/generate_slide_images.py
  ```

#### **Option 2: Relative Path from Project Root (CURRENT)**
- **Pros**: Works for standard installations, simple
- **Cons**: Breaks if plugin is in subdirectory or submodule
- **Implementation**: Keep current approach
- **Example**:
  ```bash
  python plugins/visual-generator/scripts/generate_slide_images.py
  ```

#### **Option 3: Relative Path from Agent File Location**
- **Pros**: Works regardless of execution directory
- **Cons**: Requires Claude to calculate relative path correctly
- **Implementation**: Use `../../scripts/generate_slide_images.py` from agent file
- **Example**:
  ```bash
  python ../../scripts/generate_slide_images.py
  ```
- **Risk**: Path calculation errors if agent file location changes

#### **Option 4: Environment Variable Set by User**
- **Pros**: Flexible, works with any installation
- **Cons**: Requires user setup before running
- **Implementation**: Agent checks for `PLUGIN_ROOT` env var
- **Example**:
  ```bash
  export PLUGIN_ROOT=/path/to/honeypot
  python $PLUGIN_ROOT/plugins/visual-generator/scripts/generate_slide_images.py
  ```

#### **Option 5: Hook-Based Script Wrapper (ADVANCED)**
- **Pros**: Uses official `${CLAUDE_PLUGIN_ROOT}` mechanism
- **Cons**: Complex, requires hook setup
- **Implementation**: Create hook that sets env var, agent uses it
- **Example**: Hook sets `PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT}`, agent uses `$PLUGIN_ROOT`

### Recommended Solution

**Use Option 1 + Option 3 Hybrid**:
1. Agent asks user for output directory path (required input)
2. Agent constructs script path using relative path from agent location: `../../scripts/generate_slide_images.py`
3. Agent executes from the output directory context
4. This works regardless of where plugin is installed

**Rationale**:
- Doesn't require user to know full paths
- Works with submodules and nested installations
- Follows Claude Code best practices
- Matches existing pattern in `figure.md` (uses relative paths)

### Implementation Checklist

- [ ] Update agent file to use relative path: `../../scripts/generate_slide_images.py`
- [ ] Test with plugin in standard location: `plugins/visual-generator/`
- [ ] Test with plugin in submodule: `honeypot/plugins/visual-generator/`
- [ ] Document path resolution in agent file
- [ ] Add fallback: if relative path fails, ask user for full path

