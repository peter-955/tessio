from uuid import UUID

from app.modules.plans.domains.plan_item_view.entity import PlanItemView
from app.modules.plans.domains.plan_progress.entity import PlanProgress
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.shared.common import Entity


class PlanDetail(Entity):
    plan: TestPlan
    environment_name: str | None
    user_names: dict[UUID, str]
    items: list[PlanItemView]
    progress: PlanProgress
