
- [ ] 6. hwpx-templates SKILL.md + scripts

  **What to do**:
  - Repo 2 (gonggong_hwpxskills)의 SKILL.md에서 ZIP-level 치환 워크플로우 내용을 추출하여 통합
  - **소스 SKILL.md**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/SKILL.md`
  - **소스 스크립트**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/scripts/fix_namespaces.py`
  - SKILL.md 포함할 내용:
    - frontmatter: `name: hwpx-templates`, description
    - 양식 선택 정책 (사용자 업로드 > 기본 양식 > new())
    - 필수 워크플로우 (양식복사 - ObjectFinder조사 - ZIP치환 - 네임스페이스 - 검증)
    - `zip_replace()` 함수 (일괄 치환) - 인라인 코드 포함
    - `zip_replace_sequential()` 함수 (순차 치환) - 인라인 코드 포함
    - ObjectFinder 텍스트 전수 조사 방법
    - 기본 양식(report-template.hwpx) 활용 가이드
    - 사용자 업로드 양식 활용 가이드
    - 필수 후처리: fix_namespaces.py 설명
    - Quick Reference 표
    - 주의사항 (10개)
  - **경로 수정 필수**: 모든 `/mnt/skills/user/hwpx/` -> `$SKILL_DIR/`, `/home/claude/` -> 상대경로로 변경
  - fix_namespaces.py를 `scripts/fix_namespaces.py`로 저장
  - **중요**: fix_namespaces.py는 regex/string 방식 유지 (lxml 리팩토링 절대 금지 - ns0 재도입 방지)
  - **중요**: fix_namespaces.py는 ZIP-level 치환 후에만 필요, XML-first 빌드(hwpx-core)에는 불필요함을 명시

  **Must NOT do**:
  - fix_namespaces.py를 lxml 기반으로 리팩토링 (regex 접근이 의도적 설계)
  - python-hwpx `HwpxDocument.open()` 사용 권장 (ZIP-level 치환 우선)
  - 하드코딩 경로 (`/mnt/skills/`, `/home/claude/`, `/mnt/user-data/`)
  - SKILL.md 500줄 초과

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: repo2의 워크플로우를 새 컨텍스트에 맞게 재구성 + 경로 수정 + 통합
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Tasks 2, 3, 5]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/SKILL.md` - ZIP 치환 워크플로우 원본
  - `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/scripts/fix_namespaces.py` - 네임스페이스 후처리 스크립트
  - Task 2의 hwpx-core SKILL.md - 교차 참조 확인 (워크플로우 영역 분리)

  **Acceptance Criteria**:
  - [ ] SKILL.md 존재, frontmatter `name: hwpx-templates`
  - [ ] 줄 수 <= 500
  - [ ] zip_replace, zip_replace_sequential 함수 포함
  - [ ] fix_namespaces.py 스크립트 존재
  - [ ] 하드코딩 경로 없음
  - [ ] fix_namespaces.py에 lxml import 없음 (regex/re 사용)

  **QA Scenarios:**
  ```
  Scenario: fix_namespaces.py가 regex 방식인지 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c 'import lxml' plugins/hwpx-generator/skills/hwpx-templates/scripts/fix_namespaces.py - 0 기대
      2. grep -c 'import re' 같은 파일 - 1 이상 기대
    Expected Result: lxml 0건, re 1건 이상
    Evidence: .sisyphus/evidence/task-6-fix-namespaces-regex.txt

  Scenario: SKILL.md에 하드코딩 경로 없음
    Tool: Bash (grep)
    Steps:
      1. grep -n '/mnt/skills\|/home/claude\|/mnt/user-data' plugins/hwpx-generator/skills/hwpx-templates/SKILL.md
    Expected Result: 매칭 0건
    Evidence: .sisyphus/evidence/task-6-no-hardcoded.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(hwpx-generator): add hwpx-templates and hwpx-math skills`
  - Files: `plugins/hwpx-generator/skills/hwpx-templates/**`

---

- [ ] 7. hwpx-templates references + assets

  **What to do**:
  - Repo 2 (gonggong_hwpxskills)에서 스타일 가이드와 템플릿 자산을 가져옴
  - **소스 레퍼런스**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/references/`
    1. `report-style.md` - 보고서 스타일 가이드
    2. `official-doc-style.md` - 공문서 스타일 가이드
    3. `xml-internals.md` - 저수준 XML 조작 가이드
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-templates/references/`
  - **소스 자산**: `https://raw.githubusercontent.com/Canine89/gonggong_hwpxskills/main/assets/report-template.hwpx`
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx`
  - report-template.hwpx는 바이너리 파일이므로 `curl -L -o` 사용

  **Must NOT do**:
  - 레퍼런스 내용 자체 작성

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 8, 9, 10)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Task 4]

  **References**:
  - `https://github.com/Canine89/gonggong_hwpxskills/tree/main/references` - 레퍼런스 디렉토리
  - `https://github.com/Canine89/gonggong_hwpxskills/tree/main/assets` - 자산 디렉토리

  **Acceptance Criteria**:
  - [ ] `references/report-style.md` 존재
  - [ ] `references/official-doc-style.md` 존재
  - [ ] `references/xml-internals.md` 존재
  - [ ] `assets/report-template.hwpx` 존재 (0 bytes 아님)

  **QA Scenarios:**
  ```
  Scenario: 레퍼런스 + 자산 파일 존재 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-templates/references/ - 3개 .md 파일
      2. ls -la plugins/hwpx-generator/skills/hwpx-templates/assets/report-template.hwpx - 0 bytes 아님
    Expected Result: 3개 reference + 1개 asset 모두 비어있지 않음
    Evidence: .sisyphus/evidence/task-7-refs-assets.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 8. hwpx-math SKILL.md 작성

  **What to do**:
  - Repo 3 (hwpxskill-math)의 SKILL.md에서 핵심 내용을 추출하여 hwpx-math SKILL.md 작성
  - **소스**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md`
  - SKILL.md 포함할 내용:
    - frontmatter: `name: hwpx-math`, description
    - 환경 설정 (VENV, SKILL_DIR, HWPX_SKILL_DIR -> hwpx-core 스킬 경로)
    - 핵심 워크플로우: JSON -> HWPX 문제지 (빌드 명령어)
    - 문제 JSON 형식 (학력평가 + worksheet)
    - 필드 설명표
    - 수식 XML 구조 (hp:equation 간략 설명, 상세는 references로)
    - 2단 레이아웃 설정 + 페이지 설정
    - 스타일 ID 맵 (charPr/paraPr/tabPr/borderFill)
    - 학력평가 시험지 레이아웃 구조
    - hwpx-core 스킬과의 연동 안내 (validate.py, unpack/pack 교차참조)
    - 단위 변환표 (문제지 특화)
    - Critical Rules
  - **500줄 이하로 압축** - 수식 스크립트 레퍼런스(기본~미적분/기하)는 `references/equation-reference.md`로 분리
  - **500줄 이하로 압축** - 도형 그래프 스펙(삼각형/원/사각형/좌표/입체)은 `references/geometry-reference.md`로 분리
  - hwpx-core 스킬의 validate.py 교차참조 패턴 포함:
    ```
    ### hwpx-core 스킬 검증 도구 사용
    Step 1. 상대경로: ../hwpx-core/scripts/validate.py
    Step 2. Glob 폴백: **/hwpx-core/scripts/validate.py
    Step 3. Glob: **/validate.py
    ```

  **Must NOT do**:
  - SKILL.md 500줄 초과
  - 수식 스크립트에 LaTeX 문법 사용 (한컴 문법만)
  - 하드코딩 경로

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 750+ 줄 원본을 500줄로 압축 + references 분리 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 9, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Tasks 2, 5]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md` - 수학 스킬 원본 (750+줄)
  - Task 2의 hwpx-core SKILL.md - 교차참조 확인 (검증 도구 경로)

  **Acceptance Criteria**:
  - [ ] SKILL.md 존재, frontmatter `name: hwpx-math`
  - [ ] 줄 수 <= 500
  - [ ] hwpx-core 교차참조 패턴 포함
  - [ ] 수식 스크립트 레퍼런스는 `references/`로 분리됨

  **QA Scenarios:**
  ```
  Scenario: SKILL.md 줄 수 + 교차참조 검증
    Tool: Bash
    Steps:
      1. wc -l plugins/hwpx-generator/skills/hwpx-math/SKILL.md - <= 500
      2. grep -c 'hwpx-core' 같은 파일 - 1 이상 (교차참조 존재)
    Expected Result: 500 이하 + 교차참조 1건 이상
    Evidence: .sisyphus/evidence/task-8-math-skill.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 9. hwpx-math scripts (7 modules fetch + adapt)

  **What to do**:
  - Repo 3 (hwpxskill-math)에서 7개 Python 모듈을 가져와 저장
  - **소스 base URL**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/scripts/`
  - 가져올 스크립트:
    1. `build_math_hwpx.py` - CLI + 오케스트레이션
    2. `xml_primitives.py` - IDGen, STYLE 상수, 기본 문단/수식 생성기
    3. `exam_helpers.py` - 시험지 전용 XML 생성기
    4. `table_layout.py` - 투명 테이블 레이아웃
    5. `section_generators.py` - worksheet/exam section0.xml 조립
    6. `hwpx_utils.py` - 검증/패키징/메타데이터
    7. `graph_generator.py` - 그래프 PNG 생성 (matplotlib)
  - 저장 위치: `plugins/hwpx-generator/skills/hwpx-math/scripts/`
  - **의존성**: lxml, matplotlib

  **Must NOT do**:
  - 스크립트 자체 작성 (반드시 GitHub에서 fetch)
  - 모듈 간 의존 구조 변경 (primitives -> helpers -> layout -> section -> build 순서 유지)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 10)
  - **Blocks**: [Tasks 11, 13]
  - **Blocked By**: [Task 3]

  **References**:
  - `https://github.com/Canine89/hwpxskill-math/tree/main/scripts` - 전체 스크립트 목록
  - Repo 3 SKILL.md `모듈 의존 구조` 섹션 - 순환 없는 의존 그래프

  **Acceptance Criteria**:
  - [ ] 7개 스크립트 모두 존재
  - [ ] 모든 스크립트 AST 파싱 통과

  **QA Scenarios:**
  ```
  Scenario: 7개 모듈 존재 + 구문 유효
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-math/scripts/*.py | wc -l - 7개 이상
      2. python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('plugins/hwpx-generator/skills/hwpx-math/scripts/*.py')]" - 오류 없음
    Expected Result: 7개 존재, 모두 파싱 통과
    Evidence: .sisyphus/evidence/task-9-math-scripts.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

- [ ] 10. hwpx-math templates + references + examples

  **What to do**:
  - Repo 3에서 템플릿, 레퍼런스, 예제를 가져와 저장
  - **템플릿**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/templates/base/` -> `templates/math-base/` (이름 변경! hwpx-core의 base와 충돌 방지)
  - **레퍼런스** (SKILL.md에서 분리한 내용으로 작성):
    1. `references/equation-reference.md` - 한컴 수식 스크립트 전체 레퍼런스 (기본 규칙, 분수/루트, 첨자, 적분/합, 극한, 괄호, 행렬, 연립, 장식, 그리스문자, 특수기호, 폰트, 내장함수, 학년별 예시)
    2. `references/geometry-reference.md` - 도형 그래프 타입 5개 전체 스펙 (triangle, circle, quadrilateral, coordinate, solid3d)
  - **예제**: `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/examples/` 에서 sample JSON + 빌드 스크립트 fetch
  - 레퍼런스 작성 시 Repo 3 SKILL.md의 해당 섹션을 그대로 추출하여 저장

  **Must NOT do**:
  - math 템플릿을 `base/`로 저장 (반드시 `math-base/`)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Task 4]

  **References**:
  - `https://raw.githubusercontent.com/Canine89/hwpxskill-math/main/SKILL.md` - 수식/도형 섹션 추출 원본
  - `https://github.com/Canine89/hwpxskill-math/tree/main/templates` - 템플릿 원본
  - `https://github.com/Canine89/hwpxskill-math/tree/main/examples` - 예제 원본

  **Acceptance Criteria**:
  - [ ] `templates/math-base/` 디렉토리 존재 (base/ 아님!)
  - [ ] `references/equation-reference.md` 존재 (100+ 줄)
  - [ ] `references/geometry-reference.md` 존재 (50+ 줄)
  - [ ] `examples/` 내 sample JSON 1개 이상 존재

  **QA Scenarios:**
  ```
  Scenario: 템플릿 디렉토리 이름 검증
    Tool: Bash
    Steps:
      1. ls plugins/hwpx-generator/skills/hwpx-math/templates/ - math-base/ 존재, base/ 없음
    Expected Result: math-base 존재, base 없음
    Evidence: .sisyphus/evidence/task-10-math-templates.txt
  ```

  **Commit**: YES (groups with Wave 2)

