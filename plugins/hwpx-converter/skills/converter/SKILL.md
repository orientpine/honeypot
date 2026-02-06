---
name: converter
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

### 상세 설치 가이드

#### 필수 의존성

| 프로그램 | 버전 | 용도 |
|----------|------|------|
| Pandoc | 3.0+ | 문서 변환 엔진 |
| Python | 3.6+ | pypandoc-hwpx 실행 환경 |
| pypandoc-hwpx | 최신 | HWPX 변환 도구 |

#### 1. Pandoc 설치

##### Windows

**방법 A: 공식 설치 파일 (권장)**
1. https://pandoc.org/installing.html 접속
2. Windows 설치 파일(.msi) 다운로드
3. 설치 파일 실행 및 설치 완료
4. 터미널 재시작

**방법 B: winget 사용**
```powershell
winget install --id JohnMacFarlane.Pandoc
```

**방법 C: Chocolatey 사용**
```powershell
choco install pandoc
```

##### macOS

**Homebrew 사용 (권장)**
```bash
brew install pandoc
```

**MacPorts 사용**
```bash
sudo port install pandoc
```

##### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install pandoc
```

##### Linux (Fedora/RHEL)

```bash
sudo dnf install pandoc
```

##### Linux (Arch)

```bash
sudo pacman -S pandoc
```

#### 2. Python 설치

##### Windows

1. https://python.org/downloads/ 접속
2. 최신 Python 설치 파일 다운로드
3. **"Add Python to PATH" 체크** (중요!)
4. 설치 완료

##### macOS

**Homebrew 사용 (권장)**
```bash
brew install python
```

##### Linux

대부분의 Linux 배포판에 기본 설치되어 있습니다.
```bash
# 확인
python3 --version

# 미설치 시 (Ubuntu/Debian)
sudo apt install python3 python3-pip
```

#### 3. pypandoc-hwpx 설치

Python과 pip가 설치된 후:

```bash
pip install pypandoc-hwpx
```

또는 Python 3 명시적 사용:

```bash
python3 -m pip install pypandoc-hwpx
```

#### 설치 확인

모든 설치가 완료되면 아래 명령어로 확인합니다:

```bash
# Pandoc 버전 확인
pandoc --version

# Python 버전 확인
python --version

# pypandoc-hwpx 도움말
pypandoc-hwpx --help
```

**예상 출력:**
```
pandoc 3.x.x
...

Python 3.x.x

usage: pypandoc-hwpx [-h] [--reference-doc REFERENCE_DOC] [-o OUTPUT] input
...
```

#### 트러블슈팅

##### "pandoc: command not found"

**원인:** Pandoc이 PATH에 등록되지 않음

**해결:**
- Windows: 터미널 재시작 또는 시스템 재부팅
- macOS/Linux: 셸 설정 파일 리로드 (`source ~/.bashrc` 또는 `source ~/.zshrc`)

##### "pip: command not found"

**원인:** Python pip가 PATH에 없음

**해결:**
```bash
# Python 모듈로 pip 실행
python -m pip install pypandoc-hwpx

# 또는 python3 사용
python3 -m pip install pypandoc-hwpx
```

##### "Permission denied" (Linux/macOS)

**원인:** 시스템 Python에 설치 시도

**해결:**
```bash
# 사용자 설치 (권장)
pip install --user pypandoc-hwpx

# 또는 venv 사용
python -m venv .venv
source .venv/bin/activate
pip install pypandoc-hwpx
```

##### 변환 시 한글 깨짐

**원인:** 파일 인코딩 문제

**해결:**
- 소스 .md 파일이 UTF-8로 저장되어 있는지 확인
- BOM 없는 UTF-8 권장

#### 참고 링크

- [Pandoc 공식 문서](https://pandoc.org/)
- [pypandoc-hwpx GitHub](https://github.com/msjang/pypandoc-hwpx)
- [pypandoc-hwpx PyPI](https://pypi.org/project/pypandoc-hwpx/)

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

상세 설치 가이드는 위 **Prerequisites** 섹션의 "상세 설치 가이드"를 참조하세요.
