from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4, uuid7

import pytest
from sqlalchemy import insert, select

from app.modules.files import (
    DeleteOrphanFilesJobHandler,
    DeleteOrphanFilesUseCase,
    StoredFile,
    StoredFileKind,
    StoredFileStatus,
)
from app.modules.files.infrastructure import PostgresStoredFileRepository, StoredFileTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.users import UserStatus, WorkspaceRole
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database
from app.shared.storage import ObjectHead, ObjectStorage, SignedObjectUpload, SignedUpload

OLD_AGE = timedelta(days=2)
RECENT_AGE = timedelta(hours=1)


class LocalObjectStorage(ObjectStorage):
    def __init__(self) -> None:
        self.objects: dict[str, ObjectHead] = {}

    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload:
        return SignedUpload(url="https://storage.test/tessio", fields={}, key_prefix=key_prefix)

    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload:
        return SignedObjectUpload(url="https://storage.test/tessio", fields={"key": key})

    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str:
        return f"https://storage.test/tessio/{key}"

    async def head_object(self, key: str) -> ObjectHead | None:
        return self.objects.get(key)

    async def list_keys(self, prefix: str) -> list[str]:
        return [key for key in self.objects if key.startswith(prefix)]

    async def delete_object(self, key: str) -> None:
        self.objects.pop(key, None)

    async def read_object(self, key: str) -> bytes | None:
        return None


@pytest.fixture
async def database(database_url: str) -> AsyncIterator[Database]:
    connected_database = Database(database_url)
    yield connected_database
    await connected_database.close()


async def insert_user(database: Database) -> UUID:
    user_id = uuid7()
    async with database.begin():
        await database.get_current_session().execute(
            insert(UserTable).values(
                id=user_id,
                email=f"orphans-{uuid4().hex[:8]}@tessio.test",
                name="Orphan Owner",
                workspace_role=WorkspaceRole.MEMBER,
                status=UserStatus.ACTIVE,
                created_at=datetime.now(UTC),
            )
        )
    return user_id


async def insert_project(database: Database) -> UUID:
    project_id = uuid7()
    project_key = f"O{uuid4().hex[:8].upper()}"
    async with database.begin():
        await database.get_current_session().execute(
            insert(ProjectTable).values(
                id=project_id,
                key=project_key,
                name="Orphans",
                jira_project_key=project_key,
                jira_board_id=1,
                created_at=datetime.now(UTC),
            )
        )
    return project_id


async def insert_file(
    database: Database,
    storage: LocalObjectStorage,
    uploaded_by: UUID,
    project_id: UUID,
    kind: StoredFileKind,
    status: StoredFileStatus,
    age: timedelta,
) -> StoredFile:
    file_id = uuid7()
    stored_file = StoredFile(
        id=file_id,
        project_id=project_id,
        kind=kind,
        object_key=f"projects/{project_id}/{kind}/{file_id}/file.bin",
        file_name="file.bin",
        content_type="application/octet-stream",
        size=None,
        sha256=None,
        status=status,
        uploaded_by=uploaded_by,
        created_at=datetime.now(UTC) - age,
    )
    async with database.begin():
        await PostgresStoredFileRepository(database).save(stored_file)
    storage.objects[stored_file.object_key] = ObjectHead(size=10, content_type="application/octet-stream")
    return stored_file


async def read_statuses(database: Database, stored_files: list[StoredFile]) -> dict[UUID, StoredFileStatus]:
    async with database.begin():
        rows = await database.get_current_session().execute(
            select(StoredFileTable.id, StoredFileTable.status).where(
                StoredFileTable.id.in_([stored_file.id for stored_file in stored_files])
            )
        )
        return dict(rows.all())


async def test_orphan_job_cleans_old_pending_files_and_keeps_the_rest(database: Database) -> None:
    storage = LocalObjectStorage()
    user_id = await insert_user(database)
    project_id = await insert_project(database)
    old_test_file = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.TEST_FILE, StoredFileStatus.PENDING, OLD_AGE
    )
    old_screenshot = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.SCREENSHOT, StoredFileStatus.PENDING, OLD_AGE
    )
    recent_pending = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.EVIDENCE, StoredFileStatus.PENDING, RECENT_AGE
    )
    old_missing = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.SCREENSHOT, StoredFileStatus.MISSING, OLD_AGE
    )
    old_uploaded = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.IMPORT, StoredFileStatus.UPLOADED, OLD_AGE
    )
    handler = DeleteOrphanFilesJobHandler(
        DeleteOrphanFilesUseCase(database, PostgresStoredFileRepository(database), storage)
    )

    await handler.handle({})

    statuses = await read_statuses(database, [old_test_file, old_screenshot, recent_pending, old_missing, old_uploaded])
    assert statuses == {
        old_screenshot.id: StoredFileStatus.MISSING,
        recent_pending.id: StoredFileStatus.PENDING,
        old_missing.id: StoredFileStatus.MISSING,
        old_uploaded.id: StoredFileStatus.UPLOADED,
    }
    assert old_test_file.object_key not in storage.objects
    assert {old_screenshot.object_key, recent_pending.object_key, old_uploaded.object_key} <= storage.objects.keys()


async def test_orphan_job_works_through_every_batch(database: Database, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.modules.files.usecases.delete_orphan_files.ORPHAN_BATCH_SIZE", 2)
    storage = LocalObjectStorage()
    user_id = await insert_user(database)
    project_id = await insert_project(database)
    old_files = [
        await insert_file(
            database, storage, user_id, project_id, StoredFileKind.TEST_FILE, StoredFileStatus.PENDING, OLD_AGE
        )
        for _ in range(5)
    ]
    object_without_file = await insert_file(
        database, storage, user_id, project_id, StoredFileKind.EVIDENCE, StoredFileStatus.PENDING, OLD_AGE
    )
    storage.objects.pop(object_without_file.object_key)

    await DeleteOrphanFilesUseCase(database, PostgresStoredFileRepository(database), storage).execute(datetime.now(UTC))

    assert await read_statuses(database, [*old_files, object_without_file]) == {}
    assert not any(stored_file.object_key in storage.objects for stored_file in old_files)
