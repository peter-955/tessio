from uuid import UUID

from httpx import AsyncClient

from app.container import Container
from app.modules.notifications import GapAssignedPayload, NotificationKind, RunOutcome, SendNotificationUseCase
from app.modules.notifications.infrastructure import PostgresNotificationRepository, PostgresRecipientDirectory
from app.modules.users import WorkspaceRole
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.postgres import Database
from tests.api.notifications.notification_steps import (
    build_failure_payload,
    build_gap_payload,
    build_run_payload,
    list_stored_notifications,
    send_notification,
)
from tests.api.projects.user_steps import create_invited_user, deactivate_user, sign_up_as
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


class TransactionProbingPublisher(LiveEventPublisher):
    def __init__(self, database: Database) -> None:
        self._database = database
        self.events: list[LiveEvent] = []
        self.published_inside_transaction: list[bool] = []

    async def publish(self, event: LiveEvent) -> None:
        self.events.append(event)
        try:
            self._database.get_current_session()
        except RuntimeError:
            self.published_inside_transaction.append(False)
        else:
            self.published_inside_transaction.append(True)

    async def close(self) -> None:
        return None


def list_notification_events(publisher: RecordingLiveEventPublisher) -> list[LiveEvent]:
    return [event for event in publisher.events if event.type is LiveEventType.NOTIFICATION_CREATED]


async def sign_up_members(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    roles: list[ProjectRole],
) -> list[UUID]:
    return [await sign_up_member(client, container, recording_mailer, project, role) for role in roles]


async def test_one_row_is_stored_per_distinct_recipient(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    first_id, second_id, actor_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.DEV, ProjectRole.BA]
    )
    payload = build_gap_payload()

    notifications = await send_notification(
        container, project, payload, actor_id, recipient_ids=[second_id, first_id, second_id]
    )

    assert [notification.user_id for notification in notifications] == sorted([first_id, second_id])
    assert len({notification.id for notification in notifications}) == 2
    assert {notification.created_at for notification in notifications} == {notifications[0].created_at}
    for notification in notifications:
        assert notification.project_id == project.id
        assert notification.actor_id == actor_id
        assert notification.kind is NotificationKind.GAP_ASSIGNED
        assert notification.payload == payload
        assert notification.read_at is None
    stored = await list_stored_notifications(container, first_id)
    assert len(stored) == 1
    assert stored[0].kind is NotificationKind.GAP_ASSIGNED
    assert stored[0].payload == {
        "kind": "gap_assigned",
        "gap_id": str(payload.gap_id),
        "story_id": str(payload.story_id),
        "story_jira_key": "SHOP-12",
        "question": "Which currencies does checkout accept?",
    }


async def test_the_actor_is_excluded_for_assignments_but_kept_for_run_finished(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    actor_id, colleague_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.QC]
    )
    recipients = {actor_id, colleague_id}

    gap_notifications = await send_notification(container, project, build_gap_payload(), actor_id, recipients)
    failure_notifications = await send_notification(container, project, build_failure_payload(), actor_id, recipients)
    run_notifications = await send_notification(
        container, project, build_run_payload(), actor_id, {actor_id}, {ProjectRole.QC}
    )

    assert [notification.user_id for notification in gap_notifications] == [colleague_id]
    assert [notification.user_id for notification in failure_notifications] == [colleague_id]
    assert [notification.user_id for notification in run_notifications] == sorted(recipients)
    assert [row.kind for row in await list_stored_notifications(container, actor_id)] == [NotificationKind.RUN_FINISHED]


async def test_recipient_roles_pick_active_members_with_that_role_in_that_project_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    tester_id, developer_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.DEV]
    )
    other_tester_id = await sign_up_member(client, container, recording_mailer, other_project, ProjectRole.QC)
    deactivated_tester_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await deactivate_user(container, deactivated_tester_id)

    notifications = await send_notification(
        container, project, build_run_payload(RunOutcome.FAILED), None, recipient_roles={ProjectRole.QC}
    )

    assert [notification.user_id for notification in notifications] == [tester_id]
    assert developer_id not in {notification.user_id for notification in notifications}
    assert other_tester_id not in {notification.user_id for notification in notifications}
    assert notifications[0].actor_id is None


