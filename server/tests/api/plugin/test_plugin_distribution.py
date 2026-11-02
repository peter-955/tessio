import hashlib
import io
import json
import zipfile

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import read_tool_error, seed_story
from tests.api.projects.user_steps import sign_up_as
from tests.api.test_data.project_steps import add_member, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import CURRENT_PLUGIN_VERSION, call_tool, read_tool_json

MARKETPLACE_PATH = "/api/plugin/marketplace.json"
ARCHIVE_NAME = f"tessio-{CURRENT_PLUGIN_VERSION}.zip"


async def seed_token(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> tuple[str, str]:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_member(container, project, account.user_id, ProjectRole.QC)
    return story.jira_key, await create_token(client, project.key)


async def test_the_marketplace_lists_the_served_plugin_archive(client: AsyncClient) -> None:
    response = await client.get(MARKETPLACE_PATH)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"
    archive = (await client.get(f"/api/plugin/{ARCHIVE_NAME}")).content
    assert response.json() == {
        "name": "tessio",
        "description": "The Tessio Claude Code plugin, served by this Tessio server",
        "owner": {"name": "Tessio team"},
        "plugins": [
            {
                "name": "tessio",
                "description": "Run Tessio test cases with Claude: MCP server, screenshot upload hook and skills",
                "version": CURRENT_PLUGIN_VERSION,
                "source": {
                    "source": "archive",
                    "url": f"https://tessio.test/api/plugin/{ARCHIVE_NAME}",
                    "sha256": hashlib.sha256(archive).hexdigest(),
                },
            }
        ],
    }


async def test_the_archive_holds_the_plugin_without_its_tests(client: AsyncClient) -> None:
    response = await client.get(f"/api/plugin/{ARCHIVE_NAME}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read(".claude-plugin/plugin.json"))
    assert manifest["version"] == CURRENT_PLUGIN_VERSION
    assert {
        ".mcp.json",
        "hooks/hooks.json",
        "hooks/upload_screenshots.py",
        "scripts/extract_file.py",
        "skills/import-cases/SKILL.md",
        "skills/run-story-tests/references/execute-cases.md",
        "skills/run-suite/SKILL.md",
    } <= names
    assert not any("/tests/" in name or "__pycache__" in name or name.endswith(".pyc") for name in names)


async def test_an_unknown_archive_name_is_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/plugin/tessio-0.0.1.zip")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.parametrize("plugin_version", [CURRENT_PLUGIN_VERSION, "99.0.0"])
async def test_mcp_accepts_the_current_or_a_newer_plugin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, plugin_version: str
) -> None:
    story_key, token = await seed_token(client, container, recording_mailer)

    response = await call_tool(client, token, "get_open_gaps", {"story_key": story_key}, plugin_version)

    assert read_tool_json(response)["open_gap_count"] == 0


@pytest.mark.parametrize(
    ("plugin_version", "sent"), [(None, "no version"), ("0.1.0", "version 0.1.0"), ("v2", "version v2")]
)
async def test_mcp_refuses_a_missing_older_or_unreadable_plugin_version(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, plugin_version: str | None, sent: str
) -> None:
    story_key, token = await seed_token(client, container, recording_mailer)

    response = await call_tool(client, token, "get_open_gaps", {"story_key": story_key}, plugin_version)

    assert read_tool_error(response) == (
        f"PLUGIN_OUTDATED: Your Tessio plugin sent {sent}; this Tessio needs {CURRENT_PLUGIN_VERSION}. "
        "Run `claude plugin marketplace update tessio && claude plugin update tessio@tessio`, then restart Claude Code."
    )


async def test_an_unknown_token_is_refused_before_the_plugin_version(client: AsyncClient) -> None:
    response = await call_tool(client, "tsio_unknown", "get_open_gaps", {"story_key": "SHOP-1"}, "0.1.0")

    assert read_tool_error(response).startswith("INVALID_API_TOKEN: ")


@pytest.mark.parametrize("plugin_version", ["0.1.0", CURRENT_PLUGIN_VERSION])
async def test_mcp_saves_the_plugin_version_on_the_token_even_when_it_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, plugin_version: str
) -> None:
    story_key, token = await seed_token(client, container, recording_mailer)

    await call_tool(client, token, "get_open_gaps", {"story_key": story_key}, plugin_version)

    tokens = (await client.get("/api/me/api-tokens")).json()
    assert [listed["pluginVersion"] for listed in tokens] == [plugin_version]


async def test_a_call_without_a_plugin_version_keeps_the_saved_one(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    story_key, token = await seed_token(client, container, recording_mailer)
    await call_tool(client, token, "get_open_gaps", {"story_key": story_key})

    await call_tool(client, token, "get_open_gaps", {"story_key": story_key}, None)

    tokens = (await client.get("/api/me/api-tokens")).json()
    assert [listed["pluginVersion"] for listed in tokens] == [CURRENT_PLUGIN_VERSION]
