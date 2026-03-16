# [GJ] Patent result deduplicator - cross-search deduplication with statistics
# Applies dedup + optional IPC filter + optional domain exclusion BEFORE classification
# Domain-agnostic: IPC prefix and exclusion keywords are user-configurable

import logging
import os
import glob as glob_module

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools._formatters import generate_output_path, save_dataframe

logger = logging.getLogger("mcp-kipris")


class ResultDeduplicatorArgs(BaseModel):
    input_directory: str = Field(
        ...,
        description="Directory containing Excel/Markdown patent result files to deduplicate",
    )
    dedup_column: str = Field(
        "applicationNumber",
        description="Column name for deduplication (applicationNumber or ApplicationNumber)",
    )
    apply_ipc_filter: bool = Field(
        False,
        description="Apply IPC relevance filter (default: false, requires ipc_prefix)",
    )
    ipc_prefix: str = Field(
        "",
        description="IPC code prefix for filtering (e.g., 'G06N 3/' or 'H01M 10/'). Only used when apply_ipc_filter=true.",
    )
    apply_domain_filter: bool = Field(
        False,
        description="Apply domain exclusion filter (default: false, requires exclusion_keywords)",
    )
    exclusion_keywords: str = Field(
        "",
        description="Comma-separated exclusion keywords for domain filtering (e.g., 'medical,blockchain,advertisement')",
    )
    title_column: str = Field(
        "inventionTitle",
        description="Column name for patent title (for domain filtering)",
    )
    ipc_column: str = Field(
        "ipcNumber",
        description="Column name for IPC code",
    )
    output_format: str = Field(
        "excel",
        description="Output format for deduplicated results (excel or markdown)",
    )
    output_prefix: str = Field(
        "deduplicated",
        description="Prefix for output filename",
    )


