from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.integrations.webhook_steps import (
    WEBHOOK_URL,
    create_webhook,
    create_webhook_with_secret,
    sign_in_project_admin,
    webhooks_path,
)
from tests.api.projects.user_steps import use_session
from tests.api.security.security_steps import read_code
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_an_admin_adds_lists_edits_and_removes_a_webhook(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)

    created = await create_webhook(
        client, project.key, description="CI bot", events=["failure.opened", "run.finished", "run.finished"]
    )
    webhook_id = created.json()["webhook"]["id"]
    secret = created.json()["secret"]
    listed = await client.get(webhooks_path(project.key))
    edited = await client.patch(
        f"{webhooks_path(project.key)}/{webhook_id}",
        json={"events": ["plan.signed_off"], "isActive": False, "description": None},
    )
    rotated = await client.patch(f"{webhooks_path(project.key)}/{webhook_id}", json={"rotateSecret": True})
    removed = await client.delete(f"{webhooks_path(project.key)}/{webhook_id}")
    listed_after = await client.get(webhooks_path(project.key))

    assert created.status_code == 201, created.text
    assert secret.startswith("whsec_")
    assert created.json()["webhook"] == {
        "id": webhook_id,
        "url": WEBHOOK_URL,
        "description": "CI bot",
        "events": ["run.finished", "failure.opened"],
        "isActive": True,
        "secretHint": f"whsec_…{secret[-4:]}",
        "createdAt": created.json()["webhook"]["createdAt"],
        "lastDelivery": None,
    }
    assert listed.json() == [created.json()["webhook"]]
    assert secret not in listed.text
    assert edited.status_code == 200, edited.text
    assert edited.json()["secret"] is None
    assert edited.json()["webhook"]["events"] == ["plan.signed_off"]
    assert edited.json()["webhook"]["isActive"] is False
    assert edited.json()["webhook"]["description"] is None
    assert rotated.json()["secret"].startswith("whsec_")
    assert rotated.json()["secret"] != secret
    assert rotated.json()["webhook"]["secretHint"] == f"whsec_…{rotated.json()['secret'][-4:]}"
    assert removed.status_code == 204
    assert listed_after.json() == []
    changed = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.WEBHOOK_CHANGED]
    assert [event.ids for event in changed] == [{"webhookId": webhook_id}] * 4


async def test_the_secret_is_stored_encrypted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, secret = await create_webhook_with_secret(client, project.key)

    async with container.database.begin():
        webhooks = await container.webhook_repository.list_for_project(project.id)

    assert [str(webhook.id) for webhook in webhooks] == [webhook_id]
    assert secret.encode() not in webhooks[0].secret_encrypted
    assert container.secret_cipher.decrypt(webhooks[0].secret_encrypted).decode() == secret


async def test_private_and_plain_http_urls_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)

    plain_http = await create_webhook(client, project.key, url="http://hooks.example.com/tessio")
    metadata = await create_webhook(client, project.key, url="https://169.254.169.254/latest")
    edited = await client.patch(
        f"{webhooks_path(project.key)}/{webhook_id}", json={"url": "https://localhost:8000/hook"}
    )
    no_events = await create_webhook(client, project.key, events=[])
    unknown_event = await create_webhook(client, project.key, events=["run.case_recorded"])

    assert (plain_http.status_code, read_code(plain_http)) == (422, "WEBHOOK_URL_INVALID")
    assert (metadata.status_code, read_code(metadata)) == (422, "WEBHOOK_URL_INVALID")
    assert (edited.status_code, read_code(edited)) == (422, "WEBHOOK_URL_INVALID")
    assert no_events.status_code == 422
    assert unknown_event.status_code == 422


async def test_only_integration_managers_see_webhooks(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, project)
    webhook_id, _ = await create_webhook_with_secret(client, project.key)
    qc = await sign_up_account(client, container, recording_mailer, project, ProjectRole.QC)
    use_session(client, qc.session_token)

    listed = await client.get(webhooks_path(project.key))
    deliveries = await client.get(f"{webhooks_path(project.key)}/{webhook_id}/deliveries")

    assert (listed.status_code, read_code(listed)) == (403, "PERMISSION_DENIED")
    assert (deliveries.status_code, read_code(deliveries)) == (403, "PERMISSION_DENIED")


async def test_a_webhook_of_another_project_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other_project = await seed_project(container)
    await sign_in_project_admin(client, container, recording_mailer, other_project)
    other_webhook_id, _ = await create_webhook_with_secret(client, other_project.key)
    await sign_in_project_admin(client, container, recording_mailer, project)

    edited = await client.patch(f"{webhooks_path(project.key)}/{other_webhook_id}", json={"isActive": False})
    removed = await client.delete(f"{webhooks_path(project.key)}/{other_webhook_id}")
    deliveries = await client.get(f"{webhooks_path(project.key)}/{other_webhook_id}/deliveries")

    assert [edited.status_code, removed.status_code, deliveries.status_code] == [404, 404, 404]
