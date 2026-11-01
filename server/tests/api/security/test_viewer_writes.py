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


async def test_a_viewer_cannot_write_anything(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    viewer = await sign_up_account(client, container, recording_mailer, project, ProjectRole.VIEWER)
    use_session(client, viewer.session_token)
    mismatches: list[str] = []

    for route in list_routes(RouteAccess.PROJECT_WRITE):
        response = await send(client, route, project.key)
        if response.status_code != 403 or read_code(response) != "PERMISSION_DENIED":
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_a_viewer_can_read_everything(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    viewer = await sign_up_account(client, container, recording_mailer, project, ProjectRole.VIEWER)
    use_session(client, viewer.session_token)
    mismatches: list[str] = []

    for route in list_routes(RouteAccess.PROJECT_READ):
        response = await send(client, route, project.key)
        if response.status_code in {401, 403, 409} or response.status_code >= 500:
            mismatches.append(describe(route, response))

    assert mismatches == []
