from app.modules.plans.domains.plan_progress_counts.entity import PlanProgressCounts
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.shared.common import Entity


class PlanSummary(Entity):
    plan: TestPlan
    environment_name: str | None
    item_count: int
    counts: PlanProgressCounts
