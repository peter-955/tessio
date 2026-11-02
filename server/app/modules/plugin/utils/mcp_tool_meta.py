from app.modules.plugin.typing.constants import MCP_TOOL_CAPABILITY_META_KEY
from app.shared.permissions import Capability


def build_mcp_tool_meta(capability: Capability) -> dict[str, str]:
    return {MCP_TOOL_CAPABILITY_META_KEY: capability.value}


def read_mcp_tool_capability(meta: dict[str, object] | None) -> Capability | None:
    value = (meta or {}).get(MCP_TOOL_CAPABILITY_META_KEY)
    return Capability(value) if isinstance(value, str) and value in Capability else None
