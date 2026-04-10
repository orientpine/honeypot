# Ingest Spec

### Script Execution and Path Resolution (MANDATORY)

Helper scripts live under the skill's `scripts/` directory. When an agent needs to run one, it must resolve the script path in this priority order, per project convention:

**Step 1. Relative path (preferred).**
From the skill context, reference the script by its relative path:

```bash
python scripts/ingest_obsidian.py --source-root <vault_path> --wiki-root <project_path>
python scripts/rebuild_index.py --wiki-root <wiki_path>
python scripts/check_coverage.py --wiki-root <wiki_path>
```

**Step 2. Glob fallback** if relative path resolution fails:

```
**/wiki-gen/skills/wiki-gen/scripts/{script-name}.py
```

**Step 3. Expanded glob** if the plugin is installed in a non-standard location:

```
**/{script-name}.py
```

**Forbidden behavior:** if an agent cannot find a bundled script, it must report the failure and ask the user to confirm the path. **Never** write a replacement Python script from scratch. The bundled scripts encode tested logic from real use and must not be silently re-implemented.

All bundled scripts accept CLI arguments. No script has hardcoded user paths. Pass the appropriate `--wiki-root`, `--source-root`, or `--ingest-log` values explicitly.

### Supported Data Formats

The ingest script should auto-detect the format. Here's how to handle common ones:

**Day One JSON** (`*.json` with `entries` array):
Each entry becomes a file. Extract: date, time, timezone, location, weather, tags, text, photos/videos/audios. Map `dayone-moment://` URLs to relative file paths.

**Apple Notes** (exported `.html`, `.txt`, or `.md` files):
Each note becomes a file. Extract: title (first line or filename), creation date (from metadata or filename), folder/tag, body text. Strip HTML formatting if needed.

**Obsidian Vault** (folder of `.md` files):
Each note becomes a file. Preserve frontmatter. Extract: title, date (from frontmatter or filename), tags, body. Convert `[[wikilinks]]` to plain text for raw entries.

**Notion Export** (`.md` or `.csv` files):
Each page becomes a file. Extract: title, properties/metadata, body. Handle nested pages by flattening with parent context.

**Plain Text / Markdown Files** (folder of `.txt` or `.md`):
Each file becomes an entry. Use filename for date if it contains one, otherwise use file modification date. First line or filename becomes the title.

**iMessage Export** (`.csv` or chat logs):
Group by conversation and date. Each day's conversation with one person becomes an entry. Extract: date, participants, messages.

**CSV / Spreadsheet** (`.csv`, `.tsv`):
Each row becomes an entry. Use column headers as frontmatter fields. Identify the date column and text/content column automatically.

**Email Export** (`.mbox`, `.eml`):
Each email becomes an entry. Extract: date, from, to, subject, body. Strip signatures and quoted replies.

**Twitter/X Archive** (`tweet.js` or archive export):
Each tweet becomes an entry. Extract: date, text, media URLs, reply context, engagement stats.

### Standard Exclusions

The ingest script MUST skip these directories anywhere in the source tree:

```python
SKIP_DIR_NAMES = {
    # Version control
    ".git", ".svn", ".hg",
    # Obsidian meta
    ".obsidian", ".trash",
    # AI/IDE settings
    ".claude", ".cursor", ".vscode", ".opencode", ".idea",
    # Python/Node caches
    ".ruff_cache", ".mypy_cache", ".pytest_cache",
    "__pycache__", ".venv", "venv", "env",
    # JS dependencies (frequent source of README pollution)
    "node_modules",
    # OS
    ".DS_Store", "Thumbs.db",
}
```

Additionally:

1. **Git submodules**: read `.gitmodules` at vault root. For each `path = X` entry, add `X` to the skip list. Submodules are separate projects, not personal knowledge.

2. **Empty files**: skip any `.md` file whose content, after stripping frontmatter, is empty or whitespace-only.

3. **Generated pipeline outputs**: if the user's vault uses tools that produce derivative files such as `output/` directories with prompts, logs, or generated docs, decide case by case whether they are personal knowledge or technical artifacts. Default to include only if meaningful authored content exists.

