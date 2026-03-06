<ultrawork-mode />

# visual-generator 프롬프트 시스템 전면 개편 (v2.0.0)

## 배경

visual-generator 플러그인의 현재 4-block 프롬프트 시스템(INSTRUCTION / CONFIGURATION / CONTENT / FORBIDDEN)은 Gemini 이미지 생성 모델(gemini-3-pro-image-preview)과 구조적으로 부적합하다.

### 현재 문제점

1. **텍스트 유출**: CONTENT 블록의 번호 목록(`1.`, `2.`, `3.`)이 이미지에 숫자로 렌더링됨. INSTRUCTION 블록의 메타데이터("Image Purpose:", "Target Audience:")도 텍스트로 나타남.
2. **한글 렌더링 품질**: 폰트/타이포그래피 힌트가 FORBIDDEN에서 금지되어 있어, Gemini가 한글에 적합한 서체를 선택할 단서가 없음. 작은 한글이 깨짐.
3. **콘텐츠 추출 부정확**: content-organizer가 "렌더링할 텍스트"와 "장면 설명용 컨텍스트"를 구분하지 않아, 내러티브 문장("오늘 발표의 방향을 프레이밍합니다")이 이미지 텍스트로 들어감.
4. **FORBIDDEN 블록의 역효과**: 부정형 프레이밍("~하지 마라")은 Gemini가 해당 개념을 활성화시켜 오히려 금지된 요소가 등장할 확률을 높임.
5. **번호 참조 시스템의 한계**: `Title N`, `Main N`, `Data N` 간접 참조는 Content Placement과 CONTENT 간 1:1 대응을 수동으로 검증해야 하며, 고아 항목이 빈번함.

### 목표 상태

4-block 마크다운 → **5개 XML 태그 기반 자연어 프롬프트**로 전환. 지시(instruction)와 렌더링 텍스트(content)를 XML 태그로 구조적으로 분리하여 Gemini가 태그 내부의 문자열만 이미지에 표시하도록 유도.

---

## 신규 XML-Tag 프롬프트 구조

### 5개 태그 정의

| 태그 | 역할 | 내용 형식 |
|------|------|-----------|
| `<scene>` | 크리에이티브 디렉터 스타일 장면 묘사 | 자연어 3~5문장. 분위기, 조명, 시각 메타포 서술 |
| `<text_to_render>` | 이미지에 **실제로 표시할 텍스트만** | `key: "value"` 쌍. value는 반드시 따옴표로 감쌈 |
| `<typography>` | 서체 스타일 힌트 + 한글 가독성 지시 | 서체 계열, 크기 비율, 강조 방식, 한글 렌더링 힌트 |
| `<canvas>` | 해상도, 배경, 팔레트 | 기술적 스펙을 자연어로 서술 |
| `<layout>` | 공간 배치 | 자연어 3~5문장. `<text_to_render>`의 항목을 따옴표로 인용하며 위치 지정 |

### 프롬프트 예시 (seminar 테마)

```xml
<scene>
에디토리얼 매거진 표지 느낌의 아이소메트릭 3D 인포그래픽 슬라이드.
따뜻한 그라데이션 배경 위로 반투명 프로스티드 글래스 카드가 세 개 떠 있으며,
각 카드 위에 포토리얼리스틱 3D 아이콘이 놓여 있다.
전체적으로 기술 매거진의 커버 스토리 같은 세련된 분위기.
</scene>

<text_to_render>
title: "스마트 팩토리 혁신 전략"
subtitle: "2026년 제조업 디지털 전환"
card_1: "실시간 모니터링"
card_2: "예지 정비"
card_3: "자율 최적화"
kpi_1: "생산성 34% 향상"
kpi_2: "불량률 0.3%"
</text_to_render>

<typography>
제목은 Bold Modern Korean Sans-serif(고딕 계열)로, 부제목 대비 2배 크기.
카드 라벨은 Medium 굵기, KPI 수치는 Bold로 강조.
모든 한글은 선명하고 또렷하게(crisp anti-aliased Korean typography).
전문적 타이포세팅 품질.
</typography>

<canvas>
3840×2160 해상도, 16:9 비율.
배경은 #F8F9FA(오프화이트)에서 #E8ECF0으로의 미세한 그라데이션.
주조색 #2C3E50(네이비), 보조색 #5D6D7E(슬레이트), 강조색 #2980B9(딥블루).
</canvas>

<layout>
"스마트 팩토리 혁신 전략"은 상단 1/5 영역에 좌측 정렬로 크게 배치.
"2026년 제조업 디지털 전환"은 제목 바로 아래에 작게.
세 개의 프로스티드 글래스 카드를 중앙 영역에 수평으로 균등 배치하고,
각 카드 안에 "실시간 모니터링", "예지 정비", "자율 최적화"를 표시.
하단 영역에 "생산성 34% 향상"과 "불량률 0.3%"를 나란히 배치.
</layout>
```

