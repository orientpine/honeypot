Orchestrate end-to-end HWPX document generation from user intent and inputs in `$ARGUMENTS`.

## Configuration Options

- `ARGUMENTS`: 사용자 요청 원문. 문서 유형, 목적, 포함할 내용, 산출 경로를 포함한다.
- `reference_hwpx` (optional): 스타일/레이아웃 분석용 레퍼런스 `.hwpx` 경로.
- `template_hwpx` (optional): 사용자 업로드 템플릿 `.hwpx` 경로.
- `output_dir` (optional): 결과 폴더. 기본값은 `./output/hwpx/`.
- `auto_mode` (optional): 기본값 `true`.

## Phase 1: 요구사항 파악 (문서 유형, 내용, 양식)

1. Parse `$ARGUMENTS` and normalize requirements.
   - 문서 유형 분류: 공문/보고서/회의록/제안서/수학문제지.
   - 핵심 내용 추출: 제목, 섹션 구조, 필수 문구, 표/수식 포함 여부.
   - 양식 요구 추출: 사용자 템플릿 사용 여부, 레퍼런스 문서 동일 스타일 여부.
2. Build execution context.
   - 입력 파라미터를 JSON 형태로 정리하여 다음 Phase에 전달.
   - 필수 입력 누락 시 누락 항목만 명확히 요청한다.

## Phase 2: 양식 선택 (사용자 업로드 > 기본 양식 > XML-first)

1. Select format strategy in strict priority order.
   - 1순위: `template_hwpx`가 있으면 사용자 업로드 템플릿 기반.
   - 2순위: 프로젝트 기본 템플릿이 있으면 기본 양식 기반.
   - 3순위: 템플릿이 없으면 XML-first 생성 경로.
2. When `reference_hwpx` is provided, analyze before build.
   - Use Task tool with subagent_type="hwpx-generator::hwpx-analyzer"
   - Prompt: "Analyze `{reference_hwpx}` and produce reusable style/table/layout guidance for this request: `$ARGUMENTS`. Output a concise build-ready analysis report."
   - Expected output: 스타일 ID 맵, 표 구조 규칙, 레이아웃 재현 지침.
3. Merge selected format strategy with analysis report (if any) into one build input package.

## Phase 3: 문서 생성 (delegate to hwpx-builder via Task tool)

1. Use Task tool with subagent_type="hwpx-generator::hwpx-builder"
   - Prompt: "Generate a production-ready `.hwpx` using this request `$ARGUMENTS`, selected format strategy (user template > default template > XML-first), and analyzer report if present. Return output path and generation path used."
   - Expected output: 생성된 `.hwpx` 파일 경로, 사용된 생성 경로(`hwpx-core`/`hwpx-templates`/`hwpx-math`), 생성 요약.
2. Ensure builder output includes the generated file path under `output_dir`.

## Phase 4: 검증 (validate.py)

1. Run mandatory validation on the generated output.
   - Bash: `python plugins/hwpx-generator/skills/hwpx-core/scripts/validate.py --input "{generated_hwpx_path}"`
2. Handle validation result.
   - PASS: Phase 5로 진행.
   - FAIL: 검증 오류를 첨부해 Phase 3을 재실행(최대 2회).
3. Record validation summary for final response.

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

## MUST NOT DO

- [ ] 문서 본문 내용을 오케스트레이터가 직접 생성하지 않는다.
- [ ] 템플릿 우선순서를 임의로 변경하지 않는다.
- [ ] 검증 실패 결과를 숨기거나 무시하지 않는다.
- [ ] `.hwp` 직접 생성을 지원한다고 안내하지 않는다.

## Usage Example

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
