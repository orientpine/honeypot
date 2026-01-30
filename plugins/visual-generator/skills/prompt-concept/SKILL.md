---
name: prompt-concept
description: "핵심 개념을 직관적으로 시각화하는 기술 보고서 스타일 이미지 프롬프트를 생성합니다. 국책과제 보고서, 학술저널, 기술 제안서용 시각 자료가 필요할 때 사용합니다. visual-renderer와 호환되는 프롬프트를 출력합니다."
skills: layout-types
---

# 개념 프롬프트 생성기 (Visual Prompt Concept)

핵심 개념을 직관적으로 시각화하는 **기술 보고서 스타일** 이미지 생성 프롬프트를 작성합니다.
**한 이미지, 한 메시지** 원칙으로 독자의 즉각적 이해를 돕는 시각 자료를 만듭니다.

---

## visual-prompt-gov와의 차이

| 항목 | visual-prompt-gov | visual-prompt-concept |
|------|-------------------|----------------------|
| 스타일 | 정부/공공기관 보고서 | 기술 보고서/학술 발표 |
| 정보량 | 다량 (25개 요소) | 적정 (12-15개) |
| 시각화 | 복잡한 인포그래픽 | 직관적 개념 다이어그램 |
| 3D 스타일 | 산업용 렌더링 | 개념적 렌더링 |
| 텍스트 | 상세 라벨링 | 핵심 키워드 + 약어 허용 |
| 목적 | 정보 전달 | 개념 이해 + 전문성 |

---

## 사용자 입력 스키마

### 필수 입력

| 항목 | 설명 | 예시 |
|------|------|------|
| 핵심 개념 | 시각화할 개념/주제 | "머신러닝의 학습 과정", "블록체인 합의 메커니즘" |

### 선택 입력

| 항목 | 설명 | 기본값 |
|------|------|--------|
| 시각화 유형 | 선호하는 시각화 방식 (12종) | 자동 선택 |
| 무드 테마 | 9가지 무드 중 선택 | `technical-report` |
| 도메인 키워드 | 보존해야 할 전문용어 목록 | - |
| 약어 허용 | 긴 용어의 약어 사용 허용 | true |
| 출력 폴더 | 프롬프트 저장 위치 | `concept_image_gen/prompts/` |
| 슬라이드 수 | 생성할 이미지 개수 | 1 |

---

## 워크플로우

### Phase 1: 개념 분석

```
+-- Step 1-1. 핵심 개념 파악
|   +-- 사용자 입력에서 핵심 개념 추출
|   +-- 개념의 본질적 특성 식별
|   +-- 시각화 가능한 요소 도출
|
+-- Step 1-2. 도메인 키워드 식별
|   +-- 보존해야 할 전문용어 추출
|   +-- 약어 허용 여부 확인
|   +-- 일반화 금지 용어 목록 작성
|
+-- Step 1-3. 시각적 메타포 탐색
|   +-- 개념을 대변할 수 있는 시각적 비유 탐색
|   +-- 일상적 경험과 연결되는 이미지 도출
|   +-- 직관적 이해를 돕는 구조 선택
|
+-- Step 1-4. 핵심 메시지 정의
    +-- 한 문장으로 전달할 메시지 정의
    +-- 이미지를 본 후 기억할 한 가지
    +-- 불필요한 정보 제거
```

### Phase 2: 무드 테마 선택

```
+-- Step 2-1. 개념 성격 분석
|   +-- 국책과제/학술 → technical-report
|   +-- 기술적/과학적 → tech-focus
|   +-- 성장/발전 → growth
|   +-- 연결/관계 → connection
|   +-- 명확/단순 → clarity
|   +-- 혁신/변화 → innovation
|
+-- Step 2-2. 테마 색상 로드
    +-- 아래 스타일 가이드에서 테마 색상 로드
    +-- 주조색, 보조색, 강조색 확정
```

**무드 테마 옵션:**

