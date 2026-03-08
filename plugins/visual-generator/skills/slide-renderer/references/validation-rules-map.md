# v1.9.0~v1.11.0 Validation Rules — XML-Tag Mapping

## Overview

This document maps validation rules accumulated from v1.9.0 to v1.11.0 to the XML-tag (v2.0.0+) architecture. Each rule is cross-referenced with its original context, XML-tag equivalent, and detection methodology.

## Orphan/Ghost Reference Detection

**Orphan Item**: A `key: "value"` pair in `<text_to_render>` whose value string does NOT appear quoted in `<layout>`. This causes content to be defined but never placed.

**Ghost Reference**: A quoted string in `<layout>` that does NOT correspond to any value in `<text_to_render>`. This causes layout instructions to reference non-existent content.

**Detection Algorithm**:
1. Extract all values from `<text_to_render>` (right side of `key: "value"`)
2. Extract all quoted strings from `<layout>` (text within double quotes)
3. Cross-match bidirectionally:
   - For each value in `<text_to_render>`, verify it appears quoted in `<layout>` → Orphan check
   - For each quoted string in `<layout>`, verify it exists in `<text_to_render>` → Ghost check
4. PASS: 100% bidirectional match. FAIL: Any orphan or ghost detected.

---

## Rule 1: Double-Rendering Prevention (번호 참조 체계)

| Field | Content |
|-------|---------|
| **Rule Name** | Double-Rendering Prevention / Reference Number System |
| **Original Context** | v1.9.0 — `<text_to_render>` values referenced by index numbers in `<layout>` instead of exact strings, causing text to render twice |
| **XML-tag Equivalent** | `<layout>` must ALWAYS quote exact values from `<text_to_render>` using double quotes. Index-based references (e.g., "Item 1", "첫 번째 항목") are FORBIDDEN. |
| **Detection Method** | Scan `<layout>` for patterns: numbered references like "Item 1", "첫 번째 항목", "1번", "2번" or ordinal patterns. If found, FAIL. Verify all layout references use exact quoted strings from `<text_to_render>`. |

**PASS Example:**
```xml
<text_to_render>
  title: "AI 불량 검출 시스템"
  metric1: "검출률 98.5%"
  metric2: "처리 속도 0.3초"
</text_to_render>

<layout>
  top_center: "AI 불량 검출 시스템"
  left_box: "검출률 98.5%"
  right_box: "처리 속도 0.3초"
</layout>
```

**FAIL Example:**
```xml
<text_to_render>
  title: "AI 불량 검출 시스템"
  metric1: "검출률 98.5%"
  metric2: "처리 속도 0.3초"
</text_to_render>

<layout>
  top_center: "첫 번째 항목"
  left_box: "Item 1"
  right_box: "Item 2"
</layout>
```

---

## Rule 2: Seminar Theme Scene-ification Prevention (테마 라벨 탈맥락화)

| Field | Content |
|-------|---------|
| **Rule Name** | Seminar Theme Scene-ification Prevention / Meta-Label decontextualization |
| **Original Context** | v1.9.0 — Abstract concept keywords (e.g., "AI 분석", "데이터 흐름") entered directly into `<text_to_render>` and rendered as literal slide text, breaking semantic context |
| **XML-tag Equivalent** | `<text_to_render>` values must be CONCRETE, displayable text with full context. Abstract concept labels or meta-labels are FORBIDDEN. Values must be complete subject-predicate phrases. |
| **Detection Method** | Scan `<text_to_render>` values for: (1) floating concept words without context ("혁신", "효율성", "AI 분석"), (2) meta-labels ("Data:", "Note:", "Label:", "Key:", "Item:"), (3) incomplete noun phrases. If found, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  benefit1: "AI가 실시간으로 불량품을 검출합니다"
  benefit2: "데이터 기반 의사결정으로 비용을 30% 절감합니다"
  process: "카메라 → AI 분석 → 자동 분류"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  concept1: "AI 분석"
  concept2: "데이터 흐름"
  concept3: "혁신"
  meta: "Data: 불량률"
