#!/usr/bin/env python3
"""Ingest a project's doc/ markdown files into raw/entries/ for wiki-gen."""

# pyright: reportPrivateUsage=false, reportImplicitRelativeImport=false, reportUninitializedInstanceVariable=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportExplicitAny=false, reportUnusedCallResult=false

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingest_common import (
        DEFAULT_SKIP_DIR_NAMES,
        DATE_YYYYMMDD,
        ISO_DATETIME,
        Entry,
        log,
        parse_csv_set,
        slugify,
        parse_yaml_frontmatter,
        extract_heading_title,
        extract_tags,
        _valid_date,
        _extract_path_year,
        parse_date_fields,
        coerce_tag_list,
        coerce_alias_list,
        count_markdown_files,
        format_breakdown,
    )
else:
    from .ingest_common import (
        DEFAULT_SKIP_DIR_NAMES,
        DATE_YYYYMMDD,
        ISO_DATETIME,
        Entry,
        log,
        parse_csv_set,
        slugify,
        parse_yaml_frontmatter,
        extract_heading_title,
        extract_tags,
        _valid_date,
        _extract_path_year,
        parse_date_fields,
        coerce_tag_list,
        coerce_alias_list,
        count_markdown_files,
        format_breakdown,
    )


_SHARED_IMPORT_GUARD = (DATE_YYYYMMDD, ISO_DATETIME, _valid_date, _extract_path_year)


class CLIArgs(argparse.Namespace):
    source_root: Path
    wiki_root: Path
    source_name: str
    source_top: str
    source_category: str
    source_commit: str | None
    ingest_log: Path | None
    skip_dirs: str | None


def parse_args() -> CLIArgs:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0] if __doc__ else ""
    )
    _ = parser.add_argument(
        "--source-root", type=Path, required=True, help="Path to project doc/ directory"
    )
    _ = parser.add_argument(
        "--wiki-root", type=Path, required=True, help="Path to wiki/ directory"
    )
    _ = parser.add_argument(
        "--source-name", required=True, help="Source identifier, e.g. my_project"
    )
    _ = parser.add_argument(
        "--source-top", default="External", help="Top-level source category"
    )
    _ = parser.add_argument(
        "--source-category", default="Project", help="Source category"
    )
    _ = parser.add_argument(
        "--source-commit", default=None, help="Git commit SHA for tracking"
    )
    _ = parser.add_argument(
        "--ingest-log",
        type=Path,
        default=None,
        help="Path to raw/ingest_log.json (default: <wiki-root>/../raw/ingest_log.json)",
    )
    _ = parser.add_argument(
        "--skip-dirs",
        default=None,
        help="Comma-separated directory names to skip anywhere in the tree (default: standard exclusion list)",
    )
    return parser.parse_args(namespace=CLIArgs())


def walk_project_docs(
    source_root: Path, skip_dirs: set[str] | None = None
) -> list[Path]:
    """Walk source_root and return all .md files, skipping skip_dirs."""
    effective_skip = skip_dirs if skip_dirs is not None else DEFAULT_SKIP_DIR_NAMES
    result = []
    for p in sorted(source_root.rglob("*.md")):
        if any(part in effective_skip for part in p.parts):
            continue
        result.append(p)
    return result


def ingest_file(
    path: Path,
    source_root: Path,
    *,
    source_name: str,
    source_top: str,
    source_category: str,
    source_commit: str | None,
) -> tuple[Entry | None, str | None]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "decode_error"
    except OSError:
        return None, "read_error"

    fm, body = parse_yaml_frontmatter(raw_text)
    fm = fm or {}

    heading_title, body = extract_heading_title(body)
    title = str(fm.get("title") or heading_title or path.stem).strip()
    if not title:
        return None, "empty_title"

    try:
        file_stat = path.stat()
    except OSError:
        return None, "stat_error"

    rel_path = path.relative_to(source_root).as_posix()
    date, time_s, date_source = parse_date_fields(
        fm, {}, path.stem, file_stat, rel_path
    )

    fm_tags = coerce_tag_list(fm.get("tags"))
    body_tags = extract_tags(body)
    tags = sorted({tag for tag in [*fm_tags, *body_tags] if tag})
    aliases = coerce_alias_list(fm.get("aliases"))

    normalized_body = body.strip("\n")
    combined = f"{source_name}:{rel_path}"
    entry_id = hashlib.sha1(combined.encode("utf-8")).hexdigest()[:12]

    return (
        Entry(
            id=entry_id,
            date=date,
            time=time_s,
            title=title,
            source_type="project",
            source_path=str(path),
            source_relative=rel_path,
            source_top=source_top,
            source_category=source_category,
            source_subcategory="",
            tags=tags,
            author=str(fm.get("author")).strip() if fm.get("author") else None,
            word_count=len(normalized_body.split()),
            char_count=len(normalized_body),
            line_count=len(normalized_body.splitlines()),
            aliases=aliases,
            extra={
                "date_source": date_source,
                "source_name": source_name,
                "source_commit": source_commit,
                "original_path": str(path),
            },
            body=normalized_body,
        ),
        None,
    )