---

### Wave 3 Tasks (Agents + Command - after Wave 2, 3 parallel)

---

- [ ] 11. hwpx-builder agent 작성

  **What to do**:
  - HWPX 문서를 XML-first 방식으로 생성하는 전문 에이전트 작성
  - 파일: `plugins/hwpx-generator/agents/hwpx-builder.md`
  - 에이전트 역할:
    - 사용자 요청을 분석하여 적절한 문서 유형 결정 (공문/보고서/회의록/제안서/수학문제지)
    - hwpx-core 스킬의 build_hwpx.py를 사용한 XML-first 빌드
    - hwpx-templates 스킬의 ZIP 치환 워크플로우 활용
    - hwpx-math 스킬의 수학 문제지 생성
  - frontmatter: `name: hwpx-builder`, description에 "Use PROACTIVELY when..." 포함, `model: sonnet`
  - 에이전트 구조:
    - Purpose: HWPX 문서 생성 전문가
    - Capabilities: XML-first 빌드, ZIP 치환, 수식 문제지
    - Workflow: 문서 유형 판별 -> 템플릿 선택 -> 콘텐츠 생성 -> 빌드 -> 검증
    - Constraints: HWPX만 (HWP 미지원), 검증 필수, 네임스페이스 후처리 (ZIP 치환 시)

  **Must NOT do**:
  - 에이전트가 직접 XML 코드 하드코딩 (스킬의 스크립트 사용)
  - HWP 파일 처리 약속

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 3개 스킬을 조합하는 복잡한 에이전트 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Tasks 2, 3, 6, 8, 9]

  **References**:
  - `plugins/isd-generator/agents/chapter1.md` - 에이전트 .md 포맷 참고 (프로젝트 표준)
  - Task 2 (hwpx-core SKILL.md) - 빌드 워크플로우 이해
  - Task 6 (hwpx-templates SKILL.md) - ZIP 치환 워크플로우 이해
  - Task 8 (hwpx-math SKILL.md) - 수학 문제지 워크플로우 이해
  - AGENTS.md `Agent File Structure` 섹션 - frontmatter 필드 규칙

  **Acceptance Criteria**:
  - [ ] `agents/hwpx-builder.md` 존재
  - [ ] frontmatter에 name, description, model 포함
  - [ ] description에 "Use when" 또는 "Use PROACTIVELY when" 포함
  - [ ] 3개 스킬 모두 참조

  **QA Scenarios:**
  ```
  Scenario: 에이전트 frontmatter + 스킬 참조 검증
    Tool: Bash
    Steps:
      1. head -10 plugins/hwpx-generator/agents/hwpx-builder.md - frontmatter 확인
      2. grep -c 'hwpx-core\|hwpx-templates\|hwpx-math' 같은 파일 - 3 이상
    Expected Result: frontmatter 올바름 + 3개 스킬 참조
    Evidence: .sisyphus/evidence/task-11-builder-agent.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(hwpx-generator): add agents and orchestrator command`

