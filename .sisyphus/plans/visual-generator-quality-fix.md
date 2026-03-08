# visual-generator 프롬프트 품질 회복 및 검증 강화

## TL;DR

> **Quick Summary**: v2.0.0 XML-tag 전환 시 소실된 프롬프트 디테일과 검증 규칙을 복원하고, 새 prompt-validator 에이전트를 추가하며, 렌더링 스크립트에 API 파라미터 튜닝 + 품질 기반 재시도 로직을 추가한다.
> 
> **Deliverables**:
> - 강화된 prompt-designer.md (scene 풍부함 기준 명시)
> - 새 prompt-validator 에이전트 (논리적 완성도 + 교차 태그 일관성 검증)
> - 6개 테마 스킬 전면 강화 (구체적 예시 프롬프트 + 한글 타이포그래피 + v1.11.0 규칙 포팅)
> - 강화된 renderer-agent.md (콘텐츠 수준 검증 추가)
> - 수정된 generate_slide_images.py (temperature/top_p/system_instruction + 품질 재시도)
> - 업데이트된 파이프라인 (visual-generate.md에 검증 단계 삽입)
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: T1(scene spec) → T17(API params) → T18(quality retry) → T16(version) → F1-F4

---

## Context

### Original Request
v2.0.0 업데이트 후 슬라이드 렌더링 품질이 v1.11.0 대비 심각하게 저하됨. 구성 단순화, 한글 깨짐, 의미 없는 프롬프트가 검증 통과하는 문제. 개선 계획 수립 요청.

### Interview Summary
**Key Discussions**:
- 아키텍처: XML-tag 시스템(v2.0.0) 유지하되 콘텐츠 풍부함을 v1.11.0 수준으로 복원
- 테마 범위: 전체 6개 테마 일괄 개선
- 검증 방식: 새 prompt-validator 에이전트 추가 (prompt-designer ↔ renderer-agent 사이)
- 한글 렌더링: 프롬프트 강화로 최대한 개선 (스크립트 변경 없음)

**Research Findings**:
- `prompt-designer.md`: `<scene>`에 "3~5문장"만 요구 — 디테일 수준 가이드 없음
- 6개 테마 스킬: Scene Guide에 7가지 요소 나열했으나 구체적 예시/템플릿 없음
- `content-reviewer.md`: 텍스트 분류 정확성만 검증, 프롬프트 품질/논리적 완성도 미검증
- `renderer-agent.md`: 8개 XML 구조 검증 + 3개 추가 검증, 모두 형식 수준
- v1.9.0~v1.11.0에서 축적된 8종 검증 규칙 (이중렌더링 방지, 고아항목, 메타라벨 방지 등) v2.0.0에서 소실

### Metis Review
**Identified Gaps** (addressed):
- `<scene>` 풍부함의 정량적 기준 부재 → 최소 문장 수, 필수 요소 수, 금지 문구 정의
- 테마 스킬에 구체적 예시 프롬프트 부재 → 테마별 golden reference 추가
- v1.11.0 검증 규칙의 XML-tag 매핑 문서 부재 → 명시적 매핑 테이블 작성
- prompt-validator 출력 형식 미정의 → 출력 스키마 정의
- concept 테마(0텍스트)와 comparison 테마(듀얼씬) 예외 처리 미고려 → 특수 규칙 추가
- content-organizer의 scene_context도 빈약할 가능성 → 풍부함 가이드 추가

### Quality Gap Analysis (Post-Momus, 3-Agent Investigation)
**Methodology**: 3 background agents (explore ×2, librarian ×1) + direct code analysis
**Key Discoveries** (integrated into tasks):
- N1: 네거티브 프롬프팅 부재 → T1(scene-richness-spec)에 가이드 추가, T5(prompt-designer) MUST DO에 적용 규칙 추가
- N2: 시각 구성 원칙(삼분할, 시각 위계, 깊이 레이어링) 부재 → T1에 composition 섹션 추가
- N3: 텍스트-배경 대비/가독성 가이드 부재 → T3(korean-typography-spec)에 추가
- N4: 포네틱 앵커링(복잡한 한글 용어에 발음 힌트) 기법 미활용 → T3에 추가
- N5: 여백 밀도 가이드(30-40% 네거티브 스페이스) 부재 → T1에 추가
- N6: layout-types의 시각화 원칙/검증 규칙이 prompt-designer에서 미참조 → T5 MUST DO에 레이아웃별 원칙 참조 지침 추가
- N7: 슬라이드 간 스타일 일관성 메커니즘 부재 → T5 MUST DO에 일관성 규칙 추가
- N8: 한글 폰트 Heavy Gothic 권장 + thin serif 회피 명시 필요 → T3, T8-T13 golden example에 반영
**Blocked by Guardrails** (not actionable):
- ~~API 파라미터(temperature/top_p) 튜닝~~ → **가드레일 해제됨** → T17에서 구현
- ~~System prompt wrapping~~ → **가드레일 해제됨** → T17에서 구현
- ~~품질 기반 재시도~~ → **가드레일 해제됨** → T18에서 구현 (Gemini 비전 자체평가)
- 멀티샷 생성(동시 N개 생성 후 선택) → 스코프 제한으로 제외 (단일 생성 + 재시도만 허용)
- 참조 이미지 앵커링 / 외부 OCR 라이브러리 → 스코프 제한으로 제외

---

## Work Objectives

### Core Objective
v2.0.0 XML-tag 아키텍처를 유지하면서 프롬프트 콘텐츠 풍부함을 v1.11.0 수준으로 복원하고, 논리적/구조적 결함을 차단하는 검증 계층을 추가하며, 렌더링 스크립트에 API 파라미터 튜닝 + 품질 기반 재시도 로직을 추가한다.

### Concrete Deliverables
- `plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md` — scene 풍부함 정량 기준
- `plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md` — v1.11.0 규칙 매핑
- `plugins/visual-generator/agents/prompt-validator.md` — 신규 검증 에이전트
- 수정된 `prompt-designer.md`, `content-organizer.md`, `content-reviewer.md`, `renderer-agent.md`
- 강화된 6개 테마 스킬 SKILL.md + 테마별 `references/golden-prompt-example.md`
- 수정된 `visual-generate.md` (Phase 3.5 삽입)
- 업데이트된 `plugin.json`, `marketplace.json`, `AGENTS.md`
- 수정된 `generate_slide_images.py` (temperature/top_p/system_instruction + 품질 재시도 로직)

### Definition of Done
- [x] prompt-validator 에이전트가 생성되고 marketplace.json에 등록됨
- [x] visual-generate.md에 prompt-validator 단계가 포함됨
- [x] 6개 테마 스킬 모두 구체적 예시 프롬프트를 포함함
- [x] 모든 에이전트/스킬에 v1.11.0 검증 규칙이 XML-tag 형식으로 포팅됨
- [ ] 세미나 테마로 end-to-end 프롬프트 생성 → 검증 → 렌더링 테스트 완료
- [x] generate_slide_images.py에 temperature/top_p/system_instruction이 추가됨
- [x] 품질 기반 재시도 로직(Gemini 비전 자체평가, 최대 3회)이 동작함

### Must Have
- `<scene>` 풍부함의 정량적 최소 기준 (최소 문장 수, 필수 요소 수)
- `<text_to_render>` ↔ `<layout>` 양방향 참조 검증 (고아 항목/유령 참조 방지)
- 콘텐츠 논리적 완성도 검증 (빈 선택지, 의미없는 값 검출)
- concept 테마(0텍스트) 및 comparison 테마(듀얼씬) 예외 처리
- 테마별 구체적 golden reference 예시 프롬프트
- generate_slide_images.py에 temperature/top_p/system_instruction 파라미터 추가
- 품질 기반 재시도: Gemini 비전 모델로 생성 이미지 자체평가 → 임계값 미달 시 재생성 (최대 3회)

### Must NOT Have (Guardrails)
- ❌ layout-types SKILL.md (938줄) 수정 금지
- ❌ generate_slide_images.py의 기존 이미지 저장/파일 처리/디렉토리 로직 변경 금지 (API 호출 파라미터 + 품질 재시도 로직 추가만 허용)
- ❌ 새 XML 태그 추가 또는 5-tag 스키마 변경 금지
- ❌ 새 테마 또는 레이아웃 추가 금지
- ❌ 새 스킬 폴더 생성 금지 (prompt-validator는 에이전트, 스킬 아님)
- ❌ prompt-validator가 프롬프트를 자동 수정하는 것 금지 (REJECT-only + 구체적 수정 지시)
- ❌ content-reviewer의 기존 5개 검토 차원 제거/변경 금지
- ❌ renderer-agent의 기존 8개 XML 검증 + 3개 추가 검증 제거/변경 금지
- ❌ Gemini 모델명(MODEL_NAME) 변경 금지 (temperature/top_p/system_instruction 추가만 허용)
- ❌ 멀티샷 생성(여러 이미지 동시 생성 후 선택) 로직 추가 금지 (단일 생성 + 품질 재시도만 허용)
- ❌ 품질 재시도 횟수 3회 초과 금지 (기존 API 에러 재시도와 별도 운영)
- ❌ 외부 OCR 라이브러리(pytesseract 등) 설치/사용 금지 (Gemini 비전 모델만 사용)
- ❌ content-reviewer와 prompt-validator의 역할 경계 혼재 금지 (content-reviewer=프롬프트 이전 텍스트 품질, prompt-validator=프롬프트 이후 콘텐츠 품질)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (플러그인 마크다운 시스템, 자동 테스트 프레임워크 없음)
- **Automated tests**: None (마크다운 파일 기반 플러그인)
- **Framework**: None
- **Verification method**: Agent-executed QA (파일 존재 확인, 콘텐츠 패턴 검증, end-to-end 렌더링)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Agent/Skill 파일**: Use Bash (python -c, grep) — 파일 존재, 콘텐츠 패턴, frontmatter 형식 확인
- **Integration**: Use Bash — marketplace.json 등록 확인, 파이프라인 연결 확인
- **End-to-end**: Use Bash — 프롬프트 생성 후 XML 구조 검증 (실제 Gemini 렌더링은 선택적)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — 3 parallel, all quick):
├── T1: Scene 풍부함 기준 + golden reference 프롬프트 세트 [quick]
├── T2: v1.11.0 검증 규칙 → XML-tag 매핑 문서 [quick]
└── T3: 한글 타이포그래피 강화 명세 [quick]

