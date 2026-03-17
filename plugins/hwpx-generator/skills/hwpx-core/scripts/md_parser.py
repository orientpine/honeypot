#!/usr/bin/env python3
"""Parse markdown into structured JSON blocks."""

import argparse
import json
import os
import re
import sys


HEADING_RE = re.compile(r"^\s{0,3}(#{1,4})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*([◦–□\-*])\s+(.*)$")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
SEPARATOR_RE = re.compile(r"^\s*---+\s*$")
IMAGE_REF_RE = re.compile(r"^\s*<그림\s+([0-9]+-[0-9]+)\s*:\s*(.*?)>\s*$")


def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_inline_segments(text: str) -> list[dict[str, str]]:
    token_re = re.compile(r"(\*\*[^*]+\*\*|\*[^*\n]+\*)")
    segments: list[dict[str, str]] = []
    pos = 0

    for match in token_re.finditer(text):
        if match.start() > pos:
            plain = text[pos : match.start()]
            if plain:
                segments.append({"type": "plain", "text": xml_escape(plain)})

        token = match.group(0)
        if token.startswith("**") and token.endswith("**"):
            content = token[2:-2]
            if content:
                segments.append({"type": "bold", "text": xml_escape(content)})
        elif token.startswith("*") and token.endswith("*"):
            content = token[1:-1]
            if content:
                segments.append({"type": "italic", "text": xml_escape(content)})

        pos = match.end()

    if pos < len(text):
        tail = text[pos:]
        if tail:
            segments.append({"type": "plain", "text": xml_escape(tail)})

    if not segments:
        segments.append({"type": "plain", "text": ""})
    return segments


def clean_text_to_segments(text: str) -> tuple[str, list[dict[str, str]]]:
    segments = parse_inline_segments(text.strip())
    joined = "".join(seg["text"] for seg in segments)
    return joined, segments


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and "|" in stripped[1:-1]


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    parts = stripped.split("|")[1:-1]
    return [xml_escape(cell.strip()) for cell in parts]


def is_table_delimiter(row: list[str]) -> bool:
    if not row:
        return False
    for cell in row:
        if not re.match(r"^:?-{3,}:?$", cell):
            return False
    return True


def parse_table(lines: list[str], start_idx: int) -> tuple[object | None, int]:
    rows: list[list[str]] = []
    idx = start_idx

    while idx < len(lines) and is_table_line(lines[idx]):
        rows.append(split_table_row(lines[idx]))
        idx += 1

    if not rows:
        return None, start_idx

    headers = rows[0]
    body = rows[1:]
    if body and is_table_delimiter(body[0]):
        body = body[1:]

    col_count = max([len(headers)] + [len(r) for r in body]) if (headers or body) else 0
    if col_count > 0:
        headers = headers + [""] * (col_count - len(headers))
        padded_rows: list[list[str]] = []
        for row in body:
            padded_rows.append(row + [""] * (col_count - len(row)))
        body = padded_rows

    block = {
        "type": "table",
        "headers": headers,
        "rows": body,
        "col_count": col_count,
    }
    return block, idx


def parse_markdown(content: str, source_file: str) -> dict[str, object]:
    lines = content.splitlines()
    blocks: list[dict[str, object]] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        if not stripped:
            idx += 1
            continue

        table_block, next_idx = parse_table(lines, idx)
        if table_block is not None:
            blocks.append(table_block)
            idx = next_idx
            continue

        if SEPARATOR_RE.match(line):
            blocks.append({"type": "separator"})
            idx += 1
            continue

        image_match = IMAGE_REF_RE.match(line)
        if image_match:
            image_id = image_match.group(1)
            caption = xml_escape(image_match.group(2).strip())
            blocks.append({"type": "image_ref", "id": image_id, "caption": caption})
            idx += 1
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            text, segments = clean_text_to_segments(heading_match.group(2))
            blocks.append(
                {"type": "heading", "level": level, "text": text, "segments": segments}
            )
            idx += 1
            continue

        bullet_match = BULLET_RE.match(line)
        if bullet_match:
            marker = bullet_match.group(1)
            text, segments = clean_text_to_segments(bullet_match.group(2))
            blocks.append(
                {"type": "bullet", "marker": marker, "text": text, "segments": segments}
            )
            idx += 1
            continue

        blockquote_match = BLOCKQUOTE_RE.match(line)
        if blockquote_match:
            text, segments = clean_text_to_segments(blockquote_match.group(1))
            blocks.append({"type": "blockquote", "text": text, "segments": segments})
            idx += 1
            continue

        para_lines = [line.strip()]
        idx += 1
        while idx < len(lines):
            next_line = lines[idx]
            next_stripped = next_line.strip()
            if not next_stripped:
                break
            if (
                is_table_line(next_line)
                or SEPARATOR_RE.match(next_line)
                or IMAGE_REF_RE.match(next_line)
                or HEADING_RE.match(next_line)
                or BULLET_RE.match(next_line)
                or BLOCKQUOTE_RE.match(next_line)
            ):
                break
            para_lines.append(next_line.strip())
            idx += 1

        text, segments = clean_text_to_segments(" ".join(para_lines))
        blocks.append({"type": "paragraph", "text": text, "segments": segments})

    return {"blocks": blocks, "source_file": source_file}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse markdown into structured JSON blocks"
    )
    _ = parser.add_argument("input", help="Path to input markdown file")
    _ = parser.add_argument("--output", "-o", help="Path to output JSON file")
    args = parser.parse_args()

    raw_input = getattr(args, "input", None)
    if not isinstance(raw_input, str):
        print("Error: Invalid input path", file=sys.stderr)
        sys.exit(1)
    input_path = raw_input

    raw_output = getattr(args, "output", None)
    if raw_output is not None and not isinstance(raw_output, str):
        print("Error: Invalid output path", file=sys.stderr)
        sys.exit(1)
    output_path = raw_output if raw_output else ""

    if not os.path.isfile(input_path):
        print("Error: File not found: {0}".format(input_path), file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    parsed = parse_markdown(content, input_path)
    output_text = json.dumps(parsed, ensure_ascii=False, indent=2)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            _ = f.write(output_text)
            _ = f.write("\n")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
