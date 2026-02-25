---
name: hwpx-core
description: "HWPX XML-first document authoring skill for create/edit/read/validate workflows and template-driven generation. Use when you need deterministic Korean document layout control via section0.xml/header.xml and script-based build pipelines instead of opaque editors."
---

# HWPX Core

HWPX XML-first 스킬입니다. 핵심 원칙은 `section0.xml` + `header.xml`을 직접 제어하고,
`build_hwpx.py`로 문서를 조립한 뒤 `validate.py`로 무결성을 확인하는 것입니다.

상세한 XML 요소 해설, 고급 표 산식 예시, 심화 네임스페이스 레퍼런스는
`$SKILL_DIR/references/`로 분리해 유지합니다.

## 디렉토리 기준

- `SKILL_DIR`: `SKILL.md`가 위치한 `hwpx-core` 디렉토리의 절대 경로
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

## 스크립트 요약 (6)

| Script | Purpose |
|---|---|
| `scripts/build_hwpx.py` | 템플릿 + XML 오버라이드로 `.hwpx` 조립 |
| `scripts/analyze_template.py` | 레퍼런스 HWPX 구조/스타일 분석 |
| `scripts/text_extract.py` | 본문/표 텍스트 추출 |
| `scripts/validate.py` | ZIP/XML/필수 엔트리 구조 검증 |
| `scripts/office/unpack.py` | HWPX를 디렉토리로 풀어 XML 편집 준비 |
| `scripts/office/pack.py` | 수정 디렉토리를 HWPX로 재패키징 |

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

## 템플릿별 스타일 ID 맵 (5)

### 1) base

| Group | IDs | Meaning |
|---|---|---|
| charPr | 0-6 | 기본 글꼴군 (본문/기본 변형) |
| paraPr | 0-19 | 기본 문단군 (정렬/간격/목차 계열) |
| borderFill | 1-2 | 기본 테두리/투명 배경 참조 |

### 2) gonmun

| Group | IDs | Meaning |
|---|---|---|
| charPr | 7-10 | 기관명/제목/서명/표헤더 강조 |
| paraPr | 20-22 | 중앙 정렬 및 표 셀 전용 문단 |
| borderFill | 3-4 | 일반 표선 + 헤더 배경 표선 |

### 3) report

| Group | IDs | Meaning |
|---|---|---|
| charPr | 7-13 | 제목/소제목/표헤더/강조/섹션헤더 |
| paraPr | 20-27 | 들여쓰기 단계, 우측 정렬, 섹션 헤더 라인 |
| borderFill | 3-5 | 기본 표선, 헤더 배경, 상하 라인 강조 |

### 4) minutes

| Group | IDs | Meaning |
|---|---|---|
| charPr | 7-9 | 회의 제목/라벨/표헤더 강조 |
| paraPr | 20-22 | 회의록 표준 문단 변형 |
| borderFill | 3-4 | 표선 + 연녹색 헤더 배경 |

### 5) proposal

| Group | IDs | Meaning |
|---|---|---|
| charPr | 7-11 | 제안서 제목/소제목/번호배지(흰색 텍스트) |
| paraPr | 20-22 | 섹션/표 셀 정렬 세트 |
| borderFill | 3-8 | 표선, 회색/녹색/파란색 배지 배경 |

## Workflow 1. XML-first 문서 생성 (build_hwpx.py)

1. 템플릿 선택: `base`, `gonmun`, `report`, `minutes`, `proposal`
2. `section0.xml` 준비: 본문/표/문단 ID를 순차로 설계
3. 필요 시 `header.xml` 준비: 스타일 ID와 `itemCnt` 정합성 유지
4. 빌드 실행:
   - `python "$SKILL_DIR/scripts/build_hwpx.py" --template report --section my_section0.xml --output out.hwpx`
5. 즉시 검증:
   - `python "$SKILL_DIR/scripts/validate.py" out.hwpx`

