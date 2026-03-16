# [Original] Abstract base class for tool handlers
# [GJ:refactor] Enhanced with common execution logic, error handling, and async support

import logging
from collections.abc import Sequence

import pandas as pd
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import ValidationError

logger = logging.getLogger("mcp-kipris")


class ToolHandler:
    """[GJ] Enhanced base class for all MCP tool handlers.

    Subclasses MUST implement:
        - get_tool_description() -> Tool
        - _execute_async(validated_args) -> pd.DataFrame | str
        - _format_response(result) -> str

    Subclasses MAY override:
        - _execute(validated_args) -> pd.DataFrame | str  (sync fallback)
        - _preprocess_args(args) -> dict  (arg preprocessing)

    The base class provides unified run_tool/run_tool_async with:
        - Pydantic validation via self.args_schema
        - Consistent error handling (always returns TextContent, never raises)
        - Logging of tool execution
    """

    def __init__(self, tool_name: str):
        self.name = tool_name

    def get_tool_description(self) -> Tool:
        """Return MCP Tool description. Must be overridden."""
        raise NotImplementedError("Subclasses must implement this method")

    def _preprocess_args(self, args: dict) -> dict:
        """[GJ] Optional preprocessing of raw args before validation.

        Override this to strip hyphens, set defaults, etc.
        """
        return args

    async def _execute_async(self, validated_args) -> pd.DataFrame | str:
        """[GJ] Execute the tool's core logic asynchronously.

        Args:
            validated_args: Pydantic-validated arguments.

        Returns:
            pd.DataFrame for search results, or str for file paths/messages.
        """
        raise NotImplementedError("Subclasses must implement _execute_async")

    def _execute(self, validated_args) -> pd.DataFrame | str:
        """[GJ] Execute the tool's core logic synchronously (optional fallback)."""
        raise NotImplementedError("Subclasses must implement _execute for sync support")

    def _format_response(self, result: pd.DataFrame | str) -> str:
        """[GJ] Format execution result as text for MCP response.

        Args:
            result: DataFrame or string from _execute/_execute_async.

        Returns:
            str: Formatted text response.
        """
        if isinstance(result, str):
            return result
        return result.to_markdown(index=False)

    # ── [GJ] Unified execution with error handling ────────────────

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """[GJ] Synchronous tool execution with unified error handling.

        Args:
            args: Raw arguments dict from MCP call.

        Returns:
            List of TextContent with results or error message.
        """
        try:
            args = self._preprocess_args(args)
            validated = self.args_schema(**args) if hasattr(self, "args_schema") else args
            result = self._execute(validated)

            if isinstance(result, pd.DataFrame) and result.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            return [TextContent(type="text", text=self._format_response(result))]

        except ValidationError as e:
            logger.error(f"[{self.name}] Validation error: {e}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {e}")]
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {e}")]

    async def run_tool_async(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """[GJ] Asynchronous tool execution with unified error handling.

        Args:
            args: Raw arguments dict from MCP call.

        Returns:
            List of TextContent with results or error message.
        """
        try:
            args = self._preprocess_args(args)
            validated = self.args_schema(**args) if hasattr(self, "args_schema") else args
            result = await self._execute_async(validated)

            if isinstance(result, pd.DataFrame) and result.empty:
                return [TextContent(type="text", text="검색 결과가 없습니다.")]

            return [TextContent(type="text", text=self._format_response(result))]

        except ValidationError as e:
            logger.error(f"[{self.name}] Validation error: {e}")
            return [TextContent(type="text", text=f"입력값 검증 오류: {e}")]
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return [TextContent(type="text", text=f"오류가 발생했습니다: {e}")]
