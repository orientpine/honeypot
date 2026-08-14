#!/bin/bash
# Agent File Validator
# Validates agent markdown files for correct structure and content

set -euo pipefail

# Usage
if [ $# -eq 0 ]; then
  echo "Usage: $0 <path/to/agent.md>"
  echo ""
  echo "Validates agent file for:"
  echo "  - YAML frontmatter structure"
  echo "  - Required fields (name, description)"
  echo "  - Optional field values (model, effort, tools, color)"
  echo "  - Unknown / unsupported frontmatter fields"
  echo "  - Field formats and constraints"
  echo "  - System prompt presence and length"
  echo "  - Example blocks in description"
  exit 1
fi

AGENT_FILE="$1"

echo "🔍 Validating agent file: $AGENT_FILE"
echo ""

# Check 1: File exists
if [ ! -f "$AGENT_FILE" ]; then
  echo "❌ File not found: $AGENT_FILE"
  exit 1
fi
echo "✅ File exists"

# Check 2: Starts with ---
FIRST_LINE=$(head -1 "$AGENT_FILE")
if [ "$FIRST_LINE" != "---" ]; then
  echo "❌ File must start with YAML frontmatter (---)"
  exit 1
fi
echo "✅ Starts with frontmatter"

# Check 3: Has closing ---
# NOTE: `cmd | grep -q` is unsafe under `set -o pipefail` — grep -q exits on the first
# match and the upstream writer dies with SIGPIPE (141), which pipefail reports as a
# pipeline failure. That made large agent files spuriously fail. Feed grep via a
# here-string instead so no pipeline is involved.
if ! grep -q '^---$' <<< "$(tail -n +2 "$AGENT_FILE")"; then
  echo "❌ Frontmatter not closed (missing second ---)"
  exit 1
fi
echo "✅ Frontmatter properly closed"

# Extract frontmatter and system prompt
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$AGENT_FILE")
SYSTEM_PROMPT=$(awk '/^---$/{i++; next} i>=2' "$AGENT_FILE")

# Check 4: Required fields
echo ""
echo "Checking required fields..."

error_count=0
warning_count=0

# Check name field
NAME=$(echo "$FRONTMATTER" | grep '^name:' | sed 's/name: *//' | sed 's/^"\(.*\)"$/\1/' || true)

if [ -z "$NAME" ]; then
  echo "❌ Missing required field: name"
  error_count=$((error_count + 1))
else
  echo "✅ name: $NAME"

  # Validate name format
  if ! [[ "$NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$ ]]; then
    echo "❌ name must start/end with alphanumeric and contain only letters, numbers, hyphens"
    error_count=$((error_count + 1))
  fi

  # Validate name length
  name_length=${#NAME}
  if [ $name_length -lt 3 ]; then
    echo "❌ name too short (minimum 3 characters)"
    error_count=$((error_count + 1))
  elif [ $name_length -gt 50 ]; then
    echo "❌ name too long (maximum 50 characters)"
    error_count=$((error_count + 1))
  fi

  # Check for generic names
  if [[ "$NAME" =~ ^(helper|assistant|agent|tool)$ ]]; then
    echo "⚠️  name is too generic: $NAME"
    warning_count=$((warning_count + 1))
  fi
fi

# Check description field
DESCRIPTION=$(echo "$FRONTMATTER" | grep '^description:' | sed 's/description: *//' || true)

if [ -z "$DESCRIPTION" ]; then
  echo "❌ Missing required field: description"
  error_count=$((error_count + 1))
else
  desc_length=${#DESCRIPTION}
  echo "✅ description: ${desc_length} characters"

  if [ $desc_length -lt 10 ]; then
    echo "⚠️  description too short (minimum 10 characters recommended)"
    warning_count=$((warning_count + 1))
  elif [ $desc_length -gt 5000 ]; then
    echo "⚠️  description very long (over 5000 characters)"
    warning_count=$((warning_count + 1))
  fi

  # Check for example blocks
  if ! grep -q '<example>' <<< "$DESCRIPTION"; then
    echo "⚠️  description should include <example> blocks for triggering"
    warning_count=$((warning_count + 1))
  fi

  # Check for "Use this agent when" pattern
  if ! grep -qi 'use this agent when' <<< "$DESCRIPTION"; then
    echo "⚠️  description should start with 'Use this agent when...'"
    warning_count=$((warning_count + 1))
  fi
fi

# Check model field (optional — defaults to "inherit")
MODEL=$(echo "$FRONTMATTER" | grep '^model:' | sed 's/model: *//' | sed 's/^"\(.*\)"$/\1/' || true)

if [ -z "$MODEL" ]; then
  echo "💡 model: not specified (optional — defaults to 'inherit', 부모 세션과 같은 모델을 사용)"
else
  echo "✅ model: $MODEL"

  case "$MODEL" in
    inherit|sonnet|opus|haiku|fable)
      # Rolling alias — resolves to the newest model in that family
      ;;
    *)
      if [[ "$MODEL" =~ ^claude-[a-z0-9.-]+$ ]]; then
        echo "ℹ️  '$MODEL' is a full model ID, so it PINS this generation."
        echo "   Aliases (inherit, sonnet, opus, haiku, fable) roll forward to the newest model in the family."
        echo "   배포용 플러그인에는 alias를 권장합니다 (Bedrock/Vertex 등 provider별 매핑 차이 대응)."
      else
        echo "⚠️  Unknown model: $MODEL"
        echo "   aliases: inherit, sonnet, opus, haiku, fable | full IDs: claude-* (e.g. claude-opus-5)"
        warning_count=$((warning_count + 1))
      fi
      ;;
  esac
fi

# Check effort field (optional)
EFFORT=$(echo "$FRONTMATTER" | grep '^effort:' | sed 's/effort: *//' | sed 's/^"\(.*\)"$/\1/' || true)

if [ -z "$EFFORT" ]; then
  echo "💡 effort: not specified (모델 기본 reasoning effort 사용)"
else
  case "$EFFORT" in
    low|medium|high|xhigh|max)
      echo "✅ effort: $EFFORT"
      ;;
    *)
      echo "❌ Invalid effort: $EFFORT (valid: low, medium, high, xhigh, max)"
      error_count=$((error_count + 1))
      ;;
  esac
fi

# Check color field (optional)
COLOR=$(echo "$FRONTMATTER" | grep '^color:' | sed 's/color: *//' || true)

if [ -z "$COLOR" ]; then
  echo "💡 color: not specified (optional — UI가 자동으로 배정)"
else
  echo "✅ color: $COLOR"

  case "$COLOR" in
    blue|cyan|green|yellow|magenta|red)
      # Valid color
      ;;
    *)
      echo "⚠️  Unknown color: $COLOR (valid: blue, cyan, green, yellow, magenta, red)"
      warning_count=$((warning_count + 1))
      ;;
  esac
