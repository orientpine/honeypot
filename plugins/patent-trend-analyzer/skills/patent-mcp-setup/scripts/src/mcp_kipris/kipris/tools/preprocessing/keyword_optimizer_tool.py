# [GJ] Keyword optimizer - expands, deduplicates, and classifies search keywords
# Reduces redundant searches by finding minimal covering keyword sets

import logging
from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_kipris.kipris._registry import register_tool
from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools.preprocessing._keyword_db import (
    PROCESSING_LAYER_KEYWORDS,
    MODEL_SCALE_KEYWORDS,
    FUNCTION_KEYWORDS,
    DOMAIN_EXCLUSION_KEYWORDS,
    IPC_MAPPINGS,
    get_keywords_for_category,
    find_keyword_overlaps,
    classify_by_keywords,
    check_domain_exclusion,
)

logger = logging.getLogger("mcp-kipris")


class KeywordOptimizerArgs(BaseModel):
    keywords: str = Field(..., description="Comma-separated list of search keywords to optimize")
    target_language: str = Field(
        "en",
        description="Target language for synonym expansion (en, ko, ja, or all)"
    )
    expand_synonyms: bool = Field(
        True,
        description="Whether to expand keywords with known synonyms"
    )
    detect_overlaps: bool = Field(
        True,
        description="Whether to detect overlapping/redundant keywords"
    )
    classify_keywords: bool = Field(
        True,
        description="Whether to auto-classify keywords by category"
    )
    check_exclusions: bool = Field(
        True,
        description="Whether to check if keywords match exclusion domains"
    )


