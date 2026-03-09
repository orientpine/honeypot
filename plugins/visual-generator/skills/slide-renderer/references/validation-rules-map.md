# v1.9.0~v1.11.0 Validation Rules — XML-Tag Mapping

## Overview

This document maps validation rules accumulated from v1.9.0 to v1.11.0 to the 4-block section architecture (v2.0.0+). Each rule is cross-referenced with its original context, section equivalent, and detection methodology.

## Orphan/Ghost Reference Detection

**Orphan Item**: A `key: "value"` pair in CONTENT section whose value string does NOT appear quoted in Content Placement section. This causes content to be defined but never placed.

**Ghost Reference**: A quoted string in Content Placement section that does NOT correspond to any value in CONTENT section. This causes layout instructions to reference non-existent content.

**Detection Algorithm**:
1. Extract all values from CONTENT section (right side of `key: "value"`)
2. Extract all quoted strings from Content Placement section (text within double quotes)
3. Cross-match bidirectionally:
    - For each value in CONTENT, verify it appears quoted in Content Placement → Orphan check
    - For each quoted string in Content Placement, verify it exists in CONTENT → Ghost check
4. PASS: 100% bidirectional match. FAIL: Any orphan or ghost detected.

---

## Rule 1: Double-Rendering Prevention (번호 참조 체계)

| Field | Content |
|-------|---------|
| **Rule Name** | Double-Rendering Prevention / Reference Number System |
| **Original Context** | v1.9.0 — CONTENT values referenced by index numbers in Content Placement instead of exact strings, causing text to render twice |
| **Section Equivalent** | Content Placement must ALWAYS quote exact values from CONTENT using double quotes. Index-based references (e.g., "Item 1", "첫 번째 항목") are FORBIDDEN. |
| **Detection Method** | Scan Content Placement for patterns: numbered references like "Item 1", "첫 번째 항목", "1번", "2번" or ordinal patterns. If found, FAIL. Verify all placement references use exact quoted strings from CONTENT. |

**PASS Example:**
```
CONTENT:
  title: "AI 불량 검출 시스템"
  metric1: "검출률 98.5%"
  metric2: "처리 속도 0.3초"

Content Placement:
  top_center: "AI 불량 검출 시스템"
  left_box: "검출률 98.5%"
  right_box: "처리 속도 0.3초"
```

**FAIL Example:**
```
CONTENT:
  title: "AI 불량 검출 시스템"
  metric1: "검출률 98.5%"
  metric2: "처리 속도 0.3초"

Content Placement:
  top_center: "첫 번째 항목"
  left_box: "Item 1"
  right_box: "Item 2"
```

---

## Rule 2: Seminar Theme Scene-ification Prevention (테마 라벨 탈맥락화)

| Field | Content |
|-------|---------|
| **Rule Name** | Seminar Theme Scene-ification Prevention / Meta-Label decontextualization |
| **Original Context** | v1.9.0 — Abstract concept keywords (e.g., "AI 분석", "데이터 흐름") entered directly into CONTENT and rendered as literal slide text, breaking semantic context |
| **Section Equivalent** | CONTENT values must be CONCRETE, displayable text with full context. Abstract concept labels or meta-labels are FORBIDDEN. Values must be complete subject-predicate phrases. |
| **Detection Method** | Scan CONTENT values for: (1) floating concept words without context ("혁신", "효율성", "AI 분석"), (2) meta-labels ("Data:", "Note:", "Label:", "Key:", "Item:"), (3) incomplete noun phrases. If found, FAIL. |

**PASS Example:**
```
CONTENT:
  benefit1: "AI가 실시간으로 불량품을 검출합니다"
  benefit2: "데이터 기반 의사결정으로 비용을 30% 절감합니다"
  process: "카메라 → AI 분석 → 자동 분류"
```

**FAIL Example:**
```
CONTENT:
  concept1: "AI 분석"
  concept2: "데이터 흐름"
  concept3: "혁신"
  meta: "Data: 불량률"
```

---

