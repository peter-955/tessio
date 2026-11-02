from typing import Annotated

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.plugin import build_mcp_tool_meta
from app.modules.suites.typing.constants import GET_SUITE_CONTEXT_CAPABILITY, GET_SUITE_CONTEXT_DESCRIPTION
from app.modules.suites.typing.constants.suite import MAX_SUITE_REFERENCE_LENGTH
from app.modules.suites.usecases.get_suite_context import GetSuiteContextUseCase
from app.modules.suites.utils.suite_context_tool_result import build_suite_context_tool_result
from app.shared.common import TessioError


def register_suite_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    get_suite_context: GetSuiteContextUseCase,
) -> None:
    @server.tool(
        name="get_suite_context",
        description=GET_SUITE_CONTEXT_DESCRIPTION,
        meta=build_mcp_tool_meta(GET_SUITE_CONTEXT_CAPABILITY),
    )
    async def get_suite_context_tool(
        suite: Annotated[str, Field(min_length=1, max_length=MAX_SUITE_REFERENCE_LENGTH)], context: Context
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, GET_SUITE_CONTEXT_CAPABILITY
            )
            suite_context = await get_suite_context.execute_in_token_project(actor, suite)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_suite_context_tool_result(suite_context)
