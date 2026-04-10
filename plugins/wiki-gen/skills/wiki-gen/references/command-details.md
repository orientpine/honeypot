# Command Details

### Agent prompt template

Use `assets/absorb_agent.md` as the base for each parallel absorption agent's prompt. Fill in:

- `{BATCH_ID}` for the batch identifier from the partition manifest
- `{TARGET_DIR}` for the `wiki/<dir>/` this agent owns
- `{ENTRY_COUNT}` for the number of entries assigned
- `{BATCH_MANIFEST_PATH}` for the absolute path to the batch JSON manifest

Do not write prompts from scratch. Prompts differ only about 10-20% from batch to batch. The templated 80% should stay identical so outputs stay consistent.

### The Absorption Loop

For vaults under 500 entries, process chronologically as described below. For larger vaults, see `## Scale Mode` above.

Process entries one at a time, chronologically. Read `_index.md` before each entry to match against existing articles. Re-read every article before updating it. This is non-negotiable.

For each entry:

1. **Read the entry.** Text, frontmatter, metadata. View any attached photos. Actually look at them and understand what they show.

2. **Understand what it means.** Do not catalogue facts. Extract meaning. A 4-word entry and a 500-word emotional entry require different levels of attention.

3. **Match against the index.** Identify which existing articles the entry touches. Note any material that does not match anything existing and may suggest a new article.

4. **Update and create articles.** Re-read every article before updating. Before editing, identify the new dimension this entry adds. Do not merely check whether the entry confirms or contradicts existing content; identify what you understand now that you did not understand before.

   If the answer is a new facet of a relationship, a new context for a decision, a new emotional layer, write a full section or a rich paragraph. Not a sentence. Every page you touch should get meaningfully better. Never just append to the bottom. Integrate so the article reads as a coherent whole.

5. **Connect to patterns.** When you see the same theme across multiple entries, such as loneliness, creative philosophy, recovery from burnout, or learning from masters, that pattern deserves its own article. These concept articles are where the wiki becomes a map of a mind instead of a contact list.

### Anti-Dump (CRITICAL)

When adding missing content to an article, never paste raw entry text verbatim. Always **synthesize** the content into prose that matches the article's existing voice, structure, and level of abstraction.

#### Anti-pattern (do NOT do this)

```markdown
## Remediation Entries

### Entry ID: abc123 - 2024-03-15 meeting notes
{500 lines of raw meeting notes verbatim}

### Entry ID: def456 - follow-up email
{400 lines of raw email verbatim}
```

This is filing, not writing. The agent that does this is behaving like a filing clerk, not a writer.

#### Correct pattern

```markdown
## Decision Cycle

The March 2024 meeting produced three concrete choices, A, B, and C, based on the constraints outlined in the follow-up email. Choice B was selected primarily for its alignment with the fiscal 2025 budget.

## References

- Entry ID: abc123 - 2024-03-15 meeting, raw discussion of A/B/C
- Entry ID: def456 - follow-up email, fiscal constraint
```

This is writing. The raw material was read, understood, synthesized, and compressed to a few sentences that capture the meaning.

#### Hard limits

1. **Never paste more than 3 consecutive lines of raw entry text** into any article. Quote individual sentences inside narrative prose. Maximum 2 direct quotes per article.

2. **Never let any article exceed 150 content lines** excluding frontmatter. If it does, split by theme.

3. **If your edit is mostly copy-paste, stop.** You are filing, not writing. Discard the edit and re-approach by reading entries, understanding them, and writing new prose.

4. **Always compress**: the ratio of raw entry text read to wiki prose written should be at least 5:1. Reading 5000 words and writing 1000 means you are compressing well. Reading 5000 and writing 4500 means you are copy-pasting.

### What Becomes an Article

**Named things get pages** if there's enough material. A person mentioned once in passing doesn't need a stub. A person who appears across multiple entries with a distinct role does. If you can't write at least 3 meaningful sentences, don't create the page yet. Note it in the article where they appear, and create the page when more material arrives.

**Patterns and themes get pages.** When you notice the same idea surfacing across entries, such as a creative philosophy, a recurring emotional arc, a search pattern, or a learning style, that's a concept article. These are often the most valuable articles in the wiki.

### Anti-Cramming

