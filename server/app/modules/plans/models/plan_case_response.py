from uuid import UUID

from app.modules.failures import FailureStatus
from app.modules.plans.models.plan_latest_result_response import PlanLatestResultResponse
from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.shared.common import WireModel


class PlanCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    priority: TestCasePriority
    is_needing_review: bool
    story_id: UUID
    story_jira_key: str
    story_title: str
    latest_result: PlanLatestResultResponse | None
    active_failure_id: UUID | None
    active_failure_status: FailureStatus | None
