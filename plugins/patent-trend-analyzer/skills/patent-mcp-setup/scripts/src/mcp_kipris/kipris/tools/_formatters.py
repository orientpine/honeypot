"""[GJ] Response formatting utilities for patent search tools.

Centralizes the formatting logic that was duplicated across tool files.
"""

import datetime
import logging
import os

import pandas as pd

logger = logging.getLogger("mcp-kipris")


def format_korean_search_result(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    """Format Korean patent search results as markdown table.

    Args:
        df: Search result DataFrame.
        columns: Columns to include. Defaults to standard Korean patent columns.

    Returns:
        str: Markdown-formatted table string.
    """
    if columns is None:
        # [GJ] Try common Korean patent column names
        available = df.columns.tolist()
        # Old API uses PascalCase, new kipo-api uses camelCase
        if "ApplicationNumber" in available:
            columns = ["ApplicationNumber", "ApplicationDate", "InventionName", "Applicant"]
        elif "applicationNumber" in available:
            columns = ["applicationNumber", "applicationDate", "inventionTitle", "applicantName"]
        else:
            columns = available[:4]

    # [GJ] Only use columns that actually exist
    valid_columns = [c for c in columns if c in df.columns]
    if not valid_columns:
        return df.to_markdown(index=False)

    return df[valid_columns].to_markdown(index=False)


def format_foreign_search_result(df: pd.DataFrame) -> str:
    """Format Foreign patent search results as markdown table.

    Args:
        df: Search result DataFrame.

    Returns:
        str: Markdown-formatted table string.
    """
    return df.to_markdown(index=False)


def sanitize_filename(word: str) -> str:
    """Sanitize a search word for use in filenames.

    Args:
        word: Raw search keyword.

    Returns:
        str: Filesystem-safe filename component.
    """
    return "".join(
        c for c in word if c.isalnum() or c in (" ", "-", "_")
    ).strip().replace(" ", "_")


def generate_output_path(
    word: str,
    output_format: str = "excel",
    prefix: str = "patent_export",
    country: str | None = None,
    ipc_suffix: str = "",
) -> str:
    """Generate output file path for batch export.

    Args:
        word: Search keyword (used in filename).
        output_format: 'excel' or 'markdown'.
        prefix: Filename prefix.
        country: Country code for subdirectory (optional).
        ipc_suffix: IPC filter suffix for filename (optional).

    Returns:
        str: Full output file path.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_word = sanitize_filename(word)

    ext = ".xlsx" if output_format == "excel" else ".md"
    filename = f"{prefix}_{safe_word}{ipc_suffix}_{timestamp}{ext}"

    if country:
        output_dir = os.path.join(os.getcwd(), "mcp_kipris", "output", country)
    else:
        output_dir = os.path.join(os.getcwd(), "mcp_kipris", "output")

    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def save_dataframe(df: pd.DataFrame, filepath: str, output_format: str = "excel") -> None:
    """Save DataFrame to file.

    Args:
        df: DataFrame to save.
        filepath: Output file path.
        output_format: 'excel' or 'markdown'.
    """
    if output_format == "excel":
        df.to_excel(filepath, index=False)
    else:
        df.to_markdown(filepath, index=False)