## Rule 3: Axis-Based Layout Space-Meaning Verification (축 기반 레이아웃 공간-의미 역검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Axis-Based Layout Space-Meaning Verification |
| **Original Context** | v1.9.0 — Axis-based layouts (x/y coordinates) where spatial positioning contradicts semantic hierarchy (e.g., primary concept at bottom, secondary at top) |
| **Section Equivalent** | In Content Placement, axis-based arrangements must follow semantic hierarchy: top/left = primary/cause, bottom/right = secondary/effect. Spatial position must reinforce meaning. |
| **Detection Method** | For axis-based layouts, verify: (1) top/upper positions contain primary concepts, (2) bottom/lower positions contain secondary/supporting concepts, (3) left positions precede right positions in causal chains. If spatial order contradicts semantic order, FAIL. |

**PASS Example:**
```
Content Placement:
  top_left: "원인: 공정 온도 편차"
  top_right: "결과: 제품 불량"
  bottom_left: "해결책: 온도 제어 시스템"
  bottom_right: "효과: 불량률 50% 감소"
```

**FAIL Example:**
```
Content Placement:
  bottom_left: "원인: 공정 온도 편차"
  bottom_right: "결과: 제품 불량"
  top_left: "해결책: 온도 제어 시스템"
  top_right: "효과: 불량률 50% 감소"
```

---

## Rule 4: CONTENT↔Placement Full Correspondence (전수 대응 원칙)

| Field | Content |
|-------|---------|
| **Rule Name** | CONTENT↔Placement Full Correspondence Principle |
| **Original Context** | v1.10.0 — Every item in CONTENT must receive explicit placement instruction in Content Placement. No orphan items allowed. |
| **Section Equivalent** | Count of `key: "value"` pairs in CONTENT MUST EQUAL count of quoted references in Content Placement. Every value must be placed; every placement must reference defined content. |
| **Detection Method** | (1) Count all `key: "value"` pairs in CONTENT. (2) Count all quoted strings in Content Placement. (3) Verify counts match. (4) Cross-match each value to its placement reference. If count mismatch or any value unplaced, FAIL. |

**PASS Example:**
```
CONTENT:
  title: "생산 효율성 분석"
  metric1: "월간 생산량 15,000개"
  metric2: "불량률 2.3%"
  metric3: "가동률 94.5%"

Content Placement:
  header: "생산 효율성 분석"
  box1: "월간 생산량 15,000개"
  box2: "불량률 2.3%"
  box3: "가동률 94.5%"
```

**FAIL Example:**
```
CONTENT:
  title: "생산 효율성 분석"
  metric1: "월간 생산량 15,000개"
  metric2: "불량률 2.3%"
  metric3: "가동률 94.5%"
  metric4: "에너지 소비 12kWh"

Content Placement:
  header: "생산 효율성 분석"
  box1: "월간 생산량 15,000개"
  box2: "불량률 2.3%"
  box3: "가동률 94.5%"
```

---

## Rule 5: Orphan Item Prevention (고아 항목 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Orphan Item Prevention |
| **Original Context** | v1.10.0 — Text defined in CONTENT but not referenced in Content Placement instructions, leaving content unused |
| **Section Equivalent** | Every `key: "value"` in CONTENT must appear as a quoted reference in Content Placement. Orphan items (defined but unplaced) are FORBIDDEN. |
| **Detection Method** | Extract all values from CONTENT. For each value, search Content Placement for exact quoted match. If any value has no match in Content Placement, FAIL. |

**PASS Example:**
```
CONTENT:
  stat1: "매출 증가율 25%"
  stat2: "고객 만족도 4.8/5.0"

Content Placement:
  left: "매출 증가율 25%"
  right: "고객 만족도 4.8/5.0"
```

**FAIL Example:**
```
CONTENT:
  stat1: "매출 증가율 25%"
  stat2: "고객 만족도 4.8/5.0"
  stat3: "시장 점유율 18%"

Content Placement:
  left: "매출 증가율 25%"
  right: "고객 만족도 4.8/5.0"
```

