from app.modules.plans.domains.test_plan.entity import TestPlan
from app.shared.events import LiveEvent, LiveEventType


def build_plan_changed_event(plan: TestPlan) -> LiveEvent:
    return LiveEvent(type=LiveEventType.PLAN_CHANGED, project_id=plan.project_id, ids={"planId": str(plan.id)})


def build_plan_signed_off_event(plan: TestPlan) -> LiveEvent:
    return LiveEvent(type=LiveEventType.PLAN_SIGNED_OFF, project_id=plan.project_id, ids={"planId": str(plan.id)})
