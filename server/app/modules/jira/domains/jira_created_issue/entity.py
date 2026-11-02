from app.shared.common import Entity


class JiraCreatedIssue(Entity):
    id: str
    key: str
    url: str
