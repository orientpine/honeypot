---
name: hwpx-core
description: "HWPX XML-first document authoring skill for create/edit/read/validate workflows and template-driven generation. Use when you need deterministic Korean document layout control via section0.xml/header.xml and script-based build pipelines instead of opaque editors."
---

# HWPX Core

HWPX XML-first 스킬입니다. 핵심 원칙은 `section0.xml` + `header.xml`을 직접 제어하고,
`build_hwpx.py`로 문서를 조립한 뒤 `validate.py`로 무결성을 확인하는 것입니다.

상세한 XML 요소 해설, 고급 표 산식 예시, 심화 네임스페이스 레퍼런스는
`$SKILL_DIR/references/`로 분리해 유지합니다.

## 기본 동작 모드 (필수): 첨부 HWPX 분석 → 고유 XML 복원(99% 근접) → 요청 반영 재작성

사용자가 `.hwpx`를 첨부한 경우, 이 스킬은 아래 순서를 **기본값**으로 따른다.

1. **레퍼런스 확보**: 첨부된 HWPX를 기준 문서로 사용
2. **심층 분석/추출**: `analyze_template.py`로 `header.xml`, `section0.xml` 추출
3. **구조 복원**: header 스타일 ID/표 구조/셀 병합/여백/문단 흐름을 최대한 동일하게 유지
4. **요청 반영 재작성**: 사용자가 요구한 텍스트/데이터만 교체하고 구조는 보존
5. **빌드/검증**: `build_hwpx.py` + `validate.py`로 결과 산출 및 무결성 확인
6. **쪽수 가드(필수)**: `page_guard.py`로 레퍼런스 대비 페이지 드리프트 위험 검사

### 99% 근접 복원 기준 (실무 체크리스트)

- `charPrIDRef`, `paraPrIDRef`, `borderFillIDRef` 참조 체계 동일
- 표의 `rowCnt`, `colCnt`, `colSpan`, `rowSpan`, `cellSz`, `cellMargin` 동일
- 문단 순서, 문단 수, 주요 빈 줄/구획 위치 동일
- 페이지/여백/섹션(secPr) 동일
- 변경은 사용자 요청 범위(본문 텍스트, 값, 항목명 등)로 제한

### 쪽수 동일(100%) 필수 기준

- 사용자가 레퍼런스를 제공한 경우 **결과 문서의 최종 쪽수는 레퍼런스와 동일해야 한다**
- 쪽수가 늘어날 가능성이 보이면 먼저 텍스트를 압축/요약해서 기존 레이아웃에 맞춘다
- 사용자 명시 요청 없이 `hp:p`, `hp:tbl`, `rowCnt`, `colCnt`, `pageBreak`, `secPr`를 변경하지 않는다
- `validate.py` 통과만으로 완료 처리하지 않는다. 반드시 `page_guard.py`도 통과해야 한다
- `page_guard.py` 실패 시 결과를 완료로 제출하지 않고, 원인(길이 과다/구조 변경)을 수정 후 재빌드한다
- 가능하면 한글(또는 사용자의 확인) 기준 최종 쪽수 값을 확인하고 레퍼런스와 일치 여부를 재확인한다

### 기본 실행 명령 (첨부 레퍼런스가 있을 때)

```bash
# 1) 레퍼런스 분석 + XML 추출
python3 "$SKILL_DIR/scripts/analyze_template.py" reference.hwpx \
  --extract-header /tmp/ref_header.xml \
  --extract-section /tmp/ref_section.xml

# 2) /tmp/ref_section.xml을 복제해 /tmp/new_section0.xml 작성
#    (구조 유지, 텍스트/데이터만 요청에 맞게 수정)

# 3) 복원 빌드
python3 "$SKILL_DIR/scripts/build_hwpx.py" \
  --header /tmp/ref_header.xml \
  --section /tmp/new_section0.xml \
  --output result.hwpx

# 4) 검증
python3 "$SKILL_DIR/scripts/validate.py" result.hwpx

# 5) 쪽수 드리프트 가드 (필수)
python3 "$SKILL_DIR/scripts/page_guard.py" \
  --reference reference.hwpx \
  --output result.hwpx
```

## 디렉토리 기준

- `SKILL_DIR`: `SKILL.md`가 위치한 `/hwpx-generator:hwpx-core` 디렉토리의 절대 경로
- 스크립트: `$SKILL_DIR/scripts/`
- 템플릿: `$SKILL_DIR/templates/`
- 심화 레퍼런스: `$SKILL_DIR/references/`

## 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로를 기준으로 찾습니다.

**Step 1. 상대경로로 실행 (최우선)**

```bash
python scripts/build_hwpx.py --output result.hwpx
```

**Step 2. 상대경로 실패 시 Glob 폴백**

```text
Glob: **/hwpx-generator/skills/hwpx-core/scripts/build_hwpx.py
```

**Step 3. Glob도 실패 시 확장 탐색**

```text
Glob: **/build_hwpx.py
```

절대 금지: 스크립트를 찾지 못했을 때 자체 Python 코드를 작성하지 않습니다.
즉시 중단 후 경로 확인을 요청합니다.

## 스크립트 요약 (13)

| Script | Purpose |
|---|---|
| `scripts/build_hwpx.py` | 템플릿 + XML 오버라이드로 `.hwpx` 조립 |
| `scripts/zip_surgery.py` | 기존 HWPX 안전 편집 (ZIP-level surgery, 바이트 레벨 보존) |
| `scripts/cell_writer.py` | linesegarray 생성 + 셀/테이블 높이 자동 조정 (XML-first/pack 전용) |
| `scripts/analyze_template.py` | 레퍼런스 HWPX 구조/스타일 분석 |
| `scripts/page_guard.py` | 레퍼런스 대비 페이지 드리프트 위험 검사 (필수 게이트) |
| `scripts/text_extract.py` | 본문/표 텍스트 추출 |
| `scripts/validate.py` | ZIP/XML/필수 엔트리 구조 검증 (`--strict`: surgery 호환성 검증) |
| `scripts/office/unpack.py` | HWPX를 디렉토리로 풀어 XML 편집 준비 |
| `scripts/office/pack.py` | 수정 디렉토리를 HWPX로 재패키징 |
| `scripts/md_parser.py` | 마크다운 → 구조화 JSON 파싱 (`python3 md_parser.py <input.md> --output <output.json>`) |
| `scripts/xml_writer.py` | JSON → HWPX XML 프래그먼트 생성 (`python3 xml_writer.py --input <parsed.json> --style-config <styles.json> --output <fragment.xml>`) |
| `scripts/image_embedder.py` | HWPX에 이미지 ZIP-level 임베딩 (`python3 image_embedder.py --hwpx <.hwpx> --images-dir <dir> --mapping <map.json> --max-width <int> --quality <int> --output <out.hwpx>`) |
| `scripts/proofread.py` | 이중 불릿, 줄바꿈 오류, 스타일 미적용 문단 자동 교정 |
| `scripts/md_merger.py` | 다중 MD 파일 병합, heading offset 자동 계산 | CLI: `python3 md_merger.py files --target-level N --output merged.json` |

