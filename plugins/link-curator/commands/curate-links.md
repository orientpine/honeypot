Orchestrate URL-to-markdown conversion and optional HoneyCombo submission:

## Configuration Options

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| URLs | O | One or more HTTP(S) URLs to process | Inline in `$ARGUMENTS` |
| `output_dir` | O | Directory to save generated md files | `./output/links/` |
| `submit` | - | Include to submit to HoneyCombo after md generation | `submit: true` |
| `dry_run` | - | Preview submission commands without executing | `dry_run: true` |

## Phase 1: Generate Markdown Notes

1. Load the `link-summarizer` skill from this plugin's `skills/` directory.
2. Ask the user for `output_dir` if not provided in `$ARGUMENTS`.
3. Extract all HTTP(S) URLs from `$ARGUMENTS`.
4. Deduplicate URLs. Report `N unique URLs, M duplicates removed`.
5. Fetch each URL in parallel using the strategy in `link-summarizer/references/url-fetch-strategy.md`.
6. Write one Korean summary md file per URL into `output_dir`, following `link-summarizer/references/resource-md-template.md`.
7. Verify all files exist. Report `N/N files written`.

## Phase 2: HoneyCombo Submission (opt-in)

Run when EITHER condition is met:
- `$ARGUMENTS` contains an explicit submission verb: "submit", "제출", "등록", "허니콤보에 올려줘", "HoneyCombo"
- `submit: true` parameter is included in `$ARGUMENTS`

1. Load the `honeycombo-submit` skill from this plugin's `skills/` directory.
2. Check `gh auth status`. If not authenticated → stop and tell the user.
3. Exclude any URL marked non-submittable (paywall, 404, fetch-failed).
4. For each submittable URL, derive Type, Tags (English), and Summary (Korean structured).
5. Submit based on URL count:
   - **1-5 URLs**: Single submit — one `📎 Submit Link` Issue per URL via `submit_single.sh`.
   - **6-20 URLs**: Bulk submit — one `📦 Bulk Submit` Issue via `submit_bulk.sh`.
   - **>20 URLs**: Split into batches of ≤20. Each batch gets a separate bulk Issue titled `📦 Bulk Submit (1/N)`, `📦 Bulk Submit (2/N)`, etc.
   - If `dry_run: true`, pass `--dry-run` flag to scripts.
6. Collect Issue URLs and report back.

See `honeycombo-submit/references/honeycombo-submission.md` for the full submission protocol.
