import subprocess, os, sys
env = os.environ.copy()
env['OPENAI_API_KEY'] = ''
result = subprocess.run([sys.executable, 
    'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py',
    '--prompts-dir', '.sisyphus/evidence', '--output-dir', '.sisyphus/evidence/qa-out'],
    capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print('returncode:', result.returncode)
print('stdout:', result.stdout)
print('stderr:', result.stderr)
assert result.returncode == 1, f'expected exit 1, got {result.returncode}'
assert 'OPENAI_API_KEY' in (result.stdout + result.stderr), 'key name not in error'
print('HARD_FAIL_OK')
