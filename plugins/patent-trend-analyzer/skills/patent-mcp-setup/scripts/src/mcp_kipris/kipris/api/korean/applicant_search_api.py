# [Original] Korean patent applicant search API
# [GJ:refactor] Replaced sync_search/async_search duplication with _build_params pattern

from logging import getLogger

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = getLogger("mcp-kipris")


class PatentApplicantSearchAPI(ABSKiprisAPI):
    """Korean patent search by applicant name."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"
        self.KEY_STRING = "response.body.items.PatentUtilityInfo"

    def _build_params(
        self,
        applicant: str,
        docs_start: int = 1,
        docs_count: int = 10,
        patent: bool = True,
        utility: bool = True,
        lastvalue: str = "",
        sort_spec: str = "AD",
        desc_sort: bool = False,
        **kwargs,
    ) -> dict:
        """[GJ] Build API parameters for applicant search."""
        logger.info(f"applicant: {applicant}")
        return dict(
            applicant=applicant,
            docs_start=str(docs_start),
            docs_count=str(docs_count),
            patent=str(patent),
            lastvalue=str(lastvalue),
            utility=str(utility),
            sort_spec=str(sort_spec),
            desc_sort="true" if desc_sort else "false",
        )

    # [GJ] Backward-compatible aliases
    def sync_search(self, **kwargs) -> pd.DataFrame:
        return self.search(**kwargs)

    async def async_search(self, **kwargs) -> pd.DataFrame:
        return await self.async_search_unified(**kwargs)
