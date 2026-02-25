# Patent Trend Analysis Pipeline

Full end-to-end pipeline for patent research: planning, search, and analysis. Orchestrates three specialized agents in sequence.

## Usage

Provide a research topic when invoking this command. Example:

```
/analyze-patents On-sensor AI inference chips, focusing on neuromorphic and edge computing patents from 2019-2024
```

---

## Phase 1 — Research Planning

Invoke the patent-planner agent to cluster the research area, optimize keywords, map IPC codes, and produce a search strategy.

```
Task(
  subagent_type="patent-trend-analyzer::patent-planner",
  prompt="[Research topic from user]. Analyze the technology area, optimize keywords, map IPC codes, and create a search strategy plan."
)
```

Wait for the plan output before proceeding.

Present the plan to the user:
- Optimized keyword list (with Korean equivalents)
- IPC code mapping table
- Search strategy table (IPC × keyword × country)
- API call budget breakdown

Ask the user to confirm or adjust the plan before moving to Phase 2.

---

## Phase 2 — Search & Collection

Invoke the patent-searcher agent to execute the confirmed search plan, batch-export results, and deduplicate.

```
Task(
  subagent_type="patent-trend-analyzer::patent-searcher",
  prompt="Execute the search plan: [plan details from Phase 1]. Search for patents across all target countries, batch export results to output/, deduplicate across queries and countries using patent_result_deduplicator."
)
```

Wait for the collection report before proceeding.

Report collection statistics to the user:
- Number of queries executed
- Raw patent count per country
- Deduplicated total
- API calls consumed vs. budget

---

## Phase 3 — Analysis & Visualization

Invoke the patent-analyzer agent to classify patents, run trend analysis, generate all visualizations, and export the final report.

```
Task(
  subagent_type="patent-trend-analyzer::patent-analyzer",
  prompt="Analyze the collected patent data at output/deduplicated_patents.xlsx. Classify using the 3-axis taxonomy (Layer: OnSensor/OnDevice, Function: Adaptive Learning/Inference/Lightweight/Training). Generate all 8 static charts, the combined dashboard PNG, the interactive HTML dashboard, the multi-sheet Excel report, and the Markdown summary."
)
```

Wait for analysis to complete, then present the final results to the user.

---

## Pipeline Summary

| Stage | Count |
|-------|-------|
| Search queries | N |
| Raw patents | X,XXX |
| After dedup | X,XXX |
| After filtering | X,XXX |
| Visualizations | 9 files |

Output files are located in `output/`:
- `patent_analysis_report.xlsx` — multi-sheet Excel report
- `patent_classification_summary.md` — executive summary
- `visualizations/combined_dashboard.png` — static overview
- `visualizations/patent_dashboard.html` — interactive dashboard

---

## Notes

- Each phase can be run independently if you already have intermediate outputs.
- Run `/patent-research-planning` for Phase 1 only (keyword optimization and IPC mapping).
- Run `/patent-search-collect` for Phase 2 only (search execution and deduplication).
- Run `/patent-analysis-viz` for Phase 3 only (classification, charts, and reports).
- If a phase fails mid-run, re-invoke the same phase — batch exports are resumable.
