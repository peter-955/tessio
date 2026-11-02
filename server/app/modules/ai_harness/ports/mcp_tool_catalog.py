from abc import ABC, abstractmethod

from app.modules.ai_harness.domains.mcp_tool.entity import McpTool


class McpToolCatalog(ABC):
    @abstractmethod
    async def list_tools(self) -> list[McpTool]: ...
