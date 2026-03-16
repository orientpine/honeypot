# [Original] HTTP/SSE server entry point
# [GJ:refactor] Now a thin wrapper around server/_sse.py for backward compatibility
# [GJ:fix] Previously missing KoreanPatentBatchExportTool registration (14/15 tools)
# Usage: python -m mcp_kipris.sse_server --http --port 6274 --host 0.0.0.0

from mcp_kipris.server._sse import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
