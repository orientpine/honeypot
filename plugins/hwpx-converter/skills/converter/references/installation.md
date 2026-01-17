# HWPX Converter 설치 가이드

pypandoc-hwpx를 사용하여 Markdown을 HWPX로 변환하기 위한 설치 가이드입니다.

---

## 필수 의존성

| 프로그램 | 버전 | 용도 |
|----------|------|------|
| Pandoc | 3.0+ | 문서 변환 엔진 |
| Python | 3.6+ | pypandoc-hwpx 실행 환경 |
| pypandoc-hwpx | 최신 | HWPX 변환 도구 |

---

## 1. Pandoc 설치

### Windows

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

### macOS

**Homebrew 사용 (권장)**
```bash
brew install pandoc
```

**MacPorts 사용**
```bash
sudo port install pandoc
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install pandoc
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install pandoc
```

### Linux (Arch)

```bash
sudo pacman -S pandoc
```

---

## 2. Python 설치

### Windows

1. https://python.org/downloads/ 접속
2. 최신 Python 설치 파일 다운로드
3. **"Add Python to PATH" 체크** (중요!)
4. 설치 완료

### macOS

**Homebrew 사용 (권장)**
```bash
brew install python
```

### Linux

대부분의 Linux 배포판에 기본 설치되어 있습니다.
```bash
# 확인
python3 --version

# 미설치 시 (Ubuntu/Debian)
sudo apt install python3 python3-pip
```

---

## 3. pypandoc-hwpx 설치

Python과 pip가 설치된 후:

```bash
pip install pypandoc-hwpx
```

또는 Python 3 명시적 사용:

```bash
python3 -m pip install pypandoc-hwpx
```

---

## 설치 확인

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

---

## 트러블슈팅

### "pandoc: command not found"

**원인:** Pandoc이 PATH에 등록되지 않음

**해결:**
- Windows: 터미널 재시작 또는 시스템 재부팅
- macOS/Linux: 셸 설정 파일 리로드 (`source ~/.bashrc` 또는 `source ~/.zshrc`)

### "pip: command not found"

**원인:** Python pip가 PATH에 없음

**해결:**
```bash
# Python 모듈로 pip 실행
python -m pip install pypandoc-hwpx

# 또는 python3 사용
python3 -m pip install pypandoc-hwpx
```

### "Permission denied" (Linux/macOS)

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

### 변환 시 한글 깨짐

**원인:** 파일 인코딩 문제

**해결:**
- 소스 .md 파일이 UTF-8로 저장되어 있는지 확인
- BOM 없는 UTF-8 권장

---

## 참고 링크

- [Pandoc 공식 문서](https://pandoc.org/)
- [pypandoc-hwpx GitHub](https://github.com/msjang/pypandoc-hwpx)
- [pypandoc-hwpx PyPI](https://pypi.org/project/pypandoc-hwpx/)
