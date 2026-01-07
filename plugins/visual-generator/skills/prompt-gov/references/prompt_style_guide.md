# 슬라이드 프롬프트 스타일 가이드

## 프롬프트 구조

모든 슬라이드 프롬프트는 다음 섹션으로 구성:

```
1. Purpose (영어 작성)
2. Tone & Manner (영어 작성)
3. Style (영어 작성)
4. Colors (영어 작성)
5. Lighting (영어 작성)
6. Resolution (영어 작성)
7. 슬라이드 레이아웃
8. 상단 타이틀
9. [메인 콘텐츠 섹션들]
10. 인포그래픽 디테일
11. Forbidden Elements (영어 작성)
12. 최종 결과물 목표
```

---

## 메타 섹션 작성 규칙 (중요)

**Gemini API 한글 렌더링 문제 방지를 위해 메타 섹션(1~6, 11)은 영어로 작성:**

```
[INSTRUCTION - DO NOT RENDER IN IMAGE]

Purpose:
Generate a slide for official Korean government/national research institute R&D presentations.
[구체적인 슬라이드 목적 영어로 기술]

Tone & Manner:
- Trustworthy, public-oriented, technology-leading, future-oriented
- National Research Institute & Government Report Style
- Technical expression without exaggeration
- Visual explanation understandable by non-experts

Style:
- Clean industrial 3D rendering + minimal infographic
- Realistic industrial equipment proportions
- Subtle Isometric perspective
- Thin line icons, flat + 3D hybrid
- Sans-serif font (government report style)
- Minimize text, focus on visual elements
```

**슬라이드 콘텐츠(7~10, 12)는 한글 유지:**
- 타이틀, 라벨, 키워드 등 이미지에 표시될 텍스트는 한글
- 단, 한글 라벨에 영어 힌트를 병기하여 정확한 글리프 렌더링 유도

---

## 공통 톤앤매너

```
- 신뢰감, 공공성, 기술 선도, 미래지향
- National Research Institute & Government Report Style
- 과장 없는 기술 중심 표현
- 비전공자도 이해 가능한 시각적 설명
```

---

## 공통 스타일

```
- 정돈된 산업용 3D 렌더링 + 미니멀 인포그래픽
- 현실적인 산업 장비 비율
- 약한 Isometric 시점
- 얇은 라인 아이콘, 평면 + 입체 혼합
- Sans-serif 폰트 (정부 보고서 스타일)
- 텍스트 최소화, 시각 요소 중심
```

---

## 색상 팔레트 테마 시스템

### 테마 선택 가이드

분야 또는 목적에 따라 5가지 테마 중 선택:

| 테마 ID | 테마명 | 적합 분야 |
|:---|:---|:---|
| `gov-blue` | 정부 블루 | 정책, 공공, R&D, 국책과제 (기본값) |
| `tech-green` | 테크 그린 | 기술, 혁신, AI, 디지털 전환 |
| `industry-gray` | 산업 그레이 | 제조, 건설, 인프라, 산업 장비 |
| `research-purple` | 연구 퍼플 | 바이오, 의료, 기초과학, 헬스케어 |
| `eco-mint` | 환경 민트 | 환경, 에너지, 지속가능, 탄소중립 |

---

### 테마 1: 정부 블루 (gov-blue) - 기본값

**적합 분야**: 정책, 공공, R&D, 국책과제

| 역할 | 색상명 | HEX 코드 | RGB | 사용처 |
|:---|:---|:---|:---|:---|
| 메인 | 딥 블루 | #1E3A5F | 30, 58, 95 | 제목, 핵심 박스, 주요 강조 |
| 서브 | 미디엄 블루 | #4A90A4 | 74, 144, 164 | 연결선, 보조 박스, 프로세스 |
| 강조 | 오렌지 | #E07B39 | 224, 123, 57 | 경고, 핵심 포인트, 성과 |
| 배경 | 라이트 그레이 | #F5F7FA | 245, 247, 250 | 전체 배경 |

**70% 불투명도 변형 색상:**
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 서브 연한 | 라이트 블루 70 | #8FBBC9 |
| 메인 연한 | 딥 블루 70 | #6B849A |

---

### 테마 2: 테크 그린 (tech-green)

**적합 분야**: 기술, 혁신, AI, 디지털 전환

| 역할 | 색상명 | HEX 코드 | RGB | 사용처 |
|:---|:---|:---|:---|:---|
| 메인 | 딥 그린 | #1B4332 | 27, 67, 50 | 제목, 핵심 박스 |
| 서브 | 포레스트 그린 | #2D6A4F | 45, 106, 79 | 연결선, 보조 박스 |
| 강조 | 라이트 그린 | #40916C | 64, 145, 108 | 성과, 완료, 하이라이트 |
| 배경 | 민트 화이트 | #F0F4F0 | 240, 244, 240 | 전체 배경 |

