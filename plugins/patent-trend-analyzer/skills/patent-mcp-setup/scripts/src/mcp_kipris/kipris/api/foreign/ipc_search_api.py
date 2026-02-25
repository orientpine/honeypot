"""[Original] Foreign Patent IPC Search API

해외 특허 IPC 코드 기반 검색 API
엔드포인트: ForeignPatentAdvencedSearchService/ipcSearch (Advenced - 오타 주의)
"""

# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

import logging

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = logging.getLogger("mcp-kipris")


class ForeignPatentIPCSearchAPI(ABSKiprisAPI):
    """Foreign patent IPC classification search.

    Note: The official API endpoint has a typo: 'Advenced' instead of 'Advanced'.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Note: "Advenced" is a typo in the official API endpoint
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/ForeignPatentAdvencedSearchService/ipcSearch"
        self.KEY_STRING = "response.body.items.searchResult"

    def _build_params(
        self,
        ipc: str,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
        num_of_rows: int = 500,
        **kwargs,
    ) -> dict:
        """[GJ] Build API parameters for IPC search.

        Args:
            ipc: IPC classification code (e.g., G06N, G06F17).
            current_page: Page number.
            sort_field: Sort field.
            sort_state: Descending sort if True.
            collection_values: Country code.
            num_of_rows: Results per page (default 500).
        """
        logger.info(f"IPC search: {ipc}, country: {collection_values}, page: {current_page}, rows: {num_of_rows}")
        return dict(
            ipc=ipc,
            currentPage=str(current_page),
            sortField=str(sort_field),
            sortState="true" if sort_state else "false",
            collectionValues=str(collection_values),
            numOfRows=str(num_of_rows),
        )

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
