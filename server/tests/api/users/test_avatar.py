from httpx import AsyncClient

from app.container import Container
from app.modules.files.typing.enums import StoredFileStatus
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.users.account_steps import save_stored_file
from tests.conftest import RecordingMailer


async def test_avatar_redirects_to_a_short_signed_link(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    avatar_file = await save_stored_file(container, member.user_id)
    patch_response = await client.patch("/api/me", json={"avatarFileId": str(avatar_file.id)})
    viewer = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, viewer.session_token)

    response = await client.get(f"/api/users/{member.user_id}/avatar", params={"v": str(avatar_file.id)})

    assert patch_response.status_code == 200
    assert response.status_code == 302
    assert response.headers["location"] == f"https://storage.test/tessio/{avatar_file.object_key}"
    assert response.headers["cache-control"] == "private, max-age=240"


async def test_avatar_is_not_found_without_an_uploaded_file(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    pending_file = await save_stored_file(container, member.user_id, StoredFileStatus.PENDING)

    no_avatar_response = await client.get(f"/api/users/{member.user_id}/avatar")
    unknown_user_response = await client.get("/api/users/00000000-0000-7000-8000-000000000000/avatar")
    async with container.database.begin():
        user = await container.user_repository.find_by_id(member.user_id)
        assert user is not None
        await container.user_repository.update(user, user.model_copy(update={"avatar_file_id": pending_file.id}))
    pending_response = await client.get(f"/api/users/{member.user_id}/avatar")

    assert no_avatar_response.status_code == 404
    assert no_avatar_response.json()["code"] == "NOT_FOUND"
    assert unknown_user_response.status_code == 404
    assert pending_response.status_code == 404


async def test_avatar_needs_a_signed_in_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    client.cookies.clear()

    response = await client.get(f"/api/users/{member.user_id}/avatar")

    assert response.status_code == 401
