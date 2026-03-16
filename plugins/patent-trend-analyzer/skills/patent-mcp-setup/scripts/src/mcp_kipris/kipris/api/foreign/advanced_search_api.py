"""
Foreign Patent Advanced Search API

해외 특허 고급 검색 API
엔드포인트: ForeignPatentAdvencedSearchService/advancedSearch
"""

import logging
from typing import Optional

import pandas as pd

from mcp_kipris.kipris.api.abs_class import ABSKiprisAPI

logger = logging.getLogger("mcp-kipris")


class ForeignPatentAdvancedSearchAPI(ABSKiprisAPI):
    """해외 특허 고급 검색 API"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://plus.kipris.or.kr/openapi/rest/ForeignPatentAdvencedSearchService/advancedSearch"
        self.KEY_STRING = "response.body.items.searchResult"

    async def async_search(
        self,
        ipc: Optional[str] = None,
        free: Optional[str] = None,
        applicant: Optional[str] = None,
        invention_name: Optional[str] = None,
        abstracts: Optional[str] = None,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
    ) -> pd.DataFrame:
        """고급 검색 API

        Args:
            ipc (str, optional): IPC 코드
            free (str, optional): 자유검색 키워드
            applicant (str, optional): 출원인명
            invention_name (str, optional): 발명의 명칭
            abstracts (str, optional): 초록
            current_page (int, optional): 페이지 번호. Defaults to 1.
            sort_field (str, optional): 정렬 기준. Defaults to "AD".
            sort_state (bool, optional): 내림차순 정렬. Defaults to True.
            collection_values (str, optional): 검색 대상 국가. Defaults to "US".

        Returns:
            pd.DataFrame: 검색 결과
        """
        params = {
            "api_url": self.api_url,
            "api_key_field": "accessKey",
            "currentPage": str(current_page),
            "sortField": str(sort_field),
            "sortState": "true" if sort_state else "false",
            "collectionValues": str(collection_values),
        }

        # 선택적 검색 파라미터 추가
        if ipc:
            params["ipc"] = ipc
        if free:
            params["free"] = free
        if applicant:
            params["applicant"] = applicant
        if invention_name:
            params["inventionName"] = invention_name
        if abstracts:
            params["abstracts"] = abstracts

        logger.info(f"Advanced search: ipc={ipc}, free={free}, country={collection_values}, page={current_page}")

        response = await self.async_call(**params)
        df = self.parse_response(response)
        return df

    def sync_search(
        self,
        ipc: Optional[str] = None,
        free: Optional[str] = None,
        applicant: Optional[str] = None,
        invention_name: Optional[str] = None,
        abstracts: Optional[str] = None,
        current_page: int = 1,
        sort_field: str = "AD",
        sort_state: bool = True,
        collection_values: str = "US",
    ) -> pd.DataFrame:
        """고급 검색 API (동기)"""
        params = {
            "api_url": self.api_url,
            "api_key_field": "accessKey",
            "currentPage": str(current_page),
            "sortField": str(sort_field),
            "sortState": "true" if sort_state else "false",
            "collectionValues": str(collection_values),
        }

        if ipc:
            params["ipc"] = ipc
        if free:
            params["free"] = free
        if applicant:
            params["applicant"] = applicant
        if invention_name:
            params["inventionName"] = invention_name
        if abstracts:
            params["abstracts"] = abstracts

        logger.info(f"Advanced search: ipc={ipc}, free={free}, country={collection_values}, page={current_page}")

        response = self.sync_call(**params)
        df = self.parse_response(response)
        return df
