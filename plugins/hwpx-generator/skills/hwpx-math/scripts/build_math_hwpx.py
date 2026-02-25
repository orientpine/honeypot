#!/usr/bin/env python3
"""Build a math worksheet HWPX document with equations in 2-column layout.

Generates math worksheets by:
1. Using the math-hwpx base template (2-column, optimized margins)
2. Generating section0.xml from problem data (JSON)
3. Embedding equations using hp:equation with Hancom equation script
4. Packaging as valid HWPX

Supports two formats:
- exam (기본값, 학력평가/수능): Standardized Korean exam paper format with header, horizontal choices, etc.
- worksheet: Simple 2-column math worksheet (--exam-type worksheet로 명시 필요)

Usage:
    # Exam format (기본값 — 학력평가)
    python build_math_hwpx.py --problems problems.json --output exam.hwpx

    # Simple worksheet format (명시적 지정 필요)
    python build_math_hwpx.py --problems problems.json --exam-type worksheet --output worksheet.hwpx

    # With title and metadata
    python build_math_hwpx.py --problems problems.json \
        --title "중2 일차방정식 연습" --creator "수학교사" --output worksheet.hwpx

    # Custom section0.xml override (bypass problem generation)
    python build_math_hwpx.py --section my_section0.xml --output worksheet.hwpx

    # Custom header override
    python build_math_hwpx.py --problems p.json --header my_header.xml --output worksheet.hwpx
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from hwpx_utils import (
    validate_xml,
    update_metadata,
    pack_hwpx,
    validate_hwpx,
    _add_images_to_manifest,
)
from section_generators import generate_section_xml

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
BASE_DIR = TEMPLATES_DIR / "base"


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------

def build(
    problems_file: Path | None,
    header_override: Path | None,
    section_override: Path | None,
    title: str | None,
    creator: str | None,
    output: Path,
    exam_type: str | None = None,
) -> None:
    """Main build logic."""
    if not BASE_DIR.is_dir():
        raise SystemExit(f"Base template not found: {BASE_DIR}")

    with tempfile.TemporaryDirectory() as tmpdir:
        work = Path(tmpdir) / "build"

        # 1. Copy base template
        shutil.copytree(BASE_DIR, work)

        # 2. Generate section0.xml from problem data
        if problems_file and not section_override:
            if not problems_file.is_file():
                raise SystemExit(f"Problems file not found: {problems_file}")
            with open(problems_file, encoding="utf-8") as f:
                data = json.load(f)
            if title and "title" not in data:
                data["title"] = title
            # CLI --exam-type overrides JSON exam_type
            if exam_type:
                data["exam_type"] = exam_type

            # 2a. Generate graph images for problems that have "graph" field
            image_ids = {}
            bindata_dir = work / "BinData"
            problems = data.get("problems", [])
            graph_problems = [(i, p) for i, p in enumerate(problems, 1)
                              if "graph" in p]
            if graph_problems:
                from graph_generator import generate_graph
                bindata_dir.mkdir(exist_ok=True)
                for prob_num, prob in graph_problems:
                    graph_spec = prob["graph"]
                    img_name = f"graph_{prob_num}.png"
                    img_path = bindata_dir / img_name
                    generate_graph(graph_spec, img_path)
                    item_id = f"graph{prob_num}"
                    image_ids[prob_num] = item_id
                    print(f"  Graph: problem {prob_num} → {img_name}")

            # Pass image_ids into data for section XML generation
            data["_image_ids"] = image_ids
            section_xml = generate_section_xml(data)
            (work / "Contents" / "section0.xml").write_text(section_xml, encoding="utf-8")

            # 2b. Register images in content.hpf manifest
            if image_ids:
                _add_images_to_manifest(work / "Contents" / "content.hpf",
                                         image_ids, problems)

        # 3. Apply custom overrides
        if header_override:
            if not header_override.is_file():
                raise SystemExit(f"Header file not found: {header_override}")
            shutil.copy2(header_override, work / "Contents" / "header.xml")

        if section_override:
            if not section_override.is_file():
                raise SystemExit(f"Section file not found: {section_override}")
            shutil.copy2(section_override, work / "Contents" / "section0.xml")

        # 4. Update metadata
        update_metadata(work / "Contents" / "content.hpf", title, creator)

        # 5. Validate all XML files
        for xml_file in work.rglob("*.xml"):
            validate_xml(xml_file)
        for hpf_file in work.rglob("*.hpf"):
            validate_xml(hpf_file)

        # 6. Pack
        pack_hwpx(work, output)

    # 7. Final validation
    errors = validate_hwpx(output)
    if errors:
        print(f"WARNING: {output} has issues:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    else:
        print(f"VALID: {output}")
        if problems_file:
            print(f"  Problems: {problems_file}")
        if header_override:
            print(f"  Header: {header_override}")
        if section_override:
            print(f"  Section: {section_override}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build math worksheet HWPX from problem data"
    )
    parser.add_argument(
        "--problems", "-p",
        type=Path,
        help="JSON file containing problem data",
    )
    parser.add_argument(
        "--header",
        type=Path,
        help="Custom header.xml to override",
    )
    parser.add_argument(
        "--section",
        type=Path,
        help="Custom section0.xml to override (bypasses problem generation)",
    )
    parser.add_argument(
        "--title",
        help="Document title",
    )
    parser.add_argument(
        "--creator",
        help="Document creator",
    )
    parser.add_argument(
        "--exam-type",
        choices=["worksheet", "학력평가", "수능", "exam"],
        default="학력평가",
        help="Exam type (default: 학력평가, use 'worksheet' for simple format)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output .hwpx file path",
    )
    args = parser.parse_args()

    if not args.problems and not args.section:
        parser.error("Either --problems or --section is required")

    build(
        problems_file=args.problems,
        header_override=args.header,
        section_override=args.section,
        title=args.title,
        creator=args.creator,
        output=args.output,
        exam_type=args.exam_type,
    )


if __name__ == "__main__":
    main()
