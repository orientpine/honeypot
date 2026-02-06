#!/usr/bin/env python3
"""
Template Verification Script
Verifies that all new hybrid templates are syntactically valid Jinja2.
"""

import sys
from pathlib import Path

try:
    from jinja2 import Template, TemplateSyntaxError
except ImportError:
    print("ERROR: jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)


def verify_template(template_path):
    """Verify a single template file."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to parse the template
        Template(content)
        return True, None
    except TemplateSyntaxError as e:
        return False, f"Line {e.lineno}: {e.message}"
    except Exception as e:
        return False, str(e)


def main():
    templates_dir = Path(__file__).parent.parent / "assets"

    # New hybrid templates to verify
    templates = [
        "marketplace_hybrid.json.j2",
        "agent_orchestrator.md.j2",
        "agent_writer.md.j2",
        "agent_verify.md.j2",
        "skill_style_guide.md.j2",
        "ref_voice_tense.md.j2",
        "ref_vocabulary.md.j2",
        "ref_measurement.md.j2",
        "ref_citation.md.j2",
        "ref_title_template.md.j2",
        "ref_abstract_template.md.j2",
        "ref_introduction_template.md.j2",
        "ref_methodology_template.md.j2",
        "ref_results_template.md.j2",
        "ref_discussion_template.md.j2",
        "ref_caption_template.md.j2",
    ]

    print("=" * 60)
    print("Template Verification Report")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for template_name in templates:
        template_path = templates_dir / template_name

        if not template_path.exists():
            print(f"❌ {template_name}: FILE NOT FOUND")
            failed += 1
            continue

        success, error = verify_template(template_path)

        if success:
            print(f"✅ {template_name}: VALID")
            passed += 1
        else:
            print(f"❌ {template_name}: INVALID")
            print(f"   Error: {error}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(templates)}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
