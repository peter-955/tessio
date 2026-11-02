from uuid import UUID

from app.shared.common import Entity


class SimilarAnswer(Entity):
    story_id: UUID
    story_jira_key: str
    question: str
    answer: str
