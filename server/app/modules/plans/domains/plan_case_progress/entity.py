from app.modules.plans.domains.plan_case.entity import PlanCase
from app.modules.plans.domains.plan_failure_blocker.entity import PlanFailureBlocker
from app.modules.plans.domains.plan_latest_result.entity import PlanLatestResult
from app.shared.common import Entity


class PlanCaseProgress(Entity):
    case: PlanCase
    latest_result: PlanLatestResult | None
    active_failure: PlanFailureBlocker | None
