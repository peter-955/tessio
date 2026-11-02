from fastapi import Request

from app.modules.shared_steps.usecases.create_shared_step import CreateSharedStepUseCase
from app.modules.shared_steps.usecases.get_shared_step import GetSharedStepUseCase
from app.modules.shared_steps.usecases.list_shared_step_usage import ListSharedStepUsageUseCase
from app.modules.shared_steps.usecases.list_shared_steps import ListSharedStepsUseCase
from app.modules.shared_steps.usecases.update_shared_step import UpdateSharedStepUseCase


def get_list_shared_steps(request: Request) -> ListSharedStepsUseCase:
    use_case: ListSharedStepsUseCase = request.app.state.container.list_shared_steps
    return use_case


def get_create_shared_step(request: Request) -> CreateSharedStepUseCase:
    use_case: CreateSharedStepUseCase = request.app.state.container.create_shared_step
    return use_case


def get_get_shared_step(request: Request) -> GetSharedStepUseCase:
    use_case: GetSharedStepUseCase = request.app.state.container.get_shared_step
    return use_case


def get_update_shared_step(request: Request) -> UpdateSharedStepUseCase:
    use_case: UpdateSharedStepUseCase = request.app.state.container.update_shared_step
    return use_case


def get_list_shared_step_usage(request: Request) -> ListSharedStepUsageUseCase:
    use_case: ListSharedStepUsageUseCase = request.app.state.container.list_shared_step_usage
    return use_case