@register_tool
class KeywordOptimizerTool(ToolHandler):
    def __init__(self):
        super().__init__("patent_keyword_optimizer")
        self.description = "Optimizes patent search keywords by expanding synonyms, detecting overlaps, classifying by category, and checking exclusion domains. Use before API calls to minimize redundant searches."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "검색 키워드 (쉼표 구분, 예: 'edge AI, neural accelerator, NPU')"
                    },
                    "target_language": {
                        "type": "string",
                        "description": "동의어 확장 대상 언어 (en, ko, ja, all)",
                        "enum": ["en", "ko", "ja", "all"],
                        "default": "en"
                    },
                    "expand_synonyms": {
                        "type": "boolean",
                        "description": "동의어 확장 여부 (기본값: true)",
                        "default": True
                    },
                    "detect_overlaps": {
                        "type": "boolean",
                        "description": "중복 키워드 감지 여부 (기본값: true)",
                        "default": True
                    },
                    "classify_keywords": {
                        "type": "boolean",
                        "description": "카테고리 자동 분류 여부 (기본값: true)",
                        "default": True
                    },
                    "check_exclusions": {
                        "type": "boolean",
                        "description": "제외 도메인 확인 여부 (기본값: true)",
                        "default": True
                    },
                },
                "required": ["keywords"],
            },
        )

    def _find_synonyms(self, keyword: str, target_lang: str) -> dict[str, list[str]]:
        """Find synonyms for a keyword across all category databases."""
        kw_lower = keyword.lower()
        synonyms = {}

        for db_name, db in [
            ("processing_layer", PROCESSING_LAYER_KEYWORDS),
            ("model_scale", MODEL_SCALE_KEYWORDS),
            ("function", FUNCTION_KEYWORDS),
        ]:
            for category, lang_dict in db.items():
                for lang, keywords in lang_dict.items():
                    if any(kw_lower in k.lower() or k.lower() in kw_lower for k in keywords):
                        # Found a match - collect synonyms from target language
                        if target_lang == "all":
                            for tl, tl_kws in lang_dict.items():
                                key = f"{db_name}:{category}:{tl}"
                                synonyms[key] = [k for k in tl_kws if k.lower() != kw_lower][:5]
                        else:
                            target_kws = lang_dict.get(target_lang, [])
                            if target_kws:
                                key = f"{db_name}:{category}:{target_lang}"
                                synonyms[key] = [k for k in target_kws if k.lower() != kw_lower][:5]
        return synonyms

    def _classify_keyword(self, keyword: str) -> dict[str, str]:
        """Classify a single keyword into categories."""
        return classify_by_keywords(keyword)

    async def _execute_async(self, validated_args: KeywordOptimizerArgs) -> str:
        input_keywords = [kw.strip() for kw in validated_args.keywords.split(",") if kw.strip()]
        lang = validated_args.target_language

        lines = []
        lines.append("# Keyword Optimization Report")
        lines.append(f"\n**Input keywords**: {len(input_keywords)}")
        lines.append(f"**Target language**: {lang}")

        # Step 1: Classify keywords
        if validated_args.classify_keywords:
            lines.append("\n## Keyword Classification")
            lines.append("| Keyword | Processing Layer | Model Scale | Function |")
            lines.append("|---------|-----------------|-------------|----------|")
            for kw in input_keywords:
                cls = self._classify_keyword(kw)
                lines.append(
                    f"| {kw} | {cls['processing_layer']} | "
                    f"{cls['model_scale']} | {cls['function']} |"
                )

        # Step 2: Check exclusions
        if validated_args.check_exclusions:
            excluded = []
            for kw in input_keywords:
                domain = check_domain_exclusion(kw)
                if domain:
                    excluded.append((kw, domain))

            if excluded:
                lines.append("\n## Exclusion Warnings")
                for kw, domain in excluded:
                    lines.append(f"- **{kw}** matches exclusion domain: `{domain}`")
                lines.append("\nThese keywords may retrieve patents that will be filtered out later.")
            else:
                lines.append("\n## Exclusion Check: No keywords match exclusion domains")

        # Step 3: Expand synonyms
        if validated_args.expand_synonyms:
            lines.append("\n## Synonym Expansion")
            all_expanded = set()
            for kw in input_keywords:
                synonyms = self._find_synonyms(kw, lang)
                if synonyms:
                    lines.append(f"\n### `{kw}`")
                    for source, syns in synonyms.items():
                        if syns:
                            lines.append(f"- {source}: {', '.join(syns[:5])}")
                            all_expanded.update(syns[:3])

            if all_expanded:
                new_suggestions = all_expanded - {kw.lower() for kw in input_keywords}
                if new_suggestions:
                    lines.append(f"\n**Suggested additional keywords**: {', '.join(sorted(new_suggestions)[:10])}")

        # Step 4: Detect overlaps
        if validated_args.detect_overlaps:
            lines.append("\n## Overlap Detection")
            overlaps_found = False
            for i, kw_a in enumerate(input_keywords):
                for j, kw_b in enumerate(input_keywords):
                    if i >= j:
                        continue
                    # Check substring overlap
                    if kw_a.lower() in kw_b.lower() or kw_b.lower() in kw_a.lower():
                        lines.append(f"- **Substring overlap**: `{kw_a}` ⊂ `{kw_b}`")
                        overlaps_found = True
                    else:
                        # Check if they map to the same category
                        cls_a = self._classify_keyword(kw_a)
                        cls_b = self._classify_keyword(kw_b)
                        shared = []
                        for axis in ["processing_layer", "model_scale", "function"]:
                            if cls_a[axis] != "Unknown" and cls_a[axis] == cls_b[axis]:
                                shared.append(f"{axis}={cls_a[axis]}")
                        if shared:
                            lines.append(
                                f"- **Category overlap**: `{kw_a}` & `{kw_b}` → {', '.join(shared)}"
                            )
                            overlaps_found = True

            if not overlaps_found:
                lines.append("No significant overlaps detected.")

            # Minimal covering set suggestion
            lines.append("\n## Minimal Covering Set")
            # Group by category
            category_groups = {}
            for kw in input_keywords:
                cls = self._classify_keyword(kw)
                key = f"{cls['processing_layer']}|{cls['function']}"
                if key not in category_groups:
                    category_groups[key] = []
                category_groups[key].append(kw)

            minimal_set = []
            redundant = []
            for key, kws in category_groups.items():
                # Keep the most specific keyword per group
                minimal_set.append(kws[0])
                redundant.extend(kws[1:])

            lines.append(f"- **Keep ({len(minimal_set)})**: {', '.join(minimal_set)}")
            if redundant:
                lines.append(f"- **Redundant ({len(redundant)})**: {', '.join(redundant)}")
                lines.append(f"\nUsing the minimal set saves ~{len(redundant) * len(input_keywords)}% API calls")

        # Step 5: IPC code suggestions
        lines.append("\n## Suggested IPC Codes")
        suggested_ipcs = set()
        for kw in input_keywords:
            cls = self._classify_keyword(kw)
            for axis in ["processing_layer", "function"]:
                category = cls[axis]
                if category == "Unknown":
                    continue
                axis_key = axis if axis == "function" else "processing_layer"
                for ipc, cat in IPC_MAPPINGS.get(axis_key, {}).items():
                    if cat == category:
                        suggested_ipcs.add((ipc, cat))

        if suggested_ipcs:
            for ipc, cat in sorted(suggested_ipcs):
                lines.append(f"- `{ipc}` → {cat}")
        else:
            lines.append("No specific IPC codes matched. Use broad `G06N 3/` prefix.")

        return "\n".join(lines)
