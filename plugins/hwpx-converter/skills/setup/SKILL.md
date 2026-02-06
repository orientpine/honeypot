---
name: setup
description: "hwpx-converter 사용을 위한 의존성(Pandoc, Python, pypandoc-hwpx)을 자동 설치합니다."
---

# HWPX Converter Setup

hwpx-converter 스킬 사용을 위한 의존성을 자동으로 설치합니다.

---

## 설치 대상

| 프로그램 | 용도 | 설치 방법 |
|----------|------|----------|
| Pandoc | 문서 변환 엔진 | winget (Windows) / brew (macOS) / apt (Linux) |
| Python | 실행 환경 | winget (Windows) / brew (macOS) / apt (Linux) |
| pypandoc-hwpx | HWPX 변환 도구 | pip install |

---

## 워크플로우

### Phase 1: 환경 감지

운영체제를 감지하여 적절한 설치 명령을 선택합니다.

```bash
# Windows 감지
uname -s 2>/dev/null || echo "Windows"
```

### Phase 2: Pandoc 설치 확인 및 설치

**Step 2-1. 설치 확인**
```bash
pandoc --version
```

**Step 2-2. 미설치 시 설치**

Windows (PowerShell):
```powershell
winget install --id JohnMacFarlane.Pandoc --accept-source-agreements --accept-package-agreements
```

macOS:
```bash
brew install pandoc
```

Linux (Ubuntu/Debian):
```bash
sudo apt update && sudo apt install -y pandoc
```

### Phase 3: Python 설치 확인 및 설치

**Step 3-1. 설치 확인**
```bash
python --version || python3 --version
```

**Step 3-2. 미설치 시 설치**

Windows (PowerShell):
```powershell
winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
```

macOS:
```bash
brew install python
```

Linux (Ubuntu/Debian):
```bash
sudo apt update && sudo apt install -y python3 python3-pip
```

### Phase 4: pypandoc-hwpx 설치

```bash
pip install pypandoc-hwpx
# 또는
python -m pip install pypandoc-hwpx
# 또는
python3 -m pip install pypandoc-hwpx
```

### Phase 5: 설치 검증

모든 설치가 완료되면 검증합니다:

```bash
pandoc --version
python --version
pypandoc-hwpx --help
```

**성공 기준:**
- pandoc: 버전 정보 출력
- python: 버전 정보 출력  
- pypandoc-hwpx: 사용법 출력

---

## 에러 처리

| 상황 | 처리 |
|------|------|
| winget 미설치 (Windows) | 수동 설치 링크 제공 |
| brew 미설치 (macOS) | brew 설치 명령 안내 |
| 관리자 권한 필요 | sudo 사용 또는 수동 설치 안내 |
| PATH 미등록 | 터미널 재시작 안내 |

---

## 수동 설치 링크

자동 설치 실패 시:
- **Pandoc**: https://pandoc.org/installing.html
- **Python**: https://python.org/downloads/
- **pypandoc-hwpx**: `pip install pypandoc-hwpx`

---

## 주의사항

- Windows에서 설치 후 **터미널 재시작** 필요 (PATH 반영)
- 일부 시스템에서 **관리자 권한** 필요
- Python 설치 시 **"Add to PATH" 옵션** 체크 권장
