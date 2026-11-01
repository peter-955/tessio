from datetime import datetime

from pydantic import JsonValue

from app.shared.common import Entity


class JiraIssue(Entity):
    id: str
    key: str
    summary: str
    description: JsonValue
    status_name: str
    issue_type_name: str
    is_subtask: bool
    updated_at: datetime
