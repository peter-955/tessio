import json
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_send_result.entity import WebhookSendResult
from app.modules.integrations.errors import WebhookAttemptFailedError
from app.modules.integrations.typing.enums import IntegrationEvent
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.modules.integrations.utils.webhook_signature import is_valid_webhook_signature
from app.shared.events import LiveEvent, LiveEventType
from app.shared.typing.constants import JOB_ATTEMPTS
from app.shared.typing.enums import JobName, QueueName
from tests.api.integrations.webhook_steps import (
    WEBHOOK_URL,
    create_webhook_with_secret,
    sign_in_project_admin,
    use_recording_webhook_sender,
    webhooks_path,
)
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def run_finished_event(project: SeededProject) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.RUN_FINISHED,
        project_id=project.id,
        ids={"runId": str(uuid7()), "storyId": str(uuid7()), "status": "failed"},
    )


def delivery_job_ids(recording_job_queue: RecordingJobQueue) -> list[str]:
    return [
        str(job.data["deliveryId"])
        for job in recording_job_queue.jobs
        if job.queue_name is QueueName.INTEGRATIONS and job.job_name is JobName.WEBHOOK_DELIVER
    ]


async def list_deliveries(client: AsyncClient, project: SeededProject, webhook_id: str) -> list[dict[str, object]]:
    response = await client.get(f"{webhooks_path(project.key)}/{webhook_id}/deliveries")
    assert response.status_code == 200, response.text
    deliveries: list[dict[str, object]] = response.json()
    return deliveries


