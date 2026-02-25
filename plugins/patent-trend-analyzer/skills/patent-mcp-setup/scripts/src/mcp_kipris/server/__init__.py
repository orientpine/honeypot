"""[GJ] Server package for MCP KIPRIS.

Provides unified server creation with separate entry points for stdio and HTTP/SSE modes.
Re-exports main() for backward compatibility with `python -m mcp_kipris.server`.
"""

from mcp_kipris.server._stdio import main

__all__ = ["main"]
