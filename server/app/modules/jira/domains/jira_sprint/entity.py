from datetime import datetime

from app.modules.jira.typing.enums import JiraSprintState
from app.shared.common import Entity


class JiraSprint(Entity):
    id: int
    name: str
    state: JiraSprintState
    start_at: datetime | None
    end_at: datetime | None
    complete_at: datetime | None
