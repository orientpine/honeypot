content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()
required = ['renderer', 'renderer_choice_timing', 'max_images', 'Phase 0.5', 'Phase 3.5', 'renderer-agent-openai', 'OPENAI_API_KEY']
missing = [k for k in required if k not in content]
assert not missing, f'MISSING: {missing}'
patterns = ['renderer == "openai"', "renderer == 'openai'", 'renderer == ']
assert any(p in content for p in patterns), 'no renderer == openai check found'
print('ORCHESTRATOR_OK')