---

## Rule 6: Data Duplication Prevention (Data 중복 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Data Duplication Prevention |
| **Original Context** | v1.10.0 — Same numerical value or phrase appears multiple times across CONTENT, Scene Description, or Content Placement, causing redundancy and confusion |
| **Section Equivalent** | Each unique value appears exactly once across all sections. Scene Description describes visual elements; CONTENT lists displayable text; Content Placement places text. No value should appear in multiple sections. |
| **Detection Method** | Collect all values from CONTENT, Scene Description, and Content Placement. Check for duplicates. If any value appears more than once across sections, FAIL. |

**PASS Example:**
```
Scene Description:
  background: "공장 생산 라인"
  elements: "로봇 팔, 컨베이어 벨트"

CONTENT:
  title: "자동화 생산 시스템"
  metric: "생산 속도 50% 증가"

Content Placement:
  top: "자동화 생산 시스템"
  bottom: "생산 속도 50% 증가"
```

**FAIL Example:**
```
Scene Description:
  background: "공장 생산 라인"
  elements: "생산 속도 50% 증가"

CONTENT:
  title: "자동화 생산 시스템"
  metric: "생산 속도 50% 증가"

Content Placement:
  top: "자동화 생산 시스템"
  bottom: "생산 속도 50% 증가"
```

---

## Rule 7: Concept Keyword Contamination Prevention (개념 키워드 혼입 방지)

| Field | Content |
|-------|---------|
| **Rule Name** | Concept Keyword Contamination Prevention |
| **Original Context** | v1.10.0 — Pure abstract concept words (e.g., "혁신", "효율성", "지속성") appear standalone in CONTENT without concrete context or supporting details |
| **Section Equivalent** | CONTENT values must be concrete, contextual phrases. Floating concept words without supporting context are FORBIDDEN. Each value must be displayable and meaningful on its own. |
| **Detection Method** | Scan CONTENT values for: (1) single-word abstract nouns ("혁신", "효율성", "지속성", "가치"), (2) concept words without predicates or context. If found, FAIL. |

**PASS Example:**
```
CONTENT:
  innovation: "AI 기술로 생산 공정을 혁신했습니다"
  efficiency: "에너지 효율성을 35% 개선했습니다"
  sustainability: "탄소 배출을 연 50톤 감축했습니다"
```

**FAIL Example:**
```
CONTENT:
  concept1: "혁신"
  concept2: "효율성"
  concept3: "지속성"
  concept4: "가치"
```

---

## Rule 8: Reference Number System Validation (번호 참조 체계 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Reference Number System Validation |
| **Original Context** | v1.10.1 — Explicit validation added to renderer-agent to detect index-based references in Content Placement that should use exact string quotes instead |
| **Section Equivalent** | Content Placement must use exact quoted strings from CONTENT, never index numbers or ordinal references. Patterns like "1번", "2번", "첫 번째", "두 번째" are FORBIDDEN. |
| **Detection Method** | Scan Content Placement for: (1) ordinal patterns ("첫 번째", "두 번째", "세 번째"), (2) numbered patterns ("1번", "2번", "3번"), (3) generic item references ("Item 1", "Item 2"). If found, FAIL. |

**PASS Example:**
```
Content Placement:
  position1: "AI 기술 도입으로 비용 30% 절감"
  position2: "자동화로 생산 속도 2배 증가"
  position3: "품질 관리 시간 50% 단축"
```

**FAIL Example:**
```
Content Placement:
  position1: "첫 번째 항목"
  position2: "두 번째 항목"
  position3: "세 번째 항목"
```

---

