# Issues & Gotchas: Plugin Structure Standardization

## Known Constraints
- Sub-agent files reference orchestrator `name` field in text
- Cannot change YAML frontmatter `name` without breaking references
- marketplace.json must remain valid JSON at all times
