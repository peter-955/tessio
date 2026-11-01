from uuid import UUID

from app.modules.failures.typing.enums import FailureStatus
from app.shared.common import Entity


class FailureFilter(Entity):
    statuses: frozenset[FailureStatus] = frozenset()
    assignee_id: UUID | None = None
    is_unassigned: bool = False
    story_jira_key: str | None = None
    test_case_id: UUID | None = None
