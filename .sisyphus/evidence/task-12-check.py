import re, subprocess

content = open('plugins/visual-generator/commands/visual-generate.md', encoding='utf-8').read()

# 1. Original 5 phases preserved
required_phases = ['Phase 1: 문서 분석', 'Phase 2: 콘텐츠 검토', 'Phase 3: 프롬프트 생성', 'Phase 4: 이미지 렌더링', 'Phase 5: 최종 보고서 생성']
missing = [p for p in required_phases if p not in content]
assert not missing, f'REGRESSION: phases removed: {missing}'
print('REGRESSION_PASS')
open('.sisyphus/evidence/task-12-phases.txt', 'w', encoding='utf-8').write('REGRESSION_PASS\n')

# 2. Phase 0.5 and 3.5 are conditional
def find_phase_context(phase_label):
    m = re.search(re.escape(phase_label), content)
    if not m:
        return None
    start = max(0, content.rfind('\n', 0, m.start() - 200))
    end = content.find('\n', m.end() + 500)
    return content[start:end]

phase_05 = find_phase_context('Phase 0.5')
phase_35 = find_phase_context('Phase 3.5')
assert phase_05, 'Phase 0.5 not found'
assert phase_35, 'Phase 3.5 not found'
condition_patterns = [r'renderer_choice_timing.*?pre', r'renderer_choice_timing.*?post', r'조건:', r'when ', r'IF ']
phase_05_has_condition = any(re.search(p, phase_05, re.IGNORECASE) for p in condition_patterns)
phase_35_has_condition = any(re.search(p, phase_35, re.IGNORECASE) for p in condition_patterns)
assert phase_05_has_condition, 'Phase 0.5 not conditional'
assert phase_35_has_condition, 'Phase 3.5 not conditional'
print('PHASES_CONDITIONAL_OK')
open('.sisyphus/evidence/task-12-conditional.txt', 'w', encoding='utf-8').write('PHASES_CONDITIONAL_OK\n')

# 3. Protected files byte-identical
result = subprocess.run(['git', 'diff', 'HEAD', '--',
    'plugins/visual-generator/agents/renderer-agent.md',
    'plugins/visual-generator/agents/prompt-designer.md',
    'plugins/visual-generator/agents/content-organizer.md',
    'plugins/visual-generator/agents/content-reviewer.md',
    'plugins/visual-generator/agents/prompt-validator.md',
    'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py'],
    capture_output=True, text=True, encoding='utf-8')
assert not result.stdout.strip(), f'PROTECTED FILES MODIFIED: {result.stdout[:300]}'
print('PROTECTED_FILES_BYTE_IDENTICAL')
open('.sisyphus/evidence/task-12-protected.txt', 'w', encoding='utf-8').write('PROTECTED_FILES_BYTE_IDENTICAL\n')
