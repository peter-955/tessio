from typing import Literal
from uuid import UUID

from app.modules.notifications.typing.enums import NotificationKind, RunOutcome
from app.shared.common import WireModel


class RunFinishedPayloadResponse(WireModel):
    kind: Literal[NotificationKind.RUN_FINISHED]
    run_id: UUID
    story_id: UUID
    story_jira_key: str
    outcome: RunOutcome
    passed_count: int
    failed_count: int
    blocked_count: int
