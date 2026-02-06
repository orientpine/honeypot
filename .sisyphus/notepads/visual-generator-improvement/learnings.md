# Learnings - visual-generator-improvement

## Conventions & Patterns Discovered


## [2026-02-05] Task 3: layout-types 스킬 유지 확인

**Verification Results:**
- File exists: YES ✓
- Layout count: 24/24 ✓
- Path for agent reference: `plugins/visual-generator/skills/layout-types/SKILL.md`

**Status:** PASS

**Key Finding:**
The layout-types skill file is properly maintained with all 24 layout type sections intact. This file is ready for agent file references in future development.

**Reference Path for Agents:**
When creating agent files that need to reference layout types, use the absolute path:
```
plugins/visual-generator/skills/layout-types/SKILL.md
```

Do NOT use `${CLAUDE_PLUGIN_ROOT}` or relative paths in agent content.

## Task 2: 테마 데이터 이관 (2026-02-05)

### Theme Data Structure Pattern
- **Source locations**: Each skill file has 9 mood themes embedded in SKILL.md
  - `prompt-concept/SKILL.md` lines 482-627
  - `prompt-gov/SKILL.md` lines 208-287
  - `prompt-seminar/SKILL.md` lines 559-696
- **Theme naming consistency**: All 3 skills share same 9 theme names:
  1. technical-report (기술 보고서)
  2. clarity (명료)
  3. tech-focus (테크)
  4. growth (성장)
  5. connection (연결)
  6. innovation (혁신)
  7. knowledge (지식) - marked as "신규"
  8. presentation (발표) - marked as "신규"
  9. workshop (워크숍) - marked as "신규"

### Color Palette Structure
- **4-color system**: 주조(primary), 보조(secondary), 강조(accent), 배경(background)
- **HEX format**: All colors in `#XXXXXX` format (6 hex digits)
- **Total colors per file**: 9 themes × 4 colors = 36 HEX codes
- **Verification**: `grep -c "#[0-9A-Fa-f]\{6\}"` reliably counts HEX codes

### Theme Metadata Components
Each theme includes:
1. **Name**: Korean + English (e.g., "기술 보고서 (technical-report)")
2. **용도 (Usage)**: When to use this theme
3. **색상 팔레트 (Color Palette)**: 4 colors with role descriptions
4. **스타일 노트 (Style Notes)**: 2-4 bullet points on mood/context

### Differences Between Skills
- **concept.md**: Most detailed style notes (3-4 bullets), includes "권장" tag on theme 1
- **gov.md**: Government/official tone, emphasizes formality and authority
- **seminar.md**: Academic/presentation tone, shorter style notes (2-3 bullets)
- **Color codes**: IDENTICAL theme names but DIFFERENT color palettes per skill

### File Organization Success
- Created `references/themes/` directory structure
- Separated theme data from skill logic (preparation for centralization)
- Each file is self-contained with overview section
- Markdown table format preserved for color palettes

### Verification Commands
```bash
# Directory check
ls -la plugins/visual-generator/references/themes/

# Color count (must be 36)
grep -c "#[0-9A-Fa-f]\{6\}" plugins/visual-generator/references/themes/{file}.md

# Theme section count (must be 9)
grep -c "#### 테마 [0-9]" plugins/visual-generator/references/themes/{file}.md
```

All verification passed:
- ✅ 3 files created
- ✅ 36 colors per file
- ✅ 9 themes per file

## [2026-02-05] Task 4: orchestrator.md Agent 생성

**Created:** `plugins/visual-generator/agents/orchestrator.md`

**Structure Pattern (from isd-generator orchestrator):**
1. YAML frontmatter: name, description, tools, model
2. Overview with agent pipeline diagram
3. Input Schema with table format
4. Workflow with Phase 0-5 structure
5. auto_mode behavior table
6. Error Handling with retry/rollback logic
7. Output Structure with directory tree
8. Sub-Agent References table
9. Resources (paths, themes)
10. MUST DO / MUST NOT DO checklists
11. Usage Examples

**Key Design Decisions:**
- 4-agent pipeline: content-organizer → content-reviewer → prompt-designer → renderer-agent
- Checkpoint/rollback system for failure recovery
- Auto-retry with max 2-3 attempts per phase
- Validation gates between phases

**Verification Results:**
- File exists: YES ✓
- File size: 12103 bytes
- Sub-agent references: 22 occurrences (≥4 required)
- All sections present: YES ✓
- No LSP diagnostics

**Agent File Path Pattern:**
Use `Task(subagent_type="visual-generator:{agent-name}")` for sub-agent calls.
## 2026-02-05: content-organizer.md 생성

