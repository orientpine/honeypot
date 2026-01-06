---
name: orchestrator-generator
description: 국책과제 연구계획서(ISD) 전체 5개 Chapter를 자동으로 순차 생성하는 통합 오케스트레이터. 단일 입력 파일(input_template.md 양식)을 받아 Chapter 3->1->2->4->5 순서로 문서를 생성하고 검증문서를 포함한 최종 실행 보고서를 제공한다. 사용자가 ISD 연구계획서 전체 자동 생성을 요청하거나 orchestrator를 사용해달라고 요청할 때 이 스킬을 사용한다.
---

# Orchestrator Generator

## ⚠️ CRITICAL: 검증문서 생성 필수 규칙

**절대 스킵 금지 (NEVER SKIP)**
- 각 Chapter별 검증문서는 본문 작성 전에 **반드시** 생성해야 함
- auto_mode에서도 검증문서 생성은 **절대 생략할 수 없음**
- 검증문서 없이 본문을 작성하면 **해당 Chapter 전체 작업이 무효화됨**

**필수 생성 검증문서 목록 (5개)**
| Chapter | 검증문서 파일명 | 생성 시점 |
|---------|--------------|----------|
| Chapter 3 | chapter3_research_verification.md | Phase 1-4 후 |
| Chapter 1 | chapter1_research_verification.md | Phase 2-6 후 |
| Chapter 2 | chapter2_research_verification.md | Phase 3-5 후 |
| Chapter 4 | chapter4_analysis_verification.md | Phase 1-VERIFY 후 |
| Chapter 5 | chapter5_ntis_verification.md | Phase 0-3 후 |

**auto_mode 동작 방식**
- 검증문서 생성: **필수** (절대 스킵 불가)
- 사용자 검증 대기: 스킵 (자동 진행)
- 검증문서 경로 안내: **필수** 출력

**위반 시 처리**
- 검증문서 없이 본문이 작성된 경우: 즉시 작업 중단 후 검증문서 먼저 생성

---

## Overview

국책과제 연구계획서(ISD)의 5개 Chapter를 자동으로 순차 생성하는 통합 오케스트레이터이다. 사용자가 작성한 통합 입력 파일을 받아 Chapter 3 -> 1 -> 2 -> 4 -> 5 순서로 문서를 생성한다.

## Input Requirements

사용자는 references/input_template.md 양식에 맞춰 통합 입력 파일을 작성해야 한다.

### 필수 입력 섹션

| 섹션 | 용도 | 필수 필드 |
|------|------|----------|
| 1. 연구 아이디어 | Chapter 3 | 아이디어명, 개요, 핵심기술(3개), 적용대상, 예상기간 |
| 2. 기관 정보 | Chapter 1 | 기관명, 약칭, R&R, 중점분야, 보유역량, 네트워크 |
| 3. 분야 키워드 | Chapter 2 | 기술도메인, 적용산업, 주요키워드 |
| 4. 사업화 정보 | Chapter 4 | 참여기업 목록 |
| 5. 유사사업 정보 | Chapter 5 | 기존 유사사업 (해당 시) |
| 6. 출력 설정 | 공통 | 프로젝트명 |

## Workflow

