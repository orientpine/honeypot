#!/usr/bin/env python3
"""Section XML generators for worksheet and exam formats.

Routes problem data to the appropriate generator:
- generate_worksheet_section_xml: simple 2-column worksheet
- generate_exam_section_xml: standardized Korean exam (학력평가/수능)
- generate_section_xml: router that auto-detects format from data
"""

from pathlib import Path

from lxml import etree
from xml.sax.saxutils import escape

from xml_primitives import (
    IDGen,
    NS,
    SEC_NAMESPACES,
    STYLE,
    make_empty_para,
    make_text_para,
    make_equation_para,
    make_text_with_equation,
    _make_multi_run_para,
)
from exam_helpers import (
    make_secpr_para,
)
from table_layout import (
    make_problem_table,
)


# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
BASE_DIR = TEMPLATES_DIR / "base"


# ---------------------------------------------------------------------------
# Worksheet format section generator (original behavior)
# ---------------------------------------------------------------------------


def generate_worksheet_section_xml(data: dict) -> str:
    """Generate section0.xml for worksheet format (original behavior).

    Args:
        data: Problem data with keys: title, subtitle (optional), problems[]
    """
    idgen = IDGen()
    paragraphs = []

    # Read the secPr block from base section0.xml template
    base_section = BASE_DIR / "Contents" / "section0.xml"
    tree = etree.parse(str(base_section))
    root = tree.getroot()
    first_p = root.find(f"{{{NS['hp']}}}p")
    secpr_para = etree.tostring(first_p, encoding="unicode")
    paragraphs.append(secpr_para)

    # Title
    title = data.get("title", "")
    if title:
        paragraphs.append(
            make_text_para(
                idgen, title, para_pr=STYLE["PARA_TITLE"], char_pr=STYLE["CHAR_TITLE"]
            )
        )

    # Subtitle
    subtitle = data.get("subtitle", "")
    if subtitle:
        paragraphs.append(
            make_text_para(
                idgen,
                subtitle,
                para_pr=STYLE["PARA_TITLE"],
                char_pr=STYLE["CHAR_SUBTITLE"],
            )
        )

    # Info line (name/date/score)
    info = data.get("info", "")
    if info:
        paragraphs.append(
            make_text_para(idgen, info, para_pr=0, char_pr=STYLE["CHAR_BODY"])
        )
    else:
        paragraphs.append(
            make_text_para(
                idgen,
                "이름:                    날짜:           점수:      /      ",
                para_pr=0,
                char_pr=STYLE["CHAR_BODY"],
            )
        )

    paragraphs.append(make_empty_para(idgen))

    # Problems
    problems = data.get("problems", [])
    for i, prob in enumerate(problems, 1):
        # Problem number + text
        prob_text = prob.get("text", "")
        prob_num_text = f"{i}. {prob_text}" if prob_text else f"{i}."
        paragraphs.append(
            make_text_para(
                idgen,
                prob_num_text,
                para_pr=STYLE["PARA_BODY"],
                char_pr=STYLE["CHAR_PROB_NUM"],
            )
        )

        # Main equation (display mode)
        eq = prob.get("equation", "")
        if eq:
            paragraphs.append(
                make_equation_para(
                    idgen, eq, para_pr=STYLE["PARA_EQ"], char_pr=STYLE["CHAR_BODY"]
                )
            )

        # Sub-problems
        sub_problems = prob.get("sub_problems", [])
        for j, sub in enumerate(sub_problems):
            sub_label = f"({j + 1}) "
            sub_text = sub.get("text", "")
            sub_eq = sub.get("equation", "")

            if sub_text and sub_eq:
                paragraphs.append(
                    make_text_with_equation(
                        idgen,
                        f"{sub_label}{sub_text} ",
                        sub_eq,
                        para_pr=STYLE["PARA_CHOICE"],
                        char_pr=STYLE["CHAR_BODY"],
                    )
                )
            elif sub_eq:
                paragraphs.append(
                    make_text_with_equation(
                        idgen,
                        sub_label,
                        sub_eq,
                        para_pr=STYLE["PARA_CHOICE"],
                        char_pr=STYLE["CHAR_BODY"],
                    )
                )
            elif sub_text:
                paragraphs.append(
                    make_text_para(
                        idgen,
                        f"{sub_label}{sub_text}",
                        para_pr=STYLE["PARA_CHOICE"],
                        char_pr=STYLE["CHAR_BODY"],
                    )
                )

        # Choices (multiple choice) — vertical layout
        choices = prob.get("choices", [])
        if choices:
            choice_labels = ["①", "②", "③", "④", "⑤"]
            for k, choice in enumerate(choices):
                label = choice_labels[k] if k < len(choice_labels) else f"({k + 1})"
                if choice.startswith("$") and choice.endswith("$"):
                    eq_script = choice[1:-1]
                    paragraphs.append(
                        make_text_with_equation(
                            idgen,
                            f"{label} ",
                            eq_script,
                            para_pr=STYLE["PARA_CHOICE"],
                            char_pr=STYLE["CHAR_CHOICE"],
                        )
                    )
                else:
                    paragraphs.append(
                        make_text_para(
                            idgen,
                            f"{label} {choice}",
                            para_pr=STYLE["PARA_CHOICE"],
                            char_pr=STYLE["CHAR_CHOICE"],
                        )
                    )

        # Spacing between problems
        paragraphs.append(make_empty_para(idgen))

    # Assemble
    body = "\n  ".join(paragraphs)
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<hs:sec {SEC_NAMESPACES}>
  {body}
