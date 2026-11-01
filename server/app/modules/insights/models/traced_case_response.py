from uuid import UUID

from app.modules.insights.models.latest_result_response import LatestResultResponse
from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.shared.common import WireModel


class TracedCaseResponse(WireModel):
    id: UUID
    code: str
    title: str
    status: TestCaseStatus
    priority: TestCasePriority
    needs_review: bool
    criterion_ids: list[UUID]
    latest_result: LatestResultResponse | None
