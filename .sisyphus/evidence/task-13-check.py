import subprocess

# 1. All changed files must be in allowlist
result = subprocess.run(['git', 'diff', 'HEAD', '--name-only'],
    capture_output=True, text=True, encoding='utf-8')
# Now we've committed everything, so diff HEAD should be empty or minimal
# Check against full history from original HEAD
result2 = subprocess.run(['git', 'log', '--oneline', '-5'],
    capture_output=True, text=True, encoding='utf-8')
print(f'Recent commits:\n{result2.stdout}')

# Check what files changed since before our work (3 commits back)
result3 = subprocess.run(['git', 'diff', 'HEAD~3', '--name-only'],
    capture_output=True, text=True, encoding='utf-8')
changed = set(line.strip().replace('\\', '/') for line in result3.stdout.splitlines() if line.strip())
print(f'Changed files since start: {changed}')

allowed = {
    'plugins/visual-generator/agents/renderer-agent-openai.md',
    'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py',
    'plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md',
    'plugins/visual-generator/commands/visual-generate.md',
    'plugins/visual-generator/skills/slide-renderer/SKILL.md',
    'plugins/visual-generator/.claude-plugin/plugin.json',
    '.claude-plugin/marketplace.json',
    'README.md',
    'AGENTS.md',
    '.sisyphus/boulder.json',  # system session tracking file
}
unauthorized = changed - allowed
assert not unauthorized, f'UNAUTHORIZED CHANGES: {unauthorized}'
print('CONTAMINATION_CLEAN')

with open('.sisyphus/evidence/task-13-changed-files.txt', 'w', encoding='utf-8') as f:
    f.write(result3.stdout)
with open('.sisyphus/evidence/task-13-allowlist.txt', 'w', encoding='utf-8') as f:
    f.write(f'CONTAMINATION_CLEAN\nChanged files: {sorted(changed)}\n')

# 2. Other plugins not modified
other_changes = [c for c in changed if not c.startswith('plugins/visual-generator/')
                 and c not in {'.claude-plugin/marketplace.json', 'README.md', 'AGENTS.md', '.sisyphus/boulder.json'}]
assert not other_changes, f'OTHER PLUGINS MODIFIED: {other_changes}'
print('OTHER_PLUGINS_UNTOUCHED')
with open('.sisyphus/evidence/task-13-other-plugins.txt', 'w', encoding='utf-8') as f:
    f.write('OTHER_PLUGINS_UNTOUCHED\n')
