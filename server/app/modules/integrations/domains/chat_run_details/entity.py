from uuid import UUID

from app.shared.common import Entity


class ChatRunDetails(Entity):
    id: UUID
    status: str
    executor: str
    environment_name: str
    started_by_name: str
    story_jira_key: str | None
    story_title: str | None
    suite_name: str | None
    passed_count: int | None
    failed_count: int | None
    blocked_count: int | None
    skipped_count: int | None
