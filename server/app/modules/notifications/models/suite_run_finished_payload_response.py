from typing import Literal
from uuid import UUID

from app.modules.notifications.typing.enums import NotificationKind, RunOutcome
from app.shared.common import WireModel


class SuiteRunFinishedPayloadResponse(WireModel):
    kind: Literal[NotificationKind.SUITE_RUN_FINISHED]
    run_id: UUID
    test_suite_id: UUID
    test_suite_name: str
    outcome: RunOutcome
    passed_count: int
    failed_count: int
    blocked_count: int
