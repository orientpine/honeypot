# Windows Bash 명령어 실행 규칙 (CRITICAL)

> **언제 읽나요**: 이 프로젝트에서 Bash/터미널 명령(특히 `git`, `python`, `npm`)을 실행할 때.
> **상위 문서**: [AGENTS.md](../../AGENTS.md)

> **배경**: 이 프로젝트의 개발 환경은 Windows (cmd.exe / PowerShell)입니다. Bash 도구(터미널)로 명령을 실행할 때 Unix 전용 `export` 구문을 사용하면 **모든 명령이 실패**합니다. 모델이 git 명령에 환경변수 프리픽스를 자동 생성하는 패턴이 고착되어 있으므로, 아래 규칙을 **반드시** 준수해야 합니다.

**셸 환경**: `C:\WINDOWS\system32\cmd.exe` (PowerShell에서 opencode 실행 시에도 Bash 도구는 cmd.exe 사용)

## 절대 금지

```
# NEVER — Unix 전용 구문, Windows에서 즉시 실패
export CI=true GIT_TERMINAL_PROMPT=0; git status
export VAR=value; any-command
```

## 올바른 사용법

```
# CORRECT — 명령어만 직접 실행 (환경변수 프리픽스 없이)
git status
git add -A
git commit -m "message"
git push
git log --oneline -5
```

## 환경변수가 필요한 경우 (Windows 구문)

```
# cmd.exe에서 환경변수 설정 시
set GIT_TERMINAL_PROMPT=0 & git status

# PowerShell에서 환경변수 설정 시
$env:GIT_TERMINAL_PROMPT=0; git status
```

## 플랫폼 차이 요약

| 항목 | Unix/macOS (bash) | Windows (cmd.exe) |
|------|-------------------|-------------------|
| 환경변수 설정 | `export VAR=value` | `set VAR=value` |
| 명령 구분자 | `;` | `&` 또는 `&&` |
| 환경변수 참조 | `$VAR` | `%VAR%` |
| 올바른 git 실행 | `export GIT_TERMINAL_PROMPT=0; git status` | `git status` (프리픽스 불필요) |

**핵심 원칙**: Windows에서는 `git`, `python`, `npm` 등 명령어를 **프리픽스 없이 직접 실행**하세요. `export`는 절대 사용하지 마세요.
