from collections.abc import AsyncIterator
from functools import cached_property

import pytest

from app.config import Settings
from app.container import Container
from app.modules.stories import ActiveFailureCounter, CriteriaChangedHandler, RunningRunChecker
from app.modules.stories.infrastructure import StaticActiveFailureCounter, StaticRunningRunChecker
from tests.api.stories.recording_criteria_changed_handler import RecordingCriteriaChangedHandler
from tests.conftest import RecordingMailer, TestContainer
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher
from tests.support.test_settings import build_test_settings


class StoriesTestContainer(TestContainer):
    def __init__(
        self,
        settings: Settings,
        recording_mailer: RecordingMailer,
        recording_live_event_publisher: RecordingLiveEventPublisher,
    ) -> None:
        super().__init__(settings, recording_mailer, recording_live_event_publisher)
        self.recording_criteria_changed_handler = RecordingCriteriaChangedHandler()

    @cached_property
    def criteria_changed_handler(self) -> CriteriaChangedHandler:
        return self.recording_criteria_changed_handler

    @cached_property
    def active_failure_counter(self) -> ActiveFailureCounter:
        return StaticActiveFailureCounter(0)

    @cached_property
    def running_run_checker(self) -> RunningRunChecker:
        return StaticRunningRunChecker(False)


@pytest.fixture
async def container(
    database_url: str,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> AsyncIterator[Container]:
    stories_container = StoriesTestContainer(
        build_test_settings(database_url), recording_mailer, recording_live_event_publisher
    )
    yield stories_container
    await stories_container.close()


@pytest.fixture
def stories_container(container: Container) -> StoriesTestContainer:
    assert isinstance(container, StoriesTestContainer)
    return container


@pytest.fixture
def fake_jira_client(container: Container) -> FakeJiraClient:
    jira_client = container.jira_client
    assert isinstance(jira_client, FakeJiraClient)
    return jira_client