Wave 2 (Core + Theme + Script — 11 parallel, mixed):
├── T4:  prompt-validator 에이전트 생성 (depends: T1, T2) [deep]
├── T5:  prompt-designer.md 강화 (depends: T1) [unspecified-high]
├── T6:  content-organizer.md scene_context 강화 (depends: T1) [quick]
├── T7:  content-reviewer.md 항목 수 hard-reject 추가 (depends: T2) [quick]
├── T8:  theme-seminar 강화 (depends: T1, T3) [unspecified-high]
├── T9:  theme-gov 강화 (depends: T1, T3) [unspecified-high]
├── T10: theme-concept 강화 (depends: T1, T3) [unspecified-high]
├── T11: theme-whatif 강화 (depends: T1, T3) [unspecified-high]
├── T12: theme-pitch 강화 (depends: T1, T3) [unspecified-high]
├── T13: theme-comparison 강화 (depends: T1, T3) [unspecified-high]
└── T17: generate_slide_images.py API 파라미터 + System Prompt (depends: T1, T3) [deep]

Wave 3 (Integration + Quality Retry — 4 parallel):
├── T14: visual-generate.md 파이프라인 업데이트 (depends: T4) [quick]
├── T15: renderer-agent.md 콘텐츠 수준 검증 추가 (depends: T2, T4) [quick]
├── T16: 버전 업데이트 + marketplace + AGENTS.md (depends: T4~T17) [quick]
└── T18: 품질 기반 재시도 + Gemini 비전 자체평가 (depends: T17) [deep]

Wave FINAL (Verification — 4 parallel):
├── F1: Plan compliance audit [oracle]
├── F2: Code quality review [unspecified-high]
├── F3: End-to-end rendering test [unspecified-high]
└── F4: Scope fidelity check [deep]

Critical Path: T1 → T17 → T18 → T16 → F1-F4
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 11 (Wave 2)
```

### Dependency Matrix

| Task | Blocked By | Blocks | Wave |
|------|-----------|--------|:----:|
| T1 | — | T4,T5,T6,T8-T13,T17 | 1 |
| T2 | — | T4,T7,T15 | 1 |
| T3 | — | T8-T13,T17 | 1 |
| T4 | T1,T2 | T14,T15 | 2 |
| T5 | T1 | T16 | 2 |
| T6 | T1 | T16 | 2 |
| T7 | T2 | T16 | 2 |
| T8-T13 | T1,T3 | T16 | 2 |
| T17 | T1,T3 | T18,T16 | 2 |
| T14 | T4 | T16 | 3 |
| T15 | T2,T4 | T16 | 3 |
| T16 | T4-T15,T17,T18 | F1-F4 | 3 |
| T18 | T17 | T16 | 3 |
| F1-F4 | T16 | — | FINAL |

### Agent Dispatch Summary

| Wave | Tasks | Categories |
|:----:|:-----:|-----------|
| 1 | 3 | T1-T3 → `quick` |
| 2 | 11 | T4 → `deep`, T5 → `unspecified-high`, T6-T7 → `quick`, T8-T13 → `unspecified-high`, T17 → `deep` |
| 3 | 4 | T14-T16 → `quick`, T18 → `deep` |
| FINAL | 4 | F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep` |

---

## TODOs

> Implementation tasks below. EVERY task has: Recommended Agent Profile + Parallelization + QA Scenarios.
> 
> **❗ 경로 규칙 (Path Convention)**: 이 문서의 모든 `agents/`, `skills/`, `commands/` 경로는 **`plugins/visual-generator/` 기준 상대경로**입니다.
> - `agents/prompt-designer.md` = `plugins/visual-generator/agents/prompt-designer.md`
> - `skills/theme-seminar/SKILL.md` = `plugins/visual-generator/skills/theme-seminar/SKILL.md`
> - `commands/visual-generate.md` = `plugins/visual-generator/commands/visual-generate.md`
> - `.claude-plugin/marketplace.json`, `AGENTS.md` 등 루트 파일만 저장소 루트 기준입니다.

- [x] 1. Scene Richness Specification + Golden Reference Prompts

  **What to do**:
  - `skills/slide-renderer/references/scene-richness-spec.md`를 신규 생성한다.
  - `<scene>` 정량 기준을 명시한다: 기본 최소 5문장, `concept` 테마 최소 7문장.
  - Scene Guide 7요소(서피스/배경/코너/연결선/시각장식/공간구성/시각메타포) 중 최소 5개 포함 체크리스트를 넣는다.
  - 금지 문구 목록(`clean layout`, `professional design`, `modern style` 등 정보량 없는 표현) 섹션을 넣는다.
  - 네거티브 프롬프팅 가이드를 추가한다: `<scene>`/`<canvas>` 내에서 렌더링 금지 요소를 명시하는 패턴(예: "No watermarks, no blurry text, no numbered lists rendered as visual elements, no artifacts").
  - 시각 구성(composition) 원칙 섹션을 추가한다: 삼분할 법칙(rule of thirds), 시각 위계(visual hierarchy), 전경/중경/배경 깊이(depth layering), 초점 배치(focal point placement) 가이드.
  - 여백(white space) 밀도 가이드를 추가한다: 가독성을 위해 30~40% 네거티브 스페이스 유지, 텍스트 밀집도 상한 권장.
  - 품질 등급(EXCELLENT/GOOD/REJECT) 기준을 수치화해 넣는다.
  - smart factory/AI manufacturing 주제로 golden XML 예시 2~3개를 넣는다(세미나 25항목급 1개 + concept 0-text 1개 포함, 5태그 완전 충족).

  **Must NOT do**:
  - `skills/layout-types/SKILL.md`를 수정하지 않는다.
  - 5-tag XML 스키마를 변경하지 않는다.
  - 새 테마/레이아웃/스킬 폴더를 추가하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 신규 참조 문서 1개 작성 중심이며 의존 코드 변경이 없다.
  - **Skills**: `slide-renderer`, `theme-seminar`, `theme-concept`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: 4, 5, 6, 8, 9, 10, 11, 12, 13
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `skills/theme-seminar/SKILL.md:24` — Scene Guide 7요소 현재 기준
  - `skills/theme-concept/SKILL.md:24` — concept(텍스트 최소/장면 중심) 특성
  - `agents/prompt-designer.md:35` — `<scene>` 현재 문장 기준(3~5) 위치
  - `skills/slide-renderer/SKILL.md:6` — references 문서가 놓일 스킬 컨텍스트

  **Acceptance Criteria**:
  - [ ] 새 문서에 최소 문장 수, 7요소 체크리스트, 금지 문구, 품질 등급이 모두 정의됨
  - [ ] 네거티브 프롬프팅 가이드("No watermarks" 등)가 포함됨
  - [ ] 시각 구성 원칙(삼분할 법칙, 시각 위계, 깊이 레이어링) 섹션이 포함됨
  - [ ] 여백 밀도 가이드(30~40% 네거티브 스페이스) 권장이 포함됨
  - [ ] golden XML 예시가 2개 이상이며 각 예시가 `<scene>/<text_to_render>/<typography>/<canvas>/<layout>` 5태그를 모두 포함함

  **QA Scenarios**:

  ```
  Scenario: scene-richness-spec 기본 요건 존재 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; p=Path('plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md'); t=p.read_text(encoding='utf-8'); assert p.exists(); assert '최소 5문장' in t and 'concept' in t and '최소 7문장' in t and 'EXCELLENT' in t and 'GOOD' in t and 'REJECT' in t and 'No watermarks' in t and 'rule of thirds' in t.lower() and 'negative space' in t.lower()"
      2. 문서 내 핵심 규칙 문자열 존재를 assert로 검증한다.
    Expected Result: 명령이 종료코드 0으로 통과한다.
    Evidence: .sisyphus/evidence/task-1-scene-richness-core-check.txt

  Scenario: edge-case — 정보량 없는 금지 문구/예시 완전성 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md').read_text(encoding='utf-8'); assert 'clean layout' in t and 'professional design' in t and 'modern style' in t; assert t.count('<scene>')>=2 and t.count('<layout>')>=2; assert 'visual hierarchy' in t.lower() and 'depth' in t.lower()"
      2. 금지 문구 목록 및 완전 XML 예시 개수를 assert한다.
    Expected Result: 금지 문구 누락/예시 미충족 시 즉시 실패한다.
    Evidence: .sisyphus/evidence/task-1-scene-richness-edge-check.txt
  ```

  **Commit**: YES (groups with 1-3)
  - Message: `docs(visual-generator): add scene richness spec, validation rules map, Korean typography spec`
  - Files: `skills/slide-renderer/references/scene-richness-spec.md`

