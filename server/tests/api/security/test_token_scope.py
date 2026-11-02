from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import read_tool_error_code
from tests.api.security.route_access import RouteAccess
from tests.api.security.route_catalog import SECURED_ROUTES
from tests.api.security.security_steps import MCP_PATH, describe, read_code, send
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool

TOKEN_ALLOWED_ROUTES = {
    ("GET", "/api/projects/{project_key}/runs"),
    ("GET", "/api/projects/{project_key}/runs/{run_id}"),
    ("GET", "/api/projects/{project_key}/runs/{run_id}/log"),
    ("POST", "/api/projects/{project_key}/runs/import"),
    ("GET", "/api/projects/{project_key}/failures"),
    ("GET", "/api/projects/{project_key}/failures/{failure_id}"),
    ("GET", "/api/projects/{project_key}/test-cases"),
    ("GET", "/api/projects/{project_key}/test-cases/{case_code}"),
    ("GET", "/api/projects/{project_key}/test-cases/{case_code}/versions"),
}
REFUSED_CODES = {"NOT_SIGNED_IN", "INVALID_API_TOKEN", "PERMISSION_DENIED", "TOKEN_SCOPE_NOT_ALLOWED"}


async def create_scoped_token(client: AsyncClient, project_key: str, scope: str) -> str:
    response = await client.post(
        "/api/me/api-tokens", json={"name": f"{scope} token", "projectKey": project_key, "scope": scope}
    )
    assert response.status_code == 201, response.text
    assert response.json()["apiToken"]["scope"] == scope
    token: str = response.json()["token"]
    return token


async def sign_up_token_owner(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> tuple[str, str]:
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)
    api_token = await create_scoped_token(client, project.key, "api")
    mcp_token = await create_scoped_token(client, project.key, "mcp")
    client.cookies.clear()
    return api_token, mcp_token


def test_the_catalog_marks_exactly_the_run_import_and_the_run_failure_and_case_reads() -> None:
    assert {route.key for route in SECURED_ROUTES if route.token_allowed} == TOKEN_ALLOWED_ROUTES
    assert all(
        route.access is RouteAccess.PROJECT_READ or route.method == "POST"
        for route in SECURED_ROUTES
        if route.token_allowed
    )


async def test_an_api_token_is_accepted_only_on_token_allowed_routes(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    api_token, _ = await sign_up_token_owner(client, container, recording_mailer, project)
    headers = {"authorization": f"Bearer {api_token}"}
    mismatches: list[str] = []

    for route in SECURED_ROUTES:
        if route.access is RouteAccess.PUBLIC or route.path == MCP_PATH:
            continue
        response = await send(client, route, project.key, headers)
        if route.token_allowed:
            if read_code(response) in REFUSED_CODES or response.status_code >= 500:
                mismatches.append(describe(route, response))
        elif response.status_code != 403 or read_code(response) != "TOKEN_SCOPE_NOT_ALLOWED":
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_an_mcp_token_is_still_refused_on_every_rest_route_that_needs_a_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    _, mcp_token = await sign_up_token_owner(client, container, recording_mailer, project)
    headers = {"authorization": f"Bearer {mcp_token}"}
    mismatches: list[str] = []

    for route in SECURED_ROUTES:
        if route.access in {RouteAccess.PUBLIC, RouteAccess.API_TOKEN}:
            continue
        response = await send(client, route, project.key, headers)
        if response.status_code != 401 or read_code(response) != "NOT_SIGNED_IN":
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_an_api_token_cannot_call_mcp_tools(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    api_token, _ = await sign_up_token_owner(client, container, recording_mailer, project)

    response = await call_tool(client, api_token, "get_open_gaps", {"story_key": "X-1"})

    assert read_tool_error_code(response) == "TOKEN_SCOPE_NOT_ALLOWED"


async def test_an_api_token_reads_only_its_own_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    await add_member(container, other_project, admin.user_id, ProjectRole.ADMIN)
    use_session(client, admin.session_token)
    api_token = await create_scoped_token(client, project.key, "api")
    client.cookies.clear()
    headers = {"authorization": f"Bearer {api_token}"}

    own = await client.get(f"/api/projects/{project.key}/runs", headers=headers)
    other = await client.get(f"/api/projects/{other_project.key}/runs", headers=headers)

    assert own.status_code == 200, own.text
    assert other.status_code == 404
    assert read_code(other) == "NOT_FOUND"


async def test_a_revoked_api_token_is_refused_as_invalid(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)
    api_token = await create_scoped_token(client, project.key, "api")
    token_id = (await client.get("/api/me/api-tokens")).json()[0]["id"]
    assert (await client.delete(f"/api/me/api-tokens/{token_id}")).status_code == 204
    client.cookies.clear()
    headers = {"authorization": f"Bearer {api_token}"}

    allowed = await client.get(f"/api/projects/{project.key}/runs", headers=headers)
    session_route = await client.get(f"/api/projects/{project.key}/labels", headers=headers)

    assert read_code(allowed) == "INVALID_API_TOKEN"
    assert read_code(session_route) == "NOT_SIGNED_IN"


async def test_a_token_is_an_mcp_token_unless_asked_otherwise(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)

    created = await client.post("/api/me/api-tokens", json={"name": "Claude Code", "projectKey": project.key})
    listed = await client.get("/api/me/api-tokens")
    wrong_scope = await client.post(
        "/api/me/api-tokens", json={"name": "Bad", "projectKey": project.key, "scope": "admin"}
    )

    assert created.json()["apiToken"]["scope"] == "mcp"
    assert listed.json()[0]["scope"] == "mcp"
    assert wrong_scope.status_code == 422
