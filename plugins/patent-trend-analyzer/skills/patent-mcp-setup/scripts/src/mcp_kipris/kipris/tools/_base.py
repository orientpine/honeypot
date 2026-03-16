"""[GJ] Base classes for batch export tools.

Extracts common pagination, deduplication, and file output logic
from Korean and Foreign batch export tools.
"""

import asyncio
import logging

import pandas as pd

from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.api.abs_class import KiprisAPIError
from mcp_kipris.kipris.tools._formatters import generate_output_path, save_dataframe

logger = logging.getLogger("mcp-kipris")


class BaseBatchExportTool(ToolHandler):
    """[GJ] Base class for batch export tools.

    Handles common logic:
        - Paginated data fetching
        - Deduplication by key column
        - File output (Excel/Markdown)

    Subclasses MUST implement:
        - _get_dedup_column() -> str
        - _fetch_page(validated_args, page_no) -> pd.DataFrame
        - _get_page_increment() -> int
        - _build_result_message(df, filepath, validated_args) -> str
    """

    def _get_dedup_column(self) -> str:
        """Return column name for deduplication."""
        raise NotImplementedError

    def _get_page_increment(self) -> int:
        """Return page increment value. Korean=1, Foreign=30."""
        return 1

    def _get_max_page(self, start_page: int = 1) -> int:
        """Return safety limit for maximum page number."""
        return 1500

    async def _fetch_page(self, validated_args, page_no: int) -> pd.DataFrame:
        """Fetch a single page of results. Must be overridden."""
        raise NotImplementedError

    def _build_result_message(self, df: pd.DataFrame, filepath: str, validated_args) -> str:
        """Build success message. May be overridden for custom messages."""
        return f"성공적으로 {len(df)}건의 특허 정보를 저장했습니다.\n저장 위치: {filepath}"

    def _post_process(self, df: pd.DataFrame, validated_args) -> pd.DataFrame:
        """Override for post-processing (e.g., IPC filter). Default: no-op."""
        return df

    async def _execute_async(self, validated_args) -> str:
        """[GJ] Common pagination + dedup + save logic."""
        results = []
        page_no = getattr(validated_args, "start_page", 1)
        total_fetched = 0
        max_results = validated_args.max_results
        page_increment = self._get_page_increment()
        max_page = self._get_max_page(page_no)
        consecutive_empty = 0

        last_api_error = None

        while total_fetched < max_results:
            logger.info(f"[{self.name}] Fetching page {page_no}, total: {total_fetched}")

            try:
                page_df = await self._fetch_page(validated_args, page_no)
            except KiprisAPIError as e:
                # [GJ:fix] Handle KIPRIS API errors (e.g., unregistered key) per-page.
                # If we already have partial results, return them. Otherwise propagate.
                logger.warning(f"[{self.name}] API 에러 (page {page_no}): {e}")
                last_api_error = e
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    if results:
                        logger.info(f"[{self.name}] API 에러 발생, 수집된 {sum(len(r) for r in results)}건 반환")
                        break
                    else:
                        raise  # No results at all — propagate error to user
                page_no += page_increment
                continue

            await asyncio.sleep(0.5)

            if page_df.empty:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    logger.info(f"[{self.name}] Two consecutive empty responses, stopping")
                    break
                page_no += page_increment
                continue

            consecutive_empty = 0
            last_api_error = None
            results.append(page_df)
            total_fetched += len(page_df)
            page_no += page_increment

            if page_no > max_page:
                logger.warning(f"[{self.name}] Reached page limit ({max_page}), stopping")
                break

        if not results:
            if last_api_error:
                raise last_api_error
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

        # Post-process hook (e.g., IPC filter)
        final_df = self._post_process(final_df, validated_args)

        # Trim to max_results
        if len(final_df) > max_results:
            final_df = final_df.iloc[:max_results]

        # Save to file
        filepath = self._generate_filepath(validated_args)
        save_dataframe(final_df, filepath, validated_args.output_format)

        return self._build_result_message(final_df, filepath, validated_args)

    def _generate_filepath(self, validated_args) -> str:
        """Generate output file path. May be overridden for custom paths."""
        word = getattr(validated_args, "word", getattr(validated_args, "ipc", "export"))
        country = getattr(validated_args, "collection_values", None)
        return generate_output_path(
            word=word,
            output_format=validated_args.output_format,
            country=country,
        )

    def _format_response(self, result: str) -> str:
        """Batch tools return string messages directly."""
        return result