### 핵심 원칙

1. **XML 태그 = 인지적 컨테이너**: Gemini는 태그명과 메타데이터를 무시하고 `<text_to_render>` 내부 value만 렌더링
2. **자연어 문장**: 번호 목록 절대 사용하지 않음 (모델이 숫자를 텍스트로 렌더링)
3. **긍정형 프레이밍만**: FORBIDDEN 블록 대신, `<scene>`과 `<layout>`에서 원하는 것만 서술
4. **한글 서체 힌트 필수**: `<typography>`에 "Korean Sans-serif (Gothic style)" 또는 구체적 서체 계열 명시
5. **따옴표 인용**: `<layout>`에서 텍스트를 참조할 때 반드시 `<text_to_render>`의 value를 따옴표로 인용

---

## 수정 대상 파일 (7개 + 버전/문서 3개 = 10개)

### 1. `agents/prompt-designer.md` — 전면 재작성 (CRITICAL)

**현재**: 989줄, 4-block 생성기
**목표**: ~350줄, XML-tag 생성기

변경사항:

- frontmatter description: `"4-block 이미지 프롬프트 생성 에이전트"` → `"XML-tag 이미지 프롬프트 생성 에이전트"`
- `## 4-Block Prompt Structure` 섹션 전체 → `## XML-Tag Prompt Structure`로 교체
- Block 1~4 정의 → 5개 XML 태그 정의 (위 구조 참조)
- Content Placement의 `Title N`, `Main N`, `Data N` 번호 참조 → `<layout>`에서 따옴표 직접 인용
- FORBIDDEN 블록 → 삭제. 대신 `## MUST NOT DO` 섹션에 에이전트 레벨 금지사항만 유지
- 테마별 분기 로직:
  - concept: `<text_to_render>` 비워두고 `<scene>`만 풍부하게
  - gov/seminar: `<text_to_render>` 최대 25항목, 개조식 스타일
  - whatif: `<scene>`에 미래 비전 장면, `<text_to_render>` 최대 20항목
  - pitch: `<text_to_render>` 최대 18항목, 거대 숫자 강조
  - comparison: LEFT/RIGHT `<scene>` 분리, `<text_to_render>` 최대 12항목
- 출력 포맷: 각 슬라이드별 `.md` 파일에 5개 XML 태그 블록

### 2. `skills/theme-seminar/SKILL.md` — 구조 개선

변경사항:

- 기존 "Rendering Style" 7차원 → `<scene>` 작성 가이드로 전환 (서피스, 배경, 코너, 연결선, 시각장식, 공간구성, 시각메타포를 자연어 장면 묘사로)
- "FORBIDDEN" 금지목록 → 긍정형 `<scene>` 작성 예시로 대체. 예) ~~"Figure captions 금지"~~ → "장면 묘사에 3D 아이콘과 프로스티드 글래스 카드만 포함"
- 신규 섹션: `## 한글 타이포그래피 가이드`
  - 권장 서체 힌트: "Bold Modern Korean Sans-serif (Gothic style, e.g. Nanum Gothic, Pretendard)"
  - 크기 비율: 제목 > 부제목 > 카드라벨 > KPI
  - 가독성 키워드: "Crisp anti-aliased Korean typography", "Professional typesetting"
- 신규 섹션: `## XML-Tag 출력 매핑`
  - 무드별 `<scene>` 톤 가이드 (technical-report은 차분하게, innovation은 역동적으로)

### 3. `agents/content-organizer.md` — 텍스트 분류 체계 추가

변경사항:

- concepts.md 출력 스키마에 2개 필드 추가:
  - `render_text`: 이미지에 실제로 표시할 텍스트 목록 (제목, 키워드, 수치)
  - `scene_context`: 장면 묘사에만 사용할 맥락 설명 (이미지에 텍스트로 표시 안 됨)
- 매핑 규칙 명시:
  - 슬라이드 제목, 핵심 키워드, 통계 수치 → `render_text`
  - 핵심 메시지, 서술적 설명, 발표 스크립트 → `scene_context`
  - 구분 기준: "이 텍스트가 이미지 위에 글자로 보여야 하는가?"
- `slide_plan.md` 테이블에 `render_text_count` 컬럼 추가

### 4. `agents/renderer-agent.md` — 검증 로직 교체

변경사항:

