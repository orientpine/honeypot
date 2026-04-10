#!/usr/bin/env python3
"""Sync multiple configured sources into wiki-gen raw entries."""

# pyright: reportMissingModuleSource=false, reportImplicitRelativeImport=false, reportUninitializedInstanceVariable=false, reportExplicitAny=false, reportAny=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false, reportImplicitStringConcatenation=false

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingest_common import DEFAULT_SKIP_DIR_NAMES, parse_csv_set
    from ingest_obsidian import load_submodule_paths, walk_markdown
    from ingest_projects import walk_project_docs
else:
    from .ingest_common import DEFAULT_SKIP_DIR_NAMES, parse_csv_set
    from .ingest_obsidian import load_submodule_paths, walk_markdown
    from .ingest_projects import walk_project_docs


NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ID_LINE_RE = re.compile(r"^id:\s*([^\n]+)$", re.MULTILINE)


class CLIArgs(argparse.Namespace):
    config: Path
    wiki_root: Path
    source: str | None
    dry_run: bool
    force: bool


def parse_args() -> CLIArgs:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0] if __doc__ else ""
    )
    _ = parser.add_argument(
        "--config", type=Path, required=True, help="Path to sources.yaml"
    )
    _ = parser.add_argument(
        "--wiki-root", type=Path, required=True, help="Path to wiki/ directory"
    )
    _ = parser.add_argument("--source", help="Sync only this source name")
    _ = parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    _ = parser.add_argument(
        "--force", action="store_true", help="Ignore cache and re-sync everything"
    )
    return parser.parse_args(namespace=CLIArgs())


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_csv_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return ",".join(items) if items else None
    text = str(value).strip()
    return text or None


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def entry_id_for_source(source_name: str, source_type: str, rel_path: str) -> str:
    base = rel_path if source_type == "obsidian" else f"{source_name}:{rel_path}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def extract_entry_id(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    match = ID_LINE_RE.search(text)
    return match.group(1).strip() if match else None


def run_script(script_name: str, args: list[str]) -> int:
    script_dir = Path(__file__).parent.resolve()
    result = subprocess.run(
        [sys.executable, str(script_dir / script_name)] + args, capture_output=False
    )
    return result.returncode


def git_output(args: list[str], cwd: Path) -> str | None:
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def latest_mtime_token(root: Path) -> str:
    latest = root.stat().st_mtime if root.exists() else 0.0
    for path in root.rglob("*.md"):
        if path.is_file():
            latest = max(latest, path.stat().st_mtime)
    return f"local-{int(latest)}"


def load_config(config_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with config_path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise SystemExit("ERROR: sources config must be a mapping")
    sources = config.get("sources", [])
    settings = config.get("settings", {})
    if not isinstance(sources, list):
        raise SystemExit("ERROR: 'sources' must be a list")
    if not isinstance(settings, dict):
        raise SystemExit("ERROR: 'settings' must be a mapping")
    seen_names: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for raw_source in sources:
        if not isinstance(raw_source, dict):
            raise SystemExit("ERROR: each source must be a mapping")
        source = dict(raw_source)
        name = str(source.get("name", "")).strip()
        if not NAME_RE.match(name):
            raise SystemExit(
                f"ERROR: Invalid source name '{name}'. Must match ^[a-z0-9][a-z0-9_-]*$"
            )
        if name in seen_names:
            raise SystemExit(f"ERROR: Duplicate source name '{name}'")
        seen_names.add(name)
        normalized.append(source)
    return normalized, settings


def select_sources(
    sources: list[dict[str, Any]], target: str | None
) -> list[dict[str, Any]]:
    if not target:
        return sources
    selected = [source for source in sources if source.get("name") == target]
    if not selected:
        raise SystemExit(f"ERROR: source not found in config: {target}")
    return selected


def sparse_clone(
    source: dict[str, Any], wiki_root: Path, force: bool
) -> tuple[Path, str | None]:
    name = str(source["name"])
    repo_url = str(source.get("repo") or source.get("url") or "").strip()
    if not repo_url:
        raise ValueError(f"git source '{name}' missing repo/url")
    branch = str(source.get("branch") or "HEAD").strip()
    cache_root = wiki_root.parent / ".sync_cache"
    repo_root = cache_root / name
    doc_path = Path(str(source.get("doc_path", "")).strip())
    if force and repo_root.exists():
        shutil.rmtree(repo_root)
    cache_root.mkdir(parents=True, exist_ok=True)
    if not repo_root.exists():
        clone_cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            repo_url,
            str(repo_root),
        ]
        if branch and branch != "HEAD":
            clone_cmd[2:2] = ["--branch", branch]
        if subprocess.run(clone_cmd, capture_output=False).returncode != 0:
            raise RuntimeError(f"git clone failed for {name}")
    else:
        if (
            subprocess.run(
                ["git", "-C", str(repo_root), "fetch", "--depth", "1", "origin"],
                capture_output=False,
            ).returncode
            != 0
        ):
            raise RuntimeError(f"git fetch failed for {name}")
        if branch and branch != "HEAD":
            reset_target = f"origin/{branch}"
            if (
                subprocess.run(
                    ["git", "-C", str(repo_root), "reset", "--hard", reset_target],
                    capture_output=False,
                ).returncode
                != 0
            ):
                raise RuntimeError(f"git reset failed for {name}")
        elif (
            subprocess.run(
                ["git", "-C", str(repo_root), "pull", "--ff-only"], capture_output=False
            ).returncode
            != 0
        ):
            raise RuntimeError(f"git pull failed for {name}")
    if doc_path.as_posix() not in ("", "."):
        if (
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "sparse-checkout",
                    "set",
                    doc_path.as_posix(),
                ],
                capture_output=False,
            ).returncode
            != 0
        ):
            raise RuntimeError(f"git sparse-checkout failed for {name}")
    commit = git_output(["git", "rev-parse", "HEAD"], repo_root)
    return (repo_root / doc_path).resolve(), commit


