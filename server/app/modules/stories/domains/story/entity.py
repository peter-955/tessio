from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.stories.typing.enums import TestStatus
from app.shared.common import Entity


class Story(Entity):
    id: UUID
    project_id: UUID
    sprint_id: UUID | None
    jira_id: str
    jira_key: str
    jira_url: str
    title: str
    description: JsonValue
    jira_status: str
    jira_issue_type: str
    test_status: TestStatus
    test_status_changed_at: datetime | None
    test_status_changed_by: UUID | None
    jira_updated_at: datetime
    synced_at: datetime
    jira_missing_at: datetime | None
    created_at: datetime

    @property
    def is_missing_in_jira(self) -> bool:
        return self.jira_missing_at is not None
