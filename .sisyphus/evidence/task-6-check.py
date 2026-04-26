import subprocess

content = open('plugins/visual-generator/agents/renderer-agent-openai.md', encoding='utf-8').read()

# 1. Required sections
required_sections = ['name: renderer-agent-openai', 'tools: Read, Glob, Grep, Write, Bash',
    '## Overview', '## Workflow', 'Phase 0:', 'Phase 1:', 'Phase 2:', 'Phase 3:', 'Phase 4:', 'Phase 5:',
    '## Script & Error Handling', '## MUST DO', '## MUST NOT DO', '## Usage Examples']
missing = [s for s in required_sections if s not in content]
assert not missing, f'MISSING_SECTIONS: {missing}'
print('ALL_SECTIONS_PRESENT')
open('.sisyphus/evidence/task-6-sections.txt', 'w', encoding='utf-8').write('ALL_SECTIONS_PRESENT\n')

# 2. Cross-reference check (no duplication)
has_cross_ref = 'renderer-agent.md' in content
assert has_cross_ref, 'no cross-reference to renderer-agent.md'
table_header_count = content.count('| 검증 방법 |')
assert table_header_count <= 1, f'16-item table duplicated ({table_header_count} table headers found)'
print(f'CROSS_REF_OK (table_headers: {table_header_count})')
open('.sisyphus/evidence/task-6-cross-ref.txt', 'w', encoding='utf-8').write(f'CROSS_REF_OK\n')

# 3. OpenAI keywords, no Gemini keywords
required_openai = ['OPENAI_API_KEY', 'gpt-image-2', 'generate_slide_images_openai.py', 'max-images']
missing_openai = [k for k in required_openai if k not in content]
assert not missing_openai, f'OPENAI_KEYWORDS_MISSING: {missing_openai}'
forbidden_gemini = ['GEMINI_API_KEY', 'google-genai']
present_gemini = [k for k in forbidden_gemini if k in content]
assert not present_gemini, f'GEMINI_KEYWORDS_FOUND_IN_OPENAI_AGENT: {present_gemini}'
print('OPENAI_ONLY_OK')
open('.sisyphus/evidence/task-6-openai-kw.txt', 'w', encoding='utf-8').write('OPENAI_ONLY_OK\n')

# 4. Protected file renderer-agent.md untouched
result = subprocess.run(['git', 'diff', 'HEAD', '--', 'plugins/visual-generator/agents/renderer-agent.md'],
    capture_output=True, text=True, encoding='utf-8')
assert not result.stdout.strip(), f'PROTECTED FILE MODIFIED: {result.stdout[:200]}'
print('PROTECTED_FILE_UNTOUCHED')
open('.sisyphus/evidence/task-6-renderer-untouched.txt', 'w', encoding='utf-8').write('PROTECTED_FILE_UNTOUCHED\n')
