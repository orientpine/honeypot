---
name: paper-style-toolkit
description: "Toolkit resources for paper-style-generator including conversion scripts, style analysis scripts, linguistic configuration, and Jinja templates. Use when executing PDF conversion or generating style-driven skill artifacts."
---

# Paper Style Toolkit

Use this skill for reusable resources needed by paper-style-generator agents.

- Run conversion and analysis scripts from `scripts/`.
- Load linguistic configuration from `references/`.
- Load template assets from `assets/`.

## 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/mineru_converter.py
scripts/md_postprocessor.py
scripts/style_extractor.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
```bash
python scripts/mineru_converter.py --input-dir [pdf_folder] --output-dir [md_output_folder]
python scripts/md_postprocessor.py --input-dir [md_folder] --output-dir [tagged_output_folder]
python scripts/style_extractor.py --input-dir [tagged_md_folder] --output-file [analysis.json]
```

**Step 2. 상대경로 실패 시 Glob 폴백**
```
Glob: **/paper-style-generator/skills/paper-style-toolkit/scripts/mineru_converter.py
Glob: **/paper-style-generator/skills/paper-style-toolkit/scripts/md_postprocessor.py
Glob: **/paper-style-generator/skills/paper-style-toolkit/scripts/style_extractor.py
```

**Step 3. Glob도 실패 시 확장 탐색**
```
Glob: **/mineru_converter.py
Glob: **/md_postprocessor.py
Glob: **/style_extractor.py
```

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.
