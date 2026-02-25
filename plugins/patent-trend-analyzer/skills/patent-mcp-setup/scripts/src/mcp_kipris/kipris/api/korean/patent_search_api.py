# [Original] Korean patent advanced search API (kipo-api endpoint)
# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = getLogger("mcp-kipris")


class PatentSearchAPI(ABSKiprisAPI):
    """Korean patent advanced search (new kipo-api endpoint).

    Uses ServiceKey authentication instead of accessKey.
    Supports advanced search parameters via **kwargs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getAdvancedSearch"
        self.KEY_STRING = "response.body.items.item"
        # [GJ] kipo-api uses ServiceKey instead of accessKey
        self.api_key_field = "ServiceKey"

    def _build_params(
        self,
        word: str,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        page_no: int = 1,
        num_of_rows: int = 10,
        desc_sort: bool = False,
        sort_spec: str = "AD",
        **kwargs,
    ) -> dict:
        """[GJ] Build API parameters for advanced search.

        Args:
            word: Search keyword.
            patent: Include patents.
            utility: Include utility models.
            lastvalue: Registration status filter.
            page_no: Page number.
            num_of_rows: Results per page.
            desc_sort: Descending sort.
            sort_spec: Sort field.
            **kwargs: Advanced search params (invention_title, abst_cont,
                      claim_scope, ipc_number, application_number,
                      application_date, open_date, register_date, etc.)
        """
        logger.info(f"word: {word}")
        if kwargs:
            logger.info(f"parameters: {kwargs}")
        return dict(
            word=word,
            patent="true" if patent else "false",
            utility="true" if utility else "false",
            page_no=str(page_no),
            num_of_rows=str(num_of_rows),
            lastvalue=str(lastvalue),
            desc_sort="true" if desc_sort else "false",
            sort_spec=str(sort_spec),
            **kwargs,
        )

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
