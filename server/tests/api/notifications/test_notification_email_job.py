from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.notifications import SendNotificationEmailJobHandler
from app.modules.users import UserLanguage
from app.modules.users.infrastructure import UserTable
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.notifications.notification_steps import build_failure_payload, build_gap_payload, send_notification
from tests.api.projects.user_steps import deactivate_user
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue

PREFERENCES_PATH = "/api/me/notification-preferences"


@pytest.fixture
def smtp_mailer(container: Container) -> RecordingMailer:
    mailer = RecordingMailer()
    container.__dict__["smtp_mailer"] = mailer
    return mailer


async def set_language(container: Container, user_id: UUID, language: UserLanguage) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(UserTable).where(UserTable.id == user_id).values(language=language)
        )


async def run_email_jobs(container: Container, recording_job_queue: RecordingJobQueue) -> None:
    handler = SendNotificationEmailJobHandler(container.send_notification_email)
    for job in recording_job_queue.jobs:
        if job.job_name is JobName.NOTIFICATION_EMAIL:
            await handler.handle(job.data)


async def sign_up_recipient(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> UUID:
    return await sign_up_member(client, container, recording_mailer, project, ProjectRole.BA)


async def find_email(container: Container, user_id: UUID) -> str:
    async with container.database.begin():
        user = await container.user_repository.find_by_id(user_id)
    assert user is not None
    return user.email


async def test_the_worker_sends_the_email_in_the_recipients_language(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    smtp_mailer: RecordingMailer,
) -> None:
    project = await seed_project(container)
    english_id = await sign_up_recipient(client, container, recording_mailer, project)
    french_id = await sign_up_recipient(client, container, recording_mailer, project)
    vietnamese_id = await sign_up_recipient(client, container, recording_mailer, project)
    await set_language(container, french_id, UserLanguage.FR)
    await set_language(container, vietnamese_id, UserLanguage.VI)

    await send_notification(container, project, build_gap_payload(), None, {english_id, french_id, vietnamese_id})
    await run_email_jobs(container, recording_job_queue)

    subjects = {message.recipient: message.subject for message in smtp_mailer.messages}
    assert subjects == {
        await find_email(container, english_id): f"[{project.key}] Gap assigned to you on SHOP-12",
        await find_email(container, french_id): f"[{project.key}] Écart qui vous est attribué sur SHOP-12",
        await find_email(container, vietnamese_id): f"[{project.key}] Khoảng trống được giao cho bạn ở SHOP-12",
    }
    english_message = next(message for message in smtp_mailer.messages if message.subject.endswith("on SHOP-12"))
    assert f"Project: Project {project.key} ({project.key})" in english_message.text
    assert f"https://tessio.test/projects/{project.key}/stories/SHOP-12?tab=gaps" in english_message.text


async def test_the_worker_skips_a_user_deactivated_after_the_notification(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    smtp_mailer: RecordingMailer,
) -> None:
    project = await seed_project(container)
    user_id = await sign_up_recipient(client, container, recording_mailer, project)
    await send_notification(container, project, build_failure_payload(), None, {user_id})
    await deactivate_user(container, user_id)

    await run_email_jobs(container, recording_job_queue)

    assert smtp_mailer.messages == []


async def test_the_worker_skips_a_user_who_turned_email_off_since(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    smtp_mailer: RecordingMailer,
) -> None:
    project = await seed_project(container)
    user_id = await sign_up_recipient(client, container, recording_mailer, project)
    await send_notification(container, project, build_failure_payload(), None, {user_id})
    response = await client.patch(
        PREFERENCES_PATH, json={"preferences": [{"kind": "failure_assigned", "email": False}]}
    )
    assert response.status_code == 200, response.text

    await run_email_jobs(container, recording_job_queue)

    assert smtp_mailer.messages == []


async def test_a_job_with_broken_data_is_dropped(container: Container, smtp_mailer: RecordingMailer) -> None:
    handler = SendNotificationEmailJobHandler(container.send_notification_email)

    await handler.handle({"user_id": "not-a-uuid", "payload": {"kind": "lunch"}})

    assert smtp_mailer.messages == []


async def test_the_email_job_is_wired_on_the_email_queue(container: Container) -> None:
    handlers = container.job_handlers

    assert isinstance(handlers[QueueName.EMAIL][JobName.NOTIFICATION_EMAIL], SendNotificationEmailJobHandler)
