# Issues — visual-generator-korean-safety

## Known Issues

### I1: prompt-validator pipeline gap
- prompt-validator.md is NOT included in the visual-generate.md orchestrator pipeline
- Mitigation: renderer-agent.md handles in-pipeline validation, so adding checks 15-16 there ensures enforcement

### I2: evaluate_image_quality signature change
- Currently: evaluate_image_quality(client, image_path)
- New: needs prompt_text parameter for content reference accuracy
- Must update generate_image() call site at line 144: evaluate_image_quality(client, candidate_output_path)
- New call: evaluate_image_quality(client, candidate_output_path, prompt_text=current_prompt)

### I3: concept theme detection in Python
- Detect concept theme by checking if prompt_text contains "concept" or "zero text rendering" or "Zero-Text Rendering"
- When detected: set korean_text_readability = 10.0, korean_hallucination_detection = 10.0

## Resolved Issues
(none yet)

- [2026-03-16T23:42:06]  binary unavailable in this environment; used  for syntax/evidence commands.

- [2026-03-16T23:42:15] python binary unavailable in this environment; used python3 for syntax/evidence commands.