## 단위 변환 (HWP Units)

| Item | Value | Note |
|---|---:|---|
| 1 pt | 100 HWPUNIT | 폰트/문단 기본 단위 |
| 10 pt | 1000 HWPUNIT | 기본 본문 크기 예시 |
| 1 mm | 283.5 HWPUNIT | 실무 근사치 |
| 1 cm | 2835 HWPUNIT | 실무 근사치 |
| A4 width | 59528 HWPUNIT | 210 mm |
| A4 height | 84186 HWPUNIT | 297 mm |
| Left/Right margin | 8504 HWPUNIT | 30 mm |
| Body width | 42520 HWPUNIT | 59528 - 8504 x 2 |

## 템플릿별 스타일 ID 맵

### base (기본)

| ID | 유형 | 설명 |
|----|------|------|
| charPr 0 | 글자 | 10pt 함초롬바탕, 기본 |
| charPr 1 | 글자 | 10pt 함초롬돋움 |
| charPr 2~6 | 글자 | Skeleton 기본 스타일 |
| paraPr 0 | 문단 | JUSTIFY, 160% 줄간격 |
| paraPr 1~19 | 문단 | Skeleton 기본 (개요, 각주 등) |
| borderFill 1 | 테두리 | 없음 (페이지 보더) |
| borderFill 2 | 테두리 | 없음 + 투명배경 (참조용) |

### gonmun (공문) — base + 추가

| ID | 유형 | 설명 |
|----|------|------|
| charPr 7 | 글자 | 22pt 볼드 함초롬바탕 (기관명/제목) |
| charPr 8 | 글자 | 16pt 볼드 함초롬바탕 (서명자) |
| charPr 9 | 글자 | 8pt 함초롬바탕 (하단 연락처) |
| charPr 10 | 글자 | 10pt 볼드 함초롬바탕 (표 헤더) |
| paraPr 20 | 문단 | CENTER, 160% 줄간격 |
| paraPr 21 | 문단 | CENTER, 130% (표 셀) |
| paraPr 22 | 문단 | JUSTIFY, 130% (표 셀) |
| borderFill 3 | 테두리 | SOLID 0.12mm 4면 |
| borderFill 4 | 테두리 | SOLID 0.12mm + #D6DCE4 배경 |

### report (보고서) — base + 추가

| ID | 유형 | 설명 |
|----|------|------|
| charPr 7 | 글자 | 20pt 볼드 (문서 제목) |
| charPr 8 | 글자 | 14pt 볼드 (소제목) |
| charPr 9 | 글자 | 10pt 볼드 (표 헤더) |
| charPr 10 | 글자 | 10pt 볼드+밑줄 (강조 텍스트) |
| charPr 11 | 글자 | 9pt 함초롬바탕 (소형/각주) |
| charPr 12 | 글자 | 16pt 볼드 함초롬바탕 (1줄 제목) |
| charPr 13 | 글자 | 12pt 볼드 함초롬돋움 (섹션 헤더) |
| paraPr 20~22 | 문단 | CENTER/JUSTIFY 변형 |
| paraPr 23 | 문단 | RIGHT 정렬, 160% 줄간격 |
| paraPr 24 | 문단 | JUSTIFY, left 600 (□ 체크항목 들여쓰기) |
| paraPr 25 | 문단 | JUSTIFY, left 1200 (하위항목 ①②③ 들여쓰기) |
| paraPr 26 | 문단 | JUSTIFY, left 1800 (깊은 하위항목 - 들여쓰기) |
| paraPr 27 | 문단 | LEFT, 상하단 테두리선 (섹션 헤더용), prev 400 |
| borderFill 3 | 테두리 | SOLID 0.12mm 4면 |
| borderFill 4 | 테두리 | SOLID 0.12mm + #DAEEF3 배경 |
| borderFill 5 | 테두리 | 상단 0.4mm 굵은선 + 하단 0.12mm 얇은선 (섹션 헤더) |

**들여쓰기 규칙**: 공백 문자가 아닌 반드시 paraPr의 left margin 사용. □ 항목은 paraPr 24, 하위 ①②③ 는 paraPr 25, 깊은 - 항목은 paraPr 26.

**섹션 헤더 규칙**: paraPr 27 + charPr 13 조합. 문단 테두리(borderFillIDRef="5")로 상단 굵은선 + 하단 얇은선 자동 표시.

### minutes (회의록) — base + 추가

| ID | 유형 | 설명 |
|----|------|------|
| charPr 7 | 글자 | 18pt 볼드 (제목) |
| charPr 8 | 글자 | 12pt 볼드 (섹션 라벨) |
| charPr 9 | 글자 | 10pt 볼드 (표 헤더) |
| paraPr 20~22 | 문단 | CENTER/JUSTIFY 변형 |
| borderFill 3 | 테두리 | SOLID 0.12mm 4면 |
| borderFill 4 | 테두리 | SOLID 0.12mm + #E2EFDA 배경 |

### proposal (제안서/사업개요) — base + 추가

시각적 구분이 필요한 공식 문서용. 색상 배경 헤더바와 번호 배지를 표(table) 기반 레이아웃으로 구현.

