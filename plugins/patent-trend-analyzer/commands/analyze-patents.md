# Patent Trend Analysis Pipeline

Full end-to-end pipeline for patent research: planning, search, and analysis. Orchestrates three specialized agents in sequence.

## Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| 연구 주제 | string | Yes | 분석할 기술 분야 또는 연구 주제 |
| 대상 국가 | string | No | 검색 대상 국가 (기본값: 한국, 미국, 유럽) |
| 분석 기간 | string | No | 분석 기간 (예: 2020-2025) |
| IPC 코드 | string | No | 특정 IPC 코드 (예: G06N) |

## Workflow

```
[Phase 1: Research Planning]
    |
    +-- Step 1-1. 입력 데이터 추출
    |   +-- 사용자 제공 연구 주제 파싱
    |   +-- 대상 국가, 분석 기간, IPC 코드 확인
    |
    +-- Step 1-2. 검색 전략 수립 실행
    |   +-- Task(subagent_type="patent-trend-analyzer::patent-planner")
    |   +-- 전달 파라미터:
    |       - 연구 주제: $ARGUMENTS[연구 주제]
    |       - 대상 국가: $ARGUMENTS[대상 국가]
    |       - 분석 기간: $ARGUMENTS[분석 기간]
    |       - IPC 코드: $ARGUMENTS[IPC 코드]
    |   +-- 기대 출력:
    |       - 최적화된 키워드 목록 (한영 병기)
    |       - IPC 코드 매핑 테이블
    |       - 검색 전략 테이블 (IPC × 키워드 × 국가)
    |       - API 호출 예산 분석
    |
    +-- Step 1-3. 사용자 확인
        +-- 검색 전략 제시
        +-- 사용자 승인 대기 (조정 가능)

[Phase 2: Search & Collection]
    |
    +-- Step 2-1. 검색 계획 확인
    |   +-- Phase 1 출력 파일 경로 확인
    |   +-- 검색 전략 세부사항 추출
    |
    +-- Step 2-2. 특허 검색 실행
    |   +-- Task(subagent_type="patent-trend-analyzer::patent-searcher")
    |   +-- 전달 파라미터:
    |       - 검색 전략: Phase 1 출력
    |       - 대상 국가: $ARGUMENTS[대상 국가]
    |       - 출력 경로: output/
    |   +-- 기대 출력:
    |       - 국가별 원본 특허 데이터
    |       - 중복 제거 결과
    |       - 수집 통계 보고서
    |
    +-- Step 2-3. 수집 결과 보고
        +-- 실행된 검색 쿼리 수
        +-- 국가별 원본 특허 수
        +-- 중복 제거 후 총 건수
        +-- API 호출 소비량 vs. 예산

[Phase 3: Analysis & Visualization]
    |
    +-- Step 3-1. 분석 데이터 준비
    |   +-- Phase 2 출력 파일 경로 확인
    |   +-- 중복 제거된 특허 데이터 로드
    |
    +-- Step 3-2. 분류 및 시각화 실행
    |   +-- Task(subagent_type="patent-trend-analyzer::patent-analyzer")
    |   +-- 전달 파라미터:
    |       - 특허 데이터: output/deduplicated_patents.xlsx
    |       - 분류 체계: Phase 1 정의
    |       - 출력 경로: output/
    |   +-- 기대 출력:
    |       - 8개 정적 차트 (PNG)
    |       - 통합 대시보드 (PNG)
    |       - 인터랙티브 대시보드 (HTML)
    |       - 다중시트 Excel 보고서
    |       - Markdown 요약 보고서
    |
    +-- Step 3-3. 최종 결과 제시
        +-- 분석 완료 알림
        +-- 출력 파일 목록 안내
        +-- 주요 발견사항 요약
```

## Output Structure

```
output/
├── deduplicated_patents.xlsx          # 중복 제거된 특허 데이터
├── patent_analysis_report.xlsx        # 다중시트 분석 보고서
├── patent_classification_summary.md   # 요약 보고서
├── visualizations/
│   ├── combined_dashboard.png         # 통합 대시보드 (정적)
│   ├── patent_dashboard.html          # 인터랙티브 대시보드
│   ├── chart_01_*.png                 # 개별 차트 1-8
│   └── ...
└── search_statistics.md               # 검색 통계 보고서
```

## Notes

- Each phase can be run independently if you already have intermediate outputs.
- Run `/patent-research-planning` for Phase 1 only (keyword optimization and IPC mapping).
- Run `/patent-search-collect` for Phase 2 only (search execution and deduplication).
- Run `/patent-analysis-viz` for Phase 3 only (classification, charts, and reports).
- If a phase fails mid-run, re-invoke the same phase — batch exports are resumable.
