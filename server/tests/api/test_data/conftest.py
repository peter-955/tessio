from collections.abc import AsyncIterator
from functools import cached_property

import pytest

from app.config import Settings
from app.container import Container
from app.shared.storage import ObjectStorage
from tests.api.test_data.in_memory_object_storage import InMemoryObjectStorage
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


class DataTestContainer(TestContainer):
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
    data_container = DataTestContainer(
        build_test_settings(database_url), recording_mailer, recording_live_event_publisher
    )
    yield data_container
    await data_container.close()


@pytest.fixture
def data_container(container: Container) -> DataTestContainer:
    assert isinstance(container, DataTestContainer)
    return container
