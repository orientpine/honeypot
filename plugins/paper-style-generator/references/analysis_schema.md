# Style Analysis Schema

Paper Style Generator가 분석하는 항목들의 정의입니다.

## 1. 전체 문서 수준 분석

### 1.1 Field Characteristics

| 필드 | 타입 | 설명 |
|------|------|------|
| `primary_field` | string | 주요 연구 분야 (예: biosensor, diagnostics) |
| `secondary_fields` | string[] | 관련 분야 목록 |
| `research_type` | string | 연구 유형 (experimental, computational, review) |
| `keywords` | string[] | 추출된 키워드 |
| `methodology_types` | string[] | 방법론 유형 |

### 1.2 Document Structure

| 필드 | 타입 | 설명 |
|------|------|------|
| `section_order` | string[] | 섹션 순서 |
| `section_lengths` | object | 섹션별 평균 길이 (단어 수) |

### 1.3 Citation Style

| 필드 | 타입 | 설명 |
|------|------|------|
| `format` | string | 인용 형식 (numbered, author_year, superscript) |
| `pattern` | string | 인용 패턴 예시 |
| `examples` | string[] | 실제 예시 |

### 1.4 Measurement Format

| 측정 유형 | 분석 항목 |
|----------|----------|
| Temperature | 온도 표기 (37°C vs 37 °C) |
| Concentration | 농도 표기 (0.5mg/mL vs 0.5 mg/mL) |
| Time | 시간 표기 (15min vs 15 min) |
| Centrifugation | 원심분리 (10000×g vs 10,000 × g) |

---

## 2. 섹션별 분석

### 2.1 공통 분석 항목

| 필드 | 타입 | 설명 |
|------|------|------|
| `voice.active` | float | 능동태 비율 (0-1) |
| `voice.passive` | float | 수동태 비율 (0-1) |
| `tense.past` | float | 과거 시제 비율 |
| `tense.present` | float | 현재 시제 비율 |
| `word_count.mean` | int | 평균 단어 수 |
| `word_count.std` | int | 표준편차 |
| `high_freq_verbs` | tuple[] | 고빈도 동사 [(verb, count), ...] |

### 2.2 섹션별 특화 분석

#### Abstract

| 필드 | 설명 |
|------|------|
| `structure` | 구조 요소 (background, methods, results, conclusion) |
| `sentence_count` | 문장 수 통계 |
| `key_patterns.opening` | 시작 패턴 |
| `key_patterns.closing` | 마무리 패턴 |

#### Introduction

| 필드 | 설명 |
|------|------|
| `narrative_flow` | 서사 흐름 단계 |
| `closing_pattern` | 마무리 패턴 ("Here, we present...") |
| `statistics_usage` | 통계 데이터 사용 패턴 |

#### Methods

| 필드 | 설명 |
|------|------|
| `heading_style` | 소제목 스타일 (inline vs separate) |
| `subsection_count` | 소섹션 수 |
| `supplier_citation` | 공급업체 인용 형식 |
| `paragraph_length` | 단락 길이 |

#### Results

| 필드 | 설명 |
|------|------|
| `we_usage.ratio` | "We" 문장 시작 비율 |
| `organization.style` | 구성 스타일 (theme-based vs experiment-based) |
| `figure_reference.format` | Figure 참조 형식 |
| `quantitative_patterns` | 정량적 표현 패턴 |

#### Discussion

| 필드 | 설명 |
|------|------|
| `structure` | 구조 요소 (achievement, limitations, future) |
| `limitation_pattern` | 한계 인정 패턴 |
| `future_directions.tiers` | 미래 방향 단계 |

#### Caption

| 필드 | 설명 |
|------|------|
| `title_format` | 제목 형식 (standard vs nature) |
| `panel_labeling.format` | 패널 레이블 형식 |
| `statistics_inclusion` | 통계 포함 방식 |

#### Title

| 필드 | 설명 |
|------|------|
| `length.mean` | 평균 단어 수 |
| `patterns` | 제목 패턴 목록 |
| `components` | 필수 구성요소 |

---

## 3. 언어 패턴 분석

### 3.1 High Frequency Verbs

섹션별로 자주 사용되는 학술 동사를 추출합니다.

**분석 대상 동사 풀**:
```
demonstrated, showed, revealed, achieved, obtained,
validated, confirmed, established, determined, measured,
detected, observed, found, identified, characterized,
developed, designed, constructed, fabricated, prepared,
analyzed, evaluated, assessed, compared, tested,
optimized, enhanced, improved, increased, reduced,
enabled, facilitated, allowed, provided, offered,
suggests, indicates, implies, supports, demonstrates
```

### 3.2 Transition Phrases

섹션별 전환 표현을 분석합니다.

| 섹션 | 예시 |
|------|------|
| Introduction | "Here, we present", "To address this" |
| Methods | "Briefly,", "Following" |
| Results | "We first", "To further validate" |
| Discussion | "Our results", "One limitation" |

### 3.3 Hedging Expressions

헷징 표현의 사용 빈도와 위치를 분석합니다.

**분석 대상**:
- 동사: may, might, could, would, suggest, indicate
- 부사: potentially, possibly, likely
- 구문: it is possible that, it is likely

---

## 4. 신뢰도 계산

### 4.1 신뢰도 요소

| 요소 | 계산 방법 | 기준 |
|------|----------|------|
| 샘플 크기 | n / 10 (최대 1.0) | n ≥ 10 → 높음 |
| 패턴 일관성 | 1 - (std / mean) | ≥ 0.7 → 높음 |
| 커버리지 | 추출 섹션 / 전체 섹션 | ≥ 0.9 → 높음 |

### 4.2 신뢰도 수준

| 수준 | 범위 | 의미 |
|------|------|------|
| 높음 | ≥ 80% | 신뢰할 수 있는 패턴 |
| 중간 | 60-79% | 참고용, 검토 필요 |
| 낮음 | < 60% | 추가 데이터 필요 |

---

## 5. 출력 형식

### style_analysis.json

```json
{
  "aggregated": {
    "paper_count": 12,
    "sections": {
      "abstract": {...},
      "introduction": {...},
      "methods": {...},
      "results": {...},
      "discussion": {...}
    },
    "citation_style": {...},
    "field_characteristics": {...}
  },
  "confidence": {
    "overall": 0.85,
    "by_section": {...}
  },
  "individual_analyses": [...]
}
```