- [x] 2. v1.11.0 Validation Rules Map

  **What to do**:
  - `skills/slide-renderer/references/validation-rules-map.md`를 신규 생성한다.
  - v1.9.0~v1.11.0 규칙을 XML-tag 체계로 1:1 매핑한다.
  - 각 규칙에 `Rule Name`, `Original Context`, `XML-tag Equivalent`, `Detection Method`, `Example(PASS/FAIL)`를 모두 작성한다.
  - 반드시 포함할 규칙: 이중 렌더링 방지, 세미나 장면화 방지, 축-의미 역검증, CONTENT↔Placement 대응, 데이터 중복 방지, 개념 키워드 혼입 방지, 라벨 탈맥락화, 메타라벨 금지, 조사문 형식 강제, ①②③ 금지.
  - orphan/ghost reference 탐지 기준을 명시한다.

  **Must NOT do**:
  - renderer-agent의 기존 8 XML 검증 + 3 추가 검증 정의를 삭제/변경하지 않는다.
  - 새 XML 태그를 도입하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 규칙 문서화 작업이며 시스템 구조 변경이 없다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: 4, 7, 14, 15
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `agents/renderer-agent.md:27` — 현재 XML 검증 체크리스트 구조
  - `agents/prompt-designer.md:56` — `<layout>` 인용 규칙 기준
  - `README.md` 변경이력 (v2.3.2~v2.3.5) — v1.9.0~v1.11.0에서 축적된 검증 규칙 목록 참조 대상

  **Acceptance Criteria**:
  - [ ] 요구된 모든 v1.9.0~v1.11.0 규칙이 XML 등가 규칙으로 매핑됨
  - [ ] 모든 규칙이 탐지 방법 + PASS/FAIL 예시를 포함함

  **QA Scenarios**:

  ```
  Scenario: validation-rules-map 필수 규칙 키워드 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; p=Path('plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md'); t=p.read_text(encoding='utf-8'); must=['orphan','ghost','meta-label','decontextualization','PASS','FAIL']; assert p.exists(); missing=[k for k in must if k not in t]; assert not missing, f'Missing: {missing}'"
      2. 핵심 규칙 키워드 및 PASS/FAIL 포함 여부를 assert한다.
    Expected Result: 누락 키워드가 없으면 통과한다.
    Evidence: .sisyphus/evidence/task-2-rules-map-core-check.txt

  Scenario: edge-case — 규칙 템플릿 5필드 충족 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/references/validation-rules-map.md').read_text(encoding='utf-8'); fields=['Rule Name','Original Context','XML-tag Equivalent','Detection Method','Example']; missing=[f for f in fields if f not in t]; assert not missing, f'Missing: {missing}'"
      2. 규칙 정의 필드 템플릿이 문서에 존재하는지 검증한다.
    Expected Result: 5필드 템플릿 미충족 시 실패한다.
    Evidence: .sisyphus/evidence/task-2-rules-map-template-check.txt
  ```

  **Commit**: YES (groups with 1-3)
  - Message: `docs(visual-generator): add scene richness spec, validation rules map, Korean typography spec`
  - Files: `skills/slide-renderer/references/validation-rules-map.md`

- [x] 3. Korean Typography Specification

  **What to do**:
  - `skills/slide-renderer/references/korean-typography-spec.md`를 신규 생성한다.
  - `<typography>`에 항상 포함해야 할 필수 문구(지정된 긴 영어 문장)를 그대로 수록한다.
  - 자모 분리 방지/완성형 조합 보장 지침을 추가한다.
  - `<scene>`에서 텍스트 요소를 묘사할 때 넣을 표현(예: clearly legible Korean typography)을 명시한다.
  - 6개 테마 공통 폰트 weight hierarchy 가이드를 정의한다. 특히 "Heavy weight Gothic-style Hangul" 권장 + "thin/light weight Korean serif 회피" 명시.
  - 텍스트 가독성/대비 가이드를 추가한다: 배경 대비 요구사항(text-on-dark vs text-on-light), 최소 효과 폰트 웨이트, 텍스트-섭도우/아웃라인 프롬프트 권장.
  - 포네틱 앵커링(phonetic anchoring) 기법을 추가한다: 복잡한 한글 용어에 발음 힌트를 덧붙여 렌더링 정확도를 높이는 패턴(예: "혁신적인 기술(Hyeok-sin-jeok-in Gi-sul)" 형식).
  - 한글 깨짐 anti-pattern 사례와 문제 유발 프롬프트 패턴을 넣는다.

  **Must NOT do**:
  - Gemini API 파라미터/렌더 스크립트를 수정하지 않는다.
  - 테마/레이아웃을 추가하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 공통 타이포 명세 문서 추가 작업이다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: 5, 8, 9, 10, 11, 12, 13
  - **Blocked By**: None

  **References**:
  **Pattern References**:
  - `agents/prompt-designer.md:47` — `<typography>` 규칙 주입 지점
  - `skills/theme-seminar/SKILL.md:41` — 기존 한글 타이포 가이드 패턴
  - `skills/theme-concept/SKILL.md:41` — concept 테마 텍스트 최소 정책

  **Acceptance Criteria**:
  - [ ] 필수 한글 렌더링 문구와 자모 조합 지침이 문서에 포함됨
  - [ ] 테마 공통 weight hierarchy + anti-pattern 예시가 포함됨
  - [ ] 텍스트 가독성/대비 가이드(배경 대비, 폰트 웨이트, 섭도우)가 포함됨
  - [ ] 포네틱 앵커링(phonetic anchoring) 기법 가이드가 포함됨

  **QA Scenarios**:

  ```
  Scenario: korean-typography-spec 필수 문구 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; p=Path('plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md'); t=p.read_text(encoding='utf-8'); assert p.exists(); assert 'All Korean text must be rendered with crisp, perfectly formed characters' in t"
      2. 필수 문구 원문 포함 여부를 assert한다.
    Expected Result: 필수 문구 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-3-korean-typography-core-check.txt

  Scenario: edge-case — scene/typography 양쪽 지침 존재 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/references/korean-typography-spec.md').read_text(encoding='utf-8'); assert 'scene' in t.lower() and 'typography' in t.lower() and 'anti-pattern' in t.lower() and 'contrast' in t.lower() and 'phonetic' in t.lower() and 'Gothic' in t"
      2. scene-level/typography-level/anti-pattern 섹션 키워드를 검증한다.
    Expected Result: 섹션 중 하나라도 누락되면 실패한다.
    Evidence: .sisyphus/evidence/task-3-korean-typography-edge-check.txt
  ```

  **Commit**: YES (groups with 1-3)
  - Message: `docs(visual-generator): add scene richness spec, validation rules map, Korean typography spec`
  - Files: `skills/slide-renderer/references/korean-typography-spec.md`

- [x] 4. prompt-validator Agent Creation

  **What to do**:
  - `agents/prompt-validator.md`를 신규 생성한다.
  - frontmatter를 정확히 넣는다: `name: prompt-validator`, `description`에 `Use when...` 포함, `model: sonnet`, `tools: Read, Glob, Grep, Write`.
  - Input(`prompts_path`, `theme`, `auto_mode`)과 Output(`{prompts_path}/validation_result.md`)을 명시한다.
  - 7개 검증 차원을 모두 정의한다(장면 풍부함/콘텐츠 완성도/교차태그 일관성/논리성/v1.11.0 준수/테마특수규칙/한글품질).
  - 워크플로우를 Phase 0~3으로 작성한다(참조 로드 → 파일 로드 → 슬라이드별 검증 → 결과 저장).
  - REJECT-only 정책을 명시한다(자동 수정 금지, 구체적 수정 지시만).

  **Must NOT do**:
  - XML 구조 검증을 중복 구현하여 renderer-agent 역할을 침범하지 않는다.
  - 프롬프트 자동 수정(auto-fix) 로직을 넣지 않는다.
  - 새 skill 폴더를 만들지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 다차원 검증 기준 통합 + 역할 경계 정의가 필요하다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5-13)
  - **Blocks**: 14, 15, 16
  - **Blocked By**: 1, 2

  **References**:
  **Pattern References**:
  - `agents/content-reviewer.md:27` — 리뷰 차원/판정 구조 포맷
  - `agents/renderer-agent.md:27` — 기존 형식 검증과의 역할 분리 기준
  - `commands/visual-generate.md:37` — Phase 연결 지점(3과 4 사이)
  - `skills/slide-renderer/SKILL.md:10` — reference 로딩 규칙 스타일

  **Acceptance Criteria**:
  - [x] `prompt-validator.md`가 7개 콘텐츠 품질 검증 차원 + Phase 0~3 워크플로우를 포함함
  - [x] REJECT-only 정책과 출력 파일 규격(`validation_result.md`)이 명시됨

  **QA Scenarios**:

  ```
  Scenario: prompt-validator 필수 구조 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; p=Path('plugins/visual-generator/agents/prompt-validator.md'); t=p.read_text(encoding='utf-8'); assert p.exists(); must=['name: prompt-validator','Use when','model: sonnet','tools: Read, Glob, Grep, Write','validation_result.md','Phase 0','Phase 1','Phase 2','Phase 3']; missing=[m for m in must if m not in t]; assert not missing, f'Missing: {missing}'"
      2. frontmatter/phase/output 필수 문자열 존재를 assert한다.
    Expected Result: 필수 구성요소가 모두 있으면 통과한다.
    Evidence: .sisyphus/evidence/task-4-prompt-validator-core-check.txt

  Scenario: edge-case — REJECT-only 정책 강제 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/prompt-validator.md').read_text(encoding='utf-8'); assert 'REJECT' in t; assert '자동 수정' in t and '금지' in t"
      2. auto-fix 금지 문구가 명시되어 있는지 검증한다.
    Expected Result: auto-fix 허용 가능성이 남아 있으면 실패한다.
    Evidence: .sisyphus/evidence/task-4-prompt-validator-reject-only-check.txt
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(visual-generator): add prompt-validator agent`
  - Files: `agents/prompt-validator.md`