## Rule 9: Seminar Label Decontextualization Validation (세미나 라벨 탈맥락화 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Seminar Label Decontextualization Validation |
| **Original Context** | v1.10.1 — Explicit check added to renderer-agent to detect abstract/meta labels in seminar theme CONTENT that lack concrete context |
| **Section Equivalent** | For seminar themes, CONTENT values must be concrete, actionable statements. Meta-labels ("Data:", "Note:", "Label:", "Key:", "Item:") and floating concept words are FORBIDDEN. |
| **Detection Method** | Scan CONTENT for: (1) meta-label prefixes ("Data:", "Note:", "Label:", "Key:", "Item:"), (2) abstract concept words without context, (3) incomplete phrases. If found in seminar theme, FAIL. |

**PASS Example:**
```
CONTENT:
  insight1: "AI 기술이 제조업 혁신을 주도하고 있습니다"
  insight2: "데이터 기반 의사결정으로 경쟁력을 확보합니다"
  insight3: "자동화 투자가 ROI 200%를 달성했습니다"
```

**FAIL Example:**
```
CONTENT:
  item1: "Data: AI 기술"
  item2: "Note: 제조업 혁신"
  item3: "Key: 경쟁력"
  item4: "Label: 자동화"
```

---

## Rule 10: Orphan Item Explicit Check (고아 항목 검증)

| Field | Content |
|-------|---------|
| **Rule Name** | Orphan Item Explicit Check |
| **Original Context** | v1.10.1 — Explicit count-match check added to renderer-agent to verify every CONTENT item has corresponding Content Placement instruction |
| **Section Equivalent** | Count of `key: "value"` pairs in CONTENT must exactly match count of quoted references in Content Placement. Bidirectional matching required: no orphans, no ghosts. |
| **Detection Method** | (1) Count all `key: "value"` pairs in CONTENT. (2) Count all quoted strings in Content Placement. (3) If counts differ, FAIL. (4) Cross-match each value to placement reference. If any mismatch, FAIL. |

**PASS Example:**
```
CONTENT:
  benefit1: "생산성 40% 향상"
  benefit2: "비용 절감 25%"
  benefit3: "품질 개선 99.2%"

Content Placement:
  metric1: "생산성 40% 향상"
  metric2: "비용 절감 25%"
  metric3: "품질 개선 99.2%"
```

**FAIL Example:**
```
CONTENT:
  benefit1: "생산성 40% 향상"
  benefit2: "비용 절감 25%"
  benefit3: "품질 개선 99.2%"
  benefit4: "고객 만족도 4.9/5.0"

Content Placement:
  metric1: "생산성 40% 향상"
  metric2: "비용 절감 25%"
  metric3: "품질 개선 99.2%"
```

---

## Rule 11: Meta-Label Prohibition (메타라벨 금지)

| Field | Content |
|-------|---------|
| **Rule Name** | Meta-Label Prohibition |
| **Original Context** | v1.11.0 — CONTENT values must not start with structural meta-labels like "Data:", "Note:", "Label:", "Key:", "Item:" — these are metadata, not content |
| **Section Equivalent** | CONTENT values must be pure content without meta-label prefixes. Structural labels belong in section names, not in values. |
| **Detection Method** | Scan all CONTENT values for prefixes: "Data:", "Note:", "Label:", "Key:", "Item:", "Info:", "Tip:", "Alert:". If any found, FAIL. |

**PASS Example:**
```
CONTENT:
  stat1: "월간 매출 5억 원"
  stat2: "고객 수 12,000명"
  stat3: "시장 점유율 18%"
```

**FAIL Example:**
```
CONTENT:
  stat1: "Data: 월간 매출 5억 원"
  stat2: "Note: 고객 수 12,000명"
  stat3: "Key: 시장 점유율 18%"
```

---

## Rule 12: Subject-Predicate Sentence Format Enforcement (조사문 형식 강제)

| Field | Content |
|-------|---------|
| **Rule Name** | Subject-Predicate Sentence Format Enforcement |
| **Original Context** | v1.11.0 — CONTENT values should be complete subject-predicate phrases, not floating nouns or incomplete fragments |
| **Section Equivalent** | CONTENT values must be complete, displayable sentences or phrases with subject and predicate. Floating nouns or incomplete fragments are FORBIDDEN. |
| **Detection Method** | Analyze each CONTENT value: (1) Check for subject (주어) and predicate (술어), (2) Verify it forms a complete, meaningful phrase, (3) Reject floating nouns or fragments. If incomplete, FAIL. |

