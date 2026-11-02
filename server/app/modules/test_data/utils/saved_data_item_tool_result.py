import json

from mcp_types import CallToolResult, TextContent
from pydantic import JsonValue

from app.modules.test_data.domains.saved_data_item.entity import SavedDataItem


def build_saved_data_item_tool_result(saved_item: SavedDataItem) -> CallToolResult:
    content: dict[str, JsonValue] = {"action": saved_item.action.value}
    if saved_item.overridden_in:
        content["overridden_in"] = list(saved_item.overridden_in)
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content, separators=(",", ":")))])
