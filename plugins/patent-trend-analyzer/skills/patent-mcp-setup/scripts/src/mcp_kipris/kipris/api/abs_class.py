# [Original] Base API class for KIPRIS API communication
# [GJ:refactor] Added template method pattern (search/async_search_unified)
#               and backward-compatible sync_search/async_search aliases

import logging
import os
import typing as t
from urllib.parse import urlencode

import pandas as pd
from dotenv import load_dotenv
from stringcase import camelcase

from mcp_kipris.kipris.api.utils import get_nested_key_value, get_response, get_response_async, mask_sensitive_data

logger = logging.getLogger("mcp-kipris")
load_dotenv()


class ABSKiprisAPI:
    """Base class for all KIPRIS API implementations.

    Subclasses MUST set:
        - api_url: The KIPRIS API endpoint URL.
        - KEY_STRING: Dot-separated path to extract results from response.

    Subclasses SHOULD override:
        - _build_params(**kwargs) -> dict: Convert search parameters to API params.
        - api_key_field: Override if API uses a different key field name.

    Args:
        **kwargs: Must include 'api_key' or KIPRIS_API_KEY env var must be set.
    """

    # [GJ] Class-level defaults for subclass configuration
    api_url: str = ""
    api_key_field: str = "accessKey"  # [GJ] Override to "ServiceKey" for kipo-api endpoints

    def __init__(self, **kwargs):
        # [Original] Response parsing configuration
        self.HEADER_KEY_STRING = "response.body.items.item"
        self.KEY_STRING = ""
        if "api_key" in kwargs:
            self.api_key = kwargs["api_key"]
        else:
            if os.getenv("KIPRIS_API_KEY"):
                self.api_key = os.getenv("KIPRIS_API_KEY")
            else:
                raise ValueError(
                    "KIPRIS_API_KEY is not set you must set KIPRIS_API_KEY in .env file or pass api_key to constructor "
                )

    def sync_call(self, api_url: str, api_key_field="accessKey", **params) -> t.Dict:
        """[Original] KIPRIS API synchronous call.

        Args:
            api_url: API endpoint URL.
            api_key_field: API key parameter name.
            **params: Query parameters.

        Returns:
            dict: Parsed XML response as dict.
        """
        try:
            params_dict = {camelcase(k): v for k, v in params.items() if v is not None and v != ""}
            params_dict[api_key_field] = self.api_key
            full_url = f"{api_url}?{urlencode(params_dict)}"
            logger.info(f"KIPRIS 요청 URL: {mask_sensitive_data(full_url)}")
            return get_response(full_url)
        except Exception as e:
            logger.error(f"KIPRIS 요청 실패: {e}")
            raise

    async def async_call(self, api_url: str, api_key_field="accessKey", **params) -> t.Dict:
        """[Original] KIPRIS API asynchronous call.

        Args:
            api_url: API endpoint URL.
            api_key_field: API key parameter name.
            **params: Query parameters.

        Returns:
            dict: Parsed XML response as dict.
        """
        try:
            params_dict = {camelcase(k): v for k, v in params.items() if v is not None and v != ""}
            params_dict[api_key_field] = self.api_key
            full_url = f"{api_url}?{urlencode(params_dict)}"
            logger.info(f"[async] KIPRIS 요청 URL: {mask_sensitive_data(full_url)}")
            return await get_response_async(full_url)
        except Exception as e:
            logger.error(f"[async] KIPRIS 요청 실패: {e}")
            raise

    def parse_response(self, response: dict) -> pd.DataFrame:
        """[Original] Parse API response dict into DataFrame.

        Args:
            response: Raw API response dict.

        Returns:
            pd.DataFrame: Parsed results. Empty DataFrame if no results.
        """
        res_dict = get_nested_key_value(response, self.KEY_STRING)
        if res_dict is None:
            logger.info("patents is None")
            message = get_nested_key_value(response, self.HEADER_KEY_STRING)
            if message:
                logger.warning(f"KIPRIS API 응답 메시지: {message}")
            return pd.DataFrame()
        if isinstance(res_dict, t.Dict):
            res_dict = [res_dict]
        return pd.DataFrame(res_dict)

    # ── [GJ] Template Method Pattern ─────────────────────────────────

    def _build_params(self, **kwargs) -> dict:
        """[GJ] Build API query parameters from search arguments.

        Subclasses override this to define their parameter transformation logic.
        The returned dict is passed as **kwargs to sync_call/async_call.

        Returns:
            dict: Parameters ready for API call.

        Raises:
            NotImplementedError: If subclass hasn't implemented this method.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement _build_params(). Return a dict of parameters for the API call."
        )

    def search(self, **kwargs) -> pd.DataFrame:
        """[GJ] Unified synchronous search using template method.

        Calls _build_params() to transform kwargs, then executes sync API call.

        Args:
            **kwargs: Search parameters (forwarded to _build_params).

        Returns:
            pd.DataFrame: Search results.
        """
        params = self._build_params(**kwargs)
        response = self.sync_call(api_url=self.api_url, api_key_field=self.api_key_field, **params)
        return self.parse_response(response)

    async def async_search_unified(self, **kwargs) -> pd.DataFrame:
        """[GJ] Unified asynchronous search using template method.

        Calls _build_params() to transform kwargs, then executes async API call.

        Args:
            **kwargs: Search parameters (forwarded to _build_params).

        Returns:
            pd.DataFrame: Search results.
        """
        params = self._build_params(**kwargs)
        response = await self.async_call(api_url=self.api_url, api_key_field=self.api_key_field, **params)
        return self.parse_response(response)