```
[Phase 0: 입력 검증 및 초기화]
    |
    +-- Step 0-1. 입력 파일 파싱
    |   +-- 사용자 제공 입력 파일 읽기
    |   +-- 6개 섹션 완전성 검증
    |   +-- 필수 필드 누락 시 사용자에게 보완 요청
    |
    +-- Step 0-2. 출력 디렉토리 구조 생성
        +-- output/[프로젝트명]/chapter_1/
        +-- output/[프로젝트명]/chapter_2/
        +-- output/[프로젝트명]/chapter_3/
        +-- output/[프로젝트명]/chapter_4/
        +-- output/[프로젝트명]/chapter_5/
        +-- output/[프로젝트명]/verification/

[Phase 1: Chapter 3 생성 - 사업 목표 및 추진 전략]
    |
    +-- Step 1-1. 입력 데이터 추출
    |   +-- 섹션 1 (연구 아이디어) 파싱
    |   +-- 아이디어명, 개요, 핵심기술, 적용대상, 예상기간 추출
    |
    +-- Step 1-2. Chapter 3 생성 실행
    |   +-- chapter3-generator 워크플로우 수행:
    |       - Phase 1: 아이디어 분석 (키워드 추출, 웹 검색)
    |       - Phase 1-4: 검증문서 생성 (chapter3_research_verification.md) ⚠️ 절대 스킵 금지
    |           -> ⚠️ 검증문서 저장 필수 (스킵 불가)
    |           -> 검증문서 경로 안내 후 자동 진행
    |       - Phase 2: 구조 설계 (3축 프레임워크, 연차별 마일스톤)
    |       - Phase 3: 문서 작성 (연구목표및내용.md, 이미지생성_프롬프트.md)
    |       - Phase 4: 일관성 검증
    |
    +-- Step 1-3. 출력 저장
        +-- chapter_3/연구목표및내용.md
        +-- chapter_3/이미지생성_프롬프트.md
        +-- verification/chapter3_research_verification.md

[Phase 2: Chapter 1 생성 - 개발 대상 및 필요성]
    |
    +-- Step 2-1. 입력 데이터 준비
    |   +-- Chapter 3 출력 파일 경로 확인
    |   +-- 섹션 2 (연구 수행 기관 정보) 추출
    |   +-- Chapter 3에서 핵심 정보 요약 추출:
    |       - 최종 연구 목표
    |       - 세부기술 3축 목록
    |       - 정량적 성과 목표 수치
    |
    +-- Step 2-2. Chapter 1 생성 실행
    |   +-- chapter1-generator 워크플로우 수행:
    |       - Phase 1: Chapter 3 분석 및 키워드 추출
    |       - Phase 2: 포괄적 웹 조사 (정책, 시장, 기술, VoC)
    |       - Phase 2-6: 검증문서 생성 (chapter1_research_verification.md) ⚠️ 절대 스킵 금지
    |           -> ⚠️ 검증문서 저장 필수 (스킵 불가)
    |           -> 검증문서 경로 안내 후 자동 진행
    |       - Phase 3: 문서 구조 설계
    |       - Phase 4: 본문 생성 및 검증 (300-400줄, 표 8개 이상)
    |
    +-- Step 2-3. 출력 저장
        +-- chapter_1/개발대상및필요성.md
        +-- chapter_1/chapter1_references.md
        +-- verification/chapter1_research_verification.md

[Phase 3: Chapter 2 생성 - 국내외 시장 및 기술 동향]
    |
    +-- Step 3-1. 입력 데이터 준비
    |   +-- Chapter 3 출력 파일 경로 확인
    |   +-- Chapter 1 출력 파일 경로 확인
    |   +-- 섹션 3 (연구 분야 정보) 추출
    |   +-- Chapter 3/1에서 핵심 정보 요약 추출:
    |       - 기술 키워드
    |       - 개발 대상
    |       - VoC 정보
    |
    +-- Step 3-2. Chapter 2 생성 실행
    |   +-- chapter2-generator 워크플로우 수행:
    |       - Phase 0: 사전 문헌 조사 (웹 검색)
    |       - Phase 1: 선행 문서 분석
    |       - Phase 2: 국내 시장/기술 조사
    |       - Phase 3: 국외 시장/기술 조사
    |       - Phase 3-5: 검증문서 생성 (chapter2_research_verification.md) ⚠️ 절대 스킵 금지
    |           -> ⚠️ 검증문서 저장 필수 (스킵 불가)
    |           -> 검증문서 경로 안내 후 자동 진행
    |       - Phase 4: 시사점 및 기술개발 방향 도출
    |       - Phase 5: 문서 생성 (500-600줄, 표 15-25개)
    |
    +-- Step 3-3. 출력 저장
        +-- chapter_2/국내외시장및기술동향.md
        +-- chapter_2/chapter2_references.md
        +-- verification/chapter2_research_verification.md

[Phase 4: Chapter 4 생성 - 기대효과 및 활용방안]
    |
    +-- Step 4-1. 입력 데이터 준비
    |   +-- Chapter 1 출력 파일 경로 확인
    |   +-- Chapter 3 출력 파일 경로 확인
    |   +-- 섹션 4 (사업화 정보) 추출
    |   +-- Chapter 1에서 추출:
    |       - 개발 대상 정의
    |       - 성과지표 수치
    |       - VoC 기업 목록
    |   +-- Chapter 3에서 추출:
    |       - 최종 목표
    |       - 세부기술
    |       - 참여기업 목록
    |       - 정량적 목표 (기술이전 건수/금액)
    |
    +-- Step 4-2. Chapter 4 생성 실행
    |   +-- chapter4-generator 워크플로우 수행:
    |       - Phase 1: 선행 문서 분석
    |       - Phase 1-VERIFY: 검증문서 생성 (chapter4_analysis_verification.md) ⚠️ 절대 스킵 금지
    |           -> ⚠️ 검증문서 저장 필수 (스킵 불가)
    |           -> 검증문서 경로 안내 후 자동 진행
    |       - Phase 2: 결과 활용 방안 작성
    |       - Phase 3: 기술 사업화/실용화 전략 작성
    |       - Phase 4: 기대효과 및 파급효과 작성
    |       - Phase 5: 정합성 검증 (Chapter 1/3 수치와 일치 확인)
    |
    +-- Step 4-3. 출력 저장
        +-- chapter_4/기대효과.md
        +-- verification/chapter4_analysis_verification.md

[Phase 5: Chapter 5 생성 - 기타 참고자료]
    |
    +-- Step 5-1. 입력 데이터 준비
    |   +-- Chapter 1~4 출력 파일 경로 확인
    |   +-- 섹션 5 (유사 사업 정보) 추출
    |   +-- Chapter 1~4에서 모든 인용 출처 수집
    |   +-- Chapter 3에서 참여기관 목록 추출
    |
    +-- Step 5-2. Chapter 5 생성 실행
    |   +-- chapter5-generator 워크플로우 수행:
    |       - Phase 0: NTIS 유사과제 검색
    |       - Phase 0-3: 검증문서 생성 (chapter5_ntis_verification.md) ⚠️ 절대 스킵 금지
    |           -> ⚠️ 검증문서 저장 필수 (스킵 불가)
    |           -> 검증문서 경로 안내 후 자동 진행
    |       - Phase 1: 선행 문서 분석
    |       - Phase 2: 기존 사업 차별성 작성 (해당 시)
    |       - Phase 3: 유사중복 자체점검 결과 작성
    |       - Phase 4: 참고문헌 작성 (15-25개)
    |       - Phase 5: 참여기관 참여의향서 작성
    |
    +-- Step 5-3. 출력 저장
        +-- chapter_5/기타참고자료.md
        +-- verification/chapter5_ntis_verification.md

[Phase 6: 최종 검증 및 보고서 생성]
    |
    +-- Step 6-1. 전체 정합성 검증
    |   +-- 수치 일치 검증:
    |       - Chapter 3 정량목표 = Chapter 4 기대성과
    |       - Chapter 1 성과지표 = Chapter 4 기대성과
    |   +-- 목록 일치 검증:
    |       - Chapter 3 참여기업 = Chapter 4 사업화전략 기업
    |       - Chapter 1 VoC 기업 포함 Chapter 4 수요기업
    |       - Chapter 3 참여기관 = Chapter 5 참여의향서
    |   +-- 참고문헌 번호 검증:
    |       - Chapter 2 인용번호 = Chapter 5 참고문헌 목록
    |
    +-- Step 6-2. 실행 보고서 생성
    |   +-- assets/output_template/execution_report.md 양식 사용
    |   +-- 각 Chapter별 생성 결과 기록
    |   +-- 검증문서 목록 및 위치 기록
    |   +-- 정합성 검증 결과 기록
    |   +-- 최종 출력 파일 목록 기록
    |
    +-- Step 6-3. 사용자 안내
        +-- 생성 완료 알림
        +-- 검증문서 검토 권장사항 안내
        +-- execution_report.md 위치 안내

[Phase 7: 이미지 생성]
    |
    +-- Step 7-1. 이미지 생성 준비
    |   +-- 전체 출력 문서(chapter_1~5)에서 <캡션> 패턴 추출
    |   +-- figures/, prompts/ 폴더 생성
    |   +-- 일관성 컨텍스트 데이터 수집:
    |       - 프로젝트명
    |       - 참여기관 목록 (Chapter 3에서)
    |       - 핵심 용어 목록 (전체 Chapter에서)
    |       - 연차/단계 구조 (Chapter 3에서)
    |       - 세부기술 이름 (Chapter 3에서)
    |
    +-- Step 7-2. figure-generator 실행 (컨텍스트 전달 강화)
    |   +-- 전달 파라미터 (명시적):
    |       - auto_mode: true (사용자 확인 건너뛰기)
    |       - parallel_mode: true (서브에이전트 병렬화 활성화)
    |       - quality_gate: strict (500줄+ 필수 검증)
    |       - consistency_context: [Step 7-1에서 수집한 데이터]
    |   +-- figure-generator 워크플로우 수행:
    |       - Phase 0: 입력 검증, Python 환경 확인
    |       - Phase 1: 캡션 추출 및 유형별 분류 (확인 없이 자동 진행)
    |       - Phase 2: 상세 프롬프트 생성
    |           - Step 2-1a: 서브에이전트 병렬 생성 (캡션 수 > 5개 시)
    |           - 모든 캡션에 대해 프롬프트 생성 (누락 금지)
    |           - 500줄 이상/캡션, 14섹션 필수
    |       - Phase 3: Gemini API로 이미지 생성 (4K, 16:9)
    |       - Phase 4: 검증 및 누락 이미지 재생성
    |       - Phase 5: figure_generation_report.md 생성
    |   +-- 품질 검증:
    |       - caption_list.md 캡션 수 = prompts/ 파일 수 확인
    |       - 누락 시 Step 7-2 재실행 (누락 캡션만 대상)
    |
    +-- Step 7-3. 출력 저장
        +-- figures/: 생성된 이미지 파일들 (PNG)
        +-- prompts/: 각 이미지의 프롬프트 파일들 (MD)
        +-- prompts/consistency_context.md: 일관성 컨텍스트 문서
        +-- figure_generation_report.md
```

