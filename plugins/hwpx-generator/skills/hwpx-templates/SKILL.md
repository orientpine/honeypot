---
name: hwpx-templates
description: "HWPX 템플릿 기반 문서 생성 및 ZIP-level 치환 워크플로우를 제공한다. Use when 사용자 업로드 양식 또는 기본 양식을 기반으로 보고서/공문서를 빠르게 생성해야 할 때."
---

# HWPX Templates Skill

## 목적

이 스킬은 템플릿(.hwpx) 복사 후 ZIP-level XML 치환으로 문서를 생성하는 표준 절차를 제공한다.
핵심은 **양식 우선**, **ObjectFinder 전수 조사**, **ZIP-level 치환**, **네임스페이스 후처리**, **재검증**이다.

## 양식 선택 정책 (필수)

1. 사용자 업로드 양식이 있으면 최우선 사용
2. 업로드 양식이 없으면 기본 양식 `assets/report-template.hwpx` 사용
3. `HwpxDocument.new()`는 템플릿이 필요 없는 극단적으로 단순한 문서에서만 사용

## 필수 워크플로우

1. 양식 복사
2. ObjectFinder 조사
3. ZIP 치환
4. 네임스페이스 후처리
5. 결과 검증

```text
[1] 템플릿 파일 복사
    ↓
[2] ObjectFinder로 텍스트 전수 조사
    ↓
[3] 치환 매핑 설계 및 ZIP-level 치환
    ↓
[4] fix_namespaces.py 실행 (ZIP-level 작업에서만)
    ↓
[5] ObjectFinder로 잔여 플레이스홀더 검증
```

## ObjectFinder 전수 조사

치환 전 반드시 템플릿의 실제 텍스트를 조사한다.

```python
from hwpx import ObjectFinder

finder = ObjectFinder("work.hwpx")
for result in finder.find_all(tag="t"):
    if result.text and result.text.strip():
        print(repr(result.text))
```

조사 결과를 기준으로 플레이스홀더 매핑을 작성한다.

## ZIP-level 치환 함수 (inline code)

### zip_replace()

```python
import os
import zipfile


def zip_replace(src_path, dst_path, replacements):
    """HWPX ZIP 내 Contents/*.xml 전체에서 텍스트를 일괄 치환한다."""
    tmp_path = dst_path + ".tmp"

    with zipfile.ZipFile(src_path, "r") as zin:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("Contents/") and item.filename.endswith(".xml"):
                    text = data.decode("utf-8")
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                    data = text.encode("utf-8")
                zout.writestr(item, data)

    os.replace(tmp_path, dst_path)
```

### zip_replace_sequential()

```python
import os
import zipfile


def zip_replace_sequential(src_path, dst_path, old, new_list):
    """동일 플레이스홀더를 section XML에서 순서대로 1회씩 치환한다."""
    tmp_path = dst_path + ".tmp"

    with zipfile.ZipFile(src_path, "r") as zin:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if "section" in item.filename and item.filename.endswith(".xml"):
                    text = data.decode("utf-8")
                    for new_value in new_list:
                        text = text.replace(old, new_value, 1)
                    data = text.encode("utf-8")
                zout.writestr(item, data)

    os.replace(tmp_path, dst_path)
```

## 기본 양식 활용 가이드

- 기본 양식: `assets/report-template.hwpx`
- 적용 순서:
  1) 양식 복사
  2) ObjectFinder 조사
  3) 일괄 치환 + 순차 치환
  4) `scripts/fix_namespaces.py` 실행
  5) 재검증

예시:

```python
import shutil
import subprocess

template_path = "assets/report-template.hwpx"
work_path = "output/report.hwpx"

shutil.copy(template_path, work_path)

zip_replace(work_path, work_path, {
    "브라더 공기관": "실제 기관명",
    "기본 보고서 양식": "실제 보고서 제목",
})

zip_replace_sequential(
    work_path,
    work_path,
    "헤드라인M 폰트 16포인트(문단 위 15)",
    ["항목 1", "항목 2", "항목 3"],
)

subprocess.run(["python", "scripts/fix_namespaces.py", work_path], check=True)
```

## 사용자 업로드 양식 활용 가이드

- 업로드된 양식 파일을 작업 경로로 복사
- 조사 없이 바로 치환하지 않는다
- 양식마다 플레이스홀더 구조가 달라 반드시 조사 후 매핑한다

예시:

