# [Original] Korean patent detail (bibliography) search API
# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = getLogger("mcp-kipris")


class PatentDetailSearchAPI(ABSKiprisAPI):
    """Korean patent bibliography detail search.

    Returns detailed legal and technical information for a single patent.
    Uses ServiceKey authentication and kipo-api endpoint.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = (
            "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch"
        )
        self.KEY_STRING = "response.body.item"
        # [GJ] kipo-api uses ServiceKey
        self.api_key_field = "ServiceKey"

    def _build_params(self, application_number: str, **kwargs) -> dict:
        """[GJ] Build API parameters for detail search.

        Args:
            application_number: Patent application number.
        """
        logger.info(f"application_number: {application_number}")
        return dict(application_number=application_number)

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
