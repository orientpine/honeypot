---
name: core-resources
description: "Shared references, templates, and scripts for isd-generator chapter and figure agents. Use when loading canonical writing patterns, output templates, or image generation scripts used by ISD workflows."
---

# Core Resources

Use this skill as the central resource hub for ISD generation.

- Load chapter templates and writing patterns from `references/`.
- Load output scaffolds from `assets/output_templates/`.
- Run image generation tooling from `scripts/`.

## 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/generate_images.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
```bash
python scripts/generate_images.py \
  --prompts-dir [프롬프트 폴더 경로] \
  --output-dir [이미지 출력 폴더 경로]
```

**Step 2. 상대경로 실패 시 Glob 폴백**
```
Glob: **/isd-generator/skills/core-resources/scripts/generate_images.py
```

**Step 3. Glob도 실패 시 확장 탐색**
```
Glob: **/generate_images.py
```

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.
