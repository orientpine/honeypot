# HWPX 프로그래밍 편집 지침 (ZIP-Level Surgery)

한글 워드프로세서(.hwpx) 파일을 프로그래밍으로 편집할 때 반드시 지켜야 할 규칙.
이 지침을 위반하면 한글에서 파일이 열리지 않는다.

**구현 스크립트**: `scripts/zip_surgery.py` (이 지침을 코드로 구현)

---

## 1. ZIP-Level Surgery (유일하게 안전한 편집 방법)

원본 HWPX를 ZIP으로 열고, 수정이 필요한 XML 파일**만** 교체하고, 나머지는 원본 바이트 그대로 복사한다.

```python
# zip_surgery.py의 read_zip() + write_zip()가 이 패턴을 구현
import zipfile

with zipfile.ZipFile(src, 'r') as zin:
    entries = {}
    compress = {}
    order = []
    for info in zin.infolist():
        entries[info.filename] = zin.read(info.filename)
        compress[info.filename] = info.compress_type
        order.append(info.filename)

with zipfile.ZipFile(dst, 'w') as zout:
    for name in order:
        info = zipfile.ZipInfo(name)
        info.compress_type = compress[name]
        if name == 'Contents/section0.xml':
            zout.writestr(info, modified_bytes)
        else:
            zout.writestr(info, entries[name])
```

### 왜 unpack→repack은 안 되는가

- Python zipfile의 재압축은 compression type을 변경한다 (STORED → DEFLATED)
- `PrvImage.png`, `version.xml` 등은 반드시 원본 compression type을 유지해야 한다
- 한글은 ZIP 엔트리 순서, 압축 방식, 바이트 동일성에 민감하다

---

## 2. XML 선언 보존 (절대 규칙)

원본의 XML 선언을 한 글자도 바꾸지 않는다.

```
원본: <?xml version='1.0' encoding='UTF-8' standalone='no'?>
```

### 금지 사항

| 변경                        | 결과                |
| --------------------------- | ------------------- |
| `standalone='no'` 제거      | 파일 안 열림        |
| 작은따옴표 → 큰따옴표       | 파일 안 열림 가능성 |
| `standalone='yes'`로 변경   | 파일 안 열림 가능성 |

### Python ElementTree의 함정

`ET.tostring()`과 `ET.parse()` → `tree.write()`는 XML 선언을 **임의로 변경**한다:

- `standalone` 속성을 제거함
- 따옴표 스타일을 변경함

**해결책**: XML 선언을 문자열로 직접 보존하고, ET 직렬화 결과를 사용하지 않는다.
`zip_surgery.py`의 `parse_section()`이 이를 구현한다.

---

## 3. 네임스페이스 선언 보존 (절대 규칙)

`<hs:sec>` 루트 태그의 xmlns 선언 15개를 모두 보존한다.

```xml
<hs:sec xmlns:ha="..." xmlns:hp="..." xmlns:hp10="..." xmlns:hs="..."
        xmlns:hc="..." xmlns:hh="..." xmlns:hhs="..." xmlns:hm="..."
        xmlns:hpf="..." xmlns:dc="..." xmlns:opf="..."
        xmlns:ooxmlchart="..." xmlns:hwpunitchar="..."
        xmlns:epub="..." xmlns:config="...">
```

### Python ElementTree의 함정

- `ET.tostring()`는 **사용되지 않는 네임스페이스를 제거**한다
- `ET.register_namespace()`로 등록해도, 실제 사용하지 않으면 출력에서 빠진다
- 개별 자식 요소를 `ET.tostring()`하면 각 요소에 **중복 xmlns 선언**이 추가된다

**해결책**: 루트 태그를 원본 XML 문자열에서 직접 추출하여 보존한다.
`zip_surgery.py`의 `parse_section()`이 `xml_header`로 루트 태그 전체를 보존한다.

```python
text = xml_bytes.decode('utf-8')
root_open_end = text.find('>', text.find('<hs:sec')) + 1
xml_header = text[:root_open_end]  # XML선언 + 루트 시작 태그 전체
```

