---
name: hwpx-math
description: 수학/시험지 JSON을 한컴 수식 기반 HWPX로 변환하는 스킬입니다. Use when 학력평가형 수학 문제지 또는 워크시트 HWPX를 자동 생성해야 할 때.
---

# hwpx-math

수학 문제 JSON을 입력받아 `hp:equation` 기반 HWPX 문제지를 생성한다.
본 스킬은 HWPX를 XML-first 방식으로 조립하며, 검증/패키징은 `hwpx-core` 스킬 도구를 재사용한다.

## 목적과 범위

- 입력: 학력평가(exam) 또는 worksheet 형식의 문제 JSON
- 출력: 2단(2-column) 수학 문제지 HWPX
- 수식 표기: 한컴 수식 스크립트만 허용 (`LaTeX 금지`)
- 스크립트 참조는 상대경로 우선, 실패 시 Glob 폴백

## 환경 설정

```bash
# SKILL.md가 있는 현재 스킬 루트
export SKILL_DIR="$(pwd)"

# hwpx-core 스킬 루트 (검증/패키징 도구 사용)
export HWPX_CORE_SKILL_DIR="${SKILL_DIR}/../hwpx-core"

# 가상환경 활성화 (프로젝트 정책에 맞게 경로 지정)
source ".venv/bin/activate"
```

경로 규칙:
- 모든 명령은 `$SKILL_DIR` 또는 `$HWPX_CORE_SKILL_DIR` 기준 상대 경로를 사용한다.
- 절대경로 하드코딩 금지.

## build_math_hwpx.py 스크립트 경로 해석 (3-step)

Step 1. 상대경로(최우선)
- `scripts/build_math_hwpx.py`

Step 2. Glob 폴백
- `**/hwpx-generator/skills/hwpx-math/scripts/build_math_hwpx.py`

Step 3. Glob 확장 탐색
- `**/build_math_hwpx.py`

스크립트를 찾지 못하면:
- 자체 Python 코드를 작성해 대체하지 말고 즉시 중단 후 경로 확인 요청.

## JSON -> HWPX 핵심 워크플로우

1) 문제 JSON 작성 (`exam` 또는 `worksheet`)
2) `build_math_hwpx.py`로 `Contents/section0.xml` 생성 및 패키징
3) `hwpx-core` `validate.py`로 무결성 검증
4) 필요 시 `unpack.py`/`pack.py`로 후편집

예시:

```bash
python "$SKILL_DIR/scripts/build_math_hwpx.py" \
  --problems "$SKILL_DIR/examples/exam-sample.json" \
  --output "$SKILL_DIR/output/math-exam.hwpx" \
  --creator "math-team"
```

worksheet 명시 예시:

```bash
python "$SKILL_DIR/scripts/build_math_hwpx.py" \
  --problems "$SKILL_DIR/examples/worksheet-sample.json" \
  --exam-type worksheet \
  --title "중2 일차방정식 워크시트" \
  --output "$SKILL_DIR/output/math-worksheet.hwpx"
```

## 문제 JSON 포맷

### A) 학력평가/수능형 (exam, 기본)

```json
{
  "exam_type": "학력평가",
  "year": 2026,
  "month": 3,
  "grade": "중3",
  "session": 2,
  "subject_area": "수학",
  "total_pages": 4,
  "question_type_label": "5지선다형",
  "problems": [
    {
      "text": "다음 방정식의 해는?",
      "equation": "2x + 3 = 11",
      "points": 3,
      "choices": ["2", "3", "4", "5", "6"]
    },
    {
      "section_label": "주관식",
      "text": "식을 인수분해하시오.",
      "equation": "x^2 - 5x + 6",
      "points": 4
    }
  ]
}
```

### B) worksheet형

