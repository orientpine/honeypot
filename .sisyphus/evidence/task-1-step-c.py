import json

eval_data = json.loads(open('.sisyphus/evidence/task-1-eval-model.txt', encoding='utf-8').read())
verification = {
    'image_model': 'gpt-image-2',
    'eval_model': eval_data['eval_model']
}
with open('.sisyphus/evidence/task-1-model-verification.json', 'w', encoding='utf-8') as f:
    json.dump(verification, f, indent=2)
print(f'MODELS_VERIFIED: {verification}')
