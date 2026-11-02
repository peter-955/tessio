from httpx import AsyncClient

from app.container import Container
from app.modules.integrations.errors import ChatWebhookRejectedError
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.integrations.chat_channel_steps import (
    SLACK_WEBHOOK_URL,
    TEAMS_WEBHOOK_URL,
    chat_channels_path,
    create_channel,
    create_channel_id,
    find_channel_row,
    use_recording_sender,
)
from tests.api.projects.user_steps import use_session
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def sign_in_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> None:
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)


async def test_an_admin_adds_lists_edits_and_removes_a_channel(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)

    created = await create_channel(client, project.key, events=["failure.opened", "run.finished", "run.finished"])
    chat_channel_id = created.json()["id"]
    listed = await client.get(chat_channels_path(project.key))
    edited = await client.patch(
        f"{chat_channels_path(project.key)}/{chat_channel_id}",
        json={"name": "Release room", "events": ["plan.signed_off"], "isActive": False},
    )
    removed = await client.delete(f"{chat_channels_path(project.key)}/{chat_channel_id}")
    listed_after = await client.get(chat_channels_path(project.key))

    assert created.status_code == 201, created.text
    assert created.json() == {
        "id": chat_channel_id,
        "kind": "slack",
        "name": "QA alerts",
        "webhookUrlMasked": "https://hooks.slack.com/…1234",
        "events": ["run.finished", "failure.opened"],
        "isActive": True,
        "lastDeliveryStatus": None,
        "lastDeliveryAt": None,
        "lastDeliveryError": None,
        "createdAt": created.json()["createdAt"],
    }
    assert listed.json() == [created.json()]
    assert edited.status_code == 200, edited.text
    assert edited.json()["name"] == "Release room"
    assert edited.json()["events"] == ["plan.signed_off"]
    assert edited.json()["isActive"] is False
    assert edited.json()["webhookUrlMasked"] == "https://hooks.slack.com/…1234"
    assert removed.status_code == 204
    assert listed_after.json() == []
    changed_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.CHAT_CHANNEL_CHANGED
    ]
    assert [event.ids for event in changed_events] == [{"chatChannelId": chat_channel_id}] * 3
    assert {event.project_id for event in changed_events} == {project.id}


