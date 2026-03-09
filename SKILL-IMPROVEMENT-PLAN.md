# Honeypot 스킬 품질 개선 작업 계획서

**작성일**: 2026-03-08
**목적**: 46개 SKILL.md 품질 평가 결과에 따른 9개 개선 항목 실행 계획
**원칙**: 코드 수정만, AGENTS.md/marketplace.json/plugin.json 버전 동기화 포함

---

## 작업 요약

| Wave | 항목 | 난이도 | 예상 파일 수 |
|:----:|------|:------:|:-----------:|
| **Wave 1** (병렬) | #1 plugin-dev name 소문자화, #2 layout-types/slide-renderer 트리거 추가 | 낮음 | 9 |
| **Wave 2** (병렬) | #3 22개 스킬 "Use when..." 추가 | 낮음 | 22 |
| **Wave 3** (병렬) | #4 paper-style-toolkit 확장, #5 core-resources 확장, #6 verification-rules 보강 | 중간 | 3 |
| **Wave 4** (병렬) | #7 500줄 초과 스킬 분할, #8 theme-* 교차 참조, #9 skill-development 리소스 보강 | 높음 | ~15+ |
| **Wave 5** (순차) | 버전 업데이트 + AGENTS.md 최신화 | 낮음 | 3 |

---

## Wave 1: P0 구조적 수정 (병렬 실행)

### 항목 #1: plugin-dev 7개 스킬 frontmatter name 소문자화

**문제**: Agent Skills Spec은 `name` 필드가 소문자+하이픈이어야 하고 디렉토리명과 일치해야 함. 현재 7개 전부 Title Case.
**영향**: 스킬 매칭 실패 가능성
**원인**: Anthropic 원본 저장소(anthropics/claude-code)에서 동일한 버그가 존재하며, 포팅 시 그대로 계승됨

**수정 대상 (7개 파일):**

| 파일 | 현재 `name` | 변경 후 |
|------|------------|--------|
| `plugins/plugin-dev/skills/agent-development/SKILL.md` | `Agent Development` | `agent-development` |
| `plugins/plugin-dev/skills/command-development/SKILL.md` | `Command Development` | `command-development` |
| `plugins/plugin-dev/skills/hook-development/SKILL.md` | `Hook Development` | `hook-development` |
| `plugins/plugin-dev/skills/mcp-integration/SKILL.md` | `MCP Integration` | `mcp-integration` |
| `plugins/plugin-dev/skills/plugin-settings/SKILL.md` | `Plugin Settings` | `plugin-settings` |
| `plugins/plugin-dev/skills/plugin-structure/SKILL.md` | `Plugin Structure` | `plugin-structure` |
| `plugins/plugin-dev/skills/skill-development/SKILL.md` | `Skill Development` | `skill-development` |

**수정 방법**: 각 SKILL.md의 frontmatter `name:` 줄만 변경. 본문은 건드리지 않음.

**예시:**
```yaml
# Before
---
name: Agent Development
description: ...
---

# After
---
name: agent-development
description: ...
---
```

**버전**: plugin-dev 전체 PATCH 버전 올림 (`0.1.0` → `0.1.1`)

---

### 항목 #2: layout-types, slide-renderer "Use when..." 트리거 추가

**문제**: layout-types(81줄, frontmatter 정상)와 slide-renderer(76줄)에 "Use when..." 트리거 문구 없음

**수정 대상 (2개 파일):**

| 파일 | 현재 description | 변경 후 |
|------|-----------------|--------|
| `plugins/visual-generator/skills/layout-types/SKILL.md` | `"visual-generator 스킬이 공유하는 24종 레이아웃 정의. 각 레이아웃의 핵심 아이디어, ASCII 시각 구성, 시각화 원칙, 권장 사양, 적합/부적합 케이스를 포함합니다."` | `"visual-generator 스킬이 공유하는 24종 레이아웃 정의. Use when 시각자료의 레이아웃을 선택하거나 레이아웃별 구성 원칙을 확인해야 할 때. 각 레이아웃의 핵심 아이디어, ASCII 시각 구성, 시각화 원칙, 권장 사양, 적합/부적합 케이스를 포함합니다."` |
| `plugins/visual-generator/skills/slide-renderer/SKILL.md` | `"Gemini API를 사용한 슬라이드 이미지 렌더링 스킬. renderer-agent가 프롬프트 파일을 이미지로 변환할 때 사용. ..."` | `"Gemini API를 사용한 슬라이드 이미지 렌더링 스킬. Use when 프롬프트 파일(.md)을 Gemini API로 4K PNG 이미지로 변환해야 할 때. generate_slide_images.py 스크립트 실행 가이드, 환경 요구사항, 출력 해석, 에러 처리 방법을 포함합니다."` |

