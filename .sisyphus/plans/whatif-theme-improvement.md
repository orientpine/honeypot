# whatif.md 테마 개선 계획

## TL;DR

> **Quick Summary**: `whatif.md` 테마를 comparison과 명확히 차별화하여 "미래 비전 스냅샷" 컨셉으로 재작성
> 
> **Deliverables**:
> - `plugins/visual-generator/references/themes/whatif.md` 전면 개편
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - 단일 파일 수정
> **Critical Path**: Task 1 (단일 작업)

---

## Context

### Original Request
comparison과 whatif 테마 간 차이가 불명확함. comparison은 좋으나, whatif는 확실한 미래 상을 보여줘야 함.

### 분석 결과
| 현재 문제 | 원인 |
|----------|------|
| whatif가 약한 comparison처럼 읽힘 | Section-Flow 레이아웃이 프로세스 설명처럼 보임 |
| "미래 장면" 개념이 추상적 | 구체적 장면 구성 가이드 없음 |
| 두 테마 선택 기준 불명확 | comparison vs whatif 명시적 비교표 없음 |

---

## Work Objectives

### Core Objective
whatif.md를 "단일 미래 장면 몰입" 테마로 재정의하여 comparison과 명확히 구분

### Concrete Deliverables
- `plugins/visual-generator/references/themes/whatif.md` 전면 개편

### Definition of Done
- [x] comparison vs whatif 차이표 존재
- [x] "Scene Composition" 섹션 (WHO, DOING, WHERE, RESULT, WHEN)
- [x] "Immersion Techniques" 섹션
- [x] 좋은 예 / 나쁜 예 구체적 장면 묘사
- [x] "Before 언급 금지" 규칙 명시

### Must Have
- comparison과의 명확한 차별점 설명
- 장면 구성 5요소 가이드
- 구체적 좋은 예/나쁜 예

### Must NOT Have (Guardrails)
- Before/After 비교 구조 (comparison 영역)
- 추상적 "미래가 좋아진다" 표현
- 프로세스 설명 레이아웃

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: N/A (문서 수정)
- **Automated tests**: None
- **Agent-Executed QA**: YES

---

## TODOs

