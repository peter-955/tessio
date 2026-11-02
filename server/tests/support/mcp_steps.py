import json
from pathlib import Path

from httpx import AsyncClient, Response

PLUGIN_MANIFEST = Path(__file__).resolve().parents[3] / "claude" / ".claude-plugin" / "plugin.json"
CURRENT_PLUGIN_VERSION: str = json.loads(PLUGIN_MANIFEST.read_text())["version"]
MCP_HEADERS = {
    "accept": "application/json, text/event-stream",
    "content-type": "application/json",
    "x-tessio-plugin-version": CURRENT_PLUGIN_VERSION,
}


async def call_tool(
    client: AsyncClient,
    token: str | None,
    name: str,
    arguments: dict[str, object],
    plugin_version: str | None = CURRENT_PLUGIN_VERSION,
) -> Response:
    headers = {key: value for key, value in MCP_HEADERS.items() if key != "x-tessio-plugin-version"}
    if plugin_version is not None:
        headers["x-tessio-plugin-version"] = plugin_version
    if token is not None:
        headers["authorization"] = f"Bearer {token}"
    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    return await client.post("/mcp", headers=headers, content=json.dumps(request))


def read_tool_json(response: Response) -> dict[str, object]:
    result = response.json()["result"]
    assert result.get("isError") is not True, result
    content: dict[str, object] = json.loads(result["content"][0]["text"])
    return content
