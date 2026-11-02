from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.api_tokens import get_token_allowed_actor
from app.modules.failures.dependencies import (
    get_assign_failure,
    get_change_failure_cause,
    get_change_failure_status,
    get_get_failure,
    get_list_failures,
    get_preview_jira_issue,
    get_request_jira_issue,
)
from app.modules.failures.domains.failure_filter.entity import FailureFilter
from app.modules.failures.models.assign_failure_request import AssignFailureRequest
from app.modules.failures.models.change_failure_cause_request import ChangeFailureCauseRequest
from app.modules.failures.models.change_failure_status_request import ChangeFailureStatusRequest
from app.modules.failures.models.failure_detail_response import FailureDetailResponse
from app.modules.failures.models.failure_response import FailureResponse
from app.modules.failures.models.jira_issue_preview_response import JiraIssuePreviewResponse
from app.modules.failures.typing.enums import FailureStatus
from app.modules.failures.usecases.assign_failure import AssignFailureUseCase
from app.modules.failures.usecases.change_failure_cause import ChangeFailureCauseUseCase
from app.modules.failures.usecases.change_failure_status import ChangeFailureStatusUseCase
from app.modules.failures.usecases.get_failure import GetFailureUseCase
from app.modules.failures.usecases.list_failures import ListFailuresUseCase
from app.modules.failures.usecases.preview_jira_issue import PreviewJiraIssueUseCase
from app.modules.failures.usecases.request_jira_issue import RequestJiraIssueUseCase
from app.modules.failures.utils.failure_response import build_failure_detail_response, build_failure_response
from app.modules.failures.utils.jira_issue_preview_response import build_jira_issue_preview_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

failures_router = APIRouter(prefix="/api", tags=["failures"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]
TokenAllowedActor = Annotated[Actor, Depends(get_token_allowed_actor)]


@failures_router.get("/projects/{project_key}/failures")
async def list_failures(
    project_key: str,
    actor: TokenAllowedActor,
    use_case: Annotated[ListFailuresUseCase, Depends(get_list_failures)],
    statuses: Annotated[list[FailureStatus] | None, Query(alias="status")] = None,
    assignee_id: Annotated[UUID | None, Query(alias="assigneeId")] = None,
    is_unassigned: Annotated[bool, Query(alias="unassigned")] = False,
    story_key: Annotated[str | None, Query(alias="storyKey")] = None,
    test_case_id: Annotated[UUID | None, Query(alias="testCaseId")] = None,
) -> list[FailureResponse]:
    failure_filter = FailureFilter(
        statuses=frozenset(statuses or ()),
        assignee_id=assignee_id,
        is_unassigned=is_unassigned,
        story_jira_key=None if story_key is None else story_key.upper(),
        test_case_id=test_case_id,
    )
    views = await use_case.execute(actor, project_key, failure_filter)
    return [build_failure_response(view) for view in views]


@failures_router.get("/projects/{project_key}/failures/{failure_id}")
async def get_failure(
    project_key: str,
    failure_id: UUID,
    actor: TokenAllowedActor,
    use_case: Annotated[GetFailureUseCase, Depends(get_get_failure)],
) -> FailureDetailResponse:
    return build_failure_detail_response(await use_case.execute(actor, project_key, failure_id))


@failures_router.put("/projects/{project_key}/failures/{failure_id}/status")
async def change_failure_status(
    project_key: str,
    failure_id: UUID,
    body: ChangeFailureStatusRequest,
    actor: SignedInActor,
    use_case: Annotated[ChangeFailureStatusUseCase, Depends(get_change_failure_status)],
) -> FailureResponse:
    return build_failure_response(await use_case.execute(actor, project_key, failure_id, body.status))


@failures_router.put("/projects/{project_key}/failures/{failure_id}/assignee")
async def assign_failure(
    project_key: str,
    failure_id: UUID,
    body: AssignFailureRequest,
    actor: SignedInActor,
    use_case: Annotated[AssignFailureUseCase, Depends(get_assign_failure)],
) -> FailureResponse:
    return build_failure_response(await use_case.execute(actor, project_key, failure_id, body.assignee_id))


@failures_router.put("/projects/{project_key}/failures/{failure_id}/cause")
async def change_failure_cause(
    project_key: str,
    failure_id: UUID,
    body: ChangeFailureCauseRequest,
    actor: SignedInActor,
    use_case: Annotated[ChangeFailureCauseUseCase, Depends(get_change_failure_cause)],
) -> FailureResponse:
    return build_failure_response(await use_case.execute(actor, project_key, failure_id, body.cause, body.reason))


@failures_router.get("/projects/{project_key}/failures/{failure_id}/jira-issue/preview")
async def preview_jira_issue(
    project_key: str,
    failure_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[PreviewJiraIssueUseCase, Depends(get_preview_jira_issue)],
) -> JiraIssuePreviewResponse:
    return build_jira_issue_preview_response(await use_case.execute(actor, project_key, failure_id))


@failures_router.post("/projects/{project_key}/failures/{failure_id}/jira-issue", status_code=status.HTTP_202_ACCEPTED)
async def request_jira_issue(
    project_key: str,
    failure_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RequestJiraIssueUseCase, Depends(get_request_jira_issue)],
) -> FailureResponse:
    return build_failure_response(await use_case.execute(actor, project_key, failure_id))