## Token Optimization Strategy

토큰 사용량을 최적화하기 위해 다음 전략을 적용한다:

### 1. 선택적 컨텍스트 로딩

각 Phase에서 해당 Chapter 생성에 필요한 입력 섹션만 로드한다:

| Phase | 로드할 입력 섹션 | 로드할 이전 Chapter |
|-------|-----------------|-------------------|
| Phase 1 | 섹션 1 (연구 아이디어) | 없음 |
| Phase 2 | 섹션 2 (기관 정보) | Chapter 3 요약 |
| Phase 3 | 섹션 3 (분야 키워드) | Chapter 3/1 요약 |
| Phase 4 | 섹션 4 (사업화 정보) | Chapter 1/3 요약 |
| Phase 5 | 섹션 5 (유사사업) | Chapter 1-4 참조정보만 |

### 2. 요약 전달

이전 Chapter 전체를 로드하지 않고 핵심 정보만 추출하여 전달한다:

- Chapter 3 요약: 최종목표, 3축 세부기술, 정량목표, 참여기관
- Chapter 1 요약: 개발대상, 성과지표, VoC 기업
- Chapter 2 요약: 시장규모, 주요 기업, 기술 현황

### 3. 참조 위임

기존 chapter-generator SKILL.md 내용을 복제하지 않고 워크플로우만 참조한다. 각 chapter-generator의 상세 워크플로우는 해당 스킬 실행 시 자동으로 적용된다.

