import json, subprocess

mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
vg = next(p for p in mp['plugins'] if p['name'] == 'visual-generator')

# Version + new agent
assert vg['version'] == '3.5.0', f'expected 3.5.0, got {vg["version"]}'
assert './agents/renderer-agent-openai.md' in vg.get('agents', []), f'new agent missing in {vg.get("agents")}'
print('VERSION_AND_AGENT_OK')

# Schema whitelist
M = {'name','source','description','strict','agents','skills','version','author','license','category',
     'homepage','keywords','tags','commands','hooks','mcpServers','lspServers','outputStyles',
     'monitors','userConfig','channels','dependencies','repository'}
extra = set(vg.keys()) - M
assert not extra, f'INVALID FIELDS: {extra}'
print('SCHEMA_OK')

# Other plugins not modified
result = subprocess.run(['git', 'diff', '.claude-plugin/marketplace.json'],
    capture_output=True, text=True, encoding='utf-8')
diff = result.stdout
other_plugins = ['isd-generator', 'hwpx-generator', 'report-generator', 'pptx-design-styles',
    'wiki-gen', 'patent-trend-analyzer', 'paper-style-generator', 'investments-portfolio',
    'stock-consultation', 'equity-research', 'macro-analysis', 'plugin-dev', 'worktree-workflow',
    'general-agents', 'obsidian-skills', 'accelerated-learner', 'link-curator']
affected = [n for n in other_plugins if f'"name": "{n}"' in diff]
# Filter: only lines starting with + or - (actual changes, not context)
changed_lines = [l for l in diff.splitlines() if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')]
affected_in_changes = [n for n in other_plugins if any(n in l for l in changed_lines)]
assert not affected_in_changes, f'OTHER PLUGINS AFFECTED: {affected_in_changes}'
print('OTHER_PLUGINS_UNTOUCHED')

with open('.sisyphus/evidence/task-8-entry.txt', 'w', encoding='utf-8') as f:
    f.write('VERSION_AND_AGENT_OK\nSCHEMA_OK\nOTHER_PLUGINS_UNTOUCHED\n')
with open('.sisyphus/evidence/task-8-diff.txt', 'w', encoding='utf-8') as f:
    f.write(diff)
