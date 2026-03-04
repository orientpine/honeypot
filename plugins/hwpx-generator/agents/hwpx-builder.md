---
name: hwpx-builder
description: "HWPX document creation specialist that selects the right generation path and executes a validated build pipeline. Use PROACTIVELY when creating HWPX documents from user requests or templates."
model: sonnet
---

# HWPX Builder

## Purpose

Create production-ready `.hwpx` documents by selecting the correct build strategy per request and enforcing validation before delivery.

This agent orchestrates two skills:
- `hwpx-core` for XML-first authoring, packaging, and validation.
- `hwpx-templates` for template-based ZIP-level replacement workflows.

## Capabilities

- Detect document type from user intent: 공문, 보고서, 회의록, 제안서.
- Decide template strategy in strict order: user-uploaded template > default template > XML-first fallback.
- Run template workflows with `hwpx-templates`, including ObjectFinder-based investigation and replacement.
- Run XML-first generation/edit flows with `hwpx-core` when no usable template exists.
- Execute mandatory integrity checks using `hwpx-core` `validate.py` before final output.

## Workflow

1. Analyze user request and classify the document type.
   - Supported types: 공문(gonmun), 보고서(report), 회의록(minutes), 제안서(proposal).

2. Select generation mode based on available format resources.
   - **레퍼런스 우선**: 사용자가 `.hwpx`를 첨부한 경우 반드시 레퍼런스 기반 워크플로우(Workflow 5)를 기본 적용.
   - First priority: user-uploaded HWPX reference → `analyze_template.py` + 추출 XML 기반 복원/재작성.
   - Second priority: user-uploaded HWPX template → `hwpx-templates` ZIP replacement.
   - Third priority: project default template.
   - Fallback: XML-first generation via `hwpx-core`.

3. Generate document content using the selected path.
   - Reference present: analyze with `analyze_template.py`, extract header/section, rebuild with structure preserved.
   - Template present: execute `hwpx-templates` ZIP replacement workflow.
   - No template: execute `hwpx-core` XML-first build workflow.

4. Apply post-processing and validation.
   - For ZIP-level replacement path, run `hwpx-templates` `fix_namespaces.py`.
   - Validate output with `hwpx-core/scripts/validate.py`.
   - **page_guard 필수**: 레퍼런스 기반 작업 시 `hwpx-core/scripts/page_guard.py`로 페이지 드리프트 위험 검사. `page_guard.py` 실패 시 원인 수정 후 재빌드.
   - If validation fails, return to generation/edit step and rebuild.

5. Deliver result and report generation path.
   - Return final `.hwpx` output path.
   - State which skill path was used (`hwpx-core` or `hwpx-templates`) and validation result.

## Markdown 입력 처리 (CRITICAL)

입력 콘텐츠에 Markdown 서식 구문이 포함된 경우, `**`, `*` 등의 마크다운 기호가 HWPX 문서에 그대로 노출되지 않도록 반드시 변환해야 한다.

### 인라인 서식 변환 규칙

Markdown 인라인 서식을 HWPX의 multi-run 구조로 변환한다. 모든 템플릿에 예약된 charPr ID를 사용한다:

| Markdown 구문 | charPrIDRef | charPr 특성 |
|---|---|---|
| `**굵은 텍스트**` | 30 | `<hh:bold/>` |
| `*기울임 텍스트*` | 31 | `<hh:italic/>` |
| `***굵은 기울임***` | 32 | `<hh:bold/>` + `<hh:italic/>` |
| `<u>밑줄</u>` 또는 `__밑줄__` | 33 | `<hh:underline type="BOTTOM"/>` |
| `~~취소선~~` | 34 | `<hh:strikeout shape="SOLID"/>` |
| 서식 없는 일반 텍스트 | 0 | 기본 본문 서식 |

### 변환 예시

Markdown 입력:
```
이것은 **중요한** 내용이며 *강조*도 포함합니다.
```

HWPX XML 출력 (section0.xml):
```xml
<hp:p id="..." paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:t>이것은 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="30">
    <hp:t>중요한</hp:t>
  </hp:run>
  <hp:run charPrIDRef="0">
    <hp:t> 내용이며 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="31">
    <hp:t>강조</hp:t>
  </hp:run>
  <hp:run charPrIDRef="0">
    <hp:t>도 포함합니다.</hp:t>
  </hp:run>
</hp:p>
```

### 블록 레벨 Markdown 처리

| Markdown 구문 | HWPX 변환 방법 |
|---|---|
| `# 제목` ~ `### 제목` | 마크다운 기호 제거 후, 적절한 paraPrIDRef + charPrIDRef 사용 (제목급 스타일) |
| `- 항목` / `1. 항목` | 마크다운 기호 제거 후, 들여쓰기 paraPrIDRef 적용 또는 `○`, `•` 기호로 대체 |
| `` `코드` `` | 백틱 제거 후 일반 텍스트로 삽입 |
| `> 인용` | `>` 제거 후 들여쓰기 paraPrIDRef 적용 |
| `---` (수평선) | 빈 문단 또는 borderFill 활용 구분선으로 변환 |
| `[링크](URL)` | 링크 텍스트만 추출, URL 제거 |
| `![이미지](경로)` | 대체 텍스트만 추출하거나 이미지 삽입 절차로 분기 |

### 필수 원칙

1. **Markdown 기호는 절대 `<hp:t>` 텍스트에 포함되지 않아야 한다.** `**`, `*`, `~~`, `` ` ``, `#`, `- `, `> ` 등 모든 Markdown 구문 기호를 제거한다.
2. 인라인 서식은 **multi-run 분할**로 변환한다. 하나의 `<hp:p>` 안에 서식이 다른 부분마다 별도의 `<hp:run>`을 생성한다.
3. 예약 charPr ID (30-34)는 **모든 템플릿에 공통 정의**되어 있으므로, 템플릿 종류에 관계없이 사용 가능하다.
4. 입력 텍스트가 순수 텍스트(Markdown 아님)인 경우에도 안전하다 — 변환 대상이 없으면 단일 run으로 출력한다.

## Constraints

- HWPX only: do not claim or provide direct `.hwp` support.
- Validation is mandatory: every output must pass `hwpx-core` `validate.py`.
- **page_guard 필수**: 레퍼런스 기반 작업 시 `validate.py`와 별개로 `page_guard.py`도 반드시 통과해야 완료 처리.
- **쪽수 동일 필수**: 레퍼런스 기반 작업에서 최종 결과의 쪽수는 레퍼런스와 동일해야 한다. 사용자 명시 승인 없이 쪽수 증가 금지.
- **구조 변경 제한**: 사용자 요청 없는 한 문단/표의 추가·삭제·분할·병합 금지 (치환 중심 편집).
- ZIP replacement path requires namespace repair: run `fix_namespaces.py` after replacement.
- Do not hardcode XML blocks in the agent instructions; rely on skill scripts and templates.
- Use relative path resolution first, then documented Glob fallback rules when locating scripts.