**수정 방법**: 각 SKILL.md frontmatter의 `description:` 줄만 변경.

**버전**: visual-generator PATCH 버전 올림

---

## Wave 2: "Use when..." 트리거 일괄 추가 (병렬 실행)

### 항목 #3: 22개 스킬에 "Use when..." 추가

**문제**: 46개 중 22개 스킬의 description에 "Use when..." 트리거가 없어 Claude가 자율적으로 스킬을 활성화하지 못함

**수정 방법**: 각 SKILL.md frontmatter의 `description:` 필드에 "Use when ..." 문구를 삽입. description 1024자 이내 유지.

**수정 대상 및 제안 트리거 (22개):**

#### isd-generator (10개)

| 스킬 | 제안 트리거 |
|------|-----------|
| `chapter1-guide` | `Use when ISD 연구계획서 Chapter 1 (연구 개요/필요성)을 작성할 때.` |
| `chapter2-guide` | `Use when ISD 연구계획서 Chapter 2 (국내외 기술 현황)를 작성할 때.` |
| `chapter3-guide` | `Use when ISD 연구계획서 Chapter 3 (연구 목표/내용/방법)을 작성할 때.` |
| `chapter4-guide` | `Use when ISD 연구계획서 Chapter 4 (연구 추진체계/일정)를 작성할 때.` |
| `chapter5-guide` | `Use when ISD 연구계획서 Chapter 5 (기대효과/활용)를 작성할 때.` |
| `data-collection-guide` | `Use when Chapter 2 시장/기술 데이터 수집 품질을 검증할 때.` |
| `figure-guide` | `Use when ISD 연구계획서 이미지 프롬프트를 생성할 때.` |
| `image-reference-guide` | `Use when Gemini API 이미지 생성 참조 패턴을 확인할 때.` |
| `input-template` | `Use when ISD 오케스트레이터에 입력할 프로젝트 정보 템플릿을 준비할 때.` |
| `verification-rules` | `Use when ISD 검증문서 생성 규칙을 확인하거나 검증 단계를 수행할 때.` |

#### investments-portfolio (4개)

| 스킬 | 제안 트리거 |
|------|-----------|
| `bogle-principles` | `Use when 투자 철학 원칙을 적용하거나 펀드 추천의 근거를 제시할 때.` |
| `dc-pension-rules` | `Use when DC형 퇴직연금 규정 준수 여부를 검증하거나 포트폴리오를 구성할 때.` |
| `fund-output-template` | `Use when 펀드 포트폴리오 분석 결과를 마크다운으로 출력할 때.` |
| `macro-output-template` | `Use when 거시경제 분석 보고서를 마크다운으로 출력할 때.` |

#### stock-consultation (3개)

| 스킬 | 제안 트리거 |
|------|-----------|
| `analyst-common-stock` | `Use when 주식/ETF 분석 에이전트의 웹검색 및 교차검증 프로토콜을 적용할 때.` |
| `file-save-protocol-stock` | `Use when 주식 상담 분석 결과를 파일로 저장할 때.` |
| `stock-data-verifier` | `Use when 주식/ETF 데이터의 정확성을 웹검색으로 교차검증할 때.` |

#### report-generator (3개)

| 스킬 | 제안 트리거 |
|------|-----------|
| `chapter-structure` | `Use when 연구 보고서의 챕터 구조를 정의하거나 챕터 충분성을 평가할 때.` |
| `field-keywords` | `Use when 연구 노트의 도메인(ROS2/AI/ML 등)을 감지하거나 도메인 키워드를 매핑할 때.` |
| `four-step-pattern` | `Use when 연구 보고서 소절을 4단계 패턴(과제→문제→해결→기술)으로 작성할 때.` |

#### visual-generator (2개) — Wave 1 항목 #2에서 처리됨

**수정 방법**: 기존 description 앞이나 중간에 "Use when ..." 문구를 자연스럽게 삽입.

