#!/usr/bin/env bash
# HoneyCombo single-submit wrapper.
#
# Usage: submit_single.sh [--dry-run] <URL> <TYPE> <TAGS> <SUMMARY_FILE>
#   --dry-run    Print the gh command without executing
#   URL          Source URL (http:// or https://, single-line)
#   TYPE         One of: Article | YouTube | X Thread | Threads | Other
#   TAGS         Comma+space separated, 1-5 English tags, single-line
#   SUMMARY_FILE Path to a file containing Korean structured summary (≤5000 chars)
#
# The body headers are parsed LITERALLY by HoneyCombo automation. Do not edit them.
# Summary format: Korean structured with ## 개요, ## 주요 내용, ## 시사점

set -euo pipefail

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
  shift
fi

if [ $# -ne 4 ]; then
  echo "Usage: $0 [--dry-run] <URL> <TYPE> <TAGS> <SUMMARY_FILE>" >&2
  exit 2
fi

URL="$1"
TYPE="$2"
TAGS="$3"
SUMMARY_FILE="$4"

# Validate URL
if ! [[ "$URL" =~ ^https?://[^[:space:]]+$ ]]; then
  echo "ERROR: URL must be a single-line http(s):// URL. Got: '$URL'" >&2
  exit 2
fi

# Validate TYPE
case "$TYPE" in
  "Article"|"YouTube"|"X Thread"|"Threads"|"Other") ;;
  *)
    echo "ERROR: Invalid TYPE '$TYPE'. Must be one of: Article | YouTube | X Thread | Threads | Other" >&2
    exit 2
    ;;
esac

# Validate TAGS (single-line, 1-5 comma-separated)
if [[ "$TAGS" == *$'\n'* ]] || [[ "$TAGS" == *$'\r'* ]]; then
  echo "ERROR: TAGS must be single-line." >&2
  exit 2
fi
tag_count=$(awk -F',' '{print NF}' <<<"$TAGS")
if [ "$tag_count" -lt 1 ] || [ "$tag_count" -gt 5 ]; then
  echo "ERROR: TAGS must have 1-5 comma-separated entries. Got $tag_count." >&2
  exit 2
fi

# Validate TAGS are English only (reject Korean characters)
if echo "$TAGS" | grep -qP '[\x{AC00}-\x{D7AF}\x{3131}-\x{3163}\x{1100}-\x{11FF}]' 2>/dev/null; then
  echo "ERROR: TAGS must be English only. Korean characters detected in: '$TAGS'" >&2
  exit 2
fi

# Validate individual tags are non-empty (reject leading/trailing commas, consecutive commas, empty tags)
if [[ "$TAGS" =~ ^, ]] || [[ "$TAGS" =~ ,$ ]] || [[ "$TAGS" =~ ,, ]]; then
  echo "ERROR: TAGS contain empty entries (leading/trailing/consecutive commas). Got: '$TAGS'" >&2
  exit 2
fi
IFS=',' read -ra tag_array <<< "$TAGS"
for i in "${!tag_array[@]}"; do
  trimmed=$(echo "${tag_array[$i]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  if [ -z "$trimmed" ]; then
    echo "ERROR: TAGS contain empty entry at position $((i+1)). Got: '$TAGS'" >&2
    exit 2
  fi
done

# Validate SUMMARY_FILE
if [ ! -f "$SUMMARY_FILE" ]; then
  echo "ERROR: Summary file not found: $SUMMARY_FILE" >&2
  exit 2
fi
if [ ! -r "$SUMMARY_FILE" ]; then
  echo "ERROR: Summary file not readable: $SUMMARY_FILE" >&2
  exit 2
fi

# Read and validate summary content
SUMMARY=$(sed 's/\r$//' "$SUMMARY_FILE")
summary_len=${#SUMMARY}
if [ "$summary_len" -gt 5000 ]; then
  echo "ERROR: Summary exceeds 5000 chars ($summary_len)." >&2
  exit 2
fi
if [ "$summary_len" -lt 1 ]; then
  echo "ERROR: Summary file is empty." >&2
  exit 2
fi

# Validate summary contains Korean characters (must be Korean, not English-only)
if ! echo "$SUMMARY" | grep -qP '[\x{AC00}-\x{D7AF}]' 2>/dev/null; then
  echo "ERROR: Summary must contain Korean text. Only non-Korean characters detected." >&2
  exit 2
fi

# Require Korean structured sections (## 개요, ## 주요 내용, ## 시사점)
missing_sections=""
echo "$SUMMARY" | grep -q '## 개요' || missing_sections="${missing_sections} '## 개요'"
echo "$SUMMARY" | grep -q '## 주요 내용' || missing_sections="${missing_sections} '## 주요 내용'"
echo "$SUMMARY" | grep -q '## 시사점' || missing_sections="${missing_sections} '## 시사점'"
if [ -n "$missing_sections" ]; then
  echo "ERROR: Summary is missing required sections:$missing_sections" >&2
  echo "  Required format: ## 개요 / ## 주요 내용 / ## 시사점" >&2
  exit 2
fi

# Check gh CLI
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install with 'apt install gh' or see https://cli.github.com/" >&2
  exit 3
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh not authenticated. Run 'gh auth login' first." >&2
  exit 4
fi

# Construct body
BODY="### URL

$URL

### Type

$TYPE

### Tags (comma-separated, max 5)

$TAGS

### Summary

$SUMMARY
"

if [ "$DRY_RUN" = true ]; then
  echo "=== DRY RUN ==="
  echo "gh issue create \\"
  echo "  --repo orientpine/honeycombo \\"
  echo "  --title \"📎 Submit Link\" \\"
  echo "  --body \"<body: ${#BODY} chars>\""
  echo ""
  echo "--- Body Preview ---"
  echo "$BODY"
  exit 0
fi

gh issue create \
  --repo orientpine/honeycombo \
  --title "📎 Submit Link" \
  --body "$BODY"
