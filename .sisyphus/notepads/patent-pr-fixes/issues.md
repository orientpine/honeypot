# Issues — patent-pr-fixes

## 2026-03-16 Session: ses_30a859fdbffezKmL12qIADmsEu

### Pre-work Issues Found
- PR branch has CONFLICTING state with main
- LSP import resolution errors (expected, not actual bugs - packages not installed in dev env)
  - mcp, uvicorn, starlette, dotenv, stringcase not installed
  - These DO NOT affect py_compile validation

### Known Conflicts
1. .claude-plugin/marketplace.json — parallel modifications (different plugins added)
2. AGENTS.md — PR has older state vs main 2.8.0
3. README.md — possibly conflicting
