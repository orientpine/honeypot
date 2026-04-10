#!/usr/bin/env python3
"""Generate batch manifests for parallel absorption agents.

Reads raw/ingest_log.json and writes one manifest per batch into
raw/batches/{batch_id}.json. Batches are grouped automatically by
(source_top, source_category, first-level source_subcategory) and
assigned stable batch IDs derived from the group key.

Each manifest contains:
  - batch_id, label, description
  - wiki_target_dir (derived from the group key, ASCII snake_case)
  - entry_count
  - entry_files: list of filenames in raw/entries/
  - entries_meta: [{id, file, date, title, source_relative, word_count}]

This script is intentionally vault-agnostic. It does NOT hardcode any
personal project names or batch IDs. If a specific vault needs named
batches (e.g. one batch per research project), write a thin wrapper
that generates the manifests itself and calls this script only for
the leftover entries.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0] if __doc__ else ""
    )
    parser.add_argument(
        "--wiki-root",
        type=Path,
        required=True,
        help="Path to wiki/ directory (raw/ is resolved as its sibling)",
    )
    parser.add_argument(
        "--ingest-log",
        type=Path,
        default=None,
        help="Override path to ingest log (default: <wiki-root>/../raw/ingest_log.json)",
    )
    parser.add_argument(
        "--batches-dir",
        type=Path,
        default=None,
        help="Override output directory (default: <wiki-root>/../raw/batches)",
    )
    parser.add_argument(
        "--target-batches",
        type=int,
        default=None,
        help="Expected number of non-empty batches. Warns if the actual count differs by more than 30 percent",
    )
    parser.add_argument(
        "--max-entries-per-batch",
        type=int,
        default=150,
        help="Split any group larger than this into numbered sub-batches (default: 150)",
    )
    parser.add_argument(
        "--min-entries-per-batch",
        type=int,
        default=5,
        help="Merge groups smaller than this into a single leftover batch (default: 5)",
    )
    parser.add_argument(
        "--group-depth",
        type=int,
        default=2,
        help="Number of source path levels to use for grouping. 1=top only, 2=top+category, 3=top+category+subcategory (default: 2)",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    """Convert text to ASCII snake_case for use in filenames and batch IDs.

    For non-ASCII text with no ASCII equivalent, falls back to a stable
    hash-based slug so distinct non-ASCII groups never collide into
    a single directory.
    """
    if not text:
        return "unknown"
    original = text
    # Transliterate unicode to ASCII where possible
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Replace anything non-alphanumeric with underscore
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_").lower()
    if text:
        return text
    # Fallback for text with no ASCII content (e.g., pure Korean, Chinese, Arabic).
    # Use a stable hash suffix so distinct non-ASCII groups do not collide.
    import hashlib
    digest = hashlib.md5(original.encode("utf-8")).hexdigest()[:8]
    return f"grp_{digest}"


def group_key_of(entry: dict, depth: int) -> tuple[str, ...]:
    """Return the grouping tuple for an entry at the requested depth."""
    top = str(entry.get("source_top") or "").strip()
    cat = str(entry.get("source_category") or "").strip()
    sub = str(entry.get("source_subcategory") or "").strip()
    sub_first = sub.split("/")[0] if sub else ""
    if depth <= 1:
        return (top,)
    if depth == 2:
        return (top, cat)
    return (top, cat, sub_first)


def build_label(key: tuple[str, ...]) -> str:
    parts = [p for p in key if p]
    return " / ".join(parts) if parts else "(root)"


def split_oversize(entries: list[dict], max_size: int) -> list[list[dict]]:
    """Split a list of entries into chunks no larger than max_size."""
    if len(entries) <= max_size:
        return [entries]
    chunks: list[list[dict]] = []
    for i in range(0, len(entries), max_size):
        chunks.append(entries[i : i + max_size])
    return chunks


def main(args: argparse.Namespace) -> int:
    wiki_root = args.wiki_root.resolve()
    if not wiki_root.exists():
        print(f"ERROR: wiki root not found: {wiki_root}")
        return 1

    raw_root = wiki_root.parent / "raw"
    log_path = args.ingest_log or (raw_root / "ingest_log.json")
    batches_dir = args.batches_dir or (raw_root / "batches")

    if not log_path.exists():
        print(f"ERROR: ingest log not found: {log_path}")
        return 1

    log = json.loads(log_path.read_text(encoding="utf-8"))
    entries = log.get("entries", [])
    if not entries:
        print(f"ERROR: ingest log contains no entries: {log_path}")
        return 1

    batches_dir.mkdir(parents=True, exist_ok=True)

    # Group entries by the requested depth
    groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for entry in entries:
        key = group_key_of(entry, args.group_depth)
        groups[key].append(entry)

    # Sort groups by total entry count (largest first) for predictable IDs
    sorted_groups = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    # Collect tiny groups into a leftover bucket
    leftover: list[dict] = []
    main_groups: list[tuple[tuple[str, ...], list[dict]]] = []
    for key, group_entries in sorted_groups:
        if len(group_entries) < args.min_entries_per_batch:
            leftover.extend(group_entries)
        else:
            main_groups.append((key, group_entries))

    # Assign batch IDs (Bnn_slug) and split oversize groups
    manifests: list[dict] = []
    batch_index = 1
    for key, group_entries in main_groups:
        slug = "_".join(slugify(p) for p in key if p) or "root"
        chunks = split_oversize(group_entries, args.max_entries_per_batch)
        for chunk_idx, chunk in enumerate(chunks):
            suffix = f"_{chunk_idx + 1:02d}" if len(chunks) > 1 else ""
            batch_id = f"B{batch_index:02d}_{slug}{suffix}"
            manifests.append(
                {
                    "batch_id": batch_id,
                    "label": build_label(key)
                    + (
                        f" (part {chunk_idx + 1}/{len(chunks)})"
                        if len(chunks) > 1
                        else ""
                    ),
                    "description": f"Entries from {build_label(key)}",
                    "wiki_target_dir": f"{slug}{suffix}",
                    "entries": chunk,
                }
            )
            batch_index += 1

    # Add leftover batch if any
    if leftover:
        manifests.append(
            {
                "batch_id": f"B{batch_index:02d}_leftover",
                "label": f"Leftover entries ({len(leftover)})",
                "description": "Entries from small groups that did not meet the minimum batch size threshold.",
                "wiki_target_dir": "misc_leftover",
                "entries": leftover,
            }
        )

    # Write manifests
    summary_rows: list[tuple[str, str, int]] = []
    oversize: list[tuple[str, int]] = []
    total_assigned = 0
    for m in manifests:
        entry_chunk = m["entries"]
        manifest_out = {
            "batch_id": m["batch_id"],
            "label": m["label"],
            "description": m["description"],
            "wiki_target_dir": m["wiki_target_dir"],
            "entry_count": len(entry_chunk),
            "entry_files": [e.get("file", "") for e in entry_chunk],
            "entries_meta": [
                {
                    "id": e.get("id", ""),
                    "file": e.get("file", ""),
                    "date": e.get("date", ""),
                    "title": e.get("title", ""),
                    "source_relative": e.get("source_relative", ""),
                    "word_count": e.get("word_count", 0),
                }
                for e in entry_chunk
            ],
        }
        out_path = batches_dir / f"{m['batch_id']}.json"
        out_path.write_text(
            json.dumps(manifest_out, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        summary_rows.append((m["batch_id"], m["label"], len(entry_chunk)))
        total_assigned += len(entry_chunk)
        if args.max_entries_per_batch and len(entry_chunk) > args.max_entries_per_batch:
            oversize.append((m["batch_id"], len(entry_chunk)))

    # Print summary
    print(f"{'BATCH_ID':40s} {'COUNT':>6s}  LABEL")
    print("-" * 90)
    for bid, label, n in summary_rows:
        label_short = label[:40]
        print(f"{bid:40s} {n:6d}  {label_short}")
    print("-" * 90)
    print(f"{'TOTAL':40s} {total_assigned:6d}  across {len(manifests)} batches")

    if oversize:
        print("\nWARNING: oversized batches after split:")
        for bid, n in oversize:
            print(f"  {bid}: {n} entries")

    if args.target_batches is not None:
        actual = len(manifests)
        delta = abs(actual - args.target_batches) / max(1, args.target_batches)
        if delta > 0.3:
            print(
                f"\nWARNING: batch count {actual} differs from target {args.target_batches} by more than 30%."
            )

    unassigned = len(entries) - total_assigned
    if unassigned:
        print(f"\nWARNING: {unassigned} entries were not assigned to any batch.")

    print(f"\nWrote {len(manifests)} batch manifests to {batches_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