| 테마 ID | 테마명 | 적합 개념 | 주조색 |
|:---|:---|:---|:---|
| `technical-report` | 기술 보고서 | 국책과제, 연구논문, 학술발표 **(권장)** | #2C3E50 |
| `clarity` | 명료 | 설명, 정의, 구조 | #2D3436 |
| `tech-focus` | 테크 | 기술, AI, 데이터 | #0984E3 |
| `growth` | 성장 | 발전, 학습, 진화 | #00B894 |
| `connection` | 연결 | 네트워크, 관계, 협력 | #6C5CE7 |
| `innovation` | 혁신 | 변화, 창조, 돌파 | #E17055 |

### Phase 3: 시각화 유형 선택

`layout-types` 스킬을 참조하여 개념에 맞는 시각화 선택 (공유 레이아웃):

| 개념 유형 | 시각화 유형 |
|:---|:---|
| 과정, 변환 | 플로우 메타포 |
| 구조, 계층 | 구조 메타포 |
| 관계, 연결 | 네트워크 메타포 |
| 대비, 차이 | 대비 메타포 |
| 성장, 발전 | 진화 메타포 |
| 핵심, 중심 | 중심 메타포 |
| 순환, 반복 | 순환 메타포 |
| 분류, 종류 | 그룹 메타포 |
| 레이어, 포함 | 동심원 메타포 |
| 다중주체, 협업 | Swimlane 메타포 |
| 포지셔닝, 우선순위 | 전략맵 메타포 |
| 선별, 축소 | 깔때기 메타포 |

### Phase 4: 프롬프트 작성

아래 스타일 가이드 적용.
[assets/output_template/prompt_template.md](assets/output_template/prompt_template.md) 템플릿 기반 작성.

```
+-- Step 4-1. 프롬프트 초안 작성
|   +-- INSTRUCTION 블록: 영어로 작성 (렌더링 안 됨)
|   +-- CONFIGURATION 블록: 영어로 작성 (렌더링 안 됨)
|   +-- CONTENT 블록: 한글로 작성 (렌더링됨)
|   +-- FORBIDDEN 블록: 영어로 작성 (렌더링 안 됨)
|   +-- 선택된 테마 색상 적용
|
+-- Step 4-2. 도메인 키워드 검증
|   +-- 전문용어 보존 여부 확인
|   +-- 일반화(로봇, 장비 등) 대체 금지
|   +-- 영어 힌트가 INSTRUCTION 블록에만 있는지 확인
|   +-- CONTENT 블록에 (hint: ...) 형식 없는지 확인
|
+-- Step 4-3. 텍스트 밀도 검증
|   +-- 텍스트 요소 12-15개 범위
|   +-- 핵심 메시지 1개만 전달
|   +-- 불필요한 장식 요소 제거
|
+-- Step 4-4. 임팩트 검증
|   +-- 시각적 메타포 명확성
|   +-- 즉각적 이해 가능 여부
|   +-- 학술/연구 품질 적합성
|
+-- Step 4-5. 렌더링 방지 검증 (필수)
    +-- 프롬프트에 "pt", "px" 단위 포함 여부 확인
    +-- 숫자+단위 조합 (예: 14pt, 32px) 완전 제거
    +-- 크기는 "대형/중형/소형" 또는 "large/medium/small"로만 표현
    +-- 테이블에 "크기" 열 대신 "강조도" 또는 생략
    +-- 중국어/일본어 등 비한글 아시아 문자 포함 금지
```

**프롬프트 구조:**

```
==================================================
[INSTRUCTION BLOCK - DO NOT RENDER]
1. Purpose (영어)
2. Visual Concept (영어 - 시각적 메타포)
3. Style (영어)
4. Colors (영어 - 선택된 테마 색상)
5. Lighting & Mood (영어)
6. Resolution (영어)
==================================================

==================================================
[CONFIGURATION BLOCK - DO NOT RENDER]
- Text Specifications (영어)
- Visual Specifications (영어)
==================================================

==================================================
[CONTENT BLOCK - FOR IMAGE RENDERING]
7. 핵심 메시지 (한글)
8. 도메인 키워드 (한글, 번역 힌트는 INSTRUCTION 블록에만)
9. 시각 구성 (한글)
10. 텍스트 요소 (한글) ⚠️ 폰트 크기(pt/px) 명시 금지, 내용과 위치만 기술
==================================================

==================================================
[FORBIDDEN ELEMENTS - DO NOT RENDER]
11. Forbidden Elements (영어)
12. 최종 결과물 목표 (한글)
==================================================
```

