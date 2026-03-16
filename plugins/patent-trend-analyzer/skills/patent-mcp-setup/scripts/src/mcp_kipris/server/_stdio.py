"""[GJ] stdio server entry point.

Minimal wrapper around create_mcp_server() for Claude Code integration.
"""

import logging

from mcp.server.stdio import stdio_server

from mcp_kipris.server._core import create_mcp_server

logger = logging.getLogger("mcp-kipris")


async def main():
    """Start MCP KIPRIS server in stdio mode."""
    app = create_mcp_server()

    logger.info("Starting MCP KIPRIS stdio server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio_server initialized")
            init_options = app.create_initialization_options()
            await app.run(read_stream, write_stream, init_options)
    except Exception as e:
        logger.error(f"stdio server error: {e}")
        raise RuntimeError(f"stdio server error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
