---
name: chapter-structure
description: "Research report chapter structure definition. Defines 9 candidate chapters, content mapping rules, and sufficiency evaluation criteria for national research reports."
---

# Chapter Structure Skill

## Overview

This skill defines the standard chapter structure for national research reports. It includes:

1. **9 Candidate Chapters**: Maximum chapter structure
2. **Content Mapping Rules**: How to map research notes to chapters
3. **Sufficiency Evaluation**: Criteria for chapter generation/skipping
4. **Appendix Structure**: Parameter tables and package listings

---

## Report Structure

```
# [프로젝트명] 연구보고서

>[!info]
>**Author**: [작성자명]
>**Created**: `=dateformat(this.file.ctime, "DDDD, HH:mm")`
>**Modified**: `=dateformat(this.file.mtime, "DDDD, HH:mm")`
>**Location**: `=this.file.path`
>**Tag**: #[태그1] #[태그2] #[태그3]

---

## 1. [챕터1 제목]
### 1.1. [소제목]
### 1.2. [소제목]

## 2. [챕터2 제목]
...

## N. 결론

---

## 부록 A. 시스템 파라미터 요약
## 부록 B. 패키지/모듈 구성
```

---

## 9 Candidate Chapters

| 번호 | 챕터 제목 | 핵심 내용 | 매핑 키워드 |
|:----:|----------|----------|------------|
| 1 | 하드웨어 통합 및 센서 융합 시스템 | 물리적 장치 연결, 센서 데이터 수집, 통신 프로토콜 | 센서, 통신, CAN, 하드웨어, 인터페이스, 융합, 버스 |
| 2 | 핵심 연산 시스템 | 기구학, 수학적 모델링, 알고리즘 연산 | 기구학, 연산, 알고리즘, 수학, 모델, 변환, 계산 |
| 3 | 생성/계획 시스템 | 궤적 생성, 경로 계획, 작업 시퀀스 관리 | 궤적, 경로, 계획, 생성, 시퀀스, 스케줄링 |
| 4 | 제어 시스템 | 피드백 제어, PID/PI 제어기, 게인 튜닝 | 제어, PID, PI, 피드백, 게인, 튜닝, 컨트롤러 |
| 5 | AI/학습 시스템 | 강화학습, 신경망, 추론 시스템 | AI, 학습, 추론, 강화학습, 신경망, 모델, 훈련 |
| 6 | 통신 인터페이스 설계 | 메시지 정의, 서비스/액션, 노드 토폴로지 | 메시지, 서비스, 토픽, API, 프로토콜, 인터페이스 |
| 7 | 시스템 통합 및 검증 | HMI 개발, 시뮬레이션, 테스트 | 테스트, HMI, 시뮬레이션, GUI, 검증, 통합 |
| 8 | 시스템 안정성 및 오류 처리 | 안전 시스템, 오류 복구, 재시도 로직 | 안전, 에러, 복구, 재시도, 타임아웃, 비상 |
| 9 | 결론 | 연구 성과 요약, 기술적 기여, 향후 과제 | (자동 생성) |

---

## Chapter Templates

### Chapter 1: 하드웨어 통합 및 센서 융합 시스템

```markdown
## 1. [대상 시스템] 하드웨어 통합 및 센서 융합 시스템

### 1.1. [통신 프로토콜] 기반 다중 센서 데이터 수집 및 융합 시스템 구축
[4단계 패턴 적용]
그림. [통신 프로토콜] 기반 센서 융합 시스템 아키텍처

### 1.2. [센서 유형] 센서 통합 및 [측정 대상] 측정 시스템 개발
[4단계 패턴 적용]
그림. [센서 유형] 센서 배치 및 측정 체계

### 1.3. [모니터링 대상] 모니터링 및 센서 상태 관리 시스템 개발
[4단계 패턴 적용]
그림. [모니터링 대상] 모니터링 아키텍처
```

### Chapter 2: 핵심 연산 시스템

```markdown
## 2. 핵심 연산 시스템 개발

### 2.1. [DOF]자유도 [시스템] 정기구학(Forward Kinematics) 연산 시스템 개발
[4단계 패턴 적용]
그림. [DOF]자유도 [시스템] 정기구학 연산 체계

### 2.2. 역기구학(Inverse Kinematics) 연산 시스템 개발
[4단계 패턴 적용]
그림. 역기구학 연산 알고리즘 흐름도
```

### Chapter 3: 생성/계획 시스템

```markdown
## 3. [생성/계획 대상] 생성 시스템 개발

### 3.1. 작업 유형별 [생성 대상] 생성 시스템 개발
[4단계 패턴 적용]
그림. 작업 유형별 [생성 대상] 생성 체계

### 3.2. 통합 작업 관리(Task Management) 시스템 개발
[4단계 패턴 적용]
그림. 통합 작업 관리 시스템 아키텍처
```

### Chapter 4: 제어 시스템

```markdown
## 4. 제어 시스템 개발

### 4.1. [상위 시스템] 제어 시스템 개발
[4단계 패턴 적용]
그림. [상위 시스템] [제어기 유형] 제어 시스템 블록 다이어그램

### 4.2. [하위 시스템] 제어 시스템 개발
[4단계 패턴 적용]
그림. [하위 시스템] 제어 시스템 구성도
```

### Chapter 5: AI/학습 시스템

