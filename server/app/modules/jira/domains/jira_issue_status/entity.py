from app.shared.common import Entity


class JiraIssueStatus(Entity):
    key: str
    status_name: str
    is_done: bool
