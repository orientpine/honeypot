#!/bin/bash
# KIPRIS Patent MCP Server Installer
# Usage: ./install.sh [KIPRIS_API_KEY]
# Works for both Claude Code and OpenCode environments.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SETTINGS_FILE="$HOME/.claude/settings.json"

echo "=== KIPRIS Patent MCP Server Setup ==="
echo ""

# Get API key
if [ -n "$1" ]; then
    API_KEY="$1"
elif [ -n "$KIPRIS_API_KEY" ]; then
    API_KEY="$KIPRIS_API_KEY"
else
    read -rp "Enter your KIPRIS API Key: " API_KEY
fi

if [ -z "$API_KEY" ]; then
    echo "Error: KIPRIS API key is required."
    echo "Get your key at: https://www.data.go.kr/ (search: KIPRIS Plus)"
    exit 1
fi

# Install Python package
echo "[1/3] Installing mcp-kipris package..."
cd "$SCRIPT_DIR"
pip install -e . --quiet

# Verify installation
echo "[2/3] Verifying installation..."
TOOL_COUNT=$(KIPRIS_API_KEY="$API_KEY" python -c "
from mcp_kipris.kipris._registry import get_all_tools
tools = get_all_tools()
print(len(tools))
" 2>/dev/null)

if [ "$TOOL_COUNT" = "18" ]; then
    echo "  $TOOL_COUNT tools registered successfully"
else
    echo "  Warning: Expected 18 tools, got ${TOOL_COUNT:-0}"
    echo "  Check KIPRIS_API_KEY and try again."
fi

# Configure Claude Code settings.json
echo "[3/3] Configuring MCP server..."
mkdir -p "$HOME/.claude"

if [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup.$(date +%Y%m%d)"
fi

python3 -c "
import json, os

settings_file = '$SETTINGS_FILE'
try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if 'mcpServers' not in settings:
    settings['mcpServers'] = {}

settings['mcpServers']['kipris-patent'] = {
    'command': 'python',
    'args': ['-m', 'mcp_kipris.server'],
    'env': {'KIPRIS_API_KEY': '$API_KEY'}
}

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print('  Updated ~/.claude/settings.json')
"

echo ""
echo "Setup complete!"
echo "  Package: mcp-kipris"
echo "  MCP server: kipris-patent"
echo "  Tools: 18 (Korean 8 + Foreign 7 + Preprocessing 3)"
echo ""
echo "Restart Claude Code to activate patent search tools."
