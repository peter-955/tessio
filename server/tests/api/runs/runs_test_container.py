from functools import cached_property

from app.config import Settings
from app.modules.runs import CaseResultRecordedHandler, CriterionImpactCalculator
from app.shared.storage import ObjectStorage
from tests.api.runs.recording_case_result_recorded_handler import RecordingCaseResultRecordedHandler
from tests.api.runs.stub_criterion_impact_calculator import StubCriterionImpactCalculator
from tests.api.test_data.in_memory_object_storage import InMemoryObjectStorage
from tests.conftest import RecordingMailer, TestContainer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


class RunsTestContainer(TestContainer):
    def __init__(
        self,
        settings: Settings,
        recording_mailer: RecordingMailer,
        recording_live_event_publisher: RecordingLiveEventPublisher,
    ) -> None:
        super().__init__(settings, recording_mailer, recording_live_event_publisher)
        self.in_memory_object_storage = InMemoryObjectStorage()
        self.recording_case_result_recorded_handler = RecordingCaseResultRecordedHandler()
        self.stub_criterion_impact_calculator = StubCriterionImpactCalculator()

    @cached_property
    def object_storage(self) -> ObjectStorage:
        return self.in_memory_object_storage

    @cached_property
    def case_result_recorded_handler(self) -> CaseResultRecordedHandler:
        return self.recording_case_result_recorded_handler

    @cached_property
    def criterion_impact_calculator(self) -> CriterionImpactCalculator:
        return self.stub_criterion_impact_calculator
