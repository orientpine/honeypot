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

    # Then: it selects the GA model
    assert module.MODEL_NAME == "gemini-3-pro-image"


def test_model_name_uses_gemini_model_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a custom model override and a dummy key for import-time configuration
    monkeypatch.setenv("GEMINI_MODEL", "custom-test-model")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    # When: the script module reads its environment during import
    module = _load_generate_images_module()

    # Then: it preserves the explicit override
    assert module.MODEL_NAME == "custom-test-model"