- [x] 1. whatif.md 전면 개편

  **What to do**:
  1. 기존 whatif.md 읽기
  2. 아래 새 컨텐츠로 **전체 교체** (Edit 아닌 Write 사용)
  
  **새 컨텐츠 구조**:
  ```
  # What-If (미래 비전 스냅샷) 테마
  
  ## 개요
  - 핵심 원칙: "Before가 없다. 이미 After 안에 서 있다."
  
  ## Comparison과의 차이 (CRITICAL)
  - 구조/관점/초점/수치/시제/감정 비교표
  - 선택 가이드
  
  ## 색상 팔레트
  - 기존 유지 (틸, 블루, 오렌지, 크림)
  
  ## 권장 레이아웃
  - Future Snapshot (최우선) - 단일 장면 집중
  - Hero Statement (강조형) - 대형 선언문 + 하단 장면들
  
  ## Scene Composition (장면 구성 필수 요소)
  - WHO: 행위자 (실제 사용자/수혜자)
  - DOING: 행동 (정지 상태 금지)
  - WHERE: 환경 (맥락 배경)
  - RESULT: 성과 지표 (장면 안에 자연스럽게)
  - WHEN: 시간 단서 (일상 암시)
  
  ## Immersion Techniques (몰입 기법)
  - 현재형으로 말하기
  - 구체적 수치 배치
  - 관점 설정 (1인칭/3인칭/시스템)
  
  ## 장면 묘사 예시
  - 좋은 예: AI 진단 시스템 - 구체적 장면 묘사
  - 나쁜 예: Before/After 비교 구조 → comparison으로 빠진 안티패턴
  
  ## 적합한/부적합한 케이스
  
  ## 렌더링 금지 요소
  - 기존 + "Before 언급 금지" 추가
  ```

  **Must NOT do**:
  - 기존 파일 일부만 수정 (전체 교체)
  - Before/After 비교 구조 포함
  - 추상적 표현 사용

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 단일 파일 수정, 명확한 요구사항
  - **Skills**: 없음
    - Reason: 일반 markdown 작성, 특수 스킬 불필요

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: 없음
  - **Blocked By**: 없음

  **References**:
  - `plugins/visual-generator/references/themes/whatif.md` - 현재 파일 (전체 교체 대상)
  - `plugins/visual-generator/references/themes/comparison.md` - 차별화 기준

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: whatif.md 구조 검증
    Tool: Bash (grep)
    Preconditions: 파일 수정 완료
    Steps:
      1. grep -c "Comparison과의 차이" whatif.md → 1 이상
      2. grep -c "Scene Composition" whatif.md → 1 이상
      3. grep -c "Immersion Techniques" whatif.md → 1 이상
      4. grep -c "좋은 예" whatif.md → 1 이상
      5. grep -c "나쁜 예" whatif.md → 1 이상
    Expected Result: 모든 핵심 섹션 존재
    Evidence: grep 출력 결과

  Scenario: Before 언급 금지 규칙 존재 확인
    Tool: Bash (grep)
    Steps:
      1. grep -c "Before 언급" whatif.md → 1 이상
    Expected Result: 금지 규칙 명시됨
    Evidence: grep 출력 결과

  Scenario: comparison 차별화표 존재 확인
    Tool: Bash (grep)
    Steps:
      1. grep -A 10 "Comparison과의 차이" whatif.md | grep -c "|"
    Expected Result: 테이블 형식 (| 문자 다수)
    Evidence: grep 출력 결과
  ```

  **Commit**: YES
  - Message: `docs(visual-generator): differentiate whatif theme from comparison`
  - Files: `plugins/visual-generator/references/themes/whatif.md`

---

## 새 whatif.md 전체 컨텐츠

아래 내용을 **그대로** `plugins/visual-generator/references/themes/whatif.md`에 작성:

```markdown
# What-If (미래 비전 스냅샷) 테마

## 개요

**용도**: 제안 내용이 **이미 구현된** 미래 장면을 보여주어, 청중이 성공한 세계를 직접 경험하게 합니다.

**핵심 원칙**: 비교하지 않는다. 미래 **하나에 집중**한다.

> "Before가 없다. 이미 After 안에 서 있다."

**활용 상황**:
- "우리 솔루션이 작동하는 세상은 이런 모습입니다"
- 연구 성과가 현실화된 미래 시나리오
- 투자 유치 시 비전 몰입 유도
- 정책 도입 후 일상의 변화 시각화

---

## Comparison과의 차이 (CRITICAL)

| 구분 | Comparison | What-If |
|------|------------|---------|
| **구조** | 좌우 2분할 (Before ↔ After) | 단일 장면 (After **만**) |
| **관점** | 관찰자 (밖에서 비교) | 참여자 (안에서 경험) |
| **초점** | 차이점 증명 | 비전 몰입 |
| **수치** | 전후 수치 나란히 | 성과 수치가 장면 속에 자연스럽게 배치 |
| **시제** | "A → B로 바뀝니다" | "B입니다" (이미 일어난 것처럼) |
| **감정** | 논리적 납득 | 감성적 공감 |

**선택 가이드**:
- "차이를 증명해야 한다" → Comparison
- "비전을 느끼게 해야 한다" → What-If

---

## 색상 팔레트

| 역할 | 색상 | HEX | 용도 |
|------|------|-----|------|
| 주조 | 미드나이트 틸 | #1A535C | 장면 프레임, 제목, 핵심 라벨 |
| 보조 | 슬레이트 블루 | #4ECDC4 | 미래 요소, 연결선, UI 하이라이트 |
| 강조 | 선셋 오렌지 | #FF6B35 | 핵심 성과, KPI, 콜아웃 |
| 배경 | 소프트 크림 | #F7FFF7 | 밝고 희망적인 미래 분위기 |

