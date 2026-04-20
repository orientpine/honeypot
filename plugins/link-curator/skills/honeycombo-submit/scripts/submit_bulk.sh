#!/usr/bin/env bash
# HoneyCombo bulk-submit wrapper. Up to 20 entries per Issue.
#
# Usage: submit_bulk.sh [--dry-run] <TSV_FILE> [TITLE_SUFFIX]
#   --dry-run    Print the gh command without executing
#   TSV_FILE     Tab-separated file, one entry per line:
#                  URL<TAB>TYPE<TAB>TAGS<TAB>SUMMARY
#
#     TYPE    - Article | YouTube | X Thread | Threads | Other
#     TAGS    - Comma+space separated, 1-5 English tags
#     SUMMARY - Korean single-line summary, ≤500 chars. Must not contain ' | '
#
# The '### Link List' header is parsed LITERALLY by HoneyCombo automation. Do not edit.

set -euo pipefail

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
  shift
fi

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: $0 [--dry-run] <TSV_FILE> [TITLE_SUFFIX]" >&2
  exit 2
fi

TSV_FILE="$1"
TITLE_SUFFIX="${2:-}"

if [ ! -f "$TSV_FILE" ]; then
  echo "ERROR: TSV file not found: $TSV_FILE" >&2
  exit 2
fi

# Check gh CLI
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found." >&2
  exit 3
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh not authenticated. Run 'gh auth login' first." >&2
  exit 4
fi

# Normalize line endings
NORMALIZED=$(mktemp)
trap 'rm -f "$NORMALIZED"' EXIT
sed -e 's/\r$//' "$TSV_FILE" > "$NORMALIZED"
[ -s "$NORMALIZED" ] && [ "$(tail -c1 "$NORMALIZED" | wc -l)" -eq 0 ] && printf '\n' >> "$NORMALIZED"

LINE_COUNT=$(grep -c -v '^[[:space:]]*$' "$NORMALIZED" || true)
if [ "$LINE_COUNT" -eq 0 ]; then
  echo "ERROR: No entries in TSV file." >&2
  exit 2
fi
if [ "$LINE_COUNT" -gt 20 ]; then
  echo "ERROR: Bulk submit supports at most 20 entries per issue. Got $LINE_COUNT." >&2
  echo "Split into multiple TSV files of <=20 lines each." >&2
  exit 2
fi

BODY_LINES=""
VALID_COUNT=0
LINE_NO=0
while IFS=$'\t' read -r URL TYPE TAGS SUMMARY; do
  LINE_NO=$((LINE_NO + 1))
  [ -z "${URL:-}${TYPE:-}${TAGS:-}${SUMMARY:-}" ] && continue

  if [ -z "${URL:-}" ] || [ -z "${TYPE:-}" ] || [ -z "${TAGS:-}" ] || [ -z "${SUMMARY:-}" ]; then
    echo "ERROR: Line $LINE_NO has empty field. Require all 4 TSV columns." >&2
    exit 2
  fi

  # Validate URL
  if ! [[ "$URL" =~ ^https?://[^[:space:]]+$ ]]; then
    echo "ERROR: Line $LINE_NO URL malformed: '$URL'" >&2
    exit 2
  fi

  # Validate TYPE
  case "$TYPE" in
    "Article"|"YouTube"|"X Thread"|"Threads"|"Other") ;;
    *)
      echo "ERROR: Line $LINE_NO invalid TYPE '$TYPE' for URL '$URL'" >&2
      exit 2
      ;;
  esac

  # Validate TAGS (1-5 comma-separated)
  tag_count=$(awk -F',' '{print NF}' <<<"$TAGS")
  if [ "$tag_count" -lt 1 ] || [ "$tag_count" -gt 5 ]; then
    echo "ERROR: Line $LINE_NO tags must be 1-5, got $tag_count (URL: $URL)" >&2
    exit 2
  fi

  # Validate TAGS are English only (reject Korean characters)
  if echo "$TAGS" | grep -qP '[\x{AC00}-\x{D7AF}\x{3131}-\x{3163}\x{1100}-\x{11FF}]' 2>/dev/null; then
    echo "ERROR: Line $LINE_NO tags must be English only. Korean characters detected (URL: $URL)" >&2
    exit 2
  fi

  # Validate individual tags are non-empty (reject leading/trailing commas, consecutive commas)
  if [[ "$TAGS" =~ ^, ]] || [[ "$TAGS" =~ ,$ ]] || [[ "$TAGS" =~ ,, ]]; then
    echo "ERROR: Line $LINE_NO tags contain empty entries (leading/trailing/consecutive commas) (URL: $URL)" >&2
    exit 2
  fi
  IFS=',' read -ra tag_array <<< "$TAGS"
  for ti in "${!tag_array[@]}"; do
    trimmed=$(echo "${tag_array[$ti]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -z "$trimmed" ]; then
      echo "ERROR: Line $LINE_NO tags contain empty entry at position $((ti+1)) (URL: $URL)" >&2
      exit 2
    fi
  done

  # Validate SUMMARY (Korean single-line, ≤500 chars, no ' | ')
  if [ "${#SUMMARY}" -gt 500 ]; then
    echo "ERROR: Line $LINE_NO summary exceeds 500 chars (URL: $URL)" >&2
    exit 2
  fi

  if [[ "$SUMMARY" == *" | "* ]]; then
    echo "ERROR: Line $LINE_NO summary contains ' | ' which collides with bulk delimiter (URL: $URL)" >&2
    exit 2
  fi

  # Validate SUMMARY contains Korean characters (must be Korean)
  if ! echo "$SUMMARY" | grep -qP '[\x{AC00}-\x{D7AF}]' 2>/dev/null; then
    echo "ERROR: Line $LINE_NO summary must contain Korean text (URL: $URL)" >&2
    exit 2
  fi

  LINE="$URL | $TYPE | $TAGS | $SUMMARY"
  if [ -z "$BODY_LINES" ]; then
    BODY_LINES="$LINE"
  else
    BODY_LINES="$BODY_LINES"$'\n'"$LINE"
  fi
  VALID_COUNT=$((VALID_COUNT + 1))
done < "$NORMALIZED"

if [ "$VALID_COUNT" -eq 0 ]; then
  echo "ERROR: No valid entries after parsing." >&2
  exit 2
fi

BODY="### Link List

$BODY_LINES
"

TITLE="📦 Bulk Submit"
if [ -n "$TITLE_SUFFIX" ]; then
  TITLE="$TITLE $TITLE_SUFFIX"
fi

if [ "$DRY_RUN" = true ]; then
  echo "=== DRY RUN ==="
  echo "gh issue create \\"
  echo "  --repo orientpine/honeycombo \\"
  echo "  --title \"$TITLE\" \\"
  echo "  --body \"<body: ${#BODY} chars, $VALID_COUNT entries>\""
  echo ""
  echo "--- Body Preview ---"
  echo "$BODY"
  exit 0
fi

gh issue create \
  --repo orientpine/honeycombo \
  --title "$TITLE" \
  --body "$BODY"
