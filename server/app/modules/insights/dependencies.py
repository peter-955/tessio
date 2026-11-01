from fastapi import Request

from app.modules.insights.usecases.get_dashboard import GetDashboardUseCase
from app.modules.insights.usecases.get_my_work import GetMyWorkUseCase
from app.modules.insights.usecases.get_traceability import GetTraceabilityUseCase
from app.modules.insights.usecases.list_case_latest_results import ListCaseLatestResultsUseCase
from app.modules.insights.usecases.list_story_progress import ListStoryProgressUseCase


def get_get_traceability(request: Request) -> GetTraceabilityUseCase:
    use_case: GetTraceabilityUseCase = request.app.state.container.get_traceability
    return use_case


def get_list_story_progress(request: Request) -> ListStoryProgressUseCase:
    use_case: ListStoryProgressUseCase = request.app.state.container.list_story_progress
    return use_case


def get_list_case_latest_results(request: Request) -> ListCaseLatestResultsUseCase:
    use_case: ListCaseLatestResultsUseCase = request.app.state.container.list_case_latest_results
    return use_case


def get_get_dashboard(request: Request) -> GetDashboardUseCase:
    use_case: GetDashboardUseCase = request.app.state.container.get_dashboard
    return use_case


def get_get_my_work(request: Request) -> GetMyWorkUseCase:
    use_case: GetMyWorkUseCase = request.app.state.container.get_my_work
    return use_case
