from uuid import UUID

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import (
    add_active_member,
    add_invited_member,
    list_notified_user_ids,
    raise_gap,
    seed_story,
)
from tests.api.projects.user_steps import deactivate_user
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher

ACTIVE = "active"
DEACTIVATED = "deactivated"
INVITED = "invited"


async def add_member_in_state(
    container: Container, recording_mailer: RecordingMailer, project: SeededProject, role: ProjectRole, state: str
) -> UUID:
    if state == INVITED:
        return await add_invited_member(container, recording_mailer, project, role)
    user_id = await add_active_member(container, recording_mailer, project, role, f"{role.value} member")
    if state == DEACTIVATED:
        await deactivate_user(container, user_id)
    return user_id


@pytest.mark.parametrize(
    ("gap_type", "data_scope", "members", "expected_member_index", "expected_role"),
    [
        ("missing_ac", None, [(ProjectRole.BA, ACTIVE)], 0, None),
        ("unclear_goal", None, [(ProjectRole.BA, ACTIVE), (ProjectRole.ADMIN, ACTIVE)], 0, None),
        ("missing_ac", None, [(ProjectRole.BA, ACTIVE), (ProjectRole.BA, ACTIVE)], None, ProjectRole.BA),
        ("missing_ac", None, [(ProjectRole.ADMIN, ACTIVE), (ProjectRole.QC, ACTIVE)], 0, None),
        (
            "missing_ac",
            None,
            [(ProjectRole.BA, DEACTIVATED), (ProjectRole.BA, INVITED), (ProjectRole.BA, ACTIVE)],
            2,
            None,
        ),
        (
            "missing_ac",
            None,
            [(ProjectRole.BA, DEACTIVATED), (ProjectRole.BA, DEACTIVATED), (ProjectRole.ADMIN, ACTIVE)],
            2,
            None,
        ),
        ("missing_ac", None, [(ProjectRole.ADMIN, ACTIVE), (ProjectRole.ADMIN, ACTIVE)], None, ProjectRole.ADMIN),
        ("missing_ac", None, [(ProjectRole.ADMIN, DEACTIVATED)], None, ProjectRole.ADMIN),
        ("missing_step", None, [(ProjectRole.BA, ACTIVE), (ProjectRole.QC, ACTIVE)], 1, None),
        ("missing_test_data", None, [(ProjectRole.DEV, ACTIVE), (ProjectRole.QC, ACTIVE)], 1, None),
        ("missing_test_data", "project", [(ProjectRole.DEV, ACTIVE), (ProjectRole.QC, ACTIVE)], 1, None),
        ("missing_test_data", "environment", [(ProjectRole.DEV, ACTIVE), (ProjectRole.QC, ACTIVE)], 0, None),
        ("other", None, [(ProjectRole.BA, ACTIVE), (ProjectRole.ADMIN, ACTIVE)], 1, None),
    ],
)
async def test_gap_is_routed_by_type_to_active_members(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    gap_type: str,
    data_scope: str | None,
    members: list[tuple[ProjectRole, str]],
    expected_member_index: int | None,
    expected_role: ProjectRole | None,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    member_ids = [
        await add_member_in_state(container, recording_mailer, project, role, state) for role, state in members
    ]
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.PM)

    response = await raise_gap(client, project.key, story, type=gap_type, dataScope=data_scope)

    assert response.status_code == 201, response.text
    body = response.json()
    expected_assignee_id = None if expected_member_index is None else str(member_ids[expected_member_index])
    assert body["assigneeId"] == expected_assignee_id
    assert body["assigneeRole"] == (None if expected_role is None else expected_role.value)
    assert body["status"] == "open"


async def test_data_scope_is_kept_only_for_missing_test_data(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    kept = await raise_gap(client, project.key, story, type="missing_test_data", dataScope="environment")
    dropped = await raise_gap(client, project.key, story, type="missing_step", dataScope="environment")

    assert kept.json()["dataScope"] == "environment"
    assert dropped.json()["dataScope"] is None


async def test_assignee_is_notified_and_never_the_raiser(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    analyst_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    raiser_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story)

    assert response.json()["assigneeId"] == str(analyst_id)
    assert response.json()["assigneeName"] == "Bao Analyst"
    notified_ids = await list_notified_user_ids(container, project, response.json()["id"])
    assert notified_ids == [analyst_id]
    assert raiser_id not in notified_ids


async def test_role_queue_notifies_every_active_role_member_except_the_raiser(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    first_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "First Analyst")
    second_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Second Analyst")
    deactivated_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Gone Analyst")
    await deactivate_user(container, deactivated_id)
    raiser_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.BA)

    response = await raise_gap(client, project.key, story)

    assert response.json()["assigneeRole"] == "ba"
    notified_ids = await list_notified_user_ids(container, project, response.json()["id"])
    assert sorted(notified_ids) == sorted([first_id, second_id])
    assert raiser_id not in notified_ids


async def test_raising_publishes_gap_changed(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    response = await raise_gap(client, project.key, story)

    gap_events = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.GAP_CHANGED]
    assert len(gap_events) == 1
    assert gap_events[0].project_id == project.id
    assert gap_events[0].ids == {"gapId": response.json()["id"], "storyId": str(story.id)}
