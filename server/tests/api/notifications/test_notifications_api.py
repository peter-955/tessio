from dataclasses import dataclass
from uuid import UUID, uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.notifications import RunOutcome
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.notifications.notification_steps import (
    build_failure_payload,
    build_gap_payload,
    build_run_payload,
    list_stored_notifications,
    remove_member,
    send_gap_assigned,
    send_notification,
)
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as, use_session
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer

NOTIFICATION_FIELDS = {
    "id",
    "kind",
    "projectId",
    "projectKey",
    "projectName",
    "actorId",
    "actorName",
    "payload",
    "isRead",
    "readAt",
    "createdAt",
}


@dataclass(frozen=True)
class NotificationScene:
    project: SeededProject
    recipient: SignedUpAccount
    actor: SignedUpAccount


async def set_up_scene(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    workspace_role: WorkspaceRole = WorkspaceRole.MEMBER,
) -> NotificationScene:
    project = await seed_project(container)
    actor = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, name="Alice Actor")
    recipient = await sign_up_as(client, container, recording_mailer, workspace_role, name="Rita Recipient")
    await add_member(container, project, actor.user_id, ProjectRole.BA)
    await add_member(container, project, recipient.user_id, ProjectRole.QC)
    use_session(client, recipient.session_token)
    return NotificationScene(project=project, recipient=recipient, actor=actor)


async def list_ids(client: AsyncClient, query: str = "") -> list[str]:
    response = await client.get(f"/api/notifications{query}")
    assert response.status_code == 200
    return [item["id"] for item in response.json()["items"]]


async def read_unread_count(client: AsyncClient) -> int:
    response = await client.get("/api/notifications/unread-count")
    assert response.status_code == 200
    count: int = response.json()["count"]
    return count


async def test_the_list_is_newest_first_with_project_actor_and_a_camel_case_payload(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    recipients = {scene.recipient.user_id}
    gap_payload = build_gap_payload()
    failure_payload = build_failure_payload()
    run_payload = build_run_payload(RunOutcome.FAILED)
    await send_notification(container, scene.project, gap_payload, scene.actor.user_id, recipients)
    await send_notification(container, scene.project, failure_payload, scene.actor.user_id, recipients)
    await send_notification(container, scene.project, run_payload, None, recipients)

    response = await client.get("/api/notifications")

    assert response.status_code == 200
    body = response.json()
    assert body["nextCursor"] is None
    run_item, failure_item, gap_item = body["items"]
    for item in body["items"]:
        assert item.keys() == NOTIFICATION_FIELDS
        assert item["projectId"] == str(scene.project.id)
        assert item["projectKey"] == scene.project.key
        assert item["projectName"] == f"Project {scene.project.key}"
        assert item["isRead"] is False
        assert item["readAt"] is None
    assert [item["kind"] for item in body["items"]] == ["run_finished", "failure_assigned", "gap_assigned"]
    assert gap_item["actorId"] == str(scene.actor.user_id)
    assert gap_item["actorName"] == "Alice Actor"
    assert gap_item["payload"] == {
        "kind": "gap_assigned",
        "gapId": str(gap_payload.gap_id),
        "storyId": str(gap_payload.story_id),
        "storyJiraKey": "SHOP-12",
        "question": "Which currencies does checkout accept?",
    }
    assert failure_item["payload"] == {
        "kind": "failure_assigned",
        "failureId": str(failure_payload.failure_id),
        "testCaseId": str(failure_payload.test_case_id),
        "testCaseCode": "TC-12",
        "testCaseTitle": "Pay with a saved card",
        "storyJiraKey": "SHOP-12",
    }
    assert run_item["actorId"] is None
    assert run_item["actorName"] is None
    assert run_item["payload"] == {
        "kind": "run_finished",
        "runId": str(run_payload.run_id),
        "storyId": str(run_payload.story_id),
        "storyJiraKey": "SHOP-12",
        "outcome": "failed",
        "passedCount": 8,
        "failedCount": 1,
        "blockedCount": 0,
    }


async def test_unread_only_filters_read_rows(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    older = await send_gap_assigned(container, scene.project, scene.recipient.user_id, scene.actor.user_id)
    newer = await send_gap_assigned(container, scene.project, scene.recipient.user_id, scene.actor.user_id)
    await client.put(f"/api/notifications/{newer.id}/read")

    assert await list_ids(client) == [str(newer.id), str(older.id)]
    assert await list_ids(client, "?unreadOnly=true") == [str(older.id)]
    assert await list_ids(client, "?unreadOnly=false") == [str(newer.id), str(older.id)]


async def test_cursor_paging_walks_every_row_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    sent_ids = [
        str((await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)).id) for _ in range(25)
    ]

    page_sizes: list[int] = []
    listed_ids: list[str] = []
    cursors: list[str | None] = []
    query = "?limit=10"
    while True:
        response = await client.get(f"/api/notifications{query}")
        assert response.status_code == 200
        body = response.json()
        page_sizes.append(len(body["items"]))
        listed_ids.extend(item["id"] for item in body["items"])
        cursors.append(body["nextCursor"])
        if body["nextCursor"] is None:
            break
        query = f"?limit=10&cursor={body['nextCursor']}"

    assert page_sizes == [10, 10, 5]
    assert listed_ids == list(reversed(sent_ids))
    assert cursors == [listed_ids[9], listed_ids[19], None]


async def test_the_default_page_size_is_20(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    for _ in range(21):
        await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)

    response = await client.get("/api/notifications")

    assert len(response.json()["items"]) == 20
    assert response.json()["nextCursor"] is not None


async def test_limit_is_bounded_to_1_through_100(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await set_up_scene(client, container, recording_mailer)

    statuses = [(await client.get(f"/api/notifications?limit={limit}")).status_code for limit in (0, 1, 100, 101)]

    assert statuses == [422, 200, 200, 422]


async def test_other_users_rows_are_never_listed_or_counted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    own = await send_gap_assigned(container, scene.project, scene.recipient.user_id, scene.actor.user_id)
    await send_gap_assigned(container, scene.project, scene.actor.user_id, scene.recipient.user_id)

    assert await list_ids(client) == [str(own.id)]
    assert await read_unread_count(client) == 1


async def test_rows_of_a_project_the_user_left_disappear_from_the_list_and_the_count(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    other_project = await seed_project(container)
    await add_member(container, other_project, scene.recipient.user_id, ProjectRole.DEV)
    kept = await send_gap_assigned(container, other_project, scene.recipient.user_id, None)
    await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)
    assert await read_unread_count(client) == 2

    await remove_member(container, scene.project, scene.recipient.user_id)

    assert await list_ids(client) == [str(kept.id)]
    assert await read_unread_count(client) == 1


async def test_a_workspace_admin_sees_rows_for_any_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer, WorkspaceRole.ADMIN)
    outside_project = await seed_project(container)
    outside = await send_gap_assigned(container, outside_project, scene.recipient.user_id, None)
    inside = await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)

    response = await client.get("/api/notifications")

    assert [item["id"] for item in response.json()["items"]] == [str(inside.id), str(outside.id)]
    assert response.json()["items"][1]["projectKey"] == outside_project.key
    assert await read_unread_count(client) == 2


