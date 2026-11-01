from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import (
    DEFAULT_QUESTION,
    add_active_member,
    add_invited_member,
    raise_gap,
    raise_gap_id,
    remove_criterion,
    seed_story,
    seed_test_case,
)
from tests.api.projects.user_steps import create_invited_user, deactivate_user
from tests.api.test_data.project_steps import archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer


@pytest.mark.parametrize("role", [ProjectRole.ADMIN, ProjectRole.PM, ProjectRole.BA, ProjectRole.QC, ProjectRole.DEV])
async def test_every_contributing_role_can_raise_a_gap(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    raiser_id = await sign_up_member(client, container, recording_mailer, project, role)

    response = await raise_gap(client, project.key, story, severity="high", question="  Which currencies?  ")

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["projectKey"] == project.key
    assert body["projectName"] == f"Project {project.key}"
    assert body["storyId"] == str(story.id)
    assert body["storyJiraKey"] == story.jira_key
    assert body["storyTitle"] == f"Story {story.jira_key}"
    assert body["type"] == "missing_ac"
    assert body["severity"] == "high"
    assert body["question"] == "Which currencies?"
    assert body["targetType"] == "story"
    assert body["targetId"] is None
    assert body["targetRef"] is None
    assert body["raisedBy"] == str(raiser_id)
    assert body["raisedByName"] == "Test User"
    assert body["isRaisedViaClaude"] is False
    assert body["answer"] is None


async def test_workspace_admin_raises_without_membership(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, None, WorkspaceRole.ADMIN)

    response = await raise_gap(client, project.key, story)

    assert response.status_code == 201


async def test_criterion_target_resolves_by_code(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1", "AC2"))
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story, targetType="criterion", targetRef=" ac2 ")

    assert response.status_code == 201, response.text
    assert response.json()["targetId"] == str(story.criterion_ids["AC2"])
    assert response.json()["targetRef"] == "AC2"


async def test_test_case_target_resolves_by_code(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    raiser_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    test_case_id = await seed_test_case(container, project, story.id, 12, raiser_id)

    response = await raise_gap(
        client, project.key, story, type="missing_step", targetType="test_case", targetRef="tc-12"
    )

    assert response.status_code == 201, response.text
    assert response.json()["targetId"] == str(test_case_id)
    assert response.json()["targetRef"] == "TC-12"


async def test_story_target_ignores_target_ref(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story, targetType="story", targetRef="AC1")

    assert response.status_code == 201
    assert response.json()["targetId"] is None
    assert response.json()["targetRef"] is None


@pytest.mark.parametrize(
    ("target_type", "target_ref", "message"),
    [
        ("criterion", "AC9", "AC9 is not on this story."),
        ("criterion", "AC2", "AC2 is not on this story."),
        ("criterion", None, " is not on this story."),
        ("test_case", "TC-99", "TC-99 is not on this story."),
        ("test_case", "TC-12", "TC-12 is not on this story."),
        ("test_case", "case twelve", "case twelve is not on this story."),
    ],
)
async def test_unknown_target_is_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    target_type: str,
    target_ref: str | None,
    message: str,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1", "AC2"))
    other_story = await seed_story(container, project)
    raiser_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await remove_criterion(container, story.criterion_ids["AC2"])
    await seed_test_case(container, project, other_story.id, 12, raiser_id)

    response = await raise_gap(client, project.key, story, targetType=target_type, targetRef=target_ref)

    assert response.status_code == 422
    assert response.json() == {"code": "UNKNOWN_REFERENCE", "message": message}


async def test_explicit_active_assignee_is_kept(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Dana Dev")
    await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story, assigneeId=str(developer_id))

    assert response.status_code == 201
    assert response.json()["assigneeId"] == str(developer_id)
    assert response.json()["assigneeName"] == "Dana Dev"
    assert response.json()["assigneeStatus"] == "active"
    assert response.json()["assigneeRole"] is None


@pytest.mark.parametrize("assignee_state", ["deactivated", "invited", "viewer", "not_member", "unknown"])
async def test_explicit_assignee_must_be_an_active_answering_member(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, assignee_state: str
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    if assignee_state == "deactivated":
        assignee_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Gone Analyst")
        await deactivate_user(container, assignee_id)
    elif assignee_state == "invited":
        assignee_id = await add_invited_member(container, recording_mailer, project, ProjectRole.BA)
    elif assignee_state == "viewer":
        assignee_id = await add_active_member(container, recording_mailer, project, ProjectRole.VIEWER, "Vic Viewer")
    elif assignee_state == "not_member":
        assignee_id = await create_invited_user(container, recording_mailer)
    else:
        assignee_id = uuid4()
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story, assigneeId=str(assignee_id))

    assert response.status_code == 409
    assert response.json() == {
        "code": "ASSIGNEE_NOT_ACTIVE_MEMBER",
        "message": "Pick an active project member who can answer gaps.",
    }


async def test_viewer_cannot_raise(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.VIEWER)

    response = await raise_gap(client, project.key, story)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_non_member_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, None)

    response = await raise_gap(client, project.key, story)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_archived_project_refuses_raising(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await archive_project(container, project)

    response = await raise_gap(client, project.key, story)

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_unknown_story_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await client.post(
        f"/api/projects/{project.key}/stories/{project.key}-404/gaps",
        json={"type": "missing_ac", "question": DEFAULT_QUESTION},
    )

    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "message": "Story not found."}


async def test_story_key_is_matched_case_insensitively(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await client.post(
        f"/api/projects/{project.key}/stories/{story.jira_key.lower()}/gaps",
        json={"type": "missing_ac", "question": DEFAULT_QUESTION},
    )

    assert response.status_code == 201
    assert response.json()["storyJiraKey"] == story.jira_key


@pytest.mark.parametrize(
    "body",
    [
        {"type": "missing_ac", "question": "   "},
        {"type": "missing_ac", "question": "x" * 2001},
        {"type": "missing_ac", "question": "Why?", "targetRef": "A" * 41},
        {"type": "not_a_type", "question": "Why?"},
        {"question": "Why?"},
    ],
)
async def test_invalid_body_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, body: dict[str, object]
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await client.post(f"/api/projects/{project.key}/stories/{story.jira_key}/gaps", json=body)

    assert response.status_code == 422


async def test_get_gap_returns_it_to_viewers_and_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    gap_id = await raise_gap_id(client, project.key, story)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.VIEWER)
    await archive_project(container, project)

    response = await client.get(f"/api/projects/{project.key}/gaps/{gap_id}")

    assert response.status_code == 200
    assert response.json()["id"] == gap_id


async def test_get_gap_hides_unknown_and_other_project_gaps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    gap_id = await raise_gap_id(client, project.key, story)
    await sign_up_member(client, container, recording_mailer, other_project, ProjectRole.QC)

    other_project_response = await client.get(f"/api/projects/{other_project.key}/gaps/{gap_id}")
    unknown_response = await client.get(f"/api/projects/{other_project.key}/gaps/{uuid4()}")
    non_member_response = await client.get(f"/api/projects/{project.key}/gaps/{gap_id}")

    assert other_project_response.status_code == 404
    assert other_project_response.json() == {"code": "NOT_FOUND", "message": "Gap not found."}
    assert unknown_response.status_code == 404
    assert non_member_response.status_code == 404
    assert non_member_response.json()["message"] == "Project not found."
