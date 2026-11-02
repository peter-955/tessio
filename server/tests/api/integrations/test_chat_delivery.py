from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.integrations import ChatChannelLiveEventHandler, DeliverChatMessageJobHandler, IntegrationEvent
from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob
from app.modules.integrations.errors import ChatWebhookRejectedError
from app.shared.events import LiveEvent, LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.gaps.gap_steps import raise_gap_id, seed_story, sign_up_account
from tests.api.integrations.chat_channel_steps import (
    SLACK_WEBHOOK_URL,
    TEAMS_WEBHOOK_URL,
    RecordingChatWebhookSender,
    chat_channels_path,
    create_channel_id,
    find_channel_row,
    use_recording_sender,
)
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import finish, record_case, seed_runnable_story, sign_up_runner, start_run_id
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue


def list_chat_jobs(recording_job_queue: RecordingJobQueue) -> list[ChatDeliveryJob]:
    return [
        ChatDeliveryJob.model_validate(job.data)
        for job in recording_job_queue.jobs
        if job.queue_name is QueueName.INTEGRATIONS and job.job_name is JobName.CHAT_DELIVER
    ]


async def sign_in_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> None:
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN, name="Ada Admin")
    use_session(client, admin.session_token)


async def deliver_all(container: Container, recording_job_queue: RecordingJobQueue) -> None:
    handler = DeliverChatMessageJobHandler(container.deliver_chat_message)
    for job in recording_job_queue.jobs:
        if job.job_name is JobName.CHAT_DELIVER:
            await handler.handle(job.data)


@pytest.fixture
def sender(container: Container) -> RecordingChatWebhookSender:
    return use_recording_sender(container)


