from __future__ import annotations

import importlib.util
from pathlib import Path


def load_xml_writer_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("xml_writer", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_styles() -> dict:
    return {
        "heading_1": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "heading_2": {"charPrIDRef": "49", "paraPrIDRef": "39"},
        "body": {"charPrIDRef": "48", "paraPrIDRef": "38"},
        "bullet": {
            "charPrIDRef": "36",
            "paraPrIDRef": "91",
            "left_margin": 0,
            "indent": -1584,
        },
        "bold": {"charPrIDRef": "48"},
        "table_header": {
            "charPrIDRef": "95",
            "paraPrIDRef": "71",
            "borderFillIDRef": "45",
        },
        "table_cell": {
            "charPrIDRef": "136",
            "paraPrIDRef": "98",
            "borderFillIDRef": "42",
        },
        "table_width": 42520,
        "image_placeholder": {"paraPrIDRef": "0", "charPrIDRef": "0"},
    }


def test_table_cell_xml_adds_colspan_rowspan_attributes(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    xml = writer.table_cell_xml(
        text="병합 셀",
        row_index=0,
        col_index=0,
        width=10000,
        colspan=3,
        rowspan=2,
        is_header=False,
        ids=writer.IdGenerator(),
        styles=sample_styles(),
    )

    assert '<hp:tc borderFillIDRef="42" colSpan="3" rowSpan="2">' in xml
    assert '<hp:cellSpan colSpan="3" rowSpan="2"/>' in xml


def test_build_table_reflects_merge_info_from_cell_dict(scripts_dir):
    writer = load_xml_writer_module(scripts_dir / "xml_writer.py")
    parsed = {
        "blocks": [
            {
                "type": "table",
                "headers": ["A", "B", "C"],
                "rows": [
                    [
                        {"text": "병합", "merge": {"colSpan": 2, "rowSpan": 2}},
                        "",
                        "일반",
                    ]
                ],
                "col_count": 3,
            }
        ]
    }

    xml = writer.build_fragment(parsed, sample_styles())

    assert 'colSpan="2" rowSpan="2"' in xml
