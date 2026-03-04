#!/usr/bin/env python3
"""
page_guard.py - HWPX 레퍼런스 대비 페이지 드리프트 위험 검사

목표:
- 실제 렌더러의 쪽수 계산을 대체할 수는 없지만,
  쪽수 변화로 이어지기 쉬운 구조 변경을 사전에 차단한다.

검사 항목:
- 문단 수 / 표 수 / 표 구조(rowCnt, colCnt, width, height) 동일성
- 명시적 pageBreak / columnBreak 수 동일성
- 전체 텍스트 길이 편차(기본 15%) 한도
- 문단별 텍스트 길이 급변(기본 25%) 감지
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from dataclasses import dataclass, asdict
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

from lxml import etree

NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
}


@dataclass
class Metrics:
    paragraph_count: int
    page_break_count: int
    column_break_count: int
    table_count: int
    table_shapes: List[Tuple[str, str, str, str, str, str]]
    text_char_total: int
    text_char_total_nospace: int
    paragraph_text_lengths: List[int]


def _read_section_xml_bytes(hwpx_path: Path) -> bytes:
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return zf.read("Contents/section0.xml")


def _text_of_t_node(t_node: etree._Element) -> str:
    return "".join(t_node.itertext())


def collect_metrics(hwpx_path: Path) -> Metrics:
    section_bytes = _read_section_xml_bytes(hwpx_path)
    root = etree.parse(BytesIO(section_bytes)).getroot()

    paragraphs = root.xpath(".//hs:sec/hp:p", namespaces=NS)
    if not paragraphs:
        paragraphs = root.xpath(".//hp:p", namespaces=NS)

    page_break_count = sum(1 for p in paragraphs if p.get("pageBreak") == "1")
    column_break_count = sum(1 for p in paragraphs if p.get("columnBreak") == "1")

    tables = root.xpath(".//hp:tbl", namespaces=NS)
    table_shapes: List[Tuple[str, str, str, str, str, str]] = []
    for t in tables:
        sz = t.find("hp:sz", namespaces=NS)
        width = sz.get("width", "") if sz is not None else ""
        height = sz.get("height", "") if sz is not None else ""
        table_shapes.append(
            (
                t.get("rowCnt", ""),
                t.get("colCnt", ""),
                width,
                height,
                t.get("repeatHeader", ""),
                t.get("pageBreak", ""),
            )
        )

    t_nodes = root.xpath(".//hp:t", namespaces=NS)
    text_char_total = 0
    text_char_total_nospace = 0
    for t in t_nodes:
        s = _text_of_t_node(t)
        text_char_total += len(s)
        text_char_total_nospace += len("".join(s.split()))

    paragraph_text_lengths: List[int] = []
    for p in paragraphs:
        plen = 0
        for t in p.xpath(".//hp:t", namespaces=NS):
            plen += len(_text_of_t_node(t))
        paragraph_text_lengths.append(plen)

    return Metrics(
        paragraph_count=len(paragraphs),
        page_break_count=page_break_count,
        column_break_count=column_break_count,
        table_count=len(tables),
        table_shapes=table_shapes,
        text_char_total=text_char_total,
        text_char_total_nospace=text_char_total_nospace,
        paragraph_text_lengths=paragraph_text_lengths,
    )


def _ratio_delta(a: int, b: int) -> float:
    base = max(a, 1)
    return abs(b - a) / base


def compare_metrics(
    ref: Metrics,
    out: Metrics,
    max_text_delta_ratio: float,
    max_paragraph_delta_ratio: float,
) -> List[str]:
    errors: List[str] = []

    if ref.paragraph_count != out.paragraph_count:
        errors.append(
            f"문단 수 불일치: ref={ref.paragraph_count}, out={out.paragraph_count}"
        )
    if ref.page_break_count != out.page_break_count:
        errors.append(
            f"명시적 pageBreak 수 불일치: ref={ref.page_break_count}, out={out.page_break_count}"
        )
    if ref.column_break_count != out.column_break_count:
        errors.append(
            f"명시적 columnBreak 수 불일치: ref={ref.column_break_count}, out={out.column_break_count}"
        )
    if ref.table_count != out.table_count:
        errors.append(f"표 수 불일치: ref={ref.table_count}, out={out.table_count}")
    if ref.table_shapes != out.table_shapes:
        errors.append("표 구조(rowCnt/colCnt/width/height/pageBreak) 불일치")

    td = _ratio_delta(ref.text_char_total_nospace, out.text_char_total_nospace)
    if td > max_text_delta_ratio:
        errors.append(
            "전체 텍스트 길이 편차 초과: "
            f"ref={ref.text_char_total_nospace}, out={out.text_char_total_nospace}, "
            f"delta={td:.2%}, limit={max_text_delta_ratio:.2%}"
        )

    if len(ref.paragraph_text_lengths) == len(out.paragraph_text_lengths):
        for idx, (a, b) in enumerate(
            zip(ref.paragraph_text_lengths, out.paragraph_text_lengths), start=1
        ):
            if a == 0 and b == 0:
                continue
            pd = _ratio_delta(a, b)
            if pd > max_paragraph_delta_ratio:
                errors.append(
                    f"{idx}번째 문단 텍스트 길이 편차 초과: "
                    f"ref={a}, out={b}, delta={pd:.2%}, limit={max_paragraph_delta_ratio:.2%}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HWPX 레퍼런스 대비 페이지 드리프트 위험 검사"
    )
    parser.add_argument("--reference", "-r", required=True, help="기준 HWPX 경로")
    parser.add_argument("--output", "-o", required=True, help="결과 HWPX 경로")
    parser.add_argument(
        "--max-text-delta-ratio",
        type=float,
        default=0.15,
        help="전체 텍스트 길이 허용 편차 비율 (기본: 0.15)",
    )
    parser.add_argument(
        "--max-paragraph-delta-ratio",
        type=float,
        default=0.25,
        help="문단별 텍스트 길이 허용 편차 비율 (기본: 0.25)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="metrics를 JSON으로 출력",
    )
    args = parser.parse_args()

    ref_path = Path(args.reference)
    out_path = Path(args.output)

    if not ref_path.exists():
        print(f"Error: reference not found: {ref_path}", file=sys.stderr)
        return 2
    if not out_path.exists():
        print(f"Error: output not found: {out_path}", file=sys.stderr)
        return 2

    ref = collect_metrics(ref_path)
    out = collect_metrics(out_path)

    if args.json:
        print(
            json.dumps(
                {"reference": asdict(ref), "output": asdict(out)},
                ensure_ascii=False,
                indent=2,
            )
        )

    errors = compare_metrics(
        ref,
        out,
        max_text_delta_ratio=args.max_text_delta_ratio,
        max_paragraph_delta_ratio=args.max_paragraph_delta_ratio,
    )
    if errors:
        print("FAIL: page-guard")
        for e in errors:
            print(f" - {e}")
        return 1

    print("PASS: page-guard")
    print(
        "  paragraph/table/pageBreak 구조와 텍스트 길이 편차가 허용 범위 내입니다."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
