from uuid import UUID

from app.shared.common import WireModel


class CaseStoryResponse(WireModel):
    id: UUID
    jira_key: str
    title: str
