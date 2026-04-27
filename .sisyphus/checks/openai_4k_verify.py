#!/usr/bin/env python3
"""
TDD Verification Harness for visual-generator OpenAI 4K Defaults Migration.

Task T0 from .sisyphus/plans/visual-generator-openai-4k-defaults.md

15 checks codifying the acceptance criteria. Each check prints exactly one of:
    [CHECK-NN] PASS: <one-line summary>
    [CHECK-NN] FAIL: <one-line reason>

Final summary: [SUMMARY] passed=X failed=Y total=15

Exit code = number of failed checks (0 = all green).

Usage:
    python3 .sisyphus/checks/openai_4k_verify.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

OPENAI_SCRIPT = (
    REPO_ROOT
    / "plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py"
)
GEMINI_SCRIPT = (
    REPO_ROOT
    / "plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py"
)
RENDERER_AGENT_OAI = (
    REPO_ROOT / "plugins/visual-generator/agents/renderer-agent-openai.md"
)
SLIDE_RENDERER_SKILL = (
    REPO_ROOT / "plugins/visual-generator/skills/slide-renderer/SKILL.md"
)
OAI_QUALITY_RUBRIC = (
    REPO_ROOT
    / "plugins/visual-generator/skills/slide-renderer/references/openai-quality-rubric.md"
)
VISUAL_GENERATE_CMD = REPO_ROOT / "plugins/visual-generator/commands/visual-generate.md"

OPENAI_SCOPE_FILES = [
    OPENAI_SCRIPT,
    RENDERER_AGENT_OAI,
    SLIDE_RENDERER_SKILL,
    OAI_QUALITY_RUBRIC,
    VISUAL_GENERATE_CMD,
]

# Gemini path — must remain byte-identical to df5e23a baseline
GEMINI_PROTECTED = [
    "plugins/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py",
    "plugins/visual-generator/agents/renderer-agent.md",
    "plugins/visual-generator/agents/prompt-designer.md",
    "plugins/visual-generator/skills/theme-concept/SKILL.md",
    "plugins/visual-generator/skills/theme-gov/SKILL.md",
    "plugins/visual-generator/skills/theme-seminar/SKILL.md",
    "plugins/visual-generator/skills/theme-whatif/SKILL.md",
    "plugins/visual-generator/skills/theme-pitch/SKILL.md",
    "plugins/visual-generator/skills/theme-comparison/SKILL.md",
]

GEMINI_BASELINE_COMMIT = "df5e23a"

PLUGIN_JSON = REPO_ROOT / "plugins/visual-generator/.claude-plugin/plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin/marketplace.json"
README_MD = REPO_ROOT / "README.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

PLUGIN_JSON_ALLOWED_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "commands",
    "agents",
    "hooks",
    "mcpServers",
    "lspServers",
    "outputStyles",
    "monitors",
    "userConfig",
    "channels",
    "dependencies",
}

PRICING_PATTERNS = [
    r"\$0\.165",
    r"\$0\.05",
    r"\$0\.215",
    r"예상 비용",
    r"비용 추정",
    r"cost_estimate",
]

NEUTRAL_NOTICE = "비용은 OpenAI 콘솔"

# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------
results: list[tuple[str, bool, str]] = []


def record(check_id: str, ok: bool, msg: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{check_id}] {status}: {msg}")
    results.append((check_id, ok, msg))


def read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"  (read error on {p}: {exc})", file=sys.stderr)
        return None


def run_cmd(
    args: list[str], env_extra: dict | None = None, timeout: int = 30
) -> tuple[int, str, str]:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as exc:
        return 127, "", str(exc)


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------
def check_01_ast_parse() -> None:
    """OpenAI script AST parses cleanly."""
    src = read_text(OPENAI_SCRIPT)
    if src is None:
        record("CHECK-01", False, f"could not read {OPENAI_SCRIPT.name}")
        return
    import ast

    try:
        ast.parse(src)
        record("CHECK-01", True, f"AST parse OK ({len(src.splitlines())} lines)")
    except SyntaxError as exc:
        record("CHECK-01", False, f"SyntaxError {exc.lineno}:{exc.offset}: {exc.msg}")


def _openai_help() -> tuple[int, str, str]:
    return run_cmd(
        [sys.executable, str(OPENAI_SCRIPT), "--help"],
        env_extra={"OPENAI_API_KEY": "dummy"},
    )


def check_02_cli_flags_present() -> None:
    """--help shows --size, --quality, --model, --eval-model."""
    rc, out, err = _openai_help()
    combined = (out or "") + (err or "")
    if rc != 0:
        record("CHECK-02", False, f"--help exited {rc}: {(err or out)[:120]!r}")
        return
    missing = [
        f
        for f in ("--size", "--quality", "--model", "--eval-model")
        if f not in combined
    ]
    if missing:
        record("CHECK-02", False, f"missing flags: {missing}")
    else:
        record("CHECK-02", True, "all four CLI flags present in --help")


def check_03_default_values() -> None:
    """--help advertises locked defaults: 3840x2160, high, gpt-image-2, gpt-5.5."""
    rc, out, err = _openai_help()
    combined = (out or "") + (err or "")
    if rc != 0:
        record("CHECK-03", False, f"--help exited {rc}")
        return
    expected = ["3840x2160", "high", "gpt-image-2", "gpt-5.5"]
    missing = [v for v in expected if v not in combined]
    if missing:
        record("CHECK-03", False, f"missing default values in --help: {missing}")
    else:
        record("CHECK-03", True, f"all locked defaults visible: {expected}")


def check_04_no_pricing() -> None:
    """No pricing literals in OpenAI-scope files."""
    hits = []
    for f in OPENAI_SCOPE_FILES:
        text = read_text(f)
        if text is None:
            continue
        for pat in PRICING_PATTERNS:
            for m in re.finditer(pat, text):
                line_no = text[: m.start()].count("\n") + 1
                hits.append(f"{f.relative_to(REPO_ROOT)}:{line_no}: {pat}")
    if hits:
        sample = hits[:3]
        record(
            "CHECK-04", False, f"{len(hits)} pricing literal(s) found; first: {sample}"
        )
    else:
        record("CHECK-04", True, "no pricing literals across 5 OpenAI-scope files")


def check_05_neutral_notice_present() -> None:
    """'비용은 OpenAI 콘솔' appears at least 2 times across OpenAI-scope files."""
    total = 0
    locations = []
    for f in OPENAI_SCOPE_FILES:
        text = read_text(f)
        if text is None:
            continue
        cnt = text.count(NEUTRAL_NOTICE)
        if cnt:
            total += cnt
            locations.append(f"{f.name}({cnt})")
    if total >= 2:
        record("CHECK-05", True, f"neutral notice found {total} time(s): {locations}")
    else:
        record(
            "CHECK-05",
            False,
            f"neutral notice count={total} (need ≥2); locations: {locations}",
        )


def check_06_fallback_chain() -> None:
    """Script contains all three model literals: gpt-5.5, gpt-5, gpt-4o."""
    text = read_text(OPENAI_SCRIPT)
    if text is None:
        record("CHECK-06", False, "could not read script")
        return
    # Strip comments and docstrings to ensure not all in comments
    import ast

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        record("CHECK-06", False, f"AST parse failed: {exc}")
        return
    # Collect all string constants (not docstrings)
    code_strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            code_strings.append(node.value)
    haystack = "\n".join(code_strings)
    needed = ["gpt-5.5", "gpt-5", "gpt-4o"]
    # Note: 'gpt-5' is substring of 'gpt-5.5'. Check via word-boundary regex.
    found = {}
    for n in needed:
        # match exact token (followed by non-version-char or end)
        pat = re.compile(rf"\b{re.escape(n)}(?![\.\d])")
        found[n] = bool(pat.search(haystack))
    missing = [n for n, v in found.items() if not v]
    if missing:
        record(
            "CHECK-06", False, f"missing model literal(s) in code strings: {missing}"
        )
    else:
        record(
            "CHECK-06",
            True,
            f"all three fallback models present as code strings: {needed}",
        )


def check_07_no_1536x1024() -> None:
    """No '1536x1024' literal in any OpenAI-scope file."""
    hits = []
    for f in OPENAI_SCOPE_FILES:
        text = read_text(f)
        if text is None:
            continue
        for m in re.finditer(r"1536x1024", text):
            line_no = text[: m.start()].count("\n") + 1
            hits.append(f"{f.relative_to(REPO_ROOT)}:{line_no}")
    if hits:
        sample = hits[:3]
        record(
            "CHECK-07",
            False,
            f"{len(hits)} '1536x1024' literal(s) found; first: {sample}",
        )
    else:
        record("CHECK-07", True, "no '1536x1024' literals across 5 OpenAI-scope files")


def check_08_dead_code_removed() -> None:
    """Tautological branch 'OUTPUT_FORMAT == \"jpeg\"' removed from script."""
    text = read_text(OPENAI_SCRIPT)
    if text is None:
        record("CHECK-08", False, "could not read script")
        return
    pat = re.compile(r'OUTPUT_FORMAT\s*==\s*"jpeg"')
    matches = list(pat.finditer(text))
    if matches:
        line_nos = [text[: m.start()].count("\n") + 1 for m in matches]
        record("CHECK-08", False, f"tautology still present at lines {line_nos}")
    else:
        record("CHECK-08", True, "dead-code tautology removed")


def check_09_skill_md_frontmatter() -> None:
    """SKILL.md frontmatter description mentions both Gemini and OpenAI; ≤1024 chars."""
    text = read_text(SLIDE_RENDERER_SKILL)
    if text is None:
        record("CHECK-09", False, "could not read SKILL.md")
        return
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        record("CHECK-09", False, "no YAML frontmatter found")
        return
    fm = m.group(1)
    desc_m = re.search(r"^description:\s*(.+?)\s*$", fm, re.MULTILINE)
    if not desc_m:
        record("CHECK-09", False, "no 'description:' field in frontmatter")
        return
    desc = desc_m.group(1).strip()
    # Strip outer quotes if present
    if (desc.startswith('"') and desc.endswith('"')) or (
        desc.startswith("'") and desc.endswith("'")
    ):
        desc = desc[1:-1]
    has_gemini = "Gemini" in desc
    has_openai = "OpenAI" in desc
    length_ok = len(desc) <= 1024
    if has_gemini and has_openai and length_ok:
        record(
            "CHECK-09", True, f"frontmatter mentions both renderers (len={len(desc)})"
        )
    else:
        reasons = []
        if not has_gemini:
            reasons.append("missing 'Gemini'")
        if not has_openai:
            reasons.append("missing 'OpenAI'")
        if not length_ok:
            reasons.append(f"length {len(desc)} > 1024")
        record("CHECK-09", False, "; ".join(reasons))


def check_10_gemini_protected_diff() -> None:
    """Gemini protected files unchanged vs df5e23a."""
    rc, out, err = run_cmd(
        ["git", "diff", "--name-only", GEMINI_BASELINE_COMMIT, "--", *GEMINI_PROTECTED]
    )
    if rc != 0:
        record("CHECK-10", False, f"git diff failed (rc={rc}): {err.strip()[:120]}")
        return
    changed = [line for line in out.strip().splitlines() if line]
    if changed:
        record("CHECK-10", False, f"Gemini files modified: {changed}")
    else:
        record(
            "CHECK-10",
            True,
            f"all {len(GEMINI_PROTECTED)} Gemini protected files byte-identical to {GEMINI_BASELINE_COMMIT}",
        )


def check_11_gemini_help_works() -> None:
    """Gemini script --help works (with dummy GEMINI_API_KEY)."""
    rc, out, err = run_cmd(
        [sys.executable, str(GEMINI_SCRIPT), "--help"],
        env_extra={"GEMINI_API_KEY": "dummy"},
    )
    if rc == 0:
        record(
            "CHECK-11",
            True,
            f"Gemini --help exits 0 ({len((out or '').splitlines())} lines)",
        )
    else:
        record(
            "CHECK-11", False, f"Gemini --help rc={rc}: {(err or out).strip()[:150]}"
        )


def check_12_plugin_json_schema() -> None:
    """plugin.json has only allowed fields and a semver version."""
    try:
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        record("CHECK-12", False, f"plugin.json read/parse error: {exc}")
        return
    extra = set(data.keys()) - PLUGIN_JSON_ALLOWED_FIELDS
    if extra:
        record("CHECK-12", False, f"non-whitelist fields: {sorted(extra)}")
        return
    version = data.get("version", "")
    if not re.match(r"^\d+\.\d+\.\d+(?:[-+].+)?$", version):
        record("CHECK-12", False, f"version not semver: {version!r}")
        return
    record("CHECK-12", True, f"schema clean; version={version}")


def check_13_version_sync() -> None:
    """plugin.json.version == marketplace entry version."""
    try:
        plugin_v = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
        mp = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        record("CHECK-13", False, f"read/parse error: {exc}")
        return
    entries = [p for p in mp.get("plugins", []) if p.get("name") == "visual-generator"]
    if not entries:
        record("CHECK-13", False, "no 'visual-generator' entry in marketplace.json")
        return
    entry_v = entries[0].get("version", "(missing)")
    if entry_v == plugin_v:
        record("CHECK-13", True, f"versions agree: {plugin_v}")
    else:
        record(
            "CHECK-13",
            False,
            f"plugin.json={plugin_v!r} != marketplace entry={entry_v!r}",
        )


def check_14_readme_today_row() -> None:
    """README.md 변경 이력 table contains a row dated today."""
    today = date.today().isoformat()
    text = read_text(README_MD)
    if text is None:
        record("CHECK-14", False, "could not read README.md")
        return
    if today in text:
        record("CHECK-14", True, f"README.md contains today's date ({today})")
    else:
        record("CHECK-14", False, f"today's date ({today}) not found in README.md")


def check_15_agents_md_today() -> None:
    """AGENTS.md **Generated:** matches today."""
    today = date.today().isoformat()
    text = read_text(AGENTS_MD)
    if text is None:
        record("CHECK-15", False, "could not read AGENTS.md")
        return
    m = re.search(r"\*\*Generated:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if not m:
        record("CHECK-15", False, "no '**Generated:** YYYY-MM-DD' line found")
        return
    found_date = m.group(1)
    if found_date == today:
        record("CHECK-15", True, f"AGENTS.md Generated date matches today ({today})")
    else:
        record("CHECK-15", False, f"AGENTS.md Generated={found_date}, today={today}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
CHECKS = [
    check_01_ast_parse,
    check_02_cli_flags_present,
    check_03_default_values,
    check_04_no_pricing,
    check_05_neutral_notice_present,
    check_06_fallback_chain,
    check_07_no_1536x1024,
    check_08_dead_code_removed,
    check_09_skill_md_frontmatter,
    check_10_gemini_protected_diff,
    check_11_gemini_help_works,
    check_12_plugin_json_schema,
    check_13_version_sync,
    check_14_readme_today_row,
    check_15_agents_md_today,
]


def main() -> int:
    for fn in CHECKS:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            cid = fn.__name__.split("_", 2)[1]
            record(f"CHECK-{cid.upper()}", False, f"harness exception: {exc!r}")

    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print()
    print(f"[SUMMARY] passed={passed} failed={failed} total={len(results)}")
    if failed:
        print(f"[FAILING] {[cid for cid, ok, _ in results if not ok]}")
    return failed


if __name__ == "__main__":
    sys.exit(main())