**버전**: 각 플러그인 PATCH 버전 올림

---

## Wave 3: 빈약한 SKILL.md 확장 (병렬 실행)

### 항목 #4: paper-style-toolkit SKILL.md 확장

**현재 상태**: 47줄. 스크립트 실행 경로만 나열. 리소스 조직은 우수(scripts/ 5개, references/ 2개, assets/ 12개 템플릿)하지만 SKILL.md에서 전혀 설명 없음.

**파일**: `plugins/paper-style-generator/skills/paper-style-toolkit/SKILL.md`

**추가할 내용 (기존 내용 뒤에 추가):**

```markdown
## 파이프라인 개요

paper-style-generator는 3단계 파이프라인으로 작동합니다:

1. **PDF → Markdown 변환** (`mineru_converter.py`)
   - MinerU 엔진으로 학술 논문 PDF를 구조화된 Markdown으로 변환
   - 수식, 표, 그림 캡션 보존

2. **Markdown 후처리 및 태깅** (`md_postprocessor.py`)
   - 섹션별 태깅 (Title, Abstract, Introduction, Methodology, Results, Discussion)
   - 논문 메타데이터 추출

3. **스타일 패턴 추출** (`style_extractor.py`)
   - Voice ratio (능동/수동태 비율) per section
   - Tense patterns (과거/현재 시제)
   - 학술 동사 빈도, 전환어구, 측정값 형식, 인용 스타일
   - 출력: `analysis.json` (스키마: `references/analysis_schema.json`)

## 추가 스크립트

| 스크립트 | 용도 |
|---------|------|
| `scripts/verify_templates.py` | Jinja2 템플릿 유효성 검증 |
| `scripts/paper_utils.py` | 공용 유틸리티 함수 |

## 참조 파일

| 파일 | 용도 |
|------|------|
| `references/analysis_schema.json` | style_extractor 출력 JSON 스키마 (190줄) |
| `references/linguistic_patterns.json` | 언어학적 패턴 설정 (동사, 전환어구 등) |

## Jinja2 템플릿 (assets/)

skill-generator 에이전트가 사용하는 12개 템플릿:

| 템플릿 | 생성 대상 |
|--------|----------|
| `agent_writer.md.j2` | 섹션별 에이전트 .md 파일 |
| `style_guide.md.j2` | 스타일 가이드 SKILL.md |
| `orchestrator.md.j2` | 오케스트레이터 커맨드 |
| `plugin_json.json.j2` | plugin.json 메타데이터 |
| `verify_agent.md.j2` | 검증 에이전트 |
| 기타 | 섹션별 참조 문서 템플릿 |
```

**목표 줄수**: ~120줄 (현재 47줄 → +73줄)
**버전**: paper-style-generator PATCH 버전 올림 (`1.4.0` → `1.4.1`)

---

### 항목 #5: core-resources SKILL.md 확장

**현재 상태**: 40줄. 31개 하위 파일이 존재하지만 SKILL.md에서 "무엇이 들어있는지" 설명 없음.

**파일**: `plugins/isd-generator/skills/core-resources/SKILL.md`

**추가할 내용 (스크립트 섹션 뒤에 추가):**

```markdown
## 리소스 구조

### references/writing_patterns/ — 문체 패턴
ISD 연구계획서 공통 문체 규칙을 정의합니다.

| 파일 | 내용 |
|------|------|
| `sentence_patterns.md` | 문장 구조 패턴 (주어-서술어 배치, 근거 제시 등) |
| `section_patterns.md` | 절(section) 구성 패턴 |
| `table_patterns.md` | 표 작성 패턴 |
| `vocabulary_glossary.md` | ISD 용어집 |
| `voc_template.md` | VOC(고객의 소리) 작성 템플릿 |

### references/guides/ — 작업 가이드
챕터별 웹 검색 전략, 캡션 패턴, 프롬프트 가이드를 포함합니다.

| 파일 | 내용 |
|------|------|
| `chapter1_web_search_guide.md` | Chapter 1 웹 검색 전략 |
| `chapter2_web_search_guide.md` | Chapter 2 시장/기술 동향 검색 전략 |
| `data_collection_guide.md` | 데이터 수집 품질 기준 |
| `verification_rules.md` | 검증문서 생성 규칙 |
| `image_reference_guide.md` | 이미지 참조 가이드 |
| `caption_patterns.md` | 캡션 작성 패턴 |
| `prompt_guide.md` | 이미지 프롬프트 가이드 |

### references/content_requirements/ — 챕터별 콘텐츠 요구사항
각 챕터에서 반드시 포함해야 할 항목을 정의합니다.

- `chapter1_requirements.md` ~ `chapter5_requirements.md`

### references/document_templates/ — 챕터별 출력 템플릿
최종 마크다운 출력 구조를 정의합니다.

- `chapter1_template.md` ~ `chapter5_template.md`

### assets/output_templates/ — 실행 보고서 템플릿
오케스트레이터와 에이전트가 사용하는 출력 스캐폴드입니다.

| 파일 | 용도 |
|------|------|
| `execution_report.md` | 오케스트레이터 실행 보고서 |
| `figure_generation_report.md` | 이미지 생성 보고서 |
| `prompt_template.md` | 이미지 프롬프트 템플릿 |
```

