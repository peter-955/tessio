from typing import Annotated
from uuid import UUID

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.story_context.typing.constants import (
    GET_STORY_CONTEXT_DESCRIPTION,
    GET_TEST_FILE_DESCRIPTION,
    MAX_DATA_KEY_LENGTH,
    MAX_RESOLVE_KEYS,
    RESOLVE_DATA_DESCRIPTION,
)
from app.modules.story_context.usecases.get_story_context import GetStoryContextUseCase
from app.modules.story_context.usecases.get_test_file import GetTestFileUseCase
from app.modules.story_context.usecases.resolve_data import ResolveDataUseCase
from app.modules.story_context.utils.story_context_tool_result import (
    build_resolved_data_tool_result,
    build_story_context_tool_result,
    build_test_file_tool_result,
)
from app.shared.common import TessioError
from app.shared.permissions import Capability


def register_story_context_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    get_story_context: GetStoryContextUseCase,
    resolve_data: ResolveDataUseCase,
    get_test_file: GetTestFileUseCase,
) -> None:
    @server.tool(name="get_story_context", description=GET_STORY_CONTEXT_DESCRIPTION)
    async def get_story_context_tool(story_key: str, context: Context) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, Capability.STORY_VIEW)
            story_context = await get_story_context.execute_in_token_project(actor, story_key)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_story_context_tool_result(story_context)

    @server.tool(name="resolve_data", description=RESOLVE_DATA_DESCRIPTION)
    async def resolve_data_tool(
        run_id: UUID,
        keys: Annotated[
            list[Annotated[str, Field(min_length=1, max_length=MAX_DATA_KEY_LENGTH)]],
            Field(min_length=1, max_length=MAX_RESOLVE_KEYS),
        ],
        context: Context,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(
                context.headers, authenticate_api_token, Capability.SECRET_USE_IN_RUN
            )
            resolved_data = await resolve_data.execute_in_token_project(actor, run_id, keys)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_resolved_data_tool_result(resolved_data)

    @server.tool(name="get_test_file", description=GET_TEST_FILE_DESCRIPTION)
    async def get_test_file_tool(
        run_id: UUID, key: str, context: Context, case_id: UUID | None = None
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, Capability.RUN_START)
            test_file_link = await get_test_file.execute_in_token_project(actor, run_id, key, case_id)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_test_file_tool_result(test_file_link)
