import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url

from app.container import Container
from app.main import create_app
from tests.commands.conftest import execute_on_server
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings

MIGRATION_DATABASE_NAME = "tessio_migration_downgrade"


def build_alembic_config(database_url: str) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def migration_database_url(database_url: str) -> Iterator[str]:
    asyncio.run(execute_on_server(database_url, f'CREATE DATABASE "{MIGRATION_DATABASE_NAME}"'))
    url = make_url(database_url).set(database=MIGRATION_DATABASE_NAME).render_as_string(hide_password=False)
    command.upgrade(build_alembic_config(url), "head")
    yield url
    asyncio.run(execute_on_server(database_url, f'DROP DATABASE "{MIGRATION_DATABASE_NAME}" WITH (FORCE)'))


@pytest.fixture
def alembic_config(migration_database_url: str) -> Config:
    return build_alembic_config(migration_database_url)


@pytest.fixture
async def migration_container(
    migration_database_url: str,
    redis_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    test_container = TestContainer(
        build_test_settings(migration_database_url, redis_url), recording_mailer, recording_live_event_publisher
    )
    yield test_container
    await test_container.close()


@pytest.fixture
async def migration_client(migration_container: Container) -> AsyncIterator[AsyncClient]:
    application = create_app(migration_container)
    async with (
        LifespanManager(application),
        AsyncClient(transport=ASGITransport(app=application), base_url="https://testserver") as client,
    ):
        yield client
