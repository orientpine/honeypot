#!/usr/bin/env python3
"""
analyze_template.py — HWPX 문서 구조 심층 분석

HWPX 파일을 분석하여 문서의 전체 구조, 스타일 정의, 테이블 레이아웃,
셀 병합, 내용 등을 상세하게 출력한다.
레퍼런스 기반 문서 생성의 청사진으로 사용.

Usage:
    python3 analyze_template.py <input.hwpx>
    python3 analyze_template.py <input.hwpx> --extract-header /tmp/ref_header.xml
"""

import sys
import os
import tempfile
import shutil
import zipfile
import argparse
import json
from collections import Counter, defaultdict
from lxml import etree

NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
}

FONT_MAP = {}


def get_text(el):
    texts = []
    for t in el.findall(".//hp:t", NS):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def analyze_fonts(root):
    lines = ["▶ 폰트 정의"]
    for fontface in root.findall(".//hh:fontface", NS):
        lang = fontface.get("lang", "?")
        for font in fontface.findall("hh:font", NS):
            fid = font.get("id")
            face = font.get("face")
            FONT_MAP[(lang, fid)] = face
            if lang == "HANGUL":
                lines.append(f"  hangul/{fid}: {face}")
    lines.append("")
    return lines


def analyze_borderfills(root):
    lines = ["▶ borderFill (테두리/배경)"]
    for bf in root.findall(".//hh:borderFill", NS):
        bid = bf.get("id")
        parts = []
        for side in ["left", "right", "top", "bottom"]:
            b = bf.find(f"hh:{side}Border", NS)
            if b is not None:
                btype = b.get("type", "NONE")
                bwidth = b.get("width", "")
                if btype != "NONE":
                    parts.append(f"{side}={btype} {bwidth}".strip())
                else:
                    parts.append(f"{side}=NONE")

        bg = "없음"
        fill = bf.find(".//hc:winBrush", NS)
        if fill is not None:
            fc = fill.get("faceColor", "none")
            if fc != "none":
                bg = fc

        border_desc = ", ".join(parts)
        lines.append(f"  [{bid}] {border_desc}")
        if bg != "없음":
            lines.append(f"       배경={bg}")
    lines.append("")
    return lines


def analyze_charprops(root):
    lines = ["▶ charPr (글자 스타일)"]
    for cp in root.findall(".//hh:charPr", NS):
        cid = cp.get("id")
        height = int(cp.get("height", "0"))
        pt = height / 100
        color = cp.get("textColor", "#000000")
        bfref = cp.get("borderFillIDRef", "?")

        fontref = cp.find("hh:fontRef", NS)
        font_id = fontref.get("hangul", "0") if fontref is not None else "0"
        font_name = FONT_MAP.get(("HANGUL", font_id), f"font{font_id}")

        spacing_el = cp.find("hh:spacing", NS)
        spacing = int(spacing_el.get("hangul", "0")) if spacing_el is not None else 0

        flags = []
        if cp.find("hh:bold", NS) is not None:
            flags.append("볼드")
        if cp.find("hh:italic", NS) is not None:
            flags.append("이탤릭")
        ul = cp.find("hh:underline", NS)
        if ul is not None and ul.get("type", "NONE") != "NONE":
            ul_shape = ul.get("shape", "SOLID")
            flags.append(f"밑줄({ul_shape})")
        so = cp.find("hh:strikeout", NS)
        if so is not None and so.get("shape", "NONE") != "NONE":
            flags.append("취소선")

        flag_str = " ".join(flags) if flags else ""
        spacing_str = f" spacing={spacing}" if spacing != 0 else ""
        line = f"  [{cid}] {pt}pt {font_name} {color}{spacing_str} {flag_str}".rstrip()
        lines.append(line)
        lines.append(f"       fontRef=hangul:{font_id} borderFillIDRef={bfref}")
    lines.append("")
    return lines


