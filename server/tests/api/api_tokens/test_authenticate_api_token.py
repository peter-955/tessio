from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.api_tokens.errors import InvalidApiTokenError
from app.modules.users import WorkspaceRole
from app.shared.permissions import Capability, PermissionDeniedError, ProjectArchivedError, ProjectRole
from tests.api.api_tokens.api_token_steps import (
    SeededProject,
    add_member,
    archive_project,
    change_member_role,
    create_token,
    find_token,
    insert_token,
    remove_member,
    save_token,
    seed_project,
)
from tests.api.projects.user_steps import SignedUpAccount, deactivate_user, sign_up_as
from tests.conftest import RecordingMailer


async def sign_up_with_token(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
    workspace_role: WorkspaceRole = WorkspaceRole.MEMBER,
) -> tuple[SignedUpAccount, SeededProject, str]:
    project = await seed_project(container)
    account = await sign_up_as(client, container, recording_mailer, workspace_role)
    await add_member(container, project, account.user_id, role)
    return account, project, await create_token(client, project.key)


async def test_valid_token_returns_a_token_actor_and_marks_it_used(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, project, token = await sign_up_with_token(client, container, recording_mailer)

    actor = await container.authenticate_api_token.execute(token, Capability.RUN_START)

    api_token = await find_token(container, token)
    assert actor.user_id == account.user_id
    assert actor.workspace_role.value == WorkspaceRole.MEMBER.value
    assert actor.api_token_id == api_token.id
    assert actor.token_project_id == project.id
    assert api_token.last_used_at is not None


async def test_last_used_at_is_written_at_most_once_a_minute(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, token = await sign_up_with_token(client, container, recording_mailer)
    await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)
    first_use = await find_token(container, token)

    await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)
    assert (await find_token(container, token)).last_used_at == first_use.last_used_at

    stale_use = datetime.now(UTC) - timedelta(seconds=61)
    await save_token(container, first_use.model_copy(update={"last_used_at": stale_use}))
    await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)
    refreshed = (await find_token(container, token)).last_used_at
    assert refreshed is not None
    assert refreshed > stale_use + timedelta(seconds=30)


@pytest.mark.parametrize("token", ["tsio_00000000_unknown", "abc", ""])
async def test_unknown_or_malformed_token_is_invalid(container: Container, token: str) -> None:
    with pytest.raises(InvalidApiTokenError):
        await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)


async def test_session_token_is_not_an_api_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, _, _ = await sign_up_with_token(client, container, recording_mailer)

    with pytest.raises(InvalidApiTokenError):
        await container.authenticate_api_token.execute(account.session_token, Capability.PROJECT_VIEW)


async def test_revoked_and_expired_tokens_are_invalid(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, project, _ = await sign_up_with_token(client, container, recording_mailer)
    now = datetime.now(UTC)
    revoked_token = await insert_token(container, account.user_id, project.id, now + timedelta(days=1), revoked_at=now)
    expired_token = await insert_token(container, account.user_id, project.id, now - timedelta(seconds=1))

    for token in (revoked_token, expired_token):
        with pytest.raises(InvalidApiTokenError):
            await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)


async def test_deactivated_user_token_is_invalid(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, _, token = await sign_up_with_token(client, container, recording_mailer)
    await deactivate_user(container, account.user_id)

    with pytest.raises(InvalidApiTokenError):
        await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)


async def test_removed_member_token_is_invalid(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, project, token = await sign_up_with_token(client, container, recording_mailer)
    await remove_member(container, project, account.user_id)

    with pytest.raises(InvalidApiTokenError):
        await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)


async def test_demoted_member_token_follows_the_current_role(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, project, token = await sign_up_with_token(client, container, recording_mailer)
    await container.authenticate_api_token.execute(token, Capability.RUN_START)
    await change_member_role(container, project, account.user_id, ProjectRole.VIEWER)

    with pytest.raises(PermissionDeniedError):
        await container.authenticate_api_token.execute(token, Capability.RUN_START)
    actor = await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)
    assert actor.user_id == account.user_id


async def test_archived_project_token_can_only_read(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, project, token = await sign_up_with_token(client, container, recording_mailer)
    await archive_project(container, project)

    with pytest.raises(ProjectArchivedError):
        await container.authenticate_api_token.execute(token, Capability.RUN_START)
    await container.authenticate_api_token.execute(token, Capability.PROJECT_VIEW)


async def test_workspace_admin_token_is_not_elevated(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, token = await sign_up_with_token(
        client, container, recording_mailer, role=ProjectRole.DEV, workspace_role=WorkspaceRole.ADMIN
    )

    await container.authenticate_api_token.execute(token, Capability.RUN_START)
    with pytest.raises(PermissionDeniedError):
        await container.authenticate_api_token.execute(token, Capability.RUN_FINISH_ANY)


async def test_revoker_revokes_only_the_users_active_tokens(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account, project, active_token = await sign_up_with_token(client, container, recording_mailer)
    _, _, other_users_token = await sign_up_with_token(client, container, recording_mailer)
    earlier = datetime.now(UTC) - timedelta(days=2)
    revoked_token = await insert_token(
        container, account.user_id, project.id, datetime.now(UTC) + timedelta(days=1), revoked_at=earlier
    )
    now = datetime.now(UTC)

    async with container.database.begin():
        await container.api_token_revoker.revoke_all_for_user(account.user_id, now)

    assert (await find_token(container, active_token)).revoked_at == now
    assert (await find_token(container, revoked_token)).revoked_at == earlier
    assert (await find_token(container, other_users_token)).revoked_at is None
    with pytest.raises(InvalidApiTokenError):
        await container.authenticate_api_token.execute(active_token, Capability.PROJECT_VIEW)