async def test_an_event_is_queued_only_for_active_webhooks_that_chose_it(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    chosen_id, _ = await create_webhook_with_secret(client, project.key, events=["run.finished"])
    await create_webhook_with_secret(client, project.key, events=["failure.opened"])
    await create_webhook_with_secret(client, project.key, events=["run.finished"], isActive=False)
    event = run_finished_event(project)

    await container.request_webhook_deliveries.handle(event)
    await container.request_webhook_deliveries.handle(run_finished_event(other_project))
    await container.request_webhook_deliveries.handle(
        LiveEvent(type=LiveEventType.RUN_CASE_RECORDED, project_id=project.id, ids={"runId": str(uuid7())})
    )

    deliveries = await list_deliveries(client, project, chosen_id)
    assert delivery_job_ids(recording_job_queue) == [deliveries[0]["id"]]
    assert recording_job_queue.jobs[-1].job_id == f"webhook-delivery-{deliveries[0]['id']}"
    assert deliveries[0]["status"] == "pending"
    assert deliveries[0]["attempts"] == 0
    payload = deliveries[0]["payload"]
    assert isinstance(payload, dict)
    assert payload["event"] == "run.finished"
    assert payload["project"] == {"id": str(project.id), "key": project.key, "name": f"Project {project.key}"}
    assert payload["data"] == event.ids
    assert UUID(str(payload["id"]))


async def test_a_delivery_is_signed_with_the_webhook_secret(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    sender = use_recording_webhook_sender(container)
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, secret = await create_webhook_with_secret(client, project.key)
    await container.request_webhook_deliveries.handle(run_finished_event(project))
    delivery_id = delivery_job_ids(recording_job_queue)[0]
    recording_live_event_publisher.events.clear()

    await container.job_handlers[QueueName.INTEGRATIONS][JobName.WEBHOOK_DELIVER].handle({"deliveryId": delivery_id})

    url, body, headers = sender.requests[0]
    assert url == WEBHOOK_URL
    assert headers["X-Tessio-Event"] == "run.finished"
    assert headers["X-Tessio-Delivery"] == delivery_id
    assert headers["Content-Type"] == "application/json"
    assert is_valid_webhook_signature(secret, int(headers["X-Tessio-Timestamp"]), body, headers["X-Tessio-Signature"])
    assert json.loads(body)["event"] == "run.finished"
    delivery = (await list_deliveries(client, project, webhook_id))[0]
    assert (delivery["status"], delivery["attempts"], delivery["responseStatus"]) == ("succeeded", 1, 200)
    assert delivery["deliveredAt"] is not None
    listed = (await client.get(webhooks_path(project.key))).json()
    assert listed[0]["lastDelivery"]["status"] == "succeeded"
    assert [event.type for event in recording_live_event_publisher.events] == [LiveEventType.WEBHOOK_CHANGED]


async def test_a_failing_receiver_is_retried_until_the_fifth_try(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    sender = use_recording_webhook_sender(container)
    sender.result = WebhookSendResult(is_success=False, response_status=500, error="The receiver answered HTTP 500.")
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)
    await container.request_webhook_deliveries.handle(run_finished_event(project))
    delivery_id = UUID(delivery_job_ids(recording_job_queue)[0])
    statuses: list[tuple[str, int]] = []

    for _ in range(JOB_ATTEMPTS - 1):
        with pytest.raises(WebhookAttemptFailedError):
            await container.deliver_webhook.execute(delivery_id)
        delivery = (await list_deliveries(client, project, webhook_id))[0]
        statuses.append((str(delivery["status"]), int(str(delivery["attempts"]))))
    final = await container.deliver_webhook.execute(delivery_id)
    after_final = await container.deliver_webhook.execute(delivery_id)

    assert statuses == [("pending", 1), ("pending", 2), ("pending", 3), ("pending", 4)]
    assert final is not None
    assert (final.status, final.attempts, final.response_status) == (WebhookDeliveryStatus.FAILED, 5, 500)
    assert final.error == "The receiver answered HTTP 500."
    assert after_final is not None
    assert after_final.attempts == 5
    assert len(sender.requests) == JOB_ATTEMPTS


async def test_a_turned_off_webhook_fails_its_pending_delivery_without_sending(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    sender = use_recording_webhook_sender(container)
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)
    await container.request_webhook_deliveries.handle(run_finished_event(project))
    await client.patch(f"{webhooks_path(project.key)}/{webhook_id}", json={"isActive": False})

    delivered = await container.deliver_webhook.execute(UUID(delivery_job_ids(recording_job_queue)[0]))

    assert sender.requests == []
    assert delivered is not None
    assert (delivered.status, delivered.error) == (WebhookDeliveryStatus.FAILED, "The webhook is turned off.")


async def test_a_delivery_is_redelivered_as_a_new_delivery(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    use_recording_webhook_sender(container)
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)
    other_webhook_id, _ = await create_webhook_with_secret(client, project.key, events=["gap.raised"])
    await container.request_webhook_deliveries.handle(run_finished_event(project))
    original_id = delivery_job_ids(recording_job_queue)[0]
    await container.deliver_webhook.execute(UUID(original_id))

    redelivered = await client.post(f"{webhooks_path(project.key)}/{webhook_id}/redeliver/{original_id}")
    wrong_webhook = await client.post(f"{webhooks_path(project.key)}/{other_webhook_id}/redeliver/{original_id}")

    assert redelivered.status_code == 202, redelivered.text
    assert redelivered.json()["redeliveryOfId"] == original_id
    assert redelivered.json()["status"] == "pending"
    assert delivery_job_ids(recording_job_queue) == [original_id, redelivered.json()["id"]]
    deliveries = await list_deliveries(client, project, webhook_id)
    assert [delivery["id"] for delivery in deliveries] == [redelivered.json()["id"], original_id]
    assert deliveries[0]["payload"] == deliveries[1]["payload"]
    assert wrong_webhook.status_code == 404


async def test_deliveries_older_than_30_days_are_deleted(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
) -> None:
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)
    now = datetime.now(UTC)
    old, recent = (
        WebhookDelivery(
            id=uuid7(),
            webhook_id=UUID(webhook_id),
            event=IntegrationEvent.RUN_FINISHED,
            payload={"event": "run.finished"},
            status=WebhookDeliveryStatus.SUCCEEDED,
            attempts=1,
            response_status=200,
            error=None,
            redelivery_of_id=None,
            last_attempt_at=created_at,
            delivered_at=created_at,
            created_at=created_at,
        )
        for created_at in (now - timedelta(days=31), now - timedelta(days=29))
    )
    async with container.database.begin():
        await container.webhook_delivery_repository.save(old)
        await container.webhook_delivery_repository.save(recent)

    await container.job_handlers[QueueName.MAINTENANCE][JobName.WEBHOOK_DELETE_OLD_DELIVERIES].handle({})

    deliveries = await list_deliveries(client, project, webhook_id)
    assert [delivery["id"] for delivery in deliveries] == [str(recent.id)]
    schedules = {schedule.job_name: schedule.cron_pattern for schedule in container.job_schedules}
    assert schedules[JobName.WEBHOOK_DELETE_OLD_DELIVERIES] == "15 4 * * *"


def test_the_worker_listens_for_webhook_events(container: Container) -> None:
    assert container.request_webhook_deliveries in container.live_event_handlers
