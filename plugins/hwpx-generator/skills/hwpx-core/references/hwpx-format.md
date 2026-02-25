# HWPX (OWPML) 파일 포맷 레퍼런스

## 개요

HWPX는 한글(Hancom Office)의 차세대 문서 포맷으로, **OWPML**(Open Word-Processor Markup Language) 표준(KS X 6101:2024)을 따른다. ZIP 기반 XML 컨테이너 형식이며, DOCX/XLSX와 유사한 OPC(Open Packaging Conventions) 구조를 사용한다.

## 파일 내부 구조

```
document.hwpx (ZIP archive)
├── mimetype                    # "application/hwp+zip" (첫 번째 엔트리, 비압축)
├── META-INF/
│   ├── container.xml           # 패키지 루트 파일 위치
│   ├── container.rdf           # 관계 정보
│   └── manifest.xml            # 파일 목록
├── Contents/
│   ├── content.hpf             # 매니페스트 (OPF 형식, 섹션/헤더 목록)
│   ├── header.xml              # 문서 헤더 (스타일, 폰트, CharShape, ParaShape 정의)
│   ├── section0.xml            # 본문 섹션 (문단, 표, 그림 등)
│   ├── section1.xml            # 추가 섹션 (있는 경우)
│   └── ...
├── Preview/
│   ├── PrvImage.png            # 미리보기 이미지
│   └── PrvText.txt             # 미리보기 텍스트
├── settings.xml                # 편집 설정
└── version.xml                 # 버전 정보
```

### 핵심 규칙

- **mimetype**: 반드시 ZIP 아카이브의 **첫 번째 엔트리**여야 하며 **ZIP_STORED**(비압축)로 저장
- **content.hpf**: OPF 형식의 매니페스트. 모든 콘텐츠 파일 참조
- **header.xml**: 문서 전역 스타일 정의 (CharShape, ParaShape, BorderFill 등)
- **section*.xml**: 실제 문서 콘텐츠

## XML 네임스페이스

| 접두사 | URI | 용도 |
|--------|-----|------|
| `hp` | `http://www.hancom.co.kr/hwpml/2011/paragraph` | 문단, 런, 텍스트, 표, 컨트롤 |
| `hs` | `http://www.hancom.co.kr/hwpml/2011/section` | 섹션 루트 |
| `hc` | `http://www.hancom.co.kr/hwpml/2011/core` | 핵심 데이터 타입 |
| `hh` | `http://www.hancom.co.kr/hwpml/2011/head` | 헤더 (스타일/속성 정의) |
| `ha` | `http://www.hancom.co.kr/hwpml/2011/app` | 앱 메타데이터 |
| `hp10` | `http://www.hancom.co.kr/hwpml/2016/paragraph` | 확장 문단 요소 |
| `hpf` | `http://www.hancom.co.kr/schema/2011/hpf` | 매니페스트 (content.hpf) |
| `opf` | `http://www.idpf.org/2007/opf/` | OPF 패키지 |

## 주요 XML 요소

### 섹션 (section*.xml)

```xml
<hs:sec xmlns:hp="..." xmlns:hs="...">
  <hp:p>...</hp:p>     <!-- 문단 -->
  <hp:p>...</hp:p>     <!-- 문단 -->
</hs:sec>
```

### 문단 (Paragraph)

```xml
<hp:p id="..." paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:t>텍스트 내용</hp:t>
  </hp:run>
</hp:p>
```

- `paraPrIDRef`: header.xml의 ParaShape 참조 ID
- `styleIDRef`: header.xml의 Style 참조 ID
- `charPrIDRef`: header.xml의 CharShape 참조 ID (run 레벨)

### 텍스트 런 (Run)

```xml
<hp:run charPrIDRef="2">
  <hp:t>볼드 텍스트</hp:t>
</hp:run>
```

- 하나의 문단에 여러 런 가능 (서식이 다른 텍스트)
- `charPrIDRef`로 글자 서식 참조

### 테이블 (Table)

```xml
<hp:tbl id="..." rowCnt="2" colCnt="3" cellSpacing="0" borderFillIDRef="3">
  <hp:sz width="21600" height="7200" />
  <hp:pos treatAsChar="1" />
  <hp:tr>                           <!-- 행 -->
    <hp:tc borderFillIDRef="3">     <!-- 셀 -->
      <hp:cellAddr colAddr="0" rowAddr="0" colSpan="1" rowSpan="1"/>
      <hp:cellSz width="7200" height="3600"/>
      <hp:cellMargin left="510" right="510" top="142" bottom="142"/>
      <hp:subList>
        <hp:p ...>
          <hp:run ...>
            <hp:t>셀 내용</hp:t>
          </hp:run>
        </hp:p>
      </hp:subList>
    </hp:tc>
  </hp:tr>
</hp:tbl>
```

### 섹션 속성 (Section Properties)

첫 번째 문단의 첫 번째 런에 포함됨:

```xml
<hp:secPr textDirection="HORIZONTAL" ...>
  <hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY">
    <hp:margin header="4252" footer="4252" gutter="0"
               left="8504" right="8504" top="5668" bottom="4252"/>
  </hp:pagePr>
</hp:secPr>
```

- 단위: HWPUNIT (1/7200 인치). 예: 59528 ≈ A4 폭(210mm)
- `width="59528"` = A4 가로, `height="84186"` = A4 세로
- 여백: `left/right/top/bottom` 값 (HWPUNIT)

### 인라인 컨트롤

