from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.api_tokens import get_api_token_actor, get_token_allowed_actor
from app.modules.run_logs.dependencies import get_get_run_log, get_upload_run_log
from app.modules.run_logs.domains.uploaded_run_log.entity import UploadedLogEntry, UploadedRunLog
from app.modules.run_logs.models.run_log_response import RunLogReceiptResponse, RunLogResponse
from app.modules.run_logs.models.upload_run_log_request import UploadRunLogRequest
from app.modules.run_logs.usecases.get_run_log import GetRunLogUseCase
from app.modules.run_logs.usecases.upload_run_log import UploadRunLogUseCase
from app.modules.run_logs.utils.run_log_response import build_run_log_response
from app.shared.permissions import Actor, Capability

run_logs_router = APIRouter(prefix="/api", tags=["run-logs"])


@run_logs_router.post("/runs/{run_id}/log", status_code=status.HTTP_201_CREATED)
async def upload_run_log(
    run_id: UUID,
    body: UploadRunLogRequest,
    actor: Annotated[Actor, Depends(get_api_token_actor(Capability.RUN_START))],
    use_case: Annotated[UploadRunLogUseCase, Depends(get_upload_run_log)],
) -> RunLogReceiptResponse:
    uploaded_log = UploadedRunLog(
        is_cut=body.is_cut,
        input_tokens=body.usage.input_tokens,
        cache_creation_input_tokens=body.usage.cache_creation_input_tokens,
        cache_read_input_tokens=body.usage.cache_read_input_tokens,
        output_tokens=body.usage.output_tokens,
        entries=[UploadedLogEntry.model_validate(entry.model_dump()) for entry in body.entries],
    )
    run_log = await use_case.execute(actor, run_id, uploaded_log)
    return RunLogReceiptResponse(received_at=run_log.received_at, entry_count=len(body.entries))


@run_logs_router.get("/projects/{project_key}/runs/{run_id}/log")
async def get_run_log(
    project_key: str,
    run_id: UUID,
    actor: Annotated[Actor, Depends(get_token_allowed_actor)],
    use_case: Annotated[GetRunLogUseCase, Depends(get_get_run_log)],
    case_id: Annotated[UUID | None, Query(alias="caseId")] = None,
) -> RunLogResponse:
    return build_run_log_response(await use_case.execute(actor, project_key, run_id, case_id))
