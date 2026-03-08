# Learnings — visual-generator-quality-fix

## [2026-03-07] Session Start

### Project Structure
- All agent/skill paths are relative to `plugins/visual-generator/`
- `agents/prompt-designer.md` = `plugins/visual-generator/agents/prompt-designer.md`
- Evidence files go in `.sisyphus/evidence/`

### Key Constraints
- layout-types SKILL.md (938 lines) — DO NOT MODIFY
- generate_slide_images.py — only API params + quality retry (NO file/dir changes)
- 5-tag XML schema (`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`) — NO changes
- prompt-validator is REJECT-only (NO auto-fix)

### Wave Execution Order
- Wave 1: T1, T2, T3 (parallel)
- Wave 2: T4, T5, T6, T7, T8-T13, T17 (parallel, after Wave 1)
- Wave 3: T14, T15, T18 (parallel), T16 (after all Wave 2+3)
- Final: F1-F4 (parallel)

## [2026-03-07] Task 4 — prompt-validator agent
- Added `plugins/visual-generator/agents/prompt-validator.md` with Phase 0-3 workflow and 7 validation dimensions.
- Enforced REJECT-only policy with explicit auto-fix prohibition and line-level correction instruction requirement.
- Included mandatory reference path resolution fallback chain for `skills/slide-renderer/references/*.md`.

## [2026-03-07] Task 5 — visual-generate.md Phase 3.5 insertion

**Completed**: Updated `plugins/visual-generator/commands/visual-generate.md` to insert Phase 3.5 (prompt-validator) between Phase 3 and Phase 4.

**Changes**:
1. Pipeline diagram (line 9): Added `prompt-validator` between `prompt-designer` and `renderer-agent`
2. Phase 3.5 block (lines 42-46): New phase with Task call, REJECT retry logic (max 2x), and validation_result.md output
3. MUST DO section (lines 62-63): Added 2 new rules for Phase 3.5 validation and REJECT handling

**Key Details**:
- Phase 3.5 enforces scene-richness-spec.md, validation-rules-map.md, korean-typography-spec.md compliance
- REJECT → re-run prompt-designer with rejection reason included in prompt
- Max 2 retries before escalation
- Output: validation_result.md

**QA Verification**: All 7 required elements present (prompt-validator, Phase 3.5, validation_result.md, REJECT, scene-richness-spec, validation-rules-map, korean-typography-spec)

## [2026-03-07] Task 18 — quality-based retry in slide renderer
- Added `evaluate_image_quality(client, image_path)` using Gemini vision with JSON score parsing for 한글 가독성/레이아웃/색상 3 criteria.
- Added separate quality retry loop in `generate_image()` (3 total attempts) while preserving existing API error retry (`max_retries=3`) in `_request_image`.
- Implemented threshold rule (`QUALITY_THRESHOLD = 7.0`), correction hint prompt appending, per-attempt console score logging, and best-score image fallback when threshold is not met.
