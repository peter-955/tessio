from typing import Literal
from uuid import UUID

from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class FailureAssignedPayloadResponse(WireModel):
    kind: Literal[NotificationKind.FAILURE_ASSIGNED]
    failure_id: UUID
    test_case_id: UUID
    test_case_code: str
    test_case_title: str
    story_jira_key: str
