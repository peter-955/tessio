from fastapi import Request

from app.modules.ai_harness.usecases.get_ai_harness import GetAiHarnessUseCase


def get_get_ai_harness(request: Request) -> GetAiHarnessUseCase:
    use_case: GetAiHarnessUseCase = request.app.state.container.get_ai_harness
    return use_case
