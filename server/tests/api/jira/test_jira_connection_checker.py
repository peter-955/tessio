from httpx import AsyncClient

from app.container import Container
from app.modules.jira.infrastructure import PostgresJiraConnectionChecker
from app.modules.users import WorkspaceRole
from tests.api.jira.jira_steps import put_jira_connection
from tests.api.projects.user_steps import build_create_project_body, sign_up_as
from tests.conftest import RecordingMailer


async def test_checker_reflects_the_saved_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    checker = PostgresJiraConnectionChecker(container.database)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    is_configured_before = await checker.is_configured()
    assert (await put_jira_connection(client)).status_code == 200
    is_configured_after = await checker.is_configured()

    assert is_configured_before is False
    assert is_configured_after is True


async def test_checker_joins_an_open_transaction(container: Container) -> None:
    checker = PostgresJiraConnectionChecker(container.database)

    async with container.database.begin():
        is_configured = await checker.is_configured()

    assert is_configured is False


async def test_project_creation_waits_for_the_jira_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    container.__dict__["jira_connection_checker"] = PostgresJiraConnectionChecker(container.database)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    refused_response = await client.post("/api/projects", json=build_create_project_body())
    assert (await put_jira_connection(client)).status_code == 200
    created_response = await client.post("/api/projects", json=build_create_project_body())

    assert refused_response.status_code == 409
    assert refused_response.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert created_response.status_code == 201
