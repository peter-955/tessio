from app.modules.plans.models.plan_case_response import PlanCaseResponse
from app.modules.plans.models.plan_failure_response import PlanFailureResponse
from app.modules.plans.models.plan_gap_response import PlanGapResponse
from app.modules.plans.models.plan_progress_counts_response import PlanProgressCountsResponse
from app.shared.common import WireModel


class PlanProgressResponse(WireModel):
    counts: PlanProgressCountsResponse
    cases: list[PlanCaseResponse]
    failures: list[PlanFailureResponse]
    gaps: list[PlanGapResponse]