**목표 줄수**: ~100줄 (현재 40줄 → +60줄)
**버전**: isd-generator PATCH 버전 올림 (`1.0.1` → `1.0.2`)

---

### 항목 #6: verification-rules 내용 보강

**현재 상태**: 52줄. 규칙은 명확하지만 "왜 검증문서가 필요한지", "검증 프로세스 흐름"에 대한 설명이 없음.

**파일**: `plugins/isd-generator/skills/verification-rules/SKILL.md`

**추가할 내용 ("절대 스킵 금지" 섹션 위에 삽입):**

```markdown
## 왜 검증문서가 필요한가

ISD 연구계획서의 각 챕터는 웹 검색을 통해 수집한 데이터를 기반으로 작성됩니다. 검증문서 없이 본문을 먼저 작성하면:

1. **환각(hallucination) 위험**: 검색하지 않은 내용을 사실처럼 작성할 수 있음
2. **근거 추적 불가**: 본문의 주장이 어떤 출처에서 왔는지 확인할 수 없음
3. **수정 비용 증가**: 검증 단계 없이 작성된 본문은 전면 재작성이 필요

검증문서는 "수집한 데이터의 스냅샷"으로, 본문 작성의 입력(input)이 됩니다.

## 검증 프로세스 흐름

```
웹 검색 수행
    ↓
검증문서 생성 (수집 데이터 + 출처 기록)
    ↓
검증문서 기반 본문 작성
    ↓
본문 ↔ 검증문서 교차 확인
```
```