</text_to_render>
```

---

## Rule 3: Axis-Based Layout Space-Meaning Verification (축 기반 레이아웃 공간-의미 역검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Axis-Based Layout Space-Meaning Verification |
| **Original Context** | v1.9.0 — Axis-based layouts (x/y coordinates) where spatial positioning contradicts semantic hierarchy (e.g., primary concept at bottom, secondary at top) |
| **XML-tag Equivalent** | In `<layout>`, axis-based arrangements must follow semantic hierarchy: top/left = primary/cause, bottom/right = secondary/effect. Spatial position must reinforce meaning. |
| **Detection Method** | For axis-based layouts, verify: (1) top/upper positions contain primary concepts, (2) bottom/lower positions contain secondary/supporting concepts, (3) left positions precede right positions in causal chains. If spatial order contradicts semantic order, FAIL. |

**PASS Example:**
```xml
<layout>
  top_left: "원인: 공정 온도 편차"
  top_right: "결과: 제품 불량"
  bottom_left: "해결책: 온도 제어 시스템"
  bottom_right: "효과: 불량률 50% 감소"
</layout>
```

**FAIL Example:**
```xml
<layout>
  bottom_left: "원인: 공정 온도 편차"
  bottom_right: "결과: 제품 불량"
  top_left: "해결책: 온도 제어 시스템"
  top_right: "효과: 불량률 50% 감소"
</layout>
```

---

## Rule 4: CONTENT↔Placement Full Correspondence (전수 대응 원칙)

| Field | Content |
|-------|---------|
| **Rule Name** | CONTENT↔Placement Full Correspondence Principle |
| **Original Context** | v1.10.0 — Every item in `<text_to_render>` must receive explicit placement instruction in `<layout>`. No orphan items allowed. |
| **XML-tag Equivalent** | Count of `key: "value"` pairs in `<text_to_render>` MUST EQUAL count of quoted references in `<layout>`. Every value must be placed; every placement must reference defined content. |
| **Detection Method** | (1) Count all `key: "value"` pairs in `<text_to_render>`. (2) Count all quoted strings in `<layout>`. (3) Verify counts match. (4) Cross-match each value to its layout reference. If count mismatch or any value unplaced, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  title: "생산 효율성 분석"
  metric1: "월간 생산량 15,000개"
  metric2: "불량률 2.3%"
  metric3: "가동률 94.5%"
</text_to_render>

<layout>
  header: "생산 효율성 분석"
  box1: "월간 생산량 15,000개"
  box2: "불량률 2.3%"
  box3: "가동률 94.5%"
</layout>
```

**FAIL Example:**
```xml
<text_to_render>
  title: "생산 효율성 분석"
  metric1: "월간 생산량 15,000개"
  metric2: "불량률 2.3%"
  metric3: "가동률 94.5%"
  metric4: "에너지 소비 12kWh"
</text_to_render>

<layout>
  header: "생산 효율성 분석"
  box1: "월간 생산량 15,000개"
  box2: "불량률 2.3%"
  box3: "가동률 94.5%"
</layout>
```

---

## Rule 5: Orphan Item Prevention (고아 항목 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Orphan Item Prevention |
| **Original Context** | v1.10.0 — Text defined in `<text_to_render>` but not referenced in `<layout>` placement instructions, leaving content unused |
| **XML-tag Equivalent** | Every `key: "value"` in `<text_to_render>` must appear as a quoted reference in `<layout>`. Orphan items (defined but unplaced) are FORBIDDEN. |
| **Detection Method** | Extract all values from `<text_to_render>`. For each value, search `<layout>` for exact quoted match. If any value has no match in `<layout>`, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  stat1: "매출 증가율 25%"
  stat2: "고객 만족도 4.8/5.0"
</text_to_render>

<layout>
  left: "매출 증가율 25%"
  right: "고객 만족도 4.8/5.0"
</layout>
```

**FAIL Example:**
```xml
<text_to_render>
  stat1: "매출 증가율 25%"
  stat2: "고객 만족도 4.8/5.0"
  stat3: "시장 점유율 18%"
</text_to_render>

<layout>
  left: "매출 증가율 25%"
  right: "고객 만족도 4.8/5.0"