def analyze_paraprops(root):
    lines = ["▶ paraPr (문단 스타일)"]
    for pp in root.findall(".//hh:paraPr", NS):
        pid = pp.get("id")
        tabref = pp.get("tabPrIDRef", "0")

        align = pp.find("hh:align", NS)
        h_align = align.get("horizontal", "?") if align is not None else "?"
        v_align = align.get("vertical", "?") if align is not None else "?"

        heading = pp.find("hh:heading", NS)
        h_type = heading.get("type", "NONE") if heading is not None else "NONE"
        h_level = heading.get("level", "0") if heading is not None else "0"

        ls_val = "?"
        ls_type = "?"
        ls = pp.find(".//hh:lineSpacing", NS)
        if ls is not None:
            ls_val = ls.get("value", "?")
            ls_type = ls.get("type", "PERCENT")

        margins = {}
        for m_name in ["intent", "left", "right", "prev", "next"]:
            m = pp.find(f".//hc:{m_name}", NS)
            if m is not None:
                val = m.get("value", "0")
                margins[m_name] = val

        border = pp.find("hh:border", NS)
        bf_ref = border.get("borderFillIDRef", "2") if border is not None else "2"
        b_offsets = {}
        if border is not None:
            for attr in ["offsetLeft", "offsetRight", "offsetTop", "offsetBottom"]:
                v = border.get(attr, "0")
                if v != "0":
                    b_offsets[attr] = v

        margin_parts = []
        for k, v in margins.items():
            if v != "0":
                margin_parts.append(f"{k}={v}")
        margin_str = ", ".join(margin_parts) if margin_parts else "없음"

        heading_str = ""
        if h_type != "NONE":
            heading_str = f" heading={h_type} level={h_level}"

        lines.append(f"  [{pid}] {h_align} lineSpacing={ls_val}{ls_type}{heading_str}")
        lines.append(f"       여백({margin_str}) borderFillIDRef={bf_ref}")
        if b_offsets:
            lines.append(
                f"       borderOffset({', '.join(f'{k}={v}' for k, v in b_offsets.items())})"
            )
    lines.append("")
    return lines


def analyze_cell(tc, indent=""):
    lines = []

    bf = tc.get("borderFillIDRef", "?")
    addr = tc.find("hp:cellAddr", NS)
    col = addr.get("colAddr", "?") if addr is not None else "?"
    row = addr.get("rowAddr", "?") if addr is not None else "?"

    span = tc.find("hp:cellSpan", NS)
    cs = span.get("colSpan", "1") if span is not None else "1"
    rs = span.get("rowSpan", "1") if span is not None else "1"

    sz = tc.find("hp:cellSz", NS)
    w = sz.get("width", "?") if sz is not None else "?"
    h = sz.get("height", "?") if sz is not None else "?"

    margin = tc.find("hp:cellMargin", NS)
    cm_str = ""
    if margin is not None:
        ml = margin.get("left", "0")
        mr = margin.get("right", "0")
        mt = margin.get("top", "0")
        mb = margin.get("bottom", "0")
        cm_str = f" cellMargin=[{ml},{mr},{mt},{mb}]"

    span_str = ""
    if cs != "1":
        span_str += f" colSpan={cs}"
    if rs != "1":
        span_str += f" rowSpan={rs}"

    lines.append(
        f"{indent}Cell({col},{row}) w={w} h={h}{span_str} borderFill={bf}{cm_str}"
    )

    sublist = tc.find("hp:subList", NS)
    if sublist is not None:
        valign = sublist.get("vertAlign", "?")
        if valign != "CENTER":
            lines.append(f"{indent}  vertAlign={valign}")
        for p in sublist.findall("hp:p", NS):
            ppr = p.get("paraPrIDRef", "0")
            run_parts = []
            for run in p.findall("hp:run", NS):
                cpr = run.get("charPrIDRef", "0")
                txt = get_text(run)
                nested_tbl = run.find("hp:tbl", NS)
                if nested_tbl is not None:
                    run_parts.append("[내부테이블]")
                elif txt:
                    # Truncate long text
                    display = txt[:40] + "..." if len(txt) > 40 else txt
                    run_parts.append(f'charPr={cpr}:"{display}"')
                else:
                    run_parts.append(f"charPr={cpr}:(빈)")
            content = " + ".join(run_parts) if run_parts else "(빈)"
            lines.append(f"{indent}  P paraPr={ppr} {content}")

    return "\n".join(lines)


