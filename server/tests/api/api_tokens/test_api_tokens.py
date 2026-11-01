import re
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.container import Container
from app.modules.api_tokens.utils.api_token_secret import hash_api_token
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import SeededProject, add_member, create_token, insert_token, seed_project
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as, use_session
from tests.conftest import RecordingMailer

TOKEN_PATTERN = re.compile(r"^tsio_[0-9a-f]{8}_[A-Za-z0-9_-]{43}$")
API_TOKENS_PATH = "/api/me/api-tokens"


async def sign_up_member(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole | None = ProjectRole.QC,
    workspace_role: WorkspaceRole = WorkspaceRole.MEMBER,
) -> SignedUpAccount:
    account = await sign_up_as(client, container, recording_mailer, workspace_role)
    if role is not None:
        await add_member(container, project, account.user_id, role)
    return account


async def read_stored_row(container: Container, token_id: str) -> dict[str, object]:
    async with container.database.begin():
        result = await container.database.get_current_session().execute(
            text("SELECT * FROM api_tokens WHERE id = :id"), {"id": UUID(token_id)}
        )
        row = result.mappings().one()
    return dict(row)


def assert_close_to(value: str, expected: datetime) -> None:
    assert abs(datetime.fromisoformat(value) - expected) < timedelta(minutes=1)


async def test_create_returns_the_token_once_and_stores_only_its_hash(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    account = await sign_up_member(client, container, recording_mailer, project)

    response = await client.post(API_TOKENS_PATH, json={"name": "  Claude Code  ", "projectKey": project.key})

    assert response.status_code == 201
    body = response.json()
    token = body["token"]
    assert TOKEN_PATTERN.match(token)
    api_token = body["apiToken"]
    assert api_token["prefix"] == token[5:13]
    assert api_token["name"] == "Claude Code"
    assert api_token["status"] == "active"
    assert api_token["projectId"] == str(project.id)
    assert api_token["projectKey"] == project.key
    assert api_token["projectName"] == f"Project {project.key}"
    assert api_token["lastUsedAt"] is None
    assert api_token["revokedAt"] is None
    assert_close_to(api_token["expiresAt"], datetime.now(UTC) + timedelta(days=30))
    assert "tokenHash" not in api_token
    row = await read_stored_row(container, api_token["id"])
    assert row["token_hash"] == hash_api_token(token)
    assert row["user_id"] == account.user_id
    assert row["prefix"] == api_token["prefix"]
    assert all(value != token and token not in str(value) for value in row.values())


async def test_create_accepts_ninety_days(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)

    response = await client.post(API_TOKENS_PATH, json={"name": "Long", "projectKey": project.key, "expiresInDays": 90})

    assert response.status_code == 201
    assert_close_to(response.json()["apiToken"]["expiresAt"], datetime.now(UTC) + timedelta(days=90))


@pytest.mark.parametrize("expires_in_days", [0, 91])
async def test_create_refuses_a_lifetime_out_of_range(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, expires_in_days: int
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)

    response = await client.post(
        API_TOKENS_PATH, json={"name": "Bad", "projectKey": project.key, "expiresInDays": expires_in_days}
    )

    assert response.status_code == 422


async def test_create_refuses_a_blank_name(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)

    response = await client.post(API_TOKENS_PATH, json={"name": "   ", "projectKey": project.key})

    assert response.status_code == 422


async def test_non_member_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, role=None)

    response = await client.post(API_TOKENS_PATH, json={"name": "Claude", "projectKey": project.key})

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_workspace_admin_who_is_not_a_member_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, role=None, workspace_role=WorkspaceRole.ADMIN)

    response = await client.post(API_TOKENS_PATH, json={"name": "Claude", "projectKey": project.key})

    assert response.status_code == 403
    assert response.json() == {
        "code": "PERMISSION_DENIED",
        "message": "Only project members can create a token for this project.",
    }


async def test_viewer_member_can_create_a_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, role=ProjectRole.VIEWER)

    response = await client.post(API_TOKENS_PATH, json={"name": "Claude", "projectKey": project.key})

    assert response.status_code == 201


