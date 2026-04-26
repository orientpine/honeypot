import ast, sys

# 1. Syntax check
ast.parse(open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py', encoding='utf-8').read())
print('SYNTAX_OK')
open('.sisyphus/evidence/task-5-syntax.txt', 'w', encoding='utf-8').write('SYNTAX_OK\n')

# 2. Keyword check
content = open('plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py', encoding='utf-8').read()
required = ['gpt-image-2', '1536x1024', 'quality="high"', 'OPENAI_API_KEY', 'max-images', 'QUALITY_THRESHOLD = 7.0', 'KOREAN_MIN_THRESHOLD = 5.0', 'SYSTEM_INSTRUCTION', 'json_schema', 'detail', 'input_image', 'korean_text_readability', 'korean_hallucination_detection']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
print('ALL_KEYWORDS_FOUND')
open('.sisyphus/evidence/task-5-keywords.txt', 'w', encoding='utf-8').write('ALL_KEYWORDS_FOUND\n')

# 3. Gemini script untouched check (via git diff check)
import subprocess
result = subprocess.run(['git', 'diff', 'HEAD', '--', 'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py'], capture_output=True, text=True, encoding='utf-8')
assert not result.stdout.strip(), f'PROTECTED FILE MODIFIED: {result.stdout[:200]}'
print('PROTECTED_FILE_UNTOUCHED')
open('.sisyphus/evidence/task-5-gemini-untouched.txt', 'w', encoding='utf-8').write('PROTECTED_FILE_UNTOUCHED\n')
