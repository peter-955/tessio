from app.modules.plugin.domains.plugin_mcp_server.entity import PluginMcpServer
from app.modules.plugin.errors import PluginManifestInvalidError
from app.modules.plugin.typing.constants import PLUGIN_DEFAULT_MCP_TRANSPORT


def build_plugin_mcp_servers(document: object) -> list[PluginMcpServer]:
    servers = document.get("mcpServers") if isinstance(document, dict) else None
    if not isinstance(servers, dict):
        raise PluginManifestInvalidError(".mcp.json has no 'mcpServers' object")
    mcp_servers: list[PluginMcpServer] = []
    for name, server in servers.items():
        if not isinstance(server, dict):
            raise PluginManifestInvalidError(f".mcp.json server '{name}' is not an object")
        headers = server.get("headers")
        mcp_servers.append(
            PluginMcpServer(
                name=str(name),
                transport=str(server.get("type", PLUGIN_DEFAULT_MCP_TRANSPORT)),
                url=str(server.get("url") or server.get("command", "")),
                header_names=[str(header) for header in headers] if isinstance(headers, dict) else [],
            )
        )
    return mcp_servers
