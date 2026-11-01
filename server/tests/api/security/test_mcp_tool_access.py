from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import insert_token
from tests.api.runs.run_steps import read_tool_error_code, sign_up_runner
from tests.api.security.mcp_tool_catalog import MCP_TOOL_CALLS
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool

ACCESS_ERROR_CODES = {"PERMISSION_DENIED", "PROJECT_ARCHIVED", "INVALID_API_TOKEN"}


async def call_every_tool(client: AsyncClient, token: str) -> dict[str, str | None]:
    codes: dict[str, str | None] = {}
    for tool_call in MCP_TOOL_CALLS:
        response = await call_tool(client, token, tool_call.name, tool_call.arguments)
        result = response.json()["result"]
        codes[tool_call.name] = read_tool_error_code(response) if result.get("isError") is True else None
    return codes


def find_mismatches(codes: dict[str, str | None], write_code: str) -> list[str]:
    mismatches: list[str] = []
    for tool_call in MCP_TOOL_CALLS:
        code = codes[tool_call.name]
        if tool_call.is_write and code != write_code:
            mismatches.append(f"{tool_call.name} -> {code}")
        if not tool_call.is_write and code in ACCESS_ERROR_CODES:
            mismatches.append(f"{tool_call.name} -> {code}")
    return mismatches


async def test_a_viewer_token_cannot_use_write_tools(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    viewer = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.VIEWER)

    codes = await call_every_tool(client, viewer.token)

    assert find_mismatches(codes, "PERMISSION_DENIED") == []


async def test_a_token_on_an_archived_project_cannot_use_write_tools(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.QC)
    await archive_project(container, project)

    codes = await call_every_tool(client, runner.token)

    assert find_mismatches(codes, "PROJECT_ARCHIVED") == []


async def test_revoked_and_expired_tokens_cannot_use_any_tool(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.QC)
    now = datetime.now(UTC)
    revoked_token = await insert_token(
        container, runner.account.user_id, project.id, now + timedelta(days=30), revoked_at=now
    )
    expired_token = await insert_token(container, runner.account.user_id, project.id, now - timedelta(seconds=1))
    mismatches: list[str] = []

    for label, token in (("revoked", revoked_token), ("expired", expired_token)):
        codes = await call_every_tool(client, token)
        mismatches.extend(
            f"{label} {tool_name} -> {code}" for tool_name, code in codes.items() if code != "INVALID_API_TOKEN"
        )

    assert mismatches == []
