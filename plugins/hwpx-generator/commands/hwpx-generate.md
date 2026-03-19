Orchestrate end-to-end HWPX document generation from user intent and inputs in `$ARGUMENTS`.

## Configuration Options

- `ARGUMENTS`: 사용자 요청 원문. 문서 유형, 목적, 포함할 내용, 산출 경로를 포함한다.
- `reference_hwpx` (optional): 스타일/레이아웃 분석용 레퍼런스 `.hwpx` 경로.
- `template_hwpx` (optional): 사용자 업로드 템플릿 `.hwpx` 경로.
- `content_md` (optional): 마크다운 콘텐츠 파일 경로. 단일 파일 또는 여러 파일 경로 리스트. 제공 시 "마크다운 → 템플릿 채우기" 모드로 진행.
- `images_dir` (optional): 이미지 파일 디렉토리 경로. `content_md` 기반 생성 시 이미지 임베딩에 사용.
- `output_dir` (optional): 결과 폴더. 기본값은 `./output/hwpx/`.
- `auto_mode` (optional): 기본값 `true`.

## Phase 1: 요구사항 파악 (문서 유형, 내용, 양식)

1. Parse `$ARGUMENTS` and normalize requirements.
   - 문서 유형 분류: 공문/보고서/회의록/제안서.
   - 핵심 내용 추출: 제목, 섹션 구조, 필수 문구, 표/수식 포함 여부.
   - 양식 요구 추출: 사용자 템플릿 사용 여부, 레퍼런스 문서 동일 스타일 여부.
   - **MD 채우기 모드 감지**: `content_md`가 제공되면 "마크다운 → 템플릿 채우기" 모드로 분류.
2. Build execution context.
   - 입력 파라미터를 JSON 형태로 정리하여 다음 Phase에 전달.
   - 필수 입력 누락 시 누락 항목만 명확히 요청한다.

## Phase 2: 양식 선택 (사용자 업로드 > 기본 양식 > XML-first)

1. Select format strategy in strict priority order.
   - 1순위: `template_hwpx`가 있으면 사용자 업로드 템플릿 기반.
   - 2순위: 프로젝트 기본 템플릿이 있으면 기본 양식 기반.
   - 3순위: 템플릿이 없으면 XML-first 생성 경로.
   - **MD 채우기 분기**: `content_md` + `template_hwpx` 조합 시 Workflow 7 경로 선택 (md_parser → mapping → xml_writer → zip_surgery → image_embedder).
2. When `reference_hwpx` is provided, analyze before build.
   - Use Task tool with subagent_type="hwpx-generator::hwpx-analyzer"
   - Prompt: "Analyze `{reference_hwpx}` and produce reusable style/table/layout guidance for this request: `$ARGUMENTS`. Output a concise build-ready analysis report."
   - Expected output: 스타일 ID 맵, 표 구조 규칙, 레이아웃 재현 지침.
3. Merge selected format strategy with analysis report (if any) into one build input package.

## Phase 3: 문서 생성 (delegate to hwpx-builder via Task tool)

1. Use Task tool with subagent_type="hwpx-generator::hwpx-builder"
   - Prompt: "Generate a production-ready `.hwpx` using this request `$ARGUMENTS`, selected format strategy (user template > default template > XML-first), and analyzer report if present. Return output path and generation path used."
   - **MD 채우기 모드 시**: hwpx-builder에게 md_parser, xml_writer, image_embedder 사용을 명시적으로 위임. `content_md`와 `images_dir` 파라미터를 전달하여 Workflow 7 실행.
   - 입력 콘텐츠가 Markdown이고 템플릿에 이미 섹션 헤더가 존재하는 경우, Template-Aware Markdown Insertion 절차를 적용하여 헤더 중복을 방지할 것.
   - 마크다운 heading(`#`, `##`, `###`)을 템플릿 sub-header와 매칭하고, 매칭된 heading은 skip하며 body만 해당 위치에 삽입할 것.
   - **XML 생성 규칙 (필수 전달)**: 모든 XML 생성(표, 문단, 불릿 포함)은 반드시 기존 `xml_writer.py`의 `build_table()`, `build_paragraph()` 등을 사용할 것. 에이전트가 직접 XML을 작성하거나 `generate_content.py` 등 자체 스크립트를 생성하는 것은 금지. lxml/ElementTree를 사용한 section XML 직렬화도 금지(개행 삽입으로 한/글에서 파일이 깨짐).
   - Expected output: 생성된 `.hwpx` 파일 경로, 사용된 생성 경로(`hwpx-core`/`hwpx-templates`), 생성 요약.
2. Ensure builder output includes the generated file path under `output_dir`.

## Phase 3.5: 교정 (Proofreading)

1. Run final proofreading script to fix common formatting issues.
   - Bash: `python plugins/hwpx-generator/skills/hwpx-core/scripts/proofread.py "{generated_hwpx_path}"`
   - 이 단계에서는 이중 불릿, 잘못된 줄바꿈, 스타일 미적용 문단 등을 자동으로 교정한다.
