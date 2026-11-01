from httpx import AsyncClient

from app.container import Container
from tests.api.runs.run_steps import read_tool_error_code
from tests.api.security.route_access import RouteAccess
from tests.api.security.route_catalog import SECURED_ROUTES
from tests.api.security.security_steps import MCP_PATH, describe, read_code, send
from tests.api.test_data.project_steps import seed_project
from tests.support.mcp_steps import call_tool

CREDENTIAL_ERROR_CODES = {"NOT_SIGNED_IN", "INVALID_API_TOKEN", "PERMISSION_DENIED"}
EXPECTED_CODE_BY_ACCESS = {
    RouteAccess.SESSION: "NOT_SIGNED_IN",
    RouteAccess.WORKSPACE: "NOT_SIGNED_IN",
    RouteAccess.PROJECT_READ: "NOT_SIGNED_IN",
    RouteAccess.PROJECT_WRITE: "NOT_SIGNED_IN",
    RouteAccess.API_TOKEN: "INVALID_API_TOKEN",
}


async def test_every_non_public_route_needs_credentials(client: AsyncClient, container: Container) -> None:
    project = await seed_project(container)
    mismatches: list[str] = []

    for route in SECURED_ROUTES:
        if route.access is RouteAccess.PUBLIC:
            continue
        if route.path == MCP_PATH:
            tool_code = read_tool_error_code(await call_tool(client, None, "get_open_gaps", {"story_key": "X-1"}))
            if tool_code != "INVALID_API_TOKEN":
                mismatches.append(f"POST /mcp -> {tool_code}")
            continue
        response = await send(client, route, project.key)
        if response.status_code != 401 or read_code(response) != EXPECTED_CODE_BY_ACCESS[route.access]:
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_public_routes_answer_without_credentials(client: AsyncClient, container: Container) -> None:
    project = await seed_project(container)
    mismatches: list[str] = []

    for route in SECURED_ROUTES:
        if route.access is not RouteAccess.PUBLIC:
            continue
        response = await send(client, route, project.key)
        if read_code(response) in CREDENTIAL_ERROR_CODES or response.status_code >= 500:
            mismatches.append(describe(route, response))

    assert mismatches == []
