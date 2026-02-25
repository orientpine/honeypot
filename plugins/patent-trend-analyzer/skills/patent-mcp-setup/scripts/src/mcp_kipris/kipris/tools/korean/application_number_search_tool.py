# [Original] Korean patent application number search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool
# [GJ:fix] Removed references to non-existent fields (lastvalue, patent, utility)

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.application_number_search_api import PatentApplicationNumberSearchAPI
from mcp_kipris.kipris.tools._formatters import format_korean_search_result

logger = logging.getLogger("mcp-kipris")


class PatentApplicationNumberSearchArgs(BaseModel):
    application_number: str = Field(..., description="Application number, it must be filled")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(True, description="Sort in descending order; default is True")
    sort_spec: str = Field("AD", description="Field to sort by; default is 'AD'")


@register_tool
class PatentApplicationNumberSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_application_number_search")
        self.api = PatentApplicationNumberSearchAPI(api_key=get_api_key())
        self.description = "Patent search by application number, this tool is for korean patent search"
        self.args_schema = PatentApplicationNumberSearchArgs

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
                "properties": {
                    "application_number": {"type": "string", "description": "출원번호"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD", "FD", "FOD", "RD"],
                        "default": "AD",
                    },
                },
                "required": ["application_number"],
            },
        )

    async def _execute_async(self, validated_args: PatentApplicationNumberSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            application_number=validated_args.application_number,
            docs_count=validated_args.docs_count,
            docs_start=validated_args.docs_start,
            sort_spec=validated_args.sort_spec,
            desc_sort=validated_args.desc_sort,
        )

    def _format_response(self, df: pd.DataFrame) -> str:
        return format_korean_search_result(df)
