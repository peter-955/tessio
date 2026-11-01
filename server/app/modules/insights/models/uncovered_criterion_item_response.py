from uuid import UUID

from app.shared.common import WireModel


class UncoveredCriterionItemResponse(WireModel):
    criterion_id: UUID
    code: str
    text: str
    story_jira_key: str
    story_title: str
