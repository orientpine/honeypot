# Report Generator Orchestrator

## Overview

연구 노트를 분석하여 공학 박사 수준의 국가기관 제출용 연구 보고서를 자동 생성하는 통합 오케스트레이터입니다.

**핵심 기능:**
- 다양한 입력 형식 지원 (폴더, 단일 파일, 코드+노트)
- 연구 도메인 자동 감지 (ROS2, AI/ML, 범용)
- 최대 9개 챕터 자동 매핑 (자료 부족 챕터는 생략)
- 4단계 문장 패턴 적용
- 품질 검증 및 보고서 생성

---

## Input Requirements

### 필수 입력

| 항목 | 설명 | 예시 |
|------|------|------|
| input_path | 연구 노트 경로 | `./research_notes/` 또는 `./summary.md` |
| project_name | 프로젝트명 | `HR35_자율굴착기` |

### 선택 입력

| 항목 | 설명 | 예시 | 기본값 |
|------|------|------|--------|
| code_path | 코드베이스 경로 | `/home/user/ros2_ws/src/` | 없음 |
| output_dir | 출력 디렉토리 | `./output/` | `./output/` |
| auto_mode | 자동 진행 여부 | `true` | `false` |

---

## 오케스트레이션 원칙

**챕터 구성**: 최대 9개 챕터를 생성하되, 자료 충분성 30점 미만은 생략합니다. 다만 보고서 형태를 유지하기 위해 최소 3개(상위 2개 + 결론)를 보장하고, 결론 챕터는 항상 생성합니다.

**4단계 패턴**: 모든 소섹션은 4단계 문장 패턴을 따릅니다. 심사 기관이 기대하는 서술 형식이므로 생략하면 보고서가 반려됩니다.

**품질 검증**: 본문 생성 후 quality-checker를 돌려 검증 보고서를 남깁니다. 검증 없이 산출된 보고서는 제출 적격 여부를 판단할 근거가 없습니다.

**에이전트 위임**: 파이프라인 각 단계는 오케스트레이터가 직접 수행하지 않고 `Task(subagent_type=...)`로 전담 에이전트에 넘깁니다. 각 에이전트가 자신의 스킬과 검증 규칙을 들고 있어서, 오케스트레이터가 직접 처리하면 그 규칙이 적용되지 않습니다.

- 입력 분석 → input-analyzer
- 콘텐츠 매핑 → content-mapper
- 챕터 작성 → chapter-writer
- 품질 검증 → quality-checker

---

## Workflow

```
[Phase 0: 입력 검증 및 초기화]
    |
    +-- Step 0-1. 입력 경로 검증
    |   +-- input_path 존재 여부 확인
    |   +-- project_name 유효성 확인
    |   +-- code_path 존재 여부 확인 (선택)
    |
    +-- Step 0-2. 출력 디렉토리 생성
        +-- output/{project_name}/chapters/
        +-- output/{project_name}/appendix/
        +-- output/{project_name}/verification/

[Phase 1: 입력 분석]
    |
    +-- Step 1-1. input-analyzer 에이전트 호출
    |   +-- Task(subagent_type="report-generator:input-analyzer")
    |   +-- 전달: input_path, code_path, output_dir
    |
    +-- Step 1-2. 분석 결과 확인
    |   +-- analysis_result.json 로드
    |   +-- 감지된 도메인 확인
    |   +-- 파일 분류 결과 확인
    |
    +-- Step 1-3. 사용자 확인 (auto_mode=false 시)
        +-- 감지된 도메인 확인 요청
        +-- 진행 여부 확인

[Phase 2: 컨텐츠 매핑]
    |
    +-- Step 2-1. content-mapper 에이전트 호출
    |   +-- Task(subagent_type="report-generator:content-mapper")
    |   +-- 전달: analysis_result, output_dir
    |
    +-- Step 2-2. 매핑 결과 확인
    |   +-- content_map.json 로드
    |   +-- 생성될 챕터 목록 확인
    |   +-- 생략될 챕터 목록 및 사유 확인
    |
    +-- Step 2-3. 사용자 확인 (auto_mode=false 시)
        +-- 생성/생략 챕터 목록 안내
        +-- 진행 여부 확인

[Phase 3: 챕터별 작성]
    |
    +-- Step 3-1. 생성 대상 챕터 순회
    |   +-- content_map.generated_chapters 순회
    |   +-- 각 챕터에 대해 Step 3-2 실행
    |
    +-- Step 3-2. chapter-writer 에이전트 호출
    |   +-- Task(subagent_type="report-generator:chapter-writer")
    |   +-- 전달: chapter_info, domain, output_path
    |   +-- 4단계 패턴 적용 확인
    |
    +-- Step 3-3. 챕터 파일 저장 확인
        +-- chapters/chapter_{N}_{주제}.md 생성 확인

[Phase 4: 결론 및 부록 생성]
    |
    +-- Step 4-1. 결론 챕터 생성
    |   +-- 생성된 모든 챕터 로드
    |   +-- 핵심 성과 추출
    |   +-- 결론 템플릿 적용
    |   +-- chapters/chapter_{N}_결론.md 저장
    |
    +-- Step 4-2. 부록 A 생성 (파라미터 테이블)
    |   +-- 전체 챕터에서 파라미터/수치 추출
    |   +-- 카테고리별 분류
    |   +-- 테이블 형식으로 정리
    |   +-- appendix/appendix_a_parameters.md 저장
    |   +-- (파라미터 없으면 생략)
    |
    +-- Step 4-3. 부록 B 생성 (패키지 구성)
        +-- 전체 챕터에서 모듈/패키지 정보 추출
        +-- 테이블 형식으로 정리
        +-- appendix/appendix_b_packages.md 저장
        +-- (패키지 정보 없으면 생략)

[Phase 5: 보고서 통합]
    |
    +-- Step 5-1. 메타데이터 블록 생성
    |   +-- >[!info] 블록 생성
    |   +-- Author, Created, Modified, Location, Tag
    |
    +-- Step 5-2. 전체 보고서 병합
    |   +-- 메타데이터 + 챕터 1~N + 결론 + 부록
    |   +-- {project_name}_연구보고서.md 저장
    |
    +-- Step 5-3. 목차 생성
        +-- 챕터별 링크 생성
        +-- 보고서 상단에 추가

[Phase 6: 품질 검증]
    |
    +-- Step 6-1. quality-checker 에이전트 호출
    |   +-- Task(subagent_type="report-generator:quality-checker")
    |   +-- 전달: chapters_dir, content_map, output_dir
    |
    +-- Step 6-2. 검증 결과 확인
    |   +-- verification_report.md 로드
    |   +-- 종합 점수 및 등급 확인
    |   +-- 주요 문제점 확인
    |
    +-- Step 6-3. 결과 보고
        +-- 종합 점수 및 등급 안내
        +-- 개선 권장 사항 안내
        +-- 출력 파일 위치 안내

[Phase 7: 실행 보고서 생성]
    |
    +-- Step 7-1. execution_report.md 생성
    |   +-- 생성된 챕터 목록 및 파일 경로
    |   +-- 생략된 챕터 목록 및 사유
    |   +-- 품질 검증 결과 요약
    |   +-- 총 실행 시간
    |
    +-- Step 7-2. 최종 안내
        +-- 보고서 파일 위치
        +-- 검증 보고서 위치
        +-- 권장 검토 사항
```

