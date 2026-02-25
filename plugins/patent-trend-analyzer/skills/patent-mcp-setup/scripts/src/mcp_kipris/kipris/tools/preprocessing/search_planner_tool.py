# [GJ] Patent search planner - optimizes search strategy before API calls
# Reduces redundant API calls by planning IPC × keyword combinations

import logging
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools.preprocessing._keyword_db import (
    PROCESSING_LAYER_KEYWORDS,
    MODEL_SCALE_KEYWORDS,
    FUNCTION_KEYWORDS,
    SEARCH_IPC_CODES,
    SEARCH_KEYWORDS,
    IPC_MAPPINGS,
    get_keywords_for_category,
    find_keyword_overlaps,
)

logger = logging.getLogger("mcp-kipris")


class SearchPlannerArgs(BaseModel):
    topic: str = Field(..., description="Research topic or domain to search (e.g., 'edge AI inference', 'on-device learning')")
    target_countries: str = Field(
        "US,KR",
        description="Comma-separated country codes to search (US,EP,WO,JP,CN,KR)"
    )
    max_api_calls: int = Field(
        20,
        description="Maximum number of API calls budget (default: 20)"
    )
    focus_layer: str = Field(
        "",
        description="Optional: focus on specific processing layer (OnSensor, OnDevice, or empty for all)"
    )
    focus_function: str = Field(
        "",
        description="Optional: focus on specific function (Adaptive_Learning, Inference, Training, or empty for all)"
    )
    language: str = Field(
        "en",
        description="Primary search language (en, ko, ja)"
    )


