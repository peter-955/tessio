from typing import Annotated

from mcp.server.mcpserver import Context, MCPServer
from mcp_types import CallToolResult
from pydantic import Field, StringConstraints

from app.modules.api_tokens import AuthenticateApiTokenUseCase, authenticate_mcp_api_token, build_tool_error_result
from app.modules.plugin import build_mcp_tool_meta
from app.modules.test_data.typing.constants import (
    DATA_ITEM_KEY_PATTERN,
    MAX_DATA_ITEM_VALUE_LENGTH,
    MAX_ENVIRONMENT_NAME_LENGTH,
    SET_TEST_DATA_CAPABILITY,
    SET_TEST_DATA_DESCRIPTION,
)
from app.modules.test_data.typing.enums import DataToolKind
from app.modules.test_data.usecases.set_test_data import SetTestDataUseCase
from app.modules.test_data.utils.saved_data_item_tool_result import build_saved_data_item_tool_result
from app.shared.common import TessioError

DataKey = Annotated[str, StringConstraints(strip_whitespace=True, pattern=DATA_ITEM_KEY_PATTERN)]
DataValue = Annotated[str, Field(min_length=1, max_length=MAX_DATA_ITEM_VALUE_LENGTH)]
EnvironmentName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_ENVIRONMENT_NAME_LENGTH)
]


def register_test_data_tools(
    server: MCPServer, authenticate_api_token: AuthenticateApiTokenUseCase, set_test_data: SetTestDataUseCase
) -> None:
    @server.tool(
        name="set_test_data", description=SET_TEST_DATA_DESCRIPTION, meta=build_mcp_tool_meta(SET_TEST_DATA_CAPABILITY)
    )
    async def set_test_data_tool(
        key: DataKey,
        value: DataValue,
        kind: DataToolKind,
        context: Context,
        environment: EnvironmentName | None = None,
    ) -> CallToolResult:
        try:
            actor = await authenticate_mcp_api_token(context.headers, authenticate_api_token, SET_TEST_DATA_CAPABILITY)
            saved_item = await set_test_data.execute_in_token_project(actor, key, value, kind, environment)
        except TessioError as error:
            return build_tool_error_result(error)
        return build_saved_data_item_tool_result(saved_item)