@register_tool
class ResultDeduplicatorTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_result_deduplicator")
        self.description = "Cross-search deduplication tool. Merges multiple patent result files, removes duplicates, and optionally applies IPC and domain filters. Works for any patent domain."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "input_directory": {
                        "type": "string",
                        "description": "Directory containing patent result files",
                    },
                    "dedup_column": {
                        "type": "string",
                        "description": "Column for deduplication (default: applicationNumber)",
                        "default": "applicationNumber",
                    },
                    "apply_ipc_filter": {
                        "type": "boolean",
                        "description": "Apply IPC filter (default: false)",
                        "default": False,
                    },
                    "ipc_prefix": {
                        "type": "string",
                        "description": "IPC prefix for filtering (e.g., 'G06N 3/'). Required if apply_ipc_filter=true.",
                        "default": "",
                    },
                    "apply_domain_filter": {
                        "type": "boolean",
                        "description": "Apply domain exclusion filter (default: false)",
                        "default": False,
                    },
                    "exclusion_keywords": {
                        "type": "string",
                        "description": "Comma-separated exclusion keywords for domain filtering",
                        "default": "",
                    },
                    "title_column": {
                        "type": "string",
                        "description": "Patent title column name (default: inventionTitle)",
                        "default": "inventionTitle",
                    },
                    "ipc_column": {
                        "type": "string",
                        "description": "IPC code column name (default: ipcNumber)",
                        "default": "ipcNumber",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (excel, markdown)",
                        "enum": ["excel", "markdown"],
                        "default": "excel",
                    },
                    "output_prefix": {
                        "type": "string",
                        "description": "Output filename prefix (default: deduplicated)",
                        "default": "deduplicated",
                    },
                },
                "required": ["input_directory"],
            },
        )

    async def _execute_async(self, validated_args: ResultDeduplicatorArgs) -> str:
        input_dir = validated_args.input_directory
        dedup_col = validated_args.dedup_column

        if not os.path.isdir(input_dir):
            return f"Error: Directory not found: {input_dir}"

        # Step 1: Load all files
        excel_files = glob_module.glob(os.path.join(input_dir, "*.xlsx"))
        md_files = glob_module.glob(os.path.join(input_dir, "*.md"))

        all_files = excel_files + md_files
        if not all_files:
            return f"No Excel or Markdown files found in {input_dir}"

        file_stats = []
        all_dfs = []

        for filepath in all_files:
            try:
                filename = os.path.basename(filepath)
                if filepath.endswith(".xlsx"):
                    df = pd.read_excel(filepath)
                else:
                    # Try reading markdown table
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    # Markdown 테이블 행만 추출 (| 시작, --- 구분선 제외)
                    table_lines = [
                        l.strip()
                        for l in lines
                        if l.strip().startswith("|") and not set(l.strip().strip("|").strip()).issubset({"-", " ", "|"})
                    ]
                    if len(table_lines) >= 2:
                        headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
                        rows = [[c.strip() for c in row.split("|")[1:-1]] for row in table_lines[1:]]
                        df = pd.DataFrame(rows, columns=headers)
                    else:
                        df = pd.DataFrame()

                df["_source_file"] = filename
                file_stats.append({"file": filename, "count": len(df)})
                all_dfs.append(df)
                logger.info(f"[dedup] Loaded {filename}: {len(df)} records")
            except Exception as e:
                logger.warning(f"[dedup] Failed to load {filepath}: {e}")
                file_stats.append({"file": os.path.basename(filepath), "count": 0, "error": str(e)})

        if not all_dfs:
            return "No valid data found in any files."

        # Step 2: Merge all DataFrames
        merged_df = pd.concat(all_dfs, ignore_index=True)
        total_raw = len(merged_df)

        # Step 3: Try common column name variations for dedup
        actual_dedup_col = None
        for col_name in [dedup_col, "ApplicationNumber", "applicationNumber", "applicationNo", "출원번호"]:
            if col_name in merged_df.columns:
                actual_dedup_col = col_name
                break

        # Step 4: Deduplicate
        if actual_dedup_col:
            before_dedup = len(merged_df)
            merged_df = merged_df.drop_duplicates(subset=[actual_dedup_col], keep="first")
            after_dedup = len(merged_df)
            duplicates_removed = before_dedup - after_dedup
            overlap_rate = (duplicates_removed / before_dedup * 100) if before_dedup > 0 else 0
        else:
            duplicates_removed = 0
            overlap_rate = 0
            after_dedup = total_raw

        # Step 5: IPC post-filter (configurable prefix)
        ipc_filtered = 0
        ipc_prefix = validated_args.ipc_prefix.strip()

        if validated_args.apply_ipc_filter and ipc_prefix:
            ipc_col = None
            for col_name in [validated_args.ipc_column, "ipcNumber", "ipc", "IPC", "IPCNumber"]:
                if col_name in merged_df.columns:
                    ipc_col = col_name
                    break

            if ipc_col:
                before_ipc = len(merged_df)
                # Normalize: match with and without spaces
                prefix_nospace = ipc_prefix.replace(" ", "")
                merged_df = merged_df[
                    merged_df[ipc_col].fillna("").str.replace(" ", "").str.contains(prefix_nospace, regex=False)
                    | merged_df[ipc_col].fillna("").str.contains(ipc_prefix, regex=False)
                ]
                ipc_filtered = before_ipc - len(merged_df)

        # Step 6: Domain exclusion filter (configurable keywords)
        domain_excluded = {}
        exclusion_terms = [t.strip() for t in validated_args.exclusion_keywords.split(",") if t.strip()]

        if validated_args.apply_domain_filter and exclusion_terms:
            title_col = None
            for col_name in [validated_args.title_column, "inventionTitle", "InventionName", "inventionName", "title"]:
                if col_name in merged_df.columns:
                    title_col = col_name
                    break

            if title_col:
                exclusion_mask = pd.Series([False] * len(merged_df), index=merged_df.index)
                for idx, row in merged_df.iterrows():
                    title = str(row.get(title_col, "")).upper()
                    for term in exclusion_terms:
                        if term.upper() in title:
                            exclusion_mask.at[idx] = True
                            domain_excluded[term] = domain_excluded.get(term, 0) + 1
                            break

                merged_df = merged_df[~exclusion_mask]

        # Step 7: Save output
        # Remove helper column
        if "_source_file" in merged_df.columns:
            output_df = merged_df.drop(columns=["_source_file"])
        else:
            output_df = merged_df

        filepath = generate_output_path(
            word="merged",
            output_format=validated_args.output_format,
            prefix=validated_args.output_prefix,
        )
        save_dataframe(output_df, filepath, validated_args.output_format)

        # Step 8: Build report
        final_count = len(output_df)
        total_domain_excluded = sum(domain_excluded.values())

        lines = []
        lines.append("# Deduplication Report")
        lines.append(f"\n## Input")
        lines.append(f"- Files processed: {len(all_dfs)}")
        lines.append(f"- Total raw records: {total_raw:,}")

        lines.append(f"\n## File Breakdown")
        lines.append("| File | Records |")
        lines.append("|------|---------|")
        for fs in file_stats:
            error = f" (ERROR: {fs.get('error', '')})" if fs.get("error") else ""
            lines.append(f"| {fs['file']} | {fs['count']:,}{error} |")

        lines.append(f"\n## Processing Pipeline")
        lines.append("| Stage | Input | Removed | Output |")
        lines.append("|-------|-------|---------|--------|")

        stage_input = total_raw
        lines.append(
            f"| Deduplication | {stage_input:,} | {duplicates_removed:,} ({overlap_rate:.1f}%) | {after_dedup:,} |"
        )

        stage_input = after_dedup
        if validated_args.apply_ipc_filter and ipc_prefix:
            lines.append(
                f"| IPC Filter ({ipc_prefix}) | {stage_input:,} | {ipc_filtered:,} | {stage_input - ipc_filtered:,} |"
            )
            stage_input -= ipc_filtered

        if validated_args.apply_domain_filter and total_domain_excluded > 0:
            lines.append(f"| Domain Exclusion | {stage_input:,} | {total_domain_excluded:,} | {final_count:,} |")

        lines.append(f"\n## Results")
        lines.append(f"- **Final unique records: {final_count:,}**")
        lines.append(f"- Overlap rate: {overlap_rate:.1f}%")
        lines.append(f"- Saved to: {filepath}")

        if domain_excluded:
            lines.append(f"\n## Domain Exclusions")
            for term, count in sorted(domain_excluded.items(), key=lambda x: -x[1]):
                lines.append(f"- {term}: {count:,} patents removed")

        return "\n".join(lines)
