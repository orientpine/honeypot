from __future__ import annotations

# pyright: reportAny=false

import importlib.util
from pathlib import Path

from pytest import MonkeyPatch


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_name_targets_ga_release(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    module = load_module(
        "generate_slide_images_under_test",
        PROJECT_ROOT
        / "plugins"
        / "visual-generator"
        / "skills"
        / "slide-renderer"
        / "scripts"
        / "generate_slide_images.py",
    )

    model_name = module.__dict__["MODEL_NAME"]
    assert isinstance(model_name, str)
    assert model_name == "gemini-3-pro-image"
