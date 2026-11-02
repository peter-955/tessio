from fastapi import Request

from app.modules.story_context.usecases.resolve_data import ResolveDataUseCase


def get_resolve_data(request: Request) -> ResolveDataUseCase:
    use_case: ResolveDataUseCase = request.app.state.container.resolve_data
    return use_case
