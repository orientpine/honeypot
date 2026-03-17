# Learnings

## [2026-03-17] Session: ses_3066cefb4ffeKk3Uo1Jb6d2xKO

### Project Context
- Modifying visual-generator plugin (v3.2.0 → v3.3.0)
- 9 .md files total — NO code, no tests, pure prompt directive refactoring
- Working directory: /home/cha/Documents/honeypot
- All edits are APPENDS/MODIFICATIONS to existing sections — do NOT restructure files

### Key Files
- prompt-designer: `plugins/visual-generator/agents/prompt-designer.md` (central rules hub)
- scene-richness-spec: `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md`
- theme-gov: `plugins/visual-generator/skills/theme-gov/SKILL.md`
- theme-seminar: `plugins/visual-generator/skills/theme-seminar/SKILL.md`
- theme-concept: `plugins/visual-generator/skills/theme-concept/SKILL.md`
- theme-whatif: `plugins/visual-generator/skills/theme-whatif/SKILL.md`
- theme-pitch: `plugins/visual-generator/skills/theme-pitch/SKILL.md`
- theme-comparison: `plugins/visual-generator/skills/theme-comparison/SKILL.md`

### Theme-Conditional Negative Space Targets (CORE DECISION)
| Group          | Themes              | Old Target  | New Target | Rationale |
|----------------|---------------------|-------------|------------|-----------|
| Full-bleed     | concept, whatif     | ~30-40%     | ≤20%       | Edge-to-edge bg, scale up elements |
| Full-bleed img | comparison          | ~5% (95%)   | ≤10%       | Already near-max, minor tweak |
| Structured     | gov, seminar        | 20-30%      | ≤15%       | Grid expansion + element size increase |
| Intentional    | pitch               | 30%+ intl   | 30%+ KEEP  | Apple Keynote DNA — DO NOT CHANGE |

### Guardrails (SACRED — NEVER TOUCH)
- pitch "30% 이상 의도적 어두운 여백" — PRESERVED
- concept "5% 이상 안쪽" safe zone — PRESERVED
- prompt-validator.md — NOT MODIFIED
- layout-types SKILL.md — NOT MODIFIED
- CONTENT item counts — NOT MODIFIED
- Typography dimensions — NOT MODIFIED
- 6 other Rendering Style dimensions (서피스, 배경, 코너/경계, 연결선, 시각장식, 시각메타포) — NOT MODIFIED