필수 포인트:
- 첫 문단 첫 run에 `secPr` + `colPr`가 있어야 함
- `charPrIDRef`/`paraPrIDRef`는 `header.xml` 정의와 일치해야 함

## Workflow 2. 기존 문서 편집 (unpack -> Edit -> pack)

1. 풀기:
   - `python "$SKILL_DIR/scripts/office/unpack.py" source.hwpx ./workdir`
2. 편집:
   - `./workdir/Contents/section0.xml`
   - `./workdir/Contents/header.xml`
3. 재패키징:
   - `python "$SKILL_DIR/scripts/office/pack.py" ./workdir edited.hwpx`
4. 검증:
   - `python "$SKILL_DIR/scripts/validate.py" edited.hwpx`

편집 규칙:
- XML 네임스페이스 접두사(`hp`, `hh`, `hs`, `hc`)를 유지
- 표 열 너비 합은 본문폭(42520)과 일치

## Workflow 3. 문서 읽기/텍스트 추출 (text_extract.py)

1. 기본 추출:
   - `python "$SKILL_DIR/scripts/text_extract.py" input.hwpx`
2. 표 포함 추출:
   - `python "$SKILL_DIR/scripts/text_extract.py" input.hwpx --include-tables`
3. 마크다운 포맷:
   - `python "$SKILL_DIR/scripts/text_extract.py" input.hwpx --format markdown`

활용:
- 레거시 HWPX 품질 점검 전 텍스트 스냅샷 생성
- 템플릿 재설계 전 문단/표 구조 파악

## Workflow 4. 문서 검증 (validate.py)

1. 단일 파일 검증:
   - `python "$SKILL_DIR/scripts/validate.py" target.hwpx`
2. 실패 시 원인 분기:
   - ZIP 구조 문제 / 필수 파일 누락 / XML 파싱 오류
3. 수정 후 재검증:
   - 편집 루프로 돌아가 동일 파일 재검증

검증 체크:
- `mimetype` 엔트리 순서/압축 방식
- 필수 엔트리 존재 (`Contents/*`, `META-INF/*`, `version.xml`)
- XML well-formedness

## Workflow 5. 레퍼런스 기반 문서 생성 (analyze_template.py)

1. 레퍼런스 분석:
   - `python "$SKILL_DIR/scripts/analyze_template.py" reference.hwpx`
2. 구조 추출:
   - `python "$SKILL_DIR/scripts/analyze_template.py" reference.hwpx --extract-header ref_header.xml --extract-section ref_section.xml`
3. 신규 본문 작성:
   - 추출된 스타일 ID와 테이블 span 패턴을 유지해 `new_section0.xml` 작성
4. 조립:
   - `python "$SKILL_DIR/scripts/build_hwpx.py" --header ref_header.xml --section new_section0.xml --output generated.hwpx`
5. 검증:
   - `python "$SKILL_DIR/scripts/validate.py" generated.hwpx`

재현 원칙:
- 스타일 ID를 임의 재번호화하지 않음
- `rowSpan`/`colSpan`/`cellMargin` 패턴을 보존

## Critical Rules

1. 입력 포맷은 `.hwpx`만 허용 (`.hwp`는 변환 후 처리).
2. XML-first 생성의 기본 진입점은 항상 `build_hwpx.py`.
3. 패키징 결과는 항상 `validate.py`로 검증.
4. 템플릿 스타일 ID 체계를 깨지 말고 참조 일관성을 유지.
5. 대량 내용 확장 시 본 파일은 절차 중심으로 유지하고, 세부 도표/스키마는 `references/`에 분리.

## 빠른 실행 예시

```bash
# Create
python "$SKILL_DIR/scripts/build_hwpx.py" --template base --output quick.hwpx

# Inspect
python "$SKILL_DIR/scripts/text_extract.py" quick.hwpx --format markdown

# Validate
python "$SKILL_DIR/scripts/validate.py" quick.hwpx
```
