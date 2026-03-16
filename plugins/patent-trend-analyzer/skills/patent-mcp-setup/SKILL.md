---
name: patent-mcp-setup
description: "KIPRIS 특허 MCP 서버 설치 및 설정. Use when: (1) 처음 patent-trend-analyzer 플러그인을 사용할 때, (2) KIPRIS API 키를 설정하거나 변경할 때, (3) MCP 서버 연결 문제를 해결할 때, (4) 'patent setup', 'kipris setup', 'MCP 설정' 등의 요청 시."
---

# patent-mcp-setup

KIPRIS 특허 MCP 서버를 설치하고 Claude Code / OpenCode에 연결하는 스킬입니다.

MCP 서버 소스는 이 스킬 디렉터리의 `scripts/src/mcp_kipris/` 에 위치합니다.

---

## Workflow

이 스킬이 로드되면 아래 워크플로우를 **순서대로** 실행합니다.

### Step 0. API 키 확인

사용자가 API 키를 제공했는지 확인합니다.

- **API 키가 있는 경우** → Step 1로 진행
- **API 키가 없는 경우** → 아래 발급 안내를 사용자에게 보여주고, API 키를 받을 때까지 대기

#### KIPRIS Open API 키 발급 안내

사용자에게 아래 내용을 안내합니다:

> **KIPRIS Open API 키가 필요합니다.**
>
> [KIPRIS Plus 포털](https://plus.kipris.or.kr/portal/main.do)에서 아래 5단계를 따라 발급받으세요.
>
> | 단계 | 작업 | 상세 |
> |:----:|------|------|
> | **1** | 회원 가입 | 개인 또는 단체로 가입 |
> | **2** | 서비스 조회 | Open API 메뉴 → 데이터 상품 조회 → 상품 선택 |
> | **3** | 구매 신청 | 장바구니에서 이용 조건 입력. 관리자 승인 대기 |
> | **4** | 수수료 결제 | 마이페이지에서 결제 (계좌이체/신용카드) |
> | **5** | 인증키 확인 | 마이 페이지 > **APIKEY 관리**에서 인증키 복사 |
>
> 승인까지 1~2 영업일이 소요됩니다. 발급 후 API 키를 알려주세요.

### Step 1. 환경 확인

아래 명령을 실행하여 환경을 파악합니다.

```bash
python3 --version    # Python 3.11 이상 필요
which uv             # uv 패키지 매니저 확인
which pip3           # pip 폴백 확인
```

- `python3` 이 없으면 → 사용자에게 Python 3.11+ 설치를 안내하고 중단
- `uv` 가 있으면 → uv 기반 설치 (권장)
- `uv` 가 없으면 → pip3 기반 설치 (폴백)

### Step 2. 패키지 설치

#### 스크립트 참조 및 실행 (CRITICAL)

MCP 서버 패키지 소스는 이 스킬의 상대경로에 위치합니다:

```
scripts/
```

**Step 2-1. 상대경로로 찾기** (최우선)
스킬이 로드된 컨텍스트에서 상대경로 `scripts/` 디렉터리를 직접 참조합니다.

**Step 2-2. 상대경로 실패 시 Glob 폴백**
```
**/patent-trend-analyzer/skills/patent-mcp-setup/scripts/
```

**Step 2-3. Glob도 실패 시 확장 탐색**
```
**/patent-mcp-setup/scripts/pyproject.toml
```

**절대 금지**: 스크립트 경로를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요. 에러를 보고하고 사용자에게 경로 확인을 요청하세요.

#### uv 기반 설치 (권장)

```bash
# venv 생성
uv venv ~/.kipris-mcp-venv --python 3.12

# 패키지 설치 (uv pip + --python 플래그)
uv pip install -e {SCRIPTS_DIR}/ --python ~/.kipris-mcp-venv/bin/python3
```

`{SCRIPTS_DIR}` 은 Step 2-1~2-3에서 찾은 `scripts/` 디렉터리의 절대경로입니다.

#### pip3 폴백 (uv 없는 경우)

```bash
# venv 생성
python3 -m venv ~/.kipris-mcp-venv

# 패키지 설치
~/.kipris-mcp-venv/bin/pip install -e {SCRIPTS_DIR}/
```

> **주의**: 시스템 Python에 직접 `pip install` 하면 `externally-managed-environment` 오류가 발생합니다. 반드시 venv를 사용하세요.

### Step 3. 설정 파일 등록

Claude Code와 OpenCode **모두** 설정합니다. 설정 파일이 존재하는 클라이언트만 설정합니다.

#### 3-A. Claude Code (`~/.claude/settings.json`)

`~/.claude/settings.json` 파일을 읽고, `mcpServers` 섹션에 `kipris` 항목을 추가합니다.

```json
{
  "mcpServers": {
    "kipris": {
      "command": "~/.kipris-mcp-venv/bin/python3 의 절대경로",
      "args": ["-m", "mcp_kipris.server"],
      "env": {
        "KIPRIS_API_KEY": "사용자가_제공한_API_키"
      }
    }
  }
}
```

**필수 사항:**
- `command` 값은 venv의 python3 **절대경로** (예: `/home/user/.kipris-mcp-venv/bin/python3`)
- 기존 설정이 있으면 `mcpServers` 키만 추가/업데이트 (다른 설정 유지)
- `kipris` 항목이 이미 있으면 덮어쓰기

#### 3-B. OpenCode (`~/.config/opencode/opencode.json`)

> **CRITICAL**: OpenCode는 Claude Code와 설정 형식이 **완전히 다릅니다**.

| 항목 | Claude Code | OpenCode |
|------|-------------|----------|
| 루트 키 | `"mcpServers"` | **`"mcp"`** |
| 명령어 구조 | `"command"` + `"args"` 분리 | **`"command": [...]`** 단일 배열 |
| 환경변수 키 | `"env"` | **`"environment"`** |
| 타입 지정 | 불필요 | **`"type": "local"` 필수** |

`~/.config/opencode/opencode.json` 파일을 읽고, `mcp` 섹션에 `kipris` 항목을 추가합니다.

```json
{
  "mcp": {
    "kipris": {
      "type": "local",
      "command": ["~/.kipris-mcp-venv/bin/python3 의 절대경로", "-m", "mcp_kipris.server"],
      "enabled": true,
      "environment": {
        "KIPRIS_API_KEY": "사용자가_제공한_API_키"
      }
    }
  }
}
```

**필수 사항:**
- `command` 는 **배열** (실행 파일 + 인자를 하나의 배열로)
- `"type": "local"` 과 `"enabled": true` 필수
- 환경변수는 `"environment"` (NOT `"env"`)
- 기존 설정이 있으면 `mcp` 키만 추가/업데이트 (다른 설정 유지)

### Step 4. 설치 확인

```bash
KIPRIS_API_KEY={사용자_API_키} ~/.kipris-mcp-venv/bin/python3 -c "
from mcp_kipris.kipris._registry import get_all_tools
tools = get_all_tools()
print(f'{len(tools)} tools registered')
"
```

- `18 tools registered` 출력 시 → 성공. 사용자에게 클라이언트 재시작을 안내
- 18 미만 또는 오류 → Troubleshooting 참조

### Step 5. 완료 안내

사용자에게 아래를 안내합니다:

> 설정이 완료되었습니다.
>
> - **패키지**: `~/.kipris-mcp-venv` 에 설치됨
> - **MCP 도구**: 18개 (한국 특허 8 + 해외 특허 7 + 전처리 3)
> - **설정된 클라이언트**: {설정한 클라이언트 목록}
>
> 클라이언트(Claude Code / OpenCode)를 **재시작**하면 특허 검색 도구가 활성화됩니다.

---

## Available Tools (18개)

| 분류 | 도구 이름 | 설명 |
|------|-----------|------|
| **한국 특허 (8)** | `patent_free_search` | 자유 키워드 한국 특허 검색 |
| | `patent_applicant_search` | 출원인 기반 한국 특허 검색 |
| | `patent_application_number_search` | 출원번호 기반 한국 특허 검색 |
| | `patent_search` | 통합 한국 특허 검색 |
| | `patent_detail_search` | 한국 특허 상세 정보 조회 |
| | `patent_summary_search` | 한국 특허 요약 검색 |
| | `patent_righter_search` | 권리자 기반 한국 특허 검색 |
| | `patent_batch_export` | 한국 특허 배치 내보내기 (Excel) |
| **해외 특허 (7)** | `foreign_patent_free_search` | 자유 키워드 해외 특허 검색 |
| | `foreign_patent_applicant_search` | 출원인 기반 해외 특허 검색 |
| | `foreign_patent_application_number_search` | 출원번호 기반 해외 특허 검색 |
| | `foreign_international_application_number_search` | 국제출원번호 기반 해외 특허 검색 |
| | `foreign_international_open_number_search` | 국제공개번호 기반 해외 특허 검색 |
| | `foreign_patent_batch_export` | 해외 특허 배치 내보내기 (Excel) |
| | `foreign_patent_ipc_batch_export` | IPC 코드 기반 해외 특허 배치 내보내기 |
| **전처리 (3)** | `patent_result_deduplicator` | 특허 검색 결과 중복 제거 |
| | `patent_search_planner` | 검색 전략 수립 도우미 |
| | `patent_keyword_optimizer` | 키워드 최적화 도우미 |

---

## Troubleshooting

### MCP 서버가 연결되지 않을 때

1. Python 버전 확인: `python3 --version` (3.11 이상 필요)
2. venv 확인: `ls ~/.kipris-mcp-venv/bin/python3`
3. 패키지 설치 확인: `~/.kipris-mcp-venv/bin/pip show mcp-kipris`
4. API 키 확인: 설정 파일에서 `KIPRIS_API_KEY` 값 확인
5. 직접 실행 테스트: `KIPRIS_API_KEY=your_key ~/.kipris-mcp-venv/bin/python3 -m mcp_kipris.server`

### API 인증 오류 (401/403)

- KIPRIS Plus에서 서비스 신청 승인 상태 확인 (승인까지 1~2일 소요)
- API 키에 특수문자(`/`, `=`, `+`)가 포함된 경우 따옴표로 감싸져 있는지 확인

### 도구 수가 18개 미만일 때

```bash
uv pip install -e {SCRIPTS_DIR}/ --python ~/.kipris-mcp-venv/bin/python3 --force-reinstall
```

이후 클라이언트 재시작.

### externally-managed-environment 오류

시스템 Python에 직접 설치하려 할 때 발생합니다. 반드시 venv를 사용하세요 (Step 2 참조).