---

- [ ] 12. hwpx-analyzer agent 작성

  **What to do**:
  - 기존 HWPX 파일을 분석하고 역공학하는 전문 에이전트 작성
  - 파일: `plugins/hwpx-generator/agents/hwpx-analyzer.md`
  - 에이전트 역할:
    - 사용자 제공 HWPX 파일을 analyze_template.py로 심층 분석
    - 스타일 ID, 표 구조, 레이아웃 패턴을 추출
    - 분석 결과를 기반으로 동일 레이아웃의 새 문서 생성 가이드 제공
    - unpack/pack을 사용한 기존 문서 편집
  - frontmatter: `name: hwpx-analyzer`, description에 "Use when..." 포함, `model: sonnet`
  - 에이전트 구조:
    - Purpose: HWPX 문서 분석/역공학 전문가
    - Capabilities: 심층 분석, 스타일 추출, 레이아웃 복제, 문서 편집
    - Workflow: HWPX 수신 -> analyze_template.py 실행 -> header.xml 추출 -> 분석 리포트 -> 새 문서 생성 또는 편집
    - Constraints: HWPX만, 원본 스타일 ID 보존, charPrIDRef/paraPrIDRef 정합성

  **Must NOT do**:
  - HWP 파일 처리 약속
  - 스타일 ID 임의 변경 권장

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 11, 13)
  - **Blocks**: [Task 13]
  - **Blocked By**: [Tasks 2, 3, 6]

  **References**:
  - Task 2 (hwpx-core SKILL.md) - 워크플로우 5: 레퍼런스 기반 문서 생성 이해
  - `plugins/general-agents/agents/interview.md` - 에이전트 포맷 참고

  **Acceptance Criteria**:
  - [ ] `agents/hwpx-analyzer.md` 존재
  - [ ] frontmatter에 name, description, model 포함
  - [ ] analyze_template.py 참조 포함

  **QA Scenarios:**
  ```
  Scenario: 에이전트 파일 + analyze 참조 검증
    Tool: Bash
    Steps:
      1. head -10 plugins/hwpx-generator/agents/hwpx-analyzer.md - frontmatter 확인
      2. grep -c 'analyze_template' 같은 파일 - 1 이상
    Expected Result: frontmatter 올바름 + analyze 참조 존재
    Evidence: .sisyphus/evidence/task-12-analyzer-agent.txt
  ```

  **Commit**: YES (groups with Wave 3)

