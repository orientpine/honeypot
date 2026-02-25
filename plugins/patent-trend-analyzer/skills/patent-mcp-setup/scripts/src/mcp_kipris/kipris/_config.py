"""[GJ] Centralized configuration module for KIPRIS API.

Consolidates API key initialization that was previously duplicated
across all 15 tool files.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_api_key() -> str:
    """Get KIPRIS API key from environment variables.

    Returns:
        str: The KIPRIS API key.

    Raises:
        ValueError: If KIPRIS_API_KEY is not set.
    """
    key = os.getenv("KIPRIS_API_KEY")
    if not key:
        raise ValueError(
            "KIPRIS_API_KEY is not set. "
            "Set KIPRIS_API_KEY in .env file or as environment variable."
        )
    return key