def main(args: CLIArgs) -> int:
    source_root = args.source_root.resolve()
    wiki_root = args.wiki_root.resolve()
    raw_root = wiki_root.parent / "raw"
    entries_dir = raw_root / "entries" / args.source_name
    ingest_log = (
        args.ingest_log.resolve() if args.ingest_log else (raw_root / "ingest_log.json")
    )
    skip_dir_names = parse_csv_set(args.skip_dirs) or set(DEFAULT_SKIP_DIR_NAMES)

    if not source_root.exists():
        log(f"ERROR: source not found: {source_root}")
        return 1
    if not wiki_root.exists():
        log(f"ERROR: wiki root not found: {wiki_root}")
        return 1

    entries_dir.mkdir(parents=True, exist_ok=True)

    scanned_total = count_markdown_files(source_root)
    log(f"Walking source: {source_root}")
    md_files = walk_project_docs(source_root, skip_dir_names)
    log(f"Found {len(md_files)} markdown files after directory filtering")

    produced: list[dict[str, Any]] = []
    seen_names: dict[str, int] = {}
    ingest_skip_counts: Counter[str] = Counter()
    skip_breakdown: Counter[str] = Counter()
    written = 0

    filtered_out = max(0, scanned_total - len(md_files))
    if filtered_out:
        skip_breakdown["skip_dirs"] = filtered_out

    for idx, md in enumerate(md_files, start=1):
        entry, skip_reason = ingest_file(
            md,
            source_root,
            source_name=args.source_name,
            source_top=args.source_top,
            source_category=args.source_category,
            source_commit=args.source_commit,
        )
        if entry is None:
            ingest_skip_counts[skip_reason or "unknown"] += 1
            continue

        slug = slugify(entry.title)
        base_name = f"{entry.date}_{slug}_{entry.id}.md"
        if base_name in seen_names:
            seen_names[base_name] += 1
            base_name = f"{entry.date}_{slug}_{entry.id}_{seen_names[base_name]}.md"
        else:
            seen_names[base_name] = 0

        out_path = entries_dir / base_name
        try:
            out_path.write_text(entry.to_markdown(), encoding="utf-8", newline="\n")
            written += 1
        except OSError as exc:
            log(f"WRITE ERROR: {out_path} -- {exc}")
            ingest_skip_counts["write_error"] += 1
            continue

        file_field = f"{args.source_name}/{md.name}"
        produced.append(
            {
                "id": entry.id,
                "file": file_field,
                "source_name": args.source_name,
                "date": entry.date,
                "title": entry.title,
                "source_top": entry.source_top,
                "source_category": entry.source_category,
                "source_subcategory": entry.source_subcategory,
                "source_relative": entry.source_relative,
                "word_count": entry.word_count,
                "tags": entry.tags,
            }
        )

        if idx % 200 == 0:
            log(f"  ... processed {idx}/{len(md_files)}")

    total_skipped = sum(skip_breakdown.values()) + sum(ingest_skip_counts.values())
    ingest_log.parent.mkdir(parents=True, exist_ok=True)
    ingest_log.write_text(
        json.dumps(
            {
                "source_root": str(source_root),
                "source_name": args.source_name,
                "wiki_root": str(wiki_root),
                "entries_dir": str(entries_dir),
                "total_files": len(md_files),
                "written": written,
                "skipped": total_skipped,
                "skipped_breakdown": dict(skip_breakdown + ingest_skip_counts),
                "ingested_at": datetime.now().isoformat(timespec="seconds"),
                "skip_dir_names": sorted(skip_dir_names),
                "source_top": args.source_top,
                "source_category": args.source_category,
                "source_commit": args.source_commit,
                "entries": produced,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    combined_breakdown: Counter[str] = skip_breakdown + ingest_skip_counts
    log(
        f"Scanned: {len(md_files)} files. Skipped: {total_skipped} ({format_breakdown(combined_breakdown)}). Ingested: {written} entries."
    )
    log(f"Log: {ingest_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
