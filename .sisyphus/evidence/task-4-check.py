content = open('plugins/visual-generator/skills/slide-renderer/SKILL.md', encoding='utf-8').read()

# Check new OpenAI section keywords
assert 'OpenAI gpt-image-2' in content, 'FAIL: section missing'
required = ['OPENAI_API_KEY', 'openai>=1.0', 'gpt-image-2', '1536x1024', 'max-images', 'openai-quality-rubric.md']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
print('SECTION_AND_KEYWORDS_OK')
open('.sisyphus/evidence/task-4-keywords.txt', 'w', encoding='utf-8').write('SECTION_AND_KEYWORDS_OK\n')

# Check Gemini section preserved
gemini_keywords = ['GEMINI_API_KEY', 'google-genai', 'gemini-3-pro-image-preview']
preserved = [k for k in gemini_keywords if k in content]
assert len(preserved) >= 3, f'GEMINI_SECTION_DAMAGED: only {preserved} found'
print(f'GEMINI_PRESERVED: {preserved}')
open('.sisyphus/evidence/task-4-gemini-preserved.txt', 'w', encoding='utf-8').write(f'GEMINI_PRESERVED: {preserved}\n')
