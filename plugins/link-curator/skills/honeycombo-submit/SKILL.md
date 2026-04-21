---
name: honeycombo-submit
description: "Submit URLs to HoneyCombo via gh CLI with Korean structured summaries. Use when the user explicitly requests HoneyCombo submission — phrases like '허니콤보에 올려줘', 'submit to honeycombo', '제출해줘', '등록까지 해줘'. Handles single submit (1-5 URLs, one Issue per URL) and bulk submit (6-20 URLs, one Issue). Requires gh CLI authentication."
---

# HoneyCombo Submit

Submit URLs to HoneyCombo (`orientpine/honeycombo`) via GitHub Issues using `gh` CLI.

## When to use

ONLY when the user explicitly requests HoneyCombo submission. Never auto-submit — the `link-summarizer` skill handles MD generation separately.

Trigger phrases: "허니콤보에 올려줘", "submit to honeycombo", "제출해줘", "등록까지 해줘", "HoneyCombo에 등록".

## Workflow

### Step 1: Pre-check

1. `gh auth status`. If not authenticated → stop and tell the user to run `gh auth login`.
2. Identify submittable URLs. Exclude any URL marked non-submittable (paywall, 403/404, fetch-failed placeholder). Report exclusions.

### Step 2: Derive metadata per URL

For each submittable URL, derive:

- **Type**: `Article` (default) | `YouTube` | `X Thread` | `Threads` | `Other`. See [references/honeycombo-submission.md](references/honeycombo-submission.md) for URL-pattern mapping.
- **Title** (optional but RECOMMENDED for bulk): short Korean/English title (<=200 chars, no `|`, tab, CR, or LF). For URLs with weak metadata (e.g., YouTube channel pages), providing an explicit title prevents the server from falling back to using the summary as both title and description. Skip for single submit — single-submit body does not carry a title field.
- **Tags**: 1-5 English tags, comma+space separated. Extract from md content. No Korean.
- **Summary**: Korean structured summary (≤5000 chars for single, ≤500 chars for bulk) with `## 개요`, `## 주요 내용`, `## 시사점` sections.

### Step 3: Submit

- **1-5 URLs → single submit, ONE Issue per URL.** Write summary to a temp file, then call `scripts/submit_single.sh`.
- **6-20 URLs → one bulk Issue.** Write a TSV with single-line Korean summaries, then call `scripts/submit_bulk.sh`.
  - TSV 포맷: 4컬럼 `URL<TAB>TYPE<TAB>TAGS<TAB>SUMMARY` (legacy) 또는 5컬럼 `URL<TAB>TYPE<TAB>TITLE<TAB>TAGS<TAB>SUMMARY` (권장). 각 줄마다 자율 선택—스크립트가 탭 개수로 자동 감지한다.
  - YouTube 채널·약한 metadata URL의 title≐description 중복을 방지하려면 5컬럼 사용 필수.
  - TITLE/SUMMARY 필드에 `|`, 탭, CR/LF 문자 금지 (서버 파서가 행을 드롭).
- **>20 URLs → split into ≤20-entry bulk Issues** (`📦 Bulk Submit (1/N)`, `(2/N)`, ...).
- Add `--dry-run` flag to preview commands without executing.

### Step 4: Report

Collect every Issue URL and report back using the format in [references/honeycombo-submission.md](references/honeycombo-submission.md).

## Script Reference and Execution (CRITICAL)

Scripts are located at the relative path within this skill:

```
scripts/submit_single.sh
scripts/submit_bulk.sh
```

**Execution order:**

**Step 1. Relative path** (preferred)
Reference `scripts/submit_single.sh` and `scripts/submit_bulk.sh` directly from the skill's loaded context.

**Step 2. Glob fallback if relative path fails**
```
**/link-curator/skills/honeycombo-submit/scripts/submit_single.sh
**/link-curator/skills/honeycombo-submit/scripts/submit_bulk.sh
```

**Step 3. Extended search if Glob also fails**
```
**/submit_single.sh
**/submit_bulk.sh
```

**Never**: Write your own submission scripts. Report the error and ask the user for the path.

## Hard rules

- **Never submit without explicit user request.** Default is MD generation only.
- **Tags must be English.** Summary must be Korean.
- **Preserve exact gh issue body headers** — HoneyCombo's automation parses them literally.
- **Single submit = one Issue per URL.** Never jam multiple URLs into one `📎 Submit Link` Issue.

## Report template

```
🍯 HoneyCombo 제출 완료
  - 모드: single (N Issues) | bulk
  - Issues:
    - {issue_url_1}
    - {issue_url_2}
  - 제외된 URL: {url, 이유}  (해당 시)
  - 처리 상태: Issue에 자동 댓글로 업데이트됨 (검증 → PR → merge)
```