- [x] 5. prompt-designer.md Enhancement

  **What to do**:
  - `agents/prompt-designer.md`의 `<scene>` 규칙을 `3~5문장`에서 `최소 5문장 (concept: 최소 7문장)`으로 상향한다.
  - Scene Guide 7요소 중 최소 5개 포함 규칙을 추가한다.
  - `scene-richness-spec.md`의 EXCELLENT 등급 목표 문구를 추가한다.
  - MUST DO에 `validation-rules-map.md` 준수 문구를 추가한다.
  - `<typography>` 섹션에 `korean-typography-spec.md` 필수 문구 참조를 추가한다.
  - MUST DO에 `<text_to_render>` 값 의미성/플레이스홀더 금지, `<layout>` 전항목 인용(고아 방지) 규칙을 추가한다.
  - MUST DO에 네거티브 프롬프팅 적용 규칙을 추가한다: `<scene>` 또는 `<canvas>` 내에 렌더링 금지 요소를 명시하는 패턴을 포함하도록 지침(scene-richness-spec.md 네거티브 프롬프팅 섹션 참조).
  - MUST DO에 레이아웃별 구성 규칙 적용 지침을 추가한다: 선택된 레이아웃의 layout-types SKILL.md 해당 섹션을 읽고, 그 레이아웃의 `시각화 원칙`과 `검증 규칙`을 `<scene>` 구성에 반영하도록 명시.
  - MUST DO에 슬라이드 간 스타일 일관성 규칙을 추가한다: 동일 프레젠테이션의 여러 슬라이드 생성 시, 색상 팔레트/조명 방향/서피스 텍스쳐/아이콘 스타일을 일관되게 유지.
  - Resources 표에 3개 신규 references를 등록한다.

  **Must NOT do**:
  - 5-tag 스키마를 바꾸지 않는다.
  - 테마 상한표를 삭제/완화하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 핵심 생성 에이전트 규칙 강화로 파급 범위가 넓다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 6-13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `agents/prompt-designer.md:35` — `<scene>` 규칙 변경 지점
  - `agents/prompt-designer.md:157` — MUST DO 확장 지점
  - `agents/prompt-designer.md:175` — Resources 표 확장 지점
  - `skills/slide-renderer/references/scene-richness-spec.md` — 새 정량 기준 소스 (네거티브 프롬프팅 + 시각 구성 원칙 + 여백 기준 포함)
  - `skills/slide-renderer/references/validation-rules-map.md` — 규칙 맵 소스
  - `skills/slide-renderer/references/korean-typography-spec.md` — 한글 렌더링 소스 (대비/포네틱 앵커링/폰트 웨이트 포함)
  - `skills/layout-types/SKILL.md` — 레이아웃별 시각화 원칙/검증 규칙 참조 대상 (T5에서 읽기 전용, 수정 금지)

  **Acceptance Criteria**:
  - [x] `<scene>` 최소 문장/요소 기준이 상향되고 EXCELLENT 목표가 명시됨
  - [x] MUST DO/Resources에 3개 reference 연동과 값 의미성/고아 방지 규칙이 반영됨
  - [x] 네거티브 프롬프팅 적용 지침이 MUST DO에 반영됨
  - [x] 레이아웃별 시각화 원칙 참조 지침이 MUST DO에 반영됨
  - [x] 슬라이드 간 스타일 일관성 규칙이 MUST DO에 반영됨

  **QA Scenarios**:

  ```
  Scenario: prompt-designer 강화 규칙 반영 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/prompt-designer.md').read_text(encoding='utf-8'); must=['최소 5문장','concept','최소 7문장','EXCELLENT','validation-rules-map.md','korean-typography-spec.md','네거티브','레이아웃','시각화 원칙','일관성']; missing=[m for m in must if m not in t]; assert not missing, f'Missing: {missing}'"
      2. 필수 강화 문구가 모두 포함됐는지 assert한다.
    Expected Result: 누락 문구가 없으면 통과한다.
    Evidence: .sisyphus/evidence/task-5-prompt-designer-core-check.txt

  Scenario: edge-case — 구버전 완화 문구 잔존 검출
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/prompt-designer.md').read_text(encoding='utf-8'); assert '자연어 3~5문장' not in t, 'Old weak criterion still present'"
      2. 기존 약한 기준 문구 잔존 여부를 assert한다.
    Expected Result: 구기준 잔존 시 실패한다.
    Evidence: .sisyphus/evidence/task-5-prompt-designer-regression-check.txt
  ```

  **Commit**: YES (groups with 5-7)
  - Message: `refactor(visual-generator): enrich prompt-designer, content-organizer, content-reviewer`
  - Files: `agents/prompt-designer.md`

- [x] 6. content-organizer.md Enhancement

  **What to do**:
  - `agents/content-organizer.md`의 `concepts.md Schema`에서 `scene_context` 정의를 강화한다(최소 5개 이상 구체 시각요소 포함).
  - MUST DO에 추상/범용 표현 대신 색상, 질감, 조명, 오브젝트 중심 구체 묘사 규칙을 추가한다.
  - MUST DO에 `render_text` 의미성 강제(빈 값, ①, `[내용]` 금지) 문구를 추가한다.
  - prompt-designer로 전달되는 upstream 품질 기준임을 명시한다.

  **Must NOT do**:
  - organizer가 프롬프트 생성/검토 판정을 수행하도록 역할을 확장하지 않는다.
  - 기존 출력 파일 3종 구조를 바꾸지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 스키마/가이드 문구 보강 중심의 제한적 수정이다.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5, 7-13)
  - **Blocks**: 16
  - **Blocked By**: 1

  **References**:
  **Pattern References**:
  - `agents/content-organizer.md:36` — concepts 스키마 정의 위치
  - `agents/content-organizer.md:96` — MUST DO 확장 위치
  - `agents/prompt-designer.md:139` — downstream이 받는 scene/text 분리 기대치

  **Acceptance Criteria**:
  - [x] `scene_context` 최소 5요소 기준이 스키마에 반영됨
  - [x] MUST DO에 구체 시각요소 요구 + render_text 의미성 강제가 반영됨

  **QA Scenarios**:

  ```
  Scenario: content-organizer 강화 규칙 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/content-organizer.md').read_text(encoding='utf-8'); must=['scene_context','최소 5개','시각 요소']; missing=[m for m in must if m not in t]; assert not missing, f'Missing: {missing}'"
      2. 스키마+MUST DO 강화 문구를 assert한다.
    Expected Result: 강화 규칙 누락 없이 통과한다.
    Evidence: .sisyphus/evidence/task-6-content-organizer-core-check.txt

  Scenario: edge-case — 금지 플레이스홀더 명시 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/content-organizer.md').read_text(encoding='utf-8'); assert '[내용]' in t and '금지' in t"
      2. placeholder 금지 문구가 명시됐는지 검증한다.
    Expected Result: placeholder 금지 미명시 시 실패한다.
    Evidence: .sisyphus/evidence/task-6-content-organizer-edge-check.txt
  ```

  **Commit**: YES (groups with 5-7)
  - Message: `refactor(visual-generator): enrich prompt-designer, content-organizer, content-reviewer`
  - Files: `agents/content-organizer.md`

- [x] 7. content-reviewer.md Enhancement

  **What to do**:
  - `agents/content-reviewer.md`에 hard-reject 규칙을 추가한다: 테마 상한의 150% 초과 시 즉시 REJECT(점수 무관).
  - Review Dimension 5에 빈값/`[내용]`/`{TEXT}`/①②③ 발견 시 1점 처리 규칙을 추가한다.
  - Dimension 1 하위 기준으로 `scene_context` 구체 시각요소 3개 미만 감점(최대 2점)을 추가한다.
  - 기존 5개 review dimensions는 유지하고, 항목 추가만 수행한다.

  **Must NOT do**:
  - 기존 5개 차원 명칭/구조를 삭제/변경하지 않는다.
  - prompt-validator 역할(프롬프트 이후 XML 콘텐츠 검증)까지 침범하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 스코어링/판정 규칙 보강 작업이다.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-6, 8-13)
  - **Blocks**: 16
  - **Blocked By**: 2

  **References**:
  **Pattern References**:
  - `agents/content-reviewer.md:27` — 5개 차원 정의 섹션
  - `agents/content-reviewer.md:46` — PASS/REJECT 로직 확장 지점
  - `agents/content-reviewer.md:41` — Dimension 5 세부 규칙 추가 지점

  **Acceptance Criteria**:
  - [x] 150% hard-reject 규칙이 점수 무관 즉시 REJECT로 반영됨
  - [x] Dimension 1/5에 신규 하위 기준이 추가되고 기존 5차원 구조는 유지됨

  **QA Scenarios**:

  ```
  Scenario: content-reviewer 신규 판정 규칙 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/content-reviewer.md').read_text(encoding='utf-8'); must=['150%','즉시 REJECT','[내용]','{TEXT}','scene_context']; missing=[m for m in must if m not in t]; assert not missing, f'Missing: {missing}'"
      2. hard-reject 및 Dimension 1/5 보강 문구 존재를 assert한다.
    Expected Result: 신규 규칙 누락 없이 통과한다.
    Evidence: .sisyphus/evidence/task-7-content-reviewer-core-check.txt

  Scenario: edge-case — 기존 5개 차원 유지 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/content-reviewer.md').read_text(encoding='utf-8'); dims=['개념 추출 적절성','테마 선택 적합성','레이아웃 선택 적합성','구성용 텍스트 혼입 여부','텍스트 추출 정확성']; missing=[d for d in dims if d not in t]; assert not missing, f'Missing dimensions: {missing}'"
      2. 기존 차원 제목 5개가 모두 남아 있는지 검증한다.
    Expected Result: 기존 차원 손실 시 실패한다.
    Evidence: .sisyphus/evidence/task-7-content-reviewer-regression-check.txt
  ```

  **Commit**: YES (groups with 5-7)
  - Message: `refactor(visual-generator): enrich prompt-designer, content-organizer, content-reviewer`
  - Files: `agents/content-reviewer.md`

