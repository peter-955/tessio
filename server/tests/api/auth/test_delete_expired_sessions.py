from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

from app.container import Container
from app.modules.auth import DeleteExpiredSessionsJobHandler, DeleteExpiredSessionsUseCase
from app.modules.auth.domains.user_session.entity import UserSession
from tests.api.projects.user_steps import create_invited_user
from tests.conftest import RecordingMailer


def build_user_session(user_id: UUID, expires_at: datetime) -> UserSession:
    now = datetime.now(UTC)
    session_id = uuid7()
    return UserSession(
        id=session_id,
        user_id=user_id,
        token_hash=f"hash-{session_id}",
        is_two_factor_passed=True,
        user_agent=None,
        ip=None,
        last_seen_at=now,
        expires_at=expires_at,
        created_at=now,
    )


async def test_job_deletes_only_expired_sessions(container: Container, recording_mailer: RecordingMailer) -> None:
    user_id = await create_invited_user(container, recording_mailer)
    now = datetime.now(UTC)
    expired_session = build_user_session(user_id, now - timedelta(minutes=1))
    live_session = build_user_session(user_id, now + timedelta(days=1))
    async with container.database.begin():
        await container.user_session_repository.save(expired_session)
        await container.user_session_repository.save(live_session)
    use_case = DeleteExpiredSessionsUseCase(container.database, container.user_session_repository)

    await DeleteExpiredSessionsJobHandler(use_case).handle({})

    async with container.database.begin():
        remaining_expired = await container.user_session_repository.find_by_token_hash(expired_session.token_hash)
        remaining_live = await container.user_session_repository.find_by_token_hash(live_session.token_hash)
    assert remaining_expired is None
    assert remaining_live == live_session


async def test_use_case_counts_the_deleted_sessions(container: Container, recording_mailer: RecordingMailer) -> None:
    user_id = await create_invited_user(container, recording_mailer)
    now = datetime.now(UTC)
    async with container.database.begin():
        for minutes in (1, 2):
            await container.user_session_repository.save(build_user_session(user_id, now - timedelta(minutes=minutes)))
    use_case = DeleteExpiredSessionsUseCase(container.database, container.user_session_repository)

    deleted_count = await use_case.execute(now)

    assert deleted_count >= 2
