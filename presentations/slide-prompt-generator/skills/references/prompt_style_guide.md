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

## 색상 팔레트

### 기본 팔레트
| 용도 | 색상명 | HEX 코드 |
|:---|:---|:---|
| 메인/강조 | 딥 블루 | #1E3A5F |
| 서브/연결 | 미디엄 블루 | #4A90A4 |
| 배경/보조 | 라이트 블루 | #A8C5D9 |
| 성과/완료 | 그린 | #2E7D5A |
| 보조 그린 | 민트 | #3A9D7A |
| 경고/강조 | 오렌지 | #E07B39 |
| 배경 | 화이트/라이트 그레이 | #FFFFFF / #F5F7FA |

### 분야별 색상
| 분야 | 색상 |
|:---|:---|
| 건설 | 네이비/딥 블루 (#1E3A5F) |
| 농업 | 민트/그린 (#2E7D5A) |
| 재난·구조 | 블루 + 오렌지 (#4A90A4 + #E07B39) |

### 투명도 변형 색상 (70% 불투명도 대체)
| 용도 | 색상명 | HEX 코드 | 원본 색상 |
|:---|:---|:---|:---|
| 연구기관/대학 | 라이트 블루 70 | #8FBBC9 | #4A90A4 기반 |
| 참여기업 | 라이트 그린 70 | #6FAD93 | #2E7D5A 기반 |

### 색상 표기 규칙 (중요)
- **투명도(%, alpha) 표현 금지**: `#4A90A4 at 70%` 같은 표현은 Gemini API가 "70%"를 이미지 내 텍스트로 렌더링할 수 있음
- **대체 방법**: 투명도가 필요한 경우 위 "투명도 변형 색상" 테이블의 별도 HEX 코드 사용
- **올바른 예**: `#8FBBC9` (라이트 블루 70)
- **잘못된 예**: `#4A90A4 at 70%`, `#4A90A470`, `rgba(74, 144, 164, 0.7)`

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
