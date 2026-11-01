from datetime import timedelta
from functools import cached_property

from app.config import Settings
from app.modules.live_events import StreamLiveEventsUseCase
from app.shared.events import LiveEventPublisher, RedisLiveEventPublisher
from app.shared.permissions import ProjectAccessResolver
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


class LiveEventsTestContainer(TestContainer):
    def __init__(
        self,
        settings: Settings,
        recording_mailer: RecordingMailer,
        recording_live_event_publisher: RecordingLiveEventPublisher,
        project_access_resolver: ProjectAccessResolver,
    ) -> None:
        super().__init__(settings, recording_mailer, recording_live_event_publisher)
        self._static_project_access_resolver = project_access_resolver

    @cached_property
    def project_access_resolver(self) -> ProjectAccessResolver:
        return self._static_project_access_resolver

    @cached_property
    def live_event_publisher(self) -> LiveEventPublisher:
        return RedisLiveEventPublisher(self._settings.queue.redis_url)

    @cached_property
    def stream_live_events(self) -> StreamLiveEventsUseCase:
        return StreamLiveEventsUseCase(self.database, self.live_event_hub, self.project_access_resolver, timedelta(0))