---

## 4. 개행 금지 (절대 규칙)

원본 HWPX의 section0.xml은 XML 선언 뒤 개행 1개만 존재하고, 나머지는 전부 한 줄이다.

```
<?xml version='1.0' encoding='UTF-8' standalone='no'?>\n<hs:sec ...><hp:p ...>...</hp:p><hp:p ...>...</hp:p>...</hs:sec>
```

### 금지 사항

- 자식 요소 사이에 `\n` 삽입 금지
- pretty-print / indent 금지
- `'\n'.join(children)` 금지 → `''.join(children)` 사용

### 한글이 개행을 거부하는 이유

한글 워드프로세서는 section0.xml의 개행/공백을 **텍스트 노드**로 해석하여 문서 구조를 깨뜨린다.

---

## 5. cell_writer.py 사용 금지 (ZIP-level 편집 시)

`cell_writer.py --hwpx`는 내부적으로 XML을 파싱 → 직렬화하므로:

- `standalone='no'` 제거
- 네임스페이스 선언 변경
- 대량의 개행/들여쓰기 추가

이 세 가지가 동시에 발생하여 파일을 깨뜨린다.

### 대안

- `build_hwpx.py` 또는 `pack.py` 경유 빌드에서만 cell_writer 사용 (이들은 자체적으로 네임스페이스/선언을 관리)
- ZIP-level surgery로 편집한 파일에는 cell_writer를 **절대 실행하지 않는다**
- linesegarray가 없어도 한글에서 정상적으로 열린다 (한글이 자동 재계산)

---

## 6. 자식 요소 추출: 원본 바이트 그대로

ET로 파싱한 뒤 `ET.tostring()`으로 직렬화하면 원본과 달라진다. 대신 원본 XML 문자열에서 직접 자식 요소를 슬라이싱한다.

`zip_surgery.py`의 `extract_children()`이 이를 구현한다:

```python
OPEN = "<hp:p"
CLOSE = "</hp:p>"
child_slices = []
pos = 0
while pos < len(body_text):
    start = body_text.find(OPEN, pos)
    if start == -1:
        break
    depth = 0
    scan = start
    found = False
    while True:
        next_o = body_text.find(OPEN, scan + 1)
        next_c = body_text.find(CLOSE, scan + 1)
        if next_c == -1:
            break
        if next_o != -1 and next_o < next_c:
            ch = body_text[next_o + len(OPEN)]
            if ch in (' ', '>', '/'):
                depth += 1
            scan = next_o
        else:
            if depth == 0:
                end = next_c + len(CLOSE)
                child_slices.append(body_text[start:end])
                pos = end
                found = True
                break
            depth -= 1
            scan = next_c
    if not found:
        break
```

이 방식으로 추출한 문자열은 원본과 바이트 동일하다. `<hp:p>` 내부에 중첩된 `<hp:p>` (테이블 셀 내부)를 depth 카운팅으로 올바르게 처리한다.

---

## 7. 새 요소 삽입: 문자열로 직접 생성

새로 추가하는 `<hp:p>` 요소도 ET가 아닌 문자열로 생성한다.
`zip_surgery.py`의 `make_paragraph()`, `make_multi_run_paragraph()`이 이를 구현한다.

```python
para = (
    f'<hp:p id="{pid}" paraPrIDRef="38" styleIDRef="0" '
    f'pageBreak="0" columnBreak="0" merged="0">'
    f'<hp:run charPrIDRef="45"><hp:t>내용</hp:t></hp:run>'
    f'</hp:p>'
)
```

