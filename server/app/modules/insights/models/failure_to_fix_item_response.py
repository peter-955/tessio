from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureStatus
from app.shared.common import WireModel


class FailureToFixItemResponse(WireModel):
    failure_id: UUID
    status: FailureStatus
    case_code: str
    case_title: str
    story_jira_key: str
    opened_at: datetime
