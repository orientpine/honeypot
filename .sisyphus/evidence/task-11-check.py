import re

content = open('AGENTS.md', encoding='utf-8').read()

# 1. Version 3.30.0
version_patterns = [r'\*\*Version:?\*\*:?\s*3\.30\.0', r'\*\*Version\*\*\s*:?\s*3\.30\.0']
assert any(re.search(p, content) for p in version_patterns), 'FAIL: Version 3.30.0 not found'
open('.sisyphus/evidence/task-11-version.txt', 'w', encoding='utf-8').write('VERSION_OK\n')
print('VERSION_OK')

# 2. Generated date >= 2026-04-26
gen_match = re.search(r'\*\*Generated:?\*\*:?\s*(\d{4}-\d{2}-\d{2})', content)
assert gen_match and gen_match.group(1) >= '2026-04-26', f'Generated date not updated: {gen_match.group(1) if gen_match else "missing"}'
open('.sisyphus/evidence/task-11-generated.txt', 'w', encoding='utf-8').write(f'GENERATED_OK: {gen_match.group(1)}\n')
print(f'GENERATED_OK: {gen_match.group(1)}')

# 3. WHERE TO LOOK - new files
new_files = ['renderer-agent-openai.md', 'generate_slide_images_openai.py', 'openai-quality-rubric.md']
missing_files = [f for f in new_files if f not in content]
assert not missing_files, f'WHERE_TO_LOOK_MISSING: {missing_files}'
open('.sisyphus/evidence/task-11-where-to-look.txt', 'w', encoding='utf-8').write('WHERE_TO_LOOK_OK: all 3 files referenced\n')
print('WHERE_TO_LOOK_OK')

# 4. COMMANDS section - new script
cmd_block = re.search(r'## COMMANDS.+?(?=\n## )', content, re.DOTALL)
assert cmd_block, 'FAIL: COMMANDS section missing'
cmd_text = cmd_block.group(0)
assert 'generate_slide_images_openai.py' in cmd_text and ('max-images' in cmd_text or 'prompts-dir' in cmd_text), 'FAIL: COMMANDS section does not document new script'
open('.sisyphus/evidence/task-11-commands.txt', 'w', encoding='utf-8').write('COMMANDS_OK\n')
print('COMMANDS_OK')

# 5. ANTI-PATTERNS - new rows
anti_block = re.search(r'## ANTI-PATTERNS.+?(?=\n## )', content, re.DOTALL)
assert anti_block, 'FAIL: ANTI-PATTERNS section missing'
anti_text = anti_block.group(0)
new_anti_keywords = ['Modifying Gemini path while building OpenAI', 'silent.*fallback']
present = [k for k in new_anti_keywords if re.search(k, anti_text, re.IGNORECASE)]
assert len(present) >= 1, f'FAIL: new anti-pattern rows missing (none of: {new_anti_keywords})'
open('.sisyphus/evidence/task-11-anti-patterns.txt', 'w', encoding='utf-8').write(f'ANTI_PATTERNS_OK: {present}\n')
print(f'ANTI_PATTERNS_OK: {present}')

print('ALL_FIVE_CHANGES_OK')
open('.sisyphus/evidence/task-11-master.txt', 'w', encoding='utf-8').write('ALL_FIVE_CHANGES_OK\n')
