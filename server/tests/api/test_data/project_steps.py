from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient
from sqlalchemy import insert, update

from app.container import Container
from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import sign_up_as
from tests.api.test_data.in_memory_object_storage import InMemoryObjectStorage
from tests.conftest import RecordingMailer


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
                allowed_file_types=["text/plain", "application/json"],
                archived_at=now if is_archived else None,
                created_at=now,
            )
        )
    return project


async def add_member(container: Container, project: SeededProject, user_id: UUID, role: ProjectRole) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(ProjectMemberTable).values(
                id=uuid7(), project_id=project.id, user_id=user_id, role=role, created_at=datetime.now(UTC)
            )
        )


async def sign_up_member(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole | None,
    workspace_role: WorkspaceRole = WorkspaceRole.MEMBER,
) -> UUID:
    account = await sign_up_as(client, container, recording_mailer, workspace_role)
    if role is not None:
        await add_member(container, project, account.user_id, role)
    return account.user_id


async def seed_import_file(
    container: Container,
    object_storage: InMemoryObjectStorage,
    project: SeededProject,
    uploaded_by: UUID,
    file_name: str,
    content: bytes,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    size: int | None = None,
    kind: StoredFileKind = StoredFileKind.IMPORT,
) -> UUID:
    file_id = uuid7()
    object_key = f"projects/{project.id}/{kind.value}/{file_id}/{file_name}"
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(StoredFileTable).values(
                id=file_id,
                project_id=project.id,
                kind=kind,
                object_key=object_key,
                file_name=file_name,
                content_type="text/plain",
                size=(len(content) if size is None else size) if status is StoredFileStatus.UPLOADED else None,
                sha256=None,
                status=status,
                uploaded_by=uploaded_by,
                created_at=datetime.now(UTC),
            )
        )
    if status is StoredFileStatus.UPLOADED:
        object_storage.put(object_key, content)
    return file_id


async def archive_project(container: Container, project: SeededProject) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(archived_at=datetime.now(UTC))
        )
