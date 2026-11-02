from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.modules.projects import get_signed_in_actor
from app.modules.shared_steps.dependencies import (
    get_create_shared_step,
    get_get_shared_step,
    get_list_shared_step_usage,
    get_list_shared_steps,
    get_update_shared_step,
)
from app.modules.shared_steps.domains.shared_step_changes.entity import SharedStepChanges
from app.modules.shared_steps.models.create_shared_step_request import CreateSharedStepRequest
from app.modules.shared_steps.models.shared_step_response import SharedStepResponse
from app.modules.shared_steps.models.shared_step_usage_response import SharedStepUsageResponse
from app.modules.shared_steps.models.update_shared_step_request import UpdateSharedStepRequest
from app.modules.shared_steps.usecases.create_shared_step import CreateSharedStepUseCase
from app.modules.shared_steps.usecases.get_shared_step import GetSharedStepUseCase
from app.modules.shared_steps.usecases.list_shared_step_usage import ListSharedStepUsageUseCase
from app.modules.shared_steps.usecases.list_shared_steps import ListSharedStepsUseCase
from app.modules.shared_steps.usecases.update_shared_step import UpdateSharedStepUseCase
from app.modules.shared_steps.utils.shared_step_actions import build_shared_step_actions
from app.modules.shared_steps.utils.shared_step_response import (
    build_shared_step_response,
    build_shared_step_usage_response,
)
from app.shared.permissions import Actor

shared_steps_router = APIRouter(prefix="/api", tags=["shared-steps"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@shared_steps_router.get("/projects/{project_key}/shared-steps")
async def list_shared_steps(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListSharedStepsUseCase, Depends(get_list_shared_steps)],
    archived: Annotated[bool, Query()] = False,
) -> list[SharedStepResponse]:
    return [build_shared_step_response(detail) for detail in await use_case.execute(actor, project_key, archived)]


@shared_steps_router.post("/projects/{project_key}/shared-steps", status_code=status.HTTP_201_CREATED)
async def create_shared_step(
    project_key: str,
    body: CreateSharedStepRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateSharedStepUseCase, Depends(get_create_shared_step)],
) -> SharedStepResponse:
    actions = build_shared_step_actions(body.steps)
    return build_shared_step_response(await use_case.execute(actor, project_key, body.key, body.title, actions))


@shared_steps_router.get("/projects/{project_key}/shared-steps/{key}")
async def get_shared_step(
    project_key: str,
    key: str,
    actor: SignedInActor,
    use_case: Annotated[GetSharedStepUseCase, Depends(get_get_shared_step)],
) -> SharedStepResponse:
    return build_shared_step_response(await use_case.execute(actor, project_key, key))


@shared_steps_router.patch("/projects/{project_key}/shared-steps/{key}")
async def update_shared_step(
    project_key: str,
    key: str,
    body: UpdateSharedStepRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateSharedStepUseCase, Depends(get_update_shared_step)],
) -> SharedStepResponse:
    changes = SharedStepChanges(
        title=body.title,
        steps=None if body.steps is None else build_shared_step_actions(body.steps),
        is_archived=body.archived,
    )
    detail = await use_case.execute(actor, project_key, key, body.base_version_number, changes)
    return build_shared_step_response(detail)


@shared_steps_router.get("/projects/{project_key}/shared-steps/{key}/usage")
async def list_shared_step_usage(
    project_key: str,
    key: str,
    actor: SignedInActor,
    use_case: Annotated[ListSharedStepUsageUseCase, Depends(get_list_shared_step_usage)],
) -> list[SharedStepUsageResponse]:
    return [build_shared_step_usage_response(usage) for usage in await use_case.execute(actor, project_key, key)]