def analyze_table(tbl, indent=""):
    lines = []

    rows = int(tbl.get("rowCnt", "0"))
    cols = int(tbl.get("colCnt", "0"))
    tbl_id = tbl.get("id", "?")
    bf = tbl.get("borderFillIDRef", "?")
    repeat_header = tbl.get("repeatHeader", "0")
    page_break = tbl.get("pageBreak", "?")

    sz = tbl.find("hp:sz", NS)
    w = sz.get("width", "?") if sz is not None else "?"
    h = sz.get("height", "?") if sz is not None else "?"

    pos = tbl.find("hp:pos", NS)
    treat_as_char = pos.get("treatAsChar", "?") if pos is not None else "?"
    h_align = pos.get("horzAlign", "?") if pos is not None else "?"

    lines.append(f"{indent}┌─ TABLE id={tbl_id} {rows}행×{cols}열 w={w} h={h}")
    lines.append(
        f"{indent}│  borderFill={bf} treatAsChar={treat_as_char} horzAlign={h_align}"
    )

    # Collect column widths from first data row
    col_widths = {}
    for tr in tbl.findall("hp:tr", NS):
        for tc in tr.findall("hp:tc", NS):
            addr = tc.find("hp:cellAddr", NS)
            if addr is not None:
                col_idx = int(addr.get("colAddr", "0"))
                span_el = tc.find("hp:cellSpan", NS)
                cs = int(span_el.get("colSpan", "1")) if span_el is not None else 1
                if cs == 1 and col_idx not in col_widths:
                    csz = tc.find("hp:cellSz", NS)
                    if csz is not None:
                        col_widths[col_idx] = csz.get("width", "?")

    sorted_widths = [col_widths.get(i, "?") for i in range(cols)]
    lines.append(f"{indent}│  열너비: [{', '.join(sorted_widths)}]")
    total = sum(int(v) for v in sorted_widths if v != "?")
    lines.append(f"{indent}│  합계: {total}")
    lines.append(f"{indent}│")

    for ri, tr in enumerate(tbl.findall("hp:tr", NS)):
        lines.append(f"{indent}│  ── Row {ri}")
        for tc in tr.findall("hp:tc", NS):
            cell_lines = analyze_cell(tc, indent + "│     ")
            lines.append(cell_lines)
    lines.append(f"{indent}└─────")
    lines.append("")

    return "\n".join(lines)


def analyze_paragraph(p, indent=""):
    lines = []

    pid = p.get("id", "?")
    ppr = p.get("paraPrIDRef", "0")

    run_parts = []
    has_table = False
    has_secpr = False

    for run in p.findall("hp:run", NS):
        cpr = run.get("charPrIDRef", "0")

        if run.find("hp:secPr", NS) is not None:
            has_secpr = True
            continue

        if run.find("hp:ctrl", NS) is not None:
            continue

        tbl = run.find("hp:tbl", NS)
        if tbl is not None:
            has_table = True
            if run_parts:
                content = " + ".join(run_parts)
                lines.append(f"{indent}P id={pid} paraPr={ppr} {content}")
                run_parts = []
            lines.append(analyze_table(tbl, indent))
            continue

        txt = get_text(run)
        if txt:
            display = txt[:50] + "..." if len(txt) > 50 else txt
            run_parts.append(f'charPr={cpr}:"{display}"')
        else:
            run_parts.append(f"charPr={cpr}:(빈)")

    if not has_table:
        content = " + ".join(run_parts) if run_parts else "(빈)"
        prefix = "[secPr] " if has_secpr else ""
        lines.append(f"{indent}P id={pid} paraPr={ppr} {prefix}{content}")
    elif run_parts:
        content = " + ".join(run_parts)
        lines.append(f"{indent}P id={pid} paraPr={ppr} {content}")

    return "\n".join(lines)