#### Required logging

Always log skip counts at the end of ingest:

```
Scanned: 2280 markdown files in vault
Skipped: 454 files
  - node_modules: 447 (library README files)
  - agent-video-generation submodule: 6
  - empty files: 1
Ingested: 1826 personal knowledge entries -> raw/entries/
```

#### Safety warning

If any single exclusion skips more than 1000 files, warn the user and confirm that the exclusion is intentional:

```
WARNING: node_modules exclusion will skip 1247 markdown files.
This is unusually high. Is your source vault inside a JS project?
Confirm before proceeding.
```

### Output Format

Each file: `{date}_{id}.md` with YAML frontmatter:

```yaml
---
id: <unique identifier>
date: YYYY-MM-DD
time: "HH:MM:SS"
source_type: <dayone|apple-notes|obsidian|notion|text|imessage|csv|email|twitter>
tags: []
# ... any other metadata from the source
---

<entry text content>
```

The script must be **idempotent**. Running it twice produces the same output.

### Date Extraction (MANDATORY priority order)

Try these sources in order. Accept the first one that yields a valid calendar date (year between 1990 and 2030, with real calendar validation via `datetime.date()` so invalid dates like February 30 are rejected):

| Priority | Source | Example | Notes |
|:-:|---|---|---|
| 1 | Frontmatter `created:` | `created: 2024-03-15T10:30:00` | Most reliable |
| 2 | Frontmatter `date:` | `date: 2024-03-15` | |
| 3 | Frontmatter `modified:` | `modified: 2024-03-16` | Only if no created |
| 4 | Obsidian `[!info]` callout `Created:` | `> **Created**: 2024-03-15` | Skip if Dataview expression `` `=...` `` |
| 5 | Filename | `2024-03-15_meeting.md`, `20240315_meeting.md` | Validate |
| 6 | Source path full date | `Archive/2024-03/15/note.md` | |
| 7 | Source path year | `Archive/2024/note.md` -> `2024-01-01` | Tag `date_source: source_year` |
| 8 | File mtime | Filesystem last-modified | Last resort. Tag `date_source: mtime`. Warn user if more than 20% of entries fall here. |

#### Validation regex

```python
DATE_RE = re.compile(r"(?<!\d)(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})(?!\d)")

def valid_date(y, m, d):
    """Validate against the real calendar using datetime."""
    import datetime
    if not (1990 <= y <= 2030):
        return False
    try:
        datetime.date(y, m, d)
        return True
    except ValueError:
        return False

def extract_date(source, priority):
    for match in DATE_RE.finditer(source):
        y, m, d = map(int, match.groups())
        if valid_date(y, m, d):
            return (y, m, d)
    return None
```

#### Critical: Never scan body text for dates

Body text frequently contains:

- Date ranges such as `기간: 2015-2025`, which a naive regex may parse as year 2015, month 20, day 25
- Historical references such as `제2차 세계대전 (1939-1945)`
- Phone numbers or product codes such as `제품번호 20240315001`
- Other people's birth dates
- Dates in cited papers, article headlines, or copied reference material

All of these are not the entry's own date. **Only scan title, filename, frontmatter, and source path for dates.**

#### Track date source in extra field

Record the resolution method in `extra.date_source`:

```yaml
---
id: abc123
date: 2024-03-15
time: "10:30:00"
extra:
  date_source: fm.created  # or filename | source_path | source_year | mtime
---
```

This enables downstream tools to weight chronological order correctly. `fm.created` is reliable. `mtime` is usually not.

#### Warning threshold

If more than 20% of entries fall to `mtime`, warn the user:

```
WARNING: 580 of 1826 entries (31.8%) have mtime-only dates.
These are probably all clustered on the git checkout date.
Consider re-ingesting after adding frontmatter `created:` fields
to the raw source files.
```

### Unknown Formats

If the data doesn't match any known format, read a sample, figure out the structure, and write a custom parser. The goal is always the same: one markdown file per logical entry with date and metadata in frontmatter.

---
