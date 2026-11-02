from uuid import UUID

from app.shared.common import WireModel


class SharedStepUsageResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: str
    story_jira_key: str
    version_number: int
