# 개념 프롬프트 스타일 가이드

## 프롬프트 구조

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

---

## 메타 섹션 작성 규칙 (중요)

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

---

## 기술 보고서 스타일 핵심 원칙

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
- 일반화(genericization) 방지
```

### 3. Professional Minimalism

```
전문적 미니멀리즘:
- 텍스트 요소 12-15개 범위
- 의도적 여백으로 가독성 확보
- 장식 요소 최소화, 정보 전달 우선
- 국책과제/학술저널 품질 기준
```

### 4. Intentional Whitespace

```
여백은 디자인의 일부:
- 핵심 요소 주변에 숨 쉴 공간
- 시선 유도를 위한 의도적 비움
- 복잡해 보이지 않는 풍부함
```

---

## 무드 테마 시스템

### 선택 가이드

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

---

### 테마 1: 기술 보고서 (technical-report) - 권장

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

---

### 테마 2: 명료 (clarity)

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

### 테마 3: 테크 (tech-focus)

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

### 테마 4: 성장 (growth)

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

### 테마 5: 연결 (connection)

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

### 테마 6: 혁신 (innovation)

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

### 테마 7: 지식 (knowledge) - 신규

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

---

### 테마 8: 발표 (presentation) - 신규

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

---

### 테마 9: 워크숍 (workshop) - 신규

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

---

## 시각 스타일 가이드

### 3D 렌더링 스타일 (기술 보고서용)

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

### 플랫 아이콘 스타일 (기술 보고서용)

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

---

## 텍스트 규격 (필수)

### 최소 폰트 크기 (렌더링 안전)

**텍스트는 적정 수준으로, 명확하게.**

| 요소 | 최소 크기 | 권장 크기 | 최대 글자수 |
|:---|:---:|:---:|:---:|
| 대제목 | **32pt** | 36-48pt | 12자 |
| 소제목 | **20pt** | 22-28pt | 15자 |
| 보조 라벨 | **16pt** | 18-22pt | 10자 |
| 키워드 | **14pt** | 16-18pt | 8자 |
| 캡션/주석 | **사용 금지** | - | - |

### 텍스트 밀도 제한

| 제한 항목 | 최대값 |
|:---|:---:|
| 이미지 전체 텍스트 요소 | **15개** (권장: 12-15개) |
| 한 영역 내 라벨 수 | 4개 |
| 문장 형태 텍스트 | **금지** |
| 라벨 간 최소 간격 | 25px |

### 텍스트 스타일

| 요소 | 굵기 | 색상 |
|:---|:---|:---|
| 대제목 | Bold | 주조색 또는 화이트 |
| 소제목 | Bold | 주조색 |
| 보조 라벨 | SemiBold | 주조색 또는 보조색 |
| 키워드 | Medium | 보조색 |

---

## 도메인 키워드 처리 규칙

### 키워드 보존 원칙

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

### 약어 사용 가이드

| 원형 | 허용 약어 | 금지 대체어 |
|:---|:---|:---|
| 굴착기 | 굴착기 (유지) | 로봇, 장비, 중장비 |
| 휠레그-4족보행로봇 | 4족로봇 | 보행 로봇, 로봇 |
| Cross-Embodiment | Cross-Embodiment | 범용성, 호환성 |
| 트랙터 | 트랙터 (유지) | 농기계, 차량 |

### 영어 힌트 처리 (⚠️ 중요)

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

---

## 금지 요소 (모든 프롬프트 공통)

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

---

## 품질 체크리스트

프롬프트 작성 완료 후 다음 항목 확인:

### 필수 검증 (Technical Report Test)

- [ ] 이미지를 보고 3초 안에 핵심 메시지 파악 가능
- [ ] 텍스트 요소 12-15개 범위 내
- [ ] 모든 텍스트 14pt 이상
- [ ] 도메인 키워드 정확히 보존됨
- [ ] 폰트 크기 정보가 렌더링되지 않음
- [ ] 시각적 메타포 명확
- [ ] 여백 충분히 확보
- [ ] 테마 색상 일관성

### 권장 검증 (Impact Test)

- [ ] 국책과제/학술저널에 즉시 사용 가능
- [ ] 기억에 남는 시각적 구성
- [ ] 불필요한 요소 제거 완료
- [ ] 색상 대비 충분
- [ ] 3D/아이콘 스타일 일관성
- [ ] 영어 힌트가 INSTRUCTION 블록에만 있음 (CONTENT 블록에 없음)
