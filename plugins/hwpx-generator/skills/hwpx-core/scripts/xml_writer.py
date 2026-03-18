#!/usr/bin/env python3
# pyright: basic
"""Convert parsed markdown JSON blocks into HWPX XML fragment.

This script is intentionally string-based (no XML serializer) to avoid
namespace/format mutations when fragments are inserted into section0.xml.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except Exception:  # pragma: no cover - graceful fallback when Pillow is unavailable
    Image = None


ROOT_NS = (
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"'
)

SEC_ROOT_NS = (
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"'
)

DEFAULT_SECTION_SETTINGS = {
    "page_width": 59528,
    "page_height": 84188,
    "margin_left": 5669,
    "margin_right": 5669,
    "margin_top": 2834,
    "margin_bottom": 4251,
    "margin_header": 4251,
    "margin_footer": 2834,
    "margin_gutter": 0,
}

BULLET_PREFIX_RE = re.compile(
    r"^[\u25a0-\u25ff\u2022\u2023\u2192\u203b\u25b6\u25ba\u203a◦–□\-]+\s*"
)


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class IdGenerator:
    def __init__(
        self, paragraph_start: int = 9000000001, table_start: int = 9100000001
    ) -> None:
        self._paragraph = paragraph_start
        self._table = table_start

    def next_paragraph_id(self) -> str:
        current = self._paragraph
        self._paragraph += 1
        return str(current)

    def next_table_id(self) -> str:
        current = self._table
        self._table += 1
        return str(current)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert parsed JSON + style config into HWPX XML fragment",
    )
    parser.add_argument("--input", required=True, help="Input parsed JSON path")
    parser.add_argument("--style-config", required=True, help="Style config JSON path")
    parser.add_argument("--output", required=True, help="Output XML fragment path")
    parser.add_argument(
        "--wrap-section",
        action="store_true",
        help="Wrap output in hs:sec root with hs:secPr for zip_surgery replace",
    )
    return parser.parse_args()


def load_json(path: str) -> dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_styles(styles: dict) -> None:
    # heading_3 and heading_4 are optional — fall back to heading_2 if absent
    if "heading_2" in styles:
        for k in ("heading_3", "heading_4"):
            if k not in styles:
                styles[k] = styles["heading_2"]
    required = [
        "heading_1",
        "heading_2",
        "heading_3",
        "heading_4",
        "body",
        "bullet",
        "bold",
        "table_header",
        "table_cell",
        "table_width",
        "image_placeholder",
    ]
    missing = [name for name in required if name not in styles]
    if missing:
        raise ValueError(f"Missing style config key(s): {', '.join(missing)}")


def normalize_segments(block: dict) -> list[dict]:
    segments = block.get("segments")
    if isinstance(segments, list) and segments:
        out: list[dict] = []
        for seg in segments:
            text = str(seg.get("text", ""))
            seg_type = str(seg.get("type", "plain"))
            out.append({"type": seg_type, "text": text})
        return out
    text = str(block.get("text", ""))
    return [{"type": "plain", "text": text}]


def strip_bullet_prefix(text: str) -> str:
    return BULLET_PREFIX_RE.sub("", text)


def cell_text_and_span(cell: object) -> tuple[str, int, int]:
    if isinstance(cell, dict):
        merge = cell.get("merge")
        merge_colspan = None
        merge_rowspan = None
        if isinstance(merge, dict):
            merge_colspan = merge.get("colspan", merge.get("colSpan"))
            merge_rowspan = merge.get("rowspan", merge.get("rowSpan"))

        colspan_raw = cell.get("colspan", cell.get("colSpan", merge_colspan or 1))
        rowspan_raw = cell.get("rowspan", cell.get("rowSpan", merge_rowspan or 1))

        try:
            colspan = int(colspan_raw)
        except (TypeError, ValueError):
            colspan = 1
        try:
            rowspan = int(rowspan_raw)
        except (TypeError, ValueError):
            rowspan = 1

        return str(cell.get("text", "")), max(colspan, 1), max(rowspan, 1)

    return str(cell), 1, 1


def paragraph_from_segments(
    pid: str,
    para_pr_id: str,
    default_char_pr_id: str,
    bold_char_pr_id: str,
    segments: list[dict],
    include_hanging_indent: bool = False,
    left_margin: int = 0,
    indent: int = 0,
) -> str:
    attrs = [
        f'id="{pid}"',
        f'paraPrIDRef="{para_pr_id}"',
        'styleIDRef="0"',
        'pageBreak="0"',
        'columnBreak="0"',
        'merged="0"',
    ]
    if include_hanging_indent:
        attrs.append(f'leftMargin="{int(left_margin)}"')
        attrs.append(f'indent="{int(indent)}"')

    runs: list[str] = []
    for seg in segments:
        text = str(seg.get("text", ""))
        if text == "":
            continue
        seg_type = str(seg.get("type", "plain")).lower()
        if seg_type in {"bold", "strong"}:
            char_pr = bold_char_pr_id
        else:
            char_pr = default_char_pr_id
        runs.append(
            f'<hp:run charPrIDRef="{char_pr}"><hp:t>{xml_escape(text)}</hp:t></hp:run>'
        )

    if not runs:
        runs.append(f'<hp:run charPrIDRef="{default_char_pr_id}"><hp:t/></hp:run>')

    return f"<hp:p {' '.join(attrs)}>{''.join(runs)}</hp:p>"


def build_heading(block: dict, ids: IdGenerator, styles: dict) -> str:
    level = int(block.get("level", 1))
    if level < 1:
        level = 1
    if level > 4:
        level = 4
    style = styles[f"heading_{level}"]
    return paragraph_from_segments(
        pid=ids.next_paragraph_id(),
        para_pr_id=str(style["paraPrIDRef"]),
        default_char_pr_id=str(style["charPrIDRef"]),
        bold_char_pr_id=str(styles["bold"]["charPrIDRef"]),
        segments=normalize_segments(block),
    )


def build_paragraph(block: dict, ids: IdGenerator, styles: dict) -> str:
    body = styles["body"]
    return paragraph_from_segments(
        pid=ids.next_paragraph_id(),
        para_pr_id=str(body["paraPrIDRef"]),
        default_char_pr_id=str(body["charPrIDRef"]),
        bold_char_pr_id=str(styles["bold"]["charPrIDRef"]),
        segments=normalize_segments(block),
    )


def build_bullet(block: dict, ids: IdGenerator, styles: dict) -> str:
    style_key = str(block.get("style_key", "bullet"))
    selected_style = styles.get(style_key)
    if not isinstance(selected_style, dict):
        selected_style = styles["bullet"]

    bullet_style = dict(selected_style)
    for key in ("paraPrIDRef", "charPrIDRef", "left_margin", "indent"):
        if key in block and block[key] is not None:
            bullet_style[key] = block[key]

    marker = str(block.get("marker", "◦"))
    marker_text = marker if marker else "◦"
    content_segments = normalize_segments(block)
    para_pr_id = int(bullet_style["paraPrIDRef"])
    bullet_auto = {
        int(x)
        for x in styles.get("bullet_auto", [])
        if isinstance(x, (int, str)) and str(x).strip() != ""
    }
    if para_pr_id in bullet_auto:
        stripped_segments = [dict(seg) for seg in content_segments]
        for seg in stripped_segments:
            seg_text = str(seg.get("text", ""))
            if seg_text.strip() == "":
                continue
            seg["text"] = strip_bullet_prefix(seg_text)
            break
        content_segments = stripped_segments

    full_segments: list[dict] = [
        {"type": "plain", "text": marker_text}
    ] + content_segments
    return paragraph_from_segments(
        pid=ids.next_paragraph_id(),
        para_pr_id=str(para_pr_id),
        default_char_pr_id=str(bullet_style["charPrIDRef"]),
        bold_char_pr_id=str(styles["bold"]["charPrIDRef"]),
        segments=full_segments,
        include_hanging_indent=True,
        left_margin=int(bullet_style.get("left_margin", 0)),
        indent=int(bullet_style.get("indent", 0)),
    )


def infer_col_count(headers: list, rows: list[list], fallback: int) -> int:
    if fallback > 0:
        return fallback
    if headers:
        return len(headers)
    max_len = 0
    for row in rows:
        max_len = max(max_len, len(row))
    return max_len if max_len > 0 else 1


def distribute_width(total: int, cols: int) -> list[int]:
    base = total // cols
    remain = total % cols
    out = [base for _ in range(cols)]
    out[-1] += remain
    return out


def table_cell_xml(
    *,
    text: str,
    row_index: int,
    col_index: int,
    width: int,
    colspan: int = 1,
    rowspan: int = 1,
    is_header: bool,
    ids: IdGenerator,
    styles: dict,
) -> str:
    style = styles["table_header"] if is_header else styles["table_cell"]
    pid = ids.next_paragraph_id()
    safe_text = xml_escape(text)
    span_attrs = ""
    if colspan > 1:
        span_attrs += f' colSpan="{colspan}"'
    if rowspan > 1:
        span_attrs += f' rowSpan="{rowspan}"'
    return (
        f'<hp:tc borderFillIDRef="{style["borderFillIDRef"]}"{span_attrs}>'
        f'<hp:cellAddr colAddr="{col_index}" rowAddr="{row_index}"/>'
        f'<hp:cellSpan colSpan="{colspan}" rowSpan="{rowspan}"/>'
        f'<hp:cellSz width="{width}" height="2400"/>'
        '<hp:cellMargin left="283" right="283" top="141" bottom="141"/>'
        '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" '
        'vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" '
        f'textWidth="{max(width - 566, 0)}" fieldName="">'
        f'<hp:p id="{pid}" paraPrIDRef="{style["paraPrIDRef"]}" styleIDRef="0" '
        'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="{style["charPrIDRef"]}"><hp:t>{safe_text}</hp:t></hp:run>'
        "</hp:p>"
        "</hp:subList>"
        "</hp:tc>"
    )


def build_table(block: dict, ids: IdGenerator, styles: dict) -> str:
    headers = [str(x) for x in block.get("headers", [])]
    rows = [list(row) for row in block.get("rows", []) if isinstance(row, list)]
    requested_col_count = int(block.get("col_count", 0) or 0)
    col_count = infer_col_count(headers, rows, requested_col_count)

    normalized_headers = headers[:col_count] + [
        "" for _ in range(max(0, col_count - len(headers)))
    ]
    normalized_rows = []
    for row in rows:
        normalized_rows.append(
            row[:col_count] + ["" for _ in range(max(0, col_count - len(row)))]
        )

    table_rows = []
    if normalized_headers:
        table_rows.append(normalized_headers)
    table_rows.extend(normalized_rows)
    if not table_rows:
        table_rows.append(["" for _ in range(col_count)])

    widths = distribute_width(int(styles["table_width"]), col_count)
    tr_parts: list[str] = []

    for r_idx, row in enumerate(table_rows):
        is_header = r_idx == 0 and bool(normalized_headers)
        cells: list[str] = []
        for c_idx, raw_cell in enumerate(row):
            cell_text, colspan, rowspan = cell_text_and_span(raw_cell)
            cleaned = cell_text.replace("■", "").replace("▶", "")
            cells.append(
                table_cell_xml(
                    text=cleaned,
                    row_index=r_idx,
                    col_index=c_idx,
                    width=widths[c_idx],
                    colspan=colspan,
                    rowspan=rowspan,
                    is_header=is_header,
                    ids=ids,
                    styles=styles,
                )
            )
        tr_parts.append(f"<hp:tr>{''.join(cells)}</hp:tr>")

    wrapper_pid = ids.next_paragraph_id()
    table_id = ids.next_table_id()
    table_xml = (
        f'<hp:tbl id="{table_id}" zOrder="0" numberingType="TABLE" '
        'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        'dropcapstyle="None" pageBreak="CELL" repeatHeader="0" '
        f'rowCnt="{len(table_rows)}" colCnt="{col_count}" cellSpacing="0" '
        f'borderFillIDRef="{styles["table_cell"]["borderFillIDRef"]}" noAdjust="0">'
        f'<hp:sz width="{int(styles["table_width"])}" widthRelTo="ABSOLUTE" '
        f'height="{len(table_rows) * 2400}" heightRelTo="ABSOLUTE" protect="0"/>'
        '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
        'allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" '
        'horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" '
        'vertOffset="0" horzOffset="0"/>'
        '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        '<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        f"{''.join(tr_parts)}"
        "</hp:tbl>"
    )

    return (
        f'<hp:p id="{wrapper_pid}" paraPrIDRef="0" styleIDRef="0" '
        'pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="0">'
        f"{table_xml}"
        "</hp:run>"
        "</hp:p>"
    )


def build_image_placeholder(image_index: int) -> str:
    return f"<!--IMAGE:image{image_index}-->"


def build_image_with_caption(block: dict, config: dict, image_idx: int) -> str:
    bindata_name = f"image{image_idx}"
    image_id = 2112876660 + int(image_idx)
    instid = 1000000000 + int(image_idx)
    z_order = int(image_idx)

    max_content_width = int(
        config.get(
            "table_width",
            int(config.get("page_width", 48190))
            - int(config.get("margin_left", 5669))
            - int(config.get("margin_right", 5669)),
        )
    )

    placeholder = bool(block.get("placeholder", False))
    image_path = str(block.get("path", "") or "")
    orig_w = 19200
    orig_h = 10800

    if Image is not None and image_path:
        resolved_path = Path(image_path)
        if not resolved_path.is_absolute():
            resolved_path = Path.cwd() / resolved_path
        if resolved_path.is_file() or placeholder:
            try:
                if resolved_path.is_file():
                    with Image.open(resolved_path) as img:
                        px_w, px_h = img.size
                        if px_w > 0 and px_h > 0:
                            orig_w = int(px_w) * 100
                            orig_h = int(px_h) * 100
            except Exception:
                orig_w = 19200
                orig_h = 10800

    scaled_w = int(orig_w)
    scaled_h = int(orig_h)
    if scaled_w > max_content_width:
        ratio = max_content_width / float(scaled_w)
        scaled_w = max_content_width
        scaled_h = max(1, int(round(scaled_h * ratio)))

    image_style = config.get("image_placeholder", {})
    image_para_pr = str(image_style.get("paraPrIDRef", 4))

    caption_style = config.get("image_caption", config.get("body", {}))
    caption_para_pr = str(caption_style.get("paraPrIDRef", 0))
    caption_char_pr = str(caption_style.get("charPrIDRef", 0))
    caption_id = str(block.get("caption_id", image_idx))
    caption = str(block.get("caption", ""))
    caption_text = f"그림 {caption_id}: {caption}" if caption else f"그림 {caption_id}"

    pic_para = (
        f'<hp:para paraPrIDRef="{image_para_pr}">'
        "<hp:run>"
        f'<hp:pic hp:id="{image_id}" zOrder="{z_order}" numberingType="PICTURE" '
        'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        f'dropcapstyle="None" href="" groupLevel="0" instid="{instid}" reverse="0">'
        '<hp:offset x="0" y="0"/>'
        f'<hp:orgSz width="{orig_w}" height="{orig_h}"/>'
        f'<hp:curSz width="{scaled_w}" height="{scaled_h}"/>'
        '<hp:flip horizontal="0" vertical="0"/>'
        f'<hp:rotationInfo angle="0" centerX="{scaled_w // 2}" centerY="{scaled_h // 2}"/>'
        f'<hp:renderingInfo embeddingFile="{bindata_name}">'
        f'<hp:img hp:binaryItemIDRef="{bindata_name}"/>'
        "</hp:renderingInfo>"
        "</hp:pic>"
        "</hp:run>"
        "</hp:para>"
    )
    caption_para = (
        f'<hp:para paraPrIDRef="{caption_para_pr}" hp:align="CENTER">'
        f'<hp:run charPrIDRef="{caption_char_pr}">'
        f"<hp:t>{xml_escape(caption_text)}</hp:t>"
        "</hp:run>"
        "</hp:para>"
    )
    return f"{pic_para}{caption_para}"


def section_settings(styles: dict) -> dict[str, int]:
    margins = styles.get("margins", {})
    if not isinstance(margins, dict):
        margins = {}

    def get_int(*keys: str, default: int) -> int:
        for key in keys:
            value = styles.get(key)
            if value is not None:
                return int(value)
        return default

    def get_margin(name: str) -> int:
        if name in margins and margins[name] is not None:
            return int(margins[name])
        return int(
            styles.get(f"margin_{name}", DEFAULT_SECTION_SETTINGS[f"margin_{name}"])
        )

    return {
        "page_width": get_int(
            "page_width", "pageWidth", default=DEFAULT_SECTION_SETTINGS["page_width"]
        ),
        "page_height": get_int(
            "page_height", "pageHeight", default=DEFAULT_SECTION_SETTINGS["page_height"]
        ),
        "margin_left": get_margin("left"),
        "margin_right": get_margin("right"),
        "margin_top": get_margin("top"),
        "margin_bottom": get_margin("bottom"),
        "margin_header": get_margin("header"),
        "margin_footer": get_margin("footer"),
        "margin_gutter": int(
            styles.get("margin_gutter", DEFAULT_SECTION_SETTINGS["margin_gutter"])
        ),
    }


def wrap_in_section(children_xml: str, styles: dict) -> str:
    sec = section_settings(styles)
    sec_pr = (
        "<hs:secPr>"
        f'<hs:pageSize width="{sec["page_width"]}" height="{sec["page_height"]}" orientation="PORTRAIT"/>'
        f'<hs:pageMargin left="{sec["margin_left"]}" right="{sec["margin_right"]}" '
        f'top="{sec["margin_top"]}" bottom="{sec["margin_bottom"]}" '
        f'header="{sec["margin_header"]}" footer="{sec["margin_footer"]}" gutter="{sec["margin_gutter"]}"/>'
        '<hs:pageBorderFill fillArea="PAPER"><hp:borderFill><hp:slash fillErase="0" haveSlash="NONE"/>'
        "</hp:borderFill></hs:pageBorderFill>"
        "</hs:secPr>"
    )
    return f"<hs:sec {SEC_ROOT_NS}>{sec_pr}{children_xml}</hs:sec>"


def build_fragment(parsed: dict, styles: dict, wrap_section: bool = False) -> str:
    require_styles(styles)
    blocks = parsed.get("blocks", [])
    if not isinstance(blocks, list):
        raise ValueError("Input JSON must contain list key: blocks")

    ids = IdGenerator()
    image_counter = 1
    out: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type", "paragraph")).lower()

        if btype == "heading":
            out.append(build_heading(block, ids, styles))
        elif btype == "paragraph":
            out.append(build_paragraph(block, ids, styles))
        elif btype == "bullet":
            out.append(build_bullet(block, ids, styles))
        elif btype == "table":
            out.append(build_table(block, ids, styles))
        elif btype == "image_ref":
            out.append(build_image_with_caption(block, styles, image_counter))
            image_counter += 1
        else:
            out.append(build_paragraph(block, ids, styles))

    content = "".join(out)
    if wrap_section:
        return wrap_in_section(content, styles)

    fragment = [f"<hwpx-fragment {ROOT_NS}>", content, "</hwpx-fragment>"]
    return "".join(fragment)


def main() -> None:
    args = parse_args()
    try:
        parsed = load_json(args.input)
        styles = load_json(args.style_config)
        fragment_xml = build_fragment(parsed, styles, wrap_section=args.wrap_section)
        Path(args.output).write_text(fragment_xml, encoding="utf-8")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