**목표 줄수**: ~85줄 (현재 52줄 → +33줄)
**버전**: isd-generator와 함께 PATCH (#5와 동일 버전)

---

## Wave 4: Progressive Disclosure 개선 (병렬 실행)

### 항목 #7: 500줄 초과 스킬 분할

**문제**: 13개 스킬이 500줄 초과. Agent Skills Spec 권장 위반.
**원칙**: SKILL.md는 인덱스+핵심 내용만 유지, 상세 내용은 references/로 분리

**우선순위에 따른 분할 대상:**

#### Tier A — 700줄+ (필수 분할)

| 스킬 | 현재 줄수 | 분할 방안 |
|------|:--------:|----------|
| `plugin-dev/command-development` | 834 | "Plugin-Specific Features" 섹션(~250줄)을 `references/plugin-features.md`로 이동. "Validation Patterns" 섹션(~150줄)을 `references/validation-patterns.md`로 이동. |
| `isd-generator/chapter2-guide` | 858 | 웹 검색 전략(~300줄)을 `references/web-search-strategy.md`로 이동. 템플릿 예시(~150줄)를 `references/chapter2-examples.md`로 이동. |
| `isd-generator/chapter1-guide` | 791 | 웹 검색 전략(~250줄)을 `references/web-search-strategy.md`로 이동. 템플릿 예시(~100줄)를 `references/chapter1-examples.md`로 이동. |
| `plugin-dev/hook-development` | 712 | "Advanced Patterns" 섹션(~200줄)을 기존 `references/advanced.md`와 통합. |

#### Tier B — 500~700줄 (권장 분할)

| 스킬 | 현재 줄수 | 분할 방안 |
|------|:--------:|----------|
| `plugin-dev/skill-development` | 637 | "Description Optimization" 섹션(~150줄)을 `references/description-optimization.md`로 이동. |
| `hwpx-generator/hwpx-core` | 630 | "단위 변환" 테이블(~40줄) + "스타일 ID 맵" 테이블(~60줄)을 `references/unit-style-tables.md`로 이동. |
| `isd-generator/chapter3-guide` | 588 | 리스크 관리 템플릿(~100줄)을 `references/risk-templates.md`로 이동. |
| `stock-consultation/stock-data-verifier` | 579 | Allowlist 테이블(~72줄)을 `references/allowlist.md`로 이동. 검색 프로토콜 스키마(~150줄)를 `references/search-protocols.md`로 이동. |
| `plugin-dev/mcp-integration` | 554 | "Authentication Patterns" 섹션(~100줄)을 기존 `references/authentication.md`와 통합. |
| `plugin-dev/plugin-settings` | 544 | "Real-World Examples" 섹션(~100줄)을 기존 `references/real-world-examples.md`와 통합. |
| `investments-portfolio/data-updater` | 532 | 스크립트 상세 설명(~80줄)을 `references/script-usage.md`로 이동. |
| `investments-portfolio/fund-selection-criteria` | 524 | "황금률" 섹션(~80줄)을 `references/golden-rules.md`로 이동. |
| `isd-generator/figure-guide` | 492 | 줄수가 500 미만이므로 분할 불필요. |

**분할 시 SKILL.md에 남길 내용:**
```markdown
## [분리된 섹션명]

상세 내용은 **references/[파일명].md**를 참조하세요.
```

**주의사항:**
- references/ 폴더가 없는 스킬은 새로 생성
- 기존 references/ 파일이 있으면 내용 통합 (덮어쓰기 금지)
- SKILL.md에서 분리된 내용을 참조하는 링크 추가

**버전**: 각 플러그인 MINOR 버전 올림 (구조 변경이므로)

---

### 항목 #8: theme-* 교차 참조 명시화

**문제**: 6개 theme 스킬(concept, gov, seminar, whatif, pitch, comparison)이 `scene-richness-spec.md`, `korean-typography-spec.md`, `validation-rules-map.md`를 참조하지만, 이 파일들은 `slide-renderer/references/`에만 존재. 교차 스킬 의존성이 명시적이지 않음.

**파일**: 6개 theme 스킬의 SKILL.md

**수정 방안 (택 1):**

#### Option A: 각 theme SKILL.md에 교차 참조 명시 (권장 — 간단)

각 theme SKILL.md 끝에 추가:

```markdown
## 공유 참조 문서

이 테마는 다음 공유 참조 문서를 사용합니다 (slide-renderer 스킬에 위치):

- **slide-renderer/references/scene-richness-spec.md**: 장면 복잡도 검증 규칙
- **slide-renderer/references/validation-rules-map.md**: 프롬프트 검증 체크리스트
- **slide-renderer/references/korean-typography-spec.md**: 한국어 텍스트 렌더링 가이드라인

참조 시 Glob 패턴: `**/visual-generator/skills/slide-renderer/references/*.md`
```

#### Option B: 공유 참조를 별도 스킬로 분리

`plugins/visual-generator/skills/shared-references/` 폴더를 새로 만들고 3개 파일을 이동. 하지만 slide-renderer도 이 파일들을 사용하므로 이중 관리 문제 발생.

**추천**: **Option A** (기존 구조 유지, 참조 경로만 명시)

**버전**: visual-generator PATCH 버전 올림 (Wave 1의 #2와 통합)

---

### 항목 #9: skill-development 리소스 보강

**현재 상태**: plugin-dev 7개 스킬 중 가장 빈약한 리소스 (참조 1개, 예제 0개, 스크립트 0개)

**파일**: `plugins/plugin-dev/skills/skill-development/`

**추가할 리소스:**

#### 1. `examples/good-skill-example.md` (신규)
양질의 SKILL.md 예시. 본 프로젝트의 `hwpx-templates/SKILL.md`를 모범 사례로 인용:
- 적절한 줄수 (249줄)
- "Use when..." 트리거 있음
- references/, scripts/ 분리
- 명확한 워크플로우

#### 2. `examples/common-mistakes.md` (신규)
흔한 실수 패턴과 수정 방법:
- Title Case name 사용 (이번 #1에서 발견한 바로 그 문제)
- "Use when..." 누락
- 500줄 초과 인라인
- references/ 없이 모든 내용 인라인

#### 3. `scripts/validate-skill.sh` (신규)
SKILL.md 자동 검증 스크립트:
- name 필드 소문자+하이픈 확인
- name과 디렉토리명 일치 확인
- description 1024자 이내 확인
- "Use when" 문구 존재 확인
- 줄수 500줄 초과 경고

**버전**: plugin-dev MINOR 버전 올림 (`0.1.1` → `0.2.0`, 리소스 추가이므로)
  - 항목 #1의 PATCH와 통합하여 `0.2.0`으로 한 번에 올림

---

## Wave 5: 버전 및 레지스트리 동기화 (순차 실행)

### 버전 업데이트 체크리스트

Wave 1~4 완료 후, 아래 파일들을 일괄 업데이트:

| 플러그인 | plugin.json | marketplace.json | 변경 유형 | 최종 버전 |
|----------|:-----------:|:----------------:|:---------:|:---------:|
| plugin-dev | `0.1.0` → `0.2.0` | 동기화 | MINOR (#1 name수정 + #9 리소스추가) | `0.2.0` |
| visual-generator | `2.1.0` → `2.1.1` | 동기화 | PATCH (#2 트리거 + #8 교차참조) | `2.1.1` |
| isd-generator | `1.0.1` → `1.1.0` | 동기화 | MINOR (#3 트리거 + #5 확장 + #6 보강 + #7 분할) | `1.1.0` |
| investments-portfolio | `1.0.1` → `1.1.0` | 동기화 | MINOR (#3 트리거 + #7 분할) | `1.1.0` |
| stock-consultation | 없음 → 추가 | 동기화 | MINOR (#3 트리거 + #7 분할) | `1.1.0` |
| report-generator | 없음 → 추가 | 동기화 | PATCH (#3 트리거) | `1.0.1` |
| paper-style-generator | `1.4.0` → `1.4.1` | 동기화 | PATCH (#4 확장) | `1.4.1` |
| hwpx-generator | `2.3.0` → `2.4.0` | 동기화 | MINOR (#7 분할) | `2.4.0` |

### AGENTS.md 최신화

변경 사항 반영:
- `Generated` 날짜 업데이트
- `Version` 업데이트
- 필요 시 `WHERE TO LOOK` 테이블에 새 references/ 파일 추가

### 캐시 클리어

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\plugins\cache" -ErrorAction SilentlyContinue
```

---

## 실행 지침 (다음 세션용)

### 병렬화 전략

```
Wave 1: 항목 #1, #2 → 2개 task 병렬 (quick 카테고리)
Wave 2: 항목 #3 → 플러그인별 4~5개 task 병렬 (quick 카테고리)
Wave 3: 항목 #4, #5, #6 → 3개 task 병렬 (quick 카테고리)
Wave 4: 항목 #7, #8, #9 → 3개 task 병렬 (unspecified-low 카테고리)
Wave 5: 버전 동기화 → 순차 실행 (직접 처리)
```

### 검증 방법

각 Wave 완료 후:
1. 수정된 모든 SKILL.md에 `lsp_diagnostics` 실행 (YAML 파싱 오류 확인)
2. frontmatter `name` ↔ 디렉토리명 일치 확인
3. description 내 "Use when" 존재 확인
4. 줄수 확인 (500줄 이하)
5. plugin.json ↔ marketplace.json 버전 일치 확인

### 롤백 기준

- YAML 파싱 오류 발생 → 해당 파일만 되돌리기
- 스킬 매칭 실패 보고 → frontmatter 원복 후 재수정

---

## 부록: 수정하지 않는 항목 (참고)

평가에서 발견되었으나 이번 계획에 포함하지 않는 사항:

| 항목 | 이유 |
|------|------|
| plugin-dev description 길이 (>1024자 가능성) | 기능에 직접 영향 없음, 트리거 품질 우수 |
| theme-* 스킬 내용 보강 | 현재 91~129줄로 적절, 콘텐츠 품질 양호 |
| analyst-common Allowlist 분리 | 246줄로 500줄 미만, 긴급하지 않음 |
| chapter-structure 템플릿 분리 | 294줄로 500줄 미만, 긴급하지 않음 |
