from uuid import UUID

from app.modules.insights.domains.latest_result.entity import LatestResult
from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.shared.common import Entity


class TracedCase(Entity):
    id: UUID
    story_id: UUID
    number: int
    code: str
    title: str
    status: TestCaseStatus
    priority: TestCasePriority
    is_needing_review: bool
    created_by: UUID
    criterion_ids: frozenset[UUID]
    latest_result: LatestResult | None
