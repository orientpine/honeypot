# Scale Mode

## Scale Mode

Before running `wiki absorb`, pick your mode based on raw entry count:

| Entries | Mode | Strategy |
|---|---|---|
| <= 100 | **Single-pass** | One agent, chronological, checkpoint every 15 entries |
| 100-500 | **Sectioned** | One agent, process by source section, not strict chronology, checkpoint every 30 |
| 500-2000 | **Partitioned parallel** | Orchestrator plus N parallel batch agents, one per source partition |
| 2000+ | **Partitioned parallel + multi-round** | Add remediation round plus cleanup round |

### Partitioned Parallel Mode (500+ entries)

For any vault larger than about 500 entries, do not attempt sequential processing. Instead:

#### 1. Partition

Divide raw entries into batches of 50-150 entries each, grouped by source topic or directory. Target about 20-30 batches total.

Write `raw/batches/{batch_id}.json` manifests with:

```json
{
  "batch_id": "P01_personal_robotics",
  "label": "Robotics and Isaac Sim work",
  "description": "...",
  "wiki_target_dir": "personal_robotics",
  "entry_count": 51,
  "entry_files": ["2024-01-01_...abc.md", "..."],
  "entries_meta": [
    {"id": "abc123", "title": "...", "date": "..."}
  ]
}
```

#### 2. Launch parallel absorption agents

Launch one agent per batch. Each agent:

- **Owns exactly one target directory** under `wiki/`
- Reads its batch manifest
- Reads all assigned raw entries
- Writes articles only to its owned directory
- Reports `_batch_summary.md` when done
- Never reads or writes other batches' directories, except `_index.md` read-only

See `assets/absorb_agent.md` for the prompt template.

Concurrency of 5-10 agents in parallel is usually safe. Fifteen or more may overwhelm the system. Launch in waves if needed.

#### 3. Coverage check

After all batches finish:

```bash
python scripts/check_coverage.py
```

This produces `wiki/_uncovered.md` listing any raw entries not cited by any article, grouped by source partition.

#### 4. Remediate

For any batch with less than 100% coverage, run `wiki remediate`. This launches targeted per-batch remediation agents that fill in missing citations without duplicating work.

#### 5. Cleanup + Breakdown

After coverage is 100%, run the normal cleanup and breakdown phases. They now operate on a unified wiki with full citation traceability.

### Partition Rules (Parallel Agent Safety)

When running parallel agents:

1. **Unique directory ownership**: each agent owns exactly one `wiki/<dir>/` and writes only there. No agent writes to another agent's directory.

2. **Cross-directory references are read-only**: an agent can read `_index.md` to find titles in other directories but must not edit those directories.

3. **Canonical entity safety**: if a canonical entity (person, major project, named place) appears in multiple batches, agents should prefer linking to the canonical article if one exists, or record a merge candidate for cleanup. Only create batch-local articles for entities that are genuinely local to the batch. Do not blindly duplicate canonical people or projects across partitions, because consolidation after the fact is far more expensive than linking during absorption.

4. **Batch manifests, not raw globs**: agents read from `raw/batches/{batch_id}.json`, not by globbing `raw/entries/`. This prevents cross-batch contamination.

5. **Per-batch deliverables**: each agent writes `wiki/<dir>/_batch_summary.md`. The orchestrator reads these to verify completion.

### Batch manifest format

At minimum, every manifest should include:

- `batch_id`
- `label`
- `description`
- `wiki_target_dir`
- `entry_count`
- `entry_files`
- `entries_meta`

Keep manifest fields stable across runs. This lets downstream helpers compare batches, diff changes, and run deterministic remediation.

