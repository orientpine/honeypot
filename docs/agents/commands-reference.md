# Commands Reference (CLI Cheatsheet)

> **언제 읽나요**: 플러그인 스크립트(이미지 생성, HWPX 빌드, wiki-gen 파이프라인 등)를 CLI로 직접 실행해야 할 때, 명령어 인자/옵션을 확인할 때.
> **상위 문서**: [AGENTS.md](../../AGENTS.md)

```bash
# Generate images from prompts (requires google-genai, Pillow)
python plugins/isd-generator/skills/core-resources/scripts/generate_images.py \
  --prompts-dir [path]/prompts/ \
  --output-dir [path]/figures/

# Generate slide images (Gemini)
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py \
  --prompts-dir [path] --output-dir [path]

# Generate slide images (OpenAI gpt-image-2)
python plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py \
  --prompts-dir [path] --output-dir [path] \
  [--size 3840x2160] [--quality high] [--model gpt-image-2] [--eval-model gpt-5.5] \
  [--max-images 30] [--yes]

# Paper Style Generator: Convert PDFs to Markdown (requires MinerU)
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/mineru_converter.py \
  --input-dir [pdf_folder] \
  --output-dir [md_output_folder]

# Paper Style Generator: Post-process and tag sections
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/md_postprocessor.py \
  --input-dir [md_folder] \
  --output-dir [tagged_output_folder]

# Paper Style Generator: Extract style patterns
python plugins/paper-style-generator/skills/paper-style-toolkit/scripts/style_extractor.py \
  --input-dir [tagged_md_folder] \
  --output-file [analysis.json]

# HWPX Workflow 7: Parse Markdown to JSON blocks
python plugins/hwpx-generator/skills/hwpx-core/scripts/md_parser.py \
  --input [markdown_file] \
  --output [json_blocks_file]

# HWPX Workflow 7: Write JSON blocks to HWPX XML fragment
python plugins/hwpx-generator/skills/hwpx-core/scripts/xml_writer.py \
  --blocks [json_blocks_file] \
  --style-config [style_config.json] \
  --output [hwpx_fragment.xml]

# HWPX Workflow 7: Embed PNG images into HWPX
python plugins/hwpx-generator/skills/hwpx-core/scripts/image_embedder.py \
  --hwpx [document.hwpx] \
  --images [image_folder] \
  --output [document_with_images.hwpx]

# HWPX md_merger: 다중 MD 파일을 heading offset 맥쳐 병합
python plugins/hwpx-generator/skills/hwpx-core/scripts/md_merger.py \
  file1.md file2.md --target-level 2 --output merged.json

# HWPX Section Transplant: 챕터 이식
python plugins/hwpx-generator/skills/hwpx-core/scripts/section_transplant.py \
  --source source.hwpx --target target.hwpx --chapters 3,4,5 --output result.hwpx

# HWPX Section Transplant: dry-run (매핑 테이블만 출력)
python plugins/hwpx-generator/skills/hwpx-core/scripts/section_transplant.py \
  --source source.hwpx --target target.hwpx --chapters 3,4,5 --dry-run

# wiki-gen: Ingest Obsidian vault into raw/entries/
python plugins/wiki-gen/skills/wiki-gen/scripts/ingest_obsidian.py \
  --source-root [vault_path] --wiki-root [project]/wiki

# wiki-gen: Generate portable batch manifests grouped by source_top/source_category
python plugins/wiki-gen/skills/wiki-gen/scripts/generate_batches.py \
  --wiki-root [project]/wiki --target-batches 20 --max-entries-per-batch 150

# wiki-gen: Rebuild _index.md with C1 [[filename|Title]] format
python plugins/wiki-gen/skills/wiki-gen/scripts/rebuild_index.py \
  --wiki-root [project]/wiki

# wiki-gen: Verify citation coverage (frontmatter sources + body 12-hex IDs)
python plugins/wiki-gen/skills/wiki-gen/scripts/check_coverage.py \
  --wiki-root [project]/wiki

# wiki-gen: Verify content coverage beyond direct citation
python plugins/wiki-gen/skills/wiki-gen/scripts/verify_content.py \
  --wiki-root [project]/wiki --entries-dir [project]/raw/entries

# wiki-gen: Analyze duplicates, stubs, bloat, orphans
python plugins/wiki-gen/skills/wiki-gen/scripts/consolidate_analyze.py \
  --wiki-root [project]/wiki

# wiki-gen: Run full verification pipeline and write _FINAL_REPORT.md
python plugins/wiki-gen/skills/wiki-gen/scripts/finalize.py \
  --wiki-root [project]/wiki

# wiki-gen: Diagnose wikilink resolution (filename vs alias vs title-only)
python plugins/wiki-gen/skills/wiki-gen/scripts/diag_wikilink_resolution.py \
  --wiki-root [project]/wiki

# wiki-gen: Group uncovered entry IDs by batch for wiki remediate
python plugins/wiki-gen/skills/wiki-gen/scripts/diag_uncovered.py \
  --wiki-root [project]/wiki --batches-dir [project]/raw/batches

# wiki-gen: Plan batch distribution from ingest log (summary before generate_batches)
python plugins/wiki-gen/skills/wiki-gen/scripts/plan_batches.py \
  --entries-dir [project]/raw/entries --ingest-log [project]/raw/ingest_log.json

# wiki-gen: Multi-source sync
python plugins/wiki-gen/skills/wiki-gen/scripts/sync_sources.py \
  --config sources.yaml --wiki-root /path/to/wiki

# wiki-gen: Ingest project doc/ folder
python plugins/wiki-gen/skills/wiki-gen/scripts/ingest_projects.py \
  --source-root /path/to/project/doc --wiki-root /path/to/wiki --source-name my_project

# wiki-gen: Shared ingest helpers
python plugins/wiki-gen/skills/wiki-gen/scripts/ingest_common.py
```
