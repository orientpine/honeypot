---
name: link-summarizer
description: "Fetch URLs and generate structured Korean markdown summary notes. Use WHENEVER the user provides one or more URLs — including bare URL lists with minimal instruction like '이 링크들 정리해줘', '아래 url 정리', 'md로 저장해줘' — or any message whose primary content is HTTP(S) URLs. Also triggers on requests containing 'Resource에 넣어줘', '기사 정리', or similar content curation phrases. This skill handles ONLY note generation, not HoneyCombo submission."
---

# Link Summarizer

Fetch URLs and convert them into structured Korean markdown summary notes.

## Invocation triggers

Treat ANY of these as invocation:
- A message that is mostly HTTP(S) URLs (even one line, even without other instructions).
- Explicit phrases: "정리해줘", "md로 저장", "요약해줘", "노트로 만들어줘".
- A follow-up message where the prior turn was about curating URLs.

This skill generates MD notes only. For HoneyCombo submission, see the `honeycombo-submit` skill.

## Workflow

### Phase 0: Confirm save location (ALWAYS ASK)

- **No default path.** Always ask the user where to save before proceeding:

  > "저장 위치를 알려주세요. (예: `./output/links/`)"

- If the user's message **explicitly names a save path** (e.g. "output/links에 저장해줘"), use that path without asking.
- Do NOT infer a subfolder from URL content or topic hints. Only use a subfolder when the user typed the path.
- Never invent a new folder on your own.

Wait for the user's answer before proceeding.

### Phase 1: Fetch each URL in parallel

Classify by host, then fetch. Fire all fetches as **parallel** tool calls in one message — never serialize.

| Source | Primary fetch | Fallback |
|---|---|---|
| news.hada.io / Wikipedia / blog / docs | `webfetch` | web search |
| youtube.com / youtu.be | `webfetch` (title) + web search (description/chapters) | - |
| x.com / twitter.com | web search | placeholder note |
| threads.com / threads.net | `webfetch` (or web crawl) | web search |
| paywalled / 403 / 404 / private | — | placeholder + mark **non-submittable** |

See [references/url-fetch-strategy.md](references/url-fetch-strategy.md) for per-source tactics and failure handling.

Dedupe the input URL list first. Report `N unique URLs, M duplicates removed` in the final report.

### Phase 2: Write one md file per URL

- Filename: Korean title-based, sanitized. Strip `/`, `\`, `:`, `?`, `*`, `"`, `<`, `>`, `|`. Collapse whitespace. Max 120 chars. Append ` (2)`, ` (3)` on collisions.
- Path: `{save_path}/{sanitized_title}.md`.
- YAML frontmatter fields (exact order): `source_url`, `created`, `modified`, `title`, `tags`, `summary`.
  - `created`/`modified`: current local time in ISO-8601 format (`YYYY-MM-DDTHH:MM:SS`, no timezone). Both equal on creation.
  - `tags` and `summary` may be left empty (matches existing convention).
  - Quote `title` if it contains YAML-sensitive characters (`:`, `#`, `-` at start, leading/trailing space).
- Body MUST start with `# {title}` then a `> 출처: {source_url}` blockquote, then `## 개요`.
- After `## 개요`, use **flexible topic-appropriate `##` sections** — do NOT force `## 핵심 내용`. Pick from `## 배경`, `## 핵심 기능`, `## 핵심 논지`, `## 기술 스택`, `## 예시`, `## 시사점`, `## 참고` etc., matching the content.
- When fetch fails (placeholder case): skip `## 개요` ambition; just write `# {title}` + `> 출처:` + a short `## 참고` section that states what happened. Do NOT invent content.

Full spec with examples: [references/resource-md-template.md](references/resource-md-template.md).

Strip personal context (project names, internal jargon). Never speculate — if content is missing, write a placeholder and flag the URL in the final report as non-submittable.

### Phase 3: Verify

After all writes, run a single Glob/ls to confirm every expected file exists. Report counts: `N/N files written`.

## Hard rules

- **Never modify existing files** unless the user explicitly asks. Only create new ones.
- **Never fabricate content.** If fetch fails, write a short placeholder and mark the URL non-submittable.
- **Korean body, English terms OK.** Body is Korean. Technical terms may use English in parentheses (`Skills(스킬)`).
- **No speculation.** Never write `~인 것 같다` or `아마도`. If content is missing, say so.

## Report template

```
📝 Summary 노트: N/N 작성 완료  (고유 URL N개, 중복 M개 제거)
  - {path1}
  - {path2}
  ...
⚠️ 보충 필요: {url, 이유}  (생략 가능)
```
