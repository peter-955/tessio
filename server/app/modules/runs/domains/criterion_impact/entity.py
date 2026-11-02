from uuid import UUID

from app.modules.runs.typing.enums import CriterionStatus
from app.shared.common import Entity


class CriterionImpact(Entity):
    criterion_id: UUID
    code: str
    text: str
    status: CriterionStatus
    run_case_codes: list[str]
    failed_case_codes: list[str]
    story_jira_key: str | None = None
