from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.projects import get_signed_in_actor
from app.modules.stories.dependencies import (
    get_change_test_status,
    get_get_sprint,
    get_get_story,
    get_get_sync_status,
    get_list_sprints,
    get_list_stories,
    get_request_jira_sync,
)
from app.modules.stories.domains.story_filter.entity import StoryFilter
from app.modules.stories.models.change_test_status_request import ChangeTestStatusRequest
from app.modules.stories.models.project_sync_state_response import ProjectSyncStateResponse
from app.modules.stories.models.sprint_response import SprintResponse
from app.modules.stories.models.story_detail_response import StoryDetailResponse
from app.modules.stories.models.story_summary_response import StorySummaryResponse
from app.modules.stories.typing.constants import STORY_QUERY_MAX_LENGTH
from app.modules.stories.typing.enums import TestStatus
from app.modules.stories.usecases.change_test_status import ChangeTestStatusUseCase
from app.modules.stories.usecases.get_sprint import GetSprintUseCase
from app.modules.stories.usecases.get_story import GetStoryUseCase
from app.modules.stories.usecases.get_sync_status import GetSyncStatusUseCase
from app.modules.stories.usecases.list_sprints import ListSprintsUseCase
from app.modules.stories.usecases.list_stories import ListStoriesUseCase
from app.modules.stories.usecases.request_jira_sync import RequestJiraSyncUseCase
from app.modules.stories.utils.responses import (
    build_project_sync_state_response,
    build_sprint_response,
    build_story_detail_response,
    build_story_summary_response,
)
from app.shared.permissions import Actor

stories_router = APIRouter(prefix="/api", tags=["stories"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@stories_router.get("/projects/{project_key}/sprints")
async def list_sprints(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListSprintsUseCase, Depends(get_list_sprints)],
) -> list[SprintResponse]:
    return [build_sprint_response(overview) for overview in await use_case.execute(actor, project_key)]


@stories_router.get("/projects/{project_key}/sprints/{sprint_id}")
async def get_sprint(
    project_key: str,
    sprint_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[GetSprintUseCase, Depends(get_get_sprint)],
) -> SprintResponse:
    return build_sprint_response(await use_case.execute(actor, project_key, sprint_id))


@stories_router.get("/projects/{project_key}/stories")
async def list_stories(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListStoriesUseCase, Depends(get_list_stories)],
    sprint_id: Annotated[UUID | None, Query(alias="sprintId")] = None,
    test_status: Annotated[TestStatus | None, Query(alias="testStatus")] = None,
    query: Annotated[str | None, Query(max_length=STORY_QUERY_MAX_LENGTH)] = None,
) -> list[StorySummaryResponse]:
    story_filter = StoryFilter(sprint_id=sprint_id, test_status=test_status, query=query)
    return [
        build_story_summary_response(summary) for summary in await use_case.execute(actor, project_key, story_filter)
    ]


@stories_router.get("/projects/{project_key}/stories/{jira_key}")
async def get_story(
    project_key: str,
    jira_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetStoryUseCase, Depends(get_get_story)],
) -> StoryDetailResponse:
    return build_story_detail_response(await use_case.execute(actor, project_key, jira_key))


@stories_router.put("/projects/{project_key}/stories/{jira_key}/test-status")
async def change_test_status(
    project_key: str,
    jira_key: str,
    body: ChangeTestStatusRequest,
    actor: SignedInActor,
    use_case: Annotated[ChangeTestStatusUseCase, Depends(get_change_test_status)],
) -> StoryDetailResponse:
    return build_story_detail_response(await use_case.execute(actor, project_key, jira_key, body.test_status))


@stories_router.get("/projects/{project_key}/sync")
async def get_sync_status(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[GetSyncStatusUseCase, Depends(get_get_sync_status)],
) -> ProjectSyncStateResponse:
    return build_project_sync_state_response(await use_case.execute(actor, project_key))


@stories_router.post("/projects/{project_key}/sync", status_code=status.HTTP_202_ACCEPTED)
async def request_jira_sync(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[RequestJiraSyncUseCase, Depends(get_request_jira_sync)],
) -> ProjectSyncStateResponse:
    return build_project_sync_state_response(await use_case.execute(actor, project_key))
