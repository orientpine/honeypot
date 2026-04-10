# Sources Schema Reference

## Overview
The `sources.yaml` file defines the data sources for the `wiki-gen` plugin. It should be located at the project root. This file tells the wiki system where to find your notes, projects, and other content to ingest into the wiki.

## Example sources.yaml
```yaml
# sources.yaml — wiki source configuration
sources:
  # Existing Obsidian vault (legacy support)
  - name: obsidian
    type: obsidian
    source_root: /home/cha/Documents/git-obsidian
    include_top_dirs: 000_PARA,001_KIMM_PARA

  # Git remote project
  - name: kimm_excavator_v2
    type: git
    url: https://github.com/orientpine/kimm-excavator-v2.git
    branch: main
    doc_path: doc/
    source_top: KIMM
    source_category: Project

  # Local project
  - name: retirement_seminar_2026
    type: local
    path: /home/cha/Documents/projects/retirement-seminar-2026
    doc_path: doc/
    source_top: Personal
    source_category: Project

settings:
  entries_subdir: true
  id_strategy: source_prefixed
  sync_cache_dir: .sync_cache
  post_sync:
    - rebuild_index
    - check_coverage
```

## Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `sources` | list | Yes | - | List of source configurations. |
| `settings` | object | No | - | Global settings for the sync process. |

### Source Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for the source. Must match `^[a-z0-9][a-z0-9_-]*$`. |
| `type` | string | Yes | Type of source: `obsidian`, `git`, or `local`. |

### Type-Specific Fields

#### obsidian
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_root` | string | Yes | Local path to the Obsidian vault. |
| `include_top_dirs` | string | No | Comma-separated list of top-level directories to include. |
| `skip_dirs` | string | No | Comma-separated list of directories to skip. |

#### git
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | URL of the git repository. |
| `branch` | string | No | Branch to clone (default: `main`). |
| `doc_path` | string | No | Path within the repo containing documentation (default: root). |
| `source_top` | string | Yes | Top-level category for the wiki (e.g., KIMM). |
| `source_category` | string | Yes | Sub-category for the wiki (e.g., Project). |

#### local
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Local path to the project. |
| `doc_path` | string | No | Path within the project containing documentation (default: root). |
| `source_top` | string | Yes | Top-level category for the wiki. |
| `source_category` | string | Yes | Sub-category for the wiki. |

## Settings Block

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `entries_subdir` | boolean | `true` | Whether to organize ingested entries into subdirectories. |
| `id_strategy` | string | `source_prefixed` | Strategy for generating entry IDs. `source_prefixed` or `legacy`. |
| `sync_cache_dir` | string | `.sync_cache` | Directory to store sync metadata and cache. |
| `post_sync` | list | `[]` | List of commands to run after sync (e.g., `rebuild_index`, `check_coverage`). |

## Validation Rules

### Name Field
- **Regex**: `^[a-z0-9][a-z0-9_-]*$`
- Must consist of lowercase letters, numbers, hyphens, or underscores.
- Cannot start with a hyphen or underscore.
- Must be unique within the `sources.yaml` file.

## Error Handling
- **Invalid URL**: If a git URL is malformed or unreachable, the sync will fail for that source.
- **Inaccessible Path**: If a local path or Obsidian root does not exist or is not readable, an error will be logged.
- **Duplicate Names**: Duplicate source names will trigger a validation error before processing.
