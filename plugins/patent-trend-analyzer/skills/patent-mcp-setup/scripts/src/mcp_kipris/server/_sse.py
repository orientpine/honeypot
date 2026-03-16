"""[GJ] HTTP/SSE server entry point.

Starlette-based server for web client access. Supports both SSE and REST API modes.
"""

import argparse
import json
import logging

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from mcp_kipris.kipris._registry import get_all_tools
from mcp_kipris.server._core import create_mcp_server

logger = logging.getLogger("mcp-kipris")


# ── [Original] Content serialization helpers ────────────────


def tool_to_dict(tool: Tool) -> dict:
    """Tool 객체를 dictionary로 변환."""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
        "output_schema": tool.outputSchema if hasattr(tool, "outputSchema") else None,
        "metadata": tool.metadata if hasattr(tool, "metadata") else None,
    }


def content_to_dict(content: TextContent | ImageContent | EmbeddedResource) -> dict:
    """Content 객체를 dictionary로 변환."""
    if isinstance(content, TextContent):
        return {
            "type": "text",
            "text": content.text,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    elif isinstance(content, ImageContent):
        return {
            "type": "image",
            "url": content.url,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    elif isinstance(content, EmbeddedResource):
        return {
            "type": "embedded",
            "url": content.url,
            "metadata": content.metadata if hasattr(content, "metadata") else None,
        }
    else:
        raise ValueError(f"Unknown content type: {type(content)}")


# ── [GJ] Starlette app factory ────────────────


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that serves the MCP server with SSE.

    Args:
        mcp_server: Configured MCP Server instance.
        debug: Enable Starlette debug mode.

    Returns:
        Starlette: Configured web application.
    """
    sse = SseServerTransport("/messages/")
    tools = get_all_tools()

    async def well_known_mcp(request):
        base = str(request.base_url).rstrip("/")
        body = json.dumps(
            {
                "mcpVersion": "2024-01-01",
                "capabilities": ["sse"],
                "sse": {
                    "url": f"{base}/sse",
                    "message_url": f"{base}/messages",
                },
            }
        )
        return Response(
            content=body.encode("utf-8"),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Length": str(len(body.encode("utf-8"))),
                "Connection": "close",
            },
        )

    async def handle_sse(scope, receive, send):
        """Raw ASGI SSE handler — avoids private request._send attribute."""
        try:
            logger.info("[SSE] New connection request received")
            async with sse.connect_sse(scope, receive, send) as (
                read_stream,
                write_stream,
            ):
                logger.info("[SSE] Connected, running MCP server...")
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
                logger.info("[SSE] MCP server run() completed")
            logger.info("[SSE] Disconnected cleanly")
        except Exception as e:
            logger.error(f"[SSE] Connection error: {e}")

    async def list_tools_endpoint(request: Request) -> JSONResponse:
        """Return tool list as JSON (REST API endpoint)."""
        tool_descs = [tool.get_tool_description() for tool in tools.values()]
        return JSONResponse([tool_to_dict(t) for t in tool_descs])

    async def handle_post_message(request: Request) -> Response:
        """Process tool call messages (REST API endpoint)."""
        try:
            body = await request.json()
            logger.debug(f"Received message: {body}")

            if not isinstance(body, dict):
                return Response(status_code=400, content="Message must be a dictionary")

            message_type = body.get("type")
            if message_type != "tool":
                return Response(status_code=400, content="Invalid message type")

            tool_name = body.get("name")
            if not tool_name:
                return Response(status_code=400, content="Tool name is required")

            args = body.get("args", {})
            if not isinstance(args, dict):
                return Response(status_code=400, content="Arguments must be a dictionary")

            # [GJ] Use tool handler directly from registry
            tool_handler = tools.get(tool_name)
            if not tool_handler:
                return Response(status_code=404, content=f"Unknown tool: {tool_name}")

            result = await tool_handler.run_tool_async(args)
            result_dicts = [content_to_dict(content) for content in result]
            return JSONResponse(result_dicts)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return Response(status_code=500, content=f"Error: {e}")

    return Starlette(
        debug=debug,
        routes=[
            Route("/.well-known/mcp", endpoint=well_known_mcp),
            Mount("/sse", app=handle_sse),
            Route("/tools", endpoint=list_tools_endpoint),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# ── [GJ] Main entry point ────────────────


async def main():
    """Start MCP KIPRIS server (HTTP or stdio based on args)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=6274, help="Port to listen on (default: 6274)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    args = parser.parse_args()

    app = create_mcp_server()

    if args.http:
        logger.info(f"Starting MCP KIPRIS HTTP server on {args.host}:{args.port}...")
        try:
            starlette_app = create_starlette_app(app, debug=True)
            config = uvicorn.Config(app=starlette_app, host=args.host, port=args.port)
            server = uvicorn.Server(config=config)
            await server.serve()
        except Exception as e:
            logger.error(f"SSE server error: {e}")
            raise RuntimeError(f"SSE Server Error: {e}")
    else:
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
