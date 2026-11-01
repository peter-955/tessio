from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.constants import ACTIVE_FAILURE_STATUSES
from app.modules.failures.typing.enums import FailureStatus
from app.shared.common import Entity


class Failure(Entity):
    id: UUID
    project_id: UUID
    story_id: UUID
    test_case_id: UUID
    opened_by_case_result_id: UUID
    latest_case_result_id: UUID
    assignee_id: UUID | None
    status: FailureStatus
    status_changed_at: datetime | None
    status_changed_by: UUID | None
    created_at: datetime

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_FAILURE_STATUSES
