from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.modules.health.dependencies import get_check_readiness
from app.modules.health.models.health_response import HealthResponse
from app.modules.health.models.readiness_response import ReadinessResponse
from app.modules.health.typing.enums import LivenessStatus, ReadinessStatus
from app.modules.health.usecases.check_readiness import CheckReadinessUseCase

health_router = APIRouter(prefix="/api/health", tags=["health"])


@health_router.get("")
async def check_liveness() -> HealthResponse:
    return HealthResponse(status=LivenessStatus.OK)


@health_router.get("/ready", responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}})
async def check_readiness(
    response: Response,
    use_case: Annotated[CheckReadinessUseCase, Depends(get_check_readiness)],
) -> ReadinessResponse:
    report = await use_case.execute()
    if not report.is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status=ReadinessStatus.NOT_READY, checks=report.checks)
    return ReadinessResponse(status=ReadinessStatus.READY, checks=report.checks)