---

- [ ] 13. hwpx-generate command 작성

  **What to do**:
  - HWPX 문서 생성 전체를 오케스트레이션하는 커맨드 작성
  - 파일: `plugins/hwpx-generator/commands/hwpx-generate.md`
  - 커맨드 워크플로우:
    - Phase 1: 요구사항 파악 (문서 유형, 내용, 양식)
    - Phase 2: 양식 선택 (사용자 업로드 > 기본 양식 > XML-first)
    - Phase 3: 문서 생성
      - 양식 있으면 -> hwpx-builder (ZIP 치환 모드)
      - 양식 없으면 -> hwpx-builder (XML-first 모드)
      - 수학 문제지면 -> hwpx-builder (hwpx-math 모드)
    - Phase 4: 검증 (validate.py)
    - Phase 5: 결과 전달
  - $ARGUMENTS로 사용자 입력 받기
  - Task tool로 hwpx-builder, hwpx-analyzer 에이전트 호출
  - frontmatter 없음 (커맨드는 frontmatter 없음)

  **Must NOT do**:
  - 커맨드에 frontmatter 추가 (커맨드는 frontmatter 없음)
  - 에이전트 로직 직접 포함 (Task tool로 위임)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 3개 스킬 + 2개 에이전트를 조합하는 오케스트레이터 설계
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (agents 완성 후)
  - **Parallel Group**: Wave 3
  - **Blocks**: [Tasks 14, 15]
  - **Blocked By**: [Tasks 6, 7, 8, 9, 10, 11, 12]

  **References**:
  - `plugins/isd-generator/commands/isd-generate.md` - 커맨드 포맷 참고 (프로젝트 표준 오케스트레이터)
  - `plugins/visual-generator/commands/visual-generate.md` - 또 다른 커맨드 참고
  - AGENTS.md `Commands (커맨드)` 섹션 - 커맨드 구조 규칙

  **Acceptance Criteria**:
  - [ ] `commands/hwpx-generate.md` 존재
  - [ ] frontmatter 없음
  - [ ] Phase 1-5 워크플로우 포함
  - [ ] Task tool로 에이전트 호출 패턴 포함
  - [ ] $ARGUMENTS 사용

  **QA Scenarios:**
  ```
  Scenario: 커맨드 파일 구조 검증
    Tool: Bash
    Steps:
      1. head -3 plugins/hwpx-generator/commands/hwpx-generate.md - '---'로 시작하지 않음 (frontmatter 없음)
      2. grep -c 'Task tool\|subagent_type' 같은 파일 - 1 이상
      3. grep -c 'ARGUMENTS' 같은 파일 - 1 이상
    Expected Result: frontmatter 없음 + Task tool 참조 + ARGUMENTS 참조
    Evidence: .sisyphus/evidence/task-13-command.txt
  ```

  **Commit**: YES (groups with Wave 3)

