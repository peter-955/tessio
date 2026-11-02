import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import (
    SeededStory,
    add_active_member,
    answer_gap,
    raise_gap_id,
    read_tool_error,
    seed_story,
    seed_test_case,
)
from tests.api.projects.user_steps import SignedUpAccount, deactivate_user, sign_up_as, use_session
from tests.api.test_data.project_steps import SeededProject, add_member, archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

TOOL_GAPS: list[dict[str, object]] = [
    {"type": "missing_ac", "severity": "high", "target_type": "story", "target_ref": None, "question": "Refunds?"},
    {"type": "unclear_goal", "target_type": "criterion", "target_ref": "AC1", "question": "Which page counts?"},
    {"type": "missing_step", "target_type": "test_case", "target_ref": "TC-3", "question": "What is clicked?"},
]


async def seed_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> tuple[SeededProject, SeededStory, SignedUpAccount, str]:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Claude Owner")
    await add_member(container, project, account.user_id, role)
    await seed_test_case(container, project, story.id, 3, account.user_id)
    token = await create_token(client, project.key)
    return project, story, account, token


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.BA, ProjectRole.PM, ProjectRole.ADMIN])
async def test_raise_gaps_files_every_gap_and_reports_readiness(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, story, account, token = await seed_token(client, container, recording_mailer, role)

    response = await call_tool(client, token, "raise_gaps", {"story_key": story.jira_key, "gaps": TOOL_GAPS})

    content = read_tool_json(response)
    assert content.keys() == {"gap_ids", "open_gap_count", "is_ready"}
    assert content["open_gap_count"] == 3
    assert content["is_ready"] is False
    gap_ids = content["gap_ids"]
    assert isinstance(gap_ids, list)
    assert len(gap_ids) == 3
    use_session(client, account.session_token)
    listed = await client.get(f"/api/projects/{project.key}/gaps")
    gaps_by_id = {gap["id"]: gap for gap in listed.json()}
    assert [gaps_by_id[gap_id]["targetRef"] for gap_id in gap_ids] == [None, "AC1", "TC-3"]
    assert [gaps_by_id[gap_id]["severity"] for gap_id in gap_ids] == ["high", "medium", "medium"]
    assert all(gaps_by_id[gap_id]["isRaisedViaClaude"] for gap_id in gap_ids)
    assert all(gaps_by_id[gap_id]["raisedBy"] == str(account.user_id) for gap_id in gap_ids)


async def test_raise_gaps_is_refused_for_viewers(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, _, token = await seed_token(client, container, recording_mailer, ProjectRole.VIEWER)

    response = await call_tool(client, token, "raise_gaps", {"story_key": story.jira_key, "gaps": TOOL_GAPS})

    assert read_tool_error(response).startswith("PERMISSION_DENIED: ")


async def test_raise_gaps_is_refused_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, story, _, token = await seed_token(client, container, recording_mailer, ProjectRole.QC)
    await archive_project(container, project)

    response = await call_tool(client, token, "raise_gaps", {"story_key": story.jira_key, "gaps": TOOL_GAPS})

    assert read_tool_error(response).startswith("PROJECT_ARCHIVED: ")


async def test_raise_gaps_refuses_an_unknown_target_and_files_nothing(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, _, token = await seed_token(client, container, recording_mailer, ProjectRole.QC)
    gaps = [*TOOL_GAPS, {"type": "unclear_goal", "target_type": "criterion", "target_ref": "AC7", "question": "?"}]

    response = await call_tool(client, token, "raise_gaps", {"story_key": story.jira_key, "gaps": gaps})
    open_gaps = await call_tool(client, token, "get_open_gaps", {"story_key": story.jira_key})

    assert read_tool_error(response) == "UNKNOWN_REFERENCE: AC7 is not on this story."
    assert read_tool_json(open_gaps)["open_gap_count"] == 0


async def test_raise_gaps_refuses_an_unknown_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, _, token = await seed_token(client, container, recording_mailer, ProjectRole.QC)

    response = await call_tool(client, token, "raise_gaps", {"story_key": "NOPE-1", "gaps": TOOL_GAPS})

    assert read_tool_error(response) == "NOT_FOUND: Story not found."


async def test_raise_gaps_needs_a_token(client: AsyncClient) -> None:
    response = await call_tool(client, None, "raise_gaps", {"story_key": "SHOP-1", "gaps": TOOL_GAPS})

    assert read_tool_error(response).startswith("INVALID_API_TOKEN: ")


@pytest.mark.parametrize("gap_count", [0, 51])
async def test_raise_gaps_needs_one_to_fifty_gaps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, gap_count: int
) -> None:
    _, story, _, token = await seed_token(client, container, recording_mailer, ProjectRole.QC)
    gaps = [{"type": "other", "question": f"Question {index}"} for index in range(gap_count)]

    response = await call_tool(client, token, "raise_gaps", {"story_key": story.jira_key, "gaps": gaps})

    assert response.json()["result"]["isError"] is True


@pytest.mark.parametrize("is_archived", [False, True])
async def test_get_open_gaps_lists_only_open_gaps_for_viewers(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, is_archived: bool
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    raiser = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_member(container, project, raiser.user_id, ProjectRole.QC)
    open_id = await raise_gap_id(
        client, project.key, story, severity="low", targetType="criterion", targetRef="AC1", question="Which page?"
    )
    resolved_id = await raise_gap_id(client, project.key, story)
    assert (await answer_gap(client, project.key, resolved_id)).status_code == 200
    viewer = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_member(container, project, viewer.user_id, ProjectRole.VIEWER)
    token = await create_token(client, project.key)
    if is_archived:
        await archive_project(container, project)

    response = await call_tool(client, token, "get_open_gaps", {"story_key": story.jira_key.lower()})

    assert read_tool_json(response) == {
        "open_gap_count": 1,
        "is_ready": False,
        "gaps": [
            {
                "id": open_id,
                "type": "missing_ac",
                "severity": "low",
                "target_type": "criterion",
                "target_ref": "AC1",
                "question": "Which page?",
                "assignee_name": "Bao Analyst",
            }
        ],
    }


async def test_get_open_gaps_names_the_role_queue_and_a_deactivated_assignee(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    await add_active_member(container, recording_mailer, project, ProjectRole.QC, "Quinn Checker")
    await add_active_member(container, recording_mailer, project, ProjectRole.QC, "Quentin Checker")
    developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Dana Dev")
    raiser = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_member(container, project, raiser.user_id, ProjectRole.ADMIN)
    queued_id = await raise_gap_id(client, project.key, story, type="missing_step", question="Which button?")
    assigned_id = await raise_gap_id(
        client, project.key, story, type="missing_test_data", dataScope="environment", question="Staging user?"
    )
    await deactivate_user(container, developer_id)
    token = await create_token(client, project.key)

    response = await call_tool(client, token, "get_open_gaps", {"story_key": story.jira_key})

    gaps = read_tool_json(response)["gaps"]
    assert isinstance(gaps, list)
    assignees = {
        gap["id"]: {key: gap.get(key) for key in ("assignee_name", "assignee_role", "is_assignee_deactivated")}
        for gap in gaps
        if isinstance(gap, dict)
    }
    assert assignees == {
        queued_id: {"assignee_name": None, "assignee_role": "qc", "is_assignee_deactivated": None},
        assigned_id: {"assignee_name": "Dana Dev", "assignee_role": None, "is_assignee_deactivated": True},
    }


async def test_get_open_gaps_reports_a_ready_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, _, token = await seed_token(client, container, recording_mailer, ProjectRole.VIEWER)

    response = await call_tool(client, token, "get_open_gaps", {"story_key": story.jira_key})

    assert read_tool_json(response) == {"open_gap_count": 0, "is_ready": True, "gaps": []}


async def test_get_open_gaps_needs_a_token(client: AsyncClient) -> None:
    response = await call_tool(client, None, "get_open_gaps", {"story_key": "SHOP-1"})

    assert read_tool_error(response).startswith("INVALID_API_TOKEN: ")
