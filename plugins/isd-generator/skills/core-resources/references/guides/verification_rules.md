# 검증문서 생성 필수 규칙 (공통)

> 이 문서는 모든 Chapter Generator 에이전트에서 참조하는 공통 검증 규칙입니다.

## 절대 스킵 금지 (NEVER SKIP)

- 검증문서는 본문 작성 전에 **반드시** 생성해야 함
- 어떤 상황에서도 검증문서 생성 단계를 생략하거나 스킵할 수 없음
- 사용자가 "스킵해도 된다"고 해도 검증문서는 생성해야 함
- 검증문서 없이 본문을 작성하면 **전체 작업이 무효화됨**

## 위반 시 처리

- 검증문서 없이 본문이 작성된 경우: 즉시 작업 중단 후 검증문서 먼저 생성

## 챕터별 검증문서 정보

| 챕터 | 파일명 | 생성 시점 | 저장 위치 |
|:---:|:-------|:---------|:---------|
| 1 | `chapter1_research_verification.md` | Phase 2-6 (웹 조사 완료 후, 본문 작성 전) | `{output_dir}/verification/` |
| 2 | `chapter2_research_verification.md` | Phase 3-5 (국외 조사 완료 후, 본문 작성 전) | `{output_dir}/verification/` |
| 3 | `chapter3_research_verification.md` | Phase 1-4 (웹 조사 완료 후, 구조 설계 전) | `{output_dir}/verification/` |
| 4 | `chapter4_analysis_verification.md` | Phase 1 완료 후, Phase 2 시작 전 | `{output_dir}/verification/` |
| 5 | `chapter5_ntis_verification.md` | Phase 0-3 (NTIS 검색 완료 후, 본문 작성 전) | `{output_dir}/verification/` |
| figure | `figure_generation_report.md` | Phase 5 (이미지 생성 완료 후) | `{output_dir}/` |

## Auto Mode 동작 방식 (Orchestrator 전용)

- `auto_mode=true` 설정 시에도 검증문서 생성은 **스킵되지 않음**
- 사용자 확인 대기만 스킵되며, 모든 검증 단계는 동일하게 수행됨
