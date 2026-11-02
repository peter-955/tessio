from datetime import datetime
from uuid import UUID

from app.modules.failures import FailureStatus
from app.shared.common import WireModel


class PlanFailureResponse(WireModel):
    failure_id: UUID
    test_case_id: UUID
    code: str
    title: str
    story_jira_key: str
    status: FailureStatus
    assignee_id: UUID | None
    assignee_name: str | None
    created_at: datetime