**70% 불투명도 변형 색상:**
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 서브 연한 | 포레스트 70 | #6FA38A |
| 메인 연한 | 딥 그린 70 | #5D8574 |

---

### 테마 3: 산업 그레이 (industry-gray)

**적합 분야**: 제조, 건설, 인프라, 산업 장비

| 역할 | 색상명 | HEX 코드 | RGB | 사용처 |
|:---|:---|:---|:---|:---|
| 메인 | 차콜 네이비 | #2C3E50 | 44, 62, 80 | 제목, 핵심 박스 |
| 서브 | 슬레이트 그레이 | #5D6D7E | 93, 109, 126 | 연결선, 보조 박스 |
| 강조 | 앰버 오렌지 | #F39C12 | 243, 156, 18 | 경고, 핵심 포인트 |
| 배경 | 퓨어 화이트 | #FAFAFA | 250, 250, 250 | 전체 배경 |

**70% 불투명도 변형 색상:**
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 서브 연한 | 슬레이트 70 | #9AA5AF |
| 메인 연한 | 차콜 70 | #7A8A99 |

---

### 테마 4: 연구 퍼플 (research-purple)

**적합 분야**: 바이오, 의료, 기초과학, 헬스케어

| 역할 | 색상명 | HEX 코드 | RGB | 사용처 |
|:---|:---|:---|:---|:---|
| 메인 | 딥 퍼플 | #4A1A6B | 74, 26, 107 | 제목, 핵심 박스 |
| 서브 | 로얄 퍼플 | #7B2CBF | 123, 44, 191 | 연결선, 보조 박스 |
| 강조 | 핑크 퍼플 | #E040FB | 224, 64, 251 | 성과, 하이라이트 |
| 배경 | 라벤더 화이트 | #F8F5FA | 248, 245, 250 | 전체 배경 |

**70% 불투명도 변형 색상:**
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 서브 연한 | 로얄 70 | #AB73D4 |
| 메인 연한 | 딥 퍼플 70 | #8A5FA3 |

---

### 테마 5: 환경 민트 (eco-mint)

**적합 분야**: 환경, 에너지, 지속가능, 탄소중립

| 역할 | 색상명 | HEX 코드 | RGB | 사용처 |
|:---|:---|:---|:---|:---|
| 메인 | 딥 틸 | #0B525B | 11, 82, 91 | 제목, 핵심 박스 |
| 서브 | 민트 그린 | #3A9D7A | 58, 157, 122 | 연결선, 보조 박스 |
| 강조 | 라이트 민트 | #B4D6C1 | 180, 214, 193 | 배경 강조, 보조 |
| 배경 | 민트 화이트 | #F0FAF5 | 240, 250, 245 | 전체 배경 |

**70% 불투명도 변형 색상:**
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 서브 연한 | 민트 70 | #7DC4A8 |
| 메인 연한 | 딥 틸 70 | #5A9099 |

---

### 색상 표기 규칙 (중요)

- **투명도(%, alpha) 표현 금지**: `#4A90A4 at 70%` 같은 표현은 Gemini API가 "70%"를 이미지 내 텍스트로 렌더링할 수 있음
- **대체 방법**: 투명도가 필요한 경우 위 "70% 불투명도 변형 색상" 테이블의 별도 HEX 코드 사용
- **올바른 예**: `#8FBBC9` (라이트 블루 70)
- **잘못된 예**: `#4A90A4 at 70%`, `#4A90A470`, `rgba(74, 144, 164, 0.7)`

### 명도 대비 검증

모든 테마는 WCAG 2.0 AA 기준 충족:
- 메인 색상 위 흰색 텍스트: 대비율 4.5:1 이상
- 배경 위 메인 색상 텍스트: 대비율 4.5:1 이상

---

## 조명 및 해상도

```
조명:
- 부드러운 스튜디오 라이트
- 그림자 최소화
- 높은 가독성, 명확한 윤곽

해상도:
- Ultra High Resolution
- 8K Quality
- 프레젠테이션 및 인쇄 대응
```

---

## 텍스트 규격 (필수)

### 최소 폰트 크기 (렌더링 안전)

**14pt 미만 텍스트는 Gemini API 렌더링 시 깨짐/뭉개짐 발생. 반드시 최소 크기 준수.**

| 요소 | 최소 크기 | 권장 크기 | 최대 글자수 | 비고 |
|:---|:---:|:---:|:---:|:---|
| 대제목 | **28pt** | 32-36pt | 20자 | 슬라이드당 1개, Bold |
| 섹션 제목 | **20pt** | 22-24pt | 30자 | 최대 4개, Bold |
| 박스 라벨 | **14pt** | 16-18pt | 15자 | 필수 최소값, SemiBold |
| 소항목 | **14pt** | 14-16pt | 25자 | 필수 최소값, Regular |
| 캡션/주석 | **사용 금지** | - | - | 렌더링 깨짐 위험 |