async def test_the_webhook_url_is_stored_encrypted_and_never_returned(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    sender = use_recording_sender(container)

    created = await create_channel(client, project.key)
    chat_channel_id = created.json()["id"]
    teams = await create_channel(client, project.key, kind="teams", name="Teams QA", webhookUrl=TEAMS_WEBHOOK_URL)
    responses = [
        created,
        teams,
        await client.get(chat_channels_path(project.key)),
        await client.patch(f"{chat_channels_path(project.key)}/{chat_channel_id}", json={"name": "Renamed"}),
        await client.post(f"{chat_channels_path(project.key)}/{chat_channel_id}/test"),
    ]
    row = await find_channel_row(container, chat_channel_id)

    assert [response.status_code for response in responses] == [201, 201, 200, 200, 200]
    for response in responses:
        assert "SlackSecret" not in response.text
        assert "TeamsSecret" not in response.text
        assert "/services/T0001" not in response.text
    assert teams.json()["webhookUrlMasked"] == "https://prod-01.westeurope.logic.azure.com/…5678"
    assert SLACK_WEBHOOK_URL.encode() not in row.webhook_url_encrypted
    assert container.secret_cipher.decrypt(row.webhook_url_encrypted).decode() == SLACK_WEBHOOK_URL
    assert sender.deliveries[0][0] == SLACK_WEBHOOK_URL


async def test_a_new_url_replaces_the_old_one_and_resets_the_delivery_status(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    use_recording_sender(container)
    chat_channel_id = await create_channel_id(client, project.key)
    await client.post(f"{chat_channels_path(project.key)}/{chat_channel_id}/test")
    new_url = "https://hooks.slack.com/services/T0001/B0003/OtherSecret9999"

    response = await client.patch(f"{chat_channels_path(project.key)}/{chat_channel_id}", json={"webhookUrl": new_url})

    assert response.status_code == 200, response.text
    assert response.json()["webhookUrlMasked"] == "https://hooks.slack.com/…9999"
    assert response.json()["lastDeliveryStatus"] is None
    row = await find_channel_row(container, chat_channel_id)
    assert container.secret_cipher.decrypt(row.webhook_url_encrypted).decode() == new_url


async def test_a_private_or_plain_http_url_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    chat_channel_id = await create_channel_id(client, project.key)

    responses = [
        await create_channel(client, project.key, name="Plain", webhookUrl="http://hooks.slack.com/services/T/B/x"),
        await create_channel(client, project.key, name="Metadata", webhookUrl="https://169.254.169.254/latest"),
        await create_channel(client, project.key, name="Local", webhookUrl="https://localhost:8080/hook"),
        await client.patch(
            f"{chat_channels_path(project.key)}/{chat_channel_id}", json={"webhookUrl": "https://10.0.0.5/hook"}
        ),
    ]

    assert [response.status_code for response in responses] == [422] * 4
    assert [response.json()["code"] for response in responses] == ["WEBHOOK_URL_INVALID"] * 4


async def test_names_are_unique_in_a_project_and_events_are_required(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    await create_channel_id(client, project.key)
    other_id = await create_channel_id(client, project.key, name="Other")

    same_name = await create_channel(client, project.key, name="qa ALERTS")
    renamed_to_taken = await client.patch(f"{chat_channels_path(project.key)}/{other_id}", json={"name": "QA alerts"})
    no_events = await create_channel(client, project.key, name="Empty", events=[])
    unknown_event = await create_channel(client, project.key, name="Odd", events=["coffee.ready"])

    assert same_name.status_code == 409
    assert same_name.json()["code"] == "CONFLICT"
    assert renamed_to_taken.status_code == 409
    assert no_events.status_code == 422
    assert unknown_event.status_code == 422


async def test_a_channel_of_another_project_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    other_admin = await sign_up_account(client, container, recording_mailer, other_project, ProjectRole.ADMIN)
    use_session(client, other_admin.session_token)
    other_channel_id = await create_channel_id(client, other_project.key)
    use_session(client, admin.session_token)

    responses = [
        await client.patch(f"{chat_channels_path(project.key)}/{other_channel_id}", json={"name": "Mine"}),
        await client.delete(f"{chat_channels_path(project.key)}/{other_channel_id}"),
        await client.post(f"{chat_channels_path(project.key)}/{other_channel_id}/test"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]
    assert (await client.get(chat_channels_path(project.key))).json() == []


async def test_only_project_admins_manage_chat_channels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    for role in (ProjectRole.QC, ProjectRole.PM, ProjectRole.BA, ProjectRole.DEV, ProjectRole.VIEWER):
        member = await sign_up_account(client, container, recording_mailer, project, role)
        use_session(client, member.session_token)

        listed = await client.get(chat_channels_path(project.key))
        created = await create_channel(client, project.key)

        assert listed.status_code == 403
        assert created.status_code == 403
        assert created.json()["code"] == "PERMISSION_DENIED"


async def test_a_test_message_reports_delivery(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    sender = use_recording_sender(container)
    chat_channel_id = await create_channel_id(client, project.key)

    response = await client.post(f"{chat_channels_path(project.key)}/{chat_channel_id}/test")

    assert response.status_code == 200, response.text
    assert response.json()["lastDeliveryStatus"] == "delivered"
    assert response.json()["lastDeliveryAt"] is not None
    assert response.json()["lastDeliveryError"] is None
    webhook_url, payload = sender.deliveries[0]
    assert webhook_url == SLACK_WEBHOOK_URL
    assert payload["text"] == "Tessio test message"
    assert f"/projects/{project.key}/settings" in str(payload["blocks"])
    assert "Run finished, Failure opened" in str(payload["blocks"])


async def test_a_refused_test_message_gives_chat_delivery_failed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    sender = use_recording_sender(container)
    sender.failure = ChatWebhookRejectedError("Slack or Teams answered HTTP 404.", is_retryable=False)
    chat_channel_id = await create_channel_id(client, project.key)

    response = await client.post(f"{chat_channels_path(project.key)}/{chat_channel_id}/test")
    listed = await client.get(chat_channels_path(project.key))

    assert response.status_code == 502
    assert response.json()["code"] == "CHAT_DELIVERY_FAILED"
    assert "HTTP 404" in response.json()["message"]
    assert listed.json()[0]["lastDeliveryStatus"] == "failed"
    assert listed.json()[0]["lastDeliveryError"] == "Slack or Teams answered HTTP 404."


async def test_a_project_holds_at_most_twenty_channels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_admin(client, container, recording_mailer, project)
    for index in range(20):
        await create_channel_id(client, project.key, name=f"Channel {index}")

    response = await create_channel(client, project.key, name="One too many")

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"
