from datetime import datetime
from uuid import UUID

from app.modules.stories.typing.enums import TestStatus
from app.shared.common import WireModel


class StorySummaryResponse(WireModel):
    id: UUID
    jira_key: str
    jira_url: str
    title: str
    jira_status: str
    jira_issue_type: str
    test_status: TestStatus
    sprint_id: UUID | None
    sprint_name: str | None
    criterion_count: int
    synced_at: datetime
    jira_missing_at: datetime | None