The gravitational pull of existing articles is the enemy. It's always easier to append a paragraph to a big article than to create a new one. This produces 5 bloated articles instead of 30 focused ones.

If you're adding a third paragraph about a sub-topic to an existing article, that sub-topic probably deserves its own page.

### Anti-Thinning

Creating a page is not the win. Enriching it is. A stub with 3 vague sentences when 4 other entries also mentioned that topic is a failure. Every time you touch a page, it should get richer.

### Checkpoint cadence

Use the cadence that matches your scale mode:

| Mode | Checkpoint cadence |
|---|---|
| Single-pass (<=100) | Every 15 entries |
| Sectioned (100-500) | Every 30-50 entries or every source section |
| Partitioned parallel (500+) | Every batch completion, orchestrator checkpoint |

At each checkpoint:

1. Rebuild `_index.md` with all articles and `also:` aliases.
2. Rebuild `_backlinks.json` with a Python script scanning `[[wikilinks]]`.
3. **New article audit:** how many new articles appeared since the last checkpoint? If zero, you are cramming.
4. **Quality audit:** pick your 3 most-updated articles. Re-read each as a whole piece. Ask:
   - Does it tell a coherent story, or is it a chronological dump?
   - Does it have sections organized by theme, not date?
   - Does it use direct quotes to carry emotional weight?
   - Does it connect to other articles in revealing ways?
   - Would a reader learn something non-obvious?
   If any article reads like an event log, rewrite it.
5. Check whether any articles exceed 150 lines and should be split.
6. Check directory structure. Create new directories when needed.

---

### How to Answer

1. **Read `_index.md`.** Scan for articles relevant to the query. Each entry has an `also:` field with aliases.
2. **Check `_backlinks.json`.** Find articles that reference the topic. High backlink counts indicate central topics.
3. **Read 3-8 relevant articles.** Follow `[[wikilinks]]` and `related:` entries 2-3 links deep when relevant.
4. **Synthesize.** Lead with the answer, cite articles by name, use direct quotes sparingly, connect dots across articles, and acknowledge gaps.

### Query Patterns

| Query type | Where to look |
|-----------|--------------|
| "Tell me about [person]" | Articles with `type: person`, plus backlinks |
| "What happened with [project]?" | Articles with `type: project`, related `type: era`, and decisions |
| "Why did they [decision]?" | Articles with `type: decision`, `type: transition`, and related projects |
| "What's the pattern with [theme]?" | Articles with `type: pattern`, `type: philosophy`, `type: tension`, and related bridge articles |
| "What was [time period] like?" | Articles with `type: era`, plus connected projects, people, and places |
| Broad or exploratory questions | Cast wide, read highest-backlink articles, then synthesize themes |

### Rules

- Never read raw diary entries in `raw/entries/`. The wiki is the knowledge base.
- Don't guess. If the wiki doesn't cover it, say so.
- Don't read the entire wiki. Be surgical.
## Command: `wiki remediate`

Scan for raw entries that are not yet cited in any wiki article, and launch targeted remediation agents to close the coverage gap.

**Run this after `wiki absorb` and before `wiki cleanup`.**

### Citation vs Content Coverage

Treat these as two different metrics:

- **Citation coverage**: whether an entry ID is explicitly cited in any article via frontmatter `sources:` or body `Entry ID:` references.
- **Content coverage**: whether the entry's salient terms, title, topic, or path segments appear in article prose strongly enough to suggest that its substance was actually absorbed.

Use them differently:

- Citation coverage is the completion gate. Target is **100%**.
- Content coverage is a quality signal. It checks whether the article meaningfully reflects the entry rather than just naming the ID.
- If content coverage is higher than citation coverage, the writer probably used the material but forgot to cite it.
- If citation coverage is higher than content coverage, the writer probably cited an entry without integrating it well.

### Process

#### 1. Coverage check

```bash
python scripts/check_coverage.py
```

This scans every wiki article for:

- Frontmatter `sources:` field entries
- Body text `Entry ID: {12-hex}` patterns
- Body text bare 12-hex strings that match known entry IDs

And produces:

- `wiki/_absorb_log.json` with `entry_id -> [articles citing it]`
- `wiki/_uncovered.md` with entries not cited anywhere, grouped by source partition

