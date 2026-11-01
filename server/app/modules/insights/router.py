from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.modules.insights.dependencies import (
    get_get_dashboard,
    get_get_my_work,
    get_get_traceability,
    get_list_case_latest_results,
    get_list_story_progress,
)
from app.modules.insights.models.case_latest_result_response import CaseLatestResultResponse
from app.modules.insights.models.dashboard_response import DashboardResponse
from app.modules.insights.models.my_work_response import MyWorkResponse
from app.modules.insights.models.story_progress_response import StoryProgressResponse
from app.modules.insights.models.traceability_response import TraceabilityResponse
from app.modules.insights.usecases.get_dashboard import GetDashboardUseCase
from app.modules.insights.usecases.get_my_work import GetMyWorkUseCase
from app.modules.insights.usecases.get_traceability import GetTraceabilityUseCase
from app.modules.insights.usecases.list_case_latest_results import ListCaseLatestResultsUseCase
from app.modules.insights.usecases.list_story_progress import ListStoryProgressUseCase
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
