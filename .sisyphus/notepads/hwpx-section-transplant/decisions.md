# Decisions — hwpx-section-transplant

## [2026-03-23] Architecture decisions from plan

- section_transplant.py is standalone script + library (NOT modifying other scripts)
- Chapter boundary = H1 heading (max fontSize in header.xml) with optional text pattern `^\d+\.`
- charPrIDRef="0" always maps to "0" (never remapped)
- hp:secPr stripped from transplanted paragraphs (target's secPr kept)
- hp:pic → WARNING only (no binary transplant in v1)
- dry_run=True → no file written, mapping table printed to stdout
- Paragraph ID conflicts: keep original IDs (Hangul tolerates duplicates)
- Content before first H1 = target-owned (not transplanted)

## [2026-03-23] Final QA scope decision
- Treat `zip_surgery.py save(output_path=None)` as pre-existing infrastructure behavior, not a blocker for this plan, because the plan-owned API `transplant_sections()` rejects missing `output_path` (`ValueError`) and commit `d21ef52` changed only ZipInfo metadata preservation.
