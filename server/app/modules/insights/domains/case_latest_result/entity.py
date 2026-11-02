from uuid import UUID

from app.modules.insights.domains.latest_result.entity import LatestResult
from app.shared.common import Entity


class CaseLatestResult(Entity):
    case_id: UUID
    code: str
    story_id: UUID
    latest_result: LatestResult | None
    is_flaky: bool
    is_disagreeing: bool
    is_quarantined: bool