def analyze_section(section_root):
    lines = ["▶ 문서 구조"]

    secpr = section_root.find(".//hp:secPr", NS)
    if secpr is not None:
        pagepr = secpr.find("hp:pagePr", NS)
        if pagepr is not None:
            w = pagepr.get("width", "?")
            h = pagepr.get("height", "?")
            landscape = pagepr.get("landscape", "?")
            lines.append(f"  페이지: {w} × {h} ({landscape})")
            margin = pagepr.find("hp:margin", NS)
            if margin is not None:
                lines.append(
                    f"  여백: 좌={margin.get('left')} 우={margin.get('right')} 상={margin.get('top')} 하={margin.get('bottom')}"
                )
                lines.append(
                    f"  머리말={margin.get('header')} 꼬리말={margin.get('footer')}"
                )
                left = int(margin.get("left", "0"))
                right = int(margin.get("right", "0"))
                lines.append(f"  본문폭: {int(w) - left - right} ({w}-{left}-{right})")

        for pbf in secpr.findall("hp:pageBorderFill", NS):
            ptype = pbf.get("type", "?")
            if ptype == "BOTH":
                bfref = pbf.get("borderFillIDRef", "?")
                tb = pbf.get("textBorder", "?")
                off = pbf.find("hp:offset", NS)
                if off is not None:
                    lines.append(
                        f"  페이지테두리: borderFill={bfref} textBorder={tb} offset=[{off.get('left')},{off.get('right')},{off.get('top')},{off.get('bottom')}]"
                    )

    lines.append("")
    lines.append("  ════════ 본문 ════════")
    lines.append("")

    sec = section_root.find(".//hs:sec", NS)
    if sec is None:
        sec = section_root
    for p in sec.findall("hp:p", NS):
        para_lines = analyze_paragraph(p, "  ")
        lines.append(para_lines)

    return "\n".join(lines)


