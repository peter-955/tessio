import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.auth.domains.profile_changes.entity import ProfileChanges
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.errors import NotSignedInError
from app.modules.users import User, UserStatus, WorkspaceRole
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.users.account_steps import sign_in_with_password
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD

NEW_PASSWORD = "a completely different passphrase 42"


async def read_user(container: Container, user: User) -> User:
    async with container.database.begin():
        stored_user = await container.user_repository.find_by_id(user.id)
    assert stored_user is not None
    return stored_user


async def test_password_change_after_a_deactivation_keeps_the_user_deactivated(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    authenticated = await container.authenticate_session.execute(member.session_token)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    use_session(client, admin.session_token)
    deactivate_response = await client.post(f"/api/users/{member.user_id}/deactivate")

    with pytest.raises(NotSignedInError):
        await container.change_password.execute(authenticated, PASSWORD, NEW_PASSWORD)
    stored_user = await read_user(container, authenticated.user)
    new_password_status = await sign_in_with_password(client, member.email, NEW_PASSWORD)

    assert deactivate_response.status_code == 200
    assert stored_user.status is UserStatus.DEACTIVATED
    assert stored_user.deactivated_at is not None
    assert stored_user.password_hash == authenticated.user.password_hash
    assert new_password_status == 401


async def test_profile_update_after_a_demotion_keeps_the_new_role(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    authenticated = await container.authenticate_session.execute(admin.session_token)
    use_session(client, owner.session_token)
    demote_response = await client.put(f"/api/users/{admin.user_id}/workspace-role", json={"workspaceRole": "member"})

    updated_user = await container.update_profile.execute(authenticated, ProfileChanges(name="Renamed"))
    stored_user = await read_user(container, authenticated.user)

    assert demote_response.status_code == 200
    assert updated_user.workspace_role is WorkspaceRole.MEMBER
    assert stored_user.workspace_role is WorkspaceRole.MEMBER
    assert stored_user.name == "Renamed"


async def test_profile_update_after_a_deactivation_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    authenticated = await container.authenticate_session.execute(member.session_token)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    use_session(client, admin.session_token)
    await client.post(f"/api/users/{member.user_id}/deactivate")

    with pytest.raises(NotSignedInError):
        await container.update_profile.execute(authenticated, ProfileChanges(name="Renamed"))
    stored_user = await read_user(container, authenticated.user)

    assert stored_user.status is UserStatus.DEACTIVATED
    assert stored_user.name != "Renamed"


async def test_own_two_factor_reset_after_a_demotion_keeps_the_new_role(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    authenticated = await container.authenticate_session.execute(admin.session_token)
    use_session(client, owner.session_token)
    await client.put(f"/api/users/{admin.user_id}/workspace-role", json={"workspaceRole": "member"})

    await container.reset_own_two_factor.execute(authenticated, PASSWORD, SessionClient(user_agent=None, ip=None))
    stored_user = await read_user(container, authenticated.user)

    assert stored_user.workspace_role is WorkspaceRole.MEMBER
    assert stored_user.totp_confirmed_at is None