</hs:sec>
"""


# ---------------------------------------------------------------------------
# Exam format section generator (학력평가/수능)
# ---------------------------------------------------------------------------


def generate_exam_section_xml(data: dict) -> str:
    """Generate section0.xml for standardized exam format (학력평가/수능).

    Uses invisible 2×2 tables for reliable fixed-height layout:
    1. secPr paragraph (1 column — tables provide 2-col layout)
    2. Exam header paragraphs (full-width)
    3. One 2×2 table per page of 4 problems (invisible borders)
    4. Page break between tables
    5. Footer on last page
    """
    idgen = IDGen()
    paragraphs = []

    # --- secPr paragraph (1 column — tables handle 2-col layout) ---
    paragraphs.append(make_secpr_para(idgen, col_count=1, same_gap=0))

    # --- Exam header (full-width) ---
    year = data.get("year", "")
    month = data.get("month", "")
    grade = data.get("grade", "")
    session = data.get("session", 2)
    subject_area = data.get("subject_area", "수학")

    title = data.get("title", "")
    if not title and year:
        title = f"{year}학년도 {month}월 {grade} 전국연합학력평가 문제지"
    if title:
        title_runs = [
            f'<hp:run charPrIDRef="{STYLE["CHAR_EXAM_TITLE"]}">'
            f"<hp:t>{escape(title)}</hp:t></hp:run>",
        ]
        paragraphs.append(
            _make_multi_run_para(idgen, title_runs, para_pr=STYLE["PARA_EXAM_TITLE"])
        )

    session_runs = [
        f'<hp:run charPrIDRef="{STYLE["CHAR_SESSION"]}">'
        f"<hp:t>제 {session} 교시</hp:t></hp:run>",
    ]
    paragraphs.append(
        _make_multi_run_para(idgen, session_runs, para_pr=STYLE["PARA_SESSION"])
    )

    paragraphs.append(
        make_text_para(
            idgen,
            f"{subject_area} 영역",
            para_pr=STYLE["PARA_SUBJECT"],
            char_pr=STYLE["CHAR_SUBJECT"],
        )
    )

    # Horizontal rule
    paragraphs.append(make_empty_para(idgen, para_pr=STYLE["PARA_HR"], char_pr=0))

    # --- Problem tables (invisible tables, N problems per page) ---
    problems = data.get("problems", [])
    problems_per_page = data.get("problems_per_page", 4)

    # Build image_ids mapping: prob_num → manifest item ID
    # (populated by build() when graphs exist)
    image_ids = data.get("_image_ids", {})

    # Table dimensions
    # Body height: 84186 - 4252(top) - 4252(bottom) = 75682
    # Page 1 header ≈ 15000 → available ≈ 60000 → 2 rows × 25000
    table_width = 48192  # full body width
    first_page_row_height = data.get(
        "first_row_height", 25000
    )  # ~88mm (header eats space)
    normal_row_height = data.get("row_height", 36000)  # ~127mm (full page)

    # Group problems: all pages get 4
    groups = []
    for i in range(0, len(problems), problems_per_page):
        groups.append(problems[i : i + problems_per_page])

    prob_num = 1
    for g_idx, group in enumerate(groups):
        is_first = g_idx == 0
        rh = first_page_row_height if is_first else normal_row_height

        paragraphs.append(
            make_problem_table(
                idgen,
                group,
                prob_num,
                table_width=table_width,
                image_ids=image_ids,
                row_height=rh,
                row_count=2,
                page_break=(not is_first),
            )
        )
        prob_num += len(group)

    # (footer removed — no page numbers needed)

    # Assemble
    body = "\n  ".join(paragraphs)
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<hs:sec {SEC_NAMESPACES}>
  {body}
</hs:sec>
"""


# ---------------------------------------------------------------------------
# Router: selects worksheet or exam format based on data
# ---------------------------------------------------------------------------


def generate_section_xml(data: dict) -> str:
    """Generate section0.xml — routes to worksheet or exam format.

    Default is exam format (학력평가). Only uses worksheet format when
    exam_type is explicitly set to "worksheet".
    """
    exam_type = data.get("exam_type", "학력평가")
    if exam_type == "worksheet":
        return generate_worksheet_section_xml(data)
    return generate_exam_section_xml(data)
