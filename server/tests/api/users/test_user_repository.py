from uuid import UUID

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.users import User, UserLanguage, WorkspaceRole
from tests.api.projects.user_steps import sign_up_as
from tests.conftest import RecordingMailer


async def read_user(container: Container, user_id: UUID) -> User:
    async with container.database.begin():
        user = await container.user_repository.find_by_id(user_id)
    assert user is not None
    return user


async def test_an_update_from_a_stale_copy_keeps_columns_it_did_not_change(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    stale_user = await read_user(container, member.user_id)
    async with container.database.begin():
        locked_user = await container.user_repository.find_by_id_for_update(member.user_id)
        assert locked_user is not None
        await container.user_repository.update(
            locked_user, locked_user.model_copy(update={"language": UserLanguage.FR})
        )

    async with container.database.begin():
        await container.user_repository.update(stale_user, stale_user.model_copy(update={"name": "New"}))
    stored_user = await read_user(container, member.user_id)

    assert stored_user.name == "New"
    assert stored_user.language is UserLanguage.FR


async def test_an_update_without_changes_writes_nothing(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    user = await read_user(container, member.user_id)
    async with container.database.begin():
        await container.user_repository.update(user, user.model_copy())
    stored_user = await read_user(container, member.user_id)

    assert stored_user == user


async def test_an_update_with_another_users_id_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    first_member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    second_member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    first_user = await read_user(container, first_member.user_id)
    second_user = await read_user(container, second_member.user_id)

    async with container.database.begin():
        with pytest.raises(ValueError, match="own id"):
            await container.user_repository.update(first_user, second_user)
