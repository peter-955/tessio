from uuid import UUID

from app.shared.common import Entity


class ChatFailureDetails(Entity):
    id: UUID
    status: str
    test_case_code: str
    test_case_title: str
    story_jira_key: str
    assignee_name: str | None