**PASS Example:**
```
CONTENT:
  statement1: "AI 시스템이 불량품을 자동으로 검출합니다"
  statement2: "생산 속도가 시간당 500개에서 750개로 증가했습니다"
  statement3: "품질 관리 비용이 연 2억 원 절감되었습니다"
```

**FAIL Example:**
```
CONTENT:
  fragment1: "불량 검출"
  fragment2: "생산 속도 증가"
  fragment3: "비용 절감"
  noun: "자동화"
```

---

## Rule 13: Circle-Number Marker Prohibition (원 번호 마커 금지)

| Field | Content |
|-------|---------|
| **Rule Name** | Circle-Number Marker Prohibition |
| **Original Context** | v1.11.0 — Circle-number characters (①②③④⑤⑥⑦⑧⑨⑩) are forbidden in CONTENT values as they are rendering artifacts, not content |
| **Section Equivalent** | CONTENT values must not contain circle-number characters (①②③④⑤⑥⑦⑧⑨⑩). Use plain text or Arabic numerals instead. |
| **Detection Method** | Scan all CONTENT values for Unicode circle-number characters (U+2460–U+2473). If any found, FAIL. |

**PASS Example:**
```
CONTENT:
  step1: "1단계: 데이터 수집"
  step2: "2단계: AI 분석"
  step3: "3단계: 결과 도출"
```

**FAIL Example:**
```
CONTENT:
  step1: "① 데이터 수집"
  step2: "② AI 분석"
  step3: "③ 결과 도출"
```

---

## Summary Table

| Rule # | Rule Name | v1.X.X | Key Validation |
|--------|-----------|--------|-----------------|
| 1 | Double-Rendering Prevention | v1.9.0 | No index-based references in `### Content Placement` |
| 2 | Seminar Theme Scene-ification Prevention | v1.9.0 | No abstract concept labels in `## CONTENT` |
| 3 | Axis-Based Layout Space-Meaning Verification | v1.9.0 | Spatial hierarchy matches semantic hierarchy |
| 4 | CONTENT↔Placement Full Correspondence | v1.10.0 | Count match: `## CONTENT` values = `### Content Placement` references |
| 5 | Orphan Item Prevention | v1.10.0 | Every `## CONTENT` value appears in `### Content Placement` |
| 6 | Data Duplication Prevention | v1.10.0 | No value appears in multiple sections |
| 7 | Concept Keyword Contamination Prevention | v1.10.0 | No floating concept words in `## CONTENT` |
| 8 | Reference Number System Validation | v1.10.1 | Explicit check for index-based references |
| 9 | Seminar Label Decontextualization Validation | v1.10.1 | Explicit check for meta-labels in seminar themes |
| 10 | Orphan Item Explicit Check | v1.10.1 | Explicit count-match verification |
| 11 | Meta-Label Prohibition | v1.11.0 | No "Data:", "Note:", "Label:" prefixes |
| 12 | Subject-Predicate Sentence Format Enforcement | v1.11.0 | Complete phrases, not floating nouns |
| 13 | Circle-Number Marker Prohibition | v1.11.0 | No ①②③④⑤ characters |

---

## Integration with renderer-agent.md

These 13 rules complement the 8 core section validation checks and 3 additional checks in `renderer-agent.md`:

**Core Section Checks (8):**
1. 5 sections exist: Scene Description, CONTENT, Typography, Canvas Settings, Content Placement
2. CONTENT has `key: "value"` format
3. Content Placement quotes CONTENT values in double quotes
4. No numbered list patterns (1., 2., -)
5. No pt/px units
6. No markdown formatting (**, *, #)
7. Theme-specific item count limits respected
8. Typography contains Korean font hint

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

Together, these 24 validation points (8 + 3 + 13) form the comprehensive validation framework for v2.0.0+ 4-block section architecture.
