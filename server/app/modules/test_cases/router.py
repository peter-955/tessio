from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.api_tokens import get_token_allowed_actor
from app.modules.labels import MAX_LABELS_PER_CASE, CaseLabelResponse, build_case_label_response
from app.modules.projects import get_signed_in_actor
from app.modules.test_cases.dependencies import (
    get_add_review_comment,
    get_attach_test_file,
    get_change_test_case_status,
    get_commit_test_case_import,
    get_create_test_case,
    get_get_test_case,
    get_list_quarantine_events,
    get_list_review_comments,
    get_list_test_case_versions,
    get_list_test_cases,
    get_list_test_file_versions,
    get_mark_test_case_reviewed,
    get_preview_test_case_import,
    get_quarantine_test_case,
    get_release_test_case_quarantine,
    get_resolve_review_comment,
    get_set_test_case_labels,
    get_update_test_case,
)
from app.modules.test_cases.domains.test_case_changes.entity import TestCaseChanges
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_filter.entity import TestCaseFilter
from app.modules.test_cases.models.attach_test_file_request import AttachTestFileRequest
from app.modules.test_cases.models.case_import_commit_request import CaseImportCommitRequest
from app.modules.test_cases.models.case_import_preview_request import CaseImportPreviewRequest
from app.modules.test_cases.models.case_import_preview_response import CaseImportPreviewResponse
from app.modules.test_cases.models.case_import_result_response import CaseImportResultResponse
from app.modules.test_cases.models.change_test_case_status_request import ChangeTestCaseStatusRequest
from app.modules.test_cases.models.create_review_comment_request import CreateReviewCommentRequest
from app.modules.test_cases.models.create_test_case_request import CreateTestCaseRequest
from app.modules.test_cases.models.quarantine_event_response import QuarantineEventResponse
from app.modules.test_cases.models.quarantine_test_case_request import QuarantineTestCaseRequest
from app.modules.test_cases.models.review_comment_response import ReviewCommentResponse
from app.modules.test_cases.models.set_test_case_labels_request import SetTestCaseLabelsRequest
from app.modules.test_cases.models.test_case_detail_response import TestCaseDetailResponse
from app.modules.test_cases.models.test_case_summary_response import TestCaseSummaryResponse
from app.modules.test_cases.models.test_case_version_response import TestCaseVersionResponse
from app.modules.test_cases.models.test_file_version_response import TestFileVersionResponse
from app.modules.test_cases.models.update_test_case_request import UpdateTestCaseRequest
from app.modules.test_cases.typing.constants import MAX_QUERY_LENGTH
from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.modules.test_cases.usecases.add_review_comment import AddReviewCommentUseCase
from app.modules.test_cases.usecases.attach_test_file import AttachTestFileUseCase
from app.modules.test_cases.usecases.change_test_case_status import ChangeTestCaseStatusUseCase
from app.modules.test_cases.usecases.commit_test_case_import import CommitTestCaseImportUseCase
from app.modules.test_cases.usecases.create_test_case import CreateTestCaseUseCase
from app.modules.test_cases.usecases.get_test_case import GetTestCaseUseCase
from app.modules.test_cases.usecases.list_quarantine_events import ListQuarantineEventsUseCase
from app.modules.test_cases.usecases.list_review_comments import ListReviewCommentsUseCase
from app.modules.test_cases.usecases.list_test_case_versions import ListTestCaseVersionsUseCase
from app.modules.test_cases.usecases.list_test_cases import ListTestCasesUseCase
from app.modules.test_cases.usecases.list_test_file_versions import ListTestFileVersionsUseCase
from app.modules.test_cases.usecases.mark_test_case_reviewed import MarkTestCaseReviewedUseCase
from app.modules.test_cases.usecases.preview_test_case_import import PreviewTestCaseImportUseCase
from app.modules.test_cases.usecases.quarantine_test_case import QuarantineTestCaseUseCase
from app.modules.test_cases.usecases.release_test_case_quarantine import ReleaseTestCaseQuarantineUseCase
from app.modules.test_cases.usecases.resolve_review_comment import ResolveReviewCommentUseCase
from app.modules.test_cases.usecases.set_test_case_labels import SetTestCaseLabelsUseCase
from app.modules.test_cases.usecases.update_test_case import UpdateTestCaseUseCase
from app.modules.test_cases.utils.quarantine_event_response import build_quarantine_event_response
from app.modules.test_cases.utils.responses import (
    build_case_import_preview_response,
    build_case_import_result_response,
    build_test_case_detail_response,
    build_test_case_summary_response,
    build_test_case_version_response,
    build_test_file_version_response,
)
from app.modules.test_cases.utils.review_comment_response import build_review_comment_response
from app.modules.test_cases.utils.test_steps import build_test_steps
from app.shared.permissions import Actor