def resolve_source_root(
    source: dict[str, Any], wiki_root: Path, force: bool
) -> tuple[Path, str | None]:
    source_type = str(source.get("type", "")).strip()
    if source_type == "obsidian":
        root = (
            Path(str(source.get("source_root") or source.get("path") or ""))
            .expanduser()
            .resolve()
        )
        return root, latest_mtime_token(root)
    if source_type == "local":
        root = (
            Path(str(source["path"])).expanduser() / str(source.get("doc_path", ""))
        ).resolve()
        return root, latest_mtime_token(root)
    if source_type == "git":
        return sparse_clone(source, wiki_root, force)
    raise ValueError(f"unsupported source type: {source_type}")


def scan_source_files(
    source: dict[str, Any], doc_root: Path
) -> dict[str, dict[str, str]]:
    source_type = str(source.get("type", "")).strip()
    files: dict[str, dict[str, str]] = {}
    if source_type == "obsidian":
        include_top_dirs = parse_csv_set(
            normalize_csv_value(source.get("include_top_dirs"))
        )
        skip_dirs = parse_csv_set(normalize_csv_value(source.get("skip_dirs"))) or set(
            DEFAULT_SKIP_DIR_NAMES
        )
        submodules = load_submodule_paths(doc_root)
        markdown_files, _ = walk_markdown(
            doc_root, include_top_dirs, skip_dirs, submodules
        )
        for path in markdown_files:
            rel_path = path.relative_to(doc_root).as_posix()
            files[rel_path] = {"path": str(path), "content_hash": file_hash(path)}
        return files
    skip_dirs = parse_csv_set(normalize_csv_value(source.get("skip_dirs"))) or set(
        DEFAULT_SKIP_DIR_NAMES
    )
    for path in walk_project_docs(doc_root, skip_dirs):
        rel_path = path.relative_to(doc_root).as_posix()
        files[rel_path] = {"path": str(path), "content_hash": file_hash(path)}
    return files


def build_diff(
    prev_files: dict[str, Any], current_files: dict[str, dict[str, str]], force: bool
) -> dict[str, Any]:
    prev_keys = set(prev_files)
    current_keys = set(current_files)
    added = current_keys - prev_keys
    deleted = prev_keys - current_keys
    updated = {
        rel_path
        for rel_path in (prev_keys & current_keys)
        if force
        or prev_files.get(rel_path, {}).get("content_hash")
        != current_files[rel_path]["content_hash"]
    }
    unchanged = (prev_keys & current_keys) - updated
    return {
        "added": sorted(added),
        "updated": sorted(updated),
        "unchanged": sorted(unchanged),
        "deleted": sorted(deleted),
        "needs_sync": force or bool(added or updated or deleted),
    }


def existing_entries_for_source(
    existing_log: dict[str, Any], source_name: str
) -> list[dict[str, Any]]:
    entries = existing_log.get("entries", [])
    return [dict(entry) for entry in entries if entry.get("source_name") == source_name]


