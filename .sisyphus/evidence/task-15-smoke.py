import re, os, subprocess, sys
from pathlib import Path

# Step 1: Prepare fixture from theme-gov Golden Reference
content = open('plugins/visual-generator/skills/theme-gov/SKILL.md', encoding='utf-8').read()
m = re.search(r'(## INSTRUCTION.*?## FORBIDDEN ELEMENTS.*?)(?=\n## [^F]|\n---|\Z)', content, re.DOTALL)
if m:
    fixture = m.group(1).rstrip()
    Path('.sisyphus/evidence/task-15-fixture').mkdir(parents=True, exist_ok=True)
    open('.sisyphus/evidence/task-15-fixture/01_smoke_test.md', 'w', encoding='utf-8').write(fixture)
    size = os.path.getsize('.sisyphus/evidence/task-15-fixture/01_smoke_test.md')
    print(f'FIXTURE_READY: {size} bytes')
    with open('.sisyphus/evidence/task-15-fixture-ready.txt', 'w', encoding='utf-8') as f:
        f.write(f'FIXTURE_READY: {size} bytes\n')
else:
    # Fallback: create minimal 4-block fixture
    fixture = """## INSTRUCTION
Create a professional government presentation slide.

## CONFIGURATION
Theme: gov
Mood: clarity
Primary Color: #1E3A5F

## CONTENT
Title: "스마트 팩토리 기술 혁신"
Subtitle: "4차 산업혁명 기반 제조업 디지털 전환"

## FORBIDDEN ELEMENTS
- No watermarks
- No placeholder text
- No rendered hex codes"""
    Path('.sisyphus/evidence/task-15-fixture').mkdir(parents=True, exist_ok=True)
    open('.sisyphus/evidence/task-15-fixture/01_smoke_test.md', 'w', encoding='utf-8').write(fixture)
    size = os.path.getsize('.sisyphus/evidence/task-15-fixture/01_smoke_test.md')
    print(f'FIXTURE_READY (fallback): {size} bytes')
    with open('.sisyphus/evidence/task-15-fixture-ready.txt', 'w', encoding='utf-8') as f:
        f.write(f'FIXTURE_READY (fallback): {size} bytes\n')

# Step 2: Check API keys
gemini_key = os.environ.get('GEMINI_API_KEY', '')
openai_key = os.environ.get('OPENAI_API_KEY', '')

# Step 3: Gemini smoke (SKIP if no key)
if not gemini_key:
    msg = 'SKIPPED: GEMINI_API_KEY missing'
    print(msg)
    with open('.sisyphus/evidence/task-15-gemini.txt', 'w', encoding='utf-8') as f:
        f.write(msg + '\n')
else:
    Path('.sisyphus/evidence/task-15-out-gemini').mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable,
        'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py',
        '--prompts-dir', '.sisyphus/evidence/task-15-fixture/',
        '--output-dir', '.sisyphus/evidence/task-15-out-gemini/'],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    with open('.sisyphus/evidence/task-15-gemini-stdout.txt', 'w', encoding='utf-8') as f:
        f.write(result.stdout + result.stderr)
    import glob
    files = glob.glob('.sisyphus/evidence/task-15-out-gemini/01_*.jpg')
    if files and os.path.getsize(files[0]) >= 10000:
        msg = f'PASS: gemini jpg {os.path.getsize(files[0])} bytes - {files[0]}'
    else:
        msg = f'FAIL: no valid jpg generated (files: {files})'
    print(msg)
    with open('.sisyphus/evidence/task-15-gemini.txt', 'w', encoding='utf-8') as f:
        f.write(msg + '\n')

# Step 4: OpenAI smoke (SKIP if no key)
if not openai_key:
    msg = 'SKIPPED: OPENAI_API_KEY missing'
    print(msg)
    with open('.sisyphus/evidence/task-15-openai.txt', 'w', encoding='utf-8') as f:
        f.write(msg + '\n')
else:
    Path('.sisyphus/evidence/task-15-out-openai').mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable,
        'plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py',
        '--prompts-dir', '.sisyphus/evidence/task-15-fixture/',
        '--output-dir', '.sisyphus/evidence/task-15-out-openai/',
        '--max-images', '1', '--yes'],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    with open('.sisyphus/evidence/task-15-openai-stdout.txt', 'w', encoding='utf-8') as f:
        f.write(result.stdout + result.stderr)
    import glob
    files = glob.glob('.sisyphus/evidence/task-15-out-openai/01_*.jpg')
    if files and os.path.getsize(files[0]) >= 10000:
        msg = f'PASS: openai jpg {os.path.getsize(files[0])} bytes - {files[0]}'
    else:
        msg = f'FAIL: no valid jpg generated (files: {files})'
    print(msg)
    with open('.sisyphus/evidence/task-15-openai.txt', 'w', encoding='utf-8') as f:
        f.write(msg + '\n')

# Step 5: JPEG magic bytes (for any generated files)
import glob
checked = []
for path in ['.sisyphus/evidence/task-15-out-gemini', '.sisyphus/evidence/task-15-out-openai']:
    if os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith('.jpg'):
                with open(os.path.join(path, f), 'rb') as fp:
                    head = fp.read(3)
                    if head[:2] == b'\xff\xd8' and head[2] == 0xff:
                        checked.append(f'{path}/{f}')
                        print(f'OK: {path}/{f}')
if not checked:
    print('NO_FILES_TO_CHECK (both paths SKIPPED - API keys not available)')
else:
    print(f'JPEG_MAGIC_BYTES_OK: {len(checked)} files validated')

with open('.sisyphus/evidence/task-15-magic-bytes.txt', 'w', encoding='utf-8') as f:
    if checked:
        f.write(f'JPEG_MAGIC_BYTES_OK: {len(checked)} files\n')
    else:
        f.write('NO_FILES_TO_CHECK (SKIPPED)\n')

print('SMOKE_TEST_COMPLETE')
