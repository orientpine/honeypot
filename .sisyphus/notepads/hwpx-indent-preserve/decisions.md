# Decisions — hwpx-indent-preserve

## Architecture Decisions
- 2-space per indent level (confirmed in plan)
- Heading offset auto-calculation for multi-MD merge
- Hybrid approach: 95% deterministic script + 5% agent review
- bullet_level_0, bullet_level_1, ... key naming for style_config
- md_merger.py: new standalone script (imports md_parser)
- RED coverage decision: keep existing flat-style assertions (`bullet`, `heading_1`, `body`) while requiring at least two `bullet_level_N` keys to encode the desired indent-aware style-map contract.

## Wave Execution Plan
- Wave 1: Tasks 1-5 (TDD tests, ALL parallel)
- Wave 2: Tasks 6-9 (implementations, ALL parallel)
- Wave 3: Task 10 (E2E), Task 11 (docs) — parallel; Task 12 after 11
- Final: F1-F4 in parallel
