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
