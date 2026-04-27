# Plan: visual-generator OpenAI path — 4K defaults, gpt-5.5 fallback, CLI flags, pricing removal, dead-code cleanup

> **Branch**: `main` (commit base: `df5e23a`)
> **Scope**: OpenAI rendering path only. Gemini path is untouched (regression-protected).
> **Versioning**: visual-generator plugin MINOR bump (feature additions, no removals).

## Context

Six fixes have been pre-approved by the user on the OpenAI rendering path that was added in `df5e23a`. The Gemini path must remain byte-identical (AGENTS.md anti-pattern: "Modifying Gemini path while building OpenAI path"). All user decisions (Q1 fallback chain, Q2 pricing removal, Q3 CLI flag defaults) are locked in. Investigation phase is complete.

User decisions:
- **Q1 (gpt-5.5 verification)**: User pointed me at https://developers.openai.com/api/docs/guides/latest-model. **CONFIRMED** as OpenAI's flagship model, with vision input via Responses API, Structured Outputs, image_detail=original supported. Decision: implement runtime fallback chain `gpt-5.5 → gpt-5 → gpt-4o`.
- **Q2 (4K pricing)**: REMOVE all pricing/cost-estimate lines. Replace with neutral notice: "비용은 OpenAI 콘솔(https://platform.openai.com/usage)에서 확인하세요."
- **Q3 (CLI options)**: Add `--size`, `--quality`, `--model`, `--eval-model` with defaults `3840x2160`, `high`, `gpt-image-2`, `gpt-5.5`.

Critical hard-gates to respect throughout execution:

| Gate | Verification |
|------|--------------|
| Gemini path byte-identical | `git diff df5e23a -- plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py plugins/visual-generator/agents/renderer-agent.md plugins/visual-generator/agents/prompt-designer.md 'plugins/visual-generator/skills/theme-*/SKILL.md'` returns empty |
| LSP clean on edited script | `lsp_diagnostics` on `generate_slide_images_openai.py` returns no errors |
| AST parses | `python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py').read())"` exits 0 |
| Gemini script still runs | `python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --help` exits 0 |
| OpenAI script exposes 4 new flags | `python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --help` shows `--size --quality --model --eval-model` |
| No silent Gemini fallback | grep confirms 5.5→5→4o chain is intra-OpenAI only |
| plugin.json schema | No `contributors`/`maintainer`/etc.; only allowed fields |

## Task Dependency Graph

| Task | Depends On | Reason |
|------|------------|--------|
| T0 — TDD harness (verification matrix script) | None | Defines the contract every implementation task must satisfy |
| T1 — Script: 4K default + CLI flags + dead-code cleanup (fixes 1, 3, 6) | T0 | Must pass T0 harness checks for these three fixes |
| T2 — Script: gpt-5.5 → gpt-5 → gpt-4o fallback (fix 2) | T1 | Same file as T1; serialized to avoid merge conflicts |
| T3 — Script: pricing removal (fix 5, script portion only) | T2 | Same file; serialized after T2 |
| T4 — SKILL.md OpenAI section + frontmatter (fixes 1, 4, 5 — OpenAI section only) | T0 | Independent file from script |
| T5 — renderer-agent-openai.md updates (fixes 1, 5) | T0 | Independent file |
| T6 — commands/visual-generate.md OpenAI-line updates (fixes 1, 5) | T0 | Independent file |
| T7 — openai-quality-rubric.md scan + size-agnostic update (fix 1, if applicable) | T0 | Independent file |
| T8 — Version bumps (plugin.json, marketplace.json, README.md, AGENTS.md) | T1, T2, T3, T4, T5, T6, T7 | Versioning happens after all functional changes |
| T9 — Final verification matrix run + Gemini regression check | T8 | Last gate before commits land |
| T10 — Atomic commit sequence + push | T9 | Commits must reflect verified working tree |

Critical Path: T0 → T1 → T2 → T3 → T8 → T9 → T10

## Parallel Execution Graph

