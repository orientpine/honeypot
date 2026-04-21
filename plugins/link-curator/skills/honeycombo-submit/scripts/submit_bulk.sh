#!/usr/bin/env bash
# HoneyCombo bulk-submit wrapper. Up to 20 entries per Issue.
#
# Usage: submit_bulk.sh [--dry-run] <TSV_FILE> [TITLE_SUFFIX]
#   --dry-run    Print the gh command without executing
#   TSV_FILE     Tab-separated file, one entry per line.
#
# Two column formats are accepted (auto-detected per line by TAB count):
#
#   v1 (legacy, 4 columns):
#     URL<TAB>TYPE<TAB>TAGS<TAB>SUMMARY
#
#   v2 (with explicit title, 5 columns) -- preferred for weak-metadata URLs:
#     URL<TAB>TYPE<TAB>TITLE<TAB>TAGS<TAB>SUMMARY
#
#     TYPE    - Article | YouTube | X Thread | Threads | Other
#     TITLE   - OPTIONAL short Korean/English title (<= 200 chars, must not
#               contain '|', tab, CR, or LF). Present only in 5-column rows.
#     TAGS    - Comma+space separated, 1-5 English tags
#     SUMMARY - Korean single-line summary, <= 500 chars. Must not contain
#               '|', tab, CR, or LF (these would collide with the Issue body
#               delimiter that HoneyCombo's server-side parser splits on).
#
# The '### Link List' header and the ' | ' (space-pipe-space) row delimiter
# are parsed LITERALLY by HoneyCombo automation. Do not edit.

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

# Normalize line endings (CRLF -> LF) and ensure trailing newline.
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

# Reject any pipe/tab/CR/LF in a field. The server parser splits the body
# on '|' so any literal pipe inside a TITLE/SUMMARY field would break column
# alignment, and tab/CR/LF would break the single-line row layout.
has_forbidden_char() {
  local value="$1"
  if [[ "$value" == *'|'* ]] || [[ "$value" == *$'\t'* ]] \
     || [[ "$value" == *$'\r'* ]] || [[ "$value" == *$'\n'* ]]; then
    return 0
  fi
  return 1
}

BODY_LINES=""
VALID_COUNT=0
LINE_NO=0

# IMPORTANT: Read the raw line first and split into an array so we can
# distinguish 4-column from 5-column rows. Using `read -r URL TYPE TAGS SUMMARY`
# directly would silently fold a 5th column into SUMMARY.
while IFS= read -r raw_line || [ -n "$raw_line" ]; do
  LINE_NO=$((LINE_NO + 1))

  # Skip blank lines.
  [[ -z "${raw_line//[[:space:]]/}" ]] && continue

  IFS=$'\t' read -r -a COLS <<< "$raw_line"
  NUM_COLS=${#COLS[@]}

  case "$NUM_COLS" in
    4)
      URL="${COLS[0]}"
      TYPE="${COLS[1]}"
      TITLE=""
      TAGS="${COLS[2]}"
      SUMMARY="${COLS[3]}"
      ;;
    5)
      URL="${COLS[0]}"
      TYPE="${COLS[1]}"
      TITLE="${COLS[2]}"
      TAGS="${COLS[3]}"
      SUMMARY="${COLS[4]}"
      ;;
    *)
      echo "ERROR: Line $LINE_NO has $NUM_COLS tab-separated fields; expected 4 (URL|TYPE|TAGS|SUMMARY) or 5 (URL|TYPE|TITLE|TAGS|SUMMARY)." >&2
      exit 2
      ;;
  esac

  # Required fields
  if [ -z "${URL:-}" ] || [ -z "${TYPE:-}" ] || [ -z "${TAGS:-}" ] || [ -z "${SUMMARY:-}" ]; then
    echo "ERROR: Line $LINE_NO has empty required field (URL/TYPE/TAGS/SUMMARY)." >&2
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

  # Validate optional TITLE (5-column rows only)
  if [ -n "$TITLE" ]; then
    if has_forbidden_char "$TITLE"; then
      echo "ERROR: Line $LINE_NO title contains forbidden character (|, tab, CR, or LF) for URL '$URL'" >&2
      echo "       Server parser splits Issue body on ' | '; pipes inside fields break column alignment." >&2
      exit 2
    fi
    if [ "${#TITLE}" -gt 200 ]; then
      echo "ERROR: Line $LINE_NO title exceeds 200 chars for URL '$URL'" >&2
      exit 2
    fi
  fi

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

  # Validate individual tags are non-empty
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

  # Validate SUMMARY (Korean single-line, <=500 chars, no pipe/tab/CR/LF)
  if [ "${#SUMMARY}" -gt 500 ]; then
    echo "ERROR: Line $LINE_NO summary exceeds 500 chars (URL: $URL)" >&2
    exit 2
  fi

  if has_forbidden_char "$SUMMARY"; then
    echo "ERROR: Line $LINE_NO summary contains forbidden character (|, tab, CR, or LF) for URL '$URL'" >&2
    echo "       Server parser splits Issue body on ' | '; pipes inside fields break column alignment." >&2
    exit 2
  fi

  # Validate SUMMARY contains Korean characters (must be Korean)
  if ! echo "$SUMMARY" | grep -qP '[\x{AC00}-\x{D7AF}]' 2>/dev/null; then
    echo "ERROR: Line $LINE_NO summary must contain Korean text (URL: $URL)" >&2
    exit 2
  fi

  # Emit the Issue body row in the matching format (4 or 5 pipe-separated fields).
  if [ -n "$TITLE" ]; then
    LINE="$URL | $TYPE | $TITLE | $TAGS | $SUMMARY"
  else
    LINE="$URL | $TYPE | $TAGS | $SUMMARY"
  fi

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

TITLE_FIELD="📦 Bulk Submit"
if [ -n "$TITLE_SUFFIX" ]; then
  TITLE_FIELD="$TITLE_FIELD $TITLE_SUFFIX"
fi

if [ "$DRY_RUN" = true ]; then
  echo "=== DRY RUN ==="
  echo "gh issue create \\"
  echo "  --repo orientpine/honeycombo \\"
  echo "  --title \"$TITLE_FIELD\" \\"
  echo "  --body \"<body: ${#BODY} chars, $VALID_COUNT entries>\""
  echo ""
  echo "--- Body Preview ---"
  echo "$BODY"
  exit 0
fi

gh issue create \
  --repo orientpine/honeycombo \
  --title "$TITLE_FIELD" \
  --body "$BODY"
