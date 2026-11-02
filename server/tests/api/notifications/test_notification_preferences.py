from uuid import UUID

from httpx import AsyncClient

from app.container import Container
from app.modules.notifications import NotificationKind, RunOutcome
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.notifications.notification_steps import (
    build_failure_payload,
    build_gap_payload,
    build_run_payload,
    list_stored_notifications,
    send_notification,
)
from tests.api.projects.user_steps import deactivate_user, use_session
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue

PREFERENCES_PATH = "/api/me/notification-preferences"
DEFAULT_PREFERENCES = [
    {"kind": "gap_assigned", "inApp": True, "email": True},
    {"kind": "failure_assigned", "inApp": True, "email": True},
    {"kind": "run_finished", "inApp": True, "email": False},
    {"kind": "suite_run_finished", "inApp": True, "email": False},
]


def list_email_jobs(recording_job_queue: RecordingJobQueue) -> list[RecordedJob]:
    return [job for job in recording_job_queue.jobs if job.job_name is JobName.NOTIFICATION_EMAIL]


def find_preference(body: list[dict[str, object]], kind: str) -> dict[str, object]:
    return next(item for item in body if item["kind"] == kind)


async def sign_up_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> tuple[UUID, str]:
    user_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    return user_id, client.cookies["tessio_session"]


async def test_a_new_user_gets_the_default_preferences_for_every_kind(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_session(client, container, recording_mailer, project)

    response = await client.get(PREFERENCES_PATH)

    assert response.status_code == 200, response.text
    body = response.json()
    assert [item["kind"] for item in body] == [kind.value for kind in NotificationKind]
    for expected in DEFAULT_PREFERENCES:
        assert find_preference(body, str(expected["kind"])) == expected


async def test_changing_a_preference_keeps_the_other_kinds_and_channels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_session(client, container, recording_mailer, project)

    first = await client.patch(
        PREFERENCES_PATH,
        json={"preferences": [{"kind": "run_finished", "email": True}, {"kind": "gap_assigned", "inApp": False}]},
    )
    second = await client.patch(PREFERENCES_PATH, json={"preferences": [{"kind": "run_finished", "inApp": False}]})
    listed = await client.get(PREFERENCES_PATH)

    assert first.status_code == 200, first.text
    assert find_preference(first.json(), "run_finished") == {"kind": "run_finished", "inApp": True, "email": True}
    assert find_preference(first.json(), "gap_assigned") == {"kind": "gap_assigned", "inApp": False, "email": True}
    assert second.status_code == 200, second.text
    assert find_preference(second.json(), "run_finished") == {"kind": "run_finished", "inApp": False, "email": True}
    assert listed.json() == second.json()


async def test_preferences_are_per_user(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    _, first_session = await sign_up_session(client, container, recording_mailer, project)
    _, second_session = await sign_up_session(client, container, recording_mailer, project)
    use_session(client, first_session)
    await client.patch(PREFERENCES_PATH, json={"preferences": [{"kind": "gap_assigned", "email": False}]})

    use_session(client, second_session)
    response = await client.get(PREFERENCES_PATH)

    assert find_preference(response.json(), "gap_assigned") == {"kind": "gap_assigned", "inApp": True, "email": True}


async def test_a_kind_listed_twice_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_session(client, container, recording_mailer, project)

    response = await client.patch(
        PREFERENCES_PATH,
        json={"preferences": [{"kind": "gap_assigned", "email": False}, {"kind": "gap_assigned", "email": True}]},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"


async def test_an_unknown_kind_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_session(client, container, recording_mailer, project)

    response = await client.patch(PREFERENCES_PATH, json={"preferences": [{"kind": "lunch_ready", "email": True}]})

    assert response.status_code == 422


async def test_preferences_need_a_session(client: AsyncClient) -> None:
    client.cookies.clear()

    assert (await client.get(PREFERENCES_PATH)).status_code == 401
    assert (await client.patch(PREFERENCES_PATH, json={"preferences": []})).status_code == 401


async def test_assignments_are_emailed_by_default_and_run_results_are_not(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    user_id, _ = await sign_up_session(client, container, recording_mailer, project)
    gap_payload = build_gap_payload()

    await send_notification(container, project, gap_payload, None, {user_id})
    await send_notification(container, project, build_failure_payload(), None, {user_id})
    await send_notification(container, project, build_run_payload(RunOutcome.PASSED), None, {user_id})

    jobs = list_email_jobs(recording_job_queue)
    assert [job.queue_name for job in jobs] == [QueueName.EMAIL, QueueName.EMAIL]
    assert [job.data["payload"]["kind"] for job in jobs if isinstance(job.data["payload"], dict)] == [
        "gap_assigned",
        "failure_assigned",
    ]
    assert jobs[0].data["user_id"] == str(user_id)
    assert jobs[0].data["project_id"] == str(project.id)
    assert len(await list_stored_notifications(container, user_id)) == 3


async def test_turned_off_channels_send_nothing_on_them(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    user_id, _ = await sign_up_session(client, container, recording_mailer, project)
    await client.patch(
        PREFERENCES_PATH,
        json={
            "preferences": [
                {"kind": "gap_assigned", "email": False},
                {"kind": "run_finished", "inApp": False, "email": True},
            ]
        },
    )

    await send_notification(container, project, build_gap_payload(), None, {user_id})
    run_notifications = await send_notification(container, project, build_run_payload(), None, {user_id})

    jobs = list_email_jobs(recording_job_queue)
    assert [job.data["payload"]["kind"] for job in jobs if isinstance(job.data["payload"], dict)] == ["run_finished"]
    assert run_notifications == []
    assert [row.kind for row in await list_stored_notifications(container, user_id)] == [NotificationKind.GAP_ASSIGNED]


async def test_only_recipients_who_want_email_get_a_job(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    keen_id, _ = await sign_up_session(client, container, recording_mailer, project)
    quiet_id, quiet_session = await sign_up_session(client, container, recording_mailer, project)
    inactive_id, _ = await sign_up_session(client, container, recording_mailer, project)
    use_session(client, quiet_session)
    await client.patch(PREFERENCES_PATH, json={"preferences": [{"kind": "gap_assigned", "email": False}]})
    await deactivate_user(container, inactive_id)

    await send_notification(container, project, build_gap_payload(), None, {keen_id, quiet_id, inactive_id})

    assert [job.data["user_id"] for job in list_email_jobs(recording_job_queue)] == [str(keen_id)]