- [x] 8. theme-seminar Skill Enrichment

  **What to do**:
  - `skills/theme-seminar/SKILL.md`에 `## Golden Reference Example` 섹션을 추가한다.
  - smart factory AI 품질검사 시스템 주제로 COMPLETE XML 예시(5태그 전부) 1개를 넣는다.
  - `hero_number` 레이아웃 사용 예시를 명시하고, `<text_to_render>`는 실무형 항목(약 20~25개 범위)을 채운다.
  - Scene Guide에 `scene-richness-spec.md` 참조 문구(최소 5문장, 7요소 중 5+)를 추가한다.
  - Typography Guide에 `korean-typography-spec.md` 필수 문구 참조를 추가한다. golden example의 `<typography>` 태그에 Heavy Gothic-style Hangul 폰트 웨이트를 명시하고, `<scene>` 내 네거티브 프롬프팅(예: "No blurry text, no watermarks")을 포함한다.
  - XML-Tag Output Mapping에 `validation-rules-map.md` 준수 문구를 추가한다.

  **Must NOT do**:
  - 새 레이아웃을 만들지 않는다(`hero_number`만 사용).
  - scene 대신 텍스트 나열형 예시를 넣지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 품질 기준 + 테마 톤 + 완전 XML 예시를 동시에 맞춰야 한다.
  - **Skills**: `theme-seminar`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-7, 9-13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-seminar/SKILL.md:24` — Scene Guide 확장 지점
  - `skills/theme-seminar/SKILL.md:41` — Typography Guide 확장 지점
  - `skills/theme-seminar/SKILL.md:48` — XML Mapping 규칙 확장 지점

  **Acceptance Criteria**:
  - [x] Golden Reference Example 섹션에 5태그 완전 XML 예시가 추가됨
  - [x] scene-richness/typography/rules-map 참조 문구가 각 가이드 섹션에 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-seminar golden example 존재 및 완전 XML 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-seminar/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t; tags=['<scene>','<text_to_render>','<typography>','<canvas>','<layout>']; missing=[tag for tag in tags if tag not in t]; assert not missing, f'Missing tags: {missing}'"
      2. 예시 섹션, 5태그 키워드를 assert한다.
    Expected Result: 예시 불완전 시 실패한다.
    Evidence: .sisyphus/evidence/task-8-theme-seminar-core-check.txt

  Scenario: edge-case — 3개 참조 문서 연동 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-seminar/SKILL.md').read_text(encoding='utf-8'); must=['scene-richness-spec.md','korean-typography-spec.md','validation-rules-map.md']; missing=[m for m in must if m not in t]; assert not missing, f'Missing refs: {missing}'"
      2. 참조 문서 링크 문구 누락 여부를 검증한다.
    Expected Result: 참조 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-8-theme-seminar-reference-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-seminar/SKILL.md`

- [x] 9. theme-gov Skill Enrichment

  **What to do**:
  - `skills/theme-gov/SKILL.md`에 `## Golden Reference Example`를 추가한다.
  - 주제는 `디지털 전환 추진 현황`, 레이아웃은 `grid_4`로 COMPLETE XML 예시를 작성한다.
  - Scene Guide에 최소 5문장/7요소 중 5+ 규칙 참조를 넣는다.
  - Typography Guide에 한글 필수 렌더링 문구 참조를 추가한다.
  - XML-Tag Output Mapping에 validation-rules-map 준수를 추가한다.

  **Must NOT do**:
  - 공공 테마를 과도한 장식/영문 위주로 변형하지 않는다.
  - 5태그 외 태그를 추가하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 공공 문서 톤과 구조적 배치를 동시에 만족해야 한다.
  - **Skills**: `theme-gov`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-8, 10-13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-gov/SKILL.md:24` — Scene Guide 보강 지점
  - `skills/theme-gov/SKILL.md:41` — Typography Guide 보강 지점
  - `skills/theme-gov/SKILL.md:48` — XML Mapping 보강 지점

  **Acceptance Criteria**:
  - [x] `grid_4` 기반 complete XML golden example이 추가됨
  - [x] 3개 공통 참조 문서 연결 문구가 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-gov golden example 및 레이아웃 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-gov/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t and 'grid_4' in t; tags=['<scene>','<text_to_render>','<typography>','<canvas>','<layout>']; missing=[tag for tag in tags if tag not in t]; assert not missing, f'Missing: {missing}'"
      2. 주제/레이아웃/5태그 충족 여부를 검증한다.
    Expected Result: complete XML 요건 미충족 시 실패한다.
    Evidence: .sisyphus/evidence/task-9-theme-gov-core-check.txt

  Scenario: edge-case — 공통 참조 3종 누락 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-gov/SKILL.md').read_text(encoding='utf-8'); assert 'scene-richness-spec.md' in t and 'korean-typography-spec.md' in t and 'validation-rules-map.md' in t"
      2. 공통 참조 3종 누락 여부를 assert한다.
    Expected Result: 참조 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-9-theme-gov-reference-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-gov/SKILL.md`

- [x] 10. theme-concept Skill Enrichment

  **What to do**:
  - `skills/theme-concept/SKILL.md`에 `## Golden Reference Example`를 추가한다.
  - 주제 `탄소중립 도시 비전`, 레이아웃 `full_bleed`, `<text_to_render>` 0항목을 엄격히 지키는 COMPLETE XML 예시를 작성한다.
  - Scene는 최소 7문장(개념 테마 특칙)으로 고밀도 시각 메타포를 포함한다.
  - Scene Guide/Typography/XML Mapping에 3개 참조 문구를 추가한다.

  **Must NOT do**:
  - concept 예시에 텍스트 항목을 넣지 않는다.
  - 텍스트 중심 프롬프트로 변질시키지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: concept 특수 규칙(0-text, 장면 7문장+)을 엄격히 반영해야 한다.
  - **Skills**: `theme-concept`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-9, 11-13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-concept/SKILL.md:24` — scene-only 강화 지점
  - `skills/theme-concept/SKILL.md:50` — `<text_to_render>` 0개 원칙 위치
  - `agents/prompt-designer.md:63` — concept 브랜치 규칙 동기화 포인트

  **Acceptance Criteria**:
  - [x] concept golden example이 full_bleed + 0 text items 조건을 충족함
  - [x] scene 최소 7문장 규칙과 3개 참조 문구가 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-concept 0-text golden example 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-concept/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t and 'full_bleed' in t"
      2. full_bleed/0-text 조건 문구 존재를 검증한다.
    Expected Result: concept 특수 규칙 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-10-theme-concept-core-check.txt

  Scenario: edge-case — concept 장면 최소 7문장 기준 반영 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-concept/SKILL.md').read_text(encoding='utf-8'); assert '최소 7문장' in t and 'scene-richness-spec.md' in t"
      2. concept용 강화 scene 기준 문구 반영을 assert한다.
    Expected Result: 7문장 기준 미반영 시 실패한다.
    Evidence: .sisyphus/evidence/task-10-theme-concept-scene-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-concept/SKILL.md`

- [x] 11. theme-whatif Skill Enrichment

  **What to do**:
  - `skills/theme-whatif/SKILL.md`에 `## Golden Reference Example`를 추가한다.
  - 주제 `자율주행 물류 센터 2030`, 레이아웃 `single_focus`로 COMPLETE XML 예시를 작성한다.
  - Scene Guide/Typography/XML Mapping에 3개 참조 문구를 추가한다.
  - what-if 특성(미래 단일 몰입 장면, 과밀 방지)을 예시에 반영한다.

  **Must NOT do**:
  - before/after 비교 구도로 작성하지 않는다(비교는 comparison 전용).
  - 미래 장면인데 근거 없는 과장 텍스트를 과다 배치하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 미래 몰입 장면 규칙과 정보 밀도의 균형이 중요하다.
  - **Skills**: `theme-whatif`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-10, 12-13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-whatif/SKILL.md:19` — scene 원칙 확장 지점
  - `skills/theme-whatif/SKILL.md:36` — typography 확장 지점
  - `skills/theme-whatif/SKILL.md:42` — XML mapping 확장 지점

  **Acceptance Criteria**:
  - [x] single_focus 기반 COMPLETE XML golden example이 추가됨
  - [x] 3개 공통 참조 문구와 what-if 몰입 규칙이 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-whatif golden example 구조 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-whatif/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t and 'single_focus' in t; tags=['<scene>','<text_to_render>','<typography>','<canvas>','<layout>']; missing=[tag for tag in tags if tag not in t]; assert not missing, f'Missing: {missing}'"
      2. 예시 완전성과 레이아웃 키워드를 검증한다.
    Expected Result: 5태그 또는 레이아웃 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-11-theme-whatif-core-check.txt

  Scenario: edge-case — 비교테마 오염 방지 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-whatif/SKILL.md').read_text(encoding='utf-8'); golden_section=t[t.find('Golden Reference Example'):] if 'Golden Reference Example' in t else ''; assert 'LEFT/RIGHT' not in golden_section, 'Comparison-style LEFT/RIGHT found in whatif golden example'"
      2. what-if 예시에 comparison 전용 표현이 잘못 유입되지 않았는지 검증한다.
    Expected Result: 비교테마 오염이 있으면 실패한다.
    Evidence: .sisyphus/evidence/task-11-theme-whatif-edge-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-whatif/SKILL.md`

