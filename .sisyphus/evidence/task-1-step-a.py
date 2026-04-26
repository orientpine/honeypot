from openai import OpenAI
import json, os

client = OpenAI()
try:
    r = client.images.generate(
        model='gpt-image-2',
        prompt='a simple white square on black background',
        size='1536x1024',
        quality='low',
        n=1
    )
    result = {
        'has_b64': bool(r.data[0].b64_json),
        'len': len(r.data[0].b64_json) if r.data[0].b64_json else 0,
        'status': 'success'
    }
except Exception as e:
    result = {'has_b64': False, 'len': 0, 'status': 'error', 'error': str(e)[:300]}

with open('.sisyphus/evidence/task-1-gpt-image-2-test.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result))
