"""[GJ] Tool registry with decorator-based auto-registration.

Replaces manual tool registration in server.py and sse_server.py.
Tools register themselves via @register_tool decorator at class definition time.
"""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_kipris.kipris.abc import ToolHandler

logger = logging.getLogger("mcp-kipris")

_tool_registry: dict[str, ToolHandler] = {}
_tools_loaded = False

# [GJ] All tool modules to import for registration
_TOOL_MODULES = [
    "mcp_kipris.kipris.tools.korean.applicant_search_tool",
    "mcp_kipris.kipris.tools.korean.application_number_search_tool",
    "mcp_kipris.kipris.tools.korean.patent_batch_export_tool",
    "mcp_kipris.kipris.tools.korean.patent_detail_search_tool",
    "mcp_kipris.kipris.tools.korean.patent_free_search_tool",
    "mcp_kipris.kipris.tools.korean.patent_search_tool",
    "mcp_kipris.kipris.tools.korean.patent_summary_search_tool",
    "mcp_kipris.kipris.tools.korean.righter_search_tool",
    "mcp_kipris.kipris.tools.foreign.applicant_search_tool",
    "mcp_kipris.kipris.tools.foreign.application_number_search_tool",
    "mcp_kipris.kipris.tools.foreign.batch_export_tool",
    "mcp_kipris.kipris.tools.foreign.free_search_tool",
    "mcp_kipris.kipris.tools.foreign.international_application_number_search_tool",
    "mcp_kipris.kipris.tools.foreign.international_open_number_search_tool",
    "mcp_kipris.kipris.tools.foreign.ipc_batch_export_tool",
    "mcp_kipris.kipris.tools.preprocessing.search_planner_tool",
    "mcp_kipris.kipris.tools.preprocessing.keyword_optimizer_tool",
    "mcp_kipris.kipris.tools.preprocessing.result_deduplicator_tool",
]


def register_tool(cls):
    """[GJ] Decorator: auto-register tool class at definition time.

    Usage:
        @register_tool
        class MyTool(ToolHandler):
            ...
    """
    instance = cls()
    _tool_registry[instance.name] = instance
    logger.info(f"[registry] Tool registered: {instance.name}")
    return cls


def get_all_tools() -> dict[str, ToolHandler]:
    """Return all registered tools, loading modules if needed.

    Returns:
        dict[str, ToolHandler]: Map of tool name to tool instance.
    """
    _ensure_tools_loaded()
    return dict(_tool_registry)


def _ensure_tools_loaded():
    """Import all tool modules to trigger @register_tool decorators."""
    global _tools_loaded
    if _tools_loaded:
        return
    for module_path in _TOOL_MODULES:
        try:
            importlib.import_module(module_path)
        except Exception as e:
            logger.error(f"[registry] Failed to load tool module {module_path}: {e}")
    _tools_loaded = True
