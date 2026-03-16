# [GJ] Patent search planner - optimizes search strategy before API calls
# Reduces redundant API calls by planning IPC x keyword combinations
# Domain-agnostic: works for any patent research topic

import logging
import re
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler

logger = logging.getLogger("mcp-kipris")


class SearchPlannerArgs(BaseModel):
    topic: str = Field(
        ...,
        description="Research topic or domain to search (e.g., 'edge AI inference', 'battery electrolyte')",
    )
    target_countries: str = Field(
        "US,KR",
        description="Comma-separated country codes to search (US,EP,WO,JP,CN,KR)",
    )
    max_api_calls: int = Field(
        20,
        description="Maximum number of API calls budget (default: 20)",
    )
    focus_categories: str = Field(
        "",
        description="Optional: comma-separated focus categories to narrow search (free-text, e.g., 'battery,cathode')",
    )
    ipc_prefix: str = Field(
        "",
        description="Optional: IPC code prefix to target (e.g., 'H01M 10/' for batteries). Empty = no IPC restriction.",
    )
    language: str = Field(
        "en",
        description="Primary search language (en, ko, ja)",
    )


def _extract_keywords_from_topic(topic: str) -> list[str]:
    """Extract search keywords from a topic string using basic NLP.

    Splits on whitespace and punctuation, removes stopwords, returns unique tokens.
    """
    stopwords = {
        "a", "an", "the", "of", "for", "in", "on", "and", "or", "with",
        "to", "from", "by", "at", "is", "are", "was", "were", "be", "been",
        "that", "this", "it", "its", "as", "but", "not", "no", "if",
        "using", "based", "method", "system", "device", "apparatus",
    }
    tokens = re.split(r"[\s,;/\-]+", topic.strip())
    keywords = []
    seen = set()
    for token in tokens:
        cleaned = token.strip().lower()
        if len(cleaned) >= 2 and cleaned not in stopwords and cleaned not in seen:
            keywords.append(cleaned)
            seen.add(cleaned)
    return keywords