---

### Wave 4 Tasks (Registry + Cleanup - after Wave 3, 2 sequential)

---

- [ ] 14. Update marketplace.json + delete hwpx-converter

  **What to do**:
  - `.claude-plugin/marketplace.json`에서:
    1. `hwpx-converter` 항목 제거
    2. `hwpx-generator` 항목 추가:
       ```json
       {
         "name": "hwpx-generator",
         "source": "./plugins/hwpx-generator",
         "description": "HWPX 문서 생성/편집/분석 통합 플러그인. XML-first 빌드 + ZIP 치환 + 수학 수식 지원.",
         "version": "1.0.0",
         "strict": true,
         "agents": [
           "./agents/hwpx-builder.md",
           "./agents/hwpx-analyzer.md"
         ],
         "skills": ["./skills"]
       }
       ```
  - `plugins/hwpx-converter/` 디렉토리 전체 삭제
  - marketplace.json metadata.version은 변경 불필요 (기존 플러그인 교체는 마켓플레이스 MINOR 아님)

  **Must NOT do**:
  - marketplace.json의 다른 플러그인 항목 수정
  - hwpx-converter 삭제 전 백업 생성 (git에 히스토리 있음)
  - `"skills": ["./skills/"]` (trailing slash 금지)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: JSON 편집 + 디렉토리 삭제
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: [Task 15, F1-F4]
  - **Blocked By**: [Task 13]

  **References**:
  - `.claude-plugin/marketplace.json` (현재 파일) - 기존 구조 확인
  - AGENTS.md `marketplace.json plugin 항목 필드` 표 - 필수 필드 확인
  - AGENTS.md `Forbidden Patterns` - `"skills": ["./skills/"]` trailing slash 금지

  **Acceptance Criteria**:
  - [ ] marketplace.json에 hwpx-generator 존재
  - [ ] marketplace.json에 hwpx-converter 없음
  - [ ] marketplace.json이 유효한 JSON
  - [ ] `plugins/hwpx-converter/` 디렉토리 없음
  - [ ] `"strict": true` 설정
  - [ ] `"skills": ["./skills"]` (trailing slash 없음)

  **QA Scenarios:**
  ```
  Scenario: marketplace.json 유효성 + 플러그인 교체 검증
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in d['plugins']]; assert 'hwpx-generator' in names; assert 'hwpx-converter' not in names; print('PASS')"
      2. ls plugins/hwpx-converter/ 2>&1 - "No such file or directory" 기대
    Expected Result: PASS + 디렉토리 없음
    Evidence: .sisyphus/evidence/task-14-marketplace.txt

  Scenario: hwpx-generator 항목 상세 검증
    Tool: Bash
    Steps:
      1. python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); p=[x for x in d['plugins'] if x['name']=='hwpx-generator'][0]; assert p['strict']==True; assert './skills' in p.get('skills',[]); assert len(p.get('agents',[]))>=2; print('PASS')"
    Expected Result: PASS
    Evidence: .sisyphus/evidence/task-14-generator-entry.txt
  ```

  **Commit**: YES
  - Message: `feat(hwpx-generator): register plugin and replace hwpx-converter`
  - Files: `.claude-plugin/marketplace.json`, `plugins/hwpx-converter/` (deleted)

