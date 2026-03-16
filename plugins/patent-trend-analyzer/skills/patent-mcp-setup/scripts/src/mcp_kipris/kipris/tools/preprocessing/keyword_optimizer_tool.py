# [GJ] Keyword optimizer - expands, deduplicates, and checks search keywords
# Reduces redundant searches by finding minimal covering keyword sets
# Domain-agnostic: no hardcoded taxonomy or keyword databases

import logging
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler

logger = logging.getLogger("mcp-kipris")


class KeywordOptimizerArgs(BaseModel):
    keywords: str = Field(
        ..., description="Comma-separated list of search keywords to optimize"
    )
    target_language: str = Field(
        "en",
        description="Target language for synonym expansion (en, ko, ja, or all)",
    )
    expand_synonyms: bool = Field(
        True,
        description="Whether to suggest related keywords via substring matching",
    )
    detect_overlaps: bool = Field(
        True,
        description="Whether to detect overlapping/redundant keywords",
    )
    check_exclusions: bool = Field(
        True,
        description="Whether to check if keywords match exclusion terms",
    )
    exclusion_keywords: str = Field(
        "",
        description="Optional: comma-separated exclusion keywords (e.g., 'medical,blockchain,advertisement')",
    )


@register_tool
class KeywordOptimizerTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_keyword_optimizer")
        self.description = "Optimizes patent search keywords by suggesting related terms, detecting overlaps, and checking exclusion terms. Use before API calls to minimize redundant searches. Works for any patent domain."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "Search keywords (comma-separated, e.g., 'edge AI, neural accelerator, NPU')",
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language for synonym expansion (en, ko, ja, all)",
                        "enum": ["en", "ko", "ja", "all"],
                        "default": "en",
                    },
                    "expand_synonyms": {
                        "type": "boolean",
                        "description": "Whether to suggest related keywords (default: true)",
                        "default": True,
                    },
                    "detect_overlaps": {
                        "type": "boolean",
                        "description": "Whether to detect overlapping keywords (default: true)",
                        "default": True,
                    },
                    "check_exclusions": {
                        "type": "boolean",
                        "description": "Whether to check keywords against exclusion terms (default: true)",
                        "default": True,
                    },
                    "exclusion_keywords": {
                        "type": "string",
                        "description": "Optional comma-separated exclusion keywords",
                        "default": "",
                    },
                },
                "required": ["keywords"],
            },
        )

    async def _execute_async(self, validated_args: KeywordOptimizerArgs) -> str:
        input_keywords = [
            kw.strip() for kw in validated_args.keywords.split(",") if kw.strip()
        ]
        lang = validated_args.target_language

        exclusion_terms = [
            t.strip().upper()
            for t in validated_args.exclusion_keywords.split(",")
            if t.strip()
        ]

        lines = []
        lines.append("# Keyword Optimization Report")
        lines.append(f"\n**Input keywords**: {len(input_keywords)}")
        lines.append(f"**Target language**: {lang}")

        # Step 1: Check exclusions
        if validated_args.check_exclusions and exclusion_terms:
            excluded = []
            for kw in input_keywords:
                kw_upper = kw.upper()
                for exc in exclusion_terms:
                    if exc in kw_upper or kw_upper in exc:
                        excluded.append((kw, exc))
                        break

            if excluded:
                lines.append("\n## Exclusion Warnings")
                for kw, exc_term in excluded:
                    lines.append(
                        f"- **{kw}** matches exclusion term: `{exc_term}`"
                    )
                lines.append(
                    "\nThese keywords may retrieve patents outside your target domain."
                )
            else:
                lines.append(
                    "\n## Exclusion Check: No keywords match exclusion terms"
                )
        elif validated_args.check_exclusions:
            lines.append(
                "\n## Exclusion Check: No exclusion keywords provided (skipped)"
            )

        # Step 2: Expand synonyms via substring matching between input keywords
        if validated_args.expand_synonyms:
            lines.append("\n## Keyword Expansion Suggestions")
            has_suggestions = False

            for i, kw_a in enumerate(input_keywords):
                related = []
                for j, kw_b in enumerate(input_keywords):
                    if i == j:
                        continue
                    # Detect partial substring relationships
                    if kw_a.lower() in kw_b.lower() or kw_b.lower() in kw_a.lower():
                        related.append(kw_b)

                if related:
                    lines.append(f"- **{kw_a}** is related to: {', '.join(related)}")
                    has_suggestions = True

            if not has_suggestions:
                lines.append(
                    "No substring relationships detected between input keywords."
                )

            lines.append(
                "\n**Tip**: Consider adding alternate spellings, abbreviations, "
                "or translations of your keywords to improve search coverage."
            )

        # Step 3: Detect overlaps
        if validated_args.detect_overlaps:
            lines.append("\n## Overlap Detection")
            overlaps_found = False
            for i, kw_a in enumerate(input_keywords):
                for j, kw_b in enumerate(input_keywords):
                    if i >= j:
                        continue
                    if kw_a.lower() in kw_b.lower() or kw_b.lower() in kw_a.lower():
                        lines.append(
                            f"- **Substring overlap**: `{kw_a}` <-> `{kw_b}`"
                        )
                        overlaps_found = True

            if not overlaps_found:
                lines.append("No significant overlaps detected.")

            # Minimal covering set suggestion
            lines.append("\n## Minimal Covering Set")
            # Remove keywords that are substrings of other keywords
            minimal_set = []
            redundant = []
            for kw in input_keywords:
                is_substring = False
                for other in input_keywords:
                    if kw != other and kw.lower() in other.lower():
                        is_substring = True
                        break
                if is_substring:
                    redundant.append(kw)
                else:
                    minimal_set.append(kw)

            lines.append(f"- **Keep ({len(minimal_set)})**: {', '.join(minimal_set)}")
            if redundant:
                lines.append(
                    f"- **Potentially redundant ({len(redundant)})**: {', '.join(redundant)}"
                )
                lines.append(
                    f"\nUsing the minimal set may reduce redundant API calls."
                )

        # Step 4: IPC code suggestions (generic guidance)
        lines.append("\n## IPC Code Suggestions")
        lines.append(
            "Use KIPRIS search tools to explore relevant IPC codes for your domain:"
        )
        lines.append("- `patent_free_search` with your keywords to discover IPC codes in results")
        lines.append("- Filter results by IPC prefix using `patent_result_deduplicator`")
        lines.append(
            "- Provide the `ipc_prefix` parameter to `patent_search_planner` for targeted search"
        )

        return "\n".join(lines)