```json
{
  "exam_type": "worksheet",
  "title": "중1 정수와 유리수",
  "subtitle": "기초 연산 연습",
  "problems": [
    {
      "text": "다음을 계산하시오.",
      "equation": "-3 + 7",
      "choices": ["2", "3", "4", "5", "6"]
    },
    {
      "text": "제곱근을 간단히 하시오.",
      "equation": "sqrt 12 + sqrt 27"
    }
  ]
}
```

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `exam_type` | string | O | `학력평가`, `수능`, `exam`, `worksheet` |
| `year` | int | exam 권장 | 학년도 |
| `month` | int | exam 권장 | 시행 월 |
| `grade` | string | exam 권장 | `중1~고3` |
| `session` | int | X | 교시, 기본 2 |
| `subject_area` | string | X | 기본 `수학` |
| `total_pages` | int | X | 총 페이지, 미지정 시 자동 |
| `question_type_label` | string | X | 예: `5지선다형` |
| `title` | string | worksheet 권장 | worksheet 제목 |
| `subtitle` | string | X | worksheet 부제 |
| `problems` | array | O | 문제 목록 |
| `problems[].text` | string | X | 문제 본문 |
| `problems[].equation` | string | X | 한컴 수식 스크립트 |
| `problems[].points` | int | exam 필수 | 배점 |
| `problems[].choices` | array | X | 객관식 보기 |
| `problems[].section_label` | string | X | 예: `주관식` |
| `problems[].sub_problems` | array | X | 소문제 목록 |

## 수식 작성 규칙 (핵심)

- 수식은 `hp:script` 텍스트로 전달한다.
- 한컴 수식 스크립트만 사용한다.
- LaTeX (`\\frac`, `\\sqrt`, `\\sum`) 금지.

권장 예시:
- 분수: `{a+b} over {c+d}`
- 루트: `sqrt {x^2 + 1}`
- 극한: `lim _{x -> 0} {sin x} over x`
- 시그마: `sum _{k=1} ^{n} k`

## Equation XML 구조 (요약)

상세 스펙은 `references/equation-reference.md`를 따른다.

```xml
<hp:p paraPrIDRef="22" styleIDRef="0">
  <hp:run charPrIDRef="9">
    <hp:equation id="1000000099" type="0" textColor="#000000" baseUnit="1000" lineThickness="100">
      <hp:sz width="0" height="0" widthRelTo="ABS" heightRelTo="ABS"/>
      <hp:pos treatAsChar="1" flowWithText="0" vertRelTo="PARA" horzRelTo="PARA"/>
      <hp:script>x = {-b +- sqrt {b^2 - 4ac}} over {2a}</hp:script>
    </hp:equation>
  </hp:run>
</hp:p>
```

요점:
- `baseUnit="1000"` (10pt 기준)
- `treatAsChar="1"` (문단 내 수식 배치)
- ID는 문서 내 유일해야 함

## 2-column 레이아웃과 페이지 설정

section 시작 문단에서 다단 설정:

```xml
<hp:colPr type="NEWSPAPER" layout="LEFT" colCount="2" sameSz="1" sameGap="2268"/>
```

권장 페이지 설정(문제지 특화):

```xml
<hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY">
  <hp:margin left="5668" right="5668" top="4252" bottom="4252" header="4252" footer="4252" gutter="0"/>
</hp:pagePr>
```

## 스타일 ID 맵

상세는 템플릿 XML 기준으로 유지한다.

### charPr

| ID | 용도 |
|---|---|
| 7 | worksheet 제목 |
| 8 | 문제 번호 |
| 9 | 문제 본문/수식 |
| 10 | 단원명/소제목 |
| 11 | 선택지 |
| 12 | 시험 제목줄 |
| 13 | 과목 영역 대제목 |
| 14 | 교시 라벨 |
| 15 | 시험 문제번호 |
| 16 | 배점 |
| 17 | 페이지 번호 |

### paraPr

| ID | 용도 |
|---|---|
| 20 | worksheet 제목(center) |
| 21 | 문제 본문(left) |
| 22 | 수식 문단(left) |
| 23 | 선택지 세로 배열 |
| 24 | 시험 제목줄(center) |
| 25 | 교시+과목 라인 |
| 26 | 과목 영역 대제목(center) |
| 27 | 선택지 가로(tabPr=3) |
| 28 | 문항유형 라벨(테두리) |
| 29 | 하단 페이지 번호(center) |