---

- [ ] 15. Update AGENTS.md

  **What to do**:
  - `AGENTS.md` 업데이트:
    1. **Generated 날짜** 업데이트 (현재 날짜)
    2. **STRUCTURE 섹션**: `hwpx-converter` 트리 제거, `hwpx-generator` 트리 추가
       - agents/ (hwpx-builder.md, hwpx-analyzer.md)
       - commands/ (hwpx-generate.md)
       - skills/ (hwpx-core/, hwpx-templates/, hwpx-math/)
    3. **WHERE TO LOOK 표**: hwpx-converter 행 교체 -> hwpx-generator 행들 추가
       - HWPX 문서 생성: `plugins/hwpx-generator/commands/hwpx-generate.md`
       - HWPX XML-first 빌드: `plugins/hwpx-generator/skills/hwpx-core/SKILL.md`
       - HWPX 템플릿 치환: `plugins/hwpx-generator/skills/hwpx-templates/SKILL.md`
       - 수학 수식 문제지: `plugins/hwpx-generator/skills/hwpx-math/SKILL.md`
    4. **COMMANDS 섹션**: 기존 hwpx 관련 명령어 업데이트
    5. **UNIQUE STYLES 섹션**: hwpx-generator 특이사항 추가 (fix_namespaces 필수, 한컴 수식 스크립트)
    6. **README.md 표**: hwpx-converter -> hwpx-generator로 교체

  **Must NOT do**:
  - AGENTS.md의 다른 섹션 불필요하게 수정
  - README.md 외 다른 파일 수정

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 기존 문서의 특정 섹션만 교체/추가
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Task 14 후)
  - **Parallel Group**: Wave 4
  - **Blocks**: [F1-F4]
  - **Blocked By**: [Task 14]

  **References**:
  - `AGENTS.md` (현재 파일) - 기존 구조 확인
  - AGENTS.md `MANDATORY: AGENTS.md 최신화` 섹션 - 업데이트 트리거 및 절차

  **Acceptance Criteria**:
  - [ ] AGENTS.md Generated 날짜 업데이트됨
  - [ ] STRUCTURE에 hwpx-generator 포함, hwpx-converter 없음
  - [ ] WHERE TO LOOK에 hwpx-generator 관련 행 포함

  **QA Scenarios:**
  ```
  Scenario: AGENTS.md 업데이트 검증
    Tool: Bash (grep)
    Steps:
      1. grep -c 'hwpx-generator' AGENTS.md - 3 이상
      2. grep -c 'hwpx-converter' AGENTS.md - 0
    Expected Result: hwpx-generator 3+ 건, hwpx-converter 0건
    Evidence: .sisyphus/evidence/task-15-agents-md.txt
  ```

  **Commit**: YES
  - Message: `docs: update AGENTS.md and README.md for hwpx-generator`
  - Files: `AGENTS.md`, `README.md`
