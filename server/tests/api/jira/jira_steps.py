from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import insert

from app.container import Container
from app.modules.jira.infrastructure import JiraConnectionTable
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.shared.permissions import ProjectRole

JIRA_SITE_URL = "https://team.atlassian.net"
JIRA_ACCOUNT_EMAIL = "jira-bot@example.com"
JIRA_API_TOKEN = "jira-api-token"


async def put_jira_connection(
    client: AsyncClient,
    site_url: str = JIRA_SITE_URL,
    account_email: str = JIRA_ACCOUNT_EMAIL,
    api_token: str | None = JIRA_API_TOKEN,
) -> Response:
    body: dict[str, str] = {"siteUrl": site_url, "accountEmail": account_email}
    if api_token is not None:
        body["apiToken"] = api_token
    return await client.put("/api/workspace/jira", json=body)


async def find_jira_connection_row(container: Container) -> JiraConnectionTable | None:
    async with container.database.begin():
        return await container.database.get_current_session().get(JiraConnectionTable, 1)


def generate_jira_project_key() -> str:
    return "J" + uuid4().hex[:8].upper()


async def seed_linked_project(container: Container, jira_project_key: str, is_archived: bool = False) -> UUID:
    project_id = uuid7()
    project_key = "P" + uuid4().hex[:8].upper()
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(ProjectTable).values(
                id=project_id,
                key=project_key,
                name=f"Project {project_key}",
                jira_project_key=jira_project_key,
                jira_board_id=1,
                allowed_file_types=["image/png"],
                archived_at=now if is_archived else None,
                created_at=now,
            )
        )
    return project_id


async def add_project_member(container: Container, project_id: UUID, user_id: UUID, role: ProjectRole) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(ProjectMemberTable).values(
                id=uuid7(), project_id=project_id, user_id=user_id, role=role, created_at=datetime.now(UTC)
            )
        )
