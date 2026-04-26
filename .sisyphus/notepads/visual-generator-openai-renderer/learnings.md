# Learnings — visual-generator-openai-renderer

## [2026-04-26] Session Start
- Project: Windows + PowerShell environment (AGENTS.md lines 71-103)
- No Unix commands (export, mkdir -p, grep, etc.) — use Python or PowerShell equivalents
- Shell: cmd.exe (PowerShell) — all git/python commands run directly without env prefix
- Plugin structure: plugins/visual-generator/ has agents/, commands/, skills/
- slide-renderer skill: scripts/ + references/ are inside skills/slide-renderer/
- Gemini script (reference): plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
- Existing agents (5): content-organizer, content-reviewer, prompt-designer, prompt-validator, renderer-agent
- PROTECTED FILES (must NOT modify): renderer-agent.md, prompt-designer.md, content-organizer.md, content-reviewer.md, prompt-validator.md, generate_slide_images.py, scene-richness-spec.md, validation-rules-map.md, korean-typography-spec.md, all theme-* and layout-types skills
- NEW files (allowed): renderer-agent-openai.md, generate_slide_images_openai.py, openai-quality-rubric.md
- MODIFY allowed: visual-generate.md, SKILL.md (slide-renderer), plugin.json, marketplace.json, README.md, AGENTS.md