fi

# Check tools field (optional)
TOOLS=$(echo "$FRONTMATTER" | grep '^tools:' | sed 's/tools: *//' || true)

if [ -n "$TOOLS" ]; then
  echo "✅ tools: $TOOLS"
else
  echo "💡 tools: not specified (agent has access to all tools)"
fi

# Check 5: Frontmatter field names
echo ""
echo "Checking frontmatter fields..."

# Read only the first frontmatter block, and drop <example> blocks:
# their "user:" / "assistant:" lines are prose, not YAML keys.
FIELD_NAMES=$(awk 'NR>1 && /^---$/{exit} NR>1' "$AGENT_FILE" \
  | sed '/<example>/,/<\/example>/d' \
  | grep -oE '^[A-Za-z][A-Za-z0-9_-]*:' | sed 's/:$//' || true)

unknown_fields=0
for FIELD in $FIELD_NAMES; do
  case "$FIELD" in
    name|description|model|effort|maxTurns|tools|disallowedTools|skills|memory|background|isolation|color)
      # Supported plugin-agent frontmatter field
      ;;
    hooks|mcpServers|permissionMode)
      echo "⚠️  $FIELD: not supported for plugin-shipped agents — 로드 시 조용히 무시됩니다"
      warning_count=$((warning_count + 1))
      unknown_fields=$((unknown_fields + 1))
      ;;
    *)
      echo "⚠️  Unknown field: $FIELD"
      warning_count=$((warning_count + 1))
      unknown_fields=$((unknown_fields + 1))
      ;;
  esac
done

if [ $unknown_fields -eq 0 ]; then
  echo "✅ All frontmatter fields are supported"
fi

# Check 6: System prompt
echo ""
echo "Checking system prompt..."

if [ -z "$SYSTEM_PROMPT" ]; then
  echo "❌ System prompt is empty"
  error_count=$((error_count + 1))
else
  prompt_length=${#SYSTEM_PROMPT}
  echo "✅ System prompt: $prompt_length characters"

  if [ $prompt_length -lt 20 ]; then
    echo "❌ System prompt too short (minimum 20 characters)"
    error_count=$((error_count + 1))
  elif [ $prompt_length -gt 10000 ]; then
    echo "⚠️  System prompt very long (over 10,000 characters)"
    warning_count=$((warning_count + 1))
  fi

  # Check for second person
  if ! grep -q "You are\|You will\|Your" <<< "$SYSTEM_PROMPT"; then
    echo "⚠️  System prompt should use second person (You are..., You will...)"
    warning_count=$((warning_count + 1))
  fi

  # Check for structure
  if ! grep -qi "responsibilities\|process\|steps" <<< "$SYSTEM_PROMPT"; then
    echo "💡 Consider adding clear responsibilities or process steps"
  fi

  if ! grep -qi "output" <<< "$SYSTEM_PROMPT"; then
    echo "💡 Consider defining output format expectations"
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $error_count -eq 0 ] && [ $warning_count -eq 0 ]; then
  echo "✅ All checks passed!"
  exit 0
elif [ $error_count -eq 0 ]; then
  echo "⚠️  Validation passed with $warning_count warning(s)"
  exit 0
else
  echo "❌ Validation failed with $error_count error(s) and $warning_count warning(s)"
  exit 1
fi
