from httpx import AsyncClient

from app.container import Container
from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import create_invited_user, sign_up_as, use_session
from tests.api.users.account_steps import read_invite_token, save_stored_file
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


async def test_current_user_has_default_profile_fields(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Mia Member")

    response = await client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(member.user_id),
        "email": member.email,
        "name": "Mia Member",
        "workspaceRole": "member",
        "nextStep": "signed_in",
        "language": "en",
        "colorScheme": "auto",
        "avatarFileId": None,
        "avatarUrl": None,
        "isTwoFactorSetUp": True,
    }


async def test_profile_updates_name_language_and_color_scheme(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    patch_response = await client.patch("/api/me", json={"name": "  Mia Renamed ", "language": "vi"})
    scheme_response = await client.patch("/api/me", json={"colorScheme": "dark"})
    me_response = await client.get("/api/auth/me")

    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Mia Renamed"
    assert patch_response.json()["language"] == "vi"
    assert patch_response.json()["nextStep"] == "signed_in"
    assert scheme_response.json()["colorScheme"] == "dark"
    assert scheme_response.json()["name"] == "Mia Renamed"
    assert me_response.json()["language"] == "vi"
    assert me_response.json()["colorScheme"] == "dark"


async def test_profile_sets_and_clears_an_uploaded_avatar(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    avatar_file = await save_stored_file(container, member.user_id)

    set_response = await client.patch("/api/me", json={"avatarFileId": str(avatar_file.id)})
    rename_response = await client.patch("/api/me", json={"name": "Keeps Avatar"})
    clear_response = await client.patch("/api/me", json={"avatarFileId": None})

    assert set_response.status_code == 200
    assert set_response.json()["avatarFileId"] == str(avatar_file.id)
    assert set_response.json()["avatarUrl"] == f"/api/users/{member.user_id}/avatar?v={avatar_file.id}"
    assert rename_response.json()["avatarFileId"] == str(avatar_file.id)
    assert clear_response.status_code == 200
    assert clear_response.json()["avatarFileId"] is None
    assert clear_response.json()["avatarUrl"] is None


async def test_profile_refuses_avatars_that_are_pending_foreign_or_not_avatars(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    pending_file = await save_stored_file(container, member.user_id, StoredFileStatus.PENDING)
    foreign_file = await save_stored_file(container, other.user_id)
    screenshot_file = await save_stored_file(container, member.user_id, kind=StoredFileKind.SCREENSHOT)

    pending_response = await client.patch("/api/me", json={"avatarFileId": str(pending_file.id)})
    foreign_response = await client.patch("/api/me", json={"avatarFileId": str(foreign_file.id)})
    screenshot_response = await client.patch("/api/me", json={"avatarFileId": str(screenshot_file.id)})
    unknown_response = await client.patch("/api/me", json={"avatarFileId": "00000000-0000-7000-8000-000000000000"})

    assert pending_response.status_code == 409
    assert pending_response.json()["code"] == "UPLOAD_NOT_COMPLETED"
    assert foreign_response.status_code == 404
    assert foreign_response.json()["code"] == "NOT_FOUND"
    assert screenshot_response.status_code == 404
    assert unknown_response.status_code == 404


async def test_profile_update_needs_a_full_session_and_a_name(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    blank_name_response = await client.patch("/api/me", json={"name": "   "})
    bad_language_response = await client.patch("/api/me", json={"language": "de"})
    await create_invited_user(container, recording_mailer)
    client.cookies.clear()
    await client.post(f"/api/auth/invites/{read_invite_token(recording_mailer)}", json={"password": PASSWORD})

    half_session_response = await client.patch("/api/me", json={"name": "Half"})

    assert blank_name_response.status_code == 422
    assert bad_language_response.status_code == 422
    assert half_session_response.status_code == 401
    assert half_session_response.json()["code"] == "NOT_SIGNED_IN"


async def test_profile_changes_are_only_for_the_signed_in_user(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Olly Other")
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    await client.patch("/api/me", json={"name": "Only Me"})
    use_session(client, other.session_token)
    other_response = await client.get("/api/auth/me")

    assert member.user_id != other.user_id
    assert other_response.json()["name"] == "Olly Other"
