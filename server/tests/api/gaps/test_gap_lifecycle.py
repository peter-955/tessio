from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import (
    SeededStory,
    add_active_member,
    answer_gap,
    find_gap_row,
    list_notified_user_ids,
    raise_gap_id,
    reassign_gap,
    reopen_gap,
    seed_story,
    sign_up_account,
)
from tests.api.projects.user_steps import SignedUpAccount, deactivate_user, use_session
from tests.api.test_data.project_steps import SeededProject, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_open_gap(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    raiser_role: ProjectRole = ProjectRole.QC,
) -> tuple[SeededProject, SeededStory, SignedUpAccount, UUID, str]:
    project = await seed_project(container)
    story = await seed_story(container, project)
    analyst_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    raiser = await sign_up_account(client, container, recording_mailer, project, raiser_role, "Rae Raiser")
    gap_id = await raise_gap_id(client, project.key, story)
    return project, story, raiser, analyst_id, gap_id


async def seed_resolved_gap(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    raiser_role: ProjectRole = ProjectRole.QC,
) -> tuple[SeededProject, SeededStory, SignedUpAccount, UUID, str]:
    project, story, raiser, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer, raiser_role)
    answered = await answer_gap(client, project.key, gap_id)
    assert answered.status_code == 200, answered.text
    return project, story, raiser, analyst_id, gap_id


def count_gap_events(recording_live_event_publisher: RecordingLiveEventPublisher, gap_id: str) -> int:
    return len(
        [
            event
            for event in recording_live_event_publisher.events
            if event.type is LiveEventType.GAP_CHANGED and event.ids.get("gapId") == gap_id
        ]
    )


async def test_answer_resolves_the_gap(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)
    answerer_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.BA)

    response = await answer_gap(client, project.key, gap_id, "  EUR and USD only.  ")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "resolved"
    assert body["answer"] == "EUR and USD only."
    assert body["answeredBy"] == str(answerer_id)
    assert body["answeredByName"] == "Test User"
    assert body["answeredAt"] is not None
    assert count_gap_events(recording_live_event_publisher, gap_id) == 2
    assert len(await list_notified_user_ids(container, project, gap_id)) == 1


async def test_second_answer_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, _, gap_id = await seed_resolved_gap(client, container, recording_mailer)

    response = await answer_gap(client, project.key, gap_id, "Another answer.")

    assert response.status_code == 409
    assert response.json() == {"code": "GAP_NOT_OPEN", "message": "This gap is already resolved."}
    row = await find_gap_row(container, gap_id)
    assert row.answer == "EUR and USD."


async def test_viewer_cannot_answer(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.VIEWER)

    response = await answer_gap(client, project.key, gap_id)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_answer_needs_text(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)

    blank = await answer_gap(client, project.key, gap_id, "   ")
    too_long = await answer_gap(client, project.key, gap_id, "x" * 4001)

    assert blank.status_code == 422
    assert too_long.status_code == 422


async def test_unknown_gap_cannot_be_answered(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, _, _ = await seed_open_gap(client, container, recording_mailer)

    response = await answer_gap(client, project.key, str(uuid4()))

    assert response.status_code == 404
    assert response.json()["message"] == "Gap not found."


@pytest.mark.parametrize("action", ["answer", "reopen", "reassign"])
async def test_writes_are_refused_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, action: str
) -> None:
    project, _, _, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer)
    await archive_project(container, project)

    if action == "answer":
        response = await answer_gap(client, project.key, gap_id)
    elif action == "reopen":
        response = await reopen_gap(client, project.key, gap_id)
    else:
        response = await reassign_gap(client, project.key, gap_id, assigneeId=str(analyst_id))

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


@pytest.mark.parametrize("action", ["answer", "reopen", "reassign"])
async def test_writes_hide_the_project_from_non_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, action: str
) -> None:
    project, _, _, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, project, None)

    if action == "answer":
        response = await answer_gap(client, project.key, gap_id)
    elif action == "reopen":
        response = await reopen_gap(client, project.key, gap_id)
    else:
        response = await reassign_gap(client, project.key, gap_id, assigneeId=str(analyst_id))

    assert response.status_code == 404
    assert response.json()["message"] == "Project not found."


