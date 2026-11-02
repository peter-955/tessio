from collections.abc import AsyncIterator

import pytest

from app.container import Container
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


@pytest.fixture
async def container(
    database_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    test_container = TestContainer(build_test_settings(database_url), recording_mailer, recording_live_event_publisher)
    yield test_container
    await test_container.close()
