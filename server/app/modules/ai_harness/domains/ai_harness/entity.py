from app.modules.ai_harness.domains.mcp_tool.entity import McpTool
from app.modules.plugin import PluginBundle
from app.shared.common import Entity


class AiHarness(Entity):
    server_version: str
    build_commit: str | None
    public_url: str
    plugin: PluginBundle
    mcp_tools: list[McpTool]
