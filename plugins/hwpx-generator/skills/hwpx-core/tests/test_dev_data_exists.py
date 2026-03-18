"""
Smoke tests for hwpx-core development data.

Verifies that all required dev files exist and are readable:
- 2 HWPX files (작성, 초안)
- 2 Markdown files (3장, 4장)
- 15 PNG image files
- 3 Golden reference JSON files
"""

import json
import os
from pathlib import Path


class TestDevDirectoryExists:
    """Test that dev/ directory exists."""

    def test_dev_dir_exists(self, dev_dir):
        """dev/ directory should exist."""
        assert dev_dir.exists(), f"dev/ directory not found at {dev_dir}"
        assert dev_dir.is_dir(), f"dev/ is not a directory: {dev_dir}"


class TestHWPXFiles:
    """Test that HWPX template files exist and are readable."""

    def test_hwpx_작성_exists(self, dev_dir):
        """HWPX 작성 file should exist."""
        hwpx_path = dev_dir / "(양식) '27년도 전략연구사업 제안서_작성.hwpx"
        assert hwpx_path.exists(), f"HWPX 작성 file not found at {hwpx_path}"
        assert hwpx_path.is_file(), f"HWPX 작성 is not a file: {hwpx_path}"
        assert hwpx_path.stat().st_size > 0, f"HWPX 작성 file is empty: {hwpx_path}"

    def test_hwpx_초안_exists(self, dev_dir):
        """HWPX 초안 file should exist."""
        hwpx_path = dev_dir / "(양식) '27년도 전략연구사업 제안서_초안.hwpx"
        assert hwpx_path.exists(), f"HWPX 초안 file not found at {hwpx_path}"
        assert hwpx_path.is_file(), f"HWPX 초안 is not a file: {hwpx_path}"
        assert hwpx_path.stat().st_size > 0, f"HWPX 초안 file is empty: {hwpx_path}"


class TestMarkdownFiles:
    """Test that Markdown content files exist."""

    def test_3장_md_exists(self, dev_dir):
        """3장.md file should exist."""
        md_path = dev_dir / "3장.md"
        assert md_path.exists(), f"3장.md not found at {md_path}"
        assert md_path.is_file(), f"3장.md is not a file: {md_path}"
        assert md_path.stat().st_size > 0, f"3장.md file is empty: {md_path}"

    def test_4장_md_exists(self, dev_dir):
        """4장.md file should exist."""
        md_path = dev_dir / "4장.md"
        assert md_path.exists(), f"4장.md not found at {md_path}"
        assert md_path.is_file(), f"4장.md is not a file: {md_path}"
        assert md_path.stat().st_size > 0, f"4장.md file is empty: {md_path}"


class TestImagesDirectory:
    """Test that images/ directory and PNG files exist."""

    def test_images_dir_exists(self, images_dir):
        """images/ directory should exist."""
        assert images_dir.exists(), f"images/ directory not found at {images_dir}"
        assert images_dir.is_dir(), f"images/ is not a directory: {images_dir}"

    def test_15_png_files_exist(self, images_dir):
        """Exactly 15 PNG files should exist in images/."""
        png_files = list(images_dir.glob("*.png"))
        assert len(png_files) == 15, (
            f"Expected 15 PNG files, found {len(png_files)} in {images_dir}\n"
            f"Files: {[f.name for f in png_files]}"
        )

    def test_png_files_are_readable(self, images_dir):
        """All PNG files should be readable and non-empty."""
        png_files = sorted(images_dir.glob("*.png"))
        assert len(png_files) == 15, f"Expected 15 PNG files, found {len(png_files)}"

        for png_file in png_files:
            assert png_file.is_file(), f"PNG file is not a file: {png_file}"
            size = png_file.stat().st_size
            assert size > 0, f"PNG file is empty: {png_file}"

    def test_png_files_naming_convention(self, images_dir):
        """PNG files should follow naming convention: NN_*.png."""
        png_files = sorted(images_dir.glob("*.png"))
        expected_names = [
            "01_비전_개념도.png",
            "02_최종_연구목표_체계도.png",
            "03_사업_추진체계도.png",
            "04_핵심_연구내용_전체_구조도.png",
            "05_파운데이션_모델_개념도.png",
            "06_멀티모달_센서_융합_파이프라인.png",
            "07_파인튜닝_경량화_전략.png",
            "08_전문가_AI_모델_플랫폼.png",
            "09_숙련자_노하우_디지털화.png",
            "10_LLM_작업지시_해석.png",
            "11_장착형_자율화_모듈_구성도.png",
            "12_장비별_적용_예시.png",
            "13_통합_운영_플랫폼.png",
            "14_3대분야_실증_체계도.png",
            "15_세부기술_통합_연계.png",
        ]

        actual_names = [f.name for f in png_files]
        assert actual_names == expected_names, (
            f"PNG file names don't match expected convention.\n"
            f"Expected: {expected_names}\n"
            f"Actual: {actual_names}"
        )


