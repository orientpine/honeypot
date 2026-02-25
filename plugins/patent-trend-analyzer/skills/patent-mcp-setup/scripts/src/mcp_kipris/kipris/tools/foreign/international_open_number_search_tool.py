# [Original] Foreign patent international open number search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool
# [GJ:fix] Replaced ValueError raises with TextContent returns (consistent error handling)

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.foreign.international_open_number_search import (
    ForeignPatentInternationalOpenNumberSearchAPI,
)
from mcp_kipris.kipris.tools._schemas import ForeignSearchMixin
from mcp_kipris.kipris.tools.code import country_dict, sort_field_dict

logger = logging.getLogger("mcp-kipris")


class ForeignPatentInternationalOpenNumberSearchArgs(ForeignSearchMixin):
    international_open_number: str = Field(..., description="International open number, it must be filled")


@register_tool
class ForeignPatentInternationalOpenNumberSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("foreign_international_open_number_search")
        self.api = ForeignPatentInternationalOpenNumberSearchAPI(api_key=get_api_key())
        self.description = "foreign patent search by international open number, this tool is for foreign(US, EP, WO, JP, PJ, CP, CN, TW, RU, CO, SE, ES, IL) patent search"
        self.args_schema = ForeignPatentInternationalOpenNumberSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "international_open_number": {"type": "string", "description": "국제공개번호"},
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
                "required": ["international_open_number"],
            },
        )

    async def _execute_async(
        self, validated_args: ForeignPatentInternationalOpenNumberSearchArgs
    ) -> pd.DataFrame:
        return await self.api.async_search_unified(
            international_open_number=validated_args.international_open_number,
            current_page=validated_args.current_page,
            sort_field=validated_args.sort_field,
            sort_state=validated_args.sort_state,
            collection_values=validated_args.collection_values,
        )
