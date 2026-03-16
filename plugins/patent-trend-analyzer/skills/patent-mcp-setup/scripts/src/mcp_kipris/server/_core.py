"""[GJ] Common MCP server logic.

Replaces duplicated tool registration, list_tools, and call_tool code
from server.py and sse_server.py (~80% overlap eliminated).
"""

import datetime
import logging
from collections.abc import Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from mcp_kipris.kipris._registry import get_all_tools

load_dotenv()

logger = logging.getLogger("mcp-kipris")


def create_mcp_server() -> Server:
    """Create and configure an MCP Server instance with all registered tools.

    Returns:
        Server: Configured MCP server with list_tools and call_tool handlers.
    """
    app = Server("mcp-kipris")
    tools = get_all_tools()

    logger.info(f"[core] {len(tools)} tools loaded from registry")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        logger.info(f"[core] list_tools called, {len(tools)} tools available")
        return [tool.get_tool_description() for tool in tools.values()]

    @app.call_tool()
    async def call_tool(tool_name: str, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls with async-first, sync-fallback execution."""
        if not isinstance(args, dict):
            raise RuntimeError("arguments must be dictionary")

        tool_handler = tools.get(tool_name)
        if not tool_handler:
            raise ValueError(f"Unknown tool: {tool_name}")

        logger.info(f"[core] Executing tool: {tool_name}")
        start_time = datetime.datetime.now()

        try:
            # [GJ] Async-first with sync fallback
            result = await tool_handler.run_tool_async(args)
        except NotImplementedError as e:
            logger.warning(f"[core] Async failed for {tool_name}, using sync: {e}")
            result = tool_handler.run_tool(args)

        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        logger.info(f"[core] Tool {tool_name} completed in {elapsed:.2f}s")

        return result

    return app