### Phase 5: 출력

```
+-- Step 5-1. 출력 폴더 생성
|   +-- concept_image_gen/prompts/ 폴더 생성 (없으면)
|
+-- Step 5-2. 프롬프트 파일 저장
|   +-- 파일명: [번호]_[개념명].md
|   +-- 인코딩: UTF-8
|
+-- Step 5-3. 인덱스 파일 생성
    +-- prompt_index.md 생성
    +-- 생성된 프롬프트 목록 기록
```

---

## 핵심 원칙 (기술 보고서 스타일)

### 1. Clarity with Depth

```
명확성과 깊이의 균형:
- 한 이미지에 하나의 핵심 개념
- 계층적 정보 구조 (대제목 > 소제목 > 라벨)
- 전문성을 해치지 않는 간결함
- 3초 안에 핵심 파악 가능
```

### 2. Domain-Authentic Visualization

```
도메인 전문성 보존:
- 전문 용어는 축약 가능하나 대체 금지
- 도메인 특화 시각 요소 사용
- 학술/연구 맥락에 적합한 표현
- 굴착기, 트랙터, 4족로봇 등 명시적 표기
```

### 3. Professional Minimalism

```
전문적 미니멀리즘:
- 텍스트 요소 12-15개 범위
- 의도적 여백으로 가독성 확보
- 장식 요소 최소화, 정보 전달 우선
- 국책과제/학술저널 품질 기준
```

### 4. Context-Dependent Style

```
맥락에 따른 스타일 선택:
- 물리적/기계적 개념 → 3D 렌더링
- 추상적/프로세스 개념 → 아이콘/도형
- 혼합 사용 시 일관성 유지
```

---

## 텍스트 규격 (필수)

**기술 보고서 원칙: 명확성과 간결성의 균형**

> ⚠️ **중요**: 아래 크기 규격은 내부 참고용입니다. **프롬프트에 "pt", "px" 단위를 포함하지 마세요.**

| 요소 | 크기 등급 | 최대 글자수 | 프롬프트 표기 |
|:---|:---:|:---:|:---|
| 대제목 | 대형 (XL) | 12자 | "대형" 또는 "prominent" |
| 소제목 | 중형 (L) | 15자 | "중형" 또는 "medium" |
| 보조 라벨 | 소형 (M) | 10자 | "소형" 또는 "small" |
| 키워드 | 최소형 (S) | 8자 | "최소형" 또는 "minimal" |
| 캡션/주석 | **사용 금지** | - | 프롬프트에 포함 금지 |

**텍스트 밀도 제한:**
- 이미지 전체 텍스트 요소: **12-15개 (최대 15개)**
- 한 영역 내 라벨: **최대 4개**
- 문장 사용 금지, 키워드만
- **폰트 크기 숫자 (14pt, 32px 등) 프롬프트 포함 절대 금지**

---

## 도메인 키워드 처리

### 보존 원칙

```
금지 패턴 (일반화 금지):
- "굴착기" -> "로봇" (X)
- "휠레그-4족보행로봇" -> "보행 로봇" (X)
- "트랙터" -> "농기계" (X)

허용 패턴 (약어화):
- "휠레그-4족보행로봇" -> "4족로봇" (O)
- "트랙터 기반 자율주행" -> "자율주행 트랙터" (O)
```

### 영어 힌트 처리 (⚠️ 중요)

영어 번역 정보는 **INSTRUCTION 블록에만** 기술합니다:

**INSTRUCTION 블록 (DO NOT RENDER):**
```
Domain Keywords Reference (for AI understanding only - DO NOT render):
- 굴착기 = Excavator
- 4족로봇 = Quadruped Robot
- 트랙터 = Tractor
```

**CONTENT 블록 (렌더링됨) - 한글만:**
```
라벨: "굴착기" 위치: 좌측
라벨: "4족로봇" 위치: 우측
라벨: "트랙터" 위치: 중앙
```

