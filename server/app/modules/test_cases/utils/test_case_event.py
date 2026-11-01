from app.modules.test_cases.domains.test_case.entity import TestCase
from app.shared.events import LiveEvent, LiveEventType


def build_test_case_changed_event(test_case: TestCase) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.TEST_CASE_CHANGED,
        project_id=test_case.project_id,
        ids={"testCaseId": str(test_case.id), "code": test_case.code, "storyId": str(test_case.story_id)},
    )