```
Wave 1 (TDD-first, no dependencies):
└── T0: Build verification harness in .sisyphus/checks/openai_4k_verify.sh

Wave 2 (Script edits — serialized; doc edits — fully parallel):
├── Script lane (sequential, single file):
│   T1 → T2 → T3
└── Docs lane (parallel, disjoint files):
    ├── T4: SKILL.md (OpenAI section + frontmatter only)
    ├── T5: renderer-agent-openai.md
    ├── T6: commands/visual-generate.md (OpenAI-only lines)
    └── T7: openai-quality-rubric.md

Wave 3 (Versioning, depends on all of Wave 2):
└── T8: plugin.json + marketplace.json + README.md + AGENTS.md

Wave 4 (Verification + commit, depends on T8):
├── T9: Run verification harness + Gemini regression
└── T10: Atomic commit sequence + push (after T9 green)
```

## Tasks

### T0 — TDD verification harness

**Output artifact**: `.sisyphus/checks/openai_4k_verify.sh` (new file).

15 checks (CHECK-01 … CHECK-15):

1. AST parse check on `generate_slide_images_openai.py`.
2. `--help` output captured; asserts presence of `--size`, `--quality`, `--model`, `--eval-model`.
3. Default-value introspection: `--help` regex matches for `default=3840x2160`, `default=high`, `default=gpt-image-2`, `default=gpt-5.5`.
4. grep negative assertions for pricing strings: `\$0.165`, `\$0.05`, `\$0.215`, `예상 비용`, `비용 추정`, `cost_estimate` across the in-scope OpenAI files.
5. grep positive assertion: `"비용은 OpenAI 콘솔"` appears at least once.
6. grep on script for the fallback chain literals `gpt-5.5`, `gpt-5`, `gpt-4o` co-located inside `evaluate_image_quality` (or helper).
7. grep negative assertion: no `1536x1024` literal anywhere in OpenAI-scope files.
8. Dead-code branch sanity: `if pil_image.format == "JPEG" or OUTPUT_FORMAT == "jpeg":` literal is gone.
9. SKILL.md frontmatter contains both `Gemini` and `OpenAI` tokens; description ≤ 1024 chars.
10. Gemini regression: `git diff df5e23a -- <gemini protected files>` empty.
11. Gemini script `--help` works.
12. plugin.json: only allowed fields; `version` bumped from current minor.
13. marketplace.json `metadata.version` synced; visual-generator entry `version` synced.
14. README.md `변경 이력` table contains a row matching today's date and the new version.
15. AGENTS.md `**Generated:**` date matches today.

**Delegation**: `category="quick"`, `load_skills=[]`.
**MUST DO**: Make executable (`chmod +x`); each check prints `PASS` / `FAIL: <reason>` with stable identifiers; exit code = number of failed checks.
**MUST NOT DO**: Modify any source file; hardcode absolute paths beyond `$REPO_ROOT`.
**Acceptance**: Running on current `df5e23a` tree yields known failing checks (the 6 fixes); after Waves 2–3, all PASS.

---

### T1 — Script: 4K default + CLI flags + dead-code cleanup

**File**: `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py`

**Subtasks**:

1. **Fix 1**: `IMAGE_SIZE = "1536x1024"` → `IMAGE_SIZE = "3840x2160"` (line 37).
2. **Fix 3**: argparse additions:
   - `--size` (default `IMAGE_SIZE`); validator: `WIDTHxHEIGHT`, both multiples of 16, max edge ≤ 3840, total pixels ≤ 8,294,400.
   - `--quality` (choices: `low|medium|high|auto`, default `high`).
   - `--model` (default `"gpt-image-2"`).
   - `--eval-model` (default `"gpt-5.5"`).
   - Thread all four through `process_prompts(...)` and `generate_image(...)` signatures.
3. **Fix 6**: Simplify lines 232–244. Keep `PIL.Image.open(BytesIO(...))` as validation (catch `UnidentifiedImageError`); write `image_bytes` directly to disk. Remove `or OUTPUT_FORMAT == "jpeg"` tautology.

**Delegation**: `category="deep"`, `load_skills=["git-master"]`.
**MUST DO**: Re-read fresh; precise hashline anchors; AST parse + LSP clean after edit; T0 CHECK-01/02/03/08 must flip to PASS.
**MUST NOT DO**: Touch `evaluate_image_quality` body (T2's job); remove pricing prints (T3's job); touch any other file.
**Acceptance**: T0 checks 1, 2, 3, 8 PASS; AST parses; LSP clean; `--help` shows the four new flags with documented defaults.

---

### T2 — Script: gpt-5.5 → gpt-5 → gpt-4o runtime fallback

**File**: `generate_slide_images_openai.py` only — modify `evaluate_image_quality` or add helper `_resolve_eval_model`.