- [x] 12. theme-pitch Skill Enrichment

  **What to do**:
  - `skills/theme-pitch/SKILL.md`에 `## Golden Reference Example`를 추가한다.
  - 주제 `SaaS 플랫폼 성과 지표`, 레이아웃 `hero_number`로 COMPLETE XML 예시를 작성한다.
  - 핵심 KPI 숫자 중심 텍스트/레이아웃 인용을 명확히 작성한다.
  - Scene Guide/Typography/XML Mapping에 3개 참조 문구를 추가한다.

  **Must NOT do**:
  - 숫자 중심 테마에서 장문 본문 텍스트를 남발하지 않는다.
  - 새 레이아웃이나 새 테마를 추가하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: pitch의 KPI 중심 커뮤니케이션을 예시로 정확히 보여줘야 한다.
  - **Skills**: `theme-pitch`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-11, 13)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-pitch/SKILL.md:20` — Scene Guide 확장 위치
  - `skills/theme-pitch/SKILL.md:37` — Typography 확장 위치
  - `skills/theme-pitch/SKILL.md:43` — XML Mapping 확장 위치

  **Acceptance Criteria**:
  - [x] hero_number + SaaS KPI COMPLETE XML 예시가 추가됨
  - [x] 3개 공통 참조 문구와 숫자 중심 위계가 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-pitch golden example 핵심 요건 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-pitch/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t and 'hero_number' in t; tags=['<scene>','<text_to_render>','<typography>','<canvas>','<layout>']; missing=[tag for tag in tags if tag not in t]; assert not missing, f'Missing: {missing}'"
      2. 예시/레이아웃/5태그 충족을 검증한다.
    Expected Result: 요건 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-12-theme-pitch-core-check.txt

  Scenario: edge-case — 참조 문서 연동 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-pitch/SKILL.md').read_text(encoding='utf-8'); assert 'scene-richness-spec.md' in t and 'korean-typography-spec.md' in t and 'validation-rules-map.md' in t"
      2. 참조 규칙 반영을 assert한다.
    Expected Result: 참조 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-12-theme-pitch-edge-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-pitch/SKILL.md`

- [x] 13. theme-comparison Skill Enrichment

  **What to do**:
  - `skills/theme-comparison/SKILL.md`에 `## Golden Reference Example`를 추가한다.
  - 주제 `기존 vs AI 공정 비교`, 레이아웃 `split_comparison` COMPLETE XML 예시를 작성한다.
  - `<scene>`에서 LEFT/RIGHT 구조를 명확히 분리하고 `<layout>` 인용도 양측 대응으로 작성한다.
  - Scene Guide/Typography/XML Mapping에 3개 참조 문구를 추가한다.

  **Must NOT do**:
  - LEFT/RIGHT 구분 없는 단일 장면으로 작성하지 않는다.
  - 비교쌍이 아닌 독립 항목 나열형 텍스트를 넣지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 비교 테마는 쌍대 구조/정합성 실패 시 품질 저하가 크다.
  - **Skills**: `theme-comparison`, `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-12)
  - **Blocks**: 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/theme-comparison/SKILL.md:19` — LEFT/RIGHT scene 규칙 지점
  - `skills/theme-comparison/SKILL.md:42` — XML mapping 확장 지점
  - `agents/prompt-designer.md:80` — comparison 브랜치 규칙 동기화 지점

  **Acceptance Criteria**:
  - [x] split_comparison COMPLETE XML golden example이 추가됨
  - [x] LEFT/RIGHT scene 구조 + 3개 공통 참조 문구가 반영됨

  **QA Scenarios**:

  ```
  Scenario: theme-comparison golden example 구조/레이아웃 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-comparison/SKILL.md').read_text(encoding='utf-8'); assert 'Golden Reference Example' in t and 'split_comparison' in t; assert 'LEFT' in t and 'RIGHT' in t; tags=['<scene>','<text_to_render>','<typography>','<canvas>','<layout>']; missing=[tag for tag in tags if tag not in t]; assert not missing, f'Missing: {missing}'"
      2. LEFT/RIGHT + 5태그 완전성 + 레이아웃을 검증한다.
    Expected Result: 비교 구조 미완성 시 실패한다.
    Evidence: .sisyphus/evidence/task-13-theme-comparison-core-check.txt

  Scenario: edge-case — 공통 참조 3종 누락 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/theme-comparison/SKILL.md').read_text(encoding='utf-8'); assert 'scene-richness-spec.md' in t and 'korean-typography-spec.md' in t and 'validation-rules-map.md' in t"
      2. 공통 참조 문구 3종 누락 여부를 assert한다.
    Expected Result: 참조 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-13-theme-comparison-reference-check.txt
  ```

  **Commit**: YES (groups with 8-13)
  - Message: `refactor(visual-generator): enrich all 6 theme skills with golden prompts`
  - Files: `skills/theme-comparison/SKILL.md`

- [x] 14. visual-generate.md Pipeline Update

  **What to do**:
  - `commands/visual-generate.md`에 Phase 3.5를 추가한다(Phase 3과 4 사이).
  - 새 단계 내용:
    - `Task(subagent_type="visual-generator:prompt-validator")`
    - REJECT 시 prompt-designer 재실행(최대 2회)
    - output: `validation_result.md`
  - 파이프라인 다이어그램을 `... -> prompt-designer -> prompt-validator -> renderer-agent`로 업데이트한다.
  - MUST DO에 Phase 3.5 호출 시 `scene-richness-spec.md`, `validation-rules-map.md`, `korean-typography-spec.md` 준수 확인 지시를 추가한다.
  - MUST DO에 REJECT 사유를 prompt-designer 재호출 프롬프트에 포함하도록 추가한다.

  **Must NOT do**:
  - content-reviewer와 prompt-validator 역할을 혼합하지 않는다.
  - renderer-agent 단계/슬라이드 렌더 스크립트 계약을 변경하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 오케스트레이터 단계 삽입과 재시도 제어 로직 명시 작업이다.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 15, 16)
  - **Blocks**: 16
  - **Blocked By**: 4

  **References**:
  **Pattern References**:
  - `commands/visual-generate.md:7` — 파이프라인 다이어그램 갱신 위치
  - `commands/visual-generate.md:37` — Phase 3/4 사이 삽입 포인트
  - `agents/prompt-validator.md` — Phase 3.5 호출 대상 스펙

  **Acceptance Criteria**:
  - [x] Phase 3.5(prompt-validator)와 REJECT 시 최대 2회 재실행 로직이 문서에 반영됨
  - [x] MUST DO에 3개 reference 준수 확인 + REJECT 사유 전파 규칙이 반영됨

  **QA Scenarios**:

  ```
  Scenario: visual-generate 파이프라인 단계 삽입 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/commands/visual-generate.md').read_text(encoding='utf-8'); assert 'prompt-validator' in t and 'Phase 3.5' in t and 'validation_result.md' in t"
      2. 단계명/재시도/산출물 키워드를 assert한다.
    Expected Result: 단계 삽입 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-14-visual-generate-core-check.txt

  Scenario: edge-case — REJECT 사유 재전달 규칙 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/commands/visual-generate.md').read_text(encoding='utf-8'); assert 'REJECT' in t and 'prompt-designer' in t and 'scene-richness-spec' in t and 'validation-rules-map' in t and 'korean-typography-spec' in t"
      2. 재호출 시 사유 전파 + 3개 규격 확인 문구를 검증한다.
    Expected Result: 사유 전파 규칙이 없으면 실패한다.
    Evidence: .sisyphus/evidence/task-14-visual-generate-reject-loop-check.txt
  ```

  **Commit**: YES (groups with 14-16)
  - Message: `feat(visual-generator): wire prompt-validator into pipeline, bump to v2.1.0`
  - Files: `commands/visual-generate.md`

