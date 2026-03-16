# [Original] Korean patent summary search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_summary_search_api import PatentSummarySearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentSummarySearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")


@register_tool
class PatentSummarySearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_summary_search")
        self.api = PatentSummarySearchAPI(api_key=get_api_key())
        self.description = "patent summary search by application number, this tool is for korean patent search"
        self.args_schema = PatentSummarySearchArgs

    def _preprocess_args(self, args: dict) -> dict:
        if "application_number" in args:
            args["application_number"] = str(args["application_number"]).replace("-", "")
        return args

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
                "usage_hint": "출원번호로 한국 특허를 검색하고 요약 정보를 제공합니다.",
                "example_user_queries": ["1020230045678 특허의 요약 정보를 알고 싶어."],
                "preferred_response_style": "출원번호, 출원일자, 발명의 명칭을 포함하여 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentSummarySearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            application_number=validated_args.application_number,
        )
