# Visual Generator Orchestrator

## Overview

입력 문서를 분석하고, 검토하고, XML-tag 프롬프트를 생성한 뒤 렌더링까지 수행한다.

파이프라인:
```
content-organizer -> content-reviewer -> prompt-designer -> prompt-validator -> renderer-agent
```

## Inputs

| 필드 | 설명 | 필수 |
|------|------|:----:|
| `input_document` | 입력 문서 경로 | ✓ |
| `mood` | 무드 | - |
| `layout` | 레이아웃 | - |
| `theme` | 테마 | - |
| `output_folder` | 출력 폴더 | ✓ |
| `auto_mode` | 자동 실행 | - |

## Workflow

```
[Phase 0]
    +-- Bash: mkdir -p {output_folder}/analysis {output_folder}/prompts {output_folder}/images {output_folder}/reports

[Phase 1: content-organizer]
    +-- Task(subagent_type="visual-generator:content-organizer")
    +-- output: concepts.md, slide_plan.md, theme_recommendation.md

[Phase 2: content-reviewer]
    +-- Task(subagent_type="visual-generator:content-reviewer")
    +-- output: review_result.md, concepts_revised.md(optional)

[Phase 3: prompt-designer]
    +-- 슬라이드 반복 루프 (slide_plan.md의 각 슬라이드에 대해):
        +-- 첫 번째 슬라이드(slide_index=0, is_first_slide=true):
            +-- Task(subagent_type="visual-generator:prompt-designer")
            +-- 파라미터: slide_plan, concepts, theme, layout, style_sheet_mode="create", output_path
            +-- prompt-designer가 {output_path}/style_sheet.md를 생성
        +-- 두 번째 슬라이드부터(is_first_slide=false):
            +-- Task(subagent_type="visual-generator:prompt-designer")
            +-- 파라미터: slide_plan, concepts, theme, layout, style_sheet_mode="follow", style_sheet_path="{output_path}/style_sheet.md"
            +-- prompt-designer가 style_sheet.md를 읽고 동일 팔레트/스타일 적용
    +-- output: 01_*.md, 02_*.md, prompt_index.md, style_sheet.md

[Phase 3.5: prompt-validator]
    +-- Task(subagent_type="visual-generator:prompt-validator")
    +-- REJECT 시 prompt-designer 재실행 (최대 2회)
    +-- REJECT 사유를 재호출 프롬프트에 포함
    +-- output: validation_result.md

[Phase 4: renderer-agent]
    +-- Task(subagent_type="visual-generator:renderer-agent")
    +-- XML-tag 검증 수행 지시를 명시
    +-- output: 01_*.png, generation_report.md

[Phase 5]
    +-- execution_report.md 생성
```

## MUST DO

- Phase 3 호출 시 XML-tag 형식 생성을 명시한다
- Phase 4 호출 시 XML-tag 검증 수행을 명시한다
- 실패 시 보고서에 단계별 사유를 남긴다
- Phase 3.5 호출 시 scene-richness-spec.md, validation-rules-map.md, korean-typography-spec.md 준수 확인을 명시한다
- REJECT 사유를 prompt-designer 재호출 프롬프트에 포함한다
- Phase 3 호출 시 첫 번째 슬라이드 여부(is_first_slide)를 판별하여 style_sheet_mode를 "create" 또는 "follow"로 전달한다
- 두 번째 슬라이드부터 style_sheet_path를 prompt-designer에 전달하여 슬라이드 간 팔레트 일관성을 보장한다

## MUST NOT DO

- 직접 분석/검토/프롬프트 생성/렌더링을 수행하지 않는다
- slide-renderer 스크립트 파이프라인을 변경하지 않는다