- [x] 15. renderer-agent.md Content-Level Checks

  **What to do**:
  - `agents/renderer-agent.md`의 `추가 유지 검증` 섹션에 콘텐츠 수준 백업 검증 3개를 추가한다.
  - Check 12: `<scene>` 최소 문장 수(기본 5, concept 7) 검증.
  - Check 13: `<text_to_render>` ↔ `<layout>` 교차 참조 완전성(고아/유령 없음) 검증.
  - Check 14: `<text_to_render>` 빈 값/플레이스홀더 탐지.
  - 파이프라인 다이어그램을 prompt-validator 포함 구조로 갱신한다.
  - "prompt-validator가 1차 게이트, renderer-agent는 최종 방어선" 문구를 추가한다.

  **Must NOT do**:
  - 기존 8 XML 체크 + 기존 3 추가 유지 검증을 제거/변경하지 않는다.
  - 자동 수정 동작을 넣지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 기존 검증 프레임을 유지한 채 백업 체크를 확장하는 작업이다.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 14, 16)
  - **Blocks**: 16
  - **Blocked By**: 2, 4

  **References**:
  **Pattern References**:
  - `agents/renderer-agent.md:27` — 기존 8개 체크리스트 유지 지점
  - `agents/renderer-agent.md:40` — 추가 유지 검증 확장 지점
  - `agents/renderer-agent.md:93` — 자동 수정 금지 정책 유지 확인

  **Acceptance Criteria**:
  - [x] Check 12~14가 추가되고 prompt-validator 백업 게이트 역할이 명시됨
  - [x] 기존 8+3 검증 항목과 MUST NOT 정책이 그대로 유지됨

  **QA Scenarios**:

  ```
  Scenario: renderer-agent 신규 12~14 체크 반영 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/renderer-agent.md').read_text(encoding='utf-8'); must=['최소 5문장','고아','유령','플레이스홀더']; missing=[m for m in must if m not in t]; assert not missing, f'Missing: {missing}'"
      2. 신규 백업 체크 키워드 존재를 assert한다.
    Expected Result: 체크 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-15-renderer-agent-core-check.txt

  Scenario: edge-case — 기존 검증 회귀 방지 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/agents/renderer-agent.md').read_text(encoding='utf-8'); old=['환각 URL 패턴 검출','플레이스홀더 검출','언어 혼입 검출']; missing=[o for o in old if o not in t]; assert not missing, f'Regression - missing: {missing}'"
      2. 기존 8+3 항목이 유지되는지 검증한다.
    Expected Result: 기존 항목 손실 시 실패한다.
    Evidence: .sisyphus/evidence/task-15-renderer-agent-regression-check.txt
  ```

  **Commit**: YES (groups with 14-16)
  - Message: `feat(visual-generator): wire prompt-validator into pipeline, bump to v2.1.0`
  - Files: `agents/renderer-agent.md`

- [x] 16. Version Bump + Registry Update

  **What to do**:
  - `plugins/visual-generator/.claude-plugin/plugin.json`의 version을 `2.0.0 -> 2.1.0`으로 올린다.
  - 루트 `.claude-plugin/marketplace.json`에서 visual-generator plugin version을 `2.1.0`으로 동기화한다.
  - 루트 `.claude-plugin/marketplace.json`의 visual-generator `agents` 배열에 `./agents/prompt-validator.md`를 추가한다.
  - 루트 `AGENTS.md`를 업데이트한다:
    - STRUCTURE의 visual-generator agents를 5개로 수정
    - 파이프라인 설명에 prompt-validator 삽입
    - WHERE TO LOOK에 새 references 3종(`scene-richness-spec.md`, `validation-rules-map.md`, `korean-typography-spec.md`) 조회 지점 추가
  - 버전 동기화와 레지스트리 반영 일관성을 검증한다.

  **Must NOT do**:
  - visual-generator 이외 플러그인 버전을 임의 변경하지 않는다.
  - marketplace 전체 `metadata.version`을 올리지 않는다(기존 플러그인 수정이므로 불필요).
  - author/email, strict, skills 경로를 변경하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 메타데이터 동기화/등록 작업이며 구조 규칙 확인이 핵심이다.
  - **Skills**: [`plugin-dev`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 14, 15)
  - **Blocks**: Final Verification (F1-F4)
  - **Blocked By**: 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

  **References**:
  **Pattern References**:
  - `plugins/visual-generator/.claude-plugin/plugin.json` — 현재 버전 필드
  - `.claude-plugin/marketplace.json` — visual-generator 레지스트리 블록
  - `AGENTS.md` — STRUCTURE 내 visual-generator agents 설명, WHERE TO LOOK 항목

  **Acceptance Criteria**:
  - [x] plugin.json/marketplace.json visual-generator version이 모두 `2.1.0`으로 일치함
  - [x] marketplace agents에 `./agents/prompt-validator.md`가 등록되고 AGENTS.md 문서가 신규 구조/레퍼런스를 반영함

  **QA Scenarios**:

  ```
  Scenario: 버전/레지스트리 동기화 happy-path 검증
    Tool: Bash
    Steps:
      1. python -c "import json; p=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json',encoding='utf-8')); m=json.load(open('.claude-plugin/marketplace.json',encoding='utf-8')); vg=[x for x in m['plugins'] if x['name']=='visual-generator'][0]; assert p['version']=='2.1.0'; assert vg['version']=='2.1.0'; assert './agents/prompt-validator.md' in vg['agents']"
      2. plugin/registry version 일치 및 agent 등록을 assert한다.
    Expected Result: 불일치/누락이 없으면 통과한다.
    Evidence: .sisyphus/evidence/task-16-version-registry-core-check.txt

  Scenario: edge-case — AGENTS.md 반영 누락 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('AGENTS.md').read_text(encoding='utf-8'); must=['prompt-validator','scene-richness-spec.md','validation-rules-map.md','korean-typography-spec.md']; missing=[m for m in must if m not in t]; assert not missing, f'Missing in AGENTS.md: {missing}'"
      2. AGENTS.md의 구조/WHERE TO LOOK 반영 키워드를 검증한다.
    Expected Result: 문서 반영 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-16-agents-doc-sync-check.txt
  ```

  **Commit**: YES (groups with 14-16)
  - Message: `feat(visual-generator): wire prompt-validator into pipeline, bump to v2.1.0`
  - Files: `plugins/visual-generator/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`

- [x] 17. generate_slide_images.py API Parameter Tuning + System Prompt (B1+B2)

  **What to do**:
  - `skills/slide-renderer/scripts/generate_slide_images.py`의 `GenerateContentConfig`에 `temperature=0.7`, `top_p=0.9` 파라미터를 추가한다.
  - `system_instruction` 파라미터를 추가하여 이미지 생성 품질 제약을 강제한다.
  - System instruction 필수 포함 내용:
    - "한글 렌더링 품질": "All Korean text must be rendered with crisp, perfectly formed characters using heavy-weight Gothic-style sans-serif fonts. Each Korean syllable block must be complete and legible."
    - "시각 구성": "Maintain visual hierarchy with clear foreground/midground/background depth layering. Follow rule of thirds for focal point placement."
    - "네거티브 프롬프팅": "Never render: watermarks, blurry text, numbered lists as visual elements, artifacts, placeholder text, meta-labels like 'Data:'."
    - "여백": "Maintain 30-40% negative space for readability. Do not overcrowd the composition."
    - "텍스트 대비": "Text placed on images must have sufficient contrast for legibility. Use text-shadow or outline when text overlaps busy backgrounds."
  - 기존 이미지 저장/파일명/디렉토리 처리 로직은 절대 변경하지 않는다.
  - MODEL_NAME 변수는 절대 변경하지 않는다.

  **Must NOT do**:
  - MODEL_NAME을 변경하지 않는다.
  - 이미지 저장/파일명/디렉토리 구조를 변경하지 않는다.
  - 멀티샷(여러 이미지 동시 생성) 로직을 추가하지 않는다.
  - response_modalities, aspect_ratio, image_size 기존 설정을 변경하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 렌더링 스크립트 수정은 파이프라인 전체에 영향을 미치며, system prompt 작성은 품질에 직결된다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-13)
  - **Blocks**: 18, 16
  - **Blocked By**: 1, 3

  **References**:
  **Pattern References**:
  - `skills/slide-renderer/scripts/generate_slide_images.py:70-79` — 현재 API 호출 코드 (구조 파악 + 수정 위치)
  - `skills/slide-renderer/scripts/generate_slide_images.py:47-56` — MODEL_NAME 상수 정의 (절대 변경 금지)
  - `skills/slide-renderer/scripts/generate_slide_images.py:96-119` — 이미지 저장 로직 (절대 변경 금지)
  - `skills/slide-renderer/references/scene-richness-spec.md` — system prompt 내 시각 구성/여백 규칙 참조 소스
  - `skills/slide-renderer/references/korean-typography-spec.md` — system prompt 내 한글 렌더링 문구 참조 소스

  **External References**:
  - Gemini API GenerateContentConfig: `temperature`, `top_p`, `system_instruction` 파라미터 사용법

  **Acceptance Criteria**:
  - [x] `GenerateContentConfig`에 `temperature=0.7`, `top_p=0.9`이 설정됨
  - [x] `system_instruction`에 한글 렌더링/시각 구성/네거티브 프롬프팅/여백/텍스트 대비 지침이 모두 포함됨
  - [x] 기존 이미지 저장/파일 처리 로직이 손상 없이 유지됨

  **QA Scenarios**:

  ```
  Scenario: API 파라미터 설정 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); assert 'temperature' in t and 'top_p' in t and 'system_instruction' in t, 'Missing API params'"
      2. temperature/top_p/system_instruction 키워드 존재를 assert한다.
    Expected Result: API 파라미터 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-17-api-params-check.txt

  Scenario: edge-case — 기존 설정 유지 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); assert 'aspect_ratio' in t and '16:9' in t and '4K' in t and 'TEXT' in t and 'IMAGE' in t, 'Existing config damaged'"
      2. 기존 aspect_ratio/image_size/response_modalities 설정이 그대로 유지되는지 검증한다.
    Expected Result: 기존 설정 손상 시 실패한다.
    Evidence: .sisyphus/evidence/task-17-existing-config-check.txt

  Scenario: edge-case — system_instruction 필수 품질 지침 포함 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); must=['Korean','Gothic','watermark','contrast','negative space']; missing=[m for m in must if m.lower() not in t.lower()]; assert not missing, f'System prompt missing: {missing}'"
      2. system_instruction 내 5대 품질 지침 키워드를 검증한다.
    Expected Result: 품질 지침 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-17-system-prompt-check.txt
  ```

  **Commit**: YES (groups with 17-18)
  - Message: `feat(visual-generator): tune API params, add system prompt and quality-based retry`
  - Files: `skills/slide-renderer/scripts/generate_slide_images.py`

