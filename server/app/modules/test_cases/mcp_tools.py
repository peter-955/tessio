from typing import Annotated

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.plugin import build_mcp_tool_meta
from app.modules.test_cases.models.draft_case_tool_input import DraftCaseToolInput
from app.modules.test_cases.typing.constants import (
    CHECK_DRAFT_CASES_CAPABILITY,
    CHECK_DRAFT_CASES_DESCRIPTION,
    CREATE_DRAFT_CASES_CAPABILITY,
    CREATE_DRAFT_CASES_DESCRIPTION,
    MAX_DRAFT_CASES_PER_CALL,
)
from app.modules.test_cases.usecases.check_draft_cases import CheckDraftCasesUseCase
from app.modules.test_cases.usecases.create_draft_cases import CreateDraftCasesUseCase
from app.modules.test_cases.utils.draft_case_input import build_imported_case
from app.modules.test_cases.utils.draft_case_tool_result import (
    build_checked_draft_cases_tool_result,
    build_created_draft_cases_tool_result,
)
from app.shared.common import TessioError


def register_test_case_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    check_draft_cases: CheckDraftCasesUseCase,
    create_draft_cases: CreateDraftCasesUseCase,
) -> None:
    @server.tool(
        name="check_draft_cases",
        description=CHECK_DRAFT_CASES_DESCRIPTION,
        meta=build_mcp_tool_meta(CHECK_DRAFT_CASES_CAPABILITY),
    )
    async def check_draft_cases_tool(
        cases: Annotated[list[DraftCaseToolInput], Field(min_length=1, max_length=MAX_DRAFT_CASES_PER_CALL)],
        context: Context,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, CHECK_DRAFT_CASES_CAPABILITY
            )
            items = await check_draft_cases.execute_in_token_project(
                actor, [build_imported_case(case) for case in cases]
            )
        except TessioError as error:
            return build_tool_error_result(error)
        return build_checked_draft_cases_tool_result(items)

    @server.tool(
        name="create_draft_cases",
        description=CREATE_DRAFT_CASES_DESCRIPTION,
        meta=build_mcp_tool_meta(CREATE_DRAFT_CASES_CAPABILITY),
    )
    async def create_draft_cases_tool(
        cases: Annotated[list[DraftCaseToolInput], Field(min_length=1, max_length=MAX_DRAFT_CASES_PER_CALL)],
        context: Context,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, CREATE_DRAFT_CASES_CAPABILITY
            )
            result = await create_draft_cases.execute_in_token_project(
                actor, [build_imported_case(case) for case in cases]
            )
        except TessioError as error:
            return build_tool_error_result(error)
        return build_created_draft_cases_tool_result(result)