- 기존 13개 grep 기반 검증 → XML 태그 기반 검증으로 전환:
  - 검증 1: 5개 XML 태그 존재 여부 (`<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>`)
  - 검증 2: `<text_to_render>` 내부가 `key: "value"` 형식인지
  - 검증 3: `<layout>`에서 `<text_to_render>`의 value를 따옴표로 인용하는지
  - 검증 4: 번호 목록 패턴(`1.`, `2.`, `- `) 부재
  - 검증 5: pt/px 단위 부재
  - 검증 6: 마크다운 포맷(`**`, `*`, `#`) 부재
  - 검증 7: 테마별 `<text_to_render>` 항목 수 상한 준수
  - 검증 8: `<typography>`에 한글 서체 힌트 포함 여부
- 기존 검증 중 유지할 것: hallucinated URL, placeholder, language mixing 체크

### 5. `agents/content-reviewer.md` — 평가 기준 추가

변경사항:

- 기존 4개 평가 차원에 5번째 추가:
  - `## 5. 텍스트 추출 정확성` (Text Extraction Accuracy)
    - render_text에 서술적 문장이 포함되지 않았는가? (1~5점)
    - scene_context에 렌더링 대상 키워드가 누락되지 않았는가? (1~5점)
    - render_text 항목 수가 테마별 상한을 초과하지 않는가? (1~5점)
- PASS/REJECT 로직에 5번째 차원 반영

### 6. `commands/visual-generate.md` — 오케스트레이터 (최소 수정)

변경사항:

- Phase 3 prompt-designer 호출 시 프롬프트에 "XML-tag 형식으로 생성" 명시
- Phase 4 renderer-agent 호출 시 "XML-tag 검증 수행" 명시
- 나머지 파이프라인 구조는 유지

### 7. 나머지 5개 테마 스킬 — 동일 패턴 적용

`theme-concept`, `theme-gov`, `theme-whatif`, `theme-pitch`, `theme-comparison` 각각:

- "Rendering Style" 7차원 → `<scene>` 작성 가이드로 전환
- FORBIDDEN 목록 → 긍정형 가이드로 전환
- 한글 타이포그래피 가이드 추가 (seminar와 동일 구조)
- XML-Tag 출력 매핑 섹션 추가

### 8~10. 버전/문서

- `.claude-plugin/plugin.json`: 버전 → `2.0.0` (MAJOR: 프롬프트 구조 호환성 깨짐)
- `.claude-plugin/marketplace.json`: visual-generator 버전 동기화
- `AGENTS.md`: 날짜 + visual-generator 설명 업데이트

---

## 작업 순서

```
Phase 1: 핵심 엔진 (prompt-designer.md + theme-seminar/SKILL.md)
Phase 2: 입력 파이프라인 (content-organizer.md)
Phase 3: 검증 파이프라인 (renderer-agent.md + content-reviewer.md)
Phase 4: 오케스트레이터 (visual-generate.md)
Phase 5: 나머지 5개 테마 스킬 (theme-concept, theme-gov, theme-whatif, theme-pitch, theme-comparison)
Phase 6: 버전 + 문서 (plugin.json + marketplace.json + AGENTS.md)
```

---

## 검증 기준

모든 작업 완료 후 아래를 확인:

1. **구 시스템 완전 제거**: `INSTRUCTION`, `CONFIGURATION`, `CONTENT`, `FORBIDDEN`, `4-block`, `Title N`, `Main N`, `Data N` 패턴이 visual-generator 전체에서 0건 (MUST NOT DO 경고 문구 제외)
2. **신 시스템 존재**: `<scene>`, `<text_to_render>`, `<typography>`, `<canvas>`, `<layout>` 패턴이 prompt-designer + renderer-agent + 7개 테마 스킬에 분포
3. **render_text/scene_context**: content-organizer + content-reviewer에 존재
4. **한글 타이포그래피**: 7개 테마 스킬 모두에 "Korean Sans-serif" 또는 "Gothic style" 힌트 존재
5. **번호 목록 부재**: prompt-designer의 출력 예시에 `1.`, `2.`, `- ` 패턴 없음
6. **버전 일치**: plugin.json과 marketplace.json 모두 `2.0.0`

---

## 절대 금지

- 모델을 `gemini-3-pro-image-preview` 외 다른 것으로 변경하지 않음
- `generate_slide_images.py` 스크립트를 수정하지 않음 (렌더링 스크립트는 그대로)
- 테마별 색상 팔레트(9종 무드 × 4색)를 변경하지 않음
- 24종 레이아웃 정의(`layout-types/SKILL.md`)를 변경하지 않음
- `slide-renderer/SKILL.md`를 변경하지 않음
