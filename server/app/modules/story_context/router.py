from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.projects import get_signed_in_actor
from app.modules.story_context.dependencies import get_resolve_data
from app.modules.story_context.models.resolve_data_request import ResolveDataRequest
from app.modules.story_context.models.resolved_data_response import ResolvedDataResponse
from app.modules.story_context.usecases.resolve_data import ResolveDataUseCase
from app.shared.permissions import Actor

story_context_router = APIRouter(prefix="/api", tags=["runs"])


@story_context_router.post("/projects/{project_key}/runs/{run_id}/resolve-data")
async def resolve_data(
    project_key: str,
    run_id: UUID,
    body: ResolveDataRequest,
    actor: Annotated[Actor, Depends(get_signed_in_actor)],
    use_case: Annotated[ResolveDataUseCase, Depends(get_resolve_data)],
) -> ResolvedDataResponse:
    resolved_data = await use_case.execute(actor, project_key, run_id, body.keys)
    return ResolvedDataResponse(values=resolved_data.values, unknown_keys=resolved_data.unknown_keys)
