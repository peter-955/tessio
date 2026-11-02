from app.modules.suites.domains.test_suite.entity import TestSuite
from app.shared.events import LiveEvent, LiveEventType


def build_suite_changed_event(suite: TestSuite) -> LiveEvent:
    return LiveEvent(type=LiveEventType.SUITE_CHANGED, project_id=suite.project_id, ids={"suiteId": str(suite.id)})
