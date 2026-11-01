from typing import Annotated

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.gaps.domains.gap_draft.entity import GapDraft
from app.modules.gaps.models.gap_tool_input import GapToolInput
from app.modules.gaps.typing.constants import GET_OPEN_GAPS_DESCRIPTION, MAX_GAPS_PER_CALL, RAISE_GAPS_DESCRIPTION
from app.modules.gaps.usecases.get_open_gaps import GetOpenGapsUseCase
from app.modules.gaps.usecases.raise_gaps import RaiseGapsUseCase
from app.modules.gaps.utils.gap_tool_result import build_open_gaps_tool_result, build_raised_gaps_tool_result
from app.shared.common import TessioError
from app.shared.permissions import Capability


def register_gap_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    raise_gaps: RaiseGapsUseCase,
    get_open_gaps: GetOpenGapsUseCase,
) -> None:
    @server.tool(name="raise_gaps", description=RAISE_GAPS_DESCRIPTION)
    async def raise_gaps_tool(
        story_key: str,
        gaps: Annotated[list[GapToolInput], Field(min_length=1, max_length=MAX_GAPS_PER_CALL)],
        context: Context,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, Capability.GAP_RAISE)
            raised_gaps = await raise_gaps.execute_in_token_project(
                actor,
                story_key,
                [
                    GapDraft(
                        type=gap.type,
                        severity=gap.severity,
                        target_type=gap.target_type,
                        target_ref=gap.target_ref,
                        question=gap.question,
                        data_scope=gap.data_scope,
                        assignee_id=None,
                    )
                    for gap in gaps
                ],
            )
        except TessioError as error:
            return build_tool_error_result(error)
        return build_raised_gaps_tool_result(raised_gaps)

    @server.tool(name="get_open_gaps", description=GET_OPEN_GAPS_DESCRIPTION)
    async def get_open_gaps_tool(story_key: str, context: Context) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, Capability.GAP_VIEW)
            open_gaps = await get_open_gaps.execute_in_token_project(actor, story_key)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_open_gaps_tool_result(open_gaps)
