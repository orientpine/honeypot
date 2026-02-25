# [Original] Korean patent applicant search tool
# [GJ:refactor] Simplified with BaseToolHandler pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.korean.applicant_search_api import PatentApplicantSearchAPI
from mcp_kipris.kipris.tools._formatters import format_korean_search_result

logger = logging.getLogger("mcp-kipris")


class PatentApplicantSearchArgs(BaseModel):
    applicant: str = Field(..., description="Applicant name is required")
    docs_start: int = Field(1, description="Start index for documents, default is 1")
    docs_count: int = Field(10, description="Number of documents to return, default is 10, range is 1-30")
    patent: bool = Field(True, description="Include patents, default is True")
    utility: bool = Field(True, description="Include utility models, default is True")
    lastvalue: str = Field("", description="Patent registration status; leave empty for all, (A, C, F, G, I, J, R or empty)")
    sort_spec: str = Field("AD", description="Field to sort by; default is 'AD'")
    desc_sort: bool = Field(True, description="Sort in descending order; default is True")


@register_tool
class PatentApplicantSearchTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_applicant_search")
        self.api = PatentApplicantSearchAPI(api_key=get_api_key())
        self.description = "patent search by applicant name, this tool is for korean patent search"
        self.args_schema = PatentApplicantSearchArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "applicant": {"type": "string", "description": "출원인 이름"},
                    "docs_start": {"type": "integer", "description": "검색 시작 위치 (기본값: 1)"},
                    "docs_count": {"type": "integer", "description": "검색 결과 수 (기본값: 10, 범위: 1-30)"},
                    "patent": {"type": "boolean", "description": "특허 포함 여부 (기본값: true)"},
                    "utility": {"type": "boolean", "description": "실용신안 포함 여부 (기본값: true)"},
                    "lastvalue": {
                        "type": "string",
                        "description": "특허 등록 상태 (A:공개, C:정정공개, F:공고, G:정정공고, I:무효공고, J:취소공고, R:재공고, 공백:전체)",
                        "enum": ["A", "C", "F", "G", "I", "J", "R", ""],
                    },
                    "sort_spec": {
                        "type": "string",
                        "description": "정렬 기준 필드",
                        "enum": ["PD", "AD", "GD", "OPD", "FD", "FOD", "RD"],
                        "default": "AD",
                    },
                    "desc_sort": {"type": "boolean", "description": "내림차순 정렬 여부 (기본값: true)"},
                },
                "required": ["applicant"],
            },
            metadata={
                "usage_hint": "출원인(특허를 출원한 사람 또는 회사)의 이름으로 한국 특허를 검색합니다.",
                "example_user_queries": [
                    "삼성전자가 출원한 특허 보여줘",
                    "LG화학이 최근 출원한 특허 5건 검색해줘",
                ],
                "preferred_response_style": "출원인, 출원일자, 발명의 명칭, 출원번호를 포함하여 표 형태로 정리해주세요.",
            },
        )

    async def _execute_async(self, validated_args: PatentApplicantSearchArgs) -> pd.DataFrame:
        return await self.api.async_search_unified(
            applicant=validated_args.applicant,
            docs_count=validated_args.docs_count,
            docs_start=validated_args.docs_start,
            lastvalue=validated_args.lastvalue,
            patent=validated_args.patent,
            utility=validated_args.utility,
            sort_spec=validated_args.sort_spec,
            desc_sort=validated_args.desc_sort,
        )

    def _format_response(self, df: pd.DataFrame) -> str:
        return format_korean_search_result(df)
