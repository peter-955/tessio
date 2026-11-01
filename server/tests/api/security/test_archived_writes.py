from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.projects.user_steps import use_session
from tests.api.security.route_access import RouteAccess
from tests.api.security.route_catalog import list_routes
from tests.api.security.security_steps import describe, read_code, send
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer

EXCLUDED_ROUTES = {
    ("POST", "/api/projects/{project_key}/test-data/{item_id}/reveal"): "revealing a secret is a read",
    ("POST", "/api/projects/{project_key}/archive"): "a workspace capability, refused to a workspace member",
    ("POST", "/api/projects/{project_key}/unarchive"): "a workspace capability, refused to a workspace member",
}


async def test_a_project_admin_cannot_write_to_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container, is_archived=True)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)
    mismatches: list[str] = []

    for route in list_routes(RouteAccess.PROJECT_WRITE):
        if route.key in EXCLUDED_ROUTES:
            continue
        response = await send(client, route, project.key)
        if response.status_code != 409 or read_code(response) != "PROJECT_ARCHIVED":
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_a_project_admin_still_reads_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container, is_archived=True)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)
    mismatches: list[str] = []

    for route in list_routes(RouteAccess.PROJECT_READ):
        response = await send(client, route, project.key)
        if response.status_code in {401, 403, 409} or response.status_code >= 500:
            mismatches.append(describe(route, response))

    assert mismatches == []