</layout>
```

---

## Rule 6: Data Duplication Prevention (Data 중복 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Data Duplication Prevention |
| **Original Context** | v1.10.0 — Same numerical value or phrase appears multiple times across `<text_to_render>`, `<scene>`, or `<layout>`, causing redundancy and confusion |
| **XML-tag Equivalent** | Each unique value appears exactly once across all XML tags. `<scene>` describes visual elements; `<text_to_render>` lists displayable text; `<layout>` places text. No value should appear in multiple tags. |
| **Detection Method** | Collect all values from `<text_to_render>`, `<scene>`, and `<layout>`. Check for duplicates. If any value appears more than once across tags, FAIL. |

**PASS Example:**
```xml
<scene>
  background: "공장 생산 라인"
  elements: "로봇 팔, 컨베이어 벨트"
</scene>

<text_to_render>
  title: "자동화 생산 시스템"
  metric: "생산 속도 50% 증가"
</text_to_render>

<layout>
  top: "자동화 생산 시스템"
  bottom: "생산 속도 50% 증가"
</layout>
```

**FAIL Example:**
```xml
<scene>
  background: "공장 생산 라인"
  elements: "생산 속도 50% 증가"
</scene>

<text_to_render>
  title: "자동화 생산 시스템"
  metric: "생산 속도 50% 증가"
</text_to_render>

<layout>
  top: "자동화 생산 시스템"
  bottom: "생산 속도 50% 증가"
</layout>
```

---

## Rule 7: Concept Keyword Contamination Prevention (개념 키워드 혼입 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Concept Keyword Contamination Prevention |
| **Original Context** | v1.10.0 — Pure abstract concept words (e.g., "혁신", "효율성", "지속성") appear standalone in `<text_to_render>` without concrete context or supporting details |
| **XML-tag Equivalent** | `<text_to_render>` values must be concrete, contextual phrases. Floating concept words without supporting context are FORBIDDEN. Each value must be displayable and meaningful on its own. |
| **Detection Method** | Scan `<text_to_render>` values for: (1) single-word abstract nouns ("혁신", "효율성", "지속성", "가치"), (2) concept words without predicates or context. If found, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  innovation: "AI 기술로 생산 공정을 혁신했습니다"
  efficiency: "에너지 효율성을 35% 개선했습니다"
  sustainability: "탄소 배출을 연 50톤 감축했습니다"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  concept1: "혁신"
  concept2: "효율성"
  concept3: "지속성"
  concept4: "가치"
</text_to_render>
```

---

## Rule 8: Reference Number System Validation (번호 참조 체계 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Reference Number System Validation |
| **Original Context** | v1.10.1 — Explicit validation added to renderer-agent to detect index-based references in `<layout>` that should use exact string quotes instead |
| **XML-tag Equivalent** | `<layout>` must use exact quoted strings from `<text_to_render>`, never index numbers or ordinal references. Patterns like "1번", "2번", "첫 번째", "두 번째" are FORBIDDEN. |
| **Detection Method** | Scan `<layout>` for: (1) ordinal patterns ("첫 번째", "두 번째", "세 번째"), (2) numbered patterns ("1번", "2번", "3번"), (3) generic item references ("Item 1", "Item 2"). If found, FAIL. |

**PASS Example:**
```xml
<layout>
  position1: "AI 기술 도입으로 비용 30% 절감"
  position2: "자동화로 생산 속도 2배 증가"
  position3: "품질 관리 시간 50% 단축"
</layout>
```

**FAIL Example:**
```xml
<layout>
  position1: "첫 번째 항목"
  position2: "두 번째 항목"
  position3: "세 번째 항목"
</layout>
```

---

