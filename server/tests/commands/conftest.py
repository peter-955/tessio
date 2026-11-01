import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.container import Container
from app.main import create_app
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings

SEED_DATABASE_NAME = "tessio_seed_e2e"


async def execute_on_server(database_url: str, statement: str) -> None:
    engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as connection:
            await connection.execute(text(statement))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def seed_database_url(database_url: str) -> Iterator[str]:
    asyncio.run(execute_on_server(database_url, f'CREATE DATABASE "{SEED_DATABASE_NAME}"'))
    url = make_url(database_url).set(database=SEED_DATABASE_NAME).render_as_string(hide_password=False)
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", url)
    command.upgrade(alembic_config, "head")
    yield url
    asyncio.run(execute_on_server(database_url, f'DROP DATABASE "{SEED_DATABASE_NAME}" WITH (FORCE)'))


@pytest.fixture
async def seed_container(
    seed_database_url: str,
    redis_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    test_container = TestContainer(
        build_test_settings(seed_database_url, redis_url), recording_mailer, recording_live_event_publisher
    )
    yield test_container
    await test_container.close()


@pytest.fixture
async def seed_client(seed_container: Container) -> AsyncIterator[AsyncClient]:
    application = create_app(seed_container)
    async with (
        LifespanManager(application),
        AsyncClient(transport=ASGITransport(app=application), base_url="https://testserver") as client,
    ):
        yield client
