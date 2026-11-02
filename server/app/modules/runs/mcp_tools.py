from typing import Annotated
from uuid import UUID

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.plugin import build_mcp_tool_meta
from app.modules.runs.domains.case_report.entity import CaseReport
from app.modules.runs.domains.step_report.entity import StepReport
from app.modules.runs.models.step_report_input import StepReportInput
from app.modules.runs.typing.constants.run import (
    MAX_DIAGNOSIS_TEXT_LENGTH,
    MAX_STEPS_PER_CASE,
    MAX_SUITE_REFERENCE_LENGTH,
    MAX_SUMMARY_LENGTH,
)
from app.modules.runs.typing.constants.tool_capability import (
    FINISH_RUN_CAPABILITY,
    GET_FAILED_CASES_CAPABILITY,
    RECORD_CASE_RESULT_CAPABILITY,
    START_RUN_CAPABILITY,
)
from app.modules.runs.typing.constants.tool_description import (
    FINISH_RUN_DESCRIPTION,
    GET_FAILED_CASES_DESCRIPTION,
    RECORD_CASE_RESULT_DESCRIPTION,
    START_RUN_DESCRIPTION,
)
from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.modules.runs.usecases.finish_run import FinishRunUseCase
from app.modules.runs.usecases.get_failed_cases import GetFailedCasesUseCase
from app.modules.runs.usecases.record_case_result import RecordCaseResultUseCase
from app.modules.runs.usecases.start_run import StartRunUseCase
from app.modules.runs.utils.run_tool_result import (
    build_case_result_tool_result,
    build_failed_cases_tool_result,
    build_finished_run_tool_result,
    build_started_run_tool_result,
)
from app.shared.common import TessioError


def register_run_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    start_run: StartRunUseCase,
    record_case_result: RecordCaseResultUseCase,
    finish_run: FinishRunUseCase,
    get_failed_cases: GetFailedCasesUseCase,
) -> None:
    @server.tool(name="start_run", description=START_RUN_DESCRIPTION, meta=build_mcp_tool_meta(START_RUN_CAPABILITY))
    async def start_run_tool(
        context: Context,
        story_key: str | None = None,
        suite: Annotated[str | None, Field(min_length=1, max_length=MAX_SUITE_REFERENCE_LENGTH)] = None,
        environment: str | None = None,
        case_ids: list[UUID] | None = None,
        parent_run_id: UUID | None = None,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, START_RUN_CAPABILITY)
            started_run = await start_run.execute(actor, story_key, environment, case_ids, parent_run_id, suite)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_started_run_tool_result(started_run)

    @server.tool(
        name="record_case_result",
        description=RECORD_CASE_RESULT_DESCRIPTION,
        meta=build_mcp_tool_meta(RECORD_CASE_RESULT_CAPABILITY),
    )
    async def record_case_result_tool(
        run_id: UUID,
        case_id: UUID,
        status: ResultStatus,
        duration_ms: Annotated[int, Field(ge=0)],
        steps: Annotated[list[StepReportInput], Field(min_length=1, max_length=MAX_STEPS_PER_CASE)],
        context: Context,
        suspected_cause: SuspectedCause | None = None,
        cause_reason: Annotated[str | None, Field(max_length=MAX_DIAGNOSIS_TEXT_LENGTH)] = None,
        iteration: Annotated[int, Field(ge=0)] = 0,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, RECORD_CASE_RESULT_CAPABILITY
            )
            case_result_id = await record_case_result.execute(
                actor,
                CaseReport(
                    run_id=run_id,
                    case_id=case_id,
                    status=status,
                    duration_ms=duration_ms,
                    steps=[StepReport.model_validate(step.model_dump()) for step in steps],
                    suspected_cause=suspected_cause,
                    cause_reason=cause_reason,
                    iteration=iteration,
                ),
            )
        except TessioError as error:
            return build_tool_error_result(error)
        return build_case_result_tool_result(case_result_id)

    @server.tool(name="finish_run", description=FINISH_RUN_DESCRIPTION, meta=build_mcp_tool_meta(FINISH_RUN_CAPABILITY))
    async def finish_run_tool(
        run_id: UUID,
        context: Context,
        summary: Annotated[str | None, Field(max_length=MAX_SUMMARY_LENGTH)] = None,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, FINISH_RUN_CAPABILITY)
            finished_run = await finish_run.execute(actor, run_id, summary)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_finished_run_tool_result(finished_run)

    @server.tool(
        name="get_failed_cases",
        description=GET_FAILED_CASES_DESCRIPTION,
        meta=build_mcp_tool_meta(GET_FAILED_CASES_CAPABILITY),
    )
    async def get_failed_cases_tool(run_id: UUID, context: Context) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, GET_FAILED_CASES_CAPABILITY
            )
            failed_cases = await get_failed_cases.execute(actor, run_id)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_failed_cases_tool_result(failed_cases)
