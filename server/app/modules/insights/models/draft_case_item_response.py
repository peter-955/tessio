from uuid import UUID

from app.modules.test_cases import TestCaseStatus
from app.shared.common import WireModel


class DraftCaseItemResponse(WireModel):
    case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    story_jira_key: str
