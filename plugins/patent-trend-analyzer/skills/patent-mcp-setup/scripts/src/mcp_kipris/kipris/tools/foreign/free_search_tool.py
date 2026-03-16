# [Original] Foreign patent free text search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.foreign.free_search_api import ForeignPatentFreeSearchAPI
from mcp_kipris.kipris.tools._schemas import ForeignSearchMixin
from mcp_kipris.kipris.tools.code import country_dict, sort_field_dict

logger = logging.getLogger("mcp-kipris")


class ForeignPatentFreeSearchArgs(ForeignSearchMixin):
    word: str = Field(..., description="Search word, it must be filled")


@register_tool
class ForeignPatentFreeSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("foreign_patent_free_search")
        self.api = ForeignPatentFreeSearchAPI(api_key=get_api_key())
        self.description = "foreign patent search by free text, this tool is for foreign(US, EP, WO, JP, PJ, CP, CN, TW, RU, CO, SE, ES, IL) patent search"
        self.args_schema = ForeignPatentFreeSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "검색어"},
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
                "required": ["word"],
            },
            metadata={
                "usage_hint": "해외 특허를 키워드로 자유 검색합니다.",
                "example_user_queries": ["미국 특허에서 robot navigation 검색해줘", "유럽 특허에서 LLM 관련 특허 찾아줘"],
                "preferred_response_style": "출원번호, 출원일자, 발명의 명칭을 포함하여 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: ForeignPatentFreeSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            word=validated_args.word,
            current_page=validated_args.current_page,
            sort_field=validated_args.sort_field,
            sort_state=validated_args.sort_state,
            collection_values=validated_args.collection_values,
        )