class TestGoldenDirectory:
    """Test that golden/ directory and reference JSON files exist."""

    def test_golden_dir_exists(self, golden_dir):
        """golden/ directory should exist."""
        assert golden_dir.exists(), f"golden/ directory not found at {golden_dir}"
        assert golden_dir.is_dir(), f"golden/ is not a directory: {golden_dir}"

    def test_style_map_초안_json_exists(self, golden_dir):
        """style_map_초안.json should exist."""
        json_path = golden_dir / "style_map_초안.json"
        assert json_path.exists(), f"style_map_초안.json not found at {json_path}"
        assert json_path.is_file(), f"style_map_초안.json is not a file: {json_path}"
        assert json_path.stat().st_size > 0, (
            f"style_map_초안.json is empty: {json_path}"
        )

    def test_style_map_초안_json_valid(self, golden_dir, load_json):
        """style_map_초안.json should be valid JSON."""
        json_path = golden_dir / "style_map_초안.json"
        data = load_json(json_path)
        assert isinstance(data, dict), (
            f"style_map_초안.json should be a dict, got {type(data)}"
        )

    def test_image_structures_json_exists(self, golden_dir):
        """image_structures.json should exist."""
        json_path = golden_dir / "image_structures.json"
        assert json_path.exists(), f"image_structures.json not found at {json_path}"
        assert json_path.is_file(), f"image_structures.json is not a file: {json_path}"
        assert json_path.stat().st_size > 0, (
            f"image_structures.json is empty: {json_path}"
        )

    def test_image_structures_json_valid(self, golden_dir, load_json):
        """image_structures.json should be valid JSON."""
        json_path = golden_dir / "image_structures.json"
        data = load_json(json_path)
        assert isinstance(data, dict), (
            f"image_structures.json should be a dict, got {type(data)}"
        )

    def test_bullet_styles_json_exists(self, golden_dir):
        """bullet_styles.json should exist."""
        json_path = golden_dir / "bullet_styles.json"
        assert json_path.exists(), f"bullet_styles.json not found at {json_path}"
        assert json_path.is_file(), f"bullet_styles.json is not a file: {json_path}"
        assert json_path.stat().st_size > 0, f"bullet_styles.json is empty: {json_path}"

    def test_bullet_styles_json_valid(self, golden_dir, load_json):
        """bullet_styles.json should be valid JSON."""
        json_path = golden_dir / "bullet_styles.json"
        data = load_json(json_path)
        assert isinstance(data, dict), (
            f"bullet_styles.json should be a dict, got {type(data)}"
        )


class TestScriptsDirectory:
    """Test that scripts/ directory exists."""

    def test_scripts_dir_exists(self, scripts_dir):
        """scripts/ directory should exist."""
        assert scripts_dir.exists(), f"scripts/ directory not found at {scripts_dir}"
        assert scripts_dir.is_dir(), f"scripts/ is not a directory: {scripts_dir}"