@register_tool
class SearchPlannerTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_search_planner")
        self.description = "Plans optimized patent search strategy before API calls. Recommends IPC × keyword combinations, estimates overlap, and suggests search order to minimize redundant calls."
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
                        "description": "연구 주제 또는 검색 도메인 (예: 'edge AI inference', '온디바이스 학습')"
                    },
                    "target_countries": {
                        "type": "string",
                        "description": "검색 대상 국가 코드 (쉼표 구분, 기본값: US,KR)",
                        "default": "US,KR"
                    },
                    "max_api_calls": {
                        "type": "integer",
                        "description": "최대 API 호출 예산 (기본값: 20)",
                        "default": 20
                    },
                    "focus_layer": {
                        "type": "string",
                        "description": "특정 처리 계층 집중 (OnSensor, OnDevice, 또는 빈 값)",
                        "default": ""
                    },
                    "focus_function": {
                        "type": "string",
                        "description": "특정 기능 집중 (Adaptive_Learning, Inference, Training, 또는 빈 값)",
                        "default": ""
                    },
                    "language": {
                        "type": "string",
                        "description": "검색 언어 (en, ko, ja)",
                        "enum": ["en", "ko", "ja"],
                        "default": "en"
                    },
                },
                "required": ["topic"],
            },
        )

    async def _execute_async(self, validated_args: SearchPlannerArgs) -> str:
        topic = validated_args.topic.lower()
        lang = validated_args.language
        countries = [c.strip().upper() for c in validated_args.target_countries.split(",")]
        max_calls = validated_args.max_api_calls

        # Step 1: Identify relevant keywords from topic
        relevant_layer_keywords = []
        relevant_function_keywords = []
        relevant_scale_keywords = []

        # Match topic against keyword categories
        layer_matches = {}
        for category in ["OnSensor", "OnDevice", "Cloud"]:
            if validated_args.focus_layer and validated_args.focus_layer != category:
                continue
            keywords = get_keywords_for_category(PROCESSING_LAYER_KEYWORDS, category, lang)
            matches = [kw for kw in keywords if kw.lower() in topic or topic in kw.lower()]
            if matches:
                layer_matches[category] = matches
                relevant_layer_keywords.extend(matches)

        function_matches = {}
        for category in ["Adaptive_Learning", "Inference", "Training"]:
            if validated_args.focus_function and validated_args.focus_function != category:
                continue
            keywords = get_keywords_for_category(FUNCTION_KEYWORDS, category, lang)
            matches = [kw for kw in keywords if kw.lower() in topic or topic in kw.lower()]
            if matches:
                function_matches[category] = matches
                relevant_function_keywords.extend(matches)

        # Step 2: Select IPC codes based on topic relevance
        relevant_ipcs = []
        for ipc_code, category in IPC_MAPPINGS["processing_layer"].items():
            if validated_args.focus_layer and validated_args.focus_layer != category:
                continue
            if not validated_args.focus_layer or validated_args.focus_layer == category:
                relevant_ipcs.append((ipc_code, f"Layer:{category}"))

        for ipc_code, category in IPC_MAPPINGS["function"].items():
            if validated_args.focus_function and validated_args.focus_function != category:
                continue
            if not validated_args.focus_function or validated_args.focus_function == category:
                relevant_ipcs.append((ipc_code, f"Function:{category}"))

        # If no specific matches, use default search IPCs
        if not relevant_ipcs:
            relevant_ipcs = [(ipc, "default") for ipc in SEARCH_IPC_CODES]

        # Step 3: Select search keywords
        search_kws = SEARCH_KEYWORDS.get(lang, SEARCH_KEYWORDS["en"])
        if relevant_layer_keywords:
            # Prioritize matched keywords
            search_kws = list(set(relevant_layer_keywords[:4] + search_kws[:3]))

        # Step 4: Build search combinations (IPC × keyword)
        combinations = []
        for ipc, ipc_label in relevant_ipcs[:6]:  # Limit IPC codes
            for kw in search_kws[:5]:  # Limit keywords per IPC
                combinations.append({
                    "ipc": ipc,
                    "keyword": kw,
                    "ipc_category": ipc_label,
                    "expected_overlap": "medium",  # Default
                })

        # Step 5: Estimate overlaps between combinations
        # Same IPC + similar keywords = high overlap
        for i, combo_a in enumerate(combinations):
            for j, combo_b in enumerate(combinations):
                if i >= j:
                    continue
                if combo_a["ipc"] == combo_b["ipc"]:
                    # Same IPC, different keyword → medium-high overlap
                    combo_a["expected_overlap"] = "high"
                    combo_b["expected_overlap"] = "high"

        # Step 6: Prioritize and trim to budget
        # Priority: unique IPC+keyword combos first
        seen_ipcs = set()
        prioritized = []
        remaining = []
        for combo in combinations:
            if combo["ipc"] not in seen_ipcs:
                prioritized.append(combo)
                seen_ipcs.add(combo["ipc"])
            else:
                remaining.append(combo)

        all_combos = prioritized + remaining

        # Budget per country
        calls_per_country = max_calls // len(countries)
        planned_combos = all_combos[:calls_per_country]

        # Step 7: Country priority
        country_priority = []
        country_weights = {"US": 5, "KR": 4, "EP": 3, "WO": 3, "CN": 2, "JP": 2}
        for c in sorted(countries, key=lambda x: country_weights.get(x, 1), reverse=True):
            country_priority.append({
                "country": c,
                "priority": country_weights.get(c, 1),
                "api_type": "korean" if c == "KR" else "foreign",
                "planned_calls": len(planned_combos),
            })

        # Step 8: Build result report
        total_planned = len(planned_combos) * len(countries)
        estimated_unique = int(total_planned * 0.77)  # 23% overlap based on historical data

        lines = []
        lines.append("# Patent Search Plan")
        lines.append(f"\n## Topic: {validated_args.topic}")
        lines.append(f"- Target countries: {', '.join(countries)}")
        lines.append(f"- API call budget: {max_calls}")
        lines.append(f"- Planned API calls: {total_planned}")
        lines.append(f"- Estimated unique results: ~{estimated_unique} (23% overlap expected)")

        if validated_args.focus_layer:
            lines.append(f"- Focus layer: {validated_args.focus_layer}")
        if validated_args.focus_function:
            lines.append(f"- Focus function: {validated_args.focus_function}")

        lines.append("\n## Matched Categories")
        if layer_matches:
            for cat, kws in layer_matches.items():
                lines.append(f"- Processing Layer **{cat}**: matched [{', '.join(kws[:5])}]")
        if function_matches:
            for cat, kws in function_matches.items():
                lines.append(f"- Function **{cat}**: matched [{', '.join(kws[:5])}]")

        lines.append("\n## Recommended Search Combinations")
        lines.append(f"| # | IPC Code | Keyword | Category | Expected Overlap |")
        lines.append(f"|---|----------|---------|----------|-----------------|")
        for i, combo in enumerate(planned_combos, 1):
            lines.append(
                f"| {i} | `{combo['ipc']}` | {combo['keyword']} | "
                f"{combo['ipc_category']} | {combo['expected_overlap']} |"
            )

        lines.append("\n## Country Priority")
        lines.append("| Country | Priority | API Type | Planned Calls |")
        lines.append("|---------|----------|----------|---------------|")
        for cp in country_priority:
            lines.append(
                f"| {cp['country']} | {cp['priority']}/5 | {cp['api_type']} | {cp['planned_calls']} |"
            )

        lines.append("\n## Optimization Notes")
        lines.append(f"- Deduplication by applicationNumber will be applied post-collection")
        lines.append(f"- IPC post-filter (G06N 3/) will be applied to foreign results")
        lines.append(f"- Domain exclusion (LLM/Medical/Security) applied after classification")

        if total_planned > max_calls:
            lines.append(f"\n**WARNING**: Planned calls ({total_planned}) exceed budget ({max_calls}). Consider reducing countries or narrowing focus.")

        return "\n".join(lines)
