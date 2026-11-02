from httpx import AsyncClient, Response

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import sign_up_as
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import CURRENT_PLUGIN_VERSION

AI_HARNESS_PATH = "/api/ai-harness"
MCP_TOOL_NAMES = {
    "answer_gap",
    "check_draft_cases",
    "create_draft_cases",
    "finish_run",
    "get_failed_cases",
    "get_my_gaps",
    "get_open_gaps",
    "get_story_context",
    "get_suite_context",
    "get_test_file",
    "raise_gaps",
    "reassign_gap",
    "record_case_result",
    "resolve_data",
    "set_test_data",
    "start_run",
}


async def read_ai_harness(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> Response:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    response = await client.get(AI_HARNESS_PATH)
    assert response.status_code == 200
    return response


async def test_the_harness_shows_the_server_and_plugin_versions(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    harness = (await read_ai_harness(client, container, recording_mailer)).json()

    assert harness["server"] == {"version": "0.1.0", "buildCommit": None}
    assert harness["plugin"]["name"] == "tessio"
    assert harness["plugin"]["version"] == CURRENT_PLUGIN_VERSION
    assert harness["plugin"]["updateCommand"] == (
        "claude plugin marketplace update tessio && claude plugin update tessio@tessio"
    )


async def test_the_harness_lists_the_skills_as_slash_commands(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    harness = (await read_ai_harness(client, container, recording_mailer)).json()

    skills = {skill["name"]: skill for skill in harness["skills"]}
    assert set(skills) == {
        "answer-gaps",
        "draft-cases",
        "import-cases",
        "rerun-failed",
        "review-readiness",
        "run-story-tests",
        "run-suite",
    }
    assert skills["run-suite"]["command"] == "/tessio:run-suite"
    assert skills["run-suite"]["argumentHint"] == "<suite> [environment] [case codes]"
    assert skills["run-story-tests"]["command"] == "/tessio:run-story-tests"
    assert skills["run-story-tests"]["argumentHint"] == "<STORY-KEY> [environment] [case codes]"
    assert skills["run-story-tests"]["description"].startswith("Run the Ready Tessio test cases")
    assert harness["commands"] == []


async def test_the_harness_lists_the_hooks_by_tool_and_script(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    harness = (await read_ai_harness(client, container, recording_mailer)).json()

    assert harness["hooks"] == [
        {
            "event": "PostToolUse",
            "toolName": "record_case_result",
            "script": "hooks/upload_screenshots.py",
            "timeoutSeconds": 120,
        },
        {"event": "PostToolUse", "toolName": "finish_run", "script": "hooks/upload_run_log.py", "timeoutSeconds": 120},
    ]


async def test_the_harness_shows_the_mcp_server_and_every_tool_with_its_capability(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    harness = (await read_ai_harness(client, container, recording_mailer)).json()

    assert harness["mcpServers"] == [
        {
            "name": "tessio",
            "transport": "http",
            "url": "https://tessio.test/mcp",
            "headerNames": ["Authorization", "X-Tessio-Plugin-Version"],
        }
    ]
    tools = {tool["name"]: tool for tool in harness["mcpTools"]}
    assert set(tools) == MCP_TOOL_NAMES
    assert all(tool["capability"] is not None and tool["description"] for tool in tools.values())
    assert tools["start_run"]["capability"] == "run.start"
    assert tools["start_run"]["roles"] == ["admin", "qc", "dev"]
    assert tools["get_open_gaps"]["roles"] == ["admin", "pm", "ba", "qc", "dev", "viewer"]
    assert tools["check_draft_cases"]["roles"] == ["admin", "qc"]


async def test_the_harness_needs_a_session(client: AsyncClient) -> None:
    client.cookies.clear()

    response = await client.get(AI_HARNESS_PATH)

    assert response.status_code == 401
