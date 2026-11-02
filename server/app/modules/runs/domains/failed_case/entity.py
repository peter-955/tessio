from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class FailedCase(Entity):
    test_case_id: UUID
    code: str
    title: str
    status: ResultStatus
    story_jira_key: str | None = None
