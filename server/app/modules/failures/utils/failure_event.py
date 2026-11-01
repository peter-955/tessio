from app.modules.failures.domains.failure.entity import Failure
from app.shared.events import LiveEvent, LiveEventType


def build_failure_changed_event(failure: Failure) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.FAILURE_CHANGED,
        project_id=failure.project_id,
        ids={"failureId": str(failure.id), "storyId": str(failure.story_id), "testCaseId": str(failure.test_case_id)},
    )
