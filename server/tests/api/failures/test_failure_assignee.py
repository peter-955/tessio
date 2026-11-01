from uuid import UUID

from httpx import AsyncClient

from app.container import Container
from app.modules.failures import FailureEventKind, FailureStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import (
    FailureScenario,
    assign,
    find_only_failure,
    list_event_rows,
    list_failure_notified_user_ids,
    open_failure,
    seed_scenario,
    set_failure_status,
)
from tests.api.gaps.gap_steps import add_active_member, add_invited_member, sign_up_account
from tests.api.projects.user_steps import deactivate_user, use_session
from tests.api.test_data.project_steps import archive_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[FailureScenario, UUID]:
    scenario = await seed_scenario(client, container, recording_mailer)
    return scenario, await open_failure(container, scenario)


def count_failure_changed(recording_live_event_publisher: RecordingLiveEventPublisher, failure_id: UUID) -> int:
    return len(
        [
            event
            for event in recording_live_event_publisher.events
            if event.type is LiveEventType.FAILURE_CHANGED and event.ids.get("failureId") == str(failure_id)
        ]
    )


async def test_roles_with_the_capability_assign_any_active_member(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    for assigner_role, assignee_role in (
        (ProjectRole.QC, ProjectRole.DEV),
        (ProjectRole.DEV, ProjectRole.VIEWER),
        (ProjectRole.ADMIN, ProjectRole.PM),
    ):
        scenario, failure_id = await seed_failure(client, container, recording_mailer)
        assignee_id = await add_active_member(container, recording_mailer, scenario.project, assignee_role, "Ana Fix")
        assigner = await sign_up_account(client, container, recording_mailer, scenario.project, assigner_role)

        response = await assign(client, scenario.project.key, failure_id, assignee_id)

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["assigneeId"] == str(assignee_id)
        assert body["assigneeName"] == "Ana Fix"
        assert body["assigneeStatus"] == "active"
        assert (await find_only_failure(container, scenario.case.id)).assignee_id == assignee_id
        events = await list_event_rows(container, failure_id)
        assert (events[-1].kind, events[-1].assignee_id, events[-1].actor_id) == (
            FailureEventKind.ASSIGNED,
            assignee_id,
            assigner.user_id,
        )
        assert await list_failure_notified_user_ids(container, scenario.project, failure_id) == [assignee_id]
        assert count_failure_changed(recording_live_event_publisher, failure_id) == 1


async def test_the_notification_names_the_case_and_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    assignee = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV)
    await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC)
    assert (await assign(client, scenario.project.key, failure_id, assignee.user_id)).status_code == 200
    use_session(client, assignee.session_token)
    response = await client.get("/api/notifications")

    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert len(items) == 1
    payload = items[0]["payload"]
    assert payload["kind"] == "failure_assigned"
    assert payload["failureId"] == str(failure_id)
    assert payload["testCaseCode"] == "TC-1"
    assert payload["testCaseTitle"] == "Case 1"
    assert payload["storyJiraKey"] == scenario.story.jira_key


async def test_self_assign_sends_no_notification(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    developer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV)

    response = await assign(client, scenario.project.key, failure_id, developer.user_id)

    assert response.status_code == 200, response.text
    assert await list_failure_notified_user_ids(container, scenario.project, failure_id) == []
    assert [event.kind for event in await list_event_rows(container, failure_id)][-1] is FailureEventKind.ASSIGNED


async def test_unassign_writes_an_unassigned_event(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    assignee_id = await add_active_member(container, recording_mailer, scenario.project, ProjectRole.DEV, "Ana Fix")
    tester = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC)
    assert (await assign(client, scenario.project.key, failure_id, assignee_id)).status_code == 200

    response = await assign(client, scenario.project.key, failure_id, None)

    assert response.status_code == 200, response.text
    assert response.json()["assigneeId"] is None
    assert response.json()["assigneeName"] is None
    events = await list_event_rows(container, failure_id)
    assert (events[-1].kind, events[-1].assignee_id, events[-1].actor_id) == (
        FailureEventKind.UNASSIGNED,
        assignee_id,
        tester.user_id,
    )
    assert await list_failure_notified_user_ids(container, scenario.project, failure_id) == [assignee_id]
    assert count_failure_changed(recording_live_event_publisher, failure_id) == 2


async def test_the_same_assignee_twice_adds_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    assignee_id = await add_active_member(container, recording_mailer, scenario.project, ProjectRole.DEV, "Ana Fix")
    await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC)
    assert (await assign(client, scenario.project.key, failure_id, assignee_id)).status_code == 200

    again = await assign(client, scenario.project.key, failure_id, assignee_id)
    unassigned_twice = await assign(client, scenario.project.key, failure_id, None)
    unassigned_again = await assign(client, scenario.project.key, failure_id, None)

    assert again.status_code == 200
    assert again.json()["assigneeId"] == str(assignee_id)
    assert unassigned_twice.status_code == 200
    assert unassigned_again.status_code == 200
    assert [event.kind for event in await list_event_rows(container, failure_id)] == [
        FailureEventKind.OPENED,
        FailureEventKind.ASSIGNED,
        FailureEventKind.UNASSIGNED,
    ]
    assert await list_failure_notified_user_ids(container, scenario.project, failure_id) == [assignee_id]
    assert count_failure_changed(recording_live_event_publisher, failure_id) == 2


async def test_assignees_must_be_active_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    other_scenario = await seed_scenario(client, container, recording_mailer)
    invited_id = await add_invited_member(container, recording_mailer, scenario.project, ProjectRole.DEV)
    deactivated_id = await add_active_member(container, recording_mailer, scenario.project, ProjectRole.DEV, "Ex Dev")
    await deactivate_user(container, deactivated_id)
    await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC)

    for assignee_id in (other_scenario.runner.user_id, invited_id, deactivated_id):
        response = await assign(client, scenario.project.key, failure_id, assignee_id)

        assert response.status_code == 409
        assert response.json() == {"code": "ASSIGNEE_NOT_ACTIVE_MEMBER", "message": "Pick an active project member."}
    assert (await find_only_failure(container, scenario.case.id)).assignee_id is None
    assert len(await list_event_rows(container, failure_id)) == 1


async def test_pm_cannot_assign(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    manager = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.PM)

    response = await assign(client, scenario.project.key, failure_id, manager.user_id)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_a_verified_failure_cannot_be_reassigned(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    await set_failure_status(container, failure_id, FailureStatus.VERIFIED)
    developer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV)

    response = await assign(client, scenario.project.key, failure_id, developer.user_id)

    assert response.status_code == 409
    assert response.json() == {
        "code": "INVALID_STATUS_TRANSITION",
        "message": "A verified failure cannot be reassigned.",
    }


async def test_an_archived_project_refuses_assignment(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    developer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV)
    await archive_project(container, scenario.project)

    response = await assign(client, scenario.project.key, failure_id, developer.user_id)

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_a_non_member_cannot_assign(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, scenario.project, None)

    response = await assign(client, scenario.project.key, failure_id, scenario.runner.user_id)

    assert response.status_code == 404