def backup_entries(
    raw_entries_dir: Path, source_name: str, source_type: str, entry_ids: set[str]
) -> tuple[Path | None, list[tuple[Path, Path]]]:
    backup_root = (
        raw_entries_dir.parent
        / ".sync_backup"
        / f"{source_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    if source_type in ("local", "git"):
        source_dir = raw_entries_dir / source_name
        if source_dir.exists():
            backup_root.parent.mkdir(parents=True, exist_ok=True)
            source_dir.rename(backup_root)
            return backup_root, []
        return None, []
    moved: list[tuple[Path, Path]] = []
    if not entry_ids:
        return None, moved
    for path in sorted(raw_entries_dir.glob("*.md")):
        if extract_entry_id(path) not in entry_ids:
            continue
        target = backup_root / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        path.rename(target)
        moved.append((path, target))
    return (backup_root if moved else None), moved


def restore_entries(
    raw_entries_dir: Path,
    source_name: str,
    source_type: str,
    backup_root: Path | None,
    moved_files: list[tuple[Path, Path]],
) -> None:
    if source_type in ("local", "git"):
        if backup_root is None or not backup_root.exists():
            return
        current_dir = raw_entries_dir / source_name
        if current_dir.exists():
            shutil.rmtree(current_dir)
        backup_root.rename(current_dir)
        return
    for original, backup in moved_files:
        if original.exists():
            original.unlink()
        if backup.exists():
            backup.rename(original)
    if backup_root and backup_root.exists():
        shutil.rmtree(backup_root, ignore_errors=True)


def discard_backup(backup_root: Path | None) -> None:
    if backup_root and backup_root.exists():
        shutil.rmtree(backup_root, ignore_errors=True)


def run_ingest(
    source: dict[str, Any],
    doc_root: Path,
    wiki_root: Path,
    temp_log: Path,
    source_commit: str | None,
) -> int:
    source_type = str(source.get("type", "")).strip()
    name = str(source["name"])
    if source_type == "obsidian":
        args = [
            "--source-root",
            str(doc_root),
            "--wiki-root",
            str(wiki_root),
            "--ingest-log",
            str(temp_log),
        ]
        include_top_dirs = normalize_csv_value(source.get("include_top_dirs"))
        skip_dirs = normalize_csv_value(source.get("skip_dirs"))
        if include_top_dirs:
            args += ["--include-top-dirs", include_top_dirs]
        if skip_dirs:
            args += ["--skip-dirs", skip_dirs]
        return run_script("ingest_obsidian.py", args)
    args = [
        "--source-root",
        str(doc_root),
        "--wiki-root",
        str(wiki_root),
        "--source-name",
        name,
        "--source-top",
        str(source.get("source_top", "External")),
        "--source-category",
        str(source.get("source_category", "Project")),
        "--ingest-log",
        str(temp_log),
    ]
    if source_commit:
        args += ["--source-commit", source_commit]
    skip_dirs = normalize_csv_value(source.get("skip_dirs"))
    if skip_dirs:
        args += ["--skip-dirs", skip_dirs]
    return run_script("ingest_projects.py", args)


def normalize_merged_entries(
    entries: list[dict[str, Any]], source_name: str
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        row = dict(entry)
        row.setdefault("source_name", source_name)
        normalized.append(row)
    return normalized


def merge_ingest_logs(
    wiki_root: Path, source_names: list[str], entries: list[dict[str, Any]]
) -> None:
    raw_dir = wiki_root.parent / "raw"
    payload = {
        "source_root": "(multiple)",
        "sources": source_names,
        "entries_dir": str(raw_dir / "entries"),
        "total_files": len(entries),
        "ingested_at": now_iso(),
        "entries": entries,
    }
    write_json(raw_dir / "ingest_log.json", payload)


def main(args: CLIArgs) -> int:
    config_path = args.config.resolve()
    wiki_root = args.wiki_root.resolve()
    if not config_path.exists():
        print(f"ERROR: config not found: {config_path}")
        return 1
    if not wiki_root.exists():
        print(f"ERROR: wiki root not found: {wiki_root}")
        return 1

    sources, _settings = load_config(config_path)
    selected_sources = select_sources(sources, args.source)
    raw_root = wiki_root.parent / "raw"
    raw_entries_dir = raw_root / "entries"
    sync_log_path = wiki_root.parent / "sync_log.json"
    sync_log = read_json(sync_log_path, {"last_sync": None, "sources": {}})
    sync_log.setdefault("sources", {})
    existing_ingest_log = read_json(raw_root / "ingest_log.json", {})
    tmp_root = raw_root / ".sync_tmp"

    totals = {"added": 0, "updated": 0, "unchanged": 0, "deleted": 0}
    selected_names = {str(source["name"]) for source in selected_sources}
    existing_entries = (
        existing_ingest_log.get("entries", [])
        if isinstance(existing_ingest_log, dict)
        else []
    )
    merged_entries = [
        dict(entry)
        for entry in existing_entries
        if entry.get("source_name") not in selected_names
    ]
    successful_sources = sorted(
        {
            str(entry.get("source_name"))
            for entry in merged_entries
            if str(entry.get("source_name", "")).strip()
        }
    )

    for source in selected_sources:
        name = str(source["name"])
        source_type = str(source.get("type", "")).strip()
        source_log = dict(sync_log["sources"].get(name, {}))
        prev_files = (
            source_log.get("files", {})
            if isinstance(source_log.get("files", {}), dict)
            else {}
        )
        try:
            doc_root, commit = resolve_source_root(source, wiki_root, args.force)
            if not doc_root.exists():
                raise FileNotFoundError(f"source root not found: {doc_root}")
            current_files = scan_source_files(source, doc_root)
        except Exception as exc:
            warn(f"{name}: scan failed: {exc}")
            merged_entries.extend(
                existing_entries_for_source(existing_ingest_log, name)
            )
            continue

        diff = build_diff(prev_files, current_files, args.force)
        for key in totals:
            totals[key] += len(diff[key])

        if args.dry_run:
            print(
                f"[dry-run] {name}: added={len(diff['added'])}, updated={len(diff['updated'])}, "
                f"unchanged={len(diff['unchanged'])}, deleted={len(diff['deleted'])}"
            )
            merged_entries.extend(
                existing_entries_for_source(existing_ingest_log, name)
            )
            successful_sources.append(name)
            continue

        if not diff["needs_sync"]:
            merged_entries.extend(
                existing_entries_for_source(existing_ingest_log, name)
            )
            successful_sources.append(name)
            continue

        entry_ids_to_backup = {
            str(meta.get("entry_id", "")).strip()
            for meta in prev_files.values()
            if meta.get("entry_id")
        }
        backup_root, moved_files = backup_entries(
            raw_entries_dir, name, source_type, entry_ids_to_backup
        )
        temp_log = tmp_root / f"{name}.json"
        temp_log.parent.mkdir(parents=True, exist_ok=True)

        rc = run_ingest(source, doc_root, wiki_root, temp_log, commit)
        if rc != 0:
            restore_entries(
                raw_entries_dir, name, source_type, backup_root, moved_files
            )
            warn(f"{name}: ingest failed with exit code {rc}")
            merged_entries.extend(
                existing_entries_for_source(existing_ingest_log, name)
            )
            continue

        temp_payload = read_json(temp_log, {})
        temp_entries = normalize_merged_entries(temp_payload.get("entries", []), name)
        discard_backup(backup_root)
        temp_log.unlink(missing_ok=True)
        sync_log["sources"][name] = {
            "last_sync": now_iso(),
            "commit": commit or latest_mtime_token(doc_root),
            "files": {
                rel_path: {
                    "content_hash": meta["content_hash"],
                    "entry_id": entry_id_for_source(name, source_type, rel_path),
                    "synced_at": now_iso(),
                }
                for rel_path, meta in sorted(current_files.items())
            },
        }
        merged_entries.extend(temp_entries)
        successful_sources.append(name)

    if args.dry_run:
        print(
            f"Sync complete: added={totals['added']}, updated={totals['updated']}, "
            f"unchanged={totals['unchanged']}, deleted={totals['deleted']}"
        )
        return 0

    merge_ingest_logs(wiki_root, successful_sources, merged_entries)
    sync_log["last_sync"] = now_iso()
    write_json(sync_log_path, sync_log)

    for script_name in ("rebuild_index.py", "check_coverage.py"):
        rc = run_script(script_name, ["--wiki-root", str(wiki_root)])
        if rc != 0:
            warn(f"post-sync script failed: {script_name} ({rc})")

    print(
        f"Sync complete: added={totals['added']}, updated={totals['updated']}, "
        f"unchanged={totals['unchanged']}, deleted={totals['deleted']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
