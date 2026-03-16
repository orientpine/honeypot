# [Original] Foreign patent free text search API
# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = getLogger("mcp-kipris")


class ForeignPatentFreeSearchAPI(ABSKiprisAPI):
    """Foreign patent free text (keyword) search.

    Note: This API uses pre-camelCased parameter names (searchWord, searchWordRange)
    which are idempotent under the base class's camelcase() conversion.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/ForeignPatentGeneralSearchService/wordSearch"
        self.KEY_STRING = "response.body.items.searchResult"

    def _build_params(
        self,
        word: str,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
        **kwargs,
    ) -> dict:
        """[GJ] Build API parameters for foreign free text search.

        Args:
            word: Search keyword.
            current_page: Page number.
            sort_field: Sort field (AD, PD, GD, OPD, etc.).
            sort_state: Descending sort if True.
            collection_values: Country code (US, EP, WO, JP, etc.).
        """
        logger.info(f"search word: {word}")
        return dict(
            searchWord=word,
            searchWordRange="1",
            currentPage=str(current_page),
            sortField=str(sort_field),
            sortState="true" if sort_state else "false",
            collectionValues=str(collection_values),
        )

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
