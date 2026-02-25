# [Original] Korean patent free search tool (keyword search with advanced filters)
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

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


class PatentFreeSearchArgs(BaseModel):
    word: str = Field(..., description="Search word, it must be filled")
    patent: bool = Field(True, description="Include patent search")
    utility: bool = Field(True, description="Include utility model search")
    lastvalue: str = Field("", description="Last value for pagination")
    docs_start: int = Field(1, description="Start index of documents")
    docs_count: int = Field(10, description="Number of documents to return")
    desc_sort: bool = Field(True, description="Sort in descending order")
    sort_spec: str = Field("AD", description="Sort specification")
    invention_title: str = Field("", description="Search keyword in invention title only")
    abst_cont: str = Field("", description="Search keyword in abstract only")
    claim_scope: str = Field("", description="Search keyword in claims only")
    ipc_number: str = Field("", description="IPC classification number filter (e.g., G06N)")
    application_date: str = Field("", description="Application date filter (format: YYYYMMDD~YYYYMMDD)")


@register_tool
class PatentFreeSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_free_search")
        self.api = PatentSearchAPI(api_key=get_api_key())
        self.description = "patent search by keyword with advanced filters (title, abstract, claims, IPC, date), this tool is for korean patent search"
        self.args_schema = PatentFreeSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "검색어"},
                    "patent": {"type": "boolean", "description": "특허 포함 여부 (기본값: true)"},
                    "utility": {"type": "boolean", "description": "실용신안 포함 여부 (기본값: true)"},
                    "lastvalue": {
                        "type": "string",
                        "description": "특허 등록 상태",
                        "enum": ["A", "C", "F", "G", "I", "J", "R", ""],
                    },
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10, 범위: 1-30)"},
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD"],
                        "default": "AD",
                    },
                    "invention_title": {"type": "string", "description": "발명의 명칭에서만 검색할 키워드"},
                    "abst_cont": {"type": "string", "description": "초록에서만 검색할 키워드"},
                    "claim_scope": {"type": "string", "description": "청구범위에서만 검색할 키워드"},
                    "ipc_number": {"type": "string", "description": "IPC 분류번호 필터 (예: G06N)"},
                    "application_date": {"type": "string", "description": "출원일 필터 (형식: YYYYMMDD~YYYYMMDD)"},
                },
                "required": ["word"],
            },
            metadata={
                "usage_hint": "키워드로 한국 특허를 검색하고 특허에 대한 정보를 제공합니다.",
                "example_user_queries": ["'이차전지' 관련 특허를 검색해줘"],
                "preferred_response_style": "키워드, 출원일자, 발명의 명칭, 출원인을 포함하여 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentFreeSearchArgs) -> pd.DataFrame:
        # [GJ] Build advanced search kwargs (only non-empty values)
        advanced_kwargs = {}
        for field in ("invention_title", "abst_cont", "claim_scope", "ipc_number", "application_date"):
            value = getattr(validated_args, field)
            if value:
                advanced_kwargs[field] = value

        return await self.api.async_search_unified(
            word=validated_args.word,
            num_of_rows=validated_args.docs_count,
            page_no=validated_args.docs_start,
            lastvalue=validated_args.lastvalue,
            patent=validated_args.patent,
            utility=validated_args.utility,
            sort_spec=validated_args.sort_spec,
            desc_sort=validated_args.desc_sort,
            **advanced_kwargs,
        )

    def _format_response(self, df: pd.DataFrame) -> str:
        return format_korean_search_result(df)