- 네임스페이스 접두사 (`hp:`)만 사용, xmlns 선언은 루트에만 존재
- `&`, `<`, `>`, `"`, `'`는 직접 이스케이프 (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&apos;`)
- 빈 텍스트는 `<hp:t/>` (self-closing)

---

## 8. 표 행 높이 자동 조절 및 페이지 넘김 설정

프로그래밍으로 생성한 표는 모든 행이 동일한 고정 높이(`cellSz height`)로 설정되어 내용이 잘린다. 반드시 다음 두 가지를 설정한다.

### 행 높이 자동 조절

```xml
<hp:tbl ... noAdjust="0">
```

- `noAdjust="0"`: 한글이 셀 내용에 맞춰 행 높이를 자동 확장 (필수)
- `noAdjust="1"`: 고정 높이 — 내용이 잘림 (금지)

### 페이지 간 표 넘김 허용

```xml
<hp:tbl ... pageBreak="CELL">
```

| 값       | 동작                                              |
| -------- | ------------------------------------------------- |
| `CELL`   | 셀 단위로 페이지 넘김 허용 (권장)                 |
| `NONE`   | 표 전체가 한 페이지에 강제 배치 — 표가 크면 잘림  |

---

## 9. 검증 체크리스트

편집 완료 후 반드시 확인 (`validate.py --strict` 또는 `zip_surgery.py validate`):

- [ ] `standalone='no'` 보존되었는가
- [ ] xmlns 선언 10개 이상(일반적으로 15개) 루트 태그에 존재하는가
- [ ] 본문에 추가 xmlns 선언이 0개인가
- [ ] 개행이 1개(XML 선언 뒤)만 존재하는가
- [ ] 비-section 파일이 원본과 byte-identical인가
- [ ] ZIP 엔트리 순서, 압축 방식이 원본과 동일한가
- [ ] cell_writer.py를 실행하지 않았는가
- [ ] validate.py를 통과하는가
- [ ] 한글에서 실제로 열리는가 (최종 확인 필수)

```python
with zipfile.ZipFile(v3, 'r') as z:
    sec0 = z.read('Contents/section0.xml').decode('utf-8')

assert "standalone='no'" in sec0[:100]
assert sec0.count('\n') == 1
assert 'xmlns:config=' in sec0[:2000]

import re
root_end = sec0.find('>', sec0.find('<hs:sec')) + 1
assert len(re.findall(r'xmlns:', sec0[root_end:])) == 0
```

---

## 10. 단계적 디버깅 전략

파일이 안 열릴 때:

1. **최소 변경 테스트**: 삭제만 하고 삽입 없이 열리는지 확인
2. **단일 요소 테스트**: 간단한 `<hp:p>` 1개만 추가해서 열리는지 확인
3. **테이블 테스트**: 간단한 `<hp:tbl>` 1개 추가해서 열리는지 확인
4. **전체 삽입 테스트**: 모든 내용 삽입
5. **cell_writer 테스트**: cell_writer 실행 전후 비교

각 단계에서 실패하면, 해당 단계의 변경 내용이 원인이다.

---

## 워크플로우 선택 기준

| 상황 | 권장 워크플로우 | 스크립트 |
|------|----------------|----------|
| 기존 HWPX의 텍스트만 교체 | ZIP-Level Surgery | `zip_surgery.py` |
| 기존 HWPX의 구조를 변경 (문단/표 추가/삭제) | ZIP-Level Surgery | `zip_surgery.py` |
| 레퍼런스 HWPX 기반 새 문서 생성 | XML-first + build | `build_hwpx.py` |
| 템플릿의 플레이스홀더 텍스트 치환 | ZIP 텍스트 치환 | `zip_replace()` (hwpx-templates) |
| 새 문서를 처음부터 생성 | XML-first + build | `build_hwpx.py` |
| unpack 후 수동 XML 편집 | unpack → edit → pack | `unpack.py` + `pack.py` |

### ZIP-Level Surgery vs XML-first Build

- **ZIP-Level Surgery**: 기존 파일의 바이트 레벨 무결성을 보존해야 할 때. `standalone='no'`, 네임스페이스, 개행, 압축 방식 등이 모두 원본과 동일하게 유지된다.
- **XML-first Build**: 새 문서를 조립할 때. `build_hwpx.py`가 템플릿에서 올바른 구조를 생성하므로 `standalone`이나 네임스페이스 문제가 발생하지 않는다.
