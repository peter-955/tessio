from app.modules.plans.domains.plan_case_progress.entity import PlanCaseProgress
from app.modules.plans.domains.plan_failure_blocker.entity import PlanFailureBlocker
from app.modules.plans.domains.plan_gap_blocker.entity import PlanGapBlocker
from app.modules.plans.domains.plan_progress_counts.entity import PlanProgressCounts
from app.shared.common import Entity


class PlanProgress(Entity):
    counts: PlanProgressCounts
    cases: list[PlanCaseProgress]
    failures: list[PlanFailureBlocker]
    gaps: list[PlanGapBlocker]
