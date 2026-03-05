#!/usr/bin/env python3
"""
Template Verification Script
Verifies Jinja2 templates for both syntax and semantic correctness.

Checks:
  - Jinja2 syntax validity
  - subagent_type plugin prefix (must include '-paper-skills::')
  - Jinja2 operator precedence (round filter must wrap expression)
  - Jinja2 slice() misuse
  - Non-standard frontmatter fields
"""

import re
import sys
from pathlib import Path

try:
    from jinja2 import Template, TemplateSyntaxError
except ImportError:
    print("ERROR: jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)


def verify_syntax(template_path):
    """Verify Jinja2 syntax validity."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        Template(content)
        return True, []
    except TemplateSyntaxError as e:
        return False, [f"Syntax error at line {e.lineno}: {e.message}"]
    except Exception as e:
        return False, [f"Parse error: {e}"]


def verify_semantics(template_path):
    """Verify semantic correctness of template content."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    warnings = []
    name = template_path.name

    # Check 1: subagent_type without plugin prefix
    # Valid:   subagent_type="{{ name }}-paper-skills::{{ name }}-xxx"
    # Invalid: subagent_type="{{ name }}-xxx" (missing plugin prefix)
    subagent_refs = re.findall(
        r'subagent_type="\{\{\s*name\s*\}\}-(?!paper-skills::)', content
    )
    if subagent_refs:
        warnings.append(
            f"subagent_type missing plugin prefix '-paper-skills::' "
            f"({len(subagent_refs)} occurrence(s))"
        )

    # Check 2: Jinja2 round filter precedence
    # Bad:  {{ x * 100 | round }}
    # Good: {{ (x * 100) | round }}
    bad_round = re.findall(
        r'\{\{[^}]*[^(]\s*\*\s*100\s*\|\s*round', content
    )
    if bad_round:
        warnings.append(
            f"Operator precedence issue: '* 100 | round' without parentheses "
            f"({len(bad_round)} occurrence(s)). Use '(x * 100) | round'."
        )

    # Check 3: Jinja2 slice() misuse (slice creates groups, not limits)
    slice_uses = re.findall(r'\|\s*slice\(', content)
    if slice_uses:
        warnings.append(
            f"Jinja2 slice() filter detected ({len(slice_uses)} occurrence(s)). "
            f"slice(N) creates N groups, not first-N items. "
            f"Use loop.index0 < N instead."
        )

    # Check 4: Non-standard frontmatter fields (skills: in agent)
    if name.startswith('agent_'):
        frontmatter_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            if re.search(r'^skills:', fm, re.MULTILINE):
                warnings.append(
                    "Non-standard frontmatter field 'skills:' detected. "
                    "This field is not supported in agent .md files. "
                    "Reference skills in the agent body instead."
                )

    # Check 5: Non-standard plugin entry fields (marketplace_hybrid only)
    if name == 'marketplace_hybrid.json.j2':
        for field in ['keywords', 'metadata']:
            if f'"{field}"' in content:
                warnings.append(
                    f"Non-standard marketplace field '{field}' detected. "
                    f"Only documented fields are guaranteed to work."
                )

    return warnings


def main():
    templates_dir = Path(__file__).parent.parent / "assets"

    templates = [
        "marketplace_root.json.j2",
        "marketplace_hybrid.json.j2",
        "plugin.json.j2",
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
    print("Template Verification Report (Syntax + Semantics)")
    print("=" * 60)
    print()

    syntax_pass = 0
    syntax_fail = 0
    semantic_warnings = 0

    for template_name in templates:
        template_path = templates_dir / template_name

        if not template_path.exists():
            print(f"\u274c {template_name}: FILE NOT FOUND")
            syntax_fail += 1
            continue

        # Syntax check
        ok, errors = verify_syntax(template_path)
        if ok:
            print(f"\u2705 {template_name}: SYNTAX OK")
            syntax_pass += 1
        else:
            print(f"\u274c {template_name}: SYNTAX ERROR")
            for err in errors:
                print(f"   {err}")
            syntax_fail += 1

        # Semantic check
        warnings = verify_semantics(template_path)
        if warnings:
            for w in warnings:
                print(f"   \u26a0\ufe0f  {w}")
                semantic_warnings += 1

    print()
    print("=" * 60)
    print(f"Syntax:    {syntax_pass} passed, {syntax_fail} failed")
    print(f"Semantics: {semantic_warnings} warning(s)")
    print("=" * 60)

    return 0 if syntax_fail == 0 and semantic_warnings == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