**팔레트 특징**:
- 틸 계열 주조로 미래지향적 신뢰감
- 오렌지 강조가 "성공 포인트"를 자연스럽게 부각
- 따뜻한 배경으로 긍정적이고 접근 가능한 미래 연출

---

## 권장 레이아웃

### Future Snapshot (최우선 권장)

**단일 장면에 모든 요소를 담는다.** 분할하지 않는다.

```
┌─────────────────────────────────────┐
│                                     │
│        [미래 장면 전체 비주얼]        │
│                                     │
│   ┌─────────┐                       │
│   │성과 KPI │     👤 행위자가       │
│   │ +45%    │     무언가를 하고 있다 │
│   └─────────┘                       │
│                                     │
│       환경/맥락이 보인다             │
│                                     │
└─────────────────────────────────────┘
        ↑ 제목: 단정형 선언문
```

**핵심 원칙**:
- 장면은 **한 눈에** 들어와야 함
- KPI/성과 수치는 장면 **안에** 자연스럽게 배치 (분리 금지)
- 행위자(사람/시스템)가 **행동 중**이어야 함 (정지 상태 금지)

### Hero Statement (강조형)

상단에 대형 선언문, 하단에 지원 요소.

```
┌─────────────────────────────────────┐
│                                     │
│      "모든 진단이 10분 안에"         │
│                                     │
├─────────────────────────────────────┤
│  [장면A]    [장면B]    [장면C]       │
│  의사가     환자가     데이터가      │
│  확인 중   안심 중    실시간 분석    │
└─────────────────────────────────────┘
```

**사용 시점**: 핵심 메시지 하나를 각인시켜야 할 때

---

## Scene Composition (장면 구성 필수 요소)

What-If 장면은 다음 **5가지 요소**를 모두 포함해야 합니다:

### 1. 행위자 (WHO)
- 실제 사용자/수혜자가 등장해야 함
- 추상적 아이콘 대신 **맥락 있는 인물** (의사, 관리자, 시민 등)
- 표정/자세로 **긍정적 상태** 암시

### 2. 행동 (DOING)
- 정지 상태 금지. 뭔가를 **하고 있어야** 함
- "대시보드를 확인 중", "승인 버튼을 누르는 중", "결과를 받아보는 중"
- 동작이 보여야 "살아있는 미래"가 됨

### 3. 환경 (WHERE)
- 장면이 일어나는 공간의 단서
- 사무실, 병원, 공장, 거리 등 맥락 배경
- 배경 요소로 규모/상황 암시 (다른 사람들, 장비 등)

### 4. 성과 지표 (RESULT)
- 장면 안에 **자연스럽게** KPI 배치
- 화면 UI, 표지판, 대화 말풍선 등으로 통합
- 분리된 차트/표 대신 **장면의 일부**로 녹임

### 5. 시간 단서 (WHEN)
- "이것이 일상이다"를 암시하는 요소
- 시계, 캘린더, 반복 암시 (매일, 매번, 항상)
- 특별한 순간이 아닌 **보통의 하루** 느낌

---

## Immersion Techniques (몰입 기법)

### 현재형으로 말하기
| 피해야 할 표현 | 권장 표현 |
|---------------|----------|
| "도입되면 개선됩니다" | "45% 더 빠릅니다" |
| "가능해질 것입니다" | "지금 확인하세요" |
| "기대됩니다" | "이것이 새로운 기준입니다" |

### 구체적 수치 배치
| 피해야 할 표현 | 권장 표현 |
|---------------|----------|
| "빠른 처리" | "3초 응답" |
| "높은 정확도" | "99.2% 일치" |
| "비용 절감" | "월 ₩15M 절약" |

### 관점 설정
| 관점 | 효과 | 예시 |
|------|------|------|
| 1인칭 | 직접 경험 | "당신의 대시보드입니다" |
| 3인칭 | 객관적 증거 | "김 팀장이 10분 만에 완료" |
| 시스템 | 기술 역량 | "AI가 실시간 분석 중" |

---

## 장면 묘사 예시

### 좋은 예 (구체적, 몰입형)

**주제**: AI 진단 시스템 도입 후 병원

