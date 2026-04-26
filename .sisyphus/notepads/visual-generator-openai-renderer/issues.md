# Issues — visual-generator-openai-renderer

## [2026-04-26] Known Issues / Gotchas
- Model name gpt-5.5 may be hallucinated — Task 1 MUST verify before Tasks 5, 6 can hardcode it
- Evaluation model fallback chain: gpt-5.5 → gpt-5 → gpt-4o
- OpenAI Responses API (client.responses.create) differs from Chat Completions API
- JPEG output: gpt-image-2 returns b64_json, not URL — must base64.b64decode and save
- Korean text: caveat exists (non-Latin suboptimal) — mitigated by explicit rubric + detail="original"
- Windows path separators: use forward slashes or Path() in Python
- All QA scenarios use Python inline or PowerShell (no bash heredoc, no grep, no jq)
