#!/usr/bin/env python3
"""Exam-specific XML paragraph generators for math-hwpx.

Provides helpers for:
- secPr paragraph (page settings with column config)
- Column switching paragraph
- Exam problem paragraph (bold number + points)
- Horizontal choices paragraph (tab-separated)
- Picture/image paragraph (graph embedding)
"""

from xml.sax.saxutils import escape

from xml_primitives import (
    IDGen,
    STYLE,
    SECPR_BODY,
    _make_equation_run,
    _make_tab_run,
)


def make_column_switch_para(
    idgen: IDGen, col_count: int = 2, same_gap: int = 2268
) -> str:
    """Generate a paragraph that switches the column count.

    This is the standard HWPX technique: embed hp:colPr in a hp:ctrl element.
    Used to switch from 1-column header to 2-column body in exam format.
    """
    pid = idgen.next()
    return (
        f'<hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0">'
        f"<hp:ctrl>"
        f'<hp:colPr id="" type="NEWSPAPER" layout="LEFT" '
        f'colCount="{col_count}" sameSz="1" sameGap="{same_gap}"/>'
        f"</hp:ctrl>"
        f"</hp:run>"
        f'<hp:run charPrIDRef="0"><hp:t/></hp:run>'
        f"</hp:p>"
    )


def make_secpr_para(idgen: IDGen, col_count: int = 2, same_gap: int = 2268) -> str:
    """Build the secPr paragraph with specified column settings."""
    pid = idgen.next()
    return (
        f'<hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="0">'
        f"{SECPR_BODY}"
        f"<hp:ctrl>"
        f'<hp:colPr id="" type="NEWSPAPER" layout="LEFT" '
        f'colCount="{col_count}" sameSz="1" sameGap="{same_gap}"/>'
        f"</hp:ctrl>"
        f"</hp:run>"
        f'<hp:run charPrIDRef="0"><hp:t/></hp:run>'
        f"</hp:p>"
    )


def make_horizontal_choices_para(
    idgen: IDGen,
    choices: list,
    para_pr: int = STYLE["PARA_HCHOICE"],
    char_pr: int = STYLE["CHAR_CHOICE"],
    base_unit: int = 900,
) -> str:
    """Generate a single paragraph with choices separated by tabs.

    Renders: ① val ② val ③ val ④ val ⑤ val
    All on one line using tab stops defined in tabPr ID 3.
    """
    choice_labels = ["①", "②", "③", "④", "⑤"]
    pid = idgen.next()
    runs = []

    for k, choice in enumerate(choices):
        label = choice_labels[k] if k < len(choice_labels) else f"({k + 1})"
        if k > 0:
            runs.append(_make_tab_run(char_pr))

        if choice.startswith("$") and choice.endswith("$"):
            eq_script = choice[1:-1]
            runs.append(
                f'<hp:run charPrIDRef="{char_pr}">'
                f"<hp:t>{escape(label)} </hp:t></hp:run>"
            )
            runs.append(_make_equation_run(idgen, eq_script, char_pr, base_unit))
        else:
            runs.append(
                f'<hp:run charPrIDRef="{char_pr}">'
                f"<hp:t>{escape(label)} {escape(choice)}</hp:t></hp:run>"
            )

    return (
        f'<hp:p id="{pid}" paraPrIDRef="{para_pr}" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">' + "".join(runs) + "</hp:p>"
    )