## Phase 4: 검증 (validate.py + page_guard.py)

1. Run mandatory structural validation on the generated output.
   - Bash: `python plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py "{generated_hwpx_path}"`
2. When `reference_hwpx` or `template_hwpx` was provided, run page drift guard with appropriate mode.
   - **모드 선택 기준** (Phase 2에서 결정된 워크플로우 유형에 따라):
     | 워크플로우 | page_guard 모드 |
     |------------|-----------------|
     | MD 채우기 (`content_md` 존재) | `--mode template-fill` |
     | XML-first 생성 (템플릿 없음) | 실행하지 않음 (비교 대상 없음) |
     | 스타일 복제 (`reference_hwpx`만 존재) | `--mode default` |
     | 템플릿 소규모 편집 | `--mode default` |
   - MD 채우기 모드 시:
     Bash: `python plugins/hwpx-generator/skills/hwpx-core/scripts/page_guard.py --mode template-fill --reference "{reference_hwpx}" --output "{generated_hwpx_path}"`
   - 스타일 복제/소규모 편집 시:
     Bash: `python plugins/hwpx-generator/skills/hwpx-core/scripts/page_guard.py --reference "{reference_hwpx}" --output "{generated_hwpx_path}"`
   - `page_guard.py`는 문단 수, 표 구조, 텍스트 길이 편차를 검사하여 쪽수 변동 위험을 사전 차단한다.
   - `template-fill` 모드에서는 표 추가를 WARNING으로 보고하고, 기존 표 구조 보존 여부만 검사한다.
3. Handle validation result.
   - PASS (both): Phase 5로 진행.
   - FAIL (validate.py): 검증 오류를 첨부해 Phase 3을 재실행(최대 2회).
   - FAIL (page_guard.py): 원인(길이 과다/구조 변경)을 수정하여 Phase 3을 재실행(최대 2회).
4. Record validation summary for final response.

## Phase 5: 결과 전달

1. Return final delivery package.
   - 최종 `.hwpx` 파일 경로.
   - 검증 결과(PASS/FAIL 및 핵심 메시지).
   - 적용된 양식 경로(사용자 업로드/기본 양식/XML-first).
   - (사용 시) `hwpx-analyzer` 분석 리포트 경로.
2. Provide concise next actions.
   - 필요 시 동일 양식으로 후속 문서 생성 방법 안내.
   - 실패 시 재시도에 필요한 최소 보완 입력 안내.

## MUST DO

- [ ] `$ARGUMENTS`에서 사용자 의도를 먼저 정규화한다.
- [ ] Task tool 기반 위임으로만 분석/생성을 수행한다.
- [ ] 양식 우선순서(사용자 업로드 > 기본 양식 > XML-first)를 지킨다.
- [ ] `validate.py` 검증 통과 전 결과를 완료 처리하지 않는다.
- [ ] 레퍼런스 기반 작업 시 `page_guard.py` 통과 전 결과를 완료 처리하지 않는다.
- [ ] 입력 콘텐츠에 Markdown 서식 기호(`**`, `*`, `~~` 등)가 포함된 경우, HWPX 변환 전 인라인 서식을 multi-run으로 분할하거나 순수 텍스트로 정제한다.

## MUST NOT DO

- [ ] 문서 본문 내용을 오케스트레이터가 직접 생성하지 않는다.
- [ ] 템플릿 우선순서를 임의로 변경하지 않는다.
- [ ] 검증 실패 결과를 숨기거나 무시하지 않는다.
- [ ] `.hwp` 직접 생성을 지원한다고 안내하지 않는다.
- [ ] Markdown 서식 기호(`**`, `*`, `#` 등)를 HWPX 텍스트(`<hp:t>`)에 그대로 포함시키지 않는다.

## Usage Example

### 기본 사용법 (템플릿 + 레퍼런스)

```
@hwpx-generator 다음 ARGUMENTS로 HWPX 문서를 생성해줘.

ARGUMENTS:
- 문서 유형: 보고서
- 목적: 연구개발 주간 진행 보고
- 포함 내용: 개요, 금주 성과, 이슈, 차주 계획
- 양식: 사용자 템플릿 우선
- template_hwpx: ./templates/weekly_report_template.hwpx
- reference_hwpx: ./references/style_reference.hwpx
- output_dir: ./output/hwpx/
```

### 마크다운 채우기 모드 (Workflow 7)

```
@hwpx-generator 다음 ARGUMENTS로 마크다운 콘텐츠를 템플릿에 채워 HWPX 문서를 생성해줘.

ARGUMENTS:
- 문서 유형: 연구계획서
- 목적: 정부 과제 제출용 연구계획서
- 양식: 사용자 템플릿 기반 마크다운 채우기
- template_hwpx: ./양식.hwpx
- content_md: ./3_비전_및_목표.md, ./4_핵심_연구내용.md
- images_dir: ./images/
- output_dir: ./output/hwpx/
```
