from openai import OpenAI
import json

client = OpenAI()
candidates = ['gpt-5.5', 'gpt-5', 'gpt-4o']
schema = {
    'format': {
        'type': 'json_schema',
        'strict': True,
        'json_schema': {
            'name': 'TestSchema',
            'schema': {
                'type': 'object',
                'properties': {'x': {'type': 'integer'}},
                'required': ['x'],
                'additionalProperties': False
            }
        }
    }
}
selected = None
errors = {}
for model in candidates:
    try:
        resp = client.responses.create(model=model, input='Return {"x": 1}', text=schema)
        selected = model
        print(f'SUCCESS: {model}')
        break
    except Exception as e:
        errors[model] = str(e)[:200]
        print(f'FAILED: {model} -> {str(e)[:100]}')

result = {'eval_model': selected, 'errors': errors}
with open('.sisyphus/evidence/task-1-eval-model.txt', 'w', encoding='utf-8') as f:
    f.write(json.dumps(result, indent=2, ensure_ascii=False))

print(f'EVAL_MODEL: {selected}')
if not selected:
    import sys
    print(f'ALL CANDIDATES FAILED')
    sys.exit(1)
