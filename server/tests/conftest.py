from collections.abc import AsyncIterator, Iterator
from datetime import timedelta
from functools import cached_property

import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from app.config import Settings
from app.container import Container
from app.main import create_app
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.jira import JiraClient
from app.modules.projects import JiraConnectionChecker
from app.modules.projects.infrastructure import StaticJiraConnectionChecker
from app.shared.events import LiveEventPublisher
from app.shared.mailer import EmailMessage, Mailer
from app.shared.queue import JobQueue
from app.shared.rate_limit import RateLimiter
from app.shared.storage import ObjectHead, ObjectStorage, SignedObjectUpload, SignedUpload
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.in_memory_rate_limiter import InMemoryRateLimiter
from tests.support.recording_job_queue import RecordingJobQueue
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


class RecordingMailer(Mailer):
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


class FakeObjectStorage(ObjectStorage):
    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload:
        return SignedUpload(url="https://storage.test/tessio", fields={"policy": "signed"}, key_prefix=key_prefix)

    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload:
        return SignedObjectUpload(url="https://storage.test/tessio", fields={"key": key, "policy": "signed"})

    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str:
        return f"https://storage.test/tessio/{key}"

    async def head_object(self, key: str) -> ObjectHead | None:
        return None

    async def list_keys(self, prefix: str) -> list[str]:
        return []

    async def delete_object(self, key: str) -> None:
        return None

    async def read_object(self, key: str) -> bytes | None:
        return None


BREACHED_PASSWORD = "password1234567"


class FakeBreachedPasswordChecker(BreachedPasswordChecker):
    async def is_breached(self, password: str) -> bool:
        return password == BREACHED_PASSWORD


class TestContainer(Container):
    def __init__(
        self,
        settings: Settings,
        recording_mailer: RecordingMailer,
        recording_live_event_publisher: RecordingLiveEventPublisher,
    ) -> None:
        super().__init__(settings)
        self._recording_mailer = recording_mailer
        self._recording_live_event_publisher = recording_live_event_publisher
        self.recording_job_queue = RecordingJobQueue()

    @cached_property
    def job_queue(self) -> JobQueue:
        return self.recording_job_queue

    @cached_property
    def mailer(self) -> Mailer:
        return self._recording_mailer

    @cached_property
    def live_event_publisher(self) -> LiveEventPublisher:
        return self._recording_live_event_publisher

    @cached_property
    def object_storage(self) -> ObjectStorage:
        return FakeObjectStorage()

    @cached_property
    def rate_limiter(self) -> RateLimiter:
        return InMemoryRateLimiter()

    @cached_property
    def breached_password_checker(self) -> BreachedPasswordChecker:
        return FakeBreachedPasswordChecker()

    @cached_property
    def jira_client(self) -> JiraClient:
        return FakeJiraClient()

    @cached_property
    def jira_connection_checker(self) -> JiraConnectionChecker:
        return StaticJiraConnectionChecker(is_configured=True)


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer("postgres:17.11-alpine", driver="asyncpg") as postgres:
        url = postgres.get_connection_url()
        alembic_config = Config("alembic.ini")
        alembic_config.set_main_option("sqlalchemy.url", url)
        command.upgrade(alembic_config, "head")
        yield url


@pytest.fixture(scope="session")
def redis_url() -> Iterator[str]:
    with RedisContainer("redis:8.10.3-alpine") as redis:
        yield f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}"


@pytest.fixture
def recording_mailer() -> RecordingMailer:
    return RecordingMailer()


@pytest.fixture
def recording_live_event_publisher() -> RecordingLiveEventPublisher:
    return RecordingLiveEventPublisher()


@pytest.fixture
async def container(
    database_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    settings = build_test_settings(database_url)
    test_container = TestContainer(settings, recording_mailer, recording_live_event_publisher)
    yield test_container
    await test_container.close()


@pytest.fixture
def recording_job_queue(container: Container) -> RecordingJobQueue:
    assert isinstance(container, TestContainer)
    return container.recording_job_queue


@pytest.fixture
async def client(container: Container) -> AsyncIterator[AsyncClient]:
    application = create_app(container)
    async with (
        LifespanManager(application),
        AsyncClient(transport=ASGITransport(app=application), base_url="https://testserver") as client,
    ):
        yield client
