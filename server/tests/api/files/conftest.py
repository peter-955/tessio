from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cached_property
from uuid import UUID, uuid4, uuid7

import pytest
from sqlalchemy import insert

from app.config import Settings
from app.container import Container
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.shared.permissions import ProjectRole
from app.shared.storage import ObjectHead, ObjectStorage, SignedObjectUpload, SignedUpload
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings

SIGNED_UPLOAD_URL = "https://storage.test/tessio"


class InMemoryObjectStorage(ObjectStorage):
    def __init__(self) -> None:
        self.objects: dict[str, ObjectHead] = {}
        self.deleted_keys: list[str] = []

    def put(self, key: str, size: int, content_type: str) -> None:
        self.objects[key] = ObjectHead(size=size, content_type=content_type)

    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload:
        return SignedUpload(
            url=SIGNED_UPLOAD_URL,
            fields={"policy": "signed", "max-bytes": str(max_bytes), "content-type-prefix": content_type_prefix},
            key_prefix=key_prefix,
        )

    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload:
        return SignedObjectUpload(
            url=SIGNED_UPLOAD_URL,
            fields={
                "key": key,
                "policy": "signed",
                "max-bytes": str(max_bytes),
                "content-type-prefix": content_type_prefix,
            },
        )

    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str:
        return f"{SIGNED_UPLOAD_URL}/{key}?expires={int(lifetime.total_seconds())}&name={file_name}"

    async def head_object(self, key: str) -> ObjectHead | None:
        return self.objects.get(key)

    async def list_keys(self, prefix: str) -> list[str]:
        return sorted(key for key in self.objects if key.startswith(prefix))

    async def delete_object(self, key: str) -> None:
        self.objects.pop(key, None)
        self.deleted_keys.append(key)

    async def read_object(self, key: str) -> bytes | None:
        return None


@dataclass(frozen=True)
class SeededProject:
    id: UUID
    key: str


class FilesTestContainer(TestContainer):
    def __init__(
        self,
        settings: Settings,
        recording_mailer: RecordingMailer,
        recording_live_event_publisher: RecordingLiveEventPublisher,
    ) -> None:
        super().__init__(settings, recording_mailer, recording_live_event_publisher)
        self.in_memory_object_storage = InMemoryObjectStorage()

    @cached_property
    def object_storage(self) -> ObjectStorage:
        return self.in_memory_object_storage


@pytest.fixture
async def container(
    database_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    files_container = FilesTestContainer(
        build_test_settings(database_url), recording_mailer, recording_live_event_publisher
    )
    yield files_container
    await files_container.close()


@pytest.fixture
def files_container(container: Container) -> FilesTestContainer:
    assert isinstance(container, FilesTestContainer)
    return container


async def seed_project(
    files_container: FilesTestContainer, allowed_file_types: list[str], is_archived: bool = False
) -> SeededProject:
    project = SeededProject(id=uuid7(), key=f"P{uuid4().hex[:8].upper()}")
    now = datetime.now(UTC)
    async with files_container.database.begin():
        await files_container.database.get_current_session().execute(
            insert(ProjectTable).values(
                id=project.id,
                key=project.key,
                name=f"Project {project.key}",
                jira_project_key=project.key,
                jira_board_id=1,
                allowed_file_types=allowed_file_types,
                archived_at=now if is_archived else None,
                created_at=now,
            )
        )
    return project


async def add_project_member(
    files_container: FilesTestContainer, project: SeededProject, user_id: UUID, role: ProjectRole
) -> None:
    async with files_container.database.begin():
        await files_container.database.get_current_session().execute(
            insert(ProjectMemberTable).values(
                id=uuid7(), project_id=project.id, user_id=user_id, role=role, created_at=datetime.now(UTC)
            )
        )
