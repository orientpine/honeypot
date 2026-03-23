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


@pytest.fixture
def make_header_xml():
    """Create synthetic header.xml bytes with style definitions.
    
    Usage: header_bytes = make_header_xml(char_styles, para_styles)
      char_styles: list of (id, fontSize, bold=False)
      para_styles: list of (id, align="JUSTIFY")
    """
    def _make(char_styles=None, para_styles=None):
        char_styles = char_styles or []
        para_styles = para_styles or []
        
        char_prs = ""
        for cid, fs, *rest in char_styles:
            bold = rest[0] if rest else False
            bold_attr = ' bold="1"' if bold else ''
            char_prs += f'<hh:charPr id="{cid}"><hh:fontSize size="{fs}" sizeAutomatic="0" lang="HANGUL"/>{bold_attr}</hh:charPr>'
        
        para_prs = ""
        for pid, *rest in para_styles:
            align = rest[0] if rest else "JUSTIFY"
            para_prs += f'<hh:paraPr id="{pid}"><hh:alignment type="{align}"/></hh:paraPr>'
        
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
            '<hs:head xmlns:hs="http://www.hancom.co.kr/hwpml/2011/head/head"'
            ' xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head/head">'
            f'<hh:docPrList><hh:charPrList>{char_prs}</hh:charPrList>'
            f'<hh:paraPrList>{para_prs}</hh:paraPrList></hh:docPrList>'
            '</hs:head>'
        )
        return xml.encode('utf-8')
    return _make


@pytest.fixture
def make_section_xml():
    """Create synthetic section0.xml bytes from a list of paragraph strings.
    
    Usage: section_bytes = make_section_xml(paragraphs)
      paragraphs: list of raw <hp:p>...</hp:p> strings
    """
    def _make(paragraphs=None):
        paragraphs = paragraphs or []
        body = "".join(paragraphs)
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section/section"'
            ' xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph/paragraph">'
            + body +
            '</hs:sec>'
        )
        return xml.encode('utf-8')
    return _make


@pytest.fixture
def make_test_hwpx(make_section_xml, make_header_xml, tmp_path):
    """Create synthetic HWPX file with N chapters, known style IDs.
    
    Usage: hwpx_path = make_test_hwpx(chapters=3, char_styles=[(1,1500,True),(2,1000,False)], para_styles=[(10,"JUSTIFY")])
    Returns: pathlib.Path to the .hwpx file
    """
    def _make(chapters=3, char_styles=None, para_styles=None, extra_paragraphs=None):
        import sys
        scripts_path = (
            Path(__file__).parent.parent / "scripts"
        )
        sys.path.insert(0, str(scripts_path))
        from zip_surgery import make_paragraph, make_empty_paragraph
        
        # Default styles: ID 1 = H1 (fontSize=1500, bold), ID 2 = body (fontSize=1000)
        if char_styles is None:
            char_styles = [(1, 1500, True), (2, 1000, False)]
        if para_styles is None:
            para_styles = [(10, "JUSTIFY"), (20, "JUSTIFY")]
        
        paragraphs = []
        
        # Cover page paragraph (before first H1)
        paragraphs.append(make_paragraph("100", "표지 내용", paraPrIDRef="10", charPrIDRef="2"))
        
        for ch_num in range(1, chapters + 1):
            # H1 heading for this chapter
            heading_text = f"{ch_num}. 챕터 {ch_num} 제목"
            paragraphs.append(make_paragraph(
                str(1000 + ch_num),
                heading_text,
                paraPrIDRef="20",
                charPrIDRef="1",  # ID 1 = H1 style
            ))
            # Body paragraph
            paragraphs.append(make_paragraph(
                str(2000 + ch_num),
                f"챕터 {ch_num}의 본문 내용입니다.",
                paraPrIDRef="10",
                charPrIDRef="2",
            ))
            if extra_paragraphs and ch_num in extra_paragraphs:
                for ep in extra_paragraphs[ch_num]:
                    paragraphs.append(ep)
        
        section_bytes = make_section_xml(paragraphs)
        header_bytes = make_header_xml(char_styles, para_styles)
        
        # Build HWPX (ZIP)
        hwpx_path = tmp_path / "test_synthetic.hwpx"
        with zipfile.ZipFile(str(hwpx_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Contents/section0.xml", section_bytes)
            zf.writestr("Contents/header.xml", header_bytes)
            zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types/>')
        
        return hwpx_path
    return _make