## Output Structure

```
output/[프로젝트명]/
├── chapter_1/
│   ├── 개발대상및필요성.md
│   └── chapter1_references.md
├── chapter_2/
│   ├── 국내외시장및기술동향.md
│   └── chapter2_references.md
├── chapter_3/
│   ├── 연구목표및내용.md
│   └── 이미지생성_프롬프트.md
├── chapter_4/
│   └── 기대효과.md
├── chapter_5/
│   └── 기타참고자료.md
├── verification/
│   ├── chapter3_research_verification.md
│   ├── chapter1_research_verification.md
│   ├── chapter2_research_verification.md
│   ├── chapter4_analysis_verification.md
│   └── chapter5_ntis_verification.md
├── figures/
│   ├── 01_연구개발_목표_및_비전.png
│   ├── 02_기술개발_로드맵.png
│   └── ...
├── prompts/
│   ├── 01_연구개발_목표_및_비전.md
│   ├── 02_기술개발_로드맵.md
│   └── prompt_index.md
├── figure_generation_report.md
└── execution_report.md
```

## Consistency Validation Rules

### 수치 일치 (필수)

| 항목 | 검증 규칙 |
|------|----------|
| 기술이전 건수 | Chapter 3 정량목표 = Chapter 4 기대성과 |
| 기술료 금액 | Chapter 1 성과지표 = Chapter 4 기대성과 |
| 수입대체 금액 | Chapter 1 성과지표 = Chapter 4 기대성과 |

