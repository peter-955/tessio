from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.gaps.dependencies import (
    get_answer_gap,
    get_get_gap,
    get_list_gap_inbox,
    get_list_gaps,
    get_raise_gaps,
    get_reassign_gap,
    get_reopen_gap,
)
from app.modules.gaps.domains.gap_draft.entity import GapDraft
from app.modules.gaps.domains.gap_route.entity import GapRoute
from app.modules.gaps.models.answer_gap_request import AnswerGapRequest
from app.modules.gaps.models.gap_response import GapResponse
from app.modules.gaps.models.raise_gap_request import RaiseGapRequest
from app.modules.gaps.models.reassign_gap_request import ReassignGapRequest
from app.modules.gaps.typing.enums import GapStatus
from app.modules.gaps.usecases.answer_gap import AnswerGapUseCase
from app.modules.gaps.usecases.get_gap import GetGapUseCase
from app.modules.gaps.usecases.list_gap_inbox import ListGapInboxUseCase
from app.modules.gaps.usecases.list_gaps import ListGapsUseCase
from app.modules.gaps.usecases.raise_gaps import RaiseGapsUseCase
from app.modules.gaps.usecases.reassign_gap import ReassignGapUseCase
from app.modules.gaps.usecases.reopen_gap import ReopenGapUseCase
from app.modules.gaps.utils.gap_response import build_gap_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

gaps_router = APIRouter(prefix="/api", tags=["gaps"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@gaps_router.get("/projects/{project_key}/gaps")
async def list_gaps(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListGapsUseCase, Depends(get_list_gaps)],
    story_key: Annotated[str | None, Query(alias="storyKey")] = None,
    gap_status: Annotated[GapStatus | None, Query(alias="status")] = None,
    is_mine: Annotated[bool, Query(alias="mine")] = False,
) -> list[GapResponse]:
    views = await use_case.execute(actor, project_key, story_key, gap_status, is_mine)
    return [build_gap_response(view) for view in views]


@gaps_router.post("/projects/{project_key}/stories/{jira_key}/gaps", status_code=status.HTTP_201_CREATED)
async def raise_gap(
    project_key: str,
    jira_key: str,
    body: RaiseGapRequest,
    actor: SignedInActor,
    use_case: Annotated[RaiseGapsUseCase, Depends(get_raise_gaps)],
) -> GapResponse:
    draft = GapDraft(
        type=body.type,
        severity=body.severity,
        target_type=body.target_type,
        target_ref=body.target_ref,
        question=body.question,
        data_scope=body.data_scope,
        assignee_id=body.assignee_id,
    )
    raised_gaps = await use_case.execute(actor, project_key, jira_key, [draft])
    return build_gap_response(raised_gaps.gaps[0])


@gaps_router.get("/projects/{project_key}/gaps/{gap_id}")
async def get_gap(
    project_key: str,
    gap_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[GetGapUseCase, Depends(get_get_gap)],
) -> GapResponse:
    return build_gap_response(await use_case.execute(actor, project_key, gap_id))


@gaps_router.put("/projects/{project_key}/gaps/{gap_id}/answer")
async def answer_gap(
    project_key: str,
    gap_id: UUID,
    body: AnswerGapRequest,
    actor: SignedInActor,
    use_case: Annotated[AnswerGapUseCase, Depends(get_answer_gap)],
) -> GapResponse:
    return build_gap_response(await use_case.execute(actor, project_key, gap_id, body.answer))


@gaps_router.post("/projects/{project_key}/gaps/{gap_id}/reopen")
async def reopen_gap(
    project_key: str,
    gap_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ReopenGapUseCase, Depends(get_reopen_gap)],
) -> GapResponse:
    return build_gap_response(await use_case.execute(actor, project_key, gap_id))


@gaps_router.put("/projects/{project_key}/gaps/{gap_id}/assignee")
async def reassign_gap(
    project_key: str,
    gap_id: UUID,
    body: ReassignGapRequest,
    actor: SignedInActor,
    use_case: Annotated[ReassignGapUseCase, Depends(get_reassign_gap)],
) -> GapResponse:
    route = GapRoute(assignee_id=body.assignee_id, assignee_role=body.assignee_role)
    return build_gap_response(await use_case.execute(actor, project_key, gap_id, route))


@gaps_router.get("/gaps/inbox")
async def list_gap_inbox(
    actor: SignedInActor,
    use_case: Annotated[ListGapInboxUseCase, Depends(get_list_gap_inbox)],
    is_including_resolved: Annotated[bool, Query(alias="includeResolved")] = False,
) -> list[GapResponse]:
    return [build_gap_response(view) for view in await use_case.execute(actor, is_including_resolved)]
