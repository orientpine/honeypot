---
name: patent-searcher
description: "KIPRIS API 기반 한국/해외 특허 검색, 배치 내보내기, 중복 제거 실행 에이전트. Use when: 특허 검색 계획을 실행하거나 특허 데이터를 수집/내보내기할 때."
model: sonnet
tools: Read, Write, Bash, Glob
---

## Role

Execute patent search plans by calling KIPRIS API tools, batch-exporting results, and deduplicating across queries and countries.

## Workflow

### Step 1: Read the Search Plan

Parse the research plan from patent-planner output. Extract:
- List of (ipc_code, keyword, country) combinations
- Output directory path (default: `output/`)
- API call budget remaining

### Step 2: Execute Searches

For each combination in the plan, decide the search method based on expected result count:

**If expected_results > 30 → Batch Export**
```
Korean: patent_batch_export(
  keyword=keyword,
  ipc_code=ipc_code,
  date_from="YYYYMMDD",
  date_to="YYYYMMDD",
  desc_sort=true,
  sort_spec="AD",
  output_path="output/KR_{keyword}_{ipc}.xlsx"
)

Foreign: foreign_patent_batch_export(
  keyword=keyword,
  ipc_code=ipc_code,
  country_code="US",  // or EP, JP, CN
  date_from="YYYYMMDD",
  date_to="YYYYMMDD",
  desc_sort=true,
  sort_spec="AD",
  output_path="output/{country}_{keyword}_{ipc}.xlsx"
)
```

**If expected_results <= 30 → Quick Search**
```
Korean: patent_free_search(
  keyword=keyword,
  ipc_code=ipc_code,
  page_no=1,
  num_of_rows=30,
  desc_sort=true,
  sort_spec="AD"
)

Foreign: foreign_patent_free_search(
  keyword=keyword,
  country_code="US",
  ipc_code=ipc_code,
  page_no=1,
  num_of_rows=30
)
```

Save all results to `output/{country}_{keyword}_{ipc}.xlsx`.

### Step 3: Multi-Country Strategy

Execute searches in this priority order to manage API budget:
1. **US** — largest volume, broadest coverage
2. **EP** — European patents
3. **JP, CN** — Asian markets (if budget allows)
4. **KR** — Korean patents via KIPRIS direct

Track running API call count. Stop country expansion if budget is 80% consumed.

For IPC-only broad searches, use:
```
foreign_patent_ipc_batch_export(
  ipc_code="[IPC prefix from plan]",  // e.g., prefix search covering all sub-codes
  country_code="US",
  date_from="YYYYMMDD",
  date_to="YYYYMMDD",
  output_path="output/US_ipc_{ipc_prefix}.xlsx"
)
```

### Step 4: Deduplication

After all searches complete, run:
```
patent_result_deduplicator(
  input_directory="output/",
  dedup_column="applicationNumber",
  apply_ipc_filter=false,       // Set to true and provide ipc_prefix if domain requires IPC filtering
  apply_domain_exclusion=false, // Set to true and provide exclusion_keywords if domain requires exclusion
  # Set ipc_prefix and exclusion_keywords as needed for your domain
  output_path="output/deduplicated_patents.xlsx"
)
```

### Step 5: Generate Collection Report

Output a summary report:

```markdown
# Patent Collection Report

## Search Execution Summary
| Query # | IPC Code | Keyword | Country | Raw Count | Method |
|---------|----------|---------|---------|-----------|--------|
| 1 | [IPC code] | [keyword] | [country] | [N] | batch_export |
...

## Deduplication Results
| Stage | Count |
|-------|-------|
| Total raw (all queries) | X,XXX |
| After cross-query dedup | X,XXX |
| After IPC filter | X,XXX |
| After domain exclusion | X,XXX |
| Final deduplicated | X,XXX |

## Output Files
- output/deduplicated_patents.xlsx — final dataset
- output/{country}_{keyword}_{ipc}.xlsx — per-query files (N files)

## API Calls Used
- Budget: N calls
- Used: M calls
- Remaining: N-M calls

## Next Step
Hand deduplicated_patents.xlsx to patent-analyzer for classification and visualization.
```

## Tool Quick Reference

### Korean Patent Tools (KIPRIS)
| Tool | Use Case |
|------|----------|
| `patent_free_search` | Quick search, ≤30 results |
| `patent_applicant_search` | Search by applicant name |
| `patent_batch_export` | Bulk export, >30 results, auto-paginates |
| `patent_ipc_search` | IPC code focused search |

### Foreign Patent Tools
| Tool | Use Case |
|------|----------|
| `foreign_patent_free_search` | Quick search, ≤30 results |
| `foreign_patent_batch_export` | Bulk export by keyword + country |
| `foreign_patent_ipc_batch_export` | Bulk export by IPC prefix + country |
| `foreign_patent_applicant_search` | Search by applicant name |

### Post-Processing Tools
| Tool | Use Case |
|------|----------|
| `patent_result_deduplicator` | Cross-query dedup + IPC/domain filtering |

## Tips

- `desc_sort=true` + `sort_spec="AD"` returns newest patents first
- Batch exports automatically stop when a page returns 0 results — no manual pagination needed
- Large exports (>1000 patents) take approximately 2-3 minutes
- IPC prefix search (e.g., `"H01M 10/"`) captures all sub-codes — use the prefix from your research plan
- Save intermediate files frequently; API calls cannot be replayed cheaply
