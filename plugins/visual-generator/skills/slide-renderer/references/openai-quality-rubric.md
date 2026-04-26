# OpenAI gpt-image-2 Quality Rubric

**Purpose**: gpt-image-2 생성 이미지의 5D 품질 평가 기준. Gemini 5D와 필드명·임계값 byte-identical 유지.
**Evaluation Model**: gpt-5.5 (Responses API, Structured Outputs json_schema strict)

---

## 5 Dimensions (각 0-10점)

| 필드명 | 설명 | Veto |
|--------|------|:----:|
| `korean_text_readability` | 한글 자모 완전성, 폰트 명료성, 대비 | 5.0 |
| `korean_hallucination_detection` | CONTENT 외 한글 생성 여부 (10=깨끗, 0=심각) | 5.0 |
| `content_reference_accuracy` | CONTENT key:value 충실 렌더링 | — |
| `layout_suitability` | 공간 구성, 시각적 위계 | — |
| `color_palette_compliance` | CONFIGURATION 색상 준수 (#1E3A5F 등) | — |
| `overall_score` | 5차원 가중 평균 | — |
| `feedback` | 품질 보정 힌트 ≤200자 | — |

## PASS Criteria (Gemini와 동일)
```
PASS: overall_score >= 7.0 AND korean_text_readability >= 5.0 AND korean_hallucination_detection >= 5.0
```
veto: 한글 차원 하나라도 5.0 미만 → 평균 무관 자동 FAIL.

## Concept Theme Exemption
prompt_text에 "concept" / "zero text rendering" / "zero-text rendering" 포함 시 한글 평가 면제:
`korean_text_readability = 10.0`, `korean_hallucination_detection = 10.0` 자동 설정.

## Structured Outputs Schema (json_schema strict)
6개 숫자 필드 + feedback 문자열, 모두 required, additionalProperties: false.
```json
{"type":"object","properties":{"korean_text_readability":{"type":"number"},"korean_hallucination_detection":{"type":"number"},"content_reference_accuracy":{"type":"number"},"layout_suitability":{"type":"number"},"color_palette_compliance":{"type":"number"},"overall_score":{"type":"number"},"feedback":{"type":"string"}},"required":["korean_text_readability","korean_hallucination_detection","content_reference_accuracy","layout_suitability","color_palette_compliance","overall_score","feedback"],"additionalProperties":false}
```

## Mitigation Notes
- `detail: "original"` 사용 → 한글 보존 (저해상도 압축 방지)
- hex 코드 렌더링 금지 SYSTEM_INSTRUCTION 명시
- Non-Latin 주의: gpt-image-2 한글 렌더링 불안정 → veto로 재생성 강제