test_cases_router = APIRouter(prefix="/api", tags=["test-cases"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]
TokenAllowedActor = Annotated[Actor, Depends(get_token_allowed_actor)]


@test_cases_router.get("/projects/{project_key}/test-cases")
async def list_test_cases(
    project_key: str,
    actor: TokenAllowedActor,
    use_case: Annotated[ListTestCasesUseCase, Depends(get_list_test_cases)],
    story_key: Annotated[str | None, Query(alias="storyKey", max_length=MAX_QUERY_LENGTH)] = None,
    case_status: Annotated[TestCaseStatus | None, Query(alias="status")] = None,
    priority: Annotated[TestCasePriority | None, Query()] = None,
    criterion_id: Annotated[UUID | None, Query(alias="criterionId")] = None,
    needs_review: Annotated[bool | None, Query(alias="needsReview")] = None,
    query: Annotated[str | None, Query(max_length=MAX_QUERY_LENGTH)] = None,
    label_names: Annotated[list[str] | None, Query(alias="label", max_length=MAX_LABELS_PER_CASE)] = None,
    flaky: Annotated[bool | None, Query()] = None,
    disagreeing: Annotated[bool | None, Query()] = None,
    quarantined: Annotated[bool | None, Query()] = None,
) -> list[TestCaseSummaryResponse]:
    case_filter = TestCaseFilter(
        story_key=story_key,
        status=case_status,
        priority=priority,
        criterion_id=criterion_id,
        is_needing_review=needs_review,
        query=query,
        label_names=tuple(label_names or ()),
        is_flaky=flaky,
        is_disagreeing=disagreeing,
        is_quarantined=quarantined,
    )
    summaries = await use_case.execute(actor, project_key, case_filter)
    return [build_test_case_summary_response(summary) for summary in summaries]


@test_cases_router.post("/projects/{project_key}/test-cases", status_code=status.HTTP_201_CREATED)
async def create_test_case(
    project_key: str,
    body: CreateTestCaseRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateTestCaseUseCase, Depends(get_create_test_case)],
) -> TestCaseDetailResponse:
    content = TestCaseContent(
        title=body.title,
        priority=body.priority,
        business_value=body.business_value,
        preconditions=body.preconditions,
        steps=build_test_steps(body.steps),
        criterion_ids=body.criterion_ids,
        parameters=body.parameters,
        data_rows=body.data_rows,
    )
    return build_test_case_detail_response(await use_case.execute(actor, project_key, body.story_key, content))


@test_cases_router.get("/projects/{project_key}/test-cases/{case_code}")
async def get_test_case(
    project_key: str,
    case_code: str,
    actor: TokenAllowedActor,
    use_case: Annotated[GetTestCaseUseCase, Depends(get_get_test_case)],
) -> TestCaseDetailResponse:
    return build_test_case_detail_response(await use_case.execute(actor, project_key, case_code))


@test_cases_router.patch("/projects/{project_key}/test-cases/{case_code}")
async def update_test_case(
    project_key: str,
    case_code: str,
    body: UpdateTestCaseRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateTestCaseUseCase, Depends(get_update_test_case)],
) -> TestCaseDetailResponse:
    changes = TestCaseChanges(
        title=body.title,
        priority=body.priority,
        business_value=body.business_value,
        preconditions=body.preconditions,
        steps=None if body.steps is None else build_test_steps(body.steps),
        criterion_ids=body.criterion_ids,
        parameters=body.parameters,
        data_rows=body.data_rows,
    )
    detail = await use_case.execute(actor, project_key, case_code, body.base_version_number, changes)
    return build_test_case_detail_response(detail)


@test_cases_router.get("/projects/{project_key}/test-cases/{case_code}/versions")
async def list_test_case_versions(
    project_key: str,
    case_code: str,
    actor: TokenAllowedActor,
    use_case: Annotated[ListTestCaseVersionsUseCase, Depends(get_list_test_case_versions)],
) -> list[TestCaseVersionResponse]:
    versions = await use_case.execute(actor, project_key, case_code)
    return [build_test_case_version_response(version) for version in versions]


@test_cases_router.put("/projects/{project_key}/test-cases/{case_code}/status")
async def change_test_case_status(
    project_key: str,
    case_code: str,
    body: ChangeTestCaseStatusRequest,
    actor: SignedInActor,
    use_case: Annotated[ChangeTestCaseStatusUseCase, Depends(get_change_test_case_status)],
) -> TestCaseDetailResponse:
    return build_test_case_detail_response(await use_case.execute(actor, project_key, case_code, body.status))


@test_cases_router.post("/projects/{project_key}/test-cases/{case_code}/review")
async def mark_test_case_reviewed(
    project_key: str,
    case_code: str,
    actor: SignedInActor,
    use_case: Annotated[MarkTestCaseReviewedUseCase, Depends(get_mark_test_case_reviewed)],
) -> TestCaseDetailResponse:
    return build_test_case_detail_response(await use_case.execute(actor, project_key, case_code))


@test_cases_router.get("/projects/{project_key}/test-cases/{case_code}/review-comments")
async def list_review_comments(
    project_key: str,
    case_code: str,
    actor: SignedInActor,
    use_case: Annotated[ListReviewCommentsUseCase, Depends(get_list_review_comments)],
) -> list[ReviewCommentResponse]:
    views = await use_case.execute(actor, project_key, case_code)
    return [build_review_comment_response(view) for view in views]