async def test_a_non_member_recipient_does_not_see_rows_of_that_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    outside_project = await seed_project(container)
    await send_gap_assigned(container, outside_project, scene.recipient.user_id, None)

    assert await list_ids(client) == []
    assert await read_unread_count(client) == 0


async def test_the_unread_count_matches_the_unread_rows(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    assert await read_unread_count(client) == 0
    notifications = [
        await send_gap_assigned(container, scene.project, scene.recipient.user_id, scene.actor.user_id)
        for _ in range(3)
    ]
    assert await read_unread_count(client) == 3

    await client.put(f"/api/notifications/{notifications[0].id}/read")

    assert await read_unread_count(client) == 2
    assert len(await list_ids(client, "?unreadOnly=true")) == 2


async def test_marking_one_notification_read_is_idempotent(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    notification = await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)

    first = await client.put(f"/api/notifications/{notification.id}/read")
    first_read_at = (await client.get("/api/notifications")).json()["items"][0]["readAt"]
    second = await client.put(f"/api/notifications/{notification.id}/read")

    assert first.status_code == second.status_code == 204
    item = (await client.get("/api/notifications")).json()["items"][0]
    assert item["isRead"] is True
    assert item["readAt"] is not None
    assert item["readAt"] == first_read_at


async def test_marking_another_users_or_an_unknown_notification_gives_404(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    foreign = await send_gap_assigned(container, scene.project, scene.actor.user_id, None)

    foreign_response = await client.put(f"/api/notifications/{foreign.id}/read")
    unknown_response = await client.put(f"/api/notifications/{uuid7()}/read")

    assert foreign_response.status_code == unknown_response.status_code == 404
    assert foreign_response.json()["code"] == unknown_response.json()["code"] == "NOT_FOUND"
    stored = await list_stored_notifications(container, scene.actor.user_id)
    assert [row.read_at for row in stored] == [None]


async def test_read_all_marks_only_the_callers_rows(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scene = await set_up_scene(client, container, recording_mailer)
    hidden_project = await seed_project(container)
    for _ in range(3):
        await send_gap_assigned(container, scene.project, scene.recipient.user_id, None)
    await send_gap_assigned(container, hidden_project, scene.recipient.user_id, None)
    await send_gap_assigned(container, scene.project, scene.actor.user_id, None)

    response = await client.put("/api/notifications/read-all")

    assert response.status_code == 204
    assert await read_unread_count(client) == 0
    assert await list_ids(client, "?unreadOnly=true") == []
    recipient_rows = await list_stored_notifications(container, scene.recipient.user_id)
    assert len(recipient_rows) == 4
    assert all(row.read_at is not None for row in recipient_rows)
    assert [row.read_at for row in await list_stored_notifications(container, scene.actor.user_id)] == [None]


async def test_every_endpoint_needs_a_session(client: AsyncClient) -> None:
    client.cookies.clear()
    notification_id = UUID(int=1)

    responses = [
        await client.get("/api/notifications"),
        await client.get("/api/notifications/unread-count"),
        await client.put("/api/notifications/read-all"),
        await client.put(f"/api/notifications/{notification_id}/read"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]
    assert {response.json()["code"] for response in responses} == {"NOT_SIGNED_IN"}
