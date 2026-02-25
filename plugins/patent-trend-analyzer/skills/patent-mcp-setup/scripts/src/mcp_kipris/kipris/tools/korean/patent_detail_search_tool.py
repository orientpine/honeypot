# [Original] Korean patent detail search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI

logger = logging.getLogger("mcp-kipris")


class PatentDetailSearchArgs(BaseModel):
    application_number: str = Field(..., description="출원번호 (숫자만, 하이픈(-) 없이 입력하세요)")


@register_tool
class PatentDetailSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_detail_search")
        self.api = PatentDetailSearchAPI(api_key=get_api_key())
        self.description = "patent detail search by application number for detailed legal/technical information"
        self.args_schema = PatentDetailSearchArgs

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
                "usage_hint": "출원번호가 주어졌을 때, 해당 특허의 상세한 법적/기술적 정보를 보여줍니다.",
                "example_user_queries": [
                    "출원번호 1020250037551 특허의 상세 정보 알려줘",
                    "두 번째 특허의 구체적인 내용을 알고 싶어",
                ],
                "preferred_response_style": "Markdown 형식으로 섹션별로 정리해서 보여주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentDetailSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            application_number=validated_args.application_number,
        )
