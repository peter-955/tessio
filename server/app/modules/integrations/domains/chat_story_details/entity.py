from uuid import UUID

from app.shared.common import Entity


class ChatStoryDetails(Entity):
    id: UUID
    jira_key: str
    title: str
    test_status: str
    signed_off_by_name: str | None