@register_tool
class SearchPlannerTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_search_planner")
        self.description = "Plans optimized patent search strategy before API calls. Recommends IPC x keyword combinations, estimates overlap, and suggests search order to minimize redundant calls."
        self.args_schema = SearchPlannerArgs

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Research topic or domain to search",
                    },
                    "target_countries": {
                        "type": "string",
                        "description": "Comma-separated country codes (default: US,KR)",
                        "default": "US,KR",
                    },
                    "max_api_calls": {
                        "type": "integer",
                        "description": "Maximum API call budget (default: 20)",
                        "default": 20,
                    },
                    "focus_categories": {
                        "type": "string",
                        "description": "Optional comma-separated focus categories (free-text)",
                        "default": "",
                    },
                    "ipc_prefix": {
                        "type": "string",
                        "description": "Optional IPC prefix to target (e.g., 'H01M 10/'). Empty = no restriction.",
                        "default": "",
                    },
                    "language": {
                        "type": "string",
                        "description": "Search language (en, ko, ja)",
                        "enum": ["en", "ko", "ja"],
                        "default": "en",
                    },
                },
                "required": ["topic"],
            },
        )

    async def _execute_async(self, validated_args: SearchPlannerArgs) -> str:
        topic = validated_args.topic
        countries = [c.strip().upper() for c in validated_args.target_countries.split(",")]
        max_calls = validated_args.max_api_calls
        ipc_prefix = validated_args.ipc_prefix.strip()

        # Step 1: Extract keywords from topic
        topic_keywords = _extract_keywords_from_topic(topic)

        # Step 2: Parse focus categories
        focus_cats = [
            c.strip() for c in validated_args.focus_categories.split(",") if c.strip()
        ]

        # Step 3: Build search keyword list
        # Combine topic keywords with focus categories (deduplicated)
        search_kws = list(topic_keywords)
        for cat in focus_cats:
            cat_lower = cat.lower()
            if cat_lower not in {kw.lower() for kw in search_kws}:
                search_kws.append(cat)

        # Step 4: Build search combinations
        combinations = []
        if ipc_prefix:
            # IPC-based combinations: pair IPC prefix with each keyword
            for kw in search_kws[:8]:
                combinations.append({
                    "ipc": ipc_prefix,
                    "keyword": kw,
                    "strategy": "IPC+keyword",
                    "expected_overlap": "medium",
                })
        else:
            # Keyword-only combinations: pair keywords together for broader search
            for kw in search_kws[:10]:
                combinations.append({
                    "ipc": "",
                    "keyword": kw,
                    "strategy": "keyword-only",
                    "expected_overlap": "medium",
                })

        # Step 5: Estimate overlaps
        for i, combo_a in enumerate(combinations):
            for j, combo_b in enumerate(combinations):
                if i >= j:
                    continue
                # Same IPC prefix with different keyword -> high overlap
                if combo_a["ipc"] and combo_a["ipc"] == combo_b["ipc"]:
                    combo_a["expected_overlap"] = "high"
                    combo_b["expected_overlap"] = "high"
                # Substring overlap between keywords -> medium-high
                elif (
                    combo_a["keyword"].lower() in combo_b["keyword"].lower()
                    or combo_b["keyword"].lower() in combo_a["keyword"].lower()
                ):
                    combo_a["expected_overlap"] = "medium-high"
                    combo_b["expected_overlap"] = "medium-high"

        # Step 6: Prioritize unique entries first
        seen_kws = set()
        prioritized = []
        remaining = []
        for combo in combinations:
            if combo["keyword"].lower() not in seen_kws:
                prioritized.append(combo)
                seen_kws.add(combo["keyword"].lower())
            else:
                remaining.append(combo)

        all_combos = prioritized + remaining

        # Budget per country
        calls_per_country = max_calls // max(len(countries), 1)
        planned_combos = all_combos[:calls_per_country]

        # Step 7: Country priority (infrastructure-level, not domain-specific)
        country_weights = {"US": 5, "KR": 4, "EP": 3, "WO": 3, "CN": 2, "JP": 2}
        country_priority = []
        for c in sorted(countries, key=lambda x: country_weights.get(x, 1), reverse=True):
            country_priority.append({
                "country": c,
                "priority": country_weights.get(c, 1),
                "api_type": "korean" if c == "KR" else "foreign",
                "planned_calls": len(planned_combos),
            })

        # Step 8: Build result report
        total_planned = len(planned_combos) * len(countries)
        estimated_unique = int(total_planned * 0.77)  # ~23% overlap expected

        lines = []
        lines.append("# Patent Search Plan")
        lines.append(f"\n## Topic: {topic}")
        lines.append(f"- Target countries: {', '.join(countries)}")
        lines.append(f"- API call budget: {max_calls}")
        lines.append(f"- Planned API calls: {total_planned}")
        lines.append(f"- Estimated unique results: ~{estimated_unique} (23% overlap expected)")

        if ipc_prefix:
            lines.append(f"- IPC prefix: {ipc_prefix}")
        if focus_cats:
            lines.append(f"- Focus categories: {', '.join(focus_cats)}")

        lines.append(f"\n## Extracted Search Keywords ({len(search_kws)})")
        lines.append(f"- {', '.join(search_kws)}")

        lines.append("\n## Recommended Search Combinations")
        lines.append("| # | IPC Code | Keyword | Strategy | Expected Overlap |")
        lines.append("|---|----------|---------|----------|-----------------|")
        for i, combo in enumerate(planned_combos, 1):
            ipc_display = f"`{combo['ipc']}`" if combo["ipc"] else "(none)"
            lines.append(
                f"| {i} | {ipc_display} | {combo['keyword']} | "
                f"{combo['strategy']} | {combo['expected_overlap']} |"
            )

        lines.append("\n## Country Priority")
        lines.append("| Country | Priority | API Type | Planned Calls |")
        lines.append("|---------|----------|----------|---------------|")
        for cp in country_priority:
            lines.append(
                f"| {cp['country']} | {cp['priority']}/5 | {cp['api_type']} | {cp['planned_calls']} |"
            )

        lines.append("\n## Optimization Notes")
        lines.append("- Deduplication by applicationNumber will be applied post-collection")
        if ipc_prefix:
            lines.append(f"- IPC post-filter ({ipc_prefix}) will be applied to foreign results")
        lines.append("- Use patent_keyword_optimizer to refine keywords before searching")
        lines.append("- Use patent_result_deduplicator after collection to merge and filter results")

        if total_planned > max_calls:
            lines.append(
                f"\n**WARNING**: Planned calls ({total_planned}) exceed budget ({max_calls}). "
                "Consider reducing countries or narrowing focus."
            )

        return "\n".join(lines)
