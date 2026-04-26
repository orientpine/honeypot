import re

content = open('README.md', encoding='utf-8').read()

# 1. Version 3.30.0
version_match = re.search(r'\*\*Version\*\*\s*:\s*3\.30\.0', content)
assert version_match, 'FAIL: Version not 3.30.0'
open('.sisyphus/evidence/task-10-version.txt', 'w', encoding='utf-8').write('VERSION_OK\n')
print('VERSION_OK')

# 2. Changelog row 3.30.0
changelog_match = re.search(r'\|\s*3\.30\.0\s*\|\s*2026-0[4-9]', content)
assert changelog_match, 'FAIL: changelog row 3.30.0 missing or wrong date'
open('.sisyphus/evidence/task-10-changelog.txt', 'w', encoding='utf-8').write('CHANGELOG_ROW_OK\n')
print('CHANGELOG_ROW_OK')

# 3. OpenAI mentions
openai_mentions = re.findall(r'renderer[^\n]{0,50}openai|gpt-image-2|OpenAI gpt-image', content, re.IGNORECASE)
assert openai_mentions, 'FAIL: no OpenAI mention in README'
open('.sisyphus/evidence/task-10-openai-mention.txt', 'w', encoding='utf-8').write(f'OPENAI_MENTIONS_OK: {len(openai_mentions)} found\n')
print(f'OPENAI_MENTIONS_OK: {len(openai_mentions)} found')

print('README_UPDATES_OK')
open('.sisyphus/evidence/task-10-master.txt', 'w', encoding='utf-8').write('README_UPDATES_OK\n')