async def test_archived_project_refuses_token_creation(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container, is_archived=True)
    await sign_up_member(client, container, recording_mailer, project)

    response = await client.post(API_TOKENS_PATH, json={"name": "Claude", "projectKey": project.key})

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_eleventh_active_token_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    account = await sign_up_member(client, container, recording_mailer, project)
    now = datetime.now(UTC)
    await insert_token(container, account.user_id, project.id, now - timedelta(days=1))
    await insert_token(container, account.user_id, project.id, now + timedelta(days=5), revoked_at=now)
    for _ in range(10):
        await create_token(client, project.key)

    refused = await client.post(API_TOKENS_PATH, json={"name": "Eleventh", "projectKey": project.key})

    assert refused.status_code == 409
    assert refused.json() == {
        "code": "TOKEN_LIMIT_REACHED",
        "message": "You already have 10 active tokens. Revoke one first.",
    }
    active_token = next(item for item in (await client.get(API_TOKENS_PATH)).json() if item["status"] == "active")
    assert (await client.delete(f"{API_TOKENS_PATH}/{active_token['id']}")).status_code == 204
    accepted = await client.post(API_TOKENS_PATH, json={"name": "Eleventh", "projectKey": project.key})
    assert accepted.status_code == 201


async def test_list_shows_only_my_tokens_newest_first_with_their_status(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    other = await sign_up_member(client, container, recording_mailer, project)
    await create_token(client, project.key)
    account = await sign_up_member(client, container, recording_mailer, project)
    now = datetime.now(UTC)
    await insert_token(container, account.user_id, project.id, now - timedelta(hours=1))
    await insert_token(container, account.user_id, project.id, now + timedelta(days=1), revoked_at=now)
    await create_token(client, project.key)

    response = await client.get(API_TOKENS_PATH)

    assert response.status_code == 200
    items = response.json()
    assert [item["status"] for item in items] == ["active", "revoked", "expired"]
    assert all(item.keys().isdisjoint({"token", "tokenHash"}) for item in items)
    assert all(item["projectKey"] == project.key for item in items)
    created_at_values = [datetime.fromisoformat(item["createdAt"]) for item in items]
    assert created_at_values == sorted(created_at_values, reverse=True)
    use_session(client, other.session_token)
    assert len((await client.get(API_TOKENS_PATH)).json()) == 1


async def test_revoke_own_token_is_idempotent(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)
    await create_token(client, project.key)
    token_id = (await client.get(API_TOKENS_PATH)).json()[0]["id"]

    first = await client.delete(f"{API_TOKENS_PATH}/{token_id}")
    first_listing = (await client.get(API_TOKENS_PATH)).json()[0]
    second = await client.delete(f"{API_TOKENS_PATH}/{token_id}")
    second_listing = (await client.get(API_TOKENS_PATH)).json()[0]

    assert first.status_code == 204
    assert second.status_code == 204
    assert first_listing["status"] == "revoked"
    assert first_listing["revokedAt"] is not None
    assert second_listing["revokedAt"] == first_listing["revokedAt"]


async def test_revoking_another_users_token_or_an_unknown_id_gives_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)
    await create_token(client, project.key)
    token_id = (await client.get(API_TOKENS_PATH)).json()[0]["id"]
    await sign_up_member(client, container, recording_mailer, project)

    other_users_token = await client.delete(f"{API_TOKENS_PATH}/{token_id}")
    unknown_token = await client.delete(f"{API_TOKENS_PATH}/{uuid4()}")

    assert other_users_token.status_code == 404
    assert other_users_token.json() == {"code": "NOT_FOUND", "message": "Token not found."}
    assert unknown_token.status_code == 404


async def test_endpoints_need_a_session(client: AsyncClient) -> None:
    responses = [
        await client.get(API_TOKENS_PATH),
        await client.post(API_TOKENS_PATH, json={"name": "Claude", "projectKey": "PX"}),
        await client.delete(f"{API_TOKENS_PATH}/{uuid4()}"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401]
    assert {response.json()["code"] for response in responses} == {"NOT_SIGNED_IN"}


async def test_api_token_cannot_manage_tokens(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project)
    token = await create_token(client, project.key)
    client.cookies.clear()

    response = await client.get(API_TOKENS_PATH, headers={"authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_SIGNED_IN"
