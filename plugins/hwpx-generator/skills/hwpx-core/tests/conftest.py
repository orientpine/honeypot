"""
Pytest configuration and fixtures for hwpx-core tests.

Fixtures provide:
- Path resolution (dev/, scripts/, golden/)
- HWPX file opening (zipfile)
- JSON loading and comparison
"""

import json
import zipfile
from pathlib import Path
import pytest


# Project root = 6 levels up from this conftest.py
# plugins/hwpx-generator/skills/hwpx-core/tests/conftest.py
#   -> tests/ (parent)
#   -> hwpx-core/ (parent.parent)
#   -> skills/ (parent.parent.parent)
#   -> hwpx-generator/ (parent.parent.parent.parent)
#   -> plugins/ (parent.parent.parent.parent.parent)
#   -> honeypot (project root) (parent.parent.parent.parent.parent.parent)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def dev_dir():
    """Return the dev/ directory path (contains HWPX files, MD files, images)."""
    return PROJECT_ROOT / "dev"


@pytest.fixture
def scripts_dir():
    """Return the scripts/ directory path within hwpx-core skill."""
    return (
        PROJECT_ROOT / "plugins" / "hwpx-generator" / "skills" / "hwpx-core" / "scripts"
    )


@pytest.fixture
def golden_dir():
    """Return the golden/ directory path (contains reference JSON files)."""
    return PROJECT_ROOT / "dev" / "golden"


@pytest.fixture
def images_dir():
    """Return the images/ directory path (contains PNG files)."""
    return PROJECT_ROOT / "dev" / "images"


@pytest.fixture
def open_hwpx(dev_dir):
    """
    Helper fixture to open HWPX files as zipfiles.

    Usage:
        def test_something(open_hwpx):
            with open_hwpx("(양식) '27년도 전략연구사업 제안서_초안.hwpx") as zf:
                assert "section0.xml" in zf.namelist()
    """

    def _open(filename):
        hwpx_path = dev_dir / filename
        return zipfile.ZipFile(hwpx_path, "r")

    return _open


@pytest.fixture
def load_json():
    """
    Helper fixture to load and parse JSON files.

    Usage:
        def test_something(load_json):
            data = load_json(Path("dev/golden/style_map_초안.json"))
            assert isinstance(data, dict)
    """

    def _load(path):
        if isinstance(path, str):
            path = Path(path)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    return _load


@pytest.fixture
def compare_json():
    """
    Helper fixture to compare two JSON objects with detailed diff output.

    Usage:
        def test_something(compare_json):
            expected = {"key": "value"}
            actual = {"key": "value"}
            compare_json(expected, actual)  # Passes silently
    """

    def _compare(expected, actual, path=""):
        """Recursively compare JSON objects."""
        if type(expected) != type(actual):
            raise AssertionError(
                f"Type mismatch at {path}: expected {type(expected).__name__}, "
                f"got {type(actual).__name__}"
            )

        if isinstance(expected, dict):
            expected_keys = set(expected.keys())
            actual_keys = set(actual.keys())

            if expected_keys != actual_keys:
                missing = expected_keys - actual_keys
                extra = actual_keys - expected_keys
                msg = f"Key mismatch at {path}:"
                if missing:
                    msg += f"\n  Missing: {missing}"
                if extra:
                    msg += f"\n  Extra: {extra}"
                raise AssertionError(msg)

            for key in expected_keys:
                new_path = f"{path}.{key}" if path else key
                _compare(expected[key], actual[key], new_path)

        elif isinstance(expected, list):
            if len(expected) != len(actual):
                raise AssertionError(
                    f"List length mismatch at {path}: expected {len(expected)}, "
                    f"got {len(actual)}"
                )
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                new_path = f"{path}[{i}]"
                _compare(exp_item, act_item, new_path)

        else:
            if expected != actual:
                raise AssertionError(
                    f"Value mismatch at {path}: expected {expected!r}, got {actual!r}"
                )

    return _compare
