import json

from mcp_types import CallToolResult, TextContent

from app.modules.gaps.domains.raised_gaps.entity import RaisedGaps


def build_raised_gaps_tool_result(raised_gaps: RaisedGaps) -> CallToolResult:
    content = {
        "gap_ids": [str(view.gap.id) for view in raised_gaps.gaps],
        "open_gap_count": raised_gaps.open_gap_count,
        "is_ready": raised_gaps.is_ready,
    }
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])


def build_open_gaps_tool_result(open_gaps: RaisedGaps) -> CallToolResult:
    content = {
        "open_gap_count": open_gaps.open_gap_count,
        "is_ready": open_gaps.is_ready,
        "gaps": [
            {
                "id": str(view.gap.id),
                "type": view.gap.type.value,
                "severity": view.gap.severity.value,
                "target_type": view.gap.target_type.value,
                "target_ref": view.target_ref,
                "question": view.gap.question,
            }
            for view in open_gaps.gaps
        ],
    }
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])
