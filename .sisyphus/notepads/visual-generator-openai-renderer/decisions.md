# Decisions — visual-generator-openai-renderer

## [2026-04-26] Architecture Decisions (from plan)
- D1: renderer_choice_timing: pre|post|none (default=none for backward compat)
- D2: Single renderer only (no "both" mode)
- D3: Separate agent (renderer-agent-openai.md) + separate script (generate_slide_images_openai.py)
- D4: 5D evaluation with GPT vision model + Structured Outputs json_schema strict
- D5: quality="high", size="1536x1024", output_format="jpeg"
- D9: --max-images cap (default 30)
- D10: Task 1 first = model verification smoke test
- D11: SYSTEM_INSTRUCTION as Python constant (prepend to user prompt)
- D12: 16-item checklist cross-reference to renderer-agent.md (no duplication)
- D13: Hard fail on OPENAI_API_KEY missing (no silent fallback)

## Version Targets
- plugin.json: 3.4.0 → 3.5.0
- marketplace.json plugin entry: 3.4.0 → 3.5.0
- marketplace.json metadata: 3.29.0 → 3.30.0
- README.md Version: 3.29.0 → 3.30.0
- AGENTS.md Version: 3.29.0 → 3.30.0
