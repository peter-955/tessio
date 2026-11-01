from uuid import UUID

from app.modules.test_cases import TestCaseStatus
from app.shared.common import Entity


class DraftCaseItem(Entity):
    case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    story_jira_key: str
