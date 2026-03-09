# Issues — visual-generator-revival

## [2026-03-09] Known Issues to Fix

### Issue 1: style_sheet.md Not Generated (Bug)
- **File**: plugins/visual-generator/agents/prompt-designer.md (current v2.2.0)
- **Problem**: Phase 2.5 Style Sheet management code exists but style_sheet.md is never actually saved
- **Fix**: Task 10 must ensure prompt-designer writes style_sheet.md with Write tool

### Issue 2: Per-Slide Different Palettes (Bug)
- **File**: plugins/visual-generator/agents/content-organizer.md
- **Problem**: theme_recommendation.md assigns different "mood palette" per slide (gov: slide01=#1E3A5F, slide02=#2C3E50)
- **Fix**: Task 12 must add fixed palette rule — ONE palette for entire session

### Issue 3: generate_slide_images.py Renders Metadata Files (Bug)
- **File**: plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
- **Problem**: style_sheet.md, validation_result.md, prompt_index.md not in exclude list
- **Fix**: Task 3 — add these to exclude list

### Issue 4: Color Code Rendering (Bug)
- **File**: Same script
- **Problem**: Hex color codes like #1E3A5F rendered as visible text in images
- **Fix**: Task 3 — add to SYSTEM_INSTRUCTION: "Never render hex color codes as visible text"

### Issue 5: Concept Theme Text Rendering (Bug)
- **Problem**: concept theme prompts sometimes render text (should be zero text)
- **Fix**: Task 3 (SYSTEM_INSTRUCTION) + Task 5 (concept Golden Reference with strong FORBIDDEN)
