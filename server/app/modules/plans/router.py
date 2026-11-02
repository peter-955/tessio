from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.plans.dependencies import (
    get_close_plan,
    get_create_plan,
    get_get_plan,
    get_list_plans,
    get_set_plan_items,
    get_sign_off_plan,
    get_update_plan,
)
from app.modules.plans.domains.plan_item.entity import PlanItem
from app.modules.plans.domains.plan_patch.entity import PlanPatch
from app.modules.plans.models.create_plan_request import CreatePlanRequest
from app.modules.plans.models.plan_detail_response import PlanDetailResponse
from app.modules.plans.models.plan_summary_response import PlanSummaryResponse
from app.modules.plans.models.set_plan_items_request import SetPlanItemsRequest
from app.modules.plans.models.update_plan_request import UpdatePlanRequest
from app.modules.plans.typing.enums import PlanStatus
from app.modules.plans.usecases.close_plan import ClosePlanUseCase
from app.modules.plans.usecases.create_plan import CreatePlanUseCase
from app.modules.plans.usecases.get_plan import GetPlanUseCase
from app.modules.plans.usecases.list_plans import ListPlansUseCase
from app.modules.plans.usecases.set_plan_items import SetPlanItemsUseCase
from app.modules.plans.usecases.sign_off_plan import SignOffPlanUseCase
from app.modules.plans.usecases.update_plan import UpdatePlanUseCase
from app.modules.plans.utils.plan_responses import build_plan_detail_response, build_plan_summary_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

plans_router = APIRouter(prefix="/api", tags=["plans"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@plans_router.get("/projects/{project_key}/plans")
async def list_plans(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListPlansUseCase, Depends(get_list_plans)],
    plan_status: Annotated[PlanStatus | None, Query(alias="status")] = None,
) -> list[PlanSummaryResponse]:
    summaries = await use_case.execute(actor, project_key, plan_status)
    return [build_plan_summary_response(summary) for summary in summaries]


@plans_router.post("/projects/{project_key}/plans", status_code=status.HTTP_201_CREATED)
async def create_plan(
    project_key: str,
    body: CreatePlanRequest,
    actor: SignedInActor,
    use_case: Annotated[CreatePlanUseCase, Depends(get_create_plan)],
) -> PlanDetailResponse:
    detail = await use_case.execute(
        actor, project_key, body.name, body.description, body.target_date, body.environment_id
    )
    return build_plan_detail_response(detail)


@plans_router.get("/projects/{project_key}/plans/{plan_id}")
async def get_plan(
    project_key: str,
    plan_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[GetPlanUseCase, Depends(get_get_plan)],
) -> PlanDetailResponse:
    return build_plan_detail_response(await use_case.execute(actor, project_key, plan_id))


@plans_router.patch("/projects/{project_key}/plans/{plan_id}")
async def update_plan(
    project_key: str,
    plan_id: UUID,
    body: UpdatePlanRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdatePlanUseCase, Depends(get_update_plan)],
) -> PlanDetailResponse:
    patch = PlanPatch(
        name=body.name,
        description=body.description,
        is_changing_description="description" in body.model_fields_set,
        target_date=body.target_date,
        is_changing_target_date="target_date" in body.model_fields_set,
        environment_id=body.environment_id,
        is_changing_environment="environment_id" in body.model_fields_set,
    )
    return build_plan_detail_response(await use_case.execute(actor, project_key, plan_id, patch))


@plans_router.put("/projects/{project_key}/plans/{plan_id}/items")
async def set_plan_items(
    project_key: str,
    plan_id: UUID,
    body: SetPlanItemsRequest,
    actor: SignedInActor,
    use_case: Annotated[SetPlanItemsUseCase, Depends(get_set_plan_items)],
) -> PlanDetailResponse:
    items = [PlanItem(test_suite_id=item.suite_id, story_id=item.story_id) for item in body.items]
    return build_plan_detail_response(await use_case.execute(actor, project_key, plan_id, items))


@plans_router.post("/projects/{project_key}/plans/{plan_id}/sign-off")
async def sign_off_plan(
    project_key: str,
    plan_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[SignOffPlanUseCase, Depends(get_sign_off_plan)],
) -> PlanDetailResponse:
    return build_plan_detail_response(await use_case.execute(actor, project_key, plan_id))


@plans_router.post("/projects/{project_key}/plans/{plan_id}/close")
async def close_plan(
    project_key: str,
    plan_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ClosePlanUseCase, Depends(get_close_plan)],
) -> PlanDetailResponse:
    return build_plan_detail_response(await use_case.execute(actor, project_key, plan_id))
