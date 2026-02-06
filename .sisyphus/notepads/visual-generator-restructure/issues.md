# Issues - visual-generator-restructure

## [2026-02-06T06:07:03.860Z] Plan Start

### Known Issues (From Analysis)

1. **content-reviewer.md**: Missing Write tool in frontmatter (line 4) but calls Write(review_result.md) at line 174

2. **renderer-agent.md**: Validation patterns mismatch - greps for "INSTRUCTION BLOCK" but prompt-designer outputs "## INSTRUCTION"

3. **prompt-designer.md**: Internal inconsistency - doc headings say "Block 1: INSTRUCTION BLOCK" but actual output template uses "## INSTRUCTION"

4. **orchestrator.md**: No explicit delegation enforcement rules - needs "MUST NOT do work directly" clauses

5. **Workflow Position missing**: Only renderer-agent lacks this section among all 4 pipeline agents

## Unresolved Issues

None yet.