```xml
<hp:run>
  <hp:ctrl>
    <hp:colPr type="NEWSPAPER" colCount="1" />
  </hp:ctrl>
</hp:run>
```

```xml
<hp:run>
  <hp:lineBreak/>    <!-- 줄바꿈 -->
  <hp:tab/>          <!-- 탭 -->
</hp:run>
```

## header.xml 주요 구조

### CharShape (글자 서식)

```xml
<hh:charProperties itemCnt="...">
  <hh:charPr id="0" height="1000" textColor="#000000" shadeColor="none"
             useFontSpace="0" useKerning="0" symMark="NONE"
             borderFillIDRef="0">
    <hh:fontRef hangul="한양신명조" latin="Times New Roman" .../>
    <hh:ratio hangul="100" latin="100" .../>
    <hh:spacing hangul="0" latin="0" .../>
    <hh:relSz hangul="100" latin="100" .../>
    <hh:offset hangul="0" latin="0" .../>
    <hh:bold/>          <!-- 볼드 (요소 존재 시 활성) -->
    <hh:italic/>        <!-- 이탤릭 -->
    <hh:underline type="BOTTOM" shape="SOLID" color="#000000"/>
    <hh:strikeout type="NONE"/>
    <hh:outline type="NONE"/>
    <hh:shadow type="NONE"/>
    <hh:emboss type="NONE"/>
    <hh:engrave type="NONE"/>
    <hh:supscript type="NONE"/>
  </hh:charPr>
</hh:charProperties>
```

- `height`: 글자 크기 (HWPUNIT 단위, 1000 = 10pt)
- `textColor`: 글자 색상 (#RRGGBB)
- 볼드/이탤릭: 해당 요소 존재 여부로 판단

### ParaShape (문단 서식)

```xml
<hh:paraProperties itemCnt="...">
  <hh:paraPr id="0" align="JUSTIFY" vertalign="BASELINE"
             headingType="NONE" level="0" tabPrIDRef="0"
             condense="0" fontLineHeight="0" snapToGrid="1"
             suppressLineNumbers="0" checked="0">
    <hh:margin indent="0" left="0" right="0"/>
    <hh:lineSpacing type="PERCENT" value="160" unit="HWPUNIT"/>
    <hh:heading type="NONE" idRef="0" level="0"/>
    <hh:border borderFillIDRef="0" offsetLeft="0" offsetRight="0"
               offsetTop="0" offsetBottom="0" connect="0" ignoreMargin="0"/>
    <hh:autoSpacing eAsianEng="0" eAsianNum="0"/>
  </hh:paraPr>
</hh:paraProperties>
```

- `align`: `JUSTIFY`, `LEFT`, `RIGHT`, `CENTER`
- `lineSpacing`: `type="PERCENT"`, `value="160"` = 160% 줄간격

## 단위 변환

| 단위 | 설명 | 변환 |
|------|------|------|
| HWPUNIT | 한글 내부 단위 | 1 HWPUNIT = 1/7200 인치 |
| pt (포인트) | 글꼴 크기 | 1pt = 100 HWPUNIT |
| mm (밀리미터) | 용지/여백 | 1mm ≈ 283.46 HWPUNIT |

### 일반적인 값

- A4 용지: width=59528, height=84186
- 10pt 글꼴: height=1000
- 12pt 글꼴: height=1200
- 기본 여백 (좌/우): 8504 (≈ 30mm)
- 기본 여백 (상): 5668 (≈ 20mm)
- 기본 여백 (하): 4252 (≈ 15mm)

## python-hwpx API 매핑

| 작업 | python-hwpx 메서드 | 비고 |
|------|---------------------|------|
| 새 문서 | `HwpxDocument.new()` | 빈 Skeleton 템플릿 사용 |
| 파일 열기 | `HwpxDocument.open(path)` | 경로, bytes, BinaryIO 모두 가능 |
| 문단 추가 | `doc.add_paragraph(text, section=)` | charPrIDRef로 서식 지정 가능 |
| 표 추가 | `doc.add_table(rows, cols, section=)` | borderFillIDRef 자동 생성 |
| 셀 텍스트 | `table.set_cell_text(row, col, text)` | 0-indexed |
| 머리글 | `doc.set_header_text(text, section=)` | |
| 바닥글 | `doc.set_footer_text(text, section=)` | |
| 메모 | `doc.add_memo_with_anchor(text, ...)` | MEMO 필드 자동 생성 |
| 볼드/이탤릭 런 스타일 | `doc.ensure_run_style(bold=True)` | charPrIDRef 반환 |
| 텍스트 추출 | `TextExtractor(path).extract_text()` | 테이블 포함 옵션 |
| 저장 | `doc.save_to_path(path)` | |
| bytes 반환 | `doc.to_bytes()` | |

## low-level XML 접근

python-hwpx의 고수준 API로 처리할 수 없는 경우:

1. **unpack** → XML 직접 편집 → **pack** 워크플로우 사용
2. `doc.oxml` 속성으로 low-level XML 트리 접근 가능
3. `doc.sections[0].element` 로 lxml Element 직접 조작

### 예: 용지 크기 변경 (A4 → B5)

```python
# unpack 후 section0.xml 편집
# <hp:pagePr> 의 width, height 속성 변경
# B5: width=51592, height=72850
```

### 예: 글꼴 변경 (header.xml)

```python
# <hh:charPr id="0"> 의 <hh:fontRef> 속성 변경
# hangul="맑은 고딕" latin="Arial"
```