## Rule 9: Seminar Label Decontextualization Validation (세미나 라벨 탈맥락화 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Seminar Label Decontextualization Validation |
| **Original Context** | v1.10.1 — Explicit check added to renderer-agent to detect abstract/meta labels in seminar theme `<text_to_render>` that lack concrete context |
| **XML-tag Equivalent** | For seminar themes, `<text_to_render>` values must be concrete, actionable statements. Meta-labels ("Data:", "Note:", "Label:", "Key:", "Item:") and floating concept words are FORBIDDEN. |
| **Detection Method** | Scan `<text_to_render>` for: (1) meta-label prefixes ("Data:", "Note:", "Label:", "Key:", "Item:"), (2) abstract concept words without context, (3) incomplete phrases. If found in seminar theme, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  insight1: "AI 기술이 제조업 혁신을 주도하고 있습니다"
  insight2: "데이터 기반 의사결정으로 경쟁력을 확보합니다"
  insight3: "자동화 투자가 ROI 200%를 달성했습니다"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  item1: "Data: AI 기술"
  item2: "Note: 제조업 혁신"
  item3: "Key: 경쟁력"
  item4: "Label: 자동화"
</text_to_render>
```

---

## Rule 10: Orphan Item Explicit Check (고아 항목 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Orphan Item Explicit Check |
| **Original Context** | v1.10.1 — Explicit count-match check added to renderer-agent to verify every `<text_to_render>` item has corresponding `<layout>` placement |
| **XML-tag Equivalent** | Count of `key: "value"` pairs in `<text_to_render>` must exactly match count of quoted references in `<layout>`. Bidirectional matching required: no orphans, no ghosts. |
| **Detection Method** | (1) Count all `key: "value"` pairs in `<text_to_render>`. (2) Count all quoted strings in `<layout>`. (3) If counts differ, FAIL. (4) Cross-match each value to layout reference. If any mismatch, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  benefit1: "생산성 40% 향상"
  benefit2: "비용 절감 25%"
  benefit3: "품질 개선 99.2%"
</text_to_render>

<layout>
  metric1: "생산성 40% 향상"
  metric2: "비용 절감 25%"
  metric3: "품질 개선 99.2%"
</layout>
```

**FAIL Example:**
```xml
<text_to_render>
  benefit1: "생산성 40% 향상"
  benefit2: "비용 절감 25%"
  benefit3: "품질 개선 99.2%"
  benefit4: "고객 만족도 4.9/5.0"
</text_to_render>

<layout>
  metric1: "생산성 40% 향상"
  metric2: "비용 절감 25%"
  metric3: "품질 개선 99.2%"
</layout>
```

---

## Rule 11: Meta-Label Prohibition (메타라벨 금지)

| Field | Content |
|-------|---------|
| **Rule Name** | Meta-Label Prohibition |
| **Original Context** | v1.11.0 — `<text_to_render>` values must not start with structural meta-labels like "Data:", "Note:", "Label:", "Key:", "Item:" — these are metadata, not content |
| **XML-tag Equivalent** | `<text_to_render>` values must be pure content without meta-label prefixes. Structural labels belong in XML tag names, not in values. |
| **Detection Method** | Scan all `<text_to_render>` values for prefixes: "Data:", "Note:", "Label:", "Key:", "Item:", "Info:", "Tip:", "Alert:". If any found, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  stat1: "월간 매출 5억 원"
  stat2: "고객 수 12,000명"
  stat3: "시장 점유율 18%"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  stat1: "Data: 월간 매출 5억 원"
  stat2: "Note: 고객 수 12,000명"
  stat3: "Key: 시장 점유율 18%"
</text_to_render>
```

---

## Rule 12: Subject-Predicate Sentence Format Enforcement (조사문 형식 강제)

| Field | Content |
|-------|---------|
| **Rule Name** | Subject-Predicate Sentence Format Enforcement |
| **Original Context** | v1.11.0 — `<text_to_render>` values should be complete subject-predicate phrases, not floating nouns or incomplete fragments |
| **XML-tag Equivalent** | `<text_to_render>` values must be complete, displayable sentences or phrases with subject and predicate. Floating nouns or incomplete fragments are FORBIDDEN. |
| **Detection Method** | Analyze each `<text_to_render>` value: (1) Check for subject (주어) and predicate (술어), (2) Verify it forms a complete, meaningful phrase, (3) Reject floating nouns or fragments. If incomplete, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  statement1: "AI 시스템이 불량품을 자동으로 검출합니다"
  statement2: "생산 속도가 시간당 500개에서 750개로 증가했습니다"
  statement3: "품질 관리 비용이 연 2억 원 절감되었습니다"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  fragment1: "불량 검출"
  fragment2: "생산 속도 증가"
  fragment3: "비용 절감"
  noun: "자동화"
</text_to_render>
```

