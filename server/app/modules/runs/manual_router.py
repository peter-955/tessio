from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

from app.modules.projects import get_signed_in_actor
from app.modules.runs.dependencies import (
    get_create_manual_run,
    get_finish_manual_run,
    get_record_manual_case_result,
    get_rerun_failed_cases,
)
from app.modules.runs.domains.manual_case_report.entity import ManualCaseReport
from app.modules.runs.domains.manual_step_report.entity import ManualStepReport
from app.modules.runs.models.manual_case_result_request import ManualCaseResultRequest
from app.modules.runs.models.manual_case_result_response import ManualCaseResultResponse
from app.modules.runs.models.manual_finish_request import ManualFinishRequest
from app.modules.runs.models.manual_rerun_request import ManualRerunRequest
from app.modules.runs.models.manual_run_create_request import ManualRunCreateRequest
from app.modules.runs.models.manual_run_response import ManualRunResponse
from app.modules.runs.typing.enums import RunExecutor
from app.modules.runs.usecases.create_manual_run import CreateManualRunUseCase
from app.modules.runs.usecases.finish_manual_run import FinishManualRunUseCase
from app.modules.runs.usecases.record_manual_case_result import RecordManualCaseResultUseCase
from app.modules.runs.usecases.rerun_failed_cases import RerunFailedCasesUseCase
from app.modules.runs.utils.manual_run_response import build_manual_case_result_response, build_manual_run_response
from app.shared.permissions import Actor

manual_runs_router = APIRouter(prefix="/api", tags=["runs"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@manual_runs_router.post("/projects/{project_key}/runs", status_code=status.HTTP_201_CREATED)
async def create_manual_run(
    project_key: str,
    body: ManualRunCreateRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateManualRunUseCase, Depends(get_create_manual_run)],
) -> ManualRunResponse:
    sheet = await use_case.execute(actor, project_key, body.story_key, body.environment_id, body.test_case_ids)
    return build_manual_run_response(sheet)


@manual_runs_router.put("/projects/{project_key}/runs/{run_id}/cases/{test_case_id}")
async def record_manual_case_result(
    project_key: str,
    run_id: UUID,
    test_case_id: UUID,
    body: ManualCaseResultRequest,
    actor: SignedInActor,
    use_case: Annotated[RecordManualCaseResultUseCase, Depends(get_record_manual_case_result)],
) -> ManualCaseResultResponse:
    report = ManualCaseReport(
        status=body.status,
        duration_ms=body.duration_ms,
        steps=[
            ManualStepReport(
                order=step.order,
                status=step.status,
                actual_result=step.actual_result,
                error=step.error,
                evidence_file_id=step.evidence_file_id,
            )
            for step in body.steps
        ],
    )
    recorded = await use_case.execute(actor, project_key, run_id, test_case_id, report)
    return build_manual_case_result_response(recorded)


@manual_runs_router.post("/projects/{project_key}/runs/{run_id}/finish")
async def finish_manual_run(
    project_key: str,
    run_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[FinishManualRunUseCase, Depends(get_finish_manual_run)],
    body: Annotated[ManualFinishRequest | None, Body()] = None,
) -> ManualRunResponse:
    run = await use_case.execute(actor, project_key, run_id, None if body is None else body.summary)
    return build_manual_run_response(run)


@manual_runs_router.post("/projects/{project_key}/runs/{run_id}/rerun-failed", status_code=status.HTTP_201_CREATED)
async def rerun_failed_cases(
    project_key: str,
    run_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RerunFailedCasesUseCase, Depends(get_rerun_failed_cases)],
    body: Annotated[ManualRerunRequest | None, Body()] = None,
) -> ManualRunResponse:
    sheet = await use_case.execute(
        actor, project_key, run_id, RunExecutor.MANUAL, None if body is None else body.environment_id
    )
    return build_manual_run_response(sheet)
