# Decisions — visual-generator-korean-safety

## Architecture Decisions

### D1: 3-layer defense system
- Layer 1 (upstream): Korean Safety Rules 6조 in prompt-designer.md
- Layer 2 (inference): SYSTEM_INSTRUCTION anti-hallucination in generate_slide_images.py
- Layer 3 (downstream): 5-dimension quality evaluation with Korean veto logic

### D2: Space-filling strategy
- Strategy B chosen (icon/illustration fill) over Strategy A (box decomposition)
- Aligns with user's visual richness preference

### D3: 5 dimensions confirmed
- korean_text_readability (0-10)
- korean_hallucination_detection (0-10): 10=clean, 0=severe hallucination
- content_reference_accuracy (0-10)
- layout_suitability (0-10)
- color_palette_compliance (0-10)

### D4: Veto mechanism
- KOREAN_MIN_THRESHOLD = 5.0
- korean_text_readability < 5.0 OR korean_hallucination_detection < 5.0 → auto-FAIL regardless of average
- passed = (avg >= 7.0) AND (korean_text >= 5.0) AND (korean_hallu >= 5.0)

### D5: concept theme exemption
- concept theme has 0 text items, no Korean text to hallucinate
- Exemption must appear in ALL Korean rules: prompt-designer.md, prompt-validator.md, generate_slide_images.py
- In Python: set korean dimensions to 10.0 when concept theme detected

### D6: prompt-validator NOT in orchestrator pipeline
- CRITICAL: prompt-validator is NOT called in visual-generate.md orchestrator
- Therefore, Korean safety validation MUST be added directly to renderer-agent.md
- This ensures in-pipeline protection

## Commit Groups
- Commit 1 (Wave 1): T1 + T2 + T3 — Korean rules + space-filling + 5D quality
- Commit 2 (Wave 2): T4 + T5 — prompt-validator 8th dim + renderer-agent checks
- Commit 3 (Wave 3): T6 + T7 — SKILL.md docs + version bump

- [2026-03-16T23:42:06] Applied concept/zero-text exemption by forcing Korean-related dimensions to 10.0 in quality evaluation (normal + exception path) to avoid penalizing no-text themes.

- [2026-03-16T23:42:15] Applied concept/zero-text exemption by forcing Korean-related dimensions to 10.0 in quality evaluation (normal + exception path) to avoid penalizing no-text themes.

- 2026-03-17: Verdict policy confirmed: APPROVE only when scope allowlist, forbidden-file checks, version sync (3.1.0), and content coverage (6/6) all pass.
