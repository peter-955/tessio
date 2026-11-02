from app.modules.plugin.domains.plugin_command.entity import PluginCommand
from app.modules.plugin.domains.plugin_hook.entity import PluginHook
from app.modules.plugin.domains.plugin_mcp_server.entity import PluginMcpServer
from app.modules.plugin.domains.plugin_skill.entity import PluginSkill
from app.shared.common import Entity


class PluginBundle(Entity):
    name: str
    version: str
    description: str
    file_name: str
    sha256: str
    archive: bytes
    skills: list[PluginSkill]
    commands: list[PluginCommand]
    hooks: list[PluginHook]
    mcp_servers: list[PluginMcpServer]
