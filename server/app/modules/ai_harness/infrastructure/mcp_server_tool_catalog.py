from mcp.server.mcpserver import MCPServer

from app.modules.ai_harness.domains.mcp_tool.entity import McpTool
from app.modules.ai_harness.ports import McpToolCatalog
from app.modules.plugin import read_mcp_tool_capability


class McpServerToolCatalog(McpToolCatalog):
    def __init__(self, server: MCPServer) -> None:
        self._server = server

    async def list_tools(self) -> list[McpTool]:
        tools = await self._server.list_tools()
        return [
            McpTool(name=tool.name, description=tool.description or "", capability=read_mcp_tool_capability(tool.meta))
            for tool in tools
        ]
