from mcp_types import CallToolResult, TextContent

from app.shared.common import TessioError


def build_tool_error_result(error: TessioError) -> CallToolResult:
    return CallToolResult(is_error=True, content=[TextContent(type="text", text=f"{error.code}: {error.message}")])
