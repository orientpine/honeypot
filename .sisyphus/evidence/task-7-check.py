import re

content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()

# 1. New params + phases + branching
required = ['renderer', 'renderer_choice_timing', 'max_images', 'Phase 0.5', 'Phase 3.5', 'renderer-agent-openai', 'OPENAI_API_KEY']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
branching_patterns = ['renderer == "openai"', "renderer == 'openai'", 'renderer=openai', 'renderer: openai', 'renderer == ']
has_branching = any(p in content for p in branching_patterns)
assert has_branching, f'no branching logic found'
print('PARAMS_AND_BRANCHING_OK')
open('.sisyphus/evidence/task-7-keywords.txt', 'w', encoding='utf-8').write('PARAMS_AND_BRANCHING_OK\n')

# 2. Default values documented
timing_default_patterns = [r'renderer_choice_timing[^\n]{0,100}기본[^\n]{0,30}none', r'renderer_choice_timing[^\n]{0,100}none[^\n]{0,50}백워드', r'백워드 호환']
timing_doc = any(re.search(p, content, re.IGNORECASE) for p in timing_default_patterns)
assert timing_doc, 'renderer_choice_timing default=none not documented'
renderer_default_patterns = [r'renderer[^\n]{0,100}기본[^\n]{0,30}gemini', r'기본값[^\n]{0,30}gemini', r'renderer.*gemini.*기본']
renderer_doc = any(re.search(p, content, re.IGNORECASE) for p in renderer_default_patterns)
assert renderer_doc, 'renderer default=gemini not documented'
print('DEFAULTS_DOCUMENTED')
open('.sisyphus/evidence/task-7-default-none.txt', 'w', encoding='utf-8').write('DEFAULTS_DOCUMENTED\n')

# 3. Hard-fail policy
patterns = [r'silent fallback', r'자동 전환 금지', r'hard.?fail', r'즉시 중단']
matches = [p for p in patterns if re.search(p, content, re.IGNORECASE)]
assert matches, f'hard-fail policy not documented'
print(f'HARD_FAIL_DOCUMENTED: {matches}')
open('.sisyphus/evidence/task-7-no-fallback.txt', 'w', encoding='utf-8').write(f'HARD_FAIL_DOCUMENTED: {matches}\n')

# 4. Original phases preserved
required_phases = ['Phase 1: 문서 분석', 'Phase 2: 콘텐츠 검토', 'Phase 3: 프롬프트 생성', 'Phase 4: 이미지 렌더링', 'Phase 5: 최종 보고서 생성']
missing_phases = [p for p in required_phases if p not in content]
assert not missing_phases, f'PHASES_REMOVED: {missing_phases}'
print('ALL_PHASES_PRESERVED')
open('.sisyphus/evidence/task-7-phases-preserved.txt', 'w', encoding='utf-8').write('ALL_PHASES_PRESERVED\n')