def make_exam_problem_para(
    idgen: IDGen,
    prob_num: int,
    text: str,
    points: int | None = None,
    equation: str | None = None,
    num_char_pr: int = STYLE["CHAR_EXAM_NUM"],
    text_char_pr: int = STYLE["CHAR_BODY"],
    points_char_pr: int = STYLE["CHAR_POINTS"],
    para_pr: int = STYLE["PARA_BODY"],
    base_unit: int = 1000,
) -> str:
    """Generate a problem text paragraph with bold-italic number and [점] suffix.

    Output example: **1.** -7/2 × (-3) + 4 × |-5/2| 의 값은? [2점]
    """
    pid = idgen.next()
    runs = []

    # Bold+italic problem number
    runs.append(
        f'<hp:run charPrIDRef="{num_char_pr}"><hp:t>{prob_num}. </hp:t></hp:run>'
    )

    # Problem text with optional inline equation
    if text and equation:
        # Equation comes first (e.g., "식 의 값은?" pattern)
        runs.append(_make_equation_run(idgen, equation, text_char_pr, base_unit))
        runs.append(
            f'<hp:run charPrIDRef="{text_char_pr}"><hp:t>{escape(text)}</hp:t></hp:run>'
        )
    elif text:
        runs.append(
            f'<hp:run charPrIDRef="{text_char_pr}"><hp:t>{escape(text)}</hp:t></hp:run>'
        )
    elif equation:
        runs.append(_make_equation_run(idgen, equation, text_char_pr, base_unit))

    # Points suffix
    if points is not None:
        runs.append(
            f'<hp:run charPrIDRef="{points_char_pr}">'
            f"<hp:t> [{points}점]</hp:t></hp:run>"
        )

    return (
        f'<hp:p id="{pid}" paraPrIDRef="{para_pr}" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">' + "".join(runs) + "</hp:p>"
    )


def make_picture_para(
    idgen: IDGen,
    image_id: str,
    width_hu: int = 11340,
    height_hu: int = 11340,
    para_pr: int = STYLE["PARA_EQ"],
    char_pr: int = 0,
) -> str:
    """Generate a paragraph containing an embedded picture (hp:pic + hc:img).

    Args:
        idgen: ID generator.
        image_id: The manifest item ID (matches opf:item id in content.hpf).
        width_hu: Image width in HWPUNIT.
        height_hu: Image height in HWPUNIT.
    """
    pid = idgen.next()
    pic_id = idgen.next()
    inst_id = idgen.next()
    cx = width_hu // 2
    cy = height_hu // 2

    return (
        f'<hp:p id="{pid}" paraPrIDRef="{para_pr}" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="{char_pr}">'
        f'<hp:pic id="{pic_id}" zOrder="0" numberingType="PICTURE" '
        f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        f'dropcapstyle="None" href="" groupLevel="0" instid="{inst_id}" reverse="0">'
        f'<hp:offset x="0" y="0"/>'
        f'<hp:orgSz width="{width_hu}" height="{height_hu}"/>'
        f'<hp:curSz width="{width_hu}" height="{height_hu}"/>'
        f'<hp:flip horizontal="0" vertical="0"/>'
        f'<hp:rotationInfo angle="0" centerX="{cx}" centerY="{cy}" rotateimage="1"/>'
        f"<hp:renderingInfo>"
        f'<hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        f'<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        f'<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        f"</hp:renderingInfo>"
        f"<hp:imgRect>"
        f'<hc:pt0 x="0" y="0"/>'
        f'<hc:pt1 x="{width_hu}" y="0"/>'
        f'<hc:pt2 x="{width_hu}" y="{height_hu}"/>'
        f'<hc:pt3 x="0" y="{height_hu}"/>'
        f"</hp:imgRect>"
        f'<hp:imgClip left="0" right="0" top="0" bottom="0"/>'
        f'<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        f'<hp:imgDim dimwidth="{width_hu}" dimheight="{height_hu}"/>'
        f'<hc:img binaryItemIDRef="{image_id}" bright="0" contrast="0" '
        f'effect="REAL_PIC" alpha="0"/>'
        f'<hp:sz width="{width_hu}" widthRelTo="ABSOLUTE" '
        f'height="{height_hu}" heightRelTo="ABSOLUTE" protect="0"/>'
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
        f'allowOverlap="0" holdAnchorAndSO="0" '
        f'vertRelTo="PARA" horzRelTo="COLUMN" '
        f'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
        f'<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        f"</hp:pic>"
        f"<hp:t/>"
        f"</hp:run>"
        f"</hp:p>"
    )
