# Project-Specific Unique Styles

> **언제 읽나요**: ISD figure 프롬프트 작성, 투자 포트폴리오 멀티 에이전트 워크플로우 설정, paper-style-generator 사용, wiki-gen 운영 등 **프로젝트별 고유 스타일/규칙**이 적용되는 작업을 할 때.
> **상위 문서**: [AGENTS.md](../../AGENTS.md)

## Figure Prompt Requirements (500+ lines)

ISD generator의 figure 에이전트가 사용하는 프롬프트 형식 요구사항입니다.

- 14 mandatory sections (1-14)
- ASCII layout for 6 regions
- 50+ text items, 8+ data tables
- 4-color palette: `#1E3A5F`, `#4A90A4`, `#2E7D5A`, `#F5F7FA`

## Multi-Agent Portfolio System

investments-portfolio 플러그인의 멀티 에이전트 워크플로우입니다.

- **Workflow**: `macro-analysis` → `fund-portfolio` → `compliance-checker` → `output-critic`
- **Output files**: `00-macro-outlook.md` through `04-portfolio-summary.md`
- **Folder**: `portfolios/YYYY-MM-DD-{profile}-{session}/`

## Paper Style Generator (Meta-Plugin)

PDF 논문에서 작성 스타일을 추출해 새로운 플러그인을 자동 생성하는 메타 플러그인입니다.

- **Purpose**: Analyze PDF papers (10+) and auto-generate paper writing skill sets
- **Workflow**: `paper-style-generate` (command) → `pdf-converter` → `style-analyzer` → `skill-generator`
- **Input**: PDF papers from same author/research group or same field
- **Output**: Hybrid plugin in `{CWD}/my-marketplace/plugins/{name}-paper-skills/`
  - Command (1): `{name}-paper-generate.md` (오케스트레이터)
  - Agents (8): `{name}-title-writer`, `{name}-abstract-writer`, `{name}-introduction-writer`, `{name}-methodology-writer`, `{name}-results-writer`, `{name}-discussion-writer`, `{name}-caption-writer`, `{name}-verify`
  - Skill (1): `{name}-style-guide`
  - Plugin metadata: `.claude-plugin/plugin.json`
- **Orchestrator Features**:
  - Sequential section generation: Title → Abstract → Introduction → Methodology → Results → Discussion → Captions
  - Final verification via `{name}-verify`
  - Cross-section consistency tracking (sample sizes, metrics, biomarkers)
  - Execution modes: Full Auto, Propagation Management
  - Output: `output/{paper_topic}/manuscript_complete.md`
- **Style Analysis Extracts**:
  - Voice ratio (active/passive) per section
  - Tense patterns (past/present)
  - "We" usage ratio in Results (target: ≤30%)
  - High-frequency academic verbs
  - Transition phrases by section
  - Measurement formatting patterns
  - Citation style detection
  - Field characteristics from keywords

## Personal Knowledge Wiki (wiki-gen v1.2.0)

- **Source**: Port of `farzaa/wiki-gen-skill` gist (MIT) + 1826-entry 실사용 경험 기반 v1.2.0 확장
- **Commands (10)**: `wiki ingest` → `wiki absorb [date-range]` → `wiki remediate` → `wiki query|cleanup|breakdown|status|rebuild-index|reorganize|sync`
- **New in v1.2.0**: C1 Wikilink Syntax `[[filename_stem|Title]]` (Obsidian 파일명 기반 resolution), C2 Filename Convention (ASCII snake_case 필수), C3 Citation Discipline (frontmatter `sources:` canonical + body `## References` human-readable), C4 Anti-Dump Rule (verbatim paste 금지, 150-line cap, 5:1 compression), C5 Scale Mode (Partitioned Parallel for 500+ entry vaults), C6 Date Extraction priority order (8-tier fallback, datetime validation, mtime warning), C7 Standard Exclusions (.git/.obsidian/.claude/node_modules/etc), I1 Aliases Discipline, I2 Agent Prompt Templates (assets/), I3 wiki remediate command (citation gap closure), I4 wiki sync command (multi-source sources.yaml orchestration), N1-N5 (checkpoint cadence, status format, schema, coverage vs content, query by type)
- **Writing Standards**: Wikipedia tone (flat/factual/encyclopedic). Forbidden: em dashes, peacock words, editorial voice, progressive narrative, qualifiers. Direct quotes carry emotional weight; articles stay neutral.
- **Anti-Patterns**: Anti-Cramming (3rd sub-topic paragraph → new page), Anti-Thinning (stubs are failures, every touch must enrich), Anti-Dump (never paste raw entry text verbatim — C4)
- **39-Directory Emergent Taxonomy (7 groups)**: Core (6), Media/Culture (8), Inner Life (5), Narrative (5), Relationships (3), Work/Strategy (5), Other (7). Directories emerge from data; never pre-create.
- **Absorption Loop**: Small vaults process chronologically; 500+ entry vaults use partitioned parallel (Scale Mode). Checkpoint cadence varies by mode (15/30-50/per-batch).
- **Concept Articles**: Recurring patterns/themes become pages (`philosophies/`, `patterns/`, `tensions/`, `identities/`) - where the wiki becomes "a map of a mind", not a contact list
- **Bundled resources**: `assets/` (4 agent prompt templates + README), `scripts/` (13 portable Python helpers with argparse CLI)
- **Backward compatibility**: v1.0.0 wikis work without migration; C1/C2/N3 enforced only on new/edited articles, legacy gaps become lint warnings (see `## Migration from v1.0.0` in SKILL.md)
