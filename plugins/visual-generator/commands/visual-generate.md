# Visual Generator Orchestrator

## Overview

시각자료 생성을 위한 통합 오케스트레이터. 입력 문서를 분석하여 핵심 개념을 추출하고, 테마와 레이아웃을 선택한 후, 4-block 프롬프트를 생성하여 최종 이미지를 렌더링한다.

**에이전트 파이프라인:**
```
content-organizer → content-reviewer → prompt-designer → renderer-agent
```

## Input Schema

| 필드 | 설명 | 필수 | 기본값 |
|------|------|:----:|--------|
| `input_document` | 입력 문서 경로 (연구계획서, 사업계획서, 기술문서 등) | ✓ | - |
| `theme` | 테마 선택 (9종: technical-report, clarity, tech-focus, growth, connection, innovation, knowledge, presentation, workshop) | - | clarity |
| `layout` | 레이아웃 유형 (24종 중 선택, 예: 비전-다이어그램, 기술-스펙, 협력체계 등) | - | 자동 선택 |
| `output_folder` | 출력 폴더 경로 | ✓ | - |
| `auto_mode` | 자동 파이프라인 실행 여부 | - | true |
| `style` | 스타일 유형 (concept, gov, seminar, whatif, pitch, comparison) | - | gov |

### 입력 예시

```
visual-generator-orchestrator 에이전트를 사용해서 시각자료를 생성해줘.

입력 문서: ./research_proposal.md
테마: tech-focus
스타일: gov
출력 폴더: ./output/visuals/
```

## Workflow

```
[Phase 0: 입력 검증 및 초기화]
    |
    +-- Step 0-1. 입력 파라미터 검증
    |   +-- input_document 파일 존재 여부 확인
    |   +-- theme 유효성 검증 (9종 중 하나)
    |   +-- layout 유효성 검증 (24종 참조: layout-types 스킬)
    |   +-- style 유효성 검증 (concept, gov, seminar, whatif, pitch, comparison)
    |
    +-- Step 0-2. 출력 디렉토리 구조 생성 (Bash 도구 사용, Read/Glob으로 디렉토리를 확인하지 말 것)
        +-- Bash: mkdir -p {output_folder}/analysis {output_folder}/prompts {output_folder}/images {output_folder}/reports
        +-- 주의: 디렉토리 존재 여부를 Read로 확인하지 않음. mkdir -p는 이미 존재해도 안전함.

[Phase 1: 문서 분석 - content-organizer]
    |
    +-- Step 1-1. content-organizer 호출
    |   +-- Task(subagent_type="visual-generator:content-organizer") 호출
    |   +-- 전달 파라미터:
    |       - input_document: 입력 문서 경로
    |       - style: 스타일 유형
    |       - output_path: {output_folder}/analysis/
    |       - auto_mode: true
    |
    +-- Step 1-2. 출력 확인
    |   +-- {output_folder}/analysis/concepts.md (핵심 개념 목록)
    |   +-- {output_folder}/analysis/slide_plan.md (슬라이드 구성 계획)
    |   +-- {output_folder}/analysis/theme_recommendation.md (테마/레이아웃 추천)
    |
    +-- Step 1-3. 실패 시 처리
        +-- 에러 로그 저장: {output_folder}/reports/phase1_error.log
        +-- 롤백: 생성된 파일 삭제
        +-- 사용자에게 입력 문서 검토 요청

[Phase 2: 콘텐츠 검토 - content-reviewer]
    |
    +-- Step 2-1. content-reviewer 호출
    |   +-- Task(subagent_type="visual-generator:content-reviewer") 호출
    |   +-- 전달 파라미터:
    |       - analysis_path: {output_folder}/analysis/
    |       - original_document: input_document
    |       - auto_mode: true
    |
    +-- Step 2-2. 검토 결과 처리
    |   +-- PASS: Phase 3로 진행
    |   +-- NEEDS_REVISION: content-organizer 재호출 (최대 2회)
    |   +-- FAIL: 사용자 개입 요청
    |
    +-- Step 2-3. 출력 확인
        +-- {output_folder}/analysis/review_result.md
        +-- {output_folder}/analysis/concepts_revised.md (수정된 경우)

[Phase 3: 프롬프트 생성 - prompt-designer]
    |
    +-- Step 3-1. prompt-designer 호출
    |   +-- Task(subagent_type="visual-generator:prompt-designer") 호출
    |   +-- 전달 파라미터:
    |       - concepts_path: {output_folder}/analysis/concepts.md (또는 concepts_revised.md)
    |       - slide_plan_path: {output_folder}/analysis/slide_plan.md
    |       - theme: 선택된 테마 또는 추천 테마
    |       - layout: 선택된 레이아웃 또는 자동 선택
    |       - style: 스타일 유형 (concept, gov, seminar, whatif, pitch, comparison)
    |       - output_path: {output_folder}/prompts/
    |       - auto_mode: true
    |
    +-- Step 3-2. 출력 확인
    |   +-- {output_folder}/prompts/01_*.md
    |   +-- {output_folder}/prompts/02_*.md
    |   +-- ...
    |   +-- {output_folder}/prompts/prompt_index.md
    |
    +-- Step 3-3. 품질 검증
        +-- 각 프롬프트 파일 100줄 이상 확인
        +-- 4-block 구조 검증 (INSTRUCTION, CONFIGURATION, CONTENT, FORBIDDEN)
        +-- 미달 시 재생성 요청 (최대 2회)

[Phase 4: 이미지 렌더링 - renderer-agent]
    |
    +-- Step 4-1. renderer-agent 호출
    |   +-- Task(subagent_type="visual-generator:renderer-agent") 호출
    |   +-- 전달 파라미터:
    |       - prompts_path: {output_folder}/prompts/
    |       - output_path: {output_folder}/images/
    |       - auto_mode: true
    |
    +-- Step 4-2. 출력 확인
    |   +-- {output_folder}/images/01_*.png
    |   +-- {output_folder}/images/02_*.png
    |   +-- ...
    |   +-- {output_folder}/images/generation_report.md
    |
    +-- Step 4-3. 품질 검증
        +-- 이미지 파일 생성 확인
        +-- 프롬프트 수 = 이미지 수 검증
        +-- 누락 시 해당 프롬프트만 재렌더링

[Phase 5: 최종 보고서 생성]
    |
    +-- Step 5-1. 실행 결과 수집
    |   +-- 각 Phase별 성공/실패 상태
    |   +-- 생성된 파일 목록
    |   +-- 경고 및 에러 로그
    |
    +-- Step 5-2. 실행 보고서 생성
    |   +-- {output_folder}/reports/execution_report.md
    |   +-- 내용:
    |       - 입력 파라미터 요약
    |       - 각 Phase별 실행 결과
    |       - 생성된 파일 목록 및 경로
    |       - 에러 및 경고 사항
    |       - 사용자 검토 권장사항
    |
    +-- Step 5-3. 사용자 안내
        +-- 생성 완료 알림
        +-- 출력 폴더 경로 안내
        +-- 검토 권장사항 안내
```

