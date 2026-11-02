from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.projects import get_signed_in_actor
from app.modules.suites.dependencies import (
    get_add_suite_cases_by_filter,
    get_archive_suite,
    get_create_suite,
    get_get_suite,
    get_list_suites,
    get_set_suite_cases,
    get_update_suite,
)
from app.modules.suites.domains.suite_patch.entity import SuitePatch
from app.modules.suites.models.add_suite_cases_by_filter_request import AddSuiteCasesByFilterRequest
from app.modules.suites.models.create_suite_request import CreateSuiteRequest
from app.modules.suites.models.set_suite_cases_request import SetSuiteCasesRequest
from app.modules.suites.models.suite_cases_added_response import SuiteCasesAddedResponse
from app.modules.suites.models.suite_detail_response import SuiteDetailResponse
from app.modules.suites.models.suite_summary_response import SuiteSummaryResponse
from app.modules.suites.models.update_suite_request import UpdateSuiteRequest
from app.modules.suites.usecases.add_suite_cases_by_filter import AddSuiteCasesByFilterUseCase
from app.modules.suites.usecases.archive_suite import ArchiveSuiteUseCase
from app.modules.suites.usecases.create_suite import CreateSuiteUseCase
from app.modules.suites.usecases.get_suite import GetSuiteUseCase
from app.modules.suites.usecases.list_suites import ListSuitesUseCase
from app.modules.suites.usecases.set_suite_cases import SetSuiteCasesUseCase
from app.modules.suites.usecases.update_suite import UpdateSuiteUseCase
from app.modules.suites.utils.suite_responses import build_suite_detail_response, build_suite_summary_response
from app.shared.permissions import Actor

suites_router = APIRouter(prefix="/api", tags=["suites"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@suites_router.get("/projects/{project_key}/suites")
async def list_suites(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListSuitesUseCase, Depends(get_list_suites)],
    is_including_archived: Annotated[bool, Query(alias="archived")] = False,
) -> list[SuiteSummaryResponse]:
    summaries = await use_case.execute(actor, project_key, is_including_archived)
    return [build_suite_summary_response(summary) for summary in summaries]


@suites_router.post("/projects/{project_key}/suites", status_code=status.HTTP_201_CREATED)
async def create_suite(
    project_key: str,
    body: CreateSuiteRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateSuiteUseCase, Depends(get_create_suite)],
) -> SuiteDetailResponse:
    return build_suite_detail_response(await use_case.execute(actor, project_key, body.name, body.description))


@suites_router.get("/projects/{project_key}/suites/{suite_id}")
async def get_suite(
    project_key: str,
    suite_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[GetSuiteUseCase, Depends(get_get_suite)],
) -> SuiteDetailResponse:
    return build_suite_detail_response(await use_case.execute(actor, project_key, suite_id))


@suites_router.patch("/projects/{project_key}/suites/{suite_id}")
async def update_suite(
    project_key: str,
    suite_id: UUID,
    body: UpdateSuiteRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateSuiteUseCase, Depends(get_update_suite)],
) -> SuiteDetailResponse:
    patch = SuitePatch(
        name=body.name,
        description=body.description,
        is_changing_description="description" in body.model_fields_set,
    )
    return build_suite_detail_response(await use_case.execute(actor, project_key, suite_id, patch))


@suites_router.post("/projects/{project_key}/suites/{suite_id}/archive")
async def archive_suite(
    project_key: str,
    suite_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ArchiveSuiteUseCase, Depends(get_archive_suite)],
) -> SuiteDetailResponse:
    return build_suite_detail_response(await use_case.execute(actor, project_key, suite_id))


@suites_router.put("/projects/{project_key}/suites/{suite_id}/cases")
async def set_suite_cases(
    project_key: str,
    suite_id: UUID,
    body: SetSuiteCasesRequest,
    actor: SignedInActor,
    use_case: Annotated[SetSuiteCasesUseCase, Depends(get_set_suite_cases)],
) -> SuiteDetailResponse:
    return build_suite_detail_response(await use_case.execute(actor, project_key, suite_id, body.test_case_ids))


@suites_router.post("/projects/{project_key}/suites/{suite_id}/cases/by-filter")
async def add_suite_cases_by_filter(
    project_key: str,
    suite_id: UUID,
    body: AddSuiteCasesByFilterRequest,
    actor: SignedInActor,
    use_case: Annotated[AddSuiteCasesByFilterUseCase, Depends(get_add_suite_cases_by_filter)],
) -> SuiteCasesAddedResponse:
    added = await use_case.execute(
        actor, project_key, suite_id, body.labels, body.priorities, body.story_key, body.sprint_id
    )
    return SuiteCasesAddedResponse(added_count=added.added_count, suite=build_suite_detail_response(added.detail))