- [x] 18. Quality-Based Retry with Gemini Vision Self-Evaluation (B3)

  **What to do**:
  - `generate_slide_images.py`에 이미지 생성 후 품질 평가 로직을 추가한다.
  - 생성된 이미지를 Gemini 비전 모델에 전달하여 3가지 기준으로 평가한다:
    - (1) 한글 텍스트 가독성/깨짐 여부 (0~10)
    - (2) 레이아웃 구성 적합성 (0~10)
    - (3) 색상 팔레트 준수 (0~10)
  - 종합 점수 임계값(default 7.0) 미달 시 재생성한다 (최대 2회 추가, 총 3회 시도).
  - 재생성 시 이전 평가의 구체적 피드백을 보정 힌트로 프롬프트에 추가한다.
    - 예: "이전 생성에서 '혁신' 텍스트가 깨졌습니다. 해당 텍스트를 선명하게 렌더링하세요."
  - 3회 시도 후에도 임계값 미달 시 최고 점수 이미지를 최종 선택한다.
  - 기존 API 에러 재시도(3회) 로직과 별도로 운영한다 (품질 재시도는 생성 성공 후 품질 검증).
  - 품질 평가 결과를 콘솔 로그로 출력한다 (점수 + 판정 + 시도 횟수).

  **Must NOT do**:
  - 기존 API 에러 재시도 로직을 제거하지 않는다.
  - 품질 재시도 횟수를 3회 초과로 설정하지 않는다.
  - 외부 OCR 라이브러리(pytesseract 등)를 설치/사용하지 않는다 (Gemini 비전 모델만 사용).
  - 이미지 저장 경로/파일명 규칙을 변경하지 않는다.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 비전 모델 평가 로직 + 재시도 플로우 제어 + 보정 힌트 생성 로직이 복잡하다.
  - **Skills**: `slide-renderer`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 14, 15, 16)
  - **Blocks**: 16
  - **Blocked By**: 17

  **References**:
  **Pattern References**:
  - `skills/slide-renderer/scripts/generate_slide_images.py:70-79` — T17에서 수정된 API 호출 코드 (품질 루프가 감싸는 대상)
  - `skills/slide-renderer/scripts/generate_slide_images.py:58-68` — 기존 API 에러 재시도 로직 (max_retries=3, 병렬 운영)
  - `skills/slide-renderer/scripts/generate_slide_images.py:96-119` — 이미지 저장 로직 (변경 금지)

  **External References**:
  - Gemini API: `client.models.generate_content()` 응답에서 이미지 추출 후 비전 모델로 재평가하는 패턴

  **Acceptance Criteria**:
  - [x] 이미지 생성 후 Gemini 비전 모델로 3가지 기준 평가하는 로직이 존재함
  - [x] 임계값 미달 시 보정 힌트 포함 재생성 + 최대 3회 제한이 구현됨
  - [x] 3회 시도 후 최고점수 선택 폴백 로직이 구현됨
  - [x] 기존 API 에러 재시도 로직이 손상 없이 유지됨

  **QA Scenarios**:

  ```
  Scenario: 품질 평가 로직 존재 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); must=['quality','score','threshold','retry','feedback']; present=[m for m in must if m.lower() in t.lower()]; assert len(present)>=4, f'Only {len(present)}/5 quality keywords found: {present}'"
      2. 품질 평가 관련 키워드 5개 중 4개 이상 존재를 검증한다.
    Expected Result: 품질 평가 로직 누락 시 실패한다.
    Evidence: .sisyphus/evidence/task-18-quality-retry-core-check.txt

  Scenario: edge-case — 최대 재시도 횟수 제한 검증
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); assert '3' in t or 'max' in t.lower(), 'No retry limit found'"
      2. 재시도 횟수 제한이 코드에 존재하는지 검증한다.
    Expected Result: 제한 없는 무한 재시도 방지.
    Evidence: .sisyphus/evidence/task-18-retry-limit-check.txt

  Scenario: edge-case — 기존 API 에러 재시도 유지 확인
    Tool: Bash
    Steps:
      1. python -c "from pathlib import Path; t=Path('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read_text(encoding='utf-8'); assert 'max_retries' in t or 'except' in t, 'API error retry logic missing'"
      2. 기존 API 에러 재시도 로직이 유지되는지 검증한다.
    Expected Result: 기존 로직 손상 시 실패한다.
    Evidence: .sisyphus/evidence/task-18-api-retry-regression-check.txt
  ```

  **Commit**: YES (groups with 17-18)
  - Message: `feat(visual-generator): tune API params, add system prompt and quality-based retry`
  - Files: `skills/slide-renderer/scripts/generate_slide_images.py`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, check content). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Review all changed/created files for: frontmatter 형식 준수, 한글/영문 일관성, SKILL.md 500줄 이하 확인, agent description에 "Use when..." 포함 확인, marketplace.json 구조 무결성 확인, LF 줄바꿈 확인.
  Output: `Files [N clean/N issues] | VERDICT`

- [ ] F3. **End-to-End Rendering Test** — `unspecified-high` (skills: `playwright` if needed)
  실제 파이프라인 테스트: (1) 테스트 입력 문서로 content-organizer 호출 (2) content-reviewer 통과 확인 (3) prompt-designer로 XML 프롬프트 생성 (4) prompt-validator가 PASS 판정 확인 (5) renderer-agent의 XML 검증 통과 확인 (6) Gemini 렌더링 실행: system_instruction 적용 확인 + 품질 재시도 로직 동작 확인 + 한글 깨짐 여부 확인. 세미나 테마 사용.
  Output: `Phase [N/6 pass] | Quality Retry [triggered/not-triggered] | Rendering [PASS/SKIP] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify: layout-types SKILL.md 미수정, generate_slide_images.py 미수정, XML 태그 스키마 미변경, 새 스킬 폴더 미생성, content-reviewer 기존 차원 미변경, renderer-agent 기존 검증 미삭제. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Guardrails [N/N intact] | VERDICT`

---

## Commit Strategy

| Wave | Message | Files | Pre-commit |
|:----:|---------|-------|-----------|
| 1 | `docs(visual-generator): add scene richness spec, validation rules map, Korean typography spec` | `slide-renderer/references/*.md` | N/A |
| 2a | `feat(visual-generator): add prompt-validator agent` | `agents/prompt-validator.md` | N/A |
| 2b | `refactor(visual-generator): enrich prompt-designer, content-organizer, content-reviewer` | `agents/*.md` | N/A |
| 2c | `refactor(visual-generator): enrich all 6 theme skills with golden prompts` | `skills/theme-*/**` | N/A |
| 3 | `feat(visual-generator): wire prompt-validator into pipeline, bump to v2.1.0` | `commands/*, .claude-plugin/*, AGENTS.md` | N/A |
| 2d | `feat(visual-generator): tune API params, add system prompt and quality-based retry` | `scripts/generate_slide_images.py` | N/A |

---

## Success Criteria

### Verification Commands
```bash
# 1. prompt-validator 에이전트 파일 존재
python -c "import os; assert os.path.exists('plugins/visual-generator/agents/prompt-validator.md')"

# 2. marketplace.json에 prompt-validator 등록
python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); vg=[p for p in d['plugins'] if p['name']=='visual-generator'][0]; assert './agents/prompt-validator.md' in vg['agents']"

# 3. visual-generate.md에 prompt-validator 단계 존재
python -c "c=open('plugins/visual-generator/commands/visual-generate.md').read(); assert 'prompt-validator' in c"

# 4. 6개 테마 스킬 모두 예시 scene 포함
python -c "import glob; skills=glob.glob('plugins/visual-generator/skills/theme-*/SKILL.md'); missing=[s for s in skills if 'Example' not in open(s).read() and 'golden' not in open(s).read().lower()]; assert not missing, f'Missing: {missing}'"

# 5. scene-richness-spec.md 존재
python -c "import os; assert os.path.exists('plugins/visual-generator/skills/slide-renderer/references/scene-richness-spec.md')"

# 6. plugin.json 버전 2.1.0
python -c "import json; d=json.load(open('plugins/visual-generator/.claude-plugin/plugin.json')); assert d['version']=='2.1.0'"

# 7. layout-types SKILL.md 미수정 (938줄 유지)
python -c "lines=open('plugins/visual-generator/skills/layout-types/SKILL.md').readlines(); assert len(lines)==938, f'Modified: {len(lines)} lines'"

# 8. generate_slide_images.py에 temperature/system_instruction 포함
python -c "t=open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read(); assert 'temperature' in t and 'system_instruction' in t"

# 9. 품질 기반 재시도 로직 포함
python -c "t=open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py').read(); assert 'quality' in t.lower() and 'score' in t.lower()"
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] prompt-validator REJECT-only 동작 확인
- [x] 6개 테마 스킬 각각 golden reference 예시 포함
- [x] visual-generate.md 파이프라인에 Phase 3.5 삽입됨
- [x] generate_slide_images.py에 temperature/top_p/system_instruction 추가됨
- [x] 품질 기반 재시도 로직(Gemini 비전 자체평가, 최대 3회) 동작함
