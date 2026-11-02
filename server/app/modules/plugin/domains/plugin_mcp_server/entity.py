from app.shared.common import Entity


class PluginMcpServer(Entity):
    name: str
    transport: str
    url: str
    header_names: list[str]
