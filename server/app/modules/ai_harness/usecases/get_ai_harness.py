from app.modules.ai_harness.domains.ai_harness.entity import AiHarness
from app.modules.ai_harness.ports import McpToolCatalog
from app.modules.plugin import PluginBundle


class GetAiHarnessUseCase:
    def __init__(
        self,
        plugin_bundle: PluginBundle,
        mcp_tool_catalog: McpToolCatalog,
        server_version: str,
        build_commit: str | None,
        public_url: str,
    ) -> None:
        self._plugin_bundle = plugin_bundle
        self._mcp_tool_catalog = mcp_tool_catalog
        self._server_version = server_version
        self._build_commit = build_commit
        self._public_url = public_url

    async def execute(self) -> AiHarness:
        return AiHarness(
            server_version=self._server_version,
            build_commit=self._build_commit,
            public_url=self._public_url,
            plugin=self._plugin_bundle,
            mcp_tools=sorted(await self._mcp_tool_catalog.list_tools(), key=lambda tool: tool.name),
        )