## auto_mode 동작

| 설정 | auto_mode=true | auto_mode=false |
|------|----------------|-----------------|
| Phase 간 확인 | 자동 진행 | 사용자 확인 대기 |
| 검토 결과 처리 | 자동 재시도 | 사용자 선택 요청 |
| 에러 발생 시 | 자동 롤백 후 보고 | 사용자 개입 요청 |
| 테마/레이아웃 | 추천값 자동 적용 | 사용자 선택 요청 |

## Error Handling

### 에러 유형별 처리

| 에러 유형 | 처리 방법 | 최대 재시도 |
|-----------|-----------|:-----------:|
| 입력 파일 없음 | 즉시 중단, 사용자에게 경로 확인 요청 | 0 |
| 문서 분석 실패 | content-organizer 재호출 | 2 |
| 검토 NEEDS_REVISION | content-organizer 재호출 | 2 |
| 프롬프트 품질 미달 | prompt-designer 재호출 | 2 |
| 이미지 렌더링 실패 | 해당 프롬프트만 재렌더링 | 3 |
| API 오류 | 2초 대기 후 재시도 | 3 |

### 롤백 로직

```
[롤백 트리거]
    +-- Phase 1 실패 (3회 초과): 전체 롤백
    +-- Phase 2 실패 (3회 초과): Phase 1 출력 유지, Phase 2 출력 삭제
    +-- Phase 3 실패 (3회 초과): Phase 1-2 출력 유지, Phase 3 출력 삭제
    +-- Phase 4 실패 (3회 초과): Phase 1-3 출력 유지, 부분 이미지 삭제

[롤백 동작]
    +-- 해당 Phase 출력 폴더 삭제
    +-- 에러 로그 저장
    +-- 사용자에게 재시작 지점 안내
```

### 중단점 복구

실패 시 중단점이 저장되어 해당 Phase부터 재시작 가능:

```
[중단점 파일]: {output_folder}/reports/checkpoint.json
{
  "last_success_phase": 2,
  "failed_phase": 3,
  "error_message": "프롬프트 품질 미달",
  "retry_count": 2,
  "timestamp": "2026-02-05T10:30:00"
}
```

재시작 명령:
```
visual-generator-orchestrator 에이전트로 이어서 생성해줘.
체크포인트: ./output/visuals/reports/checkpoint.json
```

## Output Structure

