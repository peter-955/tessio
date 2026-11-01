from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import seed_story
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.runs.run_steps import read_tool_error_code, sign_up_runner
from tests.api.security.route_access import RouteAccess
from tests.api.security.route_catalog import list_routes
from tests.api.security.security_steps import describe, read_code, send
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool


async def test_a_workspace_member_outside_the_project_sees_nothing(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    outsider = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, outsider.session_token)
    mismatches: list[str] = []

    for route in list_routes(RouteAccess.PROJECT_READ, RouteAccess.PROJECT_WRITE):
        response = await send(client, route, project.key)
        if response.status_code != 404 or read_code(response) != "NOT_FOUND":
            mismatches.append(describe(route, response))

    assert mismatches == []


async def test_a_token_for_one_project_cannot_read_a_story_of_another(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    first_project = await seed_project(container)
    second_project = await seed_project(container)
    second_story = await seed_story(container, second_project)
    runner = await sign_up_runner(client, container, recording_mailer, first_project, ProjectRole.QC)

    response = await call_tool(client, runner.token, "get_story_context", {"story_key": second_story.jira_key})

    assert read_tool_error_code(response) == "NOT_FOUND"