async def test_raiser_reopens_a_resolved_gap_and_the_answer_is_kept(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _, raiser, analyst_id, gap_id = await seed_resolved_gap(
        client, container, recording_mailer, ProjectRole.DEV
    )

    response = await reopen_gap(client, project.key, gap_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "open"
    assert body["reopenedByName"] == "Rae Raiser"
    assert body["reopenedAt"] is not None
    assert body["answer"] == "EUR and USD."
    assert body["assigneeId"] == str(analyst_id)
    row = await find_gap_row(container, gap_id)
    assert row.reopened_by == raiser.user_id
    assert await list_notified_user_ids(container, project, gap_id) == [analyst_id, analyst_id]
    assert count_gap_events(recording_live_event_publisher, gap_id) == 3


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.ADMIN])
async def test_qc_and_admin_reopen_gaps_they_did_not_raise(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, _, _, _, gap_id = await seed_resolved_gap(client, container, recording_mailer, ProjectRole.DEV)
    await sign_up_member(client, container, recording_mailer, project, role)

    response = await reopen_gap(client, project.key, gap_id)

    assert response.status_code == 200
    assert response.json()["status"] == "open"


@pytest.mark.parametrize("role", [ProjectRole.DEV, ProjectRole.BA, ProjectRole.PM, ProjectRole.VIEWER])
async def test_other_roles_cannot_reopen_gaps_they_did_not_raise(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, _, _, _, gap_id = await seed_resolved_gap(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, project, role)

    response = await reopen_gap(client, project.key, gap_id)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_open_gap_cannot_be_reopened(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)

    response = await reopen_gap(client, project.key, gap_id)

    assert response.status_code == 409
    assert response.json() == {
        "code": "INVALID_STATUS_TRANSITION",
        "message": "Only a resolved gap can be reopened.",
    }


async def test_reopen_routes_again_when_the_assignee_was_deactivated(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, analyst_id, gap_id = await seed_resolved_gap(client, container, recording_mailer)
    await deactivate_user(container, analyst_id)
    new_analyst_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "New Analyst")

    response = await reopen_gap(client, project.key, gap_id)

    assert response.status_code == 200
    assert response.json()["assigneeId"] == str(new_analyst_id)
    assert response.json()["assigneeName"] == "New Analyst"
    assert await list_notified_user_ids(container, project, gap_id) == [analyst_id, new_analyst_id]


async def test_reassign_to_a_member(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _, _, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer)
    developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Dana Dev")

    response = await reassign_gap(client, project.key, gap_id, assigneeId=str(developer_id))

    assert response.status_code == 200, response.text
    assert response.json()["assigneeId"] == str(developer_id)
    assert response.json()["assigneeName"] == "Dana Dev"
    assert response.json()["assigneeRole"] is None
    assert await list_notified_user_ids(container, project, gap_id) == [analyst_id, developer_id]
    assert count_gap_events(recording_live_event_publisher, gap_id) == 2


async def test_reassign_to_a_role_clears_the_assignee(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, raiser, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer)
    first_developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Dev One")
    second_developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Dev Two")
    use_session(client, raiser.session_token)

    response = await reassign_gap(client, project.key, gap_id, assigneeRole="dev")

    assert response.status_code == 200
    assert response.json()["assigneeId"] is None
    assert response.json()["assigneeName"] is None
    assert response.json()["assigneeRole"] == "dev"
    notified_ids = await list_notified_user_ids(container, project, gap_id)
    assert sorted(notified_ids[1:]) == sorted([first_developer_id, second_developer_id])
    assert notified_ids[0] == analyst_id


async def test_reassign_to_a_deactivated_member_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)
    developer_id = await add_active_member(container, recording_mailer, project, ProjectRole.DEV, "Gone Dev")
    await deactivate_user(container, developer_id)

    response = await reassign_gap(client, project.key, gap_id, assigneeId=str(developer_id))

    assert response.status_code == 409
    assert response.json()["code"] == "ASSIGNEE_NOT_ACTIVE_MEMBER"


async def test_resolved_gap_cannot_be_reassigned(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, analyst_id, gap_id = await seed_resolved_gap(client, container, recording_mailer)

    response = await reassign_gap(client, project.key, gap_id, assigneeId=str(analyst_id))

    assert response.status_code == 409
    assert response.json()["code"] == "GAP_NOT_OPEN"


@pytest.mark.parametrize(
    "body",
    [{}, {"assigneeRole": "viewer"}, {"assigneeRole": "ba", "assigneeId": "00000000-0000-0000-0000-000000000001"}],
)
async def test_reassign_needs_exactly_one_answering_target(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, body: dict[str, object]
) -> None:
    project, _, _, _, gap_id = await seed_open_gap(client, container, recording_mailer)

    response = await reassign_gap(client, project.key, gap_id, **body)

    assert response.status_code == 422


async def test_viewer_cannot_reassign(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project, _, _, analyst_id, gap_id = await seed_open_gap(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.VIEWER)

    response = await reassign_gap(client, project.key, gap_id, assigneeId=str(analyst_id))

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"
