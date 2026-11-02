from uuid import UUID

from app.modules.runs.typing.enums import SkipReason
from app.shared.common import WireModel


class SkippedRunCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    story_jira_key: str
    reason: SkipReason
