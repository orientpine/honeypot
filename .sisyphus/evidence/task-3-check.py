import re
content = open('plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md', encoding='utf-8').read()
required_fields = ['korean_text_readability', 'korean_hallucination_detection', 'content_reference_accuracy', 'layout_suitability', 'color_palette_compliance', 'overall_score']
missing = [f for f in required_fields if f not in content]
assert not missing, f'MISSING_FIELDS: {missing}'
assert '7.0' in content and '5.0' in content, 'thresholds 7.0/5.0 not documented'
lines = content.count('\n') + 1
assert lines <= 80, f'too long: {lines} lines (max 80)'
print(f'FIELDS_AND_THRESHOLDS_OK ({lines} lines)')
open('.sisyphus/evidence/task-3-fields.txt', 'w', encoding='utf-8').write(f'FIELDS_AND_THRESHOLDS_OK ({lines} lines)\n')

# Concept theme exemption check
content_lower = content.lower()
has_concept = 'concept' in content_lower
has_exempt_keyword = any(kw in content_lower for kw in ['exempt', '면제', 'skip', '10.0'])
assert has_concept and has_exempt_keyword, 'concept theme exemption not documented'
print('CONCEPT_EXEMPT_OK')
open('.sisyphus/evidence/task-3-concept-exempt.txt', 'w', encoding='utf-8').write('CONCEPT_EXEMPT_OK\n')
