# 개념 프롬프트 스타일 가이드

## 프롬프트 구조

모든 개념 프롬프트는 다음 섹션으로 구성:

```
1. Purpose (영어 작성)
2. Visual Concept (영어 작성 - 시각적 메타포)
3. Style (영어 작성)
4. Colors (영어 작성)
5. Lighting & Mood (영어 작성)
6. Resolution (영어 작성)
7. 핵심 메시지 (한글)
8. 시각 구성 (한글)
9. 텍스트 요소 (한글 - 최소)
10. Forbidden Elements (영어 작성)
11. 최종 결과물 목표 (한글)
```

---

## 메타 섹션 작성 규칙 (중요)

**Gemini API 한글 렌더링 문제 방지를 위해 메타 섹션(1~6, 10)은 영어로 작성:**

```
[INSTRUCTION - DO NOT RENDER IN IMAGE]

Purpose:
Generate a concept visualization image for educational presentation.
[개념의 목적을 영어로 1문장 기술]

Visual Concept:
[시각적 메타포를 영어로 상세 기술]
- Central metaphor: [핵심 비유]
- Visual elements: [시각 요소들]
- Spatial arrangement: [공간 배치]

Style:
- Clean conceptual 3D rendering OR flat iconic design
- Minimal decorative elements
- High contrast, clear boundaries
- TED-talk presentation aesthetic
- Focus on visual metaphor over text
```

**콘텐츠 섹션(7~9, 11)은 한글 유지:**
- 핵심 메시지, 텍스트 라벨은 한글
- 단, 기술 용어는 영어 병기 가능

---

## TED 스타일 핵심 원칙

### 1. One Message Rule

```
이미지를 본 후 청중이 기억할 한 가지:
- 복잡한 개념을 단순한 시각으로
- 모든 요소가 하나의 메시지를 향해
- "이것만 기억하세요" 테스트 통과
```

### 2. Visual Metaphor Priority

```
텍스트로 설명하지 말고 보여주기:
- 추상 → 구체 (데이터 흐름 → 물 흐르는 파이프)
- 복잡 → 단순 (신경망 → 연결된 점들)
- 생소 → 익숙 (블록체인 → 연결된 블록 체인)
```

### 3. Intentional Whitespace

```
여백은 디자인의 일부:
- 핵심 요소 주변에 숨 쉴 공간
- 시선 유도를 위한 의도적 비움
- 복잡해 보이지 않는 풍부함
```

---

## 무드 테마 시스템

### 테마 선택 가이드

개념의 성격에 따라 5가지 테마 중 선택:

| 테마 ID | 테마명 | 적합 개념 |
|:---|:---|:---|
| `clarity` | 명료 | 설명, 정의, 구조, 분류 (기본값) |
| `tech-focus` | 테크 | 기술, AI, 데이터, 시스템 |
| `growth` | 성장 | 발전, 학습, 진화, 향상 |
| `connection` | 연결 | 네트워크, 관계, 협력, 소통 |
| `innovation` | 혁신 | 변화, 창조, 돌파, 전환 |

---

### 테마 1: 명료 (clarity) - 기본값

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

---

### 테마 2: 테크 (tech-focus)

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

---

### 테마 3: 성장 (growth)

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

---

### 테마 4: 연결 (connection)

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

---

### 테마 5: 혁신 (innovation)

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

---

## 시각 스타일 가이드

### 3D 렌더링 스타일 (물리적/기계적 개념용)

```
Style:
- Clean conceptual 3D rendering
- Soft shadows, ambient occlusion
- Subtle reflections on surfaces
- Matte materials preferred
- Isometric or slight perspective
- No photorealistic textures
- Simplified geometric forms
```

**적합한 개념:**
- 하드웨어 구조
- 물리적 프로세스
- 기계적 메커니즘
- 공간적 관계

### 플랫 아이콘 스타일 (추상적/프로세스 개념용)

```
Style:
- Flat iconic design with subtle depth
- Clean geometric shapes
- Consistent line weights (2-3px)
- Rounded corners (8-12px radius)
- Minimal gradients (if any)
- Clear silhouettes
- Icon-first, text-second
```

**적합한 개념:**
- 프로세스 플로우
- 추상적 개념
- 단계별 과정
- 분류/카테고리

### 하이브리드 스타일 (복합 개념용)

```
Style:
- 3D elements for core concept
- Flat icons for supporting elements
- Consistent color palette across both
- Clear visual hierarchy
- 3D as focal point, flat as context
```

---

## 조명 및 해상도

```
Lighting & Mood:
- Soft diffused lighting
- No harsh shadows
- Even illumination
- Clean, professional atmosphere
- Subtle depth through lighting

Resolution:
- Ultra High Resolution
- 8K Quality
- Presentation and print ready
- 16:9 aspect ratio
```

---

## 텍스트 규격 (필수)

### 최소 폰트 크기 (렌더링 안전)

**텍스트는 최소화. 있다면 명확하게.**

| 요소 | 최소 크기 | 권장 크기 | 최대 글자수 |
|:---|:---:|:---:|:---:|
| 핵심 메시지 | **36pt** | 48-72pt | 10자 |
| 보조 라벨 | **18pt** | 20-24pt | 8자 |
| 키워드 | **16pt** | 18-20pt | 6자 |
| 캡션/주석 | **사용 금지** | - | - |

### 텍스트 밀도 제한

| 제한 항목 | 최대값 |
|:---|:---:|
| 이미지 전체 텍스트 요소 | **10개** |
| 한 영역 내 라벨 수 | 3개 |
| 문장 형태 텍스트 | **금지** |
| 라벨 간 최소 간격 | 30px |

### 텍스트 스타일

| 요소 | 굵기 | 색상 |
|:---|:---|:---|
| 핵심 메시지 | Bold | 주조색 또는 화이트 |
| 보조 라벨 | SemiBold | 주조색 또는 보조색 |
| 키워드 | Medium | 보조색 |

---

## 금지 요소 (모든 프롬프트 공통)

**영어로 작성하여 이미지에 렌더링되지 않도록 함:**

```
Forbidden Elements:
- Complex infographics with many data points
- Dense text blocks or paragraphs
- Decorative borders or frames
- Cartoon or childish illustrations
- Dark or busy backgrounds
- Neon glow effects
- 3D text with bevels
- Stock photo elements
- Watermarks or credits
- More than 10 text elements
- Font size below 16pt
- Full sentences (keywords only)
- Competing visual focal points
- Cluttered compositions
- Gradients as primary design element
```

---

## 품질 체크리스트

프롬프트 작성 완료 후 다음 항목 확인:

### 필수 검증 (One Message Test)

- [ ] 이미지를 보고 3초 안에 핵심 메시지 파악 가능
- [ ] 텍스트 없이도 개념 이해 가능
- [ ] 텍스트 요소 10개 이하
- [ ] 모든 텍스트 16pt 이상
- [ ] 시각적 메타포 명확
- [ ] 여백 충분히 확보
- [ ] 테마 색상 일관성

### 권장 검증 (Impact Test)

- [ ] 기억에 남는 시각적 구성
- [ ] 불필요한 요소 제거 완료
- [ ] 색상 대비 충분
- [ ] 3D/아이콘 스타일 일관성
