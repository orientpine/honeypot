#!/usr/bin/env python3
"""Merge multiple markdown files into one JSON block structure."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast

_HERE = Path(__file__).parent

Block = dict[str, object]


class ParseMarkdownFn(Protocol):
    def __call__(self, content: str, source_file: str) -> dict[str, object]: ...


def _load_md_parser() -> ModuleType:
    spec = importlib.util.spec_from_file_location("md_parser", _HERE / "md_parser.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load md_parser module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_md_parser = _load_md_parser()
parse_markdown = cast(ParseMarkdownFn, _md_parser.parse_markdown)


def _read_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def _min_heading_level(blocks: list[Block]) -> int | None:
    heading_levels: list[int] = []
    for block in blocks:
        if block.get("type") != "heading":
            continue
        level = block.get("level")
        if isinstance(level, int):
            heading_levels.append(level)
    if not heading_levels:
        return None
    return min(heading_levels)


def _offset_headings(blocks: list[Block], offset: int) -> list[Block]:
    if offset == 0:
        return [dict(block) for block in blocks]

    adjusted: list[Block] = []
    for block in blocks:
        copied = dict(block)
        level = copied.get("level")
        if copied.get("type") == "heading" and isinstance(level, int):
            copied["level"] = level + offset
        adjusted.append(copied)
    return adjusted


def merge_markdown_files(
    file_paths: list[str], target_level: int = 1
) -> dict[str, object]:
    if len(file_paths) == 1:
        content = _read_text(file_paths[0])
        return parse_markdown(content, file_paths[0])

    parsed_results: list[dict[str, object]] = []
    for file_path in file_paths:
        content = _read_text(file_path)
        if not content.strip():
            continue
        parsed_results.append(parse_markdown(content, file_path))

    combined_blocks: list[Block] = []
    for idx, parsed in enumerate(parsed_results):
        raw_blocks = parsed.get("blocks", [])
        if not isinstance(raw_blocks, list):
            continue
        block_items = cast(list[object], raw_blocks)
        blocks = [cast(Block, item) for item in block_items if isinstance(item, dict)]

        min_level = _min_heading_level(blocks)
        offset = 0 if min_level is None else target_level - min_level
        combined_blocks.extend(_offset_headings(blocks, offset))

        if idx < len(parsed_results) - 1:
            combined_blocks.append({"type": "separator"})

    return {"blocks": combined_blocks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("files", nargs="+")
    _ = parser.add_argument("--target-level", type=int, default=1)
    _ = parser.add_argument("--output", "-o")
    args = parser.parse_args()

    raw_files = getattr(args, "files", None)
    if not isinstance(raw_files, list):
        raise SystemExit("Invalid file arguments")
    file_items = cast(list[object], raw_files)
    files: list[str] = []
    for item in file_items:
        if not isinstance(item, str):
            raise SystemExit("Invalid file arguments")
        files.append(item)

    raw_target_level = getattr(args, "target_level", 1)
    if not isinstance(raw_target_level, int):
        raise SystemExit("Invalid target level")
    target_level = raw_target_level

    raw_output = getattr(args, "output", None)
    if raw_output is not None and not isinstance(raw_output, str):
        raise SystemExit("Invalid output path")
    output = raw_output

    result = merge_markdown_files(files, target_level)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
