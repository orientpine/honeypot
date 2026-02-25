#!/usr/bin/env python3
"""Invisible-border table layout for exam format 2×2 problem grids.

Provides:
- _make_problem_cell_content: paragraph XML for a single problem cell
- make_problem_table: full 2×N table with invisible borders
"""

from xml_primitives import (
    IDGen,
    STYLE,
    make_empty_para,
    make_text_para,
    make_equation_para,
    make_text_with_equation,
)
from exam_helpers import (
    make_exam_problem_para,
    make_picture_para,
)


def _make_problem_cell_content(
    idgen: IDGen,
    prob_num: int,
    prob: dict,
    prefix_label: str | None = None,
    image_id: str | None = None,
) -> str:
    """Generate paragraph XMLs for a single problem inside a table cell.

    Args:
        image_id: If this problem has a graph, the manifest item ID for the PNG.
    """
    paras = []

    if prefix_label:
        paras.append(
            make_text_para(
                idgen,
                f" {prefix_label} ",
                para_pr=STYLE["PARA_SECTION_LABEL"],
                char_pr=STYLE["CHAR_BODY"],
            )
        )

    prob_text = prob.get("text", "")
    prob_eq = prob.get("equation", "")
    points = prob.get("points")
    has_inline_eq = bool(prob_eq and prob_text)
    has_standalone_eq = bool(prob_eq and not prob_text)

    paras.append(
        make_exam_problem_para(
            idgen,
            prob_num,
            prob_text,
            points=points,
            equation=prob_eq if has_inline_eq else None,
        )
    )

    if has_standalone_eq:
        paras.append(
            make_equation_para(
                idgen, prob_eq, para_pr=STYLE["PARA_EQ"], char_pr=STYLE["CHAR_BODY"]
            )
        )

    for j, sub in enumerate(prob.get("sub_problems", [])):
        sub_label = f"({j + 1}) "
        sub_text = sub.get("text", "")
        sub_eq = sub.get("equation", "")
        if sub_text and sub_eq:
            paras.append(
                make_text_with_equation(
                    idgen,
                    f"{sub_label}{sub_text} ",
                    sub_eq,
                    para_pr=STYLE["PARA_CHOICE"],
                    char_pr=STYLE["CHAR_BODY"],
                )
            )
        elif sub_eq:
            paras.append(
                make_text_with_equation(
                    idgen,
                    sub_label,
                    sub_eq,
                    para_pr=STYLE["PARA_CHOICE"],
                    char_pr=STYLE["CHAR_BODY"],
                )
            )
        elif sub_text:
            paras.append(
                make_text_para(
                    idgen,
                    f"{sub_label}{sub_text}",
                    para_pr=STYLE["PARA_CHOICE"],
                    char_pr=STYLE["CHAR_BODY"],
                )
            )

    # Graph image (inserted before choices if present)
    if image_id:
        graph_spec = prob.get("graph", {})
        # Default: ~40mm × 40mm = 11340 HU × 11340 HU
        gw = graph_spec.get("width_hu", 11340)
        gh = graph_spec.get("height_hu", 11340)
        paras.append(make_picture_para(idgen, image_id, width_hu=gw, height_hu=gh))

    choices = prob.get("choices", [])
    choice_labels = ["①", "②", "③", "④", "⑤"]
    for k, choice in enumerate(choices):
        label = choice_labels[k] if k < len(choice_labels) else f"({k + 1})"
        if choice.startswith("$") and choice.endswith("$"):
            eq_script = choice[1:-1]
            paras.append(
                make_text_with_equation(
                    idgen,
                    f"{label} ",
                    eq_script,
                    para_pr=STYLE["PARA_CHOICE"],
                    char_pr=STYLE["CHAR_CHOICE"],
                )
            )
        else:
            paras.append(
                make_text_para(
                    idgen,
                    f"{label} {choice}",
                    para_pr=STYLE["PARA_CHOICE"],
                    char_pr=STYLE["CHAR_CHOICE"],
                )
            )

    return "\n".join(paras)


def make_problem_table(
    idgen: IDGen,
    problems_in_group: list,
    start_num: int,
    table_width: int = 48192,
    row_height: int = 32000,
    row_count: int = 2,
    page_break: bool = False,
    image_ids: dict | None = None,
) -> str:
    """Generate an invisible-border table for exam problems.

    Table layout mirrors standard Korean exam 2-column format:
      Row 0: group[0] (left col), group[row_count] (right col)
      Row 1: group[1] (left col), group[row_count+1] (right col)

    Each cell has a fixed height, guaranteeing even spacing for writing area.
    Uses correct OWPML table structure with hp:subList, hp:cellAddr, hp:cellSpan.
    """
    tbl_id = idgen.next()
    wrap_pid = idgen.next()

    col_count = 2
    col_width = table_width // col_count  # 24096 each
    table_height = row_height * row_count

    cell_margin_lr = 283  # ~1mm left/right padding inside cells
    cell_margin_tb = 142  # ~0.5mm top/bottom padding

    rows_xml = []
    for row in range(row_count):
        cells_xml = []
        for col in range(col_count):
            prob_idx = col * row_count + row
            idgen.next()

            if prob_idx < len(problems_in_group):
                prob = problems_in_group[prob_idx]
                prob_num = start_num + prob_idx
                img_id = (image_ids or {}).get(prob_num)
                cell_content = _make_problem_cell_content(
                    idgen, prob_num, prob, image_id=img_id
                )
            else:
                cell_content = make_empty_para(idgen)

            cells_xml.append(
                f'<hp:tc name="" header="0" hasMargin="0" protect="0" '
                f'editable="0" dirty="1" borderFillIDRef="{STYLE["BORDER_INVISIBLE"]}">'
                f'<hp:subList id="" textDirection="HORIZONTAL" '
                f'lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" '
                f'linkListNextIDRef="0" textWidth="0" textHeight="0" '
                f'hasTextRef="0" hasNumRef="0">'
                f"{cell_content}"
                f"</hp:subList>"
                f'<hp:cellAddr colAddr="{col}" rowAddr="{row}"/>'
                f'<hp:cellSpan colSpan="1" rowSpan="1"/>'
                f'<hp:cellSz width="{col_width}" height="{row_height}"/>'
                f'<hp:cellMargin left="{cell_margin_lr}" right="{cell_margin_lr}" '
                f'top="{cell_margin_tb}" bottom="{cell_margin_tb}"/>'
                f"</hp:tc>"
            )
        rows_xml.append(f"<hp:tr>{''.join(cells_xml)}</hp:tr>")

    tbl_xml = (
        f'<hp:tbl id="{tbl_id}" zOrder="0" numberingType="TABLE" '
        f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        f'dropcapstyle="None" pageBreak="CELL" repeatHeader="0" '
        f'rowCnt="{row_count}" colCnt="{col_count}" cellSpacing="0" '
        f'borderFillIDRef="{STYLE["BORDER_INVISIBLE"]}" noAdjust="0">'
        f'<hp:sz width="{table_width}" widthRelTo="ABSOLUTE" '
        f'height="{table_height}" heightRelTo="ABSOLUTE" protect="0"/>'
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
        f'allowOverlap="0" holdAnchorAndSO="0" '
        f'vertRelTo="PARA" horzRelTo="COLUMN" '
        f'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
        f'<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        f'<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        + "".join(rows_xml)
        + "</hp:tbl>"
    )

    pb = "1" if page_break else "0"
    return (
        f'<hp:p id="{wrap_pid}" paraPrIDRef="0" styleIDRef="0" '
        f'pageBreak="{pb}" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0">{tbl_xml}</hp:run>'
        f"</hp:p>"
    )
