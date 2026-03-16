# [Original] Korean patent search by application number (basic info)
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool
# [GJ:fix] Fixed calling non-existent self.api.search() - now uses async_search_unified

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_search_api import PatentSearchAPI
from mcp_kipris.kipris.tools._formatters import format_korean_search_result

logger = logging.getLogger("mcp-kipris")


class PatentSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


@register_tool
class PatentSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_search")
        self.api = PatentSearchAPI(api_key=get_api_key())
        self.description = "patent search by application number, this tool is for korean patent search"
        self.args_schema = PatentSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {"application_number": {"type": "string", "description": "출원번호"}},
                "required": ["application_number"],
            },
            metadata={
                "usage_hint": "출원번호로 한국 특허를 검색하고 특허에 대한 기본적인 정보를 제공합니다.",
                "example_user_queries": ["1020230045678 특허의 기본 정보를 알고 싶어."],
                "preferred_response_style": "출원번호, 출원일자, 발명의 명칭, 출원인을 포함하여 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentSearchArgs) -> pd.DataFrame:
        # [GJ:fix] Use async_search_unified with application_number as keyword
        return await self.api.async_search_unified(
            word="",
            application_number=validated_args.application_number,
        )

    def _format_response(self, df: pd.DataFrame) -> str:
        return format_korean_search_result(
            df, columns=["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]
        )