@test_cases_router.post(
    "/projects/{project_key}/test-cases/{case_code}/review-comments", status_code=status.HTTP_201_CREATED
)
async def add_review_comment(
    project_key: str,
    case_code: str,
    body: CreateReviewCommentRequest,
    actor: SignedInActor,
    use_case: Annotated[AddReviewCommentUseCase, Depends(get_add_review_comment)],
) -> ReviewCommentResponse:
    view = await use_case.execute(actor, project_key, case_code, body.body, body.step_order, body.version_number)
    return build_review_comment_response(view)


@test_cases_router.put("/projects/{project_key}/test-cases/{case_code}/review-comments/{comment_id}/resolve")
async def resolve_review_comment(
    project_key: str,
    case_code: str,
    comment_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ResolveReviewCommentUseCase, Depends(get_resolve_review_comment)],
) -> ReviewCommentResponse:
    return build_review_comment_response(await use_case.execute(actor, project_key, case_code, comment_id))


@test_cases_router.put("/projects/{project_key}/test-cases/{case_code}/labels")
async def set_test_case_labels(
    project_key: str,
    case_code: str,
    body: SetTestCaseLabelsRequest,
    actor: SignedInActor,
    use_case: Annotated[SetTestCaseLabelsUseCase, Depends(get_set_test_case_labels)],
) -> list[CaseLabelResponse]:
    labels = await use_case.execute(actor, project_key, case_code, body.label_ids)
    return [build_case_label_response(label) for label in labels]


@test_cases_router.post("/projects/{project_key}/test-cases/{case_code}/files", status_code=status.HTTP_201_CREATED)
async def attach_test_file(
    project_key: str,
    case_code: str,
    body: AttachTestFileRequest,
    actor: SignedInActor,
    use_case: Annotated[AttachTestFileUseCase, Depends(get_attach_test_file)],
) -> TestCaseDetailResponse:
    detail = await use_case.execute(actor, project_key, case_code, body.key, body.file_id, body.base_version_number)
    return build_test_case_detail_response(detail)


@test_cases_router.get("/projects/{project_key}/test-cases/{case_code}/files/{file_key}/versions")
async def list_test_file_versions(
    project_key: str,
    case_code: str,
    file_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListTestFileVersionsUseCase, Depends(get_list_test_file_versions)],
) -> list[TestFileVersionResponse]:
    versions = await use_case.execute(actor, project_key, case_code, file_key)
    return [build_test_file_version_response(version) for version in versions]


@test_cases_router.put("/projects/{project_key}/test-cases/{case_code}/quarantine")
async def quarantine_test_case(
    project_key: str,
    case_code: str,
    body: QuarantineTestCaseRequest,
    actor: SignedInActor,
    use_case: Annotated[QuarantineTestCaseUseCase, Depends(get_quarantine_test_case)],
) -> TestCaseDetailResponse:
    detail = await use_case.execute(actor, project_key, case_code, body.reason or None)
    return build_test_case_detail_response(detail)


@test_cases_router.delete("/projects/{project_key}/test-cases/{case_code}/quarantine")
async def release_test_case_quarantine(
    project_key: str,
    case_code: str,
    actor: SignedInActor,
    use_case: Annotated[ReleaseTestCaseQuarantineUseCase, Depends(get_release_test_case_quarantine)],
) -> TestCaseDetailResponse:
    return build_test_case_detail_response(await use_case.execute(actor, project_key, case_code))


@test_cases_router.get("/projects/{project_key}/test-cases/{case_code}/quarantine-events")
async def list_quarantine_events(
    project_key: str,
    case_code: str,
    actor: SignedInActor,
    use_case: Annotated[ListQuarantineEventsUseCase, Depends(get_list_quarantine_events)],
) -> list[QuarantineEventResponse]:
    return [build_quarantine_event_response(view) for view in await use_case.execute(actor, project_key, case_code)]


@test_cases_router.post("/projects/{project_key}/test-case-imports/preview")
async def preview_test_case_import(
    project_key: str,
    body: CaseImportPreviewRequest,
    actor: SignedInActor,
    use_case: Annotated[PreviewTestCaseImportUseCase, Depends(get_preview_test_case_import)],
) -> CaseImportPreviewResponse:
    return build_case_import_preview_response(await use_case.execute(actor, project_key, body.file_id))


@test_cases_router.post("/projects/{project_key}/test-case-imports/commit", status_code=status.HTTP_201_CREATED)
async def commit_test_case_import(
    project_key: str,
    body: CaseImportCommitRequest,
    actor: SignedInActor,
    use_case: Annotated[CommitTestCaseImportUseCase, Depends(get_commit_test_case_import)],
) -> CaseImportResultResponse:
    result = await use_case.execute(actor, project_key, body.file_id, body.indexes)
    return build_case_import_result_response(result)