```python
import shutil
import subprocess

uploaded_template = "input/custom-template.hwpx"
work_path = "output/custom-report.hwpx"

shutil.copy(uploaded_template, work_path)

from hwpx import ObjectFinder

finder = ObjectFinder(work_path)
for result in finder.find_all(tag="t"):
    if result.text and result.text.strip():
        print(repr(result.text))

zip_replace(work_path, work_path, {
    "양식의 기존 텍스트": "치환 값",
})

subprocess.run(["python", "scripts/fix_namespaces.py", work_path], check=True)
```

## fix_namespaces.py 설명 (중요)

`scripts/fix_namespaces.py`는 ZIP-level 치환 이후 XML prefix를 정규화하는 후처리 스크립트다.

- 목적: `ns0`, `ns1` 같은 prefix 잔존으로 인해 뷰어에서 빈 페이지가 나타나는 문제 완화
- 구현 방식: `re` 기반 문자열 치환 (의도적으로 `lxml` 미사용)
- 적용 범위: **ZIP-level replacement 워크플로우에서만 필수**
- 비적용 범위: **XML-first 빌드(`hwpx-core`)에는 기본적으로 불필요**

## 스크립트 참조 및 실행 (CRITICAL)

`fix_namespaces.py`는 이 스킬의 상대경로에 위치한다.

```text
scripts/fix_namespaces.py
```

실행 순서:

1. 상대경로로 실행 (최우선)
   - `python scripts/fix_namespaces.py <file.hwpx>`

2. 상대경로 실패 시 Glob 폴백
   - `**/hwpx-generator/skills/hwpx-templates/scripts/fix_namespaces.py`

3. Glob도 실패 시 확장 탐색
   - `**/fix_namespaces.py`

스크립트를 찾지 못하면 즉시 중단하고 경로 확인을 요청한다.
스크립트를 대체하기 위해 임의 Python 코드를 새로 작성하지 않는다.

## Quick Reference

| 작업 | 권장 방법 |
|---|---|
| 템플릿 문서 생성 | 양식 복사 + `zip_replace()` |
| 반복 플레이스홀더 치환 | `zip_replace_sequential()` |
| 양식 텍스트 조사 | `ObjectFinder(...).find_all(tag="t")` |
| ZIP-level 후처리 | `python scripts/fix_namespaces.py <file.hwpx>` |
| XML-first 생성 | `hwpx-core` 경로 우선, 본 후처리 생략 가능 |

## Markdown 서식 처리 (zip_replace 시 주의)

`zip_replace()` 또는 `zip_replace_sequential()`로 치환할 값에 Markdown 서식 기호(`**`, `*`, `~~` 등)가 포함된 경우, 해당 기호가 HWPX 문서에 그대로 노출된다.

### 대응 방법

1. **치환 값에서 Markdown 기호를 사전 제거**한다.
   - `**볼드 텍스트**` → `볼드 텍스트`
   - `*이탤릭*` → `이탤릭`
   - `~~취소선~~` → `취소선`

2. ZIP-level 치환은 **단순 텍스트 교체**이므로, Markdown 인라인 서식을 HWPX의 multi-run 구조로 변환할 수 없다. 인라인 서식이 필요한 경우 `hwpx-core`의 XML-first 생성 경로를 사용해야 한다.

3. 치환 값이 `.md` 파일에서 가져온 경우, Markdown 파싱 후 순수 텍스트만 추출하여 치환한다.

## 주의사항 (11개)

1. 양식 선택은 반드시 사용자 업로드 > 기본 양식 > `new()` 순서
2. 치환 전 ObjectFinder 조사 생략 금지
3. 반복 플레이스홀더를 일괄 치환만으로 처리하지 말 것
4. ZIP-level 치환 후 `fix_namespaces.py` 누락 금지
5. `fix_namespaces.py`를 `lxml` 기반으로 재작성하지 말 것
6. `HwpxDocument.open()` 중심 접근을 기본값으로 두지 말 것
7. 절대경로 하드코딩 대신 상대경로/환경 기반 경로 사용
8. 치환 후 잔여 플레이스홀더를 반드시 재검증할 것
9. XML-first 빌드와 ZIP-level 빌드를 혼동하지 말 것
10. 스크립트 미탐지 시 임시 대체 코드 작성 대신 즉시 중단/보고
11. Markdown 서식 기호가 포함된 값을 zip_replace에 직접 전달하지 말 것
