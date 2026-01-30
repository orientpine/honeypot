---
name: four-step-pattern
description: "Four-step sentence pattern for national research reports. Defines mandatory writing structure: task declaration, problem definition, solution approach, and technical details."
---

# Four-Step Pattern Skill

## Overview

This skill defines the mandatory 4-step sentence pattern for writing national research report sections. Each subsection (1.1, 1.2, 2.1, etc.) must follow this pattern to meet PhD-level professionalism and national agency submission requirements.

---

## The 4-Step Pattern

### Step 1: Task Declaration (연구 과제 선언)

**Pattern:**
```
- 본 사업에서 맡은 주요 연구 과제는 [기술 분야]를 위한 [개발 시스템명] 개발임
```

**Rules:**
- Must start with "본 사업에서 맡은 주요 연구 과제는"
- [기술 분야]: Technical domain (e.g., "굴착기 자율화", "실시간 제어", "강화학습 기반 의사결정")
- [개발 시스템명]: Specific, technical system name (e.g., "CAN 통신 기반 다중 센서 데이터 수집 및 융합 시스템")
- Must end with "개발임"

**Examples:**
- "본 사업에서 맡은 주요 연구 과제는 굴착기 자율화를 위한 CAN 통신 기반 다중 센서 데이터 수집 및 융합 시스템 개발임"
- "본 사업에서 맡은 주요 연구 과제는 3자유도(3-DOF) 평면 굴착기의 정기구학 연산을 통한 버킷 끝단 위치 실시간 계산 시스템 개발임"
- "본 사업에서 맡은 주요 연구 과제는 강화학습(Reinforcement Learning) 기반 자율 굴착 의사결정 시스템 개발임"

---

### Step 2: Problem Definition and Necessity (문제 정의 및 필요성)

**Pattern:**
```
- [기존 방식/상황]으로는 [문제점/한계]이므로, [해결책/목표 시스템] 구축이 필요함
```

**Rules:**
- [기존 방식/상황]: Current technology limitations or existing approach
- [문제점/한계]: Specific technical problems
- [해결책/목표 시스템]: Proposed solution in this research
- Must end with "구축이 필요함" or "시스템 개발이 필요함"

**Examples:**
- "기존의 개별 센서 운용 방식으로는 실시간 동기화 및 데이터 일관성 확보가 어려우므로, 통합 CAN 버스 아키텍처를 통한 센서 융합 시스템 구축이 필요함"
- "기존 포텐셔미터 기반 각도 측정은 기계적 마모와 환경 변화에 취약하므로, CANopen 기반 고정밀 경사계를 통한 관절 각도 측정 시스템 구축이 필요함"
- "자율 굴착 작업 중 유압 과부하 및 장비 손상을 방지하기 위해, 실시간 유압 압력 모니터링과 이상 감지 시스템 구축이 필요함"

---

### Step 3: Solution Approach (해결 방안)

**Pattern:**
```
- 이를 위해 [노드/모듈/클래스명] 개발을 통한 [기술 구현 내용] 수행
```

**Rules:**
- Must start with "이를 위해"
- [노드/모듈/클래스명]: Actual implementation name (e.g., can_bridge_node, ExcavatorKinematics 클래스)
- [기술 구현 내용]: Specific tech stack and interfaces
- Multiple implementations should be separate bullet points

**Examples:**
- "이를 위해 can_bridge_node 개발을 통한 SocketCAN 기반 실시간 CAN 통신 인터페이스 구현 및 CAN ID별 메시지 파싱 시스템 개발"
- "이를 위해 forward_kinematics_node 개발을 통한 20Hz 주기 정기구학 연산 시스템 구현 및 실시간 버킷 위치 발행 인터페이스 개발"
- "이를 위해 trajectory_generator_node 개발을 통한 /excavator/trajectory_generator 서비스 서버 구현 및 작업 유형별 궤적 생성 알고리즘 개발"

---

### Step 4: Technical Details (기술적 상세)

**Patterns:**
```
- [구체적 구현체/설정 파일] 설정을 통해 [파라미터1], [파라미터2], [파라미터3] 구현
- [알고리즘명] 기반 [세부 기능] 구현
- [구체적 수치/설정]: [값1](설명), [값2](설명) 등
```

**Rules:**
- Must include specific parameter values with units
- Algorithm names should include English (e.g., 게인 스케줄링(Gain Scheduling))
- Config file names, variable names, function names must match actual code
- Use exact values (no estimates)

