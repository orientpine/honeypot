import json, re, sys

results = {}
# 1. plugin.json
results['plugin.json'] = json.load(open('plugins/visual-generator/.claude-plugin/plugin.json', encoding='utf-8'))['version']
# 2. marketplace.json plugin entry
mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
vg = next(p for p in mp['plugins'] if p['name'] == 'visual-generator')
results['marketplace plugin entry'] = vg['version']
# 3. marketplace.json metadata.version
results['marketplace metadata'] = mp.get('metadata', {}).get('version', 'MISSING')
# 4. README.md Version
content = open('README.md', encoding='utf-8').read()
m = re.search(r'\*\*Version\*\*:\s*([\d.]+)', content)
results['README'] = m.group(1) if m else 'MISSING'
# 5. AGENTS.md Version
content = open('AGENTS.md', encoding='utf-8').read()
m = re.search(r'\*\*Version:?\*\*:?\s*([\d.]+)', content)
results['AGENTS'] = m.group(1) if m else 'MISSING'

print(json.dumps(results, indent=2, ensure_ascii=False))
expected = {
    'plugin.json': '3.5.0',
    'marketplace plugin entry': '3.5.0',
    'marketplace metadata': '3.30.0',
    'README': '3.30.0',
    'AGENTS': '3.30.0',
}
mismatches = {k: f'expected {expected[k]}, got {results[k]}' for k in expected if results[k] != expected[k]}
if mismatches:
    print(f'VERSION MISMATCHES: {mismatches}')
    sys.exit(1)
print('ALL_VERSIONS_SYNCED')
