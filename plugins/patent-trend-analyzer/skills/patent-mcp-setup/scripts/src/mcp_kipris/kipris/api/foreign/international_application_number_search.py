# [Original] Foreign patent international application number search API
# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = getLogger("mcp-kipris")


class ForeignPatentInternationalApplicationNumberSearchAPI(ABSKiprisAPI):
    """Foreign patent search by international application number."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/ForeignPatentAdvancedSearchService/internationalApplicationNumberSearch"
        self.KEY_STRING = "response.body.items.searchResult"

    def _build_params(
        self,
        international_application_number: str,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
        **kwargs,
    ) -> dict:
        """[GJ] Build API parameters for international application number search."""
        logger.info(f"international_application_number: {international_application_number}")
        return dict(
            international_application_number=international_application_number,
            current_page=str(current_page),
            sort_field=str(sort_field),
            sort_state="true" if sort_state else "false",
            collection_values=str(collection_values),
        )

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
