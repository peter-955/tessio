from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.ai_harness.dependencies import get_get_ai_harness
from app.modules.ai_harness.models.ai_harness_response import AiHarnessResponse
from app.modules.ai_harness.typing.constants import AI_HARNESS_ROUTE_PREFIX
from app.modules.ai_harness.usecases.get_ai_harness import GetAiHarnessUseCase
from app.modules.ai_harness.utils.ai_harness_response import build_ai_harness_response
from app.modules.projects import get_signed_in_actor

ai_harness_router = APIRouter(prefix=AI_HARNESS_ROUTE_PREFIX, tags=["ai-harness"])


@ai_harness_router.get("", dependencies=[Depends(get_signed_in_actor)])
async def get_ai_harness(
    use_case: Annotated[GetAiHarnessUseCase, Depends(get_get_ai_harness)],
) -> AiHarnessResponse:
    return build_ai_harness_response(await use_case.execute())
