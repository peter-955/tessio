import re
from uuid import uuid7

from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts
from httpx import AsyncClient, Response

from tests.api.security.secured_route import SecuredRoute

PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")
FIXED_PATH_VALUES = {"jira_key": "X-1", "case_code": "TC-1", "file_key": "key", "token": "unknown-token"}
MCP_PATH = "/mcp"
SAMPLE_UPLOAD = b'<testsuite name="smoke"><testcase name="TC-1 opens the shop"/></testsuite>'


def build_path(route: SecuredRoute, project_key: str) -> str:
    def fill(match: re.Match[str]) -> str:
        name = match.group(1)
        if name == "project_key":
            return project_key
        return FIXED_PATH_VALUES.get(name) or str(uuid7())

    return PLACEHOLDER_PATTERN.sub(fill, route.path)


async def send(
    client: AsyncClient, route: SecuredRoute, project_key: str, headers: dict[str, str] | None = None
) -> Response:
    if route.form is not None:
        return await client.request(
            route.method,
            build_path(route, project_key),
            data=route.form,
            files={"file": ("results.xml", SAMPLE_UPLOAD, "application/xml")},
            headers=headers,
        )
    return await client.request(route.method, build_path(route, project_key), json=route.body, headers=headers)


def describe(route: SecuredRoute, response: Response) -> str:
    return f"{route.method} {route.path} -> {response.status_code} {read_code(response)}"


def read_code(response: Response) -> str | None:
    try:
        body: object = response.json()
    except ValueError:
        return None
    if isinstance(body, dict):
        code = body.get("code")
        return code if isinstance(code, str) else None
    return None


def list_application_routes(application: FastAPI) -> set[tuple[str, str]]:
    route_keys: set[tuple[str, str]] = set()
    for route_context in iter_route_contexts(application.routes):
        original_route = route_context.original_route
        path = route_context.path
        if isinstance(original_route, APIRoute) and path is not None:
            route_keys.update((method, path) for method in original_route.methods or set())
        elif path == MCP_PATH:
            route_keys.add(("POST", MCP_PATH))
    return route_keys
