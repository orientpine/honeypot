# Decisions — hwpx-quality-upgrade

## Architecture Decisions

### Double Bullet Fix Strategy
- Strip leading bullet characters from hp:t text when paraPrIDRef is in bullet_auto list
- bullet_auto list comes from style-config JSON (dynamic, not hardcoded)
- Target bullet chars: ○●□■◆◇•▶►→※ etc.

### Image-Caption Pairing
- md_parser: ![alt](path) + next italic line = image_ref block with caption field
- xml_writer: build_image_with_caption() creates hp:pic + caption paragraph
- image_embedder: --from-parsed mode reads path field from image_ref blocks

### hs:sec Wrapper
- --wrap-section flag controls wrapping (backward-compatible)
- secPr values from style-config (page_width, page_height, margins)
- Namespaces: hp, hc, hs, hh at hs:sec root

### proofread.py Design
- Read-only, string-based XML scanning
- Returns JSON with 5 checks: double_bullets, font_consistency, empty_paragraphs, orphaned_placeholders, table_borders
- Exit code 0=all pass, 1=any fail

---

## F3: Real Manual QA — Full Pipeline Execution (2026-03-19)

### Pipeline Executed (dev/qa/ clean directory)
```
1. md_parser 3장.md → p3.json (43 blocks, 3 images) ✅
2. md_parser 4장.md → p4.json (163 blocks, 12 images) ✅
3. Merge → merged.json (206 blocks, 15 images) ✅
4. analyze_template 초안.hwpx → style_map.json ✅
5. xml_writer --wrap-section → fragment.xml (178KB, hs:sec root, 15 hp:pic, 15 captions) ✅
6. zip_surgery replace → intermediate.hwpx ✅
7. image_embedder --from-parsed ❌ FAILED (placeholder/binref mismatch)
   WORKAROUND: Manual ZIP embed → with_images.hwpx ✅ (15 BinData/, 15 manifest entries)
8. fix_namespaces → in-place ✅
   NOTE: Only renames prefixes, doesn't inject missing xmlns or XML declaration
   WORKAROUND: Manual namespace+declaration patch for strict validation
9. validate --strict → 1 issue (standalone='no' universal false positive) ✅
   validate (non-strict) → PASS ✅
   NOTE: Both 초안.hwpx and 작성.hwpx ALSO fail standalone strict check
10. proofread → double_bullets=0 ✅, orphaned_placeholders=0 ✅
    font_consistency=false (1/6 groups, score=0.8773) — BETTER than golden ref (0.7313)
    empty_paragraphs=6 (informational)
11. page_guard → 5 warnings (paragraph/table/text length differences) ✅ (≤5 threshold)
    Expected: 3장+4장 content differs from full proposal golden reference
```

### Verification Results
| Check | Result | Notes |
|-------|--------|-------|
| BinData/ images | 15/15 | All PNG files present |
| hp:pic elements | 15/15 | All in section0.xml |
| Caption 그림 paragraphs | 15/15 | 3-1~3-3, 4-1~4-12 |
| binaryItemIDRef | 15/15 | image1~image15 |
| Manifest entries | 15/15 | content.hpf registered |
| validate (non-strict) | PASS | All standard checks |
| validate --strict | 1 issue | standalone false positive (same as originals) |
| double_bullets | 0 | DoD: ✅ |
| orphaned_placeholders | 0 | DoD: ✅ |
| page_guard warnings | 5 | DoD: ≤5 ✅ |

### Integration Issues Found
1. **CRITICAL**: image_embedder cannot work with xml_writer output (placeholder vs binref)
2. **MEDIUM**: fix_namespaces doesn't complete xmlns injection for xml_writer output
3. **LOW**: validate --strict standalone check is universal false positive

```
Scenarios [9/11 pass] | Integration [1/1 critical issue] | VERDICT: CONDITIONAL APPROVE
```

### Verdict Rationale
- Pipeline produces valid HWPX with all 15 images+captions correctly positioned
- Core quality checks pass (double_bullets=0, orphaned_placeholders=0, validate=PASS)
- image_embedder integration gap requires workaround but is fixable (add binaryItemIDRef fallback)
- xml_writer output quality is excellent (hs:sec wrapper, full hp:pic, proper captions)
- Generated output has BETTER font consistency than hand-created golden reference
- CONDITIONAL because image_embedder needs 1 code fix to complete the E2E pipeline without workaround
