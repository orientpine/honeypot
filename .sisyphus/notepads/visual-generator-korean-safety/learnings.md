# Learnings — visual-generator-korean-safety

## File Locations (Confirmed)
- `plugins/visual-generator/agents/prompt-designer.md` — 587줄. Text Density Rules at line 409-430. FORBIDDEN ELEMENTS template at line 276-296 (15 items). Scene Description Rules at line 171-195. concept Theme Rules at line 341-358.
- `plugins/visual-generator/agents/prompt-validator.md` — 149줄. 7 dimensions (line 36-98). Dimension 7 ends at line 98. Workflow Phase 2 at line 112-122. "all 7 pass" at line 121.
- `plugins/visual-generator/agents/renderer-agent.md` — 341줄. Validation Checklist table at line 153-166. Workflow Phase 2 at line 67-97. Bash examples at line 178-207.
- `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py` — 392줄. SYSTEM_INSTRUCTION at line 34-47. QUALITY_THRESHOLD = 7.0 at line 48. MAX_QUALITY_RETRIES = 2 at line 49. evaluate_image_quality() at line 190-268. generate_image() at line 72-187. Console output at line 157-169. criteria dict at line 245-253.
- `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — 376줄. Negative Space section at line 170-200. Implementation Checklist at line 348-360. References section ends at line 376.
- `plugins/visual-generator/skills/slide-renderer/SKILL.md` — 76줄. Short file, 2 sections need to be added.
- `plugins/visual-generator/.claude-plugin/plugin.json` — "version": "3.0.0"
- `.claude-plugin/marketplace.json` — visual-generator "version": "3.0.0"

## Key Conventions
- prompt-designer.md: No INSTRUCTION block structure changes. Korean Safety Rules go AFTER Text Density Rules section (after line 430).
- generate_slide_images.py: No MODEL_NAME, API client, file I/O, QUALITY_THRESHOLD (7.0), MAX_QUALITY_RETRIES changes. Only add KOREAN_MIN_THRESHOLD constant, expand evaluate_image_quality() to 5 dimensions, add concept theme exemption.
- prompt-validator.md: REJECT-only policy. 7 dimensions → 8 dimensions. "all 7 pass" → "all 8 pass".
- renderer-agent.md: Add | 15 | and | 16 | rows to Validation Checklist table. Add Step 2-7 and Step 2-8 to Workflow Phase 2. concept theme exemption for checks 15-16.
- scene-richness-spec.md: New section "## 11. Space-Filling Prevention" after Implementation Checklist (currently section 9). References section (10) stays last.
- SKILL.md: Add "## Quality Evaluation Criteria" and "## Korean Text Safety" sections.
- Version: 3.0.0 → 3.1.0 in BOTH plugin.json and marketplace.json.

## Anti-patterns
- Do NOT modify visual-generate.md or any theme-*/SKILL.md
- Do NOT add --verify-only mode or new CLI args to generate_slide_images.py
- Do NOT change existing FORBIDDEN ELEMENTS items (keep 15, just add 16th if for AI Korean)
- Do NOT use Strategy A (box decomposition) — use Strategy B (icon/illustration fill)

- [2026-03-16T23:42:06] Upgraded slide renderer quality gate from 3D average-only to 5D with Korean hallucination/content-accuracy dimensions; kept QUALITY_THRESHOLD=7.0 and added Korean veto floor (5.0).

- [2026-03-16T23:42:15] Upgraded slide renderer quality gate from 3D average-only to 5D with Korean hallucination/content-accuracy dimensions; kept QUALITY_THRESHOLD=7.0 and added Korean veto floor (5.0).

- 2026-03-17: Scope fidelity check passed for last 3 commits; changed files matched exact 8-file allowlist and forbidden-file counts were all zero.