**Logic**:

1. Build chain at runtime: `chain = [args.eval_model, "gpt-5", "gpt-4o"]` deduped while preserving order.
2. On first call, iterate chain. Catch `openai.NotFoundError` and errors with `code == "model_not_found"`. Other errors bubble up.
3. Cache first working model in module-level `_resolved_eval_model`.
4. Log on first resolution: `[eval-model] resolved to <model> (preferred: <preferred>)`.
5. Comment marker: `# AGENTS.md anti-pattern: no Gemini fallback`.

**Delegation**: `category="deep"`, `load_skills=["git-master"]`.
**MUST DO**: Use `openai.NotFoundError` (native SDK class); cache resolution once per run; T0 CHECK-06 must PASS; AST + LSP after edit.
**MUST NOT DO**: Modify CLI flags or pricing strings; allow Gemini path branch.
**Acceptance**: T0 CHECK-06 PASS; cache works; no syntax/LSP regressions.

---

### T3 — Script: pricing removal

**File**: `generate_slide_images_openai.py` only.

**Targets**:

- Line ~384 `cost_estimate = ...` calculation removed.
- Line ~386 cost-estimate string removed from report dict.
- Line ~405 `print(...)` of "예상 비용" removed.
- Embedded `generation_report.md` template cost section → single neutral line `비용은 OpenAI 콘솔(https://platform.openai.com/usage)에서 확인하세요.`.
- `--max-images` mechanism stays.

**Delegation**: `category="quick"`, `load_skills=["git-master"]`.
**MUST DO**: grep first to enumerate every pricing literal; AST + LSP + T0 CHECK-04/05 PASS.
**MUST NOT DO**: Touch cost references in doc files (T4/T5/T6 own those); remove `--max-images`.
**Acceptance**: T0 CHECK-04 + CHECK-05 PASS for the script slice; AST + LSP clean.

---

### T4 — SKILL.md updates (OpenAI section + frontmatter)

**File**: `plugins/visual-generator/skills/slide-renderer/SKILL.md`, OpenAI section only (≈ line 127 onward, including frontmatter).

**Subtasks**:

1. **Fix 4 (frontmatter description)**: Update to:
   `"Gemini와 OpenAI gpt-image-2를 사용한 슬라이드 이미지 렌더링 스킬. renderer-agent / renderer-agent-openai가 프롬프트 파일을 이미지로 변환할 때 사용. generate_slide_images.py / generate_slide_images_openai.py 실행 가이드, 환경 요구사항, 출력 해석, 에러 처리 방법을 포함합니다."`
   ≤ 1024 chars.
2. **Fix 1**: Replace `1536x1024` in OpenAI section with `3840x2160` or size-agnostic phrasing. Document `--size` override; document gpt-image-2 constraints (multiples of 16, max edge 3840, total pixels ≤ 8,294,400).
3. **Fix 5**: Remove "비용 안내" table (lines ≈180–188). Replace with neutral notice.

**Delegation**: `category="writing"`, `load_skills=[]`.
**MUST DO**: DO NOT touch Gemini section (verify by section-anchor grep); description char count ≤ 1024; T0 CHECK-09 PASS.
**MUST NOT DO**: Touch other files; drop `name` frontmatter; add `contributors`-style fields.
**Acceptance**: T0 CHECK-09 PASS; Gemini section byte-identical.

---

### T5 — renderer-agent-openai.md updates

**File**: `plugins/visual-generator/agents/renderer-agent-openai.md`

**Subtasks**:

1. **Fix 1**: Replace `1536x1024` with `3840x2160` or size-agnostic. Document `--size` override.
2. **Fix 5**: Remove cost lines (132, 187–189, Phase 5-2 cost item, line 39 max_images cost framing). Single neutral notice near generation_report template.

**Delegation**: `category="writing"`, `load_skills=[]`.
**MUST DO**: Preserve Workflow/Phase numbering; single neutral cost-disclosure sentence per file.
**MUST NOT DO**: Touch `agents/renderer-agent.md` (Gemini agent — protected).
**Acceptance**: T0 CHECK-04, CHECK-05, CHECK-07 (file-slice) PASS; Gemini agent file diff vs `df5e23a` is empty.

---

### T6 — commands/visual-generate.md OpenAI-line updates

**File**: `plugins/visual-generator/commands/visual-generate.md`, OpenAI-only lines.

**Targets**:

