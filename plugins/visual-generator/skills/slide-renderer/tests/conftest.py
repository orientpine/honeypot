from __future__ import annotations

# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import importlib.util
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def scripts_dir() -> Path:
    return (
        PROJECT_ROOT
        / "plugins"
        / "visual-generator"
        / "skills"
        / "slide-renderer"
        / "scripts"
    )


@pytest.fixture
def openai_renderer_module(scripts_dir):
    module = load_module(
        "generate_slide_images_openai_under_test",
        scripts_dir / "generate_slide_images_openai.py",
    )
    module._resolved_eval_model = None
    module._eval_first_success_logged = False
    return module
