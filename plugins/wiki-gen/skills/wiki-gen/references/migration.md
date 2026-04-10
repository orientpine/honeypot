# Migration from v1.0.0

## Migration from v1.0.0

Version 1.1.0 introduces stricter rules for filenames (C2), wikilink syntax (C1), citations (C3), and required frontmatter fields (N3). Existing wikis built with v1.0.0 remain functional but may need a lightweight migration to benefit from the new guarantees.

### Compatibility policy

- **v1.0.0 content is never auto-rewritten.** Migrations are opt-in and additive.
- **New rules are enforced only on new or edited articles.** Legacy articles that violate C2 (non-ASCII filenames) or N3 (missing `aliases`/`created`) are reported as lint warnings, not errors.
- **Existing wikilinks remain readable.** The C1 `[[filename_stem|Title]]` syntax is backward-compatible with the old `[[Title]]` form in Obsidian; legacy links resolve through the aliases populated by the migration script.

### Recommended migration steps

1. **Populate aliases for every existing article.** Run a one-time script that reads each article's `title:` and current filename stem, then writes an `aliases:` field containing both plus any obvious variants. This makes old title-based wikilinks continue to resolve after the C1 rule is adopted.
2. **Rename filenames gradually.** Do not bulk-rename. As agents edit articles in the course of normal `wiki cleanup` or `wiki remediate` passes, rename violating files to ASCII snake_case and record the original filename in `aliases:` so inbound links survive.
3. **Add missing frontmatter fields.** Use `scripts/consolidate_analyze.py` to list articles missing required fields. Fill in `created:` from git history and `last_updated:` from file mtime where no better signal exists. Mark any manual entries with `extra.date_source: manual`.
4. **Add `_intentionally_uncited.md`.** If your v1.0.0 wiki has uncovered entries that should stay uncovered, document them in this file rather than deleting them. The `wiki remediate` command respects this list and will not flag listed entries as gaps.
5. **Re-run `wiki rebuild-index`.** After aliases and filenames are updated, rebuild the index so every wikilink resolves through either the new C1 form or the populated aliases.

### When a full migration is not needed

For small wikis (under 200 articles) or wikis that are not actively edited, a full migration is usually unnecessary. The lint warnings will identify which articles need attention, and you can fix them one at a time as you touch them.

### When a full migration is required

For large wikis (1000+ articles) or wikis that receive frequent parallel edits, a full migration is recommended before adopting Scale Mode. Partitioned parallel agents depend on stable filenames, correct aliases, and complete frontmatter to avoid cross-batch collisions.

### Lint warnings versus errors

| Condition | v1.0.0 behavior | v1.1.0 behavior |
|---|---|---|
| Non-ASCII filename on a legacy article | silent | warning |
| Missing `aliases:` on a legacy article | silent | warning |
| Missing `created:` on a legacy article | silent | warning |
| Missing `sources:` on a legacy article | silent | warning |
| Any of the above on a **new** article | silent | **error**, reject the edit |

Agents should treat warnings as cleanup backlog, not as blockers, unless the user explicitly asks for a full migration pass.