### tabPr

| ID | 용도 |
|---|---|
| 3 | 5지선다 가로 탭스톱 |

### borderFill

| ID | 용도 |
|---|---|
| 5 | 문제 구분선 (하단 DASH) |
| 6 | 라벨 테두리 |
| 7 | 페이지번호 박스 |

## 학력평가(exam) 레이아웃 구조

1) 1단 헤더: 연도/월/학년/교시/과목 영역
2) 2단 본문: 문제 + 배점 + 가로 선택지
3) 필요 시 하단 페이지 번호 박스

선택지는 탭 기반으로 가로 배열한다.

```text
① 보기1    ② 보기2    ③ 보기3    ④ 보기4    ⑤ 보기5
```

## hwpx-core 스킬 검증 도구 사용

Step 1. 상대경로: `../hwpx-core/scripts/validate.py`
Step 2. Glob 폴백: `**/hwpx-core/scripts/validate.py`
Step 3. Glob: `**/validate.py`

검증 예시:

```bash
python "$SKILL_DIR/../hwpx-core/scripts/validate.py" "$SKILL_DIR/output/math-exam.hwpx"
```

추가 연동 도구(상대경로 기준):

```bash
python "$SKILL_DIR/../hwpx-core/scripts/office/unpack.py" "$SKILL_DIR/output/math-exam.hwpx" "$SKILL_DIR/tmp/unpacked"
python "$SKILL_DIR/../hwpx-core/scripts/office/pack.py" "$SKILL_DIR/tmp/unpacked" "$SKILL_DIR/output/math-exam-edited.hwpx"
```

## 문제지 특화 단위 변환

| 항목 | HWPUNIT | 비고 |
|---|---:|---|
| 1pt | 100 | 폰트 기본 단위 |
| 10pt | 1000 | 수식 기본 baseUnit |
| 1mm | 283.5 | 근사값 |
| A4 폭 | 59528 | 210mm |
| A4 높이 | 84186 | 297mm |
| 좌우 여백 | 5668 | 20mm |
| 상하 여백 | 4252 | 15mm |
| 단간격 | 2268 | 8mm |

## 템플릿 경로 정책

- `templates/base/` 대신 `templates/math-base/`를 사용한다. (템플릿 충돌 방지)
- 모든 템플릿 경로는 `$SKILL_DIR/templates/...`로 참조한다.

예시:

```bash
python "$SKILL_DIR/scripts/build_math_hwpx.py" \
  --template-dir "$SKILL_DIR/templates/math-base" \
  --problems "$SKILL_DIR/examples/exam-sample.json" \
  --output "$SKILL_DIR/output/math-exam.hwpx"
```

## References 분리 정책

SKILL.md를 500줄 이하로 유지하기 위해 상세 레퍼런스를 분리한다.

- 한컴 수식 전체 스크립트 사전(기본~미적분/기하): `references/equation-reference.md`
- 도형/그래프 전체 스펙(triangle/circle/quadrilateral/coordinate/solid3d): `references/geometry-reference.md`

본 문서에는 구현/운영에 필요한 최소 규칙만 유지한다.

## Critical Rules

1. LaTeX 금지, 한컴 수식 스크립트만 사용.
2. `problems[]`는 비어 있으면 안 되며, exam 형식은 `points`를 필수로 가진다.
3. section XML의 ID(`hp:p`, `hp:equation`)는 중복 금지.
4. `secPr`/`colPr` 누락 금지 (문서 레이아웃 파손).
5. 생성 후 반드시 `hwpx-core` `validate.py`로 검증.
6. 절대경로/하드코딩 경로 금지, `$SKILL_DIR` 기준 경로만 사용.
7. 스크립트를 못 찾으면 자체 코드로 대체하지 말고 경로 해석 규칙(3-step) 적용.
