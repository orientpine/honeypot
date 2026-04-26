import json
d = json.load(open('plugins/visual-generator/.claude-plugin/plugin.json', encoding='utf-8'))
assert d['version'] == '3.5.0', f'expected 3.5.0, got {d["version"]}'
A = {'name','version','description','author','homepage','repository','license','keywords','skills','commands','agents','hooks','mcpServers','lspServers','outputStyles','monitors','userConfig','channels','dependencies'}
extra = set(d.keys()) - A
assert not extra, f'INVALID FIELDS: {extra}'
print('VERSION_OK SCHEMA_OK')
open('.sisyphus/evidence/task-2-schema-check.txt', 'w', encoding='utf-8').write('VERSION_OK SCHEMA_OK\n')
