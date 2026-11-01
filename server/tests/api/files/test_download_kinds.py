from datetime import UTC, datetime
from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient
from sqlalchemy import insert

from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.files.conftest import FilesTestContainer, SeededProject, add_project_member, seed_project
from tests.api.projects.user_steps import sign_up_as
from tests.conftest import RecordingMailer


async def seed_stored_file(
    files_container: FilesTestContainer, project: SeededProject, uploaded_by: UUID, kind: StoredFileKind
) -> UUID:
    file_id = uuid7()
    async with files_container.database.begin():
        await files_container.database.get_current_session().execute(
            insert(StoredFileTable).values(
                id=file_id,
                project_id=project.id,
                kind=kind,
                object_key=f"projects/{project.id}/{kind.value}/{file_id}/file.txt",
                file_name="file.txt",
                content_type="text/plain",
                size=12,
                sha256=None,
                status=StoredFileStatus.UPLOADED,
                uploaded_by=uploaded_by,
                created_at=datetime.now(UTC),
            )
        )
    return file_id


@pytest.mark.parametrize("kind", [StoredFileKind.IMPORT, StoredFileKind.AVATAR])
async def test_import_and_avatar_files_are_never_served_by_the_project_route(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer, kind: StoredFileKind
) -> None:
    project = await seed_project(files_container, ["text/plain"])
    uploader = await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    await add_project_member(files_container, project, uploader.user_id, ProjectRole.QC)
    file_id = await seed_stored_file(files_container, project, uploader.user_id, kind)
    viewer = await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    await add_project_member(files_container, project, viewer.user_id, ProjectRole.VIEWER)

    response = await client.get(f"/api/projects/{project.key}/files/{file_id}")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.parametrize(
    "kind", [StoredFileKind.SCREENSHOT, StoredFileKind.TEST_FILE, StoredFileKind.EVIDENCE, StoredFileKind.REPORT]
)
async def test_run_and_case_files_are_served_to_a_viewer(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer, kind: StoredFileKind
) -> None:
    project = await seed_project(files_container, ["text/plain"])
    viewer = await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    await add_project_member(files_container, project, viewer.user_id, ProjectRole.VIEWER)
    file_id = await seed_stored_file(files_container, project, viewer.user_id, kind)

    response = await client.get(f"/api/projects/{project.key}/files/{file_id}")

    assert response.status_code == 200