```
{output_folder}/
├── analysis/
│   ├── concepts.md               # 핵심 개념 목록
│   ├── concepts_revised.md       # 수정된 개념 (있는 경우)
│   ├── slide_plan.md             # 슬라이드 구성 계획
│   ├── theme_recommendation.md   # 테마/레이아웃 추천
│   └── review_result.md          # 검토 결과
├── prompts/
│   ├── 01_비전_다이어그램.md
│   ├── 02_기술_스펙.md
│   ├── ...
│   └── prompt_index.md           # 프롬프트 인덱스
├── images/
│   ├── 01_비전_다이어그램.png
│   ├── 02_기술_스펙.png
│   ├── ...
│   └── generation_report.md      # 이미지 생성 보고서
└── reports/
    ├── execution_report.md       # 실행 보고서
    ├── checkpoint.json           # 중단점 (실패 시)
    └── phase{N}_error.log        # 에러 로그 (실패 시)
```

## Sub-Agent References

| Agent | 역할 | Task 호출 |
|-------|------|-----------|
| content-organizer | 문서 분석, 핵심 개념 추출, 테마/레이아웃 선택 | `Task(subagent_type="visual-generator:content-organizer")` |
| content-reviewer | content-organizer 출력 검토 및 피드백 | `Task(subagent_type="visual-generator:content-reviewer")` |
| prompt-designer | 4-block 프롬프트 생성 | `Task(subagent_type="visual-generator:prompt-designer")` |
| renderer-agent | 최종 검증 및 이미지 렌더링 | `Task(subagent_type="visual-generator:renderer-agent")` |

## Resources

### 등록된 스킬 (컨텍스트에 자동 로드)

| 스킬명 | 설명 |
|--------|------|
| `layout-types` | 24종 레이아웃 유형 정의 |
| `theme-concept` | concept 스타일 테마 (TED 미니멀, 9종 무드 팔레트) |
| `theme-gov` | gov 스타일 테마 (정부/공공기관, 9종 무드 팔레트) |
| `theme-seminar` | seminar 스타일 테마 (세미나/발표, 9종 무드 팔레트) |
| `theme-whatif` | whatif 목적 테마 (미래 비전 스냅샷) |
| `theme-pitch` | pitch 목적 테마 (피치덱) |
| `theme-comparison` | comparison 목적 테마 (Before/After) |

### 테마 목록 (9종)

| 번호 | 영문명 | 한글명 | 용도 |
|:----:|--------|--------|------|
| 1 | technical-report | 기술 보고서 | 전문성, 신뢰감 강조 |
| 2 | clarity | 명료 | 깔끔하고 명확한 전달 |
| 3 | tech-focus | 테크 | 기술 중심, 첨단 이미지 |
| 4 | growth | 성장 | 발전, 성장 강조 |
| 5 | connection | 연결 | 네트워크, 협력 강조 |
| 6 | innovation | 혁신 | 창의성, 혁신 강조 |
| 7 | knowledge | 지식 | 학술적, 교육적 콘텐츠 |
| 8 | presentation | 발표 | 프레젠테이션용 |
| 9 | workshop | 워크숍 | 워크숍, 실습용 |

## MUST DO

- [ ] 입력 파라미터 검증 후 워크플로우 시작
- [ ] 각 Phase 완료 후 출력 파일 존재 확인
- [ ] content-reviewer 검토 결과에 따라 재시도 또는 진행 결정
- [ ] 프롬프트 품질 검증 (100줄 이상, 4-block 구조)
- [ ] 에러 발생 시 롤백 로직 실행
- [ ] 최종 execution_report.md 생성

## MUST NOT DO

- [ ] 검증 없이 다음 Phase로 진행하지 않음
- [ ] 재시도 횟수 초과 시 무한 루프 방지
- [ ] 중간 파일 없이 최종 결과만 생성하지 않음
- [ ] 에러 로그 없이 실패 처리하지 않음
- [ ] `${CLAUDE_PLUGIN_ROOT}` 변수 사용하지 않음 (상대 경로 사용)
- [ ] 직접 문서를 분석하지 않음 (content-organizer에 위임 필수)
- [ ] 직접 분석 결과를 검토하지 않음 (content-reviewer에 위임 필수)
- [ ] 직접 프롬프트를 생성하지 않음 (prompt-designer에 위임 필수)
- [ ] 직접 이미지를 렌더링하지 않음 (renderer-agent에 위임 필수)
- [ ] Task(subagent_type=...) 없이 파이프라인 단계를 수행하지 않음

## Usage Examples

### 기본 사용

```
visual-generator-orchestrator 에이전트를 사용해서 시각자료를 생성해줘.

입력 문서: ./docs/research_proposal.md
출력 폴더: ./output/visuals/
```

### 테마 지정

```
visual-generator-orchestrator 에이전트로 시각자료를 생성해줘.

입력 문서: ./docs/business_plan.md
테마: innovation
스타일: concept
출력 폴더: ./output/presentation/
```

### 체크포인트에서 재시작

```
visual-generator-orchestrator 에이전트로 이어서 생성해줘.

체크포인트: ./output/visuals/reports/checkpoint.json
```