---

## Rule 13: Circle-Number Marker Prohibition (원 번호 마커 금지)

| Field | Content |
|-------|---------|
| **Rule Name** | Circle-Number Marker Prohibition |
| **Original Context** | v1.11.0 — Circle-number characters (①②③④⑤⑥⑦⑧⑨⑩) are forbidden in `<text_to_render>` values as they are rendering artifacts, not content |
| **XML-tag Equivalent** | `<text_to_render>` values must not contain circle-number characters (①②③④⑤⑥⑦⑧⑨⑩). Use plain text or Arabic numerals instead. |
| **Detection Method** | Scan all `<text_to_render>` values for Unicode circle-number characters (U+2460–U+2473). If any found, FAIL. |

**PASS Example:**
```xml
<text_to_render>
  step1: "1단계: 데이터 수집"
  step2: "2단계: AI 분석"
  step3: "3단계: 결과 도출"
</text_to_render>
```

**FAIL Example:**
```xml
<text_to_render>
  step1: "① 데이터 수집"
  step2: "② AI 분석"
  step3: "③ 결과 도출"
</text_to_render>
```

---

## Summary Table

| Rule # | Rule Name | v1.X.X | Key Validation |
|--------|-----------|--------|-----------------|
| 1 | Double-Rendering Prevention | v1.9.0 | No index-based references in `<layout>` |
| 2 | Seminar Theme Scene-ification Prevention | v1.9.0 | No abstract concept labels in `<text_to_render>` |
| 3 | Axis-Based Layout Space-Meaning Verification | v1.9.0 | Spatial hierarchy matches semantic hierarchy |
| 4 | CONTENT↔Placement Full Correspondence | v1.10.0 | Count match: `<text_to_render>` items = `<layout>` references |
| 5 | Orphan Item Prevention | v1.10.0 | Every `<text_to_render>` value appears in `<layout>` |
| 6 | Data Duplication Prevention | v1.10.0 | No value appears in multiple tags |
| 7 | Concept Keyword Contamination Prevention | v1.10.0 | No floating concept words in `<text_to_render>` |
| 8 | Reference Number System Validation | v1.10.1 | Explicit check for index-based references |
| 9 | Seminar Label Decontextualization Validation | v1.10.1 | Explicit check for meta-labels in seminar themes |
| 10 | Orphan Item Explicit Check | v1.10.1 | Explicit count-match verification |
| 11 | Meta-Label Prohibition | v1.11.0 | No "Data:", "Note:", "Label:" prefixes |
| 12 | Subject-Predicate Sentence Format Enforcement | v1.11.0 | Complete phrases, not floating nouns |
| 13 | Circle-Number Marker Prohibition | v1.11.0 | No ①②③④⑤ characters |

---

## Integration with renderer-agent.md

These 13 rules complement the 8 core XML validation checks and 3 additional checks in `renderer-agent.md`:

**Core XML Checks (8):**
1. 5 tags exist: `<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`
2. `<text_to_render>` has `key: "value"` format
3. `<layout>` quotes `<text_to_render>` values in double quotes
4. No numbered list patterns (1., 2., -)
5. No pt/px units
6. No markdown formatting (**, *, #)
7. Theme-specific item count limits respected
8. `<typography>` contains Korean font hint

**Additional Checks (3):**
- Hallucination URL pattern detection
- Placeholder detection ([내용], {TEXT}, etc.)
- Language mixing detection

**This Document (13 Rules):**
- Semantic validation (Rules 1–7, 11–13)
- Structural validation (Rules 4–5, 8–10)
- Context validation (Rules 2, 9)
- Spatial validation (Rule 3)
- Duplication validation (Rule 6)

Together, these 24 validation points (8 + 3 + 13) form the comprehensive validation framework for v2.0.0+ XML-tag architecture.
