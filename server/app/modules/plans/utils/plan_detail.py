from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import PlanNotFoundError, PlanNotOpenError
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.utils.plan_progress import load_plan_progress


async def load_plan_detail(plan_view_reader: PlanViewReader, plan: TestPlan) -> PlanDetail:
    environment_names = (
        {}
        if plan.environment_id is None
        else await plan_view_reader.map_environment_names(plan.project_id, [plan.environment_id])
    )
    user_ids = {user_id for user_id in (plan.created_by, plan.signed_off_by, plan.closed_by) if user_id is not None}
    return PlanDetail(
        plan=plan,
        environment_name=None if plan.environment_id is None else environment_names.get(plan.environment_id),
        user_names=await plan_view_reader.map_user_names(user_ids),
        items=await plan_view_reader.list_item_views(plan.id),
        progress=await load_plan_progress(plan_view_reader, plan),
    )


async def lock_plan(repository: TestPlanRepository, project_id: UUID, plan_id: UUID) -> TestPlan:
    plan = await repository.find_by_id_for_update(project_id, plan_id)
    if plan is None:
        raise PlanNotFoundError
    return plan


async def lock_open_plan(repository: TestPlanRepository, project_id: UUID, plan_id: UUID) -> TestPlan:
    plan = await lock_plan(repository, project_id, plan_id)
    if not plan.is_open:
        raise PlanNotOpenError(plan.status)
    return plan
