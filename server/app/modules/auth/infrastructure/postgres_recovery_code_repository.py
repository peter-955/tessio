from uuid import UUID

from sqlalchemy import delete, select

from app.modules.auth.domains.recovery_code.entity import RecoveryCode
from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.infrastructure.recovery_code_table import RecoveryCodeTable
from app.shared.postgres import Database


class PostgresRecoveryCodeRepository(RecoveryCodeRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def replace_for_user(self, user_id: UUID, recovery_codes: list[RecoveryCode]) -> None:
        session = self._database.get_current_session()
        await session.execute(delete(RecoveryCodeTable).where(RecoveryCodeTable.user_id == user_id))
        session.add_all(RecoveryCodeTable(**recovery_code.model_dump()) for recovery_code in recovery_codes)

    async def find_unused(self, user_id: UUID, code_hash: str) -> RecoveryCode | None:
        row = await self._database.get_current_session().scalar(
            select(RecoveryCodeTable).where(
                RecoveryCodeTable.user_id == user_id,
                RecoveryCodeTable.code_hash == code_hash,
                RecoveryCodeTable.used_at.is_(None),
            )
        )
        return None if row is None else RecoveryCode.model_validate(row)

    async def save(self, recovery_code: RecoveryCode) -> None:
        await self._database.get_current_session().merge(RecoveryCodeTable(**recovery_code.model_dump()))
