import subprocess, os, sys

env = os.environ.copy()
env['OPENAI_API_KEY'] = ''

result = subprocess.run(
    [sys.executable, 'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py',
     '--prompts-dir', '.sisyphus/evidence', '--output-dir', '.sisyphus/evidence/task-5-out'],
    capture_output=True, text=True, encoding='utf-8', errors='replace', env=env
)

output = result.stdout + result.stderr
exit_code = result.returncode

assert 'OPENAI_API_KEY' in output, f'key name not in error message: {output[:200]}'
assert exit_code == 1, f'expected exit 1, got {exit_code}'
print('HARD_FAIL_OK')

with open('.sisyphus/evidence/task-5-no-key.txt', 'w', encoding='utf-8') as f:
    f.write(output)
with open('.sisyphus/evidence/task-5-no-key-exit.txt', 'w', encoding='utf-8') as f:
    f.write(str(exit_code))
