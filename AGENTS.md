# TOOLBOX PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-07T00:29:36+09:00
**Commit:** 9a91616
**Branch:** main

## OVERVIEW

AI agent skill/plugin toolbox for Korean government R&D proposal (ISD) auto-generation and presentation figure creation. Claude plugin ecosystem with orchestrated multi-agent workflows.

## STRUCTURE

```
toolbox/
├── .claude-plugin/         # Plugin marketplace registry
├── agents/                 # Standalone agent definitions
│   ├── general/            # General-purpose agents (interview)
│   └── investments/        # Portfolio analysis multi-agent system (Korean)
├── isd-research-proposals/ # ISD document generation system (5 chapters)
│   ├── isd-orchestrator/   # Master orchestrator (Chapter 3→1→2→4→5)
│   └── chapter{1-5}-generator/  # Individual chapter generators
└── presentations/          # Figure/slide generation
    ├── figure-generator/   # Caption extraction + Gemini API image gen
    ├── slide-prompt-generator/
    └── slide-image-generator/
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Generate full ISD proposal | `isd-research-proposals/isd-orchestrator/` | Uses `input_template.md` |
| Generate single ISD chapter | `isd-research-proposals/chapter{N}-generator/` | Chapter 3 first, then 1→2→4→5 |
| Generate figures from `<caption>` | `presentations/figure-generator/` | Gemini API required |
| Generate slide prompts | `presentations/slide-prompt-generator/` | 4-color palette, PPT style |
| Portfolio analysis agents | `agents/investments/` | Korean DC pension multi-agent |
| Plugin registry | `.claude-plugin/marketplace.json` | All 9 plugins listed |

## CONVENTIONS

### Skill File Structure
- Each plugin: `{plugin}/skills/SKILL.md` (main), `references/`, `assets/output_template/`
- SKILL.md frontmatter: `name`, `description`, `tools`, `model` (optional)
- Verification docs: `chapter{N}_research_verification.md` - NEVER skip

### Document Language
- All ISD content: Korean (한글)
- All presentations: Korean with English technical terms
- Agent definitions: Korean

### Critical Workflow Rules
- ISD chapter order: **3 → 1 → 2 → 4 → 5** (Chapter 3 first)
- Verification docs: Generate BEFORE main content (절대 스킵 금지)
- Task delegation: Use `Task(subagent_type=...)` - never analyze directly
- Auto mode: `auto_mode=true` skips user confirmations

## ANTI-PATTERNS (THIS PROJECT)

| Forbidden | Reason |
|-----------|--------|
| Skipping verification documents | Entire chapter becomes invalid |
| Direct fund_data.json analysis | Must delegate to `fund-portfolio` agent |
| Direct regulatory calculation | Must delegate to `compliance-checker` |
| Placeholder text `[내용]` in prompts | Gemini will render literally |
| Rendering hints in ASCII `(24pt)` | Will appear in generated image |
| Generating Chapter 1 before Chapter 3 | Dependency: Ch1 derives from Ch3 |

## UNIQUE STYLES

### Figure Prompt Requirements (500+ lines)
- 14 mandatory sections (1-14)
- ASCII layout for 6 regions
- 50+ text items, 8+ data tables
- 4-color palette: #1E3A5F, #4A90A4, #2E7D5A, #F5F7FA

### Multi-Agent Portfolio System
- Workflow: `macro-outlook` → `fund-portfolio` → `compliance-checker` → `output-critic`
- Output files: `00-macro-outlook.md` through `04-portfolio-summary.md`
- Folder: `portfolios/YYYY-MM-DD-{profile}-{session}/`

## COMMANDS

```bash
# Generate images from prompts (requires google-genai, Pillow)
python presentations/figure-generator/scripts/generate_images.py \
  --prompts-dir [path]/prompts/ \
  --output-dir [path]/figures/

# Generate slide images
python presentations/slide-image-generator/scripts/generate_slide_images.py \
  --prompts-dir [path] --output-dir [path]
```

## NOTES

- **API Key**: Gemini API key hardcoded in Python scripts (line 26) - replace for production
- **Model**: `gemini-3-pro-image-preview` for 4K 16:9 images with Korean text
- **Rate Limit**: 2-second delay between API calls
- **ISD Output**: `output/[프로젝트명]/chapter_{1-5}/`
- **All SKILL.md files**: Contain exhaustive workflow phases with numbered steps
