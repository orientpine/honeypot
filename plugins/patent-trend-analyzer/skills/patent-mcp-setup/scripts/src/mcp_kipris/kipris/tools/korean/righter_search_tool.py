# [Original] Korean patent right holder search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.righter_search_api import PatentRighterSearchAPI
from mcp_kipris.kipris.tools._formatters import format_korean_search_result

logger = logging.getLogger("mcp-kipris")


class PatentRighterSearchArgs(BaseModel):
    righter_name: str = Field(..., description="Righter name, it must be filled")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")


@register_tool
class PatentRighterSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_righter_search")
        self.api = PatentRighterSearchAPI(api_key=get_api_key())
        self.description = "Search patents by right holder name (권리자), distinct from applicant (출원인)"
        self.args_schema = PatentRighterSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "righter_name": {"type": "string", "description": "권리자 이름"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD"],
                        "default": "AD",
                    },
                },
                "required": ["righter_name"],
            },
            metadata={
                "usage_hint": "권리자(특허권자)의 이름으로 한국 특허를 검색합니다. 출원인과는 다릅니다.",
                "example_user_queries": [
                    "삼성전자가 권리자인 특허 보여줘",
                    "현대모비스가 특허권을 보유한 특허를 찾아줘",
                ],
                "preferred_response_style": "권리자, 출원일자, 발명의 명칭, 출원번호를 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentRighterSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            rightHoler=validated_args.righter_name,
            docs_start=validated_args.docs_start,
            docs_count=validated_args.docs_count,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
        )

    def _format_response(self, df: pd.DataFrame) -> str:
        return format_korean_search_result(
            df, columns=["ApplicationNumber", "ApplicationDate", "InventionName", "RegistrationStatus"]
        )
