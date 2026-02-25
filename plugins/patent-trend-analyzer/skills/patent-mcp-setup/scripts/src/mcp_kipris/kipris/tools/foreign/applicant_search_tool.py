# [Original] Foreign patent applicant search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool
# [GJ:fix] Replaced ValueError raises with TextContent returns (consistent error handling)

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.foreign.applicant_search import ForeignPatentApplicantSearchAPI
from mcp_kipris.kipris.tools._schemas import ForeignSearchMixin
from mcp_kipris.kipris.tools.code import country_dict, sort_field_dict

logger = logging.getLogger("mcp-kipris")


class ForeignPatentApplicantSearchArgs(ForeignSearchMixin):
    applicant: str = Field(..., description="Applicant name, it must be filled")


@register_tool
class ForeignPatentApplicantSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("foreign_patent_applicant_search")
        self.api = ForeignPatentApplicantSearchAPI(api_key=get_api_key())
        self.description = "foreign patent search by applicant, this tool is for foreign(US, EP, WO, JP, PJ, CP, CN, TW, RU, CO, SE, ES, IL) patent search"
        self.args_schema = ForeignPatentApplicantSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "applicant": {"type": "string", "description": "출원인명"},
                    "current_page": {"type": "integer", "description": "현재 페이지 번호 (기본값: 1)"},
                    "sort_field": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": list(sort_field_dict.keys()),
                        "default": "AD",
                    },
                    "sort_state": {"type": "boolean", "description": "정렬 상태 (기본값: true)"},
                    "collection_values": {
                        "type": "string",
                        "description": "검색 대상 국가",
                        "enum": list(country_dict.keys()),
                        "default": "US",
                    },
                },
                "required": ["applicant"],
            },
        )

    async def _execute_async(self, validated_args: ForeignPatentApplicantSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            applicant=validated_args.applicant,
            current_page=validated_args.current_page,
            sort_field=validated_args.sort_field,
            sort_state=validated_args.sort_state,
            collection_values=validated_args.collection_values,
        )