⚠️ **CONTENT 블록에 (hint: "...") 형식 절대 금지** → Gemini가 영어를 이미지에 병기함

---

## 공통 규칙

- **텍스트**: 한글만 렌더링 (영어 hint는 INSTRUCTION 블록에만, CONTENT에 포함 금지)
- **스타일**: 개념적 3D 또는 플랫 아이콘 (주제에 따라)
- **시점**: 정면 또는 약한 등각(Isometric, 15-30도)
- **배경**: 단색 또는 미니멀 그라데이션
- **해상도**: 8K Quality, 16:9 비율
- **금지 (프롬프트에 포함하지 말 것)**:
  - 복잡한 인포그래픽, 과도한 텍스트, 장식 요소
  - ⚠️ **폰트 크기 숫자** (14pt, 32pt, 48px 등) - 프롬프트 내 절대 포함 금지
  - ⚠️ **"pt", "px" 단위**가 포함된 모든 텍스트
  - 중국어(汉字), 일본어(仮名) 등 비한글 아시아 문자
  - 테이블의 "크기" 열 (내용과 위치만 기술)

---

## 렌더링 방지 체크리스트

프롬프트 완성 후 아래 항목이 포함되어 있지 **않은지** 반드시 확인:

- **CONTENT 블록 렌더링 규칙**: 병기 금지는 **CONTENT 블록에만** 적용 (INSTRUCTION 블록의 번역/설명 힌트는 허용)

| 금지 패턴 | 예시 | 대체 표현 |
|:---|:---|:---|
| 폰트 크기 숫자+단위 | `14pt`, `32px`, `48pt` | `large`, `medium`, `small` |
| 테이블의 크기 열 | `\| 크기 \|` 열 | 제거 또는 "강조도" 열로 대체 |
| 픽셀 단위 | `8px`, `25px` | `thin`, `thick`, `standard` |
| 퍼센트 단위 | `50%`, `100%` | `half`, `full` |
| 설정 텍스트 | `DO NOT RENDER` | 섹션 제목으로만 사용 |
| 비한글 아시아 문자 | `汎用`, `技术` | 해당 없음 (제거) |
| 언어 병기 | `굴착기 (Excavator)` | 단일 언어만 사용 |

**프롬프트 검증 방법:**
```
프롬프트 내용에서 "\d+pt" 또는 "\d+px" 패턴 검색 → 0건이어야 함
프롬프트 내용에서 "\([A-Z][a-z]+\)" 패턴 검색 → 0건이어야 함 (병기 검증)
```

**올바른 텍스트 요소 테이블 형식:**
```markdown
### 텍스트 요소
| 요소 | 내용 | 위치 |
|------|------|------|
| 메인 타이틀 | FRAI Platform | 중앙 상단 |
| 서브 타이틀 | Physical AI for Field Robots | 중앙 |
| 도메인 라벨 | Construction / Agriculture / Disaster | 각 영역 상단 |
```
> ⚠️ "크기" 열 없음 - 내용과 위치만 기술

---

---

## 스타일 가이드 (기술 보고서)

### 프롬프트 구조

모든 개념 프롬프트는 다음 4개 블록으로 구성:

```
[INSTRUCTION BLOCK - DO NOT RENDER]
1. Purpose (영어 작성)
2. Visual Concept (영어 작성 - 시각적 메타포)
3. Style (영어 작성)
4. Colors (영어 작성)
5. Lighting & Mood (영어 작성)
6. Resolution (영어 작성)

[CONFIGURATION BLOCK - DO NOT RENDER]
- Text Specifications (영어 작성)
- Visual Specifications (영어 작성)

[CONTENT BLOCK - FOR IMAGE RENDERING]
7. 핵심 메시지 (한글)
8. 도메인 키워드 (한글 + 영어 hint)
9. 시각 구성 (한글)
10. 텍스트 요소 (한글)

[FORBIDDEN ELEMENTS - DO NOT RENDER]
11. Forbidden Elements (영어 작성)
12. 최종 결과물 목표 (한글)
```

