from typing import Annotated
from uuid import UUID

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field, StringConstraints

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.gaps.domains.gap_draft.entity import GapDraft
from app.modules.gaps.models.gap_tool_input import GapToolInput
from app.modules.gaps.typing.constants import (
    ANSWER_GAP_CAPABILITY,
    ANSWER_GAP_DESCRIPTION,
    GET_MY_GAPS_CAPABILITY,
    GET_MY_GAPS_DESCRIPTION,
    GET_OPEN_GAPS_CAPABILITY,
    GET_OPEN_GAPS_DESCRIPTION,
    MAX_ANSWER_LENGTH,
    MAX_GAPS_PER_CALL,
    RAISE_GAPS_CAPABILITY,
    RAISE_GAPS_DESCRIPTION,
    REASSIGN_GAP_CAPABILITY,
    REASSIGN_GAP_DESCRIPTION,
)
from app.modules.gaps.usecases.answer_gap import AnswerGapUseCase
from app.modules.gaps.usecases.get_my_gaps import GetMyGapsUseCase
from app.modules.gaps.usecases.get_open_gaps import GetOpenGapsUseCase
from app.modules.gaps.usecases.raise_gaps import RaiseGapsUseCase
from app.modules.gaps.usecases.reassign_gap import ReassignGapUseCase
from app.modules.gaps.utils.gap_route import build_requested_gap_route
from app.modules.gaps.utils.gap_tool_result import (
    build_answered_gap_tool_result,
    build_my_gaps_tool_result,
    build_open_gaps_tool_result,
    build_raised_gaps_tool_result,
    build_reassigned_gap_tool_result,
)
from app.modules.plugin import build_mcp_tool_meta
from app.shared.common import TessioError
from app.shared.permissions import ProjectRole

GapAnswer = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_ANSWER_LENGTH)]


def register_gap_tools(
    server: MCPServer,
    authenticate_api_token: AuthenticateApiTokenUseCase,
    raise_gaps: RaiseGapsUseCase,
    get_open_gaps: GetOpenGapsUseCase,
    get_my_gaps: GetMyGapsUseCase,
    answer_gap: AnswerGapUseCase,
    reassign_gap: ReassignGapUseCase,
) -> None:
    @server.tool(name="raise_gaps", description=RAISE_GAPS_DESCRIPTION, meta=build_mcp_tool_meta(RAISE_GAPS_CAPABILITY))
    async def raise_gaps_tool(
        story_key: str,
        gaps: Annotated[list[GapToolInput], Field(min_length=1, max_length=MAX_GAPS_PER_CALL)],
        context: Context,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, RAISE_GAPS_CAPABILITY)
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

    @server.tool(
        name="get_open_gaps", description=GET_OPEN_GAPS_DESCRIPTION, meta=build_mcp_tool_meta(GET_OPEN_GAPS_CAPABILITY)
    )
    async def get_open_gaps_tool(story_key: str, context: Context) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, GET_OPEN_GAPS_CAPABILITY)
            open_gaps = await get_open_gaps.execute_in_token_project(actor, story_key)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_open_gaps_tool_result(open_gaps)

    @server.tool(
        name="get_my_gaps", description=GET_MY_GAPS_DESCRIPTION, meta=build_mcp_tool_meta(GET_MY_GAPS_CAPABILITY)
    )
    async def get_my_gaps_tool(context: Context, story_key: str | None = None) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, GET_MY_GAPS_CAPABILITY)
            my_gaps = await get_my_gaps.execute_in_token_project(actor, story_key)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_my_gaps_tool_result(my_gaps)

    @server.tool(name="answer_gap", description=ANSWER_GAP_DESCRIPTION, meta=build_mcp_tool_meta(ANSWER_GAP_CAPABILITY))
    async def answer_gap_tool(gap_id: UUID, answer: GapAnswer, context: Context) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, ANSWER_GAP_CAPABILITY)
            answered_gap = await answer_gap.execute_in_token_project(actor, gap_id, answer)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_answered_gap_tool_result(answered_gap)

    @server.tool(
        name="reassign_gap", description=REASSIGN_GAP_DESCRIPTION, meta=build_mcp_tool_meta(REASSIGN_GAP_CAPABILITY)
    )
    async def reassign_gap_tool(
        gap_id: UUID,
        context: Context,
        assignee_user_id: UUID | None = None,
        assignee_role: ProjectRole | None = None,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, REASSIGN_GAP_CAPABILITY)
            route = build_requested_gap_route(assignee_user_id, assignee_role)
            view = await reassign_gap.execute_in_token_project(actor, gap_id, route)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_reassigned_gap_tool_result(view)
