from fastapi import Request

from app.modules.health.usecases.check_readiness import CheckReadinessUseCase


def get_check_readiness(request: Request) -> CheckReadinessUseCase:
    use_case: CheckReadinessUseCase = request.app.state.container.check_readiness
    return use_case