def extract_style_map(header_root, section_root):
    """Extract style configuration JSON for use with xml_writer.py.

    Heuristically estimates body, heading, bullet, bold, table styles
    by analyzing charPr/paraPr definitions in header.xml and their usage
    frequency in section0.xml paragraphs.
    """
    # --- Step 1: Parse charPr definitions from header.xml ---
    charpr_map = {}  # id -> {"fontSize_hu": int, "bold": bool}
    for cp in header_root.findall(".//hh:charPr", NS):
        cid = cp.get("id")
        height = int(cp.get("height", "0"))
        is_bold = cp.find("hh:bold", NS) is not None
        if not is_bold and cp.get("bold", "0") == "1":
            is_bold = True
        charpr_map[cid] = {"fontSize_hu": height, "bold": is_bold}

    # --- Step 2: Parse paraPr definitions from header.xml ---
    parapr_map = {}  # id -> {"left_margin": int, "indent": int}
    for pp in header_root.findall(".//hh:paraPr", NS):
        pid = pp.get("id")
        left_margin = 0
        indent = 0
        # Method 1: hc:left and hc:intent elements (existing pattern)
        left_el = pp.find(".//hc:left", NS)
        if left_el is not None:
            left_margin = int(left_el.get("value", "0"))
        intent_el = pp.find(".//hc:intent", NS)
        if intent_el is not None:
            indent = int(intent_el.get("value", "0"))
        # Method 2: hh:paraMargin element (alternative format)
        para_margin = pp.find(".//hh:paraMargin", NS)
        if para_margin is not None:
            pm_left = para_margin.get("left")
            if pm_left is not None:
                left_margin = int(pm_left)
            pm_indent = para_margin.get("indent")
            if pm_indent is not None:
                indent = int(pm_indent)
        parapr_map[pid] = {"left_margin": left_margin, "indent": indent}

    # --- Step 3: Scan section0.xml paragraphs ---
    sec = section_root.find(".//hs:sec", NS)
    if sec is None:
        sec = section_root

    body_pairs = []  # [(charPrIDRef, paraPrIDRef), ...]
    bullet_pairs = []  # [(charPrIDRef, paraPrIDRef), ...]
    heading_entries = []  # [{"fontSize_hu", "charPrIDRef", "paraPrIDRef"}, ...]
    tbl_header_entries = []
    tbl_cell_entries = []
    BULLET_CHARS = {"◦", "–", "□", "▪"}

    def _scan_table(tbl):
        """Recursively scan table rows/cells for style info."""
        for ri, tr in enumerate(tbl.findall("hp:tr", NS)):
            is_header = ri == 0
            for tc in tr.findall("hp:tc", NS):
                cell_bf = tc.get("borderFillIDRef", "0")
                sublist = tc.find("hp:subList", NS)
                if sublist is None:
                    continue
                for p in sublist.findall("hp:p", NS):
                    ppr = p.get("paraPrIDRef", "0")
                    for run in p.findall("hp:run", NS):
                        cpr = run.get("charPrIDRef", "0")
                        nested = run.find("hp:tbl", NS)
                        if nested is not None:
                            _scan_table(nested)
                            continue
                        entry = {
                            "charPrIDRef": cpr,
                            "paraPrIDRef": ppr,
                            "borderFillIDRef": cell_bf,
                        }
                        if is_header:
                            tbl_header_entries.append(entry)
                        else:
                            tbl_cell_entries.append(entry)

    for p in sec.findall("hp:p", NS):
        ppr = p.get("paraPrIDRef", "0")
        for run in p.findall("hp:run", NS):
            cpr = run.get("charPrIDRef", "0")
            if run.find("hp:secPr", NS) is not None:
                continue
            if run.find("hp:ctrl", NS) is not None:
                continue
            tbl = run.find("hp:tbl", NS)
            if tbl is not None:
                _scan_table(tbl)
                continue
            txt = get_text(run)
            body_pairs.append((cpr, ppr))
            if txt and any(c in txt for c in BULLET_CHARS):
                bullet_pairs.append((cpr, ppr))
            if cpr in charpr_map and charpr_map[cpr]["fontSize_hu"] > 1200:
                heading_entries.append(
                    {
                        "fontSize_hu": charpr_map[cpr]["fontSize_hu"],
                        "charPrIDRef": cpr,
                        "paraPrIDRef": ppr,
                    }
                )

    # --- Step 4: Aggregate results (ordered as spec) ---
    result = {}

    # Headings: group by fontSize level, largest = heading_1
    if heading_entries:
        heading_by_size = defaultdict(list)
        for h in heading_entries:
            heading_by_size[h["fontSize_hu"]].append(
                (h["charPrIDRef"], h["paraPrIDRef"])
            )
        sorted_sizes = sorted(heading_by_size.keys(), reverse=True)
        for i, size in enumerate(sorted_sizes[:2]):
            pairs = heading_by_size[size]
            most_common = Counter(pairs).most_common(1)[0][0]
            result[f"heading_{i + 1}"] = {
                "charPrIDRef": most_common[0],
                "paraPrIDRef": most_common[1],
            }
    if "heading_1" not in result:
        result["heading_1"] = {
            "charPrIDRef": "0",
            "paraPrIDRef": "0",
            "_comment": "no heading detected",
        }
    if "heading_2" not in result:
        result["heading_2"] = {
            "charPrIDRef": "0",
            "paraPrIDRef": "0",
            "_comment": "no heading detected",
        }

    # Body: most frequent (charPrIDRef, paraPrIDRef) in non-table paragraphs
    if body_pairs:
        bc = Counter(body_pairs).most_common(1)[0][0]
        result["body"] = {"charPrIDRef": bc[0], "paraPrIDRef": bc[1]}
    else:
        result["body"] = {"charPrIDRef": "0", "paraPrIDRef": "0"}

    # Bullet: paragraphs containing ◦, –, □, ▪ + paraPr margins
    if bullet_pairs:
        bp = Counter(bullet_pairs).most_common(1)[0][0]
        bullet_entry = {"charPrIDRef": bp[0], "paraPrIDRef": bp[1]}
        if bp[1] in parapr_map:
            pi = parapr_map[bp[1]]
            bullet_entry["left_margin"] = pi["left_margin"]
            bullet_entry["indent"] = pi["indent"]
        else:
            bullet_entry["left_margin"] = 0
            bullet_entry["indent"] = 0
        result["bullet"] = bullet_entry
    else:
        result["bullet"] = {
            "charPrIDRef": "0",
            "paraPrIDRef": "0",
            "left_margin": 0,
            "indent": 0,
            "_comment": "no bullet detected",
        }

    # Bold: charPrIDRef with <hh:bold/> or bold="1"; prefer most used
    bold_ids = [cid for cid, info in charpr_map.items() if info["bold"]]
    if bold_ids:
        body_cpr_count = Counter(cpr for cpr, _ in body_pairs)
        best_bold = max(bold_ids, key=lambda x: body_cpr_count.get(x, 0))
        result["bold"] = {"charPrIDRef": best_bold}
    else:
        result["bold"] = {
            "charPrIDRef": "0",
            "_comment": "no bold charPr detected",
        }

    # Table header: first row of tables
    if tbl_header_entries:
        thc = Counter(
            (e["charPrIDRef"], e["paraPrIDRef"], e["borderFillIDRef"])
            for e in tbl_header_entries
        )
        th = thc.most_common(1)[0][0]
        result["table_header"] = {
            "charPrIDRef": th[0],
            "paraPrIDRef": th[1],
            "borderFillIDRef": th[2],
        }
    else:
        result["table_header"] = {
            "charPrIDRef": "0",
            "paraPrIDRef": "0",
            "borderFillIDRef": "0",
            "_comment": "no table header detected",
        }

    # Table cell: non-header rows
    if tbl_cell_entries:
        tcc = Counter(
            (e["charPrIDRef"], e["paraPrIDRef"], e["borderFillIDRef"])
            for e in tbl_cell_entries
        )
        tc_most = tcc.most_common(1)[0][0]
        result["table_cell"] = {
            "charPrIDRef": tc_most[0],
            "paraPrIDRef": tc_most[1],
            "borderFillIDRef": tc_most[2],
        }
    else:
        result["table_cell"] = {
            "charPrIDRef": "0",
            "paraPrIDRef": "0",
            "borderFillIDRef": "0",
            "_comment": "no table cell detected",
        }

    # Constants
    result["table_width"] = 42520
    result["image_placeholder"] = {"paraPrIDRef": "0", "charPrIDRef": "0"}

    # Font sizes map: charPrIDRef -> "Npt"
    font_sizes = {}
    for cid, info in charpr_map.items():
        if info["fontSize_hu"] > 0:
            pt = info["fontSize_hu"] / 100
            font_sizes[cid] = f"{int(pt)}pt" if pt == int(pt) else f"{pt}pt"
    result["font_sizes"] = font_sizes

    result["confidence"] = "estimated"
    return result