### 목록 일치 (필수)

| 항목 | 검증 규칙 |
|------|----------|
| 참여기업 | Chapter 3 협력전략 = Chapter 4 사업화전략 |
| VoC 기업 | Chapter 1 VoC 기업 포함 Chapter 4 수요기업 |
| 참여기관 | Chapter 3 참여기관 = Chapter 5 참여의향서 |

### 참고문헌 번호 (필수)

- Chapter 2에서 인용한 번호가 Chapter 5 참고문헌 목록에 모두 포함되어야 함

## Error Handling

### 웹 검색 실패 시

- 재시도: 최대 2회 재검색
- 대체: 기존 참조 데이터 활용
- 기록: 실행 보고서에 검색 실패 항목 명시

### Chapter 생성 실패 시

- 중단점 저장: 마지막 성공 Chapter 기록
- 재시작: 실패 Chapter부터 재실행 가능
- 보고: 실패 원인 및 해결 방안 제시

### 정합성 검증 실패 시

- 경고: 실행 보고서에 불일치 항목 명시
- 계속: 생성 완료 후 사용자 검토 요청
- 제안: 수정 필요 Chapter 및 항목 안내

## Usage Example

```
orchestrator-generator 스킬을 사용해서 ISD 연구계획서를 생성해줘.
입력 파일: ./my_project_input.md
```

또는

```
다음 입력 파일로 연구계획서 전체를 자동 생성해줘.

입력 파일 경로: /path/to/input_template.md
```

## Resources

### 참조 파일

- references/input_template.md: 사용자 입력 양식 템플릿

### 출력 템플릿

- assets/output_template/execution_report.md: 실행 보고서 템플릿

### 관련 스킬

- chapter3-generator: Chapter 3 생성 워크플로우
- chapter1-generator: Chapter 1 생성 워크플로우
- chapter2-generator: Chapter 2 생성 워크플로우
- chapter4-generator: Chapter 4 생성 워크플로우
- chapter5-generator: Chapter 5 생성 워크플로우
- figure-generator: 이미지 생성 워크플로우