### 폰트 스타일 권장

| 요소 | 굵기 | 색상 |
|:---|:---|:---|
| 대제목 | Bold | 메인 컬러 또는 화이트 (메인 박스 위) |
| 섹션 제목 | Bold | 메인 컬러 |
| 박스 라벨 | SemiBold | 메인/서브 컬러 또는 화이트 |
| 소항목 | Regular 또는 SemiBold | 다크 그레이 (#333333) |

### 텍스트 밀도 제한

| 제한 항목 | 최대값 |
|:---|:---:|
| 한 박스 내 텍스트 줄 수 | 3줄 |
| 한 라벨 내 줄 수 | 1줄 (줄바꿈 금지) |
| 슬라이드 전체 텍스트 요소 수 | 25개 |
| 한 영역 내 라벨 수 | 8개 |
| 라벨 간 최소 간격 | 20px |

---

## 렌더링 안전 규칙

### 금지 패턴 (사용 시 텍스트 깨짐)

```
Forbidden Text Patterns:
- Font size below 14pt (will become unreadable)
- More than 2 lines in a single label
- Text rotation (except 0° or 90°)
- Text over gradient backgrounds
- Narrow letter spacing
- Thin font weights (Light, Thin)
- Long sentences (use keywords only)
```

### 필수 규칙

- 배경색과 텍스트색 명도 대비 **4.5:1 이상**
- 텍스트 배경에 반투명 박스 권장 (가독성 향상)
- 한글 라벨에 영어 힌트 병기 (정확도 향상)
- 모든 텍스트는 **Bold 또는 SemiBold** 사용 (Regular 지양)

### 권장 텍스트 배치

```
텍스트 배치 원칙:
- 박스 내부에 충분한 패딩 (상하좌우 12px 이상)
- 텍스트와 박스 경계 사이 여백 확보
- 중요 텍스트는 중앙 또는 좌상단 정렬
- 복잡한 배경 위 텍스트 피하기
```

---

## 금지 요소 (모든 슬라이드 공통)

**영어로 작성하여 이미지에 렌더링되지 않도록 함:**

```
Forbidden Elements:
- Cartoon style
- Excessive SF, cyberpunk aesthetics
- Dark backgrounds
- Complex real-world backgrounds
- Exaggerated emotional expressions
- Unnecessary decorations
- Excessive glow/neon effects
- Watermarks, credits, or source text outside the slide content area
- Rendering any text from "Purpose", "Tone", or "Style" sections in the image
- Incorrect Korean characters (e.g., 관등 instead of 공동, 경부 instead of 국가)
- Font size below 14pt
- More than 25 text elements per slide
- Text over complex gradient backgrounds
```

---

## 텍스트 규칙

```
- 모든 라벨은 한글
- 기술 용어는 영어 병기 가능 (Cross-Embodiment, MLOps 등)
- 키워드 수준만 허용 (문장형 설명 금지)
- 핵심 마일스톤은 ★ 표시
```

### 한글 라벨 정확도 향상 (영어 힌트 병기)

Gemini API의 한글 글리프 렌더링 오류 방지를 위해, 중요한 한글 라벨에 영어 힌트 병기:

**예시:**
```
라벨: "공동연구기관" (Korean: 공동연구기관, meaning "Joint Research Institutions")
라벨: "주관기관" (Korean: 주관기관, meaning "Lead Organization")
라벨: "참여기업" (Korean: 참여기업, meaning "Participating Companies")
```

**적용 대상:**
- 섹션 제목 라벨 (예: 공동연구기관, 자문기관, 참여기업)
- 기관명 라벨 (예: 한국기계연구원, 농촌진흥청)
- 역할 라벨 (예: 기술 개발, 실증 데이터)

---

## 품질 체크리스트

프롬프트 작성 완료 후 다음 항목 확인:

### 필수 검증 (모두 충족해야 함)

- [ ] 모든 텍스트 최소 14pt 이상
- [ ] 대제목 28pt 이상
- [ ] 슬라이드 전체 텍스트 요소 25개 이하
- [ ] 한 박스 내 텍스트 3줄 이하
- [ ] 투명도 % 표현 없음 (HEX 코드만 사용)
- [ ] 메타 섹션(1~6, 11) 영어로 작성
- [ ] 콘텐츠 섹션(7~10, 12) 한글로 작성
- [ ] 테마 색상 일관성 유지

### 권장 검증

- [ ] 핵심 라벨에 영어 힌트 병기
- [ ] 명도 대비 4.5:1 이상
- [ ] Bold/SemiBold 폰트 사용
- [ ] 레이아웃 가이드 권장 요소 수 준수
