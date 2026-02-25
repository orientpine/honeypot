---
name: patent-mcp-setup
description: "KIPRIS 특허 MCP 서버 설치 및 설정. Use when: (1) 처음 patent-trend-analyzer 플러그인을 사용할 때, (2) KIPRIS API 키를 설정하거나 변경할 때, (3) MCP 서버 연결 문제를 해결할 때, (4) 'patent setup', 'kipris setup', 'MCP 설정' 등의 요청 시."
---

# patent-mcp-setup

KIPRIS 특허 MCP 서버를 설치하고 Claude Code에 연결하는 스킬입니다.

MCP 서버 소스는 이 스킬 디렉터리의 `scripts/src/mcp_kipris/` 에 위치합니다.

---

## Prerequisites

- Python 3.11 이상
- KIPRIS API 키: [data.go.kr](https://www.data.go.kr) 에서 "KIPRIS 특허정보검색서비스" 신청 후 발급

---

## Installation

```bash
pip install -e ${SKILL_DIR}/scripts/
```

`${SKILL_DIR}` 은 이 스킬의 절대 경로입니다. 예:

```bash
pip install -e /path/to/skills/patent-mcp-setup/scripts/
```

---

## Configuration for Claude Code

`~/.claude/settings.json` 의 `mcpServers` 섹션에 아래 항목을 추가합니다.

```json
{
  "mcpServers": {
    "kipris": {
      "command": "python",
      "args": ["-m", "mcp_kipris.server"],
      "env": {
        "KIPRIS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

설정 후 Claude Code를 재시작하면 MCP 서버가 자동으로 연결됩니다.

---

## Verification

아래 명령으로 18개 도구가 정상 등록됐는지 확인합니다.

```bash
KIPRIS_API_KEY=your_key python -c "
from mcp_kipris.kipris._registry import get_all_tools
tools = get_all_tools()
print(f'{len(tools)} tools registered')
"
```

정상 출력: `18 tools registered`

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

1. Python 버전 확인: `python --version` (3.11 이상 필요)
2. 패키지 설치 확인: `pip show mcp-kipris`
3. API 키 환경변수 확인: `echo $KIPRIS_API_KEY`
4. 직접 실행 테스트: `KIPRIS_API_KEY=your_key python -m mcp_kipris.server`

### API 인증 오류 (401/403)

- data.go.kr에서 서비스 신청 상태 확인 (승인까지 1-2일 소요)
- accessKey(구) vs ServiceKey(신) 구분: 현재 `KIPRIS_API_KEY` 환경변수는 두 방식 모두 지원

### 도구 수가 18개 미만일 때

```bash
pip install -e ${SKILL_DIR}/scripts/ --force-reinstall
```

후 Claude Code 재시작
