from fastapi import Request

from app.modules.suites.usecases.add_suite_cases_by_filter import AddSuiteCasesByFilterUseCase
from app.modules.suites.usecases.archive_suite import ArchiveSuiteUseCase
from app.modules.suites.usecases.create_suite import CreateSuiteUseCase
from app.modules.suites.usecases.get_suite import GetSuiteUseCase
from app.modules.suites.usecases.list_suites import ListSuitesUseCase
from app.modules.suites.usecases.set_suite_cases import SetSuiteCasesUseCase
from app.modules.suites.usecases.update_suite import UpdateSuiteUseCase


def get_list_suites(request: Request) -> ListSuitesUseCase:
    use_case: ListSuitesUseCase = request.app.state.container.list_suites
    return use_case


def get_create_suite(request: Request) -> CreateSuiteUseCase:
    use_case: CreateSuiteUseCase = request.app.state.container.create_suite
    return use_case


def get_get_suite(request: Request) -> GetSuiteUseCase:
    use_case: GetSuiteUseCase = request.app.state.container.get_suite
    return use_case


def get_update_suite(request: Request) -> UpdateSuiteUseCase:
    use_case: UpdateSuiteUseCase = request.app.state.container.update_suite
    return use_case


def get_archive_suite(request: Request) -> ArchiveSuiteUseCase:
    use_case: ArchiveSuiteUseCase = request.app.state.container.archive_suite
    return use_case


def get_set_suite_cases(request: Request) -> SetSuiteCasesUseCase:
    use_case: SetSuiteCasesUseCase = request.app.state.container.set_suite_cases
    return use_case


def get_add_suite_cases_by_filter(request: Request) -> AddSuiteCasesByFilterUseCase:
    use_case: AddSuiteCasesByFilterUseCase = request.app.state.container.add_suite_cases_by_filter
    return use_case