### 메타 섹션 작성 규칙 (중요)

**Gemini API 한글 렌더링 문제 방지를 위해 메타/설정 섹션은 영어로 작성:**

```
==================================================
[INSTRUCTION BLOCK - DO NOT RENDER IN IMAGE]
==================================================

Purpose:
Generate a technical concept visualization for academic/research presentations.
[개념의 목적을 영어로 1-2문장 기술]

Visual Concept:
[시각적 메타포를 영어로 상세 기술]
- Central metaphor: [핵심 비유]
- Visual elements: [시각 요소들]
- Spatial arrangement: [공간 배치]

Style:
- Clean conceptual 3D rendering with minimal infographic
- Technical diagram aesthetic (professional, academic-appropriate)
- Sans-serif typography, clean hierarchy
- Focus on visual metaphor over text
```

**콘텐츠 섹션은 한글 유지:**
- 핵심 메시지, 텍스트 라벨은 한글
- 기술 용어는 영어 hint 병기 권장

### 기술 보고서 스타일 핵심 원칙

#### 1. Clarity with Depth

```
명확성과 깊이의 균형:
- 한 이미지에 하나의 핵심 개념
- 계층적 정보 구조 (대제목 > 소제목 > 라벨)
- 전문성을 해치지 않는 간결함
- 3초 안에 핵심 파악 가능
```

#### 2. Domain-Authentic Visualization

```
도메인 전문성 보존:
- 전문 용어는 축약 가능하나 대체 금지
- 도메인 특화 시각 요소 사용
- 학술/연구 맥락에 적합한 표현
- 일반화(genericization) 방지
```

#### 3. Professional Minimalism

```
전문적 미니멀리즘:
- 텍스트 요소 12-15개 범위
- 의도적 여백으로 가독성 확보
- 장식 요소 최소화, 정보 전달 우선
- 국책과제/학술저널 품질 기준
```

#### 4. Intentional Whitespace

```
여백은 디자인의 일부:
- 핵심 요소 주변에 숨 쉴 공간
- 시선 유도를 위한 의도적 비움
- 복잡해 보이지 않는 풍부함
```

### 무드 테마 시스템

#### 선택 가이드

개념의 성격에 따라 9가지 테마 중 선택:

| 테마 ID | 테마명 | 적합 개념 |
|:---|:---|:---|
| `technical-report` | 기술 보고서 | 국책과제, 연구논문, 학술발표 **(권장)** |
| `clarity` | 명료 | 설명, 정의, 구조, 분류 |
| `tech-focus` | 테크 | 기술, AI, 데이터, 시스템 |
| `growth` | 성장 | 발전, 학습, 진화, 향상 |
| `connection` | 연결 | 네트워크, 관계, 협력, 소통 |
| `innovation` | 혁신 | 변화, 창조, 돌파, 전환 |
| `knowledge` | 지식 **(신규)** | 큐레이션, 학습, 정보 관리 **(권장)** |
| `presentation` | 발표 **(신규)** | 프레젠테이션, 세미나, 강연 |
| `workshop` | 워크숍 **(신규)** | 협업, 실습, 팀워크 |

#### 테마 1: 기술 보고서 (technical-report) - 권장

**적합 개념**: 국책과제, 연구논문, 기술 제안서, 학술 발표

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 네이비 | #2C3E50 | 핵심 요소, 메인 텍스트 |
| 보조 | 슬레이트 블루 | #5D6D7E | 보조 요소, 연결선 |
| 강조 | 딥 블루 | #2980B9 | 하이라이트, 강조점 |
| 배경 | 오프 화이트 | #F8F9FA | 전체 배경 |

**스타일 노트:**
- 정부 보고서와 학술 자료 사이의 중간 톤
- 차분하고 신뢰감 있는 분위기
- 학술/연구 맥락에 최적화
- 과도한 강조색 사용 자제

#### 테마 2: 명료 (clarity)

