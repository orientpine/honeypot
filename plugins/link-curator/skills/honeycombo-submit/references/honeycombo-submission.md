# HoneyCombo 제출 프로토콜

`orientpine/honeycombo` 레포에 GitHub Issue로 URL을 제출하는 절차. 헤더 형식이 **자동화 파서**에 의해 리터럴 파싱되므로 한 글자도 어긋나면 안 된다.

## 목차

1. [사전 조건](#사전-조건)
2. [Type 매핑](#type-매핑)
3. [메타데이터 생성 규칙](#메타데이터-생성-규칙)
4. [단건 제출 (1-5개)](#단건-제출-1-5개)
5. [대량 제출 (6-20개)](#대량-제출-6-20개)
6. [20개 초과](#20개-초과)
7. [Dry Run](#dry-run)
8. [에러 대응](#에러-대응)

---

## 사전 조건

```bash
gh auth status
```

- 실패 시: 사용자에게 `gh auth login` 실행을 요청하고 중단한다. 직접 로그인을 시도하지 말 것.
- 레포 권한: `orientpine/honeycombo`에 issue 생성 권한 필요 (public repo면 기본 허용).

---

## Type 매핑

| URL 패턴 | Type 값 |
|---|---|
| `youtube.com` / `youtu.be` | `YouTube` |
| `x.com` / `twitter.com` | `X Thread` |
| `threads.com` / `threads.net` | `Threads` |
| 그 외 (블로그, 뉴스, 문서, Wikipedia 등) | `Article` |
| 위에 명확히 안 맞는 경우 | `Other` |

대소문자까지 정확히 일치시킬 것 (`Article`, `YouTube`, `X Thread`, `Threads`, `Other`).

---

## 메타데이터 생성 규칙

### Tags

- **영어만.** 최대 5개. 쉼표+공백 구분.
- md 본문과 제목에서 핵심 명사구 추출.
- 소문자 또는 고유명사 규칙 따름 (`AI`, `Claude`, `MCP`, `llm`, `startup`).
- 일반 용어(`tech`, `general`, `article`) 지양. 구체적으로.

예: `AI, Claude, MCP, automation, developer-tools`

### Summary (한국어 구조화 요약)

- **한국어만.** 최대 5000자.
- `## 개요`, `## 주요 내용`, `## 시사점` 3개 섹션으로 구조화.
- 콘텐츠의 핵심을 한국어로 정리. 홍보성 표현 금지.
- 각 섹션은 2-5줄. `## 주요 내용`은 불릿 리스트 권장.

예:
```
## 개요
AI 에이전트를 프로덕션 환경에서 활용하는 실전 분석 기사

## 주요 내용
- 에이전트 아키텍처 설계 패턴
- 프로덕션 배포 시 고려사항
- 장애 복구 및 모니터링 전략

## 시사점
실무에서 바로 적용 가능한 에이전트 구축 가이드
```

### 금지 사항

- Tags에 한국어 혼용 금지
- Summary에 영어만 사용 금지 (반드시 한국어)
- 이모지 금지
- Tags가 영어가 아니면 HoneyCombo 자동 검증에서 거부될 수 있음

---

## 단건 제출 (1-5개)

각 URL마다 **별도 Issue**. 4개 헤더 정확히 준수.

```bash
gh issue create --repo orientpine/honeycombo --title "📎 Submit Link" --body "### URL

https://example.com/article

### Type

Article

### Tags (comma-separated, max 5)

AI, Claude, MCP, automation, developer-tools

### Summary

## 개요
AI 에이전트를 프로덕션 환경에서 활용하는 실전 분석 기사

## 주요 내용
- 에이전트 아키텍처 설계 패턴
- 프로덕션 배포 시 고려사항

## 시사점
실무에서 바로 적용 가능한 에이전트 구축 가이드
"
```

**절대 변경 금지 헤더 4종:**

1. `### URL`
2. `### Type`
3. `### Tags (comma-separated, max 5)`
4. `### Summary`

각 헤더와 값 사이에 빈 줄 1개. 값 뒤에도 빈 줄 1개. `--label` 옵션 불필요.

Summary는 다중 행이므로 파일 기반 입력 권장. 스킬의 `scripts/submit_single.sh` 래퍼 사용:

```bash
# 1. Summary를 파일에 저장
cat > /tmp/summary.md << 'SUMMARY_EOF'
## 개요
AI 에이전트를 프로덕션 환경에서 활용하는 실전 분석 기사

## 주요 내용
- 에이전트 아키텍처 설계 패턴
- 프로덕션 배포 시 고려사항

## 시사점
실무에서 바로 적용 가능한 에이전트 구축 가이드
SUMMARY_EOF

# 2. 스크립트 호출
bash scripts/submit_single.sh \
  "https://example.com/article" \
  "Article" \
  "AI, Claude, MCP, automation, developer-tools" \
  /tmp/summary.md
```

---

## 대량 제출 (6-20개)

단일 Issue에 `### Link List` **하나만** 사용 (단건의 4개 헤더와 다름).

각 줄은 다음 두 포맷 중 하나로 작성한다 (서버는 `|` 개수로 자동 감지):

### v1 (legacy, 4컬럼)

`URL | Type | Tags | 한국어 요약`

### v2 (제목 포함, 5컬럼) — 권장

`URL | Type | 제목 | Tags | 한국어 요약`

YouTube 채널처럼 metadata가 빈약한 URL에서 HoneyCombo 서버가 title을 description과 동일하게 fallback하는 문제를 방지하기 위해 **가능하면 5컬럼을 사용하라**. 제목은 한국어/영어 모두 허용, `<=` 200자.

### 공통 규칙

- 구분자: ` | ` (공백+파이프+공백)
- 쉼표는 Tags 내부에서만 (파이프 구분자와 충돌 주의)
- 제목·요약에 **`|`, 탭, CR/LF 포함 금지** (서버 파서가 컬럼 정렬 실패)
- 한국어 요약은 **단일 행**, ≤500자

```bash
gh issue create --repo orientpine/honeycombo --title "📦 Bulk Submit" --body "### Link List

https://blog.com/post-1 | Article | AI, LLM | AI 에이전트를 프로덕션 환경에서 활용하는 실전 분석 기사
https://blog.com/post-2 | Article | MCP 서버 구축 가이드 | MCP, agents | MCP 서버를 활용한 AI 에이전트 구축 가이드
https://youtube.com/watch?v=abc | YouTube | Claude Code 튜토리얼 | AI, tutorial | Claude Code 개발 환경 설정 튜토리얼 영상
"
```

### 래퍼 스크립트

```bash
bash scripts/submit_bulk.sh /tmp/links.tsv
```

TSV 포맷은 줄 단위로 4컬럼 또는 5컬럼을 혼용할 수 있으며 스크립트가 탭 개수로 자동 감지한다.

- 4컬럼: `URL<TAB>Type<TAB>Tags<TAB>한국어 요약`
- 5컬럼 (권장): `URL<TAB>Type<TAB>제목<TAB>Tags<TAB>한국어 요약`

---

## 20개 초과

20개 단위로 분할하여 여러 번 bulk 제출. 각 Issue 타이틀에 `📦 Bulk Submit (1/N)`, `📦 Bulk Submit (2/N)` 표기.

---

## Dry Run

실행 전 명령어만 확인:

```bash
# 단건
bash scripts/submit_single.sh --dry-run \
  "https://example.com/test" \
  "Article" \
  "AI, test" \
  /tmp/summary.md

# 대량
bash scripts/submit_bulk.sh --dry-run /tmp/links.tsv
```

`--dry-run` 플래그를 첫 번째 인수로 전달하면 실제 `gh issue create` 실행 없이 명령어와 본문을 출력한다.

---

## 에러 대응

### `HTTP 401: Bad credentials`

gh 인증 만료. 사용자에게 `gh auth login` 재실행 요청.

### `HTTP 403` / `HTTP 404`

레포 권한 또는 이름 오타. `orientpine/honeycombo` 철자 확인.

### `Template mismatch` / 자동 라벨 미부여

헤더 형식 오타. 위의 4개 단건 헤더 또는 `### Link List` 대량 헤더를 **글자 그대로** 확인.

### Issue는 생성되었지만 자동 PR 없음

GitHub Actions 로그 확인 필요:

```bash
gh run list --repo orientpine/honeycombo --limit 5
```

### URL 검증 실패 (bulk)

- bulk 제출에서 일부 URL이 실패해도 성공한 항목은 PR에 포함됨
- Issue에 자동 댓글로 실패 목록이 달림
- 사용자에게 "{N}개 중 {M}개 성공, 실패 URL: ..." 형태로 보고

### 중복 URL

HoneyCombo가 자동 거부하고 Issue에 상세 댓글을 남긴다 (동일 Issue 재처리 시에도 댓글이 upsert되므로 중복 생성 없음). 사전에 기존 글 검색 불가능하므로 그냥 제출하고 결과 Issue 댓글을 확인한다.

---

## 최종 보고 형식

제출 완료 후 사용자에게 반환:

```
🍯 HoneyCombo 제출 완료
  - Issue: https://github.com/orientpine/honeycombo/issues/{n}
  - 모드: single | bulk
  - 항목: {N}개
  - 처리 상태: Issue에 자동 댓글로 업데이트됨 (검증 → PR → merge)
```