```
[메인 장면]
- 진료실에서 의사가 태블릿으로 AI 분석 결과를 환자에게 보여주고 있다
- 화면에는 "분석 완료: 2분 13초" 표시
- 환자 표정이 안심한 모습
- 배경에 다른 진료실들도 같은 시스템 사용 중

[오버레이 수치]
- "평균 진단 시간: 10분 → 3분"
- "오진율 0.3%"

[제목]
"모든 환자가 10분 안에 정확한 답을 얻습니다"
```

### 나쁜 예 (추상적, 비교형으로 빠짐)

```
[왼쪽: Before]
- 기존 시스템 아이콘
- "느림", "불편"

[오른쪽: After]  
- 새 시스템 아이콘
- "빠름", "편리"

↑ 이건 Comparison입니다. What-If가 아닙니다.
```

---

## 적합한 케이스

- 신규 시스템/플랫폼의 **작동하는 모습** 제시
- 연구 성과가 **현실에 적용된 장면** 시각화
- 투자 유치 시 **성공한 미래에 투자자를 초대**
- 정책 변화 후 **시민의 일상** 변화
- "왜 해야 하는가?" 대신 **"하면 이렇게 됩니다"** 설득

---

## 부적합한 케이스

- 두 옵션을 비교해야 하는 경우 → **comparison 사용**
- 현재 문제점 분석이 주목적인 경우 → **gov/seminar 사용**
- 단계별 프로세스 설명 → **concept 사용**
- 과거 데이터/트렌드 분석 → **다른 테마 사용**
- Before 상태를 반드시 보여줘야 하는 경우 → **comparison 사용**

---

## 렌더링 금지 요소 (CRITICAL)

이 테마를 사용하여 프롬프트를 생성할 때, 다음 요소들은 **CONTENT BLOCK에 절대 포함하지 마십시오**.

### 금지 패턴

| 유형 | 금지 예시 | 설명 |
|------|-----------|------|
| 위치 지시자 | `[상단]`, `[하단 결론1]`, `[왼쪽 영역]` | 레이아웃 배치 힌트 |
| 레이아웃 유형명 | `Future Snapshot`, `Hero Statement` | 메타포/레이아웃 이름 |
| 색상 코드 | `(#HEXCODE)`, `Primary Color` | CONFIGURATION에서만 사용 |
| 크기 힌트 | `(대형)`, `(중형)`, `48pt` | INSTRUCTION에서만 사용 |
| 역할 라벨 | `Main Title`, `Sub-header` | INSTRUCTION에서만 사용 |
| Before 언급 | `기존`, `이전에는`, `Before` | What-If는 After만 존재 |

### 올바른 CONTENT 작성법

**잘못된 예:**
```
1. **[메인 타이틀]** 플랫폼 비전
2. **[핵심 지표]** 70% 개선 (#FF6B35)
3. **[Before]** 수동 처리 → **[After]** 자동 처리
```

**올바른 예:**
```
1. 모든 처리가 자동으로 완료됩니다
2. 70% 더 빠른 응답
3. 실시간 자동 처리 시스템
```

텍스트의 위치, 크기, 색상은 INSTRUCTION과 CONFIGURATION에서 설명하고,
CONTENT에는 **순수한 텍스트 내용만** 포함합니다.
```

---

## Success Criteria

### Verification Commands
```bash
# 핵심 섹션 존재 확인
grep -c "Comparison과의 차이" plugins/visual-generator/references/themes/whatif.md  # Expected: 1+
grep -c "Scene Composition" plugins/visual-generator/references/themes/whatif.md  # Expected: 1+
grep -c "Immersion Techniques" plugins/visual-generator/references/themes/whatif.md  # Expected: 1+
```

### Final Checklist
- [x] "Comparison과의 차이" 섹션 존재
- [x] "Scene Composition" 섹션 (5가지 요소)
- [x] "Immersion Techniques" 섹션
- [x] 좋은 예 / 나쁜 예 구체적 예시
- [x] "Before 언급 금지" 규칙 명시