**적합 개념**: 설명, 정의, 구조, 분류, 비교

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 차콜 | #2D3436 | 핵심 요소, 메인 텍스트 |
| 보조 | 슬레이트 | #636E72 | 보조 요소, 연결선 |
| 강조 | 스카이 | #74B9FF | 하이라이트, 강조점 |
| 배경 | 화이트 | #FAFAFA | 전체 배경 |

**스타일 노트:**
- 가장 중립적, 범용적
- 높은 가독성과 명확한 구분
- 교과서/설명서 느낌

#### 테마 3: 테크 (tech-focus)

**적합 개념**: 기술, AI, 데이터, 시스템, 알고리즘

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 블루 | #0984E3 | 핵심 요소, 데이터 흐름 |
| 보조 | 다크 블루 | #2D3436 | 구조, 프레임 |
| 강조 | 시안 | #00CEC9 | 하이라이트, 활성 상태 |
| 배경 | 라이트 그레이 | #F5F6FA | 전체 배경 |

**스타일 노트:**
- 디지털/테크 느낌
- 데이터 시각화에 적합
- 미래지향적 분위기

#### 테마 4: 성장 (growth)

**적합 개념**: 발전, 학습, 진화, 향상, 성과

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 민트 | #00B894 | 핵심 요소, 성장 방향 |
| 보조 | 다크 그린 | #1E3A3A | 기반, 출발점 |
| 강조 | 라임 | #55EFC4 | 하이라이트, 성과 |
| 배경 | 민트 화이트 | #F8FFFC | 전체 배경 |

**스타일 노트:**
- 자연스러운 성장 느낌
- 긍정적/희망적 분위기
- 학습/교육 컨텐츠에 적합

#### 테마 5: 연결 (connection)

**적합 개념**: 네트워크, 관계, 협력, 소통, 통합

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 퍼플 | #6C5CE7 | 핵심 노드, 연결점 |
| 보조 | 인디고 | #3D3D6B | 구조, 경로 |
| 강조 | 라벤더 | #A29BFE | 하이라이트, 활성 연결 |
| 배경 | 라벤더 화이트 | #F8F7FF | 전체 배경 |

**스타일 노트:**
- 부드러운 연결감
- 관계/네트워크 시각화
- 협업/소통 주제에 적합

#### 테마 6: 혁신 (innovation)

**적합 개념**: 변화, 창조, 돌파, 전환, 새로움

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 코랄 | #E17055 | 핵심 요소, 변화점 |
| 보조 | 다크 코랄 | #6B3A3A | 기존 상태 |
| 강조 | 골드 | #FDCB6E | 하이라이트, 혁신 포인트 |
| 배경 | 웜 화이트 | #FFFAF5 | 전체 배경 |

**스타일 노트:**
- 에너지 넘치는 느낌
- 변화/전환 강조
- 스타트업/혁신 주제에 적합

#### 테마 7: 지식 (knowledge) - 신규

**적합 개념**: 큐레이션, 학습, 정보 관리, 지식 공유, 교육

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 딥 블루 | #1E3A5F | 핵심 요소, 지식 노드 |
| 보조 | 퍼플 | #6B5B95 | 보조 요소, 연결 |
| 강조 | 오렌지 | #E07B39 | 하이라이트, 중요 정보 |
| 배경 | 화이트 | #FFFFFF | 전체 배경 |

**스타일 노트:**
- 지적이고 차분한 분위기
- 정보 큐레이션/관리 주제에 최적
- 학습/교육 콘텐츠에 적합

#### 테마 8: 발표 (presentation) - 신규

**적합 개념**: 프레젠테이션, 세미나, 강연, 발표 자료

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 다크 틸 | #0D4F4F | 핵심 요소, 메인 콘텐츠 |
| 보조 | 슬레이트 | #5D6D7E | 보조 요소, 구조 |
| 강조 | 코랄 | #FF6B6B | 하이라이트, 강조점 |
| 배경 | 라이트 그레이 | #F8F9FA | 전체 배경 |

**스타일 노트:**
- 전문적이면서 친근한 분위기
- 세미나/발표 맥락에 최적화
- 시각적 임팩트와 가독성 균형

#### 테마 9: 워크숍 (workshop) - 신규

**적합 개념**: 협업, 실습, 팀워크, 워크숍, 공동 작업

