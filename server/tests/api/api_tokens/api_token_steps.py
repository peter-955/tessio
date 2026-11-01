from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient
from sqlalchemy import delete, insert, update

from app.container import Container
from app.modules.api_tokens import ApiToken
from app.modules.api_tokens.utils.api_token_secret import generate_api_token, hash_api_token
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.shared.permissions import ProjectRole


@dataclass(frozen=True)
class SeededProject:
    id: UUID
    key: str


async def seed_project(container: Container, is_archived: bool = False) -> SeededProject:
    project = SeededProject(id=uuid7(), key=f"P{uuid4().hex[:8].upper()}")
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(ProjectTable).values(
                id=project.id,
                key=project.key,
                name=f"Project {project.key}",
                jira_project_key=project.key,
                jira_board_id=1,
                allowed_file_types=["text/csv"],
                archived_at=now if is_archived else None,
                created_at=now,
            )
        )
    return project


async def archive_project(container: Container, project: SeededProject) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(archived_at=datetime.now(UTC))
        )


async def add_member(container: Container, project: SeededProject, user_id: UUID, role: ProjectRole) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(ProjectMemberTable).values(
                id=uuid7(), project_id=project.id, user_id=user_id, role=role, created_at=datetime.now(UTC)
            )
        )


async def change_member_role(container: Container, project: SeededProject, user_id: UUID, role: ProjectRole) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectMemberTable)
            .where(ProjectMemberTable.project_id == project.id, ProjectMemberTable.user_id == user_id)
            .values(role=role)
        )


async def remove_member(container: Container, project: SeededProject, user_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            delete(ProjectMemberTable).where(
                ProjectMemberTable.project_id == project.id, ProjectMemberTable.user_id == user_id
            )
        )


async def create_token(client: AsyncClient, project_key: str, expires_in_days: int = 30) -> str:
    response = await client.post(
        "/api/me/api-tokens",
        json={"name": "Claude Code", "projectKey": project_key, "expiresInDays": expires_in_days},
    )
    assert response.status_code == 201, response.text
    token: str = response.json()["token"]
    return token


async def insert_token(
    container: Container,
    user_id: UUID,
    project_id: UUID,
    expires_at: datetime,
    revoked_at: datetime | None = None,
) -> str:
    token, prefix = generate_api_token()
    async with container.database.begin():
        await container.api_token_repository.save(
            ApiToken(
                id=uuid7(),
                user_id=user_id,
                project_id=project_id,
                name="Inserted token",
                prefix=prefix,
                token_hash=hash_api_token(token),
                expires_at=expires_at,
                last_used_at=None,
                revoked_at=revoked_at,
                created_at=datetime.now(UTC),
            )
        )
    return token


async def find_token(container: Container, token: str) -> ApiToken:
    async with container.database.begin():
        api_token = await container.api_token_repository.find_by_token_hash(hash_api_token(token))
    assert api_token is not None
    return api_token


async def save_token(container: Container, api_token: ApiToken) -> None:
    async with container.database.begin():
        await container.api_token_repository.save(api_token)
