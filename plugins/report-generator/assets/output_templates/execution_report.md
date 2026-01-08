# 보고서 생성 실행 보고서

## 실행 정보

| 항목 | 값 |
|------|------|
| **프로젝트명** | {project_name} |
| **입력 경로** | {input_path} |
| **코드베이스 경로** | {code_path} |
| **출력 디렉토리** | {output_dir} |
| **실행 시작** | {start_time} |
| **실행 종료** | {end_time} |
| **총 실행 시간** | {total_time} |

---

## 입력 분석 결과

### 감지된 도메인

| 항목 | 값 |
|------|------|
| **주요 도메인** | {primary_domain} |
| **신뢰도** | {confidence}% |
| **입력 모드** | {input_mode} |

### 분석된 파일

| 파일명 | 유형 | 줄 수 |
|--------|------|:-----:|
{file_list}

**총 파일 수**: {total_files}개
**총 줄 수**: {total_lines}줄

---

## 챕터 생성 결과

### 생성된 챕터

| 번호 | 제목 | 충분성 점수 | 등급 | 파일 경로 |
|:----:|------|:----------:|:----:|----------|
{generated_chapters}

### 생략된 챕터

| 원본 번호 | 제목 | 점수 | 사유 |
|:--------:|------|:----:|------|
{skipped_chapters}

**생성 챕터 수**: {generated_count}개
**생략 챕터 수**: {skipped_count}개

---

## 품질 검증 결과

### 종합 점수

| 항목 | 점수 | 등급 |
|------|:----:|:----:|
| 4단계 패턴 적용 | {pattern_score}점 | {pattern_grade} |
| 용어 일관성 | {term_score}점 | {term_grade} |
| 기술적 정확성 | {accuracy_score}점 | {accuracy_grade} |
| 문서 구조 완성도 | {structure_score}점 | {structure_grade} |
| **종합** | **{total_score}점** | **{total_grade}** |

### 주요 발견 사항

{findings}

### 개선 권장 사항

{recommendations}

---

## 출력 파일 목록

### 보고서 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| 최종 보고서 | `{project_name}_연구보고서.md` | 통합 보고서 |
| 검증 보고서 | `verification/verification_report.md` | 품질 검증 결과 |
| 실행 보고서 | `execution_report.md` | 본 문서 |

### 챕터 파일

{chapter_files}

### 부록 파일

{appendix_files}

---

## 다음 단계 권장 사항

1. **검증 보고서 검토**: `verification/verification_report.md` 확인
2. **품질 등급 확인**: 종합 점수 {total_score}점 ({total_grade} 등급)
3. **개선 필요 항목**: {improvement_count}건

{next_steps}

---

*생성일: {generation_date}*
*Report Generator v1.0.0*
