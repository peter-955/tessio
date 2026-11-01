import pytest

from tests.api.runs.recording_case_result_recorded_handler import RecordingCaseResultRecordedHandler
from tests.api.runs.runs_test_container import RunsTestContainer


@pytest.fixture
def recording_case_result_recorded_handler(runs_container: RunsTestContainer) -> RecordingCaseResultRecordedHandler:
    return runs_container.recording_case_result_recorded_handler
