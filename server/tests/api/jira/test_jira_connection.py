from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.jira.jira_steps import (
    JIRA_ACCOUNT_EMAIL,
    JIRA_API_TOKEN,
    JIRA_SITE_URL,
    find_jira_connection_row,
    put_jira_connection,
)
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient


async def test_jira_connection_is_not_configured_without_a_row(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.get("/api/workspace/jira")

    assert response.status_code == 200
    assert response.json() == {
        "isConfigured": False,
        "siteUrl": None,
        "accountEmail": None,
        "accountDisplayName": None,
        "configuredAt": None,
    }


async def test_saving_a_jira_connection_verifies_and_encrypts_the_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    save_response = await put_jira_connection(client, account_email="  Jira-Bot@Example.com ")
    get_response = await client.get("/api/workspace/jira")

    assert save_response.status_code == 200
    saved = save_response.json()
    assert saved["isConfigured"] is True
    assert saved["siteUrl"] == JIRA_SITE_URL
    assert saved["accountEmail"] == JIRA_ACCOUNT_EMAIL
    assert saved["accountDisplayName"] == "Jira Bot"
    assert "apiToken" not in saved
    assert fake_jira_client.requested_site_urls == [JIRA_SITE_URL]
    row = await find_jira_connection_row(container)
    assert row is not None
    assert row.api_token_encrypted != JIRA_API_TOKEN.encode()
    assert JIRA_API_TOKEN.encode() not in row.api_token_encrypted
    assert container.secret_cipher.decrypt(row.api_token_encrypted) == JIRA_API_TOKEN.encode()
    assert row.account_id == "acc-1"
    assert row.configured_by == admin.user_id
    assert get_response.status_code == 200
    assert get_response.json() == saved
    assert JIRA_API_TOKEN not in get_response.text


async def test_site_url_is_normalized_to_scheme_and_host(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    response = await put_jira_connection(client, site_url="https://Team.atlassian.net/jira/your-work/")

    assert response.status_code == 200
    assert response.json()["siteUrl"] == "https://team.atlassian.net"


async def test_local_dot_less_hosts_may_use_http(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await put_jira_connection(client, site_url="http://fake-jira:8080/")

    assert response.status_code == 200
    assert response.json()["siteUrl"] == "http://fake-jira:8080"


async def test_invalid_site_urls_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    for site_url in ["ftp://x", "http://team.atlassian.net", "not a url", "https://user:pass@team.atlassian.net"]:
        response = await put_jira_connection(client, site_url=site_url)

        assert response.status_code == 422, site_url
        assert response.json()["code"] == "INVALID_REQUEST"
    assert fake_jira_client.requested_site_urls == []
    assert await find_jira_connection_row(container) is None


async def test_a_wrong_token_is_refused_and_nothing_is_saved(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await put_jira_connection(client, api_token="wrong-token")

    assert response.status_code == 422
    assert response.json()["code"] == "JIRA_INVALID_CREDENTIALS"
    assert await find_jira_connection_row(container) is None


async def test_an_unreachable_jira_keeps_the_existing_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200
    saved_row = await find_jira_connection_row(container)
    fake_jira_client.is_unreachable = True

    response = await put_jira_connection(client, site_url="https://other.atlassian.net", api_token="other-token")

    assert response.status_code == 502
    assert response.json()["code"] == "JIRA_UNREACHABLE"
    row = await find_jira_connection_row(container)
    assert row is not None
    assert saved_row is not None
    assert row.site_url == JIRA_SITE_URL
    assert row.api_token_encrypted == saved_row.api_token_encrypted
    assert row.configured_at == saved_row.configured_at


async def test_an_omitted_token_reuses_the_stored_token_on_the_same_site(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200
    fake_jira_client.account = fake_jira_client.account.model_copy(update={"display_name": "Renamed Bot"})

    response = await put_jira_connection(client, site_url="https://team.atlassian.net/", api_token=None)

    assert response.status_code == 200
    assert response.json()["accountDisplayName"] == "Renamed Bot"
    row = await find_jira_connection_row(container)
    assert row is not None
    assert container.secret_cipher.decrypt(row.api_token_encrypted) == JIRA_API_TOKEN.encode()


async def test_an_omitted_token_is_refused_for_another_site_or_without_a_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    without_connection_response = await put_jira_connection(client, api_token=None)
    assert (await put_jira_connection(client)).status_code == 200
    other_site_response = await put_jira_connection(client, site_url="https://other.atlassian.net", api_token=None)

    assert without_connection_response.status_code == 422
    assert without_connection_response.json()["code"] == "INVALID_REQUEST"
    assert other_site_response.status_code == 422
    assert other_site_response.json()["code"] == "INVALID_REQUEST"
    assert "https://other.atlassian.net" not in fake_jira_client.requested_site_urls


async def test_workspace_members_cannot_read_or_save_the_jira_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    use_session(client, member.session_token)
    get_response = await client.get("/api/workspace/jira")
    put_response = await put_jira_connection(client)
    use_session(client, admin.session_token)

    assert get_response.status_code == 403
    assert put_response.status_code == 403
    assert fake_jira_client.requested_site_urls == []
    assert await find_jira_connection_row(container) is None
