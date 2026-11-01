from collections.abc import AsyncIterator

import pytest

from tests.api.live_events.live_events_test_container import LiveEventsTestContainer
from tests.api.live_events.static_project_access_resolver import StaticProjectAccessResolver
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


@pytest.fixture
def project_access_resolver() -> StaticProjectAccessResolver:
    return StaticProjectAccessResolver()


@pytest.fixture
async def container(
    database_url: str,
    redis_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    project_access_resolver: StaticProjectAccessResolver,
) -> AsyncIterator[LiveEventsTestContainer]:
    test_container = LiveEventsTestContainer(
        build_test_settings(database_url, redis_url),
        recording_mailer,
        recording_live_event_publisher,
        project_access_resolver,
    )
    yield test_container
    await test_container.close()
