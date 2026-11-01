from uuid import UUID

from app.shared.common import Entity


class UncoveredCriterionItem(Entity):
    criterion_id: UUID
    code: str
    text: str
    story_jira_key: str
    story_title: str
