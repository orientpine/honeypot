# TOOLBOX PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-09
**Version:** 4.3.0
**Branch:** main

> **Reading guide**: 이 파일은 항상 자동 로드됩니다. 상세 지침은 작업 상황에 따라 [`docs/agents/`](./docs/agents/) 하위 파일을 필요할 때만 읽으세요. 어느 파일을 읽어야 하는지는 아래 [📚 상황별 지침 인덱스](#-상황별-지침-인덱스)를 참고하십시오.

## OVERVIEW

AI agent skill/plugin toolbox for Korean government R&D proposal (ISD) auto-generation, presentation figure creation, academic paper writing style extraction, and **meta-plugin for auto-generating paper writing skill sets**. Claude plugin ecosystem with orchestrated multi-agent workflows.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Generate full ISD proposal | `plugins/isd-generator/commands/isd-generate.md` | Uses `skills/input-template/` |
| Generate single ISD chapter | `plugins/isd-generator/agents/chapter{N}.md` | Chapter 3 first, then 1→2→4→5 |
| Generate figures from `<caption>` | `plugins/isd-generator/agents/figure.md` | Gemini API required |
| Generate visual materials | `plugins/visual-generator/commands/visual-generate.md` | Multi-agent pipeline. 4-block 마크다운(INSTRUCTION/CONFIGURATION/CONTENT/FORBIDDEN) 기반 |
| OpenAI gpt-image-2 렌더링 | `plugins/visual-generator/agents/renderer-agent-openai.md` | 별도 에이전트 + 신규 스크립트, OPENAI_API_KEY 필요 |
| OpenAI 렌더링 스크립트 | `plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py` | gpt-image-2 + Structured Outputs 평가 |
| OpenAI 평가 rubric | `plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md` | 5D 평가 schema (Gemini와 호환) |
| Visual generator scene richness spec | `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` | Scene complexity validation rules |
| Visual generator validation rules | `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` | Prompt validation checklist |
| Visual generator Korean typography | `plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md` | Korean text rendering guidelines |
| **Generate paper writing skills from PDFs** | `plugins/paper-style-generator/commands/paper-style-generate.md` | MinerU + Jinja2 templates |
| Generate research report | `plugins/report-generator/commands/report-generate.md` | 연구노트 → 보고서 자동 생성 |
| 한국어 심층 인터뷰 (명령어 진입점) | `plugins/general-agents/commands/interview.md` | `/general-agents:interview --quick\|--standard\|--deep` 슬래시 진입점 (v2.0.0) |
| 한국어 심층 인터뷰 (스킬, 방법론) | `plugins/general-agents/skills/deep-interview/SKILL.md` | 7-단계 상태 머신 + 5개 게이트 + 버킷 채점 + 인라인 매트릭스. oh-my-codex deep-interview 적응 (MIT) |
| 인터뷰 한국어 질문 은행 (24개) | `plugins/general-agents/skills/deep-interview/references/question-banks-ko.md` | 4개 도메인 렌즈 × 6개 질문 유형. 행(차원) → 열(렌즈) 적용 가능성 lookup |
| 인터뷰 핸드오프 계약 | `plugins/general-agents/skills/deep-interview/references/handoff-contracts.md` | 5개 옵션: plan-only / refine / execute / delegate / terminate-with-risks |
| 인터뷰 상태 사이드카 스키마 | `plugins/general-agents/skills/deep-interview/references/state-schema.md` | `.claude/plans/*.state.json` JSON Schema, 원자적 rename G3 가드 |
| 인터뷰 wrapper 에이전트 (하위 호환) | `plugins/general-agents/agents/interview.md` | `@general-agents 의 interview` 호출 패턴 보존, deep-interview 스킬로 위임 (v2.0.0) |
| HWPX 문서 생성 | `plugins/hwpx-generator/commands/hwpx-generate.md` | XML-first + ZIP치환 |
| HWPX XML-first 빌드 | `plugins/hwpx-generator/skills/hwpx-core/SKILL.md` | build_hwpx.py 기반 (cell_writer.py는 linesegarray 제거 strip-only), 레퍼런스 복원 우선 |
| HWPX ZIP-level surgery | `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` | 안전한 ZIP-level 편집 (stdlib only, lxml 불필요), HwpxSurgeon 클래스 |
| HWPX surgery 가이드 | `plugins/hwpx-generator/skills/hwpx-core/references/zip-surgery-guide.md` | 10가지 안전 규칙 명세 |
| HWPX linesegarray 제거 (strip-only) | `plugins/hwpx-generator/skills/hwpx-core/scripts/cell_writer.py` | stale linesegarray 제거 유틸리티 (build_hwpx/pack은 기본적으로 제거, 생성 안 함) |
| HWPX linesegarray strip (ZIP-surgery 경로) | `plugins/hwpx-generator/skills/hwpx-core/scripts/zip_surgery.py` | `write_zip()`이 `Contents/section*.xml` 기록 직전 `strip_linesegarray()`로 자동 제거 — slot_filler/section_transplant/replace_text 산출물의 자간 뭉침·텍스트 중첩 버그 차단 |
| HWPX 페이지 가드 | `plugins/hwpx-generator/skills/hwpx-core/scripts/page_guard.py` | 레퍼런스 대비 페이지 드리프트 위험 검사 |
| HWPX 템플릿 치환 | `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md` | fix_namespaces.py 필수, ZIP surgery 후 cell_writer 금지 |
| HWPX 마크다운 파싱 | `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` | Markdown → JSON blocks (Workflow 7) |
| HWPX 인라인 마크다운 정규화 | `plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py` | `strip_non_emphasis_markdown()`이 코드스팬·취소선·링크를 제거. 표 셀(`strip_inline_markdown`)과 문단·불릿·인용(`parse_inline_segments`) 두 경로가 이 한 함수를 공유해 경로별로 다르게 새던 마커를 차단 |
| HWPX XML 작성 | `plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py` | JSON + style config → HWPX XML fragment |
| HWPX 이미지 임베딩 | `plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py` | PNG embedding into HWPX (Workflow 7) |
| HWPX 다중 MD 병합 | `plugins/hwpx-generator/skills/hwpx-core/scripts/md_merger.py` | heading offset 자동계산, --target-level 옵션 |
| HWPX 챕터 이식 (section transplant) | `plugins/hwpx-generator/skills/hwpx-core/scripts/section_transplant.py` | 범용 CLI + HwpxSurgeon.transplant_from() |
| HWPX 양식 파악 슬롯 추출 | `plugins/hwpx-generator/skills/hwpx-core/scripts/form_mapper.py` | analyze_template 재사용, 빈 셀/라벨 인접 결정적 추출 |
| HWPX 슬롯 채우기 (paragraph-id 치환) | `plugins/hwpx-generator/skills/hwpx-core/scripts/slot_filler.py` | id-scoped string surgery, zip_surgery 불변식 준수 |
| HWPX 슬롯 의미 매핑 에이전트 | `plugins/hwpx-generator/agents/hwpx-form-analyzer.md` | slot_type/zone/confidence 결정, addressing read-only |
| form_map.json 스키마 계약 | `plugins/hwpx-generator/skills/hwpx-core/references/form-map-schema.md` | 슬롯 JSON 계약 v1.0.0, style-map.json과 구분 |
| Plugin development toolkit | `plugins/plugin-dev/commands/create-plugin.md` | Hook, MCP, 구조, 설정, 커맨드/에이전트/스킬 개발 |
| Patent trend analysis | `plugins/patent-trend-analyzer/commands/analyze-patents.md` | KIPRIS API 기반 계획→검색→분석 파이프라인 |
| PPTX design styles (30 styles) | `plugins/pptx-design-styles/skills/pptx-design-styles/SKILL.md` | Glassmorphism, Neo-Brutalism 등 30가지 디자인 스타일 가이드 |
| Obsidian Markdown 작성 | `plugins/obsidian-skills/skills/obsidian-markdown/SKILL.md` | Wikilinks, embeds, callouts, properties |
| Obsidian Bases 작성 | `plugins/obsidian-skills/skills/obsidian-bases/SKILL.md` | .base 파일 뷰/필터/수식 |
| JSON Canvas 작성 | `plugins/obsidian-skills/skills/json-canvas/SKILL.md` | .canvas 노드/엣지/그룹 |
| Obsidian CLI | `plugins/obsidian-skills/skills/obsidian-cli/SKILL.md` | vault 조작, 플러그인 개발 |
| 웹 페이지 클린 추출 | `plugins/obsidian-skills/skills/defuddle/SKILL.md` | Defuddle CLI 마크다운 추출 |
| 가속 학습 파이프라인 실행 | `plugins/accelerated-learner/commands/accelerated-learn.md` | 48시간 딥러닝 방법론 |
| 소크라틱 튜터링 | `plugins/accelerated-learner/agents/socratic-tutor.md` | 대화형 학습 |
| 개인 지식 위키 생성 | `plugins/wiki-gen/skills/wiki-gen/SKILL.md` | 일기/노트 → Wikipedia 스타일 위키 컴파일 (v1.2.0: 10개 커맨드 ingest/absorb/remediate/query/cleanup/breakdown/status/rebuild-index/reorganize/sync, Scale Mode 파티션 병렬, Anti-Dump Rule, Citation Discipline, 에이전트 프롬프트 템플릿 assets/, 포터블 헬퍼 스크립트 scripts/) |
| HoneyCombo URL 제출 | `plugins/link-curator/commands/curate-links.md` | URL→MD (link-summarizer) + gh CLI submit (honeycombo-submit) |
| Plugin registry | `.claude-plugin/marketplace.json` | All 14 plugins listed |

**Note**: Original `examples/` folder with real company names archived in local branch `archive/examples-backup` (not pushed to public repository).

---

## 📚 상황별 지침 인덱스

> 아래 표는 **언제 어떤 상세 지침 파일을 읽어야 하는지** 알려줍니다. 작업과 무관한 파일은 읽지 마세요.

| 작업 상황 | 참조 파일 |
|-----------|-----------|
| 새 플러그인 개발, 컴포넌트 추가 시 Skill vs Agent 선택 | [`docs/agents/skills-vs-agents.md`](./docs/agents/skills-vs-agents.md) |
| Bash/터미널 명령 실행 (특히 git, python, npm) | [`docs/agents/windows-bash-rules.md`](./docs/agents/windows-bash-rules.md) |
| 스킬 내 스크립트(`scripts/*.py`) 참조/실행 | [`docs/agents/script-path-resolution.md`](./docs/agents/script-path-resolution.md) |
| Figure prompt / Paper Style / wiki-gen 워크플로우 | [`docs/agents/unique-styles.md`](./docs/agents/unique-styles.md) |
| 플러그인 스크립트 CLI 실행 (이미지, HWPX, wiki-gen 등) | [`docs/agents/commands-reference.md`](./docs/agents/commands-reference.md) |
| 플러그인 추가/수정/삭제, plugin.json·marketplace.json 변경 | [`docs/agents/marketplace-rules.md`](./docs/agents/marketplace-rules.md) |
| 작업 완료 후 AGENTS.md / README.md 최신화 | [`docs/agents/doc-maintenance.md`](./docs/agents/doc-maintenance.md) |

---

## SKILLS VS AGENTS (요약)

플러그인 개발 시 **Skill**(지식/절차 제공, 메인 컨텍스트 내 로드)과 **Agent**(자율 실행, 격리 컨텍스트) 중 적합한 유형을 선택해야 합니다. 상세 비교표와 선택 기준은 [`docs/agents/skills-vs-agents.md`](./docs/agents/skills-vs-agents.md) 참조.

---

## 핵심 컨벤션

### Skill / Agent 파일 구조

- **Skill**: `plugins/{plugin}/skills/{skill}/SKILL.md` (필수) + `references/`, `assets/`, `scripts/` (선택)
- **Agent**: `plugins/{plugin}/agents/{agent-name}.md`
- **Frontmatter 필드**: `name`, `description`, `tools`, `model` (선택)
- **상세 스펙 / 마켓플레이스 등록 규칙**: [`docs/agents/marketplace-rules.md`](./docs/agents/marketplace-rules.md)

### Document Language

- All ISD content: Korean (한글)
- All presentations: Korean with English technical terms
- Agent definitions: Korean

### Critical Workflow Rules

- ISD chapter order: **3 → 1 → 2 → 4 → 5** (Chapter 3 first)
- Verification docs: Generate BEFORE main content (절대 스킵 금지)
- Task delegation: Use `Task(subagent_type=...)` - never analyze directly
- Auto mode: `auto_mode=true` skips user confirmations
- `/start-work` 완료 후: 모든 작업이 끝나면 반드시 `git push`를 실행하여 원격 저장소에 반영

### ⚠️ 중요 환경 경고

- **Windows 환경 (cmd.exe)**: Bash 도구로 명령 실행 시 Unix `export` 구문 절대 금지. 명령어를 프리픽스 없이 직접 실행. 상세: [`docs/agents/windows-bash-rules.md`](./docs/agents/windows-bash-rules.md)
- **스킬 내 스크립트 참조**: 상대경로 우선 → Glob 폴백. **자체 Python 코드 작성 금지**. 상세: [`docs/agents/script-path-resolution.md`](./docs/agents/script-path-resolution.md)

---

## ANTI-PATTERNS (THIS PROJECT)

| Forbidden | Reason |
|-----------|--------|
| Skipping verification documents | Entire chapter becomes invalid |
| Placeholder text `[내용]` in prompts | Gemini will render literally |
| Rendering hints in ASCII `(24pt)` | Will appear in generated image |
| Generating Chapter 1 before Chapter 3 | Dependency: Ch1 derives from Ch3 |
| Modifying Gemini path while building OpenAI path | Cross-task contamination, Gemini 회귀 위험 (보호 파일 allowlist 준수 필수) |
| OpenAI 실패 시 silent Gemini fallback | 사용자 의도 위반, 명시적 OpenAI 선택을 무시함 (반드시 hard-fail with 한국어 에러) |
| 템플릿 채우기 시 form_map 없이 즉흥 삽입 위치 결정 | Must NOT — Phase 2.5 양식 파악 없이 MD↔영역 매핑 불가 |
| 빈 셀 전역 `str.replace()` 치환 | Must NOT — 바이트-동일 빈 셀 전부 변경됨. slot_filler.py의 paragraph-id 스코프 치환 사용 |

---

## NOTES

- **API Key**: `.env` 파일에서 `GEMINI_API_KEY` 환경변수 로드 (python-dotenv 사용)
- **Model**: `gemini-3-pro-image` for 4K 16:9 images with Korean text
- **Rate Limit**: 2-second delay between API calls
- **ISD Output**: `output/[프로젝트명]/chapter_{1-5}/`
- **All SKILL.md files**: Contain exhaustive workflow phases with numbered steps
