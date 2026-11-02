from fastapi import Request

from app.modules.insights.usecases.get_dashboard import GetDashboardUseCase
from app.modules.insights.usecases.get_label_coverage import GetLabelCoverageUseCase
from app.modules.insights.usecases.get_my_work import GetMyWorkUseCase
from app.modules.insights.usecases.get_token_usage import GetTokenUsageUseCase
from app.modules.insights.usecases.get_traceability import GetTraceabilityUseCase
from app.modules.insights.usecases.get_trends import GetTrendsUseCase
from app.modules.insights.usecases.list_case_latest_results import ListCaseLatestResultsUseCase
from app.modules.insights.usecases.list_failing_cases import ListFailingCasesUseCase
from app.modules.insights.usecases.list_flaky_cases import ListFlakyCasesUseCase
from app.modules.insights.usecases.list_sprint_coverage import ListSprintCoverageUseCase
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


def get_get_trends(request: Request) -> GetTrendsUseCase:
    use_case: GetTrendsUseCase = request.app.state.container.get_insight_trends
    return use_case


def get_get_label_coverage(request: Request) -> GetLabelCoverageUseCase:
    use_case: GetLabelCoverageUseCase = request.app.state.container.get_label_coverage
    return use_case


def get_list_failing_cases(request: Request) -> ListFailingCasesUseCase:
    use_case: ListFailingCasesUseCase = request.app.state.container.list_failing_cases
    return use_case


def get_list_flaky_cases(request: Request) -> ListFlakyCasesUseCase:
    use_case: ListFlakyCasesUseCase = request.app.state.container.list_flaky_cases
    return use_case


def get_get_token_usage(request: Request) -> GetTokenUsageUseCase:
    use_case: GetTokenUsageUseCase = request.app.state.container.get_token_usage
    return use_case


def get_list_sprint_coverage(request: Request) -> ListSprintCoverageUseCase:
    use_case: ListSprintCoverageUseCase = request.app.state.container.list_sprint_coverage
    return use_case
