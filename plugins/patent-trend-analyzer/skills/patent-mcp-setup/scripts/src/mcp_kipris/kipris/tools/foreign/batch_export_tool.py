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
from mcp_kipris.kipris.tools._formatters import generate_output_path, sanitize_filename
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

    async def _execute_async(self, validated_args: ForeignPatentBatchExportArgs) -> str:
        """[GJ] Extended to support IPC post-processing filter."""
        # Use parent's pagination + dedup logic
        results = []
        page_no = 1
        total_fetched = 0
        max_results = validated_args.max_results
        page_increment = self._get_page_increment()
        max_page = self._get_max_page()
        consecutive_empty = 0

        while total_fetched < max_results:
            logger.info(f"[{self.name}] Fetching page {page_no}, total: {total_fetched}")

            page_df = await self._fetch_page(validated_args, page_no)

            if page_df.empty:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    logger.info(f"[{self.name}] Two consecutive empty responses, stopping")
                    break
                page_no += page_increment
                continue

            consecutive_empty = 0
            results.append(page_df)
            total_fetched += len(page_df)
            page_no += page_increment

            if page_no > max_page:
                logger.warning(f"[{self.name}] Reached page limit ({max_page}), stopping")
                break

        if not results:
            return "검색 결과가 없습니다."

        final_df = pd.concat(results, ignore_index=True)

        # Deduplicate
        dedup_col = self._get_dedup_column()
        if dedup_col and dedup_col in final_df.columns:
            before = len(final_df)
            final_df = final_df.drop_duplicates(subset=[dedup_col], keep="first")
            after = len(final_df)
            if before != after:
                logger.info(f"[{self.name}] Deduplicated: {before} -> {after}")

        # [GJ] Apply IPC post-processing filter if specified
        ipc_filter_applied = False
        if validated_args.ipc_filter and "ipc" in final_df.columns:
            before_filter = len(final_df)
            ipc_pattern = validated_args.ipc_filter.upper()
            final_df = final_df[
                final_df["ipc"].fillna("").str.upper().str.contains(ipc_pattern, regex=False)
            ]
            after_filter = len(final_df)
            logger.info(
                f"[{self.name}] IPC filter '{validated_args.ipc_filter}': "
                f"{before_filter} -> {after_filter}"
            )
            ipc_filter_applied = True

            if final_df.empty:
                return (
                    f"IPC 필터 '{validated_args.ipc_filter}' 적용 후 검색 결과가 없습니다.\n"
                    f"총 {before_filter}건 중 해당 IPC를 포함하는 특허가 없습니다."
                )

        # Trim to max_results
        if len(final_df) > max_results:
            final_df = final_df.iloc[:max_results]

        # Generate filepath with IPC suffix if applicable
        ipc_suffix = ""
        if ipc_filter_applied and validated_args.ipc_filter:
            safe_ipc = "".join(c for c in validated_args.ipc_filter if c.isalnum())
            ipc_suffix = f"_IPC{safe_ipc}"

        filepath = generate_output_path(
            word=validated_args.word,
            output_format=validated_args.output_format,
            prefix="patent",
            country=validated_args.collection_values,
            ipc_suffix=ipc_suffix,
        )

        from mcp_kipris.kipris.tools._formatters import save_dataframe

        save_dataframe(final_df, filepath, validated_args.output_format)

        # Build result message
        country = validated_args.collection_values
        result_msg = f"성공적으로 {len(final_df)}건의 {country} 특허 정보를 저장했습니다.\n"
        if ipc_filter_applied:
            result_msg += f"IPC 필터: {validated_args.ipc_filter}\n"
        result_msg += f"저장 위치: {filepath}"

        return result_msg
