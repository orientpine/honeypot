# [Original] Korean patent batch export tool
# [GJ:refactor] Simplified with BaseBatchExportTool pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.api.korean.patent_search_api import PatentSearchAPI
from mcp_kipris.kipris.tools._base import BaseBatchExportTool
from mcp_kipris.kipris.tools._formatters import generate_output_path

logger = logging.getLogger("mcp-kipris")


class PatentBatchExportArgs(BaseModel):
    word: str = Field(..., description="검색어")
    max_results: int = Field(200, description="최대 검색 결과 수 (기본값: 200, 최대: 1000)")
    output_format: str = Field("excel", description="출력 형식 (excel 또는 markdown)")
    patent: bool = Field(True, description="특허 포함 여부")
    utility: bool = Field(True, description="실용신안 포함 여부")
    desc_sort: bool = Field(True, description="내림차순 정렬 여부")
    sort_spec: str = Field("AD", description="정렬 기준 필드")
    invention_title: str = Field("", description="발명의 명칭에서만 검색할 키워드")
    abst_cont: str = Field("", description="초록에서만 검색할 키워드")
    claim_scope: str = Field("", description="청구범위에서만 검색할 키워드")
    ipc_number: str = Field("", description="IPC 분류번호 필터")
    application_date: str = Field("", description="출원일 필터 (형식: YYYYMMDD~YYYYMMDD)")


@register_tool
class PatentBatchExportTool(BaseBatchExportTool):
    def __init__(self):
        super().__init__("patent_batch_export")
        self.api = PatentSearchAPI(api_key=get_api_key())
        self.description = "특허 검색 결과를 대량으로 수집하여 엑셀 또는 마크다운 파일로 저장합니다."
        self.args_schema = PatentBatchExportArgs

    def _get_dedup_column(self) -> str:
        return "ApplicationNumber"

    def _get_page_increment(self) -> int:
        return 1  # Korean API uses sequential page numbers

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "검색어"},
                    "max_results": {"type": "integer", "description": "최대 검색 결과 수 (기본값: 200)", "default": 200},
                    "output_format": {
                        "type": "string",
                        "description": "출력 형식",
                        "enum": ["excel", "markdown"],
                        "default": "excel",
                    },
                    "patent": {"type": "boolean", "description": "특허 포함 여부 (기본값: true)"},
                    "utility": {"type": "boolean", "description": "실용신안 포함 여부 (기본값: true)"},
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
                    "ipc_number": {"type": "string", "description": "IPC 분류번호 필터"},
                    "application_date": {"type": "string", "description": "출원일 필터 (형식: YYYYMMDD~YYYYMMDD)"},
                },
                "required": ["word"],
            },
        )

    async def _fetch_page(self, validated_args: PatentBatchExportArgs, page_no: int) -> pd.DataFrame:
        rows_per_page = min(validated_args.max_results, 100)
        advanced_kwargs = {}
        for field in ("invention_title", "abst_cont", "claim_scope", "ipc_number", "application_date"):
            value = getattr(validated_args, field)
            if value:
                advanced_kwargs[field] = value

        return await self.api.async_search_unified(
            word=validated_args.word,
            patent=validated_args.patent,
            utility=validated_args.utility,
            page_no=page_no,
            num_of_rows=rows_per_page,
            desc_sort=validated_args.desc_sort,
            sort_spec=validated_args.sort_spec,
            **advanced_kwargs,
        )

    def _generate_filepath(self, validated_args: PatentBatchExportArgs) -> str:
        return generate_output_path(
            word=validated_args.word,
            output_format=validated_args.output_format,
            prefix="patent_export",
        )
