from app.modules.ai_harness.models.ai_harness_hook_response import AiHarnessHookResponse
from app.modules.ai_harness.models.ai_harness_mcp_server_response import AiHarnessMcpServerResponse
from app.modules.ai_harness.models.ai_harness_mcp_tool_response import AiHarnessMcpToolResponse
from app.modules.ai_harness.models.ai_harness_plugin_response import AiHarnessPluginResponse
from app.modules.ai_harness.models.ai_harness_server_response import AiHarnessServerResponse
from app.modules.ai_harness.models.ai_harness_slash_command_response import AiHarnessSlashCommandResponse
from app.shared.common import WireModel


class AiHarnessResponse(WireModel):
    server: AiHarnessServerResponse
    plugin: AiHarnessPluginResponse
    skills: list[AiHarnessSlashCommandResponse]
    commands: list[AiHarnessSlashCommandResponse]
    hooks: list[AiHarnessHookResponse]
    mcp_servers: list[AiHarnessMcpServerResponse]
    mcp_tools: list[AiHarnessMcpToolResponse]
