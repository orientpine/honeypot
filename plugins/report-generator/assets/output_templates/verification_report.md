# 품질 검증 보고서

## 1. 검증 요약

| 항목 | 점수 | 등급 |
|------|:----:|:----:|
| 4단계 패턴 적용 | {pattern_score}점 | {pattern_grade} |
| 용어 일관성 | {term_score}점 | {term_grade} |
| 기술적 정확성 | {accuracy_score}점 | {accuracy_grade} |
| 문서 구조 완성도 | {structure_score}점 | {structure_grade} |
| **종합 점수** | **{total_score}점** | **{total_grade}** |

### 등급 기준

| 점수 범위 | 등급 | 의미 |
|----------|:----:|------|
| 90-100 | A | 국가기관 제출 가능 |
| 80-89 | B | 약간의 수정 권장 |
| 70-79 | C | 수정 필요 |
| 60-69 | D | 상당한 수정 필요 |
| 60 미만 | F | 재작성 권장 |

---

## 2. 4단계 패턴 검증 결과

### 2.1 완전 적용 섹션

다음 섹션은 4단계 패턴이 완전히 적용되었습니다:

{complete_sections}

### 2.2 불완전 적용 섹션

다음 섹션은 일부 단계가 누락되었습니다:

| 섹션 | 누락 단계 | 권장 조치 |
|------|----------|----------|
{incomplete_sections}

### 2.3 패턴별 적용률

| 단계 | 적용률 | 상태 |
|------|:------:|:----:|
| 1단계 (과제 정의) | {step1_rate}% | {step1_status} |
| 2단계 (필요성) | {step2_rate}% | {step2_status} |
| 3단계 (해결 방안) | {step3_rate}% | {step3_status} |
| 4단계 (기술 상세) | {step4_rate}% | {step4_status} |

---

## 3. 용어 일관성 검증 결과

### 3.1 불일치 발견 항목

| 용어 | 변형 | 출현 위치 | 권장 표현 |
|------|------|----------|----------|
{term_inconsistencies}

### 3.2 약어 정의 확인

| 약어 | 정의 여부 | 위치 |
|------|:--------:|------|
{abbreviation_check}

### 3.3 단위 표기 일관성

| 항목 | 사용된 단위 | 권장 단위 |
|------|-----------|----------|
{unit_check}

---

## 4. 기술적 정확성 검증 결과

### 4.1 수치 범위 검증

| 파라미터 | 값 | 범위 검증 | 상태 |
|----------|-----|----------|:----:|
{value_range_check}

### 4.2 참조 일관성

| 항목 | 정의 위치 | 사용 위치 | 상태 |
|------|----------|----------|:----:|
{reference_check}

### 4.3 경고 항목

{warnings}

---

## 5. 문서 구조 완성도

### 5.1 필수 요소 확인

| 요소 | 존재 여부 | 위치 |
|------|:--------:|------|
| 메타데이터 블록 | {meta_exists} | {meta_location} |
| 챕터 제목 | {chapter_exists} | - |
| 소섹션 제목 | {section_exists} | - |
| 그림 캡션 | {caption_exists} | - |
| 결론 | {conclusion_exists} | {conclusion_location} |

### 5.2 그림 캡션 검증

| 챕터 | 소섹션 수 | 캡션 수 | 상태 |
|------|:--------:|:------:|:----:|
{caption_check}

### 5.3 부록 검증

| 부록 | 존재 여부 | 내용 | 상태 |
|------|:--------:|------|:----:|
| 부록 A (파라미터) | {appendix_a_exists} | {appendix_a_count}개 항목 | {appendix_a_status} |
| 부록 B (패키지) | {appendix_b_exists} | {appendix_b_count}개 항목 | {appendix_b_status} |

---

## 6. 개선 권장 사항

### 6.1 우선 개선 항목 (필수)

{priority_improvements}

### 6.2 권장 개선 항목 (선택)

{recommended_improvements}

### 6.3 자동 수정 가능 항목

| 항목 | 현재 | 권장 | 자동 수정 |
|------|------|------|:--------:|
{auto_fix_items}

---

## 7. 검증 세부 로그

### 검증 실행 정보

| 항목 | 값 |
|------|------|
| 검증 시작 | {verification_start} |
| 검증 종료 | {verification_end} |
| 검증 대상 파일 수 | {files_checked} |
| 검증 항목 수 | {items_checked} |

### 상세 로그

```
{detailed_log}
```

---

*검증일: {verification_date}*
*Quality Checker v1.0.0*
