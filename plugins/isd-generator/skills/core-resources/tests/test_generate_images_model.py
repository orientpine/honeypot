from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "generate_images.py"


def _load_generate_images_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "generate_images_under_test", SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_name_defaults_to_ga_model_when_env_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: no model override and a dummy key for import-time configuration
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    # When: the script module reads its environment during import
    module = _load_generate_images_module()

    # Then: it selects the Pro-tier default model
    assert module.MODEL_NAME == "gemini-3-pro-image"


def test_model_name_uses_gemini_model_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a custom model override and a dummy key for import-time configuration
    monkeypatch.setenv("GEMINI_MODEL", "gemini-nano-banana-2.1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    # When: the script module reads its environment during import
    module = _load_generate_images_module()

    # Then: it preserves the explicit override
    assert module.MODEL_NAME == "gemini-nano-banana-2.1"


def test_model_flag_selects_nano_banana_option(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Given: no env override, an empty prompts dir and --model set to the 2.1 option
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    module = _load_generate_images_module()
    monkeypatch.setattr(
        "sys.argv",
        ["generate_images.py", "-p", str(tmp_path), "-o", str(tmp_path / "out"),
         "--model", "gemini-nano-banana-2.1"],
    )

    # When: the CLI runs (no prompt files, so no API call is made)
    with pytest.raises(SystemExit) as exc:
        module.main()

    # Then: it exits cleanly with the selected model
    assert exc.value.code == 0
    assert module.MODEL_NAME == "gemini-nano-banana-2.1"


@pytest.mark.parametrize(
    ("env_model", "cli_model"),
    [(None, "gemini-unknown-model"), ("gemini-unknown-model", None)],
)
def test_unsupported_model_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    env_model: str | None,
    cli_model: str | None,
) -> None:
    # Given: an unsupported model via --model or GEMINI_MODEL
    if env_model is None:
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
    else:
        monkeypatch.setenv("GEMINI_MODEL", env_model)
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    module = _load_generate_images_module()
    argv = ["generate_images.py", "-p", str(tmp_path), "-o", str(tmp_path / "out")]
    if cli_model is not None:
        argv += ["--model", cli_model]
    monkeypatch.setattr("sys.argv", argv)

    # When / Then: argparse rejects it with a usage error
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code == 2