| 역할 | 색상명 | HEX 코드 | 사용처 |
|:---|:---|:---|:---|
| 주조 | 포레스트 그린 | #2D5A3D | 핵심 요소, 협업 영역 |
| 보조 | 웜 그레이 | #6B6B6B | 보조 요소, 구조 |
| 강조 | 스카이 블루 | #4ECDC4 | 하이라이트, 활동 |
| 배경 | 크림 | #FFFEF5 | 전체 배경 |

**스타일 노트:**
- 따뜻하고 협력적인 분위기
- 워크숍/실습 주제에 적합
- 팀워크/공동 작업 강조

### 시각 스타일 가이드

#### 3D 렌더링 스타일 (기술 보고서용)

```
Style:
- Clean conceptual 3D rendering with minimal infographic
- Technical diagram aesthetic (professional, academic-appropriate)
- Soft ambient lighting with subtle shadows
- Matte surfaces, no photorealistic textures
- Isometric or slight perspective view (15-30 degrees)
- Sans-serif typography, clean hierarchy
- Simplified geometric forms
```

**적합한 개념:**
- 하드웨어 구조
- 물리적 프로세스
- 시스템 아키텍처
- 공간적 관계

#### 플랫 아이콘 스타일 (기술 보고서용)

```
Style:
- Flat iconic design with subtle depth
- Clean geometric shapes
- Consistent line weights (2-3px)
- Rounded corners (8-12px radius)
- Minimal gradients (if any)
- Clear silhouettes
- Professional diagram aesthetic
```

**적합한 개념:**
- 프로세스 플로우
- 추상적 개념
- 단계별 과정
- 분류/카테고리

#### 하이브리드 스타일 (복합 개념용)

```
Style:
- 3D elements for core concept
- Flat icons for supporting elements
- Consistent color palette across both
- Clear visual hierarchy
- 3D as focal point, flat as context
```

### 조명 및 해상도

```
Lighting & Mood:
- Soft diffused lighting
- Minimal shadows for depth
- Professional, trustworthy atmosphere
- Clean, clear outlines
- Subtle depth through lighting

Resolution:
- Ultra High Resolution
- 8K Quality
- Academic presentation and journal-ready
- 16:9 aspect ratio
```

### 텍스트 규격 (필수)

#### 최소 폰트 크기 (렌더링 안전)

**텍스트는 적정 수준으로, 명확하게.**

| 요소 | 최소 크기 | 권장 크기 | 최대 글자수 |
|:---|:---:|:---:|:---:|
| 대제목 | **32pt** | 36-48pt | 12자 |
| 소제목 | **20pt** | 22-28pt | 15자 |
| 보조 라벨 | **16pt** | 18-22pt | 10자 |
| 키워드 | **14pt** | 16-18pt | 8자 |
| 캡션/주석 | **사용 금지** | - | - |

#### 텍스트 밀도 제한

| 제한 항목 | 최대값 |
|:---|:---:|
| 이미지 전체 텍스트 요소 | **15개** (권장: 12-15개) |
| 한 영역 내 라벨 수 | 4개 |
| 문장 형태 텍스트 | **금지** |
| 라벨 간 최소 간격 | 25px |

#### 텍스트 스타일

| 요소 | 굵기 | 색상 |
|:---|:---|:---|
| 대제목 | Bold | 주조색 또는 화이트 |
| 소제목 | Bold | 주조색 |
| 보조 라벨 | SemiBold | 주조색 또는 보조색 |
| 키워드 | Medium | 보조색 |

### 도메인 키워드 처리 규칙

#### 키워드 보존 원칙

사용자가 제공한 전문용어는 반드시 보존해야 합니다:

**금지 패턴 (일반화 금지):**
- "굴착기" -> "로봇" (X)
- "휠레그-4족보행로봇" -> "보행 로봇" (X)
- "Cross-Embodiment" -> "범용 기술" (X)
- "트랙터" -> "농기계" (X)

**허용 패턴 (약어화):**
- "휠레그-4족보행로봇" -> "4족로봇" (O)
- "트랙터 기반 자율주행 시스템" -> "자율주행 트랙터" (O)
- "굴착기" -> "굴착기" (원형 유지, O)