---

## Output Structure

```
output/{project_name}/
├── {project_name}_연구보고서.md      # 최종 통합 보고서
├── chapters/                         # 개별 챕터 파일
│   ├── chapter_1_{주제}.md
│   ├── chapter_2_{주제}.md
│   ├── ...
│   └── chapter_N_결론.md
├── appendix/                         # 부록 (해당 시)
│   ├── appendix_a_parameters.md
│   └── appendix_b_packages.md
├── verification/
│   ├── analysis_result.json          # 입력 분석 결과
│   ├── content_map.json              # 챕터 매핑 결과
│   └── verification_report.md        # 품질 검증 보고서
└── execution_report.md               # 실행 보고서
```

---

## Usage Examples

### 기본 사용법 (폴더 입력)

```
report-generator로 연구 보고서를 생성해줘.
연구 노트 폴더: ./PARA/Projects/KIMM/research_notes/
프로젝트명: HR35_자율굴착기
```

### 단일 파일 입력

```
다음 연구 노트 파일로 보고서를 만들어줘.
파일: ./my_research_summary.md
프로젝트명: AI_감지시스템
```

### 코드베이스 포함

```
코드베이스와 노트를 함께 분석해서 보고서를 생성해줘.
노트: ./research_notes/
코드: /home/user/ros2_ws/src/
프로젝트명: 자율로봇_제어시스템
```

### 자동 모드

```
report-generator로 보고서를 자동 생성해줘. (auto_mode)
연구 노트: ./notes/
프로젝트명: 센서융합시스템
```

---

## 에이전트 분할 이유

파이프라인을 네 개 에이전트로 나눈 것은 산출물 경계 때문입니다. 각 단계는 다음 단계가 읽는 계약된 파일을 남기므로, 중간 산출물만으로 재실행과 디버깅이 가능합니다.

- input-analyzer → `analysis_result.json`
- content-mapper → `content_map.json`
- chapter-writer → `chapters/chapter_{N}_{주제}.md` (챕터당 1회 호출)
- quality-checker → `verification_report.md`

챕터당 별도 호출은 보고서가 챕터 단위로 구성되고 자료 부족 챕터는 생략되는 산출물 구조 때문이지, 분량 제약 때문이 아닙니다.

---

## Error Handling

### 입력 오류

| 오류 상황 | 처리 방법 |
|----------|----------|
| input_path 없음 | 오류 메시지 출력 후 중단 |
| .md 파일 없음 | 경고 후 코드 파일만으로 진행 |
| project_name 없음 | 사용자에게 입력 요청 |

### 처리 오류

| 오류 상황 | 처리 방법 |
|----------|----------|
| 도메인 감지 실패 | GENERAL로 기본 설정 후 계속 |
| 모든 챕터 점수 < 30 | 가장 높은 2개 + 결론 강제 생성 |
| 에이전트 호출 실패 | 재시도 (최대 2회) 후 스킵 |

### 품질 오류

| 오류 상황 | 처리 방법 |
|----------|----------|
| 4단계 패턴 미적용 | 경고 기록, 계속 진행 |
| 검증 점수 < 60 | 경고 및 개선 권장사항 안내 |

---

## Resources

### 하위 에이전트 (Task 도구로 호출)

- `report-generator:input-analyzer`: 입력 분석 에이전트
- `report-generator:content-mapper`: 컨텐츠 매핑 에이전트
- `report-generator:chapter-writer`: 챕터 작성 에이전트
- `report-generator:quality-checker`: 품질 검증 에이전트

### 스킬 (자동 로드)

- `/report-generator:field-keywords`: 도메인별 키워드 (ROS2, AI/ML, GENERAL)
- `/report-generator:chapter-structure`: 챕터 구조 정의 및 충분성 평가
- `/report-generator:four-step-pattern`: 4단계 문장 패턴

### 출력 템플릿 (Read 도구로 로드)

- `skills/chapter-structure/assets/output_templates/report_structure.md`: 보고서 구조 템플릿
- `skills/chapter-structure/assets/output_templates/execution_report.md`: 실행 보고서 템플릿
