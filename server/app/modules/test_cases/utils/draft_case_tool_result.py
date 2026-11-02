import json
from collections.abc import Sequence

from mcp_types import CallToolResult, TextContent

from app.modules.test_cases.domains.case_import_preview_item.entity import CaseImportPreviewItem
from app.modules.test_cases.domains.case_import_result.entity import CaseImportResult


def has_issue(item: CaseImportPreviewItem) -> bool:
    return item.problem is not None or item.is_duplicate or bool(item.unknown_criterion_codes)


def build_checked_draft_cases_tool_result(items: Sequence[CaseImportPreviewItem]) -> CallToolResult:
    content = {
        "case_count": len(items),
        "creatable_count": sum(1 for item in items if item.problem is None),
        "issues": [
            {
                "index": item.index,
                "source": item.location,
                "problem": item.problem,
                "is_duplicate": item.is_duplicate,
                "unknown_criterion_codes": item.unknown_criterion_codes,
            }
            for item in items
            if has_issue(item)
        ],
    }
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])


def build_created_draft_cases_tool_result(result: CaseImportResult) -> CallToolResult:
    content = {"codes": [created.code for created in result.created]}
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])
