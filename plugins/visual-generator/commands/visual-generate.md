# Visual Generator Orchestrator

## Overview

입력 문서를 분석하고, 검토하고, XML-tag 프롬프트를 생성한 뒤 렌더링까지 수행한다.

파이프라인:
```
content-organizer -> content-reviewer -> prompt-designer -> renderer-agent
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
    +-- Task(subagent_type="visual-generator:prompt-designer")
    +-- XML-tag 형식으로 생성 지시를 명시
    +-- output: 01_*.md, 02_*.md, prompt_index.md

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

## MUST NOT DO

- 직접 분석/검토/프롬프트 생성/렌더링을 수행하지 않는다
- slide-renderer 스크립트 파이프라인을 변경하지 않는다
