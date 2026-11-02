from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.modules.insights.dependencies import (
    get_get_dashboard,
    get_get_label_coverage,
    get_get_my_work,
    get_get_token_usage,
    get_get_traceability,
    get_get_trends,
    get_list_case_latest_results,
    get_list_failing_cases,
    get_list_flaky_cases,
    get_list_sprint_coverage,
    get_list_story_progress,
)
from app.modules.insights.models.case_latest_result_response import CaseLatestResultResponse
from app.modules.insights.models.dashboard_response import DashboardResponse
from app.modules.insights.models.failing_case_response import FailingCaseResponse
from app.modules.insights.models.flaky_case_response import FlakyCaseResponse
from app.modules.insights.models.label_coverage_report_response import LabelCoverageReportResponse
from app.modules.insights.models.my_work_response import MyWorkResponse
from app.modules.insights.models.sprint_coverage_response import SprintCoverageResponse
from app.modules.insights.models.story_progress_response import StoryProgressResponse
from app.modules.insights.models.token_usage_response import TokenUsageResponse
from app.modules.insights.models.traceability_response import TraceabilityResponse
from app.modules.insights.models.trends_response import TrendsResponse
from app.modules.insights.typing.constants import DEFAULT_CASE_LIST_LIMIT, MAX_CASE_LIST_LIMIT
from app.modules.insights.typing.enums import TrendGrouping
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
from app.modules.insights.utils.insight_responses import (
    build_failing_case_response,
    build_flaky_case_response,
    build_label_coverage_report_response,
    build_sprint_coverage_response,
    build_token_usage_response,
    build_trends_response,
)
from app.modules.insights.utils.responses import (
    build_case_latest_result_response,
    build_dashboard_response,
    build_my_work_response,
    build_story_progress_response,
    build_traceability_response,
)
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

insights_router = APIRouter(prefix="/api", tags=["insights"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]
SprintIdQuery = Annotated[UUID | None, Query(alias="sprintId")]
FromDayQuery = Annotated[date | None, Query(alias="from")]
ToDayQuery = Annotated[date | None, Query(alias="to")]
CaseListLimitQuery = Annotated[int, Query(ge=1, le=MAX_CASE_LIST_LIMIT)]


@insights_router.get("/projects/{project_key}/stories/{jira_key}/traceability")
async def get_traceability(
    project_key: str,
    jira_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetTraceabilityUseCase, Depends(get_get_traceability)],
) -> TraceabilityResponse:
    return build_traceability_response(await use_case.execute(actor, project_key, jira_key))


@insights_router.get("/projects/{project_key}/story-progress")
async def list_story_progress(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListStoryProgressUseCase, Depends(get_list_story_progress)],
    sprint_id: SprintIdQuery = None,
) -> list[StoryProgressResponse]:
    return [
        build_story_progress_response(progress) for progress in await use_case.execute(actor, project_key, sprint_id)
    ]


@insights_router.get("/projects/{project_key}/case-latest-results")
async def list_case_latest_results(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListCaseLatestResultsUseCase, Depends(get_list_case_latest_results)],
    story_key: Annotated[str | None, Query(alias="storyKey")] = None,
) -> list[CaseLatestResultResponse]:
    results = await use_case.execute(actor, project_key, story_key)
    return [build_case_latest_result_response(case_result) for case_result in results]


@insights_router.get("/projects/{project_key}/dashboard")
async def get_dashboard(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetDashboardUseCase, Depends(get_get_dashboard)],
    sprint_id: SprintIdQuery = None,
) -> DashboardResponse:
    return build_dashboard_response(await use_case.execute(actor, project_key, sprint_id))


@insights_router.get("/projects/{project_key}/my-work")
async def get_my_work(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetMyWorkUseCase, Depends(get_get_my_work)],
    sprint_id: SprintIdQuery = None,
) -> MyWorkResponse:
    return build_my_work_response(await use_case.execute(actor, project_key, sprint_id))


@insights_router.get("/projects/{project_key}/insights/trends")
async def get_insight_trends(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetTrendsUseCase, Depends(get_get_trends)],
    from_day: FromDayQuery = None,
    to_day: ToDayQuery = None,
    group_by: Annotated[TrendGrouping, Query(alias="groupBy")] = TrendGrouping.DAY,
) -> TrendsResponse:
    return build_trends_response(await use_case.execute(actor, project_key, from_day, to_day, group_by))


@insights_router.get("/projects/{project_key}/insights/coverage-by-label")
async def get_label_coverage(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetLabelCoverageUseCase, Depends(get_get_label_coverage)],
) -> LabelCoverageReportResponse:
    return build_label_coverage_report_response(await use_case.execute(actor, project_key))


@insights_router.get("/projects/{project_key}/insights/top-failing")
async def list_top_failing_cases(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListFailingCasesUseCase, Depends(get_list_failing_cases)],
    from_day: FromDayQuery = None,
    to_day: ToDayQuery = None,
    limit: CaseListLimitQuery = DEFAULT_CASE_LIST_LIMIT,
) -> list[FailingCaseResponse]:
    failing_cases = await use_case.execute(actor, project_key, from_day, to_day, limit)
    return [build_failing_case_response(failing_case) for failing_case in failing_cases]


@insights_router.get("/projects/{project_key}/insights/flaky")
async def list_flaky_cases(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListFlakyCasesUseCase, Depends(get_list_flaky_cases)],
    limit: CaseListLimitQuery = DEFAULT_CASE_LIST_LIMIT,
) -> list[FlakyCaseResponse]:
    return [build_flaky_case_response(flaky_case) for flaky_case in await use_case.execute(actor, project_key, limit)]


@insights_router.get("/projects/{project_key}/insights/tokens")
async def get_token_usage(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetTokenUsageUseCase, Depends(get_get_token_usage)],
    from_day: FromDayQuery = None,
    to_day: ToDayQuery = None,
) -> TokenUsageResponse:
    return build_token_usage_response(await use_case.execute(actor, project_key, from_day, to_day))


@insights_router.get("/projects/{project_key}/insights/sprint-coverage")
async def list_sprint_coverage(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListSprintCoverageUseCase, Depends(get_list_sprint_coverage)],
    from_day: FromDayQuery = None,
    to_day: ToDayQuery = None,
) -> list[SprintCoverageResponse]:
    coverages = await use_case.execute(actor, project_key, from_day, to_day)
    return [build_sprint_coverage_response(coverage) for coverage in coverages]
