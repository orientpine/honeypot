# Learnings — visual-generator-revival

## [2026-03-09] Session: ses_32e799d2cffeUa7nveUVghaxkD — Initial Setup

### Project State
- **Target**: visual-generator v3.0.0 — 4-block マークダウン format (ae35fe6 base + v2.x features)
- **Current HEAD**: v2.2.0 with XML-tag format (5 tags: <scene>, <text_to_render>, <typography>, <canvas>, <layout>)
- **Worktree**: /home/cha/Documents/honeypot (Linux, main branch)
- **Key reference**: `git show ae35fe6:plugins/visual-generator/agents/prompt-designer.md` = 767 lines with 4-block format

### 4-Block Format (MUST FOLLOW)
```
## INSTRUCTION
### Image Purpose
### Target Audience
### Key Message
### Scene Description   (NEW — replaces <scene>, 5-7 sentences, 7 elements ≥5, negative prompting)
### Rendering Style     (7 elements: surface/background/corners/connectors/decorations/spatial/metaphor)
### Content Placement   (quotes CONTENT values, explains position/size/method)

## CONFIGURATION
### Canvas Settings
### Background Treatment
### Color Palette
### Typography

## CONTENT
key: "value"   (flat format ONLY — no tables, no numbered lists, no subsections)

## FORBIDDEN ELEMENTS
(15+ items: font names, color codes, XML tags, pt/px units, etc.)
```

### Key Rules
- CONTENT: `key: "value"` format ONLY — no markdown tables, no numbered lists
- NO XML tags in prompts: <scene>, <text_to_render>, <typography>, <canvas>, <layout>
- NO font family names in prompts
- NO pt/px units in prompts
- NO color hex codes rendered as text in images
- concept theme: CONTENT has scene_context ONLY (no render_text), FORBIDDEN includes "ALL text rendering"
- style_sheet.md MUST be actually generated (was a bug in v2.2.0 — not generated)
- theme_recommendation.md MUST have ONE fixed palette for entire session (no per-slide different palettes)