#### 2. Classify gaps

For each batch with less than 100% coverage, extract the uncovered entry IDs:

```bash
python scripts/diag_uncovered.py  # writes raw/uncovered_by_batch.json
```

Classify each gap before assignment:

- Missing citation in an otherwise correct article
- Missing synthesized content in an existing article
- Missing supplementary article, only as a last resort
- Intentionally uncited material, which should be quarantined into `_intentionally_uncited.md` and never deleted from `raw/entries/`

#### 3. Launch remediation agents

For each under-covered batch, launch one remediation agent. Use `assets/remediation_agent.md`. Each agent:

- Reads its batch's uncovered ID list
- Reads all existing articles in its target directory
- For each uncovered entry, globs `raw/entries/*{id}*.md`, reads it, and matches it to the most relevant existing article
- Adds citation in body text using `Entry ID: {id} - brief description`
- If content is genuinely missing, adds a synthesized paragraph
- Never dumps raw text, per the Anti-Dump rule
- Creates a supplementary article only as last resort, and keep it under 50 lines
- Reports `_remediation_report.md`

#### 4. Verify

Re-run `check_coverage.py`. Target is 100% citation coverage. If any entries remain uncovered, either:

- They are too trivial to cite, in which case quarantine them in `_intentionally_uncited.md`. Never delete raw entries, because the core principle is that every entry must be absorbed somewhere, even if that place is a documented exclusion list.
- Or the remediation agent failed, in which case perform manual intervention

### When to run

- Always after initial `wiki absorb`, especially for vaults with 500 or more entries
- After manual cleanup that may have moved or deleted citations
- Before declaring a wiki complete
- Periodically on large wikis that continue to receive new entries

### Why this is a separate command from cleanup

Coverage remediation is narrow. It fills citation gaps without rewriting the wiki globally. Cleanup is broad. It restructures, merges, splits, and rewrites. They have different risk profiles and should not run simultaneously.

---

## Command: `wiki cleanup`

Audit and enrich every article in the wiki using parallel subagents.

### Agent prompt template

Use `assets/cleanup_agent.md` as the base for each cleanup agent's prompt. Fill in batch-specific paths, ownership boundaries, and expected deliverables. Do not write cleanup prompts from scratch. Keep the core structure identical so cleanup decisions stay comparable across directories.

### Phase 1: Build Context

Read `_index.md` and every article. Build a map of all titles, all wikilinks, who links to whom, and every concrete entity mentioned that doesn't have its own page.

### Phase 2: Per-Article Subagents

Spawn parallel subagents in batches of 5. Each agent reads one article and:

**Assesses:**

- Structure: theme-driven or diary-driven, with individual events as section headings
- Line count: bloated, more than 150 lines, or stub, fewer than 15 lines. The 150-line cap is the unified threshold across absorb, cleanup, and breakdown; do not use a different number in any phase.
- Tone: flat, factual, encyclopedic, or AI editorial voice
- Quote density: more than 2 direct quotes, or more than one third direct quote content
- Narrative coherence: unified story or list of random events
- Wikilinks: broken links, missing links to existing articles, weak connective tissue
- Citations: frontmatter `sources:` present, body `## References` present, references contextualized

#### Orphan policy

An orphan is an article with zero inbound wikilinks and zero outbound wikilinks.

- **Orphans are allowed** if the article is genuinely standalone, such as a one-off event or a concept with no natural connections.
- Cleanup agents should still attempt to add 1-3 wikilinks per orphan to connect it to related articles. Use `_index.md` as the source of known targets.
- Do not over-link. Maximum 8 wikilinks per article body.
- If more than 50% of articles are orphans, the wiki has a connectivity problem. Re-run breakdown to create more bridge articles.

**Restructures if needed.** The most common problem is diary-driven structure.

Bad, diary-driven:

```
## The March Meeting
## The April Pivot
## The June Launch
```

Good, narrative:

```
## Origins
## The Pivot to Institutional Sales
## Becoming the Product
```

The Steve Jobs test: Wikipedia's Steve Jobs article uses "Early life" and "Career", with subsections by era. Not "The Xerox PARC Visit" or "The Lisa Project Failure."

