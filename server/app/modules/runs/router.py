from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.modules.api_tokens import get_api_token_actor, get_token_allowed_actor
from app.modules.runs.dependencies import (
    get_create_screenshot_upload,
    get_get_run,
    get_import_junit_run,
    get_list_runs,
)
from app.modules.runs.errors import JunitFileTooLargeError
from app.modules.runs.models.junit_import_response import JunitImportResponse
from app.modules.runs.models.run_detail_response import RunDetailResponse
from app.modules.runs.models.run_summary_response import RunSummaryResponse
from app.modules.runs.models.screenshot_upload_response import ScreenshotUploadResponse
from app.modules.runs.typing.constants.junit import MAX_IMPORT_REFERENCE_LENGTH, MAX_JUNIT_FILE_BYTES
from app.modules.runs.typing.constants.run import DEFAULT_RUN_LIST_LIMIT, MAX_RUN_LIST_LIMIT
from app.modules.runs.typing.enums import RunStatus
from app.modules.runs.usecases.create_screenshot_upload import CreateScreenshotUploadUseCase
from app.modules.runs.usecases.get_run import GetRunUseCase
from app.modules.runs.usecases.import_junit_run import ImportJunitRunUseCase
from app.modules.runs.usecases.list_runs import ListRunsUseCase
from app.modules.runs.utils.run_responses import (
    build_junit_import_response,
    build_run_detail_response,
    build_run_summary_response,
)
from app.shared.permissions import Actor, Capability

runs_router = APIRouter(prefix="/api", tags=["runs"])

TokenAllowedActor = Annotated[Actor, Depends(get_token_allowed_actor)]


@runs_router.get("/projects/{project_key}/runs")
async def list_runs(
    project_key: str,
    actor: TokenAllowedActor,
    use_case: Annotated[ListRunsUseCase, Depends(get_list_runs)],
    story_key: Annotated[str | None, Query(alias="storyKey")] = None,
    run_status: Annotated[RunStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_RUN_LIST_LIMIT)] = DEFAULT_RUN_LIST_LIMIT,
    suite_id: Annotated[UUID | None, Query(alias="suiteId")] = None,
) -> list[RunSummaryResponse]:
    summaries = await use_case.execute(actor, project_key, story_key, run_status, limit, suite_id)
    return [build_run_summary_response(summary) for summary in summaries]


@runs_router.get("/projects/{project_key}/runs/{run_id}")
async def get_run(
    project_key: str,
    run_id: UUID,
    actor: TokenAllowedActor,
    use_case: Annotated[GetRunUseCase, Depends(get_get_run)],
) -> RunDetailResponse:
    return build_run_detail_response(await use_case.execute(actor, project_key, run_id))


@runs_router.post("/runs/{run_id}/case-results/{case_result_id}/screenshot-upload")
async def create_screenshot_upload(
    run_id: UUID,
    case_result_id: UUID,
    actor: Annotated[Actor, Depends(get_api_token_actor(Capability.RUN_START))],
    use_case: Annotated[CreateScreenshotUploadUseCase, Depends(get_create_screenshot_upload)],
) -> ScreenshotUploadResponse:
    signed_upload = await use_case.execute(actor, run_id, case_result_id)
    return ScreenshotUploadResponse(
        url=signed_upload.url, fields=signed_upload.fields, key_prefix=signed_upload.key_prefix
    )


@runs_router.post("/projects/{project_key}/runs/import", status_code=status.HTTP_201_CREATED)
async def import_junit_run(
    project_key: str,
    actor: TokenAllowedActor,
    use_case: Annotated[ImportJunitRunUseCase, Depends(get_import_junit_run)],
    file: Annotated[UploadFile, File(description="A JUnit XML file of 10 MB at most.")],
    environment: Annotated[str, Form(min_length=1, max_length=MAX_IMPORT_REFERENCE_LENGTH)],
    suite: Annotated[str | None, Form(min_length=1, max_length=MAX_IMPORT_REFERENCE_LENGTH)] = None,
) -> JunitImportResponse:
    content = await file.read(MAX_JUNIT_FILE_BYTES + 1)
    if len(content) > MAX_JUNIT_FILE_BYTES:
        raise JunitFileTooLargeError
    return build_junit_import_response(await use_case.execute(actor, project_key, content, environment, suite))
