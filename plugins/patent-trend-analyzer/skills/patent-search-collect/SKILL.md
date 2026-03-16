---
name: patent-search-collect
description: "KIPRIS API 기반 특허 검색 실행, 배치 내보내기, 중복 제거. Use when: (1) 특허 데이터 검색 및 다운로드 시, (2) 검색 계획 실행 시, (3) '특허 검색', 'search patents', 'collect patent data', 'export patents to Excel' 요청 시, (4) 키워드, 출원인, 출원번호, IPC 코드 기반 한국/해외 특허 배치 검색 시."
---

# patent-search-collect

KIPRIS MCP 서버 도구를 활용해 특허를 검색하고, 배치로 내보내고, 중복을 제거하는 스킬입니다.

이 스킬은 L1 (patent-research-planning) 에서 수립한 검색 전략을 실행하는 **L2 (Search)** 단계입니다.

---

## Tool Reference

### 한국 특허 검색 (8개)

| 도구 이름 | 주요 파라미터 | 설명 |
|-----------|--------------|------|
| `patent_free_search` | `query`, `page`, `sort` | 자유 키워드 전문 검색 |
| `patent_applicant_search` | `applicant`, `page` | 출원인(회사/개인) 기반 검색 |
| `patent_application_number_search` | `application_number` | 출원번호 정확 검색 |
| `patent_search` | `query`, `ipc`, `date_range` | IPC 코드 + 키워드 통합 검색 |
| `patent_detail_search` | `application_number` | 특허 상세 정보 (청구항 포함) 조회 |
| `patent_summary_search` | `query`, `page` | 요약 필드 기반 검색 |
| `patent_righter_search` | `righter`, `page` | 권리자(등록 후 양수인) 기반 검색 |
| `patent_batch_export` | `query`, `max_pages`, `output_path` | 전체 결과 Excel 배치 내보내기 |

### 해외 특허 검색 (7개)

| 도구 이름 | 주요 파라미터 | 설명 |
|-----------|--------------|------|
| `foreign_patent_free_search` | `query`, `nation`, `page` | 국가 지정 자유 키워드 검색 |
| `foreign_patent_applicant_search` | `applicant`, `nation`, `page` | 국가 지정 출원인 검색 |
| `foreign_patent_application_number_search` | `application_number`, `nation` | 국가 지정 출원번호 검색 |
| `foreign_international_application_number_search` | `pct_number` | PCT 국제출원번호 검색 |
| `foreign_international_open_number_search` | `open_number` | PCT 국제공개번호 검색 |
| `foreign_patent_batch_export` | `query`, `nation`, `max_pages`, `output_path` | 해외 특허 배치 내보내기 |
| `foreign_patent_ipc_batch_export` | `ipc`, `nation`, `date_range`, `output_path` | IPC 코드 기반 해외 배치 내보내기 |

### 후처리 (1개)

| 도구 이름 | 주요 파라미터 | 설명 |
|-----------|--------------|------|
| `patent_result_deduplicator` | `input_files`, `output_path`, `key_field` | 복수 검색 결과 파일 중복 제거 |

---

## Workflow

### Step 1. 검색 유형 선택

| 상황 | 권장 도구 |
|------|-----------|
| 빠른 결과 확인 (< 100건) | `patent_free_search` / `foreign_patent_free_search` |
| 전체 수집 (> 100건) | `patent_batch_export` / `foreign_patent_batch_export` |
| IPC 코드 중심 | `patent_search` / `foreign_patent_ipc_batch_export` |
| 특정 기업 분석 | `patent_applicant_search` / `foreign_patent_applicant_search` |

### Step 2. 검색 실행

빠른 검색 예시:

```python
# 한국 특허 - 페이지당 10건, 최신순 정렬
patent_free_search(
    query="<L1에서 수립한 키워드>",
    page=1,
    sort="desc_sort",
    sort_spec="AD"  # AD = 출원일 기준 최신순
)
```

배치 내보내기 예시:

```python
# 전체 결과를 Excel로 저장 (빈 페이지 감지 시 자동 종료)
patent_batch_export(
    query="<L1에서 수립한 키워드>",
    max_pages=50,
    output_path="./output/korea_patents.xlsx"
)
```

### Step 3. 다중 쿼리 실행

L1에서 수립한 쿼리 목록을 순차 또는 병렬로 실행합니다.

```
쿼리 1: "<한국어 키워드 1>"     → korea_q1.xlsx
쿼리 2: "<한국어 키워드 2>"     → korea_q2.xlsx
쿼리 3: "<영어 키워드 1>"       → us_q1.xlsx (US)
쿼리 4: "<영어 키워드 2>"       → ep_q1.xlsx (EP)
```

### Step 4. 중복 제거

```python
patent_result_deduplicator(
    input_files=["korea_q1.xlsx", "korea_q2.xlsx", "us_q1.xlsx", "ep_q1.xlsx"],
    output_path="./output/merged_patents.xlsx",
    key_field="application_number"  # 출원번호 기준 중복 제거
)
```

### Step 5. 수집 결과 보고

- 국가별 수집 건수 요약
- 중복 제거 전후 비교
- 이상치 (결과 0건 쿼리, 오류 쿼리) 보고
- L3 (patent-analysis-viz) 로 전달할 파일 목록 제시

---

## Multi-Country Search Strategy

해외 특허 검색 시 권장 순서:

```
1. US (미국)  → 가장 많은 공개 특허, 영어 키워드 최적
2. EP (유럽)  → 다국 패밀리 포함, 중복률 높음
3. JP (일본)  → 일본어 키워드 별도 필요
4. CN (중국)  → 최근 급증, 한자 키워드 필요
```

각 국가 결과를 별도 파일로 저장 후 `patent_result_deduplicator` 로 통합합니다.

---

## API Authentication Modes

KIPRIS API는 두 가지 인증 방식을 지원하며, 모두 `KIPRIS_API_KEY` 환경변수로 통일해 설정합니다.

| 방식 | 파라미터명 | 설명 |
|------|-----------|------|
| accessKey (구) | `accessKey` | 구형 API 엔드포인트 |
| ServiceKey (신) | `ServiceKey` | 신형 API 엔드포인트 (권장) |

MCP 서버는 키 형식을 자동 감지하여 적절한 엔드포인트로 라우팅합니다.

---

## Tips

- **최신순 정렬**: `sort="desc_sort"` + `sort_spec="AD"` 조합으로 최신 출원일 기준 정렬
- **배치 자동 종료**: `patent_batch_export` 는 빈 페이지 감지 시 자동 중단 (max_pages 초과 불필요)
- **대용량 수집**: max_pages를 높게 설정해도 실제 결과가 적으면 일찍 종료됨
- **오류 재시도**: API 타임아웃 시 동일 파라미터로 재호출하면 자동 재개
- **IPC 범위**: 상위 IPC 코드로 넓게 잡고, 결과가 너무 많으면 하위 코드로 좁힘