| ID | 유형 | 설명 |
|----|------|------|
| charPr 7 | 글자 | 20pt 볼드 함초롬바탕 (문서 제목) |
| charPr 8 | 글자 | 14pt 볼드 함초롬바탕 (소제목) |
| charPr 9 | 글자 | 10pt 볼드 함초롬바탕 (표 헤더) |
| charPr 10 | 글자 | 14pt 볼드 흰색 함초롬돋움 (대항목 번호, 녹색 배경) |
| charPr 11 | 글자 | 11pt 볼드 흰색 함초롬돋움 (소항목 번호, 파란 배경) |
| paraPr 20 | 문단 | CENTER, 160% 줄간격 |
| paraPr 21 | 문단 | CENTER, 130% (표 셀) |
| paraPr 22 | 문단 | JUSTIFY, 130% (표 셀) |
| borderFill 3 | 테두리 | SOLID 0.12mm 4면 |
| borderFill 4 | 테두리 | SOLID 0.12mm + #DAEEF3 배경 |
| borderFill 5 | 테두리 | 올리브녹색 배경 #7B8B3D (대항목 번호 셀) |
| borderFill 6 | 테두리 | 연한 회색 배경 #F2F2F2 + 회색 테두리 (대항목 제목 셀) |
| borderFill 7 | 테두리 | 파란색 배경 #4472C4 (소항목 번호 배지) |
| borderFill 8 | 테두리 | 하단 테두리만 #D0D0D0 (소항목 제목 영역) |

#### proposal 레이아웃 패턴

**대항목 헤더** (2셀 표: 번호 + 제목):
```xml
<!-- borderFillIDRef="5" + charPrIDRef="10" → 녹색배경 흰색 로마숫자 -->
<!-- borderFillIDRef="6" + charPrIDRef="8"  → 회색배경 검정 볼드 제목 -->
```

**소항목 헤더** (2셀 표: 번호배지 + 제목):
```xml
<!-- borderFillIDRef="7" + charPrIDRef="11" → 파란배경 흰색 아라비아숫자 -->
<!-- borderFillIDRef="8" + charPrIDRef="8"  → 하단선만 검정 볼드 제목 -->
```

### 인라인 서식 변환용 (예약 ID, 전 템플릿 공통)

| Group | IDs | Meaning |
|---|---|---|
| charPr | 30 | 인라인 볼드 (10pt, `<hh:bold/>`) |
| charPr | 31 | 인라인 이탤릭 (10pt, `<hh:italic/>`) |
| charPr | 32 | 인라인 볼드+이탤릭 (10pt, `<hh:bold/>` + `<hh:italic/>`) |
| charPr | 33 | 인라인 밑줄 (10pt, `<hh:underline type="BOTTOM"/>`) |
| charPr | 34 | 인라인 취소선 (10pt, `<hh:strikeout shape="SOLID"/>`) |

## Markdown-to-HWPX 인라인 서식 변환

입력 콘텐츠가 Markdown 형식(`.md` 파일 또는 Markdown 구문 포함 텍스트)인 경우,
Markdown 서식 기호(`**`, `*`, `~~` 등)를 HWPX XML의 multi-run 구조로 변환해야 한다.

### 변환 매핑

| Markdown | charPrIDRef | 설명 |
|---|---:|---|
| `**텍스트**` | 30 | 볼드 |
| `*텍스트*` | 31 | 이탤릭 |
| `***텍스트***` | 32 | 볼드+이탤릭 |
| `<u>텍스트</u>` | 33 | 밑줄 |
| `~~텍스트~~` | 34 | 취소선 |
| (없음) | 0 | 일반 본문 |

### 변환 원칙