def main():
    parser = argparse.ArgumentParser(description="HWPX 문서 구조 심층 분석")
    parser.add_argument("input", help="분석할 HWPX 파일")
    parser.add_argument(
        "--extract-header", metavar="PATH", help="header.xml을 지정 경로로 추출"
    )
    parser.add_argument(
        "--extract-section", metavar="PATH", help="section0.xml을 지정 경로로 추출"
    )
    parser.add_argument(
        "--style-map",
        metavar="PATH",
        help="스타일 설정 JSON 추출 (xml_writer.py용)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found")
        sys.exit(1)

    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(args.input, "r") as z:
            z.extractall(tmpdir)

        header_path = os.path.join(tmpdir, "Contents", "header.xml")
        section_path = os.path.join(tmpdir, "Contents", "section0.xml")

        if not os.path.exists(header_path) or not os.path.exists(section_path):
            print("Error: Contents/header.xml or Contents/section0.xml not found")
            sys.exit(1)

        header_root = etree.parse(header_path).getroot()
        section_root = etree.parse(section_path).getroot()

        # Extract files if requested
        if args.extract_header:
            shutil.copy2(header_path, args.extract_header)
            print(f"header.xml → {args.extract_header}")

        if args.extract_section:
            shutil.copy2(section_path, args.extract_section)
            print(f"section0.xml → {args.extract_section}")

        # Style map extraction
        if args.style_map:
            style_map = extract_style_map(header_root, section_root)
            out_dir = os.path.dirname(args.style_map)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.style_map, "w", encoding="utf-8") as f:
                json.dump(style_map, f, ensure_ascii=False, indent=2)
            print(f"style-map → {args.style_map}")

        # Analysis output
        print("=" * 64)
        print(f"  HWPX 심층 분석: {os.path.basename(args.input)}")
        print("=" * 64)
        print()

        for line in analyze_fonts(header_root):
            print(line)
        for line in analyze_borderfills(header_root):
            print(line)
        for line in analyze_charprops(header_root):
            print(line)
        for line in analyze_paraprops(header_root):
            print(line)
        print(analyze_section(section_root))

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
