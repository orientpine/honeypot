# [GJ] Entry point for `python -m mcp_kipris.server`
import asyncio

from mcp_kipris.server._stdio import main

asyncio.run(main())