async def test_an_event_queues_one_job_per_active_subscribed_channel(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    subscribed_id = await create_channel_id(client, project.key, name="Runs", events=["run.finished"])
    await create_channel_id(client, project.key, name="Gaps", events=["gap.raised"])
    await create_channel_id(client, project.key, name="Paused", events=["run.finished"], isActive=False)
    handler = ChatChannelLiveEventHandler(container.request_chat_deliveries)
    run_id = str(uuid7())

    await handler.handle(
        LiveEvent(type=LiveEventType.RUN_FINISHED, project_id=project.id, ids={"runId": run_id, "status": "passed"})
    )
    await handler.handle(LiveEvent(type=LiveEventType.RUN_FINISHED, project_id=other_project.id, ids={"runId": run_id}))
    await handler.handle(LiveEvent(type=LiveEventType.RUN_CASE_RECORDED, project_id=project.id, ids={"runId": run_id}))
    await handler.handle(LiveEvent(type=LiveEventType.NOTIFICATION_CREATED, user_id=uuid7(), ids={}))

    assert list_chat_jobs(recording_job_queue) == [
        ChatDeliveryJob(
            chat_channel_id=UUID(subscribed_id),
            project_id=project.id,
            event=IntegrationEvent.RUN_FINISHED,
            ids={"runId": run_id, "status": "passed"},
        )
    ]


async def test_a_finished_run_is_posted_to_slack_and_teams(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=2, step_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    await record_case(client, runner.token, run_id, story.case_ids[0], "passed")
    await record_case(client, runner.token, run_id, story.case_ids[1], "failed")
    await finish(client, runner.token, run_id)
    await sign_in_admin(client, container, recording_mailer, project)
    await create_channel_id(client, project.key, name="Slack runs", events=["run.finished"])
    await create_channel_id(
        client, project.key, kind="teams", name="Teams runs", webhookUrl=TEAMS_WEBHOOK_URL, events=["run.finished"]
    )

    jobs = await container.request_chat_deliveries.execute(
        LiveEvent(type=LiveEventType.RUN_FINISHED, project_id=project.id, ids={"runId": run_id, "status": "failed"})
    )
    await deliver_all(container, recording_job_queue)

    assert len(jobs) == 2
    deliveries = dict(sender.deliveries)
    slack_payload = deliveries[SLACK_WEBHOOK_URL]
    teams_payload = deliveries[TEAMS_WEBHOOK_URL]
    assert slack_payload["text"] == f"Run failed on {story.jira_key}"
    slack_text = str(slack_payload["blocks"])
    assert "*Passed*\\n1" in slack_text
    assert "*Failed*\\n1" in slack_text
    assert f"https://tessio.test/projects/{project.key}/runs/{run_id}" in slack_text
    assert f"Tessio · Project {project.key}" in slack_text
    assert teams_payload["type"] == "message"
    attachments = teams_payload["attachments"]
    assert isinstance(attachments, list)
    assert isinstance(attachments[0], dict)
    assert attachments[0]["contentType"] == "application/vnd.microsoft.card.adaptive"
    assert f"Run failed on {story.jira_key}" in str(attachments[0]["content"])
    assert {
        row.last_delivery_status
        for row in [await find_channel_row(container, str(job.chat_channel_id)) for job in jobs]
    } == {"delivered"}


async def test_a_raised_gap_is_posted_with_its_question(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_in_admin(client, container, recording_mailer, project)
    await create_channel_id(client, project.key, name="Gaps", events=["gap.raised"])
    gap_id = await raise_gap_id(client, project.key, story, question="Which <currencies> are accepted?")

    await container.request_chat_deliveries.execute(
        LiveEvent(type=LiveEventType.GAP_RAISED, project_id=project.id, ids={"gapId": gap_id, "storyId": str(story.id)})
    )
    await deliver_all(container, recording_job_queue)

    _, payload = sender.deliveries[0]
    text = str(payload["blocks"])
    assert payload["text"] == f"Gap raised on {story.jira_key}"
    assert "Which &lt;currencies&gt; are accepted?" in text
    assert "*Raised by*\\nAda Admin" in text
    assert f"/projects/{project.key}/stories/{story.jira_key}?tab=gaps" in text


async def test_a_retryable_failure_is_recorded_and_raised_so_the_job_is_tried_again(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_in_admin(client, container, recording_mailer, project)
    chat_channel_id = await create_channel_id(client, project.key, name="Gaps", events=["gap.raised"])
    gap_id = await raise_gap_id(client, project.key, story)
    [job] = await container.request_chat_deliveries.execute(
        LiveEvent(type=LiveEventType.GAP_RAISED, project_id=project.id, ids={"gapId": gap_id})
    )
    handler = DeliverChatMessageJobHandler(container.deliver_chat_message)
    sender.failure = ChatWebhookRejectedError("Slack or Teams answered HTTP 503.", is_retryable=True)

    with pytest.raises(ChatWebhookRejectedError):
        await handler.handle(job.model_dump(mode="json"))
    failed_row = await find_channel_row(container, chat_channel_id)
    sender.failure = None
    await handler.handle(job.model_dump(mode="json"))
    delivered_row = await find_channel_row(container, chat_channel_id)

    assert failed_row.last_delivery_status == "failed"
    assert failed_row.last_delivery_error == "Slack or Teams answered HTTP 503."
    assert delivered_row.last_delivery_status == "delivered"
    assert delivered_row.last_delivery_error is None
    assert len(sender.deliveries) == 2


async def test_a_permanent_failure_is_recorded_without_a_retry(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_in_admin(client, container, recording_mailer, project)
    chat_channel_id = await create_channel_id(client, project.key, name="Gaps", events=["gap.raised"])
    gap_id = await raise_gap_id(client, project.key, story)
    [job] = await container.request_chat_deliveries.execute(
        LiveEvent(type=LiveEventType.GAP_RAISED, project_id=project.id, ids={"gapId": gap_id})
    )
    sender.failure = ChatWebhookRejectedError("Slack or Teams answered HTTP 404.", is_retryable=False)

    is_delivered = await container.deliver_chat_message.execute(job)

    row = await find_channel_row(container, chat_channel_id)
    assert is_delivered is False
    assert row.last_delivery_status == "failed"
    assert row.last_delivery_error == "Slack or Teams answered HTTP 404."


async def test_a_job_for_a_removed_paused_or_unsubscribed_channel_sends_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_in_admin(client, container, recording_mailer, project)
    gap_id = await raise_gap_id(client, project.key, story)
    removed_id = await create_channel_id(client, project.key, name="Removed", events=["gap.raised"])
    paused_id = await create_channel_id(client, project.key, name="Paused", events=["gap.raised"])
    moved_id = await create_channel_id(client, project.key, name="Moved", events=["gap.raised"])
    jobs = await container.request_chat_deliveries.execute(
        LiveEvent(type=LiveEventType.GAP_RAISED, project_id=project.id, ids={"gapId": gap_id})
    )
    await client.delete(f"{chat_channels_path(project.key)}/{removed_id}")
    await client.patch(f"{chat_channels_path(project.key)}/{paused_id}", json={"isActive": False})
    await client.patch(f"{chat_channels_path(project.key)}/{moved_id}", json={"events": ["run.finished"]})

    results = [await container.deliver_chat_message.execute(job) for job in jobs]

    assert len(jobs) == 3
    assert results == [False, False, False]
    assert sender.deliveries == []


async def test_a_job_for_a_target_that_is_gone_sends_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    sender: RecordingChatWebhookSender,
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    chat_channel_id = await create_channel_id(client, project.key, name="Runs", events=["run.started"])
    job = ChatDeliveryJob(
        chat_channel_id=UUID(chat_channel_id),
        project_id=project.id,
        event=IntegrationEvent.RUN_STARTED,
        ids={"runId": str(uuid7())},
    )
    broken_job = job.model_copy(update={"ids": {"runId": "not-a-uuid"}})

    assert await container.deliver_chat_message.execute(job) is False
    assert await container.deliver_chat_message.execute(broken_job) is False
    assert sender.deliveries == []
