from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update

from app.modules.auth.domains.one_time_token.entity import OneTimeToken
from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.infrastructure.one_time_token_table import OneTimeTokenTable
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.shared.postgres import Database


class PostgresOneTimeTokenRepository(OneTimeTokenRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_token_hash(self, token_hash: str, purpose: OneTimeTokenPurpose) -> OneTimeToken | None:
        row = await self._database.get_current_session().scalar(
            select(OneTimeTokenTable).where(
                OneTimeTokenTable.token_hash == token_hash, OneTimeTokenTable.purpose == purpose
            )
        )
        return None if row is None else OneTimeToken.model_validate(row)

    async def save(self, one_time_token: OneTimeToken) -> None:
        await self._database.get_current_session().merge(OneTimeTokenTable(**one_time_token.model_dump()))

    async def expire_unused_for_user(self, user_id: UUID, purpose: OneTimeTokenPurpose, now: datetime) -> None:
        await self._database.get_current_session().execute(
            update(OneTimeTokenTable)
            .where(
                OneTimeTokenTable.user_id == user_id,
                OneTimeTokenTable.purpose == purpose,
                OneTimeTokenTable.used_at.is_(None),
            )
            .values(used_at=now)
        )