- Line ~60 (`$0.165/장` in question text) — remove price tag; rephrase question.
- Line ~138 (`~${N*0.215:.2f} 예상`) — remove projection; replace with neutral notice.
- Line ~132 (`max_images` description) — strip cost framing; keep cap semantics.
- Any size literal `1536x1024` in user-facing labels (Phase 0.5 / 3.5) → `3840x2160` or size-agnostic.

**Delegation**: `category="writing"`, `load_skills=[]`.
**MUST DO**: Touch only OpenAI branches; verify Gemini branches byte-identical.
**MUST NOT DO**: Touch Gemini orchestration branches; reorder phases.
**Acceptance**: `renderer="gemini"` path lines diff vs `df5e23a` is empty.

---

### T7 — openai-quality-rubric.md scan + adjust

**File**: `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md` (39 lines).

1. grep for `1536`, `1024`, `2160`, `3840`.
2. If size literals exist, replace with `3840x2160` or size-agnostic. If absent, NO-OP.

**Delegation**: `category="quick"`, `load_skills=[]`.
**MUST DO**: Always emit grep evidence; if no edit needed, leave unmodified.
**MUST NOT DO**: Reformat the rubric; add pricing.
**Acceptance**: Either no diff or minimal size-literal swap.

---

### T8 — Version bumps + changelog rows

**Subtasks**:

1. `plugins/visual-generator/.claude-plugin/plugin.json`: bump `version` MINOR. Confirm only allowed fields.
2. `.claude-plugin/marketplace.json`: bump `visual-generator` entry `version`; bump `metadata.version` MINOR.
3. `README.md`: update top `Version` line; append new row to `변경 이력` table dated today.
4. `AGENTS.md`: update `**Generated:**` date; document new OpenAI CLI flags in COMMANDS section.

**Delegation**: `category="unspecified-low"`, `load_skills=[]`.
**MUST DO**: Read current `version` first; verify field whitelist; T0 CHECK-12/13/14/15 PASS.
**MUST NOT DO**: Touch other plugins' versions; add fields outside whitelist.
**Acceptance**: All four version locations agree.

---

### T9 — Final verification matrix run + Gemini regression

**Delegation**: `category="quick"`, `load_skills=["review-work"]`.
**MUST DO**: Run `bash .sisyphus/checks/openai_4k_verify.sh` (exit 0); Gemini `--help` regression; OpenAI `--help` 4-flag check; Gemini protected diff empty; invoke `review-work`.
**MUST NOT DO**: Skip `review-work` if any check fails; apply fixes inline.
**Acceptance**: Harness exits 0; review-work 5/5 PASS.

---

### T10 — Atomic commit sequence + push

**Commit plan**:

1. `test(visual-generator-openai): add 4K verification harness` (T0)
2. `feat(visual-generator-openai): default to 4K and add --size/--quality/--model/--eval-model` (T1)
3. `feat(visual-generator-openai): runtime fallback gpt-5.5 → gpt-5 → gpt-4o` (T2)
4. `chore(visual-generator-openai): drop cost-estimate output, defer to OpenAI console` (T3 + pricing slices of T4/T5/T6)
5. `docs(visual-generator-openai): cascade 4K default to renderer docs and rubric` (non-pricing slices of T4/T5/T6/T7)
6. `docs(slide-renderer): describe both Gemini and OpenAI renderers in SKILL.md frontmatter` (T4 frontmatter slice)
7. `chore: bump visual-generator to MINOR; sync marketplace, README, AGENTS` (T8)

**Fallback**: if hunk-splitting #4–#6 is brittle, collapse into one combined `chore+docs` commit. Keep 1, 2, 3, 7 atomic always.

**Delegation**: `category="quick"`, `load_skills=["git-master"]`.
**MUST DO**: `git status` clean before staging; smoke after each commit; full harness once more after all commits; `git push origin main` only after T9 PASS.
**MUST NOT DO**: `git commit --amend` on pushed commits; force-push main; skip pre-commit hooks; commit `.env`.
**Acceptance**: 5–7 green commits on `main`; pushed; harness still PASS.

## Verification Matrix (per fix → command)