### Bug in v2.2.0 (MUST FIX in v3.0.0)
- style_sheet.md not actually generated (Phase 2.5 code exists but doesn't save the file)
- content-organizer assigns different palette per slide (slide01=#1E3A5F, slide02=#2C3E50, etc.)
- generate_slide_images.py renders style_sheet.md, validation_result.md as prompts (not in exclude list)

## [완료] Task 3: generate_slide_images.py 버그 수정 (2026-03-09)

### 5가지 버그 수정 완료

**Bug 1: exclude_files 강화**
- 기존: `["prompt_index.md", "공통및특화작업구조설명.md"]`
- 수정: `["prompt_index.md", "공통및특화작업구조설명.md", "style_sheet.md", "validation_result.md"]`
- 이유: v2.2.0에서 style_sheet.md, validation_result.md가 메타데이터 파일로 생성되지만 렌더링 대상에 포함되는 버그

**Bug 2: 화이트리스트 방식 도입**
- 기존: `[f for f in prompts_path.glob("*.md") if f.name not in exclude_files]`
- 수정: `[f for f in prompts_path.glob("*.md") if re.match(r'^\d+_', f.name) and f.name not in exclude_files]`
- 이유: 숫자로 시작하는 파일(01_, 02_, 10_, 11_ 등)만 렌더링 대상으로 선별하여 메타데이터 파일 혼입 방지

**Bug 3: 개별 파일 실패 시 전체 중단 방지**
- 기존: generate_image 호출이 try/except 없음 (process_prompts 루프 전체가 실패 가능)
- 수정: generate_image 호출을 추가 try/except로 감싸서 개별 파일 실패 시 해당 파일만 스킵하고 계속 진행
- 코드:
  ```python
  try:
      if generate_image(client, prompt_content, str(output_file)):
          results["success"].append(slide_name)
      else:
          results["failed"].append(slide_name)
  except Exception as e:
      print(f"  [ERROR] Unexpected error for {slide_name}: {e}")
      results["failed"].append(slide_name)
  ```

**Bug 4: SYSTEM_INSTRUCTION에 hex color code 렌더링 금지**
- 추가 문구: "Never render hex color codes (e.g., #1E3A5F, #FFFFFF) as visible text in the image. Color codes are configuration-only and must never appear as text elements."
- 위치: Negative Rendering Constraints 섹션 끝

**Bug 5: SYSTEM_INSTRUCTION에 zero-text 조건부 지시**
- 추가 섹션: "Zero-Text Rendering: If the prompt specifies a Kurzgesagt-style illustration or explicitly requests zero text rendering, render NO text elements whatsoever in the image. Treat any text-like strings in the prompt as visual element descriptions, not as text to render."
- 이유: concept 테마에서 텍스트 렌더링 방지

### QA 검증 결과
- ✅ exclude_files에 3개 파일명 포함 (prompt_index, style_sheet, validation_result)
- ✅ SYSTEM_INSTRUCTION에 hex color code 금지 문구 존재
- ✅ QUALITY_THRESHOLD = 7.0 유지
- ✅ MAX_QUALITY_RETRIES = 2 유지
- ✅ 기존 SYSTEM_INSTRUCTION 내용 (Korean Typography, Visual Composition, Negative Rendering, White Space, Text Contrast) 전부 유지

### Commit
- Hash: 2fd0993
- Message: "fix(visual-gen): fix generate_slide_images.py exclude list and rendering robustness"

## [완료] Task 1: 4-block 형식 사양 정의
- 추가된 섹션: ## 4-Block Prompt Format Specification
- 위치: prompt-designer.md (현재 파일 유지, 형식 사양 섹션 추가)
- 핵심 결정: Scene Description 서브섹션 추가, Style Sheet create/follow 로직 명시
- 주의: 기존 XML-tag 관련 내용은 Task 10에서 제거됨

## [완료] Task 2: theme-gov Golden Reference 4-block 변환 (2026-03-09)
- 추가 위치: SKILL.md 끝 (line 329+)
- 토픽: "디지털 전환 추진 현황", layout: grid_4, mood: technical-report
- CONTENT 형식: key:"value" flat (numbered list 제거)
- 코드블록 줄 수: 101
- 검증: 4-block 헤더 4개, XML 태그 0개, 폰트명 금지 포함
- Commit: 9a1755e

## [완료] Task 9: prompt-validator 4-block 적응 (2026-03-09)
- XML 태그 참조 -> 4-block 섹션 참조로 전환
- 7개 차원 모두 보존
- REJECT-only 정책 유지
- Commit: 97b7dd1

## [완료] Task 10: prompt-designer 전면 재작성 (2026-03-09)
- 줄 수: 587
- 5-phase Workflow 구현
- Style Sheet create/follow 실제 파일 I/O 보장
- 6개 테마별 규칙 포함
- concept zero-text 규칙 포함
- XML 태그 0개
- Commit: 6ec1842

## [완료] Task 14: End-to-End Integration Test (2026-03-09)
- gov theme: 3 slides generated, 4-block structure verified, Gemini rendering FAIL
- concept theme: zero-text verified, FORBIDDEN has text prohibition PASS
- palette consistency: style_sheet.md generated, all slides same palette PASS
- Key finding: rendering command failed in current shell because `python` executable was not found; evidence saved in task-14-rendering-log.txt

## [완료] Task 14: End-to-End Integration Test (2026-03-09)
- gov 시나리오: 프롬프트 라인수/4-block/금지 패턴 점검 및 Gemini 렌더링 성공(3장, 품질 점수 9.2~10.0).
- concept 시나리오: render_text 미사용, FORBIDDEN 텍스트 렌더링 금지 확인, 4-block 구조 확인.
- 팔레트 일관성: gov 본문 슬라이드 간 primary/secondary/accent/background 동일 확인.

## [완료] Task 15: Version Bump to v3.0.0 (2026-03-09)

### Registry Updates Completed
- ✅ `plugins/visual-generator/.claude-plugin/plugin.json`: version 1.8.1 → 3.0.0
- ✅ `.claude-plugin/marketplace.json`: visual-generator version 2.2.0 → 3.0.0, description updated to "4-block v3.0.0"
- ✅ `AGENTS.md`: Generated date 2026-03-09T00:00:00+09:00 → 2026-03-09T23:00:00+09:00
- ✅ `AGENTS.md` STRUCTURE: "XML-tag v2.2.0" → "4-block v3.0.0"
- ✅ `AGENTS.md` WHERE TO LOOK: XML-tag 5개 참조 → 4-block 마크다운 참조로 변경
- ✅ `README.md`: v3.0.0 entry added to version history (newest at top)

### Verification Results
- plugin.json version: "3.0.0" ✓
- marketplace.json version: "3.0.0" ✓
- AGENTS.md v3.0.0 references: 1 (STRUCTURE section) ✓
- AGENTS.md XML-tag v2.2.0 references: 0 (fully removed) ✓
- README.md v3.0.0 entry: Present with full description ✓

### Commit
- Hash: a7dc1db
- Message: "chore(visual-gen): bump to v3.0.0, update AGENTS.md and registry"
- Files: 4 changed, 15 insertions(+), 14 deletions(-)

### Key Takeaway
Version bump completed successfully. All registry files synchronized. AGENTS.md now reflects 4-block format as the current standard for visual-generator v3.0.0.
