"""[GJ] Generic keyword utility functions for patent preprocessing tools.

Domain-agnostic helpers for taxonomy validation, keyword classification,
IPC mapping, and domain exclusion. All functions accept taxonomy/mappings
as parameters -- no hardcoded domain data.
"""

from __future__ import annotations


def load_taxonomy_from_dict(data: dict) -> dict:
    """Validate and normalize a user-provided taxonomy structure.

    Expected format::

        {
            "axis_name": {
                "category": {
                    "en": ["kw1", "kw2"],
                    "ko": ["kw3"],
                }
            }
        }

    Returns the validated taxonomy (same dict) or raises ValueError.
    """
    if not isinstance(data, dict):
        raise ValueError("Taxonomy must be a dict")

    for axis, categories in data.items():
        if not isinstance(categories, dict):
            raise ValueError(f"Axis '{axis}' must map to a dict of categories")
        for category, lang_dict in categories.items():
            if not isinstance(lang_dict, dict):
                raise ValueError(
                    f"Category '{axis}.{category}' must map to a dict of language lists"
                )
            for lang, keywords in lang_dict.items():
                if not isinstance(keywords, list):
                    raise ValueError(
                        f"'{axis}.{category}.{lang}' must be a list of strings"
                    )
    return data


def get_all_keywords_flat(category_dict: dict, lang: str | None = None) -> list[str]:
    """Get all keywords from a category dict, optionally filtered by language."""
    result = []
    for _category, lang_dict in category_dict.items():
        if lang:
            result.extend(lang_dict.get(lang, []))
        else:
            for _l, keywords in lang_dict.items():
                result.extend(keywords)
    return list(set(result))


def get_keywords_for_category(
    category_dict: dict, category: str, lang: str | None = None
) -> list[str]:
    """Get keywords for a specific category, optionally filtered by language."""
    if category not in category_dict:
        return []
    lang_dict = category_dict[category]
    if lang:
        return lang_dict.get(lang, [])
    result = []
    for _l, keywords in lang_dict.items():
        result.extend(keywords)
    return result


def find_keyword_overlaps(keywords_a: list[str], keywords_b: list[str]) -> list[str]:
    """Find keywords that appear in both lists (case-insensitive)."""
    set_a = {k.lower() for k in keywords_a}
    set_b = {k.lower() for k in keywords_b}
    return sorted(set_a & set_b)


def classify_by_ipc(
    ipc_code: str, ipc_mappings: dict[str, dict[str, str]]
) -> dict[str, str]:
    """Generic IPC classifier.

    ipc_mappings format: ``{"axis_name": {"IPC_CODE": "category"}}``

    Returns dict with axis names as keys and category names (or 'Unknown') as values.
    """
    normalized = ipc_code.replace(" ", "")
    result = {axis: "Unknown" for axis in ipc_mappings}

    for axis, mapping in ipc_mappings.items():
        for code, category in sorted(mapping.items(), key=lambda x: -len(x[0])):
            if normalized.startswith(code) or normalized == code:
                result[axis] = category
                break

    return result


def classify_by_keywords(
    text: str,
    taxonomy: dict[str, dict[str, dict[str, list[str]]]],
    lang: str = "en",
) -> dict[str, str]:
    """Generic keyword classifier.

    taxonomy format: ``{"axis_name": {"category": {"en": [...], "ko": [...]}}}``

    Returns dict with axis names as keys and matched category (or 'Unknown') as values.
    """
    text_lower = text.lower()
    result = {axis: "Unknown" for axis in taxonomy}

    for axis, categories in taxonomy.items():
        for category, lang_dict in categories.items():
            keywords = lang_dict.get(lang, [])
            if any(kw.lower() in text_lower for kw in keywords):
                result[axis] = category
                break

    return result


def check_domain_exclusion(
    title: str, exclusion_keywords: dict[str, list[str]]
) -> str | None:
    """Generic domain exclusion check.

    exclusion_keywords format: ``{"domain_name": ["kw1", "kw2"]}``

    Returns domain name if excluded, None if not excluded.
    """
    title_upper = title.upper()
    for domain, keywords in exclusion_keywords.items():
        if any(kw.upper() in title_upper for kw in keywords):
            return domain
    return None
