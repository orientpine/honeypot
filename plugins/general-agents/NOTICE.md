# NOTICE

This plugin (`general-agents`) contains content adapted from third-party open-source projects.

---

## `skills/deep-interview/`

This skill's methodology, ambiguity scoring formulas, depth profiles, readiness gates, pressure ladder, challenge modes, and the broader Socratic interview pattern are **adapted from**:

- **Project**: [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex)
- **Source file**: [`skills/deep-interview/SKILL.md`](https://github.com/Yeachan-Heo/oh-my-codex/blob/09d6fd05cd10e66eca1e1a9e3e50d60ca4d94362/skills/deep-interview/SKILL.md)
- **Pinned commit**: `09d6fd05cd10e66eca1e1a9e3e50d60ca4d94362` (`main` as of 2026-05-10)
- **Author**: Yeachan Heo and contributors
- **License**: MIT

### Substantive changes in this adaptation

The adapted version is restructured for cross-platform use (omo / oh-my-openagent + standard Claude Code) and integrates with the existing `general-agents/interview` agent's Korean question banks. Specifically:

1. All `omx`-specific machinery removed: `state_write` / `state_read`, `omx question` CLI, `omx explore`, `.omx/context/`, `.omx/interviews/`, `.omx/specs/` paths, `OMX_QUESTION_RETURN_PANE` tmux plumbing, `--autoresearch` mode, `$ralplan` / `$autopilot` / `$ralph` / `$team` / `$ultragoal` / `$autoresearch-goal` / `$performance-goal` handoff bridge.
2. Question primitive replaced with a **try-then-fall-back instruction pattern**: try `AskUserQuestion` once → on failure (unavailable / empty / error), fall back to plain-text question + treat user's next conversation turn as the answer. Never retry a failed tool.
3. Decimal ambiguity scoring replaced with **bucketed inputs** `{0.0, 0.25, 0.50, 0.75, 1.0}` feeding the original deep-interview weighted formula. Anti-gaming caps (no evidence ≤ 0.25, contradictions ≤ 0.50). Boolean readiness gates remain separate blockers.
4. Korean domain lenses (기술 구현 / UI/UX / 우려사항 / 트레이드오프) from the original `general-agents/interview` agent integrated as **column applicability lookup** alongside deep-interview's clarity dimensions (rows). No per-cell scoring.
5. Artifact path changed from `.omx/specs/deep-interview-{slug}.md` to project-local `.claude/plans/interview-{slug}-{ts}.md` to preserve repo's existing convention. State sidecar at `.claude/plans/interview-{slug}-{ts}.state.json` (transcript-authoritative; sidecar reconstructable).
6. Handoff bridge rewritten in `references/handoff-contracts.md` with Claude-Code/omo-portable options replacing OMX-specific commands.

The original copyright and license are preserved below.

---

## MIT License (oh-my-codex)

```
MIT License

Copyright (c) Yeachan Heo and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> **Note on copyright text**: Upstream `oh-my-codex` declares MIT in `package.json` and README; the canonical `LICENSE` file at the repo root was not directly retrievable at the pinning time, so the standard MIT permission notice is reproduced above with the upstream copyright line. The `Copyright (c)` attribution is to "Yeachan Heo and contributors" per the upstream package metadata.

---

## This plugin's own license

This plugin (`general-agents`) is distributed under the **MIT License** as part of the [`honeypot`](https://github.com/orientpine/honeypot) marketplace. Author: Baekdong Cha (orientpine@gmail.com).
