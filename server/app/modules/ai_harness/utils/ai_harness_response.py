from app.modules.ai_harness.domains.ai_harness.entity import AiHarness
from app.modules.ai_harness.domains.mcp_tool.entity import McpTool
from app.modules.ai_harness.models.ai_harness_hook_response import AiHarnessHookResponse
from app.modules.ai_harness.models.ai_harness_mcp_server_response import AiHarnessMcpServerResponse
from app.modules.ai_harness.models.ai_harness_mcp_tool_response import AiHarnessMcpToolResponse
from app.modules.ai_harness.models.ai_harness_plugin_response import AiHarnessPluginResponse
from app.modules.ai_harness.models.ai_harness_response import AiHarnessResponse
from app.modules.ai_harness.models.ai_harness_server_response import AiHarnessServerResponse
from app.modules.ai_harness.models.ai_harness_slash_command_response import AiHarnessSlashCommandResponse
from app.modules.ai_harness.typing.constants import (
    COMMAND_QUOTES,
    MCP_TOOL_NAME_SEPARATOR,
    MCP_TOOL_NAME_START,
    PLUGIN_ROOT_VARIABLE,
    PLUGIN_URL_VARIABLE,
    SLASH_COMMAND_TEMPLATE,
)
from app.modules.plugin import PLUGIN_UPDATE_COMMAND, PluginCommand, PluginHook, PluginMcpServer, PluginSkill
from app.shared.permissions import PROJECT_ROLE_CAPABILITIES, Capability, ProjectRole


def read_hook_tool_name(matcher: str | None) -> str | None:
    if matcher is None or not matcher.startswith(MCP_TOOL_NAME_START):
        return matcher
    return matcher.rsplit(MCP_TOOL_NAME_SEPARATOR, 1)[-1]


def read_hook_script(command: str) -> str:
    words = command.split()
    if not words:
        return command
    return words[-1].strip(COMMAND_QUOTES).removeprefix(PLUGIN_ROOT_VARIABLE)


def list_roles_with(capability: Capability | None) -> list[ProjectRole]:
    if capability is None:
        return []
    return [role for role in ProjectRole if capability in PROJECT_ROLE_CAPABILITIES[role]]


def build_slash_command_response(plugin_name: str, entry: PluginSkill | PluginCommand) -> AiHarnessSlashCommandResponse:
    return AiHarnessSlashCommandResponse(
        name=entry.name,
        command=SLASH_COMMAND_TEMPLATE.format(plugin=plugin_name, name=entry.name),
        argument_hint=entry.argument_hint,
        description=entry.description,
    )


def build_hook_response(hook: PluginHook) -> AiHarnessHookResponse:
    return AiHarnessHookResponse(
        event=hook.event,
        tool_name=read_hook_tool_name(hook.matcher),
        script=read_hook_script(hook.command),
        timeout_seconds=hook.timeout_seconds,
    )


def build_mcp_server_response(server: PluginMcpServer, public_url: str) -> AiHarnessMcpServerResponse:
    return AiHarnessMcpServerResponse(
        name=server.name,
        transport=server.transport,
        url=server.url.replace(PLUGIN_URL_VARIABLE, public_url.rstrip("/")),
        header_names=server.header_names,
    )


def build_mcp_tool_response(tool: McpTool) -> AiHarnessMcpToolResponse:
    return AiHarnessMcpToolResponse(
        name=tool.name,
        description=tool.description,
        capability=tool.capability,
        roles=list_roles_with(tool.capability),
    )


def build_ai_harness_response(harness: AiHarness) -> AiHarnessResponse:
    plugin = harness.plugin
    return AiHarnessResponse(
        server=AiHarnessServerResponse(version=harness.server_version, build_commit=harness.build_commit),
        plugin=AiHarnessPluginResponse(
            name=plugin.name,
            version=plugin.version,
            description=plugin.description,
            update_command=PLUGIN_UPDATE_COMMAND,
        ),
        skills=[build_slash_command_response(plugin.name, skill) for skill in plugin.skills],
        commands=[build_slash_command_response(plugin.name, command) for command in plugin.commands],
        hooks=[build_hook_response(hook) for hook in plugin.hooks],
        mcp_servers=[build_mcp_server_response(server, harness.public_url) for server in plugin.mcp_servers],
        mcp_tools=[build_mcp_tool_response(tool) for tool in harness.mcp_tools],
    )
