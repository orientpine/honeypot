# Issues — hwpx-quality-upgrade

## Known Issues (from plan research)
1. xml_writer.py outputs hwpx-fragment without hs:sec wrapper → cannot insert into section0.xml directly
2. md_parser.py only supports custom format, not `![alt](path)` → dev/ sample mismatch
3. Table colSpan/rowSpan not supported — equal split only
4. analyze_template.py style map uses frequency heuristics → wrong mapping on complex templates
5. image_embedder.py: PNG-only, no alignment control, no caption linking
6. No post-processing (proofreading) step

## Ongoing
(Updated as issues discovered)