```markdown
## 5. AI [학습 방법론] 기반 [적용 분야] 시스템 개발

### 5.1. [학습 방법론] 모델 통합 및 에피소드 관리 시스템 개발
[4단계 패턴 적용]
그림. [학습 방법론] 기반 [적용 분야] 시스템 아키텍처

### 5.2. [입력 데이터] 기반 관측 공간 변환 시스템 개발
[4단계 패턴 적용]
그림. 관측 공간 변환 및 액션 마스크 생성 체계

### 5.3. 에피소드 종료 조건 및 성공 판정 시스템 개발
[4단계 패턴 적용]
그림. 에피소드 종료 조건 판정 흐름도
```

### Chapter 6: 통신 인터페이스 설계

```markdown
## 6. [프레임워크] 통신 인터페이스 설계

### 6.1. Custom 메시지/서비스/액션 인터페이스 설계
[4단계 패턴 적용]
그림. [프레임워크] Custom 인터페이스 메시지 구조

### 6.2. 노드 간 통신 토폴로지 설계
[4단계 패턴 적용]
그림. [프레임워크] 노드 간 통신 토폴로지
```

### Chapter 7: 시스템 통합 및 검증

```markdown
## 7. 시스템 통합 및 검증

### 7.1. 테스트 HMI 시스템 개발
[4단계 패턴 적용]
그림. 테스트 HMI 시스템 화면 구성

### 7.2. 시뮬레이션 환경 구축
[4단계 패턴 적용]
그림. 시뮬레이션 환경 구성도
```

### Chapter 8: 시스템 안정성 및 오류 처리

```markdown
## 8. 시스템 안정성 및 오류 처리

### 8.1. 안전 시스템 및 비상 정지 체계 구축
[4단계 패턴 적용]
그림. 안전 시스템 구성 및 동작 흐름

### 8.2. 오류 복구 및 재시도 시스템 구축
[4단계 패턴 적용]
그림. 오류 복구 및 재시도 시스템 흐름도
```

### Chapter 9: 결론 (필수)

```markdown
## 9. 결론

본 연구에서는 [기술 스택] 기반 [프로젝트명]을 개발함. 총 [N]개의 [모듈 단위]로 구성된 시스템은 [핵심 기능 1], [핵심 기능 2], [핵심 기능 3] 등 [적용 분야]에 필요한 핵심 기능을 구현함.

주요 기술적 성과:
- [성과 1]: [구체적 기술 구현 내용]
- [성과 2]: [구체적 기술 구현 내용]
- [성과 3]: [구체적 기술 구현 내용]
- [성과 4]: [구체적 기술 구현 내용]
- [성과 5]: [구체적 기술 구현 내용]

본 시스템은 [검증 방법]을 통해 [적용 분야] 작업의 가능성을 확인하였으며, 향후 [확장 방향]으로의 확장이 가능함.
```

---

## Appendix Structure

### Appendix A: 시스템 파라미터 요약

```markdown
## 부록 A. 시스템 파라미터 요약

| 구분 | 파라미터 | 값 | 단위 |
|------|----------|------|------|
| [카테고리1] | [파라미터명] | [값] | [단위] |
| [카테고리1] | [파라미터명] | [값] | [단위] |
| [카테고리2] | [파라미터명] | [값] | [단위] |
| ... | ... | ... | ... |
```

**카테고리 예시:**
- 기구학: 링크 길이, 오프셋, 관절 제한
- 제어: 제어 주기, 게인 값, 임계값
- 안전: 압력 임계값, 온도 제한
- 재시도: 최대 횟수, 대기 시간

### Appendix B: 패키지/모듈 구성

```markdown
## 부록 B. [시스템명] 패키지 구성

| 패키지 | 주요 노드/모듈 | 역할 |
|--------|---------------|------|
| [패키지1] | [노드 목록] | [역할 설명] |
| [패키지2] | [노드 목록] | [역할 설명] |
| ... | ... | ... |
```

---

## Sufficiency Evaluation

Each chapter's generation is determined by a sufficiency score (0-100):

| 평가 항목 | 가중치 | 설명 |
|----------|:------:|------|
| 키워드 빈도 | 40% | 해당 챕터 키워드가 연구 노트에 등장하는 횟수 |
| 헤더 존재 | 30% | 관련 섹션/헤더가 연구 노트에 존재하는지 여부 |
| 파라미터/수치 | 30% | 구체적인 파라미터, 수치, 설정값 포함 여부 |

### Score Calculation

```
sufficiency_score = 
  (keyword_score * 0.4) +
  (header_score * 0.3) +
  (parameter_score * 0.3)

keyword_score:
  - Count keyword occurrences
  - primary_keyword * 3 weight
  - Normalize: min(count / 10 * 100, 100)

header_score:
  - Count related headers
  - Exact match * 2 weight
  - Normalize: min(count / 5 * 100, 100)

parameter_score:
  - Numeric values with units: 20 points
  - Configuration values: 15 points
  - Algorithm/function names: 15 points
  - Normalize: min(total, 100)
```

### Thresholds

- **< 30 points**: Skip chapter
- **≥ 30 points**: Generate chapter
- **Minimum guarantee**: 3 chapters (top 2 scores + conclusion)
- **Conclusion**: Always generated

---

## Chapter Renumbering

When chapters are skipped, renumber remaining chapters sequentially:

**Example:**
- Original: 1(하드웨어), 4(제어), 5(AI), 9(결론)
- Renumbered: 1(하드웨어), 2(제어), 3(AI), 4(결론)

Chapter titles retain original topics after renumbering.
