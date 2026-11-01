import json

from httpx import AsyncClient, Response

MCP_HEADERS = {"accept": "application/json, text/event-stream", "content-type": "application/json"}


async def call_tool(client: AsyncClient, token: str | None, name: str, arguments: dict[str, object]) -> Response:
    headers = MCP_HEADERS if token is None else {**MCP_HEADERS, "authorization": f"Bearer {token}"}
    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    return await client.post("/mcp", headers=headers, content=json.dumps(request))


def read_tool_json(response: Response) -> dict[str, object]:
    result = response.json()["result"]
    assert result.get("isError") is not True, result
    content: dict[str, object] = json.loads(result["content"][0]["text"])
    return content
