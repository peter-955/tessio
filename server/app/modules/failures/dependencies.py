from fastapi import Request

from app.modules.failures.usecases.assign_failure import AssignFailureUseCase
from app.modules.failures.usecases.change_failure_status import ChangeFailureStatusUseCase
from app.modules.failures.usecases.get_failure import GetFailureUseCase
from app.modules.failures.usecases.list_failures import ListFailuresUseCase


def get_list_failures(request: Request) -> ListFailuresUseCase:
    use_case: ListFailuresUseCase = request.app.state.container.list_failures
    return use_case


def get_get_failure(request: Request) -> GetFailureUseCase:
    use_case: GetFailureUseCase = request.app.state.container.get_failure
    return use_case


def get_change_failure_status(request: Request) -> ChangeFailureStatusUseCase:
    use_case: ChangeFailureStatusUseCase = request.app.state.container.change_failure_status
    return use_case


def get_assign_failure(request: Request) -> AssignFailureUseCase:
    use_case: AssignFailureUseCase = request.app.state.container.assign_failure
    return use_case
