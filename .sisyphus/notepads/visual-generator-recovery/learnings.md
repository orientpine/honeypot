# Visual Generator Recovery — Learnings

## Project Context
- visual-generator v2.0.0 XML-tag 전환 이후 프롬프트 품질 저하 문제 수정
- 대상 청중: KIMM(한국기계연구원) 공학 박사급 — 데이터 밀도와 기술적 깊이가 핵심
- commit `afddaf7eedfc3fe6019f46dcb76fac3a6c99fffb` 시점이 최적 품질 참조점

## Key Files
- `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` — 폰트명 유출 최상위 원본
- `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — 밀도 기준
- `plugins/visual-generator/agents/content-organizer.md`
- `plugins/visual-generator/agents/content-reviewer.md`
- `plugins/visual-generator/agents/prompt-designer.md`
- `plugins/visual-generator/agents/prompt-validator.md`
- `plugins/visual-generator/commands/visual-generate.md`
- 6개 테마 SKILL.md: theme-seminar, theme-gov, theme-pitch, theme-whatif, theme-concept, theme-comparison

## Critical Rules
- Windows cmd.exe 환경 — Unix 명령 금지, `export` 금지
- 폰트명 0건 강제: Nanum Gothic, Pretendard, Apple SD Gothic Neo, Malgun Gothic
- XML-tag 구조 유지 (v1.x 마크다운 4-block 형식으로 회귀 금지)
- generate_slide_images.py 스크립트 수정 금지
- `<typography>` 내 구체적 폰트 패밀리명 사용 금지

## Dependency Chain
Wave 1 (Parallel): T1, T2, T3, T4, T5
Wave 2 (after Wave 1): T6 (needs T1), T7 (needs T1,2,3,5,6), T8 (parallel), T9 (needs T8)
Wave 3 (after Wave 2): T10 (needs T6,7,9), T11 (needs T10)
Final: F1-F4 (parallel, after T11)

## Task 9: Style Sheet Orchestration (2026-03-09)

### Completed
- ✅ Enhanced Phase 3 (prompt-designer) in visual-generate.md
- ✅ Added slide loop structure with first-slide detection
- ✅ Implemented style_sheet_mode parameter ("create" vs "follow")
- ✅ Added style_sheet_path passing for palette consistency
- ✅ Extended MUST DO section with 2 new rules
- ✅ Verified: style_sheet (5x), is_first_slide (3x), style_sheet_mode (3x)
- ✅ Commit: ab963aa

### Key Pattern
- Orchestrator (visual-generate.md) coordinates style sheet creation/following
- First slide: style_sheet_mode="create" → prompt-designer generates style_sheet.md
- Subsequent slides: style_sheet_mode="follow" + style_sheet_path → prompt-designer reads and applies
- This ensures slide-to-slide palette consistency at orchestration level
- Actual style sheet creation/reading logic lives in prompt-designer agent

### Dependency Satisfied
- T9 depends on T8 (prompt-validator) — T8 already complete
- T9 enables T10 (renderer-agent validation) and T11 (final verification)

## Task 10: Integration Structure Test (2026-03-09)

### Completed
- Performed read+grep only verification across modified visual-generator agents/skills/command/reference files
- Created evidence report: `.sisyphus/evidence/task-10-integration-test.md`
- Structural checks result: 9 PASS / 1 FAIL

### Key Finding
- Global font leakage check matched once at `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md:11`
- Match context is warning/prohibition example sentence (`"Nanum Gothic ExtraBold" appears literally...`), not prescriptive usage
- All other target improvements verified: minimum density rules, validator 7-dimension redesign, style_sheet orchestration, REJECT-only policy, theme TYPOGRAPHY CRITICAL warnings

### Implication
- If strict global zero-match policy is required, even warning-context examples must be rewritten to avoid explicit font names
- If warning-context exception is allowed, current state is structurally compliant in practical terms

## Task F4: Scope Fidelity Audit (2026-03-09)

### Audit Result Snapshot
- Verified T1-T11 against current workspace state and evidence files
- Confirmed version sync for visual-generator 2.2.0 across plugin manifest and marketplace registry
- Confirmed style_sheet orchestration markers and prompt-validator stage continuity in command workflow

### Key Learning
- Theme-wide typography warning consistency can regress silently: 6 theme files have no forbidden font-family names, but warning coverage is uneven
- `theme-concept/SKILL.md` lacks explicit TYPOGRAPHY CRITICAL warning line used in the other 5 themes

## Task F1: Plan Compliance Audit (2026-03-09)
- Read visual-generator-recovery.md end-to-end before auditing target files.
- Verified Must Have 8/8: font leakage guardrail, body/title density rules, style_sheet orchestration, validator dimensions, slide_type schema, Minimum Text Density section, and 6 theme SKILL font cleanup.
- Verified Must NOT Have 5/5: no pt/px inside inspected typography blocks, no markdown decoration inside spot-checked XML tags, generate_slide_images.py reported UNCHANGED in git, no extra theme folders, and Gemini model remained gemini-3-pro-image-preview.
- Only font-name grep hit in plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md:11 is the allowed warning/example line explaining why literal font names are forbidden.
