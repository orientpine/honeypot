# [Original] Foreign patent batch export tool
# [GJ:refactor] Simplified with BaseBatchExportTool pattern + @register_tool

import logging

import pandas as pd
from mcp.types import Tool
from pydantic import Field

from mcp_kipris.kipris._config import get_api_key
from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.api.foreign.free_search_api import ForeignPatentFreeSearchAPI
from mcp_kipris.kipris.tools._base import BaseBatchExportTool
from mcp_kipris.kipris.tools._formatters import generate_output_path
from mcp_kipris.kipris.tools._schemas import BatchExportMixin, ForeignSearchMixin
from mcp_kipris.kipris.tools.code import country_dict

logger = logging.getLogger("mcp-kipris")


class ForeignPatentBatchExportArgs(ForeignSearchMixin, BatchExportMixin):
    """해외 특허 배치 내보내기 인자."""

    word: str = Field(..., description="검색어")
    ipc_filter: str = Field(
        "",
        description="IPC 필터 (예: G06N - 후처리로 해당 IPC 포함 특허만 필터링)",
    )


@register_tool
class ForeignPatentBatchExportTool(BaseBatchExportTool):
    """해외 특허 배치 내보내기 도구."""

    def __init__(self):
        super().__init__("foreign_patent_batch_export")
        self.api = ForeignPatentFreeSearchAPI(api_key=get_api_key())
        self.description = "해외 특허 검색 결과를 대량으로 수집하여 엑셀 또는 마크다운 파일로 저장합니다."
        self.args_schema = ForeignPatentBatchExportArgs

    def _get_dedup_column(self) -> str:
        return "applicationNo"

    def _get_page_increment(self) -> int:
        return 30  # [GJ] KIPRIS foreign API pagination bug workaround

    def _get_max_page(self, start_page: int = 1) -> int:
        return 1500

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "검색어"},
                    "max_results": {
                        "type": "integer",
                        "description": "최대 검색 결과 수 (기본값: 200, 최대: 1000)",
                        "default": 200,
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
                        "description": "정렬 기준 필드 (AD-출원일자, PD-공고일자, GD-등록일자, OPD-공개일자)",
                        "enum": ["AD", "PD", "GD", "OPD"],
                        "default": "AD",
                    },
                    "sort_state": {
                        "type": "boolean",
                        "description": "내림차순 정렬 여부 (기본값: true)",
                        "default": True,
                    },
                    "ipc_filter": {
                        "type": "string",
                        "description": "IPC 필터 (예: G06N - 후처리로 해당 IPC 포함 특허만 필터링)",
                        "default": "",
                    },
                },
                "required": ["word"],
            },
        )

    async def _fetch_page(self, validated_args: ForeignPatentBatchExportArgs, page_no: int) -> pd.DataFrame:
        return await self.api.async_search_unified(
            word=validated_args.word,
            current_page=page_no,
            sort_field=validated_args.sort_field,
            sort_state=validated_args.sort_state,
            collection_values=validated_args.collection_values,
        )

    def _post_process(self, df: pd.DataFrame, validated_args: ForeignPatentBatchExportArgs) -> pd.DataFrame:
        if validated_args.ipc_filter and "ipc" in df.columns:
            ipc_pattern = validated_args.ipc_filter.upper()
            before = len(df)
            df = df[df["ipc"].fillna("").str.upper().str.contains(ipc_pattern, regex=False)]
            logger.info(f"[{self.name}] IPC filter '{validated_args.ipc_filter}': {before} -> {len(df)}")
            if df.empty:
                return df
        return df

    def _generate_filepath(self, validated_args: ForeignPatentBatchExportArgs) -> str:
        ipc_suffix = ""
        if validated_args.ipc_filter:
            safe_ipc = "".join(c for c in validated_args.ipc_filter if c.isalnum())
            ipc_suffix = f"_IPC{safe_ipc}"
        return generate_output_path(
            word=validated_args.word,
            output_format=validated_args.output_format,
            prefix="patent",
            country=validated_args.collection_values,
            ipc_suffix=ipc_suffix,
        )

    def _build_result_message(
        self, df: pd.DataFrame, filepath: str, validated_args: ForeignPatentBatchExportArgs
    ) -> str:
        country = validated_args.collection_values
        result_msg = f"성공적으로 {len(df)}건의 {country} 특허 정보를 저장했습니다.\n"
        if validated_args.ipc_filter:
            result_msg += f"IPC 필터: {validated_args.ipc_filter}\n"
        result_msg += f"저장 위치: {filepath}"
        return result_msg
