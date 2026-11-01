from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient

from app.modules.audit import AuditAction
from tests.api.files.conftest import FilesTestContainer, seed_project
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import sign_up


class RolledBackError(Exception):
    pass


async def sign_up_user(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> UUID:
    await sign_up(client, files_container, recording_mailer)
    return UUID((await client.get("/api/auth/me")).json()["id"])


async def test_audit_events_are_written_in_the_callers_transaction_and_listed_by_target(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    actor_id = await sign_up_user(client, files_container, recording_mailer)
    project = await seed_project(files_container, ["text/csv"])
    target_id, run_id, api_token_id = uuid7(), uuid7(), uuid7()

    async with files_container.database.begin():
        revealed = await files_container.record_audit_event.execute(
            actor_id, AuditAction.SECRET_REVEAL, project_id=project.id, target_id=target_id
        )
        resolved = await files_container.record_audit_event.execute(
            actor_id,
            AuditAction.SECRET_RESOLVE,
            project_id=project.id,
            target_id=target_id,
            api_token_id=api_token_id,
            run_id=run_id,
        )
        listed_inside = await files_container.audit_event_repository.list_for_target(target_id)

    async with files_container.database.begin():
        listed_after = await files_container.audit_event_repository.list_for_target(target_id)

    assert listed_inside == [revealed, resolved]
    assert listed_after == [revealed, resolved]
    assert resolved.run_id == run_id
    assert resolved.api_token_id == api_token_id
    assert revealed.project_id == project.id


async def test_audit_events_roll_back_with_the_callers_transaction(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    actor_id = await sign_up_user(client, files_container, recording_mailer)
    target_id = uuid7()

    with pytest.raises(RolledBackError):
        async with files_container.database.begin():
            await files_container.record_audit_event.execute(actor_id, AuditAction.SECRET_REVEAL, target_id=target_id)
            raise RolledBackError

    async with files_container.database.begin():
        assert await files_container.audit_event_repository.list_for_target(target_id) == []