**Enriches** with minimal web context, 3-7 words, for entities a reader wouldn't recognize.

**Identifies missing article candidates** using the concrete noun test.

### Phase 3: Integration

After all agents finish, deduplicate candidates, create new articles, fix broken wikilinks, rebuild `_index.md`, and rebuild `_backlinks.json`.

---

## Command: `wiki breakdown`

Find and create missing articles. Expands the wiki by identifying concrete entities and themes that deserve their own pages.

### Agent prompt template

Use `assets/breakdown_agent.md` as the base for each breakdown agent's prompt. Fill in the owned directory set, candidate source files, and creation limits. Keep prompt structure stable so candidate quality remains comparable across runs.

### Phase 1: Survey

Read `_index.md` and `_backlinks.json`. Identify bare directories, bloated articles of more than 150 lines, the unified threshold across all phases, high-reference backlink targets without articles, and misclassified articles.

### Phase 2: Mining

Spawn parallel subagents. Each reads a batch of about 10 articles and extracts:

**Concrete entities**, using the concrete noun test, "X is a ___":

- Named people, places, companies, organizations, institutions
- Named events or turning points with dates
- Books, films, music, and games referenced
- Tools and platforms used significantly
- Projects with names
- Restaurants or venues tied to narrative moments

**Do NOT extract:** generic technologies such as React, Python, or Docker unless there is a documented learning arc, entities already covered, or passing mentions.

### Phase 3: Planning

Deduplicate, count references, rank by reference count, classify into directories, and present a candidate table:

| # | Article | Dir | Refs | Description |
|---|---------|-----|------|-------------|

### Phase 4: Creation

Create in parallel batches of 5 agents. Each agent greps existing articles for mentions, collects material, writes the article, and adds wikilinks from existing articles back to the new one.

### Reclassification (with `--reorganize`)

Move misclassified articles to correct directories. Common moves:

- `life/` to `philosophies/` for articles stating beliefs
- `life/` to `patterns/` for articles with trigger-response structure
- `events/` to `transitions/` for multi-week uncertain periods
- `events/` to `decisions/` for articles with enumerated reasons

---

## Command: `wiki rebuild-index`

Rebuild `_index.md` and `_backlinks.json` from current wiki state.

### Exclusions

The index excludes the following files. They are not articles:

- Files starting with `_`, such as `_index.md`, `_backlinks.json`, `_absorb_log.json`, `_FINAL_REPORT.md`, `_batch_summary.md`, and related meta files
- `README.md` at the wiki root, which is a project overview, not an article
- `.wikiignore` entries, optional, one glob per line

### Format

Each index entry must use the `[[filename_stem|Display Title]]` syntax, with aliases shown after a `|also:` separator:

```markdown
- [[cha_baek_dong|차백동 (Cha Baek-dong)]] (person) | also: 차백동, Cha Baek-dong
```

Reference implementation:

```python
# BAD
index_lines.append(f"- [[{article['title']}]]")

# GOOD
stem = article["filename_stem"]
title = article["title"]
if stem == title:
    link = f"[[{stem}]]"
else:
    link = f"[[{stem}|{title}]]"
index_lines.append(f"- {link}")
```

### Verify after rebuild

Run `scripts/diag_wikilink_resolution.py` to verify that all index wikilinks resolve to existing filenames or known aliases. Any title-only matches indicate the generator has a bug. Fix the generator, not the articles.

---

## Command: `wiki reorganize`

Step back and rethink wiki structure. Read the index, sample articles, and ask: merge, split, new categories, orphan articles, missing patterns. Execute changes, then rebuild index.

## Command: `wiki status`

Use this exact output structure when reporting current wiki state:

```markdown
# Wiki Status

Generated: {ISO timestamp}
Source: {source path}

## Ingestion
- Scanned: N files
- Skipped: M, with breakdown
- Ingested: K entries

## Articles
- Total: N
- By directory: table
- By type: table

## Coverage
- Citation: 100.0% (N/N)
- Content: 100.0% (N/N)

## Quality
- Stubs: N
- Bloated: N
- Exact dups: N
- Fuzzy dups: N
- Orphans: N
- Wikilinks: N

## See also
- _index.md
- _backlinks.json
- _absorb_log.json
- _FINAL_REPORT.md
```

