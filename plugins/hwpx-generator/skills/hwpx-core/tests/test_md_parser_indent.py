from __future__ import annotations

# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportAny=false, reportUnknownVariableType=false, reportUnknownMemberType=false


def load_module(scripts_dir, name):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, scripts_dir / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dash_bullet_indent_level_0(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("- text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["marker"] == "-"
    assert bullet["indent_level"] == 0


def test_dash_bullet_indent_level_1_with_two_spaces(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("  - text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["indent_level"] == 1


def test_dash_bullet_indent_level_2_with_four_spaces(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("    - text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["indent_level"] == 2


def test_dash_bullet_indent_level_3_with_six_spaces(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("      - text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["indent_level"] == 3


def test_asterisk_bullet_indent_level_0(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("* text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["marker"] == "*"
    assert bullet["indent_level"] == 0


def test_asterisk_bullet_indent_level_1_with_two_spaces(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("  * text", "inline")
    bullet = parsed["blocks"][0]

    assert bullet["type"] == "bullet"
    assert bullet["indent_level"] == 1


def test_mixed_markers_all_include_indent_level(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    content = "\n".join(
        [
            "- dash",
            "  * star",
            "    ◦ circle",
            "      – en-dash",
            "□ box",
        ]
    )
    parsed = parser.parse_markdown(content, "inline")
    bullets = [block for block in parsed["blocks"] if block.get("type") == "bullet"]

    assert [b["marker"] for b in bullets] == ["-", "*", "◦", "–", "□"]
    assert [b["indent_level"] for b in bullets] == [0, 1, 2, 3, 0]


def test_parse_chapter5_has_multiple_indent_levels(project_root, scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    md_path = project_root / "dev" / "hwpx_indent" / "5장.md"
    parsed = parser.parse_markdown(md_path.read_text(encoding="utf-8"), str(md_path))
    bullets = [block for block in parsed["blocks"] if block.get("type") == "bullet"]

    assert bullets
    indent_levels = {bullet["indent_level"] for bullet in bullets}
    assert len(indent_levels) >= 2


def test_indent_resets_after_blank_line(scripts_dir):
    parser = load_module(scripts_dir, "md_parser")
    parsed = parser.parse_markdown("  - level1\n\n- level0", "inline")
    bullets = [block for block in parsed["blocks"] if block.get("type") == "bullet"]

    assert len(bullets) == 2
    assert bullets[0]["indent_level"] == 1
    assert bullets[1]["indent_level"] == 0
