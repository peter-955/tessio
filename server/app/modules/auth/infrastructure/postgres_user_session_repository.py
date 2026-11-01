from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select

from app.modules.auth.domains.user_session.entity import UserSession
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.infrastructure.user_session_table import UserSessionTable
from app.shared.postgres import Database


class PostgresUserSessionRepository(UserSessionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_token_hash(self, token_hash: str) -> UserSession | None:
        row = await self._database.get_current_session().scalar(
            select(UserSessionTable).where(UserSessionTable.token_hash == token_hash)
        )
        return None if row is None else UserSession.model_validate(row)

    async def save(self, user_session: UserSession) -> None:
        await self._database.get_current_session().merge(UserSessionTable(**user_session.model_dump()))

    async def delete(self, user_session_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(UserSessionTable).where(UserSessionTable.id == user_session_id)
        )

    async def delete_all_for_user(self, user_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(UserSessionTable).where(UserSessionTable.user_id == user_id)
        )

    async def delete_all_for_user_except(self, user_id: UUID, kept_user_session_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(UserSessionTable).where(
                UserSessionTable.user_id == user_id, UserSessionTable.id != kept_user_session_id
            )
        )

    async def delete_expired(self, now: datetime) -> int:
        deleted_ids = await self._database.get_current_session().scalars(
            delete(UserSessionTable).where(UserSessionTable.expires_at <= now).returning(UserSessionTable.id)
        )
        return len(deleted_ids.all())
