from collections.abc import AsyncIterator

import pytest

from app.container import Container
from tests.api.runs.runs_test_container import RunsTestContainer
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


@pytest.fixture
async def container(
    database_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    runs_container = RunsTestContainer(
        build_test_settings(database_url), recording_mailer, recording_live_event_publisher
    )
    yield runs_container
    await runs_container.close()


@pytest.fixture
def runs_container(container: Container) -> RunsTestContainer:
    assert isinstance(container, RunsTestContainer)
    return container
