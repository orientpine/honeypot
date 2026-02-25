# [Original] Tool re-exports for backward compatibility
# [GJ:refactor] Tools now auto-register via @register_tool decorator.
# For new code, use: from mcp_kipris.kipris._registry import get_all_tools
# These imports are kept for backward compatibility with existing code.

from mcp_kipris.kipris.tools.foreign.applicant_search_tool import ForeignPatentApplicantSearchTool
from mcp_kipris.kipris.tools.foreign.application_number_search_tool import ForeignPatentApplicationNumberSearchTool
from mcp_kipris.kipris.tools.foreign.batch_export_tool import ForeignPatentBatchExportTool
from mcp_kipris.kipris.tools.foreign.free_search_tool import ForeignPatentFreeSearchTool
from mcp_kipris.kipris.tools.foreign.international_application_number_search_tool import (
    ForeignPatentInternationalApplicationNumberSearchTool,
)
from mcp_kipris.kipris.tools.foreign.international_open_number_search_tool import (
    ForeignPatentInternationalOpenNumberSearchTool,
)
from mcp_kipris.kipris.tools.foreign.ipc_batch_export_tool import ForeignPatentIPCBatchExportTool
from mcp_kipris.kipris.tools.korean.applicant_search_tool import (
    PatentApplicantSearchTool as KoreanPatentApplicantSearchTool,
)
from mcp_kipris.kipris.tools.korean.application_number_search_tool import (
    PatentApplicationNumberSearchTool as KoreanPatentApplicationNumberSearchTool,
)
from mcp_kipris.kipris.tools.korean.patent_batch_export_tool import PatentBatchExportTool as KoreanPatentBatchExportTool
from mcp_kipris.kipris.tools.korean.patent_detail_search_tool import (
    PatentDetailSearchTool as KoreanPatentDetailSearchTool,
)
from mcp_kipris.kipris.tools.korean.patent_free_search_tool import PatentFreeSearchTool as KoreanPatentFreeSearchTool
from mcp_kipris.kipris.tools.korean.patent_search_tool import PatentSearchTool as KoreanPatentSearchTool
from mcp_kipris.kipris.tools.korean.patent_summary_search_tool import (
    PatentSummarySearchTool as KoreanPatentSummarySearchTool,
)
from mcp_kipris.kipris.tools.korean.righter_search_tool import PatentRighterSearchTool as KoreanPatentRighterSearchTool

# [GJ] Preprocessing tools - search optimization pipeline
from mcp_kipris.kipris.tools.preprocessing.search_planner_tool import SearchPlannerTool
from mcp_kipris.kipris.tools.preprocessing.keyword_optimizer_tool import KeywordOptimizerTool
from mcp_kipris.kipris.tools.preprocessing.result_deduplicator_tool import ResultDeduplicatorTool

__all__ = [
    # Korean patent tools (8)
    "KoreanPatentApplicantSearchTool",
    "KoreanPatentFreeSearchTool",
    "KoreanPatentSearchTool",
    "KoreanPatentRighterSearchTool",
    "KoreanPatentApplicationNumberSearchTool",
    "KoreanPatentSummarySearchTool",
    "KoreanPatentDetailSearchTool",
    "KoreanPatentBatchExportTool",
    # Foreign patent tools (7)
    "ForeignPatentApplicantSearchTool",
    "ForeignPatentApplicationNumberSearchTool",
    "ForeignPatentBatchExportTool",
    "ForeignPatentFreeSearchTool",
    "ForeignPatentInternationalApplicationNumberSearchTool",
    "ForeignPatentInternationalOpenNumberSearchTool",
    "ForeignPatentIPCBatchExportTool",
    # Preprocessing tools (3)
    "SearchPlannerTool",
    "KeywordOptimizerTool",
    "ResultDeduplicatorTool",
]
