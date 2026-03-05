# hwpx-generator Issues

## [2026-02-25] Session: ses_36b3577d0ffes3u0vrQ95zfEu6

### Known Risks (from Metis analysis)
1. SKILL.md size explosion — repo3 SKILL.md 750+ lines → split to references/
2. Cross-skill script dependency — math → core validate.py → document cross-ref pattern
3. ZIP replacement placeholder splitting risk — ObjectFinder pre-scan step must be preserved
4. Template collision — repo1 and repo3 both have templates/base/ → repo3 renamed to math-base/
5. fix_namespaces.py scope confusion — XML-first does NOT need it, ZIP-level only
6. Hardcoded sandbox paths in repo2 — /mnt/skills/, /home/claude/ → must replace with $SKILL_DIR
7. fix_namespaces.py regex approach — lxml refactoring FORBIDDEN

## [2026-02-25] Task 2 follow-up notes
1. LSP diagnostics for  are unavailable in this workspace (no markdown LSP configured).
2. Validation relied on structural checks (required sections, forbidden-string scan, line count evidence).

## [2026-02-25] Task 2 correction
1. Markdown LSP server is not configured; diagnostics unavailable for .md files.
2. Used grep plus line-count evidence for verification fallback.

## [2026-02-25] Task 6 follow-up
1. Markdown LSP remains unavailable for `.md`; verification used grep checks + line count for `SKILL.md`.
2. Existing `references/` files under `hwpx-templates` still contain legacy absolute examples; this task only updated `SKILL.md` and `scripts/fix_namespaces.py`.

## [2026-02-25] Task 9 follow-up
1. Ruff warnings were present in imported upstream files; minimal no-op edits were required to satisfy workspace lsp_diagnostics-clean rule.
2. Local Python environment lacked lxml/matplotlib/scipy initially; installed to clear import-resolution diagnostics.

## [2026-02-25] Task 11 follow-up
1. Markdown LSP server is not configured in this workspace; `lsp_diagnostics` cannot run for `.md` and requires fallback verification via grep/evidence checks.


## [2026-02-25] Task 12 follow-up
1. Markdown LSP is not configured in this workspace, so lsp_diagnostics cannot run for .md files.
2. Verification fallback used required grep count and evidence snapshot file for auditability.

## [2026-02-25] Task 13 follow-up
1. `lsp_diagnostics` for `plugins/hwpx-generator/commands/hwpx-generate.md` is unavailable because no Markdown LSP server is configured.
2. Used required evidence command output (`head` + `grep -c`) to verify no frontmatter and required orchestrator markers.