#### 약어 사용 가이드

| 원형 | 허용 약어 | 금지 대체어 |
|:---|:---|:---|
| 굴착기 | 굴착기 (유지) | 로봇, 장비, 중장비 |
| 휠레그-4족보행로봇 | 4족로봇 | 보행 로봇, 로봇 |
| Cross-Embodiment | Cross-Embodiment | 범용성, 호환성 |
| 트랙터 | 트랙터 (유지) | 농기계, 차량 |

#### 영어 힌트 처리 (⚠️ 중요)

도메인 키워드의 영어 번역은 **INSTRUCTION 블록에만** 기술합니다.
**CONTENT 블록의 라벨에는 한글만 표시**하여 영어 병기 렌더링을 방지합니다.

**INSTRUCTION 블록 (렌더링 안 됨):**
```
Domain Keywords Reference (for AI understanding only - DO NOT render in image):
- 굴착기 = Excavator
- 4족로봇 = Quadruped Robot
- 트랙터 = Tractor
```

**CONTENT 블록 (렌더링됨) - 한글만:**
```
라벨: "굴착기" 위치: 좌측
라벨: "4족로봇" 위치: 우측
라벨: "트랙터" 위치: 중앙
```

⚠️ **CONTENT 블록에 (hint: "...") 형식 사용 금지** → Gemini가 영어를 이미지에 병기함

### 금지 요소 (모든 프롬프트 공통)

**영어로 작성하여 이미지에 렌더링되지 않도록 함:**

```
Forbidden Elements:
- Complex infographics with excessive data points
- Dense text blocks or paragraphs
- Decorative borders or frames
- Cartoon or childish illustrations
- Dark or busy backgrounds
- Neon glow or excessive lighting effects
- 3D text with bevels or shadows
- Stock photo elements
- Watermarks or credits
- More than 15 text elements
- Font size below 14pt
- Full sentences (keywords only)
- Competing visual focal points
- Cluttered compositions
- Gradients as primary design element
- Rendering font size specifications (e.g., "48pt", "32pt") in the image
- Rendering configuration details in the image
- Replacing domain keywords with generic terms
- Overly flashy or "startup" aesthetics
- SF/cyberpunk visual elements for academic content
- English text alongside or under Korean labels (render Korean only, e.g., "굴착기" not "굴착기 Excavator")
- Bilingual labeling in the rendered image
- Rendering "(hint: ...)" format text in the image
```

### 품질 체크리스트

프롬프트 작성 완료 후 다음 항목 확인:

#### 필수 검증 (Technical Report Test)

- [ ] 이미지를 보고 3초 안에 핵심 메시지 파악 가능
- [ ] 텍스트 요소 12-15개 범위 내
- [ ] 모든 텍스트 14pt 이상
- [ ] 도메인 키워드 정확히 보존됨
- [ ] 폰트 크기 정보가 렌더링되지 않음
- [ ] 시각적 메타포 명확
- [ ] 여백 충분히 확보
- [ ] 테마 색상 일관성

#### 권장 검증 (Impact Test)

- [ ] 국책과제/학술저널에 즉시 사용 가능
- [ ] 기억에 남는 시각적 구성
- [ ] 불필요한 요소 제거 완료
- [ ] 색상 대비 충분
- [ ] 3D/아이콘 스타일 일관성
- [ ] 영어 힌트가 INSTRUCTION 블록에만 있음 (CONTENT 블록에 없음)

---

## 리소스

- `layout-types` 스킬: 시각화 유형별 상세 가이드 (공유 레이아웃)
- `assets/output_template/prompt_template.md`: 프롬프트 템플릿 (4블록 구조)

---

## 관련 스킬

| 스킬 | 역할 | 연계 |
|------|------|------|
| visual-prompt-concept | 개념 시각화 프롬프트 생성 | 현재 |
| visual-renderer | 프롬프트 -> 이미지 변환 | 후행 |
| visual-prompt-gov | 정부/공공 스타일 프롬프트 | 대안 |