| Fix | What it proves | Command |
|---|---|---|
| 1. 4K default + cascade | Default constant is 3840x2160; no leftover `1536x1024` in OpenAI scope | `grep -n "IMAGE_SIZE" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` shows `3840x2160`; `grep -rn "1536x1024" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py plugins/visual-generator/agents/renderer-agent-openai.md plugins/visual-generator/skills/slide-renderer/SKILL.md plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md plugins/visual-generator/commands/visual-generate.md` returns empty |
| 2. gpt-5.5 fallback chain | Chain implemented & cached; Gemini never appears | `grep -nE "gpt-5\.5\|gpt-5\|gpt-4o" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` shows all three; `grep -ni "gemini" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` returns empty |
| 3. CLI flags | `--help` exposes all four flags with locked defaults | `python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --help \| grep -E -- "--size\|--quality\|--model\|--eval-model"` shows 4 lines containing `3840x2160`, `high`, `gpt-image-2`, `gpt-5.5` |
| 4. SKILL.md frontmatter | Mentions both renderers; ≤ 1024 chars | python regex check: frontmatter contains `Gemini` and `OpenAI`; description length ≤ 1024 |
| 5. Pricing removal | No price literals remain; neutral notice present | `grep -rnE '\$0\.(165\|05\|215)\|예상 비용\|비용 추정\|cost_estimate' plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py plugins/visual-generator/agents/renderer-agent-openai.md plugins/visual-generator/skills/slide-renderer/SKILL.md plugins/visual-generator/commands/visual-generate.md` returns empty; `grep -rn "비용은 OpenAI 콘솔" plugins/visual-generator/` returns ≥ 2 hits |
| 6. Dead-code cleanup | Tautological branch removed; PIL validation preserved | `grep -n "OUTPUT_FORMAT == \"jpeg\"" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` returns empty; `grep -n "Image.open" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` still returns ≥ 1 hit |

## Final Smoke Test (one block)

```bash
# 1. AST + LSP gate
python -c "import ast; ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py').read())"

# 2. Harness gate (all 15 checks)
bash .sisyphus/checks/openai_4k_verify.sh

# 3. OpenAI --help shows all four new flags with locked defaults
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py --help \
  | grep -E -- "--size|--quality|--model|--eval-model"

# 4. Gemini regression
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py --help >/dev/null
git diff df5e23a -- \
  plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py \
  plugins/visual-generator/agents/renderer-agent.md \
  plugins/visual-generator/agents/prompt-designer.md

# 5. No silent Gemini fallback in OpenAI script
! grep -in "gemini" plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py

# 6. plugin.json schema discipline
python -c "import json; A={'name','version','description','author','homepage','repository','license','keywords','skills','commands','agents','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies'}; d=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json')); extra=set(d.keys())-A; assert not extra, extra; print('plugin.json OK')"

# 7. Version sync
python -c "import json; pj=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json'))['version']; mp=json.load(open('.claude-plugin/marketplace.json')); entry=[p for p in mp['plugins'] if p['name']=='visual-generator'][0]['version']; assert pj==entry, (pj, entry); print('versions agree:', pj)"

# 8. README + AGENTS dates
grep -E "^\*\*Generated:\*\*" AGENTS.md
grep -E "^\*\*Version" README.md
```

## TODOs

### Wave 1
- [ ] **T0**: Build TDD verification harness (`.sisyphus/checks/openai_4k_verify.sh`)

### Wave 2 (Script lane serialized; Docs lane parallel)
- [ ] **T1**: Script — 4K default + CLI flags + dead-code cleanup
- [ ] **T2**: Script — gpt-5.5 → gpt-5 → gpt-4o runtime fallback
- [ ] **T3**: Script — pricing removal
- [ ] **T4**: SKILL.md — OpenAI section + frontmatter
- [ ] **T5**: renderer-agent-openai.md — 4K cascade + pricing removal
- [ ] **T6**: commands/visual-generate.md — OpenAI lines
- [ ] **T7**: openai-quality-rubric.md — scan + adjust

### Wave 3
- [ ] **T8**: Version bumps (plugin.json, marketplace.json, README.md, AGENTS.md)

### Wave 4
- [ ] **T9**: Final verification matrix + Gemini regression + review-work
- [ ] **T10**: Atomic commits + push

## Success Criteria

- All 15 T0 harness checks PASS.
- All 6 verification-matrix commands return their expected output.
- Final smoke test runs cleanly end-to-end.
- `review-work` (T9) returns 5/5 PASS.
- Gemini path diff vs `df5e23a` is empty for all protected files.
- 5–7 atomic commits pushed to `origin main`.