1. Markdown 기호(`**`, `*`, `~~`, `#`, `` ` ``, `- `, `> `)는 `<hp:t>` 텍스트에 포함시키지 않는다.
2. 서식이 바뀌는 지점마다 별도의 `<hp:run>`을 생성한다 (multi-run 분할).
3. 예약 charPr ID 30-34는 모든 템플릿(base, gonmun, report, minutes, proposal)에 공통 정의되어 있다.
4. 블록 레벨 Markdown(`#`, `-`, `>` 등)은 해당 기호를 제거하고 적절한 `paraPrIDRef`로 변환한다.

### XML 예시: 혼합 서식 문단

입력: `연구 결과 **유의미한** 차이가 *관찰*되었다.`

```xml
<hp:p id="..." paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:t>연구 결과 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="30">
    <hp:t>유의미한</hp:t>
  </hp:run>
  <hp:run charPrIDRef="0">
    <hp:t> 차이가 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="31">
    <hp:t>관찰</hp:t>
  </hp:run>
  <hp:run charPrIDRef="0">
    <hp:t>되었다.</hp:t>
  </hp:run>
</hp:p>
```

## Markdown 섹션 삽입 시 템플릿 구조 인식 규칙

기존 HWPX의 특정 섹션에 Markdown 파일의 내용을 삽입할 때,
마크다운 heading과 템플릿 sub-header의 중복을 방지해야 한다.

### 판별 절차

1. 대상 섹션의 기존 문단 중, **sub-header 패턴**에 해당하는 문단을 식별
   - 조건: charPrIDRef가 헤더급 스타일 AND 텍스트 길이 50자 이하
   - 예: "3-1 비전", "4-2. 세부기술2", "목표 설정 근거"

2. 입력 마크다운의 `##`, `###` 레벨 heading을 추출

3. 양측 텍스트를 정규화하여 비교
   - 정규화: strip(), 선행 번호 패턴 통일 ("3-1" = "3.1" = "3 1")
   - 매칭: 정규화 결과가 동일하거나, 한쪽이 다른 쪽을 포함

### 삽입 규칙

| 상황 | heading 처리 | body 처리 | placeholder 처리 |
|------|-------------|-----------|-----------------|
| 매칭됨 | skip | 템플릿 sub-header 뒤에 삽입 | sub-header~다음 sub-header 사이의 빈 문단 삭제 |
| 미매칭 | 변환하여 삽입 | heading 뒤에 삽입 | 해당 없음 |

### 빈 placeholder 문단 판별 기준

삭제 대상:
- `<hp:t/>` (self-closing, 텍스트 없음)
- `<hp:t>` 내용이 공백만 포함
- `<hp:t>` 내용이 단독 기호: ◦, ○, •, -, ※, ·, □, ■

보존 대상:
- 실제 텍스트 내용이 있는 문단 (2글자 이상의 의미 있는 텍스트)
- 표(hp:tbl)를 포함한 문단 (★ 작성요령 표는 별도 규칙으로 삭제)

---

## Workflow 1. XML-first 문서 생성 (보조 워크플로우, 레퍼런스 파일이 없을 때만)

> 원칙: 사용자가 레퍼런스 HWPX를 제공한 경우에는 이 워크플로우 대신 상단의 "기본 동작 모드(레퍼런스 복원 우선)"를 사용한다.

### 흐름

1. **템플릿 선택** (base/gonmun/report/minutes/proposal)
2. **section0.xml 작성** (본문 내용)
3. **(선택) header.xml 수정** (새 스타일 추가 필요 시)
4. **build_hwpx.py로 빌드**
5. **validate.py로 검증**

### 기본 사용법

```bash
# 빈 문서 (base 템플릿)
python3 "$SKILL_DIR/scripts/build_hwpx.py" --output result.hwpx

# 템플릿 사용
python3 "$SKILL_DIR/scripts/build_hwpx.py" --template gonmun --output result.hwpx

# 커스텀 section0.xml 오버라이드
python3 "$SKILL_DIR/scripts/build_hwpx.py" --template gonmun --section my_section0.xml --output result.hwpx

# header도 오버라이드
python3 "$SKILL_DIR/scripts/build_hwpx.py" --header my_header.xml --section my_section0.xml --output result.hwpx

# 메타데이터 설정
python3 "$SKILL_DIR/scripts/build_hwpx.py" --template report --section my.xml \
  --title "제목" --creator "작성자" --output result.hwpx
```

### 실전 패턴: section0.xml을 인라인 작성 → 빌드

```bash
# 1. section0.xml을 임시파일로 작성
SECTION=$(mktemp /tmp/section0_XXXX.xml)
cat > "$SECTION" << 'XMLEOF'
<?xml version='1.0' encoding='UTF-8'?>
<hs:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
        xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section">
  <!-- secPr 포함 첫 문단 (base/section0.xml에서 복사) -->
  <!-- ... -->
  <hp:p id="1000000002" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:t>본문 내용</hp:t>
    </hp:run>
  </hp:p>
</hs:sec>
XMLEOF

# 2. 빌드
python3 "$SKILL_DIR/scripts/build_hwpx.py" --section "$SECTION" --output result.hwpx

# 3. 정리
rm -f "$SECTION"
```

---

## section0.xml 작성 가이드

### 필수 구조

section0.xml의 첫 문단(`<hp:p>`)의 첫 런(`<hp:run>`)에 반드시 `<hp:secPr>`과 `<hp:colPr>` 포함:

```xml
<hp:p id="1000000001" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:secPr ...>
      <!-- 페이지 크기, 여백, 각주/미주 설정 등 -->
    </hp:secPr>
    <hp:ctrl>
      <hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/>
    </hp:ctrl>
  </hp:run>
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>
```

**Tip**: `templates/base/Contents/section0.xml` 의 첫 문단을 그대로 복사하면 된다.

### 문단

```xml
<hp:p id="고유ID" paraPrIDRef="문단스타일ID" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="글자스타일ID">
    <hp:t>텍스트 내용</hp:t>
  </hp:run>
</hp:p>
```

### 빈 줄

```xml
<hp:p id="고유ID" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>
```

### 서식 혼합 런 (한 문단에 여러 스타일)

```xml
<hp:p id="고유ID" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:t>일반 텍스트 </hp:t></hp:run>
  <hp:run charPrIDRef="7"><hp:t>볼드 텍스트</hp:t></hp:run>
  <hp:run charPrIDRef="0"><hp:t> 다시 일반</hp:t></hp:run>
</hp:p>
```

### 불릿/항목 문단 (hanging indent)

hanging indent = paraPr의 `left` margin + 음수 `indent` (첫 줄이 왼쪽으로 돌출).
불릿 마커 (◦, –, □)는 첫 번째 `<hp:run>`에, 본문 텍스트는 후속 `<hp:run>`에 배치.

**올바른 예시:**

```xml
<hp:p paraPrIDRef="24"> <!-- left="600" indent="-300" → hanging indent -->
  <hp:run charPrIDRef="0"><hp:t>□ </hp:t></hp:run>
  <hp:run charPrIDRef="0"><hp:t>항목 텍스트 내용</hp:t></hp:run>
</hp:p>
```

**금지 패턴:** 공백 문자로 들여쓰기하지 않는다. 반드시 paraPr의 `left`/`indent` 속성 사용.

**불릿 계층 렌더링**: idRef(문자) + hc:left(여백) + level(자동) + leftMargin override 조합
- paraPr 87: ◦ 상위 불릿 (left=1500)
- paraPr 88: - 하위 불릿 (left=2500)

### 표 작성법 (참조 형식 — 프로그래밍 생성 시 xml_writer.py 사용 필수)

> **중요**: 아래 XML 예시는 HWPX 표 구조를 이해하기 위한 **참조 형식**이다.
> 프로그래밍으로 표를 생성할 때는 반드시 `xml_writer.py`의 `build_table()` / `table_cell_xml()` 함수를 사용한다.
> 에이전트가 직접 `<hp:tbl>` XML을 작성하면 네임스페이스(`hc:` 오용), 속성 순서, 필수 요소 누락 등의 오류가 발생한다.
>
> ```bash
> python3 xml_writer.py --input parsed.json --style-config styles.json --output fragment.xml
> ```

```xml
<hp:p id="고유ID" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:tbl id="고유ID" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM"
            textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL"
            repeatHeader="0" rowCnt="행수" colCnt="열수" cellSpacing="0"
            borderFillIDRef="3" noAdjust="0">
      <hp:sz width="42520" widthRelTo="ABSOLUTE" height="전체높이" heightRelTo="ABSOLUTE" protect="0"/>
      <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0"
              holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP"
              horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
      <hp:outMargin left="0" right="0" top="0" bottom="0"/>
      <hp:inMargin left="0" right="0" top="0" bottom="0"/>
      <hp:tr>
        <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="1" borderFillIDRef="4">
          <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER"
                     linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0"
                     hasTextRef="0" hasNumRef="0">
            <hp:p paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0" id="고유ID">
              <hp:run charPrIDRef="9"><hp:t>헤더 셀</hp:t></hp:run>
            </hp:p>
          </hp:subList>
          <hp:cellAddr colAddr="0" rowAddr="0"/>
          <hp:cellSpan colSpan="1" rowSpan="1"/>
          <hp:cellSz width="열너비" height="행높이"/>
          <hp:cellMargin left="0" right="0" top="0" bottom="0"/>
        </hp:tc>
        <!-- 나머지 셀... -->
      </hp:tr>
    </hp:tbl>
  </hp:run>
</hp:p>
```

### 표 크기 계산

- **A4 본문폭**: 42520 HWPUNIT = 59528(용지) - 8504×2(좌우여백)
- **열 너비 합 = 본문폭** (42520)
- 예: 3열 균등 → 14173 + 14173 + 14174 = 42520
- 예: 2열 (라벨:내용 = 1:4) → 8504 + 34016 = 42520
- **행 높이**: 셀당 보통 2400~3600 HWPUNIT

### 표 변환 원칙 (MD→HWPX)

- **MD 원본 데이터 그대로**: 마크다운 표의 셀 내용을 변환 없이 옮긴다
- **금지**: 셀에 ■, ▶, □ 등 장식 마커를 임의 추가하지 않는다
- **열 너비 공식**: `table_width / col_count` 균등 분배 (레퍼런스가 있으면 레퍼런스 따름)
- **예**: 3열 균등 → `42520 / 3` ≈ 14173 + 14173 + 14174
- **xml_writer.py 필수**: 프로그래밍으로 표를 생성할 때는 반드시 `xml_writer.py`의 `build_table()` 함수를 호출한다. 에이전트가 직접 `<hp:tbl>` XML을 작성하지 않는다.

### ID 규칙

- 문단 id: `1000000001`부터 순차 증가
- 표 id: `1000000099` 등 별도 범위 사용 권장
- 모든 id는 문서 내 고유해야 함

---

## header.xml 수정 가이드

### 커스텀 스타일 추가 방법

1. `templates/base/Contents/header.xml` 복사
2. 필요한 charPr/paraPr/borderFill 추가
3. 각 그룹의 `itemCnt` 속성 업데이트

### charPr 추가 예시 (볼드 14pt)

```xml
<hh:charPr id="8" height="1400" textColor="#000000" shadeColor="none"
           useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">
  <hh:fontRef hangul="1" latin="1" hanja="1" japanese="1" other="1" symbol="1" user="1"/>
  <hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
  <hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
  <hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
  <hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
  <hh:bold/>
  <hh:underline type="NONE" shape="SOLID" color="#000000"/>
  <hh:strikeout shape="NONE" color="#000000"/>
  <hh:outline type="NONE"/>
  <hh:shadow type="NONE" color="#C0C0C0" offsetX="10" offsetY="10"/>
</hh:charPr>
```

### 폰트 참조 체계

- `fontRef` 값은 `fontfaces`에 정의된 font id
- `hangul="0"` → 함초롬돋움 (고딕)
- `hangul="1"` → 함초롬바탕 (명조)
- 7개 언어 모두 동일하게 설정

### paraPr 추가 시 주의

- 반드시 `hp:switch` 구조 포함 (`hp:case` + `hp:default`)
- `hp:case`와 `hp:default`의 값은 보통 동일 (또는 default가 2배)
- `borderFillIDRef="2"` 유지

---

## Workflow 2. 기존 문서 편집 (unpack → Edit → pack)

```bash
# 1. HWPX → 디렉토리 (XML pretty-print)
python3 "$SKILL_DIR/scripts/office/unpack.py" document.hwpx ./unpacked/

# 2. XML 직접 편집 (Claude가 Read/Edit 도구로)
#    본문: ./unpacked/Contents/section0.xml
#    스타일: ./unpacked/Contents/header.xml

# 3. 다시 HWPX로 패키징
python3 "$SKILL_DIR/scripts/office/pack.py" ./unpacked/ edited.hwpx

# 4. 검증
python3 "$SKILL_DIR/scripts/validate.py" edited.hwpx
```

---

## Workflow 3. 읽기/텍스트 추출

```bash
# 순수 텍스트
python3 "$SKILL_DIR/scripts/text_extract.py" document.hwpx

# 테이블 포함
python3 "$SKILL_DIR/scripts/text_extract.py" document.hwpx --include-tables

# 마크다운 형식
python3 "$SKILL_DIR/scripts/text_extract.py" document.hwpx --format markdown
```

---

## Workflow 4. 검증

```bash
python3 "$SKILL_DIR/scripts/validate.py" document.hwpx
```

검증 항목: ZIP 유효성, 필수 파일 존재, mimetype 내용/위치/압축방식, XML well-formedness

---

## Workflow 5. 레퍼런스 기반 문서 생성 (첨부 HWPX가 있을 때 기본 적용)

사용자가 제공한 HWPX 파일을 분석하여 동일한 레이아웃의 문서를 생성하는 워크플로우.
이 스킬에서는 첨부 레퍼런스가 존재하면 본 워크플로우를 기본으로 사용한다.

### 흐름

1. **분석** — `analyze_template.py`로 레퍼런스 문서 심층 분석
2. **header.xml 추출** — 레퍼런스의 스타일 정의를 그대로 사용
3. **section0.xml 작성** — 분석 결과의 구조를 따라 새 내용으로 작성
4. **빌드** — 추출한 header.xml + 새 section0.xml로 빌드
5. **검증** — `validate.py`
6. **쪽수 가드** — `page_guard.py` (실패 시 재수정)

### 사용법

```bash
# 1. 심층 분석 (구조 청사진 출력)
python3 "$SKILL_DIR/scripts/analyze_template.py" reference.hwpx

# 2. header.xml과 section0.xml을 추출하여 참고용으로 보관
python3 "$SKILL_DIR/scripts/analyze_template.py" reference.hwpx \
  --extract-header /tmp/ref_header.xml \
  --extract-section /tmp/ref_section.xml

# 3. 분석 결과를 보고 새 section0.xml 작성
#    - 동일한 charPrIDRef, paraPrIDRef 사용
#    - 동일한 테이블 구조 (열 수, 열 너비, 행 수, rowSpan/colSpan)
#    - 동일한 borderFillIDRef, cellMargin

# 4. 추출한 header.xml + 새 section0.xml로 빌드
python3 "$SKILL_DIR/scripts/build_hwpx.py" \
  --header /tmp/ref_header.xml \
  --section /tmp/new_section0.xml \
  --output result.hwpx

# 5. 검증
python3 "$SKILL_DIR/scripts/validate.py" result.hwpx

# 6. 쪽수 드리프트 가드 (필수)
python3 "$SKILL_DIR/scripts/page_guard.py" \
  --reference reference.hwpx \
  --output result.hwpx
```

### 분석 출력 항목

| 항목 | 설명 |
|------|------|
| 폰트 정의 | hangul/latin 폰트 매핑 |
| borderFill | 테두리 타입/두께 + 배경색 (각 면별 상세) |
| charPr | 글꼴 크기(pt), 폰트명, 색상, 볼드/이탤릭/밑줄/취소선, fontRef |
| paraPr | 정렬, 줄간격, 여백(left/right/prev/next/intent), heading, borderFillIDRef |
| 문서 구조 | 페이지 크기, 여백, 페이지 테두리, 본문폭 |
| 본문 상세 | 모든 문단의 id/paraPr/charPr + 텍스트 내용 |
| 표 상세 | 행×열, 열너비 배열, 셀별 span/margin/borderFill/vertAlign + 내용 |

### 핵심 원칙

- **charPrIDRef/paraPrIDRef를 그대로 사용**: 추출한 header.xml의 스타일 ID를 변경하지 말 것
- **열 너비 합계 = 본문폭**: 분석 결과의 열너비 배열을 그대로 복제
- **rowSpan/colSpan 패턴 유지**: 분석된 셀 병합 구조를 정확히 재현
- **cellMargin 보존**: 분석된 셀 여백 값을 동일하게 적용
- **페이지 증가 금지**: 사용자 명시 승인 없이 결과 쪽수를 늘리지 말 것
- **치환 우선 편집**: 새 문단/표 추가보다 기존 텍스트 노드 치환을 우선할 것

---

## Workflow 6. ZIP-Level Surgery (기존 HWPX 안전 편집)

> **핵심**: 기존 HWPX 파일의 바이트 레벨 무결성을 보존하면서 내용을 수정하는 유일하게 안전한 방법.
> 상세 규칙: `$SKILL_DIR/references/zip-surgery-guide.md` 참조.

### 언제 사용하는가

- 기존 HWPX 파일의 텍스트를 교체할 때
- 기존 HWPX 파일에 문단/표를 추가/삭제할 때
- `standalone='no'`, 네임스페이스, 개행 형식을 보존해야 할 때

### 사용법

```python
from zip_surgery import HwpxSurgeon

surgeon = HwpxSurgeon('document.hwpx')

# 방법 1: 텍스트 치환 (구조 유지)
surgeon.replace_text({"기존 텍스트": "새 텍스트"})

# 방법 2: 자식 요소 편집 (구조 변경)
children = surgeon.extract_children()
children.append(surgeon.make_paragraph('9999', '새 문단'))
surgeon.replace_children(children)

surgeon.save('output.hwpx')

# 검증 (필수)
errors = surgeon.validate('output.hwpx')
assert not errors, errors
```

### CLI

```bash
# 추출
python3 "$SKILL_DIR/scripts/zip_surgery.py" extract document.hwpx -o section0.xml

# 교체
python3 "$SKILL_DIR/scripts/zip_surgery.py" replace document.hwpx -s new_section0.xml -o result.hwpx

# 검증
python3 "$SKILL_DIR/scripts/zip_surgery.py" validate document.hwpx result.hwpx
```

### 절대 금지 (ZIP-level surgery 후)

- `cell_writer.py` 실행 금지 → standalone/namespace/newline 파괴
- `ET.tostring()` / `tree.write()` 사용 금지 → XML 선언/네임스페이스 변경
- pretty-print / indent 금지 → 개행이 텍스트 노드로 해석됨

---

## Workflow 7. 마크다운→HWPX 템플릿 채우기

사용자가 마크다운 문서와 HWPX 템플릿을 제공했을 때, 템플릿 스타일을 유지하면서 내용을 채워 넣는 워크플로우.

### 흐름

1. **스타일 추출** — `analyze_template.py <template.hwpx> --style-map styles.json`
1.5. **(다중 MD 통합)** — 여러 MD 파일이 있는 경우 `md_merger.py` 실행
   - CLI: `python3 md_merger.py file1.md file2.md --target-level 2 --output merged.json`
   - 단일 MD 파일이면 이 단계 생략
2. **마크다운 파싱** — `md_parser.py input.md --output parsed.json`
   - md_parser.py가 numbered list를 `numbered_item` 타입으로 파싱하여 번호 마커를 보존함
   - **indent_level**: 들여쓰기 레벨 (2-space 기준, 0=최상위). bullet/numbered_item 블록에 자동 추가됨.
   - **bullet_level_N**: style_config의 레벨별 스타일 키 (analyze_template.py --style-map에서 자동 추출)
3. **매핑 결정** — 에이전트가 MD 섹션 ↔ 템플릿 영역 매핑 결정
4. **XML 생성** — `xml_writer.py --input parsed.json --style-config styles.json --output fragment.xml`
5. **삽입** — `zip_surgery.py replace template.hwpx -s fragment.xml -o result.hwpx`
6. **이미지 임베딩** — `image_embedder.py --hwpx result.hwpx --images-dir <dir> --mapping map.json --output final.hwpx`
7. **검증** — `validate.py final.hwpx` + `page_guard.py --reference template.hwpx --output final.hwpx`

### CLI 예시

```bash
# 1) 스타일 추출
python3 "$SKILL_DIR/scripts/analyze_template.py" template.hwpx --style-map /tmp/styles.json

# 2) 마크다운 파싱
python3 "$SKILL_DIR/scripts/md_parser.py" input.md --output /tmp/parsed.json

# 3) XML 프래그먼트 생성
python3 "$SKILL_DIR/scripts/xml_writer.py" \
  --input /tmp/parsed.json --style-config /tmp/styles.json --output /tmp/fragment.xml

# 4) 템플릿에 삽입
python3 "$SKILL_DIR/scripts/zip_surgery.py" replace template.hwpx \
  -s /tmp/fragment.xml -o /tmp/result.hwpx

# 5) 이미지 임베딩 (이미지가 있을 경우)
python3 "$SKILL_DIR/scripts/image_embedder.py" \
  --hwpx /tmp/result.hwpx --images-dir ./images/ --mapping map.json --output final.hwpx

# 6) 검증
python3 "$SKILL_DIR/scripts/validate.py" final.hwpx
python3 "$SKILL_DIR/scripts/page_guard.py" --reference template.hwpx --output final.hwpx
```

### 템플릿 스타일 ID 원칙

- **반드시 `analyze_template.py --style-map` 출력의 ID를 사용**한다. 템플릿마다 charPr/paraPr/borderFill ID 체계가 다르므로 하드코딩 금지.
- **빌트인 예약 ID (30-34)는 XML-first 전용**이다. 템플릿 채우기에 사용 금지 — 템플릿 header.xml에 해당 ID가 정의되어 있지 않을 수 있다.
- **XML 이스케이프 필수**: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`
- **문단 ID**: `9000000001`부터 순차 증가 (기존 템플릿 ID와 충돌 방지)

### 이미지 임베딩 가이드

HWPX 이미지 구조는 2곳에 등록한다:
1. `BinData/` 폴더에 실제 이미지 파일 (image1.png, image2.png, ...)
2. `Contents/content.hpf`에 `<opf:item>` 등록
3. `Contents/section0.xml`에 `<hp:pic>` 요소 삽입

**header.xml binDataList 추가 금지**: 기존 binDataList가 있으면 제거한다.

**CLI:**

```bash
python3 "$SKILL_DIR/scripts/image_embedder.py" \
  --hwpx input.hwpx \
  --images-dir ./images/ \
  --mapping map.json \
  --output output.hwpx
```

`--mapping` JSON 형식: `{"placeholder_id": "image_filename.png", ...}`
`--auto-map` 옵션으로 플레이스홀더-이미지 자동 매칭 가능.
`--max-width` INT: 최대 이미지 너비(px). 초과 시 비율 유지 리사이즈. (기본: 압축 없음)
`--quality` INT: JPEG 품질 (0-100). (기본: 85)

### 이미지 임베딩 필수 규칙 (CRITICAL)

| 규칙 | 설명 |
|------|------|
| **2곳 등록** | `BinData/` + `content.hpf`에만 등록. header.xml binDataList 추가 금지. 기존 binDataList가 있으면 제거 |
| **binaryItemIDRef 형식** | header.xml binDataList 미사용. section0.xml의 hc:img에서 `binaryItemIDRef="imageN"` 형식 사용 (image1, image2, ...) |
| **소스 이미지 포맷 검증** | `.png` 확장자 파일의 실제 포맷이 JPEG일 수 있음. `image_embedder.py`가 자동 감지/변환 |
| **orgSz = pixel×36** | `orgSz` = 원본 이미지 픽셀 × 36 HWP units (200DPI 기준). 예: 원본 1000×800px → orgSz=36000×28800 |
| **이미지 높이 상한** | MAX_IMAGE_HEIGHT = 70000 HWP units (~247mm). 초과 시 에러 |
| **BIN ID 형식** | imageN 형식 (image1, image2, ...). BIN0001 형식은 사용하지 않음 |
| **hp:pic 반드시 <hp:run> 안에 위치** | `hp:pic`은 section-level sibling으로 배치하면 한/글이 렌더링하지 않음. 반드시 `<hp:p><hp:run>...</hp:run></hp:p>` 구조 내에 위치해야 함 |

### `<hp:pic>` 검증된 구조 (pypandoc-hwpx, python-hwpx, HwpForge 참조)

요소 순서가 중요하며, 한/글의 직렬화 순서와 일치해야 한다:

```
offset → orgSz → curSz → flip → rotationInfo → renderingInfo → hc:img →
imgRect → imgClip → inMargin → imgDim → effects → sz → pos → outMargin → shapeComment
```xml
<hp:p>
  <hp:run>
    <hp:pic id="PIC_ID" instid="INST_ID" reverse="0"
            numberingType="PICTURE" textWrap="TOP_AND_BOTTOM"
            textFlow="BOTH_SIDES" lock="0" dropcapstyle="None"
            href="" groupLevel="0">
      <hp:offset x="0" y="0"/>
      <hp:orgSz width="36000" height="28800"/>
      <hp:curSz width="42520" height="34016"/>
      <hp:flip horizontal="0" vertical="0"/>
      <hp:rotationInfo angle="0" centerX="21260" centerY="17008" rotateimage="1"/>
      <hp:renderingInfo>
        <hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>
        <hc:scaMatrix e1="1.18111" e2="0" e3="0" e4="0" e5="1.18111" e6="0"/>
        <hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>
      </hp:renderingInfo>
      <hc:img binaryItemIDRef="image1" bright="0" contrast="0"
              effect="REAL_PIC" alpha="0"/>
      <hp:imgRect>
        <hc:pt0 x="0" y="0"/><hc:pt1 x="36000" y="0"/>
        <hc:pt2 x="36000" y="28800"/><hc:pt3 x="0" y="28800"/>
      </hp:imgRect>
      <hp:imgClip left="0" right="75000" top="0" bottom="60000"/>
      <hp:inMargin left="0" right="0" top="0" bottom="0"/>
      <hp:imgDim dimwidth="75000" dimheight="60000"/>
      <hp:effects/>
      <hp:sz width="42520" widthRelTo="ABSOLUTE" height="34016"
             heightRelTo="ABSOLUTE" protect="0"/>
      <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1"
              allowOverlap="0" holdAnchorAndSO="0"
              vertRelTo="PARA" horzRelTo="COLUMN"
              vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
      <hp:outMargin left="0" right="0" top="0" bottom="0"/>
      <hp:shapeComment>image1.png 1000x800</hp:shapeComment>
    </hp:pic>
  </hp:run>
</hp:p>
```

### header.xml binDataList (사용하지 않음)

**규칙**: header.xml에 binDataList를 추가하지 않는다. 기존 binDataList가 있으면 제거한다.

이미지 등록은 `BinData/` 폴더 + `content.hpf`만으로 충분하다.

---

## 표 행 높이 자동 조절 규칙 (CRITICAL)

프로그래밍으로 생성한 표는 반드시 다음 속성을 설정해야 한다:

```xml
<hp:tbl ... noAdjust="0" pageBreak="CELL">
```

| 속성 | 필수 값 | 효과 |
|------|---------|------|
| `noAdjust="0"` | **필수** | 셀 내용에 맞춰 행 높이 자동 확장 |
| `noAdjust="1"` | **금지** | 고정 높이 — 내용 잘림 |
| `pageBreak="CELL"` | **권장** | 셀 단위 페이지 넘김 허용 |
| `pageBreak="NONE"` | **금지** | 큰 표가 한 페이지에 강제 압축 |

---

## 단계적 디버깅 전략

HWPX 파일이 한글에서 열리지 않을 때:

1. **최소 변경 테스트**: 삭제만 하고 삽입 없이 열리는지 확인
2. **단일 요소 테스트**: 간단한 `<hp:p>` 1개만 추가해서 열리는지 확인
3. **테이블 테스트**: 간단한 `<hp:tbl>` 1개 추가해서 열리는지 확인
4. **전체 삽입 테스트**: 모든 내용 삽입
5. **cell_writer 테스트**: cell_writer 실행 전후 비교

각 단계에서 실패하면, 해당 단계의 변경 내용이 원인이다.

---

## Critical Rules

1. **HWPX만 지원**: `.hwp`(바이너리) 파일은 지원하지 않는다. 사용자가 `.hwp` 파일을 제공하면 **한글 오피스에서 `.hwpx`로 다시 저장**하도록 안내할 것. (파일 → 다른 이름으로 저장 → 파일 형식: HWPX)
2. **secPr 필수**: section0.xml 첫 문단의 첫 run에 반드시 secPr + colPr 포함
3. **mimetype 순서**: HWPX 패키징 시 mimetype은 첫 번째 ZIP 엔트리, ZIP_STORED
4. **네임스페이스 보존**: XML 편집 시 `hp:`, `hs:`, `hh:`, `hc:` 접두사 유지
5. **itemCnt 정합성**: header.xml의 charProperties/paraProperties/borderFills itemCnt가 실제 자식 수와 일치
6. **ID 참조 정합성**: section0.xml의 charPrIDRef/paraPrIDRef가 header.xml 정의와 일치
7. **검증**: 생성 후 반드시 `validate.py`로 무결성 확인
8. **레퍼런스**: 상세 XML 구조는 `$SKILL_DIR/references/hwpx-format.md` 참조
9. **build_hwpx.py 우선**: 새 문서 생성은 build_hwpx.py 사용 (python-hwpx API 직접 호출 지양)
10. **빈 줄**: `<hp:t/>` 사용 (self-closing tag)
11. **대량 내용 확장 시**: 본 파일은 절차 중심으로 유지하고, 세부 도표/스키마는 `references/`에 분리
12. **레퍼런스 우선 강제**: 사용자가 HWPX를 첨부하면 반드시 `analyze_template.py` + 추출 XML 기반으로 복원/재작성할 것
13. **examples 폴더 미사용**: 작업 중 `examples/*` 파일은 읽기/참조/복사에 사용하지 말 것
14. **쪽수 동일 필수**: 레퍼런스 기반 작업에서는 최종 결과의 쪽수를 레퍼런스와 동일하게 유지할 것
15. **무단 페이지 증가 금지**: 사용자 명시 요청/승인 없이 쪽수 증가를 유발하는 구조 변경 금지
16. **구조 변경 제한**: 사용자 요청이 없는 한 문단/표의 추가·삭제·분할·병합 금지 (치환 중심 편집)
17. **page_guard 필수 통과**: `validate.py`와 별개로 `page_guard.py`를 반드시 통과해야 완료 처리
18. **linesegarray 자동 생성**: `<hp:linesegarray>`는 라인 레이아웃 캐시로, 텍스트 수정 후 실제 내용과 불일치하면 '문서 변조' 경고 및 비-한글 뷰어에서 표시 오류를 유발한다. `build_hwpx.py`와 `pack.py`는 패키징 시 `cell_writer.py`를 호출하여 올바른 linesegarray를 자동 생성한다. 생성 실패 시 기존 방식(자동 제거)으로 폴백한다. section0.xml 작성 시 linesegarray를 포함할 필요 없다 — 빌드 파이프라인이 자동 생성한다. **단, ZIP-level surgery 편집 후에는 cell_writer를 절대 실행하지 않는다** (한글이 자동 재계산).
19. **ZIP-level surgery 규칙**: 기존 HWPX 편집 시 `zip_surgery.py`를 사용하고, 상세 규칙은 `$SKILL_DIR/references/zip-surgery-guide.md` 준수. ET.tostring()/tree.write() 사용 금지, 개행 삽입 금지, standalone='no' 보존 필수.
20. **표 속성 필수**: `noAdjust="0"` (행 높이 자동 조절) + `pageBreak="CELL"` (페이지 넘김 허용)
21. **validate.py --strict**: ZIP-level surgery 결과물은 `validate.py --strict`로 추가 검증 (standalone, xmlns, newlines, 표 속성)
22. **lxml/ElementTree로 section XML 직렬화 절대 금지**: lxml의 `etree.tostring()`과 `tree.write()`는 XML 선언(`<?xml ... ?>`) 뒤에 `\n`(개행)을 삽입한다. 한/글은 이 개행을 텍스트 노드로 해석하여 파일을 깨뜨린다. 원본: `...yes"?><hs:sec`(개행 0개) → lxml: `...yes"?>\n<hs:sec`(개행 1개). 모든 section XML 생성/조작은 순수 문자열 기반 스크립트(`xml_writer.py`, `zip_surgery.py`)만 사용한다. 에이전트가 자체 코드에서 `from lxml import etree` 또는 `import xml.etree.ElementTree`를 사용하는 것은 금지한다.
23. **표 생성 시 xml_writer.py 필수**: 표(table) XML은 반드시 `xml_writer.py`의 `build_table()` / `table_cell_xml()` 함수로 생성한다. 에이전트가 직접 `<hp:tbl>` XML을 작성하거나 `generate_content.py` 등의 자체 스크립트를 생성하는 것은 금지한다.
24. **이미지 2곳 등록**: 이미지를 HWPX에 임베딩할 때는 `BinData/` + `content.hpf` 2곳에만 등록한다. header.xml binDataList 추가 금지. 기존 binDataList가 있으면 제거. `image_embedder.py`가 자동 처리하므로 직접 등록 로직을 작성하지 않는다.
25. **이미지 포맷 검증**: `.png` 확장자 파일의 실제 포맷이 JPEG일 수 있다 (Gemini API 등). `image_embedder.py`가 PIL로 자동 감지/변환하므로 별도 처리 불필요.
26. **hp:pic 구조 직접 작성 금지**: hp:pic XML을 에이전트가 직접 작성하지 않는다. 반드시 `image_embedder.py`의 `make_pic_xml()`을 사용한다. 검증된 구조(pypandoc-hwpx/HwpForge)를 사용하며, 요소 순서가 중요하다.

## 빠른 실행 예시

```bash
# Create
python3 "$SKILL_DIR/scripts/build_hwpx.py" --template base --output quick.hwpx

# Inspect
python3 "$SKILL_DIR/scripts/text_extract.py" quick.hwpx --format markdown

# Validate
python3 "$SKILL_DIR/scripts/validate.py" quick.hwpx
```