async def test_deactivated_and_invited_users_are_skipped(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    active_id, deactivated_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.DEV, ProjectRole.DEV]
    )
    await deactivate_user(container, deactivated_id)
    invited_id = await create_invited_user(container, recording_mailer)

    notifications = await send_notification(
        container, project, build_gap_payload(), None, {active_id, deactivated_id, invited_id}
    )

    assert [notification.user_id for notification in notifications] == [active_id]


async def test_explicit_recipients_do_not_need_to_be_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    notifications = await send_notification(container, project, build_failure_payload(), None, {admin.user_id})

    assert [notification.user_id for notification in notifications] == [admin.user_id]


async def test_duplicates_across_recipient_ids_and_roles_are_merged(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    starter_id, tester_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.QC]
    )

    notifications = await send_notification(
        container, project, build_run_payload(), starter_id, [starter_id, tester_id], [ProjectRole.QC, ProjectRole.QC]
    )

    assert [notification.user_id for notification in notifications] == sorted([starter_id, tester_id])


async def test_one_notification_created_event_is_published_per_row(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    first_id, second_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.PM]
    )

    notifications = await send_notification(container, project, build_gap_payload(), None, {first_id, second_id})

    events = list_notification_events(recording_live_event_publisher)
    assert [(event.user_id, event.project_id, event.ids) for event in events] == [
        (notification.user_id, project.id, {"notificationId": str(notification.id)}) for notification in notifications
    ]
    assert events[0].model_dump(mode="json", by_alias=True) == {
        "type": "notification.created",
        "projectId": str(project.id),
        "userId": str(notifications[0].user_id),
        "ids": {"notificationId": str(notifications[0].id)},
    }


async def test_events_are_published_after_the_transaction_ends(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    first_id, second_id = await sign_up_members(
        client, container, recording_mailer, project, [ProjectRole.QC, ProjectRole.QC]
    )
    publisher = TransactionProbingPublisher(container.database)
    use_case = SendNotificationUseCase(
        container.database,
        PostgresNotificationRepository(container.database),
        PostgresRecipientDirectory(container.database),
        publisher,
    )

    notifications = await use_case.execute(project.id, build_gap_payload(), None, {first_id, second_id})

    assert len(publisher.events) == len(notifications) == 2
    assert publisher.published_inside_transaction == [False, False]


async def test_no_recipients_means_no_rows_and_no_events(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    actor_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.BA)
    invited_id = await create_invited_user(container, recording_mailer)

    nobody = await send_notification(container, project, build_gap_payload(), actor_id)
    only_actor = await send_notification(container, project, build_gap_payload(), actor_id, {actor_id})
    only_inactive = await send_notification(container, project, build_failure_payload(), None, {invited_id})
    empty_role = await send_notification(container, project, build_run_payload(), None, (), {ProjectRole.VIEWER})

    assert nobody == only_actor == only_inactive == empty_role == []
    assert await list_stored_notifications(container, actor_id) == []
    assert list_notification_events(recording_live_event_publisher) == []


async def test_a_long_question_is_stored_shortened_to_200_characters(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    recipient_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.BA)

    notifications = await send_notification(
        container, project, build_gap_payload("  " + "q" * 300 + "  "), None, {recipient_id}
    )

    stored = await list_stored_notifications(container, recipient_id)
    question = stored[0].payload["question"]
    assert isinstance(question, str)
    assert len(question) == 200
    assert question == "q" * 199 + "…"
    payload = notifications[0].payload
    assert isinstance(payload, GapAssignedPayload)
    assert payload.question == question
