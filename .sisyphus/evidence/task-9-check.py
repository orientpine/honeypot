import json
mp = json.load(open('.claude-plugin/marketplace.json', encoding='utf-8'))
v = mp.get('metadata', {}).get('version', 'MISSING')
assert v == '3.30.0', f'expected 3.30.0, got {v}'
print('METADATA_VERSION_OK')
# Verify visual-generator entry preserved
vg = next(p for p in mp['plugins'] if p['name'] == 'visual-generator')
assert vg['version'] == '3.5.0' and './agents/renderer-agent-openai.md' in vg.get('agents', []), 'Task 8 changes regressed'
print('VISUAL_GENERATOR_ENTRY_OK')
open('.sisyphus/evidence/task-9-metadata.txt', 'w', encoding='utf-8').write('METADATA_VERSION_OK\nVISUAL_GENERATOR_ENTRY_OK\n')
