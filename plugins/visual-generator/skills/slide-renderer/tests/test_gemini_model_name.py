from __future__ import annotations

# pyright: reportAny=false

import importlib.util
from pathlib import Path

import pytest
from pytest import MonkeyPatch


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
SCRIPT_PATH = (
    PROJECT_ROOT
    / "plugins"
    / "visual-generator"
    / "skills"
    / "slide-renderer"
    / "scripts"
    / "generate_slide_images.py"
)


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_name_targets_ga_release(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    module = load_module("generate_slide_images_under_test", SCRIPT_PATH)

    model_name = module.__dict__["MODEL_NAME"]
    assert isinstance(model_name, str)
    assert model_name == "gemini-3-pro-image"


def test_model_name_uses_gemini_model_env_override(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "gemini-nano-banana-2.1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    module = load_module("generate_slide_images_under_test", SCRIPT_PATH)

    assert module.__dict__["MODEL_NAME"] == "gemini-nano-banana-2.1"


def test_model_flag_selects_nano_banana_option(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    module = load_module("generate_slide_images_under_test", SCRIPT_PATH)
    monkeypatch.setattr(
        "sys.argv",
        ["generate_slide_images.py", "-p", str(tmp_path), "-o", str(tmp_path / "out"),
         "--model", "gemini-nano-banana-2.1"],
    )

    # No numbered prompt files, so the run ends before any API call.
    with pytest.raises(SystemExit) as exc:
        module.main()

    assert exc.value.code == 0
    assert module.__dict__["MODEL_NAME"] == "gemini-nano-banana-2.1"


@pytest.mark.parametrize(
    ("env_model", "cli_model"),
    [(None, "gemini-unknown-model"), ("gemini-unknown-model", None)],
)
def test_unsupported_model_is_rejected(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    env_model: str | None,
    cli_model: str | None,
) -> None:
    if env_model is None:
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
    else:
        monkeypatch.setenv("GEMINI_MODEL", env_model)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    module = load_module("generate_slide_images_under_test", SCRIPT_PATH)
    argv = ["generate_slide_images.py", "-p", str(tmp_path), "-o", str(tmp_path / "out")]
    if cli_model is not None:
        argv += ["--model", cli_model]
    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 2