### Created
- `plugins/visual-generator/agents/content-organizer.md` (12KB)

### Key Decisions
- Model: sonnet (lighter than opus, sufficient for analysis)
- Tools: Read, Glob, Grep, Write (no Bash needed)
- Output: 3 files (concepts.md, slide_plan.md, theme_recommendation.md)

### Patterns Applied
- Followed orchestrator.md structure for consistency
- Relative paths only (no ${CLAUDE_PLUGIN_ROOT})
- 9 theme moods × 3 styles = 27 palette options
- 24 layout types with selection guide
- MUST DO / MUST NOT DO clearly separates responsibilities


## [2026-02-05] Task 9: 신규 테마 생성 (whatif, pitch, comparison)

### Created Files
- `plugins/visual-generator/references/themes/whatif.md` (3188 bytes)
- `plugins/visual-generator/references/themes/pitch.md` (3465 bytes)
- `plugins/visual-generator/references/themes/comparison.md` (3978 bytes)

### Purpose-Specific Theme vs Mood Theme

| 기존 테마 (gov, seminar, concept) | 신규 테마 (whatif, pitch, comparison) |
|----------------------------------|--------------------------------------|
| 9가지 무드별 팔레트 | 단일 용도별 팔레트 |
| 36개 색상 (9×4) | 4개 색상 (1×4) |
| 범용 시각 스타일 | 특정 사용 케이스 최적화 |
| 동일 테마명 공유 | 독립적 테마 정의 |

### Theme Structure Pattern (Purpose-Specific)
```markdown
# [Theme Name] 테마

## 개요
- 용도 설명
- 활용 상황 bullet points

## 색상 팔레트
| 역할 | 색상 | HEX | 용도 |
(4 colors: 주조, 보조, 강조, 배경)

## 권장 레이아웃
- Layout 1 with ASCII diagram
- Layout 2 with ASCII diagram

## 스타일 노트
- 구체적 사용 지침

## 적합한 케이스
## 부적합한 케이스
```

### Color Palette Choices (Rationale)
| Theme | Primary | Secondary | Accent | Background | Design Intent |
|-------|---------|-----------|--------|------------|---------------|
| whatif | #1A535C (틸) | #4ECDC4 (블루) | #FF6B35 (오렌지) | #F7FFF7 (크림) | 미래지향 + 변화 강조 |
| pitch | #0A2540 (네이비) | #425466 (그레이) | #635BFF (블루) | #FFFFFF (화이트) | 고대비 + 신뢰감 |
| comparison | #2D3436 (차콜) | #00B894 (에메랄드) | #FF7675 (코랄) | #F5F6FA (그레이) | Before(어둠)→After(밝음) 방향성 |

### Layout Recommendations
- **whatif**: Section-Flow (vision + steps), Z-Pattern (persuasion flow)
- **pitch**: Z-Pattern (message flow), Single-Hero (impact number)
- **comparison**: Contrast metaphor (side-by-side A/B panels)

### Verification Commands
```bash
# File existence
ls -la plugins/visual-generator/references/themes/{whatif,pitch,comparison}.md

# Color count (must be ≥4)
for f in whatif pitch comparison; do 
  echo "$f.md: $(grep -c '#[0-9A-Fa-f]\{6\}' plugins/visual-generator/references/themes/${f}.md) colors"
done

# Layout reference check (whatif only)
grep -E "(Section-Flow|Z-Pattern)" plugins/visual-generator/references/themes/whatif.md
```

### Results
- ✅ whatif.md: 4 colors, Section-Flow + Z-Pattern recommended
- ✅ pitch.md: 4 colors, Z-Pattern + Single-Hero layouts
- ✅ comparison.md: 5 colors, Contrast metaphor layout

## E2E Test Learnings (2026-02-05)

### Successful Patterns
1. **4-block prompt structure works well**:
   - INSTRUCTION BLOCK: Image generation directive
   - CONFIGURATION BLOCK: Resolution, colors, layout
   - CONTENT BLOCK: Korean-only text content
   - FORBIDDEN ELEMENTS: Explicit constraints

2. **Gemini API behavior**:
   - `gemini-3-pro-image-preview` generates images > 4K (5504x3072)
   - Script properly handles 4K request, Gemini upscales
   - Korean text in CONTENT BLOCK renders correctly

3. **Test setup**:
   - Virtual env required on Debian systems (externally-managed)
   - `.venv/bin/python` for running scripts
   - `export $(grep -v '^#' .env | xargs)` loads API key

### Technical Details
- Output file: ~7MB PNG (5504x3072)
- Processing time: ~30 seconds per image
- Model: gemini-3-pro-image-preview with thinking mode enabled
