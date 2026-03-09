# Decisions — visual-generator-revival

## [2026-03-09] Architecture Decisions

### Format Choice: 4-Block Markdown (confirmed)
- **Decision**: Restore ae35fe6's 4-block format. Discard v2.2.0's XML-tag format for prompts.
- **Rationale**: User found ae35fe6's ~100-line prompts generated more accurate images than v2.2.0's ~30-line prompts.

### Hybrid Approach (4-block + v2.x features)
- **Keep from ae35fe6**: Detailed INSTRUCTION subsections, Content Placement, Rendering Style 7 elements, FORBIDDEN 15+ items
- **Keep from v2.x**: prompt-validator, Style Sheet, render_text/scene_context classification, Golden References, 3 reference docs
- **New in v3.0.0**: ### Scene Description subsection (replaces <scene>), fixed palette in theme_recommendation.md, actual style_sheet.md generation

### CONTENT Format: flat key:"value" (confirmed)
- **Decision**: Flat `key: "value"` format only
- **Forbidden**: Tables, numbered lists, `### subsection` headers inside CONTENT

### Golden Reference Strategy: TDD Anchors
- **Decision**: Convert 6 Golden References to 4-block (Tasks 2, 4-8)
- **Task 2 (gov)** is the template — others (4-8) follow its pattern
- Golden References serve as TDD anchors for prompt-validator testing

### Version: v3.0.0 (MAJOR bump)
- **Reason**: Format change is breaking (XML-tag → 4-block), not backward compatible
