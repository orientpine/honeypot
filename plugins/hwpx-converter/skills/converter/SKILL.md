---
name: hwpx-converter
description: "Markdown 파일을 한글 문서(HWPX)로 변환합니다. pypandoc-hwpx 기반."
---

# HWPX Converter

Markdown 파일을 한글 문서(HWPX)로 변환합니다.

---

## 사용자 입력 스키마

### 필수 입력

| 항목 | 설명 | 예시 |
|------|------|------|
| 입력 경로 | 변환할 .md 파일 또는 폴더 | `./report.md` 또는 `./docs/` |

### 선택 입력

| 항목 | 설명 | 기본값 |
|------|------|--------|
| 출력 경로 | 출력 위치 | 입력과 동일 위치 |

---

## Prerequisites (필수 설치)

⚠️ **이 스킬을 사용하려면 아래 프로그램이 설치되어 있어야 합니다.**

### 자동 설치 (권장)

**`hwpx-setup` 스킬을 호출하면 의존성을 자동으로 설치합니다.**

```
hwpx-setup 스킬을 사용해서 의존성을 설치해줘
```

### 수동 설치

**1. Pandoc 설치** (시스템 의존성)
- Windows: `winget install pandoc` 또는 [공식 다운로드](https://pandoc.org/installing.html)
- macOS: `brew install pandoc`
- Linux: `sudo apt install pandoc`

**2. pypandoc-hwpx 설치**
```bash
pip install pypandoc-hwpx
```

**설치 확인:**
```bash
pandoc --version
pypandoc-hwpx --help
```

상세 설치 가이드: 아래 "설치 가이드" 섹션 참조 또는 pypandoc-hwpx GitHub 페이지 참조

---

## 워크플로우

### Phase 1: 입력 검증
- 입력 경로 존재 확인
- .md 파일 여부 확인 (폴더면 내부 .md 파일 목록 생성)

### Phase 2: 환경 체크
- `pandoc --version` 실행하여 Pandoc 설치 확인
- 미설치 시 설치 가이드 안내 후 중단

### Phase 3: 변환 실행

**단일 파일:**
```bash
pypandoc-hwpx [input.md] -o [input.hwpx]
```

**폴더 배치 (1단계만):**
```bash
for file in [folder]/*.md; do
  pypandoc-hwpx "$file" -o "${file%.md}.hwpx"
done
```

### Phase 4: 결과 출력
- 변환 성공: 생성된 .hwpx 파일 경로 출력
- 변환 실패: Pandoc 에러 메시지 그대로 전달

---

## 에러 처리

| 상황 | 처리 |
|------|------|
| Pandoc 미설치 | 설치 가이드 안내 후 중단 |
| 파일 없음 | 에러 메시지 출력 |
| 변환 실패 | pypandoc-hwpx 에러 메시지 전달 |

---

## Limitations (v1.0)

- **MD→HWPX만 지원** (DOCX→HWPX 미지원)
- **기본 템플릿만** (`--reference-doc` 옵션 미지원)
- **1단계 폴더만** (하위 폴더 재귀 탐색 안 함)
- **자동 덮어쓰기** (동일 이름 hwpx 파일 존재 시)

---

## 리소스

- 설치 가이드: pypandoc-hwpx GitHub (https://github.com/anthropics/pypandoc-hwpx) 참조
