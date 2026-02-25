# [Original] Foreign patent IPC batch export tool
# [GJ:refactor] Simplified with BaseBatchExportTool pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.api.foreign.ipc_search_api import ForeignPatentIPCSearchAPI
from mcp_kipris.kipris.tools._base import BaseBatchExportTool
from mcp_kipris.kipris.tools._formatters import generate_output_path
from mcp_kipris.kipris.tools._schemas import BatchExportMixin, ForeignSearchMixin
from mcp_kipris.kipris.tools.code import country_dict

logger = logging.getLogger("mcp-kipris")


class ForeignPatentIPCBatchExportArgs(ForeignSearchMixin, BatchExportMixin):
    """해외 특허 IPC 배치 내보내기 인자."""

    ipc: str = Field(..., description="IPC 코드 (예: G06N, G06F17)")
    max_results: int = Field(300, description="최대 검색 결과 수 (기본값: 300, 최대: 1000)")
    start_page: int = Field(
        1, description="시작 페이지 (기본값: 1, 2020년 이후 데이터: US=1000, CN=100)"
    )


@register_tool
class ForeignPatentIPCBatchExportTool(BaseBatchExportTool):
    """해외 특허 IPC 배치 내보내기 도구."""

    def __init__(self):
        super().__init__("foreign_patent_ipc_batch_export")
        self.api = ForeignPatentIPCSearchAPI(api_key=get_api_key())
        self.description = "해외 특허를 IPC 코드 기반으로 대량 수집하여 엑셀 또는 마크다운 파일로 저장합니다."
        self.args_schema = ForeignPatentIPCBatchExportArgs

    def _get_dedup_column(self) -> str:
        return "applicationNo"

    def _get_page_increment(self) -> int:
        return 30  # [GJ] KIPRIS foreign API pagination bug workaround

    def _get_max_page(self, start_page: int = 1) -> int:
        return start_page + 1500 * 30  # Safety limit from start_page

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "ipc": {"type": "string", "description": "IPC 코드 (예: G06N, G06F17)"},
                    "max_results": {
                        "type": "integer",
                        "description": "최대 검색 결과 수 (기본값: 300, 최대: 1000)",
                        "default": 300,
                    },
                    "output_format": {
                        "type": "string",
                        "description": "출력 형식 (excel, markdown)",
                        "enum": ["excel", "markdown"],
                        "default": "excel",
                    },
                    "collection_values": {
                        "type": "string",
                        "description": "검색 대상 국가",
                        "enum": list(country_dict.keys()),
                        "default": "US",
                    },
                    "sort_field": {
                        "type": "string",
                        "description": "정렬 기준 필드 (AD-출원일자, OPD-공개일자, GD-등록일자, PD-공보일자)",
                        "enum": ["AD", "OPD", "GD", "PD"],
                        "default": "AD",
                    },
                    "sort_state": {
                        "type": "boolean",
                        "description": "내림차순 정렬 여부 (기본값: true)",
                        "default": True,
                    },
                    "start_page": {
                        "type": "integer",
                        "description": "시작 페이지 (기본값: 1, 2020년 이후 데이터: US=1000, CN=100)",
                        "default": 1,
                    },
                },
                "required": ["ipc"],
            },
        )

    async def _fetch_page(self, validated_args: ForeignPatentIPCBatchExportArgs, page_no: int) -> pd.DataFrame:
        return await self.api.async_search_unified(
            ipc=validated_args.ipc,
            current_page=page_no,
            sort_field=validated_args.sort_field,
            sort_state=validated_args.sort_state,
            collection_values=validated_args.collection_values,
        )

    def _generate_filepath(self, validated_args: ForeignPatentIPCBatchExportArgs) -> str:
        return generate_output_path(
            word=validated_args.ipc,
            output_format=validated_args.output_format,
            prefix="patent_IPC",
            country=validated_args.collection_values,
        )

    def _build_result_message(
        self, df: pd.DataFrame, filepath: str, validated_args: ForeignPatentIPCBatchExportArgs
    ) -> str:
        country = validated_args.collection_values
        return (
            f"성공적으로 {len(df)}건의 {country} 특허 정보를 저장했습니다.\n"
            f"IPC: {validated_args.ipc}\n"
            f"저장 위치: {filepath}"
        )