**Examples:**
- "can_config.yaml 설정 파일을 통해 CAN 인터페이스(can0), 비트레이트(500kbps), 디바이스별 CAN ID 매핑 체계 구현"
- "fk_excavator 함수 구현: 관절 각도(θ₁, θ₂, θ₃)로부터 버킷 끝단 위치(xk, yk) 및 자세(φ_e) 계산"
- "굴착기 기하학 파라미터 적용: L1=2464mm(Boom), L2=1352mm(Arm), L3=830mm(Bucket), a1=930mm(수평 오프셋), h1=1130mm(수직 오프셋)"
- "관절별 PI 게인 튜닝: Swing(Kp=6.0, Ki=0.0), Boom(Kp=12.0, Ki=2.0), Arm(Kp=16.0, Ki=2.0), Bucket(Kp=10.0, Ki=1.0)"

---

## Complete Section Example

```markdown
### 1.1. CAN 통신 기반 다중 센서 데이터 수집 및 융합 시스템 구축

- 본 사업에서 맡은 주요 연구 과제는 굴착기 자율화를 위한 CAN 통신 기반 다중 센서 데이터 수집 및 융합 시스템 개발임
- 기존의 개별 센서 운용 방식으로는 실시간 동기화 및 데이터 일관성 확보가 어려우므로, 통합 CAN 버스 아키텍처를 통한 센서 융합 시스템 구축이 필요함
- 이를 위해 can_bridge_node 개발을 통한 SocketCAN 기반 실시간 CAN 통신 인터페이스 구현 및 CAN ID별 메시지 파싱 시스템 개발
- can_config.yaml 설정 파일을 통해 CAN 인터페이스(can0), 비트레이트(500kbps), 디바이스별 CAN ID 매핑 체계 구현
- 다중 센서 동시 수신을 위한 멀티스레드 아키텍처 구현 및 센서 데이터 타임스탬프 동기화 시스템 구축

그림. CAN 통신 기반 센서 융합 시스템 아키텍처
```

---

## Figure Captions

Each section must end with a figure caption.

**Pattern:**
```
그림. [구체적 기술 설명]
```

### Caption Type Selection

| 섹션 특성 | 캡션 유형 | 예시 |
|----------|----------|------|
| 시스템 구조 | 아키텍처 | "~ 시스템 아키텍처" |
| 알고리즘 흐름 | 흐름도 | "~ 알고리즘 흐름도" |
| 데이터 흐름 | 블록 다이어그램 | "~ 데이터 흐름도" |
| 조직/역할 | 구성도 | "~ 구성도" |
| 시간순 프로세스 | 로드맵 | "~ 로드맵" |
| 제어 시스템 | 블록 다이어그램 | "~ 블록 다이어그램" |

---

## Prohibited Practices

### 1. Abstract Expressions (추상적 표현 금지)

❌ "시스템을 개발하였음"
✅ "can_bridge_node를 통한 SocketCAN 기반 실시간 CAN 통신 인터페이스를 구현함"

### 2. Missing Numeric Values (수치 누락 금지)

❌ "높은 주기로 연산"
✅ "20Hz 주기로 연산"

### 3. Missing Algorithm Names (알고리즘명 누락 금지)

❌ "제어 알고리즘 적용"
✅ "게인 스케줄링(Gain Scheduling) 알고리즘 적용"

### 4. Missing Units (단위 누락 금지)

❌ "길이 2464"
✅ "길이 2464mm"

---

## Domain-Specific Term Substitution

Replace generic terms with domain-specific terms based on research field:

| 범용 용어 | ROS2 | AI/ML | 물리학 |
|----------|------|-------|--------|
| 모듈 | 노드 | 모듈/레이어 | 모듈 |
| 처리 | 퍼블리시 | 추론 | 연산 |
| 설정 | 파라미터 | 하이퍼파라미터 | 파라미터 |
| 연결 | 토픽/서비스 | 레이어 연결 | 인터페이스 |
| 입력 | 구독 | 입력 텐서 | 입력 신호 |
| 출력 | 발행 | 출력 텐서 | 출력 신호 |

---

## Validation Checklist

For each subsection, verify:

- [ ] Step 1: Starts with "본 사업에서 맡은 주요 연구 과제는", ends with "개발임"
- [ ] Step 2: Contains "이므로" and "구축이 필요함"
- [ ] Step 3: Starts with "이를 위해", includes implementation name
- [ ] Step 4: Includes specific parameters with units
- [ ] Figure caption present at end
- [ ] No abstract expressions
- [ ] All numeric values have units
- [ ] Algorithm names include English translation
- [ ] Domain-specific terms used correctly
